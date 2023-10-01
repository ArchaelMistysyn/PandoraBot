import discord
from discord.ui import Button, View
import inventory
import loot
import random
import player
import explore
import tarot
import mydb
import pandorabot


# Forge menu
class ForgeView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.selected_id = self.selected_item.item_id
        self.player_object = player_object
        self.letter = "a"
        self.values = None
        self.button_label = []
        self.button_emoji = []
        self.num_buttons = 0

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Enhance", description="Enhance the item"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Upgrade", description="Upgrade the item"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Bestow", description="Bless the item"),
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Open", description="Open a socket"),
            discord.SelectOption(
                emoji="<a:ematrix:1145520262268325919>", label="Imbue", description="Add new rolls"),
            discord.SelectOption(
                emoji="<a:eshadow2:1141653468965257216>", label="Cleanse", description="Remove random rolls"),
            discord.SelectOption(
                emoji="<:eprl:1148390531345432647>", label="Augment", description="Augment existing rolls"),
            discord.SelectOption(
                emoji="<a:eorigin:1145520263954440313>", label="Implant", description="Gain new elements"),
            discord.SelectOption(
                emoji="<a:evoid:1145520260573827134>", label="Voidforge", description="Upgrade to a void weapon")
        ]
    )
    async def forge_callback(self, interaction: discord.Interaction, forge_select: discord.ui.Select):
        self.clear_items()
        match forge_select.values[0]:
            case "Enhance":
                self.letter = "a"
                self.num_buttons = 5
            case "Upgrade":
                self.letter = "b"
                self.button_emoji.append(loot.get_loot_emoji("I1b"))
                self.button_emoji.append(loot.get_loot_emoji("I2b"))
                self.button_emoji.append(loot.get_loot_emoji("I3b"))
                self.button_emoji.append(loot.get_loot_emoji("I4b"))
                self.num_buttons = 5
            case "Bestow":
                self.letter = "c"
                self.button_emoji.append(loot.get_loot_emoji("I1c"))
                self.button_emoji.append(loot.get_loot_emoji("I2c"))
                self.button_emoji.append(loot.get_loot_emoji("I3c"))
                self.button_emoji.append(loot.get_loot_emoji("I4c"))
                self.num_buttons = 5
            case "Open":
                self.letter = "d"
                self.button_emoji.append(loot.get_loot_emoji("I1d"))
                self.button_emoji.append(loot.get_loot_emoji("I2d"))
                self.button_emoji.append(loot.get_loot_emoji("I3d"))
                self.button_emoji.append(loot.get_loot_emoji("I4d"))
                self.num_buttons = 5
            case "Imbue":
                self.letter = "h"
                self.button_emoji.append(loot.get_loot_emoji("I1h"))
                self.button_emoji.append(loot.get_loot_emoji("I2h"))
                self.button_emoji.append(loot.get_loot_emoji("I3h"))
                self.button_emoji.append(loot.get_loot_emoji("I4h"))
                self.num_buttons = 5
            case "Cleanse":
                self.letter = "i"
                self.button_emoji.append(loot.get_loot_emoji("I1i"))
                self.button_emoji.append(loot.get_loot_emoji("I2i"))
                self.button_emoji.append(loot.get_loot_emoji("I3i"))
                self.button_emoji.append(loot.get_loot_emoji("I4i"))
                self.num_buttons = 5
            case "Augment":
                self.letter = "j"
                self.button_emoji.append(loot.get_loot_emoji("I1j"))
                self.button_emoji.append(loot.get_loot_emoji("I2j"))
                self.button_emoji.append(loot.get_loot_emoji("I3j"))
                self.button_emoji.append(loot.get_loot_emoji("I4j"))
                self.num_buttons = 5
            case "Implant":
                self.letter = "k"
                self.button_emoji.append(loot.get_loot_emoji("I4k"))
                self.num_buttons = 2
            case "Voidforge":
                self.letter = "l"
                self.button_emoji.append(loot.get_loot_emoji("I4l"))
                self.num_buttons = 2
            case _:
                self.num_buttons = 0

        # Assign response
        async def first_button_callback(button_interaction: discord.Interaction):
            item_code = f'I1{self.letter}'
            new_embed_msg = run_button(item_code)
            await button_interaction.response.edit_message(embed=new_embed_msg)

        async def second_button_callback(button_interaction: discord.Interaction):
            item_code = f'I2{self.letter}'
            new_embed_msg = run_button(item_code)
            await button_interaction.response.edit_message(embed=new_embed_msg)

        async def third_button_callback(button_interaction: discord.Interaction):
            item_code = f'I3{self.letter}'
            new_embed_msg = run_button(item_code)
            await button_interaction.response.edit_message(embed=new_embed_msg)

        async def fourth_button_callback(button_interaction: discord.Interaction):
            item_code = f'I4{self.letter}'
            new_embed_msg = run_button(item_code)
            await button_interaction.response.edit_message(embed=new_embed_msg)

        def run_button(item_code):
            method = forge_select.values[0]
            self.selected_item = inventory.read_custom_item(self.selected_id)
            result = inventory.craft_item(self.player_object, self.selected_item, item_code, method)
            if result == "0":
                outcome = "Failed!"
            elif result == "1":
                outcome = "Success!"
            elif result == "3":
                outcome = "Cannot upgrade further"
            elif result == "4":
                outcome = "Item not ready for upgrade"
            elif result == "5":
                outcome = "A roll has been successfully removed!"
            elif result == "6":
                outcome = "Item not eligible!"
            else:
                outcome = f"Out of Stock: {loot.get_loot_emoji(str(item_code))}"
            new_embed_msg = self.selected_item.create_citem_embed()
            new_embed_msg.add_field(name=outcome, value="", inline=False)
            return new_embed_msg

        async def button_multi_callback(button_interaction: discord.Interaction):
            self.selected_item = inventory.read_custom_item(self.selected_id)
            result = "0"
            overall = ""
            outcome = ""
            count = 0
            method = forge_select.values[0]
            match method:
                case "Enhance":
                    item_id_list = ["I1a", "I2a", "I3a"]
                case "Upgrade":
                    item_id_list = ["I1b", "I2b", "I3b"]
                case "Bestow":
                    item_id_list = ["I1c", "I2c", "I3c"]
                case "Open":
                    item_id_list = ["I1d", "I2d", "I3d"]
                case "Imbue":
                    item_id_list = ["I1h", "I2h", "I3h"]
                case "Cleanse":
                    item_id_list = ["I1i", "I2i", "I3i"]
                case "Augment":
                    item_id_list = ["I1j", "I2j", "I3j"]
                case "Implant":
                    item_id_list = ["I4k"]
                case "Voidforge":
                    item_id_list = ["I4l"]
                case _:
                    item_id_list = ["error"]
            for x in item_id_list:
                running = True
                while running and count < 50:
                    count += 1
                    result = inventory.craft_item(self.player_object, self.selected_item, x, method)
                    if result != "0" and result != "1":
                        running = False
                    elif result == "0" and overall == "":
                        overall = "All Failed"
                    elif result == "1":
                        if overall == "Success!":
                            overall = "!!MULTI-SUCCESS!!"
                        elif overall != "!!MULTI-SUCCESS!!":
                            overall = "Success!"
                if result == "3":
                    outcome = "Cannot upgrade further"
                    break
                elif result == "5":
                    overall = "Success!"
                    outcome = "A roll has been successfully removed!"
                    break
                elif result == "6":
                    overall = "Cannot Continue"
                    outcome = "Item not eligible!"
                elif count == 50:
                    outcome = f"Used: 50x{loot.get_loot_emoji(str(x))}"
                else:
                    outcome = f"Out of Stock: {loot.get_loot_emoji(str(x))}"
            new_embed_msg = self.selected_item.create_citem_embed()
            new_embed_msg.add_field(name=overall, value=outcome, inline=False)
            await button_interaction.response.edit_message(embed=new_embed_msg)

        async def reselect_callback(button_interaction: discord.Interaction):
            new_view = SelectView(self.player_object)
            await button_interaction.response.edit_message(view=new_view)

        async def button_cancel_callback(button_interaction: discord.Interaction):
            # cancel here
            await button_interaction.response.edit_message(view=None)

        self.button_label.append(f"T1 {forge_select.values[0]}")
        self.button_label.append(f"T2 {forge_select.values[0]}")
        self.button_label.append(f"T3 {forge_select.values[0]}")
        self.button_label.append(f"T4 {forge_select.values[0]}")
        self.button_label.append(f"Multi {forge_select.values[0]}")

        if self.num_buttons == 5:
            code = "I1" + self.letter
            self.button_emoji.append(loot.get_loot_emoji(code))
            code = "I2" + self.letter
            self.button_emoji.append(loot.get_loot_emoji(code))
            code = "I3" + self.letter
            self.button_emoji.append(loot.get_loot_emoji(code))
            code = "I4" + self.letter
            self.button_emoji.append(loot.get_loot_emoji(code))
            button_1 = Button(label=self.button_label[0], style=discord.ButtonStyle.success, emoji=self.button_emoji[0])
            button_2 = Button(label=self.button_label[1], style=discord.ButtonStyle.success, emoji=self.button_emoji[1])
            button_3 = Button(label=self.button_label[2], style=discord.ButtonStyle.success, emoji=self.button_emoji[2])
            button_4 = Button(label=self.button_label[3], style=discord.ButtonStyle.success, emoji=self.button_emoji[3])
            self.add_item(button_1)
            self.add_item(button_2)
            self.add_item(button_3)
            self.add_item(button_4)
            button_1.callback = first_button_callback
            button_2.callback = second_button_callback
            button_3.callback = third_button_callback
            button_4.callback = fourth_button_callback
        else:
            code = "I4" + self.letter
            self.button_emoji.append(loot.get_loot_emoji(code))
            button_4 = Button(label=self.button_label[3], style=discord.ButtonStyle.success, emoji=self.button_emoji[0])
            self.add_item(button_4)
            button_4.callback = fourth_button_callback

        button_multi = Button(label=self.button_label[4], style=discord.ButtonStyle.blurple, emoji="⬆️", row=1)
        button_reselect = Button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
        button_cancel = Button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=1)
        self.add_item(button_multi)
        button_multi.callback = button_multi_callback
        button_reselect.callback = reselect_callback
        self.add_item(button_reselect)
        self.add_item(button_cancel)
        button_cancel.callback = button_cancel_callback
        await interaction.response.edit_message(view=self)


