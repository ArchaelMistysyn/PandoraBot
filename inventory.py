import csv
import random
import bosses
import combat
import pandas as pd
import discord
import re
from discord.ui import Button, View

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
import globalitems
import string
import itemrolls
import itemicons
import itemdata

import tarot

custom_item_dict = {"W": "Weapon", "A": "Armour", "Y": "Accessory", "G": "Wing", "C": "Crest",
                    "D": "Dragon Heart Gem", "T": "Tarot Card"}
item_loc_dict = {'W': 0, 'A': 1, 'Y': 2, 'G': 3, 'C': 4, 'D': 5}
item_type_dict = {0: "Weapon", 1: "Armour", 2: "Accessory", 3: "Wing", 4: "Crest"}
reverse_item_dict = {v: k for k, v in item_type_dict.items()}


class BInventoryView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.select(
        placeholder="Select Inventory Type!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crafting", description="Crafting Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fae Cores", description="Fae Cores"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Materials", description="Material Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unprocessed", description="Unprocessed Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Misc", description="Misc Items")
        ]
    )
    async def inventory_callback(self, interaction: discord.Interaction, inventory_select: discord.ui.Select):
        try:
            if interaction.user.name == self.user.player_name:
                inventory_title = f'{self.user.player_username}\'s {inventory_select.values[0]} Inventory:\n'
                player_inventory = display_binventory(self.user.player_id, inventory_select.values[0])

                new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title,
                                          description=player_inventory)
                await interaction.response.edit_message(embed=new_embed)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Gear", style=discord.ButtonStyle.blurple, emoji="✅")
    async def toggle_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.user.player_name:
                new_view = CInventoryView(self.user)
                inventory_title = f'{self.user.player_username}\'s Equipment:\n'
                player_inventory = display_cinventory(self.user.player_id, "W")
                new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title,
                                          description=player_inventory)
                await interaction.response.edit_message(embed=new_embed, view=new_view)
        except Exception as e:
            print(e)


class CInventoryView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.select(
        placeholder="Select Inventory Type!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Weapon", value="W", description="Stored Weapons"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Armour", value="A", description="Stored Armour"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Accessory", value="Y", description="Stored Accessories"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wing", value="G", description="Stored Wings"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crest", value="C", description="Stored Crests"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Gem", value="D", description="Stored Gems")
        ]
    )
    async def inventory_callback(self, interaction: discord.Interaction, inventory_select: discord.ui.Select):
        try:
            if interaction.user.name == self.user.player_name:
                inventory_title = f'{self.user.player_username}\'s Inventory:\n'
                player_inventory = display_cinventory(self.user.player_id, inventory_select.values[0])

                new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title,
                                          description=player_inventory)
                await interaction.response.edit_message(embed=new_embed)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Items", style=discord.ButtonStyle.blurple, emoji="✅")
    async def toggle_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.user.player_name:
                new_view = BInventoryView(self.user)
                inventory_title = f'{self.user.player_username}\'s Inventory:\n'
                player_inventory = display_binventory(self.user.player_id, "Crafting")
                new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title,
                                          description=player_inventory)
                await interaction.response.edit_message(embed=new_embed, view=new_view)
        except Exception as e:
            print(e)


