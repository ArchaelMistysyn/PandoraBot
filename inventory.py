# General imports
import random
import pandas as pd
import discord
import re
import string
from discord.ui import Button, View

# Data imports
import globalitems
import sharedmethods
import itemdata

# Core imports
import player
import inventory
import mydb

# Item/crafting imports
import loot
import itemrolls
import tarot


# Inventory Dictionaries.
custom_item_dict = {"W": "Weapon", "A": "Armour", "V": "Vambraces",
                    "Y": "Amulet", "G": "Wings", "C": "Crest", "D": "Gems",
                    "D1": "Dragon Heart Gem", "D2": "Demon Heart Gem", "D3": "Paragon Heart Gem",
                    "D4": "Arbiter Heart Gem", "D5": "Incarnate Heart Gem", "T": "Tarot Card"}
item_loc_dict = {'W': 0, 'A': 1, 'V': 2, 'Y': 3, 'G': 4, 'C': 5, 'D': 6}
item_type_dict = {0: "Weapon", 1: "Armour", 2: "Vambraces", 3: "Amulet", 4: "Wings", 5: "Crest", 6: "Gems"}
reverse_item_dict = {v: k for k, v in item_type_dict.items()}
reverse_item_loc_dict = {v: k for k, v in item_loc_dict.items()}

# Name Keyword Dictionaries.
tier_keywords = {0: "Error", 1: "Lesser", 2: "Greater", 3: "Superior", 4: "Crystal",
                 5: "Void", 6: "Destiny", 7: "Stygian", 8: "Divine"}
summon_tier_keywords = {0: "Error", 1: "Illusion", 2: "Spirit", 3: "Phantasmal", 4: "Crystalline",
                        5: "Phantasmal", 6: "Fantastical", 7: "Abyssal", 8: "Divine"}
gem_tier_keywords = {0: "Error", 1: "Emerald", 2: "Sapphire", 3: "Amethyst", 4: "Diamond",
                     5: "Emptiness", 6: "Destiny", 7: "Abyss", 8: "Transcendence"}
armour_base_dict = {1: "Armour", 2: "Shell", 3: "Mail", 4: "Plate", 5: "Lorica"}
wing_base_dict = {1: "Webbed Wings", 2: "Feathered Wings", 3: "Mystical Wings", 4: "Dimensional Wings",
                  5: "Rift Wings", 6: "Wonderous Wings", 7: "Bone Wings", 8: "Ethereal Wings"}
crest_base_list = ["Halo", "Horns", "Crown", "Tiara"]


# Misc Data.
gem_point_dict = {1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 8, 7: 10, 8: 15}
sell_value_by_tier = {0: 0, 1: 500, 2: 1000, 3: 2500, 4: 5000, 5: 10000, 6: 25000, 7: 50000, 8: 100000}


class BInventoryView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.select(
        placeholder="Select Inventory Type!",
        min_values=1, max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crafting", description="Crafting Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Cores", description="Core Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Materials", description="Material Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unprocessed", description="Unprocessed Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Essences", description="Essence Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Summoning", description="Summoning Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Misc", description="Misc Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Gemstones", description="Gemstone Items"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Ultra Rare", description="Unprocessed Items")
        ]
    )
    async def inventory_callback(self, interaction: discord.Interaction, inventory_select: discord.ui.Select):
        if interaction.user.id == self.user.discord_id:
            inventory_title = f'{self.user.player_username}\'s {inventory_select.values[0]} Inventory:\n'
            inv = display_binventory(self.user.player_id, inventory_select.values[0])
            new_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=inventory_title, description=inv)
            await interaction.response.edit_message(embed=new_embed)

    @discord.ui.button(label="Gear", style=discord.ButtonStyle.blurple, emoji="✅")
    async def toggle_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.user.discord_id:
            new_view = CInventoryView(self.user)
            inventory_title = f'{self.user.player_username}\'s Equipment:\n'
            player_inventory = display_cinventory(self.user.player_id, "W")
            new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title=inventory_title, description=player_inventory)
            await interaction.response.edit_message(embed=new_embed, view=new_view)


