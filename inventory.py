import csv
import random
import bosses
import damagecalc
import pandas as pd
import player
import discord
import jinja2
from IPython.display import display


class CustomItem:
    def __init__(self, player_owner):
        # initialize owner id
        self.player_owner = player_owner
        # generate item_tier
        random_num = random.randint(1, 100)
        if random_num <= 1:
            temp_tier = 4
            temp_min = 500
            temp_max = 500
        elif random_num <= 6:
            temp_tier = 3
            temp_min = 100
            temp_max = 250
        elif random_num <= 21:
            temp_tier = 2
            temp_min = 50
            temp_max = 100
        else:
            temp_tier = 1
            temp_min = 1
            temp_max = 50

        self.item_base_tier = temp_tier
        self.base_damage_min = temp_min
        self.base_damage_max = temp_max

        # initialize default values
        self.item_id = ""
        self.item_name = ""
        self.item_num_sockets = 0
        self.item_inlaid_gem_id = ""
        self.item_num_stars = 1
        self.item_suffix_values = []
        self.item_prefix_values = []
        self.item_material_tier = ""
        self.item_blessing_tier = ""
        self.item_type = ""
        self.item_enhancement = 0
        self.item_elements = []
        self.item_bonus_stat = 0
        self.item_damage_min = 0
        self.item_damage_max = 0
        self.item_damage_type = ""
        self.item_type = ""
        self.item_identifier = ""

    def update_stored_item(self):
        filename = "cinventory.csv"
        df = pd.read_csv(filename)

        item_elements = ""
        for x in self.item_elements:
            item_elements += str(x) + ";"
        if item_elements != "":
            item_elements = item_elements[:-1]

        item_prefix_values = ""
        for x in self.item_prefix_values:
            item_prefix_values += str(x) + ";"
        if item_prefix_values != "":
            item_prefix_values = item_prefix_values[:-1]

        item_suffix_values = ""
        for x in self.item_suffix_values:
            item_suffix_values += str(x) + ";"
        if item_suffix_values != "":
            item_suffix_values = item_suffix_values[:-1]

        dfn = pd.DataFrame(columns=["player_id", "item_id",	"item_name",
                                    "item_elements",	"item_damage_type",
                                    "item_enhancement",	"item_base_tier",
                                    "item_blessing_tier", "item_material_tier", "item_type",
                                    "item_num_stars", "item_prefix_values",	"item_suffix_values",
                                    "item_bonus_stat", "item_base_dmg_min",	"item_base_dmg_max",
                                    "item_num_sockets",	"item_inlaid_gem_id"],
                           data=[[self.player_owner, self.item_id, self.item_name,
                                  item_elements, self.item_damage_type,
                                  self.item_enhancement, self.item_base_tier,
                                  self.item_blessing_tier, self.item_material_tier, self.item_type,
                                  self.item_num_stars, item_prefix_values, item_suffix_values,
                                  self.item_bonus_stat, self.base_damage_min, self.base_damage_max,
                                  self.item_num_sockets, self.item_inlaid_gem_id]])

        df.update(df[['item_id']].merge(dfn, 'left'))
        df.to_csv(filename, index=False)

    def set_item_name(self):
        # set the item name
        self.item_name = generate_item_name(self.item_enhancement, self.item_blessing_tier, self.item_material_tier,
                                            self.item_type)

    def add_roll(self):
        self.item_num_stars += 1
        if len(self.item_prefix_values) == 2:
            self.item_suffix_values.append(self.generate_new_roll("S"))
        elif len(self.item_suffix_values) == 2:
            self.item_prefix_values.append(self.generate_new_roll("P"))
        else:
            random_num = random.randint(1, 2)
            if random_num == 1:
                self.item_prefix_values.append(self.generate_new_roll("P"))
            else:
                self.item_suffix_values.append(self.generate_new_roll("S"))

    def remove_roll(self):
        self.item_num_stars -= 1
        random_num = random.randint(1, self.item_num_stars)
        count = 1
        for x in self.item_prefix_values:
            if count == random_num:
                self.item_prefix_values.remove(x)
            count += 1
        for y in self.item_suffix_values:
            if count == random_num:
                self.item_suffix_values.remove(y)
            count += 1

    def generate_new_roll(self, roll_type):
        running = True
        new_roll = ""
        tier = 1
        match roll_type:
            case "P":
                if self.item_prefix_values:
                    while running:
                        running = False
                        for x in self.item_prefix_values:
                            random_identifier = random.randint(1, 5)
                            new_roll = f"{roll_type}{tier}{random_identifier}"
                            if new_roll == x:
                                running = True
                else:
                    random_identifier = random.randint(1, 5)
                    new_roll = f"{roll_type}{tier}{random_identifier}"
            case "S":
                if self.item_suffix_values:
                    while running:
                        running = False
                        for x in self.item_suffix_values:
                            random_identifier = random.randint(1, 4)
                            new_roll = f"{roll_type}{tier}{random_identifier}"
                            if new_roll[0] == str(x)[0] and new_roll[2] == str(x)[2]:
                                running = True
                else:
                    random_identifier = random.randint(1, 4)
                    new_roll = f"{roll_type}{tier}{random_identifier}"
            case _:
                new_roll = "Error"
        return new_roll

    def create_citem_embed(self):
        gear_colours = get_gear_tier_colours(self.item_base_tier)
        tier_colour = gear_colours[0]
        gem_min = 0
        gem_max = 0

        item_title = f'{self.item_name}'

        if self.item_id[0] == "D":
            damage_bonus = f'Base Damage: {self.item_damage_min:,}'
            damage_bonus += f' - {self.item_damage_max:,}'
            item_stats = ""
            for x in self.item_prefix_values:
                buff_type, buff_amount = gem_stat_reader(str(x))
                item_stats += f'{buff_type}: +{buff_amount}%\n'
            for y in self.item_suffix_values:
                buff_type, buff_amount = gem_stat_reader(str(y))
                item_stats += f'{buff_type}: +{buff_amount}%\n'
            gem_description = f'{damage_bonus}\nItem Rolls:\n{item_stats}'
            embed_msg = discord.Embed(colour=tier_colour,
                                      title=item_title,
                                      description=gem_description)
            thumb_img = "https://i.ibb.co/ygGCRnc/sworddefaulticon.png"
        else:
            self.update_damage()
            display_stars = ""
            match self.item_identifier:
                case "W":
                    bonus_type = "Base Attack Speed "
                    aux_suffix = "/min"
                    thumb_img = "https://i.ibb.co/ygGCRnc/sworddefaulticon.png"
                case "A":
                    bonus_type = "Base Damage Mitigation "
                    aux_suffix = "%"
                    thumb_img = "https://i.ibb.co/p2K2GFK/armouricon.png"
                case "Y":
                    bonus_type = ""
                    aux_suffix = ""
                    thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
                case "G":
                    bonus_type = ""
                    aux_suffix = ""
                    thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
                case "C":
                    bonus_type = ""
                    aux_suffix = ""
                    thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
                case _:
                    bonus_type = "Error"
                    aux_suffix = "Error"
                    thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
            item_rolls = f'{bonus_type}{self.item_bonus_stat}{aux_suffix}'
            prefix_rolls = ""
            suffix_rolls = ""
            if self.item_prefix_values:
                for x in self.item_prefix_values:
                    prefix_rolls += f'\n{get_roll_by_code(str(x), self.item_identifier)} '
                    for y in range(int(str(x)[1]) - 1):
                        prefix_rolls += "<:eprl:1148390531345432647>"
            if self.item_suffix_values:
                for x in self.item_suffix_values:
                    suffix_rolls += f'\n{get_roll_by_code(str(x), self.item_identifier)} '
                    for y in range(int(str(x)[1]) - 1):
                        suffix_rolls += "<:eprl:1148390531345432647>"

            for x in range(self.item_num_stars):
                display_stars += "<:estar1:1143756443967819906>"
            for y in range((5 - self.item_num_stars)):
                display_stars += "<:ebstar2:1144826056222724106>"

            item_types = f'{self.item_damage_type}'
            for x in self.item_elements:
                item_types += f'{x}'
            if self.item_num_sockets == 1:
                gem_id = self.item_inlaid_gem_id
                if gem_id == "":
                    display_stars += " Socket: <:esocket:1148387477615300740>"
                else:
                    display_stars += f" Socket: {gem_id} Equipped"
                    e_gem = read_custom_item(gem_id)
                    gem_min = e_gem.item_damage_min
                    gem_max = e_gem.item_damage_max
            damage_min = str(gem_min + self.item_damage_min)
            damage_max = str(gem_max + self.item_damage_max)
            damage_bonus = f'Base Damage: {int(damage_min):,}'
            damage_bonus += f' - {int(damage_max):,}'
            embed_msg = discord.Embed(colour=tier_colour,
                                      title=item_title,
                                      description=display_stars)
            embed_msg.add_field(name=item_types, value=damage_bonus, inline=False)
            embed_msg.add_field(name="Item Rolls", value=item_rolls, inline=False)
            all_rolls = prefix_rolls + suffix_rolls
            if all_rolls != "":
                embed_msg.add_field(name="", value=all_rolls, inline=False)
        embed_msg.set_thumbnail(url=thumb_img)
        return embed_msg

    def update_damage(self):
        # calculate item's damage per hit
        self.item_damage_min = damagecalc.item_damage_calc(self.base_damage_min, self.item_enhancement,
                                                           self.item_material_tier, self.item_blessing_tier)
        self.item_damage_max = damagecalc.item_damage_calc(self.base_damage_max, self.item_enhancement,
                                                           self.item_material_tier, self.item_blessing_tier)

    def check_augment(self):
        augment_total = 0
        for x in self.item_prefix_values:
            augment_total += int(str(x)[1]) - 1
        for y in self.item_suffix_values:
            augment_total += int(str(y)[1]) - 1
        if len(self.item_prefix_values) + len(self.item_suffix_values) == 0:
            augment_total = 15
        return augment_total

    def add_augment(self):
        exclude_group = []
        # Build Exclusions
        check = self.item_prefix_values + self.item_suffix_values
        length_prefix = len(self.item_prefix_values)
        for idx, x in enumerate(check):
            augment_total = int(str(x)[1])
            if augment_total == 4:
                exclude_group.append(idx)

        # Apply a new augment
        random_num = random.randint(1, (self.item_num_stars - 1))
        random_num -= 1
        while random_num in exclude_group:
            random_num = random.randint(1, (self.item_num_stars - 1))
            random_num -= 1
        if random_num < length_prefix:
            target_roll = self.item_prefix_values[random_num]
            augment_total = int(str(target_roll)[1])
            new_id = f'P{augment_total + 1}{str(target_roll[2])}'
            self.item_prefix_values[random_num] = new_id
        else:
            random_num -= length_prefix
            target_roll = self.item_suffix_values[random_num]
            augment_total = int(str(target_roll)[1])
            new_id = f'S{augment_total + 1}{str(target_roll[2])}'
            self.item_suffix_values[random_num] = new_id


