# General imports
import random
import math

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import player
import quest
import inventory
from pandoradb import run_query as rqy

combat_command_list = [("solo", "Type Options: [Random/Fortress/Dragon/Demon/Paragon/Arbiter]. Stamina Cost: 200", 0),
                       ("summon", "Consume a summoning item to summon a high tier boss. Options [1-3]", 1),
                       ("gauntlet", "Challenge the gauntlet in the Spire of Illusions.", 2),
                       ("palace", "Enter the Divine Palace. [WARNING: HARD]", 3),
                       ("arena", "Enter pvp combat with another player. Daily", 4),
                       ("abandon", "Abandon an active solo boss encounter. 1 Minute delay.", 5)]

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
    "Nephilim, Incarnate of the Divine Lotus":
        ["Lotus Slash", "Propagate Ruin", "Divine Purgation", "Chaos Bloom", "**Sacred Revelation**",
         "**Eye Of The Annihilator**", "**Nightmare Saber**", "**__Fabricate Apotheosis__**"],
    "Geb, Sacred Ruler of Sin": ["Skill1", "Skil2", "Skill3", "Skill4", "**Skill5**",
                                 "**Skill6**", "**Skill7**", "**Skill8**", "**__Skill9__**"],
    "Tiamat, Sacred Ruler of Fury": ["Skill1", "Skil2", "Skill3", "Skill4", "**Skill5**",
                                     "**Skill6**", "**Skill7**", "**Skill8**", "**__Skill9__**"],
    "Veritas, Sacred Ruler of Prophecy": ["Skill1", "Skil2", "Skill3", "Skill4", "**Skill5**",
                                          "**Skill6**", "**Skill7**", "**Skill8**", "**__Skill9__**"],
    "Alaric, Sacred Ruler of Totality": ["Skill1", "Skil2", "Skill3", "Skill4", "**Skill5**",
                                         "**Skill6**", "**Skill7**", "**Skill8**", "**__Skill9__**"]}
boss_attack_exceptions = list(boss_attack_dict.keys())
skill_multiplier_list = [1, 2, 3, 5, 7, 10, 15, 20, 50]
skill_multiplier_list_high = [4, 6, 8, 10, 15, 25, 50, 99, 999]


class CombatTracker:
    def __init__(self, player_obj):
        self.player_obj = player_obj
        self.player_cHP = player_obj.player_mHP
        self.current_mana, self.mana_limit = self.player_obj.start_mana, self.player_obj.mana_limit
        self.charges, self.remaining_hits = 0, 0
        self.total_dps, self.highest_damage = 0, 0.0
        self.recovery, self.hp_regen = player_obj.recovery, int(player_obj.hp_regen * player_obj.player_mHP)
        self.total_cycles = 0
        self.stun_cycles, self.stun_status = 0, ""
        self.solar_stacks = 0
        self.time_lock, self.time_damage = 0, 0
        self.bleed_tracker = 0.0


async def run_solo_cycle(tracker_obj, boss_obj, player_obj):
    hit_list, msg, p_alive, b_alive, total_damage = await run_cycle(tracker_obj, boss_obj, player_obj)
    total_dps = int(tracker_obj.total_dps / tracker_obj.total_cycles)
    embed_msg = boss_obj.create_boss_embed(total_dps)
    embed_msg.add_field(name="", value=msg, inline=False)
    if not b_alive:
        embed_msg = boss_obj.create_boss_embed(total_dps)
    hit_field = ""
    for hit in hit_list:
        hit_field += f"{hit[1]}\n"
        if hit[0] > tracker_obj.highest_damage:
            tracker_obj.highest_damage = hit[0]
    embed_msg.add_field(name="", value=hit_field, inline=False)
    return embed_msg, p_alive, b_alive


async def run_raid_cycle(tracker_obj, boss_obj, player_obj, raid_atk):
    hit_list, player_msg, p_alive, b_alive, total_damage = await run_cycle(tracker_obj, boss_obj, player_obj, raid_atk)
    if total_damage != 0 and p_alive:
        player_msg = f"{player_msg} - dealt {sm.number_conversion(total_damage)} damage!"
    return player_msg, total_damage


