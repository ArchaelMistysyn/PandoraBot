import inventory
import globalitems as gli

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
                           {"Restored": 2000, "Deviation": 2000, "Big Bang": 4000, "Spectrum": 2000}}
type_dict = {"Restored": gli.element_names, "Deviation": gli.path_names[:-3],
             "Big Bang": ["Stars"], "Spectrum": ["Omni"]}


def assign_sovereign_data(new_item):
    sov_data = sov_weapon[new_item.item_base_type]
    new_item.base_damage_min, new_item.base_damage_max = sov_data[0]
    new_item.item_base_stat = round(random.uniform(sov_data[1][0], sov_data[1][1]), 2)
    # Assign elements
    element_index_list = random.sample(range(9), random.randint(1, 9))
    for element_index in element_index_list:
        new_item.item_elements[element_index] = 1
    # Assign variant
    variant = ""
    if sov_data[3] is not None:
        variant_name = random.choices(sov_data[3], weights=sov_data[4], k=1)[0]
        variant = f" [{variant_name}]"
    new_item.item_name = f"{new_item.item_base_type}{variant}"
    # Assign skills
    for idx, skill in enumerate(sov_data[1]):
        skill_text = skill
        if "[VALUE]" in skill:
            value_min, value_max = values_dict[new_item.item_base_type]
            skill_text = skill.replace("[VALUE]", f"{random.randint(value_min, value_max):,}")
        elif "(TYPE)" in skill:
            new_type = random.choice(type_dict[variant_name])
            skill_text = skill.replace("(TYPE)", new_type)
            skill_text = skill_text.replace("X", f"{variant_values_dict[variant_name]:,}")
        new_item.roll_values[idx] = skill


def assign_sovereign_values():
    pass
