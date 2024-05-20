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
    "Heavenly Infusion": {}, "Elemental Infusion": {}, "Core Infusion": {},
    "Void Infusion": {}, "Jewel Infusion": {}, "Skull Infusion": {},
    "Special Infusion": {
        "Radiant Heart": [("Stone5", 1), ("Fragment2", 1), 20, "Heart1"],
        "Chaos Heart": [("Stone5", 1), ("Fragment3", 1), 20, "Heart2"],
        "Abyss Flame": [("Core3", 1), ("Flame1", 10), 80, "Flame2"],
        "Lotus of Serenity": [("Heart1", 99), ("Fragment2", 99), 99, "Lotus2"],
        "Twin Rings of Divergent Stars": [("DarkStar", 1), ("LightStar", 1), 100, "TwinRings"]},
    "Elemental Ring Infusion": {}, "Primordial Signet Infusion": {}, "Path Ring Infusion": {},
    "Legendary Ring Infusion": {
        "Dragon's Eye Diamond": [("Gemstone10", 10), ("Gemstone11", 3), 100, "7"],
        "Chromatic Tears": [("Gemstone11", 10), 100, "7"],
        "Bleeding Hearts": [("Heart1", 99), ("Heart2", 99), ("Gemstone11", 3), 100, "7"],
        "Gambler's Masterpiece": [("Gemstone11", 1), 1, "7"]},
    "Sovereign Ring Infusion": {
        "Stygian Calamity": [("Gemstone12", 1), ("Gemstone11", 5), 100, "8"],
        "Sacred Ring of Divergent Stars": [("TwinRings", 1), ("Gemstone11", 5), 100, "8"],
        "Crown of Skulls": [("Skull4", 1), ("Lotus1", 1), ("Gemstone11", 5), 100, "8"]}
}


def add_recipe(category, name, data_list):
    if category not in recipe_dict:
        recipe_dict[category] = {}
    recipe_dict[category][name] = data_list


# Heavenly Infusion
for idx, (ore, count) in enumerate(zip(['Crude', 'Cosmite', 'Celestite', 'Crystallite'], [50, 20, 10, 2]), start=1):
    add_recipe("Heavenly Infusion", f"Heavenly Ore ({ore})",
               [(f"Ore{idx}", count), (f"Stone{idx}", 5), 75, "Ore5"])

primordial_rings = [("Ruby", "Incineration"), ("Sapphire", "Atlantis"), ("Topaz", "Dancing Thunder"),
                    ("Agate", "Seismic Tremors"), ("Emerald", "Wailing Winds"), ("Zircon", "Frozen Castle"),
                    ("Obsidian", "Tormented Souls"), ("Opal", "Scintillation"), ("Amethyst", "Shifting Stars")]
# Elemental Infusions
for idx, (element, (gemstone, ring_name)) in enumerate(zip(globalitems.element_names, primordial_rings)):
    # Elemental Origins
    add_recipe("Elemental Infusion", f"Elemental Origin ({element})",
               [("OriginZ", 1), (f"Fae{idx}", 300), 80, f"Origin{idx}"])
    # Elemental Rings
    add_recipe("Elemental Ring Infusion", f"Elemental Ring of {element}",
               [(f"Gemstone{idx + 1}", 1), ("Scrap", 100), 100, "4"])
    # Primordial Rings
    add_recipe("Primordial Signet Infusion", f"{gemstone} Signet of {ring_name}",
               [(f"Gemstone{idx + 1}", 5), ("Gemstone11", 1), 100, "5"])
void_cost = [('Weapon', ("Scrap", 200)), ('Armour', ("Scrap", 100)), ('Greaves', ("Unrefined2", 10)),
             ('Amulet', ("Scrap", 100)),  ('Wing', ("Unrefined1", 10)), ('Crest', ("Unrefined3", 10))]
# Skull Infusions
skull_types = ["Cursed Golden Skull", "Haunted Golden Skull", "Radiant Golden Skull", "Prismatic Golden Skull"]
for idx, skull_type in enumerate(skull_types[1:], start=1):
    add_recipe("Skull Infusion", skull_type,
               [(f"Skull{idx}", 1), 100, f"Skull{idx + 1}"])
# Core Infusions
core_types = ["Void", "Wish", "Abyss", "Divinity"]
for idx in range(1, len(core_types) + 1):
    components = [(f"Crystal{idx - 1}", 1)] if idx != 1 else []
    add_recipe("Core Infusion", f"{core_types[idx - 1]} Core",
               components + [(f"Fragment{idx}", 10), 90, f"Core{idx}"])
    add_recipe("Core Infusion", f"Crystallized {core_types[idx - 1]}",
               [(f"Core{idx}", 3), 100, f"Crystal{idx}"])