class CustomItem:
    def __init__(self, player_owner, item_type, item_tier):
        # initialize input data.
        self.player_owner = player_owner
        self.item_type = item_type
        self.item_tier = item_tier
        self.item_num_stars = self.item_tier

        # Initialize single default values
        self.item_id, self.item_name = 0, ""
        self.item_enhancement = 0
        self.item_elements = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        # Initialize associated default values.
        self.item_num_rolls, self.item_roll_values = 0, []
        self.item_base_stat, self.item_bonus_stat = 0, ""
        self.item_material_tier, self.item_blessing_tier = "", ""
        self.item_damage_min, self.item_damage_max = 0, 0
        self.item_num_sockets, self.item_inlaid_gem_id = 0, 0

        # Generate an item type and base.
        self.item_damage_type = generate_item_type()
        self.item_base_type = ""
        self.generate_base()

        # Generate base damage.
        self.base_damage_min, self.base_damage_max = get_tier_damage(self.item_tier, self.item_type)
        self.update_damage()

        # Add an element to non-gem items and set the name.
        if self.item_type != "D":
            itemrolls.add_roll(self, 1)
            self.add_item_element(9)
            self.set_item_name()

    def reforge_stats(self):
        if self.item_type == "W":
            self.set_base_attack_speed()
        if self.item_type in "AYGC":
            if self.item_type == "A":
                self.set_base_damage_mitigation()
            if self.item_bonus_stat not in globalitems.void_ability_dict:
                current_bonus_stat = self.item_bonus_stat
                while current_bonus_stat == self.item_bonus_stat and current_bonus_stat != "":
                    self.assign_bonus_stat()
        random_damage1, random_damage2 = get_tier_damage(self.item_tier, self.item_type)
        self.base_damage_min = random_damage1
        self.base_damage_max = random_damage2

    def set_base_attack_speed(self):
        speed_range_list = [(1.00, 1.20), (1.21, 1.50), (1.51, 1.90), (1.91, 2.40),
                            (2.41, 3.00), (3.01, 4.00), (4.01, 5.00)]
        selected_range = speed_range_list[(self.item_tier - 1)]
        random_speed = round(random.uniform(selected_range[0], selected_range[1]), 2)
        self.item_base_stat = f"{random_speed}"

    def set_base_damage_mitigation(self):
        random_mitigation = random.randint(1 + ((self.item_tier - 1) * 5), (self.item_tier * 5))
        self.item_base_stat = f"{random_mitigation}"

    def assign_bonus_stat(self):
        unique_skill = ""
        if self.item_tier < 5 and self.item_type != "A":
            random_pos = random.randint(0, 8)
            keyword = globalitems.element_special_names[random_pos]
            if self.item_type == "Y":
                random_pos = random.randint(0, 4)
                if random_pos != 4:
                    keyword = bosses.boss_list[random_pos]
                else:
                    keyword = "Human"
                descriptor = "Bane"
            elif self.item_type == "G":
                descriptor = "Feathers"
            else:
                descriptor = "Authority"
            unique_skill = f"{keyword} {descriptor}"
        elif self.item_tier >= 5:
            unique_skill = random.choice(list(globalitems.tier_5_ability_dict.keys()))
        if unique_skill != "":
            self.item_bonus_stat = unique_skill

    def update_stored_item(self):
        item_elements = ""
        for x in self.item_elements:
            item_elements += str(x) + ";"
        if item_elements != "":
            item_elements = item_elements[:-1]
        item_roll_values = ""
        for x in self.item_roll_values:
            item_roll_values += str(x) + ";"
        if item_roll_values != "":
            item_roll_values = item_roll_values[:-1]
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
                         "item_roll_values = :input_12, "
                         "item_base_stat = :input_13, item_bonus_stat = :input_14, "
                         "item_base_dmg_min = :input_15, item_base_dmg_max = :input_16, "
                         "item_num_sockets = :input_17, item_inlaid_gem_id = :input_18 "
                         "WHERE item_id = :id_check")
            query = query.bindparams(id_check=int(self.item_id), input_1=int(self.player_owner),
                                     input_2=str(self.item_type), input_3=str(self.item_name),
                                     input_4=str(self.item_damage_type), input_5=str(item_elements),
                                     input_6=int(self.item_enhancement), input_7=int(self.item_tier),
                                     input_8=str(self.item_blessing_tier), input_9=str(self.item_material_tier),
                                     input_10=str(self.item_base_type), input_11=int(self.item_num_stars),
                                     input_12=str(item_roll_values),
                                     input_13=str(self.item_base_stat), input_14=str(self.item_bonus_stat),
                                     input_15=int(self.base_damage_min), input_16=int(self.base_damage_max),
                                     input_17=int(self.item_num_sockets), input_18=int(self.item_inlaid_gem_id))

            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except exc.SQLAlchemyError as error:
            print(error)

    def set_item_name(self):
        if self.item_blessing_tier != "":
            item_descriptor = f"{self.item_blessing_tier} {self.item_material_tier}"
            if self.item_tier == 6 and self.item_type == "W":
                item_descriptor = f"{self.item_material_tier} {self.item_blessing_tier}"
        else:
            item_descriptor = self.item_material_tier
        item_name = f"+{self.item_enhancement} {item_descriptor} {self.item_base_type}"
        self.item_name = item_name

    def generate_base(self):
        item_lists = {
            0: [["Shortsword", "Handaxe", "Javelin"],
                ["Sword", "Axe", "Spear"],
                ["Longsword", "Battle Axe", "Longspear"],
                ["Greatsword", "Greataxe", "Trident"]],
            1: [["Shortbow", "Ballista"],
                ["Longbow", "Arbalest"],
                ["Recurve Bow", "Gun"],
                ["Greatbow", "Blaster"]],
            2: [["Lesser Wand", "Lesser Staff", "Lesser Tome", "Lesser Orb"],
                ["Magic Wand", "Magic Staff", "Magic Tome", "Crystal Ball"],
                ["Sceptre", "Quarterstaff", "Grimoire", "Seer Sphere"],
                ["Rod", "Crescent Staff", "Spellbook", "Orb"]],
            3: [["Dagger", "Claws", "Darts"],
                ["Stiletto", "Tiger Claws", "Tomahawk"],
                ["Kris", "Eagle Claws", "Kunai"],
                ["Sai", "Dragon Talons", "Shuriken"]],
            4: [["Steel String"],
                ["Cutting Wire"],
                ["Razor Threads"],
                ["Infused Threads"]],
            5: [["Pegacorn", "Night Mare", "Unicorn", "Pegasus",
                 "Wyvern", "Roc", "Gryphon", "Manta Ray",
                 "Liger", "Bear", "Elephant", "Wolf"]],
            "_": [["Zombie", "Ghoul", "Skeleton", "Specter",
                   "Fox", "Spider", "Crocodile", "Basilisk",
                   "Wyrm", "Salamander", "Coatl", "Phoenix"]]
        }
        special_weapon_variants = [
            ["Saber", "Scythe"],
            ["Cannon", "Bow"],
            ["Staff", "Spellbook"],
            ["Dagger", "Claws"],
            ["Threads"], ["Threads"],
            ["Dragon", "Cerberus"],
            ["Anima", "Golem"]
        ]

        default_material_names = {"W": "Iron", "A": "Iron", "Y": "Crude",  "G": "Crude", "C": "Crude"}
        default_blessing_names = {"W": "Basic", "A": "Standard", "Y": "Sparkling",  "G": "Sparkling", "C": "Clear"}
        wing_tier_variants = ["Feathered Wings", "Wonderous Wings", "Dimensional Wings", "Rift Wings"]
        gem_names_dict = {1: ["Unknown Gem"],
                          2: ["Gem of Nature's Wrath", "Gem of Land and Sky", "Gem of the Deep"],
                          3: ["Gem of Twilight", "Gem of Chaos", "Gem of Aurora"],
                          4: ["Gem of Dimensions", "Gem of Fate", "Gem of Dreams"],
                          5: ["Fabled Dragon Jewel - Destiny", "Fabled Dragon Jewel - Fate"],
                          6: ["Miracle Dragon Heart Gem"],
                          7: ["Miracle Dragon Heart Gem - Emptiness", "Miracle Dragon Heart Gem - Transcendence"]
                          }

        # Set non gem shared default naming values and base roll.
        if self.item_type != "D":
            if self.item_tier == 7:
                self.item_material_tier = "Eschaton"
                self.item_blessing_tier = ""
            elif self.item_tier == 6:
                self.item_material_tier = "Destiny"
                self.item_blessing_tier = ""
                # Naming exception for tier 6 weapons.
                if self.item_type == "W":
                    self.item_material_tier = "Key of Creation -"
                    self.item_blessing_tier = "Prelude"
            elif self.item_tier == 5:
                self.item_material_tier = "Fabled"
                self.item_blessing_tier = "Refined"
            elif self.item_tier <= 4:
                self.item_material_tier = default_material_names[self.item_type]
                self.item_blessing_tier = default_blessing_names[self.item_type]
                # Naming exception for rider and summoner weapons of tier 4 or lower.
                if self.item_damage_type == "Summoner" or self.item_damage_type == "Rider" and self.item_type == "W":
                    self.item_blessing_tier = "Standard"
                    self.item_material_tier = "Illusion"
                # Naming exception for crests tier 4 or lower.
                if self.item_type == "C":
                    random_blessing = random.randint(1, 2)
                    self.item_blessing_tier = "Clear" if random_blessing == 1 else "Tainted"

        # Assign a bonus stat if eligible.
        if self.item_type in "AYGC":
            self.assign_bonus_stat()

        # Set item specific details.
        match self.item_type:
            case "W":
                self.set_base_attack_speed()
                class_checker = globalitems.class_name_list.index(self.item_damage_type)
                if self.item_tier <= 4:
                    if class_checker >= 5:
                        self.item_base_type = random.choice(item_lists["_"][0])
                    else:
                        item_namelist = item_lists.get(class_checker, [])
                        self.item_base_type = random.choice(item_namelist[self.item_tier - 1]) if item_namelist else "Unknown"
                else:
                    self.item_base_type = random.choice(special_weapon_variants[class_checker])
            case "A":
                self.set_base_damage_mitigation()
                armour_base_dict = {1: "Armour", 2: "Shell", 3: "Mail", 4: "Plate", 5: "Lorica"}
                self.item_base_type = armour_base_dict[max(5, self.item_tier)]
            case "Y":
                acc_base_list = ["Bracelet", "Necklace", "Ring", "Earring"]
                self.item_base_type = random.choice(acc_base_list)
                if self.item_tier >= 5:
                    self.item_base_type = "Amulet"
            case "G":
                self.item_base_type = wing_tier_variants[(self.item_tier - 2)]
            case "C":
                crest_base_list = ["Halo", "Horns", "Crown", "Tiara"]
                self.item_base_type = random.choice(crest_base_list)
                if self.item_tier >= 5:
                    self.item_base_type = "Diadem"
            case "D":
                self.item_name = random.choice(gem_names_dict[self.item_tier])
                if self.item_tier >= 6:
                    random_resonance = random.randint(0, 22)
                    resonance = tarot.get_resonance(random_resonance)
                    if self.item_tier != 7:
                        self.item_name = f"{self.item_name} - {resonance}"
                itemrolls.add_roll(self, 6)
                points_type = random.randint(0, 5)
                points_value = self.item_tier - 1 if self.item_tier != 7 else 10
                self.item_bonus_stat = f"{points_type};{points_value}"
            case _:
                self.item_base_type = "BASE ERROR"

    def add_item_element(self, add_element):
        if add_element == 9:
            new_element = random.randint(0, 8)
        else:
            new_element = add_element
        self.item_elements[new_element] = 1

    def get_citem_thumbnail(self):
        if self.is_void_corrupted() and self.item_tier == 5:
            thumb_img = itemicons.item_icon_dict[self.item_type][0]
        else:
            thumb_img = itemicons.item_icon_dict[self.item_type][self.item_tier]
        return thumb_img

    def create_citem_embed(self):
        gear_colours = get_gear_tier_colours(self.item_tier)
        tier_colour = gear_colours[0]
        gem_min = 0
        gem_max = 0
        item_title = f'{self.item_name} '
        item_title = item_title.ljust(46, "᲼")
        self.update_damage()
        display_stars, item_rolls, base_type, aux_suffix = "", "", "", ""
        # Set the thumbnail image.
        thumb_img = self.get_citem_thumbnail()
        # Set the base stat text.
        if self.item_type == "W":
            base_type = "Base Attack Speed "
            aux_suffix = "/min"
        elif self.item_type == "A":
            base_type = "Base Damage Mitigation "
            aux_suffix = "%"
        if self.item_base_stat != 0 and self.item_base_stat != "0":
            item_rolls = f'{base_type}{self.item_base_stat}{aux_suffix}\n'
        # Set the bonus stat text.
        if self.item_type != "D":
            item_rolls += f"{self.item_bonus_stat}"
        else:
            item_rolls += f"{get_gem_stat_message(self.item_bonus_stat)}"
        rolls_msg = itemrolls.display_rolls(self)
        for x in range(self.item_num_stars):
            display_stars += globalitems.star_icon
        if self.item_num_stars < 5:
            for y in range((5 - self.item_num_stars)):
                display_stars += "<:ebstar2:1144826056222724106>"
        item_types = ""
        if self.item_type != "D":
            item_types = f'{globalitems.class_icon_dict[self.item_damage_type]}'
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
        if rolls_msg != "":
            embed_msg.add_field(name="", value=rolls_msg, inline=False)
        item_info = f'Item ID: {self.item_id}'
        embed_msg.add_field(name=item_info, value="", inline=False)
        embed_msg.set_thumbnail(url=thumb_img)
        return embed_msg

    def update_damage(self):
        # calculate item's damage per hit
        enh_multiplier = 1 + (float(self.item_enhancement) * (0.01 * self.item_num_stars))
        blessing_damage = combat.get_item_tier_damage(self.item_blessing_tier)
        material_damage = combat.get_item_tier_damage(self.item_material_tier)
        self.item_damage_min = int(float(self.base_damage_min + material_damage + blessing_damage) * enh_multiplier)
        self.item_damage_max = int(float(self.base_damage_max + material_damage + blessing_damage) * enh_multiplier)

    def give_item(self, new_owner):
        self.player_owner = new_owner
        self.update_stored_item()

    def is_void_corrupted(self):
        void_item = False
        if "Void" in self.item_material_tier or "Eschaton" == self.item_material_tier:
            void_item = True
        return void_item


