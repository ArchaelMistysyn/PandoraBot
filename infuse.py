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
        "Heavenly Ore (Cosmite)": ["Ore2", 20, "Stone2", 10, 75, "Ore5"],
        "Heavenly Ore (Celestite)": ["Ore3", 10, "Stone3", 10, 75, "Ore5"],
        "Heavenly Ore (Crystallite)": ["Ore4", 2, "Stone4", 10, 75, "Ore5"]},

    "Elemental Infusion": {
        "Elemental Origin (Fire)": ["OriginZ", 1, "Fae0", 500, 80, "Origin0"],
        "Elemental Origin (Water)": ["OriginZ", 1, "Fae1", 500, 80, "Origin1"],
        "Elemental Origin (Lightning)": ["OriginZ", 1, "Fae2", 500, 80, "Origin2"],
        "Elemental Origin (Earth)": ["OriginZ", 1, "Fae3", 500, 80, "Origin3"],
        "Elemental Origin (Wind)": ["OriginZ", 1, "Fae4", 500, 80, "Origin4"],
        "Elemental Origin (Ice)": ["OriginZ", 1, "Fae5", 500, 80, "Origin5"],
        "Elemental Origin (Shadow)": ["OriginZ", 1, "Fae6", 500, 80, "Origin6"],
        "Elemental Origin (Light)": ["OriginZ", 1, "Fae7", 500, 80, "Origin7"],
        "Elemental Origin (Celestial)": ["OriginZ", 1, "Fae8", 500, 80, "Origin8"]},

    "Void Infusion": {
        "Void Core": ["Fragment1", 10, "Heart1", 1, 95, "Core1"],
        "Fragmentized Void": ["Scrap", 5, "Stone5", 1, 100, "Fragment1"],
        "Unrefined Void Item (Weapon)": ["Crystal1", 1, "Core1", 10, 99, "Void1"],
        "Unrefined Void Item (Armour)": ["Scrap", 100, "Core1", 5, 99, "Void2"],
        "Unrefined Void Item (Vambraces)": ["Unrefined2", 10, "Core1", 5, 99, "Void3"],
        "Unrefined Void Item (Amulet)": ["Scrap", 100, "Core1", 5, 99, "Void4"],
        "Unrefined Void Item (Wing)": ["Unrefined1", 10, "Core1", 5, 99, "Void5"],
        "Unrefined Void Item (Crest)": ["Unrefined3", 10, "Core1", 5, 99, "Void6"],
        "Crystallized Void": ["Core1", 2, "Fragment1", 25, 25, "Crystal1"]},

    "Wish Infusion": {
        "Wish Core": ["Core1", 1, "Fragment2", 10, 95, "Core2"],
        "Fragmentized Wish": ["Scrap", 5, "Fragment1", 5, 100, "Fragment2"],
        "Radiant Heart": ["Stone5", 1, "Fragment2", 1, 5, "Heart1"],
        "Crystallized Wish": ["Core2", 2, "Fragment2", 25, 25, "Crystal2"]},

    "Abyss Infusion": {
        "Abyss Core": ["Core2", 1, "Fragment3", 20, 95, "Core4"],
        "Fragmentized Abyss": ["Scrap", 5, "Fragment2", 5, 100, "Fragment3"],
        "Chaos Heart": ["Stone5", 1, "Fragment3", 1, 5, "Heart2"],
        "Abyss Flame": ["Flame1", 10, "Heart2", 1, 10, "Flame2"],
        "Crystallized Abyss": ["Core3", 2, "Fragment3", 25, 25, "Crystal3"]},

    "Divine Infusion": {
        "Divinity Core (Fragment)": ["Core3", 1, "Fragment4", 20, 95, "Core4"],
        "Divinity Core (Radiant)": ["OriginZ", 1, "Heart1", 1, 1, "Core4"],
        "Divinity Core (Chaos)": ["OriginZ", 1, "Heart2", 1, 1, "Core4"],
        "Fragmentized Divinity": ["Scrap", 5, "Fragment3", 5, 100, "Fragment4"],
        "Crystallized Divinity": ["Core4", 2, "Fragment4", 25, 25, "Crystal4"],
        "Lotus of Serenity": ["Heart1", 99, "Fragment2", 99, 99, "Lotus2"],
        "Twin Rings of Divergent Stars": ["DarkStar", 1, "LightStar", 1, 100, "TwinRings"]}
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

    def create_cost_embed(self, player_obj):
        stock_1 = inventory.check_stock(player_obj, self.cost_item_1.item_id)
        stock_2 = inventory.check_stock(player_obj, self.cost_item_2.item_id)
        cost_title = f"{self.recipe_name} Infusion Cost"
        cost_info = f"{self.cost_item_1.item_emoji} {self.cost_item_1.item_name}: {stock_1} / {self.cost_qty_1}"
        cost_info += f"\n{self.cost_item_2.item_emoji} {self.cost_item_2.item_name}: {stock_2} / {self.cost_qty_2}"
        cost_info += f"\nSuccess Rate: {self.success_rate}%"
        cost_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=cost_title, description=cost_info)
        return cost_embed

    def can_afford(self, player_obj, num_crafts):
        can_proceed = False
        stock_1 = inventory.check_stock(player_obj, self.cost_item_1.item_id)
        stock_2 = inventory.check_stock(player_obj, self.cost_item_2.item_id)
        if stock_1 >= num_crafts * self.cost_qty_1 and stock_2 >= num_crafts * self.cost_qty_2:
            can_proceed = True
        return can_proceed

    def perform_infusion(self, player_obj, num_crafts):
        result = 0
        total_cost_1 = 0 - (num_crafts * self.cost_qty_1)
        total_cost_2 = 0 - (num_crafts * self.cost_qty_2)
        inventory.update_stock(player_obj, self.cost_item_1.item_id, total_cost_1)
        inventory.update_stock(player_obj, self.cost_item_2.item_id, total_cost_2)
        for x in range(num_crafts):
            random_attempt = random.randint(1, 100)
            if random_attempt <= self.success_rate:
                inventory.update_stock(player_obj, self.outcome_item.item_id, 1)
                result += 1
        return result


