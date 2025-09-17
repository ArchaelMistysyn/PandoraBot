# General imports
import random
import pandas as pd
import discord
import re
import string
from discord.ui import Button, View
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
# import time

# Data imports
import globalitems as gli
import sharedmethods as sm
import itemdata

# Core imports
import player
import inventory
from pandoradb import run_query as rqy

# Item/crafting imports
import loot
import itemrolls
import ring
from ringdata import ring_element_dict as red
import sovereigngear as sg
import tarot

# Inventory Dictionaries.
custom_item_dict = {"W": "Weapon", "A": "Armour", "V": "Greaves", "Y": "Amulet",
                    "R": "Ring", "G": "Wings", "C": "Crest", "D": "Gems",
                    "D1": "Dragon Heart Gem", "D2": "Demon Heart Gem", "D3": "Paragon Heart Gem",
                    "D4": "Arbiter Heart Gem", "D5": "Incarnate Heart Gem", "T": "Tarot Card"}
item_loc_dict = {'W': 0, 'A': 1, 'V': 2, 'Y': 3, 'R': 4, 'G': 5, 'C': 6, 'D': 7}
item_type_dict = {0: "Weapon", 1: "Armour", 2: "Greaves", 3: "Amulet", 4: "Ring", 5: "Wings", 6: "Crest", 7: "Gems"}
reverse_item_dict = {v: k for k, v in item_type_dict.items()}
reverse_item_loc_dict = {v: k for k, v in item_loc_dict.items()}

# Name Keyword Dictionaries.
tier_keywords = {0: "Error", 1: "Lesser", 2: "Greater", 3: "Superior", 4: "Crystal",
                 5: "Void", 6: "Destiny", 7: "Stygian", 8: "Divine", 9: "Sacred"}
summon_tier_keywords = {0: "Error", 1: "Illusion", 2: "Spirit", 3: "Phantasmal", 4: "Crystalline",
                        5: "Phantasmal", 6: "Fantastical", 7: "Abyssal", 8: "Divine", 9: "Sacred"}
gem_tier_keywords = {0: "Error", 1: "Emerald", 2: "Sapphire", 3: "Amethyst", 4: "Diamond",
                     5: "Emptiness", 6: "Destiny", 7: "Abyss", 8: "Transcendence", 9: "MAX"}
armour_base_dict = {1: "Armour", 2: "Shell", 3: "Mail", 4: "Plate", 5: "Lorica"}
wing_base_dict = {1: "Webbed Wings", 2: "Feathered Wings", 3: "Mystical Wings", 4: "Dimensional Wings",
                  5: "Rift Wings", 6: "Wonderous Wings", 7: "Bone Wings", 8: "Ethereal Wings", 9: "Sanctified Wings"}
crest_base_list = ["Halo", "Horns", "Crown", "Tiara"]

# Misc Data.
gem_point_dict = {1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 8, 7: 10, 8: 15, 9: 20}
sell_value_by_tier = {0: 0, 1: 500, 2: 1000, 3: 2500, 4: 5000, 5: 10000, 6: 25000, 7: 50000, 8: 100000, 9: 500000}


