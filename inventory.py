import csv
import random
import bosses
import damagecalc
import pandas as pd
import player
import discord


class CustomItem:
    def __init__(self, player_owner):
        # initialize owner id
        self.player_owner = player_owner
        # generate item_tier
        random_num = random.randint(1, 100)
        if random_num <= 1:
            temp_tier = 4
            temp_min = 50
            temp_max = 50
        elif random_num <= 6:
            temp_tier = 3
            temp_min = 10
            temp_max = 35
        elif random_num <= 21:
            temp_tier = 2
            temp_min = 5
            temp_max = 30
        else:
            temp_tier = 1
            temp_min = 1
            temp_max = 25

        self.item_base_tier = temp_tier
        self.base_damage_min = temp_min
        self.base_damage_max = temp_max

        # initialize default values
        self.item_num_sockets = 0
        self.item_inlaid_gem_id = ""
        self.item_num_stars = 1
        self.item_suffix_values = ""
        self.item_prefix_values = ""
        self.item_material_tier = "Iron"
        self.item_blessing_tier = "Inert"
        self.item_enhancement = 0
        self.item_elements = []
        self.item_bonus_stat = 0
        self.item_damage_min = 0
        self.item_damage_max = 0


class CustomWeapon(CustomItem):
    def __init__(self, player_owner):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_id = "W" + str(1 + df['item_id'].count())

        # generate weapon specifications
        self.item_damage_type = generate_weapon_type()
        self.item_type = generate_weapon_base(self.item_base_tier, self.item_damage_type)

        # generate the weapon name
        if self.item_damage_type == "<:esummon:1143754335478616114>":
            self.item_blessing_tier = "Standard"
            self.item_material_tier = "Illusion"

        # set attack speed
        match self.item_base_tier:
            case 4:
                temp_attack_speed = 1.5
            case 3:
                temp_attack_speed = 1.3
            case 2:
                temp_attack_speed = 1.2
            case _:
                temp_attack_speed = 1.1

        self.item_bonus_stat = temp_attack_speed

        # set element
        self.item_elements = bosses.get_element()

        # calculate item's damage per hit
        self.item_damage_min = damagecalc.item_damage_calc(self.base_damage_min, self.item_material_tier,
                                                           self.item_blessing_tier)
        self.item_damage_max = damagecalc.item_damage_calc(self.base_damage_max, self.item_material_tier,
                                                           self.item_blessing_tier)

        # set the item name
        self.item_name = generate_item_name(self.item_enhancement, self.item_blessing_tier, self.item_material_tier,
                                            self.item_type)


class CustomArmour(CustomItem):
    def __init__(self, player_owner):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_id = "A" + str(1 + df['item_id'].count())

        # generate armour specifications
        self.item_damage_type = ""
        self.item_type = generate_armour_base(self.item_base_tier)

        # set damage mitigation
        match self.item_base_tier:
            case 4:
                temp_mitigation = 25
            case 3:
                temp_mitigation = 15
            case 2:
                temp_mitigation = 10
            case _:
                temp_mitigation = 5

        self.item_bonus_stat = temp_mitigation

        # calculate item's damage per hit
        self.item_damage_min = damagecalc.item_damage_calc(self.base_damage_min, self.item_material_tier,
                                                           self.item_blessing_tier)
        self.item_damage_max = damagecalc.item_damage_calc(self.base_damage_max, self.item_material_tier,
                                                           self.item_blessing_tier)

        # set the item name
        self.item_name = generate_item_name(self.item_enhancement, self.item_blessing_tier, self.item_material_tier,
                                            self.item_type)


