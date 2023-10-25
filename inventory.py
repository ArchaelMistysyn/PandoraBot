import csv
import random
import bosses
import damagecalc
import pandas as pd

import inventory
import loot
import player
import discord
import jinja2
from IPython.display import display
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import mydb
import pandorabot
import globalitems
import string

custom_item_dict = {"W": "Weapon", "A": "Armour", "Y": "Accessory", "G": "Wing", "C": "Crest",
                    "D": "Dragon Heart Gem", "T": "Tarot Card"}


class CustomItem:
    def __init__(self, player_owner, item_type, item_tier):
        # initialize owner id
        self.player_owner = player_owner
        self.item_type = item_type
        self.item_tier = item_tier
        self.item_damage_type = generate_item_type()

        self.item_base_type = ""
        if self.item_type != "W" or self.item_tier <= 4:
            self.generate_base()

        # initialize default values
        self.item_id = 0
        self.item_name = ""
        self.item_elements = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.item_enhancement = 0
        self.item_num_stars = 0
        self.item_suffix_values = []
        self.item_prefix_values = []
        self.item_bonus_stat = ""
        self.item_material_tier = ""
        self.item_blessing_tier = ""
        self.item_damage_min = 0
        self.item_damage_max = 0
        self.item_num_sockets = 0
        self.item_inlaid_gem_id = 0

        random_rolltype = random.randint(0, 1)
        if random_rolltype == 0:
            rolltype = "P"
        else:
            rolltype = "S"
        random_damage1, random_damage2 = get_tier_damage(self.item_tier)
        self.base_damage_min = random_damage1
        self.base_damage_max = random_damage2
        match self.item_type:
            case "W":
                self.set_base_attack_speed()
                if self.item_damage_type == globalitems.class_summoner:
                    self.item_blessing_tier = "Standard"
                    self.item_material_tier = "Illusion"
                else:
                    self.item_material_tier = "Iron"
                    self.item_blessing_tier = "Basic"
                if self.item_tier >= 5:
                    if self.item_tier == 6:
                        self.item_material_tier = "Key of ???"
                        self.item_blessing_tier = "???"
                    else:
                        self.item_material_tier = "Fabled"
                        self.item_blessing_tier = "Refined"
                    class_matcher = globalitems.class_icon_list.index(self.item_damage_type)
                    item_variant = random.randint(0, 1)
                    match class_matcher:
                        case 0:
                            if item_variant == 0:
                                self.item_base_type = "Saber"
                            else:
                                self.item_base_type = "Scythe"
                        case 1:
                            if item_variant == 0:
                                self.item_base_type = "Cannon"
                            else:
                                self.item_base_type = "Bow"
                        case 2:
                            if item_variant == 0:
                                self.item_base_type = "Staff"
                            else:
                                self.item_base_type = "Spellbook"
                        case 3:
                            if item_variant == 0:
                                self.item_base_type = "Dagger"
                            else:
                                self.item_base_type = "Claws"
                        case 4:
                            self.item_base_type = "Threads"
                        case 5:
                            if item_variant == 0:
                                self.item_base_type = "Dragon"
                            else:
                                self.item_base_type = "Cerberus"
                        case _:
                            if item_variant == 0:
                                self.item_base_type = "Anima"
                            else:
                                self.item_base_type = "Golem"
                self.add_roll(1)
            case "A":
                self.item_material_tier = "Iron"
                self.item_blessing_tier = "Standard"
                self.set_base_damage_mitigation()
                if self.item_tier == 5:
                    self.item_material_tier = "Fabled"
                    self.item_blessing_tier = "Refined"
                self.add_roll(1)
            case "Y":
                self.item_material_tier = "Crude"
                self.item_blessing_tier = "Sparkling"
                if self.item_tier == 5:
                    self.item_material_tier = "Fabled"
                    self.item_blessing_tier = "Refined"
                    self.item_base_type = "Amulet"
                self.assign_bonus_stat()
                self.add_roll(1)
            case "G":
                self.item_material_tier = "Crude"
                self.item_blessing_tier = "Sparkling"
                match self.item_tier:
                    case 5:
                        self.item_base_type = "Rift Wings"
                        self.item_material_tier = "Fabled"
                        self.item_blessing_tier = "Refined"
                    case 4:
                        self.item_base_type = "Dimensional Wings"
                    case 3:
                        self.item_base_type = "Wonderous Wings"
                    case 2:
                        self.item_base_type = "Lucent Wings"
                    case _:
                        self.item_base_type = "Feathered Wings"
                self.assign_bonus_stat()
                self.add_roll(1)
            case "C":
                self.item_material_tier = "Iron"
                if self.item_tier == 5:
                    self.item_material_tier = "Fabled"
                random_blessing = random.randint(1, 2)
                if random_blessing == 1:
                    self.item_blessing_tier = "Clear"
                else:
                    self.item_blessing_tier = "Tainted"
                random_num = random.randint(1, 2)
                # set crest unique skill
                self.assign_bonus_stat()
                self.add_roll(1)
            case _:
                random_variant = random.randint(1, 2)
                match self.item_tier:
                    case 6:
                        self.item_name = "Gem of the Infinite"
                    case 5:
                        self.item_name = "Fabled Gem"
                    case 4:
                        self.item_name = "Gem of Dimensions"
                    case 3:
                        if random_variant == 1:
                            self.item_name = "Gem of Chaos"
                        else:
                            self.item_name = "Gem of Twilight"
                    case 2:
                        if random_variant == 1:
                            self.item_name = "Gem of Clarity"
                        else:
                            self.item_name = "Gem of Nature's Wrath"
                    case _:
                        if random_variant == 1:
                            self.item_name = "Gem of the Deep"
                        else:
                            self.item_name = "Gem of Land and Sky"

                for idx, x in enumerate(range(self.item_tier)):
                    self.add_roll(self.item_tier)

        self.update_damage()
        if self.item_type != "D":
            self.add_item_element(9)
            self.item_num_stars = 0
            self.set_item_name()
        else:
            self.item_num_stars = self.item_tier - 1

    def reforge_stats(self):
        match self.item_type:
            case "W":
                self.set_base_attack_speed()
            case "A":
                self.set_base_damage_mitigation()
            case "Y" | "G" | "C":
                self.assign_bonus_stat()
            case _:
                error = True
        random_damage1, random_damage2 = get_tier_damage(self.item_tier)
        self.base_damage_min = random_damage1
        self.base_damage_max = random_damage2

    def set_base_attack_speed(self):
        match self.item_tier:
            case 6:
                bonus_roll = random.randint(21, 30)
                self.item_bonus_stat = str(round(float(bonus_roll) * 0.1, 1))
            case 5:
                bonus_roll = random.randint(16, 20)
                self.item_bonus_stat = str(round(float(bonus_roll) * 0.1, 1))
            case 4:
                self.item_bonus_stat = "1.5"
            case 3:
                self.item_bonus_stat = "1.3"
            case 2:
                self.item_bonus_stat = "1.2"
            case _:
                self.item_bonus_stat = "1.1"

    def set_base_damage_mitigation(self):
        match self.item_tier:
            case 5:
                self.item_bonus_stat = "30"
            case 4:
                self.item_bonus_stat = "25"
            case 3:
                self.item_bonus_stat = "15"
            case 2:
                self.item_bonus_stat = "10"
            case _:
                self.item_bonus_stat = "5"

    def assign_bonus_stat(self):
        base_tier = self.item_tier
        if base_tier < 5:
            random_pos = random.randint(0, 8)
            keyword = globalitems.element_special_names[random_pos]
            if self.item_type == "Y":
                random_pos = random.randint(0, 3)
                keyword = bosses.boss_list[random_pos]
                descriptor = "Bane"
            elif self.item_type == "G":
                descriptor = "Feathers"
            else:
                descriptor = "Authority"
            unique_skill = f"{keyword} {descriptor}"
        else:
            random_pos = random.randint(0, 3)
            unique_skill = globalitems.tier_5_ability_list[random_pos]
        self.item_bonus_stat = unique_skill

    def update_stored_item(self):
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

        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("UPDATE CustomInventory "
                         "SET player_id = :input_1, "
                         "item_type = :input_2, item_name = :input_3, "
                         "item_damage_type = :input_4, item_elements = :input_5, "
                         "item_enhancement = :input_6, item_tier = :input_7, "
                         "item_blessing_tier = :input_8, item_material_tier = :input_9, "
                         "item_base_type = :input_10, item_num_stars = :input_11, "
                         "item_prefix_values = :input_12, item_suffix_values = :input_13, "
                         "item_bonus_stat = :input_14, "
                         "item_base_dmg_min = :input_15, item_base_dmg_max = :input_16, "
                         "item_num_sockets = :input_17, item_inlaid_gem_id = :input_18 "
                         "WHERE item_id = :id_check")
            query = query.bindparams(id_check=int(self.item_id), input_1=int(self.player_owner),
                                     input_2=str(self.item_type), input_3=str(self.item_name),
                                     input_4=str(self.item_damage_type), input_5=str(item_elements),
                                     input_6=int(self.item_enhancement), input_7=int(self.item_tier),
                                     input_8=str(self.item_blessing_tier), input_9=str(self.item_material_tier),
                                     input_10=str(self.item_base_type), input_11=int(self.item_num_stars),
                                     input_12=str(item_prefix_values), input_13=str(item_suffix_values),
                                     input_14=str(self.item_bonus_stat),
                                     input_15=int(self.base_damage_min), input_16=int(self.base_damage_max),
                                     input_17=int(self.item_num_sockets), input_18=int(self.item_inlaid_gem_id))

            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except exc.SQLAlchemyError as error:
            print(error)

    def set_item_name(self):
        item_name = "+" + str(self.item_enhancement) + " " + self.item_blessing_tier + " " + self.item_material_tier
        item_name += " " + self.item_base_type
        self.item_name = item_name

    def generate_base(self):
        match self.item_type:
            case "W":
                tier_location = self.item_tier - 1
                class_checker = globalitems.class_icon_list.index(self.item_damage_type)
                match class_checker:
                    case 0:
                        random_num = random.randint(0, 2)
                        item_list_t1 = ["Shortsword", "Handaxe", "Javelin"]
                        item_list_t2 = ["Sword", "Axe", "Spear"]
                        item_list_t3 = ["Longsword", "Battle Axe", "Longspear"]
                        item_list_t4 = ["Greatsword", "Greataxe", "Trident"]
                    case 1:
                        random_num = random.randint(0, 1)
                        item_list_t1 = ["Shortbow", "Ballista"]
                        item_list_t2 = ["Longbow", "Arbalest"]
                        item_list_t3 = ["Recurve Bow", "Gun"]
                        item_list_t4 = ["Greatbow", "Blaster"]
                    case 2:
                        random_num = random.randint(0, 3)
                        item_list_t1 = ["Lesser Wand", "Lesser Staff", "Lesser Tome", "Lesser Orb"]
                        item_list_t2 = ["Magic Wand", "Magic Staff", "Magic Tome", "Crystal Ball"]
                        item_list_t3 = ["Sceptre", "Quarterstaff", "Grimoire", "Seer Sphere"]
                        item_list_t4 = ["Rod", "Crescent Staff", "Spellbook", "Orb"]
                    case 3:
                        random_num = random.randint(0, 2)
                        item_list_t1 = ["Dagger", "Claws", "Darts"]
                        item_list_t2 = ["Stiletto", "Tiger Claws", "Tomahawk"]
                        item_list_t3 = ["Kris", "Eagle Claws", "Kunai"]
                        item_list_t4 = ["Sai", "Dragon Talons", "Shuriken"]
                    case 4:
                        random_num = 0
                        item_list_t1 = ["Steel String"]
                        item_list_t2 = ["Cutting Wire"]
                        item_list_t3 = ["Razor Threads"]
                        item_list_t4 = ["Infused Threads"]
                    case 5:
                        random_num = random.randint(0, 11)
                        special_item_list = ["Pegacorn", "Night Mare", "Unicorn", "Pegasus",
                                             "Wyvern", "Roc", "Gryphon", "Manta Ray",
                                             "Liger", "Bear", "Elephant", "Wolf"]
                    case _:
                        random_num = random.randint(0, 11)
                        special_item_list = ["Zombie", "Ghoul", "Skeleton", "Specter",
                                             "Fox", "Spider", "Crocodile", "Basilisk",
                                             "Wyrm", "Salamander", "Coatl", "Phoenix"]
                if class_checker >= 5:
                    item_base = special_item_list[random_num]
                else:
                    item_namelist = [item_list_t1, item_list_t2, item_list_t3, item_list_t4]
                    item_base = item_namelist[tier_location][random_num]
            case "A":
                match self.item_tier:
                    case 1:
                        item_base = "Armour"
                    case 2:
                        item_base = "Shell"
                    case 3:
                        item_base = "Mail"
                    case 4:
                        item_base = "Plate"
                    case _:
                        item_base = "Lorica"
            case "Y":
                random_number = random.randint(1, 4)
                match random_number:
                    case 1:
                        item_base = "Bracelet"
                    case 2:
                        item_base = "Necklace"
                    case 3:
                        item_base = "Ring"
                    case 4:
                        item_base = "Earring"
                    case _:
                        item_base = "Error"
            case "C":
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
            case _:
                item_base = ""
        self.item_base_type = item_base

    def add_item_element(self, add_element):
        if add_element == 9:
            new_element = random.randint(0, 8)
        else:
            new_element = add_element
        self.item_elements[new_element] = 1

    def add_roll(self, roll_tier):
        if self.item_num_stars < 5:
            self.item_num_stars += 1
            if len(self.item_prefix_values) == 3:
                new_roll, roll_location = self.generate_new_roll("S", roll_tier)
                self.item_suffix_values.append(new_roll)
            elif len(self.item_suffix_values) == 3:
                new_roll, roll_location = self.generate_new_roll("P", roll_tier)
                self.item_prefix_values.append(new_roll)
            else:
                random_num = random.randint(1, 2)
                if random_num == 1:
                    new_roll, roll_location = self.generate_new_roll("P", roll_tier)
                    self.item_prefix_values.append(new_roll)
                else:
                    new_roll, roll_location = self.generate_new_roll("S", roll_tier)
                    self.item_suffix_values.append(new_roll)
        else:
            new_roll, roll_location = self.generate_new_roll("Z", roll_tier)
            if new_roll[0] == "P":
                self.item_prefix_values[roll_location] = new_roll
            else:
                self.item_suffix_values[roll_location] = new_roll

    def reroll_roll(self, roll_type):
        if roll_type == 2:
            new_roll_type = random.randint(0, 1)
        else:
            new_roll_type = roll_type
        random_roll = random.randint(0, 2)
        if new_roll_type == 0:
            selected_roll = self.item_prefix_values[random_roll]
            roll_tier = selected_roll[1]
            self.item_prefix_values[random_roll] = ""
            self.add_roll(roll_tier)
            while selected_roll == self.item_prefix_values[random_roll]:
                self.add_roll(roll_tier)
        else:
            selected_roll = self.item_suffix_values[random_roll]
            roll_tier = selected_roll[1]
            self.item_suffix_values[random_roll] = ""
            self.add_roll(roll_tier)
            while selected_roll == self.item_suffix_values[random_roll]:
                self.add_roll(roll_tier)

    def generate_new_roll(self, roll_type, roll_tier):
        new_roll = ""
        roll_location = 0
        available_identifier = list(string.ascii_lowercase)
        match roll_type:
            case "P":
                affix_type = "P"
                for x in self.item_prefix_values:
                    available_identifier.remove(x[2])
            case "S":
                affix_type = "S"
                for y in self.item_suffix_values:
                    available_identifier.remove(y[2])
            case _:
                if "" in self.item_prefix_values:
                    affix_type = "P"
                    for idx, x in enumerate(self.item_prefix_values):
                        if x != "":
                            available_identifier.remove(x[2])
                        else:
                            roll_location = idx
                else:
                    affix_type = "S"
                    for idy, y in enumerate(self.item_suffix_values):
                        if y != "":
                            available_identifier.remove(y[2])
                        else:
                            roll_location = idy
        random.shuffle(available_identifier)
        new_roll = f"{affix_type}{roll_tier}{available_identifier[0]}"

        return new_roll, roll_location

    def create_citem_embed(self):
        gear_colours = get_gear_tier_colours(self.item_tier)
        tier_colour = gear_colours[0]
        gem_min = 0
        gem_max = 0

        item_title = f'{self.item_name} '
        item_title = item_title.ljust(46, "᲼")
        self.update_damage()
        display_stars = ""
        bonus_type = ""
        aux_suffix = ""
        match self.item_type:
            case "W":
                bonus_type = "Base Attack Speed "
                aux_suffix = "/min"
                thumb_img = "https://i.ibb.co/ygGCRnc/sworddefaulticon.png"
            case "A":
                bonus_type = "Base Damage Mitigation "
                aux_suffix = "%"
                thumb_img = "https://i.ibb.co/p2K2GFK/armouricon.png"
            case "Y":
                thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
            case "G":
                thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
            case "C":
                thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
            case _:
                thumb_img = "https://i.ibb.co/FbhP60F/ringicon.png"
        item_rolls = f'{bonus_type}{self.item_bonus_stat}{aux_suffix}'
        prefix_rolls = ""
        suffix_rolls = ""
        if self.item_prefix_values:
            for x in self.item_prefix_values:
                prefix_rolls += f'\n{get_roll_by_code(self, str(x))} '
                for y in range(int(str(x)[1]) - 1):
                    prefix_rolls += "<:eprl:1148390531345432647>"
        if self.item_suffix_values:
            for x in self.item_suffix_values:
                suffix_rolls += f'\n{get_roll_by_code(self, str(x))} '
                for y in range(int(str(x)[1]) - 1):
                    suffix_rolls += "<:eprl:1148390531345432647>"

        for x in range(self.item_num_stars):
            display_stars += "<:estar1:1143756443967819906>"
        for y in range((5 - self.item_num_stars)):
            display_stars += "<:ebstar2:1144826056222724106>"
            item_types = ""
        if self.item_type != "D":
            item_types = f'{self.item_damage_type}'
            for idz, z in enumerate(self.item_elements):
                if z == 1:
                    item_types += f'{globalitems.global_element_list[idz]}'
            if self.item_num_sockets == 1:
                gem_id = self.item_inlaid_gem_id
                if gem_id == 0:
                    display_stars += " Socket: <:esocket:1148387477615300740>"
                else:
                    gem_emoji = "🔵"
                    display_stars += f" Socket: {gem_emoji} {gem_id}"
                    e_gem = read_custom_item(gem_id)
                    if e_gem:
                        gem_min = e_gem.item_damage_min
                        gem_max = e_gem.item_damage_max
        else:
            gem_min = 0
            gem_max = 0
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
        item_info = f'Item ID: {self.item_id}'
        embed_msg.add_field(name=item_info, value="", inline=False)
        embed_msg.set_thumbnail(url=thumb_img)
        return embed_msg

    def update_damage(self):
        # calculate item's damage per hit
        enh_multiplier = 1 + (float(self.item_enhancement) * 0.01)
        blessing_damage = damagecalc.get_item_tier_damage(self.item_blessing_tier)
        material_damage = damagecalc.get_item_tier_damage(self.item_material_tier)
        self.item_damage_min = int(float(self.base_damage_min + material_damage + blessing_damage) * enh_multiplier)
        self.item_damage_max = int(float(self.base_damage_max + material_damage + blessing_damage) * enh_multiplier)

    def check_augment(self):
        augment_total = 0
        for x in self.item_prefix_values:
            augment_total += int(str(x)[1]) - 1
        for y in self.item_suffix_values:
            augment_total += int(str(y)[1]) - 1
        if len(self.item_prefix_values) + len(self.item_suffix_values) == 0:
            augment_total = -1
        return augment_total

    def add_augment(self):
        check = self.item_prefix_values + self.item_suffix_values
        random.shuffle(check)
        random_num = random.randint(0, self.item_num_stars)
        augment_total = 0
        for x in check:
            augment_total = int(str(x)[1])
            if augment_total != 4:
                selected_roll = x
                break
        if selected_roll[0] == "P":
            roll_location = self.item_prefix_values.index(selected_roll)
            new_id = f'P{augment_total + 1}{str(selected_roll[2])}'
            self.item_prefix_values[roll_location] = new_id
        else:
            roll_location = self.item_suffix_values.index(selected_roll)
            new_id = f'S{augment_total + 1}{str(selected_roll[2])}'
            self.item_suffix_values[roll_location] = new_id

    def give_item(self, new_owner):
        self.player_owner = new_owner
        self.update_stored_item()