class CInventoryView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        select_options = [
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label=custom_item_dict[key], value=reverse_item_loc_dict[value],
                description=f"{custom_item_dict[key]} storage"
            ) for key, value in list(item_loc_dict.items())
        ]
        self.select_menu = discord.ui.Select(
            placeholder="Select crafting base.", min_values=1, max_values=1, options=select_options)
        self.select_menu.callback = self.inventory_callback
        self.add_item(self.select_menu)

    async def inventory_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.discord_id:
            return
        selected_item = interaction.data['values'][0]
        inventory_title = f'{self.user.player_username}\'s Inventory:\n'
        player_inventory = display_cinventory(self.user.player_id, selected_item)
        new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title=inventory_title, description=player_inventory)
        await interaction.response.edit_message(embed=new_embed)

    @discord.ui.button(label="Items", style=discord.ButtonStyle.blurple, emoji="✅")
    async def toggle_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.user.discord_id:
                new_view = BInventoryView(self.user)
                inventory_title = f'{self.user.player_username}\'s Inventory:\n'
                player_inventory = display_binventory(self.user.player_id, "Crafting")
                new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title, description=player_inventory)
                await interaction.response.edit_message(embed=new_embed, view=new_view)
        except Exception as e:
            print(e)


class CustomItem:
    def __init__(self, player_owner, item_type, item_tier):
        # initialize input data.
        self.player_owner = player_owner
        self.item_type, self.item_tier = item_type, item_tier
        # Initialize single default values
        self.item_id, self.item_name = 0, ""
        self.item_enhancement, self.item_quality_tier = 0, 1
        self.item_elements = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # Initialize associated default values.
        self.item_num_rolls, self.item_roll_values = 0, []
        self.item_base_stat, self.item_bonus_stat = 0.0, ""
        self.item_damage_min, self.item_damage_max = 0, 0
        self.item_num_sockets, self.item_inlaid_gem_id = 0, 0

        # Generate an item type and base.
        self.item_damage_type = random.choice(list(globalitems.class_names))
        self.item_base_type = ""
        self.generate_base()
        # Generate base damage.
        self.base_damage_min, self.base_damage_max = get_tier_damage(self.item_tier, self.item_type)
        self.update_damage()
        # Set the item name.
        self.set_item_name()

    def reforge_stats(self, unlock=False):
        self.base_damage_min, self.base_damage_max = get_tier_damage(self.item_tier, self.item_type)
        if "D" in self.item_type:
            return
        if self.item_type == "W":
            self.set_base_attack_speed()
            return
        if self.item_type == "A":
            self.set_base_damage_mitigation()
        if self.item_tier >= 5 and unlock:
            available = [key for key in globalitems.rare_ability_dict.keys() if key != self.item_bonus_stat]
            self.item_bonus_stat = random.choice(available)
            return
        if self.item_tier < 5:
            current_bonus_stat = self.item_bonus_stat
            while current_bonus_stat == self.item_bonus_stat and current_bonus_stat != "":
                self.assign_bonus_stat()

    def set_base_attack_speed(self):
        selected_range = globalitems.speed_range_list[(self.item_tier - 1)]
        self.item_base_stat = round(random.uniform(selected_range[0], selected_range[1]), 2)

    def set_base_damage_mitigation(self):
        self.item_base_stat = random.randint(1 + ((self.item_tier - 1) * 5), (self.item_tier * 5))

    def assign_bonus_stat(self):
        if self.item_type in "W" or "D" in self.item_type:
            return
        if self.item_tier < 5:
            if self.item_type in ["A", "V"]:
                return
            keyword = globalitems.element_special_names[random.randint(0, 8)]
            self.item_bonus_stat = f"{keyword} Authority"
            if self.item_type == "Y":
                bane_type = random.randint(0, 5)
                keyword = "Human" if bane_type == 5 else globalitems.boss_list[bane_type]
                self.item_bonus_stat = f"{keyword} Bane"
                return
            if self.item_type == "G":
                self.item_bonus_stat = f"{keyword} Feathers"
                return
            return
        self.item_bonus_stat = random.choice(list(globalitems.rare_ability_dict.keys()))

    def get_gem_stat_message(self):
        points_value = gem_point_dict[self.item_tier]
        path_name = globalitems.path_names[int(self.item_bonus_stat)]
        stat_message = f"Path of {path_name} +{points_value}"
        return stat_message

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
        pandora_db = mydb.start_engine()
        raw_query = ("UPDATE CustomInventory SET player_id = :input_1, item_type = :input_2, item_name = :input_3, "
                     "item_damage_type = :input_4, item_elements = :input_5, item_enhancement = :input_6, "
                     "item_tier = :input_7, item_quality_tier = :input_8, item_base_type = :input_9, "
                     "item_roll_values = :input_10, item_base_stat = :input_11, item_bonus_stat = :input_12, "
                     "item_base_dmg_min = :input_13, item_base_dmg_max = :input_14, item_num_sockets = :input_15, "
                     "item_inlaid_gem_id = :input_16 "
                     "WHERE item_id = :id_check")
        params = {
            'id_check': int(self.item_id),
            'input_1': int(self.player_owner),'input_2': str(self.item_type), 'input_3': str(self.item_name),
            'input_4': str(self.item_damage_type), 'input_5': str(item_elements), 'input_6': int(self.item_enhancement),
            'input_7': int(self.item_tier), 'input_8': int(self.item_quality_tier),
            'input_9': str(self.item_base_type), 'input_10': str(item_roll_values),
            'input_11': str(self.item_base_stat), 'input_12': str(self.item_bonus_stat),
            'input_13': int(self.base_damage_min), 'input_14': int(self.base_damage_max),
            'input_15': int(self.item_num_sockets), 'input_16': int(self.item_inlaid_gem_id)
        }
        pandora_db.run_query(raw_query, params=params)
        pandora_db.close_engine()

    def set_item_name(self):
        # Handle naming exceptions.
        if "D" in self.item_type:
            self.set_gem_name()
            return
        target_list = tier_keywords
        if (self.item_damage_type == "Summoner" or self.item_damage_type == "Rider") and self.item_type == "W":
            target_list = summon_tier_keywords
        tier_keyword = target_list[self.item_tier]
        quality_name = globalitems.quality_damage_map[max(4, self.item_tier), self.item_quality_tier]
        item_name = f"+{self.item_enhancement} {tier_keyword} {self.item_base_type} [{quality_name}]"
        self.item_name = item_name

    def generate_base(self):
        if "D" in self.item_type:
            itemrolls.add_roll(self, 6)
            path = random.randint(0, 6)
            self.item_bonus_stat = f"{path}"
            return

        # Add a roll and element to non-gem items.
        itemrolls.add_roll(self, 1)
        self.add_item_element(9)

        # Handle weapon items.
        if self.item_type == "W":
            self.set_base_attack_speed()
            class_checker = globalitems.class_names.index(self.item_damage_type)
            if self.item_tier >= 5:
                target_list = globalitems.weapon_list_high[class_checker]
            else:
                target_list = globalitems.weapon_list_low[class_checker][self.item_tier - 1]
            self.item_base_type = random.choice(target_list)
            return

        # Handle non-weapon, non-gem items.
        self.assign_bonus_stat()
        match self.item_type:
            case "A":
                self.set_base_damage_mitigation()
                self.item_base_type = armour_base_dict[min(5, self.item_tier)]
            case "V":
                self.item_base_type = "Vambraces"
            case "Y":
                self.item_base_type = "Amulet" if self.item_tier >= 5 else "Necklace"
            case "G":
                self.item_base_type = wing_base_dict[self.item_tier]
            case "C":
                self.item_base_type = random.choice(crest_base_list)
                if self.item_tier >= 5:
                    self.item_base_type = "Diadem"
            case _:
                self.item_base_type = "base_type_error"

    def set_gem_name(self):
        # resonance = tarot.get_resonance(-1)
        # self.item_name = f"{self.item_name} - {resonance}"
        tier_keyword = tier_keywords[self.item_tier]
        type_keyword = gem_tier_keywords[self.item_tier]
        item_type = "Gem" if self.item_tier <= 4 else "Jewel"
        self.item_name = f"{tier_keyword} {globalitems.boss_list[int(self.item_type[1])]} Heart {item_type} [{type_keyword}]"

    def add_item_element(self, add_element):
        new_element = random.randint(0, 8) if add_element == 9 else add_element
        self.item_elements[new_element] = 1

    def create_citem_embed(self, roll_change_list=None):
        tier_colour, _ = sharedmethods.get_gear_tier_colours(self.item_tier)
        gem_min, gem_max = 0, 0
        stat_msg, base_type, aux_suffix = "", "", ""
        item_types = ""
        item_title = f'{self.item_name} '
        self.update_damage()
        # Set the base stat text.
        if self.item_type == "W":
            base_type, aux_suffix = "Base Attack Speed ", "/min"
        elif self.item_type == "A":
            base_type, aux_suffix = "Base Damage Mitigation ", "%"
        if self.item_base_stat != 0:
            stat_msg = f'{base_type}{self.item_base_stat}{aux_suffix}\n'
        # Set the bonus stat text.
        tier_specifier = {5: "Void", 6: "Wish", 7: "Abyss", 8: "Divine"}
        bonus_stat = self.item_bonus_stat
        if self.item_tier >= 5 and self.item_type != "W":
            bonus_stat = f"{tier_specifier[self.item_tier]} Application ({self.item_bonus_stat})"
        stat_msg += bonus_stat if "D" not in self.item_type else f"{self.get_gem_stat_message()}"
        rolls_msg = itemrolls.display_rolls(self, roll_change_list)
        display_stars = sharedmethods.display_stars(self.item_tier)
        if "D" not in self.item_type:
            elements = [globalitems.global_element_list[idz] for idz, z in enumerate(self.item_elements) if z == 1]
            item_types = f'{globalitems.class_icon_dict[self.item_damage_type]}' + ''.join(elements)
            # Handle socket and inlaid gem.
            gem_id = self.item_inlaid_gem_id if self.item_num_sockets == 1 else 0
            e_gem = read_custom_item(gem_id)
            if e_gem is not None:
                e_gem = read_custom_item(gem_id)
                display_stars += f" Socket: {globalitems.augment_icons[e_gem.item_tier - 1]} ({gem_id})"
                gem_min, gem_max = e_gem.item_damage_min, e_gem.item_damage_max
            elif self.item_num_sockets != 0:
                display_stars += " Socket: <:esocket:1148387477615300740>"
        damage_min, damage_max = str(gem_min + self.item_damage_min), str(gem_max + self.item_damage_max)
        damage_bonus = f'Base Damage: {int(damage_min):,} - {int(damage_max):,}'
        embed_msg = discord.Embed(colour=tier_colour, title=item_title, description=display_stars)
        embed_msg.add_field(name=item_types, value=damage_bonus, inline=False)
        embed_msg.add_field(name="Item Rolls", value=stat_msg, inline=False)
        if rolls_msg != "":
            embed_msg.add_field(name="", value=rolls_msg, inline=False)
        item_info = f'Item ID: {self.item_id}'
        embed_msg.add_field(name=item_info, value="", inline=False)
        thumbnail_url = sharedmethods.get_gear_thumbnail(self)
        if thumbnail_url is not None:
            embed_msg.set_thumbnail(url=thumbnail_url)
        else:
            frame_url = globalitems.frame_icon_list[self.item_tier - 1]
            frame_url = frame_url.replace("[EXT]", globalitems.frame_extension[0])
            embed_msg.set_thumbnail(url=frame_url)
        return embed_msg

    def update_damage(self):
        if "D" in self.item_type:
            self.item_damage_min, self.item_damage_max = self.base_damage_min, self.base_damage_max
            return
        # calculate item's damage per hit
        enh_multiplier = 1 + self.item_enhancement * (0.01 * self.item_tier)
        quality_damage = 1 + (self.item_quality_tier * 0.2)
        self.item_damage_min = int(self.base_damage_min * quality_damage * enh_multiplier)
        self.item_damage_max = int(self.base_damage_max * quality_damage * enh_multiplier)

    def give_item(self, new_owner):
        self.player_owner = new_owner
        self.update_stored_item()


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

    def create_bitem_embed(self, player_obj):
        item_qty = inventory.check_stock(player_obj, self.item_id)
        item_msg = f"{self.item_description}\n{player_obj.player_username}'s Stock: {item_qty}"
        colour, _ = inventory.sharedmethods.get_gear_tier_colours(self.item_tier)
        embed_msg = discord.Embed(colour=colour, title=self.item_name, description=item_msg)
        # loot_embed.set_thumbnail(url=self.item_image)
        return embed_msg


