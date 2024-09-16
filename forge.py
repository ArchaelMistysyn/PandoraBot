# General imports
import discord
from discord.ui import Button, View
import random
import asyncio

# Data imports
import globalitems as gli
import sharedmethods as sm
from pandoradb import run_query as rqy

# Core imports
import player
import inventory
import menus

# Item/crafting imports
import itemrolls
import loot

item_type_lotus_dict = {"W": "Lotus1", "A": "Lotus6", "V": "Lotus3", "Y": "Lotus2", "G": "Lotus4", "C": "Lotus7"}


class SelectView(discord.ui.View):
    def __init__(self, player_obj, method):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item = player_obj, None
        self.method, self.value = method, None
        exclusions = ['D', 'R']
        select_options = [
            discord.SelectOption(emoji=gli.gear_icons_dict[key], label=inventory.custom_item_dict[key],
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
        embed_msg = await self.selected_item.create_citem_embed()
        if self.selected_item.item_base_type in gli.sovereign_item_list:
            title, description = "Cannot Upgrade", "Sovereign class item cannot be upgraded."
            embed_msg.add_field(name=title, value=description, inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=None)
            return
        # Handle the Forge view.
        if self.method == "celestial":
            if self.selected_item.item_tier == 9:
                title, description = "Cannot Upgrade", "Sacred items can no longer be modified."
                embed_msg.add_field(name=title, value=description, inline=False)
                await interaction.response.edit_message(embed=embed_msg, view=None)
                return
            new_view = ForgeView(self.player_obj, self.selected_item)
        # Handle the Purify view.
        elif self.method == "purify":
            if self.selected_item.item_tier < 5:
                msg = ("This item does not meet the qualifications for void purification. "
                       "Soaking it in the Deep Void would only erase it.")
                embed_msg = discord.Embed(colour=discord.Colour.magenta(), title="Oblivia, The Void", description=msg)
                new_view = None
            new_view = PurifyView(self.player_obj, self.selected_item)
        # Display the Scribe view.
        elif self.method == "custom":
            new_view = itemrolls.SelectRollsView(self.player_obj, self.selected_item)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


class PurifyView(discord.ui.View):
    def __init__(self, player_obj, selected_item):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item = player_obj, selected_item
        self.embed, self.new_view, self.material = None, None, None
        purification_data = {5: ["Crystal2", "Wish Purification", " [Miracle"],
                             6: ["Crystal3", "Abyss Purification", " [Stygian"],
                             7: ["Crystal4", "Divine Purification", " [Transcend"],
                             8: ["Sacred", "Blood Purification", " [Sacred]"],
                             9: ["Sacred", "Sacred Item", " [MAX]"]}
        selected_dataset = purification_data[self.selected_item.item_tier]
        self.purify.label = selected_dataset[1] + selected_dataset[2]
        if self.selected_item.item_tier != 9:
            self.material = inventory.BasicItem(selected_dataset[0])
            self.purify.emoji, self.purify_check = self.material.item_emoji, self.material.item_base_rate
            self.purify.label += f": {self.purify_check}%]"
            self.remove_item(self.children[1])
        else:
            self.material = inventory.BasicItem(selected_dataset[0])
            self.purify.disabled, self.purify.style = True, gli.button_colour_list[3]

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def purify(self, interaction: discord.Interaction, button: discord.Button):
        await self.purify_callback(interaction, button, "Purify")

    @discord.ui.button(label="Extraction", style=discord.ButtonStyle.red)
    async def extraction(self, interaction: discord.Interaction, button: discord.Button):
        await self.purify_callback(interaction, button, "Extract")

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple)
    async def reselect(self, interaction: discord.Interaction, button: discord.Button):
        await self.reselect_callback(interaction, button)

    async def purify_callback(self, interaction: discord.Interaction, button: discord.Button, method):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is None:
            self.embed, self.selected_item = await run_button(self.player_obj, self.selected_item,
                                                              self.material.item_id, method)
            self.new_view = PurifyView(self.player_obj, self.selected_item)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if not self.embed:
            self.embed = discord.Embed(colour=discord.Colour.blurple(), title="Echo of Oblivia", description=gli.abyss_msg)
            self.embed.set_image(url=gli.abyss_img)
            self.new_view = SelectView(self.player_obj, "purify")
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class ForgeView(discord.ui.View):
    def __init__(self, player_obj, selected_item):
        super().__init__(timeout=None)
        self.player_obj, self.selected_item = player_obj, selected_item
        # Build the option menu.
        options_dict = {
            "Enhance": {"emoji": "<a:eenergy:1145534127349706772>", "label": "Enhance",
                        "description": "Enhance the item"},
            "Upgrade": {"emoji": "<:eore:1145534835507593236>", "label": "Upgrade",
                        "description": "Upgrade the item quality"},
            "Open": {"emoji": "<a:elootitem:1144477550379274322>", "label": "Open Socket",
                     "description": "Add a socket to the item"},
            "Reforge": {"emoji": "<a:eshadow2:1141653468965257216>", "label": "Reforge",
                        "description": "Reforge the item with a new ability and base stats."},
            "Attune": {"emoji": "<:eprl:1148390531345432647>", "label": "Cosmic Attunement",
                       "description": "Upgrade the item rolls"},
            "Augment": {"emoji": "<:Hammer:1243800065013714955>", "label": "Astral Augment",
                        "description": "Add/Modify the item rolls"},
            "Implant": {"emoji": "<a:eorigin:1145520263954440313>", "label": "Implant Element",
                        "description": "Add new elements to the item"}}
        option_data = [discord.SelectOption(emoji=options_dict[key]["emoji"], label=options_dict[key]["label"],
                                            description=options_dict[key]["description"]) for key in options_dict]
        select_menu = discord.ui.Select(placeholder="Select crafting method!", min_values=1, max_values=1,
                                        options=option_data)
        select_menu.callback = self.forge_callback
        self.add_item(select_menu)

    async def forge_callback(self, interaction: discord.Interaction):
        selected_option = interaction.data['values'][0]
        if interaction.user.id != self.player_obj.discord_id:
            return
        await self.selected_item.reload_item()
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
            if craft_method in ["Fae", "Gemstone"]:
                label, emoji = f"{option} Enhancement", gli.ele_icon[i]
                item_1 = inventory.BasicItem(f"{craft_method}{i}")
                description = f"{cost_qty}x {item_1.item_name} "
                if item_tier >= 5:
                    item_2 = inventory.BasicItem(f"Fragment{item_tier - 4}")
                    description += f"+ 1x {item_2.item_name}"
            elif craft_method == "Fusion":
                description_list = ["Add/Reroll", "Reroll defensive", "Reroll All", "Reroll damage",
                                    "Reroll penetration", "Reroll curse", "Reroll unique"]
                item_1, item_2 = inventory.BasicItem("Hammer"), None
                description = f"{description_list[i]}: {cost_qty}x {item_1.item_name} "
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
            self.menu_type, selected_list, quantity = "Fae", gli.element_names, 10
        elif self.method == "Implant Element":
            self.menu_type, selected_list = "Gemstone", gli.element_names
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
        # Method: num_buttons, button_names, material_ids, crafting_method
        method_dict = {
            "Enhance": [2, ["Enhance", "Gemstone"], ["Enhance", "EnhanceAll"],
                        [f"Fae{self.element}", f"Gemstone{self.element}"]],
            "Upgrade": [1, ["Reinforce"], ["Reinforce"], ["Ore5"]],
            "Open Socket": [1, ["Create Socket"], ["Open"], ["Matrix"]],
            "Reforge": [3, ["Hellfire", "Abyssfire", "Mutate"], ["ReforgeA", "ReforgeV", "ReforgeM"],
                        ["Flame1", "Flame2", "Metamorphite"]],
            "Cosmic Attunement": [1, ["Attune"], ["Attunement"], ["Pearl"]],
            "Astral Augment": [1, ["Star Fusion (Add/Reroll)", "Radiant Fusion (Defensive)", "Chaos Fusion (All)",
                                   "Void Fusion (Damage)", "Wish Fusion (Penetration)", "Abyss Fusion (Curse)",
                                   "Divine Fusion (Unique)"],
                               ["any fusion", "defensive fusion", "all fusion", "damage fusion",
                                "penetration fusion", "curse fusion", "unique fusion"], ["Hammer"]],
            "Implant Element": [1, [f"Implant ({gli.element_names[self.element]})"], ["Implant"],
                                [f"Gemstone{self.element}"]]}
        self.menu_details = method_dict[self.menu_type]
        self.method, self.material_id = self.menu_details[2], self.menu_details[3]
        # Construct the buttons.
        for button_count in range(self.menu_details[0]):
            button_num, material_id = self.hammer_type, self.material_id[0]
            if self.hammer_type == -1:
                button_num, material_id = button_count, self.material_id[button_count]
            is_maxed, success_rate = check_maxed(self.selected_item, self.method[button_num], material_id, self.element)
            temp_material = inventory.BasicItem(material_id)
            button_label, button_emoji = self.menu_details[1][button_num], temp_material.item_emoji
            button_style = gli.button_colour_list[1]
            if not is_maxed:
                button_label += f" ({success_rate}%)"
            else:
                button_style = gli.button_colour_list[3]
                button_label += " [MAX]"
            # Assign values to the buttons
            button_object = self.children[button_count]
            button_object.label, button_object.custom_id = button_label, str(button_num)
            button_object.style, button_object.emoji, button_object.disabled = button_style, button_emoji, is_maxed
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
        await self.selected_item.reload_item()
        if self.selected_item is None:
            return
        view = ForgeView(self.player_obj, self.selected_item) if method == "change_method" \
            else SelectView(self.player_obj, "celestial")
        embed_msg = await self.selected_item.create_citem_embed()
        await button_interaction.response.edit_message(embed=embed_msg, view=view)


async def run_button(player_obj, selected_item, material_id, method):
    cost_item = inventory.BasicItem(material_id)
    await selected_item.reload_item()
    result, cost = await craft_item(player_obj, selected_item, cost_item, method)
    result_dict = {0: "Failed!", 1: "Success!", 2: "Cannot upgrade further.", 3: "Item not eligible",
                   4: "This element cannot be used",
                   5: f"Success! The item evolved to tier {selected_item.item_tier}!",
                   6: "Sacred items can no longer be modified."}
    if result in result_dict:
        outcome = result_dict[result]
    else:
        no_stock_item = inventory.BasicItem(result)
        item_stock = await inventory.check_stock(player_obj, no_stock_item.item_id)
        outcome = sm.get_stock_msg(no_stock_item, item_stock, cost)
    new_embed_msg = await selected_item.create_citem_embed()
    new_embed_msg.add_field(name=outcome, value="", inline=False)
    return new_embed_msg, selected_item


def check_maxed(target_item, method, material_id, element):
    material_item = inventory.BasicItem(material_id)
    success_rate = material_item.item_base_rate
    match method:
        case "Enhance" | "EnhanceAll":
            success_rate = max(5, (100 - (target_item.item_enhancement // 10) * 5)) if method == "Enhance" else 100
            if target_item.item_enhancement >= gli.max_enhancement[(target_item.item_tier - 1)]:
                return True, 0
            return False, success_rate
        case "ReforgveA" | "ReforgeV" | "ReforgeM":
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


async def craft_item(player_obj, item_obj, material_item, method_type):
    if item_obj.item_tier == 9 and method_type != "Extract":
        return 6
    success_rate, success_check = material_item.item_base_rate, random.randint(1, 100)
    # Handle the first cost.
    cost_list = []
    player_stock = await inventory.check_stock(player_obj, material_item.item_id)
    cost_1 = 1 if method_type != "Enhance" else 10
    if player_stock < cost_1:
        return material_item.item_id, cost_1
    cost_list.append(material_item)
    # Handle secondary costs if applicable.
    secondary_item = None
    if method_type in ["Enhance", "EnhanceAll"]:
        if item_obj.item_tier >= 5:
            secondary_item = inventory.BasicItem(f"Fragment{item_obj.item_tier - 4}")
    elif method_type == "Purify":
        if item_obj.item_tier in [7, 8]:
            secondary_item = inventory.BasicItem(item_type_lotus_dict[item_obj.item_type])
    elif "fusion" in method_type:
        cost_dict = {"defensive": "Heart1", "all": "Heart2", "damage": "Fragment1", "penetration": "Fragment2",
                     "curse": "Fragment3", "unique": "Fragment4"}
        method = method_type.split()
        if method[0] in cost_dict:
            secondary_item = inventory.BasicItem(cost_dict[method[0]])
    if secondary_item is not None:
        secondary_stock = await inventory.check_stock(player_obj, secondary_item.item_id)
        if secondary_stock < 1:
            return secondary_item.item_id, 1
        cost_list.append(secondary_item)
    # Attempt the craft.
    match method_type:
        case "Enhance" | "EnhanceAll":
            outcome = await enhance_item(player_obj, item_obj, cost_list, success_check, cost_qty=cost_1)
        case "Reinforce":
            outcome = await reinforce_item(player_obj, item_obj, cost_list, success_check)
        case "ReforgeA":
            outcome = await reforge_item(player_obj, item_obj, cost_list, success_rate, success_check, "Hell")
        case "ReforgeV":
            outcome = await reforge_item(player_obj, item_obj, cost_list, success_rate, success_check, "Abyss")
        case "ReforgeM":
            outcome = await reforge_item(player_obj, item_obj, cost_list, success_rate, success_check, "Mutate")
        case "Open":
            outcome = await open_item(player_obj, item_obj, cost_list, success_rate, success_check)
        case "Attunement":
            outcome = await attune_item(player_obj, item_obj, cost_list, success_rate, success_check)
        case "Implant":
            outcome = await implant_item(player_obj, item_obj, cost_list, success_rate, success_check)
        case "Purify":
            outcome = await purify_item(player_obj, item_obj, cost_list, success_rate, success_check)
        case "Extract":
            outcome = await extract_item(player_obj, item_obj, cost_list, success_rate, success_check)
        case _:
            if "fusion" in method_type:
                outcome = await modify_rolls(player_obj, item_obj, cost_list, success_rate, success_check, method[0])
    return outcome, 0


async def update_crafted_item(selected_item):
    selected_item.set_item_name()
    selected_item.update_damage()
    await selected_item.update_stored_item()


async def handle_craft_costs(player_obj, cost_list, cost_1=1, cost_2=1):
    await inventory.update_stock(player_obj, cost_list[0].item_id, -1 * cost_1)
    if len(cost_list) > 1:
        await inventory.update_stock(player_obj, cost_list[1].item_id, -1 * cost_2)


async def enhance_item(player_obj, selected_item, cost_list, success_check, cost_qty):
    success_rate = max(5, (100 - (selected_item.item_enhancement // 10) * 5)) if cost_qty == 10 else 100
    # Check if enhancement is already maxed.
    if selected_item.item_enhancement >= gli.max_enhancement[(selected_item.item_tier - 1)]:
        return 4
    # Check if the material being used is eligible.
    element_location = int(cost_list[0].item_id[-1])
    if selected_item.item_elements[element_location] != 1:
        return 3
    # Material is consumed. Attempts to enhance the item.
    await handle_craft_costs(player_obj, cost_list, cost_1=cost_qty)
    if success_check <= success_rate:
        selected_item.item_enhancement += 1
        await update_crafted_item(selected_item)
        return 1
    return 0


async def reinforce_item(player_obj, selected_item, cost_list, success_check):
    success_rate = 100 - selected_item.item_quality_tier * 10
    # Check if item is eligible.
    if selected_item.item_quality_tier >= 5:
        return 2
    # Material is consumed. Attempts to upgrade the item (Reinforcement).
    await handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.item_quality_tier += 1
        await update_crafted_item(selected_item)
        return 1
    return 0


async def open_item(player_obj, selected_item, cost_list, success_rate, success_check):
    # Check the item is eligible.
    if selected_item.item_num_sockets == 1:
        return 2
    # Material is consumed. Attempts to add a socket and update the item.
    await handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.item_num_sockets += 1
        await update_crafted_item(selected_item)
        return 1
    return 0


async def reforge_item(player_obj, selected_item, cost_list, success_rate, success_check, method):
    outcome = 0
    # Material is consumed. Attempts to re-roll and update the item.
    await handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        if method == "Mutate":
            selected_item.reforge_class()
            return 1
        selected_item.reforge_stats(unlock=(method == "Abyss"))
        await update_crafted_item(selected_item)
        return 1
    return 0


async def modify_rolls(player_obj, selected_item, cost_list, success_rate, success_check, method):
    outcome = 0
    if selected_item.item_num_rolls < 6:
        # Check eligibility for which methods can add a roll.
        if method != "any":
            return 3
        # Material is consumed. Attempts to add a roll to the item.
        await handle_craft_costs(player_obj, cost_list)
        if success_check <= success_rate:
            itemrolls.add_roll(selected_item, 1)
            outcome = 1
    elif method == "any":
        # Material is consumed. Attempts to re-roll the item.
        await handle_craft_costs(player_obj, cost_list)
        if success_check <= success_rate:
            itemrolls.reroll_roll(selected_item, method)
            outcome = 1
    else:
        # Check eligibility for which methods can be used on the item.
        if method not in itemrolls.roll_structure_dict[selected_item.item_type] and method != "all":
            return 3
        # Material is consumed. Attempts to re-roll the item.
        await handle_craft_costs(player_obj, cost_list)
        if success_check <= success_rate:
            itemrolls.reroll_roll(selected_item, method)
            outcome = 1
    # Update the item if applicable.
    if outcome == 1:
        await update_crafted_item(selected_item)
    return outcome


async def attune_item(player_obj, selected_item, cost_list, success_rate, success_check):
    check_aug = itemrolls.check_augment(selected_item)
    outcome = 0
    # Confirm if the item has rolls.
    if check_aug == -1:
        return 3
    # Confirm that the augments are not already maxed.
    if check_aug == selected_item.item_tier * 6:
        return 2
    # Material is consumed. Attempts to add an augment.
    await handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        itemrolls.add_augment(selected_item)
        await update_crafted_item(selected_item)
        return 1
    return 0


async def implant_item(player_obj, selected_item, cost_list, success_rate, success_check):
    outcome = 0
    # Confirm the item does not already have every element.
    if sum(selected_item.item_elements) == 9:
        return 2
    # Determine the element to add.
    check_element = int(cost_list[0].item_id[8])
    selected_element = int(check_element)
    # Confirm if the element already exists.
    if selected_item.item_elements[selected_element] == 1:
        return 4
    # Material is consumed. Attempts to add an element and update the item.
    await handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.add_item_element(selected_element)
        await update_crafted_item(selected_item)
        return 1
    return 0


async def purify_item(player_obj, selected_item, cost_list, success_rate, success_check):
    # Check if item is eligible
    outcome, check_aug = 0, itemrolls.check_augment(selected_item)
    if check_aug != selected_item.item_tier * 6:
        return 3
    if selected_item.item_enhancement < gli.max_enhancement[(selected_item.item_tier - 1)]:
        return 3
    if selected_item.item_num_sockets == 0:
        return 3
    # Material is consumed. Attempts to enhance the item.
    await handle_craft_costs(player_obj, cost_list)
    if success_check <= success_rate:
        selected_item.item_tier += 1
        if selected_item.item_tier < 9:
            selected_item.item_quality_tier = 1
        else:
            itemrolls.add_augment(selected_item, "All")
        selected_item.reforge_stats()
        await update_crafted_item(selected_item)
        return 5
    return 0


async def extract_item(player_obj, selected_item, cost_list, success_rate, success_check):
    # Check if item is eligible
    if selected_item.item_tier != 9:
        return 3
    # Material is consumed. Attempts to extract the item. (cost is recouped in this case)
    if success_check <= success_rate:
        selected_item.item_tier -= 1
        selected_item.item_quality_tier = 5
        itemrolls.add_augment(selected_item, "ReduceAll")
        selected_item.reforge_stats()
        await inventory.update_stock(player_obj, cost_list[0].item_id, 1)
        await update_crafted_item(selected_item)
        return 5
    return 0


# Refinery Menus
class RefSelectView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.item_dict = {"Weapon": "W", "Armour": "A", "Greaves": "V", "Amulet": "Y",
                          "Dragon Wing": "G", "Paragon Crest": "C", "Gem": "Gem", "Jewel": "Jewel"}

    @discord.ui.select(
        placeholder="Select crafting method!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<:Saber5:1275575137537888269>", label="Weapon", description="Refine weapons."),
            discord.SelectOption(
                emoji="<:Armour5:1275570612089389179>", label="Armour", description="Refine armours."),
            discord.SelectOption(
                emoji="<:Greaves5:1275575746890301632>", label="Greaves", description="Refine Greaves."),
            discord.SelectOption(
                emoji="<:Amulet5:1275570527423172609>", label="Amulet", description="Refine amulets."),
            discord.SelectOption(
                emoji="<:Wings5:1275576146615992452>", label="Dragon Wing", description="Refine wings."),
            discord.SelectOption(
                emoji="<:Crest5:1275576378502156369>", label="Paragon Crest", description="Refine crests."),
            discord.SelectOption(
                emoji="<:Gem_4:1275569729737719879>", label="Gem", description="Refine gems."),
            discord.SelectOption(
                emoji="<:Gem_8:1275569754932777072>", label="Jewel", description="Refine jewels.")
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
            "W": [1, ["Void (100%)"],
                  ["<:Saber5:1275575137537888269>"],
                  [5], ["Void1"]],
            "A": [1, ["Void (80%)"],
                  ["<:Armour5:1275570612089389179>"],
                  [5], ["Void2"]],
            "V": [2, ["Greaves (75%)", "Void (80%)"],
                  ['<:Greaves4:1275575740036812830>', "<Greaves5:1275575746890301632>"],
                  [4, 5], ["Unrefined2", "Void3"]],
            "Y": [1, ["Void (80%)"],
                  ["<Amulet5:1275570527423172609>"],
                  [5], ["Void4"]],
            "G": [2, ["Wing (75%)", "Void (80%)"],
                  ["<:Wings4:1275576140202770536>", "<:Wings5:1275576146615992452>"],
                  [4, 5], ["Unrefined1", "Void5"]],
            "C": [2, ["Crest (75%)", "Void (80%)"],
                  ["<:Crest4:1275576371053203526>", "<:Crest5:1275576378502156369>"],
                  [4, 5], ["Unrefined3", "Void6"]],
            "Gem": [3, ["Dragon (75%)", "Demon (75%)", "Paragon (75%)"],
                    ["<:Gem_2:1275569715078627359>", "<:Gem_3:1275569723568029786>", "<:Gem_4:1275569729737719879>"],
                    [4, 4, 4], ["Gem1", "Gem2", "Gem3"]],
            "Jewel": [5, ["Dragon (50%)", "Demon (50%)", "Paragon (50%)", "Arbiter (50%)", "Incarnate (50%)"],
                      ["<:Gem_5:1275569736205340773>", "<:Gem_5:1275569736205340773>", "<:Gem_5:1275569736205340773>",
                       "<:Gem_7:1275569749173993503>", "<:Gem_8:1275569754932777072>"],
                      [5, 5, 5, 6, 7], ["Jewel1", "Jewel2", "Jewel3", "Jewel4", "Jewel5"]]}
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
        new_embed.set_image(url=gli.refinery_img)
        await interaction.response.edit_message(embed=new_embed, view=new_view)


async def refine_item(player_user, selected_type, selected_tier, required_material, cost=1):
    # Check if player has stock.
    loot_item = inventory.BasicItem(required_material)
    item_stock = await inventory.check_stock(player_user, required_material)
    if item_stock == 0:
        stock_message = sm.get_stock_msg(loot_item, item_stock)
        return sm.easy_embed("red", "Cannot Refine!", stock_message)
    # Pay the cost and attempt to refine.
    await inventory.update_stock(player_user, required_material, (cost * -1))
    new_item, is_success = inventory.try_refine(player_user.player_id, selected_type, selected_tier)
    if not is_success:
        stock_message = sm.get_stock_msg(loot_item, (item_stock - cost))
        return sm.easy_embed("red", "Refinement Failed! The item is destroyed", stock_message)
    result_id = await inventory.add_custom_item(new_item)
    # Check if inventory is full.
    if result_id == 0:
        return inventory.full_inventory_embed(new_item, discord.Colour.red())
    return await new_item.create_citem_embed()


class MeldView(discord.ui.View):
    def __init__(self, player_obj, gem_1, gem_2, cost):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.gem_1, self.gem_2, self.cost = gem_1, gem_2, cost
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
        stock = await inventory.check_stock(self.player_obj, "Token4")
        self.embed = discord.Embed(colour=discord.Colour.blurple(),
                                   title="Kazyth, The Lifeblood", description="")
        # Check the cost
        if stock < self.cost:
            self.embed.description = "Begone fool. Those without tokens have no right to stand before me."
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Pay the cost
        await inventory.update_stock(self.player_obj, "Token4", (self.cost * -1))
        # Process the meld attempt.
        if random.randint(1, 100) > self.affinity:
            await inventory.delete_item(self.player_obj, self.gem_2)
            self.embed.description = "The jewels were not compatible enough, the sacrificial heart died."
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        error_msg, roll_change_list = await meld_gems(self.player_obj, self.gem_1, self.gem_2)
        # Handle error.
        if error_msg != "":
            self.embed.description = error_msg
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        self.embed = await self.gem_1.create_citem_embed(roll_change_list)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        return


async def meld_gems(player_obj, gem_1, gem_2):
    if not await inventory.if_custom_exists(gem_1.item_id) or not await inventory.if_custom_exists(gem_2.item_id):
        return "Melding interrupted : Jewels no longer recognized before processing.", None
    # Might be a good idea to run a reload on the gems here and compare tier to input tier
    await inventory.delete_item(player_obj, gem_2)
    if gem_1.item_tier <= gem_2.item_tier and gem_1.item_tier < 8:
        gem_1.item_tier += 1
        gem_1.get_tier_damage()
        gem_1.set_gem_name()
    roll_change_list = []
    for roll_index, secondary_roll in enumerate(gem_2.roll_values):
        random_roll = random.randint(0, 1)
        if random_roll == 1:
            new_roll_value = secondary_roll[1:]
            roll_change_list.append(True)
        else:
            new_roll_value = gem_1.roll_values[roll_index][1:]
            roll_change_list.append(False)
        gem_1.roll_values[roll_index] = f"{gem_1.item_tier}{new_roll_value}"
    await gem_1.update_stored_item()
    return "", roll_change_list