class BasicItem:
    def __init__(self):
        self.item_name = ""
        self.item_id = ""
        self.item_tier = 0
        self.item_emoji = ""
        self.item_image = ""
        self.item_description = ""
        self.item_cost = 0

    def create_bitem_embed(self):
        tier_colour, tier_emoji = get_gear_tier_colours(self.item_tier)
        embed_msg = discord.Embed(colour=tier_colour,
                                  title=self.item_name,
                                  description=f"Item ID: {self.item_id} - Item Tier: {self.item_tier}")
        embed_msg.add_field(name="", value=self.item_description, inline=False)
        # embed_msg.set_thumbnail(url=self.item_image)
        return embed_msg


def get_item_shop_list(item_tier):
    df = pd.read_csv("itemlist.csv")
    if item_tier != 0:
        df = df.loc[df['item_tier'] == item_tier]
        df = df.loc[df['item_id'].str.contains('i')]
    else:
        df = df.loc[df['item_id'].str.contains('Fae')]
    item_list = []
    if len(df.index) != 0:
        for index, row in df.iterrows():
            if int(row["item_cost"]) != 0:
                target_item = BasicItem()
                target_item.item_name = str(row["item_name"])
                target_item.item_id = str(row["item_id"])
                target_item.item_tier = int(row["item_tier"])
                target_item.item_emoji = str(row["item_emoji"])
                target_item.item_description = str(row["item_description"])
                target_item.item_cost = int(row["item_cost"])
                target_item.item_image = str(row["item_image"])
                item_list.append(target_item)
    return item_list


