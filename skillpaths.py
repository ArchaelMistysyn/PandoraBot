import discord
import globalitems

glyph_data = {
            "Storms": [["Critical Application +X", 1],
                       ["Vortex", None, 20], ["Typhoon", None, 40], ["Cyclone", None, 60],
                       ["Tempest", "", 80],
                       ["Maelstrom", "", 100]],
            "Frostfire": [["None", 0],
                          ["Iceburn", None, 20], ["Glacial Flame", None, 40], ["Snowy Blaze", None, 60],
                          ["Subzero Inferno", "Elemental Capacity becomes 3. Grants Cascade.", 80],
                          ["Paradox", "Fire/Ice Damage, Penetration, and Curse values are tripled.", 100]],
            "Horizon": [["Bleed Application +X", 1],
                        ["Red Boundary", None, 20], ["Vermilion Dawn", None, 40], ["Scarlet Sunset", None, 60],
                        ["Ruby Skies", "", 80],
                        ["Scarlet Divide", "", 100]],
            "Eclipse": [["Ultimate Application +X", 1],
                        ["Nightfall", None, 20], ["Moonshadow", None, 40], ["Umbra", None, 60],
                        ["Twilight", "Ultimate Damage and Penetration are applied to all skills.", 80],
                        ["Eventide", "Ultimate Base Damage increases by 300%.", 100]],
            "Stars": [["Basic Attack 1 Bonus Damage X%", 25],
                      ["Nebulas", None, 20], ["Galaxies", None, 40], ["Superclusters", None, 60],
                      ["Universes", "Basic Attack 1 Bonus Damage also applies to Basic Attack 2.", 80],
                      ["Cosmos", "Basic Attack 1 Bonus Damage also applies to Basic Attack 3.", 100]],
            "Confluence": [["Elemental Overflow +X", 2],
                           ["Unity", None, 20], ["Harmony", None, 40], ["Synergy", None, 60],
                           ["Equilibrium", "Omni Damage is doubled.", 80],
                           ["Convergence", "Omni Penetration and Omni Curse are doubled.", 100]],
            "Solitude": [["Temporal Application +X", 1],
                         ["Unity", None, 20], ["Harmony", None, 40], ["Synergy", None, 60],
                         ["Fast Forward", "Time Shatter is applied immediately.", 80],
                         ["Equilibrium", "Elemental Capacity becomes 1. Singularity multipliers are doubled", 100]]
            }
path_perks = {
    "Storms": [["Water Damage X%", 5], ["Lightning Damage X%", 5],
               ["Water Resistance X%", 1], ["Lightning Resistance X%", 1], ["Critical Damage X%", 3]],
    "Frostfire": [
        ["Ice Damage X%", 5], ["Fire Damage X%", 5],
        ["Ice Resistance X%", 1], ["Fire Resistance X%", 1], ["Class Mastery X%", 1]],
    "Horizon": [["Earth Damage X%", 5], ["Wind Damage X%", 5],
                ["Earth Resistance X%", 1], ["Wind Resistance X%", 1], ["Bleed Damage X%", 10]],
    "Eclipse": [["Dark Damage X%", 5], ["Light Damage X%", 5],
                ["Dark Resistance X%", 1], ["Light Resistance X%", 1], ["Ultimate Damage X%", 10]],
    "Stars": [["Celestial Damage X%", 7], ["Celestial Resistance X%", 1], ["Combo Damage X%", 3]],
    "Solitude": [["Singularity Damage X%", 10], ["Singularity Penetration X%", 5], ["Singularity Curse X%", 1]],
    "Confluence": [["Omni Aura X%", 1], ["Omni Curse X%", 1]]
}


def display_glyph(path_type, total_points, embed_msg):
    current_data = glyph_data[path_type]
    path_bonuses = path_perks[path_type]
    if total_points != 0:
        bonus = current_data[0][1] * (total_points // 20)
        glyph_name = f"Glyph of {path_type}"
        # Build the description.
        description = globalitems.display_stars(total_points // 20)
        for modifier in path_bonuses:
            total_value = modifier[1] * total_points
            modified_string = modifier[0].replace("X", str(total_value))
            description += f"\n{modified_string}"
        description += f"\n{current_data[0][0].replace('X', str(bonus))}"
        for breakpoint_data in current_data[1:]:
            if total_points >= breakpoint_data[2]:
                glyph_name = f"Glyph of {breakpoint_data[0]}"
                if breakpoint_data[1] is not None:
                    description += f"\n{breakpoint_data[1]}"
        embed_msg.add_field(name=glyph_name, value=f"{description}", inline=False)
    return embed_msg