class BInventoryView(discord.ui.View):
    def __init__(self, player_obj, current_menu, view_type, include_id=False):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.current_menu, self.view_type, self.include_id = current_menu, view_type, include_id
        self.show_id.label = "Hide ID" if self.include_id else "Show ID"
        self.toggle_view.label = "Basic View" if view_type == 0 else "Embed View"

    @discord.ui.select(
        placeholder="Select Inventory Type!", min_values=1, max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:Cry5:1274785116572614856>", label="Crafting", description="Crafting Items"),
            discord.SelectOption(
                emoji="<:Fae8:1274786370497417330>", label="Fae Cores", description="Fae Core Items"),
            discord.SelectOption(
                emoji="<:Scrap:1274787448681005158>", label="Materials", description="Material Items"),
            discord.SelectOption(
                emoji="<:Gem_5:1275569736205340773>", label="Unprocessed", description="Unprocessed Items"),
            discord.SelectOption(
                emoji="<:Essence5:1297651547186139206>", label="Essences", description="Essence Items"),
            discord.SelectOption(
                emoji="<:Cmps:1388913589535899758>", label="Summoning", description="Summoning Items"),
            discord.SelectOption(
                emoji="<:Chest:1398709914381324318>", label="Misc", description="Misc Items"),
            discord.SelectOption(
                emoji="<:Alt:1275588731272953916>", label="Gemstone", description="Gemstone Items"),
            discord.SelectOption(
                emoji="<:F5:1398709820466659471>", label="Fish", description="Fish Items"),
            discord.SelectOption(
                emoji="<:Lotus11:1274786525560701132>", label="Ultra Rare", description="Unprocessed Items")])
    async def inventory_callback(self, interaction: discord.Interaction, inventory_select: discord.ui.Select):
        if interaction.user.id != self.player_obj.discord_id:
            return
        self.current_menu = inventory_select.values[0]
        self.view_type = int(await self.player_obj.check_misc_data("toggle_inv"))
        content, embed = await display_binventory(self.player_obj, self.current_menu, self.view_type, self.include_id)
        new_view = BInventoryView(self.player_obj, self.current_menu, self.view_type, self.include_id)
        await interaction.response.edit_message(content=content, embed=embed, view=new_view)

    @discord.ui.button(label="Gear", style=discord.ButtonStyle.blurple, emoji=gli.gear_icons_dict['W'])
    async def toggle_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title = f'{self.player_obj.player_username}\'s Equipment:\n'
        player_inv = await display_cinventory(self.player_obj, "W")
        new_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=player_inv)
        await interaction.response.edit_message(content=None, embed=new_embed, view=CInventoryView(self.player_obj, self.include_id))

    @discord.ui.button(label="Show ID", style=discord.ButtonStyle.blurple)
    async def show_id(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        self.view_type = int(await self.player_obj.check_misc_data("toggle_inv"))
        self.include_id = True if not self.include_id else False
        content, embed = await display_binventory(self.player_obj, self.current_menu, self.view_type, self.include_id)
        new_view = BInventoryView(self.player_obj, self.current_menu, self.view_type, self.include_id)
        await interaction.response.edit_message(content=content, embed=embed, view=new_view)

    @discord.ui.button(label="Toggle View", style=discord.ButtonStyle.blurple)
    async def toggle_view(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        self.view_type = int(await self.player_obj.check_misc_data("toggle_inv"))
        self.view_type = 1 if self.view_type == 0 else 0
        await self.player_obj.update_misc_data("toggle_inv", self.view_type, overwrite_value=True)
        content, embed = await display_binventory(self.player_obj, self.current_menu, self.view_type, self.include_id)
        new_view = BInventoryView(self.player_obj, self.current_menu, self.view_type, self.include_id)
        await interaction.response.edit_message(content=content, embed=embed, view=new_view)


class CInventoryView(discord.ui.View):
    def __init__(self, player_obj, include_id=False):
        super().__init__(timeout=None)
        self.player_obj, self.include_id = player_obj, include_id
        select_options = [discord.SelectOption(
            emoji=gli.gear_icons_dict[key], label=custom_item_dict[key], value=reverse_item_loc_dict[value],
            description=f"{custom_item_dict[key]} storage") for key, value in list(item_loc_dict.items())]
        self.select_menu = discord.ui.Select(
            placeholder="Select item base.", min_values=1, max_values=1, options=select_options)
        self.select_menu.callback = self.inventory_callback
        self.add_item(self.select_menu)

    async def inventory_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        selected_item = interaction.data['values'][0]
        inventory_title = f'{self.player_obj.player_username}\'s Inventory:\n'
        player_inv = await display_cinventory(self.player_obj, selected_item)
        new_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=inventory_title, description=player_inv)
        await interaction.response.edit_message(embed=new_embed)

    @discord.ui.button(label="Items", style=discord.ButtonStyle.blurple)
    async def toggle_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        view_type = int(await self.player_obj.check_misc_data("toggle_inv"))
        new_view = BInventoryView(self.player_obj, "Crafting", view_type)
        content, embed = await display_binventory(self.player_obj, "Crafting", view_type, self.include_id)
        await interaction.response.edit_message(content=content, embed=embed, view=new_view)


class CustomItem:
    def __init__(self, player_owner, item_type, item_tier, base_type="", is_sacred=False, random_enhance=False):
        # initialize input data.
        self.player_owner = player_owner
        self.item_type, self.item_tier = item_type, item_tier
        self.is_sacred = is_sacred
        # Initialize single default values
        self.item_id, self.item_name = 0, ""
        self.item_enhancement, self.item_quality_tier = self.set_enhancement(random_enhance), 1
        self.item_elements = [0] * 9
        # Initialize associated default values.
        self.item_num_rolls, self.roll_values = 0, []
        self.item_base_stat, self.item_bonus_stat = 0.0, ""
        self.base_damage_min, self.base_damage_max, self.item_damage_min, self.item_damage_max = 0, 0, 0, 0
        self.item_num_sockets, self.item_inlaid_gem_id = (1 if self.is_sacred else 0), 0
        # Generate an item type and base.
        self.item_damage_type, self.item_base_type = random.choice(list(gli.class_names)), base_type
        self.generate_base()
        self.get_tier_damage()
        # Exceptions
        if self.item_type == "R":
            self.item_quality_tier = 0
            ring_element_data = red[self.item_base_type]
            if ring_element_data[0] == "all":
                self.item_elements = [1] * 9
            else:
                for element_index in ring_element_data:
                    self.item_elements[element_index] = 1
        elif self.item_base_type != "" and self.item_base_type in gli.sovereign_item_list:
            self.item_quality_tier = 0
            sg.build_sovereign_item(self)
        # Finalize item
        self.update_damage()
        self.set_item_name()

    async def reload_item(self):
        _ = await read_custom_item(self.item_id, reloading=self)

    def reforge_class(self, specific_class=""):
        if specific_class:
            self.item_damage_type = specific_class
        else:
            available_classes = [cls for cls in gli.class_names if cls != self.item_damage_type]
            self.item_damage_type = random.choice(available_classes)

    def set_enhancement(self, random_enhance):
        if not random_enhance or self.item_tier <= 0:
            return 0
        else:
            calc_tier = generate_random_tier(1, min(self.item_tier, 8))
            rare_roll = random.randint(1, 1000)
            if rare_roll <= 1:
                return gli.max_enhancement[self.item_tier - 1]
            rare_bonus = 1 if rare_roll >= 50 else 2 if rare_roll > 10 else 4
            bonus_value = ((calc_tier - 1) * 5 * rare_bonus) + random.randint(5 * rare_bonus, 15 * rare_bonus)
            return min(bonus_value, gli.max_enhancement[self.item_tier - 1])

    def get_gear_score(self):
        quality_score, base_damage_score, base_max, rolls_score, enhancement_score = 1500, 0, 150000, 3000, 1500
        tier_score = 0 if self.item_tier <= 8 else 999
        if "D" not in self.item_type and self.item_type != "R":
            enhancement_score = round((self.item_enhancement / 200) * 1500)
            quality_score = round((self.item_quality_tier / 5) * 1500)
            base_max = 250000
        base_stat_max = 4.00 if self.item_type == "W" else 30.00 if self.item_type == "A" else 0
        base_stat_score = round((self.item_base_stat / base_stat_max) * 1500) if base_stat_max > 0 else 1500
        if self.item_base_type in gli.sovereign_item_list and self.item_type != "R":
            base_damage_score = 1500
        elif self.base_damage_min > 0 and self.base_damage_max > 0:
            base_damage_score = round((self.base_damage_min / base_max) * 750 + (self.base_damage_max / base_max) * 750)
        # 5. Rolls Completion
        if self.item_type == "R":
            rolls_score = round(min(self.item_tier, 8) / 8 * 3000)
        elif self.item_base_type not in gli.sovereign_item_list:
            roll_scores = []
            for roll in self.roll_values:
                if roll:
                    roll_scores.append(round((min(int(roll[0]), 8) / 8) * 500))
            rolls_score = sum(roll_scores) if roll_scores else 0
        return tier_score + enhancement_score + quality_score + base_stat_score + base_damage_score + rolls_score

    def reforge_stats(self, unlock=False):
        self.get_tier_damage()
        if "D" in self.item_type:
            return
        if self.item_type == "W":
            self.set_base_attack_speed()
            return
        if self.item_type == "A":
            self.set_base_damage_mitigation()
        if self.item_tier >= 5 and unlock:
            available = [key for key in gli.rare_ability_dict.keys() if key != self.item_bonus_stat]
            self.item_bonus_stat = random.choice(available)
            return
        if self.item_tier < 5:
            current_bonus_stat = self.item_bonus_stat
            while current_bonus_stat == self.item_bonus_stat and current_bonus_stat != "":
                self.assign_bonus_stat()

    def set_base_attack_speed(self):
        selected_range = gli.speed_range_list[(self.item_tier - 1)]
        self.item_base_stat = round(random.uniform(selected_range[0], selected_range[1]), 2)

    def set_base_damage_mitigation(self):
        self.item_base_stat = 30.00
        if self.item_tier < 9:
            self.item_base_stat = round(random.uniform(10, 14), 2) + (self.item_tier - 1) * 2

    def assign_bonus_stat(self):
        if self.item_type in ["W"] or "D" in self.item_type:
            return
        if self.item_tier < 5:
            if self.item_type in ["A", "V"]:
                return
            keyword = gli.element_special_names[random.randint(0, 8)]
            self.item_bonus_stat = f"{keyword} Authority"
            if self.item_type == ["Y", "R"]:
                bane_type = random.randint(0, 5)
                keyword = "Human" if bane_type == 5 else gli.boss_list[bane_type]
                self.item_bonus_stat = f"{keyword} Bane"
                return
            if self.item_type == "G":
                self.item_bonus_stat = f"{keyword} Feathers"
                return
            return
        self.item_bonus_stat = random.choice(list(gli.rare_ability_dict.keys()))

    def get_gem_stat_message(self):
        points_value = gem_point_dict[self.item_tier]
        path_name = gli.path_names[int(self.item_bonus_stat)]
        stat_message = f"Path of {path_name} +{points_value}"
        return stat_message

    async def update_stored_item(self):
        item_elements = ""
        for x in self.item_elements:
            item_elements += str(x) + ";"
        if item_elements != "":
            item_elements = item_elements[:-1]
        roll_values = ""
        for x in self.roll_values:
            roll_values += str(x) + ";"
        if roll_values != "":
            roll_values = roll_values[:-1]

        raw_query = ("UPDATE CustomInventory SET player_id = :input_1, item_type = :input_2, item_name = :input_3, "
                     "item_damage_type = :input_4, item_elements = :input_5, item_enhancement = :input_6, "
                     "item_tier = :input_7, item_quality_tier = :input_8, item_base_type = :input_9, "
                     "item_roll_values = :input_10, item_base_stat = :input_11, item_bonus_stat = :input_12, "
                     "item_base_dmg_min = :input_13, item_base_dmg_max = :input_14, item_num_sockets = :input_15, "
                     "item_inlaid_gem_id = :input_16 "
                     "WHERE item_id = :id_check")
        params = {
            'id_check': int(self.item_id),
            'input_1': int(self.player_owner), 'input_2': str(self.item_type), 'input_3': str(self.item_name),
            'input_4': str(self.item_damage_type), 'input_5': str(item_elements), 'input_6': int(self.item_enhancement),
            'input_7': int(self.item_tier), 'input_8': int(self.item_quality_tier),
            'input_9': str(self.item_base_type), 'input_10': str(roll_values),
            'input_11': str(self.item_base_stat), 'input_12': str(self.item_bonus_stat),
            'input_13': int(self.base_damage_min), 'input_14': int(self.base_damage_max),
            'input_15': int(self.item_num_sockets), 'input_16': int(self.item_inlaid_gem_id)}
        await rqy(raw_query, params=params)

    def set_item_name(self):
        # Handle naming exceptions.
        if self.item_base_type in gli.sovereign_item_list:
            self.item_name = self.item_base_type
            if self.is_sacred:
                self.item_name += f" [Sacred]"
            return
        elif self.item_type == "R":
            self.item_name = self.item_base_type
            return
        elif "D" in self.item_type:
            self.set_gem_name()
            return
        target_list = tier_keywords
        if (self.item_damage_type == "Summoner" or self.item_damage_type == "Rider") and self.item_type == "W":
            target_list = summon_tier_keywords
        tier_keyword = target_list[self.item_tier]
        quality_name = gli.quality_damage_map[max(4, self.item_tier), self.item_quality_tier]
        self.item_name = f"+{self.item_enhancement} {tier_keyword} {self.item_base_type} [{quality_name}]"

    def generate_base(self):
        if self.item_type not in ["W"] and "D" not in self.item_type:
            self.assign_bonus_stat()
        if self.item_type == "R":
            # Default unique values for rings.
            self.roll_values = [None] * 6
            return
        if self.item_base_type != "":
            return
        if "D" in self.item_type:
            itemrolls.add_roll(self, 6)
            path = random.randint(0, 6)
            self.item_bonus_stat = f"{path}"
            return
        if self.item_base_type in gli.sovereign_item_list:
            return
        # Add a roll and element to non-gem items.
        itemrolls.add_roll(self, 1)
        self.add_item_element(9)
        # Handle non-gem items.
        match self.item_type:
            case "A":
                self.set_base_damage_mitigation()
                self.item_base_type = armour_base_dict[min(5, self.item_tier)]
            case "V":
                self.item_base_type = "Greaves"
            case "Y":
                self.item_base_type = "Amulet" if self.item_tier >= 5 else "Necklace"
            case "G":
                self.item_base_type = wing_base_dict[self.item_tier]
            case "C":
                self.item_base_type = "Diadem" if self.item_tier >= 5 else random.choice(crest_base_list)
            case "W":
                self.set_base_attack_speed()
                item_data = gli.weapon_type_dict[self.item_damage_type]
                combined_list = item_data[1] + item_data[2] if self.item_tier >= 5 else item_data[0] + item_data[1]
                self.item_base_type = random.choice(combined_list)
            case _:
                self.item_base_type = "base_type_error"

    def set_gem_name(self):
        tier_keyword = tier_keywords[self.item_tier]
        type_keyword = gem_tier_keywords[self.item_tier]
        item_type = "Gem" if self.item_tier <= 4 else "Jewel"
        self.item_name = f"{tier_keyword} {gli.boss_list[int(self.item_type[1])]} Heart {item_type} [{type_keyword}]"

    def add_item_element(self, add_element):
        new_element = random.randint(0, 8) if add_element == 9 else add_element
        self.item_elements[new_element] = 1

    def get_tier_damage(self):
        damage_values = gli.damage_tier_list[self.item_tier - 1]
        if self.item_base_type == "Crown of Skulls":
            return
        # Gem max tier exception.
        if "D" in self.item_type and self.item_tier == 8:
            damage_values = (150000, 150000)
        # Weapon has twice the value.
        damage_adjust = 2 if self.item_type == "W" else 1
        temp_damage = [random.randint(damage_values[0], damage_values[1]) * damage_adjust for _ in range(2)]
        self.base_damage_min, self.base_damage_max = min(temp_damage), max(temp_damage)

    async def create_citem_embed(self, roll_change_list=None):
        tier_colour, _ = sm.get_gear_tier_colours(self.item_tier)
        gem_min, gem_max = 0, 0
        stat_msg, base_type, aux_suffix = "", "", ""
        item_types, item_title = "", f'{self.item_name} '
        self.update_damage()
        # Set the base stat text.
        if self.item_type == "W":
            base_type, aux_suffix = "Base Attack Speed ", "/min"
        elif self.item_type == "A":
            base_type, aux_suffix = "Base Damage Mitigation ", "%"
        if self.item_base_stat != 0.0:
            if isinstance(self.item_base_stat, int):
                display_base_stat = f"{int(self.item_base_stat)}"
            else:
                display_base_stat = f"{self.item_base_stat:.2f}".rstrip('0').rstrip('.')
            stat_msg = f'{base_type}{display_base_stat}{aux_suffix}\n'
        # Set the bonus stat text.
        tier_specifier = {5: "Void", 6: "Wish", 7: "Abyss", 8: "Divine", 9: "Sacred"}
        bonus_stat = self.item_bonus_stat
        if self.item_tier >= 5 and self.item_type != "W" and "D" not in self.item_type:
            bonus_stat = f"{tier_specifier[self.item_tier]} Application ({self.item_bonus_stat})"
        stat_msg += bonus_stat if "D" not in self.item_type else f"{self.get_gem_stat_message()}"
        if self.item_type == "R":
            rolls_msg = await ring.display_ring_values(self)
        elif self.item_base_type not in gli.sovereign_item_list:
            rolls_msg = itemrolls.display_rolls(self, roll_change_list)
        else:
            rolls_msg = sg.display_sovereign_rolls(self)
        display_stars = sm.display_stars(self.item_tier)
        if "D" not in self.item_type:
            elements = [gli.ele_icon[idz] for idz, z in enumerate(self.item_elements) if z == 1]
            item_types = f'{gli.class_icon_dict[self.item_damage_type]}' + ''.join(elements)
            # Handle socket and inlaid gem.
            gem_id = self.item_inlaid_gem_id if self.item_num_sockets == 1 else 0
            e_gem = await read_custom_item(gem_id)
            if e_gem is not None:
                display_stars += f" Socket: {gli.augment_icons[e_gem.item_tier - 1]} ({gem_id})"
                # gem_min, gem_max = e_gem.item_damage_min, e_gem.item_damage_max
            elif self.item_num_sockets != 0:
                display_stars += " Socket: <:esocket:1148387477615300740>"
        damage_min, damage_max = str(self.item_damage_min), str(self.item_damage_max)
        damage_bonus = f'Base Damage: {int(damage_min):,} - {int(damage_max):,}'
        embed_msg = discord.Embed(colour=tier_colour, title=item_title, description=display_stars)
        if self.item_name == "Bathyal, Enigmatic Chasm Bauble":
            damage_bonus, stat_msg = sm.hide_text(damage_bonus), sm.hide_text(stat_msg)
            rolls_msg = sm.hide_text(rolls_msg) if rolls_msg != "" else rolls_msg
        embed_msg.add_field(name=item_types, value=damage_bonus, inline=False)
        embed_msg.add_field(name="Item Rolls", value=stat_msg, inline=False)
        if rolls_msg != "":
            embed_msg.add_field(name="", value=rolls_msg, inline=False)
        if self.item_id != 0:
            embed_msg.add_field(name=f'Item ID: {self.item_id}', value="", inline=False)
        gear_score = self.get_gear_score()
        star_symbol = "☆" if gear_score < 9999 else "★"
        embed_msg.add_field(name=f'Gear Score: {star_symbol}{gear_score}', value="", inline=False)
        thumbnail_url = sm.get_gear_thumbnail(self)
        if thumbnail_url is not None:
            pass
            # timestamp = int(time.time())
            # embed_msg.set_thumbnail(url=f"{thumbnail_url}?ts={timestamp}")
            embed_msg.set_thumbnail(url=thumbnail_url)
        else:
            frame_url = gli.frame_icon_list[self.item_tier - 1]
            embed_msg.set_thumbnail(url=frame_url.replace("[EXT]", gli.frame_extension[0]))
        return embed_msg

    def update_damage(self):
        flat_bonus, mult_bonus = 0, 1
        if "D" in self.item_type:
            self.item_damage_min, self.item_damage_max = self.base_damage_min, self.base_damage_max
            return
        # Handle unique base damage exceptions
        if self.item_base_type == "Crown of Skulls" and self.roll_values[0] is not None:
            flat_bonus, mult_bonus = (int(self.roll_values[0]) * 100000), (1 + (int(self.roll_values[1]) * 0.001))
        # calculate item's damage per hit
        enh_multiplier = 1 + self.item_enhancement * (0.01 * self.item_tier)
        quality_damage = 1 + (self.item_quality_tier * 0.2)
        self.item_damage_min = int((self.base_damage_min + flat_bonus) * quality_damage * enh_multiplier * mult_bonus)
        self.item_damage_max = int((self.base_damage_max + flat_bonus) * quality_damage * enh_multiplier * mult_bonus)

    async def give_item(self, new_owner):
        self.player_owner = new_owner
        self.item_inlaid_gem_id = 0
        await self.update_stored_item()


class BasicItem:
    def __init__(self, item_id):
        self.item_id, self.item_name, self.item_tier = "", "", 1
        self.item_category, self.item_description, = "", ""
        self.item_emoji, self.item_image = "", ""
        self.item_cost, self.item_base_rate = 0, 0
        self.get_bitem_by_id(item_id)

    def __str__(self):
        return self.item_name

    def get_bitem_by_id(self, item_id):
        if item_id in itemdata.itemdata_dict:
            item = itemdata.itemdata_dict[item_id]
            self.item_id, self.item_name, self.item_tier = item_id, item['name'], int(item['tier'])
            self.item_category, self.item_description = item['category'], item['description']
            self.item_base_rate, self.item_cost = int(item['rate']), int(item['cost'])
            self.item_emoji = item['emoji']
            self.item_image = ""
            if "Nadir" in self.item_id:
                self.item_image = f"{gli.web_url}NonGear_Icon/Misc/{self.item_id}.png"
            elif "Essence" in self.item_id:
                self.item_image = f"{gli.web_url}NonGear_Icon/Essence/Frame_Essence_{self.item_tier}.png"
            elif "Void" in self.item_id:
                name_data = self.item_name.split()
                item_type = name_data[-1].strip('()') if "Weapon" not in self.item_name else "Saber"
                self.item_image = f"{gli.web_url}Gear_Icon/{item_type}/Frame_{item_type}_5.png"
            elif "Unrefined" in self.item_id:
                item_type = self.item_name.split()[-1]
                self.item_image = f"{gli.web_url}Gear_Icon/{item_type}/Frame_{item_type}_4.png"
            elif "Gem" in self.item_id and "Gemstone" not in self.item_id:
                self.item_image = f"{gli.web_url}/Gear_Icon/Frame_{self.item_id.replace('Gem', 'Gem_')}.png"
            elif self.item_id in ["Gemstone10", "Gemstone11"]:
                self.item_image = f"{gli.web_url}NonGear_Icon/Gemstone/Frame_{self.item_id}.png"
            elif "Jewel" in self.item_id:
                icon = {"Jewel1": "Gem_1", "Jewel2": "Gem_1", "Jewel3": "Gem_5", "Jewel4": "Gem_7", "Jewel5": "Gem_8"}
                self.item_image = f"{gli.web_url}Gear_Icon/Frame_{icon[self.item_id]}.png"
            elif self.item_category in gli.availability_list_nongear:
                self.item_image = f"{gli.web_url}NonGear_Icon/{self.item_category}/Frame_{self.item_id}.png"
        else:
            print(f"Item with ID '{item_id}' not found in itemdata_dict.")

    async def create_bitem_embed(self, player_obj):
        item_qty = await inventory.check_stock(player_obj, self.item_id)
        item_msg = f"{self.item_description}\n{player_obj.player_username}'s Stock: {item_qty}"
        colour, _ = inventory.sm.get_gear_tier_colours(self.item_tier)
        loot_embed = discord.Embed(colour=colour, title=self.item_name, description=item_msg)
        if self.item_image != "":
            loot_embed.set_thumbnail(url=self.item_image)
        return loot_embed


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
            if 'Fae' not in item_id and 'Skull' not in item_id:
                target_item = inventory.BasicItem(item_id)
                item_list.append(target_item)
    return item_list


async def read_custom_item(item_id=None, reloading=None, fetch_equipped=None):
    # Handle single item
    if fetch_equipped is None:
        raw_query = "SELECT * FROM CustomInventory WHERE item_id = :id_check"
        df = await rqy(raw_query, return_value=True, params={'id_check': item_id})
        if df is None or len(df.index) == 0:
            return None
        item = await assign_item_values(df.to_dict('records')[0])
        if reloading is not None:  # Reloading is only supported for single item input at this time.
            reloading.__dict__.update(item.__dict__)
        if "[Sacred]" in item.item_name:
            item.is_sacred = True
        return item

    # Handle multiple items
    id_list = [item_id if item_id != 0 else None for item_id in fetch_equipped]
    query_id_list = [item_id for item_id in id_list if item_id is not None]
    if not query_id_list:
        return None
    id_data = ', '.join([str(item_id) for item_id in query_id_list])
    raw_query = f"SELECT * FROM CustomInventory WHERE item_id IN ({id_data})"
    df = await rqy(raw_query, return_value=True)
    if df is None or len(df.index) == 0:
        return
    equipped_items, item_list, count = [], [], 0
    for row in df.to_dict('records'):
        equipped_items.append(await assign_item_values(row))
    item_iterable = iter(equipped_items)
    item_list = [None if item_id is None else next(item_iterable) for item_id in id_list]
    return item_list


async def scan_specific_item(player_obj, base_types):
    raw_query = (f"SELECT * FROM CustomInventory "
                 f"WHERE player_id = :player_check AND item_base_type LIKE :base_type")
    batch_params = [{"player_check": player_obj.player_id, "base_type": base_type} for base_type in base_types]
    df_list = await rqy(raw_query, params=batch_params, batch=True, return_value=True)
    results = [False] * len(base_types)
    for idx, df in enumerate(df_list):
        if df is None or len(df.index) == 0:
            results[idx] = True
    return results


async def assign_item_values(row):
    base_type, item_tier = str(row['item_base_type']), int(row['item_tier'])
    item = CustomItem(int(row['player_id']), str(row['item_type']), item_tier, base_type=base_type)
    item.item_id, item.item_name = int(row['item_id']), str(row['item_name'])
    temp_elements = list(row['item_elements'].split(';'))
    item.item_elements, item.item_damage_type = list(map(int, temp_elements)), row['item_damage_type']
    item.item_enhancement = int(row['item_enhancement'])
    item.item_quality_tier = int(row['item_quality_tier'])
    item.roll_values = list(row['item_roll_values'].split(';'))
    item.item_num_rolls = len(item.roll_values)
    item.item_base_stat, item.item_bonus_stat = float(row['item_base_stat']), str(row['item_bonus_stat'])
    item.base_damage_min, item.base_damage_max = int(row['item_base_dmg_min']), int(row['item_base_dmg_max'])
    item.item_num_sockets, item.item_inlaid_gem_id = int(row['item_num_sockets']), int(row['item_inlaid_gem_id'])
    item.update_damage()
    return item


async def add_custom_item(item):
    # Item element string.
    item_elements = ""
    for x in item.item_elements:
        item_elements += str(x) + ";"
    if item_elements != "":
        item_elements = item_elements[:-1]

    # Item roll string.
    roll_values = ""
    for x in item.roll_values:
        roll_values += str(x) + ";"
    roll_values = roll_values[:-1]

    # Insert the item if applicable.
    if await check_capacity(item.player_owner, item.item_type):
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
        'input_10': roll_values, 'input_11': item.item_base_stat, 'input_12': item.item_bonus_stat,
        'input_13': item.base_damage_min, 'input_14': item.base_damage_max,
        'input_15': item.item_num_sockets, 'input_16': item.item_inlaid_gem_id
    }
    await rqy(insert_query, params=params)
    # Fetch the item id of the inserted item
    select_query = ("SELECT item_id FROM CustomInventory WHERE player_id = :player_check AND item_name = :name_check "
                    "AND item_base_dmg_min = :min_check AND item_base_dmg_max = :max_check "
                    "AND item_elements = :element_check")
    params = {"player_check": item.player_owner, "name_check": item.item_name,
              "min_check": item.base_damage_min, "max_check": item.base_damage_max, "element_check": item_elements}
    df = await rqy(select_query, return_value=True, params=params)
    if len(df) == 0:
        return 0
    id_list = list(df['item_id'])
    result_id = max(id_list)
    item.item_id = result_id
    return result_id


