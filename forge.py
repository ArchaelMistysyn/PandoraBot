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
fae_icon = [element_fire, element_water, element_lightning, element_earth, element_wind, element_ice,
            element_dark, element_light, element_celestial]


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
                else:
                    error_msg = "Not equipped"
                    embed_msg = menus.create_error_embed(error_msg)
                    new_view = None
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class ForgeView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Enhance", description="Enhance the item"),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Upgrade", description="Upgrade the item quality."),
            discord.SelectOption(
                emoji="<a:eshadow2:1141653468965257216>", label="Reforge",
                description="Reforge an item with a new ability and base stats."),
            discord.SelectOption(
                emoji="⚫", label="Add Socket", description="Add an open socket to an item."),
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Cosmic Augment", description="Add/Modify item rolls."),
            discord.SelectOption(
                emoji="<:ehammer:1145520259248427069>", label="Astral Augment", description="Add/Modify item rolls."),
            discord.SelectOption(
                emoji="<a:eorigin:1145520263954440313>", label="Implant Element", description="Gain new elements.")
        ]
    )
    async def forge_callback(self, interaction: discord.Interaction, forge_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                match forge_select.values[0]:
                    case "Enhance":
                        new_view = ElementSelectView(self.player_object, self.selected_item, "Enhance")
                    case "Upgrade":
                        new_view = UpgradeView(self.player_object, self.selected_item)
                    case "Reforge":
                        new_view = ReforgeView(self.player_object, self.selected_item)
                    case "Add Socket":
                        new_view = SocketView(self.player_object, self.selected_item)
                    case "Cosmic Augment":
                        new_view = CosmicAugmentView(self.player_object, self.selected_item)
                    case "Astral Augment":
                        new_view = AstralAugmentView(self.player_object, self.selected_item)
                    case "Implant Element":
                        new_view = ElementSelectView(self.player_object, self.selected_item, "Implant")
                    case _:
                        new_view = None
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class ElementSelectView(discord.ui.View):
    def __init__(self, player_object, selected_item, method):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.method = method

    @discord.ui.select(
        placeholder="Select the element to use.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji=fae_icon[0], label="Fire",
                value="0", description="Use fire item."),
            discord.SelectOption(
                emoji=fae_icon[1], label="Water",
                value="1", description="Use water item."),
            discord.SelectOption(
                emoji=fae_icon[2], label="Lighting",
                value="2", description="Use lightning item."),
            discord.SelectOption(
                emoji=fae_icon[3], label="Earth",
                value="3", description="Use earth item."),
            discord.SelectOption(
                emoji=fae_icon[4], label="Wind",
                value="4", description="Use wind item."),
            discord.SelectOption(
                emoji=fae_icon[5], label="Ice",
                value="5", description="Use ice item."),
            discord.SelectOption(
                emoji=fae_icon[6], label="Shadow",
                value="6", description="Use shadow item."),
            discord.SelectOption(
                emoji=fae_icon[7], label="Light",
                value="7", description="Use light item."),
            discord.SelectOption(
                emoji=fae_icon[8], label="Celestial",
                value="8", description="Use celestial item.")
        ]
    )
    async def element_callback(self, interaction: discord.Interaction, element_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                selected_element = int(element_select.values[0])
                if self.method == "Enhance":
                    new_view = EnhanceView(self.player_object, self.selected_item, selected_element)
                else:
                    new_view = ImplantView(self.player_object, self.selected_item, selected_element)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class EnhanceView(discord.ui.View):
    def __init__(self, player_object, selected_item, element):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.element = element

    @discord.ui.button(label="Enhance", style=discord.ButtonStyle.success, emoji="<a:eenergy:1145534127349706772>")
    async def enhance_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = f"Fae{self.element}"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Enhance")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def button_cancel_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                await button_interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class UpgradeView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Reinforce", style=discord.ButtonStyle.success, emoji="<:eore:1145534835507593236>")
    async def reinforce_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i5o"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Reinforce")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Bestow", style=discord.ButtonStyle.success, emoji="<:esoul:1145520258241806466>")
    async def bestow_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i5s"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Bestow")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def button_cancel_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                await button_interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class ReforgeView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Reforge", style=discord.ButtonStyle.success, emoji="<a:eshadow2:1141653468965257216>")
    async def reforge_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i3f"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Reforge")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def button_cancel_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                await button_interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class SocketView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Add Socket", style=discord.ButtonStyle.success, emoji="⚫")
    async def socket_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i3k"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Open")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def button_cancel_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                await button_interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class CosmicAugmentView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Star Fusion", style=discord.ButtonStyle.success, emoji="<:ehammer:1145520259248427069>")
    async def star_fusion_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i4h"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Star Fusion")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Attunement", style=discord.ButtonStyle.success, emoji="<:eprl:1148390531345432647>")
    async def attunement_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i4p"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Attunement")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def button_cancel_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                await button_interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class AstralAugmentView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Pulsar Fusion", style=discord.ButtonStyle.success, emoji="<:ehammer:1145520259248427069>")
    async def pulsar_fusion_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i5hP"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Pulsar Fusion")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Quasar Fusion", style=discord.ButtonStyle.success, emoji="<:ehammer:1145520259248427069>")
    async def quasar_fusion_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = "i5hS"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Quasar Fusion")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def button_cancel_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                await button_interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class ImplantView(discord.ui.View):
    def __init__(self, player_object, selected_item, element):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.element = element

    @discord.ui.button(label="Implant", style=discord.ButtonStyle.success, emoji="<a:eorigin:1145520263954440313>")
    async def implant_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                material_id = f"Origin{self.element}"
                embed_msg = run_button(self.player_object, self.selected_item, material_id, "Implant")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def button_cancel_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                await button_interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