class SelectView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.selected_item = None
        self.player_object = player_object
        self.value = None

    @discord.ui.select(
        placeholder="Select crafting base!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Weapon", description="Equipped Weapon"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Armour", description="Equipped Armour"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Accessory", description="Equipped Accessory"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wing", description="Equipped Wing"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crest", description="Equipped Paragon Crest")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
        match item_select.values[0]:
            case "Weapon":
                selected_item = self.player_object.equipped_weapon
            case "Armour":
                selected_item = self.player_object.equipped_armour
            case "Accessory":
                selected_item = self.player_object.equipped_acc
            case "Wing":
                selected_item = self.player_object.equipped_wing
            case "Crest":
                selected_item = self.player_object.equipped_crest
            case _:
                selected_item = 0
        if selected_item != 0:
            self.selected_item = inventory.read_custom_item(selected_item)
            embed_msg = self.selected_item.create_citem_embed()
            new_view = ForgeView(self.player_object, self.selected_item)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
        else:
            error_msg = "Not equipped"
            error_embed = create_error_embed(error_msg)
            await interaction.response.edit_message(embed=error_embed, view=None)


# Inventory menu
class InventoryView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.select(
        placeholder="Select Inventory Type!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Equipment", description="Stored Equipment"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Items", description="Regular Items")
        ]
    )
    async def inventory_callback(self, interaction: discord.Interaction, inventory_select: discord.ui.Select):
        if inventory_select.values[0] == "Equipment":
            inventory_title = f'{self.user.player_username}\'s Equipment:\n'
            player_inventory = inventory.display_cinventory(self.user.player_id)
        else:
            inventory_title = f'{self.user.player_username}\'s Inventory:\n'
            player_inventory = inventory.display_binventory(self.user.player_id)

        new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title=inventory_title,
                                  description=player_inventory)
        await interaction.response.edit_message(embed=new_embed)


