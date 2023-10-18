import pandorabot
import discord
import inventory
import player

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
                emoji="<a:eenergy:1145534127349706772>", label="Tier 1 Items", description="Browse our common wares."),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Tier 2 Items", description="Browse our rarer items."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Tier 3 Items", description="Browse our special stock"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Tier 4 Items", description="Browse our premium goods."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Tier 5+ Items",
                description="There are too many prying eyes here. Let's discuss elsewhere.")
        ]
    )
    async def tier_select_callback(self, interaction: discord.Interaction, tier_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_type = tier_select.values[0]
                selected_tier = int(selected_type[5])
                if selected_tier <= self.player_user.player_echelon:
                    tier_colour, tier_emoji = inventory.get_gear_tier_colours(selected_tier)
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
                        case _:
                            shop_view = ShopView1(self.player_user, tier_colour)

                    embed_msg = discord.Embed(colour=tier_colour,
                                              title=f"Black Market - Tier {selected_tier} items.",
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
                emoji="<a:eenergy:1145534127349706772>", label="Vibrant Condensed Energy", value="I1a"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Clouded Ore", value="I1b"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Light Soul", value="I1c"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Hard Socket Hammer", value="I1d"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Static Comet Powder", value="I1h"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Puzzling Cleansing Matrix", value="I1i"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Ancient Pearl", value="I1j"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Lesser Stamina Potion", value="I1s"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Crate", value="I1r")
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
                emoji="<a:eenergy:1145534127349706772>", label="Vivid Condensed Energy", value="I2a"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Clear Ore", value="I2b"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Luminous Soul", value="I2c"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Heavy Socket Hammer", value="I2d"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Sparking Comet Powder", value="I2h"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Perplexing Cleansing Matrix", value="I2i"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Astral Pearl", value="I2j"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Standard Stamina Potion", value="I2s")
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
                emoji="<a:eenergy:1145534127349706772>", label="Viridescent Condensed Energy", value="I3a"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Crystal Ore", value="I3b"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Lustrous Soul", value="I3c"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Hallowed Socket Hammer", value="I3d"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Scintillating Comet Powder", value="I3h"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Paradoxical Cleansing Matrix", value="I3i"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Awakened Pearl", value="I3j"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Greater Stamina Potion", value="I3s")
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
                emoji="<a:eenergy:1145534127349706772>", label="Victorious Condensed Energy", value="I4a"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Champion's Ore", value="I4b"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Limitless Soul", value="I4c"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Heroic Socket Hammer", value="I4d"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Serene Comet Powder", value="I4h"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Perfect Cleansing Matrix", value="I4i"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Ascension Pearl", value="I4j"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Ultimate Stamina Potion", value="I4s"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Elemental Origin", value="I4k"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Unrefined Dragon Heart Gem (T4)", value="I4n"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Unrefined Wings (T4)", value="I4m")
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
                emoji="<a:eenergy:1145534127349706772>", label="Summoning Token (T5)", value="I5t"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Summoning Token (T6)", value="I6t"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Void Traces", value="I5l"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Unrefined Fabled Item", value="I5x"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Unrefined Dragon Heart Gem (T6)", value="I6n"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crystallized Wish", value="I6x"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Crystallized Void", value="I7x")
        ]
    )
    async def shop5_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
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