# check if item already exists. Prevent duplication
async def if_custom_exists(item_id) -> bool:
    raw_query = "SELECT * FROM CustomInventory WHERE item_id = :id_check"
    df = await rqy(raw_query, True, params={'id_check': item_id})
    return False if len(df.index) == 0 else True


async def display_cinventory(player_obj, item_type):
    raw_query = ("SELECT item_id, item_name, item_tier, item_type, item_base_type, item_elements FROM CustomInventory "
                 "WHERE player_id = :player_id AND item_type LIKE :item_type "
                 "ORDER BY item_tier DESC")
    params = {'player_id': player_obj.player_id, 'item_type': f'%{item_type}%'}
    df = await rqy(raw_query, True, params=params)
    item_list = df[['item_id', 'item_name', 'item_tier', 'item_type', 'item_base_type', 'item_elements']].values.tolist()
    item_list.sort(key=lambda x: (-x[2], -x[0], x[1]))
    player_inventory = ""
    for item in item_list:
        item_id, item_name, item_tier, item_type, item_base_type, item_elements = item
        element_list = item_elements.split(";")
        if item_type == "R":
            icon_key = item_base_type
            if item_tier == 6:
                icon_key = (item_tier, item_name.split()[-1])
            elif item_tier <= 5:
                icon_key = (item_tier, element_list.index("1"))
            item_icon = gli.ring_icon_dict[icon_key]
        elif item_base_type in gli.sovereign_item_list:
            item_icon = gli.sov_icon_dict[item_base_type]
        elif "D" in item_type:
            item_icon = gli.gear_icons_map[("D", min(8, item_tier))]
        else:
            item_icon = gli.gear_icons_map[(item_type, min(8, item_tier))]
        player_inventory += f"{item_icon} <{item_id}> {item_name}\n"
    return player_inventory