def get_basic_item_by_id(item_id):
    df = pd.read_csv("itemlist.csv")
    df = df.loc[df['item_id'] == item_id]
    target_item = None
    if len(df.index) != 0:
        target_item = BasicItem()
        target_item.item_name = str(df["item_name"].values[0])
        target_item.item_id = str(df["item_id"].values[0])
        target_item.item_tier = int(df["item_tier"].values[0])
        target_item.item_emoji = str(df["item_emoji"].values[0])
        target_item.item_description = str(df["item_description"].values[0])
        target_item.item_cost = int(df["item_cost"].values[0])
        target_item.item_image = str(df["item_image"].values[0])
    return target_item


def read_custom_item(item_id):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM CustomInventory WHERE item_id = :id_check")
        query = query.bindparams(id_check=item_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()

        if len(df.index) != 0:
            player_id = int(df['player_id'].values[0])
            item_id = int(df['item_id'].values[0])
            item_type = str(df['item_type'].values[0])
            target_item = CustomItem(player_id, item_type, 1)
            target_item.player_owner = player_id
            target_item.item_id = item_id
            target_item.item_name = str(df['item_name'].values[0])
            temp_elements = list(df['item_elements'].values[0].split(';'))
            target_item.item_elements = list(map(int, temp_elements))
            target_item.item_damage_type = df['item_damage_type'].values[0]
            target_item.item_enhancement = int(df['item_enhancement'].values[0])
            target_item.item_tier = int(df['item_tier'].values[0])
            target_item.item_blessing_tier = str(df['item_blessing_tier'].values[0])
            target_item.item_material_tier = str(df['item_material_tier'].values[0])
            target_item.item_base_type = str(df['item_base_type'].values[0])
            target_item.item_num_stars = int(df['item_num_stars'].values[0])
            if str(df['item_prefix_values'].values[0]) != "":
                target_item.item_prefix_values = list(df['item_prefix_values'].values[0].split(';'))
            else:
                target_item.item_prefix_values = []
            if str(df['item_suffix_values'].values[0]) != "":
                target_item.item_suffix_values = list(df['item_suffix_values'].values[0].split(';'))
            else:
                target_item.item_suffix_values = []
            target_item.item_bonus_stat = str(df['item_bonus_stat'].values[0])
            target_item.base_damage_min = int(df['item_base_dmg_min'].values[0])
            target_item.base_damage_max = int(df['item_base_dmg_max'].values[0])
            target_item.item_num_sockets = int(df['item_num_sockets'].values[0])
            target_item.item_inlaid_gem_id = int(df['item_inlaid_gem_id'].values[0])
            if item_type != "D":
                target_item.update_damage()
            else:
                target_item.item_damage_min = target_item.base_damage_min
                target_item.item_damage_max = target_item.base_damage_max
            return target_item
        else:
            return None
    except exc.SQLAlchemyError as error:
        print(error)
        return None


def generate_item_type():
    random_num = random.randint(1, 9)
    match random_num:
        case 1 | 2 | 3:
            damage_type = "<:cA:1150195102589931641>"
        case 3 | 4 | 5:
            damage_type = "<:cB:1154266777396711424>"
        case 6 | 7 | 8:
            damage_type = "<:cC:1150195246588764201>"
        case _:
            damage_type = "<:cD:1150195280969478254>"
    return damage_type


def get_tier_damage(item_tier):
    match item_tier:
        case 6:
            random_damage1 = random.randint(1, 100000)
            random_damage2 = random.randint(1, 100000)
        case 5:
            random_damage1 = random.randint(1, 25000)
            random_damage2 = random.randint(1, 25000)
        case 4:
            random_damage1 = random.randint(2500, 10000)
            random_damage2 = random.randint(2500, 10000)
        case 3:
            random_damage1 = random.randint(1000, 2500)
            random_damage2 = random.randint(1000, 2500)
        case 2:
            random_damage1 = random.randint(500, 1000)
            random_damage2 = random.randint(500, 1000)
        case _:
            random_damage1 = random.randint(250, 500)
            random_damage2 = random.randint(250, 500)
    if random_damage2 < random_damage1:
        temp_damage = random_damage1
        random_damage1 = random_damage2
        random_damage2 = temp_damage
    return random_damage1, random_damage2


# write item to inventory
def inventory_add_custom_item(item):
    # item elements
    item_elements = ""
    for x in item.item_elements:
        item_elements += str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]

    # item rolls
    item_prefix_values = ""
    item_suffix_values = ""
    item_num_stars = item.item_num_stars
    for x in item.item_prefix_values:
        item_prefix_values += str(x) + ";"
    item_prefix_values = item_prefix_values[:-1]
    for y in item.item_suffix_values:
        item_suffix_values += str(y) + ";"
    item_suffix_values = item_suffix_values[:-1]

    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("INSERT INTO CustomInventory "
                     "(player_id, item_type, item_name, item_damage_type, item_elements, item_enhancement,"
                     "item_tier, item_blessing_tier, item_material_tier, item_base_type,"
                     "item_num_stars, item_prefix_values, item_suffix_values, item_bonus_stat,"
                     "item_base_dmg_min, item_base_dmg_max, item_num_sockets, item_inlaid_gem_id)"
                     "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6, "
                     ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, "
                     ":input_13, :input_14, :input_15, :input_16, :input_17, :input_18) ")
        query = query.bindparams(input_1=item.player_owner, input_2=item.item_type, input_3=item.item_name,
                                 input_4=item.item_damage_type, input_5=item_elements,
                                 input_6=item.item_enhancement, input_7=item.item_tier,
                                 input_8=item.item_blessing_tier, input_9=item.item_material_tier,
                                 input_10=item.item_base_type, input_11=item_num_stars,
                                 input_12=item_prefix_values, input_13=item_suffix_values,
                                 input_14=item.item_bonus_stat,
                                 input_15=item.base_damage_min, input_16=item.base_damage_max,
                                 input_17=item.item_num_sockets, input_18=item.item_inlaid_gem_id)
        pandora_db.execute(query)
        query = text("SELECT MAX(item_id) AS item_id FROM CustomInventory "
                     "WHERE player_id = :player_check AND item_name = :name_check")
        query = query.bindparams(player_check=item.player_owner, name_check=item.item_name)
        df = pd.read_sql(query, pandora_db)
        result_id = int(df['item_id'].values[0])
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)
        return 0

    return int(result_id)


