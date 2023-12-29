import inventory
import player
import random
import bosses
import pandorabot
import quest
import globalitems

import pandas as pd
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import mydb

skill_names_dict = {
    "Knight": ["Destructive Cleave", "Merciless Blade", "Ruinous Slash", "Destiny Divider"],
    "Ranger": ["Viper Shot", "Comet Arrow", "Meteor Volley", "Blitz Barrage"],
    "Assassin": ["Wound Carver", "Exploit Injury", "Eternal Laceration", "Blood Recursion"],
    "Mage": ["Magical Bolt", "Aether Blast", "Mystic Maelstrom", "Astral Convergence"],
    "Weaver": ["Power Stitch", "Infused Slice", "Multithreading", "Reality Fabricator"],
    "Rider": ["Valiant Charge", "Surge Dash", "Mounted Onslaught", "Chaos Rampage"],
    "Summoner": ["Savage Blows", "Moonlit Hunt", "Berserk Frenzy", "Synchronized Wrath"]
}

combat_command_list = [("solo", "Challenge a solo boss. Stamina Cost: 200", 0),
                       ("arena", "Enter pvp combat with another player.", 1),
                       ("abandon", "Abandon an active solo encounter.", 2)]

t5_hp_bar_empty = ["<:HP_Bar_Empty_03:1176059083204337744>", "<:HP_Bar_Empty_04:1176059084840124458>",
                   "<:HP_Bar_Empty_05:1176059085951606856>", "<:HP_Bar_Empty_06:1176059046617428039>",
                   "<:HP_Bar_Empty_07:1176059047607287888>", "<:HP_Bar_Empty_08:1176059049293393930>",
                   "<:HP_Bar_Empty_09:1176059050186788934>", "<:HP_Bar_Empty_10:1176059050979512370>",
                   "<:HP_Bar_Empty_11:1176059052325879879>", "<:HP_Bar_Empty_12:1176059019119558776>",
                   "<:HP_Bar_Empty_13:1176059020365266995>", "<:HP_Bar_Empty_14:1176059021724237895>",
                   "<:HP_Bar_Empty_15:1176059022802161694>", "<:HP_Bar_Empty_16:1176059023599075328>",
                   "<:HP_Bar_Empty_17:1176059025721393162>"]
t5_hp_bar_full = ["<:HP_Bar_Full_03:1176053423049822219>", "<:HP_Bar_Full_04:1176053419346235403>",
                  "<:HP_Bar_Full_05:1176053420914905139>", "<:HP_Bar_Full_06:1176053422127054888>",
                  "<:HP_Bar_Full_07:1176053399561711626>", "<:HP_Bar_Full_08:1176053401029718036>",
                  "<:HP_Bar_Full_09:1176053402132820048>", "<:HP_Bar_Full_10:1176053403193987133>",
                  "<:HP_Bar_Full_11:1176056919396470824>", "<:HP_Bar_Full_12:1176053365298450526>",
                  "<:HP_Bar_Full_13:1176053366321852416>", "<:HP_Bar_Full_14:1176053367563362354>",
                  "<:HP_Bar_Full_15:1176053368293175346>", "<:HP_Bar_Full_16:1176053369320775761>",
                  "<:HP_Bar_Full_17:1176053370876870659>"]
hp_bar_dict = {1: [t5_hp_bar_full, t5_hp_bar_empty], 2: [t5_hp_bar_full, t5_hp_bar_empty],
               3: [t5_hp_bar_full, t5_hp_bar_empty], 4: [t5_hp_bar_full, t5_hp_bar_empty],
               5: [t5_hp_bar_full, t5_hp_bar_empty], 6: [t5_hp_bar_full, t5_hp_bar_empty]}


class CombatTracker:
    def __init__(self):
        self.charges = 0
        self.remaining_hits = 0
        self.total_dps = 0
        self.total_cycles = 0
        self.stun_cycles = 0
        self.time_lock = 0
        self.time_damage = 0
        self.player_cHP = 0
        self.bleed_tracker = 0.0


