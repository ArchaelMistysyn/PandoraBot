import csv
import random
import bosses
import damagecalc
import pandas as pd

class CustomWeapon:
    def __init__(self, player_owner):
        self.player_owner = player_owner
        self.item_id = 1

        random_num = random.randint(1, 100)
        if random_num <= 1:
            temp_tier = 4
            temp_min = 50
            temp_max = 50
            temp_attack_speed = 1.5
        elif random_num <= 6:
            temp_tier = 3
            temp_min = 10
            temp_max = 35
            temp_attack_speed = 1.3
        elif random_num <= 21:
            temp_tier = 2
            temp_min = 5
            temp_max = 30
            temp_attack_speed = 1.2
        else:
            temp_tier = 1
            temp_min = 1
            temp_max = 25
            temp_attack_speed = 1.1

        self.item_base_tier = temp_tier
        self.base_damage_min = temp_min
        self.base_damage_max = temp_max
        self.base_attack_speed = temp_attack_speed

        self.item_num_sockets = 0
        self.item_inlaid_gem_id = ""
        self.item_num_stars = 1
        self.item_suffix_values = ""
        self.item_prefix_values = ""

        self.item_enhancement = 0
        self.item_num_elements = 1
        self.item_elements = bosses.get_element()
        self.item_damage_type = generate_weapon_type()
        if self.item_damage_type != "<:esummon:1143754335478616114>":
            self.item_material_tier = "Wood"
            self.item_blessing_tier = "Sturdy"
        else:
            self.item_material_tier = "Faint"
            self.item_blessing_tier = "Essence"
        self.item_weapon_type = generate_weapon_base(self.item_base_tier, self.item_damage_type)
        self.weapon_damage_min = damagecalc.weapon_damage_calc(self.base_damage_min, self.item_material_tier,
                                                    self.item_blessing_tier, self.base_attack_speed)
        self.weapon_damage_max = damagecalc.weapon_damage_calc(self.base_damage_min, self.item_material_tier,
                                                    self.item_blessing_tier, self.base_attack_speed)

        self.item_name = self.generate_item_name()

    # return the boss display string
    def __str__(self):
        item_output = "**" + self.item_name + "**" + "\n"
        for x in range(self.item_num_stars):
            item_output += "<:estar1:1143756443967819906>"
        item_output += "\n" + self.item_damage_type + self.item_elements
        item_output += "\nWeapon Damage: " + str(self.weapon_damage_min) + " - " + str(self.weapon_damage_max)
        item_output += " Attack Speed: " + str(self.base_attack_speed) + "/min"
        return item_output

    def generate_item_name(self) -> str:
        item_name = "+" + str(self.item_enhancement) + " " + self.item_blessing_tier + " " + self.item_material_tier
        item_name += " " + self.item_weapon_type
        return item_name


def generate_weapon_type() -> str:
    random_num = random.randint(1, 9)
    match random_num:
        case 1 | 2 | 3:
            damage_type = "<:emelee:1141654530619088906>"
        case 3 | 4 | 5:
            damage_type = "<:eranged:1141654478748135545>"
        case 6 | 7 | 8:
            damage_type = "<:emagical:1143754281846059119>"
        case _:
            damage_type = "<:esummon:1143754335478616114>"
    return damage_type


