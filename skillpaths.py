# General imports
import discord

# Data imports
import globalitems as gli
import sharedmethods as sm

glyph_data = {
    "Storms": [["Critical Application +X", 1],
               ["Vortex", None, 20], ["Typhoon", None, 40], ["Cyclone", None, 60],
               ["Tempest", "Critical Application is Doubled", 80],
               ["Maelstrom", "Critical Application +10", 100]],
    "Frostfire": [["Hybrid Penetration (Frostfire) X%", 0],
                  ["Iceburn", None, 20], ["Glacial Flame", None, 40], ["Snowy Blaze", None, 60],
                  ["Subzero Inferno", "Elemental Capacity becomes 3. Grants Cascade", 80],
                  ["Paradox", "Triple Hybrid Damage, Hybrid Penetration, and Hybrid Curse (Frostfire)", 100]],
    "Horizon": [["Bleed Application +X", 1],
                ["Red Boundary", None, 20], ["Vermilion Dawn", None, 40], ["Scarlet Sunset", None, 60],
                ["Ruby Skies", "Bleed Penetration is Doubled", 80],
                ["Scarlet Divide", "Bleed Damage/Pen applies to all hits", 100]],
    "Eclipse": [["Ultimate Application +X", 1],
                ["Nightfall", None, 20], ["Moonshadow", None, 40], ["Umbra", None, 60],
                ["Twilight", "Ultimate Application is Doubled", 80],
                ["Eventide", "Ultimate Damage and Penetration are Applied to All Skills", 100]],
    "Stars": [["Combo Application +X", 1],
              ["Nebulas", None, 20], ["Galaxies", None, 40], ["Superclusters", None, 60],
              ["Universes", "Combo Application is doubled", 80],
              ["Cosmos", "Basic Attack 1 Bonus Applies to All Basic Attacks", 100]],
    "Solar Flux": [["Life Application +X", 1],
                   ["Blue Giant", None, 20], ["White Dwarf", None, 40], ["Yellow Dwarf", None, 60],
                   ["Orange Dwarf", "Life Application is doubled", 80],
                   ["Red Dwarf", "HP Bonus is doubled", 100]],
    "Lunar Tides": [["Mana Application +X", 1],
                    ["New Moon", None, 20], ["Crescent Moon", None, 40], ["Quarter Moon", None, 60],
                    ["Waxing Moon", "Mana Application is Doubled", 80],
                    ["Full Moon", "Mana Damage is Doubled", 100]],
    "Terrestria": [["Temporal Application +X", 1],
                   ["Unity", None, 20], ["Harmony", None, 40], ["Synergy", None, 60],
                   ["Fast Forward", "Time Application is Doubled", 80],
                   ["Equilibrium", "Time Shatter is Applied Immediately", 100]],
    "Confluence": [["Elemental Application +X", 2],
                   ["Unity", None, 20], ["Harmony", None, 40], ["Synergy", None, 60],
                   ["Equilibrium", "Omni Damage is Doubled", 80],
                   ["Convergence", "Omni Penetration and Omni Curse are Doubled", 100]],
    "Waterfalls": [["Aqua Application +X", 1],
                   ["Waterfalls", None, 20], ["Waterfalls", None, 40], ["Waterfalls", None, 60],
                   ["Waterfalls", "Critical Rate Becomes 100%", 80],
                   ["Waterfalls", "Attack Skills are Changed", 100]]
}
path_perks = {
    "Storms": [["Water Damage X%", 5], ["Lightning Damage X%", 5],
               ["Water Resistance X%", 0.1], ["Lightning Resistance X%", 0.1], ["Critical Damage X%", 3]],
    "Frostfire": [
        ["Ice Damage X%", 5], ["Fire Damage X%", 5],
        ["Ice Resistance X%", 0.1], ["Fire Resistance X%", 0.1], ["Class Mastery X%", 1]],
    "Horizon": [["Earth Damage X%", 5], ["Wind Damage X%", 5],
                ["Earth Resistance X%", 0.1], ["Wind Resistance X%", 0.1], ["Bleed Damage X%", 10]],
    "Eclipse": [["Dark Damage X%", 5], ["Light Damage X%", 5],
                ["Dark Resistance X%", 0.1], ["Light Resistance X%", 0.1], ["Ultimate Damage X%", 10]],
    "Stars": [["Celestial Damage X%", 7], ["Celestial Resistance X%", 0.1], ["Combo Damage X%", 3]],
    "Solar Flux": [["Fire Damage X%", 3], ["Wind Damage X%", 3], ["Light Damage X%", 3],
                   ["Fire Resistance X%", 0.1], ["Wind Resistance X%", 0.1], ["Light Resistance X%", 0.1],
                   ["HP Multiplier X%", 1]],
    "Lunar Tides": [["Water Damage X%", 3], ["Ice Damage X%", 3], ["Shadow Damage X%", 3],
                    ["Water Resistance X%", 0.1], ["Ice Resistance X%", 0.1], ["Shadow Resistance X%", 0.1],
                    ["Mana Damage X%", 10]],
    "Terrestria": [["Singularity Damage X%", 10], ["Singularity Penetration X%", 5], ["Singularity Curse X%", 1]],
    "Confluence": [["Omni Damage X%", 1], ["Omni Curse X%", 1]],
    "Waterfalls": [["Water Damage X%", 25], ["Water Resistance X%", 0.2]]
}


