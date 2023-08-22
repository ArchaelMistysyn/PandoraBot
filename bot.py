import discord
import chatcommands
from discord.ext import commands
import json
import asyncio
import inventory
import bosses
import random
import pandas as pd
from discord import embeds


# chat responses
async def send_message(message, user_message, is_private):
    try:
        response = chatcommands.get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# run the bot
def run_discord_bot():
    TOKEN = 'MTE0MDUwNTY2NTk5NjA2Mjc4MA.GlwpR7.aEd1dBGZMpDNIFDgWG0DaClTUyCmg316EwGEZ0'
    intents = discord.Intents.default()
    intents.message_content = True
    pandora_bot = discord.Client(intents=intents)

    @pandora_bot.event
    async def on_ready():
        print(f'{pandora_bot.user} Online!')
        # write line to inventory file
        # outcome = inventory.test_create_csv()
        # print(f'{outcome}!')

        # run the active boss. text files should be initialized to 0 before running.
        channel_id = bosses.get_channel_id()
        message_id = bosses.get_message_id()
        if channel_id != 0:
            channel = pandora_bot.get_channel(channel_id)

            # initialize the boss post
            random_number = random.randint(1, 4)
            boss_object = bosses.spawn_boss(channel_id, message_id, random_number)
            sent_message = await channel.send(content=str(boss_object))
            boss_object.message_id = sent_message.id
            #e = discord.embed(title = "embed", url = "https://r2.starryai.com/results/725215039/7fddb218-4199-45b2-bba6-0e2a04a3e4d7.webp")
            #await channel.send(embed=e)
            bosses.store_boss_ids(channel_id, boss_object.message_id)

        #set timer 1 minute
        pandora_bot.loop.create_task(timed_task(60, message_id, channel_id))

        # edit the boss
        # boss_object = fortress.spawn_boss(channel_id, message_id)
        # message = await channel.fetch_message(message_id)
        # await message.edit(content=str(boss_object))

    @pandora_bot.event
    async def on_message(message):
        if message.author == pandora_bot.user:
            return
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{message}" ({channel})')

        if user_message[0] == '?':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

            if user_message == 'testreroll':
                channel_id = bosses.get_channel_id()
                message_id = bosses.get_message_id()
                if channel_id != 0:
                    channel = pandora_bot.get_channel(channel_id)
                    random_number = random.randint(1, 4)
                    updated_boss = bosses.spawn_boss(channel_id, message_id, random_number)
                    message = await channel.fetch_message(message_id)
                    await message.edit(content=str(updated_boss))

    async def timed_task(duration_seconds, message_id, channel_id):

        if channel_id != 0:
            channel = pandora_bot.get_channel(channel_id)

        while True:
            await asyncio.sleep(duration_seconds)
            random_number = random.randint(1, 4)
            boss_object = bosses.spawn_boss(channel_id, message_id, random_number)
            sent_message = await channel.send(content=str(boss_object))


    pandora_bot.run(TOKEN)
