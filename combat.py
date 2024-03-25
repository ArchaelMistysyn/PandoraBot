# General imports
import random

# Data imports
import globalitems
import sharedmethods

# Core imports
import player
import quest
import inventory
import mydb


combat_command_list = [("solo", "Challenge a solo boss. Stamina Cost: 200", 0),
                       ("arena", "Enter pvp combat with another player.", 1),
                       ("abandon", "Abandon an active solo encounter.", 2)]

boss_attack_dict = {
    "Dragon": ["[ELEMENT] Claw Slash", "[ELEMENT] Wing Blast", "Amplified [ELEMENT] Breath"],
    "Demon": ["Dark Flame", "Abyss Bolt", "Blood Deluge"],
    "Paragon": ["Essence Strike", "Essence Shock", "Essence Destruction"],
    "Arbiter": ["Decree Of Pain", "Revoke Control", "Invoke Authority"],
    "Pandora, The Celestial":
        ["Cosmic Pulse", "Constellation Blast", "Starfall", "**__Collapsing Star Hammer__**"],
    "Oblivia, The Void":
        ["Gravity Crush", "Void Grasp", "Disintegrate", "**Void Impaler**", "**__Black Hole__**"],
    "Akasha, The Infinite":
        ["Overwhelm", "Subjugation", "Manifest Armaments", "**Blade Recursion**", "**__Exceed Infinity__**"],
    "Astratha, The Dimensional":
        ["Rift Claws", "Quantum Wing Blast", "Amplified Dimension Breath", "**__Starlight Beam__**"],
    "Tyra, The Behemoth":
        ["Power Slam", "Horn Thrust", "Tectonic Rumble", "**__Tyrant's Roar__**"],
    "Diabla, The Primordial":
        ["Elemental Divergence", "Magma Blizzard", "Pyroclasmic Rain", "**__Glacial Meltdown__**"],
    "Aurora, The Fortress":
        ["Living Fortress", "Brilliant Bastion", "Radiant Aura", "**__Luminous Cascade__**"],
    "Eleuia, The Wish":
        ["Twisted Dream", "Desire's Echo", "Fervent Wish",
         "**Heartfelt Tears**", "**Shape Miracle**", "**__Shatter All Hope__**"],
    "Kazyth, Lifeblood of the True Laws":
        ["Natural Order", "Life Absorption", "Spirit Reclamation", "**__Form Distortion__**"],
    "Vexia, Scribe of the True Laws":
        ["Vengeful Inscription", "Create Rule", "Words To Life", "**Alter Chronicle**", "**__Record Erasure__**"],
    "Fleur, Oracle of the True Laws":
        ["Vine Lash", "Falling Petals", "Thorn's Embrace",
         "**Severed Fate**", "**Withering Future**", "**__Blossoming Death__**"],
    "Yubelle, Adjudicator of the True Laws":
        ["Tainted Smite", "Distorted Gavel", "Alter Verdict", "Counterfeit Retribution",
         "**Weight Of Sin**", "**Scales Of Judgement**", "**__White Abyss__**"],
    "Amaryllis, Incarnate of the Divine Lotus":
        ["Lotus Slash", "Propagate Ruin", "Divine Purgation", "Chaos Bloom", "**Sacred Revelation**",
         "**Eye Of The Annihilator**", "**Nightmare Saber**", "**__Fabricate Apotheosis__**"]
}
boss_attack_exceptions = list(boss_attack_dict.keys())
skill_multiplier_list = [1, 2, 3, 5, 7, 10, 15, 20]


class CombatTracker:
    def __init__(self, player_obj):
        self.player_obj = player_obj
        self.player_cHP = player_obj.player_mHP
        self.charges, self.remaining_hits = 0, 0
        self.total_dps, self.highest_damage = 0, 0.0
        self.recovery, self.hp_regen = player_obj.recovery, int(player_obj.hp_regen * player_obj.player_mHP)
        self.total_cycles, self.stun_cycles = 0, 0
        self.status_type, status_recovery = "", ""
        self.time_lock, self.time_damage = 0, 0
        self.bleed_tracker = 0.0