# check if item already exists. Prevent duplication
def if_custom_exists(item_id) -> bool:
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM CustomInventory WHERE item_id = :id_check")
        query = query.bindparams(id_check=item_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            return True
        else:
            return False
    except exc.SQLAlchemyError as error:
        print(str(error))
        return False


def display_cinventory(player_id) -> str:
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT item_id, item_name FROM CustomInventory "
                     "WHERE player_id = :id_check ORDER BY item_tier DESC")
        query = query.bindparams(id_check=player_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        temp = df.style.set_properties(**{'text-align': 'left'}).hide(axis='index').hide(axis='columns')
        player_inventory = temp.to_string()
    except exc.SQLAlchemyError as error:
        print(error)
        player_inventory = ""
    return player_inventory


def display_binventory(player_id):
    filename = 'itemlist.csv'
    item_list = pd.read_csv(filename)
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT item_id, item_qty FROM BasicInventory "
                     "WHERE player_id = :id_check AND item_qty <> 0 ORDER BY item_id DESC")
        query = query.bindparams(id_check=player_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        merged_df = df.merge(item_list, left_on='item_id', right_on='item_id')
        merged_df = merged_df[['item_emoji', 'item_name', 'item_qty']]
        temp = merged_df.style.set_properties(**{'text-align': 'left'}).hide(axis='index').hide(axis='columns')
        player_inventory = temp.to_string()
    except exc.SQLAlchemyError as error:
        print(error)
        player_inventory = ""
    return player_inventory


def get_gear_tier_colours(base_tier):
    match base_tier:
        case 0:
            tier_colour = discord.Colour.dark_gray()
            tier_emoji = '⚫'
        case 1:
            tier_colour = discord.Colour.green()
            tier_emoji = '🟢'
        case 2:
            tier_colour = discord.Colour.blue()
            tier_emoji = '🔵'
        case 3:
            tier_colour = discord.Colour.purple()
            tier_emoji = '🟣'
        case 4:
            tier_colour = discord.Colour.gold()
            tier_emoji = '🟡'
        case 5:
            tier_colour = discord.Colour.red()
            tier_emoji = '🔴'
        case _:
            tier_colour = discord.Colour.pink()
            tier_emoji = '⚪'

    return tier_colour, tier_emoji


def generate_random_tier():
    random_num = random.randint(1, 100)
    if random_num <= 1:
        temp_tier = 4
    elif random_num <= 6:
        temp_tier = 3
    elif random_num <= 40:
        temp_tier = 2
    else:
        temp_tier = 1
    return temp_tier


def check_stock(player_object, item_id):
    player_stock = 0
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT item_qty FROM BasicInventory "
                     "WHERE player_id = :id_check AND item_id = :item_check")
        query = query.bindparams(id_check=player_object.player_id, item_check=item_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            player_stock = int(df.values[0])
    except exc.SQLAlchemyError as error:
        print(error)
    return player_stock


def update_stock(player_object, item_id, change):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT item_qty FROM BasicInventory "
                     "WHERE player_id = :id_check AND item_id = :item_check")
        query = query.bindparams(id_check=player_object.player_id, item_check=item_id)
        df = pd.read_sql(query, pandora_db)
        if len(df.index) != 0:
            player_stock = int(df['item_qty'].values[0])
            player_stock += change
            query = text("UPDATE BasicInventory SET item_qty = :new_qty "
                         "WHERE player_id = :id_check AND item_id = :item_check")
            query = query.bindparams(id_check=player_object.player_id, item_check=item_id, new_qty=player_stock)
            pandora_db.execute(query)
        else:
            if change > 0:
                player_stock = change
            else:
                player_stock = 0
            query = text("INSERT INTO BasicInventory (player_id, item_id, item_qty) "
                         "VALUES(:player_id, :item_id, :new_qty)")
            query = query.bindparams(item_id=item_id, player_id=player_object.player_id, new_qty=player_stock)
            pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)


