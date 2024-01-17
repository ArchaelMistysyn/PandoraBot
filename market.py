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
                if selected_tier <= (self.player_user.player_echelon + 1):
                    item_list = inventory.get_item_shop_list(selected_tier)
                    shop_view = ShopView(self.player_user, tier_colour, selected_tier, item_list)
                    embed_msg = discord.Embed(colour=tier_colour, title=shop_msg, description="")
                    for x in item_list:
                        embed_msg.add_field(name=f"{x.item_emoji} {x.item_name}",
                                            value=f"Cost: {x.item_cost:,}", inline=False)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Black Market",
                                              description="You're not a high enough echelon to buy these items.")
                    shop_view = self
                await interaction.response.edit_message(embed=embed_msg, view=shop_view)
        except Exception as e:
            print(e)


class ShopView(discord.ui.View):
    def __init__(self, player_user, tier_colour, selected_shop, item_list):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour
        self.selected_shop = selected_shop
        self.item_list = item_list
        select_options = [
            discord.SelectOption(emoji=item.item_emoji, label=item.item_name, value=item.item_id)
            for item in item_list
        ]
        self.select_menu = discord.ui.Select(
            placeholder="Choose an item from the shop!", min_values=1, max_values=1, options=select_options
        )
        self.select_menu.callback = self.shop_callback
        self.add_item(self.select_menu)

    async def shop_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, purchase_view = show_item(self.player_user, interaction.data['values'][0])
                await interaction.response.edit_message(embed=embed_msg, view=purchase_view)
        except Exception as e:
            print(e)


def show_item(player_user, selected_info):
    selected_item = inventory.BasicItem(selected_info)
    embed_msg = selected_item.create_bitem_embed(player_user)
    cost = selected_item.item_cost
    embed_msg.add_field(name="Cost", value=f"{cost:,}", inline=False)
    purchase_view = PurchaseView(player_user, selected_item)
    return embed_msg, purchase_view


class PurchaseView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_item = selected_item
        self.is_paid = False

    def handle_purchase(self, quantity):
        reload_player = player.get_player_by_id(self.player_user.player_id)
        total_cost = self.selected_item.item_cost * quantity
        if total_cost <= reload_player.player_coins:
            if not self.is_paid:
                reload_player.player_coins -= total_cost
                reload_player.set_player_field("player_coins", reload_player.player_coins)
                inventory.update_stock(reload_player, self.selected_item.item_id, quantity)
                self.is_paid = True
            embed_title = "Purchase Successful!"
            embed_description = (f"Purchased {self.selected_item.item_emoji} {self.selected_item.item_name}"
                                 f" {quantity:,}x. Remaining lotus coins: {reload_player.player_coins}.")
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title=embed_title,
                                      description=embed_description)
            new_view = PurchaseView(self.player_user, self.selected_item)
        else:
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="Cannot Afford!",
                                      description="Please come back when you have more coins.")
            new_view = TierSelectView(reload_player)
        return embed_msg, new_view

    @discord.ui.button(label="Buy 1", style=discord.ButtonStyle.success, emoji="1️⃣")
    async def buy_one(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, new_view = self.handle_purchase(1)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Buy 10", style=discord.ButtonStyle.success, emoji="🔟")
    async def buy_ten(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, new_view = self.handle_purchase(10)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Buy 100", style=discord.ButtonStyle.success, emoji="💯")
    async def buy_hundred(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg, new_view = self.handle_purchase(100)
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
                new_view = TierSelectView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