class BasicItem:
    def __init__(self, item_id):
        self.item_id = ""
        self.item_name = ""
        self.item_tier = ""
        self.item_base_rate = 0
        self.item_description = ""
        self.item_emoji = ""
        self.item_image = ""
        self.item_cost = 0
        self.get_bitem_by_id(item_id)

    def __str__(self):
        return self.item_name

    def get_bitem_by_id(self, item_id):
        if item_id in itemdata.itemdata_dict:
            item = itemdata.itemdata_dict[item_id]
            self.item_id = item_id
            self.item_name = item['name']
            self.item_tier = item['tier']
            self.item_base_rate = item['rate']
            self.item_description = item['description']
            self.item_emoji = item['emoji']
            self.item_cost = item['cost']
            self.item_image = item['image']
        else:
            # Handle the case where the item_id is not found in the dictionary
            print(f"Item with ID '{item_id}' not found in itemdata_dict.")

    def create_bitem_embed(self, player_object):
        item_qty = inventory.check_stock(player_object, self.item_id)
        item_msg = f"{self.item_description}\n{player_object.player_username}'s Stock: {item_qty}"
        colour, emoji = inventory.get_gear_tier_colours(self.item_tier)
        embed_msg = discord.Embed(colour=colour, title=self.item_name, description=item_msg)
        # loot_embed.set_thumbnail(url=self.item_image)
        return embed_msg