async def run_cycle(tracker_obj, boss_obj, player_obj, raid_attack=None):
    tracker_obj.total_cycles += 1
    hit_list, total_damage = [], 0
    player_alive, boss_alive = True, True
    # Step 1: Check and handle status effects
    status_effects_result = handle_status(tracker_obj, player_obj)
    if status_effects_result is not None:
        return hit_list, status_effects_result, player_alive, boss_obj.boss_cHP > 0, total_damage
    # Step 2: Boss takes action
    player_alive, boss_action_msg = handle_boss_actions(boss_obj, tracker_obj, player_obj, raid_attack)
    if not player_alive:
        tracker_obj.hp_regen = 0
        battle_msg = f"{player_obj.player_username} has been felled!"
        await player_obj.update_misc_data("deaths", 1)
        return hit_list, battle_msg, player_alive, boss_alive, total_damage
    # Step 3: Player takes action
    hit_list = await handle_player_actions(hit_list, tracker_obj, boss_obj, player_obj)
    # Step 4: Handle Cyclic DoT
    if player_obj.appli["Bleed"] > 0:
        hit_list.append(await trigger_bleed(tracker_obj, player_obj, boss_obj=boss_obj))
    # Step 5: Compile final battle message and return results
    total_damage = sum(hit[0] for hit in hit_list)
    tracker_obj.total_dps += total_damage
    battle_msg = f"{player_obj.player_username} - [HP: {sm.display_hp(tracker_obj.player_cHP, player_obj.player_mHP)}]"
    battle_msg += f" - [Recovery: {tracker_obj.recovery}]"
    if raid_attack is None:
        battle_msg = f"{player_obj.player_username} - [HP: {sm.number_conversion(tracker_obj.player_cHP)} "
        battle_msg += f" - R: {tracker_obj.recovery}]"
    else:
        battle_msg = f"{boss_action_msg}{battle_msg}"
    return hit_list, battle_msg, player_alive, boss_obj.boss_cHP > 0, total_damage


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


def handle_boss_actions(boss_obj, tracker_obj, player_obj, raid_atk=None):
    is_alive, boss_msg = True, ""
    # Handle Boss Status
    if boss_obj.stun_cycles > 0 and boss_obj.boss_type != "Ruler":
        tracker_obj.stun_cycles -= 1
        boss_msg = f"{boss_obj.boss_name} is {boss_obj.stun_status}! Duration: {boss_obj.stun_cycles} cycles.\n"
        if boss_obj.stun_cycles == 0:
            boss_msg = f"{boss_obj.boss_name} has recovered from being {boss_obj.stun_status}!"
        return is_alive, boss_msg
    if boss_obj.boss_type_num == 0:
        return is_alive, boss_msg
    # Handle boss attacks.
    boss_element = boss_obj.boss_element if boss_obj.boss_element != 9 else random.randint(0, 8)
    if raid_atk is None:
        specific_key = [key for key in boss_attack_exceptions if key in boss_obj.boss_name]
        skill_list = boss_attack_dict[specific_key[0]] if specific_key else boss_attack_dict[boss_obj.boss_type]
        idx = random.randint(0, len(skill_list) - 1)
        skill = skill_list[idx]
    else:
        skill, idx = raid_atk
    if "[ELEMENT]" in skill:
        skill = skill.replace("[ELEMENT]", gli.element_special_names[boss_element])
    base_set = [100, 100] if "_" in skill else [25, 50]
    bypass1 = True if "_" in skill else False
    bypass2 = True if "**" in skill else False
    skill_bonus = skill_multiplier_list[idx] if boss_obj.boss_level < 500 else skill_multiplier_list_high[idx]
    # Handle boss enrage.
    if boss_obj.boss_type_num >= 2 and boss_obj.boss_cHP <= int(boss_obj.boss_mHP / 2):
        base_set = [2 * value for value in base_set]
    damage_set = [base_set[0] * boss_obj.boss_level * skill_bonus, base_set[1] * boss_obj.boss_level * skill_bonus]
    damage_set, _ = handle_evasions(player_obj.block, player_obj.dodge, damage_set, bypass1=bypass1, bypass2=bypass2)
    is_alive, damage = take_combat_damage(player_obj, tracker_obj, damage_set, boss_element, bypass2)
    boss_msg += f"{boss_obj.boss_name} uses {skill} dealing {sm.number_conversion(damage)} damage!\n"
    # Handle boss regen.
    if boss_obj.boss_type_num < 3:
        return is_alive, boss_msg
    regen_value = 0.001 * boss_obj.boss_tier if raid_atk is None else 0.01
    boss_obj.boss_cHP += int(regen_value * boss_obj.boss_mHP)
    boss_obj.boss_cHP = min(boss_obj.boss_cHP, boss_obj.boss_mHP)
    boss_msg += f"{boss_obj.boss_name} regenerated 0.{boss_obj.boss_tier}% HP!\n"
    return is_alive, boss_msg


