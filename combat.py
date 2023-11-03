import inventory
import player
import random
import bosses
import pandorabot

skill_names_dict = {
    "Knight": ["Destructive Cleave", "Ruinous Slash", "Destiny Divider"],
    "Ranger": ["Precise Shot", "Comet Arrow", "Blitz Barrage"],
    "Assassin": ["Exploit Injury", "Eternal Laceration", "Blood Recursion"],
    "Mage": ["Aether Bolt", "Mystic Maelstrom", "Primal Convergence"],
    "Weaver": ["Infused Slice", "Multithreading", "Reality Fabricator"],
    "Rider": ["Valiant Charge", "Mounted Onslaught", "Chaos Rampage"],
    "Summoner": ["Savage Blow", "Relentless Frenzy", "Conqueror's Wrath"]
}


class CombatTracker:
    def __init__(self):
        self.charges = 0
        self.remaining_hits = 0
        self.total_dps = 0
        self.total_cycles = 0
        self.stun_cycles = 0
        self.player_cHP = 0
        self.bleed_tracker = 0.0


def run_solo_cycle(combat_tracker, active_boss, player_object):
    class_skill_list = skill_names_dict[player_object.player_class]
    is_alive = True
    if combat_tracker.stun_cycles <= 0:
        combo_count = 0
        combo_adjuster = 1
        charge_adjuster = 0
        match player_object.player_class:
            case "Knight":
                charge_adjuster = 1
            case "Summoner":
                combo_adjuster = 2
            case _:
                pass
        hp_adjust_msg = ""
        if active_boss.boss_type_num >= 2:
            if active_boss.boss_element != 9:
                boss_damage_element = active_boss.boss_element
            else:
                boss_damage_element = random.randint(0, 8)
            boss_damage = random.randint(50 * active_boss.boss_tier, 200 * active_boss.boss_tier)
            boss_damage -= int(boss_damage * player_object.elemental_resistance[boss_damage_element])
            combat_tracker.player_cHP -= boss_damage
            hp_adjust_msg = f"{active_boss.boss_name} attacks dealing {boss_damage:,} damage!\n"
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
                    hp_adjust_msg += f"{player_object.player_username} regenerated {regen_value:,} HP!\n"

        hit_list = []
        hits_per_cycle = int(player_object.attack_speed)
        combat_tracker.remaining_hits += player_object.attack_speed - hits_per_cycle
        while combat_tracker.remaining_hits >= 1:
            hits_per_cycle += 1
            combat_tracker.remaining_hits -= 1
        for x in range(hits_per_cycle):
            combo_count += combo_adjuster
            hit_damage, is_critical = player_object.get_player_damage(active_boss)
            combo_multiplier = (1 + (player_object.combo_multiplier * combo_count))
            if combo_count < 5:
                damage = int(hit_damage * 0.5 * combo_multiplier)
                skill_name = class_skill_list[0]
                charges_gained = 1 + (1 * charge_adjuster)
            else:
                damage = int(hit_damage * 0.75 * combo_multiplier)
                skill_name = class_skill_list[1]
                charges_gained = 1 + (2 * charge_adjuster)
            if player_object.can_bleed:
                combat_tracker.bleed_tracker += 0.05
                if combat_tracker.bleed_tracker >= 1.5:
                    combat_tracker.bleed_tracker = 1.5
            combat_tracker.charges += charges_gained
            hit_msg = f"{combo_count}x Combo: {skill_name} {damage}"
            if is_critical:
                hit_msg += f" *CRITICAL*"
            hit_list.append([damage, is_critical, hit_msg])
            active_boss.boss_cHP -= damage
            if combat_tracker.charges >= 10:
                combo_count += combo_adjuster
                hit_damage, is_critical = player_object.get_player_damage(active_boss)
                combat_tracker.charges -= 10
                combo_multiplier = 1 + (player_object.combo_multiplier * combo_count)
                ultimate_multiplier = 1 + player_object.ultimate_multiplier
                damage = int(hit_damage * 2 * combo_multiplier * ultimate_multiplier)
                skill_name = class_skill_list[2]
                hit_msg = f"{combo_count}x Combo: {skill_name} {damage}"
                if is_critical:
                    hit_msg += f" *CRITICAL*"
                hit_list.append([damage, is_critical, hit_msg])
                if player_object.can_bleed:
                    bleed_damage = 2 * player_object.get_bleed_damage(active_boss)
                    hit_msg = f"Sanguine Rupture: {bleed_damage} *BLEED*"
                    is_critical = False
                    hit_list.append([bleed_damage, is_critical, hit_msg])
            if not active_boss.calculate_hp():
                is_alive = False
                break
        if player_object.can_bleed:
            bleed_damage = player_object.get_bleed_damage(active_boss)
            hit_msg = f"Blood Rupture: {bleed_damage} *BLEED*"
            is_critical = False
            hit_list.append([bleed_damage, is_critical, hit_msg])
        damage_values = [hit[0] for hit in hit_list]
        combat_tracker.total_dps += sum(damage_values)
        battle_msg = f"{player_object.player_username} - HP: {combat_tracker.player_cHP} / {player_object.player_mHP}"
        battle_msg = f"{hp_adjust_msg}{battle_msg}"
    else:
        combat_tracker.stun_cycles -= 1
        if combat_tracker.stun_cycles == 0:
            f"{player_object.player_username} has recovered!"
        else:
            battle_msg = f"{player_object.player_username} is recovering!"
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
        hit_field += f"{hit[2]}\n"
    embed_msg.add_field(name="", value=hit_field, inline=False)
    return embed_msg


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
        case "Voidcrystal":
            damage_temp = 25000
        case "Voidplasma":
            damage_temp = 50000
        case _:
            damage_temp = 0

    return damage_temp


def boss_defences(method, player_object, boss_object, location, weapon):
    type_multiplier = (1 - 0.01 * boss_object.boss_lvl / 1.5)
    bonus_multiplier = 0.01 * player_object.player_lvl / 1.5
    if method == "Element":
        if boss_object.boss_eleweak[location] == 1:
            curse_penalty = boss_object.curse_debuffs[location]
            type_multiplier += bonus_multiplier + curse_penalty
    else:
        if weapon.item_damage_type in boss_object.boss_typeweak:
            type_multiplier += bonus_multiplier
    return type_multiplier


def boss_true_mitigation(boss_object):
    mitigation_multiplier = 1 - (boss_object.boss_tier * 0.1)
    return mitigation_multiplier