def get_roll_by_code(item_object, code):
    roll_text = ""
    check_roll = ord(code[2])
    text_method = 1
    match code[0]:
        case "P":
            if check_roll <= 106:
                roll_num = check_roll - 97
                if roll_num == 9:
                    roll_adjust = 8
                    roll_keyword = "Omni"
                else:
                    roll_adjust = 20
                    roll_keyword = globalitems.element_names[roll_num]
                roll = f"{roll_keyword} Damage"
            elif check_roll <= 116:
                roll_num = check_roll - 97 - 10
                if roll_num == 9:
                    roll_adjust = 7
                    roll_keyword = "Omni"
                else:
                    roll_adjust = 15
                    roll_keyword = globalitems.element_names[roll_num]
                roll = f"{roll_keyword} Penetration"
            else:
                match check_roll:
                    case 117:
                        roll = "Damage Mitigation"
                        roll_adjust = 15
                    case 118:
                        roll = "Health Regen"
                        roll_adjust = 1
                    case 119:
                        roll = "Health Bonus"
                        roll_adjust = 250
                        text_method = 2
                    case 120:
                        roll = "Health Multiplier"
                        roll_adjust = 15
                    case 121:
                        roll = "Omni Aura"
                        roll_adjust = 5
                    case _:
                        roll = "Class Mastery"
                        roll_adjust = 3
            bonus = str((1 + int(code[1])) * roll_adjust)
            roll_text += f'+{bonus}% {roll}'
        case "S":
            if check_roll <= 106:
                roll_num = check_roll - 97
                if roll_num == 9:
                    roll_keyword = "Omni"
                    roll_adjust = 5
                else:
                    roll_keyword = globalitems.element_names[roll_num]
                    roll_adjust = 10
                roll = f"{roll_keyword} Resistance"
            elif check_roll <= 116:
                roll_num = check_roll - 97 - 10
                if roll_num == 9:
                    roll_adjust = 6
                    roll_keyword = "Omni"
                else:
                    roll_adjust = 12
                    roll_keyword = globalitems.element_names[roll_num]
                roll = f"{roll_keyword} Curse"
            elif check_roll >= 119:
                roll_num = check_roll - 119
                roll_adjust = 20
                roll = f"{bosses.boss_list[roll_num]} Bane"
            else:
                match check_roll:
                    case 117:
                        roll = "Critical Chance"
                        roll_adjust = 20
                    case 118:
                        roll = "Critical Multiplier"
                        roll_adjust = 15
                    case _:
                        nothing = True
            bonus = str((1 + int(code[1])) * roll_adjust)
            if text_method == 1:
                roll_text += f'+{bonus}% {roll}'
            elif text_method == 2:
                roll_text += f'+{bonus} {roll}'
        case _:
            roll_text = "Error"
    return roll_text