# Void Infusions
for idx, (item_type, secondary_cost) in enumerate(void_cost):
    add_recipe("Void Infusion", f"Unrefined Void Item ({item_type})",
               [("Crystal1", 1), secondary_cost, 99, f"Void{idx + 1}"])
# Jewel Infusion
for idx, jewel_type in enumerate(['Dragon', 'Demon', 'Paragon'], start=1):
    add_recipe("Jewel Infusion", f"Unrefined {jewel_type} Jewel",
               [(f"Gem{idx}", 10), 75, f"Jewel{idx}"])
# Path Ring Infusions
path_rings = [
    ("Invoking Ring of Storms", [(1, 5), (3, 5), (11, 2)]),
    ("Primordial Ring of Frostfire", [(2, 5), (6, 5), (11, 2)]),
    ("Boundary Ring of Horizon", [(4, 5), (5, 5), (11, 2)]),
    ("Hidden Ring of Eclipse", [(7, 5), (8, 5), (11, 2)]),
    ("Cosmic Ring of Stars", [(9, 10), (11, 2)]),
    ("Rainbow Ring of Confluence", [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (11, 2)]),
    ("Lonely Ring of Solitude", [(0, 20), (11, 1)])]
for ring_name, gemstones in path_rings:
    add_recipe("Path Ring Infusion", ring_name, [(f"Gemstone{idx}", qty) for idx, qty in gemstones] + [100, "6"])

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

    async def create_cost_embed(self, player_obj):
        cost_title = f"{self.recipe_name} Infusion Cost"
        cost_info = ""
        for (item, qty) in self.cost_items:
            stock = await inventory.check_stock(player_obj, item.item_id)
            cost_info += f"{item.item_emoji} {item.item_name}: {stock} / {qty}\n"
        cost_info += f"Success Rate: {self.success_rate}%"
        cost_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=cost_title, description=cost_info)
        return cost_embed

    async def can_afford(self, player_obj, num_crafts):
        for (item, qty) in self.cost_items:
            stock = await inventory.check_stock(player_obj, item.item_id)
            if stock < num_crafts * qty:
                return False
        return True

    async def perform_infusion(self, player_obj, num_crafts, ring=False):
        result = 0
        labels = ['player_id', 'item_id', 'item_qty']
        batch_df = pd.DataFrame(columns=labels)
        # Deduct the cost for each item
        for (item, qty) in self.cost_items:
            total_cost = 0 - (num_crafts * qty)
            batch_df.loc[len(batch_df)] = [player_obj.player_id, item.item_id, total_cost]
        await inventory.update_stock(None, None, None, batch=batch_df)
        if ring:
            outcome = random.randint(1, 100)
            return 1 if ("Gambler's Masterpiece" not in self.recipe_name or outcome == 1) else 0
        # Perform the infusion attempts
        for _ in range(num_crafts):
            if random.randint(1, 100) <= self.success_rate:
                result += 1
        if result > 0:
            await inventory.update_stock(player_obj, self.outcome_item.item_id, result)
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
        self.embed = await recipe_object.create_cost_embed(self.player_obj)
        self.new_view = CraftView(self.player_obj, recipe_object)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class CraftView(discord.ui.View):
    def __init__(self, player_user, recipe_object):
        super().__init__(timeout=None)
        self.player_user, self.recipe_object = player_user, recipe_object
        self.embed_msg, self.new_view = None, None
        if "Ring" in self.recipe_object.category:
            self.infuse_1.label = "Infuse Ring"
            if "Gambler's Masterpiece" in self.recipe_object.recipe_name:
                self.infuse_1.label += f" (1%)"
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
        # Handle cannot afford response
        if not await self.recipe_object.can_afford(self.player_user, selected_qty):
            self.embed_msg = await self.recipe_object.create_cost_embed(self.player_user)
            self.embed_msg.add_field(name="Not Enough Materials!",
                                     value="Please come back when you have more materials.", inline=False)
            new_view = InfuseView(self.player_user)
            await interaction.response.edit_message(embed=self.embed_msg, view=new_view)
            return
        is_ring = "Ring" in self.recipe_object.category or "Signet" in self.recipe_object.category
        result = await self.recipe_object.perform_infusion(self.player_user, selected_qty, ring=is_ring)
        self.embed_msg = await self.recipe_object.create_cost_embed(self.player_user)
        # Handle infusion
        if is_ring and result == 1:
            # Handle ring
            new_ring = inventory.CustomItem(self.player_user.player_id, "R", self.recipe_object.outcome_item)
            new_ring.item_base_type = self.recipe_object.recipe_name
            if new_ring.item_base_type == "Crown of Skulls":
                new_ring.item_roll_values[0] += 1000
            new_ring.set_item_name()
            inventory.add_custom_item(new_ring)
            self.embed_msg = await new_ring.create_citem_embed()
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        # Handle non-ring failure
        if result == 0:
            header, description = "Infusion Failed!", "I guess it's just not your day today. How about another try?"
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
