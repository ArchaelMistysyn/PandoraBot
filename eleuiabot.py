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

# Get Bot Token
token_info = None
with open("eleuia_bot_token.txt", 'r') as token_file:
    for line in token_file:
        token_info = line
TOKEN = token_info


class EleuiaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())


def run_discord_bot():
    eleuia_bot = EleuiaBot()

    @eleuia_bot.event
    async def on_ready():
        print(f'\n{eleuia_bot.user} Online!')
        eleuia_bot.help_command = None

    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

    eleuia_bot.run(TOKEN)
