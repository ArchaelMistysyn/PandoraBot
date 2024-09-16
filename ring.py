# Data imports
import sharedmethods as sm
import globalitems as gli
from ringdata import ring_values_dict as rvd

# Core imports
import player
import inventory
import tarot

scaling_rings = ["Crown of Skulls", "Chromatic Tears"]


async def assign_ring_values(player_obj, e_ring):
    # Sacred Core
    if e_ring.is_sacred:
        player_obj.defence_pen += 0.5
    bonuses, (points, path_index), _ = rvd[e_ring.item_base_type]
    if points > 0:
        player_obj.gear_points[path_index] += points
    player_obj.final_damage += e_ring.item_tier * 0.1
    player_obj.attack_speed += e_ring.item_tier * 0.05
    # Exit on ring exceptions.
    if e_ring.item_base_type in scaling_rings:
        if e_ring.item_base_type == "Chromatic Tears":
            player_obj.all_elemental_mult += e_ring.roll_values[1] // 100
            player_obj.all_elemental_pen += e_ring.roll_values[1] // 100
            player_obj.all_elemental_curse += (e_ring.roll_values[0] // 100) + (e_ring.roll_values[1] // 100)
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


async def display_ring_values(e_ring):
    player_obj = await player.get_player_by_id(e_ring.player_owner) if e_ring.player_owner > 0 else None
    output = ""
    bonuses, (points, path_index), _ = rvd[e_ring.item_base_type]
    _, augment = sm.get_gear_tier_colours(e_ring.item_tier)
    if points > 0:
        output += f"Path of {gli.path_names[path_index]} +{points}\n"
    output += f"{augment} Final Damage {e_ring.item_tier * 10:,}%\n"
    output += f"{augment} Attack Speed {e_ring.item_tier * 5:,}%\n"
    # Handle rings with unique scaling.
    if e_ring.item_base_type in scaling_rings:
        output += f"{augment} {bonuses[0]} [{int(e_ring.roll_values[0]):,}]\n"
        output += f"{augment} {bonuses[1]} [{int(e_ring.roll_values[1]):,}]\n"
        resonance_index = int(e_ring.roll_values[2])
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
    if e_ring.item_tier == 8 and e_ring.item_base_type not in ["Hadal's Raindrop"]:
        resonance_index = int(e_ring.roll_values[0])
        resonance = f"{augment} Resonance [{await tarot.get_resonance(resonance_index)}]\n"
        if player_obj is not None and player_obj.equipped_tarot != "":
            if player_obj.equipped_tarot == tarot.get_key_by_index(resonance_index):
                resonance = f"**{resonance}**"
        output += resonance
    if e_ring.is_sacred:
        output += f"{augment} Sacred Core\n"
    return output

