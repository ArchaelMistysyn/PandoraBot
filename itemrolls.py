# General imports
import discord
from discord.ui import Button, View
import random

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import player
import inventory
import combat

# Item/crafting imports
import ring

roll_structure_dict = {"W": ["damage", "damage", "penetration", "penetration", "curse", "unique"],
                       "A": ["damage", "penetration", "curse", "defensive", "defensive", "unique"],
                       "V": ["damage", "penetration", "curse", "defensive", "defensive", "unique"],
                       "Y": ["damage", "damage", "damage", "penetration", "curse", "unique"],
                       "G": ["damage", "damage", "damage", "penetration", "curse", "unique"],
                       "C": ["damage", "damage", "damage", "penetration", "curse", "unique"],
                       "D1": ["damage", "damage", "damage", "penetration", "defensive", "defensive"],
                       "D2": ["damage", "damage", "penetration", "penetration", "defensive", "defensive"],
                       "D3": ["damage", "damage", "damage", "penetration", "curse", "defensive"],
                       "D4": ["damage", "damage", "penetration", "penetration", "curse", "defensive"],
                       "D5": ["damage", "damage", "penetration", "penetration", "curse", "curse"]}
damage_rolls = {
    "damage-0": ["Fire Damage", 25, 10, [["elemental_mult", 0]]],
    "damage-1": ["Water Damage", 25, 10, [["elemental_mult", 1]]],
    "damage-2": ["Lightning Damage", 25, 10, [["elemental_mult", 2]]],
    "damage-3": ["Earth Damage", 25, 10, [["elemental_mult", 3]]],
    "damage-4": ["Wind Damage", 25, 10, [["elemental_mult", 4]]],
    "damage-5": ["Ice Damage", 25, 10, [["elemental_mult", 5]]],
    "damage-6": ["Shadow Damage", 25, 10, [["elemental_mult", 6]]],
    "damage-7": ["Light Damage", 25, 10, [["elemental_mult", 7]]],
    "damage-8": ["Celestial Damage", 25, 10, [["elemental_mult", 8]]],
    "damage-9": ["Hybrid Damage (Eclipse)", 20, 8, [["special_mult", "Eclipse"]]],
    "damage-10": ["Hybrid Damage (Horizon)", 20, 8, [["special_mult", "Horizon"]]],
    "damage-11": ["Hybrid Damage (Frostfire)", 20, 8, [["special_mult", "Frostfire"]]],
    "damage-12": ["Hybrid Damage (Storms)", 20, 8, [["special_mult", "Storms"]]],
    "damage-13": ["Omni Damage", 15, 5, [["all_elemental_mult", -1]]],
    "damage-14": ["Ultimate Damage", 25, 5, [["ultimate_mult", -1]]],
    "damage-15": ["Bleed Damage", 25, 5, [["bleed_mult", -1]]],
    "damage-16": ["Combo Damage", 10, 5, [["combo_mult", -1]]],
    "damage-17": ["Hybrid Damage (Chaos)", 18, 5, [["special_mult", "Chaos"]]],
    "damage-18": ["Hybrid Damage (Holy)", 18, 5, [["special_mult", "Holy"]]]}