def run_cycle(combat_tracker, boss_obj, player_obj, method):
    hit_list, total_damage = [], 0
    player_alive, boss_alive = True, True

    # Check stun cycles/recovery.
    if combat_tracker.stun_cycles > 0:
        combat_tracker.stun_cycles -= 1
        battle_msg = (f"{player_obj.player_username} is {combat_tracker.status_type}! "
                      f"Duration: {combat_tracker.stun_cycles} cycles")
        if combat_tracker.stun_cycles == 0:
            battle_msg = f"{player_obj.player_username} has recovered from {combat_tracker.status_recovery}!"
            if combat_tracker.status_type == "stunned":
                combat_tracker.player_cHP = player_obj.player_mHP
            status_type = ""
        return hit_list, battle_msg, player_alive, boss_alive, total_damage
    # The boss takes action.
    player_alive, boss_action_msg = handle_boss_action(combat_tracker, boss_obj, player_obj)
    if not player_alive:
        combat_tracker.hp_regen = 0
        battle_msg = f"{player_obj.player_username} has been felled!"
        return hit_list, battle_msg, player_alive, boss_alive, total_damage
    # The player takes action.
    combat_tracker.player_cHP = min(player_obj.player_mHP, combat_tracker.hp_regen + combat_tracker.player_cHP)
    combo_count, hits_per_cycle = 1 + player_obj.combo_application, int(player_obj.attack_speed)
    combat_tracker.remaining_hits += player_obj.attack_speed - hits_per_cycle
    while combat_tracker.remaining_hits >= 1:
        hits_per_cycle += 1
        combat_tracker.remaining_hits -= 1
    for x in range(hits_per_cycle):
        hit_list.append(hit_boss(combat_tracker, boss_obj, player_obj, combo_count))
        combo_count += 1
        combat_tracker.charges += player_obj.ultimate_application
        if combat_tracker.charges >= 20:
            combat_tracker.charges -= 20
            hit_list.append(hit_boss(combat_tracker, boss_obj, player_obj, combo_count, hit_type="Ultimate"))
            for b in range(player_obj.bleed_application):
                hit_list.append(trigger_bleed_boss(combat_tracker, boss_obj, player_obj, hit_type="Ultimate"))
        if not boss_obj.calculate_hp():
            boss_alive = False
            break
    for b in range(player_obj.bleed_application):
        hit_list.append(trigger_bleed_boss(combat_tracker, boss_obj, player_obj))

    # Compile messages
    total_damage = sum(hit[0] for hit in hit_list)
    combat_tracker.total_dps += total_damage
    battle_msg = f"{player_obj.player_username} - [HP: {sharedmethods.display_hp(combat_tracker.player_cHP, player_obj.player_mHP)}]"
    battle_msg += f" - [Recovery: {combat_tracker.recovery}]"
    if method == "Solo":
        battle_msg = f"{boss_action_msg}{battle_msg}"
    return hit_list, battle_msg, player_alive, boss_alive, total_damage


def handle_boss_action(combat_tracker, boss_obj, player_obj):
    boss_msg = ""
    is_alive = True
    if boss_obj.boss_type_num >= 1:
        # Handle boss attacks.
        boss_element = boss_obj.boss_element if boss_obj.boss_element != 9 else random.randint(0, 8)
        specific_key = [key for key in boss_attack_exceptions if key in boss_obj.boss_name]
        if specific_key:
            skill_list = boss_attack_dict[specific_key[0]]
        else:
            skill_list = boss_attack_dict[boss_obj.boss_type]
        target_index = random.randint(0, len(skill_list) - 1)
        skill = skill_list[target_index]
        if "[ELEMENT]" in skill:
            skill = skill.replace("[ELEMENT]", globalitems.element_special_names[boss_element])
        base_set = [100, 100] if "_" in skill else [25, 50]
        bypass_immortal = True if "**" in skill else False
        skill_bonus = skill_multiplier_list[target_index]
        # Handle boss enrage.
        if boss_obj.boss_type_num >= 2 and boss_obj.boss_cHP <= int(boss_obj.boss_mHP / 2):
            base_set = [2 * value for value in base_set]
        damage_set = [base_set[0] * boss_obj.boss_level * skill_bonus, base_set[1] * boss_obj.boss_level * skill_bonus]
        is_alive, damage = take_combat_damage(player_obj, combat_tracker, damage_set, boss_element, bypass_immortal)
        boss_msg += f"{boss_obj.boss_name} uses {skill} dealing {sharedmethods.number_conversion(damage)} damage!\n"
    # Handle boss regen.
    if boss_obj.boss_type_num >= 3:
        boss_healing = int(0.001 * boss_obj.boss_tier * boss_obj.boss_mHP)
        boss_obj.boss_cHP += boss_healing
        if boss_obj.boss_cHP >= boss_obj.boss_mHP:
            boss_obj.boss_cHP = boss_obj.boss_mHP
        boss_msg += f"{boss_obj.boss_name} regenerated 0.{boss_obj.boss_tier}% HP!\n"
    return is_alive, boss_msg