class CustomAccessory(CustomItem):
    def __init__(self, player_owner):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_id = "Y" + str(1 + df['item_id'].count())

        # generate armour specifications
        self.item_damage_type = ""
        self.item_type = generate_accessory_base()

        self.item_material_tier = "Crude"

        random_num = random.randint(1,4)
        # set accessory unique skill
        match self.item_base_tier:
            case 4:
                match random_num:
                    case 1:
                        temp_unique_skill = "Curse of Immorality"
                    case _:
                        temp_unique_skill = "Perfect Counter"
            case 3:
                match random_num:
                    case 1:
                        temp_unique_skill = "Coup de Grace"
                    case 2:
                        temp_unique_skill = "Final Stand"
                    case 3:
                        temp_unique_skill = "Mountain's Will"
                    case _:
                        temp_unique_skill = "Inferno's Will"
            case 2:
                match random_num:
                    case 1:
                        temp_unique_skill = "Breaker"
                    case 2:
                        temp_unique_skill = "Last Breath"
                    case 3:
                        temp_unique_skill = "Guardian Stance"
                    case _:
                        temp_unique_skill = "Onslaught Stance"
            case _:
                match random_num:
                    case 1:
                        temp_unique_skill = "First Blood"
                    case 2:
                        temp_unique_skill = "Hybrid Stance"
                    case 3:
                        temp_unique_skill = "Defensive Stance"
                    case _:
                        temp_unique_skill = "Offensive Stance"

        self.item_bonus_stat = temp_unique_skill
        # calculate item's damage per hit
        self.item_damage_min = damagecalc.item_damage_calc(self.base_damage_min, self.item_material_tier,
                                                           self.item_blessing_tier)
        self.item_damage_max = damagecalc.item_damage_calc(self.base_damage_max, self.item_material_tier,
                                                           self.item_blessing_tier)

        # set the item name
        self.item_name = generate_item_name(self.item_enhancement, self.item_blessing_tier, self.item_material_tier,
                                            self.item_type)


def generate_item_name(item_enhancement, item_blessing_tier, item_material_tier, item_type) -> str:
    item_name = "+" + str(item_enhancement) + " " + item_blessing_tier + " " + item_material_tier
    item_name += " " + item_type
    return item_name


def read_weapon(item_id: str) -> CustomWeapon:
    filename = 'cinventory.csv'
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['item_id']) == str(item_id):
                player_id = int(line['player_id'])
                target_item = CustomWeapon(player_id)
                target_item.player_owner = player_id
                target_item.item_id = item_id
                target_item.item_name = str(line['item_name'])
                target_item.item_elements = str(line['item_elements']).split(';')
                target_item.item_damage_type = str(line['item_damage_type'])
                target_item.item_enhancement = int(line['item_enhancement'])
                target_item.item_base_tier = int(line['item_base_tier'])
                target_item.item_blessing_tier = str(line['item_blessing_tier'])
                target_item.item_material_tier = str(line['item_material_tier'])
                target_item.item_num_stars = int(line['item_num_stars'])
                target_item.item_prefix_values = str(line['item_prefix_values'])
                target_item.item_suffix_values = str(line['item_suffix_values'])
                target_item.item_bonus_stat = str(line['item_bonus_stat'])
                target_item.item_base_damage_min = int(line['item_base_dmg_min'])
                target_item.item_base_damage_max = int(line['item_base_dmg_max'])
                target_item.item_num_sockets = int(line['item_num_sockets'])
                target_item.item_inlaid_gem_id = str(line['item_inlaid_gem_id'])
                target_item.item_damage_min = damagecalc.item_damage_calc(target_item.item_base_damage_min,
                                                                          target_item.item_material_tier,
                                                                          target_item.item_blessing_tier)
                target_item.item_damage_max = damagecalc.item_damage_calc(target_item.item_base_damage_max,
                                                                          target_item.item_material_tier,
                                                                          target_item.item_blessing_tier)
                break

    return target_item


def display_weapon(item_id):
    x = 1


def read_armour(item_id: str) -> CustomArmour:
    filename = 'cinventory.csv'
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['item_id']) == str(item_id):
                player_id = int(line['player_id'])
                target_item = CustomArmour(player_id)
                target_item.player_owner = player_id
                target_item.item_id = item_id
                target_item.item_name = str(line['item_name'])
                target_item.item_elements = str(line['item_elements']).split(';')
                target_item.item_damage_type = str(line['item_damage_type'])
                target_item.item_enhancement = int(line['item_enhancement'])
                target_item.item_base_tier = int(line['item_base_tier'])
                target_item.item_blessing_tier = str(line['item_blessing_tier'])
                target_item.item_material_tier = str(line['item_material_tier'])
                target_item.item_num_stars = int(line['item_num_stars'])
                target_item.item_prefix_values = str(line['item_prefix_values'])
                target_item.item_suffix_values = str(line['item_suffix_values'])
                target_item.item_bonus_stat = str(line['item_bonus_stat'])
                target_item.item_base_damage_min = int(line['item_base_dmg_min'])
                target_item.item_base_damage_max = int(line['item_base_dmg_max'])
                target_item.item_num_sockets = int(line['item_num_sockets'])
                target_item.item_inlaid_gem_id = str(line['item_inlaid_gem_id'])
                target_item.item_damage_min = damagecalc.item_damage_calc(target_item.item_base_damage_min,
                                                                          target_item.item_material_tier,
                                                                          target_item.item_blessing_tier)
                target_item.item_damage_max = damagecalc.item_damage_calc(target_item.item_base_damage_max,
                                                                          target_item.item_material_tier,
                                                                          target_item.item_blessing_tier)
                break

    return target_item


