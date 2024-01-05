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

recipe_dict = {
    "Heavenly Ore (Crude)": ["i1o", 50, "STONE1", 10, 75, "i5o"],
    "Heavenly Soul (Light)": ["i1s", 50, "STONE1", 10, 75, "i5s"],
    "Heavenly Ore (Cosmite)": ["i2o", 20, "STONE2", 10, 75, "i5o"],
    "Heavenly Soul (Luminous)": ["i2s", 20, "STONE2", 10, 75, "i5s"],
    "Heavenly Ore (Celestite)": ["i3o", 10, "STONE3", 10, 75, "i5o"],
    "Heavenly Soul (Lucent)": ["i3s", 10, "STONE3", 10, 75, "i5s"],
    "Heavenly Ore (Crystallite)": ["i4o", 2, "STONE4", 10, 75, "i5o"],
    "Heavenly Soul (Lustrous)": ["i4s", 2, "STONE4", 10, 75, "i5s"],

    "Elemental Origin (Fire)": ["i4z", 1, "Fae0", 50, 80, "Origin0"],
    "Elemental Origin (Water)": ["i4z", 1, "Fae1", 50, 80, "Origin1"],
    "Elemental Origin (Lightning)": ["i4z", 1, "Fae2", 50, 80, "Origin2"],
    "Elemental Origin (Earth)": ["i4z", 1, "Fae3", 50, 80, "Origin3"],
    "Elemental Origin (Wind)": ["i4z", 1, "Fae4", 50, 80, "Origin4"],
    "Elemental Origin (Ice)": ["i4z", 1, "Fae5", 50, 80, "Origin5"],
    "Elemental Origin (Shadow)": ["i4z", 1, "Fae6", 50, 80, "Origin6"],
    "Elemental Origin (Light)": ["i4z", 1, "Fae7", 50, 80, "Origin7"],
    "Elemental Origin (Celestial)": ["i4z", 1, "Fae8", 50, 80, "Origin8"],

    "Chaos Hammer": ["i4h", 1, "i5l", 1, 90, "i5hA"],
    "Pulsar Hammer": ["i4h", 1, "i5l", 1, 90, "i5hP"],
    "Quasar Hammer": ["i4h", 1, "i5l", 1, 90, "i5hS"],

    "Void Hammer": ["i5v", 1, "i4h", 1, 90, "v6h"],
    "Void Pearl": ["i5v", 1, "i4p", 1, 90, "v6p"],
    "Void Origin": ["i5v", 1, "i4z", 1, 90, "OriginV"],
    "Crystallized Void": ["i5v", 1, "i6x", 1, 10, "v7x"],

    "Fabled Core": ["STONE5", 25, "i5l", 1, 90, "i5u"],
    "Fabled Flame": ["i5u", 1, "i3f", 1, 90, "i5f"],
    "Unrefined Fabled Item (Weapon)": ["i5aW", 200, "i5u", 5, 100, "i5xW"],
    "Unrefined Fabled Item (Armour)": ["i5aA", 100, "i5u", 2, 100, "i5xA"],
    "Unrefined Fabled Item (Accessory)": ["i5aY", 100, "i5u", 2, 100, "i5xY"],
    "Unrefined Fabled Item (Wing)": ["i4w", 50, "i5u", 2, 100, "i5xG"],
    "Unrefined Fabled Item (Crest)": ["i4c", 50, "i5u", 2, 100, "i5xC"],
    "Unrefined Fabled Item (Gem)": ["i4g", 25, "i5u", 1, 100, "i5xD"],

    "Fragmentized Wish (Weapon)": ["i5aW", 10, "STONE4", 1, 100, "i6m"],
    "Fragmentized Wish (Armour)": ["i5aA", 10, "STONE4", 1, 100, "i6m"],
    "Fragmentized Wish (Accessory)": ["i5aY", 10, "STONE4", 1, 100, "i6m"],
    "Crystallized Wish": ["i6m", 25, "STONE5", 10, 100, "i6x"],
    "Wish Core": ["i6x", 5, "i5u", 1, 50, "STONE5"],
    "Unrefined Wish Item (Weapon)": ["i6x", 5, "i5l", 10, 100, "i6uW"],
    "Unrefined Dragon Heart Gem": ["i4g", 50, "i6x", 1, 100, "i6g"],

    "Miracle Origin": ["i6x", 1, "i4z", 1, 100, "m6z"],
    "Miracle Ore": ["i6x", 1, "i5o", 2, 100, "m6o"],
    "Miracle Soul": ["i6x", 1, "i5s", 2, 100, "m6s"],
    "Miracle Flame": ["i6m", 5, "i3f", 20, 100, "m6f"],
    "Miracle Matrix": ["i6x", 1, "i3k", 50, 100, "m6k"],
    "Miracle Pearl": ["i6m", 5, "i4p", 1, 100, "m6p"],
    "Miracle Hammer": ["i6m", 10, "i4h", 1, 100, "m6h"],
    "Miracle Heart": ["i6x", 1, "i5l", 1, 100, "m6l"],
    "Zenith Hammer": ["m6h", 1, "i5l", 1, 100, "i5hA"],
    "Genesis Hammer": ["m6h", 1, "m6l", 1, 100, "m6hP"],
    "Terminus Hammer": ["m6h", 1, "m5l", 1, 100, "m6hS"]
}