async def display_binventory(player_obj, method, view_type, include_id=False):
    regex_dict = {
        "Crafting": "^(Matrix|Hammer|Pearl|Fragment|Crystal|Flame)",
        "Fae Cores": "^(Fae)",
        "Materials": "^(Scrap|Ore|Metamorphite|Shard|Heart)",
        "Unprocessed": "^(Unrefined|Gem|Jewel|Void)",
        "Essences": "^(Essence)",
        "Summoning": "^(Compass|Summon)",
        "Gemstone": "^(Catalyst|Gemstone([0-9]|1[0]))$",
        "Fish": "^(Fish)",
        "Misc": "^(Potion|Trove|Chest|Stone|Token|Skull[0-3])",
        "Ultra Rare": "^(Lotus|LightStar|DarkStar|Gemstone12|Skull4|Nephilim|Nadir|Salvation|RoyalCoin)"}
    content, title = "", f'__**{player_obj.player_username}\'s {method} Inventory:\n**__'
    raw_query = ("SELECT item_id, item_qty FROM BasicInventory "
                 "WHERE player_id = :id_check AND item_qty <> 0 ORDER BY item_id ASC")
    df = await rqy(raw_query, True, params={'id_check': player_obj.player_id})

    # Filter the data, pull associated data by the id, and build the output string.
    inventory_list = []
    regex_pattern = regex_dict[method]
    df = df[df['item_id'].str.match(regex_pattern)]
    for _, row in df.iterrows():
        temp_id = str(row['item_id'])
        if temp_id in itemdata.itemdata_dict:
            # Gemstone exception
            current_item = BasicItem(temp_id)
            if method == "Unprocessed" and "Gemstone" in temp_id:
                continue
            inventory_list.append([current_item, str(row['item_qty'])])
    for item, quantity in inventory_list:
        id_text = "" if not include_id else f" [**Item ID:** {item.item_id}]"
        content += f"{item.item_emoji} {quantity}x {item.item_name}{id_text}\n"
    if view_type == 0:
        colour, _ = sm.get_gear_tier_colours(player_obj.player_echelon)
        embed = discord.Embed(colour=colour, title=title, description=content)
        return None, embed
    content = f"{title}{content}"
    return content, None


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


