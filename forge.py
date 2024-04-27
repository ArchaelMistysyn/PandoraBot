# General imports
import discord
from discord.ui import Button, View
import random
import asyncio

# Data imports
import globalitems
import sharedmethods
from pandoradb import run_query as rq

# Core imports
import player
import inventory
import menus

# Item/crafting imports
import itemrolls
import loot

void_icon = "<a:evoid:1145520260573827134>"
item_type_lotus_dict = {"W": "Lotus9", "A": "Lotus5", "V": "Lotus2", "Y": "Lotus1", "G": "Lotus3", "C": "Lotus6"}


class SelectView(discord.ui.View):
    def __init__(self, player_obj, method):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item = player_obj, None
        self.method, self.value = method, None
        exclusions = ['D', 'R']
        select_options = [
            discord.SelectOption(emoji="<a:eenergy:1145534127349706772>", label=inventory.custom_item_dict[key],
                                 description=f"Equipped {inventory.custom_item_dict[key].lower()}")
            for key, value in inventory.item_loc_dict.items() if key not in exclusions]
        self.select_menu = discord.ui.Select(
            placeholder="Select crafting base.", min_values=1, max_values=1, options=select_options)
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_obj.discord_id:
            return
        item_select = interaction.data['values'][0]
        location = inventory.reverse_item_dict[item_select]
        selected_item = self.player_obj.player_equipped[location]
        if selected_item == 0:
            error_msg = "Not equipped"
            embed_msg = menus.create_error_embed(error_msg)
            await interaction.response.edit_message(embed=embed_msg, view=None)
            return

        self.selected_item = await inventory.read_custom_item(selected_item)
        # Handle the Forge view.
        if self.method == "celestial":
            # Display the View.
            embed_msg = await self.selected_item.create_citem_embed()
            new_view = ForgeView(self.player_obj, self.selected_item)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)

        # Handle the Purify view.
        if self.method == "purify":
            # Confirm eligibility.
            if self.selected_item.item_tier < 5:
                msg = ("This item does not meet the qualifications for void purification. "
                       "Soaking it in the true abyss would only erase it.")
                embed_msg = discord.Embed(colour=discord.Colour.magenta(), title="Oblivia, The Void", description=msg)
                await interaction.response.edit_message(embed=embed_msg, view=None)
                return
            # Display the view.
            embed_msg = await self.selected_item.create_citem_embed()
            new_view = PurifyView(self.player_obj, self.selected_item)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
            return

        # Display the Scribe view.
        if self.method == "custom":
            embed_msg = await self.selected_item.create_citem_embed()
            new_view = itemrolls.SelectRollsView(self.player_obj, self.selected_item)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
            return


