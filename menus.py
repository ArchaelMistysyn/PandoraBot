import discord
from discord.ui import Button, View
import inventory
import loot
import player


class RefSelectView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Dragon Heart Gems", description="Refine dragon heart gems"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Wings", description="Refine equippable wings"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Paragon Crests", description="Refine equippable crests")
        ]
    )
    async def ref_select_callback(self, interaction: discord.Interaction, ref_select: discord.ui.Select):
        selected_type = ref_select.values[0]
        match selected_type:
            case "Dragon Heart Gems":
                tier_view = RefineryGemView(self.player_user, selected_type)
            case "Wings":
                tier_view = RefineryWingView(self.player_user, selected_type)
            case "Paragon Crests":
                tier_view = RefineryCrestView(self.player_user, selected_type)
            case _:
                tier_view = RefineryWingView(self.player_user, selected_type)

        await interaction.response.edit_message(view=tier_view)


class RefineryGemView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""

    @discord.ui.button(label="Tier 1", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_one_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 1
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 2", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_two_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 2
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 3", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_three_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 3
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 4", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_four_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 4
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class RefineryWingView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""

    @discord.ui.button(label="Tier 1", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_one_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 1
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 2", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_two_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 2
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 3", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_three_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 3
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 4", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_four_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 4
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class RefineryCrestView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""

    @discord.ui.button(label="Tier 1", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_one_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 1
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 2", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_two_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 2
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 3", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_three_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 3
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Tier 4", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_four_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 4
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


def refine_item(player_user, selected_type, selected_tier):

    item_id = f"I{str(selected_tier)}"

    match selected_type:
        case "Dragon Heart Gems":
            item_id += "n"
        case "Wings":
            item_id += "m"
        case "Paragon Crests":
            item_id += "o"
        case _:
            item_id = "error"

    if inventory.check_stock(player_user, item_id) > 0:
        inventory.update_stock(player_user, item_id, -1)
        new_item = inventory.try_refine(player_user.player_id, selected_type, selected_tier)
        if new_item.item_id != "":
            inventory.inventory_add_custom_item(new_item)
            embed_msg = new_item.create_citem_embed()
        else:
            embed_msg = discord.Embed(colour=discord.Colour.red(),
                                      title="Refinement Failed! The item is destroyed",
                                      description="Try Again?")
    else:
        selected_icon = loot.get_loot_emoji(item_id)
        stock_message = f'{selected_icon} Out of Stock!'
        embed_msg = discord.Embed(colour=discord.Colour.red(),
                                  title=stock_message,
                                  description="")

    return embed_msg


class InlaySelectView(discord.ui.View):
    def __init__(self, player_user, gem_id):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.gem_id = gem_id

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Weapon", description="Inlay gem in your weapon"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Armour", description="Inlay gem in your armour"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Accessory", description="Inlay gem in your accessory"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wings", description="Inlay gem in your wing"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crest", description="Inlay gem in your crest")
        ]
    )
    async def inlay_select_callback(self, interaction: discord.Interaction, inlay_select: discord.ui.Select):
        selected_type = inlay_select.values[0]
        not_equipped = True
        no_socket = True
        self.player_user.get_equipped()
        match selected_type:
            case "Weapon":
                if self.player_user.equipped_weapon != "":
                    not_equipped = False
                    e_item = inventory.read_custom_item(self.player_user.equipped_weapon)
                    if e_item.item_num_sockets == 1:
                        no_socket = False
                        embed_msg = e_item.create_citem_embed()
                        confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
            case "Armour":
                if self.player_user.equipped_armour != "":
                    not_equipped = False
                    e_item = inventory.read_custom_item(self.player_user.equipped_armour)
                    if e_item.item_num_sockets == 1:
                        no_socket = False
                        embed_msg = e_item.create_citem_embed()
                        confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
            case "Accessory":
                if self.player_user.equipped_acc != "":
                    not_equipped = False
                    e_item = inventory.read_custom_item(self.player_user.equipped_acc)
                    if e_item.item_num_sockets == 1:
                        no_socket = False
                        embed_msg = e_item.create_citem_embed()
                        confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
            case "Wings":
                if self.player_user.equipped_wing != "":
                    not_equipped = False
                    e_item = inventory.read_custom_item(self.player_user.equipped_wing)
                    if e_item.item_num_sockets == 1:
                        no_socket = False
                        embed_msg = e_item.create_citem_embed()
                        confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
            case _:
                if self.player_user.equipped_crest != "":
                    not_equipped = False
                    e_item = inventory.read_custom_item(self.player_user.equipped_crest)
                    if e_item.item_num_sockets == 1:
                        no_socket = False
                        embed_msg = e_item.create_citem_embed()
                        confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)

        if not_equipped:
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="Inlay Failed.",
                                      description="No item equipped in this slot")
            await interaction.response.edit_message(embed=embed_msg)
        elif no_socket:
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="Inlay Failed.",
                                      description="This equipped item has no socket")
            await interaction.response.edit_message(embed=embed_msg)
        else:
            await interaction.response.edit_message(embed=embed_msg, view=confirm_view)


class ConfirmInlayView(discord.ui.View):
    def __init__(self, player_user, e_item, gem_id):
        super().__init__(timeout=None)
        self.e_item = e_item
        self.player_user = player_user
        self.gem_id = gem_id

    @discord.ui.button(label="Inlay Gem", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_one_callback(self, interaction: discord.Interaction, button: discord.Button):
        self.e_item.item_inlaid_gem_id = self.gem_id
        self.e_item.update_stored_item()
        embed_msg = self.e_item.create_citem_embed()
        await interaction.response.edit_message(embed=embed_msg, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)