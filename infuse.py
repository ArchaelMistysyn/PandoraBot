# Forge menu
import discord
from discord.ui import Button, View
import inventory
import loot
import menus
import random
import player
import tarot
import mydb
import pandorabot
import globalitems
import quest
import asyncio
import combat
import bazaar
import itemdata

recipe_dict = {
    "Heavenly Infusion": {
        "Heavenly Ore (Crude)": ["Ore1", 50, "Stone1", 10, 75, "Ore5"],
        "Heavenly Soul (Light)": ["Soul1", 50, "Stone1", 10, 75, "Soul5"],
        "Heavenly Ore (Cosmite)": ["Ore2", 20, "Stone2", 10, 75, "Ore5"],
        "Heavenly Soul (Luminous)": ["Soul2", 20, "Stone2", 10, 75, "Soul5"],
        "Heavenly Ore (Celestite)": ["Ore3", 10, "Stone3", 10, 75, "Ore5"],
        "Heavenly Soul (Lucent)": ["Soul3", 10, "Stone3", 10, 75, "Soul5"],
        "Heavenly Ore (Crystallite)": ["Ore4", 2, "Stone4", 10, 75, "Ore5"],
        "Heavenly Soul (Lustrous)": ["Soul4", 2, "Stone4", 10, 75, "Soul5"],
        "Astral Hammer": ["Hammer1", 1, "Heart1", 1, 90, "Hammer2"]},

    "Elemental Infusion": {
        "Elemental Origin (Fire)": ["OriginZ", 1, "Fae0", 100, 80, "Origin0"],
        "Elemental Origin (Water)": ["OriginZ", 1, "Fae1", 100, 80, "Origin1"],
        "Elemental Origin (Lightning)": ["OriginZ", 1, "Fae2", 100, 80, "Origin2"],
        "Elemental Origin (Earth)": ["OriginZ", 1, "Fae3", 100, 80, "Origin3"],
        "Elemental Origin (Wind)": ["OriginZ", 1, "Fae4", 100, 80, "Origin4"],
        "Elemental Origin (Ice)": ["OriginZ", 1, "Fae5", 100, 80, "Origin5"],
        "Elemental Origin (Shadow)": ["OriginZ", 1, "Fae6", 100, 80, "Origin6"],
        "Elemental Origin (Light)": ["OriginZ", 1, "Fae7", 100, 80, "Origin7"],
        "Elemental Origin (Celestial)": ["OriginZ", 1, "Fae8", 100, 80, "Origin8"]},

    "Fabled Infusion": {
        "Fabled Core": ["Stone5", 25, "Heart1", 1, 90, "Core1"],
        "Fabled Matrix": ["Matrix1", 1, "Core1", 1, 90, "Matrix2"],
        "Fabled Flame": ["Flame1", 1, "Core1", 1, 90, "Flame2"],
        "Fabled Pearl": ["Pearl1", 1, "Core1", 1, 90, "Pearl2"],
        "Fabled Hammer (Star Hammer)": ["Hammer1", 1, "Core1", 1, 90, "Hammer3"],
        "Fabled Hammer (Astral Hammer)": ["Hammer2", 1, "Core1", 1, 90, "Hammer3"],
        "Unrefined Fabled Item (Weapon)": ["Fragment1", 200, "Core1", 5, 100, "Fabled1"],
        "Unrefined Fabled Item (Armour)": ["Fragment2", 100, "Core1", 2, 100, "Fabled2"],
        "Unrefined Fabled Item (Accessory)": ["Fragment3", 100, "Core1", 2, 100, "Fabled3"],
        "Unrefined Fabled Item (Wing)": ["Unrefined1", 50, "Core1", 2, 100, "Fabled4"],
        "Unrefined Fabled Item (Crest)": ["Unrefined3", 50, "Core1", 2, 100, "Fabled5"],
        "Unrefined Fabled Item (Gem)": ["Unrefined2", 25, "Core1", 1, 100, "Fabled6"]},

    "Void Infusion": {
        "Void Core": ["Traces1", 1, "Core1", 1, 90, "Core2"],
        "Void Pearl": ["Traces1", 1, "Pearl2", 1, 90, "Pearl3"],
        "Void Flame": ["Traces1", 1, "Flame2", 1, 90, "Flame3"],
        "Void Origin": ["Traces1", 1, "OriginZ", 1, 90, "OriginV"],
        "Crystallized Void": ["Traces1", 1, "Crystal1", 1, 10, "Crystal2"]},

    "Wish Infusion": {
        "Fragmentized Wish (Weapon)": ["Fragment1", 10, "Stone4", 1, 100, "FragmentM"],
        "Fragmentized Wish (Armour)": ["Fragment2", 10, "Stone4", 1, 100, "FragmentM"],
        "Fragmentized Wish (Accessory)": ["Fragment3", 10, "Stone4", 1, 100, "FragmentM"],
        "Crystallized Wish": ["FragmentM", 50, "Stone5", 10, 100, "Crystal1"],
        "Wish Core": ["Crystal1", 5, "Core1", 1, 50, "Core3"],
        "Unrefined Wish Item (Gem)": ["Unrefined2", 50, "Crystal1", 1, 100, "Unrefined4"],
        "Unrefined Wish Item (Weapon)": ["Crystal1", 5, "Heart1", 10, 100, "Unrefined5"]},

    "Miracle Infusion": {
        "Miracle Origin": ["Heart2", 1, "OriginZ", 1, 100, "OriginM"],
        "Miracle Ore": ["Crystal1", 1, "Ore5", 2, 100, "Ore6"],
        "Miracle Soul": ["Crystal1", 1, "Soul5", 2, 100, "Soul6"],
        "Miracle Flame": ["FragmentM", 5, "Flame1", 20, 100, "Flame4"],
        "Miracle Matrix": ["Crystal1", 1, "Matrix1", 50, 100, "Matrix3"],
        "Miracle Pearl": ["FragmentM", 5, "Pearl1", 1, 100, "Pearl4"],
        "Miracle Hammer": ["FragmentM", 10, "Hammer1", 1, 100, "Hammer4"],
        "Miracle Heart": ["Crystal1", 1, "Heart1", 1, 100, "Heart2"]},

    "Lotus Infusion": {
        "Lotus of Miracles": ["Heart2", 99, "FragmentM", 99, 99, "Lotus2"]}
}


