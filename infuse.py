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
import quest
import asyncio
import damagecalc
import bazaar

element_fire = "<:ee:1141653476816986193>"
element_water = "<:ef:1141653475059572779>"
element_lightning = "<:ei:1141653471154671698>"
element_earth = "<:eh:1141653473528664126>"
element_wind = "<:eg:1141653474480767016>"
element_ice = "<:em:1141647050342146118>"
element_dark = "<:ek:1141653468080242748>"
element_light = "<:el:1141653466343800883>"
element_celestial = "<:ej:1141653469938339971>"
omni_icon = "🌈"
element_icon = [element_fire, element_water, element_lightning, element_earth, element_wind, element_ice,
                element_dark, element_light, element_celestial]


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
                description="Creates astral hammers"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Void Infusion",
                description="Creates void items")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                method = item_select.values[0]
                embed_msg = create_cost_embed(method)
                match method:
                    case "Elemental Infusion":
                        new_view = ElementSelectView(self.player_object, method)
                    case "Astral Infusion":
                        new_view = AstralView(self.player_object)
                    case "Void Infusion":
                        new_view = VoidView(self.player_object)
                    case "Heavenly Infusion":
                        new_view = HeavenlyView(self.player_object)
                    case _:
                        new_view = None
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class ElementSelectView(discord.ui.View):
    def __init__(self, player_object, method):
        super().__init__(timeout=None)
        self.player_object = player_object
        self.method = method

    @discord.ui.select(
        placeholder="Select the element to infuse.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji=element_icon[0], label="Fire",
                value="0", description="Use fire cores."),
            discord.SelectOption(
                emoji=element_icon[1], label="Water",
                value="1", description="Use water cores."),
            discord.SelectOption(
                emoji=element_icon[2], label="Lighting",
                value="2", description="Use lightning cores."),
            discord.SelectOption(
                emoji=element_icon[3], label="Earth",
                value="3", description="Use earth cores."),
            discord.SelectOption(
                emoji=element_icon[4], label="Wind",
                value="4", description="Use wind cores."),
            discord.SelectOption(
                emoji=element_icon[5], label="Ice",
                value="5", description="Use ice cores."),
            discord.SelectOption(
                emoji=element_icon[6], label="Shadow",
                value="6", description="Use shadow cores."),
            discord.SelectOption(
                emoji=element_icon[7], label="Light",
                value="7", description="Use light cores."),
            discord.SelectOption(
                emoji=element_icon[8], label="Celestial",
                value="8", description="Use celestial cores.")
        ]
    )
    async def element_callback(self, interaction: discord.Interaction, element_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                selected_element = int(element_select.values[0])
                embed_msg = create_cost_embed(method)
                new_view = ElementInfuseView(self.player_object, selected_element)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


def create_cost_embed(method):
    cost_embed = ""
    return cost_embed


class PurchaseView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_item = selected_item
        self.is_paid = False

    @discord.ui.button(label="Buy 1", style=discord.ButtonStyle.success, emoji="1️⃣")
    async def buy_one(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                reload_player = player.get_player_by_id(self.player_user.player_id)
                if self.selected_item.item_cost <= reload_player.player_coins:
                    if not self.is_paid:
                        reload_player.player_coins -= self.selected_item.item_cost
                        reload_player.set_player_field("player_coins", reload_player.player_coins)
                        inventory.update_stock(reload_player, self.selected_item.item_id, 1)
                        self.is_paid = True
                    embed_title = "Purchase Successful!"
                    embed_description = (f"Purchased {self.selected_item.item_emoji} {self.selected_item.item_name}"
                                         f" 1x. Remaining lotus coins: {reload_player.player_coins}.")
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title=embed_title,
                                              description=embed_description)
                    refresh_view = PurchaseView(self.player_user, self.selected_item)
                    await interaction.response.edit_message(embed=embed_msg, view=refresh_view)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Cannot Afford!",
                                              description="Please come back when you have more coins.")
                    reset_view = TierSelectView(reload_player)
                    await interaction.response.edit_message(embed=embed_msg, view=reset_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Buy 5", style=discord.ButtonStyle.success, emoji="5️⃣")
    async def buy_five(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                reload_player = player.get_player_by_id(self.player_user.player_id)
                total_cost = self.selected_item.item_cost * 5
                if total_cost <= reload_player.player_coins:
                    if not self.is_paid:
                        reload_player.player_coins -= total_cost
                        reload_player.set_player_field("player_coins", reload_player.player_coins)
                        inventory.update_stock(reload_player, self.selected_item.item_id, 5)
                        self.is_paid = True
                    embed_title = "Purchase Successful!"
                    embed_description = (f"Purchased {self.selected_item.item_emoji} {self.selected_item.item_name}"
                                         f" 5x. Remaining lotus coins: {reload_player.player_coins}.")
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title=embed_title,
                                              description=embed_description)
                    refresh_view = PurchaseView(self.player_user, self.selected_item)
                    await interaction.response.edit_message(embed=embed_msg, view=refresh_view)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Cannot Afford!",
                                              description="Please come back when you have more coins.")
                    reset_view = TierSelectView(reload_player)
                    await interaction.response.edit_message(embed=embed_msg, view=reset_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Buy 10", style=discord.ButtonStyle.success, emoji="🔟")
    async def buy_ten(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                reload_player = player.get_player_by_id(self.player_user.player_id)
                total_cost = self.selected_item.item_cost * 10
                if total_cost <= reload_player.player_coins:
                    if not self.is_paid:
                        reload_player.player_coins -= total_cost
                        reload_player.set_player_field("player_coins", reload_player.player_coins)
                        inventory.update_stock(reload_player, self.selected_item.item_id, 10)
                        self.is_paid = True
                    embed_title = "Purchase Successful!"
                    embed_description = (f"Purchased {self.selected_item.item_emoji} {self.selected_item.item_name}"
                                         f" 10x. Remaining lotus coins: {reload_player.player_coins}.")
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title=embed_title,
                                              description=embed_description)
                    refresh_view = PurchaseView(self.player_user, self.selected_item)
                    await interaction.response.edit_message(embed=embed_msg, view=refresh_view)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Cannot Afford!",
                                              description="Please come back when you have more coins.")
                    reset_view = TierSelectView(reload_player)
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
                new_view = TierSelectView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)
