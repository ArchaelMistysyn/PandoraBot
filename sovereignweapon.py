import inventory
import random
import globalitems as gli
import sharedmethods as sm

# weapon name: [(base_dmg_min, base_dmg_max), (attack_speed_min, attack_speed_max),
#               (skill1, skill2, skill3),
#               variants, weights]
sov_weapon = {"Pandora's Universe Hammer":
              [(9999999, 9999999), (2, 3),
               ("Genesis Dream X% (TYPE)", "Resonance Override", "Sovereign's Omniscience"),
               ["Restored", "Deviation", "Big Bang", "Spectrum"], [50, 45, 4, 1]],
              "Fallen Lotus of Nephilim":
              [(1, 1), (1, 1),
               ("Phase Breaker", "Blood Bloom", "Sovereign's Omniscience"),
               None, None],
              "Solar Flare Blaster":
              [(1111111, 7777777), (7, 7),
               ("Solar Winds [VALUE]%", "Chain Flare", "Sovereign's Omniscience"),
               None, None],
              "Bathyal, Chasm Bauble":
              [(1234567, 7654321), (1, 4),
               ("Disruption Boundary", "Mana of the Boundless Ocean", "Sovereign's Omniscience"),
               ["Enigma", "Shrouded", "Clear"], [60, 30, 10]]}

random_values_dict = {"Solar Flare Blaster": (100, 500)}
variant_values_dict = {"Pandora's Universe Hammer":
                       {"Restored": 1000, "Deviation": 1000, "Big Bang": 2000, "Spectrum": 1000}}
variant_type_dict = {"Restored": gli.element_names, "Deviation": gli.path_names[:-3],
                     "Big Bang": ["Stars"], "Spectrum": ["Omni"]}
non_variant_type_dict = {"Bathyal, Chasm Bauble": ["Critical", "Fractal", "Time Lock", "Hyperbleed", "Bloom"]}


def build_sovereign_item(new_item):
    sov_data = sov_weapon[new_item.item_base_type]
    new_item.base_damage_min, new_item.base_damage_max = sov_data[0]
    new_item.item_base_stat = round(random.uniform(sov_data[1][0], sov_data[1][1]), 2)
    # Assign elements
    element_index_list = random.sample(range(9), random.randint(1, 9))
    for element_index in element_index_list:
        new_item.item_elements[element_index] = 1
    # Assign variant
    variant, variant_name = "", None
    if sov_data[3] is not None:
        variant_name = random.choices(sov_data[3], weights=sov_data[4], k=1)[0]
        variant = f" [{variant_name}]"
    new_item.item_name = f"{new_item.item_base_type}{variant}"
    # Assign skills
    for idx, skill in enumerate(sov_data[2]):
        skill_text = skill
        if "[VALUE]" in skill:
            value_min, value_max = random_values_dict[new_item.item_base_type]
            skill_text = skill.replace("[VALUE]", f"{random.randint(value_min, value_max):,}")
        elif "(TYPE)" in skill:
            if variant_name is not None:
                new_type = random.choice(variant_type_dict[variant_name])
            else:
                new_type = random.choice(non_variant_type_dict[new_item.item_base_type])
            skill_text = skill.replace("TYPE", new_type)
            if "X" in skill_text:
                skill_text = skill_text.replace("X", f"{variant_values_dict[new_item.item_base_type][variant_name]:,}")
        new_item.roll_values.append(skill_text)


def display_sovereign_rolls(item_obj):
    _, augment = sm.get_gear_tier_colours(item_obj.item_tier)
    roll_msg = "".join(f"{augment} {skill}\n" for skill in item_obj.roll_values if skill != "")
    return roll_msg


async def assign_sovereign_values(player_obj, item_obj):
    # Sovereign's Omniscience is applied directly in damage calc.
    # Sovereign weapon abilities are exceedingly unique and assigned on a case by case basis.
    match item_obj.item_base_type:
        case "Pandora's Universe Hammer":
            # Genesis Dream
            parts = item_obj.roll_values[0].split()
            numeric_value = parts[2].strip("%")
            numeric_value = numeric_value.replace(",", "")
            damage_value, variant = (int(numeric_value) / 100), parts[3].strip("()")
            for ele_idx in gli.element_dict[variant]:
                player_obj.elemental_mult[ele_idx] += damage_value
                player_obj.elemental_pen[ele_idx] += damage_value
                player_obj.elemental_curse[ele_idx] += damage_value
            # Resonance Override
        case "Fallen Lotus of Nephilim":
            # Phase Breaker
            pass
            # Blood Blossom
        case "Solar Flare Blaster":
            # Solar Winds
            parts = item_obj.roll_values[0].split()
            numeric_value = parts[2].strip("%")
            numeric_value = numeric_value.replace(",", "")
            player_obj.apply_elemental_conversion(gli.element_dict["Solar"], 99, int(numeric_value))
            player_obj.trigger_rate["Status"] += 10
            # Chain Flare
            player_obj.spec_conv["Chain Flare"] = True
        case "Bathyal, Chasm Bauble":
            # Disruption Boundary
            parts = item_obj.roll_values[1].split()
            player_obj.perfect_rate[parts[2].strip("()")] = 1
            # Mana of the Boundless Ocean
            parts = item_obj.roll_values[1].split()
            numeric_value = parts[5].strip("[]")
            numeric_value = numeric_value.replace(",", "")
            player_obj.mana_limit, player_obj.mana_shatter = int(numeric_value), True
        case _:
            return
