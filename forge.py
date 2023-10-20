# Forge menu
import discord
from discord.ui import Button, View
import inventory
import loot
import random
import player
import tarot
import mydb
import pandorabot
import quest
import asyncio
import bazaar


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
        try:
            if interaction.user.name == self.player_object.player_name:
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
                        self.button_emoji.append(loot.get_loot_emoji("I5l"))
                        self.num_buttons = 2
                    case _:
                        self.num_buttons = 0

                # Assign response
                async def first_button_callback(button_interaction: discord.Interaction):
                    try:
                        if button_interaction.user.name == self.player_object.player_name:
                            item_code = f'I1{self.letter}'
                            new_embed_msg = run_button(item_code)
                            await button_interaction.response.edit_message(embed=new_embed_msg)
                    except Exception as e:
                        print(e)

                async def second_button_callback(button_interaction: discord.Interaction):
                    try:
                        if button_interaction.user.name == self.player_object.player_name:
                            item_code = f'I2{self.letter}'
                            new_embed_msg = run_button(item_code)
                            await button_interaction.response.edit_message(embed=new_embed_msg)
                    except Exception as e:
                        print(e)

                async def third_button_callback(button_interaction: discord.Interaction):
                    try:
                        if button_interaction.user.name == self.player_object.player_name:
                            item_code = f'I3{self.letter}'
                            new_embed_msg = run_button(item_code)
                            await button_interaction.response.edit_message(embed=new_embed_msg)
                    except Exception as e:
                        print(e)

                async def fourth_button_callback(button_interaction: discord.Interaction):
                    try:
                        if button_interaction.user.name == self.player_object.player_name:
                            if self.letter == "l":
                                item_code = "I5l"
                            else:
                                item_code = f'I4{self.letter}'
                            new_embed_msg = run_button(item_code)
                            await button_interaction.response.edit_message(embed=new_embed_msg)
                    except Exception as e:
                        print(e)

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
                    try:
                        if button_interaction.user.name == self.player_object.player_name:
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
                                    item_id_list = ["I5l"]
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
                    except Exception as e:
                        print(e)

                async def reselect_callback(button_interaction: discord.Interaction):
                    try:
                        if button_interaction.user.name == self.player_object.player_name:
                            new_view = SelectView(self.player_object)
                            await button_interaction.response.edit_message(view=new_view)
                    except Exception as e:
                        print(e)

                async def button_cancel_callback(button_interaction: discord.Interaction):
                    try:
                        if button_interaction.user.name == self.player_object.player_name:
                            await button_interaction.response.edit_message(view=None)
                    except Exception as e:
                        print(e)

                self.clear_items()
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
                    if self.letter == "l":
                        code = "I5l"
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
        except Exception as z:
            print(z)


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
        try:
            if interaction.user.name == self.player_object.player_name:
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
        except Exception as e:
            print(e)