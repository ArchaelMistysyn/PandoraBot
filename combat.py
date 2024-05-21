# General imports
import random

# Data imports
import globalitems
import sharedmethods

# Core imports
import player
import quest
import inventory
from pandoradb import run_query as rq


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
        self.total_cycles = 0
        self.stun_cycles, self.stun_status = 0, ""
        self.time_lock, self.time_damage = 0, 0
        self.bleed_tracker = 0.0


async def run_cycle(tracker_obj, boss_obj, player_obj, method):
    hit_list, total_damage = [], 0
    player_alive, boss_alive = True, True
    # Step 1: Check and handle status effects
    status_effects_result = handle_status(tracker_obj, player_obj)
    if status_effects_result is not None:
        return hit_list, status_effects_result, player_alive, boss_obj.calculate_hp(), total_damage
    # Step 2: Boss takes action
    player_alive, boss_action_msg = handle_boss_actions(boss_obj, tracker_obj, player_obj)
    if not player_alive:
        tracker_obj.hp_regen = 0
        battle_msg = f"{player_obj.player_username} has been felled!"
        player_obj.update_misc_data("deaths", 1)
        return hit_list, battle_msg, player_alive, boss_alive, total_damage
    # Step 3: Player takes action
    hit_list = await handle_player_actions(hit_list, tracker_obj, boss_obj, player_obj)
    # Step 4: Handle Cyclic DoT
    if player_obj.bleed_app > 0:
        hit_list.append(await trigger_bleed(tracker_obj, player_obj, boss_obj=boss_obj))
    # Step 5: Compile final battle message and return results
    total_damage = sum(hit[0] for hit in hit_list)
    tracker_obj.total_dps += total_damage
    battle_msg = f"{player_obj.player_username} - [HP: {sharedmethods.display_hp(tracker_obj.player_cHP, player_obj.player_mHP)}]"
    battle_msg += f" - [Recovery: {tracker_obj.recovery}]"
    battle_msg = f"{boss_action_msg}{battle_msg}" if method == "Solo" else battle_msg
    # Check again if boss is dead.
    return hit_list, battle_msg, player_alive, boss_obj.calculate_hp(), total_damage


def handle_status(tracker_obj, player_obj):
    if tracker_obj.stun_cycles <= 0:
        return None
    tracker_obj.stun_cycles -= 1
    battle_msg = f"{player_obj.player_username} is {tracker_obj.stun_status}! Duration: {tracker_obj.stun_cycles} cycles."
    if tracker_obj.stun_cycles == 0 and tracker_obj.stun_status != "":
        battle_msg = f"{player_obj.player_username} has recovered from being {tracker_obj.stun_status}!"
        tracker_obj.player_cHP = player_obj.player_mHP if tracker_obj.stun_status == "stunned" else tracker_obj.player_cHP
        tracker_obj.stun_status = ""
    return battle_msg


def handle_boss_actions(boss_obj, tracker_obj, player_obj):
    is_alive, boss_msg = True, ""
    # Handle Boss Status
    if boss_obj.stun_cycles > 0:
        tracker_obj.stun_cycles -= 1
        boss_msg = f"{boss_obj.boss_name} is {boss_obj.stun_status}! Duration: {boss_obj.stun_cycles} cycles.\n"
        if boss_obj.stun_cycles == 0:
            boss_msg = f"{boss_obj.boss_name} has recovered from being {boss_obj.stun_status}!"
        return is_alive, boss_msg

    if boss_obj.boss_type_num == 0:
        return is_alive, boss_msg
        # Handle boss attacks.
    boss_element = boss_obj.boss_element if boss_obj.boss_element != 9 else random.randint(0, 8)
    specific_key = [key for key in boss_attack_exceptions if key in boss_obj.boss_name]
    skill_list = boss_attack_dict[specific_key[0]] if specific_key else boss_attack_dict[boss_obj.boss_type]
    target_index = random.randint(0, len(skill_list) - 1)
    skill = skill_list[target_index]
    if "[ELEMENT]" in skill:
        skill = skill.replace("[ELEMENT]", globalitems.element_special_names[boss_element])
    base_set = [100, 100] if "_" in skill else [25, 50]
    bypass1 = True if "_" in skill else False
    bypass2 = True if "**" in skill else False
    skill_bonus = skill_multiplier_list[target_index]
    # Handle boss enrage.
    if boss_obj.boss_type_num >= 2 and boss_obj.boss_cHP <= int(boss_obj.boss_mHP / 2):
        base_set = [2 * value for value in base_set]
    damage_set = [base_set[0] * boss_obj.boss_level * skill_bonus, base_set[1] * boss_obj.boss_level * skill_bonus]
    damage_set, _ = handle_evasions(player_obj.block, player_obj.dodge, damage_set, bypass1=bypass1, bypass2=bypass2)
    is_alive, damage = take_combat_damage(player_obj, tracker_obj, damage_set, boss_element, bypass2)
    boss_msg += f"{boss_obj.boss_name} uses {skill} dealing {sharedmethods.number_conversion(damage)} damage!\n"
    # Handle boss regen.
    if boss_obj.boss_type_num < 3:
        return is_alive, boss_msg
    boss_obj.boss_cHP += int(0.001 * boss_obj.boss_tier * boss_obj.boss_mHP)
    boss_obj.boss_cHP = boss_obj.boss_mHP if boss_obj.boss_cHP >= boss_obj.boss_mHP else boss_obj.boss_cHP
    boss_msg += f"{boss_obj.boss_name} regenerated 0.{boss_obj.boss_tier}% HP!\n"
    return is_alive, boss_msg