def run_cycle(combat_tracker, active_boss, player_object, method):
    class_skill_list = skill_names_dict[player_object.player_class]
    is_alive = True
    total_damage = 0
    hit_list = []
    if combat_tracker.stun_cycles <= 0:
        combo_count = 0
        hp_adjust_msg = ""
        if active_boss.boss_type_num >= 2:
            if active_boss.boss_element != 9:
                boss_damage_element = active_boss.boss_element
            else:
                boss_damage_element = random.randint(0, 8)
            boss_adjuster = int(active_boss.boss_lvl / 10 + 1)
            boss_damage = random.randint(100 * boss_adjuster, 250 * boss_adjuster)
            boss_damage -= int(boss_damage * player_object.elemental_resistance[boss_damage_element])
            boss_damage -= int(boss_damage * player_object.damage_mitigation * 0.01)
            combat_tracker.player_cHP -= boss_damage
            hp_adjust_msg = f"{active_boss.boss_name} attacks dealing {globalitems.number_conversion(boss_damage)} damage!\n"
            if active_boss.boss_type_num >= 3:
                boss_healing = int(0.001 * active_boss.boss_tier * active_boss.boss_mHP)
                active_boss.boss_cHP += boss_healing
                if active_boss.boss_cHP >= active_boss.boss_mHP:
                    active_boss.boss_cHP = active_boss.boss_mHP
                hp_adjust_msg += f"{active_boss.boss_name} regenerated 0.{active_boss.boss_tier}% HP!\n"
            if combat_tracker.player_cHP <= 0:
                if player_object.immortal:
                    combat_tracker.player_cHP = 1
                else:
                    combat_tracker.player_cHP = 0
                    combat_tracker.stun_cycles = 5
            else:
                if player_object.hp_regen != 0:
                    regen_value = int(player_object.player_mHP * player_object.hp_regen)
                    combat_tracker.player_cHP += regen_value
                    if combat_tracker.player_cHP > player_object.player_mHP:
                        combat_tracker.player_cHP = player_object.player_mHP
                    hp_adjust_msg += f"{player_object.player_username} regenerated {globalitems.number_conversion(regen_value)} HP!\n"

        hits_per_cycle = int(player_object.attack_speed)
        combat_tracker.remaining_hits += player_object.attack_speed - hits_per_cycle
        while combat_tracker.remaining_hits >= 1:
            hits_per_cycle += 1
            combat_tracker.remaining_hits -= 1
        for x in range(hits_per_cycle):
            combo_count += 1 + player_object.combo_application
            hit_damage, critical_type = player_object.get_player_boss_damage(active_boss)
            damage, skill_name = skill_adjuster(player_object, combat_tracker, hit_damage,
                                                combo_count, False)
            if player_object.bleed_application >= 1:
                combat_tracker.bleed_tracker += 0.05 * player_object.bleed_application
                if combat_tracker.bleed_tracker >= 1:
                    combat_tracker.bleed_tracker = 1
            extension = ""
            if damage >= active_boss.damage_cap != -1:
                damage = active_boss.damage_cap
                extension = " *LIMIT*"
            damage, status_msg = check_lock(player_object, combat_tracker, damage)
            hit_msg = f"{combo_count}x Combo: {skill_name} {globalitems.number_conversion(damage)}{extension}"
            if status_msg != "":
                hit_msg += f" *{status_msg}*"
            if critical_type != "":
                hit_msg += f" *{critical_type}*"
            hit_list.append([damage, hit_msg])
            active_boss.boss_cHP -= damage
            if combat_tracker.charges >= 20:
                combo_count += 1 + player_object.combo_application
                hit_damage, critical_type = player_object.get_player_boss_damage(active_boss)
                damage, skill_name = skill_adjuster(player_object, combat_tracker, hit_damage,
                                                    combo_count, True)
                extension = ""
                if damage >= active_boss.damage_cap != -1:
                    damage = active_boss.damage_cap
                    extension = " *LIMIT*"
                damage, status_msg = check_lock(player_object, combat_tracker, damage)
                hit_msg = f"Ultimate: {skill_name} {globalitems.number_conversion(damage)}{extension}"
                if status_msg != "":
                    hit_msg += f" *{status_msg}*"
                if critical_type != "":
                    hit_msg += f" *{critical_type}*"
                hit_list.append([damage, hit_msg])
                active_boss.boss_cHP -= damage
                if player_object.bleed_application >= 1:
                    hit_damage = 1.5 * player_object.get_bleed_damage(active_boss)
                    hit_damage = int(hit_damage * combat_tracker.bleed_tracker)
                    hit_damage, bleed_type = check_hyper_bleed(player_object, hit_damage)
                    hit_damage *= (1 + player_object.bleed_penetration)
                    bleed_damage = int(hit_damage)
                    extension = ""
                    if bleed_damage >= active_boss.damage_cap != -1:
                        bleed_damage = active_boss.damage_cap
                        extension = " *LIMIT*"
                    hit_msg = f"Sanguine Rupture: {globalitems.number_conversion(bleed_damage)}{extension} *{bleed_type}*"
                    for b in range(player_object.bleed_application):
                        hit_list.append([bleed_damage, hit_msg])
                        active_boss.boss_cHP -= bleed_damage
            if not active_boss.calculate_hp():
                is_alive = False
                break
        if player_object.bleed_application >= 1:
            hit_damage = 0.75 * player_object.get_bleed_damage(active_boss)
            hit_damage = int(hit_damage * combat_tracker.bleed_tracker)
            hit_damage, bleed_type = check_hyper_bleed(player_object, hit_damage)
            hit_damage *= (1 + player_object.bleed_penetration)
            bleed_damage = int(hit_damage)
            extension = ""
            if bleed_damage >= active_boss.damage_cap != -1:
                bleed_damage = active_boss.damage_cap
                extension = " *LIMIT*"
            hit_msg = f"Blood Rupture: {globalitems.number_conversion(bleed_damage)}{extension} *{bleed_type}*"
            for b in range(player_object.bleed_application):
                hit_list.append([bleed_damage, hit_msg])
                active_boss.boss_cHP -= bleed_damage
            if not active_boss.calculate_hp():
                is_alive = False
        damage_values = [hit[0] for hit in hit_list]
        total_damage = sum(damage_values)
        combat_tracker.total_dps += total_damage
        battle_msg = f"{player_object.player_username} - HP: {globalitems.display_hp(combat_tracker.player_cHP, player_object.player_mHP)}"
        if method == "Solo":
            battle_msg = f"{hp_adjust_msg}{battle_msg}"
    else:
        combat_tracker.stun_cycles -= 1
        if combat_tracker.stun_cycles == 0:
            battle_msg = f"{player_object.player_username} has recovered!"
            combat_tracker.player_cHP = player_object.player_mHP
        else:
            battle_msg = f"{player_object.player_username} is recovering!"
    return hit_list, battle_msg, is_alive, total_damage


