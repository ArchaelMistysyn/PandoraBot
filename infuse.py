# General imports
import discord
import pandas as pd
from discord.ui import Button, View
import random

# Data imports
import globalitems as gli
import itemdata
import sharedmethods as sm
import tarot

# Core imports
from pandoradb import run_query as rqy
import player
import inventory

# Gear/item imports
from ringdata import ring_resonance_dict as rrd, ring_icons as ricon

recipe_dict = {
    "Heavenly Infusion": {}, "Elemental Infusion": {}, "Crystal Infusion": {},
    "Void Infusion": {}, "Jewel Infusion": {}, "Skull Infusion": {},
    "Special Infusion": {
        "Radiant Heart": [("Stone6", 1), ("Fragment2", 1), 20, "Heart1", None],
        "Chaos Heart": [("Stone6", 1), ("Fragment3", 1), 20, "Heart2", None],
        "Abyss Flame": [("Crystal3", 1), ("Flame1", 10), 80, "Flame2", None],
        "Lotus of Serenity": [("Heart1", 99), ("Fragment2", 99), 99, "Lotus3"]},
    "Elemental Signet Infusion": {}, "Primordial Ring Infusion": {}, "Path Ring Infusion": {},
    "Fabled Ring Infusion": {
        "Dragon's Eye Diamond": [("Gemstone9", 15), ("Gemstone10", 3), 100, "7", "R"],
        "Bleeding Hearts": [("Gemstone9", 5), ("Heart1", 50), ("Heart2", 50), ("Gemstone10", 3), 100, "7", "R"],
        "Gambler's Masterpiece": [("Gemstone9", 1), ("Gemstone10", 1), 1, "7", "R"],
        "Lonely Ring of the Dark Star": [("DarkStar", 1), ("Gemstone9", 5),("Gemstone10", 3), 100, "7", "R"],
        "Lonely Ring of the Light Star": [("LightStar", 1), ("Gemstone9", 5),("Gemstone10", 3), 100, "7", "R"]},
    "Sovereign Ring Infusion": {
        "Stygian Calamity": [("Shard", 25), ("Gemstone11", 1), ("Gemstone10", 5), ("Crystal3", 10), ("Crystal4", 1), 100, "8", "R"],
        "Heavenly Calamity": [("Shard", 25), ("Gemstone11", 1), ("Ore5", 10), ("Gemstone10", 5), ("Crystal4", 1), 100, "8", "R"],
        "Hadal's Raindrop": [("Shard", 25), ("Nadir", 1), ("EssenceXIV", 10), ("Gemstone10", 5), ("Crystal4", 1), 100, "8", "R"],
        "Twin Rings of Divergent Stars": [("LightStar", 1), ("DarkStar", 1), ("Gemstone10", 5), ("Crystal4", 1), 100, "8", "R"],
        "Crown of Skulls": [("Shard", 50), ("Skull4", 1), ("Lotus2", 1), ("Gemstone10", 5), ("Crystal4", 1), 100, "8", "R"],
        "Chromatic Tears": [("Shard", 50), ("Lotus11", 1), ("Gemstone10", 10), ("Crystal4", 1), 100, "8", "R"]},
    "Sovereign Weapon Infusion": {
        "Pandora's Universe Hammer": [("Shard", 50), ("Lotus10", 1), ("Crystal4", 1), 100, "8", "W"],
        "Fallen Lotus of Nephilim": [("Shard", 50), ("Nephilim", 1), ("Lotus10", 1), ("Crystal4", 1), 100, "8", "W"],
        "Solar Flare Blaster": [("Shard", 25), ("Gemstone0", 10), ("Gemstone4", 10), ("Gemstone7", 10),
                                ("Gemstone9", 10), ("EssenceXIX", 10), ("Crystal4", 1), 100, "8", "W"],
        "Bathyal, Enigmatic Chasm Bauble": [("Shard", 25), ("Nadir", 1), ("Crystal4", 1), 100, "8", "W"]},
    "Sovereign Special Infusion": {
        "Ruler's Crest": [("Shard", 1000), ("Ruler", 1), ("Gemstone0", 100), ("Gemstone1", 100), ("Gemstone2", 100),
                          ("Gemstone3", 100), ("Gemstone4", 100), ("Gemstone5", 100), ("Gemstone6", 100),
                          ("Gemstone7", 100), ("Gemstone8", 100), ("Gemstone9", 100), ("Crystal4", 10), 100, "8", "C"]}}


