import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import inventory
import bosses
import random
from discord import embeds
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


# run the bot
def run_discord_bot():
    TOKEN = 'MTE0MDUwNTY2NTk5NjA2Mjc4MA.GlwpR7.aEd1dBGZMpDNIFDgWG0DaClTUyCmg316EwGEZ0'
    intents = discord.Intents.all()
    intents.message_content = True
    pandora_bot = Bot(command_prefix='!', intents=intents)

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
            boss_object = bosses.spawn_boss(channel_id, 1)
            out = Image.new("RGB", (150, 100), (255, 255, 255))
            d = ImageDraw.Draw(out)
            d = bosses.drawProgressBar(d, 10, 10, 100, 25, 1)
            # out.save("output.jpg")

            sent_message = await channel.send(content=str(boss_object))
            boss_object.message_id = sent_message.id

            # e = discord.embed(title = "embed", url = "https://r2.starryai.com/results/725215039/7fddb218-4199-45b2-bba6-0e2a04a3e4d7.webp")
            # await channel.send(embed=e)
            bosses.store_channel_id(channel_id)

        # set timer 1 minute
        pandora_bot.loop.create_task(timed_task(60, boss_object))

    @pandora_bot.event
    async def timed_task(duration_seconds, boss_object):
        active_boss = boss_object
        channel_id = active_boss.boss_channel_id
        if channel_id != 0:
            channel = pandora_bot.get_channel(channel_id)

        while True:
            await asyncio.sleep(duration_seconds)
            player1_damage = 1000
            player2_damage = 2000
            player3_damage = 3000
            total_player_damage = player1_damage + player2_damage + player3_damage
            active_boss.boss_cHP -= total_player_damage

            if active_boss.calculate_hp():
                # update boss info
                message = await channel.fetch_message(active_boss.message_id )
                await message.edit(content=str(active_boss))
            else:
                # update dead boss info
                active_boss.boss_cHP = 0
                message = await channel.fetch_message(active_boss.message_id )
                dead_boss = str(active_boss) + "\n**SLAIN**\n__Damage Rankings__\n__Loot Awarded__"
                await message.edit(content=str(dead_boss))

                random_number = random.randint(1, 2)
                new_boss_type = 1

                # spawn a new boss
                match active_boss.boss_type:
                    case "fortress":
                        if random_number == 2:
                            new_boss_type = 2
                    case "dragon":
                        if random_number == 2:
                            new_boss_type = 3
                    case "primordial":
                        new_boss_type = 1
                    case _:
                        error = "this boss should not be a Paragon"

                active_boss = bosses.spawn_boss(channel_id, new_boss_type)
                sent_message = await channel.send(content=str(active_boss))
                active_boss.message_id = sent_message.id

    @pandora_bot.event
    async def on_command_error(channel, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            minutes = seconds / 60
            hours = int(minutes / 60)
            await channel.send(f'This command is on a {hours} hour cooldown' )
        raise error

    @pandora_bot.command(name='lab', help="run a labyrinth")
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def lab(channel):
        weapon_object = inventory.CustomWeapon(channel.author)
        response = "You found a tier " + str(weapon_object.item_base_tier) + " weapon!\n"
        response += str(weapon_object)
        response += "\n\nWould you like to keep or discard this item?"
        message = await channel.send(response)

        keep = '✅'
        discard = '❌'

        await message.add_reaction(keep)
        await message.add_reaction(discard)

        def check(reaction, user):
            return user == channel.author and str(reaction.emoji) in [keep, discard]

        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == keep:
                    if not inventory.if_exists("inventory.csv", weapon_object.item_id):
                        status = inventory.inventory_add_weapon(weapon_object)
                        await channel.send(status)
                        break

                if str(reaction.emoji) == discard:
                    await channel.send('You have discarded the item')
                    break
            except Exception as e:
                print(e)

    pandora_bot.run(TOKEN)