class CustomWeapon(CustomItem):
    def __init__(self, player_owner):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_identifier = "W"
        self.item_id = self.item_identifier + str(1 + df['item_id'].count())

        # generate weapon specifications
        self.item_damage_type = generate_item_type()
        self.item_type = generate_weapon_base(self.item_base_tier, self.item_damage_type)

        # generate the weapon name
        if self.item_damage_type == "<:cD:1150195280969478254>":
            self.item_blessing_tier = "Standard"
            self.item_material_tier = "Illusion"
        else:
            self.item_material_tier = "Iron"
            self.item_blessing_tier = "Basic"

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
        self.item_elements.append(bosses.get_element())

        # calculate item's damage per hit
        self.update_damage()
        # set item name
        self.set_item_name()


class CustomArmour(CustomItem):
    def __init__(self, player_owner):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_identifier = "A"
        self.item_id = self.item_identifier + str(1 + df['item_id'].count())

        # generate armour specifications
        self.item_damage_type = generate_item_type()
        self.item_type = generate_armour_base(self.item_base_tier)

        self.item_material_tier = "Iron"
        self.item_blessing_tier = "Inert"

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
        self.update_damage()

        # set the item name
        self.set_item_name()


class CustomAccessory(CustomItem):
    def __init__(self, player_owner):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_identifier = "Y"
        self.item_id = self.item_identifier + str(1 + df['item_id'].count())

        # generate accessory specifications
        self.item_damage_type = generate_item_type()
        self.item_type = generate_accessory_base()

        self.item_material_tier = "Crude"
        self.item_blessing_tier = "Sparkling"

        random_num = random.randint(1,4)
        # set accessory unique skill
        match self.item_base_tier:
            case 4:
                match random_num:
                    case 1:
                        temp_unique_skill = "Bahamut's Grace"
                    case 2:
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
        self.update_damage()

        # set the item name
        self.set_item_name()


