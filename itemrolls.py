import discord
from discord.ui import Button, View

import inventory
import globalitems
import player
import random

roll_structure_dict = {"W": ["damage", "damage", "penetration", "penetration", "curse", "unique"],
                       "A": ["damage", "penetration", "curse", "defensive", "defensive", "unique"],
                       "Y": ["damage", "damage", "damage", "penetration", "curse", "unique"],
                       "G": ["damage", "damage", "damage", "penetration", "curse", "unique"],
                       "C": ["damage", "damage", "damage", "penetration", "curse", "unique"],
                       "D": ["damage", "damage", "damage", "penetration", "curse", "defensive"]}

damage_rolls = {
    "damage-0": ["Fire Damage", 25, 10, [["elemental_multiplier", 0]]],
    "damage-1": ["Water Damage", 25, 10, [["elemental_multiplier", 1]]],
    "damage-2": ["Lightning Damage", 25, 10, [["elemental_multiplier", 2]]],
    "damage-3": ["Earth Damage", 25, 10, [["elemental_multiplier", 3]]],
    "damage-4": ["Wind Damage", 25, 10, [["elemental_multiplier", 4]]],
    "damage-5": ["Ice Damage", 25, 10, [["elemental_multiplier", 5]]],
    "damage-6": ["Shadow Damage", 25, 10, [["elemental_multiplier", 6]]],
    "damage-7": ["Light Damage", 25, 10, [["elemental_multiplier", 7]]],
    "damage-8": ["Celestial Damage", 25, 10, [["elemental_multiplier", 8]]],
    "damage-9": ["Hybrid Damage (Eclipse)", 15, 8, [["elemental_multiplier", 7],
                                                    ["elemental_multiplier", 6]]],
    "damage-10": ["Hybrid Damage (Horizon)", 15, 8, [["elemental_multiplier", 4],
                                                     ["elemental_multiplier", 3]]],
    "damage-11": ["Hybrid Damage (Frostfire)", 15, 8, [["elemental_multiplier", 5],
                                                       ["elemental_multiplier", 0]]],
    "damage-12": ["Hybrid Damage (Storm)", 15, 8, [["elemental_multiplier", 1],
                                                   ["elemental_multiplier", 2]]],
    "damage-13": ["Omni Damage", 15, 5, [["all_elemental_multiplier", -1]]],
    "damage-14": ["Ultimate Damage", 25, 5, [["ultimate_multiplier", -1]]],
    "damage-15": ["Bleed Damage", 25, 5, [["bleed_multiplier", -1]]],
    "damage-16": ["Combo Damage", 10, 5, [["combo_multiplier", -1]]]
}

penetration_rolls = {
    "penetration-0": ["Fire Penetration", 15, 10, [["elemental_penetration", 0]]],
    "penetration-1": ["Water Penetration", 15, 10, [["elemental_penetration", 1]]],
    "penetration-2": ["Lightning Penetration", 15, 10, [["elemental_penetration", 2]]],
    "penetration-3": ["Earth Penetration", 15, 10, [["elemental_penetration", 3]]],
    "penetration-4": ["Wind Penetration", 15, 10, [["elemental_penetration", 4]]],
    "penetration-5": ["Ice Penetration", 15, 10, [["elemental_penetration", 5]]],
    "penetration-6": ["Shadow Penetration", 15, 10, [["elemental_penetration", 6]]],
    "penetration-7": ["Light Penetration", 15, 10, [["elemental_penetration", 7]]],
    "penetration-8": ["Celestial Penetration", 15, 10, [["elemental_penetration", 8]]],
    "penetration-9": ["Hybrid Penetration (Eclipse)", 10, 8, [["elemental_penetration", 7],
                                                              ["elemental_penetration", 6]]],
    "penetration-10": ["Hybrid Penetration (Horizon)", 10, 8, [["elemental_penetration", 4],
                                                               ["elemental_penetration", 3]]],
    "penetration-11": ["Hybrid Penetration (Frostfire)", 10, 8, [["elemental_penetration", 5],
                                                                 ["elemental_penetration", 0]]],
    "penetration-12": ["Hybrid Penetration (Storm)", 10, 8, [["elemental_penetration", 1],
                                                             ["elemental_penetration", 2]]],
    "penetration-13": ["Omni Penetration", 8, 5, [["all_elemental_penetration", -1]]],
    "penetration-14": ["Critical Penetration", 25, 5, [["critical_penetration", -1]]],
    "penetration-15": ["Bleed Penetration", 25, 5, [["bleed_penetration", -1]]],
    "penetration-16": ["Combo Penetration", 20, 5, [["combo_penetration", -1]]],
    "penetration-17": ["Ultimate Penetration", 20, 5, [["ultimate_penetration", -1]]]
}

