# Data imports
import sharedmethods

# Core imports
import player
import inventory

ring_values_dict = {
    # Elemental Rings
    "Elemental Ring of Fire": [[("Fire Curse X%", "elemental_curse", 100, 0)], (0, None)],
    "Elemental Ring of Water": [[("Water Curse X%", "elemental_curse", 100, 1)], (0, None)],
    "Elemental Ring of Lightning": [[("Lightning Curse X%", "elemental_curse", 100, 2)], (0, None)],
    "Elemental Ring of Earth": [[("Earth Curse X%", "elemental_curse", 100, 3)], (0, None)],
    "Elemental Ring of Wind": [[("Wind Curse X%", "elemental_curse", 100, 4)], (0, None)],
    "Elemental Ring of Ice": [[("Ice Curse X%", "elemental_curse", 100, 5)], (0, None)],
    "Elemental Ring of Shadow": [[("Shadow Curse X%", "elemental_curse", 100, 6)], (0, None)],
    "Elemental Ring of Light": [[("Light Curse X%", "elemental_curse", 100, 7)], (0, None)],
    "Elemental Ring of Celestial": [[("Celestial Curse X%", "elemental_curse", 100, 8)], (0, None)],
    # Primordial Signet
    "Ruby Signet of Incineration": [[("Fire Curse X%", "elemental_curse", 500, 0)], (0, None)],
    "Sapphire Signet of Atlantis": [[("Water Curse X%", "elemental_curse", 500, 1)], (0, None)],
    "Topaz Signet of Dancing Thunder": [[("Lightning Curse X%", "elemental_curse", 500, 2)], (0, None)],
    "Agate Signet of Seismic Tremors": [[("Earth Curse X%", "elemental_curse", 500, 3)], (0, None)],
    "Emerald Signet of Wailing Winds": [[("Wind Curse X%", "elemental_curse", 500, 4)], (0, None)],
    "Zircon Signet of the Frozen Castle": [[("Ice Curse X%", "elemental_curse", 500, 5)], (0, None)],
    "Obsidian Signet of Tormented Souls": [[("Shadow Curse X%", "elemental_curse", 500, 6)], (0, None)],
    "Opal Signet of Scintillation": [[("Light Curse X%", "elemental_curse", 500, 7)], (0, None)],
    "Amethyst Signet of Shifting Stars": [[("Celestial Curse X%", "elemental_curse", 500, 8)], (0, None)],
    # Path Rings
    "Invoking Ring of Storms": [[("Water Curse X%", "elemental_curse", 250, 1),
                                 ("Lightning Curse X%", "elemental_curse", 250, 2)], (10, 0)],
    "Primordial Ring of Frostfire": [[("Fire Curse X%", "elemental_curse", 250, 0),
                                      ("Ice Curse X%", "elemental_curse", 250, 5)], (10, 1)],
    "Boundary Ring of Horizon": [[("Earth Curse X%", "elemental_curse", 250, 3),
                                  ("Wind Curse X%", "elemental_curse", 250, 4)], (10, 2)],
    "Hidden Ring of Eclipse": [[("Shadow Curse X%", "elemental_curse", 250, 6),
                                ("Light Curse X%", "elemental_curse", 250, 7)], (10, 3)],
    "Cosmic Ring of Stars": [[("Celestial Curse X%", "elemental_curse", 1000, 8)], (10, 4)],
    "Rainbow Ring of Confluence": [[("Omni Curse X%", "all_elemental_curse", 200, None)], (10, 5)],
    "Lonely Ring of Solitude": [[("Singularity Curse X%", "singularity_curse", 750, None)], (10, 6)],
    # Legendary Rings
    "Dragon's Eye Diamond": [[("Critical Rate is always X%", "perfect_crit", 100, None),
                              ("Critical Damage X%", "critical_multiplier", 500, None)], (100, None)],
    "Chromatic Tears": [[("Omni Curse X%", "all_elemental_curse", 500, None)], (0, None)],
    "Bleeding Hearts": [[("bleed_application +X", "bleed_application", 5, None)], (0, None)],
    "Gambler's Masterpiece": [[("All-In!", "rng_bonus", 777, None)], (0, None)],
    # Sovereign Rings
    "Stygian Calamity": [[("X% chance for Non-Bloom hits to trigger Calamity", "spec_conv", 99, 2)],
                         [("X% Hybrid Curse (Chaos)", "elemental_curse", 999, (0, 2, 3, 6))], (0, None)],
    "Sacred Ring of Divergent Stars": [[("X% chance for Bloom hits to trigger Sacred Bloom", "spec_conv", 50, 0)],
                                       [("X% chance for Non-Bloom hits to trigger Abyssal Bloom", "spec_conv", 50, 1)],
                                       [("Omni Curse X%", "all_elemental_curse", 300, None)], (0, None)],
    "Crown of Skulls": [["Avaricious Ruin", "Banquet of Bones"], (0, None)]
}


def assign_ring_values(player_obj, ring_equipment):
    bonuses, (points, path_index) = ring_values_dict[ring_equipment.item_base_type]
    if points > 0:
        player_obj.gear_points[path_index] += points
    player_obj.final_damage += ring_equipment.item_tier * 0.1
    player_obj.hp_bonus += ring_equipment.item_tier * 500
    player_obj.attack_speed += ring_equipment.item_tier * 0.05
    # Exit on ring exceptions.
    if ring_equipment.item_base_type == "Crown of Skulls":
        return
    # Handle everything else
    for (attr_name, attr, value, index) in bonuses:
        percent_adjust = 0.01 if "Application" not in attr_name and "All-In" not in attr_name else 1
        if index is None:
            setattr(player_obj, attr, getattr(player_obj, attr, 0) + value * percent_adjust)
        else:
            target_list = getattr(player_obj, attr)
            target_list[index] += value * percent_adjust


def display_ring_values(ring_equipment):
    output = ""
    bonuses, (points, path_index) = ring_values_dict[ring_equipment.item_base_type]
    _, augment = sharedmethods.get_gear_tier_colours(ring_equipment.item_tier)
    if points > 0:
        output += f"Path of {globalitems.path_names[path_index]} +{points}\n"
    output += f"{augment} HP Bonus +{ring_equipment.item_tier * 500:,}\n"
    output += f"{augment} Final Damage {ring_equipment.item_tier * 10:,}%\n"
    output += f"{augment} Attack Speed {ring_equipment.item_tier * 5:,}%\n"
    # Handle rings with unique scaling.
    if ring_equipment.item_base_type in ["Crown of Skulls"]:
        for idx, bonus in enumerate(ring_equipment.item_roll_values):
            output += f"{bonuses[idx]} [{bonus:,}]\n" if bonus >= 0 else ""
        return output
    # Handle all other rings bonuses.
    for (attr_name, _, value, index) in bonuses:
        output += f"{augment} {attr_name.replace('X', f'{value:,}')}\n"
    return output