class CustomWing(CustomItem):
    def __init__(self, player_owner, selected_tier):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_identifier = "G"
        self.item_id = self.item_identifier + str(1 + df['item_id'].count())

        # generate wing specifications
        self.item_damage_type = generate_item_type()

        self.item_material_tier = "Crude"
        self.item_blessing_tier = "Sparkling"
        self.item_elements.clear()
        self.item_base_tier = selected_tier

        # set wing bonus stat
        match self.item_base_tier:
            case 4:
                self.item_type = "Dimensional Wings"
                self.base_damage_min = 500
                self.base_damage_max = 500
                bonus_stat = ""
            case 3:
                self.item_type = "Wonderous Wings"
                self.base_damage_min = 100
                self.base_damage_max = 250
                bonus_stat = ""
            case 2:
                self.item_type = "Lucent Wings"
                self.base_damage_min = 50
                self.base_damage_max = 100
                bonus_stat = ""
            case _:
                self.item_type = "Feathered Wings"
                self.base_damage_min = 1
                self.base_damage_max = 50
                bonus_stat = ""

        self.item_bonus_stat = bonus_stat
        # calculate item's damage per hit
        self.update_damage()

        # set the item name
        self.set_item_name()


class CustomCrest(CustomItem):
    def __init__(self, player_owner, selected_tier):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_identifier = "C"
        self.item_id = self.item_identifier + str(1 + df['item_id'].count())

        # generate crest specifications
        self.item_damage_type = generate_item_type()
        self.item_type = generate_crest_base()

        self.item_elements.clear()

        self.item_material_tier = "Iron"
        random_blessing = random.randint(1, 2)
        if random_blessing == 1:
            self.item_blessing_tier = "Light"
        else:
            self.item_blessing_tier = "Dark"
        self.item_base_tier = selected_tier

        random_num = random.randint(1, 2)
        # set crest unique skill
        match self.item_base_tier:
            case 4:
                self.base_damage_min = 500
                self.base_damage_max = 500
                match random_num:
                    case 1:
                        temp_unique_skill = "Elemental Fractal"
                    case _:
                        temp_unique_skill = "Omega Critical"
            case 3:
                self.base_damage_min = 100
                self.base_damage_max = 250
                match random_num:
                    case 1:
                        temp_unique_skill = "Specialized Mastery"
                    case _:
                        temp_unique_skill = "Ignore Protection"
            case 2:
                self.base_damage_min = 50
                self.base_damage_max = 100
                match random_num:
                    case 1:
                        temp_unique_skill = "Perfect Precision"
                    case _:
                        temp_unique_skill = "Resistance Bypass"
            case _:
                self.base_damage_min = 1
                self.base_damage_max = 50
                match random_num:
                    case 1:
                        temp_unique_skill = ""
                    case _:
                        temp_unique_skill = "Defence Bypass"

        self.item_bonus_stat = temp_unique_skill
        # calculate item's damage per hit
        self.update_damage()

        # set the item name
        self.set_item_name()