curse_rolls = {
    "curse-0": ["Fire Curse", 15, 10, [["elemental_curse", 0]]],
    "curse-1": ["Water Curse", 15, 10, [["elemental_curse", 1]]],
    "curse-2": ["Lightning Curse", 15, 10, [["elemental_curse", 2]]],
    "curse-3": ["Earth Curse", 15, 10, [["elemental_curse", 3]]],
    "curse-4": ["Wind Curse", 15, 10, [["elemental_curse", 4]]],
    "curse-5": ["Ice Curse", 15, 10, [["elemental_curse", 5]]],
    "curse-6": ["Shadow Curse", 15, 10, [["elemental_curse", 6]]],
    "curse-7": ["Light Curse", 15, 10, [["elemental_curse", 7]]],
    "curse-8": ["Celestial Curse", 15, 10, [["elemental_curse", 8]]],
    "curse-9": ["Hybrid Curse (Eclipse)", 10, 5, [["elemental_curse", 7], ["elemental_curse", 6]]],
    "curse-10": ["Hybrid Curse (Horizon)", 10, 5, [["elemental_curse", 4], ["elemental_curse", 3]]],
    "curse-11": ["Hybrid Curse (Frostfire)", 10, 5, [["elemental_curse", 5], ["elemental_curse", 0]]],
    "curse-12": ["Hybrid Curse (Storm)", 10, 5, [["elemental_curse", 1], ["elemental_curse", 2]]],
    "curse-13": ["Omni Curse", 8, 5, [["all_elemental_curse", -1]]]
}

defensive_rolls = {
    "defensive-0": ["Health Regen", 1, 3, [["hp_regen", -1]]],
    "defensive-1": ["Health Multiplier", 15, 10, [["hp_multiplier", -1]]],
    "defensive-2": ["Damage Mitigation", 15, 5, [["damage_mitigation", -1]]],
    "defensive-3": ["Fire Resistance", 10, 5, [["elemental_resistance", 0]]],
    "defensive-4": ["Water Resistance", 10, 5, [["elemental_resistance", 1]]],
    "defensive-5": ["Lightning Resistance", 10, 5, [["elemental_resistance", 2]]],
    "defensive-6": ["Earth Resistance", 10, 5, [["elemental_resistance", 3]]],
    "defensive-7": ["Wind Resistance", 10, 5, [["elemental_resistance", 4]]],
    "defensive-8": ["Ice Resistance", 10, 5, [["elemental_resistance", 5]]],
    "defensive-9": ["Shadow Resistance", 10, 5, [["elemental_resistance", 6]]],
    "defensive-10": ["Light Resistance", 10, 5, [["elemental_resistance", 7]]],
    "defensive-11": ["Celestial Resistance", 10, 5, [["elemental_resistance", 8]]],
    "defensive-12": ["Hybrid Resistance (Eclipse)", 8, 3, [["elemental_resistance", 7], ["elemental_resistance", 6]]],
    "defensive-13": ["Hybrid Resistance (Horizon)", 8, 3, [["elemental_resistance", 4], ["elemental_resistance", 3]]],
    "defensive-14": ["Hybrid Resistance (Frostfire)", 8, 3, [["elemental_resistance", 5], ["elemental_resistance", 0]]],
    "defensive-15": ["Hybrid Resistance (Storm)", 8, 3, [["elemental_resistance", 1], ["elemental_resistance", 2]]],
    "defensive-16": ["Omni Resistance", 5, 2, [["all_elemental_resistance", -1]]]
}

