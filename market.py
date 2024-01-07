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
                    shop_view = ShopView(self.player_user, tier_colour, selected_tier)
                    embed_msg = discord.Embed(colour=tier_colour, title=shop_msg, description="")
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


class ShopView(discord.ui.View):
    def __init__(self, player_user, tier_colour, selected_shop):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.tier_colour = tier_colour
        self.selected_shop = selected_shop
        select_options_dict = {
            0: [
                discord.SelectOption(emoji=globalitems.global_element_list[0], label="Fae Core (Fire)", value="Fae0"),
                discord.SelectOption(emoji=globalitems.global_element_list[1], label="Fae Core (Water)", value="Fae1"),
                discord.SelectOption(emoji=globalitems.global_element_list[2], label="Fae Core (Lightning)",
                                     value="Fae2"),
                discord.SelectOption(emoji=globalitems.global_element_list[3], label="Fae Core (Earth)", value="Fae3"),
                discord.SelectOption(emoji=globalitems.global_element_list[4], label="Fae Core (Wind)", value="Fae4"),
                discord.SelectOption(emoji=globalitems.global_element_list[5], label="Fae Core (Ice)", value="Fae5"),
                discord.SelectOption(emoji=globalitems.global_element_list[6], label="Fae Core (Shadow)", value="Fae6"),
                discord.SelectOption(emoji=globalitems.global_element_list[7], label="Fae Core (Light)", value="Fae7"),
                discord.SelectOption(emoji=globalitems.global_element_list[8], label="Fae Core (Celestial)",
                                     value="Fae8")
            ],
            1: [
                discord.SelectOption(emoji="<:eore:1145534835507593236>", label="Crude Ore", value="i1o"),
                discord.SelectOption(emoji="<:esoul:1145520258241806466>", label="Light Soul", value="i1s"),
                discord.SelectOption(emoji=globalitems.stamina_icon, label="Lesser Stamina Potion", value="i1y"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Crate", value="i1r")
            ],
            2: [
                discord.SelectOption(emoji="<:eore:1145534835507593236>", label="Cosmite Ore", value="i2o"),
                discord.SelectOption(emoji="<:esoul:1145520258241806466>", label="Luminous Soul", value="i2s"),
                discord.SelectOption(emoji=globalitems.stamina_icon, label="Standard Stamina Potion", value="i2y"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Namechanger Token",
                                     value="cNAME"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Pathchanger Token",
                                     value="cCLASS"),
                discord.SelectOption(emoji="<:ehammer:1145520259248427069>", label="Star Hammer", value="i2h"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Resetter Token", value="cSKILL")
            ],
            3: [
                discord.SelectOption(emoji="<:eore:1145534835507593236>", label="Celestite Ore", value="i3o"),
                discord.SelectOption(emoji="<:esoul:1145520258241806466>", label="Lucent Soul", value="i3s"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Socket Adder", value="i3k"),
                discord.SelectOption(emoji="<a:eshadow2:1141653468965257216>", label="Purgatorial Flame", value="i3f"),
                discord.SelectOption(emoji=globalitems.stamina_icon, label="Greater Stamina Potion", value="i3y")
            ],
            4: [
                discord.SelectOption(emoji="<:eore:1145534835507593236>", label="Crystallite Ore", value="i4o"),
                discord.SelectOption(emoji="<:esoul:1145520258241806466>", label="Lustrous Soul", value="i4s"),
                discord.SelectOption(emoji="<:eprl:1148390531345432647>", label="Stellar Pearl", value="i4p"),
                discord.SelectOption(emoji="<a:eorigin:1145520263954440313>", label="Origin Catalyst", value="i4z"),
                discord.SelectOption(emoji=globalitems.stamina_icon, label="Ultimate Stamina Potion", value="i4y"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Dragon Wings",
                                     value="i4w"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Dragon Jewel",
                                     value="i4g"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Paragon Crest",
                                     value="i4c"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Summoning Token", value="i4t")
            ],
            5: [
                discord.SelectOption(emoji="<:eore:1145534835507593236>", label="Heavenly Ore", value="i5o"),
                discord.SelectOption(emoji="<:esoul:1145520258241806466>", label="Heavenly Soul", value="i5s"),
                discord.SelectOption(emoji="<a:evoid:1145520260573827134>", label="Void Traces", value="i5v"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Astral Heart", value="i5l"),
                discord.SelectOption(emoji="<a:eenergy:1145534127349706772>", label="Summoning Relic", value="i5t"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Fabled Core", value="i5u"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Fabled Item (Weapon)",
                                     value="i5xW"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Fabled Item (Armour)",
                                     value="i5xA"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>",
                                     label="Unrefined Fabled Item (Accessory)",
                                     value="i5xY"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Fabled Item (Wing)",
                                     value="i5xG"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Fabled Item (Crest)",
                                     value="i5xC"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Fabled Item (Gem)",
                                     value="i5xD"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Fabled Weapon Fragment",
                                     value="i5aW"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Fabled Armour Fragment",
                                     value="i5aA"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>",
                                     label="Fabled Accessory Fragment", value="i5aY")
            ],
            6: [
                discord.SelectOption(emoji="<:esoul:1145520258241806466>", label="Summoning Artifact", value="i6t"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Unrefined Dragon Heart Gem",
                                     value="i6g"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Fragmentized Wish", value="i6m"),
                discord.SelectOption(emoji="<a:elootitem:1144477550379274322>", label="Crystallized Void", value="i7x"),
            ]
        }
        select_options = select_options_dict[self.selected_shop]
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
                                 f" {quantity}x. Remaining lotus coins: {reload_player.player_coins}.")
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

