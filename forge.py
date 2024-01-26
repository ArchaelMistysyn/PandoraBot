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
import itemrolls

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
                      "Key of Creation -", "Key of Desires -", "Key of Hopes -",
                      "Key of Dreams -", "Key of Wishes -", "Key of Miracles -",
                      "Cosmite", "Celestite", "Crystallite", "Astralite", "Stellarite", "Nebulite"]
blessing_tier_list = ["Standard", "Faint", "Luminous", "Lustrous", "Radiant", "Sanctified",
                      "Basic", "Enchanted", "Luminous", "Lustrous", "Radiant", "Sanctified",
                      "Sparkling", "Glittering", "Dazzling", "Shining", "Radiant", "Divine",
                      "Tainted", "Corrupt", "Inverted", "Abyssal", "Calamitous", "Balefire",
                      "Clear", "Pure", "Pristine", "Majestic", "Radiant", "Sanctified",
                      "Prelude", "Opalescent", "Chromatic", "Prismatic", "Resplendent", "Iridescent",
                      "Fabled", "Heroic", "Legendary", "Mythical", "Fantastical", "Vorpal"]
maxed_values = [25000, 75000, 125000, 300000, 500000, 1000000, 2000000]
void_ready_values = [75000, 300000]
reinforce_success_rates = [100, 90, 80, 70, 60, 50]
max_enhancement = [10, 20, 30, 40, 50, 100, 1000]


class SelectView(discord.ui.View):
    def __init__(self, player_object, method):
        super().__init__(timeout=None)
        self.selected_item = None
        self.player_object = player_object
        self.method = method
        self.value = None
        select_options = [
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
        self.select_menu = discord.ui.Select(
            placeholder="Select crafting base!", min_values=1, max_values=1, options=select_options
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        try:
            item_select = interaction.data['values'][0]
            if interaction.user.id == self.player_object.discord_id:
                location = inventory.reverse_item_dict[item_select]
                selected_item = self.player_object.player_equipped[location]
                if selected_item != 0:
                    self.selected_item = inventory.read_custom_item(selected_item)
                    if self.method == "purify":
                        # Determine if the item is eligible.
                        is_eligible = True
                        if self.selected_item.item_type in "AYGC" and self.selected_item.item_tier < 5:
                            is_eligible = False
                            if self.selected_item.is_void_corrupted():
                                is_eligible = False
                        elif self.selected_item.item_type == "W" and self.selected_item.item_tier < 6:
                            is_eligible = False
                            _, check_vaug, _ = itemrolls.check_augment(self.selected_item)
                            if check_vaug != 6:
                                is_eligible = False
                        # Display the correct view and message.
                        if is_eligible:
                            embed_msg = self.selected_item.create_citem_embed()
                            new_view = PurifyView(self.player_object, self.selected_item)
                        else:
                            key_msg = ("This item does not meet the qualifications for void purification. "
                                       "Soaking it in the true abyss would only erase it.")
                            embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                                      title="Oblivia, The Void", description=key_msg)
                            new_view = self
                    elif self.selected_item.item_tier >= 6 and self.method == "celestial":
                        key_msg = ("I've never seen anything like this. I'm sorry, this item is resonates with power "
                                   "beyond that of the stars. You will need to find another method of reforging it.")
                        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                                  title="Pandora, The Celestial", description=key_msg)
                        new_view = self
                    elif self.method == "custom":
                        embed_msg = self.selected_item.create_citem_embed()
                        new_view = itemrolls.SelectRollsView(self.player_object, self.selected_item)
                    else:
                        embed_msg = self.selected_item.create_citem_embed()
                        new_view = ForgeView(self.player_object, self.selected_item, self.method)
                else:
                    error_msg = "Not equipped"
                    embed_msg = menus.create_error_embed(error_msg)
                    new_view = None
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class PurifyView(discord.ui.View):
    def __init__(self, player_object, selected_item):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.embed = None
        self.new_view = None
        if self.selected_item.item_tier == 5:
            item_id = "Core3"
            label_name = "Purify"
            if self.selected_item.item_type == "W":
                self.purify.disabled = True
                self.purify.style = globalitems.button_colour_list[3]
                label_name += " [???]"
        else:
            item_id = "Crystal2"
            label_name = "Transcend"
            if self.selected_item.item_tier == 7:
                self.purify.disabled = True
                self.purify.style = globalitems.button_colour_list[3]
                label_name += " [MAX]"
        self.material = inventory.BasicItem(item_id)
        self.purify_check = self.material.item_base_rate
        if not self.purify.disabled:
            label_name += f" ({self.purify_check}%)"
        self.purify.label = label_name
        self.purify.emoji = self.material.item_emoji

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def purify(self, interaction: discord.Interaction, button: discord.Button):
        await self.purify_callback(interaction, button)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple)
    async def reselect(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button)

    async def purify_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_object.discord_id:
                if not self.embed:
                    result_msg = ""
                    self.embed, self.selected_item = run_button(self.player_object, self.selected_item,
                                                                self.material.item_id, "Purify")
                    self.new_view = PurifyView(self.player_object, self.selected_item)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_object.discord_id:
                if not self.embed:
                    entry_msg = (
                        "Within this cave resides the true abyss. Only a greater darkness can cleanse the void "
                        "and reveal the true form. The costs will be steep, I trust you came prepared. "
                        "Nothing can save you down there.")
                    self.embed = discord.Embed(colour=discord.Colour.blurple(),
                                               title="Echo of Oblivia",
                                               description=entry_msg)
                    self.new_view = SelectView(self.player_object, "purify")
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