def read_accessory(item_id: str) -> CustomAccessory:
    filename = 'cinventory.csv'
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['item_id']) == str(item_id):
                player_id = int(line['player_id'])
                target_item = CustomAccessory(player_id)
                target_item.player_owner = player_id
                target_item.item_id = item_id
                target_item.item_name = str(line['item_name'])
                target_item.item_elements = str(line['item_elements']).split(';')
                target_item.item_damage_type = str(line['item_damage_type'])
                target_item.item_enhancement = int(line['item_enhancement'])
                target_item.item_base_tier = int(line['item_base_tier'])
                target_item.item_blessing_tier = str(line['item_blessing_tier'])
                target_item.item_material_tier = str(line['item_material_tier'])
                target_item.item_num_stars = int(line['item_num_stars'])
                target_item.item_prefix_values = str(line['item_prefix_values'])
                target_item.item_suffix_values = str(line['item_suffix_values'])
                target_item.item_bonus_stat = str(line['item_bonus_stat'])
                target_item.item_base_damage_min = int(line['item_base_dmg_min'])
                target_item.item_base_damage_max = int(line['item_base_dmg_max'])
                target_item.item_num_sockets = int(line['item_num_sockets'])
                target_item.item_inlaid_gem_id = str(line['item_inlaid_gem_id'])
                target_item.item_damage_min = damagecalc.item_damage_calc(target_item.item_base_damage_min,
                                                                          target_item.item_material_tier,
                                                                          target_item.item_blessing_tier)
                target_item.item_damage_max = damagecalc.item_damage_calc(target_item.item_base_damage_max,
                                                                          target_item.item_material_tier,
                                                                          target_item.item_blessing_tier)
                break

    return target_item


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


def generate_armour_base(item_tier) -> str:

    match item_tier:
        case 1:
            item_base = "Armour"
        case 2:
            item_base = "Shell"
        case 3:
            item_base = "Mail"
        case 4:
            item_base = "Plate"
        case _:
            item_base = "error"

    return item_base


def generate_accessory_base() -> str:
    random_number = random.randint(1,5)
    match random_number:
        case 1:
            item_base = "Amulet"
        case 2:
            item_base = "Necklace"
        case 3:
            item_base = "Ring"
        case 4:
            item_base = "Earring"
        case _:
            item_base = "Bracelet"

    return item_base


# write item to inventory
def inventory_add_weapon(item: CustomWeapon) -> str:
    # file specifications
    filename = 'cinventory.csv'

    # item name and id
    player_id = item.player_owner
    item_id = item.item_id
    item_name = item.item_name

    # item elements and damage type
    item_elements = ""
    for x in item.item_elements:
        item_elements = str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]
    item_damage_type = item.item_damage_type

    # item damage adjustments
    item_enhancement = item.item_enhancement
    item_base_tier = item.item_base_tier
    item_blessing_tier = item.item_blessing_tier
    item_material_tier = item.item_material_tier

    # item rolls
    item_num_stars = item.item_num_stars
    item_prefix_values = item.item_prefix_values
    item_suffix_values = item.item_suffix_values

    # item base damage
    item_bonus_stat = item.item_bonus_stat
    item_base_dmg_min = item.base_damage_min
    item_base_dmg_max = item.base_damage_max

    # sockets
    item_num_sockets = item.item_num_sockets
    item_inlaid_gem_id = item.item_inlaid_gem_id

    # insert item into csv file
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([player_id, item_id, item_name,
                         item_elements, item_damage_type,
                         item_enhancement, item_base_tier, item_blessing_tier, item_material_tier,
                         item_num_stars, item_prefix_values, item_suffix_values,
                         item_bonus_stat, item_base_dmg_min, item_base_dmg_max,
                         item_num_sockets,item_inlaid_gem_id])

    return 'You have placed the item in your inventory'


