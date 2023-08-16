import discord
import chatcommands
from discord.ext import commands
import json
import asyncio
import inventory
import fortress
import pandas as pd


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
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} Online!')
        # write line to inventory file
        # outcome = inventory.test_create_csv()
        # print(f'{outcome}!')

        # run the active boss. text files should be initialized to 0 before running.
        channel_id = fortress.get_channel_id()
        message_id = fortress.get_message_id()

        if channel_id != 0:
            channel = client.get_channel(channel_id)

            if fortress.check_existing_boss(message_id):
                updated_boss = fortress.update_existing_boss()
                message = await channel.fetch_message(message_id)
                await message.edit(content=updated_boss)
            else:
                boss_post = fortress.spawn_boss()
                sent_message = await channel.send(content=boss_post)
                message_id = sent_message.id
                fortress.store_boss_details(channel_id, message_id)
        else:
            # important to set this to the correct id
            fortress.store_boss_details(1141256394662760498, message_id)

    @client.event
    async def on_message(message):
        if message.author == client.user:
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
                channel_id = fortress.get_channel_id()
                message_id = fortress.get_message_id()
                if channel_id != 0:
                    channel = client.get_channel(channel_id)
                    updated_boss = fortress.update_existing_boss()
                    message = await channel.fetch_message(message_id)
                    await message.edit(content=updated_boss)



    client.run(TOKEN)