penetration_rolls = {
    "penetration-0": ["Fire Penetration", 15, 10, [["elemental_pen", 0]]],
    "penetration-1": ["Water Penetration", 15, 10, [["elemental_pen", 1]]],
    "penetration-2": ["Lightning Penetration", 15, 10, [["elemental_pen", 2]]],
    "penetration-3": ["Earth Penetration", 15, 10, [["elemental_pen", 3]]],
    "penetration-4": ["Wind Penetration", 15, 10, [["elemental_pen", 4]]],
    "penetration-5": ["Ice Penetration", 15, 10, [["elemental_pen", 5]]],
    "penetration-6": ["Shadow Penetration", 15, 10, [["elemental_pen", 6]]],
    "penetration-7": ["Light Penetration", 15, 10, [["elemental_pen", 7]]],
    "penetration-8": ["Celestial Penetration", 15, 10, [["elemental_pen", 8]]],
    "penetration-9": ["Hybrid Penetration (Eclipse)", 10, 8, [["special_pen", "Eclipse"]]],
    "penetration-10": ["Hybrid Penetration (Horizon)", 10, 8, [["special_pen", "Horizon"]]],
    "penetration-11": ["Hybrid Penetration (Frostfire)", 10, 8, [["special_pen", "Frostfire"]]],
    "penetration-12": ["Hybrid Penetration (Storms)", 10, 8, [["special_pen", "Storms"]]],
    "penetration-13": ["Omni Penetration", 8, 5, [["all_elemental_pen", -1]]],
    "penetration-14": ["Critical Penetration", 25, 5, [["critical_pen", -1]]],
    "penetration-15": ["Bleed Penetration", 25, 5, [["bleed_pen", -1]]],
    "penetration-16": ["Combo Penetration", 20, 5, [["combo_pen", -1]]],
    "penetration-17": ["Ultimate Penetration", 20, 5, [["ultimate_pen", -1]]],
    "penetration-18": ["Hybrid Penetration (Chaos)", 9, 8, [["special_pen", "Chaos"]]],
    "penetration-19": ["Hybrid Penetration (Holy)", 9, 8, [["special_pen", "Holy"]]]}
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
    "curse-9": ["Hybrid Curse (Eclipse)", 10, 5, [["special_curse", "Eclipse"]]],
    "curse-10": ["Hybrid Curse (Horizon)", 10, 5, [["special_curse", "Horizon"]]],
    "curse-11": ["Hybrid Curse (Frostfire)", 10, 5, [["special_curse", "Frostfire"]]],
    "curse-12": ["Hybrid Curse (Storms)", 10, 5, [["special_curse", "Storms"]]],
    "curse-13": ["Omni Curse", 8, 5, [["all_elemental_curse", -1]]],
    "curse-14": ["Hybrid Curse (Chaos)", 9, 5, [["special_curse", "Chaos"]]],
    "curse-15": ["Hybrid Curse (Holy)", 9, 5, [["special_curse", "Holy"]]]}
defensive_rolls = {
    "defensive-0": ["Health Regen", 0.5, 3, [["hp_regen", -1]]],
    "defensive-1": ["Health Multiplier", 15, 10, [["hp_multiplier", -1]]],
    "defensive-2": ["Mitigation Bonus", 15, 5, [["damage_mitigation", -1]]],
    "defensive-3": ["Fire Resistance", 10, 5, [["elemental_res", 0]]],
    "defensive-4": ["Water Resistance", 10, 5, [["elemental_res", 1]]],
    "defensive-5": ["Lightning Resistance", 10, 5, [["elemental_res", 2]]],
    "defensive-6": ["Earth Resistance", 10, 5, [["elemental_res", 3]]],
    "defensive-7": ["Wind Resistance", 10, 5, [["elemental_res", 4]]],
    "defensive-8": ["Ice Resistance", 10, 5, [["elemental_res", 5]]],
    "defensive-9": ["Shadow Resistance", 10, 5, [["elemental_res", 6]]],
    "defensive-10": ["Light Resistance", 10, 5, [["elemental_res", 7]]],
    "defensive-11": ["Celestial Resistance", 10, 5, [["elemental_res", 8]]],
    "defensive-12": ["Hybrid Resistance (Eclipse)", 8, 3, [["special_res", "Eclipse"]]],
    "defensive-13": ["Hybrid Resistance (Horizon)", 8, 3, [["special_res", "Horizon"]]],
    "defensive-14": ["Hybrid Resistance (Frostfire)", 8, 3, [["special_res", "Frostfire"]]],
    "defensive-15": ["Hybrid Resistance (Storms)", 8, 3, [["special_res", "Storms"]]],
    "defensive-16": ["Omni Resistance", 5, 2, [["all_elemental_res", -1]]],
    "defensive-17": ["Recovery", 1, 2, [["recovery", -1]]],
    "defensive-18": ["Block Rate", 2, 3, [["block", -1]]],
    "defensive-19": ["Dodge Rate", 1, 3, [["dodge", -1]]],
    "defensive-20": ["Hybrid Resistance (Chaos)", 5, 5, [["special_res", "Chaos"]]],
    "defensive-21": ["Hybrid Resistance (Holy)", 5, 5, [["special_res", "Holy"]]]}