async def handle_player_actions(hit_list, tracker_obj, boss_obj, player_obj):
    regen_value = tracker_obj.hp_regen if tracker_obj.player_cHP != 0 else 0
    tracker_obj.player_cHP = min(player_obj.player_mHP, regen_value + tracker_obj.player_cHP)
    combo_count, hits_per_cycle = 1 + player_obj.combo_application, int(player_obj.attack_speed)
    tracker_obj.remaining_hits += player_obj.attack_speed - hits_per_cycle
    while tracker_obj.remaining_hits >= 1:
        hits_per_cycle += 1
        tracker_obj.remaining_hits -= 1
    # Handle all hits
    for x in range(hits_per_cycle):
        hit_list.append(await hit_boss(tracker_obj, boss_obj, player_obj, combo_count))
        combo_count += 1
        tracker_obj.charges += player_obj.ultimate_app
        # Handle Ultimate
        if tracker_obj.charges >= 20:
            hit_list.append(await hit_boss(tracker_obj, boss_obj, player_obj, combo_count, hit_type="Ultimate"))
            if player_obj.bleed_app > 0:
                hit_list.append(await trigger_bleed(tracker_obj, player_obj, hit_type="Ultimate", boss_obj=boss_obj))
        # Stop iterating if boss dies
        if not boss_obj.calculate_hp():
            return hit_list
    return hit_list


def take_combat_damage(player_obj, tracker_obj, damage_set, dmg_element, bypass_immortal, no_trigger=False):
    damage = random.randint(damage_set[0], damage_set[1])
    player_resist = 0
    if dmg_element != -1:
        player_resist = player_obj.elemental_resistance[dmg_element]
        if (tracker_obj.stun_status != "stunned" and random.randint(1, 100) <= 1 and
                globalitems.element_status_list[dmg_element] is not None):
            tracker_obj.stun_status = globalitems.element_status_list[dmg_element]
            tracker_obj.stun_cycles += 1
    damage -= damage * player_resist
    damage = int(damage - (damage * player_obj.damage_mitigation * 0.01))
    tracker_obj.player_cHP -= damage
    if tracker_obj.player_cHP > 0:
        return True, damage
    if player_obj.immortal and not bypass_immortal:
        tracker_obj.player_cHP = 1
        return True, damage
    if tracker_obj.recovery > 0:
        tracker_obj.player_cHP = 0
        tracker_obj.recovery -= 1
        tracker_obj.stun_cycles, tracker_obj.stun_status = max(1, 10 - player_obj.recovery), "stunned"
        return True, damage
    return False, damage