async def check_stock(player_obj, item_id):
    player_stock = 0
    raw_query = ("SELECT item_qty FROM BasicInventory "
                 "WHERE player_id = :id_check AND item_id = :item_check")
    df = await rqy(raw_query, True, params={'id_check': player_obj.player_id, 'item_check': item_id})
    if len(df.index) != 0:
        player_stock = int(df['item_qty'].values[0])
    return player_stock


async def update_stock(player_obj, item_id, change, batch=None):
    if batch is not None:
        raw_query = ("INSERT INTO BasicInventory (player_id, item_id, item_qty) "
                     "VALUES (:player_id, :item_id, :item_qty) "
                     "ON DUPLICATE KEY UPDATE item_qty = item_qty + VALUES(item_qty);")
        batch_params = batch.to_dict('records')
        await rqy(raw_query, batch=True, params=batch_params)
        return
    if player_obj is None or item_id is None or change is None:
        return
    raw_query = ("SELECT item_qty FROM BasicInventory "
                 "WHERE player_id = :id_check AND item_id = :item_check")
    df = await rqy(raw_query, True, params={'id_check': player_obj.player_id, 'item_check': item_id})
    raw_query = ("INSERT INTO BasicInventory (player_id, item_id, item_qty) "
                 "VALUES(:player_check, :item_check, :new_qty)")
    player_stock = change
    if len(df.index) != 0:
        player_stock = int(df['item_qty'].values[0]) + change
        raw_query = ("UPDATE BasicInventory SET item_qty = :new_qty "
                     "WHERE player_id = :player_check AND item_id = :item_check")
    player_stock = max(player_stock, 0)
    params = {'new_qty': player_stock, 'player_check': player_obj.player_id, 'item_check': item_id}
    await rqy(raw_query, params=params)