shared_unique_rolls = {
    "unique-0-s": ["Attack Speed", 5, 50, [["attack_speed", -1]]],
    "unique-1-s": ["Critical Strike Chance", 20, 100, [["trigger_rate", "Critical"]]],
    "unique-2-s": ["Critical Strike Multiplier", 25, 100, [["critical_mult", -1]]],
    "unique-3-s": ["NEED TO CHANGE", 0, 50, [["all_elemental_mult", -1]]],
    "unique-4-s": ["Class Mastery Bonus", 3, 50, [["class_multiplier", -1]]],
    "unique-5-s": ["Human Bane", 20, 200, [["banes", 5]]]}
weapon_unique_rolls = {
    "unique-0-w": ["X% Chance to trigger Bloom on hit", 5, 1, [["trigger_rate", "Bloom"]]],
    "unique-1-w": ["X% Less Non-Fire, X% More Fire Damage", 12, 10, [["elemental_conversion", 0]]],
    "unique-2-w": ["X% Less Non-Water, X% More Water Damage", 12, 10, [["elemental_conversion", 1]]],
    "unique-3-w": ["X% Less Non-Lightning, X% More Lightning Damage", 12, 10, [["elemental_conversion", 2]]],
    "unique-4-w": ["X% Less Non-Earth, X% More Earth Damage", 12, 10, [["elemental_conversion", 3]]],
    "unique-5-w": ["X% Less Non-Wind, X% More Wind Damage", 12, 10, [["elemental_conversion", 4]]],
    "unique-6-w": ["X% Less Non-Ice, X% More Ice Damage", 12, 10, [["elemental_conversion", 5]]],
    "unique-7-w": ["X% Less Non-Shadow, X% More Shadow Damage", 12, 10, [["elemental_conversion", 6]]],
    "unique-8-w": ["X% Less Non-Light, X% More Light Damage", 12, 10, [["elemental_conversion", 7]]],
    "unique-9-w": ["X% Less Non-Celestial, X% More Celestial Damage", 12, 10, [["elemental_conversion", 8]]],
    "unique-10-w": ["X% Less Non-Eclipse, X% More Eclipse Damage", 10, 5, [["elemental_conversion", (6, 7)]]],
    "unique-11-w": ["X% Less Non-Horizon, X% More Horizon Damage", 10, 5, [["elemental_conversion", (3, 4)]]],
    "unique-12-w": ["X% Less Non-Frostfire, X% More Frostfire Damage", 10, 5, [["elemental_conversion", (0, 5)]]],
    "unique-13-w": ["X% Less Non-Storm, X% More Storm Damage", 10, 5, [["elemental_conversion", (1, 2)]]],
    "unique-14-w": ["X% Less Non-Chaos, X% More Chaos Damage", 8, 5, [["elemental_conversion", (0, 2, 3, 6)]]],
    "unique-15-w": ["X% Less Non-Holy, X% More Holy Damage", 8, 5, [["elemental_conversion", (1, 4, 5, 7)]]]}
armour_unique_rolls = {
    "unique-0-a": ["Gain X% Elemental Damage per Matching Resistance", 1, 5, [["unique_conversion", 0]]],
    "unique-1-a": ["Convert X% Max HP to 1% Final Damage per 100 HP", 1, 5, [["unique_conversion", 1]]],
    "unique-2-a": ["Block Rate", 4, 10, [["block", -1]]],
    "unique-3-a": ["Dodge Rate", 2, 10, [["dodge", -1]]],
    "unique-4-a": ["Gain X% Final Damage per 1% damage mitigation", 1, 5, [["unique_conversion", 3]]]}