# Refinery Menus
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
                emoji="<a:eenergy:1145534127349706772>", label="Dragon Heart Gem", description="Refine dragon heart gems"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Dragon Wing", description="Refine equippable wings"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Paragon Crest", description="Refine equippable crests"),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Fabled Weapon", description="Refine equippable crests")
        ]
    )
    async def ref_select_callback(self, interaction: discord.Interaction, ref_select: discord.ui.Select):
        selected_type = ref_select.values[0]
        match selected_type:
            case "Dragon Heart Gem":
                tier_view = RefineryGemView(self.player_user, selected_type)
            case "Dragon Wing":
                tier_view = RefineryWingView(self.player_user, selected_type)
            case "Paragon Crest":
                tier_view = RefineryCrestView(self.player_user, selected_type)
            case _:
                tier_view = RefineryWeaponView(self.player_user, selected_type)

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

    @discord.ui.button(label="Tier 6", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_six_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 6
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_view = RefSelectView(self.player_user)
        await interaction.response.edit_message(view=new_view)

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

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_view = RefSelectView(self.player_user)
        await interaction.response.edit_message(view=new_view)

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

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_view = RefSelectView(self.player_user)
        await interaction.response.edit_message(view=new_view)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class RefineryWeaponView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""

    @discord.ui.button(label="Rift Weapon", style=discord.ButtonStyle.success, emoji="✅")
    async def rift_weapon_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 5
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="True Name", style=discord.ButtonStyle.success, emoji="✅")
    async def relic_weapon_callback(self, interaction: discord.Interaction, button: discord.Button):
        selected_tier = 6
        embed_msg = refine_item(self.player_user, self.selected_type, selected_tier)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_view = RefSelectView(self.player_user)
        await interaction.response.edit_message(view=new_view)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


def refine_item(player_user, selected_type, selected_tier):
    item_id = f"I{str(selected_tier)}"

    match selected_type:
        case "Dragon Heart Gem":
            item_id += "n"
        case "Dragon Wing":
            item_id += "m"
        case "Paragon Crest":
            item_id += "o"
        case _:
            item_id += "x"

    if inventory.check_stock(player_user, item_id) > 0:
        inventory.update_stock(player_user, item_id, -1)
        new_item = inventory.try_refine(player_user.player_id, selected_type, selected_tier)
        if new_item.item_id != 0:
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