def try_refine(player_owner, item_type, target_tier):
    # Handle flat-tier refinement (Tier 5+ non-gems)
    if "D" not in item_type and target_tier >= 5:
        is_success = False
        new_tier = generate_random_tier()
        new_tier = target_tier if new_tier <= target_tier else new_tier
        if item_type == "W" or random.randint(1, 100) <= 80:
            is_success = True
        new_item = inventory.CustomItem(player_owner, item_type, new_tier, random_enhance=True)
        return new_item, is_success
    random_check = random.randint(1, 100)
    is_success = False
    if ("D" in item_type and target_tier >= 5 and random_check <= 50) or (target_tier <= 4 and random_check <= 75):
        is_success = True
    # All other refinement.
    new_tier = generate_random_tier() if target_tier == 4 else generate_random_tier(min_tier=target_tier, max_tier=8)
    new_tier = 2 if new_tier == 1 else new_tier
    new_item = inventory.CustomItem(player_owner, item_type, new_tier, random_enhance=True)
    return new_item, is_success


async def sell(user, item, embed_msg):
    await user.reload_player()
    response_embed = embed_msg
    response = await user.check_equipped(item)
    sell_value = inventory.sell_value_by_tier[item.item_tier]
    if response != "":
        response_embed.add_field(name="Item Not Sold!", value=response, inline=False)
        return response_embed
    # Sell the item.
    sell_msg = await user.adjust_coins(sell_value, apply_pact=False)
    raw_query = "DELETE FROM CustomInventory WHERE item_id = :item_check"
    await rqy(raw_query, params={'item_check': item.item_id})
    currency_msg = f'You now have {user.player_coins:,} lotus coins!'
    response_embed.add_field(name=f"Item Sold! {gli.coin_icon} {sell_msg} lotus coins acquired!",
                             value=currency_msg, inline=False)
    return response_embed