def add_recipe(category, name, data_list):
    if category not in recipe_dict:
        recipe_dict[category] = {}
    recipe_dict[category][name] = data_list


# Heavenly Infusion
for idx, (ore, count) in enumerate(zip(['Crude', 'Cosmite', 'Celestite', 'Crystallite'], [50, 20, 10, 2]), start=1):
    add_recipe("Heavenly Infusion", f"Heavenly Ore ({ore})",
               [(f"Ore{idx}", count), (f"Stone{idx}", 5), 75, "Ore5", None])

primordial_rings = [("Ruby", "Incineration"), ("Sapphire", "Atlantis"), ("Topaz", "Dancing Thunder"),
                    ("Agate", "Seismic Tremors"), ("Emerald", "Wailing Winds"), ("Zircon", "Frozen Castle"),
                    ("Obsidian", "Tormented Souls"), ("Opal", "Scintillation"), ("Amethyst", "Shifting Stars")]
# Elemental Infusions
for idx, (element, (gemstone, ring_name)) in enumerate(zip(gli.element_names, primordial_rings)):
    # Elemental Gemstones
    gemstone_id = f"Gemstone{idx}"
    temp_item = inventory.BasicItem(gemstone_id)
    add_recipe("Elemental Infusion", temp_item.item_name,
               [("Catalyst", 1), (f"Fae{idx}", 300), 80, gemstone_id, None])
    # Elemental Signets
    add_recipe("Elemental Signet Infusion", f"Elemental Signet of {element}",
               [(gemstone_id, 2), ("Scrap", 100), 100, "4", "R"])
    # Primordial Rings
    add_recipe("Primordial Ring Infusion", f"{gemstone} Ring of {ring_name}",
               [(gemstone_id, 5), ("Gemstone10", 1), 100, "5", "R"])
void_cost = [('Weapon', ("Scrap", 200)), ('Armour', ("Scrap", 100)), ('Greaves', ("Unrefined2", 10)),
             ('Amulet', ("Scrap", 100)), ('Wing', ("Unrefined1", 10)), ('Crest', ("Unrefined3", 10))]
# Skull Infusions
skull_types = ["Cursed Golden Skull", "Haunted Golden Skull", "Radiant Golden Skull", "Prismatic Golden Skull"]
for idx, skull_type in enumerate(skull_types[1:], start=1):
    add_recipe("Skull Infusion", skull_type,
               [(f"Skull{idx}", 1), 100, f"Skull{idx + 1}", None])
# Crystal Infusions
fragment_types = ["Void", "Wish", "Abyss", "Divinity"]
for idx in range(1, len(fragment_types) + 1):
    add_recipe("Crystal Infusion", f"Crystallized {fragment_types[idx - 1]} (Fragment)",
               [(f"Fragment{idx}", 20), 100, f"Crystal{idx}", None])
    if idx == 1:
        continue
    add_recipe("Crystal Infusion", f"Crystallized {fragment_types[idx - 1]} (Upgrade)",
               [(f"Crystal{idx - 1}", 3), 90, f"Crystal{idx}", None])

# Void Infusions
for idx, (item_type, secondary_cost) in enumerate(void_cost):
    add_recipe("Void Infusion", f"Unrefined Void Item ({item_type})",
               [("Crystal1", 1), secondary_cost, 99, f"Void{idx + 1}", None])
# Jewel Infusion
for idx, jewel_type in enumerate(['Dragon', 'Demon', 'Paragon'], start=1):
    add_recipe("Jewel Infusion", f"Unrefined {jewel_type} Jewel",
               [(f"Gem{idx}", 10), 75, f"Jewel{idx}", None])
