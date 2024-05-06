# General imports
import discord
from discord.ui import Button, View
import asyncio
import random

# Data imports
import globalitems

# Core imports
import player
import inventory
import quest
import combat
import skillpaths
import bazaar

# Item/crafting imports
import loot
import insignia
import pact
import tarot


starter_guide = "1. Use /quest to progress through the quest."
starter_guide += "\n2. Use /map to farm for tier 1-4 Weapons, Armour, Amulets, and EXP."
starter_guide += "\n3. Use /inv to check your inventory. Then click Toggle to check your gear."
starter_guide += "\n4. Use /display [item id] to view, sell, inlay, and equip items."
starter_guide += "\n5. Use /solo to farm tier 1-4 bosses for gear. Stones can be used to select the boss type."
starter_guide += "\n6. Use /stamina to check your stamina and consume stamina potions."
starter_guide += "\n7. Use /market to buy fae cores, stamina potions, crafting materials, and more."
starter_guide += "\n8. Use /gear to view your equipped gear, gems, pact, tarot, and insignia."
starter_guide += "\n9. Use /info for a command list."
starter_guide += "\n10. Use /profile to view your server card, level, and exp."

intermediate_guide = "1. Use /forge to craft your items. Details can be found in the wiki."
intermediate_guide += "\n2. Use /manifest to hunt monsters for more exp."
intermediate_guide += "\n3. Use /points to allocate skill points and acquire glyphs."
intermediate_guide += "\n4. Use /infuse to transmute new items."
intermediate_guide += "\n5. Use /stats to check your stats details and point glyphs."
intermediate_guide += "\n6. Use /engrave to engrave an insignia on your soul. Req Quest: 20"
intermediate_guide += "\n7. Use /refinery to refine powerful unprocessed gear items."
intermediate_guide += "\n8. Use /tarot [card number] to bind essence items to tarot cards."
intermediate_guide += "\n9. Use /bazaar, /sell, /give, /trade, and /buy to trade items."


advanced_guide = "1. Use /summon and spend summoning items to fight powerful opponents above tier 5!"
advanced_guide += "\n2. Use /gauntlet to challenge the difficult Spire of Illusions for great rewards!"
advanced_guide += "\n3. Use /abyss to upgrade gear items past tier 5. Req Quest: 38"
advanced_guide += "\n4. Use /scribe to attain perfect rolls on your items."
advanced_guide += "\n5. Use /meld to combine and upgrade heart jewels to higher tiers. Req Quest: 42"
advanced_guide += "\n6. Use /purge [itemtype] [Tier] to clear out useless low tier items."
advanced_guide += "\n7. Use /infuse to create ring gear items using rare materials."
advanced_guide += "\n8. Use /sanctuary and search everywhere for the rare and elusive lotus items."
advanced_guide += "\n9. Challenge /palace on higher difficulties to raise the level limit and reach alternate endings."
advanced_guide += "\n10. Fight for the top stop on the /leaderboard for unique roles."
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
                emoji="<a:eenergy:1145534127349706772>", label="Greaves",
                description="Inlay gem in your Greaves", value="2"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Amulet",
                description="Inlay gem in your amulet", value="3"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wings",
                description="Inlay gem in your wing", value="5"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Crest",
                description="Inlay gem in your crest", value="6")
        ]
    )
    async def inlay_select_callback(self, interaction: discord.Interaction, inlay_select: discord.ui.Select):
        if interaction.user.id != self.player_user.discord_id:
            return
        selected_type = int(inlay_select.values[0])
        # Set default embed.
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title="Inlay Failed.", description="No item equipped in this slot")
        await self.player_user.reload_player()
        # Confirm an item is equipped in the selected slot.
        if self.player_user.player_equipped[selected_type] == 0:
            await interaction.response.edit_message(embed=embed_msg)
            return
        e_item, gem_item = await asyncio.gather(
            inventory.read_custom_item(self.player_user.player_equipped[selected_type]),
            inventory.read_custom_item(self.gem_id)
        )
        if e_item is None or gem_item is None:
            embed_msg.description = "Cannot load items."
            await interaction.response.edit_message(embed=embed_msg)
            return
        # Confirm the item has sockets available.
        if e_item.item_num_sockets != 1:
            embed_msg.description = "The equipped item has no available sockets."
            await interaction.response.edit_message(embed=embed_msg)
            return
        # Confirm the tier is eligible
        if e_item.item_tier < gem_item.item_tier:
            embed_msg.description = "Gem must be inlaid in an equal or higher tier item."
            await interaction.response.edit_message(embed=embed_msg)
            return
        # Display confirmation menu.
        embed_msg = await e_item.create_citem_embed()
        confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
        await interaction.response.edit_message(embed=embed_msg, view=confirm_view)


