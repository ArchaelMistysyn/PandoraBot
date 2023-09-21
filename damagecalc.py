import inventory
import player
import random


def item_damage_calc(base_damage: int, item_enhancement: int, material_tier: str, blessing_tier: str) -> int:
    enhancement_multiplier = 1 + (float(item_enhancement) * 0.01)
    material_damage = get_item_tier_damage(material_tier)
    blessing_damage = get_item_tier_damage(blessing_tier)
    weapon_damage_temp = float(base_damage + material_damage + blessing_damage) * enhancement_multiplier
    weapon_damage_total = int(weapon_damage_temp)
    return int(weapon_damage_total)


def get_item_tier_damage(material_tier: str) -> int:
    match material_tier:
        case  "Steel" | "Glittering" | "Essence" | "Metallic" | "Faint" | "Enchanted" | "Shadow" | "Glowing":
            damage_temp = 125
        case "Silver" | "Dazzling" | "Spirit" | "Gold" | "Luminous" | "Inverted" | "Pure":
            damage_temp = 250
        case "Mithril" | "Lustrous" | "Soulbound" | "Jeweled" | "Shining" | "Abyssal" | "Majestic":
            damage_temp = 500
        case "Diamond" | "Radiant" | "Phantasmal" | "Prismatic" | "Calamitous":
            damage_temp = 1000
        case "Crystal" | "Divine" | "Spectral" | "Resplendent" | "Balefire":
            damage_temp = 2500
        case "Voidcrystal":
            damage_temp = 9500
        case _:
            damage_temp = 0

    return damage_temp


def accessory_ability_multipliers(acc_keyword, boss_cHP, boss_mHP, player_hp):
    damage_multiplier = 0.0
    situational_damage_multiplier = 0.0
    damage_mitigation = 0.0
    match acc_keyword:
        case "Hybrid Stance":
            damage_multiplier = 0.05
            damage_mitigation = 0.05
        case "Offensive Stance":
            damage_multiplier = 0.1
        case "First Blood":
            if (boss_cHP / boss_mHP) > 0.75:
                situational_damage_multiplier = 0.25
        case "Onslaught Pose":
            damage_multiplier = 0.2
        case "Guarding Pose":
            damage_mitigation = 0.2
        case "Last Breath":
            if player_hp == 1:
                damage_multiplier = 1.0
        case "Breaker":
            if (boss_cHP / boss_mHP) > 0.5:
                situational_damage_multiplier = 0.5
        case "Inferno's Will":
            damage_multiplier = 0.3
        case "Mountain's Will":
            damage_mitigation = 0.3
        case "Final Stand":
            if player_hp == 1:
                situational_damage_multiplier = 4.0
        case "Coup de Grace":
            if (boss_cHP / boss_mHP) < 0.5:
                situational_damage_multiplier = 0.5
        case "Perfect Counter":
            damage_multiplier = 0.5
            damage_mitigation = 0.5
        case "Bahamut's Grace":
            damage_multiplier = 1.0
        case _:
            damage_multiplier = 0.0
    return damage_multiplier, situational_damage_multiplier, damage_mitigation


def boss_weakness_multiplier(boss_object, weapon, elemental_penetration):
    resist_multiplier = 0.6
    type_multiplier = 0.7
    for x in weapon.item_elements:
        for y in boss_object.boss_eleweak:
            if str(x) == str(y):
                resist_multiplier += 0.4
                resist_multiplier += 1 + elemental_penetration
    for z in boss_object.boss_typeweak:
        if weapon.item_damage_type == str(z):
            type_multiplier += 0.5

    defences_multiplier = resist_multiplier * type_multiplier
    return defences_multiplier


def get_player_damage(player_object, boss_object):
    player_object.get_player_multipliers(boss_object.boss_cHP, boss_object.boss_mHP)
    float_damage = float(player_object.player_damage)

    # Critical hits
    random_num = random.randint(1, 100)
    if random_num < player_object.critical_chance:
        critical_type = " CRITICAL HIT!"
        float_damage *= (1 + player_object.critical_multiplier)
        # Special Critical Multipliers
        float_damage *= (1 + player_object.special_multipliers)
    else:
        critical_type = ""
    # Attack Speed
    float_damage *= player_object.attack_speed
    # Hit Multiplier
    float_damage *= player_object.hit_multiplier
    # Class Multiplier
    float_damage *= (1 + player_object.class_multiplier)

    # Boss defences
    if player_object.equipped_acc != "":
        e_weapon = inventory.read_custom_item(player_object.equipped_weapon)
        float_damage *= boss_weakness_multiplier(boss_object, e_weapon, player_object.elemental_penetration)

    # Additional increases
    additional_multiplier = 1 + (player_object.player_lvl * 0.01)
    additional_multiplier *= (1 + player_object.aura)
    additional_multiplier *= (1 + player_object.curse)
    additional_multiplier *= (1 + player_object.final_damage)
    float_damage *= additional_multiplier

    player_damage = int(float_damage)

    return player_damage, critical_type