def take_combat_damage(player_obj, combat_tracker, damage_set, dmg_element, bypass_immortal):
    damage = random.randint(damage_set[0], damage_set[1])
    player_resist = 0
    if dmg_element != -1:
        player_resist = player_obj.elemental_resistance[dmg_element]
    damage -= damage * player_resist
    damage -= damage * player_obj.damage_mitigation * 0.01
    damage = int(damage)
    combat_tracker.player_cHP -= damage
    if combat_tracker.player_cHP > 0:
        return True, damage
    if player_obj.immortal and not bypass_immortal:
        combat_tracker.player_cHP = 1
        return True, damage
    if combat_tracker.recovery > 0:
        combat_tracker.player_cHP = 0
        combat_tracker.recovery -= 1
        combat_tracker.stun_cycles = max(1, 10 - player_obj.recovery)
        combat_tracker.status_type,  combat_tracker.status_recovery = "stunned", "stun"
        return True, damage
    return False, damage


def hit_boss(combat_tracker, boss_obj, player_obj, combo_count, hit_type="Regular"):
    extension = ""
    update_bleed(combat_tracker, player_obj)
    hit_damage, critical_type = player_obj.get_player_boss_damage(boss_obj)
    damage, skill_name = skill_adjuster(player_obj, combat_tracker, hit_damage, combo_count, (hit_type == "Ultimate"))
    if damage >= boss_obj.damage_cap != -1:
        damage = boss_obj.damage_cap
        extension = " *LIMIT*"
    damage, status_msg = check_lock(player_obj, combat_tracker, damage)
    damage, second_msg = check_bloom(player_obj, damage)
    hit_msg = f"{combo_count}x Combo: {skill_name} {sharedmethods.number_conversion(damage)}{extension}"
    if hit_type == "Ultimate":
        hit_msg = f"Ultimate: {skill_name} {sharedmethods.number_conversion(damage)}{extension}"
    hit_msg += f"{status_msg}{second_msg}{critical_type}"
    boss_obj.boss_cHP -= damage
    return [damage, hit_msg]


def trigger_bleed_boss(combat_tracker, boss_obj, player_obj, hit_type="Normal"):
    extension = ""
    hit_multiplier = 1.5 if hit_type == "Ultimate" else 0.75
    damage = hit_multiplier * player_obj.get_bleed_damage(boss_obj)
    damage = int(damage * combat_tracker.bleed_tracker)
    damage, bleed_type = check_hyper_bleed(player_obj, damage)
    if damage >= boss_obj.damage_cap != -1:
        damage = boss_obj.damage_cap
        extension = " *LIMIT*"
    keyword = "Sanguine" if hit_type == "Ultimate" else "Blood"
    bleed_msg = f"{keyword} Rupture: {sharedmethods.number_conversion(damage)}{extension} *{bleed_type}*"
    damage = int(damage * (1 + player_obj.bleed_penetration))
    boss_obj.boss_cHP -= damage
    return [damage, bleed_msg]


def update_bleed(combat_tracker, player_obj):
    if player_obj.bleed_application <= 0:
        return
    combat_tracker.bleed_tracker += 0.05 * player_obj.bleed_application
    if combat_tracker.bleed_tracker >= 1:
        combat_tracker.bleed_tracker = 1


def run_solo_cycle(combat_tracker, boss_obj, player_obj):
    hit_list, battle_msg, player_alive, boss_alive, total_damage = run_cycle(combat_tracker, boss_obj, player_obj,
                                                                             "Solo")
    combat_tracker.total_cycles += 1
    total_dps = int(combat_tracker.total_dps / combat_tracker.total_cycles)
    embed_msg = boss_obj.create_boss_embed(total_dps)
    embed_msg.add_field(name="", value=battle_msg, inline=False)
    if not boss_alive:
        embed_msg = boss_obj.create_boss_embed(total_dps)
        if boss_obj.boss_tier >= 4:
            quest.assign_unique_tokens(player_obj, boss_obj.boss_name)
    hit_field = ""
    for hit in hit_list:
        hit_field += f"{hit[1]}\n"
        if hit[0] > combat_tracker.highest_damage:
            combat_tracker.highest_damage = hit[0]
    embed_msg.add_field(name="", value=hit_field, inline=False)
    return embed_msg, player_alive


