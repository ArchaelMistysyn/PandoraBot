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

    async def run_solo_cog(player_obj, boss_obj, channel_id, sent_message, ctx, gauntlet=False, mode=0, magnitude=0):
        return enginecogs.SoloCog(engine_bot, player_obj, boss_obj, channel_id, sent_message, ctx,
                                  gauntlet=gauntlet, mode=mode, magnitude=magnitude)

    # Admin Commands
    @engine_bot.command(name='sync', help="Archael Only")
    async def sync(ctx):
        if ctx.message.author.id != 185530717638230016:
            await ctx.send('You must be the owner to use this command!')
        try:
            synced = await engine_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
            print(f"Combat Engine Synced! {len(synced)} command(s)")
            await ctx.send('commands synced!')
        except Exception as e:
            print(e)

    @engine_bot.command(name='reset_sync', help="Archael Only")
    async def reset_sync(ctx):
        if ctx.message.author.id != 185530717638230016:
            await ctx.send('You must be the owner to use this command!')
        try:
            global_sync = await engine_bot.tree.sync(guild=None)
            print(f"Combat Engine Synced! {len(global_sync)} global command(s)")
            synced = await engine_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
            print(f"Combat Engine Synced! {len(synced)} command(s)")
            await ctx.send('commands synced!')
        except Exception as e:
            print(e)

    @engine_bot.command(name='start_raid', help="Archael Only")
    async def start_raid(ctx, server_select="single"):
        if ctx.message.author.id != 185530717638230016:
            await ctx.send('You must be the owner to use this command!')
            return
        if server_select == "single":
            raid_channel_id = gli.servers[ctx.guild.id][1]
            await encounters.clear_all_encounter_info(ctx.guild.id)
            enginecogs.RaidSchedularCog(engine_bot, engine_bot.get_channel(raid_channel_id), raid_channel_id)
            return
        elif server_select == "all":
            for server_id, (_, raid_channel_id, _, _) in gli.servers.items():
                await encounters.clear_all_encounter_info(server_id)
                enginecogs.RaidSchedularCog(engine_bot, engine_bot.get_channel(raid_channel_id), raid_channel_id)

    @engine_bot.hybrid_command(name='abandon', help="Abandon an active solo encounter.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def abandon(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        flag_response = await combat.abandon_flag(player_obj, toggle=True)
        if flag_response is None:
            await ctx.send("You are not in any solo encounter.")
            return
        elif flag_response == 1:
            await ctx.send("You are already flagged to abandon the encounter.")
            return
        await ctx.send("You have flagged to abandon the encounter.")

    @engine_bot.hybrid_command(name='fortress', help="Challenge a fortress boss. Cost: 1 Fortress Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def fortress(ctx, magnitude=0):
        await solo(ctx, boss_type="Fortress", magnitude=magnitude)

    @engine_bot.hybrid_command(name='dragon', help="Challenge a dragon boss. Cost: 1 Dragon Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def dragon(ctx, magnitude=0):
        await solo(ctx, boss_type="Dragon", magnitude=magnitude)

    @engine_bot.hybrid_command(name='demon', help="Challenge a demon boss. Cost: 1 Demon Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def demon(ctx, magnitude=0):
        await solo(ctx, boss_type="Demon", magnitude=magnitude)

    @engine_bot.hybrid_command(name='paragon', help="Challenge a paragon boss. Cost: 1 Paragon Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def paragon(ctx, magnitude=0):
        await solo(ctx, boss_type="Paragon", magnitude=magnitude)

    @engine_bot.hybrid_command(name='arbiter', help="Challenge a paragon boss. Cost: 1 Arbiter Stone + 200 Stamina")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def arbiter(ctx, magnitude=0):
        await solo(ctx, boss_type="Arbiter", magnitude=magnitude)

    @engine_bot.hybrid_command(name='solo',
                               help="Type Options: [Random/Fortress/Dragon/Demon/Paragon/Arbiter]. Stamina Cost: 200")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def solo(ctx, boss_type="random", magnitude=0):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if magnitude not in range(11):
            await ctx.send("Selected magnitude must be between 0-10. Default 0.")
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        existing_id = await encounters.get_encounter_id(ctx.channel.id, player_obj.player_id)
        if existing_id is not None:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        if not await player_obj.spend_stamina(200):
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
            if boss_type not in gli.boss_list[:-2]:
                await ctx.send(
                    "Boss type not recognized. Please select [Random/Fortress/Dragon/Demon/Paragon/Arbiter].")
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
        new_boss_tier = bosses.get_random_bosstier(boss_type)
        boss_obj = await bosses.spawn_boss(ctx.channel.id, player_obj.player_id, new_boss_tier, boss_type,
                                           player_obj.player_level, magnitude=magnitude)
        boss_obj.player_id = player_obj.player_id
        embed_msg = boss_obj.create_boss_embed()
        magnitude_msg = f" [Magnitude: {magnitude}]" if magnitude > 0 else ""
        msg = f"{player_obj.player_username} has spawned a tier {boss_obj.boss_tier} boss!{magnitude_msg}"
        await ctx.send(msg)
        sent_message = await ctx.channel.send(embed=embed_msg)
        solo_cog = await run_solo_cog(player_obj, boss_obj, ctx.channel.id, sent_message, ctx, magnitude)
        task = asyncio.create_task(solo_cog.run())
        await task

    @engine_bot.hybrid_command(name='palace', help="Enter the Divine Palace. [WARNING: HARD]")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def palace(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        existing_id = await encounters.get_encounter_id(ctx.channel.id, player_obj.player_id)
        if existing_id is not None:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        if player_obj.player_quest < 50:
            await ctx.send("The divine palace is not a place mortals may tread.")
            return
        await ctx.send(f"{player_obj.player_username} enters the divine palace.")
        lotus_obj = inventory.BasicItem("Lotus10")
        lotus_stock = await inventory.check_stock(player_obj, lotus_obj.item_id)

        if lotus_stock >= 1:
            description = (f"Rows of torches lining the ivory halls ignite with divine fire. "
                           f"Yubelle's echo manifests drawing energy from the Divine Lotus. "
                           f"Shifting into a new being, 'it' challenges you before the eyes of god."
                           f"\n**EXTREME DIFFICUILTY WARNING:\n{lotus_obj.item_emoji} 1x Divine Lotus "
                           f"will be consumed.**")
            img_url, colour = gli.palace_day_img, "white"
        else:
            description = "The palace interior remains still, the torches unlit and the halls silent."
            img_url, colour = gli.palace_night_img, "purple"
        embed_msg = sm.easy_embed(colour, "Divine Palace of God", description)
        embed_msg.set_image(url=img_url)
        sent_message = await ctx.channel.send(embed=embed_msg)
        palace_view = PalaceView(player_obj, lotus_obj, lotus_stock, sent_message, ctx)
        await sent_message.edit(embed=embed_msg, view=palace_view)

    class PalaceView(discord.ui.View):
        def __init__(self, player_obj, lotus_obj, lotus_stock, sent_message, ctx):
            super().__init__(timeout=None)
            self.player_obj, self.lotus_obj, self.lotus_stock = player_obj, lotus_obj, lotus_stock
            self.ctx, self.sent_message = ctx, sent_message
            self.embed_msg = False
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
            lotus_stock = await inventory.check_stock(self.player_obj, self.lotus_obj.item_id)
            embed_msg = sm.easy_embed("purple", "Divine Palace of God", "")
            if lotus_stock < 1:
                embed_msg.description = "The echo falls silent and fades away alongside the light of the torches."
                embed_msg.set_image(url=gli.palace_night_img)
                await interaction.response.edit_message(embed=embed_msg, view=None)
                return
            boss_level = 300 if difficulty == 1 else 600 if difficulty == 2 else 999
            await inventory.update_stock(self.player_obj, self.lotus_obj.item_id, -1)
            boss_obj = await bosses.spawn_boss(self.ctx.channel.id, self.player_obj.player_id, 8,
                                               "Incarnate", boss_level)
            label_list = {1: " [Challenger]", 2: " [Usurper]", 3: " [Samsara]"}
            embed_msg = boss_obj.create_boss_embed(extension=label_list[difficulty])
            await interaction_obj.response.edit_message(embed=embed_msg, view=None)
            solo_cog = await run_solo_cog(self.player_obj, boss_obj, self.ctx.channel.id, self.sent_message, self.ctx,
                                          mode=difficulty)
            task = asyncio.create_task(solo_cog.run())
            await task

    @engine_bot.hybrid_command(name='gauntlet', help="Challenge the gauntlet in the Spire of Illusions.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def run_gauntlet(ctx, magnitude=0):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if magnitude not in range(11):
            await ctx.send("Selected magnitude must be between 0-10. Default 0.")
            return
        if player_obj.player_equipped[0] == 0:
            await ctx.send("You must have a weapon equipped.")
            return
        if player_obj.player_quest < 36:
            await ctx.send("You must complete quest 36 to challenge the Spire of Illusions.")
            return
        existing_id = await encounters.get_encounter_id(ctx.channel.id, player_obj.player_id)
        if existing_id is not None:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        token_item = inventory.BasicItem("Compass")
        player_stock = await inventory.check_stock(player_obj, "Compass")
        if player_stock <= 0:
            await ctx.send(f"Out of Stock: {token_item.item_emoji} {token_item.item_name}.")
            return
        await inventory.update_stock(player_obj, "Compass", -1)
        await quest.assign_unique_tokens(player_obj, "Gauntlet")
        boss_obj = await bosses.spawn_boss(
            ctx.channel.id, player_obj.player_id, 1, "Fortress",
            player_obj.player_level, gauntlet=True, magnitude=magnitude)
        boss_obj.player_id = player_obj.player_id
        magnitude_msg = f" [Magnitude: {magnitude}]" if magnitude > 0 else ""
        await ctx.send(f"{player_obj.player_username} has entered the Spire of Illusions!{magnitude_msg}")
        embed_msg = boss_obj.create_boss_embed(extension=" [Gauntlet]")
        sent_message = await ctx.channel.send(embed=embed_msg)
        gauntlet_cog = await run_solo_cog(player_obj, boss_obj, ctx.channel.id, sent_message, ctx,
                                          gauntlet=True, magnitude=magniutde)
        task = asyncio.create_task(gauntlet_cog.run())
        await task

    @engine_bot.hybrid_command(name='summon', help="Consume a summoning item to summon a high tier boss. Options [1-3]")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def summon(ctx, token_version: int, magnitude=0):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if magnitude not in range(11):
            await ctx.send("Selected magnitude must be between 0-10. Default 0.")
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
        existing_id = await encounters.get_encounter_id(ctx.channel.id, player_obj.player_id)
        if existing_id is not None:
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
        boss_obj = await bosses.spawn_boss(ctx.channel.id, player_obj.player_id, new_boss_tier,
                                           boss_type, player_obj.player_level, magnitude=magnitude)
        boss_obj.player_id = player_obj.player_id
        magnitude_msg = f" [Magnitude: {magnitude}]" if magnitude > 0 else ""
        msg = f"{player_obj.player_username} has summoned a tier {boss_obj.boss_tier} boss!{magnitude_msg}"
        await ctx.send(msg)
        embed_msg = boss_obj.create_boss_embed()
        sent_message = await ctx.channel.send(embed=embed_msg)
        solo_cog = await run_solo_cog(player_obj, boss_obj, ctx.channel.id, sent_message, ctx, magnitude=magnitude)
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
        difference, method = await player_obj.check_cooldown("arena")
        if difference:
            one_day = timedelta(days=1)
            cooldown = one_day - difference
            if difference <= one_day:
                cooldown_timer = int(cooldown.total_seconds() / 60 / 60)
                time_msg = f"Your next arena match is in {cooldown_timer} hours."
                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title="Arena Closed!",
                                          description=time_msg)
                await ctx.send(embed=embed_msg)
                return
        await player_obj.set_cooldown("arena", "")
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
        existing_id = await encounters.get_encounter_id(ctx.channel.id, player_obj.player_id)
        if existing_id is not None:
            await ctx.send("You already have a solo boss or map encounter running.")
            return
        if not await player_obj.spend_stamina(500 + 50 * tier):
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