class ConfirmInlayView(discord.ui.View):
    def __init__(self, player_user, e_item, gem_id):
        super().__init__(timeout=None)
        self.e_item = e_item
        self.player_user = player_user
        self.gem_id = gem_id

    @discord.ui.button(label="Inlay Gem", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_one_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                if not inventory.if_custom_exists(self.e_item.item_id):
                    embed_msg = await self.e_item.create_citem_embed()
                    embed_msg.add_field(name="Inlay Failed!", value=f"Item with id {self.e_item.item_id}", inline=False)
                    await interaction.response.edit_message(embed=embed_msg, view=None)
                    return
                if not inventory.if_custom_exists(self.gem_id):
                    embed_msg = await self.e_item.create_citem_embed()
                    embed_msg.add_field(name="Inlay Failed!", value=f"Item with id {self.gem_id}", inline=False)
                    await interaction.response.edit_message(embed=embed_msg, view=None)
                    return
                # Update the inlaid gem and re-display the item.
                self.e_item.item_inlaid_gem_id = self.gem_id
                self.e_item.update_stored_item()
                embed_msg = await self.e_item.create_citem_embed()
                await interaction.response.edit_message(embed=embed_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class StaminaView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player = player_user

    @discord.ui.button(label="Lesser Potion", style=discord.ButtonStyle.success, emoji=globalitems.stamina_icon)
    async def t1_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 1, 500)

    @discord.ui.button(label="Stamina Potion", style=discord.ButtonStyle.success, emoji=globalitems.stamina_icon)
    async def t2_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 2, 1000)

    @discord.ui.button(label="Greater Potion", style=discord.ButtonStyle.success, emoji=globalitems.stamina_icon)
    async def t3_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 3, 2500)

    @discord.ui.button(label="Ultimate Potion", style=discord.ButtonStyle.success, emoji=globalitems.stamina_icon)
    async def t4_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 4, 5000)

    async def drink_potion(self, interaction, potion_version, potion_value):
        if interaction.user.id != self.player.discord_id:
            return
        await self.player.reload_player()
        embed_msg = self.use_stamina_potion(f"Potion{potion_version}", potion_value)
        await interaction.response.edit_message(embed=embed_msg, view=self)

    def use_stamina_potion(self, item_id, restore_amount):
        potion_stock = inventory.check_stock(self.player, item_id)
        if potion_stock > 0:
            pact_object = pact.Pact(self.player.pact)
            max_stamina = 5000 if pact_object.pact_variant != "Sloth" else 2500
            inventory.update_stock(self.player, item_id, -1)
            self.player.player_stamina += restore_amount
            if self.player.player_stamina > max_stamina:
                self.player.player_stamina = max_stamina
            self.player.set_player_field("player_stamina", self.player.player_stamina)
        embed_msg = self.player.create_stamina_embed()
        return embed_msg


gear_button_list = ["Weapon", "Armour", "Greaves", "Amulet",  "Ring", "Wing", "Crest", "Pact", "Insignia", "Tarot"]