accessory_unique_rolls = {
    "unique-0-y": ["Hyperbleed Rate", 2, 15, [["trigger_rate", "Hyperbleed"]]],
    "unique-1-y": ["Omega Critical Rate", 2, 15, [["trigger_rate", "Omega"]]],
    "unique-2-y": ["Fractal Rate", 2, 15, [["trigger_rate", "Fractal"]]],
    "unique-3-y": ["Time Lock Rate", 2, 15, [["trigger_rate", "Temporal"]]],
    "unique-4-y": ["Fortress Bane", 25, 10, [["banes", 0]]],
    "unique-5-y": ["Dragon Bane", 25, 10, [["banes", 1]]],
    "unique-6-y": ["Demon Bane", 25, 10, [["banes", 2]]],
    "unique-7-y": ["Paragon Bane", 25, 10, [["banes", 3]]],
    "unique-8-y": ["Arbiter Bane", 25, 10, [["banes", 4]]],
    "unique-9-y": ["Class Mastery Bonus X%. Class Mastery is inverted", 5, 5, [["unique_conversion", 2]]],
    "unique-10-y": ["X% Singularity Damage, Penetration, and Curse", 5, 5,
                    [["singularity_mult", -1], ["singularity_pen", -1], ["singularity_curse", -1]]]}
unique_skill_rolls = {}
for roll_idx, (class_name, skills) in enumerate(gli.skill_names_dict.items()):
    for skill_idx, skill_name in enumerate(skills):
        key = f"unique-{skill_idx}-{class_name}"
        unique_skill_rolls[key] = [f"{skill_name} Damage", 10, 1, [["skill_damage_bonus", skill_idx]]]
unique_rolls = {
    "s": [shared_unique_rolls, sum(weighting for _, _, weighting, _ in shared_unique_rolls.values())],
    "w": [weapon_unique_rolls, sum(weighting for _, _, weighting, _ in weapon_unique_rolls.values())],
    "a": [armour_unique_rolls, sum(weighting for _, _, weighting, _ in armour_unique_rolls.values())],
    "y": [accessory_unique_rolls, sum(weighting for _, _, weighting, _ in accessory_unique_rolls.values())],
    "SKILL": [unique_skill_rolls, sum(weighting for _, _, weighting, _ in unique_skill_rolls.values())]}
item_roll_master_dict = {
    "damage": [damage_rolls, sum(weighting for _, _, weighting, _ in damage_rolls.values())],
    "penetration": [penetration_rolls, sum(weighting for _, _, weighting, _ in penetration_rolls.values())],
    "curse": [curse_rolls, sum(weighting for _, _, weighting, _ in curse_rolls.values())],
    "defensive": [defensive_rolls, sum(weighting for _, _, weighting, _ in defensive_rolls.values())],
    "unique": unique_rolls}
valid_rolls = [key for dict_obj in [
    damage_rolls, penetration_rolls, curse_rolls, defensive_rolls, weapon_unique_rolls,
    armour_unique_rolls, accessory_unique_rolls, shared_unique_rolls] for key in dict_obj.keys()]

cost_list = [2, 3, 6, 10, 15, 25]
NPC_name = "Vexia, The Scribe"