class CustomGem(CustomItem):
    def __init__(self, player_owner, selected_tier):
        CustomItem.__init__(self, player_owner)

        # initialize item_id
        df = pd.read_csv('cinventory.csv')
        self.item_identifier = "D"
        self.item_id = self.item_identifier + str(1 + df['item_id'].count())

        # generate gem specifications
        self.item_damage_type = ""
        self.item_type = ""
        self.item_material_tier = ""
        self.item_blessing_tier = ""
        self.item_bonus_stat = ""
        self.item_base_tier = selected_tier
        self.item_elements.clear()

        random_num = random.randint(1, 2)
        # set attack speed
        match selected_tier:
            case 4:
                self.base_damage_min = 5000
                self.base_damage_max = 5000
                self.item_name = "Gem of Dimensions"
                self.item_prefix_values.append("P4b")
                self.item_prefix_values.append("P4c")
                self.item_suffix_values.append("S4b")
                self.item_suffix_values.append("S4c")
            case 3:
                self.base_damage_min = 2000
                self.base_damage_max = 4000
                if random_num == 1:
                    self.item_name = "Gem of Chaos"
                    self.item_prefix_values.append("P3a")
                    self.item_prefix_values.append("P3b")
                    self.item_suffix_values.append("S3b")
                    self.item_suffix_values.append("S3c")
                else:
                    self.item_name = "Gem of Twilight"
                    self.item_prefix_values.append("P3a")
                    self.item_prefix_values.append("P3c")
                    self.item_suffix_values.append("S3a")
                    self.item_suffix_values.append("S3b")
            case 2:
                self.base_damage_min = 500
                self.base_damage_max = 1500
                if random_num == 1:
                    self.item_name = "Gem of Clarity"
                    self.item_prefix_values.append("P2a")
                    self.item_prefix_values.append("P2b")
                    self.item_suffix_values.append("S2b")
                    self.item_suffix_values.append("S2c")
                else:
                    self.item_name = "Gem of Nature's Wrath"
                    self.item_prefix_values.append("P2a")
                    self.item_prefix_values.append("P2c")
                    self.item_suffix_values.append("S2a")
                    self.item_suffix_values.append("S2b")
            case _:
                self.base_damage_min = 100
                self.base_damage_max = 500
                if random_num == 1:
                    self.item_name = "Gem of the Deep"
                    self.item_prefix_values.append("P1a")
                    self.item_prefix_values.append("P1b")
                    self.item_suffix_values.append("S1b")
                    self.item_suffix_values.append("S1c")
                else:
                    self.item_name = "Gem of Land and Sky"
                    self.item_prefix_values.append("P1a")
                    self.item_prefix_values.append("P1c")
                    self.item_suffix_values.append("S1a")
                    self.item_suffix_values.append("S1b")
        self.item_damage_min = self.base_damage_min
        self.item_damage_max = self.base_damage_max


