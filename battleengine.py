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
import globalitems as gli
import sharedmethods as sm
import adventuredata
import leaderboards

# Core imports
import inventory
import player
import quest
import bosses
import combat
import encounters

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
        clicked_by = await player.get_player_by_discord(interaction.user.id)
        outcome = clicked_by.player_username
        echelon_req = [self.channel_num * 2 + 1, self.channel_num * 2 + 2]
        if clicked_by.player_echelon not in echelon_req:
            outcome = f"{clicked_by.player_username} is not echelon {echelon_req} and cannot join this raid."
            await interaction.response.send_message(outcome)
            return
        outcome = await encounters.add_participating_player(interaction.channel.id, clicked_by)
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
        except KeyboardInterrupt:
            sys.exit(0)

    async def run_solo_cog(player_obj, active_boss, channel_id, sent_message, ctx, gauntlet=False, mode=0):
        return enginecogs.SoloCog(engine_bot, player_obj, active_boss, channel_id, sent_message, ctx,
                                  gauntlet=gauntlet, mode=mode)

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
            sm.reset_all_cooldowns()
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

        for server in gli.global_server_channels:
            command_channel_id = server[0]
            cmd_channel = engine_bot.get_channel(command_channel_id)
            for x in range(1, 5):
                raid_channel_id = server[x]
                raid_channel = engine_bot.get_channel(raid_channel_id)
                asyncio.create_task(run_raid_task(raid_channel_id, x, raid_channel))
        print("Initialized Bosses")

    @engine_bot.event
    async def raid_task(channel_id, channel_num, channel_object):
        level, boss_type, boss_tier = encounters.get_raid_boss_details(channel_num)
        active_boss = await bosses.spawn_boss(channel_id, 0, boss_tier, boss_type, level, channel_num)
        embed_msg = active_boss.create_boss_embed()
        raid_button = RaidView(channel_num)
        sent_message = await channel_object.send(embed=embed_msg, view=raid_button)
        enginecogs.RaidCog(engine_bot, active_boss, channel_id, channel_num, sent_message, channel_object)

    @engine_bot.event
    async def raid_boss(combat_tracker_list, active_boss, channel_id, channel_num, sent_message, channel_object):
        player_list, damage_list = await bosses.get_damage_list(channel_id)
        active_boss.reset_modifiers()
        temp_user = []
        dps = 0
        for idy, y in enumerate(player_list):
            temp_user.append(await player.get_player_by_id(int(y)))
            await temp_user[idy].get_player_multipliers()
            curse_lists = [active_boss.curse_debuffs, temp_user[idy].elemental_curse]
            active_boss.curse_debuffs = [sum(z) for z in zip(*curse_lists)]
            if idy >= len(combat_tracker_list):
                combat_tracker_list.append(combat.CombatTracker(temp_user[idy]))
        player_msg_list = []
        for idx, x in enumerate(temp_user):
            player_msg, player_damage = await combat.run_raid_cycle(combat_tracker_list[idx], active_boss, x)
            new_player_damage = int(damage_list[idx]) + player_damage
            dps += int(combat_tracker_list[idx].total_dps / combat_tracker_list[idx].total_cycles)
            await bosses.update_player_damage(channel_id, x.player_id, new_player_damage)
            player_msg_list.append(player_msg)
        await bosses.update_boss_cHP(channel_id, 0, active_boss.boss_cHP)
        if active_boss.calculate_hp():
            embed_msg = active_boss.create_boss_embed(dps=dps)
            for m in player_msg_list:
                embed_msg.add_field(name="", value=m, inline=False)
            await sent_message.edit(embed=embed_msg)
            return True
        else:
            embed_msg = await bosses.create_dead_boss_embed(channel_id, active_boss, dps)
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
    async def solo_boss(combat_tracker, player_obj, active_boss, channel_id, sent_message, ctx_object,
                        gauntlet=False, mode=0):
        active_boss.reset_modifiers()
        active_boss.curse_debuffs = player_obj.elemental_curse
        embed, player_alive, boss_alive = await combat.run_solo_cycle(combat_tracker, active_boss, player_obj)
        await bosses.update_boss_cHP(channel_id, active_boss.player_id, active_boss.boss_cHP)
        if not player_alive:
            await sent_message.edit(embed=embed)
            await bosses.clear_boss_info(channel_id, player_obj.player_id)
            return False, active_boss
        if boss_alive:
            await sent_message.edit(embed=embed)
            return True, active_boss
        if active_boss.boss_tier >= 4:
            quest.assign_unique_tokens(player_obj, active_boss.boss_name, mode=mode)
        extension = " [Gauntlet]" if gauntlet else ""
        if gauntlet and active_boss.boss_tier != 6:
            await bosses.clear_boss_info(channel_id, player_obj.player_id)
            boss_type = random.choice(["Paragon", "Arbiter"])
            if active_boss.boss_tier < 4:
                boss_type = random.choice(["Fortress", "Dragon", "Demon", "Paragon"])
            active_boss = await bosses.spawn_boss(channel_id, player_obj.player_id, active_boss.boss_tier + 1,
                                                  boss_type, player_obj.player_level, 0, gauntlet=gauntlet)
            active_boss.player_id = player_obj.player_id
            current_dps = int(combat_tracker.total_dps / combat_tracker.total_cycles)
            embed = active_boss.create_boss_embed(dps=current_dps, extension=extension)
            await sent_message.edit(embed=embed)
            return True, active_boss
        # Handle dead boss
        player_list = [player_obj.player_id]
        loot_bonus = 5 if gauntlet else 1
        if "XXX" in active_boss.boss_name:
            loot_bonus = loot.incarnate_attempts_dict[active_boss.boss_level]
            await leaderboards.update_leaderboard(combat_tracker, player_obj, ctx_object)
        loot_embed = await loot.create_loot_embed(embed, active_boss, player_list, ctx=ctx_object,
                                                  loot_multiplier=loot_bonus, gauntlet=gauntlet)
        await bosses.clear_boss_info(channel_id, player_obj.player_id)
        if combat_tracker.total_cycles <= 5:
            await sent_message.edit(embed=loot_embed)
            return False, active_boss
        await sent_message.edit(embed=embed)
        await ctx_object.send(embed=loot_embed)
        return False, active_boss

    @engine_bot.hybrid_command(name='abandon', help="Abandon an active solo encounter.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def abandon(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        existing_id = await encounters.get_raid_id(ctx.channel.id, player_obj.player_id)
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
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        existing_id = await encounters.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss or map encounter running.")
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
            boss_type = gli.boss_list[spawned_boss]
        else:
            if boss_type not in gli.boss_list:
                await ctx.send("Boss type not recognized. Please select [Random/Fortress/Dragon/Demon/Paragon/Arbiter].")
                return
            spawned_boss = gli.boss_list.index(boss_type)
            if spawned_boss > max_spawn:
                await ctx.send("Your echelon is not high enough to challenge this boss type.")
                return
            stone_id = f"Stone{spawned_boss + 1}" if spawned_boss <= 3 else "Stone6"
            stone_obj = inventory.BasicItem(stone_id)
            stone_stock = await inventory.check_stock(player_obj, stone_obj.item_id)
            if stone_stock < 1:
                await ctx.send(sm.get_stock_msg(stone_obj, stone_stock))
                return
            await inventory.update_stock(player_obj, stone_obj.item_id, -1)

        # Spawn the boss
        new_boss_tier, boss_type = bosses.get_random_bosstier(boss_type)
        active_boss = await bosses.spawn_boss(ctx.channel.id, player_obj.player_id, new_boss_tier,
                                        boss_type, player_obj.player_level, 0)
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
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        existing_id = await encounters.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        if player_obj.player_quest < 50:
            await ctx.send("The divine palace is not a place mortals may tread.")
            return
        await ctx.send(f"{player_obj.player_username} enters the divine palace.")
        lotus_object = inventory.BasicItem("Lotus10")
        lotus_stock = await inventory.check_stock(player_obj, lotus_object.item_id)
        embed_msg = discord.Embed(colour=discord.Colour.gold(), title="Divine Palace of God", description="")
        embed_msg.description = "The palace interior remains still, the torches unlit and the halls silent."
        if lotus_stock >= 1:
            embed_msg.description = (f"As you set foot in the palace rows of torches lining the ivory halls "
                                     f"ignite with divine fire. Approaching the throne of god "
                                     f"Yubelle's echo manifests by drawing on the energy of the Divine Lotus. "
                                     f"Shifting into a new being, 'it' challenges you before the eyes of god."
                                     f"\n**EXTREME DIFFICUILTY WARNING: {lotus_object.item_emoji} 1x Divine Lotus "
                                     f"will be consumed.**")
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
            if self.lotus_stock <= 0:
                for button in self.children:
                    button.disabled, button.style = True, gli.button_colour_list[3]
            elif self.player_obj.player_quest == 50:
                self.usurper.disabled, self.usurper.style = True, gli.button_colour_list[3]
                self.samsara.disabled, self.samsara.style = True, gli.button_colour_list[3]
            elif self.player_obj.player_level < 200:
                self.samsara.disabled, self.samsara.style = True, gli.button_colour_list[3]

        @discord.ui.button(label="Challenger", style=discord.ButtonStyle.success)
        async def challenger(self, interaction: discord.Interaction, button: discord.Button):
            if interaction.user.id != self.player_obj.discord_id:
                return
            await self.begin_encounter(interaction, 1)

        @discord.ui.button(label="Usurper", style=discord.ButtonStyle.blurple)
        async def usurper(self, interaction: discord.Interaction, button: discord.Button):
            if interaction.user.id != self.player_obj.discord_id:
                return
            await self.begin_encounter(interaction, 2)

        @discord.ui.button(label="Samsara", style=discord.ButtonStyle.red)
        async def samsara(self, interaction: discord.Interaction, button: discord.Button):
            if interaction.user.id != self.player_obj.discord_id:
                return
            await self.begin_encounter(interaction, 3)

        async def begin_encounter(self, interaction_obj, difficulty):
            lotus_stock = await inventory.check_stock(self.player_obj, self.lotus_object.item_id)
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title="Divine Palace of God", description="")
            if lotus_stock < 1:
                embed_msg.description = "The echo falls silent and fades away alongside the light of the torches."
                await interaction.response.edit_message(embed=embed_msg, view=None)
                return
            boss_level = 300 if difficulty == 1 else 600 if difficulty == 2 else 999
            await inventory.update_stock(self.player_obj, self.lotus_object.item_id, -1)
            boss_obj = await bosses.spawn_boss(self.ctx.channel.id, self.player_obj.player_id, 8,
                                               "Incarnate", boss_level, 0)
            label_list = {1: " [Challenger]", 2: " [Usurper]", 3: " [Samsara]"}
            embed_msg = boss_obj.create_boss_embed(extension=label_list[difficulty])
            await interaction_obj.response.edit_message(embed=embed_msg, view=None)
            solo_cog = await run_solo_cog(self.player_obj, boss_obj, self.ctx.channel.id, self.sent_message, self.ctx,
                                          mode=difficulty)
            task = asyncio.create_task(solo_cog.run())
            await task

    @engine_bot.hybrid_command(name='gauntlet', help="Challenge the gauntlet in the Spire of Illusions.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def run_gauntlet(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        if player_obj.player_quest < 36:
            await ctx.send("You must complete quest 36 to challenge the Spire of Illusions.")
            return
        existing_id = await encounters.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        token_item = inventory.BasicItem("Compass")
        player_stock = await inventory.check_stock(player_obj, "Compass")
        if player_stock <= 0:
            await ctx.send(f"Out of Stock: {token_item.item_emoji} {token_item.item_name}.")
            return
        await inventory.update_stock(player_obj, "Compass", -1)
        quest.assign_unique_tokens(player_obj, "Gauntlet")
        active_boss = await bosses.spawn_boss(ctx.channel.id, player_obj.player_id, 1,
                                              "Fortress", player_obj.player_level, 0, gauntlet=True)
        active_boss.player_id = player_obj.player_id
        await ctx.send(f"{player_obj.player_username} has entered the Spire of Illusions!")
        embed_msg = active_boss.create_boss_embed(extension=" [Gauntlet]")
        sent_message = await ctx.channel.send(embed=embed_msg)
        gauntlet_cog = await run_solo_cog(player_obj, active_boss, ctx.channel.id, sent_message, ctx, gauntlet=True)
        task = asyncio.create_task(gauntlet_cog.run())
        await task

    @engine_bot.hybrid_command(name='summon', help="Challenge a paragon boss.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def summon(ctx, token_version: int):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
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
        existing_id = await encounters.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        token_id = f"Summon{token_version}"
        token_item = inventory.BasicItem(token_id)
        player_stock = await inventory.check_stock(player_obj, token_id)
        if player_stock <= 0:
            await ctx.send(sm.get_stock_msg(token_item, player_stock))
            return
        await inventory.update_stock(player_obj, token_id, -1)
        # Set the boss tier and type
        boss_type = "Paragon" if token_version < 3 else "Arbiter"
        new_boss_tier = 4 + token_version
        active_boss = await bosses.spawn_boss(ctx.channel.id, player_obj.player_id, new_boss_tier,
                                              boss_type, player_obj.player_level, 0)
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
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_echelon < 1:
            await ctx.send("You must be Echelon 1 or higher to participate in the arena.")
            return
        opponent_player = await combat.get_random_opponent(player_obj.player_echelon)
        if opponent_player is None:
            await ctx.send("No available opponent found.")
            return
        echelon_colour, _ = sm.get_gear_tier_colours(player_obj.player_echelon)
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
        channel_obj = ctx.channel
        message = await channel_obj.send(embed=pvp_embed)

        async def run_pvp_cog():
            return enginecogs.PvPCog(engine_bot, ctx, player_obj, opponent_player, message, channel_obj)

        pvp_cog = await run_pvp_cog()
        task = asyncio.create_task(pvp_cog.run())
        await task

    @engine_bot.hybrid_command(name='automapper', help="Run a map automatically. "
                                                       "Default tier: Highest. Cost: 500 + (50 x Tier)")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def automapper(ctx, tier=0):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_echelon < 4:
            await ctx.send("Player must be echelon 4 or higher.")
            return
        if player_obj.player_echelon + 1 < tier:
            await ctx.send("Too Perilous! You are only qualified for expeditions one tier above your echelon.")
            return
        if tier not in range(0, 11):
            await ctx.send("Tier must be between 1 and 10.")
            return
        tier = min(10, player_obj.player_echelon + 1) if tier == 0 else tier
        existing_id = await encounters.get_raid_id(ctx.channel.id, player_obj.player_id)
        if existing_id != 0:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        if not player_obj.spend_stamina(500 + 50 * tier):
            await ctx.send("Insufficient stamina to embark.")
            return
        await encounters.add_automapper(ctx.channel.id, player_obj.player_id)
        colour, _ = sm.get_gear_tier_colours(tier)
        title = f"{player_obj.player_username} - {adventuredata.reverse_map_tier_dict[tier]} [AUTO]"
        map_embed = discord.Embed(colour=colour, title=title, description="")
        await ctx.send(f"{player_obj.player_username} embarks on a tier {tier} expedition.")
        message = await ctx.channel.send(embed=map_embed)

        async def run_map_cog():
            return enginecogs.MapCog(engine_bot, ctx, player_obj, tier, message, colour)

        map_cog = await run_map_cog()
        task = asyncio.create_task(map_cog.run())
        await task

    engine_bot.run(TOKEN)
