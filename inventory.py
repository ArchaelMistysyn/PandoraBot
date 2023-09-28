import csv
import random
import bosses
import damagecalc
import pandas as pd
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


class CustomItem:
    def __init__(self, player_owner, item_type, item_tier):
        # initialize owner id
        self.player_owner = player_owner
        self.item_type = item_type
        self.item_tier = item_tier
        self.item_damage_type = generate_item_type()
        self.generate_base()

        # initialize default values
        self.item_id = 0
        self.item_name = ""
        self.item_elements = []
        self.item_enhancement = 0
        self.item_num_stars = 1
        self.item_suffix_values = []
        self.item_prefix_values = []
        self.item_bonus_stat = ""
        self.item_damage_min = 0
        self.item_damage_max = 0
        self.item_num_sockets = 0
        self.item_inlaid_gem_id = 0
        special_name = ""
        prefix = ""

        random_damage1, random_damage2 = get_tier_damage(item_tier)
        match self.item_type:
            case "W":
                if self.item_damage_type == class_summoner:
                    self.item_blessing_tier = "Standard"
                    self.item_material_tier = "Illusion"
                else:
                    self.item_material_tier = "Iron"
                    self.item_blessing_tier = "Basic"
                match self.item_tier:
                    case 6:
                        bonus_roll = random.randint(21, 30)
                        self.item_bonus_stat = str(float(bonus_roll) * 0.1)
                        prefix = "Relic"
                        self.item_material_tier = "Special"
                        self.item_blessing_tier = "Special"
                    case 5:
                        prefix = "Rift"
                        self.item_material_tier = "Special"
                        self.item_blessing_tier = "Special"
                        bonus_roll = random.randint(16, 20)
                        self.item_bonus_stat = str(float(bonus_roll) * 0.1)
                    case 4:
                        self.item_bonus_stat = "1.5"
                    case 3:
                        self.item_bonus_stat = "1.3"
                    case 2:
                        self.item_bonus_stat = "1.2"
                    case _:
                        self.item_bonus_stat = "1.1"
                self.item_elements.append(bosses.get_element(0))
                if prefix != "":
                    class_matcher = pandorabot.class_icon_list.index(self.item_damage_type)
                    item_variant = random.randint(0, 1)
                    match class_matcher:
                        case 0:
                            if item_variant == 0:
                                suffix = "Saber"
                            else:
                                suffix = "Scythe"
                        case 1:
                            if item_variant == 0:
                                suffix = "Cannon"
                            else:
                                suffix = "Bow"
                        case 2:
                            if item_variant == 0:
                                suffix = "Staff"
                            else:
                                suffix = "Spellbook"
                        case 3:
                            if item_variant == 0:
                                suffix = "Dagger"
                            else:
                                suffix = "Claws"
                        case 4:
                            suffix = "Threads"
                        case 5:
                            if item_variant == 0:
                                suffix = "Dragon"
                            else:
                                suffix = "Cerberus"
                        case _:
                            if item_variant == 0:
                                suffix = "Anima"
                            else:
                                suffix = "Golem"
                    special_name = f"+{self.item_enhancement} {prefix} {suffix}"
            case "A":
                self.item_material_tier = "Iron"
                self.item_blessing_tier = "Standard"
                match self.item_tier:
                    case 4:
                        self.item_bonus_stat = "25"
                    case 3:
                        self.item_bonus_stat = "15"
                    case 2:
                        self.item_bonus_stat = "10"
                    case _:
                        self.item_bonus_stat = "5"
            case "Y":
                self.item_material_tier = "Crude"
                self.item_blessing_tier = "Sparkling"
                self.item_bonus_stat = assign_bonus_stat(self.item_tier)
            case "G":
                self.item_material_tier = "Crude"
                self.item_blessing_tier = "Sparkling"
                match self.item_tier:
                    case 4:
                        self.item_base_type = "Dimensional Wings"
                    case 3:
                        self.item_base_type = "Wonderous Wings"
                    case 2:
                        self.item_base_type = "Lucent Wings"
                    case _:
                        self.item_base_type = "Feathered Wings"
                self.item_bonus_stat = assign_bonus_stat(self.item_tier)
            case "C":
                self.item_material_tier = "Iron"
                random_blessing = random.randint(1, 2)
                if random_blessing == 1:
                    self.item_blessing_tier = "Light"
                else:
                    self.item_blessing_tier = "Dark"
                random_num = random.randint(1, 2)
                # set crest unique skill
                match self.item_tier:
                    case 4:
                        match random_num:
                            case 1:
                                self.item_bonus_stat = "Elemental Fractal"
                            case _:
                                self.item_bonus_stat = "Omega Critical"
                    case 3:
                        match random_num:
                            case 1:
                                self.item_bonus_stat = "Specialized Mastery"
                            case _:
                                self.item_bonus_stat = "Ignore Protection"
                    case 2:
                        match random_num:
                            case 1:
                                self.item_bonus_stat = "Perfect Precision"
                            case _:
                                self.item_bonus_stat = "Resistance Bypass"
                    case _:
                        match random_num:
                            case 1:
                                self.item_bonus_stat = "Extreme Vitality"
                            case _:
                                self.item_bonus_stat = "Defence Bypass"
            case _:
                random_variant = random.randint(1, 2)
                match self.item_tier:
                    case 6:
                        self.item_name = "Gem of the Infinite"
                        self.item_prefix_values += ["P6b", "P6c"]
                        self.item_suffix_values += ["S6b", "S6c"]
                    case 4:
                        self.item_name = "Gem of Dimensions"
                        self.item_prefix_values += ["P4b", "P4c"]
                        self.item_suffix_values += ["S4b", "S4c"]
                    case 3:
                        if random_variant == 1:
                            self.item_name = "Gem of Chaos"
                            self.item_prefix_values += ["P3a", "P3b"]
                            self.item_suffix_values += ["S3b", "S3c"]
                        else:
                            self.item_name = "Gem of Twilight"
                            self.item_prefix_values += ["P3a", "P3c"]
                            self.item_suffix_values += ["S3a", "S3b"]
                    case 2:
                        if random_variant == 1:
                            self.item_name = "Gem of Clarity"
                            self.item_prefix_values += ["P2a", "P2b"]
                            self.item_suffix_values += ["S2b", "S2c"]
                        else:
                            self.item_name = "Gem of Nature's Wrath"
                            self.item_prefix_values += ["P2a", "P2c"]
                            self.item_suffix_values += ["S2a", "S2b"]
                    case _:
                        if random_variant == 1:
                            self.item_name = "Gem of the Deep"
                            self.item_prefix_values += ["P1a", "P1b"]
                            self.item_suffix_values += ["S1b", "S1c"]
                        else:
                            self.item_name = "Gem of Land and Sky"
                            self.item_prefix_values += ["P1a", "P1c"]
                            self.item_suffix_values += ["S1a", "S1b"]
        if random_damage1 < random_damage2:
            self.base_damage_min = random_damage1
            self.base_damage_max = random_damage2
        else:
            self.base_damage_min = random_damage2
            self.base_damage_max = random_damage1
        self.update_damage()
        self.set_item_name()
        if special_name != "":
            self.item_name = special_name

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
            query = text("UPDATE CustomInventory"
                         "SET player_id = :input_1,"
                         "item_type = :input_2, item_name = :input_3,"
                         "item_damage_type = :input_4, item_elements = :input_5,"
                         "item_enhancement = :input_6, item_tier = :input_7,"
                         "item_blessing_tier = :input_8, item_material_tier = :input_9,"
                         "item_base_type = :input_10, item_num_stars = :input_11,"
                         "item_prefix_values = :input_12, item_suffix_values = input_13,"
                         "item_bonus_stat = :input_14,"
                         "item_base_dmg_min = :input_15, item_base_dmg_max = :input_16,"
                         "item_num_sockets = :input_17, item_inlaid_gem_id = :input_18"
                         "WHERE item_id = :id_check")
            query = query.bindparams(id_check=int(item_id), input_1=int(self.player_owner),
                                     input_2=int(self.item_type), input_3=str(self.item_name),
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
                special_item_list = None
                tier_location = self.item_tier - 1
                random_num = random.randint(0, 6)
                class_checker = pandorabot.class_icon_list.index(self.item_damage_type)
                match class_checker:
                    case 0:
                        item_list_t1 = ["Shortsword", "Handaxe", "Javelin"]
                        item_list_t2 = ["Sword", "Axe", "Spear"]
                        item_list_t3 = ["Longsword", "Battle Axe", "Longspear"]
                        item_list_t4 = ["Greatsword", "Greataxe", "Trident"]
                    case 1:
                        item_list_t1 = ["Shortbow", "Ballista"]
                        item_list_t2 = ["Longbow", "Arbalest"]
                        item_list_t3 = ["Recurve Bow", "Gun"]
                        item_list_t4 = ["Greatbow", "Blaster"]
                    case 2:
                        item_list_t1 = ["Lesser Wand", "Lesser Staff", "Lesser Tome", "Lesser Orb"]
                        item_list_t2 = ["Magic Wand", "Magic Staff", "Magic Tome", "Crystal Ball"]
                        item_list_t3 = ["Sceptre", "Quarterstaff", "Grimoire", "Seer Sphere"]
                        item_list_t4 = ["Rod", "Crescent Staff", "Spellbook", "Orb"]
                    case 3:
                        item_list_t1 = ["Dagger", "Claws", "Darts"]
                        item_list_t2 = ["Stiletto", "Tiger Claws", "Tomahawk"]
                        item_list_t3 = ["Kris", "Eagle Claws", "Kunai"]
                        item_list_t4 = ["Sai", "Dragon Talons", "Shuriken"]
                    case 4:
                        item_list_t1 = ["Steel String"]
                        item_list_t2 = ["Cutting Wire"]
                        item_list_t3 = ["Razor Threads"]
                        item_list_t4 = ["Infused Threads"]
                    case 5:
                        special_item_list = ["Pegacorn", "Night Mare", "Unicorn", "Pegasus",
                                             "Wyvern", "Roc", "Gryphon", "Manta Ray",
                                             "Liger", "Bear", "Elephant", "Wolf"]
                    case _:
                        special_item_list = ["Zombie", "Ghoul", "Skeleton", "Specter"
                                             "Fox", "Spider", "Crocodile", "Basilisk"
                                             "Wyrm", "Salamander", "Coatl", "Phoenix"]
                if not special_item_list.empty:
                    random_position = random.randint(0, 11)
                    item_base = special_item_list[random_position]
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
                        item_base = "error"
            case "Y":
                random_number = random.randint(1, 5)
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
                            if new_roll[2] == str(x)[2]:
                                running = True
                else:
                    random_identifier = random.randint(1, 5)
                    new_roll = f"{roll_type}{tier}{random_identifier}"
            case "S":
                if self.item_suffix_values:
                    while running:
                        running = False
                        for y in self.item_suffix_values:
                            random_identifier = random.randint(1, 4)
                            new_roll = f"{roll_type}{tier}{random_identifier}"
                            if new_roll[2] == str(y)[2]:
                                running = True
                else:
                    random_identifier = random.randint(1, 4)
                    new_roll = f"{roll_type}{tier}{random_identifier}"
            case _:
                new_roll = "Error"
        return new_roll

    def create_citem_embed(self):
        gear_colours = get_gear_tier_colours(self.item_tier)
        tier_colour = gear_colours[0]
        gem_min = 0
        gem_max = 0

        item_title = f'{self.item_name} '
        item_title = item_title.ljust(46, "᲼")

        if self.item_type == "D":
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
                    prefix_rolls += f'\n{get_roll_by_code(str(x), self.item_type)} '
                    for y in range(int(str(x)[1]) - 1):
                        prefix_rolls += "<:eprl:1148390531345432647>"
            if self.item_suffix_values:
                for x in self.item_suffix_values:
                    suffix_rolls += f'\n{get_roll_by_code(str(x), self.item_type)} '
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
                    gem_emoji = "🔵"
                    display_stars += f" Socket: {gem_emoji} {gem_id}"
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
        item_info = f'Item ID: {self.item_id}'
        embed_msg.add_field(name=item_info, value="", inline=False)
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


def gem_stat_reader(item_code):
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

        if not df.empty:
            player_id = int(df['player_id'].values[0])
            item_id = int(df['item_id'].values[0])
            item_type = str(df['item_type'].values[0])
            target_item = CustomItem(player_id, item_type, 1)
            target_item.player_owner = player_id
            target_item.item_id = item_id
            target_item.item_name = str(df['item_name'].values[0])
            item_elements = str(df['item_elements'].values[0])
            if str(df['item_elements'].values[0]) != "":
                target_item.item_elements = list(df['item_elements'].values[0].split(';'))
            target_item.item_damage_type = df['item_damage_type'].values[0]
            target_item.item_enhancement = int(df['item_enhancement'].values[0])
            target_item.item_tier = int(df['item_tier'].values[0])
            target_item.item_blessing_tier = str(df['item_blessing_tier'].values[0])
            target_item.item_material_tier = str(df['item_material_tier'].values[0])
            target_item.item_num_stars = int(df['item_num_stars'].values[0])
            if str(df['item_prefix_values'].values[0]) != "":
                target_item.item_prefix_values = list(df['item_prefix_values'].values[0].split(';'))
            if str(df['item_suffix_values'].values[0]) != "":
                target_item.item_suffix_values = list(df['item_suffix_values'].values[0].split(';'))
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


def generate_item_type() -> str:
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
            random_damage1 = random.randint(1, 500)
            random_damage2 = random.randint(1, 500)
    return random_damage1, random_damage2


# write item to inventory
def inventory_add_custom_item(item) -> str:
    # item elements
    item_elements = ""
    for x in item.item_elements:
        item_elements = str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]

    # item rolls
    item_prefix_values = ""
    item_suffix_values = ""
    item_num_stars = item.item_num_stars
    if item.item_id == "D":
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
                     "VALUES(:input_1, :input_2, :input_3, :input_4, :input_5, :input_6, "
                     ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, "
                     ":input_13, :input_14, :input_15, :input_16, :input_17, :input_18)")
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
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)

    return 'You have placed the item in your inventory'