def get_item_shop_list(item_tier):
    item_list = []
    for item_id, item_data in itemdata.itemdata_dict.items():
        temp_tier = min(6, int(item_data['tier']))
        # Fae Core shop exception.
        if item_tier == 0:
            if 'Fae' in item_id and item_data['cost'] != 0:
                target_item = inventory.BasicItem(item_id)
                item_list.append(target_item)
        # Handle all other items.
        elif temp_tier == item_tier and item_data['cost'] != 0:
            if 'Fae' not in item_id:
                target_item = inventory.BasicItem(item_id)
                item_list.append(target_item)
    return item_list


def read_custom_item(item_id):
    pandora_db = mydb.start_engine()
    raw_query = "SELECT * FROM CustomInventory WHERE item_id = :id_check"
    df = pandora_db.run_query(raw_query, return_value=True, params={'id_check': item_id})
    pandora_db.close_engine()
    if len(df.index) == 0:
        return None
    item = CustomItem(int(df['player_id'].values[0]), str(df['item_type'].values[0]), 1)
    item.item_id, item.item_name = int(df['item_id'].values[0]), str(df['item_name'].values[0])
    temp_elements = list(df['item_elements'].values[0].split(';'))
    item.item_elements, item.item_damage_type = list(map(int, temp_elements)), df['item_damage_type'].values[0]
    item.item_tier, item.item_enhancement = int(df['item_tier'].values[0]), int(df['item_enhancement'].values[0])
    item.item_quality_tier, item.item_base_type = int(df['item_quality_tier'].values[0]), str(df['item_base_type'].values[0])
    item.item_roll_values = list(df['item_roll_values'].values[0].split(';'))
    item.item_num_rolls = len(item.item_roll_values)
    item.item_base_stat, item.item_bonus_stat = float(df['item_base_stat'].values[0]), str(df['item_bonus_stat'].values[0])
    item.base_damage_min, item.base_damage_max = int(df['item_base_dmg_min'].values[0]), int(df['item_base_dmg_max'].values[0])
    item.item_num_sockets, item.item_inlaid_gem_id = int(df['item_num_sockets'].values[0]), int(df['item_inlaid_gem_id'].values[0])
    item.update_damage()
    return item