class PurifyView(discord.ui.View):
    def __init__(self, player_obj, selected_item):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item = player_obj, selected_item
        self.material = None
        self.embed, self.new_view = None, None

        purification_data = {5: ["Crystal2", "Wish Purification", " [Miracle"],
                             6: ["Crystal3", "Abyss Purification", " [Stygian"],
                             7: ["Crystal4", "Divine Purification", " [Transcend"],
                             8: [None, "Divine Purification", " [MAX]"]}
        selected_dataset = purification_data[self.selected_item.item_tier]
        self.purify.label = selected_dataset[1] + selected_dataset[2]
        if self.selected_item.item_tier != 8:
            self.material = inventory.BasicItem(selected_dataset[0])
            self.purify.emoji, self.purify_check = self.material.item_emoji, self.material.item_base_rate
            self.purify.label += f": {self.purify_check}%]"
        else:
            self.purify.disabled, self.purify.style = True, globalitems.button_colour_list[3]

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def purify(self, interaction: discord.Interaction, button: discord.Button):
        await self.purify_callback(interaction, button)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple)
    async def reselect(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button)

    async def purify_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if not self.embed:
            self.embed, self.selected_item = await run_button(self.player_obj, self.selected_item,
                                                              self.material.item_id, "Purify")
            self.new_view = PurifyView(self.player_obj, self.selected_item)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if not self.embed:
            self.embed = discord.Embed(colour=discord.Colour.blurple(), title="Echo of Oblivia", description=globalitems.abyss_msg)
            self.new_view = SelectView(self.player_obj, "purify")
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class ForgeView(discord.ui.View):
    def __init__(self, player_obj, selected_item):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item = player_obj, selected_item

        # Build the option menu.
        options_dict = {
            "Enhance": {"emoji": "<a:eenergy:1145534127349706772>", "label": "Enhance",
                        "description": "Enhance the item."},
            "Upgrade": {"emoji": "<:eore:1145534835507593236>", "label": "Upgrade",
                        "description": "Upgrade the item quality."},
            "Reforge": {"emoji": "<a:eshadow2:1141653468965257216>", "label": "Reforge",
                        "description": "Reforge an item with a new ability and base stats."},
            "Attune": {"emoji": "<:eprl:1148390531345432647>", "label": "Cosmic Attunement",
                       "description": "Upgrade item rolls."},
            "Augment": {"emoji": "<:ehammer:1145520259248427069>", "label": "Astral Augment",
                        "description": "Add/Modify item rolls."},
            "Implant": {"emoji": "<a:eorigin:1145520263954440313>", "label": "Implant Element",
                        "description": "Gain new elements."},
        }
        option_data = [discord.SelectOption(
                emoji=options_dict[key]["emoji"], label=options_dict[key]["label"],
                description=options_dict[key]["description"]) for key in options_dict]
        select_menu = discord.ui.Select(placeholder="Select crafting method!", min_values=1, max_values=1,
                                        options=option_data)
        select_menu.callback = self.forge_callback
        self.add_item(select_menu)

    async def forge_callback(self, interaction: discord.Interaction):
        selected_option = interaction.data['values'][0]
        if interaction.user.id != self.player_obj.discord_id:
            return
        # Handle Element Selections
        if selected_option in ["Enhance", "Implant Element"]:
            new_view = SubSelectView(self.player_obj, self.selected_item, selected_option)
            await interaction.response.edit_message(view=new_view)
            return

        # Handle hammer methods.
        if "Augment" in selected_option:
            new_view = UpgradeView(self.player_obj, self.selected_item, selected_option, 0, 0)
            if self.selected_item.item_num_rolls == 6:
                new_view = SubSelectView(self.player_obj, self.selected_item, selected_option)
            await interaction.response.edit_message(view=new_view)
            return

        # Handle all other upgrade options.
        new_view = UpgradeView(self.player_obj, self.selected_item, selected_option, -1, 0)
        await interaction.response.edit_message(view=new_view)


