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
with open("bot_token.txt", 'r') as token_file:
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
        else:
            await ctx.reply(error, ephemeral=True)
        raise error

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
    @pandora_bot.command(name='init_bosses', help="Archael Only")
    async def initialize_bosses(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                timer = 60
                for server in globalitems.global_server_channels:
                    command_channel_id = server[0]
                    cmd_channel = pandora_bot.get_channel(command_channel_id)
                    for x in range(1, 5):
                        raid_channel_id = server[x]
                        raid_channel = pandora_bot.get_channel(raid_channel_id)
                        await raid_task(raid_channel_id, x, raid_channel)
                    restore_boss_list = bosses.restore_solo_bosses(command_channel_id)
                    for idy, y in enumerate(restore_boss_list):
                        player_object = player.get_player_by_id(y.player_id)
                        await solo_boss_task(player_object, y, command_channel_id, cmd_channel)
                print("Initialized Bosses")
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @set_command_category('admin', 1)
    @pandora_bot.command(name='sync', help="Archael Only")
    async def sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                synced = await pandora_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @set_command_category('admin', 2)
    @pandora_bot.command(name='reset_sync', help="Archael Only")
    async def reset_sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                global_sync = await pandora_bot.tree.sync(guild=None)
                print(f"Synced! {len(global_sync)} global command(s)")
                synced = await pandora_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @set_command_category('admin', 3)
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
                    player_object.set_player_field("player_stamina", value)
                if backdoor == "item_hack":
                    inventory.update_stock(player_object, value, 10)
                if backdoor == "item_hack_all":
                    filename = "itemlist.csv"
                    with (open(filename, 'r') as f):
                        for item_line in csv.DictReader(f):
                            inventory.update_stock(player_object, str(item_line['item_id']), int(value))
            else:
                await ctx.send("Only testers can use this command.")

    @pandora_bot.event
    async def on_user_update(before, after):
        if before.name != after.name:
            temp_player = player.get_player_by_name(before.name)
            temp_player.player_name = after.name
            temp_player.set_player_field("player_name", after.name)

    @pandora_bot.event
    async def solo_boss_task(player_object, active_boss, channel_id, channel_object):
        embed_msg = active_boss.create_boss_embed(0)
        sent_message = await channel_object.send(embed=embed_msg)
        player_object.get_player_multipliers()
        solo_cog = pandoracogs.SoloCog(pandora_bot, player_object, active_boss, channel_id, sent_message, channel_object)
        await solo_cog.run()

    @pandora_bot.event
    async def raid_task(channel_id, channel_num, channel_object):
        level, boss_type, boss_tier = bosses.get_boss_details(channel_num)
        active_boss = bosses.spawn_boss(channel_id, 0, boss_tier, boss_type, level, channel_num)
        embed_msg = active_boss.create_boss_embed(0)
        raid_button = menus.RaidView()
        sent_message = await channel_object.send(embed=embed_msg, view=raid_button)
        pandoracogs.RaidCog(pandora_bot, active_boss, channel_id, channel_num, sent_message, channel_object)

    @pandora_bot.event
    async def raid_boss(combat_tracker_list, active_boss, channel_id, channel_num, sent_message, channel_object):
        player_list, damage_list = bosses.get_damage_list(channel_id)
        active_boss.reset_modifiers()
        temp_user = []
        dps = 0
        for idy, y in enumerate(player_list):
            temp_user.append(player.get_player_by_id(int(y)))
            temp_user[idy].get_player_multipliers()
            active_boss.aura += temp_user[idy].aura
            curse_lists = [active_boss.curse_debuffs, temp_user[idy].elemental_curse]
            active_boss.curse_debuffs = [sum(z) for z in zip(*curse_lists)]
            if idy >= len(combat_tracker_list):
                combat_tracker_list.append(combat.CombatTracker())
                combat_tracker_list[idy].player_cHP = temp_user[idy].player_mHP
        player_msg_list = []
        for idx, x in enumerate(temp_user):
            player_msg, player_damage = combat.run_raid_cycle(combat_tracker_list[idx], active_boss, x)
            new_player_damage = int(damage_list[idx]) + player_damage
            dps += int(combat_tracker_list[idx].total_dps / combat_tracker_list[idx].total_cycles)
            bosses.update_player_damage(channel_id, x.player_id, new_player_damage)
            player_msg_list.append(player_msg)
        bosses.update_boss_cHP(channel_id, 0, active_boss.boss_cHP)
        if active_boss.calculate_hp():
            embed_msg = active_boss.create_boss_embed(dps)
            for m in player_msg_list:
                embed_msg.add_field(name="", value=m, inline=False)
            await sent_message.edit(embed=embed_msg)
            return True
        else:
            embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
            for m in player_msg_list:
                embed_msg.add_field(name="", value=m, inline=False)
            await sent_message.edit(embed=embed_msg)
            loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
            await channel_object.send(embed=loot_embed)
            return False

    @pandora_bot.event
    async def solo_boss(combat_tracker, player_object, active_boss, channel_id, sent_message, channel_object):
        active_boss.reset_modifiers()
        player_object.get_player_multipliers()
        active_boss.curse_debuffs = player_object.elemental_curse
        active_boss.aura = player_object.aura
        embed_msg = combat.run_solo_cycle(combat_tracker, active_boss, player_object)
        bosses.update_boss_cHP(channel_id, active_boss.player_id, active_boss.boss_cHP)
        if active_boss.calculate_hp():
            await sent_message.edit(embed=embed_msg)
            return True
        else:
            is_alive = False
            await sent_message.edit(embed=embed_msg)
            player_list = [player_object.player_id]
            loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
            bosses.clear_boss_info(channel_id, player_object.player_id)
            await channel_object.send(embed=loot_embed)
            return False

    # Game Commands
    @set_command_category('game', 0)
    @pandora_bot.hybrid_command(name='solo', help="Challenge a solo boss. Stamina Cost: 200")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def solo(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            player_name = ctx.author
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                if player_object.equipped_weapon != 0:
                    existing_id = bosses.get_raid_id(channel_id, player_object.player_id)
                    if existing_id == 0:
                        if player_object.spend_stamina(200):
                            max_spawn = player_object.player_echelon
                            if max_spawn > 2:
                                max_spawn = 2
                            spawned_boss = random.randint(0, max_spawn)
                            boss_type = bosses.boss_list[spawned_boss]
                            new_boss_tier = bosses.get_random_bosstier(boss_type)
                            active_boss = bosses.spawn_boss(channel_id, player_object.player_id, new_boss_tier,
                                                            boss_type, player_object.player_lvl, 0)
                            active_boss.player_id = player_object.player_id
                            embed_msg = active_boss.create_boss_embed(0)
                            channel_object = ctx.channel
                            spawn_msg = f"{player_object.player_username} has spawned a tier {active_boss.boss_tier} boss!"
                            await ctx.send(spawn_msg)
                            player_object.get_player_multipliers()
                            sent_message = await channel_object.send(embed=embed_msg)
                            solo_cog = pandoracogs.SoloCog(pandora_bot, player_object, active_boss,
                                                           channel_id, sent_message, channel_object)
                            await solo_cog.run()
                        else:
                            await ctx.send("Not enough stamina.")
                    else:
                        await ctx.send("You already have a solo boss encounter running.")

                else:
                    await ctx.send("You must have a weapon equipped.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 1)
    @pandora_bot.hybrid_command(name='map', help="Explore! Stamina Cost: 200 + 50/map tier")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def expedition(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
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

    @set_command_category('game', 2)
    @pandora_bot.hybrid_command(name='quest', help="Check and hand in quests.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def story_quest(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
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

    @set_command_category('game', 3)
    @pandora_bot.hybrid_command(name='stamina', help="Display your stamina and use potions.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def stamina(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = player_object.create_stamina_embed()
                stamina_view = menus.StaminaView(player_object)
                await ctx.send(embed=embed_msg, view=stamina_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 4)
    @pandora_bot.hybrid_command(name='bdsm', help="Claim daily reward.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def bdsm(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                run_command = False
                difference = player_object.check_cooldown("bdsm")
                if difference:
                    one_day = timedelta(days=1)
                    cooldown = one_day - difference
                    if difference <= one_day:
                        cooldown_timer = int(cooldown.total_seconds() / 60 / 60)
                        time_msg = f"Your shipment is on cooldown for {cooldown_timer} hours."
                        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                                  title="Boxed Daily Shipment!",
                                                  description=time_msg)
                        await ctx.send(embed=embed_msg)
                    else:
                        run_command = True
                else:
                    run_command = True

                if run_command:
                    player_object.set_cooldown("bdsm")
                    random_qty = random.randint(0, 10)
                    if random_qty <= 7:
                        quantity = 1
                    elif random_qty <= 9:
                        quantity = 2
                    else:
                        quantity = 3
                    crate_id = "i1r"
                    loot_item = loot.BasicItem(crate_id)
                    inventory.update_stock(player_object, crate_id, quantity)
                    embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                              title=f"{player_object.player_username}: Boxed Daily Shipment!",
                                              description=f"{loot_item.item_emoji} {quantity}x Daily crate acquired!")
                    await ctx.send(embed=embed_msg)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('game', 5)
    @pandora_bot.hybrid_command(name='crate', help="Open a crate.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def crate(ctx):
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
                        loot_description = f"{globalitems.coin_icon} {reward_coins}x Lotus Coins!"
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
            existing_user = player.get_player_by_name(ctx.author)
            if new_username.isalpha():
                if player.check_username(new_username):
                    token_stock = inventory.check_stock(existing_user, "cNAME")
                    if token_stock >= 1:
                        inventory.update_stock(existing_user, "cNAME", -1)
                        existing_user.player_username = new_username
                        existing_user.set_player_field("player_username", new_username)
                        message = f'Got it! I\'ll call you {existing_user.player_username} from now on!'
                    else:
                        message = f"It's not that easy to change your name. Bring me a token to prove you are serious."
                else:
                    message = f'Sorry that username is taken.'
            else:
                message = "Please enter a valid username with no numeric or special characters."
            await ctx.send(message)

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
    async def gear(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                player_object.get_equipped()
                if player_object.equipped_weapon != 0:
                    equipped_item = inventory.read_custom_item(player_object.equipped_weapon)
                    embed_msg = equipped_item.create_citem_embed()
                    gear_view = menus.GearView(player_object)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_gray(),
                                              title="Equipped weapon",
                                              description="No weapon is equipped")
                    gear_view = None
                await ctx.send(embed=embed_msg, view=gear_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('gear', 1)
    @pandora_bot.hybrid_command(name='inv', help="Display your item and gear inventories.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def inv(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                inventory_view = inventory.BInventoryView(player_object)
                inventory_title = f'{player_object.player_username}\'s Inventory:\n'
                player_inventory = inventory.display_binventory(player_object.player_id, "Crafting Items")
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title,
                                          description=player_inventory)
                await ctx.send(embed=embed_msg, view=inventory_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('gear', 2)
    @pandora_bot.hybrid_command(name='display', help="Display a specific gear item.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def display_item(ctx, gear_id: str):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                if gear_id.isnumeric():
                    item_id = int(gear_id)
                    if inventory.if_custom_exists(item_id):
                        selected_item = inventory.read_custom_item(item_id)
                        embed_msg = selected_item.create_citem_embed()
                        if selected_item.player_owner == -1:
                            seller_id = bazaar.get_seller_by_item(item_id)
                            seller_object = player.get_player_by_id(seller_id)
                            owner_msg = f"Listed for sale by: {seller_object.player_username}"
                        else:
                            item_owner = player.get_player_by_id(selected_item.player_owner)
                            owner_msg = f"Owned by: {item_owner.player_username}"
                        embed_msg.add_field(name="", value=owner_msg)
                        if player_object.player_id == selected_item.player_owner:
                            manage_item_view = menus.ManageCustomItemView(player_object, item_id)
                            await ctx.send(embed=embed_msg, view=manage_item_view)
                        else:
                            await ctx.send(embed=embed_msg)
                    else:
                        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                                  title="An item with this ID does not exist.",
                                                  description=f"Inputted ID: {item_id}")
                        await ctx.send(embed=embed_msg)
                elif gear_id.isalnum():
                    checked_id = gear_id
                    player_stock = inventory.check_stock(player_object, checked_id)
                    item_object = inventory.get_basic_item_by_id(checked_id)
                    item_embed = item_object.create_bitem_embed()
                    item_embed.add_field(name="", value=f"{player_object.player_username}'s Stock: {player_stock}")
                else:
                    await ctx.send("Please enter a valid id.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('gear', 3)
    @pandora_bot.hybrid_command(name='tarot', help="View your tarot collection.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def tarot_collection(ctx, start_location: int = 0):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
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
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                if not player.checkNaN(item_id) and not player.checkNaN(cost):
                    num_listings = bazaar.check_num_listings(player_object)
                    if num_listings < 6:
                        if inventory.if_custom_exists(item_id):
                            selected_item = inventory.read_custom_item(item_id)
                            if selected_item.item_tier > 4:
                                response = player_object.check_equipped(selected_item)
                                if response == "":
                                    bazaar.list_custom_item(selected_item, cost)
                                    await ctx.send(f"Item {item_id} has been listed for {cost} lotus coins.")
                                else:
                                    await ctx.send(response)
                            else:
                                await ctx.send(f"Only tier 5 or higher gear items can be listed at the Bazaar.")
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
    @pandora_bot.hybrid_command(name='bazaar', help="View the Bazaar.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def view_bazaar(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                embed_msg = bazaar.show_bazaar_items()
                bazaar_view = None
                await ctx.send(embed=embed_msg, view=bazaar_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('trade', 3)
    @pandora_bot.hybrid_command(name='market', help="Visit the black market item shop.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def black_market(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
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

    @set_command_category('trade', 4)
    @pandora_bot.hybrid_command(name='give', help="Transfer ownership of a gear item.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def give(ctx, item_id: int, receiving_player_id: int):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                if inventory.if_custom_exists(item_id):
                    selected_item = inventory.read_custom_item(item_id)
                    embed_msg = selected_item.create_citem_embed()
                    if player.check_user_exists(receiving_player_id):
                        owner_check = selected_item.player_owner
                        if selected_item.player_owner == -1:
                            owner_check = bazaar.get_seller_by_item(item_id)
                        if player_object.player_id == owner_check:
                            selected_item.give_item(receiving_player_id)
                            embed_title = "Item Transfer Complete!"
                            embed_description = f"User: {receiving_player_id} has received item: {item_id}"
                        else:
                            embed_title = "Cannot Transfer Item."
                            embed_description = f"You do not own item {item_id}"
                    else:
                        embed_title = "A user with this ID does not exist."
                        embed_description = f"Inputted ID: {receiving_player_id}"
                else:
                    embed_title = "An item with this ID does not exist."
                    embed_description = f"Inputted ID: {item_id}"
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=embed_title,
                                          description=embed_description)
            else:
                embed_msg = unregistered_message()
            await ctx.send(embed=embed_msg)

    @set_command_category('trade', 5)
    @pandora_bot.hybrid_command(name='purge', help="Sells all gear in or below a tier.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def purge(ctx, tier: int):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            existing_user = player.get_player_by_name(ctx.author)
            if tier in range(1, 6):
                await ctx.defer()
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
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                player_object.get_equipped()
                embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                          title="Pandora's Celestial Forge",
                                          description="Let me know what you'd like me to upgrade today!")
                embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                forge_view = forge.SelectView(player_object)
                await ctx.send(embed=embed_msg, view=forge_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('craft', 1)
    @pandora_bot.hybrid_command(name='refinery', help="Go to the refinery.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def refinery(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
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

    @set_command_category('craft', 3)
    @pandora_bot.hybrid_command(name='infuse', help="Infuse items using alchemy.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def infusion(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
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

    @set_command_category('craft', 4)
    @pandora_bot.hybrid_command(name='fountain', help="Go to the ???")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def fountain(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                player_object.get_equipped()
                e_weapon = inventory.read_custom_item(player_object.equipped_weapon)
                if player_object.player_quest >= 27 and e_weapon.item_tier == 6:
                    entry_msg = ("You who has defiled my wish now seek to realize your own. You now have the key "
                                 "which grants you the right to enter this place. Just ahead resides the fountain of "
                                 "genesis, origin of all. The power you still covet can be acquired here. Go now, "
                                 "I am no longer qualified to stand in your path.")
                    embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                              title="Echo of Eleuia",
                                              description=entry_msg)
                    embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                    new_view = forge.GenesisView(player_object, e_weapon)

                else:
                    embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                              title="???",
                                              description="A powerful force emanates from within. Preventing entry.")
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
        embed = discord.Embed(title="Help Command Menu")
        embed_msg = menus.build_help_embed(category_dict, 'info')
        help_view = menus.HelpView(category_dict)
        await ctx.send(embed=embed_msg, view=help_view)

    @set_command_category('info', 1)
    @pandora_bot.hybrid_command(name='register', help="Register a new user.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def play(ctx, username: str):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            user = ctx.author
            if username.isalpha():
                if player.check_username(username):
                    register_msg = ('You find yourself seperated from your companions in the labyrinth. Unarmed, you '
                                    'are desperately searching every room and chest for something you can use.\n You'
                                    'stumble into an empty room in which sits a peculiar box. You hesitate at first '
                                    'and consider the possibility of a trap or mimic. However, hearing footsteps in '
                                    'the distance extinguishes any doubt. There is no time. You open the box.\n'
                                    'A flurry of souls rushes by, assuredly scaring away any nearby monsters. '
                                    'Everything goes silent and all that remains is an otherworldly girl staring at '
                                    'you in confusion. A soft voice coming not from the girl echoes through your mind, '
                                    '"Everything begins and ends with a wish. What do you wish to be?" '
                                    'You think it for only a second and the voice responds with a playful laugh, '
                                    ' "Let it be so." Then the voice disappears without a trace.')
                    embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                              title="Register - Select Class",
                                              description=register_msg)
                    player_name = str(user)
                    class_view = menus.ClassSelect(player_name, username)
                    await ctx.send(embed=embed_msg, view=class_view)
                else:
                    ctx.send("Username already in use.")
            else:
                await ctx.send("Please enter a valid username.")

    @set_command_category('info', 2)
    @pandora_bot.hybrid_command(name='stats', help="Display your stats page.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def stats(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = player_object.get_player_stats(1)
                stat_view = menus.StatView(player_object)
                await ctx.send(embed=embed_msg, view=stat_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @set_command_category('info', 3)
    @pandora_bot.hybrid_command(name='profile', help="View profile rank card.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def profile(ctx):
        user = ctx.author
        achievement_list = []
        roles_list = [r.name for r in user.roles]
        for role in roles_list:
            if "Achv" in role:
                achievement_list.append(role)
            elif "Notification" in role:
                achievement_list.append(role)
            elif "Holder" in role:
                achievement_list.append(role)
            elif "Echelon 5" in role:
                achievement_list.append(role)
        player_object = player.get_player_by_name(user)
        if player_object.player_class != "":
            filepath = pilengine.get_player_profile(player_object, achievement_list)
            file_object = discord.File(filepath)
            await ctx.send(file=file_object)
        else:
            embed_msg = unregistered_message()
            await ctx.send(embed=embed_msg)

    @set_command_category('info', 4)
    @pandora_bot.command(name='credits', help="Displays the game credits.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def credits_list(ctx):
        if any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
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