async def display_glyph(path_type, total_points, embed_msg, is_inline=True):
    current_data = glyph_data[path_type]
    path_bonuses = path_perks[path_type]
    if total_points != 0:
        bonus = current_data[0][1] * (total_points // 20)
        glyph_name = f"Glyph of {path_type}"
        # Build the description.
        num_stars = min(9, total_points // 20)
        blue_stars = f"{gli.star_icon[2] * num_stars}{gli.star_icon[0] * max(0, (8 - num_stars))}"
        description = sm.display_stars(num_stars) if path_type != "Waterfalls" else blue_stars
        for modifier in path_bonuses:
            total_value = round(modifier[1] * total_points, 1)
            modified_string = modifier[0].replace("X", str(total_value))
            description += f"\n{modified_string}"
        description += f"\n{current_data[0][0].replace('X', str(bonus))}"
        for breakpoint_data in current_data[1:]:
            if total_points >= breakpoint_data[2]:
                glyph_name = f"Glyph of {breakpoint_data[0]}"
                if breakpoint_data[1] is not None:
                    description += f"\n{breakpoint_data[1]}"
        embed_msg.add_field(name=glyph_name, value=f"{description}", inline=is_inline)
    return embed_msg


async def allocate_points(player_obj, selected_path, num_change):
    path_type = selected_path.replace("Path of ", "")
    path_location = gli.path_names.index(path_type)
    spent_points = sum(player_obj.player_stats)
    available_points = player_obj.player_level - spent_points
    if available_points < num_change:
        return "Not enough remaining skill points to allocate!"
    player_obj.player_stats[path_location] += num_change
    condensed_stats = ';'.join(map(str, player_obj.player_stats))
    await player_obj.set_player_field("player_stats", condensed_stats)
    return "Skill point has been allocated!"


async def create_path_embed(player_obj):
    colour, _ = sm.get_gear_tier_colours((player_obj.player_echelon + 1) // 2)
    points_msg = "Your shiny toys are useless if you don't know how to use them."
    embed = discord.Embed(color=colour, title="Avalon, The Pathwalker", description=points_msg)
    embed.add_field(name=f"{player_obj.player_username}'s Skill Points", value="", inline=False)
    for path_label, points, gear_points in zip(gli.path_names, player_obj.player_stats, player_obj.gear_points):
        value_msg = f"Points: {points}"
        if gear_points > 0:
            value_msg += f" (+{gear_points})"
        if player_obj.aqua_mode != 0:
            path_label = f"Waterfalls [{path_label}]"
        embed.add_field(name=f"Path of {path_label}", value=value_msg, inline=True)
    spent_points = sum(player_obj.player_stats)
    remaining_points = player_obj.player_level - spent_points
    embed.add_field(name=f"Unspent Points: {remaining_points}", value="", inline=False)
    return embed


async def build_points_embed(player_obj, selected_path, water_converted=False):
    colour, _ = sm.get_gear_tier_colours((player_obj.player_echelon + 1) // 2)
    embed = discord.Embed(color=colour, title=f"{selected_path}", description="Stats per point:\n")
    path_type = selected_path.replace("Path of ", "") if not water_converted else "Waterfalls"
    for modifier in path_perks[path_type]:
        embed.description += f'{modifier[0].replace("X", str(modifier[1]))}\n'

    # Calculate the points.
    if not water_converted:
        points_field = player_obj.player_stats[gli.path_names.index(path_type)]
        gear_points = player_obj.gear_points[gli.path_names.index(path_type)]
    else:
        points_field = player_obj.aqua_points
    points_msg = f"{player_obj.player_username}'s **{selected_path}** points: {points_field}"
    total_points = points_field + gear_points
    if gear_points > 0:
        points_msg += f" (+{gear_points})"
    embed.add_field(name="", value=points_msg, inline=False)

    # Build the embed.
    embed = await display_glyph(path_type, total_points, embed)
    spent_points = sum(player_obj.player_stats)
    remaining_points = player_obj.player_level - spent_points
    embed.add_field(name="", value=f"Remaining Points: {remaining_points}", inline=False)
    return embed


def assign_path_multipliers(player_obj):
    # Path Multipliers
    total_points = [x + y for x, y in zip(player_obj.player_stats, player_obj.gear_points)]

    # Aqua Path exception
    if player_obj.aqua_mode != 0:
        player_obj.aqua_points = sum(total_points)
        total_points = [0] * len(total_points)
        player_obj.appli["Aqua"] += player_obj.aqua_mode // 20
        player_obj.appli["Aqua"] = sum(player_obj.appli.values())
        player_obj.appli = {key: (player_obj.appli["Aqua"] if key == "Aqua" else 0) for key in player_obj.appli}
        player_obj.elemental_res[1] += 0.002 * player_obj.aqua_points
        player_obj.elemental_mult[1] += (0.25 * player_obj.aqua_points) + (100 * player_obj.appli["Aqua"])
        return total_points

    # Storm Path (0)
    storm_bonus = total_points[0]
    for ele_idx in gli.element_dict["Storms"]:
        player_obj.elemental_mult[ele_idx] += 0.05 * storm_bonus
        player_obj.elemental_res[ele_idx] += 0.001 * storm_bonus
    player_obj.critical_mult += 0.03 * storm_bonus
    player_obj.appli["Critical"] += storm_bonus // 20
    if storm_bonus >= 100:
        player_obj.appli["Critical"] += 10

    # Horizon Path (2)
    horizon_bonus = total_points[2]
    for ele_idx in gli.element_dict["Horizon"]:
        player_obj.elemental_mult[ele_idx] += 0.05 * horizon_bonus
        player_obj.elemental_res[ele_idx] += 0.001 * horizon_bonus
    player_obj.bleed_mult += 0.1 * horizon_bonus
    player_obj.appli["Bleed"] += horizon_bonus // 20
    if horizon_bonus >= 80:
        player_obj.bleed_pen *= 2

    # Eclipse Path (3)
    eclipse_bonus = total_points[3]
    for ele_idx in gli.element_dict["Eclipse"]:
        player_obj.elemental_mult[ele_idx] += 0.05 * eclipse_bonus
        player_obj.elemental_res[ele_idx] += 0.001 * eclipse_bonus
    player_obj.ultimate_mult += 0.1 * eclipse_bonus
    player_obj.appli["Ultimate"] += eclipse_bonus // 20

    # Star Path (4)
    star_bonus = total_points[4]
    player_obj.elemental_mult[8] += 0.07 * star_bonus
    player_obj.elemental_res[8] += 0.001 * star_bonus
    player_obj.combo_mult += 0.03 * star_bonus
    star_skill_bonus = 0.25 * star_bonus // 20
    player_obj.skill_damage_bonus[0] += star_skill_bonus
    if star_bonus >= 100:
        player_obj.skill_damage_bonus[1] += player_obj.skill_damage_bonus[0]
        player_obj.skill_damage_bonus[2] += player_obj.skill_damage_bonus[0]

    # Solar Flux Path (5)
    solar_bonus = total_points[5]
    for ele_idx in gli.element_dict["Solar"]:
        player_obj.elemental_mult[ele_idx] += 0.03 * solar_bonus
        player_obj.elemental_res[ele_idx] += 0.001 * solar_bonus
    player_obj.appli["Life"] += solar_bonus // 20
    if total_points[5] >= 100:
        player_obj.hp_bonus *= 2

    # Lunar Tides Path (6)
    lunar_bonus = total_points[6]
    for ele_idx in gli.element_dict["Lunar"]:
        player_obj.elemental_mult[ele_idx] += 0.03 * lunar_bonus
        player_obj.elemental_res[ele_idx] += 0.001 * lunar_bonus
    player_obj.appli["Mana"] += lunar_bonus // 20
    if total_points[6] >= 100:
        player_obj.mana_mult *= 2

    # Terrestria Path (7)
    terrestria_bonus = total_points[7]
    for ele_idx in gli.element_dict["Terrestria"]:
        player_obj.elemental_mult[ele_idx] += 0.03 * terrestria_bonus
        player_obj.elemental_res[ele_idx] += 0.001 * terrestria_bonus
    player_obj.appli["Temporal"] += terrestria_bonus // 20

    # Confluence Path (8)
    confluence_bonus = total_points[5]
    player_obj.all_elemental_mult += 0.02 * confluence_bonus
    player_obj.all_elemental_curse += 0.01 * confluence_bonus
    player_obj.appli["Elemental"] += 2 * confluence_bonus // 20
    if confluence_bonus >= 100:
        player_obj.all_elemental_pen *= 2
        player_obj.all_elemental_curse *= 2

    # Frostfire Path (1)
    frostfire_bonus = total_points[1]
    for ele_idx in gli.element_dict["Frostfire"]:
        player_obj.elemental_mult[ele_idx] += 0.05 * frostfire_bonus
        player_obj.elemental_res[ele_idx] += 0.001 * frostfire_bonus
        player_obj.elemental_pen[ele_idx] += frostfire_bonus // 20
    player_obj.class_multiplier += 0.01 * frostfire_bonus

    def apply_cascade(bonus, data_list):
        temp_list = data_list.copy()
        temp_list[0], temp_list[5] = 0, 0
        highest_index = temp_list.index(max(temp_list))
        data_list[highest_index] += data_list[0] + data_list[5]

    if frostfire_bonus >= 80:
        apply_cascade(player_obj.elemental_mult, frostfire_bonus)
        apply_cascade(player_obj.elemental_pen, frostfire_bonus)
        apply_cascade(player_obj.elemental_curse, frostfire_bonus)
    if frostfire_bonus >= 100:
        for ele_idx in gli.element_dict["Frostfire"]:
            player_obj.elemental_mult[ele_idx] *= 3
            player_obj.elemental_pen[ele_idx] *= 3
            player_obj.elemental_curse[ele_idx] *= 3

    appli_dict = {0: "Critical", 3: "Ultimate", 4: "Combo",
                  5: "Life", 6: "Mana", 7: "Temporal", 8: "Elemental"}
    for idx, points in enumerate(total_points):
        if points >= 80 and idx in appli_dict.keys():
            player_obj.appli[appli_dict[idx]] *= 2
        if points >= 100:
            player_obj.unique_glyph_ability[idx] = True

    return total_points