async def delete_item(user_object, item):
    if "D" in item.item_type:
        raw_query = "UPDATE CustomInventory SET item_inlaid_gem_id = 0 WHERE item_inlaid_gem_id = :item_check"
        await rqy(raw_query, params={'item_check': item.item_id})
    else:
        await user_object.unequip_item(item)
    raw_query = "DELETE FROM CustomInventory WHERE item_id = :item_check"
    await rqy(raw_query, params={'item_check': item.item_id})


async def purge(player_obj, item_type, tier):
    await player_obj.get_equipped()
    exclusion_list = player_obj.player_equipped
    inlaid_gem_list = []
    item_list = await inventory.read_custom_item(fetch_equipped=exclusion_list)
    for e_item in item_list:
        if e_item is not None and e_item.item_inlaid_gem_id != 0:
            inlaid_gem_list.append(e_item.item_inlaid_gem_id)
    exclusion_list += inlaid_gem_list
    params = {'id_check': player_obj.player_id, 'tier_check': tier}
    exclusion_ids = ', '.join([str(item_id) for item_id in exclusion_list])
    type_checker = "" if item_type == "" else f' AND item_type = "{reverse_item_loc_dict[reverse_item_dict[item_type]]}"'
    raw_query = (f"SELECT item_tier FROM CustomInventory "
                 f"WHERE player_id = :id_check AND item_tier <= :tier_check "
                 f"AND item_id NOT IN ({exclusion_ids}){type_checker}")
    df = await rqy(raw_query, return_value=True, params=params)
    delete_query = (f"DELETE FROM CustomInventory "
                    f"WHERE player_id = :id_check AND item_tier <= :tier_check "
                    f"AND item_id NOT IN ({exclusion_ids}){type_checker}")
    await rqy(delete_query, params=params)
    coin_total = 0
    for item_tier in df['item_tier']:
        coin_total += inventory.sell_value_by_tier[int(item_tier)]
    coin_msg = await player_obj.adjust_coins(coin_total)
    return f"{player_obj.player_username} sold {len(df):,} items and received {gli.coin_icon} {coin_msg} lotus coins"


def full_inventory_embed(lost_item, embed_colour):
    item_type = custom_item_dict[lost_item.item_type]
    return sm.easy_embed("red", "Inventory Full", f"Please make space in your {item_type} inventory.")


