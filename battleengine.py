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
from datetime import datetime as dt, timedelta

import inventory
import player
import bosses
import globalitems
import menus
import enginecogs
import combat
import loot


# Get Bot Token
token_info = None
with open("engine_bot_token.txt", 'r') as token_file:
    for line in token_file:
        token_info = line
TOKEN = token_info


# Raid View
class RaidView(discord.ui.View):
    def __init__(self, channel_num):
        super().__init__(timeout=None)
        self.channel_num = channel_num

    @discord.ui.button(label="Join the raid!", style=discord.ButtonStyle.success, emoji="⚔️")
    async def raid_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        clicked_by = player.get_player_by_discord(interaction.user.id)
        outcome = clicked_by.player_username
        echelon_req = globalitems.channel_echelon_dict[self.channel_num]
        if clicked_by.player_echelon == echelon_req:
            outcome += bosses.add_participating_player(interaction.channel.id, clicked_by.player_id)
        elif clicked_by.player_echelon == 4 and echelon_req == 3:
            outcome += bosses.add_participating_player(interaction.channel.id, clicked_by.player_id)
        else:
            outcome += f" is not echelon {echelon_req} and cannot join this raid."
        await interaction.response.send_message(outcome)


class EngineBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())


def run_discord_bot():
    engine_bot = EngineBot()

    @engine_bot.event
    async def on_ready():
        print(f'{engine_bot.user} Online!')
        engine_bot.help_command = None

    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

    async def on_shutdown():
        print("Battle Engine Off")
        try:
            await engine_bot.close()
            await engine_bot.session.close()
        except KeyboardInterrupt:
            sys.exit(0)

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

    @engine_bot.command(name='resetCD', help="Archael Only")
    async def resetCD(ctx):
        if ctx.message.author.id == 185530717638230016:
            player.reset_all_cooldowns()
            await ctx.send("All player cooldowns have been reset.")
        else:
            await ctx.send('You must be the owner to use this command!')

    @engine_bot.command(name='init_bosses', help="Archael Only")
    async def initialize_bosses(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                timer = 60

                async def run_raid_task(pass_raid_channel_id, pass_x, pass_raid_channel):
                    await raid_task(pass_raid_channel_id, pass_x, pass_raid_channel)

                async def run_solo_boss_task(pass_player_object, pass_y, pass_command_channel_id, ctx_object):
                    await solo_boss_task(pass_player_object, pass_y, pass_command_channel_id, ctx_object)

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
                        asyncio.create_task(run_solo_boss_task(player_object, y, command_channel_id, ctx))
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
        raid_button = RaidView(channel_num)
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
    async def solo_boss_task(player_object, active_boss, channel_id, ctx_object):
        embed_msg = active_boss.create_boss_embed(0)
        sent_message = await ctx_object.channel.send(embed=embed_msg)
        player_object.get_player_multipliers()
        solo_cog = enginecogs.SoloCog(engine_bot, player_object, active_boss, channel_id, sent_message, ctx_object)
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

    @engine_bot.hybrid_command(name='abandon', help="Abandon an active solo encounter.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def abandon(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            player_object = player.get_player_by_discord(ctx.author.id)
            await ctx.defer()
            if player_object.player_class != "":
                existing_id = bosses.get_raid_id(channel_id, player_object.player_id)
                if existing_id != 0:
                    if not combat.check_flag(player_object):
                        combat.toggle_flag(player_object)
                        await ctx.send("You have flagged to abandon the encounter.")
                    else:
                        await ctx.send("You are already flagged to abandon the encounter.")
                else:
                    await ctx.send("You are not in any solo encounter.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @engine_bot.hybrid_command(name='solo', help="Challenge a solo boss. Stamina Cost: 200")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def solo(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_discord(ctx.author.id)

            # Confirm if the command can be run.
            if player_object.player_class == "":
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)
                return
            if player_object.player_equipped[0] == 0:
                await ctx.send("You must have a weapon equipped.")
                return
            existing_id = bosses.get_raid_id(channel_id, player_object.player_id)
            if existing_id != 0:
                await ctx.send("You already have a solo boss encounter running.")
                return
            if not player_object.spend_stamina(200):
                await ctx.send("Not enough stamina.")
                return

            # Spawn the boss.
            max_spawn = min(player_object.player_echelon, 2)
            spawned_boss = random.randint(0, max_spawn)
            boss_type = bosses.boss_list[spawned_boss]
            new_boss_tier, boss_type = bosses.get_random_bosstier(boss_type)
            player_object.get_player_multipliers()
            active_boss = bosses.spawn_boss(channel_id, player_object.player_id, new_boss_tier,
                                            boss_type, player_object.player_lvl, 0)
            active_boss.player_id = player_object.player_id
            embed_msg = active_boss.create_boss_embed(0)
            spawn_msg = f"{player_object.player_username} has spawned a tier {active_boss.boss_tier} boss!"
            await ctx.send(spawn_msg)
            sent_message = await ctx.channel.send(embed=embed_msg)

            # Run the boss cog.
            async def run_solo_cog():
                return enginecogs.SoloCog(engine_bot, player_object, active_boss, channel_id,
                                          sent_message, ctx)

            solo_cog = await run_solo_cog()
            task = asyncio.create_task(solo_cog.run())
            await task

    @engine_bot.hybrid_command(name='summon', help="Challenge a paragon boss.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def solo(ctx, token_version: int):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_discord(ctx.author.id)

            # Confirm if the command can be run.
            if token_version not in range(1, 6):
                await ctx.send("Selected token not between 1 and 5.")
                return
            if player_object.player_class == "":
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)
                return
            if player_object.player_equipped[0] == 0:
                await ctx.send("You must have a weapon equipped.")
                return
            if (player_object.player_echelon < 5 or player_object.player_quest < 29) and token_version == 5:
                await ctx.send("You must be player echelon 5 and complete quest 28 to challenge the high arbiter.")
                return
            if (player_object.player_echelon < 5 or player_object.player_quest < 28) and token_version == 4:
                await ctx.send("You must be player echelon 5 and complete quest 27 to challenge an arbiter.")
                return
            if player_object.player_echelon < 5 and token_version == 3:
                await ctx.send("You must be player echelon 5 to challenge the paragon sovereign.")
                return
            elif player_object.player_echelon < 4 and token_version == 2:
                await ctx.send("You must be player echelon 4 to challenge a superior paragon.")
                return
            elif player_object.player_echelon < 3:
                await ctx.send("You must be player echelon 3 to challenge a paragon.")
                return
            existing_id = bosses.get_raid_id(channel_id, player_object.player_id)
            if existing_id != 0:
                await ctx.send("You already have a solo boss encounter running.")
                return
            token_id = f"Summon{token_version}"
            token_item = inventory.BasicItem(token_id)
            player_stock = inventory.check_stock(player_object, token_id)
            if player_stock <= 0:
                await ctx.send(f"Out of Stock: {token_item.item_emoji} {token_item.item_name}.")
                return
            inventory.update_stock(player_object, token_id, -1)
            spawned_boss = 3 if token_version < 4 else 4
            boss_type = bosses.boss_list[spawned_boss]
            if token_version in [1, 4]:
                new_boss_tier, boss_type = bosses.get_random_bosstier(boss_type)
            elif token_version == 5:
                new_boss_tier = 7
            else:
                new_boss_tier = token_version + 3
            active_boss = bosses.spawn_boss(channel_id, player_object.player_id, new_boss_tier,
                                            boss_type, player_object.player_lvl, 0)
            active_boss.player_id = player_object.player_id
            embed_msg = active_boss.create_boss_embed(0)
            spawn_msg = f"{player_object.player_username} has spawned a tier {active_boss.boss_tier} boss!"
            await ctx.send(spawn_msg)
            player_object.get_player_multipliers()
            sent_message = await ctx.channel.send(embed=embed_msg)

            async def run_solo_cog():
                return enginecogs.SoloCog(engine_bot, player_object, active_boss, channel_id,
                                          sent_message, ctx)

            solo_cog = await run_solo_cog()
            task = asyncio.create_task(solo_cog.run())
            await task

    @engine_bot.hybrid_command(name='arena', help="Enter pvp combat with another player.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def arena(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in globalitems.global_server_channels):
            await ctx.defer()
            player_object = player.get_player_by_discord(ctx.author.id)
            if player_object.player_class != "":
                if player_object.player_echelon >= 1:
                    opponent_player = combat.get_random_opponent(player_object.player_echelon)
                    echelon_colour, colour_img = inventory.get_gear_tier_colours(player_object.player_echelon)
                    if opponent_player.player_equipped[0] != 0:
                        run_command = False
                        difference, method = player_object.check_cooldown("arena")
                        if difference:
                            one_day = timedelta(days=1)
                            cooldown = one_day - difference
                            if difference <= one_day:
                                cooldown_timer = int(cooldown.total_seconds() / 60 / 60)
                                time_msg = f"Your next arena match is in {cooldown_timer} hours."
                                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                                          title="Arena Closed!",
                                                          description=time_msg)
                                await ctx.send(embed=embed_msg)
                            else:
                                run_command = True
                        else:
                            run_command = True
                        if run_command:
                            player_object.set_cooldown("arena", "")
                            if player_object.player_username == opponent_player.player_username:
                                opponent_player.player_username = f"Shadow {opponent_player.player_username}"
                            pvp_msg = f"{player_object.player_username} vs {opponent_player.player_username}!"
                            pvp_embed = discord.Embed(
                                title="Arena PvP",
                                description="",
                                color=echelon_colour
                            )
                            # pvp_embed.set_thumbnail(url="")
                            pvp_embed.add_field(name="Challenger", value=player_object.player_username, inline=True)
                            pvp_embed.add_field(name="Opponent", value=opponent_player.player_username, inline=True)
                            # combat.run_initial_pvp_message(player_object, opponent_player)
                            player_object.get_player_multipliers()
                            opponent_player.get_player_multipliers()
                            await ctx.send(pvp_msg)
                            channel_object = ctx.channel
                            sent_message = await channel_object.send(embed=pvp_embed)

                            async def run_pvp_cog():
                                return enginecogs.PvPCog(engine_bot, player_object, opponent_player, channel_id,
                                                         sent_message, channel_object)

                            pvp_cog = await run_pvp_cog()
                            task = asyncio.create_task(pvp_cog.run())
                            await task
                    else:
                        await ctx.send("No opponent found.")
                else:
                    await ctx.send("You must be Echelon 1 or higher to participate in the arena.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    def unregistered_message():
        register_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                       title="Unregistered",
                                       description="Please register using !register to play.")
        return register_embed

    engine_bot.run(TOKEN)