def run_button(player_object, selected_item, material_id, method):
    loot_item = loot.BasicItem(material_id)
    reload_item = inventory.read_custom_item(selected_item.item_id)
    result = craft_item(player_object, reload_item, loot_item, method)
    match result:
        case "0":
            outcome = "Failed!"
        case "1":
            outcome = "Success!"
        case "2":
            outcome = "Cannot upgrade further."
        case "3":
            outcome = "Item not eligible."
        case "4":
            outcome = "This element cannot be used."
        case _:
            outcome = f"Out of Stock: {loot_item.item_emoji}"
    new_embed_msg = reload_item.create_citem_embed()
    new_embed_msg.add_field(name=outcome, value="", inline=False)
    return new_embed_msg


def craft_item(player_object, selected_item, material_item, method):
    success_rate = material_item.item_base_rate
    player_stock = inventory.check_stock(player_object, material_item.item_id)
    if player_stock > 0:
        success_check = random.randint(1, 100)
        match method:
            case "Enhance":
                outcome = enhance_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Reinforce":
                outcome = reinforce_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Bestow":
                outcome = bestow_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Reforge":
                outcome = reforge_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Open":
                outcome = open_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Star Fusion":
                outcome = star_fusion_item(player_object, selected_item, material_item, success_rate, success_check, 2)
            case "Pulsar Fusion":
                outcome = star_fusion_item(player_object, selected_item, material_item, success_rate, success_check, 0)
            case "Quasar Fusion":
                outcome = star_fusion_item(player_object, selected_item, material_item, success_rate, success_check, 1)
            case "Attunement":
                outcome = attune_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Implant":
                outcome = implant_item(player_object, selected_item, material_item, success_rate, success_check)
            case _:
                outcome = "Error"
    else:
        outcome = material_item.item_id
    return outcome


def update_crafted_item(selected_item, outcome):
    if outcome == "1":
        selected_item.update_damage()
        selected_item.update_stored_item()


def enhance_item(player_object, selected_item, material_item, success_rate, success_check):
    success_rate = success_rate - selected_item.item_enhancement
    if selected_item.item_enhancement < 100:
        if selected_item.item_elements[int(material_item.item_id[3])] == 1:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                selected_item.item_enhancement += 1
                selected_item.set_item_name()
                outcome = "1"
            else:
                outcome = "0"
        else:
            outcome = "4"
    else:
        outcome = "2"
    update_crafted_item(selected_item, outcome)
    return outcome