class RecipeObject:
    def __init__(self, category, recipe_name):
        recipe_info = recipe_dict[category][recipe_name]

        self.recipe_name = recipe_name
        self.cost_item_1 = inventory.BasicItem(recipe_info[0])
        self.cost_qty_1 = recipe_info[1]
        self.cost_item_2 = inventory.BasicItem(recipe_info[2])
        self.cost_qty_2 = recipe_info[3]
        self.success_rate = recipe_info[4]
        self.outcome_item = inventory.BasicItem(recipe_info[5])

    def create_cost_embed(self, player_object):
        stock_1 = inventory.check_stock(player_object, self.cost_item_1.item_id)
        stock_2 = inventory.check_stock(player_object, self.cost_item_2.item_id)
        cost_title = f"{self.recipe_name} Infusion Cost"
        cost_info = f"{self.cost_item_1.item_emoji} {self.cost_item_1.item_name}: {stock_1} / {self.cost_qty_1}"
        cost_info += f"\n{self.cost_item_2.item_emoji} {self.cost_item_2.item_name}: {stock_2} / {self.cost_qty_2}"
        cost_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=cost_title, description=cost_info)
        return cost_embed

    def can_afford(self, player_object, num_crafts):
        can_proceed = False
        stock_1 = inventory.check_stock(player_object, self.cost_item_1.item_id)
        stock_2 = inventory.check_stock(player_object, self.cost_item_2.item_id)
        if stock_1 >= num_crafts * self.cost_qty_1 and stock_2 >= self.cost_qty_2:
            can_proceed = True
        return can_proceed

    def perform_infusion(self, player_object, num_crafts):
        result = 0
        total_cost_1 = 0 - (num_crafts * self.cost_qty_1)
        total_cost_2 = 0 - (num_crafts * self.cost_qty_2)
        inventory.update_stock(player_object, self.cost_item_1.item_id, total_cost_1)
        inventory.update_stock(player_object, self.cost_item_2.item_id, total_cost_2)
        print(f"{player_object.player_username}: infusion paid")
        for x in range(num_crafts):
            random_attempt = random.randint(1, 100)
            print(f"{player_object.player_username}: infusion roll: {random_attempt} / {self.success_rate}")
            if random_attempt <= self.success_rate:
                inventory.update_stock(player_object, self.outcome_item.item_id, 1)
                result += 1
        return result


