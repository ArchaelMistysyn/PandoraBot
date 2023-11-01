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


class HelpView(discord.ui.View):
    def __init__(self, category_dict):
        super().__init__(timeout=None)
        self.category_dict = category_dict

    @discord.ui.button(label="Game", style=discord.ButtonStyle.blurple, row=0, emoji="🐉")
    async def game_help_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        embed_msg = build_help_embed(self.category_dict,'game')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Gear", style=discord.ButtonStyle.blurple, row=0, emoji="⚔️")
    async def gear_help_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        embed_msg = build_help_embed(self.category_dict,'gear')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Craft", style=discord.ButtonStyle.blurple, row=0, emoji="<:ehammer:1145520259248427069>")
    async def craft_help_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        embed_msg = build_help_embed(self.category_dict,'craft')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Trade", style=discord.ButtonStyle.blurple, row=1, emoji="💲")
    async def trade_help_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        embed_msg = build_help_embed(self.category_dict,'trade')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Info", style=discord.ButtonStyle.blurple, row=1, emoji="ℹ️")
    async def account_help_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        embed_msg = build_help_embed(self.category_dict, 'info')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Admin", style=discord.ButtonStyle.red, row=1, emoji="⌨")
    async def admin_help_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        embed_msg = build_help_embed(self.category_dict, 'admin')
        await interaction.response.edit_message(embed=embed_msg)


def build_help_embed(category_dict, category_name):
    display_category_name = category_name.capitalize()
    embed = discord.Embed(title=f"{display_category_name} Commands:", color=discord.Colour.dark_orange())
    commands = category_dict[category_name]
    commands.sort(key=lambda x: x[2])
    if category_name != 'admin':
        command_prefix = '/'
    else:
        command_prefix = '!'
    for command_name, description, _ in commands:
        embed.add_field(name=f"{command_prefix}{command_name}", value=f"{description}", inline=False)
    return embed