forge_options = {
    "Enhance": {
        "emoji": "<a:eenergy:1145534127349706772>",
        "label": "Enhance",
        "description": "Enhance the item"
    },
    "Upgrade": {
        "emoji": "<:eore:1145534835507593236>",
        "label": "Upgrade",
        "description": "Upgrade the item quality."
    },
    "Reforge": {
        "emoji": "<a:eshadow2:1141653468965257216>",
        "label": "Reforge",
        "description": "Reforge an item with a new ability and base stats."
    },
    "Cosmic Attunement": {
        "emoji": "<:eprl:1148390531345432647>",
        "label": "Cosmic Attunement",
        "description": "Upgrade item rolls"
    },
    "Astral Augment": {
        "emoji": hammer_icon,
        "label": "Astral Augment",
        "description": "Add/Modify item rolls."
    },
    "Implant Element": {
        "emoji": "<a:eorigin:1145520263954440313>",
        "label": "Implant Element",
        "description": "Gain new elements."
    },
    "Voidforge": {
        "emoji": "<a:eorigin:1145520263954440313>",
        "label": "Voidforge",
        "description": "Unlock forbidden power."
    }
}

t6_forge_options = {
    "Enhance": {
        "emoji": "<a:eenergy:1145534127349706772>",
        "label": "Enhance",
        "description": "Enhance the item"
    },
    "Upgrade": {
        "emoji": "<:eore:1145534835507593236>",
        "label": "Upgrade",
        "description": "Upgrade the item quality."
    },
    "Reforge": {
        "emoji": "<a:eshadow2:1141653468965257216>",
        "label": "Reforge",
        "description": "Reforge an item with a new ability and base stats."
    },
    "Wish Attunement": {
        "emoji": "<:eprl:1148390531345432647>",
        "label": "Wish Attunement",
        "description": "Upgrade item rolls."
    },
    "Miracle Augment": {
        "emoji": hammer_icon,
        "label": "Miracle Augment",
        "description": "Add/Modify item rolls."
    },
    "Miracle Implant": {
        "emoji": "<a:eorigin:1145520263954440313>",
        "label": "Miracle Implant",
        "description": "Gain new elements."
    }
}


