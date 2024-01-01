# Forge menu
import discord
from discord.ui import Button, View

import globalitems
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
import combat
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
hammer_icon = "<:ehammer:1145520259248427069>"
void_icon = "<a:evoid:1145520260573827134>"
material_tier_list = ["Iron", "Steel", "Silver", "Mithril", "Diamond", "Crystal",
                      "Illusion", "Essence", "Spirit", "Soulbound", "Phantasmal", "Spectral",
                      "Crude", "Metallic", "Gold", "Jewelled", "Diamond", "Crystal",
                      "Key of ???", "Key of Freedoms", "Key of Desires", "Key of Hopes",
                      "Key of Dreams", "Key of Wishes",
                      "Fabled", "Legendary", "Mythical", "Fantastical", "Omniscient", "Plasma"]
blessing_tier_list = ["Standard", "Faint", "Luminous", "Lustrous", "Radiant", "Divine",
                      "Basic", "Enchanted", "Luminous", "Lustrous", "Radiant", "Divine",
                      "Sparkling", "Glittering", "Dazzling", "Shining", "Radiant", "Divine",
                      "Tainted", "Corrupt", "Inverted", "Abyssal", "Calamitous", "Balefire",
                      "Clear", "Pure", "Pristine", "Majestic", "Radiant", "Divine",
                      "???", "Chroma", "Chromatic", "Prisma", "Prismatic", "Iridescent",
                      "Refined", "Tempered", "Empowered", "Unsealed", "Awakened", "Transcendent"]
