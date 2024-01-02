import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.ui import Button, View
from discord import app_commands
import asyncio
import csv
import pandas as pd
import mysql.connector
from mysql.connector.errors import Error
import sys
from datetime import datetime as dt, timedelta

import globalitems
import adventure
import inventory
import bosses
import random
import loot
import forge
import player
import combat
import menus
import quest
import tarot
import market
import bazaar
import insignia
import infuse
import pilengine
import pandoracogs


# Get Bot Token
token_info = None
with open("pandora_bot_token.txt", 'r') as token_file:
    for line in token_file:
        token_info = line
TOKEN = token_info

# Initialize database
db_info = None
with open("bot_db_login.txt", 'r') as data_file:
    for line in data_file:
        db_info = line.split(";")


class PandoraBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())


def run_discord_bot():
    print(sys.version)
    pandora_bot = PandoraBot()

    class CommandPlaceholder:
        def __init__(self, category):
            self.category = category

    def set_command_category(category, command_position):
        def decorator(func):
            func.category_type = category
            func.position = command_position
            return func
        return decorator

    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            minutes = seconds / 60
            hours = int(minutes / 60)
            await ctx.send(f'This command is on a {hours} hour cooldown')
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send('You are at your command limit for this command')
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            await ctx.reply(error, ephemeral=True)

    async def on_shutdown():
        print("Pandora Bot Off")
        try:
            await engine_bot.close()
            await engine_bot.session.close()
        except KeyboardInterrupt:
            sys.exit(0)

    @pandora_bot.event
    async def on_ready():
        print(f'{pandora_bot.user} Online!')
        pandoracogs.StaminaCog(pandora_bot)
        pandora_bot.help_command = CustomHelpCommand()

    class CustomHelpCommand(commands.DefaultHelpCommand):
        def __init__(self):
            super().__init__()

        async def send_bot_help(self, mapping):
            embed = discord.Embed(title="Help Command Menu")
            embed_msg = menus.build_help_embed(category_dict, 'info')
            help_view = menus.HelpView(category_dict)
            await self.get_destination().send(embed=embed_msg, view=help_view)

        async def send_command_help(self, command):
            # Customize the help message when !help <command> is used
            embed = discord.Embed(title=f"Help for (!{command.name}) Command")
            embed.add_field(name="Usage", value=f"```{self.get_command_signature(command)}```", inline=False)
            embed.add_field(name="Description", value=command.help, inline=False)

            await self.get_destination().send(embed=embed)

    # Admin Commands
    @set_command_category('admin', 0)
    @pandora_bot.command(name='sync', help="Archael Only")
    async def sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                synced = await pandora_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Pandora Bot Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @set_command_category('admin', 1)
    @pandora_bot.command(name='reset_sync', help="Archael Only")
    async def reset_sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                global_sync = await pandora_bot.tree.sync(guild=None)
                print(f"Pandora Bot Synced! {len(global_sync)} global command(s)")
                synced = await pandora_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Pandora Bot Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @set_command_category('admin', 2)
    @pandora_bot.command(name='admin', help="Tester Only")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def admin(ctx, backdoor, value):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            user = ctx.author
            achievement_list = []
            roles_list = [r.name for r in user.roles]
            if "Passcard - Pandora Tester" in roles_list:
                player_object = player.get_player_by_name(user)
                if backdoor == "stamina_hack":
                    player_object.set_player_field("player_stamina", int(value))
                if backdoor == "item_hack":
                    inventory.update_stock(player_object, value, 10)
                if backdoor == "item_hack_all":
                    filename = "itemlist.csv"
                    with (open(filename, 'r') as f):
                        for item_line in csv.DictReader(f):
                            inventory.update_stock(player_object, str(item_line['item_id']), 10)
            else:
                await ctx.send("Only testers can use this command.")

    @pandora_bot.event
    async def on_user_update(before, after):
        if before.name != after.name:
            temp_player = player.get_player_by_name(before.name)
            temp_player.player_name = after.name
            temp_player.set_player_field("player_name", after.name)

    # Game Commands
    @set_command_category('game', 0)
    @pandora_bot.hybrid_command(name='map', help="Explore! Stamina Cost: 200 + 50/map tier")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def expedition(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_name = str(ctx.author)
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Map Exploration",
                                          description="Please select an expedition.")
                embed_msg.set_image(url="")
                map_select_view = adventure.MapSelectView(player_object, embed_msg)
                await ctx.send(embed=embed_msg, view=map_select_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 1)
    @pandora_bot.hybrid_command(name='quest', help="Check and hand in quests.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def story_quest(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(str(user))
            current_quest = player_object.player_quest
            if current_quest != 0:
                current_quest = player_object.player_quest
                quest_object = quest.get_quest(current_quest, player_object)
                quest_message = quest_object.get_quest_embed(player_object)
                quest_view = quest.QuestView(player_object, quest_object)
                await ctx.send(embed=quest_message, view=quest_view)
            elif current_quest > 30:
                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                          title="Quests",
                                          description="All quests completed!")
                await ctx.send(embed=embed_msg)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 2)
    @pandora_bot.hybrid_command(name='stamina', help="Display your stamina and use potions.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def stamina(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = player_object.create_stamina_embed()
                stamina_view = menus.StaminaView(player_object)
                await ctx.send(embed=embed_msg, view=stamina_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 3)
    @pandora_bot.hybrid_command(name='points', help="Assign your skill points.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def points(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                existing_id = bosses.get_raid_id(channel_id, player_object.player_id)
                if existing_id == 0:
                    embed_msg = player_object.create_path_embed()
                    points_view = menus.PointsView(player_object)
                    await ctx.send(embed=embed_msg, view=points_view)
                else:
                    await ctx.send("You cannot speak to Lyra while in combat.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 4)
    @pandora_bot.hybrid_command(name='manifest',
                                help="Manifest the echo of a bound paragon to perform a task. Cost: 500 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def manifest(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class == "":
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)
                return
            difference, method_info = player_object.check_cooldown("manifest")
            colour, icon = inventory.get_gear_tier_colours(player_object.player_echelon)
            num_hours = 6 + player_object.player_echelon
            if difference:
                wait_time = timedelta(hours=num_hours)
                cooldown = wait_time - difference
                if difference <= wait_time:
                    cooldown_timer = int(cooldown.total_seconds() / 60 / 60)
                    time_msg = f"Your manifestation will return in {cooldown_timer} hours."
                    embed_msg = discord.Embed(colour=colour,
                                              title="Echo Manifestation",
                                              description=time_msg)
                else:
                    player_object.clear_cooldown("manifest")
                    embed_msg = adventure.build_manifest_return_embed(player_object, method_info, colour)
                await ctx.send(embed=embed_msg)
            else:
                player_object.get_equipped()
                if player_object.equipped_tarot != "":
                    tarot_info = player_object.equipped_tarot.split(";")
                    e_tarot = tarot.check_tarot(player_object.player_id,
                                                tarot.tarot_card_list(int(tarot_info[0])), int(tarot_info[1]))
                else:
                    e_tarot = tarot.TarotCard(player_object.player_id, "II", 1,
                                              "Pandora, The Celestial", 0, 0, 0)
                manifest_description = ""
                embed_msg = discord.Embed(colour=colour)
                if player_object.equipped_tarot != "":
                    embed_msg.set_image(url=e_tarot.card_image_link)
                    embed_msg.title = f"Echo of {e_tarot.card_name}"
                    manifest_description = "What do you need me to help you with?"
                    display_stars = ""
                    for x in range(e_tarot.num_stars):
                        display_stars += "<:estar1:1143756443967819906>"
                    for y in range((5 - e_tarot.num_stars)):
                        display_stars += "<:ebstar2:1144826056222724106>"
                    manifest_description += f"\nSelected Tarot Rating: {display_stars}"
                else:
                    embed_msg.title = "Pandora, The Celestial"
                    manifest_description = ("You don't seem to have any tarot cards set to perform echo manifestation."
                                            " Let's divide and conquer. I'll handle the task for you. What would you"
                                            " like me to help with?")
                embed_msg.description = manifest_description
                if player_object.player_echelon < 2:
                    new_view = adventure.ManifestView1(player_object, embed_msg, e_tarot, colour, num_hours)
                elif player_object.player_echelon < 4:
                    new_view = adventure.ManifestView2(player_object, embed_msg, e_tarot, colour, num_hours)
                else:
                    new_view = adventure.ManifestView3(player_object, embed_msg, e_tarot, colour, num_hours)
                await ctx.send(embed=embed_msg, view=new_view)

    @set_command_category('game', 5)
    @pandora_bot.hybrid_command(name='crate', help="Open a crate.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def crate(ctx):
        await ctx.defer()
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                crate_id = "i1r"
                crate_stock = inventory.check_stock(player_object, crate_id)
                if crate_stock >= 1:
                    inventory.update_stock(player_object, crate_id, -1)
                    embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                              title=f"{player_object.player_username}: Opening Crate!",
                                              description="What could be inside?")
                    reward_id, quantity = loot.generate_random_item()
                    loot_item = loot.BasicItem(reward_id)
                    inventory.update_stock(player_object, reward_id, quantity)
                    message = await open_lootbox(ctx, embed_msg, loot_item.item_tier)
                    loot_description = f"{loot_item.item_emoji} {quantity}x {loot_item.item_name}"
                    embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                              title=f"{player_object.player_username}: Crate Opened!",
                                              description=loot_description)
                    await message.edit(embed=embed_msg)
                else:
                    loot_item = loot.BasicItem(crate_id)
                    await ctx.send(f"Out of stock: {loot_item.item_emoji}!")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 6)
    @pandora_bot.hybrid_command(name='trove', help="Open a trove!")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def trove(ctx, trove_tier: int):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                if trove_tier in range(1, 5):
                    trove_id = f"i{trove_tier}j"
                    loot_item = loot.BasicItem(trove_id)
                    trove_stock = inventory.check_stock(player_object, trove_id)
                    if trove_stock >= 1:
                        inventory.update_stock(player_object, trove_id, -1)
                        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                                  title=f"{player_object.player_username}: Opening {loot_item.item_name}!",
                                                  description="Feeling lucky today?")
                        reward_coins = loot.generate_trove_reward(trove_tier)
                        player_object.player_coins += reward_coins
                        player_object.set_player_field("player_coins", player_object.player_coins)
                        message = await open_lootbox(ctx, embed_msg, trove_tier)
                        loot_description = f"{globalitems.coin_icon} {reward_coins:,}x Lotus Coins!"
                        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                                  title=f"{player_object.player_username}: Trove Opened!",
                                                  description=loot_description)
                        await message.edit(embed=embed_msg)
                    else:
                        await ctx.send(f"Out of stock: {loot_item.item_emoji}!")
                else:
                    await ctx.send(f"Please enter a valid tier.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 7)
    @pandora_bot.hybrid_command(name='changer', help="Change your class.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def changer(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_name = ctx.author
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                existing_id = bosses.get_raid_id(channel_id, player_object.player_id)
                if existing_id == 0:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Mysmiria, The Changer",
                                              description="With the right payment even you can be rewritten.")
                    new_view = menus.ClassChangeView(player_object)
                    await ctx.send(embed=embed_msg, view=new_view)
                else:
                    await ctx.send("You cannot speak to the changer while in combat.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 8)
    @pandora_bot.hybrid_command(name='who', help="Set a new username.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def who(ctx, new_username: str):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            existing_user = player.get_player_by_name(ctx.author)
            if not new_username.isalpha():
                await ctx.send("Please enter a valid username. No special or numeric characters.")
                return
            if not player.check_username(new_username):
                await ctx.send("Username already in use.")
                return
            if len(new_username) > 10:
                await ctx.send("Please enter a username 10 or less characters.")
                return
            token_stock = inventory.check_stock(existing_user, "cNAME")
            if token_stock < 1:
                await ctx.send(f"It's not that easy to change your name. Bring me a token to prove you are serious.")
            else:
                inventory.update_stock(existing_user, "cNAME", -1)
                existing_user.player_username = new_username
                existing_user.set_player_field("player_username", new_username)
                await ctx.send(f'Got it! I\'ll call you {existing_user.player_username} from now on!')

    @pandora_bot.event
    async def open_lootbox(ctx, embed_msg, item_tier):
        message = await ctx.send(embed=embed_msg)
        opening_chest = ""
        for t in range(1, item_tier + 1):
            opening_chest += "♦️"
            tier_colour, tier_icon = inventory.get_gear_tier_colours(t)
            embed_msg.add_field(name="", value=opening_chest)
            await message.edit(embed=embed_msg)
            await asyncio.sleep(1)
            embed_msg.clear_fields()
            opening_chest += tier_icon
            embed_msg.add_field(name="", value=opening_chest)
            await message.edit(embed=embed_msg)
            await asyncio.sleep(1)
            embed_msg.clear_fields()
        await asyncio.sleep(1)
        embed_msg.clear_fields()
        return message

    # Gear commands
    @set_command_category('gear', 0)
    @pandora_bot.hybrid_command(name='gear', help="Display your equipped gear items.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def gear(ctx, user: discord.User = None):
        await ctx.defer()
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if user:
                target_user = player.get_player_by_name(str(user.name))
            else:
                target_user = player_object
            if target_user.player_class != "":
                target_user.get_equipped()
                if target_user.player_equipped[0] != 0:
                    equipped_item = inventory.read_custom_item(target_user.player_equipped[0])
                    embed_msg = equipped_item.create_citem_embed()
                    gear_view = menus.GearView(player_object, target_user)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_gray(),
                                              title="Equipped weapon",
                                              description="No weapon is equipped")
                    gear_view = None
                await ctx.send(embed=embed_msg, view=gear_view)
            else:
                await ctx.send("Target user is not registered.")

    @set_command_category('gear', 1)
    @pandora_bot.hybrid_command(name='inv', help="Display your item and gear inventories.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def inv(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                inventory_view = inventory.BInventoryView(player_object)
                inventory_title = f'{player_object.player_username}\'s Crafting Inventory:\n'
                player_inventory = inventory.display_binventory(player_object.player_id, "Crafting")
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title,
                                          description=player_inventory)
                await ctx.send(embed=embed_msg, view=inventory_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('gear', 2)
    @pandora_bot.hybrid_command(name='display', help="Display a specific item.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def display_item(ctx, item_id: str):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            item_view = None
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="An item with this ID does not exist.",
                                      description=f"Inputted ID: {item_id}")
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                if item_id.isnumeric():
                    gear_id = int(item_id)
                    if inventory.if_custom_exists(gear_id):
                        selected_item = inventory.read_custom_item(gear_id)
                        embed_msg = selected_item.create_citem_embed()
                        if selected_item.player_owner == -1:
                            seller_id = bazaar.get_seller_by_item(gear_id)
                            seller_object = player.get_player_by_id(seller_id)
                            owner_msg = f"Listed for sale by: {seller_object.player_username}"
                        else:
                            item_owner = player.get_player_by_id(selected_item.player_owner)
                            owner_msg = f"Owned by: {item_owner.player_username}"
                        embed_msg.add_field(name="", value=owner_msg)
                        if player_object.player_id == selected_item.player_owner:
                            item_view = menus.ManageCustomItemView(player_object, gear_id)
                elif item_id.isalnum():
                    selected_item = loot.BasicItem(item_id)
                    if selected_item.item_id != "":
                        embed_msg = selected_item.create_loot_embed(player_object)
                        # item_view = menus.ManageBasicItem(player_object, selected_item)
            else:
                embed_msg = unregistered_message()
            await ctx.send(embed=embed_msg, view=item_view)

    @set_command_category('gear', 3)
    @pandora_bot.hybrid_command(name='tarot', help="View your tarot collection.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def tarot_collection(ctx, start_location: int = 0):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                if start_location in range(0, 23):
                    completion_count = tarot.collection_check(player_object.player_id)
                    embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                              title=f"{player_object.player_username}'s Tarot Collection",
                                              description=f"Completion Total: {completion_count} / 46")
                    embed_msg.set_image(url="")
                    tarot_view = tarot.CollectionView(player_object, embed_msg, start_location)
                    await ctx.send(embed=embed_msg, view=tarot_view)
                else:
                    await ctx.send("Please enter a valid start location from 0-22 or leave the start location blank.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('gear', 4)
    @pandora_bot.hybrid_command(name='inlay', help="Inlay a gem into an equipped gear item.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def inlay(ctx, item_id: int):
        await ctx.defer()
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            if inventory.if_custom_exists(item_id):
                selected_item = inventory.read_custom_item(item_id)
                player_object = player.get_player_by_name(str(ctx.author))
                if player_object.player_class != "":
                    if player_object.player_id == selected_item.player_owner:
                        embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                                  title="Inlay Gem",
                                                  description="Let me know what item you'd like to inlay this gem into!")
                        embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                        view = menus.InlaySelectView(player_object, selected_item.item_id)
                        view.embed = await ctx.send(embed=embed_msg, view=view)

                    else:
                        response = "wrong item id"
                        await ctx.send(response)
                else:
                    embed_msg = unregistered_message()
                    await ctx.send(embed=embed_msg)
            else:
                response = "wrong item id"
                await ctx.send(response)

    @set_command_category('gear', 5)
    @pandora_bot.hybrid_command(name='engrave', help="Engrave an insignia on your soul.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def engrave(ctx):
        await ctx.defer()
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                engrave_msg = "You've come a long way from home child. Tell me, what kind of power do you seek?"
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Weaver Lord, Isabelle",
                                          description=engrave_msg)
                insignia_view = insignia.InsigniaView(player_object)
                await ctx.send(embed=embed_msg, view=insignia_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    # Trading Commands
    @set_command_category('trade', 0)
    @pandora_bot.hybrid_command(name='sell', help="List a gear item for sale in the bazaar.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def sell(ctx, item_id: int, cost: int):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                if not player.checkNaN(item_id) and not player.checkNaN(cost):
                    num_listings = bazaar.check_num_listings(player_object)
                    if num_listings < 6:
                        if inventory.if_custom_exists(item_id):
                            selected_item = inventory.read_custom_item(item_id)
                            if selected_item.item_tier > 3:
                                response = player_object.check_equipped(selected_item)
                                if response == "":
                                    bazaar.list_custom_item(selected_item, cost)
                                    await ctx.send(f"Item {item_id} has been listed for {cost} lotus coins.")
                                else:
                                    await ctx.send(response)
                            else:
                                await ctx.send(f"Only tier 4 or higher gear items can be listed at the Bazaar.")
                        else:
                            await ctx.send(f"Item {item_id} could not be listed.")
                    else:
                        await ctx.send("Already at maximum allowed listings.")
                else:
                    await ctx.send(f"Invalid inputs, please enter numeric values only.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('trade', 1)
    @pandora_bot.hybrid_command(name='buy', help="Buy an item that is listed on the Bazaar.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def buy(ctx, item_id: int):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                if inventory.if_custom_exists(item_id):
                    selected_item = inventory.read_custom_item(item_id)
                    if selected_item.player_owner == -1:
                        embed_msg = selected_item.create_citem_embed()
                        buy_view = menus.BuyView(player_object, selected_item)
                        await ctx.send(embed=embed_msg, view=buy_view)
                    else:
                        await ctx.send(f"Item {item_id} is not for sale.")
                else:
                    await ctx.send(f"Item {item_id} does not exist.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('trade', 2)
    @pandora_bot.hybrid_command(name='retrieve', help="Retrieve your items listed on the Bazaar.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def retrieve(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                num_items = bazaar.retrieve_items(player_object.player_id)
                await ctx.send(f"{num_items} unsold items retrieved.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('trade', 3)
    @pandora_bot.hybrid_command(name='bazaar', help="View the Bazaar.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def view_bazaar(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                embed_msg = bazaar.show_bazaar_items()
                bazaar_view = None
                await ctx.send(embed=embed_msg, view=bazaar_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('trade', 4)
    @pandora_bot.hybrid_command(name='market', help="Visit the black market item shop.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def black_market(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_name = str(ctx.author)
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Black Market",
                                          description="Everything has a price.")
                embed_msg.set_image(url="")
                market_select_view = market.TierSelectView(player_object)
                await ctx.send(embed=embed_msg, view=market_select_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('trade', 5)
    @pandora_bot.hybrid_command(name='give', help="Transfer ownership of a gear item.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def give(ctx, item_id: int, receiving_player: discord.User):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                selected_item = inventory.read_custom_item(item_id)
                if selected_item:
                    response = player_object.check_equipped(selected_item)
                    if response == "":
                        embed_msg = selected_item.create_citem_embed()
                        target_player_object = player.get_player_by_name(receiving_player.name)
                        if player.check_user_exists(target_player_object.player_id):
                            owner_check = selected_item.player_owner
                            if selected_item.player_owner == -1:
                                owner_check = bazaar.get_seller_by_item(item_id)
                            if player_object.player_id == owner_check:

                                selected_item.give_item(target_player_object.player_id)
                                embed_title = "Item Transfer Complete!"
                                embed_description = f"User: {target_player_object.player_username} has received item: {item_id}"
                        else:
                            embed_title = "Target user is not registered."
                            embed_description = f"Unregistered users cannot receive items."
                    else:
                        embed_title = f"Item {item_id} could not be transferred."
                        embed_description = response
                else:
                    embed_title = f"Item {item_id} could not be transferred."
                    embed_description = response
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=embed_title,
                                          description=embed_description)
            else:
                embed_msg = unregistered_message()
            await ctx.send(embed=embed_msg)

    @set_command_category('trade', 6)
    @pandora_bot.hybrid_command(name='purge', help="Sells all gear in or below a tier.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def purge(ctx, tier: int):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            existing_user = player.get_player_by_name(ctx.author)
            if tier in range(1, 6):
                result, coin_total = inventory.purge(existing_user, tier)
                message = f"{result} items sold.\n {globalitems.coin_icon} {coin_total}x lotus coins acquired."
            else:
                message = "The tier must be between 1 and 5."
            await ctx.send(message)

    # Crafting Commands
    @set_command_category('craft', 0)
    @pandora_bot.hybrid_command(name='forge', help="Go to Pandora's Celestial Forge")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def celestial_forge(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                player_object.get_equipped()
                embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                          title="Pandora's Celestial Forge",
                                          description="Let me know what you'd like me to upgrade today!")
                embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                forge_view = forge.SelectView(player_object, "celestial")
                await ctx.send(embed=embed_msg, view=forge_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('craft', 1)
    @pandora_bot.hybrid_command(name='refinery', help="Go to the refinery.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def refinery(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_name = str(ctx.author)
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title='',
                                          description="Please select the item to refine")
                embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                ref_view = forge.RefSelectView(player_object)
                await ctx.send(embed=embed_msg, view=ref_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('craft', 2)
    @pandora_bot.hybrid_command(name='bind', help="Perform a binding ritual on an essence.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def bind_ritual(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                bind_view = menus.BindingTierView(player_object)
                await ctx.send(embed=embed_msg, view=bind_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.hybrid_command(name='testing', help="Testing Command.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def testing(ctx):
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title="This command is for testing purposes.",
                                  description="This command serves no function.")
        await ctx.send(embed=embed_msg)

    @set_command_category('craft', 3)
    @pandora_bot.hybrid_command(name='infuse', help="Infuse items using alchemy.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def infusion(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Cloaked Alchemist, Sangam",
                                          description="I can make anything, if you bring the right stuff.")
                embed_msg.set_image(url="")
                infuse_view = infuse.InfuseView(player_object)
                await ctx.send(embed=embed_msg, view=infuse_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

        # Crafting Commands
    @set_command_category('craft', 4)
    @pandora_bot.hybrid_command(name='purify', help="Purify voidforged gear items.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def void_purification(ctx):
        await ctx.defer()
        user = ctx.author
        player_object = player.get_player_by_name(user)
        if player_object.player_class != "":
            player_object.get_equipped()
            e_weapon = inventory.read_custom_item(player_object.player_equipped[0])
            if player_object.player_quest >= 27:
                entry_msg = ("Within this cave resides the true abyss. Only a greater darkness can cleanse the void "
                             "and reveal the true form. The costs will be steep, I trust you came prepared. "
                             "Nothing can save you down there.")
                embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                          title="Echo of Oblivia",
                                          description=entry_msg)
                embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                new_view = forge.SelectView(player_object, "purify")
            else:
                embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                          title="???",
                                          description="A great darkness clouds your path. Entry is impossible.")
                new_view = None
            await ctx.send(embed=embed_msg, view=new_view)
        else:
            embed_msg = unregistered_message()
            await ctx.send(embed=embed_msg)

    @set_command_category('craft', 5)
    @pandora_bot.hybrid_command(name='fountain', help="Go to the ???")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def fountain(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                player_object.get_equipped()
                e_weapon = inventory.read_custom_item(player_object.player_equipped[0])
                if player_object.player_quest >= 27:
                    entry_msg = ("You who has defiled my wish now seek to realize your own. Just ahead resides the "
                                 "fountain of genesis, origin of all. The power you still covet can be acquired here. "
                                 "Go now, I am no longer qualified to stand in your path.")
                    embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                              title="Echo of Eleuia",
                                              description=entry_msg)
                    embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                    new_view = forge.SelectView(player_object, "miracle")
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                              title="???",
                                              description="A powerful light emanates from within. Entry is impossible.")
                    new_view = None
                await ctx.send(embed=embed_msg, view=new_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    # Info commands
    @set_command_category('info', 0)
    @pandora_bot.hybrid_command(name='info', help="Display the help menu.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def help_menu(ctx):
        await ctx.defer()
        embed = discord.Embed(title="Help Command Menu")
        embed_msg = menus.build_help_embed(category_dict, 'info')
        help_view = menus.HelpView(category_dict)
        await ctx.send(embed=embed_msg, view=help_view)

    @set_command_category('info', 1)
    @pandora_bot.hybrid_command(name='register', help="Register a new user.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def play(ctx, username: str):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            user = ctx.author
            if not username.isalpha():
                await ctx.send("Please enter a valid username.")
                return
            if not player.check_username(username):
                await ctx.send("Username already in use.")
                return
            if len(username) > 10:
                await ctx.send("Please enter a username 10 or less characters.")
                return
            register_msg = ('In an ancient ruin you come across an empty room in which sits a peculiar box. '
                            'Hesitating at first you consider the possibility of a trap or mimic. '
                            'Without a trap in sight you reach forward and open the box.\n'
                            'A flurry of souls flood the room and leak out into the corridor. '
                            'One pauses and speaks softly into your mind. '
                            '"Everything begins and ends with a wish. What do you wish to be?" '
                            'You think it for only a second and the voice responds with a playful laugh, '
                            '"Let it be so." Then the voice disappears without a trace. '
                            'Silence falls and then all that remains is an '
                            'otherworldly girl staring at you in confusion.')
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title="Register - Select Class",
                                      description=register_msg)
            player_name = str(user)
            class_view = menus.ClassSelect(player_name, username)
            await ctx.send(embed=embed_msg, view=class_view)

    @set_command_category('info', 2)
    @pandora_bot.hybrid_command(name='guide', help="Display basic starter guide.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def guide(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title=menus.guide_dict[0][0],
                                      description=menus.guide_dict[0][1])
            current_guide = "Beginner"
            guide_view = menus.GuideMenu()
            await ctx.send(embed=embed_msg, view=guide_view)

    @set_command_category('info', 3)
    @pandora_bot.hybrid_command(name='stats', help="Display your stats page.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def stats(ctx, user: discord.User = None):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            command_user = ctx.author
            player_object = player.get_player_by_name(command_user)
            if user:
                target_user = player.get_player_by_name(user.name)
            else:
                target_user = player_object
            if target_user.player_class != "":
                embed_msg = target_user.get_player_stats(1)
                stat_view = menus.StatView(player_object, target_user)
                await ctx.send(embed=embed_msg, view=stat_view)
            else:
                await ctx.send("Selected user is not registered.")

    @set_command_category('info', 4)
    @pandora_bot.hybrid_command(name='profile', help="View profile rank card.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def profile(ctx, user: discord.User = None):
        await ctx.defer()
        command_user = ctx.author
        achv_list = []
        if user:
            target_name = user.name
            achv_list = [role.name for role in user.roles if "Holder" in role.name or "Herrscher" in role.name]
        else:
            target_name = command_user.name
            achv_list = [role.name for role in command_user.roles if "Holder" in role.name or "Herrscher" in role.name]
        target_user = player.get_player_by_name(target_name)
        if target_user.player_class != "":
            filepath = pilengine.get_player_profile(target_user, achv_list)
            file_object = discord.File(filepath)
            await ctx.send(file=file_object)
        else:
            await ctx.send(f"Target user {target_name} is not registered")

    @set_command_category('info', 5)
    @pandora_bot.command(name='credits', help="Displays the game credits.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def credits_list(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            credit_list = "Game created by: Kyle Mistysyn (Archael)"
            # Artists
            credit_list += "\n@labcornerr - Emoji Artist (Fiverr)"
            credit_list += "\n@Nong Dit - Artist (Fiverr)"
            # Programming
            credit_list += "\nBahamutt - Programming Assistance"
            credit_list += "\nPota - Programming Assistance"
            # Testers
            credit_list += "\nZweii - Alpha Tester"
            credit_list += "\nSoulViper - Alpha Tester"
            embed_msg = discord.Embed(colour=discord.Colour.light_gray(),
                                      title="Credits",
                                      description=credit_list)
            embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
            await ctx.send(embed=embed_msg)

    def unregistered_message():
        register_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                       title="Unregistered",
                                       description="Please register using !register to play.")
        return register_embed

    def build_category_dict():
        temp_dict = {}
        for command in pandora_bot.walk_commands():
            if hasattr(command, 'category_type'):
                category_name = command.category_type
                if category_name not in temp_dict:
                    temp_dict[category_name] = []
                temp_dict[category_name].append((command.name, command.help, command.position))
        return temp_dict

    category_dict = build_category_dict()
    pandora_bot.run(TOKEN)