def try_refine(player_owner, item_type, selected_tier):
    if selected_tier == 4:
        new_tier = generate_random_tier()
    else:
        new_tier = selected_tier
    match item_type:
        case "Dragon Heart Gem":
            new_item = CustomItem(player_owner, "D", new_tier)
        case "Dragon Wing":
            new_item = CustomItem(player_owner, "G", new_tier)
        case "Paragon Crest":
            new_item = CustomItem(player_owner, "C", new_tier)
        case "Fabled Item":
            item_typelist = ["W", "A", "Y", "G", "C", "D"]
            random_type = random.randint(0, 5)
            new_item = CustomItem(player_owner, item_typelist[random_type], selected_tier)
        case _:
            new_item = CustomItem(player_owner, "W", selected_tier)
    if new_tier != 1:
        new_item.item_id = 0
    else:
        new_item.item_id = -1

    return new_item


def sell(user, item, embed_msg):
    reload_player = player.get_player_by_id(user.player_id)
    response_embed = embed_msg
    response = user.check_equipped(item)
    sell_value = item.item_tier * 250
    if response == "":
        reload_player.player_coins += sell_value
        reload_player.set_player_field("player_coins", reload_player.player_coins)
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("DELETE FROM CustomInventory "
                         "WHERE item_id = :item_check")
            query = query.bindparams(item_check=item.item_id)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
            currency_msg = f'You now have {reload_player.player_coins} lotus coins!'
            response_embed.add_field(name=f"Item Sold! {sell_value} lotus coins acquired!",
                                     value=currency_msg, inline=False)
        except exc.SQLAlchemyError as error:
            print(error)
            response = "Database Error!"
            response_embed.add_field(name="Item Not Sold!", value=response, inline=False)
    else:
        response_embed.add_field(name="Item Not Sold!", value=response, inline=False)
    return response_embed