def get_tier_damage(item_tier, item_type):
    damage_values = globalitems.damage_tier_list[item_tier - 1]
    # Gem max tier exception.
    if "D" in item_type:
        if item_tier == 8:
            damage_values = (150000, 150000)
    # Weapon has twice the value.
    damage_adjust = 2 if item_type == "W" else 1
    temp_damage = [random.randint(damage_values[0], damage_values[1]) * damage_adjust for _ in range(2)]
    return min(temp_damage), max(temp_damage)


def add_custom_item(item):
    # Item element string.
    item_elements = ""
    for x in item.item_elements:
        item_elements += str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]

    # Item roll string.
    item_roll_values = ""
    for x in item.item_roll_values:
        item_roll_values += str(x) + ";"
    item_roll_values = item_roll_values[:-1]

    # Insert the item if applicable.
    pandora_db = mydb.start_engine()
    raw_query = "SELECT * FROM CustomInventory WHERE player_id = :player_check AND item_type = :item_check"
    params = {'player_check': item.player_owner, 'item_check': item.item_type}
    check_df = pandora_db.run_query(raw_query, return_value=True, params=params)
    if len(check_df) > 30:
        return 0
    insert_query = ("INSERT INTO CustomInventory "
                    "(player_id, item_type, item_name, item_damage_type, item_elements, item_enhancement,"
                    "item_tier, item_quality_tier, item_base_type, item_roll_values, item_base_stat, item_bonus_stat, "
                    "item_base_dmg_min, item_base_dmg_max, item_num_sockets, item_inlaid_gem_id) "
                    "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6, :input_7, :input_8, "
                    ":input_9, :input_10, :input_11, :input_12, :input_13, :input_14, :input_15, :input_16)")
    params = {
        'input_1': item.player_owner, 'input_2': item.item_type, 'input_3': item.item_name,
        'input_4': item.item_damage_type, 'input_5': item_elements, 'input_6': item.item_enhancement,
        'input_7': item.item_tier, 'input_8': item.item_quality_tier, 'input_9': item.item_base_type,
        'input_10': item_roll_values, 'input_11': item.item_base_stat, 'input_12': item.item_bonus_stat,
        'input_13': item.base_damage_min, 'input_14': item.base_damage_max,
        'input_15': item.item_num_sockets, 'input_16': item.item_inlaid_gem_id
    }
    pandora_db.run_query(insert_query, params=params)
    # Fetch the item id of the inserted item
    select_query = "SELECT item_id FROM CustomInventory WHERE player_id = :player_check AND item_name = :name_check"
    df = pandora_db.run_query(select_query, return_value=True,
                              params={'player_check': item.player_owner, 'name_check': item.item_name})
    pandora_db.close_engine()
    if len(df) == 0:
        return 0
    id_list = list(df['item_id'])
    result_id = max(id_list)
    item.item_id = result_id
    return result_id