async def handle_player_actions(hit_list, tracker_obj, boss_obj, player_obj):
    regen_value = tracker_obj.hp_regen if tracker_obj.player_cHP != 0 else 0
    tracker_obj.player_cHP = min(player_obj.player_mHP, regen_value + tracker_obj.player_cHP)
    combo_count, hits_per_cycle = 1 + player_obj.appli["Combo"], int(player_obj.attack_speed)
    tracker_obj.remaining_hits += player_obj.attack_speed - hits_per_cycle
    while tracker_obj.remaining_hits >= 1:
        hits_per_cycle += 1
        tracker_obj.remaining_hits -= 1
    # Handle all hits
    for x in range(hits_per_cycle):
        hit_list.append(await hit_boss(tracker_obj, boss_obj, player_obj, combo_count))
        if tracker_obj.solar_stacks >= 35:
            hit_list.append(await trigger_flare(tracker_obj, player_obj, boss_obj=boss_obj))
        combo_count += 1
        tracker_obj.charges += player_obj.appli["Ultimate"]
        # Handle Ultimate
        if tracker_obj.charges >= 20:
            hit_list.append(await hit_boss(tracker_obj, boss_obj, player_obj, combo_count, hit_type="Ultimate"))
            if player_obj.appli["Bleed"] > 0:
                hit_list.append(await trigger_bleed(tracker_obj, player_obj, hit_type="Ultimate", boss_obj=boss_obj))
        if tracker_obj.solar_stacks >= 35:
            hit_list.append(await trigger_flare(tracker_obj, player_obj, boss_obj=boss_obj))
        # Stop iterating if boss dies
        if not boss_obj.boss_cHP > 0:
            return hit_list
    return hit_list


def take_combat_damage(player_obj, tracker_obj, damage_set, dmg_element, bypass_immortal, no_trigger=False):
    damage = random.randint(damage_set[0], damage_set[1])
    player_resist = 0
    if dmg_element != -1:
        player_resist = player_obj.elemental_res[dmg_element]
        if (tracker_obj.stun_status != "stunned" and random.randint(1, 100) <= 1 and
                gli.element_status_list[dmg_element] is not None):
            tracker_obj.stun_status = gli.element_status_list[dmg_element]
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
    critical_type = await player_obj.get_player_boss_damage(boss_obj)
    damage, skill_name = skill_adjuster(player_obj, tracker_obj, player_obj.total_damage, combo_count,
                                        (hit_type == "Ultimate"))
    damage, mana_msg = check_mana(player_obj, tracker_obj, damage)
    damage, status_msg = check_lock(player_obj, tracker_obj, damage)
    damage, second_msg = check_bloom(player_obj, damage)
    if player_obj.unique_glyph_ability[2]:
        damage *= (1 + player_obj.bleed_mult)
    if status_msg == " *TIME SHATTER*" or critical_type != "":
        damage *= random.randint(1, max(1, player_obj.rng_bonus))
    damage, extension = (boss_obj.damage_cap, " *LIMIT*") if damage >= boss_obj.damage_cap != -1 else (damage, "")
    hit_msg = f"{combo_count}x Combo: {skill_name} {sm.number_conversion(damage)}{extension}"
    if hit_type == "Ultimate":
        hit_msg = f"Ultimate: {skill_name} {sm.number_conversion(damage)}{extension}"
    hit_msg += f"{mana_msg}{status_msg}{second_msg}{critical_type}"
    damage = scale_raid_damage(damage)
    boss_obj.boss_cHP -= damage
    return [damage, hit_msg]