class GearView(discord.ui.View):
    def __init__(self, player_user, target_user, current_position, view_type):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.target_user = target_user
        self.view_type = view_type
        self.current_position = current_position
        self.previous_button.label = self.get_positional_label(-1)
        self.next_button.label = self.get_positional_label(1)

        if self.current_position <= 6:
            toggle_type = "Gem" if self.view_type == "Gear" else "Gear"
            self.toggle_view_button.label = f"Toggle View ({toggle_type})"
        else:
            self.remove_item(self.children[1])

    def get_positional_label(self, direction):
        max_position = 9 if self.view_type == "Gear" else 6
        new_position = (self.current_position + direction) % (max_position + 1)
        button_label = gear_button_list[new_position]
        return f"{button_label} Gem" if self.view_type == "Gem" else button_label

    async def cycle_gear(self, direction):
        await self.target_user.reload_player()
        max_position = 9 if self.view_type == "Gear" else 6
        self.current_position = (self.current_position + direction) % (max_position + 1)

        # Build no item return message
        item_type = gear_button_list[self.current_position]
        no_item = item_type.lower()
        gem_msg = "" if self.view_type == "Gear" else " Gem"
        no_item_msg = discord.Embed(colour=discord.Colour.dark_gray(), title=f"Equipped {item_type}{gem_msg}",
                                    description=f"No {no_item}{gem_msg.lower()} is equipped")
        # Handle gear positions.
        if self.current_position <= 6:
            item_type = inventory.item_type_dict[self.current_position]
            selected_item = self.target_user.player_equipped[self.current_position]
            if selected_item == 0:
                return no_item_msg
            # Handle the view variations.
            equipped_item = await inventory.read_custom_item(selected_item)
            if self.view_type == "Gem":
                if equipped_item.item_inlaid_gem_id == 0:
                    return no_item_msg
                equipped_gem = await inventory.read_custom_item(equipped_item.item_inlaid_gem_id)
                return await equipped_gem.create_citem_embed()
            return await equipped_item.create_citem_embed()

        # Handle tarot position.
        elif self.current_position == 9:
            tarot_item = self.target_user.equipped_tarot
            if tarot_item == "":
                return no_item_msg
            tarot_card = tarot.check_tarot(self.target_user.player_id, tarot.card_dict[self.target_user.equipped_tarot][0])
            return tarot_card.create_tarot_embed()
        # Handle insignia position.
        if self.current_position == 8:
            insignia_item = self.target_user.insignia
            if insignia_item == "":
                return no_item_msg
            insignia_obj = insignia.Insignia(self.target_user, insignia_code=insignia_item)
            return insignia_obj.insignia_output
        # Handle pact position.
        if self.current_position == 7:
            if self.target_user.pact == "":
                return no_item_msg
            return pact.display_pact(self.target_user)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        new_msg = await self.cycle_gear(-1)
        new_view = GearView(self.player_user, self.target_user, self.current_position, self.view_type)
        await interaction.response.edit_message(embed=new_msg, view=new_view)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def toggle_view_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        self.view_type = "Gear" if self.view_type == "Gem" else "Gem"
        new_msg = await self.cycle_gear(0)
        new_view = GearView(self.target_user, self.target_user, self.current_position, self.view_type)
        await interaction.response.edit_message(embed=new_msg, view=new_view)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        new_msg = await self.cycle_gear(1)
        new_view = GearView(self.target_user, self.target_user, self.current_position, self.view_type)
        await interaction.response.edit_message(embed=new_msg, view=new_view)