# check if item already exists. Prevent duplication
def if_custom_exists(item_id) -> bool:
    pandora_db = mydb.start_engine()
    raw_query = "SELECT * FROM CustomInventory WHERE item_id = :id_check"
    df = pandora_db.run_query(raw_query, True, params={'id_check': item_id})
    pandora_db.close_engine()
    if len(df.index) == 0:
        return False
    return True


def display_cinventory(player_id, item_type) -> str:
    pandora_db = mydb.start_engine()
    raw_query = ("SELECT item_id, item_name FROM CustomInventory "
                 "WHERE player_id = :player_id AND item_type LIKE :item_type "
                 "ORDER BY item_tier DESC")
    params = {'player_id': player_id, 'item_type': f'%{item_type}%'}
    df = pandora_db.run_query(raw_query, True, params=params)
    pandora_db.close_engine()
    temp = df.style.set_properties(**{'text-align': 'left'}).hide(axis='index').hide(axis='columns')
    player_inventory = temp.to_string()
    return player_inventory


def display_binventory(player_id, method):
    regex_dict = {
        "Crafting": "^(Matrix|Hammer|Pearl|Origin)",
        "Cores": "^(Fae|Core)",
        "Materials": "^(Scrap|Ore|Heart|Fragment|Crystal)",
        "Unprocessed": "^(Unrefined|Gem|Jewel|Void)",
        "Essences": "^(Essence)",
        "Summoning": "^(Compass|Summon)",
        "Gemstones": "^(Gemstone)",
        "Misc": "^(Potion|Trove|Crate|Stone|Token)",
        "Ultra Rare": "^(Lotus|Star)"
    }
    player_inventory = ""
    pandora_db = mydb.start_engine()
    raw_query = ("SELECT item_id, item_qty FROM BasicInventory "
                 "WHERE player_id = :id_check AND item_qty <> 0 ORDER BY item_id ASC")
    df = pandora_db.run_query(raw_query, True, params={'id_check': player_id})

    # Filter the data, pull associated data by the id, and build the output string.
    inventory_list = []
    regex_pattern = regex_dict[method]
    df = df[df['item_id'].str.match(regex_pattern)]
    for _, row in df.iterrows():
        temp_id = str(row['item_id'])
        if temp_id in itemdata.itemdata_dict:
            current_item = BasicItem(temp_id)
            inventory_list.append([current_item, str(row['item_qty'])])
    for item, quantity in inventory_list:
        player_inventory += f"{item.item_emoji} {quantity}x {item.item_name}\n"
    pandora_db.close_engine()
    return player_inventory