async def trigger_bleed(tracker_obj, player_obj, hit_type="Normal", boss_obj=None, pvp_data=None):
    bleed_dict = {1: "Single", 2: "Double", 3: "Triple", 4: "Quadra", 5: "Penta"}
    hit_multiplier, keyword = (1.5, "Sanguine") if hit_type == "Ultimate" else (0.75, "Blood")
    count = "Zenith" if player_obj.appli["Bleed"] > 5 else bleed_dict[player_obj.appli["Bleed"]]
    # Calculate damage
    await player_obj.get_bleed_damage(boss_obj)
    damage = pvp_data[2] if pvp_data is not None else int(hit_multiplier * player_obj.total_damage)
    damage *= tracker_obj.bleed_tracker * (1 + player_obj.bleed_mult) * (1 + player_obj.bleed_pen)
    damage, bleed_type = check_hyper_bleed(player_obj, damage)
    # Handle application scaling
    damage *= (1 + player_obj.appli["Bleed"])
    # Determine boss or pvp specific damage adjustments.
    if boss_obj is not None:
        damage, extension = (boss_obj.damage_cap, " *LIMIT*") if damage >= boss_obj.damage_cap != -1 else (damage, "")
        damage = scale_raid_damage(damage)
        boss_obj.boss_cHP -= damage
    else:
        damage, extension = pvp_scale_damage(*pvp_data), ""
        # apply damage to other player need to add <<<<<<<<<<<<<<<<<<<<<
    bleed_msg = f"{keyword} Rupture [{count}]: {sm.number_conversion(damage)}{extension} *{bleed_type}*"
    return [damage, bleed_msg]


async def trigger_flare(tracker_obj, player_obj, boss_obj=None, pvp_data=None):
    tracker_obj.solar_stacks = 0
    flare_value = 0.10 if player_obj.flare_type == "Solar" else 0.25
    # Determine boss or pvp specific damage adjustments.
    if boss_obj is not None:
        damage = int(boss_obj.boss_cHP * flare_value)
        damage = scale_raid_damage(damage)
        boss_obj.boss_cHP -= damage
    else:
        damage = int(pvp_data.player_cHP * flare_value)
        pvp_data.player_cHP -= damage
    flare_msg = f"{player_obj.flare_type} Flare: {sm.number_conversion(damage)}{extension}"
    return [damage, flare_msg]


def check_hyper_bleed(player_obj, bleed_damage):
    bleed_type = "BLEED"
    if random.randint(1, 100) <= player_obj.trigger_rate["Hyperbleed"]:
        bleed_type = "HYPERBLEED"
        bleed_damage *= (1 + player_obj.bleed_mult)
    return int(bleed_damage), bleed_type


def update_bleed(tracker_obj, player_obj):
    if player_obj.appli["Bleed"] <= 0:
        return
    tracker_obj.bleed_tracker += 0.05 * player_obj.appli["Bleed"]
    tracker_obj.bleed_tracker = min(1, tracker_obj.bleed_tracker)


def scale_raid_damage(damage):
    s_damage, base = damage // 10, 10000000000
    return s_damage if s_damage <= base else int(min(base * (1 + math.log10(s_damage / base) / 3), base * 10))


