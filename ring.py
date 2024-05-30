# Data imports
import sharedmethods as sm
from ringdata import ring_values_dict as rvd

# Core imports
import player
import inventory
import tarot


def assign_ring_values(player_obj, ring_equipment):
    bonuses, (points, path_index) = rvd[ring_equipment.item_base_type]
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
        if attr is None or attr_name == "[RESONANCE]":
            continue
        percent_adjust = 0.01 if "Application" not in attr_name and "All-In" not in attr_name else 1
        if index is None:
            setattr(player_obj, attr, getattr(player_obj, attr, 0) + value * percent_adjust)
        else:
            target_list = getattr(player_obj, attr)
            target_list[index] += value * percent_adjust


def display_ring_values(ring_equipment):
    output = ""
    bonuses, (points, path_index) = rvd[ring_equipment.item_base_type]
    _, augment = sm.get_gear_tier_colours(ring_equipment.item_tier)
    if points > 0:
        output += f"Path of {gli.path_names[path_index]} +{points}\n"
    output += f"{augment} HP Bonus +{ring_equipment.item_tier * 500:,}\n"
    output += f"{augment} Final Damage {ring_equipment.item_tier * 10:,}%\n"
    output += f"{augment} Attack Speed {ring_equipment.item_tier * 5:,}%\n"
    # Handle rings with unique scaling.
    if ring_equipment.item_base_type in ["Crown of Skulls"]:
        output += f"{bonuses[0]} [{ring_equipment.item_roll_values[0]:,}]\n"
        output += f"{bonuses[1]} [{ring_equipment.item_roll_values[1]:,}]\n"
        output += f"**Resonance [{tarot.get_resonance(ring_equipment.item_roll_values[2])}]**"
        return output
    # Handle all other rings bonuses.
    for (attr_name, _, value, index) in bonuses:
        if attr_name == "[RESONANCE]":
            resonance_index = index if ring_equipment.item_tier != 8 else ring_equipment.item_roll_values[0]
            resonance = f"**Resonance [{tarot.get_resonance(resonance_index)}]**"
            output += f"{augment} {resonance}\n"
            continue
        output += f"{augment} {attr_name.replace('X', f'{value:,}')}\n"
    return output