def get_item_shop_list(item_tier):
    df = pd.read_csv("itemlist.csv")
    if item_tier != 0:
        df = df.loc[df['item_tier'] == item_tier]
        if item_tier == 2:
            df = df.loc[df['item_id'].str.contains('i|c', regex=True)]
        else:
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
            target_item.item_roll_values = list(df['item_roll_values'].values[0].split(';'))
            target_item.item_num_rolls = len(target_item.item_roll_values)
            target_item.item_base_stat = str(df['item_base_stat'].values[0])
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
    damage_type = random.choice(list(globalitems.class_icon_dict.keys()))
    return damage_type


def get_tier_damage(item_tier, item_type):
    damage_tier_list = [[250, 500], [500, 1000], [1000, 2500], [2500, 10000],
                        [1, 25000], [1, 100000], [1, 500000]]
    damage_values = damage_tier_list[item_tier - 1]
    damage_adjust = 2 if item_type == "W" else 1
    temp_damage = [random.randint(damage_values[0], damage_values[1]) * damage_adjust for _ in range(2)]
    return min(temp_damage), max(temp_damage)


# write item to inventory
def inventory_add_custom_item(item):
    # item elements
    item_elements = ""
    for x in item.item_elements:
        item_elements += str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]

    # item rolls
    item_roll_values = ""
    for x in item.item_roll_values:
        item_roll_values += str(x) + ";"
    item_roll_values = item_roll_values[:-1]

    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM CustomInventory WHERE player_id = :player_check AND item_type = :item_check")
        query = query.bindparams(player_check=item.player_owner, item_check=item.item_type)
        check_df = pd.read_sql(query, pandora_db)
        if len(check_df) >= 30:
            result_id = 0
        else:
            query = text("INSERT INTO CustomInventory "
                         "(player_id, item_type, item_name, item_damage_type, item_elements, item_enhancement,"
                         "item_tier, item_blessing_tier, item_material_tier, item_base_type,"
                         "item_num_stars, item_roll_values, item_base_stat, item_bonus_stat,"
                         "item_base_dmg_min, item_base_dmg_max, item_num_sockets, item_inlaid_gem_id)"
                         "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6, "
                         ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, "
                         ":input_13, :input_14, :input_15, :input_16, :input_17, :input_18) ")
            query = query.bindparams(input_1=item.player_owner, input_2=item.item_type, input_3=item.item_name,
                                     input_4=item.item_damage_type, input_5=item_elements,
                                     input_6=item.item_enhancement, input_7=item.item_tier,
                                     input_8=item.item_blessing_tier, input_9=item.item_material_tier,
                                     input_10=item.item_base_type, input_11=item.item_num_stars,
                                     input_12=item_roll_values,
                                     input_13=item.item_base_stat, input_14=item.item_bonus_stat,
                                     input_15=item.base_damage_min, input_16=item.base_damage_max,
                                     input_17=item.item_num_sockets, input_18=item.item_inlaid_gem_id)
            pandora_db.execute(query)
            query = text("SELECT item_id AS item_id FROM CustomInventory "
                         "WHERE player_id = :player_check AND item_name = :name_check")
            query = query.bindparams(player_check=item.player_owner, name_check=item.item_name)
            df = pd.read_sql(query, pandora_db)
            if len(df) != 0:
                id_list = list(df['item_id'])
                result_id = max(id_list)
                item.item_id = result_id
            else:
                result_id = 0
        pandora_db.close()
        engine.dispose()
        return result_id
    except exc.SQLAlchemyError as error:
        print(error)
        return 0


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


