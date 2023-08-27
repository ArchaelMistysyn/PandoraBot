import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import inventory
import bosses
import random
import pandas as pd
import loot
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

        # get boss channel info // needs to be updated for multiple values
        # channel_id = bosses.get_channel_id()
        # ctx = pandora_bot.get_channel(channel_id)

        channel_id = 1141256419161673739
        ctx = pandora_bot.get_channel(channel_id)

        # register all members
        member_list = ctx.guild.members
        for x in member_list:
            player_x = player.PlayerProfile()
            player_x.player_name = x
            player_x.add_new_player()

        # set timer 1 minute
        pandora_bot.loop.create_task(timed_task(60, channel_id, ctx))
        pandora_bot.loop.create_task(stamina_manager(600, ctx))

    @pandora_bot.event
    async def stamina_manager(duration_seconds, ctx):
        while True:
            await asyncio.sleep(duration_seconds)
            filename = "playerlist.csv"
            df = pd.read_csv(filename)
            df.loc[df['stamina'] < 100, 'stamina'] = df['stamina']+1
            df.to_csv(filename, index=False)

    @pandora_bot.event
    async def timed_task(duration_seconds, channel_id, ctx):

        # initialize the boss post
        active_boss = bosses.spawn_boss(2)
        img_link = "https://i.ibb.co/hyT1d8M/dragon.jpg"
        hp_bar_location = active_boss.draw_boss_hp(active_boss.boss_cHP/active_boss.boss_mHP)

        # build embedded message
        match active_boss.boss_tier:
            case 1:
                tier_colour = discord.Colour.green()
                life_emoji = "💚"
            case 2:
                tier_colour = discord.Colour.blue()
                life_emoji = "💙"
            case 3:
                tier_colour = discord.Colour.purple()
                life_emoji = "💜"
            case 4:
                tier_colour = discord.Colour.gold()
                life_emoji = "💛"
            case _:
                tier_colour = discord.Colour.red()
                life_emoji = "❤️"

        boss_title = f'{active_boss.boss_name}'
        boss_field = f'Tier {active_boss.boss_tier} {active_boss.boss_type}'
        boss_hp = f'{life_emoji}({active_boss.boss_cHP} / {active_boss.boss_mHP})'
        boss_weakness = f'Weakness: {active_boss.boss_typeweak}'
        boss_weakness += f'{active_boss.boss_eleweak_a}{active_boss.boss_eleweak_b}'
        embed_msg = discord.Embed(colour=tier_colour,
                                  title=boss_title,
                                  description="")
        embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
        embed_msg.add_field(name=boss_weakness, value="", inline=False)
        embed_msg.set_image(url=img_link)
        # file = discord.File("boss_hp.jpg", filename="image.jpg")
        # embed_msg.set_thumbnail(url="attachment://image.jpg")
        sent_message = await ctx.send(embed=embed_msg)

        active_boss.message_id = sent_message.id

        # participate reaction
        participate = '⚔️'
        await sent_message.add_reaction(participate)

        def battle(reaction, user):
            return user == ctx.author and str(reaction.emoji) == participate

        while True:
            total_player_damage = 100000
            await asyncio.sleep(duration_seconds)
            """for x in active_boss.player_dmg_min:
                total_player_damage += x
            for y in active_boss.player_dmg_max:
                total_player_damage += y"""
            active_boss.boss_cHP -= total_player_damage/2

            if active_boss.calculate_hp():
                # update boss info
                boss_hp = f'{life_emoji}({active_boss.boss_cHP} / {active_boss.boss_mHP})'
                embed_msg.remove_field(index=0)
                embed_msg.insert_field_at(index=0, name=boss_field, value=boss_hp, inline=False)
                await sent_message.edit(embed=embed_msg)
            else:
                # update dead boss info
                active_boss.boss_cHP = 0
                boss_hp = f'{life_emoji}({active_boss.boss_cHP} / {active_boss.boss_mHP})'
                embed_msg.remove_field(index=0)
                embed_msg.remove_field(index=0)
                embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
                embed_msg.add_field(name=boss_weakness, value="", inline=False)
                embed_msg.add_field(name="SLAIN", value="", inline=False)
                embed_msg.add_field(name="Damage Rankings", value="", inline=False)
                embed_msg.add_field(name="Loot Awarded", value="", inline=False)
                # embed_msg.set_image(url="slain image?")
                await sent_message.edit(embed=embed_msg)

                random_number = random.randint(1, 2)
                new_boss_type = 2
                img_link = "https://i.ibb.co/hyT1d8M/dragon.jpg"
                # spawn a new boss
                match active_boss.boss_type:
                    case "Dragon":
                        if random_number == 2:
                            new_boss_type = 3
                            img_link = "https://i.ibb.co/DMhCjpB/primordial.png"
                    case "Primordial":
                        new_boss_type = 2
                    case _:
                        error = "this boss should not be anything else"

                active_boss = bosses.spawn_boss(new_boss_type)

                # build embedded message
                match active_boss.boss_tier:
                    case 1:
                        tier_colour = discord.Colour.green()
                        life_emoji = "💚"
                    case 2:
                        tier_colour = discord.Colour.blue()
                        life_emoji = "💙"
                    case 3:
                        tier_colour = discord.Colour.purple()
                        life_emoji = "💜"
                    case 4:
                        tier_colour = discord.Colour.gold()
                        life_emoji = "💛"
                    case _:
                        tier_colour = discord.Colour.red()
                        life_emoji = "❤️"

                boss_title = f'{active_boss.boss_name}'
                boss_field = f'Tier {active_boss.boss_tier} {active_boss.boss_type}'
                boss_hp = f'{life_emoji}({active_boss.boss_cHP} / {active_boss.boss_mHP})'
                boss_weakness = f'Weakness: {active_boss.boss_typeweak}'
                boss_weakness += f'{active_boss.boss_eleweak_a}{active_boss.boss_eleweak_b}'
                embed_msg = discord.Embed(colour=tier_colour,
                                          title=boss_title,
                                          description="")
                embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
                embed_msg.add_field(name=boss_weakness, value="", inline=False)
                embed_msg.set_image(url=img_link)
                # file = discord.File("boss_hp.jpg", filename="image.jpg")
                # embed_msg.set_thumbnail(url="attachment://image.jpg")

                sent_message = await ctx.send(embed=embed_msg)
                active_boss.message_id = sent_message.id

    @pandora_bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            minutes = seconds / 60
            hours = int(minutes / 60)
            await ctx.send(f'This command is on a {hours} hour cooldown' )
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send('You are at your command limit for this command')
        raise error

    @pandora_bot.command(name='lab', help="**!lab** to run a daily labyrinth")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    # @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def lab(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(4):
            weapon_object = inventory.CustomWeapon(command_user.player_id)

            gear_colours = inventory.get_gear_tier_colours(weapon_object.item_base_tier)
            tier_colour = gear_colours[0]
            tier_emoji = gear_colours[1]

            item_title = f'{weapon_object.item_name}'
            display_stars = ""
            damage_bonus = f'Base Damage: {str(weapon_object.item_damage_min)} - {str(weapon_object.item_damage_max)}'
            item_rolls = f'Base Attack Speed {weapon_object.item_bonus_stat}/min'
            for x in range(weapon_object.item_num_stars):
                display_stars += "<:estar1:1143756443967819906>"
            for y in range((5 - weapon_object.item_num_stars)):
                display_stars += "<:ebstar2:1144826056222724106>"
            item_types = f'{weapon_object.item_damage_type}'
            for z in weapon_object.item_elements:
                item_types += f'{z}'
            inquiry = "Would you like to keep or discard this item?"
            embed_msg = discord.Embed(colour=tier_colour,
                                      title=item_title,
                                      description=display_stars)
            embed_msg.add_field(name=item_types, value=damage_bonus, inline=False)
            embed_msg.add_field(name="Item Rolls", value=item_rolls, inline=False)
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(weapon_object.item_base_tier)} item found!', value=inquiry, inline=False)
            embed_msg.set_thumbnail(url="https://i.ibb.co/ygGCRnc/sworddefaulticon.png")
            message = await ctx.send(embed=embed_msg)

            keep_weapon = '☑️'
            discard_weapon = '🚫'

            await message.add_reaction(keep_weapon)
            await message.add_reaction(discard_weapon)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [keep_weapon, discard_weapon]

            while True:
                try:
                    reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=check)

                    if str(reaction.emoji) == keep_weapon:
                        if not inventory.if_custom_exists(weapon_object.item_id):
                            status = inventory.inventory_add_weapon(weapon_object)
                            await ctx.send(status)
                            break

                    if str(reaction.emoji) == discard_weapon:
                        await ctx.send('You have discarded the item')
                        break
                except Exception as e:
                    print(e)

    @pandora_bot.command(name='dung', help="**!dung** to run a daily dungeon")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    # @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def dung(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(4):
            armour_object = inventory.CustomArmour(command_user.player_id)

            gear_colours = inventory.get_gear_tier_colours(armour_object.item_base_tier)
            tier_colour = gear_colours[0]
            tier_emoji = gear_colours[1]

            item_title = f'{armour_object.item_name}'
            display_stars = ""
            damage_bonus = f'Base Damage: {str(armour_object.item_damage_min)} - {str(armour_object.item_damage_max)}'
            item_rolls = f'Base Damage Mitigation {armour_object.item_bonus_stat}%'
            for x in range(armour_object.item_num_stars):
                display_stars += "<:estar1:1143756443967819906>"
            for y in range((5 - armour_object.item_num_stars)):
                display_stars += "<:ebstar2:1144826056222724106>"

            inquiry = "Would you like to keep or discard this item?"
            embed_msg = discord.Embed(colour=tier_colour,
                                      title=item_title,
                                      description=display_stars)
            embed_msg.add_field(name="", value=damage_bonus, inline=False)
            embed_msg.add_field(name="Item Rolls", value=item_rolls, inline=False)
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(armour_object.item_base_tier)} item found!', value=inquiry,
                                inline=False)
            embed_msg.set_thumbnail(url="https://i.ibb.co/p2K2GFK/armouricon.png")
            message = await ctx.send(embed=embed_msg)

            keep_armour = '✅'
            discard_armour = '❌'

            await message.add_reaction(keep_armour)
            await message.add_reaction(discard_armour)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [keep_armour, discard_armour]

            while True:
                try:
                    reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=check)

                    if str(reaction.emoji) == keep_armour:
                        if not inventory.if_custom_exists(armour_object.item_id):
                            status = inventory.inventory_add_armour(armour_object)
                            await ctx.send(status)
                            break

                    if str(reaction.emoji) == discard_armour:
                        await ctx.send('You have discarded the item')
                        break
                except Exception as e:
                    print(e)

    @pandora_bot.command(name='tow', help="**!tow** to run a daily tower")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    # @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def tow(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(4):
            acc_object = inventory.CustomAccessory(command_user.player_id)

            gear_colours = inventory.get_gear_tier_colours(acc_object.item_base_tier)
            tier_colour = gear_colours[0]
            tier_emoji = gear_colours[1]

            item_title = f'{acc_object.item_name}'
            display_stars = ""
            damage_bonus = f'Base Damage: {str(acc_object.item_damage_min)} - {str(acc_object.item_damage_max)}'
            item_rolls = f'{acc_object.item_bonus_stat}'
            for x in range(acc_object.item_num_stars):
                display_stars += "<:estar1:1143756443967819906>"
            for y in range((5 - acc_object.item_num_stars)):
                display_stars += "<:ebstar2:1144826056222724106>"
            inquiry = "Would you like to keep or discard this item?"
            embed_msg = discord.Embed(colour=tier_colour,
                                      title=item_title,
                                      description=display_stars)
            embed_msg.add_field(name="", value=damage_bonus, inline=False)
            embed_msg.add_field(name="Item Rolls", value=item_rolls, inline=False)
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(acc_object.item_base_tier)} item found!', value=inquiry,
                                inline=False)
            embed_msg.set_thumbnail(url="https://i.ibb.co/FbhP60F/ringicon.png")
            message = await ctx.send(embed=embed_msg)

            keep_accessory = '💍'
            discard_accessory = '📵'

            await message.add_reaction(keep_accessory)
            await message.add_reaction(discard_accessory)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [keep_accessory, discard_accessory]

            while True:
                try:
                    reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=check)

                    if str(reaction.emoji) == keep_accessory:
                        if not inventory.if_custom_exists(acc_object.item_id):
                            status = inventory.inventory_add_accessory(acc_object)
                            await ctx.send(status)
                            break

                    if str(reaction.emoji) == discard_accessory:
                        await ctx.send('You have discarded the item')
                        break
                except Exception as e:
                    print(e)

    @pandora_bot.command(name='equip', help="**!equip [itemID]** to equip an item")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def equip(ctx, item_id):
        item_id = item_id.upper()
        item_type = item_id[0].upper()
        if inventory.if_custom_exists(item_id):
            match item_type:
                case 'W':
                    selected_item = inventory.read_weapon(item_id)
                    current_user = player.get_player_by_name(str(ctx.author))
                    if current_user.player_id == selected_item.player_owner:
                        response = current_user.equip(item_type, selected_item.item_id)
                    else:
                        response = "wrong item id"
                case 'A':
                    selected_item = inventory.read_armour(item_id)
                    current_user = player.get_player_by_name(str(ctx.author))
                    if current_user.player_id == selected_item.player_owner:
                        response = current_user.equip(item_type, selected_item.item_id)
                    else:
                        response = "wrong item id"
                case 'Y':
                    selected_item = inventory.read_accessory(item_id)
                    current_user = player.get_player_by_name(str(ctx.author))
                    if current_user.player_id == selected_item.player_owner:
                        response = current_user.equip(item_type, selected_item.item_id)
                    else:
                        response = "wrong item id"
                case 'wing':
                    response = "bad input"
                case 'crest':
                    response = "bad input"
                case _:
                    response = "Equippable item type not recognized"
        else:
            response = "wrong item id"

        await ctx.send(response)

    @pandora_bot.command(name='fort', help="**!fort** to challenge a fortress")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def fort(ctx):
        player_name = ctx.author
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(10):
            # initialize the boss post
            active_boss = bosses.spawn_boss(1)
            img_link = "https://i.ibb.co/0ngNM7h/castle.png"
            hp_bar_location = active_boss.draw_boss_hp(active_boss.boss_cHP / active_boss.boss_mHP)

            # build embedded message
            match active_boss.boss_tier:
                case 1:
                    tier_colour = discord.Colour.green()
                    life_emoji = "💚"
                case 2:
                    tier_colour = discord.Colour.blue()
                    life_emoji = "💙"
                case 3:
                    tier_colour = discord.Colour.purple()
                    life_emoji = "💜"
                case 4:
                    tier_colour = discord.Colour.gold()
                    life_emoji = "💛"
                case _:
                    tier_colour = discord.Colour.red()
                    life_emoji = "❤️"

            boss_title = f'{active_boss.boss_name}'
            boss_field = f'Tier {active_boss.boss_tier} {active_boss.boss_type}'
            boss_hp = f'{life_emoji}({active_boss.boss_cHP} / {active_boss.boss_mHP})'
            boss_weakness = f'Weakness: {active_boss.boss_typeweak}'
            boss_weakness += f'{active_boss.boss_eleweak_a}{active_boss.boss_eleweak_b}'
            embed_msg = discord.Embed(colour=tier_colour,
                                      title=boss_title,
                                      description="")
            embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
            embed_msg.add_field(name=boss_weakness, value="", inline=False)
            embed_msg.add_field(name="Current DPS: ", value="0 / min")
            embed_msg.set_image(url=img_link)
            # file = discord.File("boss_hp.jpg", filename="image.jpg")
            # embed_msg.set_thumbnail(url="attachment://image.jpg")
            sent_message = await ctx.send(embed=embed_msg)
            is_alive = True
            user = player.get_player_by_name(ctx.author)
            while is_alive:
                await asyncio.sleep(60)
                dps = user.get_player_damage(active_boss)
                active_boss.boss_cHP -= dps
                boss_hp = f'{life_emoji}({active_boss.boss_cHP} / {active_boss.boss_mHP})'
                if active_boss.calculate_hp():
                    embed_msg.remove_field(0)
                    embed_msg.insert_field_at(index=0, name=boss_field, value=boss_hp, inline=False)
                    embed_msg.remove_field(2)
                    dps_msg = str(dps) + " / min"
                    embed_msg.add_field(name="Current DPS: ", value=dps_msg)
                    await sent_message.edit(embed=embed_msg)
                else:
                    # update dead boss info
                    active_boss.boss_cHP = 0
                    embed_msg.remove_field(index=0)
                    embed_msg.remove_field(index=0)
                    embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
                    embed_msg.add_field(name=boss_weakness, value="", inline=False)
                    embed_msg.add_field(name="SLAIN", value="", inline=False)
                    embed_msg.add_field(name="Damage Rankings", value="", inline=False)
                    player_list = [ctx.author]
                    loot_output = loot.award_loot(active_boss.boss_type, active_boss.boss_tier, player_list)
                    embed_msg.add_field(name="Loot Awarded", value=loot_output, inline=False)
                    # embed_msg.set_image(url="slain image?")
                    await sent_message.edit(embed=embed_msg)
                    is_alive = False

    @pandora_bot.command(name='quest', help="**!quest** to start the story quest")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def quest(ctx):
        # quest progression
        sparkle = '✨'
        story_response = chatcommands.get_command_text("!story1")
        sent_message = await ctx.send(content=str(story_response))
        await sent_message.add_reaction(sparkle)

        def box_open(reaction, user):
            return user == ctx.author and str(reaction.emoji) == sparkle

        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=box_open)
                if str(reaction.emoji) == sparkle:
                    status = chatcommands.get_command_text('story2')
                    await ctx.send(status)
                    break
            except Exception as e:
                print(e)

    @pandora_bot.command(name='gear', help="**!inv** to display your gear inventory")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def gear(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        player_inventory = f'{player_object.player_name}\'s Inventory:\n'
        player_inventory += inventory.display_cinventory(player_object.player_id)
        await ctx.send(player_inventory)

    @pandora_bot.command(name='stamina', help="**!stam** to display your stamina total")
    async def gear(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        output = f'{player_object.player_name}\'s stamina: '
        output += str(player_object.player_stamina)
        await ctx.send(output)

    @pandora_bot.command(name='admin', help="**!admin** inputs")
    async def admin(ctx, backdoor, value):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        if backdoor == "stamina_hack":
            player_object.add_stamina(value)

    @pandora_bot.command(name='item', help="**!item** to display your item details")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def item(ctx, item_id):
        message = ""
        user = ctx.author
        player_object = player.get_player_by_name(user)
        item_type = item_id[0].upper()
        if inventory.if_custom_exists(item_id):
            match item_type:
                case 'W':
                    selected_item = inventory.read_weapon(item_id)
                    if player_object.player_id == selected_item.player_owner:
                        gear_colours = inventory.get_gear_tier_colours(selected_item.item_base_tier)
                        tier_colour = gear_colours[0]

                        item_title = f'{selected_item.item_name}'
                        display_stars = ""
                        damage_bonus = f'Base Damage: {str(selected_item.item_damage_min)}'
                        damage_bonus += f' - {str(selected_item.item_damage_max)}'
                        item_rolls = f'Base Attack Speed {selected_item.item_bonus_stat}/min'

                        for x in range(selected_item.item_num_stars):
                            display_stars += "<:estar1:1143756443967819906>"
                        for y in range((5 - selected_item.item_num_stars)):
                            display_stars += "<:ebstar2:1144826056222724106>"

                        item_types = f'{selected_item.item_damage_type}'
                        for x in selected_item.item_elements:
                            item_types += f'{x}'

                        embed_msg = discord.Embed(colour=tier_colour,
                                                  title=item_title,
                                                  description=display_stars)
                        embed_msg.add_field(name=item_types, value=damage_bonus, inline=False)
                        embed_msg.add_field(name="Item Rolls", value=item_rolls, inline=False)
                        embed_msg.set_thumbnail(url="https://i.ibb.co/ygGCRnc/sworddefaulticon.png")

                        await ctx.send(embed=embed_msg)
                    else:
                        message = "wrong item id"
                        await ctx.send(message)
                case 'A':
                    selected_item = inventory.read_armour(item_id)
                    if player_object.player_id == selected_item.player_owner:
                        gear_colours = inventory.get_gear_tier_colours(selected_item.item_base_tier)
                        tier_colour = gear_colours[0]

                        item_title = f'{selected_item.item_name}'
                        display_stars = ""
                        damage_bonus = f'Base Damage: {str(selected_item.item_damage_min)}'
                        damage_bonus += f' - {str(selected_item.item_damage_max)}'
                        item_rolls = f'Base Damage Mitigation {selected_item.item_bonus_stat}%'

                        for x in range(selected_item.item_num_stars):
                            display_stars += "<:estar1:1143756443967819906>"
                        for y in range((5 - selected_item.item_num_stars)):
                            display_stars += "<:ebstar2:1144826056222724106>"

                        item_types = f'{selected_item.item_damage_type}'
                        for x in selected_item.item_elements:
                            item_types += f'{x}'

                        embed_msg = discord.Embed(colour=tier_colour,
                                                  title=item_title,
                                                  description=display_stars)
                        embed_msg.add_field(name=item_types, value=damage_bonus, inline=False)
                        embed_msg.add_field(name="Item Rolls", value=item_rolls, inline=False)
                        embed_msg.set_thumbnail(url="https://i.ibb.co/ygGCRnc/sworddefaulticon.png")

                        await ctx.send(embed=embed_msg)
                    else:
                        message = "wrong item id"
                        await ctx.send(message)
                case 'Y':
                    selected_item = inventory.read_accessory(item_id)
                    if player_object.player_id == selected_item.player_owner:
                        gear_colours = inventory.get_gear_tier_colours(selected_item.item_base_tier)
                        tier_colour = gear_colours[0]

                        item_title = f'{selected_item.item_name}'
                        display_stars = ""
                        damage_bonus = f'Base Damage: {str(selected_item.item_damage_min)}'
                        damage_bonus += f' - {str(selected_item.item_damage_max)}'
                        item_rolls = f'{selected_item.item_bonus_stat}'

                        for x in range(selected_item.item_num_stars):
                            display_stars += "<:estar1:1143756443967819906>"
                        for y in range((5 - selected_item.item_num_stars)):
                            display_stars += "<:ebstar2:1144826056222724106>"

                        item_types = f'{selected_item.item_damage_type}'
                        for x in selected_item.item_elements:
                            item_types += f'{x}'

                        embed_msg = discord.Embed(colour=tier_colour,
                                                  title=item_title,
                                                  description=display_stars)
                        embed_msg.add_field(name=item_types, value=damage_bonus, inline=False)
                        embed_msg.add_field(name="Item Rolls", value=item_rolls, inline=False)
                        embed_msg.set_thumbnail(url="https://i.ibb.co/ygGCRnc/sworddefaulticon.png")

                        await ctx.send(embed=embed_msg)
                    else:
                        message = "wrong item id"
                        await ctx.send(message)
                case 'G':
                    message = "bad input"
                    await ctx.send(message)
                case 'C':
                    message = "bad input"
                    await ctx.send(message)
                case _:
                    message = "bad input: item type not recognized"
                    await ctx.send(message)

    pandora_bot.run(TOKEN)
