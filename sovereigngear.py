# General imports
import random
import pandas as pd

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import inventory
import ring
from tarot import tarot_damage
from pandoradb import run_query as rqy

# weapon name: [(base_dmg_min, base_dmg_max), (attack_speed_min, attack_speed_max),
#               (skill1, skill2, skill3),
#               (Sacred Skills)]
sov_item = {
    "Pandora's Universe Hammer":
        [(9999999, 9999999), (2, 3),
         ("Genesis Dream (TYPE)", "Universal Advent"),
         ("Divine Genesis (TYPE)", "Entwined Universe")],
    "Fallen Lotus of Nephilim":
        [(1, 1), (1, 1),
         ("Blood Blossom", "Phase Breaker"),
         ("Divine Blossom", "Reality Breaker")],
    "Solar Flare Blaster":
        [(1111111, 7777777), (7, 7),
         ("Blazing Dawn [VALUE]%", "Solar Winds"),
         ("Blazing Apex [VALUE]%", "Divine Winds")],
    "Bathyal, Enigmatic Chasm Bauble":
        [(1234567, 7654321), (1, 4),
         ("Mana of the Boundless Ocean", "Disruption Boundary (TYPE)"),
         ("Mana of the Divine Sea", "Forbidden Boundary (TYPE)")],
    "Ruler's Crest":
        [(9999999, 9999999), None,
         ("Ruler's Glare", "Ruler's Tenacity"),
         ("Divine Glare", "Ruler's Aegis")]}

random_values_dict = {"Solar Flare Blaster": (100, 500)}
sov_type_dict = {"Bathyal, Enigmatic Chasm Bauble": ["Critical", "Fractal", "Temporal", "Hyperbleed", "Combo", "Bloom"],
                 "Pandora's Universe Hammer": gli.element_names + gli.path_names[:-4] + ["Omni"]}


def build_sovereign_item(new_item):
    sov_data = sov_item[new_item.item_base_type]
    new_item.base_damage_min, new_item.base_damage_max = sov_data[0]
    if new_item.item_type == "W":
        new_item.item_base_stat = round(random.uniform(sov_data[1][0], sov_data[1][1]), 2)
    # Assign elements
    num_elements = random.choices([num for num in range(9)], weights=[1, 1, 2, 3, 4, 3, 2, 1, 1], k=1)[0]
    element_index_list = random.sample(range(9), num_elements)
    for element_index in element_index_list:
        new_item.item_elements[element_index] = 1
    # Assign data
    skill_data = sov_data[2]
    new_item.item_name = new_item.item_base_type
    if new_item.is_sacred:
        skill_data = sov_data[3]
    # Assign skills
    for idx, skill in enumerate(skill_data):
        skill_text = skill
        if "[VALUE]" in skill:
            value_min, value_max = random_values_dict[new_item.item_base_type]
            skill_text = skill.replace("[VALUE]", f"{random.randint(value_min, value_max):,}")
        elif "(TYPE)" in skill:
            new_type = random.choice(sov_type_dict[new_item.item_base_type])
            skill_text = skill.replace("TYPE", new_type)
        new_item.roll_values.append(skill_text)
    if new_item.item_type == "W":
        new_item.roll_values.append("Sovereign's Omniscience")
    if new_item.is_sacred:
        new_item.roll_values.append("Sacred Core")


def display_sovereign_rolls(item_obj):
    _, augment = sm.get_gear_tier_colours(item_obj.item_tier)
    roll_msg = "".join(f"{augment} {skill}\n" for skill in item_obj.roll_values if skill != "")
    return roll_msg


async def assign_sovereign_values(player_obj, item_obj):
    if item_obj.item_type == "R":
        await ring.assign_ring_values(player_obj, item_obj)
        return
    # Sacred Core
    if item_obj.is_sacred:
        player_obj.defence_pen += 0.5
    # Sovereign's Omniscience is applied directly in damage calc.
    # Sovereign weapon abilities are exceedingly unique and assigned on a case by case basis.
    match item_obj.item_base_type:
        case "Pandora's Universe Hammer":
            variant = item_obj.roll_values[0].split()[2].strip("()")
            if item_obj.is_sacred:
                damage_values = [30, 30, 30]
                raw_query = "SELECT num_stars FROM TarotInventory WHERE player_id = :player_id"
                df = await rqy(raw_query, return_value=True, params={"player_id": player_obj.player_id})
                star_counts = df['num_stars'].value_counts().sort_index()
                dmg_bonus = sum(star_counts.index.map(lambda x: tarot_damage[x]) * star_counts)
                player_obj.player_damage_min, player_obj.player_damage_max = dmg_bonus, dmg_bonus
            else:
                damage_values = [30, 20, 10]
            for ele_idx in gli.element_dict[variant]:
                player_obj.elemental_mult[ele_idx] += damage_values[0]
                player_obj.elemental_pen[ele_idx] += damage_values[1]
                player_obj.elemental_curse[ele_idx] += damage_values[2]
        case "Fallen Lotus of Nephilim":
            player_obj.resist_pen += 0.05 * min(player_obj.capacity, sum(item_obj.item_elements))
            player_obj.unique_conversion[4] = 1
            if item_obj.is_sacred:
                player_obj.resist_pen += 0.25
                player_obj.unique_conversion[4] = 2
            player_obj.hp_multiplier += 0.5
        case "Solar Flare Blaster":
            player_obj.flare_type, reduction_value = "Solar", 99
            if item_obj.is_sacred:
                player_obj.flare_type, reduction_value = "Zenith", 0
            parts = item_obj.roll_values[0].split()
            numeric_value = parts[2].strip("%")
            numeric_value = numeric_value.replace(",", "")
            player_obj.apply_elemental_conversion(gli.element_dict["Solar"], reduction_value, int(numeric_value))
            player_obj.trigger_rate["Status"] = 5
        case "Bathyal, Enigmatic Chasm Bauble":
            parts = item_obj.roll_values[1].split()
            player_obj.perfect_rate[parts[2].strip("()")] = 1
            parts = item_obj.roll_values[1].split()
            numeric_value = parts[5].strip("[]")
            numeric_value = numeric_value.replace(",", "")
            player_obj.mana_limit, player_obj.mana_shatter = int(numeric_value), True
            if item_obj.is_sacred:
                player_obj.appli["Life"] += 5
                player_obj.appli["Mana"] += 5
                player_obj.start_mana = 0
        case "Ruler's Crest":
            player_obj.hp_multiplier += 10
            player_obj.ruler_mult = player_obj.player_level * 0.05
            if item_obj.is_sacred:
                player_obj.hp_multiplier += 10
                player_obj.ruler_mult *= 2
            if item_obj.is_sacred:
                pass
        case _:
            return