class SelectRollsView(discord.ui.View):
    def __init__(self, player_obj, selected_item):
        super().__init__()
        self.player_obj = player_obj
        self.selected_item = selected_item
        self.embed, self.new_view = None, None
        self.count_view = discord.ui.Select(
            placeholder="Select Number of Rolls", min_values=1, max_values=1,
            options=[discord.SelectOption(label=f"{str(i)} Rolls", description=f"Token Cost: {cost_list[i - 1]:,}",
                                          value=str(i)) for i in range(1, 7)])
        self.count_view.callback = self.count_callback
        self.add_item(self.count_view)

    async def count_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        roll_count = int(interaction.data['values'][0])
        self.embed = discord.Embed(title=NPC_name, description="Select a damage skill. (1st Selection)",
                                   color=discord.Color.blue())
        self.new_view = SkillSelectView(self.player_obj, self.selected_item, roll_count, 1, [])
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class SkillSelectView(discord.ui.View):
    def __init__(self, player_obj, selected_item, total_rolls, roll_num, selected_skills):
        super().__init__()
        self.player_obj, self.selected_item = player_obj, selected_item
        self.total_rolls, self.roll_num = total_rolls, roll_num
        self.skills = selected_skills
        self.embed, self.new_view = None, None
        roll_structure = roll_structure_dict[self.selected_item.item_type]
        roll_type = roll_structure[self.roll_num - 1]
        if roll_type == "unique":
            roll_list, _ = handle_unique(self.selected_item, player_obj.player_class)
        else:
            roll_list = item_roll_master_dict[roll_type][0]
        options = [discord.SelectOption(label=roll[1][0], description=f"Weighting: {roll[1][2]}", value=roll[0])
                   for roll in roll_list.items() if roll[0] not in self.skills]
        self.skill_view = discord.ui.Select(placeholder=f"Select Skill for Roll {self.roll_num}",
                                            min_values=1, max_values=1, options=options)
        self.skill_view.callback = self.skill_callback
        self.add_item(self.skill_view)

    async def skill_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        selected_skill = str(interaction.data['values'][0])
        self.skills.append(selected_skill)
        if (self.roll_num + 1) <= self.total_rolls:
            # Load the next view for the next roll
            npc_comment = f"I really haven't got all day you know. (Selection: {self.roll_num + 1})\n"
            for roll_id in self.skills:
                current_roll = ItemRoll(f"1-{roll_id}")
                npc_comment += f"{current_roll.roll_name}\n"
            self.embed = sm.easy_embed("blue", NPC_name, npc_comment)
            self.new_view = SkillSelectView(self.player_obj, self.selected_item,
                                            self.total_rolls, self.roll_num + 1, self.skills)
        else:
            # This is the last roll, display the summary
            npc_comment, skill_display = "Is this really all you wanted?\n", ""
            for roll_id in self.skills:
                temp_id = f"1-{roll_id}"
                current_roll = ItemRoll(temp_id)
                skill_display += f"{current_roll.roll_name}\n"
                if current_roll.roll_code == "unique-0-y":
                    npc_comment = "Oho, you have impeccable taste.\n"
            token_obj = inventory.BasicItem("Token4")
            cost_msg = await sm.cost_embed(self.player_obj, token_obj, cost_list[self.total_rolls - 1])
            self.embed = sm.easy_embed("green", NPC_name, f"{npc_comment}{skill_display}\n{cost_msg}")
            self.new_view = SkillPurchaseView(self.player_obj, self.selected_item, self.total_rolls, self.skills, skill_display)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class SkillPurchaseView(discord.ui.View):
    def __init__(self, player_obj, selected_item, total_rolls, selected_skills, skill_display):
        super().__init__()
        self.player_obj, self.selected_item = player_obj, selected_item
        self.total_rolls, self.selected_skills, self.skill_display = total_rolls, selected_skills, skill_display
        self.embed = None

    @discord.ui.button(label="Inscribe", style=discord.ButtonStyle.green)
    async def inscribe_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=None)
            return
        token_obj, custom_cost = inventory.BasicItem("Token4"), cost_list[self.total_rolls - 1]
        # Display the cost failed message. Reload the same view.
        cost_msg, can_afford = await sm.cost_embed(self.player_obj, token_obj, cost_list[self.total_rolls - 1])
        if not can_afford:
            npc_comment = "If you really want this then you'd better provide a sufficient offering."
            embed_msg = sm.easy_embed("green", NPC_name, f"{npc_comment}{self.skill_display}\n{cost_msg}")
            current_stock = await inventory.check_stock(self.player_obj, token_obj.item_id)
            stock_msg = sm.get_stock_msg(token_obj, current_stock, custom_cost)
            embed_msg.add_field(name="", value=stock_msg, inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=self)
            return
        # Pay the cost. Reload the item data.
        await inventory.update_stock(self.player_obj, token_obj.item_id, (custom_cost * -1))
        reload_item = await inventory.read_custom_item(self.selected_item.item_id)
        new_roll_list, roll_tier_list = [], []
        # Proxy the number of rolls. This is required.
        temp_num_rolls = reload_item.item_num_rolls
        for roll_index in range(max(temp_num_rolls, self.total_rolls)):
            # Log the tiers from the original rolls.
            temp_tier = 1
            if (roll_index + 1) <= temp_num_rolls:
                current_roll = ItemRoll(reload_item.roll_values[roll_index])
                temp_tier = current_roll.roll_tier
            roll_tier_list.append(temp_tier)
            # Build a list of the new roll ids.
            if roll_index + 1 <= self.total_rolls:
                new_roll = f"1-{self.selected_skills[roll_index]}"
                new_roll_list.append(new_roll)
        # Add all the new selected and unselected rolls. Compare the Proxy after updating the value.
        reload_item.roll_values = new_roll_list
        reload_item.item_num_rolls = self.total_rolls
        if temp_num_rolls > self.total_rolls:
            add_roll(reload_item, (temp_num_rolls - self.total_rolls))
        # Set all the roll tiers
        for idx in range(reload_item.item_num_rolls):
            unassigned_roll = reload_item.roll_values[idx][1:]
            reload_item.roll_values[idx] = f"{roll_tier_list[idx]}{unassigned_roll}"
        # Save the item.
        await reload_item.update_stored_item()
        self.embed = await reload_item.create_citem_embed()
        await interaction.response.edit_message(embed=self.embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        cancel_embed = sm.easy_embed("red", NPC_name, "Come back when you've made up your mind.")
        await interaction.response.edit_message(embed=cancellation_embed, view=None)


class ItemRoll:
    def __init__(self, roll_id):
        # Initialize values
        self.roll_id = roll_id
        roll_details = roll_id.split("-")
        self.roll_tier = int(roll_details[0])
        self.roll_icon = f"{gli.augment_icons[self.roll_tier - 1]}"
        self.roll_category, self.roll_code = roll_details[1], f"{roll_details[1]}-{roll_details[2]}"
        self.roll_value, self.roll_msg = 0, ""
        # Adjust specific values
        roll_adjust = 0.01 * self.roll_tier
        if self.roll_category != "unique":
            category_dict = item_roll_master_dict[self.roll_category]
            current = category_dict[0]
            current_roll = current[self.roll_code]
            self.roll_value = current_roll[1] * roll_adjust
            self.roll_msg, self.roll_name = f"{current_roll[0]} {int(round(self.roll_value * 100))}%", current_roll[0]
            return
        # Handle unique roll
        self.roll_code += f"-{roll_details[3]}"
        current = unique_skill_rolls if roll_details[3] in gli.class_names else unique_rolls[roll_details[3]][0]
        current_roll = current[self.roll_code]
        self.roll_value = current_roll[1] * roll_adjust
        temp_msg = f"{current_roll[0]}"
        self.roll_msg = f"{temp_msg} {int(round(self.roll_value * 100))}%"
        if "X" in temp_msg:
            self.roll_msg = temp_msg.replace("X", str(int(round(self.roll_value * 100))))
        self.roll_name = current_roll[0]


def display_rolls(selected_item, roll_change_list=None):
    item_rolls_msg = ""
    for roll_index, roll_information in enumerate(selected_item.roll_values):
        current_roll = ItemRoll(roll_information)
        item_rolls_msg += f'\n{current_roll.roll_icon} {current_roll.roll_msg}'
        if roll_change_list is not None:
            if roll_change_list[roll_index]:
                item_rolls_msg += " [Transferred]"
    return item_rolls_msg


def add_roll(selected_item, num_rolls):
    for _ in range(num_rolls):
        # Initialize variables.
        exclusions_list, exclusions_weighting = [], []
        new_roll_type = roll_structure_dict[selected_item.item_type][selected_item.item_num_rolls]
        # Handle "unique" method
        if new_roll_type == "unique":
            roll_list, total_weighting = handle_unique(selected_item)
        else:
            roll_list = item_roll_master_dict[new_roll_type][0]
            total_weighting = item_roll_master_dict[new_roll_type][1]
        # Build the list of available options from the exclusions.
        for roll_id in selected_item.roll_values:
            current_roll = ItemRoll(roll_id)
            if current_roll.roll_category == new_roll_type:
                exclusions_list.append(current_roll.roll_code)
                roll_weighting = roll_list[current_roll.roll_code][2]
                exclusions_weighting.append(roll_weighting)
        available_rolls = [roll for roll in roll_list if roll not in exclusions_list]
        # Select and set a new roll.
        selected_roll_code = select_roll(total_weighting, exclusions_weighting, available_rolls, roll_list)
        roll_tier = 1
        if "D" in selected_item.item_type:
            roll_tier = selected_item.item_tier
        new_roll_id = f"{roll_tier}-{selected_roll_code}"
        selected_item.roll_values.append(new_roll_id)
        selected_item.item_num_rolls += 1


def reroll_roll(selected_item, method_type):
    # Handle full reroll
    if method_type == "all":
        tier_list = [ItemRoll(roll_id).roll_tier for roll_id in selected_item.roll_values]
        selected_item.item_num_rolls, selected_item.roll_values = 0, []
        add_roll(selected_item, 6)
        selected_item.roll_values = [f"{tier_list[i]}-{ItemRoll(roll_id).roll_code}"
                                     for i, roll_id in enumerate(selected_item.roll_values)]
        return
    # Handle single reroll
    method = random.choice(roll_structure_dict[selected_item.item_type]) if method_type == "any" else method_type
    exclusions_list, exclusions_weighting = [], []
    max_count = roll_structure_dict[selected_item.item_type].count(method)
    target_count = random.randint(1, max_count)
    # Determine the roll list and total weighting based on method
    if method == "unique":
        roll_list, total_weighting = handle_unique(selected_item)
    else:
        roll_list, total_weighting = item_roll_master_dict[method][0], item_roll_master_dict[method][1]
    # Build the list of exclusions and identify the roll to be replaced
    for roll_index, roll_id in enumerate(selected_item.roll_values):
        current_roll = ItemRoll(roll_id)
        if current_roll.roll_category != method:
            continue
        exclusions_list.append(current_roll.roll_code)
        roll_weighting = roll_list[current_roll.roll_code][2]
        exclusions_weighting.append(roll_weighting)
        if len(exclusions_list) == target_count:
            original_roll_tier, original_roll_location = current_roll.roll_tier, roll_index
    available_rolls = [roll for roll in roll_list if roll not in exclusions_list]
    # Select and set a new roll.
    selected_roll_code = select_roll(total_weighting, exclusions_weighting, available_rolls, roll_list)
    new_roll_id = f"{original_roll_tier}-{selected_roll_code}"
    selected_item.roll_values[original_roll_location] = new_roll_id


def handle_unique(selected_item, specific_class=None):
    # Determine the unique rolls to use.
    shared_roll_dict = {"W": "w", "A": "a", "V": "a", "Y": "y", "G": "y", "C": "y"}
    specific_type = shared_roll_dict[selected_item.item_type]
    selected_unique_type = ["s", specific_type]
    # Combine the data.
    combined_dict = {}
    combined_dict.update(unique_rolls[selected_unique_type[0]][0])
    combined_dict.update(unique_rolls[selected_unique_type[1]][0])
    combined_weighting = unique_rolls[selected_unique_type[0]][1] + unique_rolls[selected_unique_type[1]][1]
    if specific_type == "y":
        temp_list = unique_rolls["SKILL"][0]
        if specific_class is not None:
            temp_list = {code: value for code, value in temp_list.items() if code.endswith(specific_class)}
        combined_dict.update(temp_list)
        combined_weighting += sum(weighting for _, _, weighting, _ in temp_list.values())
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
    # check if the item has no rolls.
    if selected_item.item_num_rolls == 0:
        return aug_total
    # Calculate the number of augments
    for roll in selected_item.roll_values:
        current_roll = ItemRoll(roll)
        aug_total += current_roll.roll_tier
    return aug_total


def add_augment(selected_item, method="default"):
    rolls_copy = selected_item.roll_values.copy()
    if method in ["All", "ReduceAll"]:
        change = 1 if method == "All" else -1
        for idx, roll in enumerate(rolls_copy):
            current_roll = ItemRoll(roll)
            selected_item.roll_values[idx] = str(current_roll.roll_tier + change) + selected_item.roll_values[idx][1:]
        return
    random.shuffle(rolls_copy)
    selected_id, selected_tier = "", 0
    # Check each roll for eligibility in a random order.
    for roll in rolls_copy:
        current_roll = ItemRoll(roll)
        selected_tier = current_roll.roll_tier
        if current_roll.roll_tier < selected_item.item_tier:
            selected_id = roll
            break
    # If a roll was selected then upgrade the tier.
    if selected_id != "":
        roll_location = selected_item.roll_values.index(selected_id)
        selected_item.roll_values[roll_location] = str(selected_tier + 1) + selected_item.roll_values[roll_location][1:]


async def assign_gem_values(player_obj, e_item):
    gem_id = e_item.item_inlaid_gem_id
    if gem_id != 0:
        e_gem = await inventory.read_custom_item(gem_id)
        player_obj.player_damage_min += e_gem.item_damage_min
        player_obj.player_damage_max += e_gem.item_damage_max
        points_value = int(inventory.gem_point_dict[e_gem.item_tier])
        player_obj.gear_points[int(e_gem.item_bonus_stat)] += points_value
        await assign_roll_values(player_obj, e_gem)


async def assign_roll_values(player_obj, equipped_item):
    if equipped_item.item_type == "R":
        await ring.assign_ring_values(player_obj, equipped_item)
        return
    for roll_id in equipped_item.roll_values:
        current_roll = ItemRoll(roll_id)
        # Locate the roll information.
        if current_roll.roll_category == "unique":
            roll_list, _ = handle_unique(equipped_item)
            roll_data = roll_list[current_roll.roll_code][3]
        else:
            roll_data = item_roll_master_dict[current_roll.roll_category][0][current_roll.roll_code][3]
        # Check for exception rolls that require special handling.
        if not handle_roll_exceptions(player_obj, current_roll, roll_data):
            # Update all the attributes associated with the roll.
            for attribute_info in roll_data:
                attribute_name, attribute_position = attribute_info
                if attribute_position == -1:
                    setattr(player_obj, attribute_name, getattr(player_obj, attribute_name) + current_roll.roll_value)
                else:
                    target_list = getattr(player_obj, attribute_name)
                    target_list[attribute_position] += current_roll.roll_value


def handle_roll_exceptions(player_obj, selected_roll, selected_data):
    if selected_roll.roll_id.endswith(player_obj.player_class):
        return True
    if "elemental_conversion" in selected_data[0]:
        _, attribute_position = selected_data[0]
        player_obj.apply_elemental_conversion(attribute_position, selected_roll.roll_value, selected_roll.roll_value)
        return True
    return False


def assign_item_element_stats(player_obj, equipped_item):
    associated_stats = {
        "A": [player_obj.elemental_res, 0.1], "V": [player_obj.elemental_res, 0.1],
        "Y": [player_obj.elemental_damage, 0.25],
        "G": [player_obj.elemental_pen, 0.15],
        "C": [player_obj.elemental_curse, 0.1]}
    # Assign stats from elements on the item.
    for idz, z in enumerate(equipped_item.item_elements):
        if z == 1 and equipped_item.item_type in associated_stats:
            associated_stats[equipped_item.item_type][0][idz] += associated_stats[equipped_item.item_type][1]