def generate_random_tier(min_tier=1, max_tier=8, luck_bonus=0):
    # Determine probabilities based on tier range.
    tier_range = max_tier - min_tier + 1
    base_probabilities = [2 ** (tier_range - 1 - tier) for tier in range(tier_range)]
    probabilities_actual = [prob / sum(base_probabilities) for prob in base_probabilities]
    # Construct cumulative breakpoints
    cumulative, cumulative_thresholds = 0, {}
    for idx, tier in enumerate(range(min_tier, max_tier + 1)):
        cumulative += probabilities_actual[idx]
        cumulative_thresholds[tier] = cumulative
    # Determine and return a tier.
    adjusted_random = random.random() - (luck_bonus * 0.001)
    for tier, threshold in cumulative_thresholds.items():
        if adjusted_random <= threshold:
            return tier
    return min_tier



def check_stock(player_obj, item_id):
    player_stock = 0
    pandora_db = mydb.start_engine()
    raw_query = ("SELECT item_qty FROM BasicInventory "
                 "WHERE player_id = :id_check AND item_id = :item_check")
    df = pandora_db.run_query(raw_query, True, params={'id_check': player_obj.player_id, 'item_check': item_id})
    pandora_db.close_engine()
    if len(df.index) != 0:
        player_stock = int(df['item_qty'].values[0])
    return player_stock


def update_stock(player_obj, item_id, change, batch=None):
    pandora_db = mydb.start_engine()
    if batch is not None:
        raw_query = ("INSERT INTO BasicInventory (player_id, item_id, item_qty) "
                     "VALUES (:player_id, :item_id, :item_qty) "
                     "ON DUPLICATE KEY UPDATE item_qty = item_qty + VALUES(item_qty);")
        batch_params = batch.to_dict('records')
        pandora_db.run_query(raw_query, batch=True, params=batch_params)
        pandora_db.close_engine()
        return
    if player_obj is None or item_id is None or change is None:
        return
    raw_query = ("SELECT item_qty FROM BasicInventory "
                 "WHERE player_id = :id_check AND item_id = :item_check")
    df = pandora_db.run_query(raw_query, True, params={'id_check': player_obj.player_id, 'item_check': item_id})
    raw_query = ("INSERT INTO BasicInventory (player_id, item_id, item_qty) "
                 "VALUES(:player_check, :item_check, :new_qty)")
    player_stock = change
    if len(df.index) != 0:
        player_stock = int(df['item_qty'].values[0]) + change
        raw_query = ("UPDATE BasicInventory SET item_qty = :new_qty "
                     "WHERE player_id = :player_check AND item_id = :item_check")
    player_stock = max(player_stock, 0)
    params = {'new_qty': player_stock, 'player_check': player_obj.player_id, 'item_check': item_id}
    pandora_db.run_query(raw_query, params=params)
    pandora_db.close_engine()


