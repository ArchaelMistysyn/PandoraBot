import pandorabot
import discord
import inventory
import player
import globalitems

import pandas as pd
import mydb
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc


class TierSelectView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select a shop!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fae Cores", description="These are our best sellers."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 1 Items", description="Browse our common wares."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 2 Items", description="Browse our rarer items."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 3 Items", description="Browse our special stock."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 4 Items", description="Browse our premium goods."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 5 Items",
                description="There are too many prying eyes here."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 6+ Items",
                description="Do you even realize what you're asking for?")
        ]
    )
    async def tier_select_callback(self, interaction: discord.Interaction, tier_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_type = tier_select.values[0]
                if selected_type == "Fae Cores":
                    selected_tier = 0
                    shop_msg = f"Black Market - Fae Cores."
                    tier_colour = discord.Colour.dark_orange()
                else:
                    selected_tier = int(selected_type[5])
                    shop_msg = f"Black Market - Tier {selected_tier} items."
                    tier_colour, tier_emoji = inventory.get_gear_tier_colours(selected_tier)
                if selected_tier <= self.player_user.player_echelon or self.player_user.player_echelon == 5:
                    match selected_tier:
                        case 1:
                            shop_view = ShopView1(self.player_user, tier_colour)
                        case 2:
                            shop_view = ShopView2(self.player_user, tier_colour)
                        case 3:
                            shop_view = ShopView3(self.player_user, tier_colour)
                        case 4:
                            shop_view = ShopView4(self.player_user, tier_colour)
                        case 5:
                            shop_view = ShopView5(self.player_user, tier_colour)
                        case 6:
                            shop_view = ShopView6(self.player_user, tier_colour)
                        case _:
                            shop_view = ShopView0(self.player_user, tier_colour)

                    embed_msg = discord.Embed(colour=tier_colour,
                                              title=shop_msg,
                                              description="")
                    item_list = inventory.get_item_shop_list(selected_tier)
                    for x in item_list:
                        embed_msg.add_field(name=f"{x.item_emoji} {x.item_name}",
                                            value=f"Cost: {x.item_cost}", inline=False)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Black Market",
                                              description="You're not a high enough echelon to buy these items.")
                    shop_view = self
                await interaction.response.edit_message(embed=embed_msg, view=shop_view)
        except Exception as e:
            print(e)


class ShopView0(discord.ui.View):
    def __init__(self, player_user, tier_colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour

    @discord.ui.select(
        placeholder="Choose an item from the shop!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji=globalitems.global_element_list[0], label="Fae Core (Fire)", value="Fae0"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[1], label="Fae Core (Water)", value="Fae1"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[2], label="Fae Core (Lightning)", value="Fae2"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[3], label="Fae Core (Earth)", value="Fae3"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[4], label="Fae Core (Wind)", value="Fae4"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[5], label="Fae Core (Ice)", value="Fae5"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[6], label="Fae Core (Shadow)", value="Fae6"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[7], label="Fae Core (Light)", value="Fae7"),
            discord.SelectOption(
                emoji=globalitems.global_element_list[8], label="Fae Core (Celestial)", value="Fae8")
        ]
    )
    async def shop0_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, item_select.values[0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


class ShopView1(discord.ui.View):
    def __init__(self, player_user, tier_colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour

    @discord.ui.select(
        placeholder="Choose an item from the shop!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Crude Ore", value="i1o"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Light Soul", value="i1s"),
            discord.SelectOption(
                emoji=globalitems.stamina_icon, label="Lesser Stamina Potion", value="i1y"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Crate", value="i1r")
        ]
    )
    async def shop1_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, item_select.values[0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


class ShopView2(discord.ui.View):
    def __init__(self, player_user, tier_colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Cosmite Ore", value="i2o"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Luminous Soul", value="i2s"),
            discord.SelectOption(
                emoji=globalitems.stamina_icon, label="Standard Stamina Potion", value="i2y")
        ]
    )
    async def shop2_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, item_select.values[0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


class ShopView3(discord.ui.View):
    def __init__(self, player_user, tier_colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Celestite Ore", value="i3o"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Lucent Soul", value="i3s"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Socket Adder", value="i3k"),
            discord.SelectOption(
                emoji="<a:eshadow2:1141653468965257216>", label="Purgatorial Flame", value="I3f"),
            discord.SelectOption(
                emoji=globalitems.stamina_icon, label="Greater Stamina Potion", value="i3y")
        ]
    )
    async def shop3_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, item_select.values[0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


class ShopView4(discord.ui.View):
    def __init__(self, player_user, tier_colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Crystallite Ore", value="i4o"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Lustrous Soul", value="i4s"),
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Star Hammer", value="i4h"),
            discord.SelectOption(
                emoji="<:eprl:1148390531345432647>", label="Stellar Pearl", value="i4p"),
            discord.SelectOption(
                emoji="<a:eorigin:1145520263954440313>", label="Origin Catalyst", value="i4z"),
            discord.SelectOption(
                emoji=globalitems.stamina_icon, label="Ultimate Stamina Potion", value="i4y"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Unrefined Dragon Wings", value="i4w"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Unrefined Dragon Jewel", value="i4g"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Unrefined Paragon Crest", value="i4c"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Summoning Token", value="i4t")
        ]
    )
    async def shop4_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, item_select.values[0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


class ShopView5(discord.ui.View):
    def __init__(self, player_user, tier_colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Heavenly Ore", value="i5o"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Heavenly Soul", value="i5s"),
            discord.SelectOption(
                emoji="<a:evoid:1145520260573827134>", label="Void Traces", value="i5v"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Astral Heart", value="i5l"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Summoning Relic", value="i5t"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Unrefined Fabled Item", value="i5x"),
        ]
    )
    async def shop5_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, item_select.values[0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


class ShopView6(discord.ui.View):
    def __init__(self, player_user, tier_colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Summoning Artifact", value="i6t"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Unrefined Dragon Heart Gem", value="i6g"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Fragmentized Wish", value="i6m"),
            discord.SelectOption(
                emoji="<a:elootitem:1144477550379274322>", label="Crystallized Void", value="i7x")
        ]
    )
    async def shop6_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, item_select.values[0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


def show_item(player_user, selected_info):
    selected_item = inventory.get_basic_item_by_id(selected_info)
    embed_msg = selected_item.create_bitem_embed()
    cost = selected_item.item_cost
    embed_msg.add_field(name="Cost", value=cost, inline=False)
    purchase_view = PurchaseView(player_user, selected_item)
    return embed_msg, purchase_view


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

