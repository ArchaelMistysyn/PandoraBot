# General imports
import discord
import datetime
import random
import pandas as pd

# Data imports
import sharedmethods as sm
import globalitems as gli

# Core imports
import inventory
import player
from pandoradb import run_query as rqy

# Item/gear imports
import tarot
import itemdata


lotus_list = [itemdata.itemdata_dict[key] for key in itemdata.itemdata_dict.keys() if "Lotus" in key]
fish_list = [itemdata.itemdata_dict[key] for key in itemdata.itemdata_dict.keys() if "Fish" in key]
Fleur_Name = "Fleur, Oracle of the True Laws"
Yubelle = "Yubelle, Adjudicator the True Laws"
description_list = [
            "These are our best sellers.",
            "Browse our common wares.",
            "Browse our rarer items.",
            "Browse our special stock.",
            "Browse our premium goods.",
            "There are too many prying eyes here.",
            "Do you even realize what you're asking for?"]


async def get_daily_fish_items(fish_only=False):
    current_date = datetime.datetime.now().date()
    date_seed = int(current_date.strftime('%Y%m%d'))
    fish_random = random.Random(date_seed)
    daily_fish = fish_random.choice(fish_list)
    fish_obj = inventory.BasicItem(daily_fish['item_id'])
    if fish_only:
        return fish_obj
    item_list = [itemdata.itemdata_dict[key] for key in itemdata.itemdata_dict.keys()
                 if fish_obj.item_tier == itemdata.itemdata_dict[key]['tier'] and "Fish" not in key and "Fae" not in key]
    trade_obj = inventory.BasicItem(fish_random.choice(item_list)['item_id'])
    return fish_obj, trade_obj


async def display_fish_shop(player_obj, fish_obj, trade_obj):
    title = f"Black Market - Daily Fish Exchange"
    item_msg = f"Today's Item: {trade_obj.item_emoji} {trade_obj.item_name}"
    embed_msg = discord.Embed(colour=discord.Colour.blue(), title=title, description=item_msg)
    fish_stock = await inventory.check_stock(player_obj, fish_obj.item_id)
    cost_msg = f"{fish_stock} / 10 {fish_obj.item_emoji} {fish_obj.item_name}"
    embed_msg.add_field(name="Cost", value=cost_msg, inline=False)
    exchange_view = ExchangeView(player_obj, fish_obj, trade_obj)
    return fish_stock, embed_msg, exchange_view


class TierSelectView(discord.ui.View):
    def __init__(self, player_user, fish_obj, trade_obj):
        super().__init__(timeout=None)
        self.player_obj = player_user
        self.fish_obj, self.trade_obj = fish_obj, trade_obj
        emoji_list = ["<a:eenergy:1145534127349706772>"] * 7
        select_options = [discord.SelectOption(label="Fae Cores", emoji=emoji_list[0], description=description_list[0])]
        for i in range(1, 7):
            select_options.append(discord.SelectOption(
                label=f'Tier {i if i != 6 else "6+"} Items', emoji=emoji_list[i], description=description_list[i - 1]))
        title, fish_emoji = "Daily Fish Exchange", self.fish_obj.item_emoji
        fish_text = self.fish_obj.item_name.split("**")
        description = f"Daily Fish: {fish_text[1]}"
        select_options.append(discord.SelectOption(label=title, emoji=fish_emoji, description=description))
        self.select_menu = discord.ui.Select(
            placeholder="Select a shop.", min_values=1, max_values=1, options=select_options)
        self.select_menu.callback = self.tier_select_callback
        self.add_item(self.select_menu)

    async def display_shop(self, interaction, selected_tier, tier_colour, shop_msg):
        item_list = inventory.get_item_shop_list(selected_tier)
        embed_msg = discord.Embed(colour=tier_colour, title=shop_msg, description="")
        for x in item_list:
            embed_msg.add_field(name=f"{x.item_emoji} {x.item_name}", value=f"Cost: {x.item_cost:,}", inline=False)
        shop_view = ShopView(self.player_obj, tier_colour, selected_tier, item_list)
        await interaction.response.edit_message(embed=embed_msg, view=shop_view)

    async def tier_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        selected_type = interaction.data['values'][0]
        if selected_type == "Fae Cores":
            shop_msg = f"Black Market - Fae Cores."
            await self.display_shop(interaction, 0, discord.Colour.dark_orange(), shop_msg)
            return
        elif selected_type == "Daily Fish Exchange":
            _, fish_embed, exchange_view = await display_fish_shop(self.player_obj, self.fish_obj, self.trade_obj)
            await interaction.response.edit_message(embed=fish_embed, view=exchange_view)
            return
        else:
            selected_tier = int(selected_type[5])
        if selected_tier > (self.player_obj.player_echelon + 1):
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title="Black Market",
                                      description="You're not a high enough echelon to buy these items.")
            await interaction.response.edit_message(embed=embed_msg, view=self)
            return
        selected_tier = int(selected_type[5])
        shop_msg = f"Black Market - Tier {selected_tier} items."
        tier_colour, _ = sm.get_gear_tier_colours(selected_tier)
        await self.display_shop(interaction, selected_tier, tier_colour, shop_msg)