def purge(player_object, tier):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        player_object.get_equipped()
        exclusion_list = [player_object.equipped_weapon, player_object.equipped_armour, player_object.equipped_acc,
                          player_object.equipped_wing, player_object.equipped_crest]
        inlaid_gem_list = []
        for x in exclusion_list:
            if x != 0:
                e_item = inventory.read_custom_item(x)
                if e_item.item_inlaid_gem_id != 0:
                    inlaid_gem_list.append(e_item.item_inlaid_gem_id)
        exclusion_list += inlaid_gem_list
        query = text("SELECT item_tier FROM CustomInventory "
                     "WHERE player_id = :id_check AND item_tier <= :tier_check "
                     "AND item_id NOT IN :excluded_ids")
        query = query.bindparams(id_check=player_object.player_id, tier_check=tier, excluded_ids=exclusion_list)
        df = pd.read_sql(query, pandora_db)
        query = text("DELETE FROM CustomInventory "
                     "WHERE player_id = :id_check AND item_tier <= :tier_check "
                     "AND item_id NOT IN :excluded_ids")
        query = query.bindparams(id_check=player_object.player_id, tier_check=tier, excluded_ids=exclusion_list)
        pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
        result = len(df)
        total_tiers = df['item_tier'].sum()
        coin_total = total_tiers * 250
    except exc.SQLAlchemyError as error:
        print(error)
        result = 0
        coin_total = 0
    return result, coin_total
