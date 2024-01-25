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
import bosses
import globalitems
import insignia
import combat

starter_guide = "1. Use /quest to progress through the quest."
starter_guide += "\n2. Use /map to farm for tier 1-4 Weapons, Armour, and Accessories."
starter_guide += " Maps are also a great source of EXP."
starter_guide += "\n3. Use /inv to check your inventory. Click Gear to check your gear."
starter_guide += "\n4. Use /display [item id] to view, sell, and equip items."
starter_guide += "\n5. Use /solo to farm bosses for gear."
starter_guide += "\n6. Use /stamina to check your stamina and use stamina potions."
starter_guide += "\n7. Use /market to buy fae cores, stamina potions, crafting materials, and more."
starter_guide += "\n8. Use /gear to view your equipped gear."
starter_guide += "\n9. Use /info for a command list."
starter_guide += "\n10. Use /profile to view your server card, level, and exp."

intermediate_guide = "1. Use /forge to craft your items. Details can be found in the wiki."
intermediate_guide += "\n2. Use /engrave to engrave an insignia on your soul."
intermediate_guide += " The insignia will grow in strength as you increase your echelon."
intermediate_guide += "\n3. Use /infuse to craft new items."
intermediate_guide += "\n4. Use /stats to check your stats."
intermediate_guide += "\n5. Use /points to allocate skill points and acquire glyphs."
intermediate_guide += "\n6. Use /refinery to refine unprocessed gear items."
intermediate_guide += "\n7. Use /inlay [gem id] to inlay a gem in a socket."
intermediate_guide += "\n8. Use /bind to bind essence items to tarot cards."

advanced_guide = "1. Use /bazaar, /sell, /give, and /buy to trade items."
advanced_guide += "\n2. "
advanced_guide += "\n3."
advanced_guide += "\n4. "
advanced_guide += "\n5."
advanced_guide += "\n6. After clearing quest 23 you can use /purify to upgrade items past tier 5."
advanced_guide += "\n7. After clearing quest 26 you can use /fountain to upgrade tier 6 and higher items."
advanced_guide += "\n7. You can use /scribe to customize perfect items."
guide_dict = {0: ["Beginner Guide", starter_guide],
              1: ["Intermediate Guide", intermediate_guide],
              2: ["Advanced Guide", advanced_guide]}


class GuideMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Beginner", style=discord.ButtonStyle.blurple, emoji="🌟")
    async def beginner_help_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title=guide_dict[0][0], description=guide_dict[0][1])
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Intermediate", style=discord.ButtonStyle.blurple, emoji="✨")
    async def intermediate_help_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title=guide_dict[1][0], description=guide_dict[1][1])
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Advanced", style=discord.ButtonStyle.blurple, emoji="🚀")
    async def advanced_help_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title=guide_dict[2][0], description=guide_dict[2][1])
        await interaction.response.edit_message(embed=embed_msg)


class HelpView(discord.ui.View):
    def __init__(self, category_dict):
        super().__init__(timeout=None)
        self.category_dict = category_dict

    @discord.ui.button(label="Game", style=discord.ButtonStyle.blurple, row=0, emoji="🐉")
    async def game_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict,'game')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Combat", style=discord.ButtonStyle.blurple, row=0, emoji="⚔️")
    async def combat_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'combat')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Gear", style=discord.ButtonStyle.blurple, row=0, emoji="⚔️")
    async def gear_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict,'gear')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Craft", style=discord.ButtonStyle.blurple, row=1, emoji="<:ehammer:1145520259248427069>")
    async def craft_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict,'craft')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Trade", style=discord.ButtonStyle.blurple, row=1, emoji="💲")
    async def trade_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict,'trade')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Info", style=discord.ButtonStyle.blurple, row=1, emoji="ℹ️")
    async def account_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'info')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Admin", style=discord.ButtonStyle.red, row=2, emoji="⌨")
    async def admin_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'admin')
        await interaction.response.edit_message(embed=embed_msg)