def gem_stat_reader(item_code):
    buff_type = ""
    buff_amount = 0
    tier_code = int(item_code[1])
    if item_code[0] == "P":
        match item_code[2]:
            case "a":
                buff_type = "HP"
                buff_amount = 5 * tier_code
            case "b":
                buff_type = "Critical Chance"
                buff_amount = 25 * tier_code
            case "c":
                buff_type = "Final Damage"
                buff_amount = 15 * tier_code
            case _:
                buff_type = "Error"
    else:
        match item_code[2]:
            case "a":
                buff_type = "Attack Speed"
                buff_amount = 15 * tier_code
            case "b":
                buff_type = "Damage Mitigation"
                buff_amount = 5 * tier_code
            case "c":
                buff_type = "Critical Damage"
                buff_amount = 25 * tier_code
            case _:
                buff_type = "Error"
    return buff_type, buff_amount

def generate_item_name(item_enhancement, item_blessing_tier, item_material_tier, item_type) -> str:
    item_name = "+" + str(item_enhancement) + " " + item_blessing_tier + " " + item_material_tier
    item_name += " " + item_type
    return item_name


def read_custom_item(item_id: str):
    filename = 'cinventory.csv'
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['item_id']) == str(item_id):
                player_id = int(line['player_id'])
                identifier = str(line['item_id'])
                identifier = identifier[0]
                if identifier == "W":
                    target_item = CustomWeapon(player_id)
                elif identifier == "A":
                    target_item = CustomArmour(player_id)
                elif identifier == "Y":
                    target_item = CustomAccessory(player_id)
                elif identifier == "G":
                    target_item = CustomWing(player_id, 0)
                elif identifier == "C":
                    target_item = CustomCrest(player_id, 0)
                else:
                    target_item = CustomGem(player_id, 0)
                target_item.player_owner = player_id
                target_item.item_id = item_id
                target_item.item_name = str(line['item_name'])
                if str(line['item_elements']) != "":
                    target_item.item_elements = list(str(line['item_elements']).split(';'))
                target_item.item_type = str(line['item_type'])
                target_item.item_damage_type = str(line['item_damage_type'])
                target_item.item_enhancement = int(line['item_enhancement'])
                target_item.item_base_tier = int(line['item_base_tier'])
                target_item.item_blessing_tier = str(line['item_blessing_tier'])
                target_item.item_material_tier = str(line['item_material_tier'])
                target_item.item_num_stars = int(line['item_num_stars'])
                if str(line['item_prefix_values']) != "":
                    target_item.item_prefix_values = list(str(line['item_prefix_values']).split(';'))
                if str(line['item_suffix_values']) != "":
                    target_item.item_suffix_values = list(str(line['item_suffix_values']).split(';'))
                target_item.item_bonus_stat = str(line['item_bonus_stat'])
                target_item.base_damage_min = int(line['item_base_dmg_min'])
                target_item.base_damage_max = int(line['item_base_dmg_max'])
                target_item.item_num_sockets = int(line['item_num_sockets'])
                target_item.item_inlaid_gem_id = str(line['item_inlaid_gem_id'])
                if identifier != "D":
                    target_item.update_damage()
                else:
                    target_item.item_damage_min = target_item.base_damage_min
                    target_item.item_damage_max = target_item.base_damage_max
                break

    return target_item