# write item to inventory
def inventory_add_armour(item: CustomArmour) -> str:
    # file specifications
    filename = 'cinventory.csv'

    # item name and id
    player_id = item.player_owner
    item_id = item.item_id
    item_name = item.item_name

    # item elements and damage type
    item_elements = ""
    for x in item.item_elements:
        item_elements = str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]
    item_damage_type = item.item_damage_type

    # item damage adjustments
    item_enhancement = item.item_enhancement
    item_base_tier = item.item_base_tier
    item_blessing_tier = item.item_blessing_tier
    item_material_tier = item.item_material_tier

    # item rolls
    item_num_stars = item.item_num_stars
    item_prefix_values = item.item_prefix_values
    item_suffix_values = item.item_suffix_values

    # item base damage
    item_bonus_stat = item.item_bonus_stat
    item_base_dmg_min = item.base_damage_min
    item_base_dmg_max = item.base_damage_max

    # sockets
    item_num_sockets = item.item_num_sockets
    item_inlaid_gem_id = item.item_inlaid_gem_id

    # insert item into csv file
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([player_id, item_id, item_name,
                         item_elements, item_damage_type,
                         item_enhancement, item_base_tier, item_blessing_tier, item_material_tier,
                         item_num_stars, item_prefix_values, item_suffix_values,
                         item_bonus_stat, item_base_dmg_min, item_base_dmg_max,
                         item_num_sockets,item_inlaid_gem_id])

    return 'You have placed the item in your inventory'


# write item to inventory
def inventory_add_accessory(item: CustomAccessory) -> str:
    # file specifications
    filename = 'cinventory.csv'

    # item name and id
    player_id = item.player_owner
    item_id = item.item_id
    item_name = item.item_name

    # item elements and damage type
    item_elements = ""
    for x in item.item_elements:
        item_elements = str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]
    item_damage_type = item.item_damage_type

    # item damage adjustments
    item_enhancement = item.item_enhancement
    item_base_tier = item.item_base_tier
    item_blessing_tier = item.item_blessing_tier
    item_material_tier = item.item_material_tier

    # item rolls
    item_num_stars = item.item_num_stars
    item_prefix_values = item.item_prefix_values
    item_suffix_values = item.item_suffix_values

    # item base damage
    item_bonus_stat = item.item_bonus_stat
    item_base_dmg_min = item.base_damage_min
    item_base_dmg_max = item.base_damage_max

    # sockets
    item_num_sockets = item.item_num_sockets
    item_inlaid_gem_id = item.item_inlaid_gem_id

    # insert item into csv file
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([player_id, item_id, item_name,
                         item_elements, item_damage_type,
                         item_enhancement, item_base_tier, item_blessing_tier, item_material_tier,
                         item_num_stars, item_prefix_values, item_suffix_values,
                         item_bonus_stat, item_base_dmg_min, item_base_dmg_max,
                         item_num_sockets,item_inlaid_gem_id])

    return 'You have placed the item in your inventory'


# check if item already exists. Prevent duplication
def if_custom_exists(item_id: int) -> bool:
    filename = 'cinventory.csv'
    df = pd.read_csv(filename)
    if str(item_id) in df['item_id'].values:
        return True
    else:
        return False


def display_cinventory(player_id: int) -> str:
    filename = 'cinventory.csv'
    df = pd.read_csv(filename)
    df = df[df['player_id'] == player_id][['item_id', 'item_name']]
    # .ljust(10) can pad the text
    player_inventory = df.to_string(index=False, header=False)
    return player_inventory


def get_gear_tier_colours(base_tier):
    match base_tier:
        case 1:
            tier_colour = discord.Colour.green()
            tier_emoji = "🟢"
        case 2:
            tier_colour = discord.Colour.blue()
            tier_emoji = "🔵"
        case 3:
            tier_colour = discord.Colour.purple()
            tier_emoji = "🟣"
        case 4:
            tier_colour = discord.Colour.gold()
            tier_emoji = "🟡"
        case _:
            tier_colour = discord.Colour.red()
            tier_emoji = "🔴"

    return tier_colour, tier_emoji