class InfuseView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.selected_item = None
        self.player_object = player_object
        self.value = None

        # Build the option menu dynamically based on recipe categories.
        select_options = [
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label=category,
                description=f"Creates {category.lower()} items."
            ) for category in recipe_dict
        ]
        self.select_menu = discord.ui.Select(
            placeholder="What kind of infusion do you want to perform?",
            min_values=1, max_values=1, options=select_options
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.name == self.player_object.player_name:
                selected_category = interaction.data['values'][0]
                embed_msg = discord.Embed(
                    colour=discord.Colour.magenta(),
                    title="Cloaked Alchemist, Sangam",
                    description="Alright, what do you need?"
                )
                new_view = SelectRecipeView(self.player_object, selected_category)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class SelectRecipeView(discord.ui.View):
    def __init__(self, player_object, category):
        super().__init__(timeout=None)
        self.player_object = player_object
        self.category = category

        # Build the option menu dynamically based on the category's recipes.
        category_recipes = recipe_dict.get(self.category, {})
        options_data_list = []
        for recipe_name, recipe in category_recipes.items():
            result_item = inventory.BasicItem(recipe[5])
            options_data_list.append([recipe_name, recipe[4], result_item.item_emoji])
        select_options = [
            discord.SelectOption(
                emoji=result_emoji, label=recipe_name, description=f"Success Rate {success_rate}%", value=recipe_name
            ) for recipe_name, success_rate, result_emoji in options_data_list
        ]
        self.select_menu = discord.ui.Select(
            placeholder=f"Select the {self.category.lower()} infusion recipe.",
            min_values=1, max_values=1, options=select_options
        )
        self.select_menu.callback = self.recipe_callback
        self.add_item(self.select_menu)

    async def recipe_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                selected_option = interaction.data['values'][0]
                recipe_object = RecipeObject(self.category, selected_option)
                embed_msg = recipe_object.create_cost_embed(reload_player)
                new_view = CraftView(reload_player, recipe_object)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class CraftView(discord.ui.View):
    def __init__(self, player_user, recipe_object):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.recipe_object = recipe_object
        self.is_paid = False

    def run_button(self, selected_qty):
        reload_player = player.get_player_by_id(self.player_user.player_id)
        embed_title = "Cloaked Alchemist, Sangam"
        if self.recipe_object.can_afford(reload_player, selected_qty):
            if not self.is_paid:
                result = self.recipe_object.perform_infusion(reload_player, selected_qty)
                self.is_paid = True
            if result > 0:
                outcome_item = self.recipe_object.outcome_item
                embed_description = "Infusion Successful!"
                embed_description += f"\n{outcome_item.item_emoji} {result}x {outcome_item.item_name}"
            else:
                embed_description = "Infusion Failed! I guess it's just not your day today."
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title=embed_title,
                                      description=embed_description)
            new_view = CraftView(reload_player, self.recipe_object)
        else:
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="Not Enough Materials!",
                                      description="Please come back when you have more materials.")
            new_view = InfuseView(reload_player)
        return embed_msg, new_view

    @discord.ui.button(label="Infuse 1", style=discord.ButtonStyle.success, emoji="1️⃣")
    async def infuse_1(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, new_view = self.run_button(1)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Infuse 5", style=discord.ButtonStyle.success, emoji="5️⃣")
    async def infuse_5(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, new_view = self.run_button(5)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Infuse 10", style=discord.ButtonStyle.success, emoji="🔟")
    async def infuse_10(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, new_view = self.run_button(10)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Black Market",
                                          description="Everything has a price.")
                new_view = InfuseView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)
