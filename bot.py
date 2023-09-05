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
from discord.ui import Button, View
import csv


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
            df.loc[df['stamina'] >= 1998, 'stamina'] = 2000
            df.loc[df['stamina'] < 1998, 'stamina'] = df['stamina'] + 2
            df.to_csv(filename, index=False)

    @pandora_bot.event
    async def timed_task(duration_seconds, channel_id, ctx):

        # initialize the boss post
        active_boss = bosses.spawn_boss(2)
        active_boss.set_boss_lvl(1)
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
        boss_field = f'Tier {active_boss.boss_tier} {active_boss.boss_type} - Level: {active_boss.boss_lvl}'
        boss_hp = f'{life_emoji} ({active_boss.boss_cHP} / {active_boss.boss_mHP})'
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
                boss_hp = f'{life_emoji} ({active_boss.boss_cHP} / {active_boss.boss_mHP})'
                embed_msg.remove_field(index=0)
                embed_msg.insert_field_at(index=0, name=boss_field, value=boss_hp, inline=False)
                await sent_message.edit(embed=embed_msg)
            else:
                # update dead boss info
                active_boss.boss_cHP = 0
                boss_hp = f'{life_emoji} ({active_boss.boss_cHP} / {active_boss.boss_mHP})'
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
                boss_field = f'Tier {active_boss.boss_tier} {active_boss.boss_type} - Level: {active_boss.boss_lvl}'
                boss_hp = f'{life_emoji} ({active_boss.boss_cHP} / {active_boss.boss_mHP})'
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
        if command_user.spend_stamina(25):
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
    @commands.max_concurrency(25, per=commands.BucketType.default, wait=False)
    # @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def dung(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(25):
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
    @commands.max_concurrency(25, per=commands.BucketType.default, wait=False)
    # @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def tow(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(25):
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
    @commands.max_concurrency(25, per=commands.BucketType.default, wait=False)
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
        if command_user.spend_stamina(50):
            # initialize the boss post
            active_boss = bosses.spawn_boss(1)
            active_boss.set_boss_lvl(command_user.player_lvl)
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
            boss_field = f'Tier {active_boss.boss_tier} {active_boss.boss_type} - Level {active_boss.boss_lvl}'
            boss_hp = f'{life_emoji} ({active_boss.boss_cHP} / {active_boss.boss_mHP})'
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
                boss_hp = f'{life_emoji} ({active_boss.boss_cHP} / {active_boss.boss_mHP})'
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
                    embed_msg.remove_field(index=0)
                    dps_msg = str(dps) + " / min"
                    embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
                    embed_msg.add_field(name=boss_weakness, value="", inline=False)
                    embed_msg.add_field(name="Current DPS: ", value=dps_msg)
                    embed_msg.add_field(name="SLAIN", value="", inline=False)
                    player_list = [user.player_name]
                    exp_amount = active_boss.boss_tier * (1 + active_boss.boss_lvl) * 100
                    loot_output = loot.award_loot(active_boss.boss_type, active_boss.boss_tier, player_list, exp_amount)
                    for counter, loot_section in enumerate(loot_output):
                        temp_player = player.get_player_by_name(str(player_list[counter]))
                        loot_msg = f'{temp_player.player_username} received:'
                        embed_msg.add_field(name=loot_msg, value=loot_section, inline=False)
                    # embed_msg.set_image(url="slain image?")
                    await sent_message.edit(embed=embed_msg)
                    is_alive = False
        else:
            await ctx.send("Not enough stamina.")

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
        gear_list = []
        if user.equipped_weapon != "":
            equipped_w = inventory.read_custom_item(user.equipped_weapon)
            gear_list.append(equipped_w)
        if user.equipped_armour != "":
            equipped_a = inventory.read_custom_item(user.equipped_armour)
            gear_list.append(equipped_a)
        if user.equipped_acc != "":
            equipped_y = inventory.read_custom_item(user.equipped_acc)
            gear_list.append(equipped_y)
        # equipped_g = inventory.read_custom_item(user.equipped_wing)
        # equipped_c = inventory.read_custom_item(user.equipped_crest)
        # gear_list = [equipped_w, equipped_a, equipped_y, equipped_g, equipped_c]

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
        player_inventory = f'{player_object.player_username}\'s Equipment:\n'
        player_inventory += inventory.display_cinventory(player_object.player_id)
        await ctx.send(player_inventory)

        player_object = player.get_player_by_name(user)
        player_inventory = f'{player_object.player_username}\'s Inventory:\n'
        player_inventory += inventory.display_binventory(player_object.player_id)
        await ctx.send(player_inventory)

    @pandora_bot.command(name='stamina', help="**!stamina** to display your stamina total")
    async def gear(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        output = f'<:estamina:1145534039684562994> {player_object.player_username}\'s stamina: '
        output += str(player_object.player_stamina)
        await ctx.send(output)

    @pandora_bot.command(name='profile', help="**!profile** to display your profile")
    async def profile(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)

        echelon_colour = inventory.get_gear_tier_colours(player_object.player_echelon)
        stamina = f'<:estamina:1145534039684562994> {player_object.player_username}\'s stamina: '
        stamina += str(player_object.player_stamina)
        exp = f'Level: {player_object.player_lvl} Exp: ({player_object.player_exp} / '
        exp += f'{player.get_max_exp(player_object.player_lvl)})'
        id_msg = f'User ID: {player_object.player_id}'

        embed_msg = discord.Embed(colour=echelon_colour[0],
                                  title=player_object.player_username,
                                  description=id_msg)
        embed_msg.add_field(name=exp, value=stamina, inline=False)
        # embed_msg.set_thumbnail(url="")
        await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='admin', help="**!admin** inputs")
    async def admin(ctx, backdoor, value):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        if backdoor == "stamina_hack":
            player_object.add_stamina(value)
        if backdoor == "item_hack":
            inventory.update_stock(player_object, value, 10)
        if backdoor == "item_hack_all":
            filename = "itemlist.csv"
            with (open(filename, 'r') as f):
                for line in csv.DictReader(f):
                    inventory.update_stock(player_object, str(line['item_id']), int(value))

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

    class ForgeView(discord.ui.View):
        def __init__(self, player_object, selected_item):
            super().__init__(timeout=600)
            self.selected_item = selected_item
            self.player_object = player_object
            self.values = None
            self.button_label = []
            self.button_emoji = []
            self.num_buttons = 0

        @discord.ui.select(
            placeholder="Select crafting method!",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Enhance", description="Enhancement!"),
                discord.SelectOption(
                    emoji="<:eore:1145534835507593236>", label="Upgrade", description="Upgrade!"),
                discord.SelectOption(
                    emoji="<:esoul:1145520258241806466>", label="Bestow", description="Bestow!"),
                discord.SelectOption(
                    emoji="<:ehammer:1145520259248427069>", label="Open", description="Open!"),
                discord.SelectOption(
                    emoji="<a:ematrix:1145520262268325919>", label="Tune", description="Tuning!"),
                discord.SelectOption(
                    emoji="<a:ematrix:1145520262268325919>", label="Imbue", description="Imbue!"),
                discord.SelectOption(
                    emoji="<a:eorigin:1145520263954440313>", label="Implant", description="Implant Origin!"),
                discord.SelectOption(
                    emoji="<a:evoid:1145520260573827134>",label="Voidforge", description="Voidforge!")
            ]
        )
        async def forge_callback(self, interaction: discord.Interaction, forge_select: discord.ui.Select):
            match forge_select.values[0]:
                case "Enhance":
                    self.button_emoji.append(loot.get_loot_emoji("I1"))
                    self.button_emoji.append(loot.get_loot_emoji("I2"))
                    self.button_emoji.append(loot.get_loot_emoji("I3"))
                    self.num_buttons = 4
                case "Upgrade":
                    self.button_emoji.append(loot.get_loot_emoji("I4"))
                    self.button_emoji.append(loot.get_loot_emoji("I5"))
                    self.button_emoji.append(loot.get_loot_emoji("I6"))
                    self.num_buttons = 4
                case "Bestow":
                    self.button_emoji.append(loot.get_loot_emoji("I7"))
                    self.button_emoji.append(loot.get_loot_emoji("I8"))
                    self.button_emoji.append(loot.get_loot_emoji("I9"))
                    self.num_buttons = 4
                case "Open":
                    self.button_emoji.append(loot.get_loot_emoji("I10"))
                    self.button_emoji.append(loot.get_loot_emoji("I11"))
                    self.button_emoji.append(loot.get_loot_emoji("I12"))
                    self.num_buttons = 4
                case "Imbue":
                    self.button_emoji.append(loot.get_loot_emoji("I13"))
                    self.button_emoji.append(loot.get_loot_emoji("I14"))
                    self.button_emoji.append(loot.get_loot_emoji("I15"))
                    self.num_buttons = 4
                case "Tune":
                    self.button_emoji.append(loot.get_loot_emoji("I16"))
                    self.button_emoji.append(loot.get_loot_emoji("I17"))
                    self.button_emoji.append(loot.get_loot_emoji("I18"))
                    self.num_buttons = 4
                case "Implant":
                    self.button_emoji.append(loot.get_loot_emoji("I20"))
                    self.num_buttons = 2
                case "Voidforge":
                    self.button_emoji.append(loot.get_loot_emoji("I21"))
                    self.num_buttons = 2
                case _:
                    self.num_buttons = 0

            # Assign response
            async def first_button_callback(button_interaction: discord.Interaction):
                new_embed_msg = run_button(1)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            async def second_button_callback(button_interaction: discord.Interaction):
                new_embed_msg = run_button(2)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            async def third_button_callback(button_interaction: discord.Interaction):
                new_embed_msg = run_button(3)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            def run_button(selected_button):
                method = forge_select.values[0]
                condition = self.button_label[selected_button]
                result = inventory.craft_item(self.player_object, self.selected_item, condition, method)
                if result == "0":
                    outcome = "Failed!"
                elif result == "1":
                    outcome = "Success!"
                elif result == "3":
                    outcome = "Cannot upgrade further"
                elif result == "4":
                    outcome = "Item not ready for upgrade"
                else:
                    outcome = f"Out of Stock: {loot.get_loot_emoji(result)}"
                new_embed_msg = self.selected_item.create_citem_embed()
                new_embed_msg.add_field(name=outcome, value="", inline=False)
                return new_embed_msg

            async def button_multi_callback(button_interaction: discord.Interaction):
                result = "0"
                overall = "All failed"
                outcome = ""
                method = forge_select.values[0]
                match method:
                    case "Enhance":
                        item_id_list = ["I1", "I2", "I3"]
                    case "Upgrade":
                        item_id_list = ["I4", "I5", "I6"]
                    case "Bestow":
                        item_id_list = ["I7", "I8", "I9"]
                    case "Open":
                        item_id_list = ["I10", "I11", "I12"]
                    case "Imbue":
                        item_id_list = ["I13", "I14", "I15"]
                    case "Tune":
                        item_id_list = ["I16", "I17", "I18"]
                    case "Implant":
                        item_id_list = ["I20"]
                    case "Voidforge":
                        item_id_list = ["I21"]
                    case _:
                        item_id_list = ["error"]
                for x in item_id_list:
                    running = True
                    while running:
                        result = inventory.craft_item(self.player_object, self.selected_item, x, method)
                        if result != "0" and result != "1":
                            running = False
                        elif result == "1":
                            if overall == "Success!":
                                overall = "!!MULTI-SUCCESS!!"
                            elif overall != "!!MULTI-SUCCESS!!":
                                overall = "Success!"
                    if result == "3":
                        outcome = "Cannot upgrade further"
                        break
                    else:
                        outcome = f"Out of Stock: {loot.get_loot_emoji(result)}"
                new_embed_msg = self.selected_item.create_citem_embed()
                new_embed_msg.add_field(name=overall, value=outcome, inline=False)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            async def button_cancel_callback(button_interaction: discord.Interaction):
                # cancel here
                await button_interaction.response.edit_message(view=None)

            self.button_label.append(f"T1 {forge_select.values[0]}")
            self.button_label.append(f"T2 {forge_select.values[0]}")
            self.button_label.append(f"T3 {forge_select.values[0]}")
            self.button_label.append(f"Multi {forge_select.values[0]}")
            button_1 = Button(label=self.button_label[0],
                              style=discord.ButtonStyle.success, emoji=self.button_emoji[0], custom_id="1")
            button_all = Button(label=self.button_label[3],
                                style=discord.ButtonStyle.blurple, emoji="⬆️", custom_id="4")
            button_cancel = Button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
            self.add_item(button_1)
            if self.num_buttons == 4:
                button_2 = Button(label=self.button_label[1],
                                  style=discord.ButtonStyle.success, emoji=self.button_emoji[1], custom_id="2")
                button_3 = Button(label=self.button_label[2],
                                  style=discord.ButtonStyle.success, emoji=self.button_emoji[2], custom_id="3")
                self.add_item(button_2)
                self.add_item(button_3)
                button_2.callback = second_button_callback
                button_3.callback = third_button_callback
            self.add_item(button_all)
            self.add_item(button_cancel)
            button_1.callback = first_button_callback
            button_all.callback = button_multi_callback
            button_cancel.callback = button_cancel_callback
            forge_select.disabled = True
            await interaction.response.edit_message(view=self)

    class SelectView(discord.ui.View):
        def __init__(self, player_object):
            super().__init__(timeout=600)
            self.player_object = player_object
            self.value = None

        @discord.ui.select(
            placeholder="Select crafting base!",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Weapon", description="Equipped Weapon"),
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Armour", description="Equipped Armour"),
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Accessory", description="Equipped Accessory")
                # discord.SelectOption(
                    # emoji="<a:eenergy:1145534127349706772>", label="Wing", description="Equipped Wing"),
                # discord.SelectOption(
                    # emoji="<a:eenergy:1145534127349706772>", label="Crest", description="Equipped Paragon Crest")
            ]
        )
        async def select_callback(self, interaction: discord.Interaction, item_select: discord.ui.Select):
            error_msg = ""
            match item_select.values[0]:
                case "Weapon":
                    if self.player_object.equipped_weapon != "":
                        self.selected_item = inventory.read_custom_item(self.player_object.equipped_weapon)
                    else:
                        error_msg = "Not equipped"
                case "Armour":
                    if self.player_object.equipped_armour != "":
                        self.selected_item = inventory.read_custom_item(self.player_object.equipped_armour)
                    else:
                        error_msg = "Not equipped"
                case "Accessory":
                    if self.player_object.equipped_acc != "":
                        self.selected_item = inventory.read_custom_item(self.player_object.equipped_acc)
                    else:
                        error_msg = "Not equipped"
                case _:
                    error_msg = "Error"
            if error_msg == "":
                embed_msg = self.selected_item.create_citem_embed()
                new_view = ForgeView(self.player_object, self.selected_item)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
            else:
                await interaction.response.edit_message(view=None)

    @pandora_bot.command(name='forge', help="**!forge** to enter the celestial forge")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def forge(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        player_object.get_equipped()
        embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                  title="Pandora's Celestial Forge",
                                  description="Let me know what you'd like me to upgrade today!")
        embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
        view = SelectView(player_object)
        view.embed = await ctx.send(embed=embed_msg, view=view)

    pandora_bot.run(TOKEN)