class InfuseView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__(timeout=None)
        self.selected_item = None
        self.player_obj = player_obj
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
            if interaction.user.id == self.player_obj.discord_id:
                selected_category = interaction.data['values'][0]
                embed_msg = discord.Embed(
                    colour=discord.Colour.magenta(),
                    title="Cloaked Alchemist, Sangam",
                    description="Alright, what do you need?"
                )
                new_view = SelectRecipeView(self.player_obj, selected_category)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class SelectRecipeView(discord.ui.View):
    def __init__(self, player_obj, category):
        super().__init__(timeout=None)
        self.player_obj = player_obj
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
            if interaction.user.id == self.player_obj.discord_id:
                reload_player = player.get_player_by_id(self.player_obj.player_id)
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
        self.embed_msg, self.new_view = None, None

    async def run_button(self, interaction, selected_qty):
        if interaction.user.id != self.player_user.discord_id:
            return
        self.player_user.reload_player()
        embed_title = "Cloaked Alchemist, Sangam"
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        # Handle cannot afford response
        if not self.recipe_object.can_afford(self.player_user, selected_qty):
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title="Not Enough Materials!",
                                      description="Please come back when you have more materials.")
            new_view = InfuseView(self.player_user)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
            return
        # Handle can afford response
        result = self.recipe_object.perform_infusion(self.player_user, selected_qty)
        self.new_view = CraftView(self.player_user, self.recipe_object)
        if result > 0:
            outcome_item = self.recipe_object.outcome_item
            embed_description = f"Infusion Successful!\n{outcome_item.item_emoji} {result:,}x {outcome_item.item_name}"
            self.embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=embed_title, description=embed_description)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        # Handle failure
        embed_description = "Infusion Failed! I guess it's just not your day today."
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=embed_title, description=embed_description)
        new_view = CraftView(self.player_user, self.recipe_object)
        await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)

    @discord.ui.button(label="Infuse 1", style=discord.ButtonStyle.success, emoji="1️⃣")
    async def infuse_1(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_button(interaction, 1)

    @discord.ui.button(label="Infuse 5", style=discord.ButtonStyle.success, emoji="5️⃣")
    async def infuse_5(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_button(interaction, 5)

    @discord.ui.button(label="Infuse 10", style=discord.ButtonStyle.success, emoji="🔟")
    async def infuse_10(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_button(interaction, 10)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title="Black Market", description="Everything has a price.")
        new_view = InfuseView(self.player_user)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)