def generate_item_type() -> str:
    random_num = random.randint(1, 9)
    match random_num:
        case 1 | 2 | 3:
            damage_type = "<:cA:1150195102589931641>"
        case 3 | 4 | 5:
            damage_type = "<:cB:1150516823524114432>"
        case 6 | 7 | 8:
            damage_type = "<:cC:1150195246588764201>"
        case _:
            damage_type = "<:cD:1150195280969478254>"
    return damage_type


def generate_weapon_base(item_tier, damage_type) -> str:

    random_num = random.randint(1, 5)
    if item_tier == 4:
        random_num *= random.randint(1,3)
    else:
        random_num += (item_tier - 1) * 5

    match damage_type:
        case "<:cB:1150516823524114432>":
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
        case "<:cA:1150195102589931641>":
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
        case "<:cC:1150195246588764201>":
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


def generate_crest_base() -> str:
    random_number = random.randint(1, 9)
    match random_number:
        case 1 | 2:
            item_base = "Halo"
        case 3 | 4:
            item_base = "Horns"
        case 5 | 6:
            item_base = "Crown"
        case 7 | 8:
            item_base = "Tiara"
        case _:
            item_base = "Diadem"

    return item_base


# write item to inventory
def inventory_add_custom_item(item) -> str:
    # File specifications
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
    item_type = item.item_type

    # item rolls
    item_prefix_values = ""
    item_suffix_values = ""
    item_num_stars = item.item_num_stars
    if item.item_id[0] == "D":
        for x in item.item_prefix_values:
            item_prefix_values += str(x) + ";"
        item_prefix_values = item_prefix_values[:-1]
        for y in item.item_suffix_values:
            item_suffix_values += str(y) + ";"
        item_suffix_values = item_suffix_values[:-1]

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
                         item_enhancement, item_base_tier, item_blessing_tier, item_material_tier, item_type,
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
    temp = df.style.set_properties(**{'text-align': 'left'}).hide(axis='index').hide(axis='columns')
    player_inventory = temp.to_string()
    return player_inventory