# Gem inlay menus
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
        no_socket = True
        self.player_user.get_equipped()
        match selected_type:
            case "Weapon":
                selected_item = self.player_user.equipped_weapon
            case "Armour":
                selected_item = self.player_user.equipped_armour
            case "Accessory":
                selected_item = self.player_user.equipped_acc
            case "Wings":
                selected_item = self.player_user.equipped_wing
            case _:
                selected_item = self.player_user.equipped_crest
        if self.player_user.equipped_weapon != 0:
            e_item = inventory.read_custom_item(selected_item)
            if e_item.item_num_sockets == 1:
                no_socket = False
                embed_msg = e_item.create_citem_embed()
                confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
        else:
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="Inlay Failed.",
                                      description="No item equipped in this slot")
            await interaction.response.edit_message(embed=embed_msg)
        if no_socket:
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


# Explore menus
class TreasureView(discord.ui.View):
    def __init__(self, user, new_item, msg, item_type):
        super().__init__(timeout=None)
        self.user = user
        self.new_item = new_item
        self.msg = msg
        self.item_type = item_type

    @discord.ui.button(label="Keep", style=discord.ButtonStyle.success, emoji="✅")
    async def keep_callback(self, interaction: discord.Interaction, choice_select: discord.ui.Select):
        if not inventory.if_custom_exists(self.new_item.item_id):
            message = inventory.inventory_add_custom_item(self.new_item)
            self.msg.add_field(name="", value=message, inline=False)
        await interaction.response.edit_message(embed=self.msg, view=None)

    @discord.ui.button(label="Discard", style=discord.ButtonStyle.red, emoji="✖️")
    async def discard_callback(self, interaction: discord.Interaction, choice_select: discord.ui.Select):
        message = f'You have discarded the {self.item_type}'
        self.msg.add_field(name="", value=message, inline=False)
        await interaction.response.edit_message(embed=self.msg, view=None)

    @discord.ui.button(label="Try Again", style=discord.ButtonStyle.blurple, emoji="↪️")
    async def again_callback(self, interaction: discord.Interaction, choice_select: discord.ui.Select):
        if self.user.spend_stamina(25):
            match self.item_type:
                case "weapon":
                    item_type = "W"
                case "armour":
                    item_type = "A"
                case "accessory":
                    item_type = "Y"
                case _:
                    item_type = "W"
            inventory.CustomItem(self.user.player_id, item_type, 1)
            embed_msg = self.new_item.create_citem_embed()
            inquiry = f"Would you like to keep or discard this {self.item_type}?"
            gear_colours = inventory.get_gear_tier_colours(self.new_item.item_tier)
            tier_emoji = gear_colours[1]
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(self.new_item.item_tier)} item found!',
                                value=inquiry, inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=self)
        else:
            await interaction.response.send_message('Not enough !stamina')


