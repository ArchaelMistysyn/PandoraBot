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
import random

import player
import bosses
import globalitems
import menus
import enginecogs
import combat


# Get Bot Token
token_info = None
with open("engine_bot_token.txt", 'r') as token_file:
    for line in token_file:
        token_info = line
TOKEN = token_info


class EngineBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())


def run_discord_bot():
    engine_bot = EngineBot()

    @engine_bot.event
    async def on_ready():
        print(f'\n{engine_bot.user} Online!')
        engine_bot.help_command = None

    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

    # Admin Commands
    @engine_bot.command(name='sync', help="Archael Only")
    async def sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                synced = await engine_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Combat Engine Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @engine_bot.command(name='reset_sync', help="Archael Only")
    async def reset_sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                global_sync = await engine_bot.tree.sync(guild=None)
                print(f"Combat Engine Synced! {len(global_sync)} global command(s)")
                synced = await engine_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Combat Engine Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @engine_bot.command(name='init_bosses', help="Archael Only")
    async def initialize_bosses(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                timer = 60

                async def run_raid_task(pass_raid_channel_id, pass_x, pass_raid_channel):
                    await raid_task(pass_raid_channel_id, pass_x, pass_raid_channel)

                async def run_solo_boss_task(pass_player_object, pass_y, pass_command_channel_id, pass_cmd_channel):
                    await solo_boss_task(pass_player_object, pass_y, pass_command_channel_id, pass_cmd_channel)

                for server in globalitems.global_server_channels:
                    command_channel_id = server[0]
                    cmd_channel = engine_bot.get_channel(command_channel_id)
                    for x in range(1, 5):
                        raid_channel_id = server[x]
                        raid_channel = engine_bot.get_channel(raid_channel_id)
                        asyncio.create_task(run_raid_task(raid_channel_id, x, raid_channel))
                    restore_boss_list = bosses.restore_solo_bosses(command_channel_id)
                    for idy, y in enumerate(restore_boss_list):
                        player_object = player.get_player_by_id(y.player_id)
                        asyncio.create_task(run_solo_boss_task(player_object, y, command_channel_id, cmd_channel))
                print("Initialized Bosses")
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @engine_bot.event
    async def raid_task(channel_id, channel_num, channel_object):
        level, boss_type, boss_tier = bosses.get_boss_details(channel_num)
        active_boss = bosses.spawn_boss(channel_id, 0, boss_tier, boss_type, level, channel_num)
        embed_msg = active_boss.create_boss_embed(0)
        raid_button = menus.RaidView()
        sent_message = await channel_object.send(embed=embed_msg, view=raid_button)
        enginecogs.RaidCog(engine_bot, active_boss, channel_id, channel_num, sent_message, channel_object)

    @engine_bot.event
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

    @engine_bot.event
    async def solo_boss_task(player_object, active_boss, channel_id, channel_object):
        embed_msg = active_boss.create_boss_embed(0)
        sent_message = await channel_object.send(embed=embed_msg)
        player_object.get_player_multipliers()
        solo_cog = enginecogs.SoloCog(engine_bot, player_object, active_boss, channel_id, sent_message, channel_object)
        await solo_cog.run()

    @engine_bot.event
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

    @engine_bot.hybrid_command(name='solo', help="Challenge a solo boss. Stamina Cost: 200")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def solo(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
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

                            async def run_solo_cog():
                                return pandoracogs.SoloCog(pandora_bot, player_object, active_boss, channel_id,
                                                           sent_message, channel_object)

                            solo_cog = await run_solo_cog()
                            task = asyncio.create_task(solo_cog.run())
                            await task
                        else:
                            await ctx.send("Not enough stamina.")
                    else:
                        await ctx.send("You already have a solo boss encounter running.")

                else:
                    await ctx.send("You must have a weapon equipped.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    def unregistered_message():
        register_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                       title="Unregistered",
                                       description="Please register using !register to play.")
        return register_embed

    engine_bot.run(TOKEN)