def check_bloom(player_obj, input_damage):
    damage, status_msg = input_damage, ""
    if random.randint(1, 100) <= int(round(player_obj.trigger_rate["Bloom"] * 100)):
        damage, status_msg = int(damage * player_obj.bloom_mult), " *BLOOM*"
        if random.randint(1, 100) <= int(round(player_obj.spec_conv["Heavenly"] * 10)):
            damage, status_msg = damage * 10, " *HEAVENLY BLOOM*"
    elif random.randint(1, 100) <= int(round(player_obj.spec_conv["Stygian"] * 100)):
        damage, status_msg = int(damage * player_obj.bloom_mult * 3), " *STYGIAN BLOOM*"
    elif random.randint(1, 100) <= int(round(player_obj.spec_conv["Calamity"] * 100)):
        damage, status_msg = int(damage * 9.99), " *CALAMITY*"
    return damage, status_msg


def check_mana(player_obj, combat_tracker, damage):
    if combat_tracker.current_mana > 0:
        return damage, ""
    if not player_obj.mana_shatter:
        combat_tracker.current_mana = combat_tracker.mana_limit
    else:
        combat_tracker.current_mana = max((combat_tracker.mana_limit * -1), combat_tracker.current_mana)
        damage *= 1 + (player_obj.mana_mult + combat_tracker.current_mana * -1)
        return damage, " *MANA SHATTER*"
    damage *= (1 + player_obj.mana_mult)
    return damage, " *MANA BURST*"


def check_lock(player_obj, combat_tracker, damage):
    status_msg = ""
    # Create a new time lock.
    if combat_tracker.time_lock == 0:
        if random.randint(1, 100) > player_obj.trigger_rate["Temporal"]:
            return damage, status_msg
        combat_tracker.time_lock = player_obj.appli["Temporal"]
        status_msg = " *TIME LOCK*"
    # Handle existing time lock.
    elif combat_tracker.time_lock > 0:
        combat_tracker.time_lock -= 1
        combat_tracker.time_damage += damage
        # Trigger time shatter.
        if combat_tracker.time_lock == 0 or player_obj.unique_glyph_ability[7]:
            damage = combat_tracker.time_damage * player_obj.temporal_mult
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


def boss_defences(method, player_obj, boss_object, location, e_weapon):
    mult = (1 - (0.05 * boss_object.boss_tier - 1))
    if method == "Element" and boss_object.boss_eleweak[location] != 1:
        return mult
    c_idx, w_idx = gli.class_names.index(player_obj.player_class), gli.class_names.index(e_weapon.item_damage_type)
    if method != "Element" and boss_object.boss_typeweak[c_idx] != 1 and boss_object.boss_typeweak[w_idx] != 1:
        return mult
    return 1.1


def boss_true_mitigation(boss_level):
    a, b, c = 1, 0.5, 0.1
    return a - (a - b) * boss_level / 99 if boss_level <= 99 else b - (b - c) * (boss_level - 100) / 899


def check_critical(player_obj, player_damage, num_elements):
    critical_type, critical_roll = "", random.randint(1, 100)
    # Check for fractal type critical.
    if critical_roll <= player_obj.trigger_rate["Fractal"]:
        player_damage *= num_elements
        critical_type = " *FRACTAL*"
    # Check for regular critical.
    elif critical_roll < player_obj.trigger_rate["Critical"]:
        player_damage *= (1 + player_obj.critical_mult)
        critical_type = " *CRITICAL*"
        # Check for omega critical.
        if random.randint(1, 100) <= player_obj.trigger_rate["Omega"]:
            critical_type = " *OMEGA CRITICAL*"
            player_damage *= (1 + player_obj.critical_mult)
        player_damage *= (1 + player_obj.critical_pen)
    return player_damage, critical_type


