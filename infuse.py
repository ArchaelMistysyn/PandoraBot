# General imports
import discord
from discord.ui import Button, View
import random

# Data imports
import globalitems

# Core imports
from pandoradb import run_query as rq
import player
import inventory

recipe_dict = {
    "Heavenly Infusion": {
        "Heavenly Ore (Crude)": [("Ore1", 50), ("Stone1", 10), 75, "Ore5"],
        "Heavenly Ore (Cosmite)": [("Ore2", 20), ("Stone2", 10), 75, "Ore5"],
        "Heavenly Ore (Celestite)": [("Ore3", 10), ("Stone3", 10), 75, "Ore5"],
        "Heavenly Ore (Crystallite)": [("Ore4", 2), ("Stone4", 10), 75, "Ore5"]},
    "Elemental Infusion": {
        "Elemental Origin (Fire)": [("OriginZ", 1), ("Fae0", 500), 80, "Origin0"],
        "Elemental Origin (Water)": [("OriginZ", 1), ("Fae1", 500), 80, "Origin1"],
        "Elemental Origin (Lightning)": [("OriginZ", 1), ("Fae2", 500), 80, "Origin2"],
        "Elemental Origin (Earth)": [("OriginZ", 1), ("Fae3", 500), 80, "Origin3"],
        "Elemental Origin (Wind)": [("OriginZ", 1), ("Fae4", 500), 80, "Origin4"],
        "Elemental Origin (Ice)": [("OriginZ", 1), ("Fae5", 500), 80, "Origin5"],
        "Elemental Origin (Shadow)": [("OriginZ", 1), ("Fae6", 500), 80, "Origin6"],
        "Elemental Origin (Light)": [("OriginZ", 1), ("Fae7", 500), 80, "Origin7"],
        "Elemental Origin (Celestial)": [("OriginZ", 1), ("Fae8", 500), 80, "Origin8"]},
    "Void Infusion": {
        "Void Core": [("Fragment1", 10), ("Heart1", 1), 95, "Core1"],
        "Fragmentized Void": [("Scrap", 5), ("Stone5", 1), 100, "Fragment1"],
        "Unrefined Void Item (Weapon)": [("Crystal1", 1), ("Core1", 10), 99, "Void1"],
        "Unrefined Void Item (Armour)": [("Scrap", 100), ("Core1", 5), 99, "Void2"],
        "Unrefined Void Item (Vambraces)": [("Unrefined2", 10), ("Core1", 5), 99, "Void3"],
        "Unrefined Void Item (Amulet)": [("Scrap", 100), ("Core1", 5), 99, "Void4"],
        "Unrefined Void Item (Wing)": [("Unrefined1", 10), ("Core1", 5), 99, "Void5"],
        "Unrefined Void Item (Crest)": [("Unrefined3", 10), ("Core1", 5), 99, "Void6"],
        "Crystallized Void": [("Core1", 2), ("Fragment1", 25), 25, "Crystal1"]},
    "Wish Infusion": {
        "Wish Core": [("Core1", 1), ("Fragment2", 10), 95, "Core2"],
        "Fragmentized Wish": [("Scrap", 5), ("Fragment1", 5), 100, "Fragment2"],
        "Radiant Heart": [("Stone5", 1), ("Fragment2", 1), 5, "Heart1"],
        "Crystallized Wish": [("Core2", 2), ("Fragment2", 25), 25, "Crystal2"]},
    "Abyss Infusion": {
        "Abyss Core": [("Core2", 1), ("Fragment3", 20), 95, "Core4"],
        "Fragmentized Abyss": [("Scrap", 5), ("Fragment2", 5), 100, "Fragment3"],
        "Chaos Heart": [("Stone5", 1), ("Fragment3", 1), 5, "Heart2"],
        "Abyss Flame": [("Flame1", 10), ("Heart2", 1), 10, "Flame2"],
        "Crystallized Abyss": [("Core3", 2), ("Fragment3", 25), 25, "Crystal3"]},
    "Divine Infusion": {
        "Divinity Core (Fragment)": [("Core3", 1), ("Fragment4", 20), 95, "Core4"],
        "Divinity Core (Radiant)": [("OriginZ", 1), ("Heart1", 1), 1, "Core4"],
        "Divinity Core (Chaos)": [("OriginZ", 1), ("Heart2", 1), 1, "Core4"],
        "Fragmentized Divinity": [("Scrap", 5), ("Fragment3", 5), 100, "Fragment4"],
        "Crystallized Divinity": [("Core4", 2), ("Fragment4", 25), 25, "Crystal4"],
        "Lotus of Serenity": [("Heart1", 99), ("Fragment2", 99), 99, "Lotus2"],
        "Twin Rings of Divergent Stars": [("DarkStar", 1), ("LightStar", 1), 100, "TwinRings"]},
    "Elemental Ring Infusion": {
        "Elemental Ring of Fire": [("Gemstone1", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Water": [("Gemstone2", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Lightning": [("Gemstone3", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Earth": [("Gemstone4", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Wind": [("Gemstone5", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Ice": [("Gemstone6", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Shadow": [("Gemstone7", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Light": [("Gemstone8", 1), ("Scrap", 100), 100, "4"],
        "Elemental Ring of Celestia": [("Gemstone9", 1), ("Scrap", 100), 100, "4"]},
    "Primordial Ring Infusion": {
        "Ruby Ring of Incineration": [("Gemstone1", 5), ("Gemstone11", 1), 100, "5"],
        "Sapphire Ring of Atlantis": [("Gemstone2", 5), ("Gemstone11", 1), 100, "5"],
        "Topaz Ring of Dancing Thunder": [("Gemstone3", 5), ("Gemstone11", 1), 100, "5"],
        "Agate Ring of Seismic Tremors": [("Gemstone4", 5), ("Gemstone11", 1), 100, "5"],
        "Emerald Ring of Wailing Winds": [("Gemstone5", 5), ("Gemstone11", 1), 100, "5"],
        "Zircon Ring of the Frozen Castle": [("Gemstone6", 5), ("Gemstone11", 1), 100, "5"],
        "Obsidian Ring of Tormented Souls": [("Gemstone7", 5), ("Gemstone11", 1), 100, "5"],
        "Opal Ring of Scintillation": [("Gemstone8", 5), ("Gemstone11", 1), 100, "5"],
        "Amethyst Ring of Shifting Stars": [("Gemstone9", 5), ("Gemstone11", 1), 100, "5"]},
    "Path Ring Infusion": {
        "Invoking Ring of Storms": [("Gemstone1", 5), ("Gemstone3", 5), ("Gemstone11", 2), 100, "6"],
        "Primordial Ring of Frostfire": [("Gemstone2", 5), ("Gemstone6", 5), ("Gemstone11", 2), 100, "6"],
        "Boundary Ring of Horizon": [("Gemstone4", 5), ("Gemstone5", 5), ("Gemstone11", 2), 100, "6"],
        "Hidden Ring of Eclipse": [("Gemstone7", 5), ("Gemstone8", 5), ("Gemstone11", 2), 100, "6"],
        "Cosmic Ring of Stars": [("Gemstone9", 10), ("Gemstone11", 2), 100, "6"],
        "Rainbow Ring of Confluence": [("Gemstone1", 2), ("Gemstone2", 2), ("Gemstone3", 2),
                                       ("Gemstone4", 2), ("Gemstone5", 2), ("Gemstone6", 2),
                                       ("Gemstone7", 2), ("Gemstone8", 2), ("Gemstone9", 2),
                                       ("Gemstone11", 2), 100, "6"],
        "Lonely Ring of Solitude": [("Gemstone0", 20), ("Gemstone11", 1), 100, "6"]},
    "Legendary Ring Infusion": {
        "Dragon's Eye Diamond": [("Gemstone10", 10), ("Gemstone11", 3), 100, "7"],
        "Chromatic Tears": [("Gemstone11", 10), 100, "7"],
        "Bleeding Hearts": [("Heart1", 99), ("Heart2", 99), ("Gemstone11", 3), 100, "7"]},
    "Mythic Ring Infusion": {
        "Stygian Calamity": [("Gemstone12", 1), ("Gemstone11", 5), 100, "8"],
        "Sacred Ring of Divergent Stars": [("TwinRings", 1), ("Gemstone11", 5), 100, "8"]}
}

NPC_name = "Cloaked Alchemist, Sangam"


class RecipeObject:
    def __init__(self, category, recipe_name):
        self.category = category
        self.recipe_name, self.recipe_info = recipe_name, recipe_dict[category][recipe_name]

        # Initialize cost items dynamically
        self.cost_items = []
        self.success_rate = self.recipe_info[-2]
        self.outcome_item = inventory.BasicItem(self.recipe_info[-1]) if "Ring" not in self.category else int(self.recipe_info[-1])
        for item_info in self.recipe_info[:-2]:
            item_id, qty = item_info
            self.cost_items.append((inventory.BasicItem(item_id), qty))

    def create_cost_embed(self, player_obj):
        cost_title = f"{self.recipe_name} Infusion Cost"
        cost_info = ""
        for (item, qty) in self.cost_items:
            stock = inventory.check_stock(player_obj, item.item_id)
            cost_info += f"{item.item_emoji} {item.item_name}: {stock} / {qty}\n"
        cost_info += f"Success Rate: {self.success_rate}%"
        cost_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=cost_title, description=cost_info)
        return cost_embed

    def can_afford(self, player_obj, num_crafts):
        for (item, qty) in self.cost_items:
            stock = inventory.check_stock(player_obj, item.item_id)
            if stock < num_crafts * qty:
                return False
        return True

    def perform_infusion(self, player_obj, num_crafts, ring=False):
        result = 0
        # Deduct the cost for each item
        for (item, qty) in self.cost_items:
            total_cost = 0 - (num_crafts * qty)
            inventory.update_stock(player_obj, item.item_id, total_cost)  # This needs to update all at once instead.
        if ring:
            return 1
        # Perform the infusion attempts
        for _ in range(num_crafts):
            if random.randint(1, 100) <= self.success_rate:
                result += 1
        if result > 0:
            inventory.update_stock(player_obj, self.outcome_item.item_id, result)
        return result


class InfuseView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.selected_item, self.value = None, None

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
        if interaction.user.id != self.player_obj.discord_id:
            return
        selected_category = interaction.data['values'][0]
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title=NPC_name, description="Alright, what do you need?")
        new_view = SelectRecipeView(self.player_obj, selected_category)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class SelectRecipeView(discord.ui.View):
    def __init__(self, player_obj, category):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.category = category
        self.embed, self.new_view = None, None

        # Build the option menu dynamically based on the category's recipes.
        category_recipes = recipe_dict.get(self.category, {})
        options_data_list = []
        for recipe_name, recipe in category_recipes.items():
            if "Ring" in self.category:
                option_emoji = "💍"
            else:
                result_item = inventory.BasicItem(recipe[-1])
                option_emoji = result_item.item_emoji
            options_data_list.append([recipe_name, recipe[-2], option_emoji])
        select_options = [
            discord.SelectOption(
                emoji=result_emoji, label=recipe_name, description=f"Success Rate {success_rate}%", value=recipe_name
            ) for recipe_name, success_rate, result_emoji in options_data_list
        ]
        self.select_menu = discord.ui.Select(
            placeholder=f"Select the {self.category.lower()} recipe.",
            min_values=1, max_values=1, options=select_options
        )
        self.select_menu.callback = self.recipe_callback
        self.add_item(self.select_menu)

    async def recipe_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        await self.player_obj.reload_player()
        selected_option = interaction.data['values'][0]
        recipe_object = RecipeObject(self.category, selected_option)
        self.embed = recipe_object.create_cost_embed(self.player_obj)
        self.new_view = CraftView(self.player_obj, recipe_object)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class CraftView(discord.ui.View):
    def __init__(self, player_user, recipe_object):
        super().__init__(timeout=None)
        self.player_user, self.recipe_object = player_user, recipe_object
        self.embed_msg, self.new_view = None, None
        if "Ring" in self.recipe_object.category:
            self.infuse_1.label = "Infuse Ring"
            self.infuse_1.emoji = "💍"
            self.remove_item(self.children[2])
            self.remove_item(self.children[1])

    async def run_button(self, interaction, selected_qty):
        if interaction.user.id != self.player_user.discord_id:
            return
        await self.player_user.reload_player()
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        self.new_view = CraftView(self.player_user, self.recipe_object)
        self.embed_msg = self.recipe_object.create_cost_embed(self.player_user)
        # Handle cannot afford response
        if not self.recipe_object.can_afford(self.player_user, selected_qty):
            self.embed_msg.add_field(name="Not Enough Materials!",
                                     value="Please come back when you have more materials.", inline=False)
            new_view = InfuseView(self.player_user)
            await interaction.response.edit_message(embed=self.embed_msg, view=new_view)
            return
        is_ring = "Ring" in self.recipe_object.category
        result = self.recipe_object.perform_infusion(self.player_user, selected_qty, ring=is_ring)
        # Handle infusion
        if is_ring:
            # Handle ring
            new_ring = inventory.CustomItem(self.player_user.player_id, "R", self.recipe_object.outcome_item)
            new_ring.item_base_type = self.recipe_object.recipe_name
            new_ring.set_item_name()
            inventory.add_custom_item(new_ring)
            self.embed_msg = await new_ring.create_citem_embed()
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        # Handle non-ring failure
        if result == 0:
            header, description = "Infusion Failed!", "I guess it's just not your day today."
            self.embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=NPC_name, description=description)
            self.embed_msg.add_field(name=header, value=description, inline=False)
            self.new_view = CraftView(self.player_user, self.recipe_object)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        # Handle non-ring success
        outcome_item = self.recipe_object.outcome_item
        header, description = "Infusion Successful!", f"\n{outcome_item.item_emoji} {result:,}x {outcome_item.item_name}"
        self.embed_msg.add_field(name=header, value=description, inline=False)
        await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
        return

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