class SubSelectView(discord.ui.View):
    def __init__(self, player_obj, selected_item, method):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item, self.method = player_obj, selected_item, method

        def build_select_option(i, option, craft_method, item_tier, cost_qty):
            if craft_method in ["Fae", "Origin"]:
                label, emoji = f"{option} Enhancement", globalitems.global_element_list[i]
                item_1 = inventory.BasicItem(f"{craft_method}{i}")
                description = f"{cost_qty}x {item_1.item_name} "
                if item_tier >= 5:
                    item_2 = inventory.BasicItem(f"Fragment{item_tier - 4}")
                    description += f"+ 1x {item_2.item_name}"
            elif craft_method == "Fusion":
                description_list = ["Add/Reroll", "Reroll defensive", "Reroll All", "Reroll damage",
                                    "Reroll penetration", "Reroll curse", "Reroll unique"]
                item_variant = 1 if item_tier < 6 else 2
                item_1 = inventory.BasicItem("Hammer")
                description = f"{description_list[i]}: "
                description += f"{cost_qty}x {item_1.item_name} "
                item_2 = None
                if i >= 3:
                    item_2 = inventory.BasicItem(f"Fragment{i - 2}")
                elif i >= 1:
                    item_2 = inventory.BasicItem(f"Heart{i}")
                if item_2 is not None and item_tier >= 5:
                    description += f"+ 1x {item_2.item_name}"
                label, emoji = f"{option} Fusion", item_1.item_emoji
            return discord.SelectOption(emoji=emoji, label=label, value=str(i), description=description)

        quantity = 1
        if self.method == "Enhance":
            self.menu_type = "Fae"
            selected_list = globalitems.element_names
            quantity = 10
        elif self.method == "Implant Element":
            self.menu_type = "Origin"
            selected_list = globalitems.element_names
        else:
            self.menu_type = "Fusion"
            selected_list = ["Star", "Radiant", "Chaos", "Void", "Wish", "Abyss", "Divine"]
        options = [build_select_option(i, option, self.menu_type, self.selected_item.item_tier, quantity)
                   for i, option in enumerate(selected_list)]
        self.select_menu = discord.ui.Select(placeholder="Select the crafting method to use.",
                                             min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        method_select = int(interaction.data['values'][0])
        hammer_select = method_select if self.menu_type == "Fusion" else -1
        if interaction.user.id != self.player_obj.discord_id:
            return
        new_view = UpgradeView(self.player_obj, self.selected_item, self.method, hammer_select, method_select)
        await interaction.response.edit_message(view=new_view)


# Regular Crafting
class UpgradeView(discord.ui.View):
    def __init__(self, player_obj, selected_item, menu_type, hammer_type, element):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item = player_obj, selected_item
        self.menu_type = menu_type
        self.hammer_type, self.element = hammer_type, element
        self.change_method.emoji = self.change_base.emoji = "↩️"

        # Method: num_buttons, button_names, button_emojis, material_ids, crafting_method
        method_dict = {
            "Enhance": [1, ["Enhance"], ["Enhance"], [f"Fae{self.element}"]],
            "Upgrade": [1, ["Reinforce"], ["Reinforce"], ["Ore5"]],
            "Reforge": [3, ["Create Socket", "Hellfire", "Abyssfire"], ["Open", "ReforgeA", "ReforgeV"],
                        ["Matrix1", "Flame1", "Flame2"]],
            "Cosmic Attunement": [1, ["Attune"], ["Attunement"], ["Pearl"]],
            "Astral Augment": [1, ["Star Fusion (Add/Reroll)", "Radiant Fusion (Defensive)", "Chaos Fusion (All)",
                                   "Void Fusion (Damage)", "Wish Fusion (Penetration)", "Abyss Fusion (Curse)",
                                   "Divine Fusion (Unique)"],
                               ["any fusion", "defensive fusion", "all fusion", "damage fusion",
                                "penetration fusion", "curse fusion", "unique fusion"], ["Hammer"]],
            "Implant Element": [1, [f"Implant ({globalitems.element_names[self.element]})"], ["Implant"],
                                [f"Origin{self.element}"]]
        }
        self.menu_details = method_dict[self.menu_type]
        self.method = self.menu_details[2]
        self.material_id = self.menu_details[3]

        # Construct the buttons.
        for button_count in range(self.menu_details[0]):
            if self.hammer_type != -1:
                button_num = self.hammer_type
                material_id = self.material_id[0]
            else:
                button_num = button_count
                material_id = self.material_id[button_num]
            is_maxed, success_rate = check_maxed(self.selected_item, self.method[button_num], material_id, self.element)
            temp_material = inventory.BasicItem(material_id)
            button_label, button_emoji = self.menu_details[1][button_num], temp_material.item_emoji
            button_style = globalitems.button_colour_list[1]
            if not is_maxed:
                button_label += f" ({success_rate}%)"
            else:
                button_style = globalitems.button_colour_list[3]
                button_label += " [MAX]"

            # Assign values to the buttons
            button_object = self.children[button_count]
            button_object.label, button_object.emoji = button_label, button_emoji
            button_object.custom_id = str(button_num)
            button_object.style = button_style
            button_object.disabled = is_maxed

        # Remove unused buttons.
        buttons_to_remove = []
        for button_index, button_object in enumerate(self.children):
            if self.menu_details[0] <= button_index < (len(self.children) - 2):
                buttons_to_remove.append(button_object)
        for button_object in buttons_to_remove:
            self.remove_item(button_object)

    @discord.ui.button(label="DefaultLabel1", style=discord.ButtonStyle.success, row=1)
    async def button1(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="DefaultLabel2",style=discord.ButtonStyle.success, row=1)
    async def button2(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="DefaultLabel3",style=discord.ButtonStyle.success, row=1)
    async def button3(self, interaction: discord.Interaction, button: discord.Button):
        await self.button_callback(interaction, button)

    @discord.ui.button(label="Change Base", style=discord.ButtonStyle.blurple, row=2)
    async def change_base(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button, "change_base")

    @discord.ui.button(label="Change Method", style=discord.ButtonStyle.blurple, row=2)
    async def change_method(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button, "change_method")

    async def button_callback(self, button_interaction: discord.Interaction, button: discord.Button):
        if button_interaction.user.id != self.player_obj.discord_id:
            return
        button_id = int(button.custom_id)
        material_id = self.material_id[0] if self.menu_type == "Astral Augment" else self.material_id[button_id]
        embed_msg, self.selected_item = await run_button(self.player_obj, self.selected_item, material_id, self.method[button_id])
        new_view = UpgradeView(self.player_obj, self.selected_item, self.menu_type, self.hammer_type, self.element)
        await button_interaction.response.edit_message(embed=embed_msg, view=new_view)

    async def reselect_callback(self, button_interaction: discord.Interaction, button: discord.Button, method):
        if button_interaction.user.id != self.player_obj.discord_id:
            return
        reload_item = await inventory.read_custom_item(self.selected_item.item_id)
        if reload_item is not None:
            if method == "change_method":
                new_view = ForgeView(self.player_obj, reload_item)
            else:
                new_view = SelectView(self.player_obj, "celestial")
            embed_msg = await reload_item.create_citem_embed()
            await button_interaction.response.edit_message(embed=embed_msg, view=new_view)


async def run_button(player_obj, selected_item, material_id, method):
    cost_item = inventory.BasicItem(material_id)
    reload_item = await inventory.read_custom_item(selected_item.item_id)
    result, cost = craft_item(player_obj, reload_item, cost_item, method)
    result_dict = {0: "Failed!", 1: "Success!", 2: "Cannot upgrade further.", 3: "Item not eligible",
                   4: "This element cannot be used",
                   5: f"Success! The item evolved to tier {reload_item.item_tier}!"}
    if result in result_dict:
        outcome = result_dict[result]
    else:
        no_stock_item = inventory.BasicItem(result)
        item_stock = inventory.check_stock(player_obj, no_stock_item.item_id)
        outcome = sharedmethods.get_stock_msg(no_stock_item, item_stock, cost)
    new_embed_msg = await reload_item.create_citem_embed()
    new_embed_msg.add_field(name=outcome, value="", inline=False)
    return new_embed_msg, reload_item


def check_maxed(target_item, method, material_id, element):
    material_item = inventory.BasicItem(material_id)
    success_rate = material_item.item_base_rate
    match method:
        case "Enhance":
            success_rate = max(5, (100 - (target_item.item_enhancement // 10) * 5))
            if target_item.item_enhancement >= globalitems.max_enhancement[(target_item.item_tier - 1)]:
                return True, 0
            return False, success_rate
        case "ReforgveA" | "ReforgeV":
            return False, success_rate
        case "Reinforce":
            success_rate = 100 - target_item.item_quality_tier * 10
            return (True, 0) if target_item.item_quality_tier == 5 else (False, success_rate)
        case "Open":
            return (True, 0) if target_item.item_num_sockets == 1 else (False, success_rate)
        case "Attunement":
            check_aug = itemrolls.check_augment(target_item)
            return (True, 0) if check_aug == target_item.item_tier * 6 else (False, success_rate)
        case "Implant":
            return (True, 0) if target_item.item_elements[element] == 1 else (False, success_rate)
        case _:
            return False, success_rate


def craft_item(player_obj, selected_item, material_item, method):
    success_rate = material_item.item_base_rate
    success_check = random.randint(1, 100)

    # Handle the first cost.
    cost_list = []
    player_stock = inventory.check_stock(player_obj, material_item.item_id)
    cost_1 = 1 if method != "Enhance" else 10
    if player_stock < cost_1:
        return material_item.item_id, cost_1
    cost_list.append(material_item)

    # Handle secondary costs if applicable.
    secondary_item = None
    if method == "Enhance":
        if selected_item.item_tier >= 5:
            secondary_item = inventory.BasicItem(f"Fragment{selected_item.item_tier - 4}")
    elif method == "Purify":
        if selected_item.item_tier == 7:
            secondary_item = inventory.BasicItem(item_type_lotus_dict[selected_item.item_type])
    elif "fusion" in method:
        cost_dict = {"defensive": "Heart1", "all": "Heart2", "damage": "Fragment1", "penetration": "Fragment2",
                     "curse": "Fragment3", "unique": "Fragment4"}
        method_type = method.split()
        if method_type[0] in cost_dict:
            secondary_item = inventory.BasicItem(cost_dict[method_type[0]])

    if secondary_item is not None:
        secondary_stock = inventory.check_stock(player_obj, secondary_item.item_id)
        if secondary_stock < 1:
            return secondary_item.item_id, 1
        cost_list.append(secondary_item)

    # Attempt the craft.
    match method:
        case "Enhance":
            outcome = enhance_item(player_obj, selected_item, cost_list, success_check)
        case "Reinforce":
            outcome = reinforce_item(player_obj, selected_item, cost_list, success_check)
        case "ReforgeA":
            outcome = reforge_item(player_obj, selected_item, cost_list, success_rate, success_check, "Hell")
        case "ReforgeV":
            outcome = reforge_item(player_obj, selected_item, cost_list, success_rate, success_check, "Abyss")
        case "Open":
            outcome = open_item(player_obj, selected_item, cost_list, success_rate, success_check)
        case "Attunement":
            outcome = attune_item(player_obj, selected_item, cost_list, success_rate, success_check)
        case "Implant":
            outcome = implant_item(player_obj, selected_item, cost_list, success_rate, success_check)
        case "Purify":
            outcome = purify_item(player_obj, selected_item, cost_list, success_rate, success_check)
        case _:
            if "fusion" in method:
                outcome = modify_item_rolls(player_obj, selected_item, cost_list,
                                            success_rate, success_check, method_type[0])
    return outcome, 0


def update_crafted_item(selected_item):
    selected_item.set_item_name()
    selected_item.update_damage()
    selected_item.update_stored_item()


def handle_craft_costs(player_obj, cost_list, cost_1=1, cost_2=1):
    inventory.update_stock(player_obj, cost_list[0].item_id, -1 * cost_1)
    if len(cost_list) > 1:
        inventory.update_stock(player_obj, cost_list[1].item_id, -1 * cost_2)


def enhance_item(player_obj, selected_item, cost_list, success_check):
    success_rate = max(5, (100 - (selected_item.item_enhancement // 10) * 5))
    # Check if enhancement is already maxed.
    if selected_item.item_enhancement >= globalitems.max_enhancement[(selected_item.item_tier - 1)]:
        return 4
    # Check if the material being used is eligible.
    element_location = int(cost_list[0].item_id[3])
    if selected_item.item_elements[element_location] != 1:
        return 3
    # Material is consumed. Attempts to enhance the item.
    handle_craft_costs(player_obj, cost_list, cost_1=10)
    if success_check <= success_rate:
        selected_item.item_enhancement += 1
        update_crafted_item(selected_item)
        return 1
    return 0


def reinforce_item(player_obj, selected_item, cost_list, success_check):
    success_rate = 100 - selected_item.item_quality_tier * 10
    # Check if item is eligible.
    if selected_item.item_quality_tier >= 5:
        return 2
    # Material is consumed. Attempts to upgrade the item (Reinforcement).
    handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.item_quality_tier += 1
        update_crafted_item(selected_item)
        return 1
    return 0


def open_item(player_obj, selected_item, cost_list, success_rate, success_check):
    # Check the item is eligible.
    if selected_item.item_num_sockets == 1:
        return 2
    # Material is consumed. Attempts to add a socket and update the item.
    handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.item_num_sockets += 1
        update_crafted_item(selected_item)
        return 1
    return 0


def reforge_item(player_obj, selected_item, cost_list, success_rate, success_check, method):
    outcome = 0
    # Material is consumed. Attempts to re-roll and update the item.
    handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.reforge_stats(unlock=(method == "Abyss"))
        update_crafted_item(selected_item)
        return 1
    return 0


def modify_item_rolls(player_obj, selected_item, cost_list, success_rate, success_check, method):
    outcome = 0
    if selected_item.item_num_rolls < 6:
        # Check eligibility for which methods can add a roll.
        if method != "any":
            return 3
        # Material is consumed. Attempts to add a roll to the item.
        handle_craft_costs(player_obj, cost_list)
        if success_check <= success_rate:
            itemrolls.add_roll(selected_item, 1)
            outcome = 1
    elif method == "any":
        # Material is consumed. Attempts to re-roll the item.
        handle_craft_costs(player_obj, cost_list)
        if success_check <= success_rate:
            itemrolls.reroll_roll(selected_item, method)
            outcome = 1
    else:
        # Check eligibility for which methods can be used on the item.
        if method not in itemrolls.roll_structure_dict[selected_item.item_type] and method != "all":
            return 3
        # Material is consumed. Attempts to re-roll the item.
        handle_craft_costs(player_obj, cost_list)
        if success_check <= success_rate:
            itemrolls.reroll_roll(selected_item, method)
            outcome = 1
    # Update the item if applicable.
    if outcome == 1:
        update_crafted_item(selected_item)
    return outcome


def attune_item(player_obj, selected_item, cost_list, success_rate, success_check):
    check_aug = itemrolls.check_augment(selected_item)
    outcome = 0
    # Confirm if the item has rolls.
    if check_aug == -1:
        return 3
    # Confirm that the augments are not already maxed.
    if check_aug == selected_item.item_tier * 6:
        return 2
    # Material is consumed. Attempts to add an augment.
    handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        itemrolls.add_augment(selected_item)
        update_crafted_item(selected_item)
        return 1
    return 0


def implant_item(player_obj, selected_item, cost_list, success_rate, success_check):
    outcome = 0
    # Confirm the item does not already have every element.
    if sum(selected_item.item_elements) == 9:
        return 2
    # Determine the element to add.
    check_element = cost_list[0].item_id[6]
    selected_element = int(check_element)
    # Confirm if the element already exists.
    if selected_item.item_elements[selected_element] == 1:
        return 4
    # Material is consumed. Attempts to add an element and update the item.
    handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.add_item_element(selected_element)
        update_crafted_item(selected_item)
        return 1
    return 0


def purify_item(player_obj, selected_item, cost_list, success_rate, success_check):
    # Check if item is eligible
    outcome = 0
    check_aug = itemrolls.check_augment(selected_item)
    if check_aug != selected_item.item_tier * 6:
        return 3
    if selected_item.item_enhancement < globalitems.max_enhancement[(selected_item.item_tier - 1)]:
        return 3
    if selected_item.item_num_sockets == 0:
        return 3
    # Material is consumed. Attempts to enhance the item.
    handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.item_quality_tier = 1
        selected_item.item_tier += 1
        selected_item.reforge_stats()
        update_crafted_item(selected_item)
        return 5
    return 0


# Refinery Menus
class RefSelectView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.item_dict = {"Weapon": "W", "Armour": "A", "Vambraces": "V", "Amulet": "Y",
                          "Dragon Wing": "G", "Paragon Crest": "C", "Gem": "Gem", "Jewel": "Jewel"}

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
                emoji="<a:eenergy:1145534127349706772>", label="Vambraces", description="Refine vambraces."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Amulet", description="Refine amulets."),
            discord.SelectOption(
                emoji="<:eore:1145534835507593236>", label="Dragon Wing", description="Refine wings."),
            discord.SelectOption(
                emoji="<:esoul:1145520258241806466>", label="Paragon Crest", description="Refine crests."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Gem", description="Refine gems."),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Jewel", description="Refine jewels.")
        ]
    )
    async def ref_select_callback(self, interaction: discord.Interaction, ref_select: discord.ui.Select):
        if interaction.user.id == self.player_user.discord_id:
            selected_type = self.item_dict[ref_select.values[0]]
            new_view = RefineItemView(self.player_user, selected_type)
            await interaction.response.edit_message(view=new_view)


class RefineItemView(discord.ui.View):
    def __init__(self, player_user, selected_type):
        super().__init__(timeout=None)
        menu_dict = {
            "W": [1, ["Void (100%)"], ["✅"], [5], ["Void1"]],
            "A": [1, ["Void (80%)"], ["✅"], [5], ["Void2"]],
            "V": [2, ["Vambraces (75%)", "Void (80%)"], ["✅", "✅"], [4, 5], ["Unrefined2", "Void3"]],
            "Y": [1, ["Void (80%)"], ["✅"], [5], ["Void4"]],
            "G": [2, ["Wing (75%)", "Void (80%)"], ["✅", "✅"], [4, 5], ["Unrefined1", "Void5"]],
            "C": [2, ["Crest (75%)", "Void (80%)"], ["✅", "✅"], [4, 5], ["Unrefined3", "Void6"]],
            "Gem": [3, ["Dragon (75%)", "Demon (75%)", "Paragon (75%)"], ["✅", "✅", "✅"],
                    [4, 4, 4], ["Gem1", "Gem2", "Gem3"]],
            "Jewel": [5, ["Dragon (50%)", "Demon (50%)", "Paragon (50%)", "Arbiter (50%)", "Incarnate (50%)"],
                      ["✅", "✅", "✅", "✅", "✅"],
                      [5, 5, 5, 6, 7], ["Jewel1", "Jewel2", "Jewel3", "Jewel4", "Jewel5"]]
        }
        self.selected_type = selected_type
        self.player_user = player_user
        self.embed, self.new_view = None, None
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

    @discord.ui.button(style=discord.ButtonStyle.success, row=1)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.success, row=1)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.success, row=1)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.success, row=2)
    async def option4(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.success, row=2)
    async def option5(self, interaction: discord.Interaction, button: discord.Button):
        await self.selected_callback(interaction, button)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️", row=2)
    async def reselect(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button)

    async def selected_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            if not self.embed:
                button_id = int(button.custom_id)
                selected_tier = self.menu_details[3][button_id]
                required_material = self.menu_details[4][button_id]
                # Handle gem type exceptions.
                item_type = f"D{button_id + 1}" if self.selected_type in ["Gem", "Jewel"] else self.selected_type
                self.embed = await refine_item(self.player_user, item_type, selected_tier, required_material)
            new_view = RefineItemView(self.player_user, self.selected_type)
            await interaction.response.edit_message(embed=self.embed, view=new_view)

    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        new_view = RefSelectView(self.player_user)
        new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title='Refinery', description="Please select the item to refine")
        new_embed.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
        await interaction.response.edit_message(embed=new_embed, view=new_view)


async def refine_item(player_user, selected_type, selected_tier, required_material, cost=1):
    # Check if player has stock.
    loot_item = inventory.BasicItem(required_material)
    item_stock = inventory.check_stock(player_user, required_material)
    if item_stock == 0:
        stock_message = sharedmethods.get_stock_msg(loot_item, item_stock)
        return discord.Embed(colour=discord.Colour.red(), title="Cannot Refine!", description=stock_message)
    # Pay the cost and attempt to refine.
    inventory.update_stock(player_user, required_material, (cost * -1))
    new_item, is_success = inventory.try_refine(player_user.player_id, selected_type, selected_tier)
    if not is_success:
        stock_message = sharedmethods.get_stock_msg(loot_item, (item_stock - cost))
        return discord.Embed(colour=discord.Colour.red(), title="Refinement Failed! The item is destroyed",
                             description=stock_message)
    result_id = inventory.add_custom_item(new_item)
    # Check if inventory is full.
    if result_id == 0:
        return inventory.full_inventory_embed(new_item, discord.Colour.red())
    return await new_item.create_citem_embed()


class MeldView(discord.ui.View):
    def __init__(self, player_obj, gem_1, gem_2, cost):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.gem_1 = gem_1
        self.gem_2 = gem_2
        self.cost = cost
        self.embed, self.new_view = None, None

        # Calculate affinity and update the meld button.
        gem_damage_1 = self.gem_1.item_damage_min + self.gem_1.item_damage_max
        gem_damage_2 = self.gem_2.item_damage_min + self.gem_2.item_damage_max
        self.affinity = int(round((min(gem_damage_1, gem_damage_2) / max(gem_damage_1, gem_damage_2) * 100)))
        self.affinity = min(100, (50 + self.affinity))
        self.meld_gems.label = f"Meld (Affinity: {self.affinity}%)"
        self.meld_gems.emoji = "🌟"

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def meld_gems(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Reload the data.
        await self.player_obj.reload_player()
        self.gem_1 = await inventory.read_custom_item(self.gem_1.item_id)
        self.gem_2 = await inventory.read_custom_item(self.gem_2.item_id)
        stock = inventory.check_stock(self.player_obj, "Token4")
        self.embed = discord.Embed(colour=discord.Colour.blurple(),
                                   title="Kazyth, Lifeblood of the True Laws", description="")
        # Check the cost
        if stock < self.cost:
            self.embed.description = "Begone fool. Those without tokens have no right to stand before me."
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Pay the cost
        inventory.update_stock(self.player_obj, "Token4", (self.cost * -1))
        # Process the meld attempt.
        if random.randint(1, 100) > self.affinity:
            inventory.delete_item(self.player_obj, self.gem_2)
            self.embed.description = "The jewels were not compatible enough, the sacrificial heart died."
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        error_msg, roll_change_list = meld_gems(self.player_obj, self.gem_1, self.gem_2)
        # Handle error.
        if error_msg != "":
            self.embed.description = error_msg
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        self.embed = await self.gem_1.create_citem_embed(roll_change_list)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        return


def meld_gems(player_obj, gem_1, gem_2):
    if not inventory.if_custom_exists(gem_1.item_id) or not inventory.if_custom_exists(gem_2.item_id):
        return "Melding interrupted : Jewels no longer recognized before processing.", None
    if gem_1.item_tier >= 7:
        return "Melding interrupted : Jewel eligibility changed before processing.", None
    inventory.delete_item(player_obj, gem_2)
    if gem_1.item_tier == gem_2.item_tier and gem_1.item_tier < 8 and gem_2.item_tier < 8:
        gem_1.item_tier += 1
        gem_1.base_damage_min, gem_1.base_damage_max = inventory.get_tier_damage(gem_1.item_tier, gem_1.item_type)
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