def try_refine(player_owner, item_type, target_tier):
    # Handle flat-tier refinement (Tier 5+ non-gems)
    if "D" not in item_type and target_tier >= 5:
        is_success = False
        if item_type == "W" or random.randint(1, 100) <= 80:
            is_success = True
        new_item = inventory.CustomItem(player_owner, item_type, target_tier)
        return new_item, is_success
    is_success = True if random.randint(1, 100) <= 75 else False
    # All other refinement.
    new_tier = generate_random_tier() if target_tier == 4 else generate_random_tier(min_tier=target_tier, max_tier=8)
    new_tier = 2 if new_tier == 1 else new_tier
    new_item = inventory.CustomItem(player_owner, item_type, new_tier)
    return new_item, is_success


def sell(user, item, embed_msg):
    user.reload_player()
    response_embed = embed_msg
    response = user.check_equipped(item)
    sell_value = inventory.sell_value_by_tier[item.item_tier]
    if response != "":
        response_embed.add_field(name="Item Not Sold!", value=response, inline=False)
        return response_embed
    # Sell the item.
    sell_msg = user.adjust_coins(sell_value)
    pandora_db = mydb.start_engine()
    raw_query = "DELETE FROM CustomInventory WHERE item_id = :item_check"
    pandora_db.run_query(raw_query, params={'item_check': item.item_id})
    pandora_db.close_engine()
    currency_msg = f'You now have {user.player_coins:,} lotus coins!'
    response_embed.add_field(name=f"Item Sold! {globalitems.coin_icon} {sell_msg} lotus coins acquired!",
                             value=currency_msg, inline=False)
    return response_embed


def delete_item(user_object, item):
    pandora_db = mydb.start_engine()
    if "D" in item.item_type:
        raw_query = "UPDATE CustomInventory SET item_inlaid_gem_id = 0 WHERE item_inlaid_gem_id = :item_check"
        pandora_db.run_query(raw_query, params={'item_check': item.item_id})
    else:
        user_object.unequip_item(item)
    raw_query = "DELETE FROM CustomInventory WHERE item_id = :item_check"
    pandora_db.run_query(raw_query, params={'item_check': item.item_id})
    pandora_db.close_engine()


def purge(player_obj, item_type, tier):
    pandora_db = mydb.start_engine()
    player_obj.get_equipped()
    exclusion_list = player_obj.player_equipped
    inlaid_gem_list = []
    for x in exclusion_list:
        if x != 0:
            e_item = inventory.read_custom_item(x)
            if e_item.item_inlaid_gem_id != 0:
                inlaid_gem_list.append(e_item.item_inlaid_gem_id)
    exclusion_list += inlaid_gem_list
    type_check = item_loc_dict[reverse_item_dict[item_type]]
    params = {'id_check': player_obj.player_id, 'tier_check': tier, 'type_check': type_check}
    exclusion_ids = ', '.join([str(item_id) for item_id in exclusion_list])
    raw_query = (f"SELECT item_tier FROM CustomInventory "
                 f"WHERE player_id = :id_check AND item_tier <= :tier_check "
                 f"AND item_id NOT IN ({exclusion_ids}) AND item_type = :type_check")
    df = pandora_db.run_query(raw_query, return_value=True, params=params)
    delete_query = (f"DELETE FROM CustomInventory "
                    f"WHERE player_id = :id_check AND item_tier <= :tier_check "
                    f"AND item_id NOT IN ({exclusion_ids}) AND item_type = :type_check")
    pandora_db.run_query(delete_query, params=params)
    pandora_db.close_engine()
    result = len(df)
    coin_total = 0
    for item_tier in df['item_tier']:
        coin_total += inventory.sell_value_by_tier[int(item_tier)]
    coin_msg = player_obj.adjust_coins(coin_total)
    return f"{player_obj.player_username} sold {result} items and received {coin_msg} lotus coins"


def full_inventory_embed(lost_item, embed_colour):
    item_type = custom_item_dict[lost_item.item_type]
    return discord.Embed(colour=embed_colour, title="Inventory Full!",
                         description=f"Please make space in your {item_type} inventory.")