def run_raid_cycle(combat_tracker, boss_obj, player_obj):
    hit_list, battle_msg, player_alive, boss_alive, total_damage = run_cycle(combat_tracker, boss_obj, player_obj,
                                                                             "Raid")
    combat_tracker.total_cycles += 1
    if not boss_alive and boss_obj.boss_tier >= 4:
        quest.assign_unique_tokens(player_obj, boss_obj.boss_name)
    player_msg = battle_msg
    if total_damage != 0 and player_alive:
        player_msg = f"{battle_msg} - dealt {sharedmethods.number_conversion(total_damage)} damage!"
    return player_msg, total_damage


def check_bloom(player_obj, input_damage):
    status_msg = ""
    damage = input_damage
    random_num = random.randint(1, 100)
    if random_num <= int(round(player_obj.specialty_rate[0] * 100)):
        damage = int(damage * player_obj.bloom_multiplier)
        status_msg = " *BLOOM*"
    return damage, status_msg


def check_lock(player_obj, combat_tracker, damage):
    status_msg = ""
    if combat_tracker.time_lock == 0:
        lock_rate = 5 * player_obj.temporal_application + int(round(player_obj.specialty_rate[4] * 100))
        random_lock_chance = random.randint(1, 100)
        if random_lock_chance <= lock_rate:
            if player_obj.unique_glyph_ability[6]:
                damage *= damage * (player_obj.temporal_application + 1)
                status_msg = " *TIME SHATTER*"
            else:
                combat_tracker.time_lock = player_obj.temporal_application + 1
                status_msg = " *TIME LOCK*"
    elif combat_tracker.time_lock > 0:
        combat_tracker.time_lock -= 1
        combat_tracker.time_damage += damage
        if combat_tracker.time_lock == 0:
            damage = combat_tracker.time_damage * (player_obj.temporal_application + 1)
            combat_tracker.time_damage = 0
            status_msg = " TIME SHATTER"
        else:
            damage = 0
            status_msg = " LOCKED"
    return damage, status_msg


def boss_defences(method, player_obj, boss_object, location):
    type_multiplier = (1 - 0.05 * boss_object.boss_tier)
    if method == "Element":
        if boss_object.boss_eleweak[location] == 1:
            type_multiplier = 1
            curse_penalty = boss_object.curse_debuffs[location]
            type_multiplier += curse_penalty
    else:
        location = globalitems.class_names.index(player_obj.player_class)
        if boss_object.boss_typeweak[location] == 1:
            type_multiplier = 1
    return type_multiplier


def boss_true_mitigation(boss_level):
    a, b, c = 1, 0.5, 0.1
    return a - (a - b) * boss_level / 99 if boss_level <= 99 else b - (b - c) * (boss_level - 100) / 899


def critical_check(player_obj, player_damage, num_elements):
    # Critical hits
    random_num = random.randint(1, 100)
    if random_num <= (player_obj.elemental_application * 5 + int(round(player_obj.specialty_rate[3] * 100))):
        player_damage *= num_elements
        critical_type = " *FRACTA*L"
    elif random_num < player_obj.critical_chance:
        player_damage *= (1 + player_obj.critical_multiplier)
        omega_chance = player_obj.critical_application * 3 + int(round(player_obj.specialty_rate[2] * 100))
        omega_check = random.randint(1, 100)
        if omega_check <= omega_chance:
            critical_type = " *OMEGA CRITICAL*"
            player_damage *= (1 + player_obj.critical_multiplier)
        else:
            critical_type = " *CRITICAL*"
        player_damage *= (1 + player_obj.critical_penetration)
    else:
        critical_type = ""
    return player_damage, critical_type


