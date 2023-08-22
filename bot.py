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
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


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
        message_id = 0
        if channel_id != 0:
            channel = pandora_bot.get_channel(channel_id)

            # initialize the boss post
            random_number = random.randint(1, 3)
            boss_object = bosses.spawn_boss(channel_id, random_number)
            out = Image.new("RGB", (150, 100), (255, 255, 255))
            d = ImageDraw.Draw(out)
            d = bosses.drawProgressBar(d, 10, 10, 100, 25, 1)
            # out.save("output.jpg")

            sent_message = await channel.send(content=str(boss_object))
            boss_object.message_id = sent_message.id

            #e = discord.embed(title = "embed", url = "https://r2.starryai.com/results/725215039/7fddb218-4199-45b2-bba6-0e2a04a3e4d7.webp")
            #await channel.send(embed=e)
            bosses.store_channel_id(channel_id)

        #set timer 1 minute
        pandora_bot.loop.create_task(timed_task(60, boss_object))


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

            # if user_message == 'specialcommand':


    async def timed_task(duration_seconds, boss_object):
        active_boss = boss_object
        channel_id = active_boss.boss_channel_id
        if channel_id != 0:
            channel = pandora_bot.get_channel(channel_id)

        while True:
            await asyncio.sleep(duration_seconds)
            player1_damage = 25000
            player2_damage = 50000
            player3_damage = 75000
            total_player_damage = player1_damage + player2_damage + player3_damage
            active_boss.boss_cHP -= total_player_damage

            if bosses.calculate_hp(active_boss):
                # update boss info
                message = await channel.fetch_message(active_boss.message_id )
                await message.edit(content=str(active_boss))
            else:
                # update dead boss info
                active_boss.boss_cHP = 0
                message = await channel.fetch_message(active_boss.message_id )
                dead_boss = str(active_boss) + "\n**SLAIN**\n__Damage Rankings__\n__Loot Awarded__"
                await message.edit(content=str(dead_boss))

                #spawn a new boss
                random_number = random.randint(1,3)
                active_boss = bosses.spawn_boss(channel_id, random_number)
                sent_message = await channel.send(content=str(active_boss))
                active_boss.message_id = sent_message.id


    pandora_bot.run(TOKEN)