# Path Ring Infusions
path_rings = [
    ("Invoking Ring of Storms", [(1, 5), (2, 5), (10, 2)]),
    ("Primordial Ring of Frostfire", [(0, 5), (5, 5), (10, 2)]),
    ("Boundary Ring of Horizon", [(3, 5), (4, 5), (10, 2)]),
    ("Hidden Ring of Eclipse", [(6, 5), (7, 5), (10, 2)]),
    ("Cosmic Ring of Stars", [(8, 10), (10, 2)]),
    ("Rainbow Ring of Confluence", [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (10, 2)]),
    ("Lonely Ring of Solitude", [(9, 10), (10, 2)])]
for ring_name, gemstones in path_rings:
    add_recipe("Path Ring Infusion", ring_name, [(f"Gemstone{idx}", qty) for idx, qty in gemstones] + [100, "6", "R"])

recipe_index_dict = {}
for i_category, recipes in recipe_dict.items():
    recipe_index_dict[i_category] = {recipe: index for index, recipe in enumerate(recipes.keys())}
sov_icon = ["<:p_hammer:1275566048619528252>", "<:lotus_sword:1275566042068025364>",
            "<:Blaster:1304109337500844154>", "<:Bathyal:1304109287164870687>"]
spec_icon = ["<:ruler:1275566119343755384>"]
cat_icon = {
    "Heavenly Infusion": "<:Fae0:1274786282010316913>",
    "Elemental Infusion": "<:Cata:1274786559996198944>",
    "Crystal Infusion": "<:Cry1:1274785116572614856>",
    "Void Infusion": "<:Saber5:1275575137537888269>",
    "Jewel Infusion": "<:Gem_5:1275569736205340773>",
    "Skull Infusion": "<:Skull4:1274786891677302784>",
    "Special Infusion": "<:Lotus3:1274786460486336605>",
    "Elemental Signet Infusion": "<:Signet0:1275564530088415242>",
    "Primordial Ring Infusion": "<:E_Ring0:1275563709519106190>",
    "Path Ring Infusion": "<:P_Ring8:1303816617200713811>",
    "Fabled Ring Infusion": "<:DE_Ring:1303816766899884042>",
    "Sovereign Ring Infusion": "<:twin_rings:1275566143238836295>",
    "Sovereign Weapon Infusion": "<:p_hammer:1275566048619528252>",
    "Sovereign Special Infusion": "<:ruler:1275566119343755384>"}
NPC_name, NPC_description = "Cloaked Alchemist, Sangam", "Alright, what do you need?"


class RecipeObject:
    def __init__(self, category, recipe_name):
        self.category = category
        self.recipe_name, self.recipe_info = recipe_name, recipe_dict[category][recipe_name]

        # Initialize cost items dynamically
        self.cost_items = []
        self.item_type = self.recipe_info[-1]
        self.success_rate = self.recipe_info[-3]
        if self.item_type is None:
            self.outcome_item = inventory.BasicItem(self.recipe_info[-2])
        else:
            self.outcome_item = int(self.recipe_info[-2])
        for item_info in self.recipe_info[:-3]:
            item_id, qty = item_info
            self.cost_items.append((inventory.BasicItem(item_id), qty))

    async def create_cost_embed(self, player_obj):
        cost_title = f"{self.recipe_name} Infusion Cost"
        cost_info = ""
        for (item, qty) in self.cost_items:
            stock = await inventory.check_stock(player_obj, item.item_id)
            cost_info += f"{item.item_emoji} {item.item_name}: {stock} / {qty}\n"
        cost_info += f"Success Rate: {self.success_rate}%"
        cost_embed = sm.easy_embed("Magenta", cost_title, cost_info)
        if self.item_type is None:
            cost_embed.set_thumbnail(url=self.outcome_item.item_image)
        else:
            t_obj = inventory.CustomItem(player_obj.player_id, self.item_type, int(self.outcome_item), self.recipe_name)
            cost_embed.set_thumbnail(url=sm.get_gear_thumbnail(t_obj))
        return cost_embed

    async def can_afford(self, player_obj, num_crafts):
        for (item, qty) in self.cost_items:
            stock = await inventory.check_stock(player_obj, item.item_id)
            if stock < num_crafts * qty:
                return False
        return True

    async def perform_infusion(self, player_obj, num_crafts):
        result = 0
        labels = ['player_id', 'item_id', 'item_qty']
        batch_df = pd.DataFrame(columns=labels)
        # Deduct the cost for each item
        for (item, qty) in self.cost_items:
            total_cost = 0 - (num_crafts * qty)
            batch_df.loc[len(batch_df)] = [player_obj.player_id, item.item_id, total_cost]
        await inventory.update_stock(None, None, None, batch=batch_df)
        if self.item_type is not None:
            return 1 if ("Gambler's Masterpiece" not in self.recipe_name or random.randint(1, 100) == 1) else 0
        # Perform the infusion attempts
        for _ in range(num_crafts):
            if random.randint(1, 100) <= self.success_rate:
                result += 1
        if result > 0:
            await inventory.update_stock(player_obj, self.outcome_item.item_id, result)
        return result


