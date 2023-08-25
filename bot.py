import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import inventory
import bosses
import random
import player
import damagecalc
import chatcommands
from discord import embeds


# run the bot
def run_discord_bot():
    TOKEN = 'MTE0MDUwNTY2NTk5NjA2Mjc4MA.GlwpR7.aEd1dBGZMpDNIFDgWG0DaClTUyCmg316EwGEZ0'
    intents = discord.Intents.all()
    intents.message_content = True
    pandora_bot = Bot(command_prefix='!', intents=intents)

    # handle username changes
    @pandora_bot.event
    async def on_user_update(before, after):
        if before.name != after.name:
            temp_player = player.get_player_by_name(before.name)
            temp_player.update_player_name(after.name)

    # bot startup actions
    @pandora_bot.event
    async def on_ready():
        print(f'{pandora_bot.user} Online!')

        # get boss channel info
        channel_id = bosses.get_channel_id()
        channel = pandora_bot.get_channel(channel_id)

        # register all members
        member_list = channel.guild.members
        for x in member_list:
            player_x = player.PlayerProfile()
            player_x.player_name = x
            player_x.add_new_player()

        # set timer 1 minute
        pandora_bot.loop.create_task(timed_task(60, channel_id, channel))

    @pandora_bot.event
    async def timed_task(duration_seconds, channel_id, channel):

        # initialize channel info
        bosses.store_channel_id(channel_id)

        # initialize the boss post
        active_boss = bosses.spawn_boss(channel_id, 1)
        hp_bar_location = active_boss.draw_boss_hp()
        sent_message = await channel.send(content=str(active_boss))
        active_boss.message_id = sent_message.id

        # participate reaction
        participate = '⚔'
        await sent_message.add_reaction(participate)

        def battle(reaction, user):
            return user == channel.author and str(reaction.emoji) == participate

        # e = discord.embed(title = "embed", url = "")
        # await channel.send(embed=e)

        # update boss on a timed loop
        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=600, check=battle)
                player_object = player.PlayerProfile()
                player_object.player_name = str(user)
                player_object.player_id = player.get_player_by_name(str(player_object.player_name))
                if str(reaction.emoji) == participate:
                    is_participating = False
                    for x in active_boss.participating_players:
                        if x == player:
                            is_participating = True
                    if not is_participating:
                        active_boss.participating_players.append(player_object.player_name)
                        player_object.get_equipped()
                        active_boss.player_dmg_min.append(damagecalc.get_dmg_min(player_object))
                        active_boss.player_dmg_max.append(damagecalc.get_dmg_max(player_object))

                    status = "You have joined the raid!"
                    await channel.send(status)
                    break
            except Exception as e:
                print(e)

            total_player_damage = 0
            await asyncio.sleep(duration_seconds)
            for x in active_boss.player_dmg_min:
                total_player_damage += x
            for y in active_boss.player_dmg_max:
                total_player_damage += y
            active_boss.boss_cHP -= total_player_damage/2

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
                    case "Fortress":
                        if random_number == 2:
                            new_boss_type = 2
                    case "Dragon":
                        if random_number == 2:
                            new_boss_type = 3
                    case "Primordial":
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

    @pandora_bot.command(name='lab', help="**!lab** to run a daily labyrinth")
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def lab(channel):
        command_user = player.PlayerProfile
        command_user.player_name = channel.author
        command_user.player_id = player.get_player_by_name(command_user.player_name)
        weapon_object = inventory.CustomWeapon(command_user.player_id)
        response = "You found a tier " + str(weapon_object.item_base_tier) + " weapon!\n"
        response += str(weapon_object)
        response += "\n\nWould you like to keep or discard this item?"
        message = await channel.send(response)

        keep_weapon = '☑️'
        discard_weapon = '🚫'

        await message.add_reaction(keep_weapon)
        await message.add_reaction(discard_weapon)

        def check(reaction, user):
            return user == channel.author and str(reaction.emoji) in [keep_weapon, discard_weapon]

        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == keep_weapon:
                    if not inventory.if_exists("inventory.csv", weapon_object.item_id):
                        status = inventory.inventory_add_weapon(weapon_object)
                        await channel.send(status)
                        break

                if str(reaction.emoji) == discard_weapon:
                    await channel.send('You have discarded the item')
                    break
            except Exception as e:
                print(e)

    @pandora_bot.command(name='dung', help="**!dung** to run a daily dungeon")
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def dung(channel):
        command_user = player.PlayerProfile
        command_user.player_name = channel.author
        command_user.player_id = player.get_player_by_name(command_user.player_name)
        armour_object = inventory.CustomArmour(command_user.player_id)
        response = "You found a tier " + str(armour_object.item_base_tier) + " armour!\n"
        response += str(armour_object)
        response += "\n\nWould you like to keep or discard this item?"
        message = await channel.send(response)

        keep_armour = '✅'
        discard_armour = '❌'

        await message.add_reaction(keep_armour)
        await message.add_reaction(discard_armour)

        def check(reaction, user):
            return user == channel.author and str(reaction.emoji) in [keep_armour, discard_armour]

        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == keep_armour:
                    if not inventory.if_exists("inventory.csv", armour_object.item_id):
                        status = inventory.inventory_add_armour(armour_object)
                        await channel.send(status)
                        break

                if str(reaction.emoji) == discard_armour:
                    await channel.send('You have discarded the item')
                    break
            except Exception as e:
                print(e)

    @pandora_bot.command(name='tow', help="**!tow** to run a daily tower")
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def tow(channel):
        command_user = player.PlayerProfile
        command_user.player_name = channel.author
        command_user.player_id = player.get_player_by_name(command_user.player_name)
        acc_object = inventory.CustomAccessory(command_user.player_id)
        response = "You found a tier " + str(acc_object.item_base_tier) + " accessory!\n"
        response += str(acc_object)
        response += "\n\nWould you like to keep or discard this item?"
        message = await channel.send(response)

        keep_accessory = '💍'
        discard_accessory = '📵'

        await message.add_reaction(keep_accessory)
        await message.add_reaction(discard_accessory)

        def check(reaction, user):
            return user == channel.author and str(reaction.emoji) in [keep_accessory, discard_accessory]

        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == keep_accessory:
                    if not inventory.if_exists("inventory.csv",acc_object.item_id):
                        status = inventory.inventory_add_accessory(acc_object)
                        await channel.send(status)
                        break

                if str(reaction.emoji) == discard_accessory:
                    await channel.send('You have discarded the item')
                    break
            except Exception as e:
                print(e)

    @pandora_bot.command(name='equip', help="**!equip itemTYPE itemID** to equip an item")
    async def equip(channel, item_shortcut, item_id):
        filename = 'inventory.csv'
        item_id = item_id.upper()
        match item_shortcut:
            case 'weapon':
                if inventory.if_exists('inventory.csv', item_id):
                    selected_item = inventory.read_weapon(filename, item_id)
                    current_user = player.get_player_by_name(str(channel.author))
                    if current_user.player_id == selected_item.player_owner:
                        response = current_user.equip(item_shortcut, selected_item.item_id)
                    else:
                        response = "wrong item id"
                else:
                    response = "wrong item id"
            case 'armour':
                if inventory.if_exists('inventory.csv', item_id):
                    selected_item = inventory.read_armour(filename, item_id)
                    current_user = player.get_player_by_name(str(channel.author))
                    if current_user.player_id == selected_item.player_owner:
                        response = current_user.equip(item_shortcut, selected_item.item_id)
                    else:
                        response = "wrong item id"
                else:
                    response = "wrong item id"
            case 'accessory':
                if inventory.if_exists('inventory.csv', item_id):
                    selected_item = inventory.read_accessory(filename, item_id)
                    current_user = player.get_player_by_name(str(channel.author))
                    if current_user.player_id == selected_item.player_owner:
                        response = current_user.equip(item_shortcut, selected_item.item_id)
                    else:
                        response = "wrong item id"
                else:
                    response = "wrong item id"
            case 'wing':
                response = "bad input"
            case 'crest':
                response = "bad input"
            case _:
                response = "Equippable item type not recognized"

        await channel.send(response)

    @pandora_bot.command(name='quest', help="**!quest** to start the story quest")
    async def quest(channel):
        # quest progression
        sparkle = '✨'
        story_response = chatcommands.get_command_text("!story1")
        sent_message = await channel.send(content=str(story_response))
        await sent_message.add_reaction(sparkle)

        def box_open(reaction, user):
            return user == channel.author and str(reaction.emoji) == sparkle

        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=box_open)
                if str(reaction.emoji) == sparkle:
                    status = chatcommands.get_command_text('story2')
                    await channel.send(status)
                    break
            except Exception as e:
                print(e)

    pandora_bot.run(TOKEN)