class EmptyRoomView(discord.ui.View):
    def __init__(self, player_user, room):
        super().__init__(timeout=None)
        self.player = player_user
        self.room = room

    @discord.ui.button(label="Stick Left", style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def left_callback(self, interaction: discord.Interaction, button: discord.Button):
        if self.room.is_trap:
            new_room = explore.generate_trap_room(self.player, self.room, "side")
        else:
            new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Proceed Forward", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def middle_callback(self, interaction: discord.Interaction, button: discord.Button):
        if self.room.is_trap:
            new_room = explore.generate_trap_room(self.player, self.room, "middle")
        else:
            new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Stick Right", style=discord.ButtonStyle.blurple, emoji="➡️")
    async def right_callback(self, interaction: discord.Interaction, button: discord.Button):
        if self.room.is_trap:
            new_room = explore.generate_trap_room(self.player, self.room, "side")
        else:
            new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red, emoji="✖️")
    async def flee_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class MonsterRoomView(discord.ui.View):
    def __init__(self, player_user, room):
        super().__init__(timeout=None)
        self.player = player_user
        self.room = room

    @discord.ui.button(label="Fight", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def fight_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_room = self.room
        new_room.room_type = "Transition Room"
        player_hp = f'{self.player.player_cHP} / {self.player.player_mHP} HP'
        dmg_msg = f'You take {new_room.monster_damage} damage!'
        new_room.embed = discord.Embed(title=player_hp, description=dmg_msg, colour=new_room.room_colour)
        if self.player.player_cHP <= 0:
            self.player.player_cHP = 0
            over_msg = "EXPLORATION OVER"
            over_description = "Having taken too much damage, you are forced to return from your exploration."
            new_room.embed.add_field(name=over_msg, value=over_description, inline=False)
        if self.player.player_cHP == 0:
            new_view = None
        else:
            new_view = explore.generate_room_view(self.player, new_room)
        await interaction.response.edit_message(embed=new_room.embed, view=new_view)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red, emoji="✖️")
    async def flee_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class SafeRoomView(discord.ui.View):
    def __init__(self, player_user, room):
        super().__init__(timeout=None)
        self.player = player_user
        self.room = room

    @discord.ui.button(label="Rest", style=discord.ButtonStyle.blurple, emoji="➕")
    async def rest_callback(self, interaction: discord.Interaction, button: discord.Button):
        if self.room.is_trap:
            new_room = explore.generate_trap_room(self.player, self.room, "")
        else:
            heal_amount = random.randint(25, 100) * self.room.room_tier
            self.player.player_cHP += heal_amount
            if self.player.player_cHP > self.player.player_mHP:
                self.player.player_cHP = self.player.player_mHP
            player_hp = f'{self.player.player_cHP} / {self.player.player_mHP} HP'
            heal_msg = f"Resting restored {heal_amount} HP."
            new_room = self.room
            new_room.room_type = "Transition Room"
            new_room.embed = discord.Embed(title=player_hp, description=heal_msg, colour=new_room.room_colour)
            new_room.room_view = explore.generate_room_view(self.player, new_room)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Move on", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def move_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red, emoji="✖️")
    async def flee_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class TreasureRoomView(discord.ui.View):
    def __init__(self, player_user, room):
        super().__init__(timeout=None)
        self.player = player_user
        self.room = room

    @discord.ui.button(label="Open Chest", style=discord.ButtonStyle.blurple, emoji="➕")
    async def open_callback(self, interaction: discord.Interaction, button: discord.Button):
        if self.room.is_trap:
            new_room = explore.generate_trap_room(self.player, self.room, "")
            new_view = new_room.room_view
            embed_msg = new_room.embed
        else:
            random_type = random.randint(1, 5)
            match random_type:
                case 1 | 2:
                    item_type = "W"
                case 3 | 4:
                    item_type = "A"
                case _:
                    item_type = "Y"
            new_tier = inventory.generate_random_tier()
            for x in range(self.room.room_tier - 1):
                check_tier = inventory.generate_random_tier()
                if check_tier > new_tier:
                    new_tier = check_tier
            new_object = inventory.CustomItem(self.player.player_id, item_type, new_tier)
            embed_msg = new_object.create_citem_embed()
            gear_colours = inventory.get_gear_tier_colours(new_object.item_tier)
            tier_emoji = gear_colours[1]
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(new_object.item_tier)} item found!',
                                value="",
                                inline=False)
            new_view = ItemRoomView(self.player, self.room, new_object)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Move on", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def move_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_room = explore.generate_new_room(self.player)
        new_view = explore.generate_room_view(self.player, new_room)
        embed_msg = discord.Embed(colour=new_room.room_colour,
                                  title=new_room.room_type,
                                  description=new_room.room_description)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red, emoji="✖️")
    async def flee_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class ItemRoomView(discord.ui.View):
    def __init__(self, player_user, room, item):
        super().__init__(timeout=None)
        self.player = player_user
        self.room = room
        self.item = item

    @discord.ui.button(label="Claim Item", style=discord.ButtonStyle.blurple, emoji="➕")
    async def claim_callback(self, interaction: discord.Interaction, button: discord.Button):
        inventory.inventory_add_custom_item(self.item)
        new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Leave Item", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def move_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red, emoji="✖️")
    async def flee_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class TrapRoomView(discord.ui.View):
    def __init__(self, player_user, room):
        super().__init__(timeout=None)
        self.player = player_user
        self.room = room

    @discord.ui.button(label="Escape", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def move_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red, emoji="✖️")
    async def flee_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class TransitionRoomView(discord.ui.View):
    def __init__(self, player_user, room):
        super().__init__(timeout=None)
        self.player = player_user
        self.room = room

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def move_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_room = explore.generate_new_room(self.player)
        new_view = new_room.room_view
        embed_msg = new_room.embed
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red, emoji="✖️")
    async def flee_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class StaminaView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player = player_user

    @discord.ui.button(label="Lesser Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t1_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = use_stamina_potion(self.player, "I1s", 50)
        await interaction.response.edit_message(embed=embed_msg, view=self)

    @discord.ui.button(label="Stamina Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t2_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = use_stamina_potion(self.player, "I2s", 250)
        await interaction.response.edit_message(embed=embed_msg, view=self)

    @discord.ui.button(label="Greater Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t3_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = use_stamina_potion(self.player, "I3s", 500)
        await interaction.response.edit_message(embed=embed_msg, view=self)

    @discord.ui.button(label="Ultimate Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t4_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = use_stamina_potion(self.player, "I4s", 1000)
        await interaction.response.edit_message(embed=embed_msg, view=self)


def use_stamina_potion(player_object, item_id, restore_amount):
    potion_stock = inventory.check_stock(player_object, item_id)
    if potion_stock > 0:
        inventory.update_stock(player_object, item_id, -1)
        player_object.player_stamina += restore_amount
        if player_object.player_stamina > 2000:
            player_object.player_stamina = 2000
        player_object.set_player_field("stamina", player_object.player_stamina)
    embed_msg = player_object.create_stamina_embed()
    return embed_msg


class BindingTierView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select Essence Tier!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 1", description="Tier 1 Essences"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 2", description="Tier 2 Essences"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 3", description="Tier 3 Essences"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 4", description="Tier 4 Essences"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Tier 5+", description="Tier 5+ Essences")
        ]
    )
    async def bind_tier_callback(self, interaction: discord.Interaction, bind_tier_select: discord.ui.Select):
        match bind_tier_select.values[0]:
            case "Tier 1":
                new_view = BindingT1View(self.player_user)
            case "Tier 2":
                new_view = BindingT2View(self.player_user)
            case "Tier 3":
                new_view = BindingT3View(self.player_user)
            case "Tier 4":
                new_view = BindingT4View(self.player_user)
            case _:
                new_view = BindingT5View(self.player_user)
        await interaction.response.edit_message(view=new_view)


class BindingT1View(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select Essence!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="0", description="Essence of The Reflection"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="I", description="Essence of The Magic"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="VI", description="Essence of The Love"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="IX", description="Essence of The Memory"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XIV", description="Essence of The Clarity")
        ]
    )
    async def bind_select_callback(self, interaction: discord.Interaction, bind_select: discord.ui.Select):
        new_view = PerformRitualView(self.player_user, bind_select.values[0])
        await interaction.response.edit_message(view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title="Pandora's Binding Ritual",
                                  description="Let me know if you've acquired any new essences!")
        embed_msg.set_image(url="")
        new_view = BindingTierView(self.player_user)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class BindingT2View(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select Essence!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XVI", description="Essence of The Star"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XVII", description="Essence of The Moon"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XIX", description="Essence of The Sun"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XX", description="Essence of The Requiem"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XXI", description="Essence of The Creation")
        ]
    )
    async def bind_select_callback(self, interaction: discord.Interaction, bind_select: discord.ui.Select):
        new_view = PerformRitualView(self.player_user, bind_select.values[0])
        await interaction.response.edit_message(view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title="Pandora's Binding Ritual",
                                  description="Let me know if you've acquired any new essences!")
        embed_msg.set_image(url="")
        new_view = BindingTierView(self.player_user)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class BindingT3View(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select Essence!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="V", description="Essence of The Duality"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="X", description="Essence of The Temporal"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XI", description="Essence of The Heavens"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XII", description="Essence of The Abyss"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XIII", description="Essence of The Death")
        ]
    )
    async def bind_select_callback(self, interaction: discord.Interaction, bind_select: discord.ui.Select):
        new_view = PerformRitualView(self.player_user, bind_select.values[0])
        await interaction.response.edit_message(view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title="Pandora's Binding Ritual",
                                  description="Let me know if you've acquired any new essences!")
        embed_msg.set_image(url="")
        new_view = BindingTierView(self.player_user)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class BindingT4View(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select Essence!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="II", description="Essence of The Celestial"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="VII", description="Essence of The Dragon"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="VIII", description="Essence of The Behemoth"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XV", description="Essence of The Primordial"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XVI", description="Essence of The Fortress")
        ]
    )
    async def bind_select_callback(self, interaction: discord.Interaction, bind_select: discord.ui.Select):
        new_view = PerformRitualView(self.player_user, bind_select.values[0])
        await interaction.response.edit_message(view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title="Pandora's Binding Ritual",
                                  description="Let me know if you've acquired any new essences!")
        embed_msg.set_image(url="")
        new_view = BindingTierView(self.player_user)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class BindingT5View(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select Essence!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="III", description="Essence of The Void"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="IV", description="Essence of The Infinite")
        ]
    )
    async def bind_select_callback(self, interaction: discord.Interaction, bind_select: discord.ui.Select):
        new_view = PerformRitualView(self.player_user, bind_select.values[0])
        await interaction.response.edit_message(view=new_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title="Pandora's Binding Ritual",
                                  description="Let me know if you've acquired any new essences!")
        embed_msg.set_image(url="")
        new_view = BindingTierView(self.player_user)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class PerformRitualView(discord.ui.View):
    def __init__(self, player_user, essence_type):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.essence_type = essence_type

    @discord.ui.button(label="Bind Essence", style=discord.ButtonStyle.blurple, emoji="<a:eshadow2:1141653468965257216>")
    async def attempt_bind(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = binding_ritual(self.player_user, self.essence_type)
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title="Pandora's Binding Ritual",
                                  description="Let me know if you've acquired any new essences!")
        embed_msg.set_image(url="")
        new_view = BindingTierView(self.player_user)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