class ForgeView(discord.ui.View):
    def __init__(self, player_object, selected_item, permission):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.permission = permission
        # Build the option menu.
        options_dict = t6_forge_options if self.selected_item.item_tier >= 6 else forge_options
        select_options = [
            discord.SelectOption(
                emoji=options_dict[key]["emoji"],
                label=options_dict[key]["label"],
                description=options_dict[key]["description"]
            ) for key in options_dict
        ]
        select_menu = discord.ui.Select(
            placeholder="Select crafting base!", min_values=1, max_values=1, options=select_options
        )
        select_menu.callback = self.forge_callback
        self.add_item(select_menu)

    async def forge_callback(self, interaction: discord.Interaction):
        try:
            selected_option = interaction.data['values'][0]
            if interaction.user.id == self.player_object.discord_id:
                if selected_option in ["Enhance", "Implant Element"] and self.selected_item.item_tier < 6:
                    new_view = SubSelectView(self.player_object, self.selected_item,
                                             selected_option, self.permission)
                elif "Augment" in selected_option:
                    if self.selected_item.item_num_rolls < 6:
                        new_view = UpgradeView(self.player_object, self.selected_item, selected_option,
                                               0, 0, self.permission)
                    else:
                        new_view = SubSelectView(self.player_object, self.selected_item,
                                                 selected_option, self.permission)
                else:
                    new_view = UpgradeView(self.player_object, self.selected_item, selected_option,
                                           -1, 0, self.permission)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class SubSelectView(discord.ui.View):
    def __init__(self, player_object, selected_item, method, permission):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.method = method
        self.permission = permission
        if self.method in ["Enhance", "Implant Element"]:
            self.menu_type = "Element"
            selected_list = globalitems.element_names
            options = [discord.SelectOption(
                emoji=globalitems.global_element_list[i], label=option, value=str(i),
                description=f"Use {option.lower()} item.")
                for i, option in enumerate(selected_list)
            ]
        else:
            self.menu_type = "Fusion"
            selected_list = ["Star", "Astral", "Astral", "Astral", "Astral", "Astral", "Astral"]
            if self.selected_item.item_tier == 5:
                selected_list = ["Star", "Fabled", "Fabled", "Fabled", "Fabled", "Fabled", "Fabled"]
            elif self.selected_item.item_tier == 6:
                selected_list = ["Miracle", "Miracle", "Miracle", "Miracle", "Miracle", "Miracle", "Miracle"]
            description_list = ["Add/Reroll", "Reroll All", "Reroll damage", "Reroll defensive", "Reroll penetration",
                                "Reroll curse", "Reroll unique"]
            options = [discord.SelectOption(
                emoji=hammer_icon, label=f"{option} Fusion", value=str(i),
                description=f"Use {option.lower()} fusion: ({description_list[i]})")
                for i, option in enumerate(selected_list)
            ]
        self.select_menu = discord.ui.Select(placeholder="Select the crafting method to use.",
                                             min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        method_select = int(interaction.data['values'][0])
        hammer_select = method_select if self.menu_type == "Fusion" else -1
        try:
            if interaction.user.id == self.player_object.discord_id:
                new_view = UpgradeView(self.player_object, self.selected_item, self.method,
                                       hammer_select, method_select, self.permission)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


# Regular Crafting
class UpgradeView(discord.ui.View):
    def __init__(self, player_object, selected_item, menu_type, hammer_type, element, permission):
        super().__init__(timeout=None)
        self.selected_item = selected_item
        self.player_object = player_object
        self.menu_type = menu_type
        self.hammer_type = hammer_type
        self.element = element
        self.permission = permission
        # Method: num_buttons, button_names, button_emojis, material_ids, crafting_method
        method_dict = {"Enhance": [
                            1, ["Enhance"], [globalitems.global_element_list[self.element]], [[f"Fae{self.element}"]],
                            ["Enhance"]],
                       "Upgrade": [
                            2, ["Reinforce", "Bestow"],
                            ["<:eore:1145534835507593236>", "<:esoul:1145520258241806466>"], [[f"Ore5"], [f"Soul5"]],
                            ["Reinforce", "Bestow"]],
                       "Reforge": [
                            2, ["Reforge", "Create Socket"], ["<a:eshadow2:1141653468965257216>", "⚫"],
                            [[f"Flame1", f"Flame2"], [f"Matrix1", "Matrix2"]], ["Reforge", "Open"]],
                       "Cosmic Attunement": [
                            1, ["Attunement"], ["<:eprl:1148390531345432647>"], [[f"Pearl1", "Pearl2"]], ["Attunement"]],
                       "Astral Augment": [
                            1, ["Star Fusion (Add/Reroll)", "Astral Fusion (All)", "Astral Fusion (Damage)",
                                "Astral Fusion (Defensive)", "Astral Fusion (Penetration)", "Astral Fusion (Curse)",
                                "Astral Fusion (Unique)"],
                            [hammer_icon, hammer_icon, hammer_icon, hammer_icon,
                             hammer_icon, hammer_icon, hammer_icon],
                            [[f"Hammer1", "Hammer3"], ["Hammer2", "Hammer3"], [f"Hammer2", "Hammer3"],
                             [f"Hammer2", "Hammer3"], [f"Hammer2", "Hammer3"], [f"Hammer2", "Hammer3"],
                             [f"Hammer2", "Hammer3"]],
                            ["any fusion", "all fusion", "damage fusion", "defensive fusion",
                             "penetration fusion", "curse fusion", "unique fusion"]],
                       "Implant Element": [
                            1, [f"Implant ({globalitems.element_names[self.element]})"],
                            ["<a:eorigin:1145520263954440313>"], [[f"Origin{self.element}"]],
                            ["Implant"]],
                       "Voidforge": [
                            3, ["Void Fusion", "Augment", "Corruption"],
                            [void_icon, void_icon, void_icon], [[f"Core2"], [f"Pearl3"], ["OriginV"]],
                            ["VReinforce", "VAttunement", "Corrupt"]]
                       }
        method_dict_t6 = {"Enhance": [
                              1, ["Enhance"], ["<:Star_PinkBlue:1179736203013140480>"], [[f"FragmentM"]],
                              ["Enhance"]],
                          "Upgrade": [
                              2, ["Reinforce", "Bestow"],
                              ["<:eore:1145534835507593236>", "<:esoul:1145520258241806466>"], [[f"Ore6"], [f"Soul6"]],
                              ["Reinforce", "Bestow"]],
                          "Reforge": [
                              2, ["Reforge", "Create Socket"], ["<a:eshadow2:1141653468965257216>", "⚫"],
                              [[f"Flame4"], [f"Matrix3"]], ["Reforge", "Open"]],
                          "Wish Attunement": [
                              1, ["Attunement"], ["<:eprl:1148390531345432647>"], [[f"Pearl4"]], ["MultiAttunement"]],
                          "Miracle Augment": [
                            1, ["Miracle Fusion (Add/Reroll)", "Miracle Fusion (All)", "Miracle Fusion (Damage)",
                                "Miracle Fusion (Defensive)", "Miracle Fusion (Penetration)", "Miracle Fusion (Curse)",
                                "Miracle Fusion (Unique)"],
                            [hammer_icon, hammer_icon, hammer_icon, hammer_icon,
                             hammer_icon, hammer_icon, hammer_icon],
                            [[f"Hammer4"], ["Hammer4"], [f"Hammer4"], [f"Hammer4"],
                             [f"Hammer4"], [f"Hammer4"], [f"Hammer4"]],
                            ["any fusion", "all fusion", "damage fusion", "defensive fusion",
                             "penetration fusion", "curse fusion", "unique fusion"]],
                          "Miracle Implant": [
                              1, [f"Implant"], ["<a:eorigin:1145520263954440313>"], [[f"OriginM"]], ["Implant"]]
                          }
        if self.selected_item.item_tier >= 6:
            self.menu_details = method_dict_t6[self.menu_type]
        else:
            self.menu_details = method_dict[self.menu_type]
        self.material_id_list = self.menu_details[3]
        self.method = self.menu_details[4]
        for button_count in range(self.menu_details[0]):
            button_num = button_count
            if self.hammer_type != -1:
                button_num = self.hammer_type
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
            button_object = self.children[button_count]
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

    @discord.ui.button(label="DefaultLabel1", style=discord.ButtonStyle.success, row=1)
    async def button1(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="DefaultLabel2",style=discord.ButtonStyle.success, row=1)
    async def button2(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="DefaultLabel3",style=discord.ButtonStyle.success, row=1)
    async def button3(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, row=2)
    async def reselect(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button)

    async def button_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.id == self.player_object.discord_id:
                button_id = int(button.custom_id)
                if self.selected_item.item_tier < 5 or len(self.material_id_list[button_id]) == 1:
                    material_id = self.material_id_list[button_id][0]
                else:
                    material_id = self.material_id_list[button_id][1]
                embed_msg, self.selected_item = run_button(self.player_object, self.selected_item,
                                                           material_id, self.method[button_id])
                new_view = UpgradeView(self.player_object, self.selected_item, self.menu_type, self.hammer_type,
                                       self.element, self.permission)
                await button_interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        try:
            if button_interaction.user.id == self.player_object.discord_id:
                new_view = SelectView(self.player_object, self.permission)
                await button_interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


def run_button(player_object, selected_item, material_id, method):
    loot_item = inventory.BasicItem(material_id)
    reload_item = inventory.read_custom_item(selected_item.item_id)
    result, cost = craft_item(player_object, reload_item, loot_item, method)
    result_dict = {0: "Failed!",
                   1: "Success!",
                   2: "Cannot upgrade further.",
                   3: "Item not eligible",
                   4: "This element cannot be used",
                   5: f"Success! The item evolved to tier {reload_item.item_tier}!"}
    if result in result_dict:
        outcome = result_dict[result]
    else:
        outcome = "Out of Stock:" if cost == 1 else "Not Enough Stock:"
        outcome += f" {loot_item.item_emoji}"
    new_embed_msg = reload_item.create_citem_embed()
    new_embed_msg.add_field(name=outcome, value="", inline=False)
    return new_embed_msg, reload_item


def check_maxed(target_item, method, material_id, element):
    is_maxed = False
    material_item = inventory.BasicItem(material_id)
    success_rate = material_item.item_base_rate
    match method:
        case "Enhance":
            if target_item.item_enhancement >= max_enhancement[(target_item.item_tier - 1)]:
                is_maxed = True
            else:
                success_rate = max(5, (100 - (target_item.item_enhancement // 10) * 10))
        case "Reinforce":
            if target_item.item_material_tier in ["Void", "Destiny", "Eschaton", "Divine"]:
                is_maxed = True
            else:
                current_location = material_tier_list.index(target_item.item_material_tier)
                success_rate = reinforce_success_rates[(current_location % 6)]
                damage_check = combat.get_item_tier_damage(target_item.item_material_tier)
                if damage_check in maxed_values:
                    is_maxed = True
        case "VReinforce":
            if target_item.is_void_corrupted():
                is_maxed = True
        case "Bestow":
            if target_item.item_material_tier in ["Void", "Destiny", "Eschaton", "Divine"]:
                is_maxed = True
            else:
                current_location = blessing_tier_list.index(target_item.item_blessing_tier)
                success_rate = reinforce_success_rates[(current_location % 6)]
                damage_check = combat.get_item_tier_damage(target_item.item_blessing_tier)
                if damage_check in maxed_values:
                    is_maxed = True
        case "Open":
            if target_item.item_num_sockets == 1:
                is_maxed = True
        case "Attunement":
            check_aug, _, _ = itemrolls.check_augment(target_item)
            if check_aug == 18:
                is_maxed = True
        case "VAttunement":
            _, check_vaug, _ = itemrolls.check_augment(target_item)
            if check_vaug == 6:
                is_maxed = True
        case "MultiAttunement":
            check_aug, check_vaug, check_maug = itemrolls.check_augment(target_item)
            if target_item.item_num_rolls * 5 == check_aug + check_vaug + check_maug:
                is_maxed = True
        case "Corrupt":
            if target_item.item_bonus_stat in globalitems.void_ability_dict:
                is_maxed = True
        case "Implant":
            if target_item.item_tier >= 6:
                if sum(target_item.item_elements) == 9:
                    is_maxed = True
            elif target_item.item_elements[element] == 1:
                is_maxed = True
        case _:
            pass
    return is_maxed, success_rate


def craft_item(player_object, selected_item, material_item, method):
    success_rate = material_item.item_base_rate
    player_stock = inventory.check_stock(player_object, material_item.item_id)
    cost = 1
    if method == "Enhance":
        cost = 10
    if player_stock >= cost:
        success_check = random.randint(1, 100)
        match method:
            case "Enhance":
                outcome = enhance_item(player_object, selected_item, material_item, success_rate, success_check, cost)
            case "Reinforce":
                outcome = reinforce_item(player_object, selected_item, material_item,
                                         success_rate, success_check, False, "reinforce")
            case "VReinforce":
                outcome = reinforce_item(player_object, selected_item, material_item,
                                         success_rate, success_check, True, "reinforce")
            case "Bestow":
                outcome = reinforce_item(player_object, selected_item, material_item,
                                         success_rate, success_check, False, "bestow")
            case "Reforge":
                outcome = reforge_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Open":
                outcome = open_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Attunement":
                outcome = attune_item(player_object, selected_item, material_item, success_rate, success_check, 0)
            case "VAttunement":
                outcome = attune_item(player_object, selected_item, material_item, success_rate, success_check, 1)
            case "MultiAttunement":
                outcome = attune_item(player_object, selected_item, material_item, success_rate, success_check, 2)
            case "Corrupt":
                outcome = void_corruption(player_object, selected_item, material_item, success_rate, success_check)
            case "Implant":
                outcome = implant_item(player_object, selected_item, material_item, success_rate, success_check)
            case "Purify":
                outcome = purify_item(player_object, selected_item, material_item, success_rate, success_check)
            case _:
                if "fusion" in method:
                    method_type = method.split()
                    outcome = modify_item_rolls(player_object, selected_item, material_item,
                                                success_rate, success_check, method_type[0])
    else:
        outcome = material_item.item_id
    return outcome, cost


def update_crafted_item(selected_item, outcome):
    if outcome == 1 or outcome == 5:
        selected_item.update_damage()
        selected_item.update_stored_item()


def enhance_item(player_object, selected_item, material_item, success_rate, success_check, cost):
    outcome = 0
    success_rate = max(5, (success_rate - (selected_item.item_enhancement // 10) * 10))
    # Check if enhancement is already maxed.
    if selected_item.item_enhancement >= max_enhancement[(selected_item.item_tier - 1)]:
        return 4
    # Check if the material being used is eligible.
    element_location = 0
    if selected_item.item_tier < 6:
        element_location = int(material_item.item_id[3])
    if selected_item.item_elements[element_location] != 1 and selected_item.item_tier < 6:
        return 3
    # Material is consumed. Attempts to enhance the item.
    inventory.update_stock(player_object, material_item.item_id, (0 - cost))
    if success_check <= success_rate:
        selected_item.item_enhancement += 1
        outcome = 1
    # Update the item if applicable.
    if outcome == 1:
        selected_item.set_item_name()
        update_crafted_item(selected_item, outcome)
    return outcome


def reinforce_item(player_object, selected_item, material_item, success_rate, success_check, void_upgrade, method):
    outcome = 0
    damage_check_material = combat.get_item_tier_damage(selected_item.item_material_tier)
    damage_check_blessing = combat.get_item_tier_damage(selected_item.item_blessing_tier)
    if selected_item.item_material_tier in ["Void", "Destiny", "Eschaton" "Divine"]:
        return 2
    if method == "bestow":
        # Check the item is eligible.
        if damage_check_blessing in maxed_values:
            return 2
        if selected_item.item_blessing_tier == "":
            return 2
        # Material is consumed. Attempts to upgrade the item (Bestow).
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            current_location = blessing_tier_list.index(selected_item.item_blessing_tier)
            selected_item.item_blessing_tier = blessing_tier_list[current_location + 1]
            outcome = 1
    else:
        if void_upgrade:
            # Check the item is eligible.
            if damage_check_material not in void_ready_values:
                return 3
            if damage_check_blessing not in maxed_values:
                return 3
            if selected_item.item_num_rolls != 6:
                return 3
            # Material is consumed. Attempts to upgrade the item (Void Corruption).
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                if damage_check_material == void_ready_values[0]:
                    selected_item.item_material_tier = "Void"
                else:
                    selected_item.item_material_tier = "Divine" if selected_item.item_type != "W" else "Eschaton"
                    selected_item.item_blessing_tier = ""
                outcome = 1
        else:
            # Check if item is eligible.
            if damage_check_material in maxed_values:
                return 2
            # Material is consumed. Attempts to upgrade the item (Reinforcement).
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                current_location = material_tier_list.index(selected_item.item_material_tier)
                selected_item.item_material_tier = material_tier_list[current_location + 1]
                outcome = 1
    # Update the item if applicable.
    if outcome == 1:
        selected_item.set_item_name()
        update_crafted_item(selected_item, outcome)
    return outcome


def open_item(player_object, selected_item, material_item, success_rate, success_check):
    outcome = 0
    # Check the item is eligible.
    if selected_item.item_num_sockets == 1:
        return 2
    # Material is consumed. Attempts to add a socket and update the item.
    inventory.update_stock(player_object, material_item.item_id, -1)
    if success_check <= success_rate:
        selected_item.item_num_sockets += 1
        outcome = 1
        update_crafted_item(selected_item, outcome)
    return outcome


def reforge_item(player_object, selected_item, material_item, success_rate, success_check):
    outcome = 0
    inventory.update_stock(player_object, material_item.item_id, -1)
    # Material is consumed. Attempts to re-roll and update the item.
    if success_check <= success_rate:
        selected_item.reforge_stats()
        outcome = 1
        update_crafted_item(selected_item, outcome)
    return outcome


def modify_item_rolls(player_object, selected_item, material_item, success_rate, success_check, method):
    outcome = 0
    if selected_item.item_num_rolls < 6:
        # Check eligibility for which methods can add a roll.
        if method != "any":
            return 3
        # Material is consumed. Attempts to add a roll to the item.
        if success_check <= success_rate:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                itemrolls.add_roll(selected_item, 1)
                outcome = 1
    elif method == "any":
        # Material is consumed. Attempts to re-roll the item.
        if success_check <= success_rate:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                itemrolls.reroll_roll(selected_item, method)
                outcome = 1
    else:
        # Check eligibility for which methods can be used on the item.
        if method not in itemrolls.roll_structure_dict[selected_item.item_type] and method != "all":
            return 3
        # Material is consumed. Attempts to re-roll the item.
        if success_check <= success_rate:
            inventory.update_stock(player_object, material_item.item_id, -1)
            if success_check <= success_rate:
                itemrolls.reroll_roll(selected_item, method)
                outcome = 1
    # Update the item if applicable.
    if outcome == 1:
        update_crafted_item(selected_item, outcome)
    return outcome


def attune_item(player_object, selected_item, material_item, success_rate, success_check, method):
    check_aug, check_vaug, check_maug = itemrolls.check_augment(selected_item)
    outcome = 0
    # Confirm if the item has eligible rolls if not maxed.
    if check_aug == -1:
        return 3
    if method == 0:
        # Confirm that the augments are not already maxed.
        if check_aug == 18:
            return 2
        # Material is consumed. Attempts to add an augment.
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            itemrolls.add_augment(selected_item, method)
            outcome = 1
    elif method == 1:
        # If the item is not a void item it is not eligible.
        if not selected_item.is_void_corrupted():
            return 3
        # If the regular augments are not maxed or the void augments are maxed the item is not eligible.
        if check_aug < 18:
            return 3
        if check_vaug == 6:
            return 2
        # Material is consumed. Attempts to add a void augment.
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            itemrolls.add_augment(selected_item, method)
            outcome = 1
    else:
        # Confirm if the item has eligible rolls and is not maxed.
        if check_aug == 18 and check_vaug == 6 and check_maug == 6:
            return 2
        if selected_item.item_num_rolls * 5 == check_aug + check_vaug + check_maug:
            return 3
        inventory.update_stock(player_object, material_item.item_id, -1)
        if success_check <= success_rate:
            itemrolls.add_augment(selected_item, method)
            outcome = 1

    # Update the item if applicable.
    if outcome == 1:
        update_crafted_item(selected_item, outcome)
    return outcome


def implant_item(player_object, selected_item, material_item, success_rate, success_check):
    outcome = 0
    # Confirm the item does not already have every element.
    if sum(selected_item.item_elements) == 9:
        return 2
    # Determine the element to add.
    if material_item.item_id == "OriginM":
        zero_indices = [index for index, value in enumerate(selected_item.item_elements) if value == 0]
        selected_index = random.choice(zero_indices)
        selected_element = selected_index
    else:
        check_element = material_item.item_id[6]
        selected_element = int(check_element)
    # Confirm if the element already exists.
    if selected_item.item_elements[selected_element] == 1:
        return 4
    # Material is consumed. Attempts to add an element and update the item.
    inventory.update_stock(player_object, material_item.item_id, -1)
    if success_check <= success_rate:
        selected_item.add_item_element(selected_element)
        outcome = 1
        update_crafted_item(selected_item, outcome)
    return outcome


def void_corruption(player_object, selected_item, material_item, success_rate, success_check):
    outcome = 0
    # Confirm the item is eligible.
    if selected_item.item_num_rolls < 6:
        return 3
    check_aug, check_vaug, _ = itemrolls.check_augment(selected_item)
    if check_vaug != 6:
        return 3
    # Material is consumed. Attempt to upgrade the unique skill.
    inventory.update_stock(player_object, material_item.item_id, -1)
    if success_check <= success_rate:
        selected_item.item_bonus_stat = globalitems.reverse_void_ability_dict[selected_item.item_bonus_stat]
        outcome = 1
        update_crafted_item(selected_item, outcome)
    return outcome


def purify_item(player_object, selected_item, material_item, success_rate, success_check):
    outcome = 0
    _, check_vaug, check_maug = itemrolls.check_augment(selected_item)
    # Check if item is eligible
    if selected_item.item_enhancement < max_enhancement[(selected_item.item_tier - 1)]:
        return 3
    if selected_item.item_tier == 5:
        target_tier = "Destiny"
        if not selected_item.is_void_corrupted():
            return 3
        if check_vaug != 6:
            return 3
    elif selected_item.item_tier == 6:
        target_tier = "Divine" if selected_item.item_type != "W" else "Eschaton"
        if selected_item.item_num_sockets == 0:
            return 3
        if check_maug != 6:
            return 3
        if selected_item.item_type == "W":
            damage_check_material = combat.get_item_tier_damage(selected_item.item_material_tier)
            damage_check_blessing = combat.get_item_tier_damage(selected_item.item_blessing_tier)
            if damage_check_material not in maxed_values or damage_check_blessing not in maxed_values:
                return 3
    else:
        return 2
    # Material is consumed. Attempts to enhance the item.
    inventory.update_stock(player_object, material_item.item_id, -1)
    if success_check <= success_rate:
        selected_item.item_material_tier = target_tier
        selected_item.item_blessing_tier = ""
        selected_item.item_tier += 1
        selected_item.item_num_stars += 1
        selected_item.reforge_stats()
        outcome = 5
    # Update the item if applicable.
    if outcome == 5:
        selected_item.set_item_name()
        update_crafted_item(selected_item, outcome)
    return outcome


# Refinery Menus
class RefSelectView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.item_dict = {"Weapon": "W", "Armour": "A", "Accessory": "Y",
                          "Dragon Wing": "G", "Paragon Crest": "C", "Dragon Gem": "D"}

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
            if interaction.user.id == self.player_user.discord_id:
                selected_type = self.item_dict[ref_select.values[0]]
                new_view = RefineItemView(self.player_user, selected_type)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class RefineItemView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        menu_dict = {
            "W": [2, ["Fabled", "Wish"], ["✅", "✅"], [5, 6], ["Fabled1", "Unrefined5"]],
            "A": [1, ["Fabled"], ["✅"], [5], ["Fabled2"]],
            "Y": [1, ["Fabled"], ["✅"], [5], ["Fabled3"]],
            "G": [2, ["Wing", "Fabled"], ["✅", "✅"], [4, 5], ["Unrefined1", "Fabled4"]],
            "C": [2, ["Crest", "Fabled"], ["✅", "✅"], [4, 5], ["Unrefined3", "Fabled5"]],
            "D": [3, ["Jewel", "Fabled", "Heart Gem"], ["✅", "✅", "✅"],
                  [4, 5, 6], ["Unrefined2", "Fabled6", "Unrefined4"]]
        }
        self.selected_type = selected_type
        self.player_user = player_user
        self.embed = None
        self.menu_details = menu_dict[self.selected_type]
        for button_num in range(self.menu_details[0]):
            button_object = self.children[button_num]
            button_object.label = self.menu_details[1][button_num]
            button_object.emoji = self.menu_details[2][button_num]
            button_object.custom_id = str(button_num)
        buttons_to_remove = []
        for button_index, button_object in enumerate(self.children):
            if button_index >= self.menu_details[0] and button_index != (len(self.children) - 1):
                buttons_to_remove.append(button_object)
        for button_object in buttons_to_remove:
            self.remove_item(button_object)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button)

    async def selected_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                if not self.embed:
                    button_id = int(button.custom_id)
                    selected_tier = self.menu_details[3][button_id]
                    required_material = self.menu_details[4][button_id]
                    self.embed = refine_item(self.player_user, self.selected_type, selected_tier, required_material)
                new_view = RefineItemView(self.player_user, self.selected_type)
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)

    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                new_view = RefSelectView(self.player_user)
                new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title='Refinery',
                                          description="Please select the item to refine")
                new_embed.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                await interaction.response.edit_message(embed=new_embed, view=new_view)
        except Exception as e:
            print(e)


def refine_item(player_user, selected_type, selected_tier, required_material):
    if inventory.check_stock(player_user, required_material) > 0:
        inventory.update_stock(player_user, required_material, -1)
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
        loot_item = inventory.BasicItem(required_material)
        stock_message = f'Out of Stock: {loot_item.item_emoji}!'
        embed_msg = discord.Embed(colour=discord.Colour.red(),
                                  title="Cannot Refine!",
                                  description=stock_message)
    return embed_msg


class MeldView(discord.ui.View):
    def __init__(self, player_object, gem_1, gem_2, cost):
        super().__init__(timeout=None)
        self.player_object = player_object
        self.gem_1 = gem_1
        self.gem_2 = gem_2
        self.cost = cost
        self.embed = None
        self.new_view = None

        # Calculate affinity and update the meld button.
        gem_damage_1 = self.gem_1.item_damage_min + self.gem_1.item_damage_max
        gem_damage_2 = self.gem_2.item_damage_min + self.gem_2.item_damage_max
        self.affinity = int(round((min(gem_damage_1, gem_damage_2) / max(gem_damage_1, gem_damage_2) * 100)))
        self.affinity = min(100, (50 + self.affinity))
        self.meld_gems.label = f"Meld (Affinity: {self.affinity}%)"
        self.meld_gems.emoji = "🌟"

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def meld_gems(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_object.discord_id:
                if not self.embed:
                    # Reload the data.
                    self.player_object = player.get_player_by_id(self.player_object.player_id)
                    self.gem_1 = inventory.read_custom_item(self.gem_1.item_id)
                    self.gem_2 = inventory.read_custom_item(self.gem_2.item_id)
                    stock = inventory.check_stock(self.player_object, "Token4")
                    if stock < self.cost:
                        cannot_afford_msg = "Begone fool. Those without tokens have no right to stand before me."
                        self.embed = discord.Embed(colour=discord.Colour.blurple(),
                                                   title="Kazyth, Lifeblood of the True Laws",
                                                   description=cannot_afford_msg)
                    else:
                        # Pay the cost
                        inventory.update_stock(self.player_object, "Token4", (self.cost * -1))
                        # Process the meld attempt.
                        success_roll = random.randint(1, 100)
                        if success_roll <= self.affinity:
                            error_msg, roll_change_list = meld_gems(self.gem_1, self.gem_2)
                            if error_msg == "":
                                inventory.delete_item(self.player_object, self.gem_2)
                                self.embed = self.gem_1.create_citem_embed(roll_change_list)
                            else:
                                self.embed = discord.Embed(colour=discord.Colour.blurple(),
                                                           title="Kazyth, Lifeblood of the True Laws",
                                                           description=error_msg)
                        else:
                            inventory.delete_item(self.player_object, self.gem_2)
                            fail_description = "The gems were not compatible enough, the sacrificial heart died."
                            self.embed = discord.Embed(colour=discord.Colour.blurple(),
                                                       title="Kazyth, Lifeblood of the True Laws",
                                                       description=fail_description)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


def meld_gems(gem_1, gem_2):
    if not inventory.if_custom_exists(gem_1.item_id) or not inventory.if_custom_exists(gem_2.item_id):
        return "Melding interrupted : Gems no longer recognized before processing.", None
    if gem_1.item_tier >= 7:
        return "Melding interrupted : Gem eligibility changed before processing.", None
    tier_adjust = 0
    if gem_1.item_tier == gem_2.item_tier:
        tier_adjust = 1
        gem_1.item_tier += tier_adjust
        gem_1.item_num_stars += tier_adjust
        gem_1.base_damage_min, gem_1.base_damage_max = inventory.get_tier_damage(gem_1.item_tier, gem_1.item_type)
        gem_1.item_bonus_stat = f"{gem_1.item_bonus_stat[0]};{5 * (tier_adjust + 1)}"
        gem_1.set_gem_name()
    roll_change_list = []
    for roll_index, secondary_roll in enumerate(gem_2.item_roll_values):
        random_roll = random.randint(0, 1)
        if random_roll == 1:
            new_roll_value = secondary_roll[1:]
            roll_change_list.append(True)
        else:
            new_roll_value = gem_1.item_roll_values[roll_index][1:]
            roll_change_list.append(False)
        gem_1.item_roll_values[roll_index] = f"{gem_1.item_tier}{new_roll_value}"
    gem_1.update_stored_item()
    return "", roll_change_list