def build_help_embed(category_dict, category_name):
    display_category_name = category_name.capitalize()
    embed = discord.Embed(title=f"{display_category_name} Commands:", color=discord.Colour.dark_orange())
    if category_name != "combat":
        commands = category_dict[category_name]
    else:
        commands = combat.combat_command_list
    commands.sort(key=lambda x: x[2])
    if category_name != 'admin':
        command_prefix = '/'
    else:
        command_prefix = '!'
    for command_name, description, _ in commands:
        embed.add_field(name=f"{command_prefix}{command_name}", value=f"{description}", inline=False)
    return embed


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
                emoji="<a:eenergy:1145534127349706772>", label="Weapon",
                description="Inlay gem in your weapon", value="0"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Armour",
                description="Inlay gem in your armour", value="1"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Accessory",
                description="Inlay gem in your accessory", value="2"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wings",
                description="Inlay gem in your wing", value="3"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crest",
                description="Inlay gem in your crest", value="4")
        ]
    )
    async def inlay_select_callback(self, interaction: discord.Interaction, inlay_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_type = int(inlay_select.values[0])
                # Set default embed.
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Inlay Failed.",
                                          description="No item equipped in this slot")
                self.player_user.get_equipped()
                # Confirm an item is equipped in the selected slot.
                if self.player_user.player_equipped[selected_type] == 0:
                    await interaction.response.edit_message(embed=embed_msg)
                    return
                e_item = inventory.read_custom_item(self.player_user.player_equipped[selected_type])
                # Confirm the item has sockets available.
                if e_item.item_num_sockets != 1:
                    embed_msg.description = "The equipped item has no available sockets."
                    await interaction.response.edit_message(embed=embed_msg)
                    return
                # Display confirmation menu.
                embed_msg = e_item.create_citem_embed()
                confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
                await interaction.response.edit_message(embed=embed_msg, view=confirm_view)
        except Exception as e:
            print(e)