async def generate_item(ctx, target_player, tier, elements, item_type, base_type, class_name, enhancement,
                        quality, base_stat, bonus_stat, base_dmg, num_sockets, roll_list):
    valid_damage_range = (globalitems.damage_tier_list[tier - 1][0], globalitems.damage_tier_list[tier - 1][1] + 1)
    pattern = r"^\d(;[0-9]+){8}$"

    # Create the new item.
    if tier not in range(9):
        await ctx.send('Tier input not valid.')
        return None
    if item_type not in inventory.custom_item_dict.keys() and item_type != "T":
        await ctx.send('Item type input not valid.')
        return None
    new_item = inventory.CustomItem(target_player, item_type, tier)
    new_item.player_owner = target_player.player_id

    if "D" not in item_type:
        # Handle non-gem inputs.
        if not bool(re.match(pattern, elements)):
            await ctx.send('Element input not valid.')
            return None
        if num_sockets not in range(2):
            await ctx.send('Socket input not valid.')
            return None
        if enhancement not in range(1, globalitems.max_enhancement[tier - 1] + 1):
            await ctx.send('Enhancement input not valid for given tier.')
            return None
        if quality not in range(1, 6):
            await ctx.send('Quality input not valid.')
            return None
        if class_name not in globalitems.class_names:
            await ctx.send('Class name input not valid.')
            return None
        if base_dmg[0] not in range(*valid_damage_range) or base_dmg[1] not in range(*valid_damage_range):
            await ctx.send('Base damage input not valid.')
            return
        new_item.item_elements = list(map(int, elements.split(';')))
        new_item.item_num_sockets, new_item.item_enhancement = num_sockets, enhancement
        new_item.item_quality_tier, new_item.item_damage_type = quality, class_name
        # Handle type specific inputs.
        speed_range = globalitems.speed_range_list[tier - 1]
        if ((item_type == "A" and base_stat not in range((1 + (tier - 1) * 5), tier * 5))
                or (item_type == "W" and not (speed_range[0] <= base_stat <= speed_range[1]))):
            await ctx.send('Base stat input not valid.')
            return None
        if item_type != "W":
            words = bonus_stat.split()
            if len(words) != 2:
                await ctx.send('Bonus stat input not valid.')
                return None
            if tier >= 5 and bonus_stat not in globalitems.rare_ability_dict.keys():
                await ctx.send('Bonus stat input not valid.')
                return None
            elif tier <= 4:
                if ((words[1] == "Bane" and words[0] not in globalitems.boss_list and words[0] != "Human") or
                        (words[0] not in globalitems.element_special_names and words[1] not in ["Feathers", "Authority"])):
                    await ctx.send('Bonus stat input not valid.')
                    return None
        else:
            # Set the item weapon item base.
            class_checker = globalitems.class_names.index(new_item.item_damage_type)
            if tier >= 5:
                target_list = globalitems.weapon_list_high[class_checker]
            else:
                target_list = globalitems.weapon_list_low[class_checker][tier - 1]
            new_item.item_base_type = random.choice(target_list)
            if base_type != "" and base_type in target_list:
                new_item.item_base_type = base_type
        # Assign base/bonus stats.
        new_item.item_bonus_stat = bonus_stat if item_type != "W" else ""
        new_item.item_base_stat = base_stat if item_type in ["W", "A"] else new_item.item_base_stat
    else:
        # Handle gem/jewel specific inputs.
        if bonus_stat not in globalitems.path_names:
            await ctx.send('Bonus Stat input not valid for gem/jewel.')
            return None
        if tier == 8:
            base_dmg = [150000, 150000]
        elif base_dmg[0] not in range(*valid_damage_range) or base_dmg[1] not in range(*valid_damage_range):
            await ctx.send('Base damage input not valid.')
            return
        new_item.item_bonus_stat = globalitems.path_names.index(bonus_stat)

    # Apply the item rolls.
    count, new_roll_values = 0, []
    for roll in roll_list:
        if roll is None:
            break
        if (not roll[0].isdigit() or int(roll[0]) not in range(1, tier + 1)
                or roll[1] != "-" or roll[2:] not in itemrolls.valid_rolls):
            await ctx.send(f'{roll} is not a roll valid input.')
            return
        new_roll_values.append(roll)
        count += 1
    new_item.item_roll_values = new_roll_values
    if count != 6 and ("D" in item_type or tier >= 6):
        await ctx.send(f'Please input 6 item rolls.')
        return

    new_item.base_damage_min, new_item.base_damage_max = min(base_dmg), max(base_dmg)
    new_item.set_item_name()
    new_item.item_id = add_custom_item(new_item)
    return new_item