class InfuseView(discord.ui.View):
    def __init__(self, ctx_obj, player_obj):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_obj = ctx_obj, player_obj
        self.selected_item, self.value = None, None

        # Build the option menu dynamically based on recipe categories.
        opt = [discord.SelectOption(
            emoji=cat_icon[category], label=category, description=f"Creates {category.lower()} items."
        ) for category in recipe_dict]
        self.select_menu = discord.ui.Select(
            placeholder="What kind of infusion do you want to perform?", min_values=1, max_values=1, options=opt)
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        embed_msg = sm.easy_embed("Magenta", NPC_name, NPC_description)
        embed_msg.set_image(url=gli.infuse_img)
        new_view = SelectRecipeView(self.ctx_obj, self.player_obj, interaction.data['values'][0])
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class SelectRecipeView(discord.ui.View):
    def __init__(self, ctx_obj, player_obj, category):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_obj, self.category = ctx_obj, player_obj, category
        self.embed, self.new_view = None, None

        # Build the option menu dynamically based on the category's recipes.
        category_recipes = recipe_dict.get(self.category, {})
        options_data_list = []
        for recipe_idx, (recipe_name, recipe) in enumerate(category_recipes.items()):
            if recipe[-1] == "R":
                option_emoji = "💍"
                if self.category in ricon:
                    option_emoji = ricon[self.category][recipe_idx]
            elif recipe[-1] == "W":
                option_emoji = sov_icon[recipe_idx]
            elif self.category == "Sovereign Special Infusion":
                option_emoji = spec_icon[recipe_idx]
            else:
                result_item = inventory.BasicItem(recipe[-2])
                option_emoji = result_item.item_emoji
            options_data_list.append([recipe_name, recipe[-3], option_emoji])
        select_options = [
            discord.SelectOption(
                emoji=result_emoji, label=recipe_name, description=f"Success Rate {success_rate}%", value=recipe_name
            ) for recipe_name, success_rate, result_emoji in options_data_list]
        self.select_menu = discord.ui.Select(placeholder=f"Select the {self.category.lower()} recipe.",
                                             min_values=1, max_values=1, options=select_options)
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
        self.new_view = CraftView(self.ctx_obj, self.player_obj, recipe_object)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class CraftView(discord.ui.View):
    def __init__(self, ctx_obj, player_obj, recipe_object):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_obj, self.recipe_object = ctx_obj, player_obj, recipe_object
        self.embed_msg, self.new_view = None, None
        r_cat, r_name = recipe_object.category, recipe_object.recipe_name
        if ("Ring" in r_cat or "Signet" in r_cat) or r_cat in ["Sovereign Weapon Infusion", "Sovereign Special Infusion"]:
            self.remove_item(self.children[2])
            blood_obj = inventory.BasicItem("Sacred")
            self.infuse_5.label = "Sacred Blood"
            self.infuse_5.emoji = blood_obj.item_emoji
            self.infuse_5.style = gli.button_colour_list[0]
        if "Ring" in r_cat or "Signet" in r_cat:
            if r_cat != "Sovereign Ring Infusion":
                self.remove_item(self.children[1])
            self.infuse_1.label = "Infuse Ring"
            if "Gambler's Masterpiece" in r_name:
                self.infuse_1.label += f" (1%)"
            self.infuse_1.emoji = "💍"
            if r_cat in ricon:
                self.infuse_1.emoji = ricon[r_cat][recipe_index_dict[r_cat][r_name]]
        elif r_cat == "Sovereign Weapon Infusion":
            self.infuse_1.label = "Infuse Weapon"
            self.infuse_1.emoji = sov_icon[recipe_index_dict[r_cat][r_name]]
        elif r_cat == "Sovereign Special Infusion":
            self.infuse_1.label = "Special Infusion"
            self.infuse_1.emoji = spec_icon[recipe_index_dict[r_cat][r_name]]

    async def run_button(self, interaction, selected_qty):
        if interaction.user.id != self.player_obj.discord_id:
            return
        await self.player_obj.reload_player()
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        self.new_view = CraftView(self.ctx_obj, self.player_obj, self.recipe_object)
        item_tier, full_inv = 0 if self.recipe_object.item_type is None else int(self.recipe_object.outcome_item), False
        target_qty = 0 if self.recipe_object.item_type is None else 1
        # Handle cannot afford response
        if not await self.recipe_object.can_afford(self.player_obj, target_qty):
            self.embed_msg = await self.recipe_object.create_cost_embed(self.player_obj)
            self.embed_msg.add_field(name="Not Enough Materials!",
                                     value="Please come back when you have more materials.", inline=False)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        if self.recipe_object.item_type is not None:
            is_sacred = False if item_tier != 8 else True if selected_qty == 5 or random.randint(1, 100) <= 5 else False
            # Confirm inventory space
            full_inv = await inventory.check_capacity(self.player_obj.player_id, self.recipe_object.item_type)
            if full_inv:
                type_name = inventory.custom_item_dict[self.recipe_object.item_type]
                header, description = "Full Inventory!", f"Please make space in your {type_name.lower()} inventory."
                self.embed_msg.add_field(name=header, value=description, inline=False)
                self.new_view = CraftView(self.ctx_obj, self.player_obj, self.recipe_object)
                await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
                return
        # Handle infusion
        result = await self.recipe_object.perform_infusion(self.player_obj, target_qty)
        self.embed_msg = await self.recipe_object.create_cost_embed(self.player_obj)
        if result == 0:
            # Handle Failure
            header, description = "Infusion Failed!", "I guess it's just not your day today. How about another try?"
            self.embed_msg.add_field(name=header, value=description, inline=False)
            self.new_view = CraftView(self.ctx_obj, self.player_obj, self.recipe_object)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        elif self.recipe_object.item_type is None:
            # Non-Gear Success
            outcome_item = self.recipe_object.outcome_item
            header, description = "Infusion Successful!", f"\n{outcome_item.item_emoji} {result:,}x {outcome_item.item_name}"
            self.embed_msg.add_field(name=header, value=description, inline=False)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        # Handle Gear Success
        classification, item_tier = ("Sacred", 9) if is_sacred else ("Sovereign", 8) if item_tier == 8 else (None, item_tier)
        new_item = inventory.CustomItem(self.player_obj.player_id, self.recipe_object.item_type, item_tier,
                                        base_type=self.recipe_object.recipe_name, is_sacred=is_sacred)
        # Handle Ring Exceptions
        if self.recipe_object.item_type == "R":
            new_item.roll_values[0] = random.randint(0, 30) if new_item.item_tier in [8, 9] \
                else rrd[new_item.item_base_type]
            if new_item.item_base_type == "Crown of Skulls":
                new_item.roll_values[2] = new_item.roll_values[0]  # Store resonance in slot 3
                new_item.roll_values[0], new_item.roll_values[1] = 1000, 0
            elif new_item.item_base_type == "Chromatic Tears":
                new_item.roll_values[2] = 25  # Store static resonance in slot 3
                new_item.roll_values[0], new_item.roll_values[1] = 10, 500
        await inventory.add_custom_item(new_item)
        self.embed_msg = await new_item.create_citem_embed()
        await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
        if classification is not None:
            await sm.send_notification(self.ctx_obj, self.player_obj, classification, new_item.item_base_type)
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
        if interaction.user.id != self.player_obj.discord_id:
            return
        embed_msg = sm.easy_embed("Magenta", NPC_name, NPC_description)
        new_view = InfuseView(self.ctx_obj, self.player_obj)
        embed_msg.set_image(url=gli.infuse_img)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)