class ConfirmInlayView(discord.ui.View):
    def __init__(self, player_user, e_item, gem_id):
        super().__init__(timeout=None)
        self.e_item = e_item
        self.player_user = player_user
        self.gem_id = gem_id

    @discord.ui.button(label="Inlay Gem", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_one_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not inventory.if_custom_exists(self.e_item.item_id):
                    embed_msg = self.e_item.create_citem_embed()
                    embed_msg.add_field(name="Inlay Failed!", value=f"Item with id {self.e_item.item_id}", inline=False)
                    await interaction.response.edit_message(embed=embed_msg, view=None)
                    return
                if not inventory.if_custom_exists(self.gem_id):
                    embed_msg = self.e_item.create_citem_embed()
                    embed_msg.add_field(name="Inlay Failed!", value=f"Item with id {self.gem_id}", inline=False)
                    await interaction.response.edit_message(embed=embed_msg, view=None)
                    return
                # Update the inlaid gem and re-display the item.
                self.e_item.item_inlaid_gem_id = self.gem_id
                self.e_item.update_stored_item()
                embed_msg = self.e_item.create_citem_embed()
                await interaction.response.edit_message(embed=embed_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class StaminaView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player = player_user

    @discord.ui.button(label="Lesser Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t1_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player.player_name:
                reload_player = player.get_player_by_id(self.player.player_id)
                embed_msg = use_stamina_potion(reload_player, "Potion1", 500)
                await interaction.response.edit_message(embed=embed_msg, view=self)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Stamina Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t2_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player.player_name:
                reload_player = player.get_player_by_id(self.player.player_id)
                embed_msg = use_stamina_potion(reload_player, "Potion2", 1000)
                await interaction.response.edit_message(embed=embed_msg, view=self)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Greater Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t3_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player.player_name:
                reload_player = player.get_player_by_id(self.player.player_id)
                embed_msg = use_stamina_potion(reload_player, "Potion3", 2500)
                await interaction.response.edit_message(embed=embed_msg, view=self)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Ultimate Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t4_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player.player_name:
                reload_player = player.get_player_by_id(self.player.player_id)
                embed_msg = use_stamina_potion(reload_player, "Potion4", 5000)
                await interaction.response.edit_message(embed=embed_msg, view=self)
        except Exception as e:
            print(e)


def use_stamina_potion(player_object, item_id, restore_amount):
    potion_stock = inventory.check_stock(player_object, item_id)
    if potion_stock > 0:
        inventory.update_stock(player_object, item_id, -1)
        player_object.player_stamina += restore_amount
        if player_object.player_stamina > 5000:
            player_object.player_stamina = 5000
        player_object.set_player_field("player_stamina", player_object.player_stamina)
    embed_msg = player_object.create_stamina_embed()
    return embed_msg


class GearView(discord.ui.View):
    def __init__(self, player_user, target_user, current_position, view_type):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.target_user = target_user
        self.view_type = view_type
        self.current_position = current_position
        self.previous_button.label = self.get_positional_label(-1)
        self.next_button.label = self.get_positional_label(1)

        if self.current_position <= 4:
            toggle_type = "Gem" if self.view_type == "Gear" else "Gear"
            self.toggle_view_button.label = f"Toggle View ({toggle_type})"
        else:
            self.remove_item(self.children[1])

    def get_positional_label(self, direction):
        gear_button_list = ["Weapon", "Armour", "Accessory", "Wing", "Crest", "Tarot", "Insignia"]
        max_position = 6 if self.view_type == "Gear" else 4
        new_position = (self.current_position + direction) % (max_position + 1)
        button_label = gear_button_list[new_position]
        if self.view_type == "Gem":
            button_label += " Gem"
        return button_label

    def cycle_gear(self, direction):
        reload_user = player.get_player_by_id(self.target_user.player_id)
        no_item = False
        max_position = 6 if self.view_type == "Gear" else 4
        self.current_position = (self.current_position + direction) % (max_position + 1)

        # Handle gear positions.
        if self.current_position <= 4:
            item_type = inventory.item_type_dict[self.current_position]
            selected_item = reload_user.player_equipped[self.current_position]
            if selected_item == 0:
                no_item = True
            else:
                # Handle the view variations.
                equipped_item = inventory.read_custom_item(selected_item)
                if self.view_type == "Gem":
                    if equipped_item.item_inlaid_gem_id == 0:
                        no_item = True
                    else:
                        equipped_gem = inventory.read_custom_item(equipped_item.item_inlaid_gem_id)
                        new_msg = equipped_gem.create_citem_embed()
                else:
                    new_msg = equipped_item.create_citem_embed()

        # Handle tarot position
        elif self.current_position == 5:
            item_type = "Tarot"
            tarot_item = reload_user.equipped_tarot
            if tarot_item == "":
                no_item = True
            else:
                tarot_card = tarot.check_tarot(reload_user.player_id, tarot.card_dict[reload_user.equipped_tarot][0])
                new_msg = tarot_card.create_tarot_embed()
        # Handle insignia position
        else:
            item_type = "Insignia"
            insignia_item = reload_user.insignia
            if insignia_item == "":
                no_item = True
            else:
                new_msg = insignia.display_insignia(reload_user, insignia_item)

        # Build the output
        if no_item:
            no_item = item_type.lower()
            gem_msg = "" if self.view_type == "Gear" else " Gem"
            new_msg = discord.Embed(colour=discord.Colour.dark_gray(),
                                    title=f"Equipped {item_type}{gem_msg}",
                                    description=f"No {no_item}{gem_msg.lower()} is equipped")
        return new_msg

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.cycle_gear(-1)
                new_view = GearView(self.player_user, self.target_user, self.current_position, self.view_type)
                await interaction.response.edit_message(embed=new_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def toggle_view_button(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                self.view_type = "Gear" if self.view_type == "Gem" else "Gem"
                new_msg = self.cycle_gear(0)
                new_view = GearView(self.player_user, self.target_user, self.current_position, self.view_type)
                await interaction.response.edit_message(embed=new_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.cycle_gear(1)
                new_view = GearView(self.player_user, self.target_user, self.current_position, self.view_type)
                await interaction.response.edit_message(embed=new_msg, view=new_view)
        except Exception as e:
            print(e)


class ManageCustomItemView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_item = selected_item
        if self.selected_item.item_type == "D":
            self.equip_item.label = "Inlay"
            self.equip_item.emoji = "🔱"
        self.stored_embed = None

    @discord.ui.button(label="Equip", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def equip_item(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.selected_item.create_citem_embed()
                if self.selected_item.item_type == "D":
                    new_view = InlaySelectView(self.player_user, self.selected_item.item_id)
                    await interaction.response.edit_message(view=new_view)
                else:
                    response = self.player_user.equip(self.selected_item)
                    new_msg.add_field(name=response, value="", inline=False)
                    await interaction.response.edit_message(embed=new_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.success, emoji="💲")
    async def sell_item(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_item = inventory.read_custom_item(self.selected_item.item_id)
                if not self.stored_embed:
                    if selected_item.player_owner == self.player_user.player_id:
                        embed_msg = selected_item.create_citem_embed()
                        new_embed = inventory.sell(self.player_user, selected_item, embed_msg)
                        self.stored_embed = new_embed
                    else:
                        new_embed = selected_item.create_citem_embed()
                        new_embed.add_field(name="Cannot Sell Item!",
                                            value="Item is not owned or currently listed on the bazaar.",
                                            inline=False)
                else:
                    new_embed = self.stored_embed
                await interaction.response.edit_message(embed=new_embed, view=None)
        except Exception as e:
            print(e)


def create_error_embed(error_msg):
    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                              title="Error",
                              description=error_msg)
    return embed_msg


class ClassSelect(discord.ui.View):
    def __init__(self, player_name, username):
        super().__init__(timeout=None)
        self.username = username
        self.player_name = player_name

    @discord.ui.select(
        placeholder="Select a class!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji=globalitems.class_icon_list[0], label="Knight", description="The Valiant Knight"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[1], label="Ranger", description="The Precise Ranger"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[2], label="Mage", description="The Arcane Mage"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[3], label="Assassin", description="The Stealthy Assassin"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[4], label="Weaver", description="The Mysterious Weaver"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[5], label="Rider", description="The Mounted Rider"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[6], label="Summoner", description="The Trusted Summoner")
        ]
    )
    async def class_callback(self, interaction: discord.Interaction, class_select: discord.ui.Select):
        try:
            formatted_player_name = self.player_name
            if interaction.user.discriminator != "":
                formatted_player_name = self.player_name[:-5]
            if interaction.user.name == player_name:
                new_player = player.PlayerProfile()
                formatted_player_name = player.normalize_username(formatted_player_name)
                new_player.player_name = formatted_player_name
                new_player.player_username = self.username
                chosen_class = class_select.values[0]
                response = new_player.add_new_player(chosen_class)
                chosen_class_role = f"Class Role - {chosen_class}"
                add_role = discord.utils.get(interaction.guild.roles, name=chosen_class_role)
                remove_role = discord.utils.get(interaction.guild.roles, name="Class Role - Rat")
                await interaction.user.add_roles(add_role)
                await asyncio.sleep(1)
                await interaction.user.remove_roles(remove_role)
                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                          title="Register",
                                          description=response)
                await interaction.response.edit_message(embed=embed_msg, view=None)
        except Exception as e:
            print("An exception occurred in class_callback:")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {e}")


class ClassChangeView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__(timeout=None)
        self.player_object = player_object
        self.embed = False

    @discord.ui.select(
        placeholder="Select a new class!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji=globalitems.class_icon_list[0], label="Knight", description="The Valiant Knight"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[1], label="Ranger", description="The Precise Ranger"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[2], label="Mage", description="The Arcane Mage"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[3], label="Assassin", description="The Stealthy Assassin"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[4], label="Weaver", description="The Mysterious Weaver"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[5], label="Rider", description="The Mounted Rider"),
            discord.SelectOption(
                emoji=globalitems.class_icon_list[6], label="Summoner", description="The Trusted Summoner")
        ]
    )
    async def change_callback(self, interaction: discord.Interaction, class_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                if not self.embed:
                    reload_player = player.get_player_by_id(self.player_object.player_id)
                    current_class = reload_player.player_class
                    chosen_class = class_select.values[0]
                    token_stock = inventory.check_stock(reload_player, "Token1")
                    if token_stock >= 1:
                        token_stock = inventory.update_stock(reload_player, "Token1", -1)
                        reload_player.set_player_field("player_class", chosen_class)
                        add_role = discord.utils.get(interaction.guild.roles, name=f"Class Role - {chosen_class}")
                        remove_role = discord.utils.get(interaction.guild.roles, name=f"Class Role - {current_class}")
                        await interaction.user.add_roles(add_role)
                        await asyncio.sleep(1)
                        await interaction.user.remove_roles(remove_role)
                        response = f"{reload_player.player_username} you are a {chosen_class} now."
                    else:
                        response = "It seems you are not prepared. You must bring me a pathchanger token."
                    self.embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                               title="Mysmiria, The Changer",
                                               description=response)
                await interaction.response.edit_message(embed=self.embed, view=None)
        except Exception as e:
            print("An exception occurred in change_callback:")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {e}")


class StatView(discord.ui.View):
    def __init__(self, player_user, target_user):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.target_user = target_user

    @discord.ui.button(label="Offensive", style=discord.ButtonStyle.blurple)
    async def offensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.target_user.get_player_stats(1)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Breakdown", style=discord.ButtonStyle.blurple)
    async def breakdown(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.target_user.get_player_stats(2)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Defensive", style=discord.ButtonStyle.blurple)
    async def defensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.target_user.get_player_stats(3)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Multipliers", style=discord.ButtonStyle.blurple)
    async def multiplier_stats(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.target_user.get_player_stats(4)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Points", style=discord.ButtonStyle.blurple)
    async def bonus_stats(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.target_user.get_player_stats(5)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)


class BuyView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_item = selected_item

    @discord.ui.button(label="Confirm Purchase", style=discord.ButtonStyle.success, emoji="⚔️")
    async def confirm(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if self.selected_item.player_owner == -1:
                    bazaar.buy_item(self.selected_item.item_id)
                    self.selected_item.player_owner = self.player_user.player_id
                    self.selected_item.update_stored_item()
                    embed_msg = self.selected_item.create_citem_embed()
                embed_msg.add_field(name="PURCHASE COMPLETED!", value="", inline=False)
                await interaction.response.edit_message(embed=embed_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class PointsView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__()
        self.path_names = player.path_names
        self.player_object = player_object

    @discord.ui.select(
        placeholder="Select a Path",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(emoji=globalitems.path_icon[0], label="Path of Storms",
                                 description="Water, Lightning, and Critical Specialist"),
            discord.SelectOption(emoji=globalitems.path_icon[1], label="Path of Frostfire",
                                 description="Ice, Fire, and Class Specialist"),
            discord.SelectOption(emoji=globalitems.path_icon[2], label="Path of Horizon",
                                 description="Earth, Wind, and Bleed Specialist"),
            discord.SelectOption(emoji=globalitems.path_icon[3], label="Path of Eclipse",
                                 description="Dark, Light, and Ultimate Specialist"),
            discord.SelectOption(emoji=globalitems.path_icon[4], label="Path of Stars",
                                 description="Celestial and Combo Specialist"),
            discord.SelectOption(emoji=globalitems.path_icon[5], label="Path of Time",
                                 description="Time Control Specialist"),
            discord.SelectOption(emoji=globalitems.path_icon[5], label="Path of Confluence",
                                 description="Multi Elemental Specialist"),
            discord.SelectOption(emoji="❌", label="Reset",
                                 description="Reset all skill points")
        ]
    )
    async def path_select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.name == self.player_object.player_name:
            selected_path = select.values[0]
            if selected_path == "Reset":
                response = "Starting over is no easy feat. You'll first need to bring me a token."
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title="Avalon, Pathwalker of the True Laws",
                                          description=response)
                new_view = ResetView(self.player_object)
            else:
                embed_msg = self.player_object.build_points_embed(selected_path)
                new_view = PointsMenu(self.player_object, selected_path)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)


class PointsMenu(discord.ui.View):
    def __init__(self, player_object, selected_path):
        super().__init__()
        self.player_object = player_object
        self.selected_path = selected_path
        self.embed_msg = None
        self.view = None

    @discord.ui.button(emoji="1️⃣", label="Allocate 1", style=discord.ButtonStyle.primary)
    async def add_one_point(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name == self.player_object.player_name:
            if not self.embed_msg:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                response = reload_player.allocate_points(self.selected_path, 1)
                self.embed_msg = reload_player.build_points_embed(self.selected_path)
                self.embed_msg.add_field(name="", value=response, inline=False)
                self.view = PointsMenu(reload_player, self.selected_path)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    @discord.ui.button(emoji="5️⃣", label="Allocate 5", style=discord.ButtonStyle.primary)
    async def add_five_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name == self.player_object.player_name:
            if not self.embed_msg:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                response = reload_player.allocate_points(self.selected_path, 5)
                self.embed_msg = reload_player.build_points_embed(self.selected_path)
                self.embed_msg.add_field(name="", value=response, inline=False)
                self.view = PointsMenu(reload_player, self.selected_path)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    @discord.ui.button(emoji="🔟", label="Allocate 10", style=discord.ButtonStyle.primary)
    async def add_ten_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name == self.player_object.player_name:
            if not self.embed_msg:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                response = reload_player.allocate_points(self.selected_path, 10)
                self.embed_msg = reload_player.build_points_embed(self.selected_path)
                self.embed_msg.add_field(name="", value=response, inline=False)
                self.view = PointsMenu(reload_player, self.selected_path)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.secondary)
    async def reselect_path_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name == self.player_object.player_name:
            reload_player = player.get_player_by_id(self.player_object.player_id)
            embed_msg = reload_player.create_path_embed()
            points_view = PointsView(reload_player)
            await interaction.response.edit_message(embed=embed_msg, view=points_view)


class ResetView(discord.ui.View):
    def __init__(self, player_object):
        super().__init__()
        self.player_object = player_object
        self.embed_msg = None

    @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name == self.player_object.player_name:
            if not self.embed_msg:
                reload_player = player.get_player_by_id(self.player_object.player_id)
                num_tokens = inventory.check_stock(reload_player, "Token3")
                if num_tokens >= 1:
                    inventory.update_stock(reload_player, "Token3", -1)
                    reload_player.reset_skill_points()
                    result_msg = "ALL SKILL POINTS RESET!"
                else:
                    result_msg = "Come back when you have a token."
                self.embed_msg = reload_player.create_path_embed()
                self.embed_msg.add_field(name=result_msg, value="", inline=False)
            points_view = PointsView(reload_player)
            await interaction.response.edit_message(embed=self.embed_msg, view=points_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.secondary)
    async def reselect_path_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name == self.player_object.player_name:
            reload_player = player.get_player_by_id(self.player_object.player_id)
            embed_msg = reload_player.create_path_embed()
            points_view = PointsView(reload_player)
            if self.embed_msg:
                embed_msg.add_field(name="ALL SKILL POINTS RESET!", value="", inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=points_view)
