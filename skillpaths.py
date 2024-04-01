# General imports
import discord

# Data imports
import globalitems
import sharedmethods

glyph_data = {
            "Storms": [["Critical Application +X", 1],
                       ["Vortex", None, 20], ["Typhoon", None, 40], ["Cyclone", None, 60],
                       ["Tempest", "Critical Application +5", 80],
                       ["Maelstrom", "Critical Application +10", 100]],
            "Frostfire": [["Hybrid Penetration (Frostfire) X%", 0],
                          ["Iceburn", None, 20], ["Glacial Flame", None, 40], ["Snowy Blaze", None, 60],
                          ["Subzero Inferno", "Elemental Capacity becomes 3. Grants Cascade.", 80],
                          ["Paradox", "Triple Hybrid Damage, Hybrid Penetration, and Hybrid Curse (Frostfire)", 100]],
            "Horizon": [["Bleed Application +X", 1],
                        ["Red Boundary", None, 20], ["Vermilion Dawn", None, 40], ["Scarlet Sunset", None, 60],
                        ["Ruby Skies", "Bleed Damage is doubled", 80],
                        ["Scarlet Divide", "Bleed Penetration is doubled", 100]],
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
        description = sharedmethods.display_stars(total_points // 20)
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


def allocate_points(player_obj, selected_path, num_change):
    path_type = selected_path.split(" ")[-1]
    path_location = globalitems.path_names.index(path_type)
    spent_points = sum(player_obj.player_stats)
    available_points = player_obj.player_level - spent_points
    if available_points < num_change:
        return "Not enough remaining skill points to allocate!"
    player_obj.player_stats[path_location] += num_change
    condensed_stats = ';'.join(map(str, player_obj.player_stats))
    player_obj.set_player_field("player_stats", condensed_stats)
    return "Skill point has been allocated!"


def create_path_embed(player_obj):
    colour, _ = sharedmethods.get_gear_tier_colours((player_obj.player_echelon + 1) // 2)
    points_msg = "Your shiny toys are useless if you don't know how to use them."
    embed = discord.Embed(color=colour, title="Avalon, Pathwalker of the True Laws", description=points_msg)
    embed.add_field(name=f"{player_obj.player_username}'s Skill Points", value="", inline=False)
    for path_label, points, gear_points in zip(globalitems.path_names, player_obj.player_stats, player_obj.gear_points):
        value_msg = f"Points: {points}"
        if gear_points > 0:
            value_msg += f" (+{gear_points})"
        embed.add_field(name=f"Path of {path_label}", value=value_msg, inline=True)
    spent_points = sum(player_obj.player_stats)
    remaining_points = player_obj.player_level - spent_points
    embed.add_field(name=f"Unspent Points: {remaining_points}", value="", inline=False)
    return embed


def build_points_embed(player_obj, selected_path):
    colour, _ = sharedmethods.get_gear_tier_colours((player_obj.player_echelon + 1) // 2)
    embed = discord.Embed(color=colour, title=f"{selected_path}", description="Stats per point:\n")

    path_type = selected_path.split(" ")[-1]
    for modifier in path_perks[path_type]:
        embed.description += f'{modifier[0].replace("X", str(modifier[1]))}\n'

    # Calculate the points.
    points_field = player_obj.player_stats[globalitems.path_names.index(path_type)]
    gear_points = player_obj.gear_points[globalitems.path_names.index(path_type)]
    points_msg = f"{player_obj.player_username}'s {selected_path} points: {points_field}"
    total_points = points_field + gear_points
    if gear_points > 0:
        points_msg += f" (+{gear_points})"
    embed.add_field(name="", value=points_msg, inline=False)

    # Build the embed.
    embed = display_glyph(path_type, total_points, embed)
    spent_points = sum(player_obj.player_stats)
    remaining_points = player_obj.player_level - spent_points
    embed.add_field(name="", value=f"Remaining Points: {remaining_points}", inline=False)
    return embed
    
    
def assign_path_multipliers(player_obj):
    # Path Multipliers
    total_points = [x + y for x, y in zip(player_obj.player_stats, player_obj.gear_points)]
    unique_breakpoints = [80, 80, 80, 80, 100, 80, 100]
    for glyph, (points, unique_breakpoint) in enumerate(zip(total_points, unique_breakpoints)):
        if points >= unique_breakpoint:
            player_obj.unique_glyph_ability[glyph] = True

    # Storm Path
    storm_bonus = total_points[0]
    player_obj.elemental_multiplier[1] += 0.05 * storm_bonus
    player_obj.elemental_multiplier[2] += 0.05 * storm_bonus
    player_obj.elemental_resistance[1] += 0.01 * storm_bonus
    player_obj.elemental_resistance[2] += 0.01 * storm_bonus
    player_obj.critical_multiplier += 0.03 * storm_bonus
    player_obj.critical_application += storm_bonus // 20
    if storm_bonus >= 80:
        player_obj.critical_application += 5
    if storm_bonus >= 100:
        player_obj.critical_application += 10

    # Horizon Path
    horizon_bonus = total_points[2]
    player_obj.elemental_multiplier[3] += 0.05 * horizon_bonus
    player_obj.elemental_multiplier[4] += 0.05 * horizon_bonus
    player_obj.elemental_resistance[3] += 0.01 * horizon_bonus
    player_obj.elemental_resistance[4] += 0.01 * horizon_bonus
    player_obj.bleed_multiplier += 0.1 * horizon_bonus
    player_obj.bleed_application += horizon_bonus // 20
    if storm_bonus >= 80:
        player_obj.bleed_multiplier *= 2
    if storm_bonus >= 100:
        player_obj.bleed_penetration *= 2

    # Frostfire Path
    frostfire_bonus = total_points[1]
    player_obj.elemental_multiplier[5] += 0.05 * frostfire_bonus
    player_obj.elemental_multiplier[0] += 0.05 * frostfire_bonus
    player_obj.elemental_resistance[5] += 0.01 * frostfire_bonus
    player_obj.elemental_resistance[0] += 0.01 * frostfire_bonus
    player_obj.class_multiplier += 0.01 * frostfire_bonus
    player_obj.elemental_penetration[5] += frostfire_bonus // 20
    player_obj.elemental_penetration[0] += frostfire_bonus // 20

    def apply_cascade(bonus, data_list):
        temp_list = data_list.copy()
        temp_list[0], temp_list[5] = 0, 0
        highest_index = temp_list.index(max(temp_list))
        data_list[highest_index] += data_list[0] + data_list[5]

    if frostfire_bonus >= 80:
        apply_cascade(player_obj.elemental_multiplier, frostfire_bonus)
        apply_cascade(player_obj.elemental_penetration, frostfire_bonus)
        apply_cascade(player_obj.elemental_curse, frostfire_bonus)
    if frostfire_bonus >= 100:
        player_obj.elemental_multiplier[0] *= 3
        player_obj.elemental_multiplier[5] *= 3
        player_obj.elemental_penetration[0] *= 3
        player_obj.elemental_penetration[5] *= 3
        player_obj.elemental_curse[0] *= 3
        player_obj.elemental_curse[5] *= 3

    # Eclipse Path
    eclipse_bonus = total_points[3]
    player_obj.elemental_multiplier[6] += 0.05 * eclipse_bonus
    player_obj.elemental_multiplier[7] += 0.05 * eclipse_bonus
    player_obj.elemental_resistance[6] += 0.01 * eclipse_bonus
    player_obj.elemental_resistance[7] += 0.01 * eclipse_bonus
    player_obj.ultimate_multiplier += 0.1 * eclipse_bonus
    player_obj.ultimate_application += eclipse_bonus // 20
    if eclipse_bonus >= 100:
        player_obj.skill_base_damage_bonus[3] += 3

    # Confluence Path
    confluence_bonus = total_points[5]
    player_obj.aura += 0.01 * confluence_bonus
    player_obj.all_elemental_curse += 0.01 * confluence_bonus
    player_obj.elemental_application += 2 * confluence_bonus // 20
    if confluence_bonus >= 80:
        player_obj.all_elemental_multiplier *= 2
    if confluence_bonus >= 100:
        player_obj.all_elemental_penetration *= 2
        player_obj.all_elemental_curse *= 2

    # Star Path
    star_bonus = total_points[4]
    player_obj.elemental_multiplier[8] += 0.07 * star_bonus
    player_obj.elemental_resistance[8] += 0.01 * star_bonus
    player_obj.combo_multiplier += 0.03 * star_bonus
    star_skill_bonus = 0.25 * star_bonus // 20
    player_obj.skill_base_damage_bonus[0] += star_skill_bonus
    if star_bonus >= 80:
        player_obj.skill_base_damage_bonus[1] += star_skill_bonus
    if star_bonus >= 100:
        player_obj.skill_base_damage_bonus[2] += star_skill_bonus

    # Solitude Path
    solitude_bonus = total_points[6] * 2 if total_points[6] >= 100 else total_points[6]
    player_obj.singularity_damage += (0.10 * solitude_bonus)
    player_obj.singularity_penetration += (0.05 * solitude_bonus)
    player_obj.singularity_curse += (0.01 * solitude_bonus)
    player_obj.temporal_application += solitude_bonus // 20

    return total_points
        