shared_unique_rolls = {
    "unique-0-s": ["Attack Speed", 5, 50, [["attack_speed", -1]]],
    "unique-1-s": ["Critical Strike Chance", 20, 100, [["critical_chance", -1]]],
    "unique-2-s": ["Critical Strike Multiplier", 25, 100, [["critical_multiplier", -1]]],
    "unique-3-s": ["Omni Aura", 5, 50, [["aura", -1]]],
    "unique-4-s": ["Class Mastery", 3, 50, [["class_multiplier", -1]]],
    "unique-5-s": ["Human Bane", 20, 200, [["banes", 4]]]
}

weapon_unique_rolls = {
    "unique-0-w": ["1% Chance for trigger Annihilator X", 1, 1, [["specialty_rate", 0]]],
    "unique-1-w": ["X% of Non-Fire Damage Converted to Fire Damage", 10, 10, [["elemental_conversion", 0]]],
    "unique-2-w": ["X% of Non-Water Damage Converted to Water Damage", 10, 10, [["elemental_conversion", 1]]],
    "unique-3-w": ["X% of Non-Lightning Damage Converted to Lightning Damage", 10, 10, [["elemental_conversion", 2]]],
    "unique-4-w": ["X% of Non-Earth Damage Converted to Earth Damage", 10, 10, [["elemental_conversion", 3]]],
    "unique-5-w": ["X% of Non-Wind Damage Converted to Wind Damage", 10, 10, [["elemental_conversion", 4]]],
    "unique-6-w": ["X% of Non-Ice Damage Converted to Ice Damage", 10, 10, [["elemental_conversion", 5]]],
    "unique-7-w": ["X% of Non-Shadow Damage Converted to Shadow Damage", 10, 10, [["elemental_conversion", 6]]],
    "unique-8-w": ["X% of Non-Light Damage Converted to Light Damage", 10, 10, [["elemental_conversion", 7]]],
    "unique-9-w": ["X% of Non-Celestial Damage Converted to Celestial Damage", 10, 10, [["elemental_conversion", 8]]],
    "unique-10-w": ["X% Hybrid Conversion (Eclipse)", 7, 5, [["elemental_conversion", 7], ["elemental_conversion", 6]]],
    "unique-11-w": ["X% Hybrid Conversion (Horizon)", 7, 5, [["elemental_conversion", 4], ["elemental_conversion", 3]]],
    "unique-12-w": ["X% Hybrid Conversion (Frostfire)", 7, 5, [["elemental_conversion", 5], ["elemental_conversion", 0]]],
    "unique-13-w": ["X% Hybrid Conversion (Storm)", 7, 5, [["elemental_conversion", 1], ["elemental_conversion", 2]]]
}

armour_unique_rolls = {
    "unique-0-a": ["Gain X% Elemental Damage per Matching Resistance", 1, 30, [["unique_conversion", 0]]],
    "unique-1-a": ["Gain X% Final Damage per 10 HP", 1, 30, [["unique_conversion", 1]]]
}

accessory_unique_rolls = {
    "unique-0-y": ["Hyper Bleed Rate", 2, 15, [["specialty_rate", 0]]],
    "unique-1-y": ["Omega Critical Rate", 2, 15, [["specialty_rate", 1]]],
    "unique-2-y": ["Fractal Rate", 2, 15, [["specialty_rate", 2]]],
    "unique-3-y": ["Time Lock Rate", 2, 15, [["specialty_rate", 3]]],
    "unique-4-y": ["Fortress Bane", 25, 10, [["banes", 0]]],
    "unique-5-y": ["Dragon Bane", 25, 10, [["banes", 1]]],
    "unique-6-y": ["Demon Bane", 25, 10, [["banes", 2]]],
    "unique-7-y": ["Paragon Bane", 25, 10, [["banes", 3]]]
}

unique_rolls = {
    "s": [shared_unique_rolls, sum(weighting for _, _, weighting, _ in shared_unique_rolls.values())],
    "w": [weapon_unique_rolls, sum(weighting for _, _, weighting, _ in weapon_unique_rolls.values())],
    "a": [armour_unique_rolls, sum(weighting for _, _, weighting, _ in armour_unique_rolls.values())],
    "y": [accessory_unique_rolls, sum(weighting for _, _, weighting, _ in accessory_unique_rolls.values())]
}