async def hit_boss(tracker_obj, boss_obj, player_obj, combo_count, hit_type="Regular"):
    update_bleed(tracker_obj, player_obj)
    hit_damage, critical_type = await player_obj.get_player_boss_damage(boss_obj)
    damage, skill_name = skill_adjuster(player_obj, tracker_obj, hit_damage, combo_count, (hit_type == "Ultimate"))
    damage, status_msg = check_lock(player_obj, tracker_obj, damage)
    damage, second_msg = check_bloom(player_obj, damage)
    damage, extension = (boss_obj.damage_cap, " *LIMIT*") if damage >= boss_obj.damage_cap != -1 else (damage, "")
    if status_msg == " *TIME SHATTER*" or critical_type != "":
        damage *= random.randint(1, max(1, player_obj.rng_bonus))
    hit_msg = f"{combo_count}x Combo: {skill_name} {sharedmethods.number_conversion(damage)}{extension}"
    if hit_type == "Ultimate":
        hit_msg = f"Ultimate: {skill_name} {sharedmethods.number_conversion(damage)}{extension}"
    hit_msg += f"{status_msg}{second_msg}{critical_type}"
    boss_obj.boss_cHP -= damage
    return [damage, hit_msg]


async def trigger_bleed(tracker_obj, player_obj, hit_type="Normal", boss_obj=None, pvp_data=None):
    bleed_dict = {1: "Single", 2: "Double", 3: "Triple", 4: "Quadra", 5: "Penta"}
    hit_multiplier, keyword = (1.5, "Sanguine") if hit_type == "Ultimate" else (0.75, "Blood")
    count = "Zenith" if player_obj.bleed_app > 5 else bleed_dict[player_obj.bleed_app]
    # Calculate damage
    damage = pvp_data[2] if pvp_data is not None else int(hit_multiplier * await player_obj.get_bleed_damage(boss_obj))
    damage *= tracker_obj.bleed_tracker
    damage, bleed_type = check_hyper_bleed(player_obj, damage)
    damage = int(damage * (1 + player_obj.bleed_penetration))
    # Handle application scaling
    for b in range(player_obj.bleed_app):
        damage += damage
    # Determine boss or pvp specific damage adjustments.
    if boss_obj is not None:
        damage, extension = (boss_obj.damage_cap, " *LIMIT*") if damage >= boss_obj.damage_cap != -1 else (damage, "")
        boss_obj.boss_cHP -= damage
    else:
        damage, extension = pvp_scale_damage(*pvp_data), ""
    bleed_msg = f"{keyword} Rupture [{count}]: {sharedmethods.number_conversion(damage)}{extension} *{bleed_type}*"
    return [damage, bleed_msg]


def check_hyper_bleed(player_obj, bleed_damage):
    hyper_bleed_rate = player_obj.bleed_app * 5 + int(round(player_obj.spec_rate[1] * 100))
    bleed_type = "BLEED"
    if random.randint(1, 100) <= hyper_bleed_rate:
        bleed_type = "HYPERBLEED"
        bleed_damage *= (1 + player_obj.bleed_mult)
    return int(bleed_damage), bleed_type


def update_bleed(tracker_obj, player_obj):
    if player_obj.bleed_app <= 0:
        return
    tracker_obj.bleed_tracker += 0.05 * player_obj.bleed_app
    tracker_obj.bleed_tracker = min(1, tracker_obj.bleed_tracker)


async def run_solo_cycle(tracker_obj, boss_obj, player_obj):
    hit_list, battle_msg, player_alive, boss_alive, total_damage = await run_cycle(tracker_obj, boss_obj, player_obj, "Solo")
    tracker_obj.total_cycles += 1
    total_dps = int(tracker_obj.total_dps / tracker_obj.total_cycles)
    embed_msg = boss_obj.create_boss_embed(total_dps)
    embed_msg.add_field(name="", value=battle_msg, inline=False)
    if not boss_alive:
        embed_msg = boss_obj.create_boss_embed(total_dps)
    hit_field = ""
    for hit in hit_list:
        hit_field += f"{hit[1]}\n"
        if hit[0] > tracker_obj.highest_damage:
            tracker_obj.highest_damage = hit[0]
    embed_msg.add_field(name="", value=hit_field, inline=False)
    return embed_msg, player_alive, boss_alive


async def run_raid_cycle(tracker_obj, boss_obj, player_obj):
    hit_list, battle_msg, player_alive, boss_alive, total_damage = await run_cycle(tracker_obj, boss_obj, player_obj, "Raid")
    tracker_obj.total_cycles += 1
    if not boss_alive and boss_obj.boss_tier >= 4:
        quest.assign_unique_tokens(player_obj, boss_obj.boss_name)
    player_msg = battle_msg
    if total_damage != 0 and player_alive:
        player_msg = f"{battle_msg} - dealt {sharedmethods.number_conversion(total_damage)} damage!"
    return player_msg, total_damage