def display_cinventory(player_id, item_type) -> str:
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT item_id, item_name FROM CustomInventory "
                     "WHERE player_id = :id_check AND item_type = :type_check "
                     "ORDER BY item_tier DESC")
        query = query.bindparams(id_check=player_id, type_check=item_type)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        temp = df.style.set_properties(**{'text-align': 'left'}).hide(axis='index').hide(axis='columns')
        player_inventory = temp.to_string()
    except exc.SQLAlchemyError as error:
        print(error)
        player_inventory = ""
    return player_inventory


def display_binventory(player_id, method):
    player_inventory = ""
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()

        # Set the regular expression.
        regex_dict = {
            "Crafting": "^(Matrix|Hammer|Pearl|Origin|Lotus)",
            "Fae Cores": "^Fae",
            "Materials": "^(Fragment[0-9]|Ore|Soul|Heart|Core|FragmentM|Crystal)",
            "Unprocessed": "^(Essence|Unrefined|Fabled)",
            "Misc": "^(Potion|Trove|Crate|Stone|Token|Summon)"
        }
        regex_pattern = regex_dict[method]

        # Pull the player's inventory
        query = text(
            f"SELECT item_id, item_qty FROM BasicInventory "
            f"WHERE player_id = :id_check AND item_qty <> 0 "
            "ORDER BY item_id ASC"
        )
        query = query.bindparams(id_check=player_id)
        df = pd.read_sql(query, pandora_db)

        # Filter the data, pull associated data by the id, and build the output string.
        inventory_list = []
        df = df[df['item_id'].str.match(regex_pattern)]
        for _, row in df.iterrows():
            current_item = BasicItem(str(row['item_id']))
            inventory_list.append([current_item, str(row['item_qty'])])
        for item, quantity in inventory_list:
            player_inventory += f"{item.item_emoji} {item.item_name}: {quantity}x\n"
        # Close the connection.
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)
    return player_inventory