def skill_adjuster(player_obj, combat_tracker, hit_damage, combo_count, is_ultimate):
    mult_dict = {0: 0.5, 1: 0.75, 2: 1, 3: 2}
    combo_mult = (1 + (player_obj.combo_mult * combo_count)) * (1 + player_obj.combo_pen)
    ultimate_mult = (1 + player_obj.ultimate_mult) * (1 + player_obj.ultimate_pen)
    skill_list = gli.skill_names_dict[player_obj.player_class]
    if player_obj.aqua_points >= 100:
        skill_list = ["Sea of Subjugation", "Ocean of Oppression", "Deluge of Domination", "Tides of Annihilation"]
        mult_dict = {0: 1, 1: 1.5, 2: 2, 3: 5}
    if is_ultimate:
        combat_tracker.charges -= 20
        damage = int(hit_damage * combo_mult * ultimate_mult * (mult_dict[3] + player_obj.skill_damage_bonus[3]))
        return damage, skill_list[3]
    # Handle non-ultimates.
    combat_tracker.current_mana -= combo_mult
    index = 0 if combo_count < 3 else 1 if combo_count < 5 else 2
    damage = int(hit_damage * combo_mult * (mult_dict[index] + player_obj.skill_damage_bonus[index]))
    if player_obj.unique_glyph_ability[3]:
        damage = int(hit_damage * ultimate_mult)
    combat_tracker.charges += 1 + player_obj.charge_generation
    combat_tracker.solar_stacks += 1 if player_obj.flare_type != "" else 0
    return damage, skill_list[index]


def pvp_defences(attacker, defender, player_damage, e_weapon):
    # Type Defences
    adjusted_damage = player_damage - defender.damage_mitigation * 0.01 * player_damage
    # Elemental Defences
    temp_ele = limit_elements(attacker, e_weapon) if attacker.elemental_capacity < 9 else e_weapon.item_elements.copy()
    highest = 0
    for idx, x in enumerate(temp_ele):
        if x == 1:
            attacker.elemental_damage[idx] = adjusted_damage * (1 + attacker.elemental_mult[idx])
            resist_multi = 1 - defender.elemental_res[idx]
            penetration_multi = 1 + attacker.elemental_pen[idx]
            attacker.elemental_damage[idx] *= resist_multi * penetration_multi * attacker.elemental_conversion[idx]
            if attacker.elemental_damage[idx] > attacker.elemental_damage[highest]:
                highest = idx
    stun_status = gli.element_status_list[highest]
    stun_status = stun_status if (
                stun_status is not None and random.randint(1, 100) <= attacker.trigger_rate["Status"]) else None
    return stun_status, int(sum(attacker.elemental_damage) * (1 + attacker.banes[5]))


async def pvp_attack(attacker, defender):
    e_weapon = await inventory.read_custom_item(attacker.player_equipped[0])
    num_elements = sum(e_weapon.item_elements)
    player_damage = await attacker.get_player_initial_damage()
    player_damage, critical_type = check_critical(attacker, player_damage, num_elements)
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


async def abandon_flag(player_obj, toggle=False):
    params = {'player_check': player_obj.player_id}
    check_query = "SELECT abandon, encounter FROM EncounterList WHERE player_id = :player_check"
    df = await rqy(check_query, return_value=True, params=params)
    if df is None or len(df) == 0:
        return None
    elif int(df['abandon'].values[0]) == 1 and str(df['encounter'].values[0]) in ["solo", "gauntlet"]:
        return 1
    if toggle:
        await rqy("UPDATE EncounterList SET abandon = 1 WHERE player_id = :player_check", params=params)
    return 0


def limit_elements(player_obj, e_weapon):
    elemental_breakdown = []
    temp_list = e_weapon.item_elements.copy()
    if player_obj.elemental_capacity == 9:
        return temp_list
    for x, is_used in enumerate(temp_list):
        if is_used:
            temp_total = player_obj.elemental_mult[x] * player_obj.elemental_pen[x]
            temp_total *= player_obj.elemental_curse[x]
            elemental_breakdown.append([x, temp_total])
    sorted_indices = sorted(elemental_breakdown, key=lambda e: e[1], reverse=True)
    damage_limitation = [idx for idx, _ in sorted_indices[:player_obj.elemental_capacity]]
    for i in [i for i in range(len(temp_list)) if i not in damage_limitation]:
        temp_list[i] = 0
    return temp_list