maxed_values = [10000, 25000, 50000, 250000]
void_ready_values = [10000, 150000]


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
                location = inventory.reverse_item_dict[item_select.values[0]]
                selected_item = self.player_object.player_equipped[location]
                if selected_item != 0:
                    self.selected_item = inventory.read_custom_item(selected_item)
                    if self.selected_item.item_type == "W" and self.selected_item.item_tier == 6:
                        key_msg = ("I've never seen anything like this. I'm sorry, this item is not powered by the "
                                   "stars. You will need to find another method of reforging it.")
                        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                                  title="Pandora, The Celestial", description=key_msg)
                        new_view = self
                    else:
                        embed_msg = self.selected_item.create_citem_embed()
                        new_view = ForgeView(self.player_object, self.selected_item)
                else:
                    error_msg = "Not equipped"
                    embed_msg = menus.create_error_embed(error_msg)
                    new_view = None
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class GenesisView(discord.ui.View):
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
                emoji="<a:eenergy:1145534127349706772>", label="Enhance", description="Enhance the weapon."),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Upgrade", description="Upgrade the weapon quality."),
            discord.SelectOption(
                emoji="<a:eshadow2:1141653468965257216>", label="Reforge", description="Reforge the weapon base stats"),
            discord.SelectOption(
                emoji="⚫", label="Add Socket", description="Add an open socket to the weapon."),
            discord.SelectOption(
                emoji=hammer_icon, label="Miracle Augment", description="Add/Modify weapon rolls."),
            discord.SelectOption(
                emoji=hammer_icon, label="??? Augment",
                description="Add/Modify specific weapon rolls."),
            discord.SelectOption(
                emoji="<a:eorigin:1145520263954440313>", label="Implant Element", description="Gain new elements.")
        ]
    )
    async def forge_callback(self, interaction: discord.Interaction, forge_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                match forge_select.values[0]:
                    case "Enhance":
                        new_view = MiracleEnhanceView(self.player_object, self.selected_item)
                    case "Upgrade":
                        new_view = MiracleUpgradeView(self.player_object, self.selected_item)
                    case "Reforge":
                        new_view = MiracleReforgeView(self.player_object, self.selected_item)
                    case "Add Socket":
                        new_view = MiracleSocketView(self.player_object, self.selected_item)
                    case "Wish Augment":
                        new_view = WishAugmentView(self.player_object, self.selected_item)
                    case "Miracle Augment":
                        new_view = MiracleAugmentView(self.player_object, self.selected_item)
                    case "Implant Element":
                        new_view = MiracleOriginView(self.player_object, self.selected_item)
                    case _:
                        new_view = None
                await interaction.response.edit_message(view=new_view)
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
                emoji=hammer_icon, label="Cosmic Augment", description="Add/Modify item rolls."),
            discord.SelectOption(
                emoji=hammer_icon, label="Astral Augment", description="Add/Modify item rolls."),
            discord.SelectOption(
                emoji="<a:eorigin:1145520263954440313>", label="Implant Element", description="Gain new elements."),
            discord.SelectOption(
                emoji="<a:eorigin:1145520263954440313>", label="Voidforge", description="Unlock forbidden power.")
        ]
    )
    async def forge_callback(self, interaction: discord.Interaction, forge_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                if forge_select.values[0] == "Enhance" or forge_select.values[0] == "Implant Element":
                    new_view = ElementSelectView(self.player_object, self.selected_item, forge_select.values[0])
                else:
                    new_view = UpgradeView(self.player_object, self.selected_item, forge_select.values[0], 0)
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
                emoji=fae_icon[2], label="Lightning",
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
                new_view = UpgradeView(self.player_object, self.selected_item, self.method, selected_element)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


# Regular Crafting
class UpgradeView(discord.ui.View):
    def __init__(self, player_object, selected_item, menu_type, element):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.menu_type = menu_type
        self.element = element
        # Method: num_buttons, button_names, button_emojis, material_ids, crafting_method
        method_dict = {"Enhance": [
                            1, ["Enhance"], [globalitems.global_element_list[self.element]], [[f"Fae{self.element}"]],
                            ["Enhance"]],
                       "Upgrade": [
                            2, ["Reinforce", "Bestow"],
                            ["<:eore:1145534835507593236>", "<:esoul:1145520258241806466>"], [[f"i5o"], [f"i5s"]],
                            ["Reinforce", "Bestow"]],
                       "Reforge": [
                            1, ["Reforge"], ["<a:eshadow2:1141653468965257216>"], [[f"i3f", f"i5f"]],
                            ["Reforge"]],
                       "Add Socket": [
                            1, ["Add Socket"], ["⚫"], [[f"i3k"]], ["Open"]],
                       "Cosmic Augment": [
                            2, ["Star Fusion", "Attunement"],
                            [hammer_icon, "<:eprl:1148390531345432647>"], [[f"i4h"], [f"i4p"]],
                            ["Single Fusion", "Attunement"]],
                       "Astral Augment": [
                            3, ["Pulsar Fusion", "Quasar Fusion", "Chaos Fusion"], [hammer_icon, hammer_icon], 
                            [[f"i5hP"], [f"i5hS"], ["i5hA"]], ["Prefix Fusion", "Suffix Fusion", "All Fusion"]],
                       "Implant Element": [
                            1, [f"Implant ({globalitems.element_names[self.element]})"],
                            ["<a:eorigin:1145520263954440313>"], [[f"Origin{self.element}"]],
                            ["Implant"]],
                       "Voidforge": [
                            3, ["Corrupt", "Augment", "HammerGoesHere"],
                            [void_icon, void_icon, void_icon], [[f"OriginV"], [f"v6p"], ["i6x"]],
                            ["VReinforce", "VAttunement", "VHammer"]]
                       }
        self.menu_details = method_dict[self.menu_type]
        self.material_id_list = self.menu_details[3]
        self.method = self.menu_details[4]
        for button_num in range(self.menu_details[0]):
            is_maxed, success_rate = check_maxed(self.selected_item, self.method[button_num],
                                                 self.material_id_list[button_num][0], self.element)
            button_label = self.menu_details[1][button_num]
            button_emoji = self.menu_details[2][button_num]
            if is_maxed:
                button_style = globalitems.button_colour_list[3]
                button_label += " [MAX]"
            else:
                button_style = globalitems.button_colour_list[1]
                button_label += f" ({success_rate}%)"
            # Assign values to the buttons
            button_object = self.children[button_num]
            button_object.label = button_label
            button_object.emoji = button_emoji
            button_object.style = button_style
            button_object.disabled = is_maxed
            button_object.custom_id = str(button_num)
        buttons_to_remove = []
        for button_index, button_object in enumerate(self.children):
            if button_index >= self.menu_details[0] and button_index != (len(self.children) - 1):
                buttons_to_remove.append(button_object)
        for button_object in buttons_to_remove:
            self.remove_item(button_object)
        self.reselect.emoji = "↩️"

    @discord.ui.button(label="DefaultLabel1", style=discord.ButtonStyle.success)
    async def button1(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="DefaultLabel2",style=discord.ButtonStyle.success)
    async def button2(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="DefaultLabel3",style=discord.ButtonStyle.success)
    async def button3(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple)
    async def reselect(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button)

    async def button_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                button_id = int(button.custom_id)
                if self.selected_item.item_tier < 5 or len(self.material_id_list[button_id]) == 1:
                    material_id = self.material_id_list[button_id][0]
                else:
                    material_id = self.material_id_list[button_id][1]
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item,
                                                           material_id, self.method[button_id])
                new_view = UpgradeView(self.player_object, self.selected_item, self.menu_type, self.element)
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                new_view = SelectView(self.player_object)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


