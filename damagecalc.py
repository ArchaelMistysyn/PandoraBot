import inventory
import player


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
            damage_temp = 10
        case "Silver" | "Dazzling" | "Spirit" | "Gold" | "Luminous":
            damage_temp = 50
        case "Mithril" | "Lustrous" | "Soulbound" | "Jeweled" | "Shining":
            damage_temp = 100
        case "Diamond" | "Radiant" | "Phantasmal" | "Prismatic":
            damage_temp = 200
        case "Crystal" | "Divine" | "Spectral" | "Resplendent":
            damage_temp = 400
        case "Voidcrystal":
            damage_temp = 1000
        case _:
            damage_temp = 0

    return damage_temp


def get_dmg_min(player_object: player.PlayerProfile) -> int:
    filename = "cinventory.csv"
    dmg_min = 0

    if player_object.equipped_armour == "":
        dmg_min += 0
    else:
        armour_object = inventory.read_custom_item(player_object.equipped_armour)
        dmg_min += armour_object.item_damage_max

    if player_object.equipped_acc == "":
        dmg_min += 0
    else:
        acc_object = inventory.read_custom_item(player_object.equipped_acc)
        dmg_min += acc_object.item_damage_max

    if player_object.equipped_weapon == "":
        dmg_min += 0
    else:
        weapon_object = inventory.read_custom_item(player_object.equipped_weapon)
        dmg_min += weapon_object.item_damage_max
        dmg_min *= weapon_object.item_bonus_stat

    return dmg_min


def get_dmg_max(player_object: player.PlayerProfile) -> int:
    filename = "cinventory.csv"
    dmg_max = 0

    if player_object.equipped_armour == "":
        dmg_max += 0
    else:
        armour_object = inventory.read_custom_item(player_object.equipped_armour)
        dmg_max += armour_object.item_damage_max

    if player_object.equipped_acc == "":
        dmg_max += 0
    else:
        acc_object = inventory.read_custom_item(player_object.equipped_acc)
        dmg_max += acc_object.item_damage_max

    if player_object.equipped_weapon == "":
        dmg_max += 0
    else:
        weapon_object = inventory.read_custom_item(player_object.equipped_weapon)
        dmg_max += weapon_object.item_damage_max
        dmg_max *= weapon_object.item_bonus_stat

    return dmg_max


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


def boss_weakness_multiplier(weapon, boss_typeweak, boss_eleweak_a, boss_eleweak_b) -> float:
    resist_multiplier = 0.7
    type_multiplier = 0.8
    for x in weapon.item_elements:
        if str(x) == boss_eleweak_a or str(x) == boss_eleweak_b:
            resist_multiplier += 0.5
    if weapon.item_damage_type == boss_typeweak:
        type_multiplier += 0.5

    defences_multiplier = resist_multiplier * type_multiplier
    return defences_multiplier