def display_binventory(player_id: int):
    filename = 'binventory.csv'
    df = pd.read_csv(filename)
    filename = 'itemlist.csv'
    item_list = pd.read_csv(filename)

    merged_df = df.merge(item_list, left_on='item_id', right_on='item_id')
    merged_df = merged_df[merged_df['player_id'] == player_id][['item_emoji', 'item_name', 'item_qty']]
    merged_df = merged_df[merged_df['item_qty'] != 0][['item_emoji', 'item_name', 'item_qty']]
    # merged_df = merged_df.sort_values(ascending=True)
    temp = merged_df.style.set_properties(**{'text-align': 'left'}).hide(axis='index').hide(axis='columns')
    player_inventory = temp.to_string()

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


def craft_item(player_object, selected_item, item_id, method):
    filename = 'itemlist.csv'
    item_list = pd.read_csv(filename)

    success_rate = int(item_list[item_list['item_id'] == item_id][['item_base_rate']].values[0])
    player_stock = check_stock(player_object, item_id)
    if player_stock > 0:
        match method:
            case "Enhance":
                success_rate = success_rate - selected_item.item_enhancement
                if selected_item.item_enhancement < 100:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        selected_item.item_enhancement += 1
                        selected_item.set_item_name()
                        is_success = "1"
                    else:
                        is_success = "0"
                else:
                    is_success = "3"
            case "Upgrade":
                if damagecalc.get_item_tier_damage(selected_item.item_material_tier) != 2500:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        material_tier_list = ["Iron", "Steel", "Silver", "Mithril", "Diamond", "Crystal",
                                              "Illusion", "Essence", "Spirit", "Soulbound", "Phantasmal", "Spectral",
                                              "Crude", "Metallic", "Gold", "Jewelled", "Diamond", "Crystal"]
                        for idx, elem in enumerate(material_tier_list):
                            if selected_item.item_material_tier == elem:
                                selected_item.item_material_tier = material_tier_list[(idx + 1)]
                                break
                        selected_item.set_item_name()
                        is_success = "1"
                    else:
                        is_success = "0"
                else:
                    is_success = "3"
            case "Bestow":
                if damagecalc.get_item_tier_damage(selected_item.item_blessing_tier) < 2500:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        blessing_tier_list = ["Inert", "Faint", "Luminous", "Lustrous", "Radiant", "Divine",
                                              "Basic", "Enchanted", "Luminous", "Lustrous", "Radiant", "Divine",
                                              "Sparkling", "Glittering", "Dazzling", "Shining", "Prismatic", "Resplendent",
                                              "Dark", "Shadow", "Inverted", "Abyssal", "Calamitous", "Balefire",
                                              "Light", "Glowing", "Pure", "Majestic", "Radiant", "Divine"]
                        for idx, elem in enumerate(blessing_tier_list):
                            if selected_item.item_blessing_tier == elem:
                                selected_item.item_blessing_tier = blessing_tier_list[(idx + 1)]
                                break
                        selected_item.set_item_name()
                        is_success = "1"
                    else:
                        is_success = "0"
                else:
                    is_success = "3"
            case "Open":
                if selected_item.item_num_sockets < 1:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        selected_item.item_num_sockets += 1
                        is_success = "1"
                    else:
                        is_success = "0"
                else:
                    is_success = "3"
            case "Imbue":
                if selected_item.item_num_stars < 5:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        selected_item.add_roll()
                        is_success = "1"
                    else:
                        is_success = "0"
                else:
                    is_success = "3"
            case "Cleanse":
                if selected_item.item_num_stars > 1:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        selected_item.remove_roll()
                        is_success = "5"
                    else:
                        is_success = "0"
                else:
                    is_success = "3"
            case "Augment":
                check_aug = selected_item.check_augment()
                if check_aug < 12:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        selected_item.add_augment()
                        is_success = "1"
                    else:
                        is_success = "0"
                elif check_aug == 15:
                    is_success = 6
                else:
                    is_success = "3"
            case "Implant":
                if len(selected_item.item_elements) < 9:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        running = True
                        new_element = ""
                        while running:
                            new_element = bosses.get_element()
                            running = False
                            for x in selected_item.item_elements:
                                if str(x) == new_element:
                                    running = True
                        selected_item.item_elements.append(new_element)
                        is_success = "1"
                    else:
                        is_success = "0"
                else:
                    is_success = "3"
            case "Voidforge":
                damage_check = damagecalc.get_item_tier_damage(selected_item.item_material_tier)
                if damage_check == 2500:
                    update_stock(player_object, item_id, -1)
                    random_num = random.randint(1, 100)
                    if random_num <= success_rate:
                        selected_item.item_material_tier = "Voidcrystal"
                        selected_item.set_item_name()
                        is_success = "1"
                    else:
                        is_success = "0"
                elif damage_check == 9500:
                    is_success = "3"
                else:
                    is_success = "4"
            case _:
                is_success = "Error"
    else:
        is_success = item_id

    if is_success == "1" or is_success == "5":
        selected_item.update_damage()
        selected_item.update_stored_item()

    return is_success