class RecipeObject:
    def __init__(self, recipe_name):
        recipe_info = recipe_dict[recipe_name]

        self.recipe_name = recipe_name
        self.cost_item_1 = loot.BasicItem(recipe_info[0])
        self.cost_qty_1 = recipe_info[1]
        self.cost_item_2 = loot.BasicItem(recipe_info[2])
        self.cost_qty_2 = recipe_info[3]
        self.success_rate = recipe_info[4]
        self.outcome_item = loot.BasicItem(recipe_info[5])

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

    @discord.ui.select(
        placeholder="What kind of infusion do you want to preform?",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Heavenly Infusion",
                description="Creates heavenly upgrade materials."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Elemental Infusion",
                description="Creates an elemental origin."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Astral Infusion",
                description="Creates upgraded astral hammers."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Void Infusion",
                description="Creates upgraded void items."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fabled Infusion",
                description="Creates Fabled Items."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wish Infusion",
                description="Creates Wish Items."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Infusion",
                description="Creates Miracle Items.")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, method_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                method = method_select.values[0]
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Cloaked Alchemist, Sangam",
                                          description="Alright, what do you need?")
                match method:
                    case "Elemental Infusion":
                        new_view = ElementSelectView(self.player_object)
                    case "Astral Infusion":
                        new_view = AstralSelectView(self.player_object)
                    case "Void Infusion":
                        new_view = VoidSelectView(self.player_object)
                    case "Heavenly Infusion":
                        new_view = HeavenlySelectView(self.player_object)
                    case "Fabled Infusion":
                        new_view = FabledSelectView(self.player_object)
                    case "Wish Infusion":
                        new_view = WishSelectView(self.player_object)
                    case "Miracle Infusion":
                        new_view = MiracleSelectView(self.player_object)
                    case _:
                        new_view = None
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class ElementSelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select the infusion recipe.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji=globalitems.global_element_list[0], label="Fire", description="Use fire cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[1], label="Water", description="Use water cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[2], label="Lightning", description="Use lightning cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[3], label="Earth", description="Use earth cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[4], label="Wind", description="Use wind cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[5], label="Ice", description="Use ice cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[6], label="Shadow", description="Use shadow cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[7], label="Light", description="Use light cores."),
            discord.SelectOption(
                emoji=globalitems.global_element_list[8], label="Celestial", description="Use celestial cores.")
        ]
    )
    async def element_callback(self, interaction: discord.Interaction, element_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                recipe_name = f"Elemental Origin ({element_select.values[0]})"
                recipe_object = RecipeObject(recipe_name)
                embed_msg = recipe_object.create_cost_embed(reload_player)
                new_view = CraftView(reload_player, recipe_object)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class HeavenlySelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select the infusion recipe.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Crude Ore", description="Use crude ores."),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Cosmite Ore", description="Use cosmite ores."),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Celestite Ore", description="Use celestite ores."),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Crystallite Ore", description="Use crystallite ores."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Light Soul", description="Use light souls."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Luminous Soul", description="Use luminous souls."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Lucent Soul", description="Use lucent souls."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Lustrous Soul", description="Use lustrous souls."),
        ]
    )
    async def heavenly_callback(self, interaction: discord.Interaction, heavenly_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                selected_option = heavenly_select.values[0].split()
                recipe_name = f"Heavenly {selected_option[1]} ({selected_option[0]})"
                recipe_object = RecipeObject(recipe_name)
                embed_msg = recipe_object.create_cost_embed(reload_player)
                new_view = CraftView(reload_player, recipe_object)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class AstralSelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select the infusion recipe.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Chaos Hammer", description="Rerolls all affixes."),
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Pulsar Hammer", description="Modifies prefixes."),
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Quasar Hammer", description="Modifies suffixes.")
        ]
    )
    async def astral_callback(self, interaction: discord.Interaction, astral_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                recipe_name = astral_select.values[0]
                recipe_object = RecipeObject(recipe_name)
                embed_msg = recipe_object.create_cost_embed(reload_player)
                new_view = CraftView(reload_player, recipe_object)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class VoidSelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select the infusion recipe.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:evoid:1145520260573827134>", label="Void Hammer", description="Upgrade to 6 stars."),
            discord.SelectOption(
                emoji="<a:evoid:1145520260573827134>", label="Void Pearl", description="Upgrade max tier rolls."),
            discord.SelectOption(
                emoji="<a:evoid:1145520260573827134>", label="Void Origin",
                description="Further upgrade the reinforcement."),
            discord.SelectOption(
                emoji="<a:evoid:1145520260573827134>", label="Crystallized Void", description="???")
        ]
    )
    async def void_callback(self, interaction: discord.Interaction, void_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                recipe_name = void_select.values[0]
                recipe_object = RecipeObject(recipe_name)
                embed_msg = recipe_object.create_cost_embed(reload_player)
                new_view = CraftView(reload_player, recipe_object)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class FabledSelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select the infusion recipe.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fabled Core",
                description="An ancient mechanism from a time long past."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fabled Flame",
                description="A powerful flame said to burn forever."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Fabled Item (Weapon)",
                description="Forge an unrefined fabled weapon."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Fabled Item (Armour)",
                description="Forge an unrefined fabled armour."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Fabled Item (Accessory)",
                description="Forge an unrefined fabled accessory."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Fabled Item (Wing)",
                description="Forge an unrefined fabled wing."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Fabled Item (Crest)",
                description="Forge an unrefined fabled crest."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Fabled Item (Gem)",
                description="Forge an unrefined fabled gem.")

        ]
    )
    async def fabled_callback(self, interaction: discord.Interaction, fabled_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                recipe_name = fabled_select.values[0]
                recipe_object = RecipeObject(recipe_name)
                embed_msg = recipe_object.create_cost_embed(reload_player)
                new_view = CraftView(reload_player, recipe_object)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class WishSelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select the infusion recipe.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fragmentized Wish (Weapon)",
                description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fragmentized Wish (Armour)",
                description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fragmentized Wish (Accessory)",
                description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crystallized Wish",
                description="A wish never fulfilled."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wish Core",
                description="The embodiment of a wish."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Wish Item (Weapon)",
                description="Forge an unrefined wish item (weapon)."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Unrefined Dragon Heart Gem",
                description="Forge a Dragon Heart Gem")
        ]
    )
    async def wish_callback(self, interaction: discord.Interaction, wish_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                recipe_name = wish_select.values[0]
                recipe_object = RecipeObject(recipe_name)
                embed_msg = recipe_object.create_cost_embed(reload_player)
                new_view = CraftView(reload_player, recipe_object)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class MiracleSelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select the infusion recipe.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Ore", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Soul", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Flame", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Matrix", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Hammer", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Pearl", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Heart", description="???"),
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Zenith Hammer", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Genesis Hammer", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Terminus Hammer", description="???"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Miracle Origin", description="???")
        ]
    )
    async def miracle_callback(self, interaction: discord.Interaction, miracle_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                recipe_name = miracle_select.values[0]
                recipe_object = RecipeObject(recipe_name)
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

    @discord.ui.button(label="Infuse 1", style=discord.ButtonStyle.success, emoji="1️⃣")
    async def infuse_1(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_qty = 1
                reload_player = player.get_player_by_id(self.player_user.player_id)
                if self.recipe_object.can_afford(reload_player, selected_qty):
                    if not self.is_paid:
                        result = self.recipe_object.perform_infusion(reload_player, selected_qty)
                        self.is_paid = True
                    if result > 0:
                        embed_title = "Cloaked Alchemist, Sangam"
                        outcome_item = self.recipe_object.outcome_item
                        embed_description = "Infusion Successful!"
                        embed_description += f"\n{outcome_item.item_emoji} {result}x {outcome_item.item_name}"
                    else:
                        embed_title = "Cloaked Alchemist, Sangam"
                        embed_description = "Infusion Failed! I guess it's just not your day today."
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title=embed_title,
                                              description=embed_description)
                    refresh_view = CraftView(reload_player, self.recipe_object)
                    await interaction.response.edit_message(embed=embed_msg, view=refresh_view)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Not Enough Materials!",
                                              description="Please come back when you have more materials.")
                    reset_view = InfuseView(reload_player)
                    await interaction.response.edit_message(embed=embed_msg, view=reset_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Infuse 5", style=discord.ButtonStyle.success, emoji="5️⃣")
    async def infuse_5(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_qty = 5
                reload_player = player.get_player_by_id(self.player_user.player_id)
                if self.recipe_object.can_afford(reload_player, selected_qty):
                    if not self.is_paid:
                        result = self.recipe_object.perform_infusion(reload_player, selected_qty)
                        self.is_paid = True
                    if result > 0:
                        embed_title = "Cloaked Alchemist, Sangam"
                        outcome_item = self.recipe_object.outcome_item
                        embed_description = f"{result}x Infusions Successful!"
                        embed_description += f"\n{outcome_item.item_emoji} {result}x {outcome_item.item_name}"
                    else:
                        embed_title = "Cloaked Alchemist, Sangam"
                        embed_description = "All Infusions Failed! Are you bringing me faulty materials?."
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title=embed_title,
                                              description=embed_description)
                    refresh_view = CraftView(reload_player, self.recipe_object)
                    await interaction.response.edit_message(embed=embed_msg, view=refresh_view)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Not Enough Materials!",
                                              description="Please come back when you have more materials.")
                    reset_view = InfuseView(reload_player)
                    await interaction.response.edit_message(embed=embed_msg, view=reset_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Infuse 10", style=discord.ButtonStyle.success, emoji="🔟")
    async def infuse_10(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_qty = 10
                reload_player = player.get_player_by_id(self.player_user.player_id)
                if self.recipe_object.can_afford(reload_player, selected_qty):
                    if not self.is_paid:
                        result = self.recipe_object.perform_infusion(reload_player, selected_qty)
                        self.is_paid = True
                    if result > 0:
                        embed_title = "Cloaked Alchemist, Sangam"
                        outcome_item = self.recipe_object.outcome_item
                        embed_description = f"{result}x Infusions Successful!"
                        embed_description += f"\n{outcome_item.item_emoji} {result}x {outcome_item.item_name}"
                    else:
                        embed_title = "Cloaked Alchemist, Sangam"
                        embed_description = "All Infusions Failed! Your lack of luck is impressive."
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title=embed_title,
                                              description=embed_description)
                    refresh_view = CraftView(reload_player, self.recipe_object)
                    await interaction.response.edit_message(embed=embed_msg, view=refresh_view)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Not Enough Materials!",
                                              description="Please come back when you have more materials.")
                    reset_view = InfuseView(reload_player)
                    await interaction.response.edit_message(embed=embed_msg, view=reset_view)
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