def generate_weapon_base(item_tier, damage_type) -> str:

    random_num = random.randint(1, 5)
    if item_tier == 4:
        random_num *= random.randint(1,3)
    else:
        random_num += (item_tier - 1) * 5

    match damage_type:
        case "<:emelee:1141654530619088906>":
            match random_num:
                case 1:
                    item_base = "Axe"
                case 2:
                    item_base = "Halberd"
                case 3:
                    item_base = "Dagger"
                case 4:
                    item_base = "Torch"
                case 5:
                    item_base = "Spear"
                case 6:
                    item_base = "Longsword"
                case 7:
                    item_base = "Greatsword"
                case 8:
                    item_base = "Claws"
                case 9:
                    item_base = "Hammer"
                case 10:
                    item_base = "Trident"
                case 11:
                    item_base = "Tree"
                case 12:
                    item_base = "Chakram"
                case 13:
                    item_base = "Scythe"
                case 14:
                    item_base = "Glaive"
                case _:
                    item_base = "Energy Blade"
        case "<:eranged:1141654478748135545>":
            match random_num:
                case 1:
                    item_base = "Slingshot"
                case 2:
                    item_base = "Rock"
                case 3:
                    item_base = "Kunai"
                case 4:
                    item_base = "Darts"
                case 5:
                    item_base = "Crossbow"
                case 6:
                    item_base = "Longbow"
                case 7:
                    item_base = "Whip"
                case 8:
                    item_base = "Harpoon"
                case 9:
                    item_base = "Ballista"
                case 10:
                    item_base = "Greatbow"
                case 11:
                    item_base = "Cannon"
                case 12:
                    item_base = "Gun"
                case 13:
                    item_base = "Threads"
                case 14:
                    item_base = "Flamethrower"
                case _:
                    item_base = "Blaster"
        case "<:emagical:1143754281846059119>":
            match random_num:
                case 1:
                    item_base = "Wand"
                case 2:
                    item_base = "Staff"
                case 3:
                    item_base = "Sceptre"
                case 4:
                    item_base = "Talisman"
                case 5:
                    item_base = "Lantern"
                case 6:
                    item_base = "Rod"
                case 7:
                    item_base = "Orb"
                case 8:
                    item_base = "Spellbook"
                case 9:
                    item_base = "Grimoire"
                case 10:
                    item_base = "Skull"
                case 11:
                    item_base = "Necronomicon"
                case 12:
                    item_base = "Jeweled Implement"
                case 13:
                    item_base = "Krosse"
                case 14:
                    item_base = "Chalice"
                case _:
                    item_base = "Mirror"
        case _:
            match random_num:
                case 1:
                    item_base = "Skeleton"
                case 2:
                    item_base = "Wolf"
                case 3:
                    item_base = "Golem"
                case 4:
                    item_base = "Butterfly"
                case 5:
                    item_base = "Lynx"
                case 6:
                    item_base = "Wyvern"
                case 7:
                    item_base = "Basilisk"
                case 8:
                    item_base = "Shark"
                case 9:
                    item_base = "Whale"
                case 10:
                    item_base = "Wyrm"
                case 11:
                    item_base = "Unicorn"
                case 12:
                    item_base = "Dragon"
                case 13:
                    item_base = "Phoenix"
                case 14:
                    item_base = "Hydra"
                case _:
                    item_base = "Fish"

    return item_base


# write item to inventory
def inventory_add_weapon(item: CustomWeapon) -> str:
    # file specifications
    filename = 'inventory.csv'

    # wpn name and id
    player_id = item.player_owner
    wpn_id = item.item_id
    wpn_name = item.item_name

    # wpn elements and damage type
    num_elements = item.item_num_elements
    wpn_elements = item.item_elements
    wpn_damage_type = item.item_damage_type

    # wpn damage adjustments
    wpn_enhancement = item.item_enhancement
    wpn_blessing_tier = item.item_blessing_tier
    wpn_material_tier = item.item_material_tier

    # wpn rolls
    num_stars = item.item_num_stars
    wpn_prefix_values = item.item_prefix_values
    wpn_suffix_values = item.item_suffix_values

    # wpn base damage
    wpn_atk_spd = item.base_attack_speed
    wpn_base_dmg_min = item.base_damage_min
    wpn_base_dmg_max = item.base_damage_max



    # insert wpn into csv file
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([player_id, wpn_id, wpn_name,
                         num_elements, wpn_elements, wpn_damage_type,
                         wpn_enhancement, wpn_blessing_tier, wpn_material_tier,
                         num_stars, wpn_prefix_values, wpn_suffix_values,
                         wpn_atk_spd, wpn_base_dmg_min, wpn_base_dmg_max])

    return 'You have placed the item in your inventory'


# check if item already exists. Prevent duplication
def if_exists(filename: str, item_id: int) -> bool:
    df = pd.read_csv(filename)
    if str(item_id) in df['wpn_id'].values:
        return True
    else:
        return False


def read_custom_weapon(filename: str, weapon_id: int) -> str:
    weapon_info = ''
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['wpn_id'] == weapon_id:
                weapon_info = row

    return weapon_info