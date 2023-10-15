import inventory
import player
import random
import bosses
import pandorabot


def item_damage_calc(base_damage: int, item_enhancement: int, material_tier: str, blessing_tier: str):

    return int(weapon_damage_total)


def get_item_tier_damage(material_tier):
    match material_tier:
        case  "Steel" | "Glittering" | "Essence" | "Metallic" | "Faint" | "Enchanted" | \
              "Shadow" | "Glowing" | "Tempered" | "Legendary":
            damage_temp = 250
        case "Silver" | "Dazzling" | "Spirit" | "Gold" | "Luminous" | "Inverted" | "Pure" | "Empowered" | "Mythical":
            damage_temp = 500
        case "Mithril" | "Lustrous" | "Soulbound" | "Jeweled" | "Shining" | \
             "Abyssal" | "Majestic" | "Unsealed" | "Fantastical":
            damage_temp = 1000
        case "Diamond" | "Radiant" | "Phantasmal" | "Calamitous" | "Awakened" | "Omniscient":
            damage_temp = 2500
        case "Crystal" | "Divine" | "Spectral" | "Balefire" | "Transcendent" | "Plasma":
            damage_temp = 5000
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
    type_multiplier = (1 - 0.01 * boss_object.boss_lvl)
    bonus_multiplier = 0.01 * player_object.player_lvl
    if method == "Element":
        if boss_object.boss_eleweak[location] == 1:
            type_multiplier += bonus_multiplier
    else:
        if weapon.item_damage_type in boss_object.boss_typeweak:
            type_multiplier += bonus_multiplier
    return type_multiplier