# check if item already exists. Prevent duplication
def if_custom_exists(item_id) -> bool:
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM CustomInventory WHERE item_id = :id_check")
        query = query.bindparams(id_check=str(item_id))
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if int(item_id) == int(df['item_id'].values[0]):
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
                     "WHERE player_id = :id_check ORDER BY item_id DESC")
        query = query.bindparams(id_check=player_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        merged_df = df.merge(item_list, left_on='item_id', right_on='item_id')
        merged_df = merged_df[merged_df['player_id'] == player_id][['item_emoji', 'item_name', 'item_qty']]
        merged_df = merged_df[merged_df['item_qty'] != 0][['item_emoji', 'item_name', 'item_qty']]
        # merged_df = merged_df.sort_values(ascending=True)
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
                        blessing_tier_list = ["Standard", "Faint", "Luminous", "Lustrous", "Radiant", "Divine",
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
                            new_element = bosses.get_element(0)
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


def generate_random_tier():
    random_num = random.randint(1, 100)
    if random_num <= 1:
        temp_tier = 4
    elif random_num <= 6:
        temp_tier = 3
    elif random_num <= 21:
        temp_tier = 2
    else:
        temp_tier = 1
    return temp_tier


def check_stock(player_object, item_id):
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
        if not df.empty:
            player_stock = int(df.values[0])
        else:
            player_stock = 0
    except exc.SQLAlchemyError as error:
        print(error)
        player_stock = 0
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
        if not df.empty:
            player_stock = int(df.values[0])
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
            query = text("INSERT INTO BasicInventory VALUES (:new_qty) "
                         "WHERE player_id = :id_check AND item_id = :item_check")
            query = query.bindparams(id_check=player_object.player_id, item_check=item_id, new_qty=player_stock)
            pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)


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
                    bonus = str(int(code[1])*0.25)
                    roll_text = f"Aura: +{bonus}x Team Damage"
                case "3":
                    bonus = str(int(code[1])*0.25)
                    roll_text = f"Curse: +{bonus}x Boss Damage Received"
                case "4":
                    bonus = str(int(code[1]) + 1)
                    if item_type == "W":
                        roll_text = f"Multi-Hit: {bonus}x Combo"
                    else:
                        bonus = str(int(code[1]) * 50)
                        roll_text = f"+{bonus} HP%"
                case _:
                    roll_text = "Error"
        case _:
            roll_text = "Error"
    return roll_text


def try_refine(player_owner, item_type, selected_tier):
    match item_type:
        case "Dragon Heart Gem":
            new_item = CustomItem(player_owner, "D", selected_tier)
        case "Dragon Wing":
            new_item = CustomItem(player_owner, "G", selected_tier)
        case "Paragon Crest":
            new_item = CustomItem(player_owner, "C", selected_tier)
        case _:
            new_item = CustomItem(player_owner, "W", selected_tier)

    random_num = random.randint(1, 100)
    if random_num > 25:
        new_item.item_id = 0

    return new_item


def assign_bonus_stat(base_tier):
    random_num = random.randint(1, 4)
    # set accessory unique skill
    match base_tier:
        case 4:
            match random_num:
                case 1:
                    unique_skill = "Bahamut's Grace"
                case 2:
                    unique_skill = "Curse of Immorality"
                case _:
                    unique_skill = "Perfect Counter"
        case 3:
            match random_num:
                case 1:
                    unique_skill = "Coup de Grace"
                case 2:
                    unique_skill = "Final Stand"
                case 3:
                    unique_skill = "Mountain's Will"
                case _:
                    unique_skill = "Inferno's Will"
        case 2:
            match random_num:
                case 1:
                    unique_skill = "Breaker"
                case 2:
                    unique_skill = "Last Breath"
                case 3:
                    unique_skill = "Guardian Stance"
                case _:
                    unique_skill = "Onslaught Stance"
        case _:
            match random_num:
                case 1:
                    unique_skill = "First Blood"
                case 2:
                    unique_skill = "Hybrid Stance"
                case 3:
                    unique_skill = "Defensive Stance"
                case _:
                    unique_skill = "Offensive Stance"
    return unique_skill


def sell(user, item, embed_msg):
    reload_player = player.get_player_by_id(user.player_id)
    response_embed = embed_msg
    response = user.check_equipped(user, item)
    sell_value = item.item_tier * 100
    if response == "":
        reload_player.player_coins += sell_value
        reload_player.set_player_field("player_coins", user.player_coins)
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
