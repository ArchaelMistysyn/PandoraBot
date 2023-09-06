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
        case  "Steel" | "Glittering" | "Essence" | "Metallic" | "Faint" | "Enchanted":
            damage_temp = 125
        case "Silver" | "Dazzling" | "Spirit" | "Gold" | "Luminous":
            damage_temp = 250
        case "Mithril" | "Lustrous" | "Soulbound" | "Jeweled" | "Shining":
            damage_temp = 500
        case "Diamond" | "Radiant" | "Phantasmal" | "Prismatic":
            damage_temp = 1000
        case "Crystal" | "Divine" | "Spectral" | "Resplendent":
            damage_temp = 2500
        case "Voidcrystal":
            damage_temp = 9500
        case _:
            damage_temp = 0

    return damage_temp


def accessory_ability_damage(acc_keyword, boss_cHP, boss_mHP, player_hp) -> float:
    damage_multiplier = 1.0

    match acc_keyword:
        case "Hybrid Stance":
            damage_multiplier = 1.05
        case "Offensive Stance":
            damage_multiplier = 1.1
        case "First Blood":
            if (boss_cHP / boss_mHP) > 0.75:
                damage_multiplier = 1.25
            else:
                damage_multiplier = 1.0
        case "Onslaught Pose":
            damage_multiplier = 1.2
        case "Last Breath":
            if player_hp == 1:
                damage_multiplier = 0.25
            else:
                damage_multiplier = 1.0
        case "Breaker":
            if (boss_cHP / boss_mHP) > 0.5:
                damage_multiplier = 1.5
            else:
                damage_multiplier = 1.0
        case "Inferno's Will":
            damage_multiplier = 1.2
        case "Final Stand":
            if player_hp == 1:
                damage_multiplier = 5.0
            else:
                damage_multiplier = 1.0
        case "Coup de Grace":
            if (boss_cHP / boss_mHP) < 0.5:
                damage_multiplier = 1.5
            else:
                damage_multiplier = 1.0
        case "Perfect Counter":
            damage_multiplier = 1.5
        case "Bahamut's Grace":
            damage_multiplier = 2.0
        case _:
            damage_multiplier = 1.0
    return damage_multiplier


def boss_weakness_multiplier(weapon, elemental_penetration, boss_typeweak, boss_eleweak_a, boss_eleweak_b) -> float:
    resist_multiplier = 0.6
    type_multiplier = 0.7
    for x in weapon.item_elements:
        if str(x) == boss_eleweak_a or str(x) == boss_eleweak_b:
            resist_multiplier += 0.4
            resist_multiplier += 1 + elemental_penetration
    if weapon.item_damage_type == boss_typeweak:
        type_multiplier += 0.3

    defences_multiplier = resist_multiplier * type_multiplier
    return defences_multiplier