def check_stock(player_object, item_id):
    filename = 'binventory.csv'
    df = pd.read_csv(filename)
    df = df[(df['item_id'] == item_id) & (df['player_id'] == player_object.player_id)][['item_qty']]
    if not df.empty:
        player_stock = int(df.values[0])
    else:
        player_stock = 0
    return player_stock


def update_stock(player_object, item_id, change):
    filename = 'binventory.csv'
    df = pd.read_csv(filename)
    player_stock = check_stock(player_object, item_id)
    df.loc[(df['item_id'] == item_id) & (df['player_id'] == player_object.player_id),
           'item_qty'] = player_stock + change
    df.to_csv(filename, index=False)


def get_roll_by_code(code, item_type):
    roll_adjust = 25
    roll_text = ""
    match code[0]:
        case "P":
            match code[2]:
                case "1":
                    roll = "Critical Chance"
                case "2":
                    roll = "Attack Speed"
                case "3":
                    roll = "Elemental Penetration"
                case "4":
                    roll = "Final Damage"
                case "5":
                    roll = "Damage Mitigation"
                    roll_adjust = 10
                case _:
                    roll = "Error"
            bonus = str(int(code[1]) * roll_adjust)
            roll_text += f'+{bonus}% {roll}'
        case "S":
            match code[2]:
                case "1":
                    bonus = str(int(code[1]) * 50)
                    roll_text = f"+{bonus}% Critical Damage"
                case "2":
                    bonus = str(int(code[1])*0.25 + 1)
                    roll_text = f"Aura: {bonus}x Team Damage"
                case "3":
                    bonus = str(int(code[1])*0.25 + 1)
                    roll_text = f"Curse: {bonus}x Boss Damage Received"
                case "4":
                    bonus = str(int(code[1]) + 1)
                    if item_type == "W":
                        roll_text = f"Multi-Hit: {bonus}x Combo"
                    else:
                        roll_text = f"Undecided Roll: {bonus}x Combo"
                case _:
                    roll_text = "Error"
        case _:
            roll_text = "Error"
    return roll_text


def try_refine(player_owner, item_type, selected_tier):
    match item_type:
        case "Dragon Heart Gems":
            new_item = CustomGem(player_owner, selected_tier)
        case "Wings":
            new_item = CustomWing(player_owner, selected_tier)
        case "Paragon Crests":
            new_item = CustomCrest(player_owner, selected_tier)
        case _:
            new_item = CustomWing(player_owner, selected_tier)

    random_num = random.randint(1, 100)
    if random_num > 25:
        new_item.item_id = ""

    return new_item
