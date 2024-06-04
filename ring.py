# Data imports
import sharedmethods as sm
import globalitems as gli
from ringdata import ring_values_dict as rvd

# Core imports
import player
import inventory
import tarot


async def assign_ring_values(player_obj, ring_equipment):
    bonuses, (points, path_index), _ = rvd[ring_equipment.item_base_type]
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
            if isinstance(index, tuple):
                for idx in index:
                    target_list[idx] += value * percent_adjust
            else:
                target_list = getattr(player_obj, attr)
                target_list[index] += value * percent_adjust


async def display_ring_values(ring_equipment):
    player_obj = await player.get_player_by_id(ring_equipment.player_owner) if ring_equipment.player_owner > 0 else None
    output = ""
    bonuses, (points, path_index), _ = rvd[ring_equipment.item_base_type]
    _, augment = sm.get_gear_tier_colours(ring_equipment.item_tier)
    if points > 0:
        output += f"Path of {gli.path_names[path_index]} +{points}\n"
    output += f"{augment} HP Bonus +{ring_equipment.item_tier * 500:,}\n"
    output += f"{augment} Final Damage {ring_equipment.item_tier * 10:,}%\n"
    output += f"{augment} Attack Speed {ring_equipment.item_tier * 5:,}%\n"
    # Handle rings with unique scaling.
    if ring_equipment.item_base_type in ["Crown of Skulls"]:
        output += f"{augment} {bonuses[0]} [{int(ring_equipment.roll_values[0]):,}]\n"
        output += f"{augment} {bonuses[1]} [{int(ring_equipment.roll_values[1]):,}]\n"
        resonance_index = int(ring_equipment.roll_values[2])
        resonance = f"{augment} Resonance [{await tarot.get_resonance(resonance_index)}]"
        if player_obj is not None and player_obj.equipped_tarot != "":
            if player_obj.equipped_tarot == tarot.get_key_by_index(resonance_index):
                resonance = f"**{resonance}**"
        output += resonance
        return output
    # Handle all other rings bonuses.
    for (attr_name, _, value, index) in bonuses:
        if attr_name == "[RESONANCE]":
            resonance_index = index
            resonance = f"{augment} Resonance [{await tarot.get_resonance(int(resonance_index))}]"
            if player_obj is not None and player_obj.equipped_tarot != "":
                if player_obj.equipped_tarot == tarot.get_key_by_index(resonance_index):
                    resonance = f"**{resonance}**"
            output += resonance
            continue
        output += f"{augment} {attr_name.replace('X', f'{value:,}')}\n"
    # Handle sovereign rings.
    if ring_equipment.item_tier == 8 and ring_equipment.item_base_type not in ["Hadal's Teardrop"]:
        resonance_index = int(ring_equipment.roll_values[0])
        resonance = f"{augment} Resonance [{await tarot.get_resonance(resonance_index)}]\n"
        if player_obj is not None and player_obj.equipped_tarot != "":
            if player_obj.equipped_tarot == tarot.get_key_by_index(resonance_index):
                resonance = f"**{resonance}**"
        output += resonance
    return output