def binding_ritual(player_object, essence_type):
    filename = ""
    essence_id = f't{essence_type}'
    essence_stock = inventory.check_stock(player_object, essence_id)
    if essence_stock > 0:
        inventory.update_stock(player_object, essence_id, -1)
        random_num = random.randint(1, 10)
        match random_num:
            case 1:
                variant_num = 3
            case 2 | 3:
                variant_num = 2
            case 4 | 5 | 6:
                variant_num = 1
            case _:
                variant_num = 0
        if variant_num == 0:
            result = "Binding Failed!"
            description_msg = "The essence is gone."
        else:
            name_position = tarot.get_numeral_by_number(essence_type)
            card_name = tarot.tarot_card_list(name_position)
            tarot_check = tarot.check_tarot(player_object.player_id, card_name)
            if tarot_check:
                new_qty = tarot_check.card_qty + 1
                tarot_check.set_tarot_field("card_qty", new_qty)
            else:
                new_tarot = tarot.TarotCard(player_object.player_id, essence_type, variant_num, card_name,
                                            1, 0, 0, 0)
                new_tarot.add_tarot_card()
            result = "Binding Successful!"
            inventory.update_tarot_inventory(player_object, card_file)
            description_msg = "The sealed tarot card has been added to your collection."
    else:
        print(essence_id)
        essence_emoji = loot.get_loot_emoji(essence_id)
        result = "Ritual Failed!"
        description_msg = f"{essence_emoji} Out of Stock!"

    embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                              title=result,
                              description=description_msg)
    embed_msg.set_image(url=filename)
    return embed_msg