class ManageCustomItemView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_item = selected_item
        if "D" in self.selected_item.item_type:
            self.equip_item.label = "Inlay"
            self.equip_item.emoji = "🔱"
        self.stored_embed = None

    @discord.ui.button(label="Equip", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def equip_item(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                new_msg = await self.selected_item.create_citem_embed()
                if "D" in self.selected_item.item_type:
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
        if interaction.user.id == self.player_user.discord_id:
            selected_item = await inventory.read_custom_item(self.selected_item.item_id)
            if not self.stored_embed:
                if selected_item.player_owner == self.player_user.player_id:
                    embed_msg = await selected_item.create_citem_embed()
                    new_embed = await inventory.sell(self.player_user, selected_item, embed_msg)
                    self.stored_embed = new_embed
                else:
                    new_embed = await selected_item.create_citem_embed()
                    new_embed.add_field(name="Cannot Sell Item!",
                                        value="Item is not owned or currently listed on the bazaar.", inline=False)
            else:
                new_embed = self.stored_embed
            await interaction.response.edit_message(embed=new_embed, view=None)


def create_error_embed(error_msg):
    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title="Error", description=error_msg)
    return embed_msg


class ClassSelect(discord.ui.View):
    def __init__(self, discord_id, username):
        super().__init__(timeout=None)
        self.username = username
        self.discord_id = discord_id

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
        if interaction.user.id != self.discord_id:
            return
        new_player = player.PlayerProfile()
        new_player.player_username = self.username
        chosen_class = class_select.values[0]
        msg = await new_player.add_new_player(chosen_class, interaction.user.id)
        chosen_class_role = f"Class Role - {chosen_class}"
        add_role = discord.utils.get(interaction.guild.roles, name=chosen_class_role)
        remove_role = discord.utils.get(interaction.guild.roles, name="Class Role - Rat")
        await interaction.user.add_roles(add_role)
        await asyncio.sleep(1)
        await interaction.user.remove_roles(remove_role)
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title="Registration Complete!", description=msg)
        await interaction.response.edit_message(embed=embed_msg, view=None)


class ClassChangeView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.embed = False

    @discord.ui.select(
        placeholder="Select a new class!",
        min_values=1, max_values=1,
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
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=None)
            return
        await self.player_obj.reload_player()
        current_class = self.player_obj.player_class
        chosen_class = class_select.values[0]
        token_stock = inventory.check_stock(self.player_obj, "Token1")
        if token_stock >= 50:
            token_stock = inventory.update_stock(self.player_obj, "Token1", -50)
            self.player_obj.set_player_field("player_class", chosen_class)
            add_role = discord.utils.get(interaction.guild.roles, name=f"Class Role - {chosen_class}")
            remove_role = discord.utils.get(interaction.guild.roles, name=f"Class Role - {current_class}")
            await interaction.user.add_roles(add_role)
            await asyncio.sleep(1)
            await interaction.user.remove_roles(remove_role)
            response = f"{self.player_obj.player_username} you are a {chosen_class} now."
        else:
            response = "Not enough tokens. I refuse."
        self.embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                   title="Mysmir, The Changer", description=response)
        await interaction.response.edit_message(embed=self.embed, view=None)



