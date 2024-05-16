# General imports
import discord

# Data imports
import globalitems
import itemdata

# Core imports
import inventory
import sharedmethods


class TradeObject:
    def __init__(self, offer_player, target_player, offer_obj, offer_qty, receive_obj, receive_qty):
        self.offer_player, self.target_player = offer_player, target_player
        self.offer_obj, self.offer_qty = offer_obj, offer_qty
        self.receive_obj, self.receive_qty = receive_obj, receive_qty
        self.trade_msg = discord.Embed(colour=discord.Colour.green(), title="Trade Request", description="")
        self.set_trade_details(self.offer_player, self.offer_obj, self.offer_qty)
        self.set_trade_details(self.target_player, self.receive_obj, self.receive_qty)
    
    def set_trade_details(self, select_player, select_obj, select_qty):
        if select_qty == 0:
            return
        if select_obj is None:
            trade_details = f"{globalitems.coin_icon} {select_qty:,}x Lotus Coins"
        else:
            trade_details = f"{select_obj.item_emoji} {select_obj.item_name} {select_qty:,}x"
        self.trade_msg.add_field(name=f"{select_player.player_username} Offers:", value=trade_details, inline=True)

    async def perform_trade(self):
        # Validate coins/stock
        if ((self.offer_obj is None and self.target_player.player_coins < self.receive_qty) or
                (self.target_player.player_coins < self.receive_qty)):
            return "Insufficient coins to complete the trade."
        if self.offer_obj is not None:
            offer_stock = await inventory.check_stock(self.offer_player, self.offer_obj.item_id)
            if offer_stock < self.offer_qty:
                return "Insufficient items to complete the trade."
        if self.receive_obj is not None:
            receive_stock = await inventory.check_stock(self.target_player, self.receive_obj.item_id)
            if receive_stock < self.receive_qty:
                return "Insufficient items to complete the trade."
        # Execute trade and transfer all item/coins.
        if self.offer_obj:
            await inventory.update_stock(self.offer_player, self.offer_obj.item_id, (self.offer_qty * -1))
            await inventory.update_stock(self.target_player, self.offer_obj.item_id, self.offer_qty)
        else:
            _ = self.offer_player.adjust_coins(self.offer_qty, reduction=True)
            _ = self.target_player.adjust_coins(self.offer_qty, apply_pact=False)
        if self.receive_obj:
            await inventory.update_stock(self.target_player, self.receive_obj.item_id, (self.receive_qty * -1))
            await inventory.update_stock(self.offer_player, self.receive_obj.item_id, self.receive_qty)
        else:
            _ = self.target_player.adjust_coins(self.receive_qty, reduction=True)
            _ = self.offer_player.adjust_coins(self.receive_qty, apply_pact=False)
        return ""


async def create_trade(offer_player, target_player, offer_item, offer_qty, receive_item, receive_qty):
    async def check_item_availability(select_player, select_item, select_qty):
        if select_item != "" and select_item in itemdata.itemdata_dict.keys():
            select_obj = inventory.BasicItem(select_item)
            select_stock = await inventory.check_stock(select_player, select_item)
            if select_stock < select_qty:
                return None, f"{select_player.player_username} only has {select_item.item_emoji} {select_obj.item_name} {select_stock:,}x"
            return select_obj, ""
        return None, ""

    # Validate the trade amounts.
    if offer_qty <= 0 or receive_qty <= 0:
        return None, "Trade amounts cannot be negative or 0."
    # Validate the items and stock.
    offer_obj, err_msg = await check_item_availability(offer_player, offer_item, offer_qty)
    if err_msg != "":
        return None, err_msg
    receive_obj, err_msg = await check_item_availability(target_player, receive_item, receive_qty)
    if err_msg != "":
        return None, err_msg
    # Validate coin amounts.
    if offer_obj is None and offer_player.player_coins < offer_qty:
        return None, f"{offer_player.player_username} only has {globalitems.coin_icon} {offer_player.player_coins:,}x Lotus Coins"
    elif receive_obj is None and target_player.player_coins < receive_qty:
        return None, f"{target_player.player_username} only has {globalitems.coin_icon} {target_player.player_coins:,}x Lotus Coins"

    # Create the trade object
    trade_obj = TradeObject(offer_player, target_player, offer_obj, offer_qty, receive_obj, receive_qty)
    return trade_obj, ""


class TradeView(discord.ui.View):
    def __init__(self, trade_obj):
        super().__init__(timeout=None)
        self.trade_obj = trade_obj
        self.new_embed, self.new_view = None, None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept_trade(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.trade_obj.target_player.discord_id:
            return
        if self.new_embed is not None:
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        self.new_embed = self.trade_obj.trade_msg
        fail_msg = await self.trade_obj.perform_trade()
        if fail_msg != "":
            self.new_embed.add_field(name="Trade Failed", value=fail_msg, inline=False)
            self.new_view = TradeView(self.trade_obj)
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        self.new_embed.add_field(name="Trade Completed", value="Items/Coins have been transferred.", inline=False)
        await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖️")
    async def cancel_trade(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id in [self.trade_obj.offer_player.discord_id, self.trade_obj.target_player.discord_id]:
            title, description = "Trade Cancelled", f"User {interaction.user.display_name} cancelled the trade."
            self.new_embed = discord.Embed(colour=discord.Colour.red(), title=title, description=description)
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
