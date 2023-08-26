import inventory
import player


def item_damage_calc(base_damage: int, material_tier: str, blessing_tier: str) -> int:
    material_damage = get_item_tier_damage(material_tier)
    blessing_damage = get_item_tier_damage(blessing_tier)
    weapon_damage_temp = (base_damage + material_damage + blessing_damage)
    return int(weapon_damage_temp)


def get_item_tier_damage(material_tier: str) -> int:
    match material_tier:
        case  "Steel" | "Sparkling" | "Essence" | "Metallic" | "Faint" | "Enchanted":
            damage_temp = 10
        case "Silver" | "Glittering" | "Spirit" | "Gold" | "Luminous":
            damage_temp = 50
        case "Mithril" | "Lustrous" | "Soulbound" | "Jeweled":
            damage_temp = 100
        case "Diamond" | "Radiant" | "Phantasmal":
            damage_temp = 200
        case "Crystal" | "Divine" | "Spectral" | "Resplendant":
            damage_temp = 400
        case _:
            damage_temp = 0

    return damage_temp


def get_dmg_min(player_object: player.PlayerProfile) -> int:
    filename = "cinventory.csv"
    dmg_min = 0

    if player_object.equipped_armour == "":
        dmg_min += 0
    else:
        armour_object = inventory.read_armour(filename, player_object.equipped_armour)
        dmg_min += armour_object.item_damage_max

    if player_object.equipped_acc == "":
        dmg_min += 0
    else:
        acc_object = inventory.read_accessory(filename, player_object.equipped_acc)
        dmg_min += acc_object.item_damage_max

    if player_object.equipped_weapon == "":
        dmg_min += 0
    else:
        weapon_object = inventory.read_weapon(filename, player_object.equipped_weapon)
        dmg_min += weapon_object.item_damage_max
        dmg_min *= weapon_object.item_bonus_stat

    return dmg_min


def get_dmg_max(player_object: player.PlayerProfile) -> int:
    filename = "cinventory.csv"
    dmg_max = 0

    if player_object.equipped_armour == "":
        dmg_max += 0
    else:
        armour_object = inventory.read_armour(filename, player_object.equipped_armour)
        dmg_max += armour_object.item_damage_max

    if player_object.equipped_acc == "":
        dmg_max += 0
    else:
        acc_object = inventory.read_accessory(filename, player_object.equipped_acc)
        dmg_max += acc_object.item_damage_max

    if player_object.equipped_weapon == "":
        dmg_max += 0
    else:
        weapon_object = inventory.read_weapon(filename, player_object.equipped_weapon)
        dmg_max += weapon_object.item_damage_max
        dmg_max *= weapon_object.item_bonus_stat

    return dmg_max