# Raid View
class RaidView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join the raid!", style=discord.ButtonStyle.success, emoji="⚔️")
    async def raid_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        clicked_by = player.get_player_by_name(str(interaction.user))
        outcome = clicked_by.player_username
        outcome += bosses.add_participating_player(interaction.channel.id, clicked_by.player_id)
        await interaction.response.send_message(outcome)


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
        try:
            if interaction.user.name == self.player_user.player_name:
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
                embed_msg = use_stamina_potion(reload_player, "i1y", 500)
                await interaction.response.edit_message(embed=embed_msg, view=self)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Stamina Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t2_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player.player_name:
                reload_player = player.get_player_by_id(self.player.player_id)
                embed_msg = use_stamina_potion(reload_player, "i2y", 1000)
                await interaction.response.edit_message(embed=embed_msg, view=self)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Greater Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t3_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player.player_name:
                reload_player = player.get_player_by_id(self.player.player_id)
                embed_msg = use_stamina_potion(reload_player, "i3y", 2500)
                await interaction.response.edit_message(embed=embed_msg, view=self)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Ultimate Potion", style=discord.ButtonStyle.success, emoji="<:estamina:1145534039684562994>")
    async def t4_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player.player_name:
                reload_player = player.get_player_by_id(self.player.player_id)
                embed_msg = use_stamina_potion(reload_player, "i4y", 5000)
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
        try:
            if interaction.user.name == self.player_user.player_name:
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
        except Exception as e:
            print(e)


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
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = PerformRitualView(self.player_user, bind_select.values[0])
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                new_view = BindingTierView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


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
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = PerformRitualView(self.player_user, bind_select.values[0])
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                new_view = BindingTierView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


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
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = PerformRitualView(self.player_user, bind_select.values[0])
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                new_view = BindingTierView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


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
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = PerformRitualView(self.player_user, bind_select.values[0])
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                new_view = BindingTierView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


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
                emoji="<a:eenergy:1145534127349706772>", label="IV", description="Essence of The Infinite"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="XXX", description="Essence of The Wish")
        ]
    )
    async def bind_select_callback(self, interaction: discord.Interaction, bind_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_view = PerformRitualView(self.player_user, bind_select.values[0])
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                new_view = BindingTierView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class PerformRitualView(discord.ui.View):
    def __init__(self, player_user, essence_type):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.essence_type = essence_type

    @discord.ui.button(label="Bind Essence", style=discord.ButtonStyle.blurple, emoji="<a:eshadow2:1141653468965257216>")
    async def attempt_bind(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = binding_ritual(self.player_user, self.essence_type)
                await interaction.response.edit_message(embed=embed_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                new_view = BindingTierView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


def binding_ritual(player_object, essence_type):
    filename = ""
    essence_id = f't{essence_type}'
    essence_stock = inventory.check_stock(player_object, essence_id)
    if essence_stock > 0:
        inventory.update_stock(player_object, essence_id, -1)
        random_num = random.randint(1, 8)
        if random_num == 1:
            variant_num = 2
        elif random_num <= 4:
            variant_num = 1
        else:
            variant_num = 0
        if variant_num == 0:
            result = "Binding Failed!"
            description_msg = "The essence is gone."
        else:
            name_position = tarot.get_number_by_numeral(essence_type)
            card_name = tarot.tarot_card_list(name_position)
            tarot_check = tarot.check_tarot(player_object.player_id, card_name, variant_num)
            if tarot_check:
                new_qty = tarot_check.card_qty + 1
                tarot_check.set_tarot_field("card_qty", new_qty)
            else:
                new_tarot = tarot.TarotCard(player_object.player_id, essence_type, variant_num, card_name,
                                            1, 1, 0)
                new_tarot.add_tarot_card()
            result = "Binding Successful!"
            description_msg = "The sealed tarot card has been added to your collection."
    else:
        loot_item = loot.BasicItem(essence_id)
        result = "Ritual Failed!"
        description_msg = f"Out of stock: {loot_item.item_emoji}!"

    embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                              title=result,
                              description=description_msg)
    embed_msg.set_image(url=filename)
    return embed_msg


class GearView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.current_position = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous_gear(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                direction = -1
                new_msg, self.current_position = cycle_gear(self.player_user, self.current_position, direction)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_gear(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                direction = 1
                new_msg, self.current_position = cycle_gear(self.player_user, self.current_position, direction)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)


def cycle_gear(user, current_position, direction):
    reload_user = player.get_player_by_id(user.player_id)

    no_item = ""
    if current_position == 0 and direction == -1:
        new_position = 6
    elif current_position == 6 and direction == 1:
        new_position = 0
    else:
        new_position = current_position + direction

    match new_position:
        case 0:
            item_type = "Weapon"
            selected_item = reload_user.equipped_weapon
        case 1:
            item_type = "Armour"
            selected_item = reload_user.equipped_armour
        case 2:
            item_type = "Accessory"
            selected_item = reload_user.equipped_acc
        case 3:
            item_type = "Wing"
            selected_item = reload_user.equipped_wing
        case 4:
            item_type = "Crest"
            selected_item = reload_user.equipped_crest
        case 5:
            item_type = "Tarot"
            tarot_item = reload_user.equipped_tarot
        case _:
            item_type = "Insignia"
            insignia_item = reload_user.insignia
    no_item = False
    type_list_1 = ["Weapon", "Armour", "Accessory", "Wing", "Crest"]
    if item_type in type_list_1:
        if selected_item == 0:
            no_item = True
        else:
            equipped_item = inventory.read_custom_item(selected_item)
            new_msg = equipped_item.create_citem_embed()
    elif item_type == "Tarot":
        if tarot_item == "":
            no_item = True
        else:
            tarot_info = reload_user.equipped_tarot.split(";")
            tarot_card = tarot.check_tarot(reload_user.player_id, tarot.tarot_card_list(int(tarot_info[0])), int(tarot_info[1]))
            new_msg = tarot.create_tarot_embed(tarot_card)
    else:
        if insignia_item == "":
            no_item = True
        else:
            new_msg = insignia.display_insignia(reload_user, insignia_item, "Embed")
    if no_item:
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
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_item = inventory.read_custom_item(self.item_id)
                new_msg = selected_item.create_citem_embed()
                response = self.player_user.equip(selected_item)
                new_msg.add_field(name=response, value="", inline=False)
                await interaction.response.edit_message(embed=new_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.success, emoji="💲")
    async def sell_item(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_item = inventory.read_custom_item(self.item_id)
                embed_msg = selected_item.create_citem_embed()
                response_embed = inventory.sell(self.player_user, selected_item, embed_msg)
                await interaction.response.edit_message(embed=response_embed, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                await interaction.response.edit_message(view=None)
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
        try:
            if interaction.user.name == self.player_name:
                new_player = player.PlayerProfile()
                new_player.player_name = self.player_name
                new_player.player_username = self.username
                chosen_class = globalitems.class_icon_dict[class_select.values[0]]
                response = new_player.add_new_player(chosen_class)
                chosen_class_role = f"Class Role - {class_select.values[0]}"
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


class StatView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.button(label="Offensive", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def offensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.player_user.get_player_stats(1)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Defensive", style=discord.ButtonStyle.blurple, emoji="🛡️")
    async def defensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.player_user.get_player_stats(2)
                await interaction.response.edit_message(embed=new_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Bonuses", style=discord.ButtonStyle.blurple, emoji="🔫")
    async def bonus_stats(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                new_msg = self.player_user.get_player_stats(3)
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