def check_bloom(player_obj, input_damage):
    damage, status_msg = input_damage, ""
    if random.randint(1, 100) <= int(round(player_obj.spec_rate[0] * 100)):
        damage, status_msg = int(damage * player_obj.bloom_multiplier), " *BLOOM*"
        if random.randint(1, 100) <= int(round(player_obj.spec_conv[0] * 10)):
            damage, status_msg = damage * 10, " *SACRED BLOOM*"
    elif random.randint(1, 100) <= int(round(player_obj.spec_conv[1] * 100)):
        damage, status_msg = int(damage * player_obj.bloom_multiplier * 3), " *ABYSSAL BLOOM*"
    elif random.randint(1, 100) <= int(round(player_obj.spec_conv[2] * 100)):
        damage, status_msg = int(damage * 9.99), " *CALAMITY*"
    return damage, status_msg


def check_lock(player_obj, combat_tracker, damage):
    status_msg = ""
    # Create a new time lock.
    if combat_tracker.time_lock == 0:
        lock_rate = 5 * player_obj.temporal_app + int(round(player_obj.spec_rate[4] * 100))
        if random.randint(1, 100) > lock_rate:
            return damage, status_msg
        combat_tracker.time_lock = player_obj.temporal_app + 1
        status_msg = " *TIME LOCK*"
    # Handle existing time lock.
    elif combat_tracker.time_lock > 0:
        combat_tracker.time_lock -= 1
        combat_tracker.time_damage += damage
        # Trigger time shatter.
        if combat_tracker.time_lock == 0:
            damage = combat_tracker.time_damage * (player_obj.temporal_app + 1)
            combat_tracker.time_damage = 0
            return damage, " *TIME SHATTER*"
        damage, status_msg = 0, " *LOCKED*"
    return damage, status_msg


def handle_evasions(block_rate, dodge_rate, damage, bypass1=False, bypass2=False):
    damage_set = [damage, damage] if not isinstance(damage, list) else damage
    if not bypass1 and not bypass2 and random.randint(1, 100) <= dodge_rate:
        damage_set = [0, 0]
        return (damage_set[0], " **DODGE**") if not isinstance(damage, list) else (damage_set, " **DODGE**")
    elif not bypass2 and random.randint(1, 100) <= block_rate:
        damage_set = [int(damage_set[0] / 2), int(damage_set[1] / 2)]
        return (damage_set[0], " **BLOCK**") if not isinstance(damage, list) else (damage_set, " **BLOCK**")
    return (damage_set[0], "") if not isinstance(damage, list) else (damage_set, "")


def boss_defences(method, player_obj, boss_object, location):
    mult = (1 - 0.05 * boss_object.boss_tier)
    if method == "Element":
        return 1 + boss_object.curse_debuffs[location] if boss_object.boss_eleweak[location] == 1 else mult
    else:
        return 1 if boss_object.boss_typeweak[globalitems.class_names.index(player_obj.player_class)] == 1 else mult


def boss_true_mitigation(boss_level):
    a, b, c = 1, 0.5, 0.1
    return a - (a - b) * boss_level / 99 if boss_level <= 99 else b - (b - c) * (boss_level - 100) / 899


def critical_check(player_obj, player_damage, num_elements):
    critical_type, critical_roll = "", random.randint(1, 100)
    # Check for fractal type critical.
    if critical_roll <= (player_obj.elemental_app * 5 + int(round(player_obj.spec_rate[3] * 100))):
        player_damage *= num_elements
        critical_type = " *FRACTAL*"
    # Check for regular critical.
    elif critical_roll < player_obj.critical_chance:
        player_damage *= (1 + player_obj.critical_multiplier)
        critical_type = " *CRITICAL*"
        # Check for omega critical.
        if random.randint(1, 100) <= player_obj.critical_app * 3 + int(round(player_obj.spec_rate[2] * 100)):
            critical_type = " *OMEGA CRITICAL*"
            player_damage *= (1 + player_obj.critical_multiplier)
        player_damage *= (1 + player_obj.critical_penetration)
    return player_damage, critical_type