def get_gem_stat_message(gem_bonus_code):
    bonus_stat_details = gem_bonus_code.split(";")
    path_name = player.path_names[int(bonus_stat_details[0])]
    stat_message = f"Path of {path_name} +{bonus_stat_details[1]}"
    return stat_message


def get_gear_tier_colours(base_tier):
    tier_colors = {
        0: (discord.Colour.dark_gray(), '⚫'),
        1: (discord.Colour.green(), '🟢'),
        2: (discord.Colour.blue(), '🔵'),
        3: (discord.Colour.purple(), '🟣'),
        4: (discord.Colour.gold(), '🟡'),
        5: (0xcc0000, '🔴'),
        6: (discord.Colour.magenta(), '⚪'),
        7: (discord.Colour.pink(), '⚪')
    }

    return tier_colors[base_tier][0], tier_colors[base_tier][1]


def generate_random_tier():
    random_num = random.randint(1, 100)
    if random_num <= 1:
        temp_tier = 4
    elif random_num <= 11:
        temp_tier = 3
    elif random_num <= 51:
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
            if player_stock <= 0:
                player_stock = 0
            query = text("UPDATE BasicInventory SET item_qty = :new_qty "
                         "WHERE player_id = :id_check AND item_id = :item_check")
            query = query.bindparams(id_check=player_object.player_id, item_check=item_id, new_qty=player_stock)
            pandora_db.execute(query)
        else:
            if change <= 0:
                player_stock = 0
            else:
                player_stock = change
            query = text("INSERT INTO BasicInventory (player_id, item_id, item_qty) "
                         "VALUES(:player_id, :item_id, :new_qty)")
            query = query.bindparams(item_id=item_id, player_id=player_object.player_id, new_qty=player_stock)
            pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)