def skill_adjuster(player_obj, combat_tracker, hit_damage, combo_count, is_ultimate):
    class_skill_list = globalitems.skill_names_dict[player_obj.player_class]
    combo_multiplier = (1 + (player_obj.combo_multiplier * combo_count)) * (1 + player_obj.combo_penetration)
    if is_ultimate:
        ultimate_multiplier = (1 + player_obj.ultimate_multiplier) * (1 + player_obj.ultimate_penetration)
        damage = int(hit_damage * combo_multiplier * ultimate_multiplier * (2 + player_obj.skill_base_damage_bonus[3]))
        skill_name = class_skill_list[3]
        charges_gained = -20
    elif combo_count < 3:
        damage = int(hit_damage * combo_multiplier * (0.5 + player_obj.skill_base_damage_bonus[0]))
        skill_name = class_skill_list[0]
        charges_gained = 1 + player_obj.charge_generation
    elif combo_count < 5:
        damage = int(hit_damage * combo_multiplier * (0.75 + player_obj.skill_base_damage_bonus[1]))
        skill_name = class_skill_list[1]
        charges_gained = 1 + player_obj.charge_generation
    else:
        damage = int(hit_damage * combo_multiplier * (1 + player_obj.skill_base_damage_bonus[2]))
        skill_name = class_skill_list[2]
        charges_gained = 1 + player_obj.charge_generation
    if not is_ultimate and player_obj.unique_glyph_ability[3]:
        ultimate_multiplier = (1 + player_obj.ultimate_multiplier) * (1 + player_obj.ultimate_penetration)
        damage = int(hit_damage * ultimate_multiplier)
    combat_tracker.charges += charges_gained

    return damage, skill_name


def pvp_defences(attacker, defender, player_damage, e_weapon):
    # Type Defences
    adjusted_damage = player_damage - defender.damage_mitigation * 0.01 * player_damage
    # Elemental Defences
    if attacker.elemental_capacity < 9:
        temp_element_list = limit_elements(attacker, e_weapon)
    else:
        temp_element_list = e_weapon.item_elements.copy()
    for idx, x in enumerate(temp_element_list):
        if x == 1:
            attacker.elemental_damage[idx] = adjusted_damage * (1 + attacker.elemental_multiplier[idx])
            resist_multi = 1 - defender.elemental_resistance[idx]
            penetration_multi = 1 + attacker.elemental_penetration[idx]
            attacker.elemental_damage[idx] *= resist_multi * penetration_multi * attacker.elemental_conversion[idx]
    subtotal_damage = sum(attacker.elemental_damage) * (1 + attacker.aura) * (1 + attacker.banes[5])
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


def check_hyper_bleed(player_obj, bleed_damage):
    hyper_bleed_rate = player_obj.bleed_application * 5 + int(round(player_obj.specialty_rate[1] * 100))
    bleed_check = random.randint(1, 100)
    bleed_type = "BLEED"
    if bleed_check <= hyper_bleed_rate:
        bleed_type = "HYPERBLEED"
        bleed_damage *= (1 + player_obj.bleed_multiplier)
    return int(bleed_damage), bleed_type


def get_random_opponent(player_echelon):
    player_list = player.get_players_by_echelon(player_echelon)
    opponent_object = random.choice(player_list) if player_list else None
    return opponent_object


def check_flag(player_obj):
    is_flagged = False
    pandora_db = mydb.start_engine()
    raw_query = "SELECT * FROM AbandonEncounter WHERE player_id = :player_check"
    df = pandora_db.run_query(raw_query, True, params={'player_check': int(player_obj.player_id)})
    if len(df) != 0:
        is_flagged = True
    pandora_db.close_engine()
    return is_flagged


def toggle_flag(player_obj):
    player_id = int(player_obj.player_id)
    pandora_db = mydb.start_engine()
    # Check if a flag exists
    check_query = "SELECT * FROM AbandonEncounter WHERE player_id = :player_check"
    df = pandora_db.run_query(check_query, True, params={'player_check': player_id})
    if len(df) != 0:
        delete_query = "DELETE FROM AbandonEncounter WHERE player_id = :player_check"
        pandora_db.run_query(delete_query, params={'player_check': player_id})
    else:
        insert_query = "INSERT INTO AbandonEncounter (player_id) VALUES (:player_check)"
        pandora_db.run_query(insert_query, params={'player_check': player_id})
    pandora_db.close_engine()


def limit_elements(player_obj, e_weapon):
    elemental_breakdown = []
    temp_list = e_weapon.item_elements.copy()
    if player_obj.elemental_capacity == 9:
        return temp_list
    for x, is_used in enumerate(temp_list):
        if is_used:
            temp_total = player_obj.elemental_multiplier[x] * player_obj.elemental_penetration[x]
            temp_total *= player_obj.elemental_curse[x]
            elemental_breakdown.append([x, temp_total])
    sorted_indices = sorted(elemental_breakdown, key=lambda e: e[1], reverse=True)
    damage_limitation = [idx for idx, _ in sorted_indices[:player_obj.elemental_capacity]]
    for i in [i for i in range(len(temp_list)) if i not in damage_limitation]:
        temp_list[i] = 0
    return temp_list