class CollectionView(discord.ui.View):
    def __init__(self, player_user, embed_msg):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg
        self.current_position = 0
        self.current_variant = 1

    @discord.ui.button(label="View Collection", style=discord.ButtonStyle.blurple, emoji="✅")
    async def view_collection(self, interaction: discord.Interaction, button: discord.Button):
        new_msg, x, y = cycle_tarot(self.player_user, self.embed_msg, 0, 1, 0)
        new_view = TarotView(self.player_user, self.embed_msg)
        await interaction.response.edit_message(embed=new_msg, view=new_view)


class TarotView(discord.ui.View):
    def __init__(self, player_user, embed_msg):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg
        self.current_position = 0
        self.current_variant = 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous_card(self, interaction: discord.Interaction, button: discord.Button):
        direction = -1
        current_message = self.embed_msg.clear_fields()
        new_msg, self.current_position, self.current_variant = cycle_tarot(self.player_user,
                                                                           current_message,
                                                                           self.current_position,
                                                                           self.current_variant,
                                                                           direction)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_card(self, interaction: discord.Interaction, button: discord.Button):
        direction = 1
        current_message = self.embed_msg.clear_fields()
        new_msg, self.current_position, self.current_variant = cycle_tarot(self.player_user,
                                                                           current_message,
                                                                           self.current_position,
                                                                           self.current_variant,
                                                                           direction)
        await interaction.response.edit_message(embed=new_msg)


def cycle_tarot(player_owner, current_msg, current_position, current_variant, direction):
    card_num_list = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                     "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
    card_name_list = ["Karma, The Reflection", "Runa, The Magic", "Pandora, The Celestial", "Oblivia, The Void",
                      "Akasha, The Infinite", "Arkaya, The Duality", "Kama, The Love", "Astratha, The Dragon",
                      "Tyra, The Behemoth", "Alaya, The Memory", "Chrona, The Temporal", "Nua, The Heavens",
                      "Rua, The Abyss", "Thana, The Death", "Arcelia, The Clarity", "Diabla, The Primordial",
                      "Aurora, The Fortress", "Nova, The Star", "Luna, The Moon", "Luma, The Sun",
                      "Aria, The Requiem", "Ultima, The Creation"]
    if current_variant == 1 and direction == -1:
        new_variant = 3
        new_position = current_position + direction
        if new_position == -1:
            new_position = 21
    elif current_variant == 3 and direction == 1:
        new_variant = 1
        new_position = current_position + direction
        if new_position == 22:
            new_position = 0
    else:
        new_variant = current_variant + direction
        new_position = current_position
    current_msg.clear_fields()
    new_msg = current_msg
    card_checker = tarot.check_tarot(player_owner.player_id, card_name_list[new_position], new_variant)
    if card_checker:
        card_qty = card_checker.card_qty
        filename = card_checker.card_image_link
    else:
        card_qty = 0
        filename = ""
    new_msg.add_field(name=f"Tarot Card: {card_num_list[new_position]} {card_name_list[new_position]}",
                      value=f"Variant {new_variant}",
                      inline=False)
    new_msg.add_field(name=f"",
                      value=f"Quantity: {card_qty}",
                      inline=False)
    new_msg.set_image(url=filename)
    return new_msg, new_position, new_variant


class GearView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.current_position = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous_gear(self, interaction: discord.Interaction, button: discord.Button):
        direction = -1
        new_msg, self.current_position = cycle_gear(self.player_user, self.current_position, direction)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_gear(self, interaction: discord.Interaction, button: discord.Button):
        direction = 1
        new_msg, self.current_position = cycle_gear(self.player_user, self.current_position, direction)
        await interaction.response.edit_message(embed=new_msg)


def cycle_gear(user, current_position, direction):
    no_item = ""
    if current_position == 0 and direction == -1:
        new_position = 4
    elif current_position == 4 and direction == 1:
        new_position = 0
    else:
        new_position = current_position + direction

    match new_position:
        case 0:
            item_type = "Weapon"
            selected_item = user.equipped_weapon
        case 1:
            item_type = "Armour"
            selected_item = user.equipped_armour
        case 2:
            item_type = "Accessory"
            selected_item = user.equipped_acc
        case 3:
            item_type = "Wing"
            selected_item = user.equipped_wing
        case _:
            item_type = "Crest"
            selected_item = user.equipped_crest
    if selected_item != 0:
        equipped_item = inventory.read_custom_item(selected_item)
        new_msg = equipped_item.create_citem_embed()
    else:
        no_item = item_type.lower()
        new_msg = discord.Embed(colour=discord.Colour.dark_gray(),
                                title=f"Equipped {item_type}",
                                description=f"No {no_item} is equipped")
    return new_msg, new_position