def try_refine(player_owner, item_type, selected_tier):
    if selected_tier == 4:
        new_tier = generate_random_tier()
        is_success = True if new_tier != 1 else False
    else:
        if selected_tier == 5:
            success_check = random_outcome = random.randint(1, 100)
            is_success = True if success_check <= 50 else False
        elif selected_tier == 6:
            is_success = True
        new_tier = selected_tier
    new_item = CustomItem(player_owner, item_type, new_tier)
    return new_item, is_success


def sell(user, item, embed_msg):
    reload_player = player.get_player_by_id(user.player_id)
    response_embed = embed_msg
    response = user.check_equipped(item)
    sell_value = item.item_tier * 500
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
        exclusion_list = player_object.player_equipped
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


def full_inventory_embed(lost_item, embed_colour):
    item_type = custom_item_dict[lost_item.item_type]
    embed_msg = discord.Embed(colour=embed_colour,
                              title="Inventory Full!",
                              description=f"Please make space in your {item_type} inventory.")
    return embed_msg


def max_all_items(player_id, quantity):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()

        # Clear the inventory.
        query = text("DELETE FROM BasicInventory WHERE player_id = :id_check")
        query = query.bindparams(id_check=player_id)
        pandora_db.execute(query)

        # Build the item list.
        insert_values = ','.join(
            f"('{player_id}', '{item_id}', {quantity})" for item_id in itemdata.itemdata_dict.keys()
        )
        # Add quantity to all items in the inventory.
        query_string = f"INSERT INTO BasicInventory (player_id, item_id, item_qty) VALUES {insert_values}"
        query = text(query_string)
        pandora_db.execute(query)

        # Close the connection.
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)