async def generate_item(ctx, target_player, tier, elements, item_type, base_type, class_name, enhancement,
                        quality, base_stat, bonus_stat, base_dmg, num_sockets, roll_list):
    valid_damage_range = gli.damage_tier_list[tier - 1]
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
        if enhancement not in range(1, gli.max_enhancement[tier - 1] + 1):
            await ctx.send('Enhancement input not valid for given tier.')
            return None
        if quality not in range(1, 6):
            await ctx.send('Quality input not valid.')
            return None
        if class_name not in gli.class_names:
            await ctx.send('Class name input not valid.')
            return None
        if base_dmg[0] not in range(*valid_damage_range) or base_dmg[1] not in range(*valid_damage_range):
            await ctx.send('Base damage input not valid.')
            return
        new_item.item_elements = list(map(int, elements.split(';')))
        new_item.item_num_sockets, new_item.item_enhancement = num_sockets, enhancement
        new_item.item_quality_tier, new_item.item_damage_type = quality, class_name
        # Handle type specific inputs.
        speed_range = gli.speed_range_list[tier - 1]
        if ((item_type == "A" and base_stat not in range((1 + (tier - 1) * 5), tier * 5))
                or (item_type == "W" and not (speed_range[0] <= base_stat <= speed_range[1]))):
            await ctx.send('Base stat input not valid.')
            return None
        if item_type != "W":
            words = bonus_stat.split()
            if len(words) != 2:
                await ctx.send('Bonus stat input not valid.')
                return None
            if tier >= 5 and bonus_stat not in gli.rare_ability_dict.keys():
                await ctx.send('Bonus stat input not valid.')
                return None
            elif tier <= 4:
                if ((words[1] == "Bane" and words[0] not in gli.boss_list and words[0] != "Human") or
                        (words[0] not in gli.element_special_names and words[1] not in ["Feathers", "Authority"])):
                    await ctx.send('Bonus stat input not valid.')
                    return None
        else:
            item_data = gli.weapon_type_dict[new_item.item_damage_type]
            combined_list = item_data[1] + item_data[2] if new_item.item_tier >= 5 else item_data[0] + item_data[1]
            new_item.item_base_type = random.choice(combined_list)
        # Assign base/bonus stats.
        new_item.item_bonus_stat = bonus_stat if item_type != "W" else ""
        new_item.item_base_stat = base_stat if item_type in ["W", "A"] else new_item.item_base_stat
    else:
        # Handle gem/jewel specific inputs.
        if bonus_stat not in gli.path_names:
            await ctx.send('Bonus Stat input not valid for gem/jewel.')
            return None
        if tier == 8:
            base_dmg = [150000, 150000]
        elif base_dmg[0] not in range(*valid_damage_range) or base_dmg[1] not in range(*valid_damage_range):
            await ctx.send('Base damage input not valid.')
            return
        new_item.item_bonus_stat = gli.path_names.index(bonus_stat)
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
    new_item.roll_values = new_roll_values
    if count != 6 and ("D" in item_type or tier >= 6):
        await ctx.send(f'Please input 6 item rolls.')
        return

    new_item.base_damage_min, new_item.base_damage_max = min(base_dmg), max(base_dmg)
    new_item.set_item_name()
    new_item.item_id = await add_custom_item(new_item)
    return new_item


async def set_gift(player_obj, item, qty):
    raw_query = ("INSERT INTO GiftBox (issued_by_id, valid_until, claimed_by, gift_item_id, item_qty) "
                 "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5)")
    v_date = dt.now(ZoneInfo('America/Toronto')) + timedelta(days=7)
    v_date = v_date.strftime(gli.date_formatting)
    param = {"input_1": player_obj.player_id, "input_2": v_date, "input_3": "", "input_4": item.item_id, "input_5": qty}
    await rqy(raw_query, params=param)


async def claim_gifts(player_obj):
    raw_query = "SELECT * FROM GiftBox"
    df = await rqy("SELECT * FROM GiftBox", return_value=True)
    if df is None or len(df.index) == 0:
        return None
    gift_data, expired_listing, item_dict = [], [], {}
    current_date = dt.now(ZoneInfo('America/Toronto'))
    for _, row in df.iterrows():
        v_date = dt.strptime(str(row['valid_until']), gli.date_formatting)
        v_date = v_date.replace(tzinfo=ZoneInfo('America/Toronto'))
        gift_id = int(row['gift_id'])
        if current_date > v_date:
            expired_listing.append(gift_id)
            continue
        issuer, claimed = await player.get_player_by_id(str(row['issued_by_id'])), str(row['claimed_by']).split(";")
        if str(player_obj.player_id) in claimed:
            continue
        item_id, qty = str(row['gift_item_id']), int(row['item_qty'])
        temp = {"gift_id": gift_id, "issuer": issuer, "v_date": v_date, "claimed": claimed, "item": item_id, "qty": qty}
        gift_data.append(temp)
        item_dict[item_id] = item_dict[item_id] + qty if item_id in item_dict else qty
    # Assign items
    item_list = [(item_id, qty) for item_id, qty in item_dict.items()]
    batch_df = sm.list_to_batch(player_obj, item_list)
    await inventory.update_stock(None, None, None, batch=batch_df)
    # Add user to claimed listings
    if gift_data:
        params = []
        for data in gift_data:
            if data["claimed"] == ['']:
                data["claimed"] = [str(player_obj.player_id)]
            else:
                data["claimed"].append(str(player_obj.player_id))
            params.append({"player_data": ";".join(data["claimed"]), "gift_id": data["gift_id"]})
        raw_query = "UPDATE GiftBox SET claimed_by = :player_data WHERE gift_id = :gift_id"
        await rqy(raw_query, params=params, batch=True)
    # Clear expired listings
    if expired_listing:
        params = [{"gift_id": id_to_remove} for id_to_remove in expired_listing]
        await rqy("DELETE FROM GiftBox WHERE gift_id = :gift_id", params=params, batch=True)
    return item_list if len(item_list) != 0 else None


async def check_capacity(player_id, item_type):
    # For gem types (D1-D5), we need to check all gem items
    if item_type in ['D1', 'D2', 'D3', 'D4', 'D5']:
        raw_query = ("SELECT * FROM CustomInventory WHERE player_id = :player_check "
                     "AND (item_type = 'D1' OR item_type = 'D2' OR item_type = 'D3' "
                     "OR item_type = 'D4' OR item_type = 'D5')")
        params = {'player_check': player_id}
    else:
        raw_query = "SELECT * FROM CustomInventory WHERE player_id = :player_check AND item_type = :item_check"
        params = {'player_check': player_id, 'item_check': item_type}
    check_df = await rqy(raw_query, return_value=True, params=params)
    if len(check_df) > 40:
        return True
    return False
