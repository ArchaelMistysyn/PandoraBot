# General import
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.ui import Button, View
from discord import app_commands
import asyncio
import pandas as pd
import sys
import random
from datetime import datetime as dt, timedelta

# Data imports
import globalitems
import sharedmethods

# Core imports
import inventory
import player
import quest
import bosses
import combat

# Cog imports
import enginecogs

# Item/crafting imports
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
        echelon_req = [self.channel_num * 2 + 1, self.channel_num * 2 + 2]
        if clicked_by.player_echelon not in echelon_req:
            outcome = f"{clicked_by.player_username} is not echelon {echelon_req} and cannot join this raid."
            await interaction.response.send_message(outcome)
            return
        outcome = bosses.add_participating_player(interaction.channel.id, clicked_by)
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

    async def run_solo_cog(player_obj, active_boss, channel_id, sent_message, ctx, gauntlet=False):
        return enginecogs.SoloCog(engine_bot, player_obj, active_boss, channel_id, sent_message, ctx, gauntlet=gauntlet)

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
            sharedmethods.reset_all_cooldowns()
            await ctx.send("All player cooldowns have been reset.")
        else:
            await ctx.send('You must be the owner to use this command!')

    @engine_bot.command(name='init_bosses', help="Archael Only")
    async def initialize_bosses(ctx):
        if ctx.message.author.id != 185530717638230016:
            await ctx.send('You must be the owner to use this command!')
            return
        timer = 60

        async def run_raid_task(pass_raid_channel_id, pass_x, pass_raid_channel):
            await raid_task(pass_raid_channel_id, pass_x, pass_raid_channel)

        async def run_solo_boss_task(pass_player_obj, pass_y, pass_command_channel_id, ctx_object):
            await solo_boss_task(pass_player_obj, pass_y, pass_command_channel_id, ctx_object)

        for server in globalitems.global_server_channels:
            command_channel_id = server[0]
            cmd_channel = engine_bot.get_channel(command_channel_id)
            for x in range(1, 5):
                raid_channel_id = server[x]
                raid_channel = engine_bot.get_channel(raid_channel_id)
                asyncio.create_task(run_raid_task(raid_channel_id, x, raid_channel))
            restore_boss_list = bosses.restore_solo_bosses(command_channel_id)
            for idy, y in enumerate(restore_boss_list):
                player_obj = player.get_player_by_id(y.player_id)
                asyncio.create_task(run_solo_boss_task(player_obj, y, command_channel_id, ctx))
        print("Initialized Bosses")

    @engine_bot.event
    async def raid_task(channel_id, channel_num, channel_object):
        level, boss_type, boss_tier = bosses.get_raid_boss_details(channel_num)
        active_boss = bosses.spawn_boss(channel_id, 0, boss_tier, boss_type, level, channel_num)
        embed_msg = active_boss.create_boss_embed()
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
                combat_tracker_list.append(combat.CombatTracker(temp_user[idy]))
        player_msg_list = []
        for idx, x in enumerate(temp_user):
            player_msg, player_damage = combat.run_raid_cycle(combat_tracker_list[idx], active_boss, x)
            new_player_damage = int(damage_list[idx]) + player_damage
            dps += int(combat_tracker_list[idx].total_dps / combat_tracker_list[idx].total_cycles)
            bosses.update_player_damage(channel_id, x.player_id, new_player_damage)
            player_msg_list.append(player_msg)
        bosses.update_boss_cHP(channel_id, 0, active_boss.boss_cHP)
        if active_boss.calculate_hp():
            embed_msg = active_boss.create_boss_embed(dps=dps)
            for m in player_msg_list:
                embed_msg.add_field(name="", value=m, inline=False)
            await sent_message.edit(embed=embed_msg)
            return True
        else:
            embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
            for m in player_msg_list:
                embed_msg.add_field(name="", value=m, inline=False)
            await sent_message.edit(embed=embed_msg)
            loot_embed = await loot.create_loot_embed(embed_msg, active_boss, player_list, loot_multiplier=5)
            await channel_object.send(embed=loot_embed)
            return False

    @engine_bot.event
    async def solo_boss_task(player_obj, active_boss, channel_id, ctx_object):
        embed_msg = active_boss.create_boss_embed()
        sent_message = await ctx_object.channel.send(embed=embed_msg)
        solo_cog = enginecogs.SoloCog(engine_bot, player_obj, active_boss, channel_id, sent_message, ctx_object)
        await solo_cog.run()

    @engine_bot.event
    async def solo_boss(combat_tracker, player_obj, active_boss, channel_id, sent_message, ctx_object, gauntlet=False):
        active_boss.reset_modifiers()
        active_boss.curse_debuffs = player_obj.elemental_curse
        active_boss.aura = player_obj.aura
        embed, player_alive = combat.run_solo_cycle(combat_tracker, active_boss, player_obj)
        bosses.update_boss_cHP(channel_id, active_boss.player_id, active_boss.boss_cHP)
        if not player_alive:
            await sent_message.edit(embed=embed)
            bosses.clear_boss_info(channel_id, player_obj.player_id)
            return False
        if active_boss.calculate_hp():
            await sent_message.edit(embed=embed)
            return True
        else:
            if gauntlet and active_boss.boss_tier != 6:
                bosses.clear_boss_info(channel_id, player_obj.player_id)
                boss_type = random.choice(["Paragon", "Arbiter"])
                if active_boss.boss_tier < 4:
                    boss_type = random.choice(["Fortress", "Dragon", "Demon", "Paragon"])
                active_boss = bosses.spawn_boss(channel_id, player_obj.player_id, active_boss.boss_tier + 1,
                                                boss_type, player_obj.player_lvl, 0, gauntlet=gauntlet)
                active_boss.player_id = player_obj.player_id
                embed = active_boss.create_boss_embed(dps=int(combat_tracker.total_dps / combat_tracker.total_cycles))
                await sent_message.edit(embed=embed)
                return True
            await sent_message.edit(embed=embed)
            player_list = [player_obj.player_id]
            loot_bonus = 5 if gauntlet else 1
            if "XXX" in active_boss.boss_name:
                loot_bonus = loot.incarnate_attempts_dict[active_boss.boss_level]
            loot_embed = await loot.create_loot_embed(embed, active_boss, player_list, ctx=ctx_object,
                                                      loot_multiplier=loot_bonus, gauntlet=gauntlet)
            bosses.clear_boss_info(channel_id, player_obj.player_id)
            await ctx_object.send(embed=loot_embed)
            return False

    @engine_bot.hybrid_command(name='abandon', help="Abandon an active solo encounter.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def abandon(ctx):
        player_obj = await sharedmethods.check_registration(ctx)
        if player_obj is None:
            return
        existing_id = bosses.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id is None:
            await ctx.send("You are not in any solo encounter.")
            return
        if combat.check_flag(player_obj):
            await ctx.send("You are already flagged to abandon the encounter.")
            return
        combat.toggle_flag(player_obj)
        await ctx.send("You have flagged to abandon the encounter.")

    @engine_bot.hybrid_command(name='fortress', help="Challenge a fortress boss. Cost: 1 Fortress Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def fortress(ctx):
        await solo(ctx, boss_type="Fortress")

    @engine_bot.hybrid_command(name='dragon', help="Challenge a dragon boss. Cost: 1 Dragon Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def dragon(ctx):
        await solo(ctx, boss_type="Dragon")

    @engine_bot.hybrid_command(name='demon', help="Challenge a demon boss. Cost: 1 Demon Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def demon(ctx):
        await solo(ctx, boss_type="Demon")

    @engine_bot.hybrid_command(name='paragon', help="Challenge a paragon boss. Cost: 1 Paragon Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def paragon(ctx):
        await solo(ctx, boss_type="Paragon")

    @engine_bot.hybrid_command(name='arbiter', help="Challenge a paragon boss. Cost: 1 Arbiter Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def arbiter(ctx):
        await solo(ctx, boss_type="Arbiter")

    @engine_bot.hybrid_command(name='solo',
                               help="Options: [Random/Fortress/Dragon/Demon/Paragon/Arbiter]. Stamina Cost: 200")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def solo(ctx, boss_type="random"):
        player_obj = await sharedmethods.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        existing_id = bosses.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss encounter running.")
            return
        if not player_obj.spend_stamina(200):
            await ctx.send("Not enough stamina.")
            return

        # Determine the restrictions
        spawn_dict = {0: 0, 1: 1, 3: 2, 5: 3, 9: 4}
        highest_key = max(key for key in spawn_dict if key <= player_obj.player_echelon)
        max_spawn = spawn_dict[highest_key]

        # Handle boss type selection
        boss_type = boss_type.capitalize()
        if boss_type == "Random":
            spawned_boss = random.randint(0, max_spawn)
            boss_type = globalitems.boss_list[spawned_boss]
        else:
            if boss_type not in globalitems.boss_list:
                await ctx.send("Boss type not recognized. Please select [Random/Fortress/Dragon/Demon/Paragon/Arbiter].")
                return
            spawned_boss = globalitems.boss_list.index(boss_type)
            if spawned_boss > max_spawn:
                await ctx.send("Your echelon is not high enough to challenge this boss type.")
                return
            stone_id = f"Stone{spawned_boss}" if spawned_boss <= 4 else 6
            stone_obj = inventory.BasicItem(stone_id)
            stone_stock = inventory.check_stock(player_obj, stone_obj.item_id)
            if stone_stock < 1:
                await ctx.send(sharedmethods.get_stock_msg(stone_obj, stone_stock))
                return
            inventory.update_stock(player_obj, stone_obj.item_id, -1)

        # Spawn the boss
        new_boss_tier, boss_type = bosses.get_random_bosstier(boss_type)
        active_boss = bosses.spawn_boss(ctx.channel.id, player_obj.player_id, new_boss_tier,
                                        boss_type, player_obj.player_lvl, 0)
        active_boss.player_id = player_obj.player_id
        embed_msg = active_boss.create_boss_embed()
        spawn_msg = f"{player_obj.player_username} has spawned a tier {active_boss.boss_tier} boss!"
        await ctx.send(spawn_msg)
        sent_message = await ctx.channel.send(embed=embed_msg)
        solo_cog = await run_solo_cog(player_obj, active_boss, ctx.channel.id, sent_message, ctx)
        task = asyncio.create_task(solo_cog.run())
        await task

    @engine_bot.hybrid_command(name='palace', help="Enter the Divine Palace.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def palace(ctx):
        player_obj = await sharedmethods.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        existing_id = bosses.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss encounter running.")
            return
        if not player_obj.player_quest < 50:
            await ctx.send("The divine palace is not a place mortals may tread.")
            return
        spawn_msg = f"{player_obj.player_username} has spawned a tier {active_boss.boss_tier} boss!"
        await ctx.send(spawn_msg)
        lotus_object = inventory.BasicItem("Lotus10")
        lotus_stock = inventory.check_stock(player_obj, lotus_object.item_id)
        embed_msg = discord.Embed(colour=discord.Colour.gold(), title="Divine Palace of God", description="")
        embed_msg.description = ("The inside of the palace is still, the torches unlit as if it hasn't been used"
                                 "in thousands of years.")
        if lotus_stock >= 1:
            embed_msg.description = ("As you set foot in the palace, the rows of torches lining the ivory halls "
                                     "shine, alight with divine fire. As you approach the throne of god "
                                     "you see Yubelle's echo appears before you. She draws the Divine Lotus "
                                     "inside herself manifesting into a new physical form. "
                                     "She challenges you to decide your fate in combat before the eyes of god."
                                     "\n**FINAL WARNING: a Divine Lotus will be consumed if you start the encounter.**")
        sent_message = await ctx.channel.send(embed=embed_msg)
        palace_view = PalaceView(player_obj, lotus_object, lotus_stock, sent_message, ctx)
        sent_message = await sent_message.edit(embed=embed_msg, view=palace_view)

    class PalaceView(discord.ui.View):
        def __init__(self, player_obj, lotus_object, lotus_stock, sent_message, ctx):
            super().__init__(timeout=None)
            self.player_obj = player_obj
            self.lotus_object = lotus_object
            self.ctx, self.sent_message = ctx, sent_message
            self.embed_msg = False
            self.lotus_stock = lotus_stock
            if self.lotus_stock < 0:
                self.children.disabled = True
                self.children.style = globalitems.button_colour_list[3]
            elif self.player_obj.player_quest == 50:
                self.usurper_difficulty.disabled = True
                self.samsara_difficulty.disabled = True
                self.usurper_difficulty.style = globalitems.button_colour_list[3]
                self.samsara_difficulty.style = globalitems.button_colour_list[3]
            elif self.player_obj.ascendency == "Demi-God":
                self.samsara_difficulty.disabled = True
                self.samsara_difficulty.style = globalitems.button_colour_list[3]

        @discord.ui.button(label="Challenger", style=discord.ButtonStyle.blurple)
        async def challenger_difficulty(self, interaction: discord.Interaction, button: discord.Button):
            if interaction.user.id != self.player_obj.discord_id:
                return
            await self.begin_encounter(1)

        @discord.ui.button(label="Usurper", style=discord.ButtonStyle.blurple)
        async def usurper_difficulty(self, interaction: discord.Interaction, button: discord.Button):
            if interaction.user.id != self.player_obj.discord_id:
                return
            await self.begin_encounter(2)

        @discord.ui.button(label="Samsara", style=discord.ButtonStyle.blurple)
        async def samsara_difficulty(self, interaction: discord.Interaction, button: discord.Button):
            if interaction.user.id != self.player_obj.discord_id:
                return
            await self.begin_encounter(3)

        async def begin_encounter(self, difficulty):
            lotus_stock = inventory.check_stock(self.player_obj, self.lotus_object.item_id)
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title="Divine Palace of God", description="")
            if lotus_stock < 1:
                embed_msg.description = "The echo falls silent and fades away alongside the light of the torches."
                await interaction.response.edit_message(embed=embed_msg, view=None)
                return
            boss_level = 600 + 100 * difficulty
            inventory.update_stock(self.player_obj, self.lotus_object.item_id, -1)
            active_boss = bosses.spawn_boss(self.ctx.channel.id, self.player_obj.player_id,
                                            8, 5, boss_level, 0)
            embed_msg = active_boss.create_boss_embed()
            await interaction.response.edit_message(embed=embed_msg, view=None)
            solo_cog = await run_solo_cog(self.player_obj, active_boss,
                                          self.ctx.channel.id, self.sent_message, self.ctx)
            task = asyncio.create_task(solo_cog.run())
            await task

    @engine_bot.hybrid_command(name='gauntlet', help="Challenge the gauntlet in the Spire of Illusions.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def run_gauntlet(ctx):
        player_obj = await sharedmethods.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        if player_obj.player_quest < 36:
            await ctx.send("You must complete quest 36 to challenge the Spire of Illusions.")
            return
        existing_id = bosses.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss encounter running.")
            return
        token_item = inventory.BasicItem("Compass")
        player_stock = inventory.check_stock(player_obj, "Compass")
        if player_stock <= 0:
            await ctx.send(f"Out of Stock: {token_item.item_emoji} {token_item.item_name}.")
            return
        inventory.update_stock(player_obj, "Compass", -1)
        quest.assign_unique_tokens(player_obj, "Gauntlet")
        active_boss = bosses.spawn_boss(ctx.channel.id, player_obj.player_id, 1,
                                        boss_type, player_obj.player_lvl, 0, gauntlet=True)
        active_boss.player_id = player_obj.player_id
        await ctx.send(f"{player_obj.player_username} has entered the Spire of Illusions!")
        embed_msg = active_boss.create_boss_embed()
        sent_message = await ctx.channel.send(embed=embed_msg)
        gauntlet_cog = await run_solo_cog(player_obj, active_boss, ctx.channel.id, sent_message, ctx, gauntlet=True)
        task = asyncio.create_task(gauntlet_cog.run())
        await task

    @engine_bot.hybrid_command(name='summon', help="Challenge a paragon boss.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def summon(ctx, token_version: int):
        player_obj = await sharedmethods.check_registration(ctx)
        if player_obj is None:
            return
        if token_version not in range(1, 4):
            await ctx.send("Selected token not between 1 and 3.")
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        if (player_obj.player_echelon < 9 or player_obj.player_quest < 48) and token_version == 3:
            await ctx.send("You must be player echelon 9 and complete quest 47 to challenge the high arbiter.")
            return
        if player_obj.player_echelon < 8 and token_version == 2:
            await ctx.send("You must be player echelon 8 to challenge the paragon sovereign.")
            return
        elif player_obj.player_echelon < 7 and token_version == 1:
            await ctx.send("You must be player echelon 7 to challenge a superior paragon.")
            return
        existing_id = bosses.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss encounter running.")
            return
        token_id = f"Summon{token_version}"
        token_item = inventory.BasicItem(token_id)
        player_stock = inventory.check_stock(player_obj, token_id)
        if player_stock <= 0:
            await ctx.send(sharedmethods.get_stock_msg(token_item, player_stock))
            return
        inventory.update_stock(player_obj, token_id, -1)
        # Set the boss tier and type
        boss_type = "Paragon" if token_version < 3 else "Arbiter"
        new_boss_tier = boss_tier_dict[4 + token_version]
        active_boss = bosses.spawn_boss(ctx.channel.id, player_obj.player_id, new_boss_tier,
                                        boss_type, player_obj.player_lvl, 0)
        active_boss.player_id = player_obj.player_id
        spawn_msg = f"{player_obj.player_username} has summoned a tier {active_boss.boss_tier} boss!"
        await ctx.send(spawn_msg)
        embed_msg = active_boss.create_boss_embed()
        sent_message = await ctx.channel.send(embed=embed_msg)
        solo_cog = await run_solo_cog(player_obj, active_boss, ctx.channel.id, sent_message, ctx)
        task = asyncio.create_task(solo_cog.run())
        await task

    @engine_bot.hybrid_command(name='arena', help="Enter pvp combat with another player.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def arena(ctx):
        player_obj = await sharedmethods.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_echelon < 1:
            await ctx.send("You must be Echelon 1 or higher to participate in the arena.")
            return
        opponent_player = combat.get_random_opponent(player_obj.player_echelon)
        if opponent_player is None:
            await ctx.send("No available opponent found.")
            return
        echelon_colour, _ = sharedmethods.get_gear_tier_colours(player_obj.player_echelon)
        if opponent_player.player_equipped[0] == 0:
            await ctx.send("No available opponent found.")
            return
        difference, method = player_obj.check_cooldown("arena")
        if difference:
            one_day = timedelta(days=1)
            cooldown = one_day - difference
            if difference <= one_day:
                cooldown_timer = int(cooldown.total_seconds() / 60 / 60)
                time_msg = f"Your next arena match is in {cooldown_timer} hours."
                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title="Arena Closed!", description=time_msg)
                await ctx.send(embed=embed_msg)
                return
        player_obj.set_cooldown("arena", "")
        if player_obj.player_username == opponent_player.player_username:
            opponent_player.player_username = f"Shadow {opponent_player.player_username}"
        pvp_msg = f"{player_obj.player_username} vs {opponent_player.player_username}!"
        pvp_embed = discord.Embed(title="Arena PvP", description="", color=echelon_colour)
        # pvp_embed.set_thumbnail(url="")
        pvp_embed.add_field(name="Challenger", value=player_obj.player_username, inline=True)
        pvp_embed.add_field(name="Opponent", value=opponent_player.player_username, inline=True)
        # combat.run_initial_pvp_message(player_obj, opponent_player)
        await ctx.send(pvp_msg)
        channel_object = ctx.channel
        sent_message = await channel_object.send(embed=pvp_embed)

        async def run_pvp_cog():
            return enginecogs.PvPCog(engine_bot, player_obj, opponent_player, ctx.channel.id,
                                     sent_message, channel_object)

        pvp_cog = await run_pvp_cog()
        task = asyncio.create_task(pvp_cog.run())
        await task

    engine_bot.run(TOKEN)