class ManageCustomItemView(discord.ui.View):
    def __init__(self, player_user, item_id):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.item_id = item_id

    @discord.ui.button(label="Equip", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def equip_item(self, interaction: discord.Interaction, button: discord.Button):
        selected_item = inventory.read_custom_item(self.item_id)
        new_msg = selected_item.create_citem_embed()
        response = self.player_user.equip(selected_item)
        new_msg.add_field(name=response, value="", inline=False)
        await interaction.response.edit_message(embed=new_msg, view=None)

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.success, emoji="💲")
    async def sell_item(self, interaction: discord.Interaction, button: discord.Button):
        selected_item = inventory.read_custom_item(self.item_id)
        embed_msg = selected_item.create_citem_embed()
        response_embed = inventory.sell(self.player_user, selected_item, embed_msg)
        await interaction.response.edit_message(embed=response_embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


def create_error_embed(error_msg):
    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                              title="Error",
                              description=error_msg)
    return embed_msg


class QuestView(discord.ui.View):
    def __init__(self, player_user, quest_object):
        super().__init__(timeout=None)
        self.player_object = player_user
        self.quest_object = quest_object

    @discord.ui.button(label="Hand In", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def hand_in(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg, is_completed = self.quest_object.hand_in(self.player_object)
        if is_completed:
            reward_view = RewardView(self.player_object)
            if self.quest_object.award_role != "":
                add_role = discord.utils.get(interaction.guild.roles, name=self.quest_object.award_role)
                await interaction.user.add_roles(add_role)
                if self.player_object.player_echelon != 1:
                    previous_role = discord.utils.get(interaction.guild.roles,
                                                      name=role_list[(self.player_object.player_echelon - 2)])
                    remove_role = discord.utils.get(interaction.guild.roles, name=previous_role)
                    await interaction.user.remove_roles(remove_role)
            await interaction.response.edit_message(embed=embed_msg, view=reward_view)
        else:
            embed_msg.add_field(name="", value="Quest is not yet completed!", inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class RewardView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_object = player_user

    @discord.ui.button(label="Next Quest", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def next_quest(self, interaction: discord.Interaction, button: discord.Button):
        end_quest = 50
        if self.player_object.player_quest <= end_quest:
            current_quest = self.player_object.player_quest
            quest_object = quest.get_quest(current_quest, self.player_object)
            token_count = self.player_object.check_tokens(current_quest)
            quest_object.set_quest_output(token_count)
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title=quest_object.quest_title,
                                      description=quest_object.story_message)
            embed_msg.add_field(name=f"Quest", value=quest_object.quest_output, inline=False)
            quest_view = menus.QuestView(self.player_object, quest_object)
            await ctx.send(embed=embed_msg, view=quest_view)
        else:
            embed_msg.add_field(name="", value="Quest is not yet completed!", inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(view=None)


class ClassSelect(discord.ui.View):
    def __init__(self, player_name, username, ctx):
        super().__init__(timeout=None)
        self.username = username
        self.player_name = player_name
        self.ctx = ctx

    @discord.ui.select(
        placeholder="Select a class!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:cB:1154266777396711424>", label="Knight", description="The Valiant Knight"),
            discord.SelectOption(
                emoji="<:cA:1150195102589931641>", label="Ranger", description="The Precise Ranger"),
            discord.SelectOption(
                emoji="<:cC:1150195246588764201>", label="Mage", description="The Arcane Mage"),
            discord.SelectOption(
                emoji="❌", label="Assassin", description="The Stealthy Assassin"),
            discord.SelectOption(
                emoji="❌", label="Weaver", description="The Mysterious Weaver"),
            discord.SelectOption(
                emoji="❌", label="Rider", description="The Mounted Rider"),
            discord.SelectOption(
                emoji="<:cD:1150195280969478254>", label="Summoner", description="The Trusted Summoner")
        ]
    )
    async def class_callback(self, interaction: discord.Interaction, class_select: discord.ui.Select):
        new_player = player.PlayerProfile()
        new_player.player_name = self.player_name
        new_player.player_username = self.username
        chosen_class = pandorabot.class_icon_dict[class_select.values[0]]
        response = new_player.add_new_player(chosen_class)
        chosen_class_role = f"Class Role - {class_select.values[0]}"
        add_role = discord.utils.get(interaction.guild.roles, name=chosen_class_role)
        remove_role = discord.utils.get(interaction.guild.roles, name="Class Role - Rat (No Class)")
        await interaction.user.add_roles(add_role)
        await interaction.user.remove_roles(remove_role)
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title="Register",
                                  description=response)
        await interaction.response.edit_message(embed=embed_msg, view=None)