def run_button(player_object, selected_item, material_id, method):
    loot_item = loot.BasicItem(material_id)
    reload_item = inventory.read_custom_item(selected_item.item_id)
    result, cost = craft_item(player_object, reload_item, loot_item, method)
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
            if cost == 1:
                outcome = f"Out of Stock: {loot_item.item_emoji}"
            else:
                outcome = f"Not Enough Stock: {loot_item.item_emoji}"
    new_embed_msg = reload_item.create_citem_embed()
    new_embed_msg.add_field(name=outcome, value="", inline=False)
    return new_embed_msg, reload_item


def check_maxed(target_item, method, material_id, element):
    is_maxed = False
    material_item = inventory.get_basic_item_by_id(material_id)
    success_rate = material_item.item_base_rate
    match method:
        case "Enhance":
            if target_item.item_enhancement >= 100:
                is_maxed = True
            else:
                success_rate = 100 - (target_item.item_enhancement // 10) * 10
        case "Reinforce":
            damage_check = combat.get_item_tier_damage(target_item.item_material_tier)
            if damage_check in maxed_values:
                is_maxed = True
        case "VReinforce":
            pass
        case "Bestow":
            damage_check = combat.get_item_tier_damage(target_item.item_blessing_tier)
            if damage_check in maxed_values:
                is_maxed = True
        case "Reforge":
            pass
        case "Open":
            if target_item.item_num_sockets == 1:
                is_maxed = True
        case "Single Fusion":
            pass
        case "All Fusion":
            pass
        case "Prefix Fusion":
            pass
        case "Suffix Fusion":
            pass
        case "Attunement":
            check_aug, check_vaug = target_item.check_augment()
            if check_aug == 18:
                is_maxed = True
        case "VAttunement":
            check_aug, check_vaug = target_item.check_augment()
            if check_vaug == 6:
                is_maxed = True
        case "Implant":
            if target_item.item_elements[element] == 1:
                is_maxed = True
        case _:
            pass
    return is_maxed, success_rate


def craft_item(player_object, selected_item, material_item, method):
    success_rate = material_item.item_base_rate
    player_stock = inventory.check_stock(player_object, material_item.item_id)
    cost = 1
    if method == "Enhance":
        cost = selected_item.item_enhancement + 1
    if player_stock >= cost:
        success_check = random.randint(1, 100)
        match method:
            case "Enhance":
                outcome = enhance_item(player_object, selected_item, material_item, success_rate, success_check, cost)
            case "Reinforce":
                outcome = reinforce_item(player_object, selected_item, material_item, success_rate, success_check, 0)
            case "VReinforce":
                outcome = reinforce_item(player_object, selected_item, material_item, success_rate, success_check, 1)
            case "Bestow":
                outcome = bestow_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Reforge":
                outcome = reforge_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Open":
                outcome = open_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Single Fusion":
                outcome = modify_item_rolls(player_object, selected_item, material_item, success_rate, success_check, 2)
            case "All Fusion":
                outcome = modify_item_rolls(player_object, selected_item, material_item, success_rate, success_check, 3)
            case "Prefix Fusion":
                outcome = modify_item_rolls(player_object, selected_item, material_item, success_rate, success_check, 0)
            case "Suffix Fusion":
                outcome = modify_item_rolls(player_object, selected_item, material_item, success_rate, success_check, 1)
            case "Attunement":
                outcome = attune_item(player_object, selected_item, material_item, success_rate, success_check, 0)
            case "VAttunement":
                outcome = attune_item(player_object, selected_item, material_item, success_rate, success_check, 1)
            case "Implant":
                outcome = implant_item(player_object, selected_item, material_item, success_rate, success_check)
            case _:
                outcome = "Error"
    else:
        outcome = material_item.item_id
    return outcome, cost


def update_crafted_item(selected_item, outcome):
    if outcome == "1":
        selected_item.update_damage()
        selected_item.update_stored_item()


def enhance_item(player_object, selected_item, material_item, success_rate, success_check, cost):
    success_rate = success_rate - (selected_item.item_enhancement // 10) * 10
    if selected_item.item_enhancement < 100:
        if selected_item.item_tier != 6:
            element_location = int(material_item.item_id[3])
        else:
            if sum(selected_item.item_elements) == 9:
                return 3
            else:
                zero_indices = [i for i, x in enumerate(selected_item.item_elements) if x == 0]
                random_index = random.randint(0, len(zero_indices) - 1)
                element_location = zero_indices[random_index]
        if selected_item.item_elements[element_location] == 1:
            inventory.update_stock(player_object, material_item.item_id, (0 - cost))
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


def reinforce_item(player_object, selected_item, material_item, success_rate, success_check, method):
    damage_check = combat.get_item_tier_damage(selected_item.item_material_tier)
    if method == 0:
        if damage_check not in maxed_values:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                current_location = material_tier_list.index(selected_item.item_material_tier)
                selected_item.item_material_tier = material_tier_list[current_location + 1]
                selected_item.set_item_name()
                outcome = "1"
            else:
                outcome = "0"
        else:
            outcome = "2"
    else:
        if damage_check in void_ready_values:
            if success_check <= success_rate:
                over_upgrades = {"Plasma": "Voidplasma", "Crystal": "VoidCrystal",
                                 "Spectral": "Voidspecter", "Key of Wishes": "Key of Miracles"}
                if selected_item.item_tier < 5:
                    selected_item.item_material_tier = over_upgrades[selected_item.item_material_tier]
                else:
                    if selected_item.item_material_tier == "Spectral":
                        selected_item.item_material_tier = "Voidforme"
                    else:
                        selected_item.item_material_tier = over_upgrades[selected_item.item_material_tier]
                        selected_item.set_item_name()
                outcome = "1"
            else:
                outcome = "0"
        else:
            outcome = "3"
    update_crafted_item(selected_item, outcome)
    return outcome


def bestow_item(player_object, selected_item, material_item, success_rate, success_check):
    damage_check = combat.get_item_tier_damage(selected_item.item_blessing_tier)
    if damage_check not in maxed_values:
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
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
    if selected_item.item_tier < 6:
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


def modify_item_rolls(player_object, selected_item, material_item, success_rate, success_check, method):
    if success_check <= success_rate:
        outcome = "1"
        if method == 2:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if selected_item.item_num_stars >= 5:
                selected_item.reroll_roll(method)
            else:
                selected_item.add_roll(1)
        else:
            if selected_item.item_num_stars >= 5:
                inventory.update_stock(player_object, material_item.item_id, -1)
                selected_item.reroll_roll(method)
            else:
                outcome = "3"
    else:
        outcome = "0"
    update_crafted_item(selected_item, outcome)
    return outcome


def attune_item(player_object, selected_item, material_item, success_rate, success_check, method):
    check_aug, check_vaug = selected_item.check_augment()
    if method == 0:
        if check_aug == -1:
            return "3"
        if check_aug < 18:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                selected_item.add_augment(method)
                outcome = "1"
            else:
                outcome = "0"
        else:
            outcome = "2"
    else:
        if check_aug == -1 or check_aug < 18:
            return "3"
        elif check_vaug == 6:
            return "2"
        else:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                selected_item.add_augment(method)
                outcome = "1"
            else:
                outcome = "0"
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
                emoji="<a:eenergy:1145534127349706772>", label="Weapon", description="Refine weapons."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Armour", description="Refine armours."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Accessory", description="Refine accessories."),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Dragon Wing", description="Refine wings."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Paragon Crest", description="Refine crests."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Dragon Gem", description="Refine gems.")
        ]
    )
    async def ref_select_callback(self, interaction: discord.Interaction, ref_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_type = ref_select.values[0]
                match selected_type:
                    case "Weapon":
                        new_view = RefineryWeaponView(self.player_user, "W")
                    case "Armour":
                        new_view = RefineryArmourView(self.player_user, "A")
                    case "Accessory":
                        new_view = RefineryAccessoryView(self.player_user, "Y")
                    case "Dragon Wing":
                        new_view = RefineryWingView(self.player_user, "G")
                    case "Paragon Crest":
                        new_view = RefineryCrestView(self.player_user, "C")
                    case "Dragon Gem":
                        new_view = RefineryGemView(self.player_user, "D")
                    case _:
                        pass
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class RefineryWeaponView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""
        self.embed = None

    @discord.ui.button(label="Fabled", style=discord.ButtonStyle.success, emoji="✅")
    async def fabled_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 5
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Wish", style=discord.ButtonStyle.success, emoji="✅")
    async def wish_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 6
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = RefSelectView(self.player_user)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class RefineryArmourView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""
        self.embed = None

    @discord.ui.button(label="Fabled", style=discord.ButtonStyle.success, emoji="✅")
    async def fabled_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 5
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = RefSelectView(self.player_user)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class RefineryAccessoryView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""
        self.embed = None

    @discord.ui.button(label="Fabled", style=discord.ButtonStyle.success, emoji="✅")
    async def fabled_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 5
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = RefSelectView(self.player_user)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class RefineryWingView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""
        self.embed = None

    @discord.ui.button(label="Wings", style=discord.ButtonStyle.success, emoji="✅")
    async def wing_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 4
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Fabled", style=discord.ButtonStyle.success, emoji="✅")
    async def fabled_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 5
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        new_view = RefSelectView(self.player_user)
        try:
            if interaction.user.name == self.player_user.player_name:
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class RefineryCrestView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""
        self.embed = None

    @discord.ui.button(label="Crest", style=discord.ButtonStyle.success, emoji="✅")
    async def crest_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 4
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Fabled", style=discord.ButtonStyle.success, emoji="✅")
    async def fabled_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 5
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = RefSelectView(self.player_user)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class RefineryGemView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        self.selected_type = selected_type
        self.player_user = player_user
        self.item_id = ""
        self.embed = None

    @discord.ui.button(label="Jewel", style=discord.ButtonStyle.success, emoji="✅")
    async def jewel_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 4
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Fabled", style=discord.ButtonStyle.success, emoji="✅")
    async def fabled_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 5
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Heart Gem", style=discord.ButtonStyle.success, emoji="✅")
    async def gem_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed:
                    selected_tier = 6
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier)
                new_view = OutcomeView(self.player_user, self.selected_type, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = RefSelectView(self.player_user)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)
            
            