def reinforce_item(player_object, selected_item, material_item, success_rate, success_check):
    damage_check = damagecalc.get_item_tier_damage(selected_item.item_material_tier)
    maxed_values = [10000, 25000, 50000, 250000]
    if damage_check not in maxed_values:
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            material_tier_list = ["Iron", "Steel", "Silver", "Mithril", "Diamond", "Crystal",
                                  "Illusion", "Essence", "Spirit", "Soulbound", "Phantasmal", "Spectral",
                                  "Crude", "Metallic", "Gold", "Jewelled", "Diamond", "Crystal",
                                  "Key of ???", "Key of Freedoms", "Key of Desires", "Key of Hopes",
                                  "Key of Dreams", "Key of Wishes",
                                  "Fabled", "Legendary", "Mythical", "Fantastical", "Omniscient", "Plasma"]
            current_location = material_tier_list.index(selected_item.item_material_tier)
            selected_item.item_material_tier = material_tier_list[current_location + 1]
            selected_item.set_item_name()
            outcome = "1"
        else:
            outcome = "0"
    else:
        outcome = "2"
    update_crafted_item(selected_item, outcome)
    return outcome


def bestow_item(player_object, selected_item, material_item, success_rate, success_check):
    damage_check = damagecalc.get_item_tier_damage(selected_item.item_blessing_tier)
    maxed_values = [10000, 25000, 50000, 250000]
    if damage_check not in maxed_values:
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            blessing_tier_list = ["Standard", "Faint", "Luminous", "Lustrous", "Radiant", "Divine",
                                  "Basic", "Enchanted", "Luminous", "Lustrous", "Radiant", "Divine",
                                  "Sparkling", "Glittering", "Dazzling", "Shining", "Radiant", "Divine",
                                  "Tainted", "Corrupt", "Inverted", "Abyssal", "Calamitous", "Balefire",
                                  "Clear", "Pure", "Pristine", "Majestic", "Radiant", "Divine",
                                  "???", "Chroma", "Chromatic", "Prisma", "Prismatic", "Iridescent",
                                  "Refined", "Tempered", "Empowered", "Unsealed", "Awakened", "Transcendent"]
            current_location = blessing_tier_list.index(selected_item.item_blessing_tier)
            selected_item.item_blessing_tier = blessing_tier_list[current_location + 1]
            selected_item.set_item_name()
            outcome = "1"
        else:
            outcome = "0"
    else:
        outcome = "2"
    update_crafted_item(selected_item, outcome)
    return outcome


def open_item(player_object, selected_item, material_item, success_rate, success_check):
    if selected_item.item_num_sockets < 1:
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            selected_item.item_num_sockets += 1
            outcome = "1"
        else:
            outcome = "0"
    else:
        outcome = "2"
    update_crafted_item(selected_item, outcome)
    return outcome


def reforge_item(player_object, selected_item, material_item, success_rate, success_check):
    if selected_item.item_num_sockets < 6:
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            selected_item.reforge_stats()
            outcome = "1"
        else:
            outcome = "0"
    else:
        outcome = "3"
    update_crafted_item(selected_item, outcome)
    return outcome


def star_fusion_item(player_object, selected_item, material_item, success_rate, success_check, method):
    inventory.update_stock(player_object, material_item.item_id, -1)
    if success_check <= success_rate:
        outcome = "1"
        if selected_item.item_num_stars == 5:
            selected_item.reroll_roll(method)
        else:
            selected_item.add_roll(1)
    else:
        outcome = "0"
    update_crafted_item(selected_item, outcome)
    return outcome


def attune_item(player_object, selected_item, material_item, success_rate, success_check):
    check_aug = selected_item.check_augment()
    if check_aug < 18:
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            selected_item.add_augment()
            outcome = "1"
        else:
            outcome = "0"
    elif check_aug == -1:
        outcome = "3"
    else:
        outcome = "2"
    update_crafted_item(selected_item, outcome)
    return outcome


def implant_item(player_object, selected_item, material_item, success_rate, success_check):
    selected_element = int(material_item.item_id[6])
    if selected_item.item_elements[selected_element] == 0:
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            selected_item.add_item_element(selected_element)
            outcome = "1"
        else:
            outcome = "0"
    else:
        outcome = "4"
    update_crafted_item(selected_item, outcome)
    return outcome