item_roll_master_dict = {
    "damage": [damage_rolls, sum(weighting for _, _, weighting, _ in damage_rolls.values())],
    "penetration": [penetration_rolls, sum(weighting for _, _, weighting, _ in penetration_rolls.values())],
    "curse": [curse_rolls, sum(weighting for _, _, weighting, _ in curse_rolls.values())],
    "defensive": [defensive_rolls, sum(weighting for _, _, weighting, _ in defensive_rolls.values())],
    "unique": unique_rolls
}

augment_icons = ["<:esocket:1148387477615300740>", "🟢", "🔵",
                 "<:eprl:1148390531345432647>", "<:ov:1177184321686228992>", "<:or:1177184323691098195>"]
cost_list = [500000, 1000000, 2500000, 5000000, 10000000, 20000000]


class SelectRollsView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__()
        self.player_object = player_object
        self.selected_item = selected_item
        self.embed = None
        self.new_view = None
        self.count_view = discord.ui.Select(
            placeholder="Select Number of Rolls", min_values=1, max_values=1,
            options=[
                discord.SelectOption(label=f"{str(i)} Rolls", description=f"Cost: {cost_list[i - 1]:,}", value=str(i))
                for i in range(1, 7)
            ]
        )
        self.count_view.callback = self.count_callback
        self.add_item(self.count_view)

    async def count_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.name == self.player_object.player_name:
                if not self.embed:
                    roll_count = int(interaction.data['values'][0])
                    self.embed = discord.Embed(
                        title="Vexia, Scribe of the Eons",
                        description="Select a damage skill. (1st Selection)",
                        color=discord.Color.blue()
                    )
                    self.new_view = SkillSelectView(self.player_object, self.selected_item,
                                                    roll_count, 1, [])
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class SkillSelectView(discord.ui.View):
    def __init__(self, player_object, selected_item, total_rolls, roll_num, selected_skills):
        super().__init__()
        self.player_object = player_object
        self.selected_item = selected_item
        self.total_rolls = total_rolls
        self.roll_num = roll_num
        self.selected_skills = selected_skills
        self.embed = None
        self.new_view = None

        roll_structure = roll_structure_dict[self.selected_item.item_type]
        roll_type = roll_structure[self.roll_num - 1]
        if roll_type == "unique":
            roll_list, _ = handle_unique(self.selected_item)
        else:
            roll_list = item_roll_master_dict[roll_type][0]

        options = [
            discord.SelectOption(
                label=roll[1][0], description=f"Weighting: {roll[1][2]}", value=roll[0]
            )
            for roll in roll_list.items() if roll[0] not in self.selected_skills
        ]

        self.skill_view = discord.ui.Select(placeholder=f"Select Skill for Roll {self.roll_num}",
                                            min_values=1, max_values=1, options=options)
        self.skill_view.callback = self.skill_callback
        self.add_item(self.skill_view)

    async def skill_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.name == self.player_object.player_name:
                if not self.embed:
                    selected_skill = str(interaction.data['values'][0])
                    self.selected_skills.append(selected_skill)
                    if (self.roll_num + 1) <= self.total_rolls:
                        # Load the next view for the next roll
                        npc_comment = f"I really haven't got all day you know. (Selection: {self.roll_num + 1})\n"
                        for roll_id in self.selected_skills:
                            temp_id = f"1-{roll_id}"
                            current_roll = ItemRoll(temp_id)
                            npc_comment += f"{current_roll.roll_name}\n"
                        self.embed = discord.Embed(
                            title="Vexia, Scribe of the Eons",
                            description=npc_comment,
                            color=discord.Color.blue()
                        )
                        self.new_view = SkillSelectView(self.player_object, self.selected_item,
                                                        self.total_rolls, self.roll_num + 1, self.selected_skills)
                    else:
                        # This is the last roll, display the summary
                        npc_comment = "Is this really all you wanted?\n"
                        skill_display = ""
                        for roll_id in self.selected_skills:
                            temp_id = f"1-{roll_id}"
                            current_roll = ItemRoll(temp_id)
                            skill_display += f"{current_roll.roll_name}\n"
                            if current_roll.roll_code == "unique-0-y":
                                npc_comment = "Oooh, you have impeccable taste.\n"
                        summary_msg = npc_comment + skill_display
                        summary_msg += f"\n{globalitems.coin_icon} Coin Offering: {cost_list[self.total_rolls - 1]:,}"
                        self.embed = discord.Embed(
                            title="Vexia, Scribe of the Eons",
                            description=summary_msg,
                            color=discord.Color.green()
                        )
                        self.new_view = SkillPurchaseView(self.player_object, self.selected_item,
                                                          self.total_rolls, self.selected_skills)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class SkillPurchaseView(discord.ui.View):
    def __init__(self, player_object, selected_item, total_rolls, selected_skills):
        super().__init__()
        self.player_object = player_object
        self.selected_item = selected_item
        self.total_rolls = total_rolls
        self.selected_skills = selected_skills
        self.embed = None

    @discord.ui.button(label="Inscribe", style=discord.ButtonStyle.green)
    async def inscribe_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name == self.player_object.player_name:
            if not self.embed:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                custom_cost = cost_list[self.total_rolls - 1]
                # Handle the cost and cost eligibility.
                if reload_player.player_coins >= custom_cost:
                    # Reload the player and item data.
                    reload_player.player_coins -= custom_cost
                    reload_player.set_player_field("player_coins", reload_player.player_coins)
                    reload_item = inventory.read_custom_item(self.selected_item.item_id)
                    new_roll_list = []
                    roll_tier_list = []
                    # Proxy the number of rolls. This is required.
                    temp_num_rolls = reload_item.item_num_rolls
                    for roll_index in range(max(temp_num_rolls, self.total_rolls)):
                        # Log the tiers from the original rolls.
                        if (roll_index + 1) >= temp_num_rolls:
                            temp_tier = 1
                        else:
                            current_roll = ItemRoll(reload_item.item_roll_values[roll_index])
                            temp_tier = current_roll.roll_tier
                        roll_tier_list.append(temp_tier)
                        # Build a list of the new roll ids.
                        if roll_index + 1 <= self.total_rolls:
                            new_roll = f"1-{self.selected_skills[roll_index]}"
                            new_roll_list.append(new_roll)
                    # Add all the new selected and unselected rolls. Compare the Proxy after updating the value.
                    reload_item.item_roll_values = new_roll_list
                    reload_item.item_num_rolls = self.total_rolls
                    if temp_num_rolls > self.total_rolls:
                        add_roll(reload_item, (temp_num_rolls - self.total_rolls))
                    # Set all the roll tiers
                    for idx in range(reload_item.item_num_rolls):
                        unassigned_roll = reload_item.item_roll_values[idx][1:]
                        reload_item.item_roll_values[idx] = f"{roll_tier_list[idx]}{unassigned_roll}"
                    # Save the item.
                    reload_item.update_stored_item()
                    self.embed = reload_item.create_citem_embed()
                    await interaction.response.edit_message(embed=self.embed, view=None)
                else:
                    # Display the cost failed message. Reload the same view.
                    cost_msg = "If you really want me you'd better provide a sufficient offering."
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Vexia, Scribe of the Eons",
                                              description=cost_msg)
                    await interaction.response.edit_message(embed=embed_msg, view=self)
            else:
                await interaction.response.edit_message(embed=self.embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.name == self.player_object.player_name:
                cancellation_embed = discord.Embed(
                    title="Vexia, Scribe of the Eons",
                    description="Come back when you've made up your mind.",
                    color=discord.Color.red()
                )
                await interaction.response.edit_message(embed=cancellation_embed, view=None)
        except Exception as e:
            print(e)


class ItemRoll:
    def __init__(self, roll_id):
        # Initialize values
        self.roll_id = roll_id
        roll_details = roll_id.split("-")
        self.roll_tier = int(roll_details[0])
        self.roll_icon = f"{augment_icons[self.roll_tier - 1]}"
        self.roll_category = roll_details[1]
        self.roll_code = f"{roll_details[1]}-{roll_details[2]}"
        self.roll_value = 0
        self.roll_msg = ""
        # Adjust specific values
        roll_adjust = 0.01 * self.roll_tier
        if self.roll_category != "unique":
            category_dict = item_roll_master_dict[self.roll_category]
            current_dict = category_dict[0]
            current_roll = current_dict[self.roll_code]
            self.roll_value = current_roll[1] * roll_adjust
            self.roll_msg = f"{current_roll[0]} {int(round(self.roll_value * 100))}%"
        else:
            self.roll_code += f"-{roll_details[3]}"
            current_dict = unique_rolls[roll_details[3]][0]
            current_roll = current_dict[self.roll_code]
            self.roll_value = current_roll[1] * roll_adjust
            temp_msg = f"{current_roll[0]}"
            if "X" in temp_msg:
                self.roll_msg = temp_msg.replace("X", str(int(round(self.roll_value * 100))))
            else:
                self.roll_msg = f"{temp_msg} {int(round(self.roll_value * 100))}%"
        self.roll_name = current_roll[0]


def display_rolls(selected_item):
    item_rolls_msg = ""
    for roll_information in selected_item.item_roll_values:
        current_roll = ItemRoll(roll_information)
        item_rolls_msg += f'\n{current_roll.roll_icon} {current_roll.roll_msg}'
    return item_rolls_msg


def add_roll(selected_item, num_rolls):
    for _ in range(num_rolls):
        # Initialize variables.
        exclusions_list = []
        exclusions_weighting = []
        new_roll_type = roll_structure_dict[selected_item.item_type][selected_item.item_num_rolls]
        # Handle "unique" method
        if new_roll_type == "unique":
            roll_list, total_weighting = handle_unique(selected_item)
        else:
            roll_list = item_roll_master_dict[new_roll_type][0]
            total_weighting = item_roll_master_dict[new_roll_type][1]
        # Build the list of available options from the exclusions.
        for roll_id in selected_item.item_roll_values:
            current_roll = ItemRoll(roll_id)
            if current_roll.roll_category == new_roll_type:
                exclusions_list.append(current_roll.roll_code)
                roll_weighting = roll_list[current_roll.roll_code][2]
                exclusions_weighting.append(roll_weighting)
        available_rolls = [roll for roll in roll_list if roll not in exclusions_list]
        # Select and set a new roll.
        selected_roll_code = select_roll(total_weighting, exclusions_weighting, available_rolls, roll_list)
        roll_tier = 1
        if selected_item.item_type == "D":
            roll_tier = selected_item.item_tier if selected_item.item_tier < 7 else 6
        new_roll_id = f"{roll_tier}-{selected_roll_code}"
        selected_item.item_roll_values.append(new_roll_id)
        selected_item.item_num_rolls += 1


def reroll_roll(selected_item, method_type):
    if method_type == "all":
        selected_item.item_num_rolls = 0
        selected_item.item_roll_values = []
        add_roll(selected_item, 6)
    else:
        exclusions_list = []
        exclusions_weighting = []
        method = random.choice(roll_structure_dict[selected_item.item_type]) if method_type == "any" else method_type
        # Determine the target roll index based on the structure.
        max_count = roll_structure_dict[selected_item.item_type].count(method)
        target_count = random.randint(1, max_count)
        # Build the list of available options from the exclusions.
        if method == "unique":
            roll_list, total_weighting = handle_unique(selected_item)
        else:
            roll_list = item_roll_master_dict[method][0]
            total_weighting = item_roll_master_dict[method][1]
        matches_count = 0
        for roll_index, roll_id in enumerate(selected_item.item_roll_values):
            current_roll = ItemRoll(roll_id)
            if current_roll.roll_category == method:
                matches_count += 1
                exclusions_list.append(current_roll.roll_code)
                roll_weighting = roll_list[current_roll.roll_code][2]
                exclusions_weighting.append(roll_weighting)
                if matches_count == target_count:
                    original_roll_tier = current_roll.roll_tier
                    original_roll_location = roll_index
        available_rolls = [roll for roll in roll_list if roll not in exclusions_list]
        # Select and set a new roll.
        selected_roll_code = select_roll(total_weighting, exclusions_weighting, available_rolls, roll_list)
        new_roll_id = f"{original_roll_tier}-{selected_roll_code}"
        selected_item.item_roll_values[original_roll_location] = new_roll_id


def handle_unique(selected_item):
    # Determine the unique rolls to use.
    specific_type = "y" if selected_item.item_type in "YGC" else selected_item.item_type.lower()
    selected_unique_type = ["s", specific_type]
    # Combine the data.
    combined_dict = {}
    combined_dict.update(unique_rolls[selected_unique_type[0]][0])
    combined_dict.update(unique_rolls[selected_unique_type[1]][0])
    combined_weighting = unique_rolls[selected_unique_type[0]][1] + unique_rolls[selected_unique_type[1]][1]
    return combined_dict, combined_weighting


def select_roll(total_weighting, exclusions_weighting, available_rolls, roll_list):
    adjusted_weighting = total_weighting - sum(exclusions_weighting) - 1
    random_value = random.randint(0, adjusted_weighting)
    cumulative_weight = 0
    selected_roll_code = ""
    for roll_code in available_rolls:
        cumulative_weight += roll_list[roll_code][2]
        if random_value < cumulative_weight:
            return roll_code


def check_augment(selected_item):
    aug_total = 0
    v_aug_total = 0
    m_aug_total = 0

    def split_augment(augment_total, v_augment_total, m_augment_total, roll_tier):
        temp_total = roll_tier - 1
        if temp_total > 3:
            extra_augments = temp_total - 3
            if extra_augments == 1:
                v_augment_total += 1
            if extra_augments == 2:
                m_augment_total += 1
            augment_total += temp_total - extra_augments
        return augment_total, v_augment_total, m_augment_total

    # check if the item has no rolls.
    if selected_item.item_num_rolls == 0:
        aug_total = -1
        return aug_total, v_aug_total, m_aug_total
    # Calculate the number of regular, void, and miracle augments.
    for roll in selected_item.item_roll_values:
        current_roll = ItemRoll(roll)
        aug_total, v_aug_total, m_aug_total = split_augment(aug_total, v_aug_total, m_aug_total,
                                                            current_roll.roll_tier)
    # If the item has less then 6 rolls, check if they are already maxed.
    if selected_item.item_num_rolls < 6 and selected_item.item_num_rolls * 3 == aug_total:
        aug_total = -1
    return aug_total, v_aug_total, m_aug_total


def add_augment(selected_item, method):
    rolls_copy = selected_item.item_roll_values.copy()
    random.shuffle(rolls_copy)
    selected_id = ""
    selected_tier = 0
    # Check each roll for eligibility in a random order.
    for roll in rolls_copy:
        current_roll = ItemRoll(roll)
        selected_tier = current_roll.roll_tier
        if ((current_roll.roll_tier < 4 and method == 0) or
                (current_roll.roll_tier < 5 and method == 1) or current_roll.roll_tier < 6 and method == 2):
            selected_id = roll
            break
    # If a roll was selected then upgrade the tier.
    if selected_id != "":
        roll_location = selected_item.item_roll_values.index(selected_id)
        selected_item.item_roll_values[roll_location] = str(selected_tier + 1) + selected_id[1:]


def assign_gem_values(player_object, e_item):
    gem_id = e_item.item_inlaid_gem_id
    if gem_id != 0:
        e_gem = inventory.read_custom_item(gem_id)
        player_object.player_damage += (e_gem.item_damage_min + e_gem.item_damage_max) / 2
        assign_roll_values(player_object, e_gem)


def assign_roll_values(player_object, equipped_item):
    for roll_id in equipped_item.item_roll_values:
        current_roll = ItemRoll(roll_id)
        # Locate the roll information.
        if current_roll.roll_category == "unique":
            roll_list, _ = handle_unique(equipped_item)
            roll_data = roll_list[current_roll.roll_code][3]
        else:
            roll_data = item_roll_master_dict[current_roll.roll_category][0][current_roll.roll_code][3]
        # Update all the attributes associated with the roll.
        for attribute_info in roll_data:
            attribute_name, attribute_position = attribute_info
            if attribute_position == -1:
                setattr(player_object, attribute_name, getattr(player_object, attribute_name) + current_roll.roll_value)
            else:
                target_list = getattr(player_object, attribute_name)
                target_list[attribute_position] += current_roll.roll_value
    assign_item_element_stats(player_object, equipped_item)


def assign_item_element_stats(player_object, equipped_item):
    associated_stats = {
        "A": [player_object.elemental_resistance, 0.15],
        "Y": [player_object.elemental_damage, 0.25],
        "G": [player_object.elemental_penetration, 0.15],
        "C": [player_object.elemental_curse, 0.1],
    }
    # Assign stats from elements on the item.
    for idz, z in enumerate(equipped_item.item_elements):
        if z == 1:
            if equipped_item.item_type in associated_stats:
                associated_stats[equipped_item.item_type][0][idz] += associated_stats[equipped_item.item_type][1]

