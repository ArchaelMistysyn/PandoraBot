import csv


# write item to inventory
def test_create_csv() -> str:
    # file specifications
    filename = 'testing.csv'
    wpn_id = 1

    # wpn elements
    num_elements = 2
    wpn_elements = ["Fire", "Lightning"]

    # wpn rolls
    num_rolls = 1
    num_stars = num_rolls - 1
    wpn_rolls = ["Elemental Penetration"]
    wpn_rolls_value = ["10%"]

    # wpn name details
    wpn_blessing_tier = "Sturdy"
    wpn_blessing_value = 25
    wpn_material = "Wooden"
    wpn_material_value_min = 1
    wpn_material_value_max= 25
    wpn_base_type = "Sword"

    # wpn specifications
    wpn_enhancement = 0
    wpn_sharpness = 0
    wpn_atk_spd = 1.5

    wpn_base_dmg_min = (wpn_material_value_min * (1 + wpn_enhancement) * (1 + wpn_sharpness)) + wpn_blessing_value
    wpn_base_dmg_max = (wpn_material_value_max * (1 + wpn_enhancement) * (1 + wpn_sharpness)) + wpn_blessing_value

    # wpn name
    wpn_name = "+" + str(wpn_enhancement) + " " + str(wpn_blessing_tier) + " " + str(wpn_material)
    wpn_name += " " + str(wpn_base_type)

    # insert wpn into csv file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["wpn_id", "wpn_name",
                 "wpn_enhancement", "wpn_sharpness", "num_elements", "wpn_elements",
                 "wpn_base_dmg_min", "wpn_base_dmg_max", "wpn_material", "wpn_base_type"
                 "num_rolls", "item_rolls", "wpn_rolls_value"]

        writer.writerow(field)
        writer.writerow([wpn_id, wpn_name,
                         wpn_enhancement, wpn_sharpness, num_elements, wpn_elements,
                         wpn_base_dmg_min, wpn_base_dmg_max, wpn_material, wpn_base_type,
                         num_rolls, wpn_rolls, wpn_rolls_value])

    return 'success'


def read_custom_weapon(filename: str, weapon_id: int) -> str:
    weapon_info = ''
    with open('filename.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['wpn_id']==weapon_id:
                weapon_info = row


    return weapon_info