def run_solo_cycle(combat_tracker, active_boss, player_object):
    hit_list, battle_msg, is_alive, total_damage = run_cycle(combat_tracker, active_boss, player_object, "Solo")
    combat_tracker.total_cycles += 1
    total_dps = int(combat_tracker.total_dps / combat_tracker.total_cycles)
    if is_alive:
        embed_msg = active_boss.create_boss_embed(total_dps)
        embed_msg.add_field(name="", value=battle_msg, inline=False)
    else:
        embed_msg = active_boss.create_boss_embed(total_dps)
        if active_boss.boss_tier >= 4:
            quest.assign_tokens(player_object, active_boss)
    hit_field = ""
    for hit in hit_list:
        hit_field += f"{hit[1]}\n"
    embed_msg.add_field(name="", value=hit_field, inline=False)
    return embed_msg


def run_raid_cycle(combat_tracker, active_boss, player_object):
    hit_list, battle_msg, is_alive, total_damage = run_cycle(combat_tracker, active_boss, player_object, "Raid")
    combat_tracker.total_cycles += 1
    if not is_alive and active_boss.boss_tier >= 4:
        quest.assign_tokens(player_object, active_boss)
    if total_damage != 0:
        player_msg = f"{battle_msg} - dealt {globalitems.number_conversion(total_damage)} damage!"
    else:
        player_msg = battle_msg
    return player_msg, total_damage


def get_item_tier_damage(material_tier):
    match material_tier:
        case  "Steel" | "Glittering" | "Essence" | "Metallic" | "Faint" | "Enchanted" | \
              "Corrupt" | "Pure" | "Tempered" | "Legendary":
            damage_temp = 2000
        case "Silver" | "Dazzling" | "Spirit" | "Gold" | "Luminous" | "Inverted" | "Pristine" | "Empowered" | "Mythical":
            damage_temp = 4000
        case "Mithril" | "Lustrous" | "Soulbound" | "Jeweled" | "Shining" | \
             "Abyssal" | "Majestic" | "Unsealed" | "Fantastical":
            damage_temp = 6000
        case "Diamond" | "Radiant" | "Phantasmal" | "Calamitous" | "Awakened" | "Omniscient":
            damage_temp = 8000
        case "Crystal" | "Divine" | "Spectral" | "Balefire" | "Transcendent" | "Plasma":
            damage_temp = 10000
        case "Key of Freedom," | "Chroma":
            damage_temp = 20000
        case "Key of Desires," | "Chromatic":
            damage_temp = 40000
        case "Key of Hopes," | "Prisma":
            damage_temp = 60000
        case "Key of Dreams," | "Prismatic":
            damage_temp = 80000
        case "Key of Wishes," | "Iridescent":
            damage_temp = 150000
        case "Key of Miracles,":
            damage_temp = 250000
        case "Voidcrystal" | "Voidspecter":
            damage_temp = 25000
        case "Voidplasma" | "Voidforme":
            damage_temp = 50000
        case _:
            damage_temp = 0

    return damage_temp