class StatView(discord.ui.View):
    def __init__(self, player_user, target_user):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.target_user = target_user

    @discord.ui.button(label="Offense", style=discord.ButtonStyle.blurple, row=1)
    async def offensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(1)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Defense", style=discord.ButtonStyle.blurple, row=1)
    async def defensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(3)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Details", style=discord.ButtonStyle.blurple, row=1)
    async def breakdown(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(2)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Multipliers", style=discord.ButtonStyle.blurple, row=1)
    async def multiplier_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(4)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Points", style=discord.ButtonStyle.blurple, row=2)
    async def bonus_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(5)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Glyphs", style=discord.ButtonStyle.blurple, row=2)
    async def glyphs(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(6)
        await interaction.response.edit_message(embed=new_msg)


class BuyView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_item = selected_item

    @discord.ui.button(label="Confirm Purchase", style=discord.ButtonStyle.success, emoji="⚔️")
    async def confirm(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                if self.selected_item.player_owner == -1:
                    await bazaar.buy_item(self.selected_item.item_id)
                    self.selected_item.player_owner = self.player_user.player_id
                    self.selected_item.update_stored_item()
                    embed_msg = await self.selected_item.create_citem_embed()
                embed_msg.add_field(name="PURCHASE COMPLETED!", value="", inline=False)
                await interaction.response.edit_message(embed=embed_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class PointsView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__()
        self.path_names = globalitems.path_names
        self.player_obj = player_obj

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
            discord.SelectOption(emoji=globalitems.path_icon[5], label="Path of Solitude",
                                 description="Mono Element and Time Specialist"),
            discord.SelectOption(emoji=globalitems.path_icon[5], label="Path of Confluence",
                                 description="Multi Elemental Specialist"),
            discord.SelectOption(emoji="❌", label="Reset",
                                 description="Reset all skill points")
        ]
    )
    async def path_select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id == self.player_obj.discord_id:
            await self.player_obj.reload_player()
            selected_path = select.values[0]
            if selected_path == "Reset":
                token_object = inventory.BasicItem("Token3")
                token_cost = sum(self.player_obj.player_stats) // 10
                token_stock = inventory.check_stock(self.player_obj, "Token3")
                response = (f"The farther you are, the harder it is to go back to the start.\nReset Cost:\n "
                            f"{token_object.item_emoji} {token_object.item_name}: {token_stock} / {token_cost}")
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Avalon, Pathwalker of the True Laws",
                                          description=response)
                new_view = ResetView(self.player_obj)
            else:
                embed_msg = skillpaths.build_points_embed(self.player_obj, selected_path)
                new_view = PointsMenu(self.player_obj, selected_path)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)


class PointsMenu(discord.ui.View):
    def __init__(self, player_obj, selected_path):
        super().__init__()
        self.player_obj = player_obj
        self.selected_path = selected_path
        self.embed_msg = None
        self.view = None

    @discord.ui.button(emoji="1️⃣", label="Allocate 1", style=discord.ButtonStyle.primary)
    async def add_one_point(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.allocate_callback(1)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    @discord.ui.button(emoji="5️⃣", label="Allocate 5", style=discord.ButtonStyle.primary)
    async def add_five_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.allocate_callback(5)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    @discord.ui.button(emoji="🔟", label="Allocate 10", style=discord.ButtonStyle.primary)
    async def add_ten_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.allocate_callback(10)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    async def allocate_callback(self, num_points):
        if not self.embed_msg:
            await self.player_obj.reload_player()
            response = skillpaths.allocate_points(self.player_obj, self.selected_path, num_points)
            self.embed_msg = skillpaths.build_points_embed(self.player_obj, self.selected_path)
            self.embed_msg.add_field(name="", value=response, inline=False)
            self.view = PointsMenu(self.player_obj, self.selected_path)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.secondary)
    async def reselect_path_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.player_obj.reload_player()
            embed_msg = skillpaths.create_path_embed(self.player_obj)
            points_view = PointsView(self.player_obj)
            await interaction.response.edit_message(embed=embed_msg, view=points_view)


class ResetView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__()
        self.player_obj = player_obj
        self.embed_msg = None

    @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            if not self.embed_msg:
                await self.player_obj.reload_player()
                token_cost = sum(self.player_obj.player_stats) // 10
                token_stock = inventory.check_stock(self.player_obj, "Token3")
                if token_stock >= token_cost:
                    inventory.update_stock(self.player_obj, "Token3", -1)
                    self.player_obj.reset_skill_points()
                    result_msg = "ALL SKILL POINTS RESET!"
                else:
                    result_msg = "Come back when you have a token."
                await self.player_obj.reload_player()
                self.embed_msg = skillpaths.create_path_embed(self.player_obj)
                self.embed_msg.add_field(name=result_msg, value="", inline=False)
            points_view = PointsView(self.player_obj)
            await interaction.response.edit_message(embed=self.embed_msg, view=points_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.secondary)
    async def reselect_path_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.player_obj.reload_player()
            embed_msg = skillpaths.create_path_embed(self.player_obj)
            points_view = PointsView(self.player_obj)
            if self.embed_msg:
                embed_msg.add_field(name="ALL SKILL POINTS RESET!", value="", inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=points_view)