class OutcomeView(discord.ui.View):
    def __init__(self, player_user, method, embed):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.method = method
        self.embed = embed

    @discord.ui.button(label="Return", style=discord.ButtonStyle.success, emoji="↩️")
    async def try_again_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                match self.method:
                    case "W":
                        new_view = RefineryWeaponView(self.player_user, self.method)
                    case "A":
                        new_view = RefineryArmourView(self.player_user, self.method)
                    case "Y":
                        new_view = RefineryAccessoryView(self.player_user, self.method)
                    case "G":
                        new_view = RefineryWingView(self.player_user, self.method)
                    case "C":
                        new_view = RefineryCrestView(self.player_user, self.method)
                    case "D":
                        new_view = RefineryGemView(self.player_user, self.method)
                    case _:
                        pass
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)


def refine_item(player_user, selected_type, selected_tier):
    item_id = f"i{str(selected_tier)}"
    if selected_tier == 4:
        match selected_type:
            case "G":
                item_id += "w"
            case "C":
                item_id += "c"
            case "D":
                item_id += "g"
            case _:
                pass
    elif selected_tier == 5:
        item_id += f"x{selected_type}"
    elif selected_tier == 6:
        item_id += f"u{selected_type}"
    if inventory.check_stock(player_user, item_id) > 0:
        inventory.update_stock(player_user, item_id, -1)
        new_item, is_success = inventory.try_refine(player_user.player_id, selected_type, selected_tier)
        if is_success:
            result_id = inventory.inventory_add_custom_item(new_item)
            if result_id == 0:
                embed_msg = inventory.full_inventory_embed(new_item, discord.Colour.red())
            else:
                embed_msg = new_item.create_citem_embed()
        else:
            embed_msg = discord.Embed(colour=discord.Colour.red(),
                                      title="Refinement Failed! The item is destroyed",
                                      description="Try Again?")
    else:
        loot_item = loot.BasicItem(item_id)
        stock_message = f'Out of stock: {loot_item.item_emoji}!'
        embed_msg = discord.Embed(colour=discord.Colour.red(),
                                  title=stock_message,
                                  description="")
    return embed_msg


# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS
# THIS SHIT NEEDS JESUS




# Genesis Fountain Crafting
class MiracleEnhanceView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Enhance", style=discord.ButtonStyle.success, emoji="<a:eenergy:1145534127349706772>")
    async def enhance_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "i6m", "Enhance")
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


class MiracleUpgradeView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Reinforce", style=discord.ButtonStyle.success, emoji="<:eore:1145534835507593236>")
    async def reinforce_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6o", "Reinforce")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Bestow", style=discord.ButtonStyle.success, emoji="<:esoul:1145520258241806466>")
    async def bestow_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6s", "Bestow")
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


class MiracleReforgeView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Reforge", style=discord.ButtonStyle.success, emoji="<a:eshadow2:1141653468965257216>")
    async def reforge_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6f", "Reforge")
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


class MiracleSocketView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Add Socket", style=discord.ButtonStyle.success, emoji="⚫")
    async def socket_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6k", "Open")
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


class WishAugmentView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Wish Fusion", style=discord.ButtonStyle.success, emoji=hammer_icon)
    async def star_fusion_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6h", "Single Fusion")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Attunement", style=discord.ButtonStyle.success, emoji="<:eprl:1148390531345432647>")
    async def attunement_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6p", "Attunement")
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


class MiracleAugmentView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object

    @discord.ui.button(label="Genesis Fusion", style=discord.ButtonStyle.success, emoji=hammer_icon)
    async def genesis_fusion_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6hP", "Prefix Fusion")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Terminus Fusion", style=discord.ButtonStyle.success, emoji=hammer_icon)
    async def terminus_fusion_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6hS", "Suffix Fusion")
                new_view = self
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Zenith Fusion", style=discord.ButtonStyle.success,
                       emoji=hammer_icon)
    async def Zenith_fusion_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6hA", "All Fusion")
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


class MiracleImplantView(discord.ui.View):
    def __init__(self, player_object, selected_item, element):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.element = element

    @discord.ui.button(label="Implant", style=discord.ButtonStyle.success, emoji="<a:eorigin:1145520263954440313>")
    async def implant_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.name == self.player_object.player_name:
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item, "m6z", "Implant")
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