def check_lock(player_object, combat_tracker, damage):
    status_msg = ""
    if combat_tracker.time_lock == 0:
        lock_rate = 5 * player_object.temporal_application
        random_lock_chance = random.randint(1, 100)
        if random_lock_chance <= lock_rate:
            combat_tracker.time_lock = player_object.temporal_application + 1
            status_msg = "TIME LOCK"
    elif combat_tracker.time_lock > 0:
        combat_tracker.time_lock -= 1
        combat_tracker.time_damage += damage
        if combat_tracker.time_lock == 0:
            damage = combat_tracker.time_damage * (player_object.temporal_application + 1)
            combat_tracker.time_damage = 0
            status_msg = "TIME SHATTER"
        else:
            damage = 0
            status_msg = "LOCKED"
    return damage, status_msg


def boss_defences(method, player_object, boss_object, location):
    type_multiplier = (1 - 0.05 * boss_object.boss_tier)
    if method == "Element":
        if boss_object.boss_eleweak[location] == 1:
            type_multiplier = 1
            curse_penalty = boss_object.curse_debuffs[location]
            type_multiplier += curse_penalty
    else:
        location = globalitems.class_name_list.index(player_object.player_class)
        if boss_object.boss_typeweak[location] == 1:
            type_multiplier = 1
    return type_multiplier


def boss_true_mitigation(boss_object):
    mitigation_multiplier = 1 - (boss_object.boss_lvl * 0.01)
    return mitigation_multiplier


def critical_check(player_object, player_damage, num_elements):
    # Critical hits
    random_num = random.randint(1, 100)
    if random_num <= (player_object.elemental_application * 5):
        player_damage *= num_elements
        critical_type = "FRACTAL"
    elif random_num < player_object.critical_chance:
        player_damage *= (1 + player_object.critical_multiplier)
        omega_chance = player_object.critical_application * 10
        omega_check = random.randint(1, 100)
        if omega_check <= omega_chance:
            critical_type = "OMEGA CRITICAL"
            player_damage *= (1 + player_object.critical_multiplier)
        else:
            critical_type = "CRITICAL"
        player_damage *= (1 + player_object.critical_penetration)
    else:
        critical_type = ""
    return player_damage, critical_type


def skill_adjuster(player_object, combat_tracker, hit_damage,
                   combo_count, is_ultimate):
    class_skill_list = skill_names_dict[player_object.player_class]
    combo_multiplier = (1 + (player_object.combo_multiplier * combo_count)) * (1 + player_object.combo_penetration)
    if is_ultimate:
        ultimate_multiplier = (1 + player_object.ultimate_multiplier) * (1 + player_object.ultimate_penetration)
        damage = int(hit_damage * combo_multiplier * ultimate_multiplier * (2 + player_object.skill_base_damage_bonus[3]))
        skill_name = class_skill_list[3]
        charges_gained = -20
    elif combo_count < 3:
        damage = int(hit_damage * combo_multiplier * (0.5 + player_object.skill_base_damage_bonus[0]))
        skill_name = class_skill_list[0]
        charges_gained = 1 + player_object.ultimate_application
    elif combo_count < 5:
        damage = int(hit_damage * combo_multiplier * (0.75 + player_object.skill_base_damage_bonus[1]))
        skill_name = class_skill_list[1]
        charges_gained = 1 + player_object.ultimate_application
    else:
        damage = int(hit_damage * combo_multiplier * (1 + player_object.skill_base_damage_bonus[2]))
        skill_name = class_skill_list[2]
        charges_gained = 1 + player_object.ultimate_application
    if not is_ultimate and player_object.glyph_of_eclipse:
        ultimate_multiplier = (1 + player_object.ultimate_multiplier) * (1 + player_object.ultimate_penetration)
        damage = int(hit_damage * ultimate_multiplier)
    combat_tracker.charges += charges_gained

    return damage, skill_name