def get_player_damage(player_object, boss_object):
    player_damage = 0
    is_weapon = False
    is_armour = False
    is_acc = False

    base_critical = 5.0
    base_attack_speed = 1.0

    elemental_penetration = 0.0
    critical_chance = 0.0
    attack_speed = 0.0
    critical_multiplier = 2.0
    hit_multiplier = 1.0
    aura_multiplier = 1.0
    curse_multiplier = 1.0
    final_damage_multiplier = 1.0

    player_object.get_equipped()
    if player_object.equipped_weapon != "":
        e_weapon = inventory.read_custom_item(player_object.equipped_weapon)
        player_damage += (e_weapon.item_damage_min + e_weapon.item_damage_max) / 2
        attack_speed = float(e_weapon.item_bonus_stat)
        is_weapon = True
    if player_object.equipped_armour != "":
        e_armour = inventory.read_custom_item(player_object.equipped_armour)
        player_damage += (e_armour.item_damage_min + e_armour.item_damage_max) / 2
        is_armour = True
    if player_object.equipped_acc != "":
        e_acc = inventory.read_custom_item(player_object.equipped_acc)
        player_damage += (e_acc.item_damage_min + e_acc.item_damage_max) / 2
        is_acc = True

    float_damage = float(player_damage)

    # bonus stats
    if is_weapon:
        for x in e_weapon.item_prefix_values:
            roll_tier = int(str(x)[1])
            match str(x)[2]:
                case "1":
                    critical_chance += 0.25 * float(roll_tier)
                case "2":
                    attack_speed += 0.25 * float(roll_tier)
                case "3":
                    elemental_penetration += 0.25 * float(roll_tier)
                case "4":
                    final_damage_multiplier += 0.25 * float(roll_tier)
                case _:
                    no_change = True
        for y in e_weapon.item_suffix_values:
            roll_tier = int(str(y)[1])
            match str(y)[2]:
                case "1":
                    critical_multiplier += 0.50 * float(roll_tier)
                case "2":
                    aura_multiplier += 0.25 * float(roll_tier)
                case "3":
                    curse_multiplier += 0.25 * float(roll_tier)
                case "4":
                    hit_multiplier += float(roll_tier)
                case _:
                    no_change = True
    if is_armour:
        for x in e_armour.item_prefix_values:
            roll_tier = int(str(x)[1])
            match str(x)[2]:
                case "1":
                    critical_chance += 0.25 * float(roll_tier)
                case "2":
                    attack_speed += 0.25 * float(roll_tier)
                case "3":
                    elemental_penetration += 0.25 * float(roll_tier)
                case "4":
                    final_damage_multiplier += 0.25 * float(roll_tier)
                case _:
                    no_change = True
        for y in e_armour.item_suffix_values:
            roll_tier = int(str(y)[1])
            match str(y)[2]:
                case "1":
                    critical_multiplier += 0.50 * float(roll_tier)
                case "2":
                    aura_multiplier += 0.25 * float(roll_tier)
                case "3":
                    curse_multiplier += 0.25 * float(roll_tier)
                case "4":
                    # hit_multiplier += float(roll_tier)
                    no_change = True
                case _:
                    no_change = True
    if is_acc:
        for x in e_acc.item_prefix_values:
            roll_tier = int(str(x)[1])
            match str(x)[2]:
                case "1":
                    critical_chance += 0.25 * float(roll_tier)
                case "2":
                    attack_speed += 0.25 * float(roll_tier)
                case "3":
                    elemental_penetration += 0.25 * float(roll_tier)
                case "4":
                    final_damage_multiplier += 0.25 * float(roll_tier)
                case _:
                    no_change = True
        for y in e_acc.item_suffix_values:
            roll_tier = int(str(y)[1])
            match str(y)[2]:
                case "1":
                    critical_multiplier += 0.50 * float(roll_tier)
                case "2":
                    aura_multiplier += 0.25 * float(roll_tier)
                case "3":
                    curse_multiplier += 0.25 * float(roll_tier)
                case "4":
                    # hit_multiplier += float(roll_tier)
                    no_change = True
                case _:
                    no_change = True
        float_damage *= accessory_ability_damage(e_acc.item_bonus_stat,
                                                            boss_object.boss_cHP,
                                                            boss_object.boss_mHP,
                                                            player_object.player_hp)
    # Critical hits
    random_num = random.randint(1, 100)
    if random_num < int(base_critical * (1 + critical_chance)):
        critical_type = " CRITICAL HIT!"
        float_damage *= critical_multiplier
    else:
        critical_type = ""

    # Attack Speed
    float_damage *= (base_attack_speed * (1 + attack_speed))

    # Hit Multiplier
    float_damage *= hit_multiplier

    # Additional increases
    additional_multiplier = 1 + (player_object.player_lvl * 0.01)
    additional_multiplier *= (1 + aura_multiplier)
    additional_multiplier *= (1 + curse_multiplier)
    additional_multiplier *= (1 + final_damage_multiplier)
    float_damage *= additional_multiplier

    # Boss defences
    float_damage *= boss_weakness_multiplier(e_weapon, elemental_penetration,
                                                        boss_object.boss_typeweak,
                                                        boss_object.boss_eleweak_a,
                                                        boss_object.boss_eleweak_b)

    player_damage = int(float_damage)

    return player_damage, critical_type
