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
from discord.ui import Button, View, Select


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
            total_player_damage = 1000
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
            embed_msg = weapon_object.create_citem_embed()

            gear_colours = inventory.get_gear_tier_colours(weapon_object.item_base_tier)
            tier_emoji = gear_colours[1]

            inquiry = "Would you like to keep or discard this item?"
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(weapon_object.item_base_tier)} item found!', value=inquiry, inline=False)
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
                            status = inventory.inventory_add_custom_item(weapon_object)
                            await ctx.send(status)
                            break

                    if str(reaction.emoji) == discard_weapon:
                        await ctx.send('You have discarded the item')
                        break
                except Exception as e:
                    print(e)
        else:
            await ctx.send('Not enough !stamina')

    @pandora_bot.command(name='dung', help="**!dung** to run a daily dungeon")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    # @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def dung(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(4):
            armour_object = inventory.CustomArmour(command_user.player_id)
            embed_msg = armour_object.create_citem_embed()

            gear_colours = inventory.get_gear_tier_colours(armour_object.item_base_tier)
            tier_emoji = gear_colours[1]

            inquiry = "Would you like to keep or discard this item?"
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(armour_object.item_base_tier)} item found!', value=inquiry,
                                inline=False)
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
                            status = inventory.inventory_add_custom_item(armour_object)
                            await ctx.send(status)
                            break

                    if str(reaction.emoji) == discard_armour:
                        await ctx.send('You have discarded the item')
                        break
                except Exception as e:
                    print(e)
        else:
            await ctx.send('Not enough !stamina')

    @pandora_bot.command(name='tow', help="**!tow** to run a daily tower")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    # @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def tow(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(4):
            acc_object = inventory.CustomAccessory(command_user.player_id)
            embed_msg = acc_object.create_citem_embed()
            gear_colours = inventory.get_gear_tier_colours(acc_object.item_base_tier)
            tier_emoji = gear_colours[1]

            inquiry = "Would you like to keep or discard this item?"
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(acc_object.item_base_tier)} item found!', value=inquiry,
                                inline=False)
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
                            status = inventory.inventory_add_custom_item(acc_object)
                            await ctx.send(status)
                            break

                    if str(reaction.emoji) == discard_accessory:
                        await ctx.send('You have discarded the item')
                        break
                except Exception as e:
                    print(e)
        else:
            await ctx.send('Not enough !stamina')

    @pandora_bot.command(name='equip', help="**!equip [itemID]** to equip an item")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def equip(ctx, item_id):
        item_id = item_id.upper()
        item_identifier = item_id[0].upper()
        if inventory.if_custom_exists(item_id):
            selected_item = inventory.read_custom_item(item_id)
            current_user = player.get_player_by_name(str(ctx.author))
            if current_user.player_id == selected_item.player_owner:
                response = current_user.equip(item_identifier, selected_item.item_id)
            else:
                response = "wrong item id"
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
                    boss_hp = f'{life_emoji}({active_boss.boss_cHP} / {active_boss.boss_mHP})'
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
        box = "<a:eshadow2:1141653468965257216>"
        story_response = chatcommands.get_command_text("!story1a")
        quest_title = "Story: A New Beginning!"
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title=quest_title,
                                      description=story_response)
        sent_message = await ctx.send(embed = embed_msg)
        await sent_message.add_reaction(box)

        def box_open(reaction, user):
            return user == ctx.author and str(reaction.emoji) == box

        while True:
            try:
                reaction, user = await pandora_bot.wait_for("reaction_add", timeout=60, check=box_open)
                if str(reaction.emoji) == box:
                    story_response = chatcommands.get_command_text('!story1b')
                    quest_title = "Story: Unchained!"
                    embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                              title=quest_title,
                                              description=story_response)
                    quest_title = chatcommands.get_command_text('!quest1')
                    embed_msg.add_field(name="Quest Acquired!", value=quest_title)
                    await ctx.send(embed=embed_msg)
                    break
            except Exception as e:
                print(e)

    @pandora_bot.command(name='gear', help="**!inv** to display your equipped gear")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def gear(ctx):
        user = player.get_player_by_name(str(ctx.author))
        user.get_equipped()
        equipped_w = inventory.read_custom_item(user.equipped_weapon)
        equipped_a = inventory.read_custom_item(user.equipped_armour)
        equipped_y = inventory.read_custom_item(user.equipped_acc)
        # equipped_g = inventory.read_custom_item(user.equipped_wing)
        # equipped_c = inventory.read_custom_item(user.equipped_crest)
        # gear_list = [equipped_w, equipped_a, equipped_y, equipped_g, equipped_c]
        gear_list = [equipped_w, equipped_a, equipped_y]

        gear_title = f'{user.player_name}\'s Equipped Gear'
        embed_msg = discord.Embed(colour=discord.Colour.red(),
                                  title=gear_title,
                                  description="")
        for x in gear_list:
            embed_msg = x.create_citem_embed()
            item_info = f'Item ID: {x.item_id}'
            embed_msg.add_field(name=item_info, value="", inline=False)
            await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='inv', help="**!inv** to display your gear and item inventory")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def inv(ctx):
        user = ctx.author

        player_object = player.get_player_by_name(user)
        player_inventory = f'{player_object.player_name}\'s Equipment:\n'
        player_inventory += inventory.display_cinventory(player_object.player_id)
        await ctx.send(player_inventory)

        player_object = player.get_player_by_name(user)
        player_inventory = f'{player_object.player_name}\'s Inventory:\n'
        player_inventory += inventory.display_binventory(player_object.player_id)
        await ctx.send(player_inventory)

    @pandora_bot.command(name='stamina', help="**!stam** to display your stamina total")
    async def gear(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        output = f'<:estamina:1145534039684562994> {player_object.player_name}\'s stamina: '
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
        user = ctx.author
        player_object = player.get_player_by_name(user)
        item_identifier = item_id.upper()
        if inventory.if_custom_exists(item_identifier):
            selected_item = inventory.read_custom_item(item_identifier)
            if player_object.player_id == selected_item.player_owner:
                embed_msg = selected_item.create_citem_embed()
                await ctx.send(embed=embed_msg)
            else:
                message = "wrong item id"
                await ctx.send(message)
        else:
            message = "wrong item id"
            await ctx.send(message)

    @pandora_bot.command(name='who', help="**!who [NewUsername]** to set your username")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def who(ctx, new_username):
        existing_user = player.get_player_by_name(ctx.author)
        if player.check_username(new_username):
            existing_user.update_username(new_username)
            message = f'Got it! I\'ll call you {existing_user.player_username} from now on!'
        else:
            message = f'Sorry that username is taken.'
        await ctx.send(message)

    @pandora_bot.command(name='forge', help="**!forge** to enter the celestial forge")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def forge(ctx):

        selected = 1

        user = ctx.author
        player_object = player.get_player_by_name(user)
        player_object.get_equipped()
        view = View(timeout=60)
        match selected:
            case 1:
                selected_item = inventory.read_custom_item(player_object.equipped_weapon)
            case 2:
                selected_item = inventory.read_custom_item(player_object.equipped_armour)
            case _:
                selected_item = inventory.read_custom_item(player_object.equipped_acc)

        embed_msg = selected_item.create_citem_embed()

        # Build dropdown menu
        forge_select = Select(
            placeholder="Select crafting method!",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Enhance", description="Enhancement!",),
                discord.SelectOption(
                    emoji="<:eore:1145534835507593236>", label="Upgrade", description="Upgrade!"),
                discord.SelectOption(
                    emoji="<:esoul:1145520258241806466>", label="Bestow", description="Bestow!"),
                discord.SelectOption(
                    emoji="<:ehammer:1145520259248427069>", label="Open", description="Open!"),
                discord.SelectOption(
                    emoji="<a:ematrix:1145520262268325919>", label="Tune", description="Tuning!"),
                discord.SelectOption(
                    emoji="<a:eorigin:1145520263954440313>", label="Implant", description="Implant Origin!"),
                discord.SelectOption(
                    emoji="<a:evoid:1145520260573827134>",label="Voidforge", description="Voidforge!")
            ]
        )

        # Build view
        view.add_item(forge_select)
        view.message = embed_msg

        # Assign response
        async def button1_callback(interaction):
            match forge_select.values[0]:
                case "Enhance":
                    result = inventory.enhance_item(player_object, selected_item)
                case "Upgrade":
                    item_id = ["I4", "I5", "I6"]
                    result = inventory.enhance_item(player_object, selected_item)
                case "Bestow":
                    item_id = ["I7", "I8", "I9"]
                    result = inventory.enhance_item(player_object, selected_item)
                case "Open":
                    item_id = ["I10", "I11", "I12"]
                    result = inventory.enhance_item(player_object, selected_item)
                case "Imbue":
                    item_id = ["I13", "I14", "I15"]
                    result = inventory.enhance_item(player_object, selected_item)
                case "Tune":
                    item_id = ["I16", "I17", "I18", "I19"]
                    result = inventory.enhance_item(player_object, selected_item)
                case "Implant":
                    item_id = ["I20"]
                    result = inventory.enhance_item(player_object, selected_item)
                case _:
                    item_id = ["I21"]
                    result = inventory.enhance_item(player_object, selected_item)
            if result:
                outcome = "Success!"
            else:
                outcome = "Failed!"
            new_embed_msg = selected_item.create_citem_embed()
            new_embed_msg.add_field(name=outcome, value="", inline=False)
            await interaction.response.edit_message(embed=new_embed_msg)

        async def button2_callback(interaction):

            await interaction.response.edit_message(embed=embed_msg)

        async def button3_callback(interaction):
            await interaction.response.edit_message(embed=embed_msg)
            # view.timeout = True

        async def dropdown_callback(interaction):
            match forge_select.values[0]:
                case "Enhance":
                    button_1 = Button(label="Enhance",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Enhance All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')
                case "Upgrade":
                    button_1 = Button(label="Upgrade",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Upgrade All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')
                case "Bestow":
                    button_1 = Button(label="Bestow",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Bestow All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')
                case "Imbue":
                    button_1 = Button(label="Imbue",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Imbue All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')
                case "Open":
                    button_1 = Button(label="Open",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Open All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')
                case "Tune":
                    button_1 = Button(label="Tune",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Tune All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')
                case "Implant":
                    button_1 = Button(label="Implant",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Implant All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')
                case _:
                    button_1 = Button(label="Voidforge",
                                      style=discord.ButtonStyle.success, emoji="⬆️", custom_id='single')
                    button_2 = Button(label="Voidforge All",
                                      style=discord.ButtonStyle.blurple, emoji="⏫", custom_id='all')

            button_3 = Button(label="Cancel",
                              style=discord.ButtonStyle.red, emoji="✖️", custom_id='cancel')
            view.add_item(button_1)
            view.add_item(button_2)
            view.add_item(button_3)
            button_1.callback = button1_callback
            button_2.callback = button2_callback
            button_3.callback = button3_callback
            await interaction.response.edit_message(embed=embed_msg, view=view)
            forge_select.disabled = True

        forge_select.callback = dropdown_callback

        # Display the view
        view.embed = await ctx.send(embed=embed_msg, view=view)

    pandora_bot.run(TOKEN)