def pvp_defences(attacker, defender, player_damage, e_weapon):
    # Type Defences
    adjusted_damage = player_damage - defender.damage_mitigation * 0.01 * player_damage
    # Elemental Defences
    if attacker.elemental_capacity < 9:
        temp_element_list = combat.limit_elements(attacker, e_weapon)
    else:
        temp_element_list = e_weapon.item_elements.copy()
    for idx, x in enumerate(temp_element_list):
        if x == 1:
            attacker.elemental_damage[idx] = adjusted_damage * (1 + attacker.elemental_damage_multiplier[idx])
            resist_multi = 1 - defender.elemental_resistance[idx]
            penetration_multi = 1 + attacker.elemental_penetration[idx]
            attacker.elemental_damage[idx] *= resist_multi * penetration_multi
    subtotal_damage = sum(attacker.elemental_damage) * (1 + attacker.aura) * (1 + attacker.banes[4])
    adjusted_damage = int(subtotal_damage)
    return adjusted_damage


def pvp_attack(attacker, defender):
    e_weapon = inventory.read_custom_item(attacker.player_equipped[0])
    num_elements = sum(e_weapon.item_elements)
    player_damage = attacker.get_player_initial_damage()
    player_damage, critical_type = critical_check(attacker, player_damage, num_elements)
    player_damage = pvp_defences(attacker, defender, player_damage, e_weapon)
    return player_damage, critical_type


def pvp_bleed_damage(attacker, defender):
    e_weapon = inventory.read_custom_item(attacker.player_equipped[0])
    bleed_damage = attacker.get_player_initial_damage()
    bleed_damage = pvp_defences(attacker, defender, bleed_damage, e_weapon)
    bleed_damage *= (1 + attacker.bleed_multiplier)
    bleed_damage, bleed_type = check_hyper_bleed(attacker, bleed_damage)
    bleed_damage *= (1 + attacker.bleed_penetration)
    return bleed_damage, bleed_type


def check_hyper_bleed(player_object, bleed_damage):
    hyper_bleed_rate = player_object.bleed_application * 5
    bleed_check = random.randint(1, 100)
    if bleed_check <= hyper_bleed_rate:
        bleed_type = "HYPERBLEED"
        bleed_damage *= (1 + player_object.bleed_multiplier)
    else:
        bleed_type = "BLEED"
    return bleed_damage, bleed_type


def get_random_opponent(player_echelon):
    player_list = player.get_players_by_echelon(player_echelon)
    if player_list:
        opponent_object = random.choice(player_list)
    else:
        opponent_object = player.get_player_by_name("mistysyn")
    opponent_object.get_equipped()
    return opponent_object


def check_flag(player_object):
    is_flagged = False
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text(f"SELECT * FROM AbandonEncounter WHERE player_id = :player_check")
        query = query.bindparams(player_check=int(player_object.player_id))
        df = pd.read_sql(query, pandora_db)
        if len(df) != 0:
            is_flagged = True
        pandora_db.close()
        engine.dispose()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
    return is_flagged


def toggle_flag(player_object):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text(f"SELECT * FROM AbandonEncounter WHERE player_id = :player_check")
        query = query.bindparams(player_check=int(player_object.player_id))
        df = pd.read_sql(query, pandora_db)
        if len(df) != 0:
            query = text(f"DELETE FROM AbandonEncounter WHERE player_id = :player_check")
            query = query.bindparams(player_check=int(player_object.player_id))
            pandora_db.execute(query)
        else:
            query = text(f"INSERT INTO AbandonEncounter (player_id) VALUES (:player_check)")
            query = query.bindparams(player_check=int(player_object.player_id))
            pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))


def limit_elements(player_object, e_weapon):
    elemental_breakdown = []
    temp_list = e_weapon.item_elements.copy()
    for x, is_used in enumerate(temp_list):
        if is_used:
            temp_total = player_object.elemental_damage_multiplier[x] * player_object.elemental_penetration[x]
            temp_total *= player_object.elemental_curse[x]
            elemental_breakdown.append([x, temp_total])
    sorted_indices = sorted(elemental_breakdown, key=lambda e: e[1], reverse=True)
    damage_limitation = [idx for idx, _ in sorted_indices[:player_object.elemental_capacity]]
    for i in [i for i in range(len(temp_list)) if i not in damage_limitation]:
        temp_list[i] = 0
    return temp_list