class ShopView(discord.ui.View):
    def __init__(self, player_user, tier_colour, selected_shop, item_list):
        super().__init__(timeout=None)
        self.player_obj = player_user
        self.tier_colour, self.selected_shop = tier_colour, selected_shop
        self.item_list = item_list
        select_options = [
            discord.SelectOption(emoji=item.item_emoji, label=item.item_name, value=item.item_id)
            for item in item_list]
        self.select_menu = discord.ui.Select(
            placeholder="Choose an item.", min_values=1, max_values=1, options=select_options)
        self.select_menu.callback = self.shop_callback
        self.add_item(self.select_menu)

    async def shop_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        embed_msg, purchase_view = await show_item(self.player_obj, interaction.data['values'][0])
        await interaction.response.edit_message(embed=embed_msg, view=purchase_view)


async def show_item(player_user, selected_info):
    selected_item = inventory.BasicItem(selected_info)
    embed_msg = await selected_item.create_bitem_embed(player_user)
    cost = selected_item.item_cost
    embed_msg.add_field(name="Cost", value=f"{cost:,}", inline=False)
    purchase_view = PurchaseView(player_user, selected_item)
    return embed_msg, purchase_view


class ExchangeView(discord.ui.View):
    def __init__(self, player_user, fish_obj, trade_obj):
        super().__init__(timeout=None)
        self.player_obj = player_user
        self.fish_obj, self.trade_obj = fish_obj, trade_obj
        self.handle_exchange.emoji = trade_obj.item_emoji
        self.is_paid = False

    @discord.ui.button(label="Exchange", style=discord.ButtonStyle.success)
    async def handle_exchange(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        fish_stock, fish_embed, exchange_view = await display_fish_shop(self.player_obj, self.fish_obj, self.trade_obj)
        if fish_stock < 10:
            stock_msg = sm.get_stock_msg(self.fish_obj, fish_stock, 10)
            fish_embed.add_field(name="Insufficient Fish!", value=stock_msg, inline=False)
            await interaction.response.edit_message(embed=fish_embed, view=exchange_view)
            return
        if not self.is_paid:
            labels = ['player_id', 'item_id', 'item_qty']
            batch_df = pd.DataFrame(columns=labels)
            batch_df.loc[len(batch_df)] = [self.player_obj.player_id, self.fish_obj.item_id, -10]
            batch_df.loc[len(batch_df)] = [self.player_obj.player_id, self.trade_obj.item_id, 1]
            await inventory.update_stock(None, None, None, batch=batch_df)
            self.is_paid = True
        _, fish_embed, exchange_view = await display_fish_shop(self.player_obj, self.fish_obj, self.trade_obj)
        swap_msg = f"1x {self.trade_obj.item_emoji} {self.trade_obj.item_name} received."
        fish_embed.add_field(name="Swap Successful", value=swap_msg, inline=False)
        await interaction.response.edit_message(embed=fish_embed, view=exchange_view)

    @discord.ui.button(label="Return", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def return_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        colour, title, description = discord.Colour.dark_orange(), "Black Market", "Everything has a price."
        embed_msg = discord.Embed(colour=colour, title=title, description=description)
        fish_obj, trade_obj = await market.get_daily_fish_items()
        new_view = TierSelectView(self.player_obj, fish_obj, trade_obj)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class PurchaseView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_obj = player_user
        self.selected_item = selected_item
        self.is_paid = False

    async def handle_purchase(self, quantity):
        await self.player_obj.reload_player()
        total_cost = self.selected_item.item_cost * quantity
        if self.player_obj.player_coins < total_cost:
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="Cannot Afford!", description="Please come back when you have more coins.")
            return embed_msg, self
        if not self.is_paid:
            _ = await self.player_obj.adjust_coins(total_cost, True)
            await inventory.update_stock(self.player_obj, self.selected_item.item_id, quantity)
            self.is_paid = True
        embed_title = "Purchase Successful!"
        embed_description = (f"Purchased {self.selected_item.item_emoji} {quantity:,}x {self.selected_item.item_name}"
                             f"\nRemaining: {gli.coin_icon} {self.player_obj.player_coins:,}x lotus coins")
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=embed_title, description=embed_description)
        new_view = PurchaseView(self.player_obj, self.selected_item)
        return embed_msg, new_view

    @discord.ui.button(label="Buy 1", style=discord.ButtonStyle.success, emoji="1️⃣")
    async def buy_one(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_obj.discord_id:
            embed_msg, new_view = await self.handle_purchase(1)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Buy 10", style=discord.ButtonStyle.success, emoji="🔟")
    async def buy_ten(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_obj.discord_id:
            embed_msg, new_view = await self.handle_purchase(10)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Buy 100", style=discord.ButtonStyle.success, emoji="💯")
    async def buy_hundred(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_obj.discord_id:
            embed_msg, new_view = await self.handle_purchase(100)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        colour, title, description = discord.Colour.dark_orange(), "Black Market", "Everything has a price."
        embed_msg = discord.Embed(colour=colour, title=title, description=description)
        fish_obj, trade_obj = await market.get_daily_fish_items()
        new_view = TierSelectView(self.player_obj, fish_obj, trade_obj)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class ChangelingShopView(discord.ui.View):
    def __init__(self, player_obj, token_obj, ore_obj):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.token_obj, self.ore_obj = token_obj, ore_obj
        self.embed_msg = None

    @discord.ui.button(label="Exchange", style=discord.ButtonStyle.success)
    async def exchange(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        token_stock = await inventory.check_stock(self.player_obj, self.token_obj.item_id)
        new_view = ChangelingShopView(self.player_obj, self.token_obj, self.ore_obj)
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        if token_stock < 10:
            temp_embed = await changeling_cost_msg(self.token_obj, token_stock, self.ore_obj)
            cost_msg = "It seems you're not prepared. I'll be waiting."
            temp_embed.add_field(name="Insufficient Tokens", value=cost_msg, inline=False)
            await interaction.response.edit_message(embed=temp_embed, view=new_view)
            return
        self.embed_msg = await changeling_cost_msg(self.token_obj, token_stock - 10, self.ore_obj)
        acquisition_msg = f"{self.ore_obj.item_emoji} 1x {self.ore_obj.item_name} acquired"
        self.embed_msg.add_field(name="", value=acquisition_msg, inline=False)
        await inventory.update_stock(self.player_obj, self.token_obj.item_id, -10)
        await inventory.update_stock(self.player_obj, self.ore_obj.item_id, 1)
        await interaction.response.edit_message(embed=self.embed_msg, view=new_view)


class LotusSelectView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        options = [discord.SelectOption(
            emoji=item['emoji'], label=item['name'], value=item['item_id'], description=item['description'])
            for item in lotus_list]
        self.select_menu = discord.ui.Select(
            placeholder="Select an item.", min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.lotus_select_callback
        self.add_item(self.select_menu)

    async def lotus_select_callback(self, interaction: discord.Interaction):
        lotus_id = str(interaction.data['values'][0])
        if interaction.user.id != self.player_obj.discord_id:
            return
        token_obj = inventory.BasicItem("Token6")
        token_stock = await inventory.check_stock(self.player_obj, token_obj.item_id)
        lotus_object = inventory.BasicItem(lotus_id)
        # Handle regular lotus.
        if lotus_id != "Lotus10":
            purchase_msg = (f"Are you absolutely certain this is the one you're looking for? It's not every day I let "
                            f"somebody lay their hands on my forbidden flowers."
                            f"\n{lotus_object.item_emoji} {lotus_object.item_name}")
            cost_msg = f"{token_stock} / 20 {token_obj.item_emoji} {token_obj.item_name}"
            embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=Fleur_Name, description=purchase_msg)
            embed_msg.add_field(name="Offering", value=cost_msg, inline=False)
            new_view = LotusPurchaseView(self.player_obj, token_obj, lotus_object)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
            return
        # Handle divine lotus.
        purchase_msg = (f"You've evaded my foresight again. Truly remarkable. ... I suppose it could be done. "
                        f"\nSurely you understand that the cost equivalent to your request will be ... unfathomable."
                        f"\n{lotus_object.item_emoji} {lotus_object.item_name}")
        cost_msg = f"{token_stock} / 20 {token_obj.item_name}"
        for item in lotus_list[:-1]:
            temp_object = inventory.BasicItem(item['item_id'])
            stock = await inventory.check_stock(self.player_obj, temp_object.item_id)
            cost_msg += f"\n{temp_object.item_emoji} {temp_object.item_name} {stock} / 1"
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=Fleur_Name, description=purchase_msg)
        embed_msg.add_field(name="Offering", value=cost_msg, inline=False)
        new_view = LotusPurchaseView(self.player_obj, token_obj, lotus_object)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)
        return


class LotusPurchaseView(discord.ui.View):
    def __init__(self, player_obj, token_obj, lotus_object):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.token_obj, self.lotus_object = token_obj, lotus_object
        self.embed_msg = None
        self.token_cost = 20
        self.pluck.emoji = self.token_obj.item_emoji
        if self.lotus_object.item_id == "Lotus10":
            self.pluck.label = "Divine Seed"
            self.token_cost = 20

    @discord.ui.button(label="Pluck Lotus", style=discord.ButtonStyle.success)
    async def pluck(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        token_stock = await inventory.check_stock(self.player_obj, "Token6")
        temp_embed = discord.Embed(colour=discord.Colour.dark_orange(), title=Fleur_Name, description="")
        new_view = LotusPurchaseView(self.player_obj, self.token_obj, self.lotus_object)
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        # Handle regular lotus.
        if self.lotus_object.item_id != "Lotus10":
            if token_stock < self.token_cost:
                temp_embed.description = "You'll have to come back with something a little more convincing."
                await interaction.response.edit_message(embed=temp_embed, view=new_view)
                return
            await inventory.update_stock(self.player_obj, "Token6", (self.token_cost * -1))
            await inventory.update_stock(self.player_obj, self.lotus_object.item_id, 1)
            temp_embed.description = f"{self.lotus_object.item_emoji} 1x {self.lotus_object.item_name} acquired"
            self.embed_msg = temp_embed
            await interaction.response.edit_message(embed=self.embed_msg, view=new_view)
            return
        # Handle divine lotus.
        lotus_stock = [await inventory.check_stock(self.player_obj, lotus_item.item_id) for lotus_item in lotus_list[:-1]]
        if token_stock < self.token_cost or any(stock == 0 for stock in lotus_stock):
            temp_embed.description = "I'm offended you had the gall to ask without sufficient preparations."
            await interaction.response.edit_message(embed=temp_embed, view=new_view)
            return
        await inventory.update_stock(self.player_obj, "Token6", (self.token_cost * -1))
        _ = [await inventory.update_stock(self.player_obj, self.lotus_object, -1) for lotus_item in lotus_list[:-1]]
        await inventory.update_stock(self.player_obj, self.lotus_object.item_id, 1)
        temp_embed.description = f"{self.lotus_object.item_emoji} 1x {self.lotus_object.item_name} acquired"
        self.embed_msg = temp_embed
        await interaction.response.edit_message(embed=self.embed_msg, view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = "Surely you didn't come all this way just to flirt with the divine maiden."
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=Fleur_Name, description=description)
        new_view = LotusSelectView(self.player_obj)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class EssencePurchaseView(discord.ui.View):
    def __init__(self, player_obj, token_obj, essence_obj):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.token_obj, self.essence_obj = token_obj, essence_obj
        self.embed_msg = None
        self.token_cost = essence_obj.item_tier
        self.exchange.emoji = self.token_obj.item_emoji

    @discord.ui.button(label="Exchange", style=discord.ButtonStyle.success)
    async def exchange(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        token_stock = await inventory.check_stock(self.player_obj, self.token_obj.item_id)
        new_view = EssencePurchaseView(self.player_obj, self.token_obj, self.essence_obj)
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        if token_stock < self.token_cost:
            temp_embed = await cathedral_cost_msg(self.token_obj, token_stock, self.essence_obj)
            cost_msg = "I'm not your servant *hero*, you must compensate me appropriately."
            temp_embed.add_field(name="Insufficient Tokens", value=cost_msg, inline=False)
            await interaction.response.edit_message(embed=temp_embed, view=new_view)
            return
        self.embed_msg = await cathedral_cost_msg(self.token_obj, token_stock - self.token_cost, self.essence_obj)
        acquisition_msg = f"{self.essence_obj.item_emoji} 1x {self.essence_obj.item_name} acquired"
        self.embed_msg.add_field(name="", value=acquisition_msg, inline=False)
        await inventory.update_stock(self.player_obj, self.token_obj.item_id, (self.token_cost * -1))
        await inventory.update_stock(self.player_obj, self.essence_obj.item_id, 1)
        await interaction.response.edit_message(embed=self.embed_msg, view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = "Hurry up."
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=Yubelle, description=description)
        new_view = tarot.SearchTierView(self.player_obj, cathedral=True)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


async def cathedral_cost_msg(token_obj, token_stock, essence_obj):
    temp_embed = discord.Embed(colour=discord.Colour.blurple(), title=Yubelle, description="")
    msg = f"I should have some traces of this particular essence.\n{essence_obj.item_emoji} {essence_obj.item_name}"
    cost_msg = f"{token_stock} / {essence_obj.item_tier} {token_obj.item_emoji} {token_obj.item_name}"
    temp_embed.description = msg
    temp_embed.add_field(name="Offering", value=cost_msg, inline=False)
    return temp_embed


async def changeling_cost_msg(token_obj, token_stock, ore_obj):
    Mysmir = "Mysmir, Changeling of the True Laws"
    temp_embed = discord.Embed(colour=discord.Colour.blurple(), title=Mysmir, description="")
    msg = (f"All things are malleable. One simply requires the right materials. "
           f"Shall I give you the {ore_obj.item_emoji} {ore_obj.item_name} that you seek?")
    cost_msg = f"{token_stock} / 10 {token_obj.item_emoji} {token_obj.item_name}"
    temp_embed.description = msg
    temp_embed.add_field(name="Offering", value=cost_msg, inline=False)
    return temp_embed
