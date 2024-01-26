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
import player
from datetime import datetime as dt, timedelta

# Get Bot Token
token_info = None
with open("vouch_bot_token.txt", 'r') as token_file:
    for line in token_file:
        token_info = line
TOKEN = token_info


class VouchBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())


def run_discord_bot():
    vouch_bot = VouchBot()

    @vouch_bot.event
    async def on_ready():
        print(f'{vouch_bot.user} Online!')
        vouch_bot.help_command = None

    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

    async def on_shutdown():
        print("Vouch Wyvern Off")
        try:
            await engine_bot.close()
            await engine_bot.session.close()
        except KeyboardInterrupt:
            sys.exit(0)

    # Admin Commands
    @vouch_bot.command(name='sync', help="Archael Only")
    async def sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                synced = await vouch_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Vouch Wyvern Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @vouch_bot.command(name='reset_sync', help="Archael Only")
    async def reset_sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                global_sync = await vouch_bot.tree.sync(guild=None)
                print(f"Vouch Wyvern Synced! {len(global_sync)} global command(s)")
                synced = await vouch_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Vouch Wyvern Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @vouch_bot.hybrid_command(name='vouch', help="Grants one vouch to a user.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def vouch(ctx, user: discord.User):
        if user.id == ctx.author.id:
            await ctx.send("You cannot vouch for yourself.")
        command_user = player.get_player_by_discord(ctx.author.id)
        if command_user.player_class != "":
            difference, method = command_user.check_cooldown("vouch")
            run_command = False
            if difference:
                six_hours = timedelta(hours=6)
                cooldown = six_hours - difference
                if difference <= six_hours:
                    cooldown_hours, cooldown_minutes = divmod(int(cooldown.total_seconds() / 60), 60)
                    await ctx.send(f"Your vouch command is on cooldown for {cooldown_hours} hours and {cooldown_minutes} minutes.")
                else:
                    run_command = True
            else:
                run_command = True
            if run_command:
                command_user.set_cooldown("vouch", "")
                player_object = player.get_player_by_discord(user.id)
                if player_object.player_class != "":
                    role_points = {
                        1011375497265033216: 20,  # Owner role ID
                        1134301246648488097: 10,  # Administrator role ID
                        1134293907136585769: 5,  # Moderator role ID
                        1140738057381871707: 2,  # Guild Member role ID
                    }
                    default_points = 1
                    user_roles = [role.id for role in ctx.author.roles]
                    highest_role_id = max(user_roles, key=lambda role_id: role_points.get(role_id, default_points))
                    num_points = role_points.get(highest_role_id, default_points)
                    new_points = num_points + player_object.vouch_points
                    player_object.set_player_field("vouch_points", new_points)
                    if new_points >= 1000:
                        trusted_rat_role = discord.utils.get(ctx.guild.roles, name='Trusted Rat')
                        if trusted_rat_role not in user.roles:
                            await user.add_roles(trusted_rat_role)
                    await ctx.send(f"{num_points} vouch points awarded to {user.name}.")
                else:
                    await ctx.send(f"Unregistered users cannot receive vouch points.")
        else:
            embed_msg = unregistered_message()
            await ctx.send(embed=embed_msg)

    @vouch_bot.hybrid_command(name='vcheck', help="Check the vouches of a user.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def vouch(ctx, user: discord.User):
        selected_user = player.get_player_by_discord(user.id)
        if selected_user.player_class != "":
            num_vouches = selected_user.vouch_points
        else:
            num_vouches = 0
        await ctx.send(f"{user.name} has {num_vouches} vouch points in server [{ctx.guild.name}].")

    def unregistered_message():
        register_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                       title="Unregistered",
                                       description="Please register using !register to play.")
        return register_embed

    vouch_bot.run(TOKEN)