def skill_adjuster(player_obj, combat_tracker, hit_damage, combo_count, is_ultimate):
    mult_dict = {0: 0.5, 1: 0.75, 2: 1, 3: 2}
    combo_mult = (1 + (player_obj.combo_mult * combo_count)) * (1 + player_obj.combo_penetration)
    ultimate_mult = (1 + player_obj.ultimate_mult) * (1 + player_obj.ultimate_penetration)
    skill_list = globalitems.skill_names_dict[player_obj.player_class]
    if player_obj.aqua_points >= 100:
        skill_list = ["Sea of Subjugation", "Ocean of Oppression", "Deluge of Domination", "Tides of Annihilation"]
        mult_dict = {0: 1, 1: 1.5, 2: 2, 3: 5}
    if is_ultimate:
        combat_tracker.charges -= 20
        damage = int(hit_damage * combo_mult * ultimate_mult * (mult_dict[3] + player_obj.skill_damage_bonus[3]))
        return damage, skill_list[3]
    # Handle non-ultimates.
    index = 0 if combo_count < 3 else 1 if combo_count < 5 else 2
    damage = int(hit_damage * combo_mult * (mult_dict[index] + player_obj.skill_damage_bonus[index]))
    if player_obj.unique_glyph_ability[3]:
        damage = int(hit_damage * ultimate_mult)
    combat_tracker.charges += 1 + player_obj.charge_generation
    return damage, skill_list[index]


def pvp_defences(attacker, defender, player_damage, e_weapon):
    # Type Defences
    adjusted_damage = player_damage - defender.damage_mitigation * 0.01 * player_damage
    # Elemental Defences
    temp_ele = limit_elements(attacker, e_weapon) if attacker.elemental_capacity < 9 else e_weapon.item_elements.copy()
    highest = 0
    for idx, x in enumerate(temp_ele):
        if x == 1:
            attacker.elemental_damage[idx] = adjusted_damage * (1 + attacker.elemental_multiplier[idx])
            resist_multi = 1 - defender.elemental_resistance[idx]
            penetration_multi = 1 + attacker.elemental_penetration[idx]
            attacker.elemental_damage[idx] *= resist_multi * penetration_multi * attacker.elemental_conversion[idx]
            if attacker.elemental_damage[idx] > attacker.elemental_damage[highest]:
                highest = idx
    stun_status = globalitems.element_status_list[highest]
    stun_status = stun_status if (stun_status is not None and random.randint(1, 100) <= 1) else None
    return stun_status, int(sum(attacker.elemental_damage) * (1 + attacker.aura) * (1 + attacker.banes[5]))


async def pvp_attack(attacker, defender):
    e_weapon = await inventory.read_custom_item(attacker.player_equipped[0])
    num_elements = sum(e_weapon.item_elements)
    player_damage = attacker.get_player_initial_damage()
    player_damage, critical_type = critical_check(attacker, player_damage, num_elements)
    stun_status, player_damage = pvp_defences(attacker, defender, player_damage, e_weapon)
    return stun_status, player_damage, critical_type


def pvp_scale_damage(role_order, combatants, hit_damage):
    attacker, defender = role_order[0], role_order[1]
    reduction = (combatants[defender].player_mHP // 500) * 0.002
    damage = (len(str(hit_damage)) - 1) * 0.02
    string_damage = str(hit_damage)
    first_number = int(string_damage[0])
    damage = max(0.01, damage + (first_number * 0.001) - reduction)
    scaled_damage = int(combatants[defender].player_mHP * damage)
    return scaled_damage


async def get_random_opponent(player_echelon):
    player_list = await player.get_players_by_echelon(player_echelon)
    opponent_object = random.choice(player_list) if player_list else None
    return opponent_object


def check_flag(player_obj):
    raw_query = "SELECT * FROM AbandonEncounter WHERE player_id = :player_check"
    df = rq(raw_query, return_value=True, params={'player_check': int(player_obj.player_id)})
    return True if df is not None and len(df) != 0 else False


def toggle_flag(player_obj):
    player_id = int(player_obj.player_id)
    # Check if a flag exists
    check_query = "SELECT * FROM AbandonEncounter WHERE player_id = :player_check"
    df = rq(check_query, return_value=True, params={'player_check': player_id})
    if len(df) != 0:
        toggle_query = "DELETE FROM AbandonEncounter WHERE player_id = :player_check"
    else:
        toggle_query = "INSERT INTO AbandonEncounter (player_id) VALUES (:player_check)"
    rq(toggle_query, params={'player_check': player_id})


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
