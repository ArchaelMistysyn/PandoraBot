import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio

import explore
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
import menus


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

    class RaidView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Join the raid!", style=discord.ButtonStyle.success, emoji="⚔️")
        async def raid_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
            clicked_by = player.get_player_by_name(str(interaction.user))
            outcome = clicked_by.player_username
            outcome += bosses.add_participating_player(clicked_by.player_id)

            await interaction.response.send_message(outcome)

    @pandora_bot.event
    async def timed_task(duration_seconds, channel_id, ctx):

        # initialize the boss post
        active_boss = bosses.spawn_boss(2)
        active_boss.set_boss_lvl(1)
        is_alive = True
        embed_msg = active_boss.create_boss_embed(0, is_alive)
        raid_button = RaidView()
        sent_message = await ctx.send(embed=embed_msg, view=raid_button)
        active_boss.message_id = sent_message.id
        while True:
            await asyncio.sleep(duration_seconds)
            player_list = bosses.get_players()
            dps = 0
            for x in player_list:
                temp_user = player.get_player_by_id(int(x))
                player_dps, critical_type = damagecalc.get_player_damage(temp_user, active_boss)
                bosses.update_player_damage(int(x), player_dps)
                dps += player_dps
            active_boss.boss_cHP -= dps
            if active_boss.calculate_hp():
                embed_msg = active_boss.create_boss_embed(dps, is_alive)
                await sent_message.edit(embed=embed_msg)
            else:
                # update dead boss info
                is_alive = False
                embed_msg = active_boss.create_boss_embed(dps, is_alive)
                # embed_msg.set_image(url="slain image?")
                damage_list = bosses.get_damage_list()
                embed_msg.add_field(name="SLAIN", value=damage_list, inline=False)
                exp_amount = active_boss.boss_tier * (1 + active_boss.boss_lvl) * 100
                loot_output = loot.award_loot(active_boss.boss_type, active_boss.boss_tier, player_list, exp_amount)
                for counter, loot_section in enumerate(loot_output):
                    temp_player = player.get_player_by_id(player_list[counter])
                    loot_msg = f'{temp_player.player_username} received:'
                    embed_msg.add_field(name=loot_msg, value=loot_section, inline=False)
                await sent_message.edit(embed=embed_msg)
                # spawn a new boss
                random_number = random.randint(1, 2)
                new_boss_type = 2
                match active_boss.boss_type:
                    case "Dragon":
                        if random_number == 2:
                            new_boss_type = 3
                    case "Primordial":
                        new_boss_type = 2
                    case _:
                        error = "this boss should not be anything else"

                active_boss = bosses.spawn_boss(new_boss_type)
                active_boss.set_boss_lvl(1)
                bosses.clear_list()
                player_list.clear()
                is_alive = True
                embed_msg = active_boss.create_boss_embed(0, is_alive)
                sent_message = await ctx.send(embed=embed_msg, view=raid_button)
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

    @pandora_bot.command(name='explore', help="**!explore** to go on an an exploration")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def adventure(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        command_user.get_equipped()
        command_user.get_player_multipliers(-1, -1)
        if command_user.spend_stamina(25):
            starting_room = explore.generate_new_room(command_user)
            embed_msg = starting_room.embed
            starting_view = starting_room.room_view
            await ctx.send(embed=embed_msg, view=starting_view)
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

    @pandora_bot.command(name='inlay', help="**!equip [itemID]** to equip an item")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def equip(ctx, item_id):
        item_id = item_id.upper()
        if inventory.if_custom_exists(item_id):
            selected_item = inventory.read_custom_item(item_id)
            current_user = player.get_player_by_name(str(ctx.author))
            if current_user.player_id == selected_item.player_owner:
                embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                          title="Inlay Gem",
                                          description="Let me know what item you'd like to inlay this gem into!")
                embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                view = menus.InlaySelectView(current_user, selected_item.item_id)
                view.embed = await ctx.send(embed=embed_msg, view=view)

            else:
                response = "wrong item id"
                await ctx.send(response)
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
            is_alive = True
            embed_msg = active_boss.create_boss_embed(0, is_alive)
            sent_message = await ctx.send(embed=embed_msg)
            user = player.get_player_by_name(ctx.author)
            while is_alive:
                await asyncio.sleep(60)
                dps, critical_type = damagecalc.get_player_damage(user, active_boss)
                active_boss.boss_cHP -= dps
                if active_boss.calculate_hp():
                    embed_msg = active_boss.create_boss_embed(dps, is_alive)
                    await sent_message.edit(embed=embed_msg)
                else:
                    # update dead boss info
                    is_alive = False
                    active_boss.boss_cHP = 0
                    embed_msg = active_boss.create_boss_embed(dps, is_alive)
                    # embed_msg.set_image(url="slain image?")
                    embed_msg.add_field(name="SLAIN", value="", inline=False)
                    player_list = [user.player_id]
                    exp_amount = active_boss.boss_tier * (1 + active_boss.boss_lvl) * 100
                    loot_output = loot.award_loot(active_boss.boss_type, active_boss.boss_tier, player_list, exp_amount)
                    for counter, loot_section in enumerate(loot_output):
                        temp_player = player.get_player_by_id(player_list[counter])
                        loot_msg = f'{temp_player.player_username} received:'
                        embed_msg.add_field(name=loot_msg, value=loot_section, inline=False)

                    await sent_message.edit(embed=embed_msg)

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
        if user.equipped_wing != "":
            equipped_g = inventory.read_custom_item(user.equipped_wing)
            gear_list.append(equipped_g)
        if user.equipped_crest != "":
            equipped_c = inventory.read_custom_item(user.equipped_crest)
            gear_list.append(equipped_c)

        for x in gear_list:
            embed_msg = x.create_citem_embed()
            item_info = f'Item ID: {x.item_id}'
            embed_msg.add_field(name=item_info, value="", inline=False)
            await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='inv', help="**!inv** to display your gear and item inventory")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def inv(ctx):
        user = player.get_player_by_name(str(ctx.author))
        inventory_view = menus.InventoryView(user)

        inventory_title = f'{user.player_username}\'s Equipment:\n'
        player_inventory = inventory.display_cinventory(user.player_id)

        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title=inventory_title,
                                  description=player_inventory)
        await ctx.send(embed=embed_msg, view=inventory_view)

    @pandora_bot.command(name='stamina', help="**!stamina** to display your stamina total")
    async def stamina(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        potion_stock = inventory.check_stock(player_object, "I1s")
        output = f'<:estamina:1145534039684562994> {player_object.player_username}\'s stamina: '
        output += str(player_object.player_stamina)
        embed_msg = discord.Embed(colour=discord.Colour.green(), title="Stamina", description=output)
        potion_msg = f"Potion Stock: {potion_stock}"
        embed_msg.add_field(name="", value=potion_msg)
        stamina_view = menus.StaminaView(player_object)
        await ctx.send(embed=embed_msg, view=stamina_view)

    @pandora_bot.command(name='profile', help="**!profile** to display your profile")
    async def profile(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)

        echelon_colour = inventory.get_gear_tier_colours(player_object.player_echelon)
        stamina = f'<:estamina:1145534039684562994> {player_object.player_username}\'s stamina: '
        stamina += str(player_object.player_stamina)
        exp = f'Level: {player_object.player_lvl} Exp: ({player_object.player_exp} / '
        exp += f'{player.get_max_exp(player_object.player_lvl)})'
        id_msg = f'User ID: {player_object.player_id}\nClass: {player_object.player_class}'
        player_object.get_player_multipliers(-1, -1)
        stats = f"Player HP: {player_object.player_mHP:,}"
        stats += f"\nDamage Mitigation: +{player_object.damage_mitigation}%"
        stats += f"\nItem Base Damage: {int(player_object.player_damage):,}"
        stats += f"\nAttack Speed: {player_object.attack_speed} / min"
        stats += f"\nClass Multiplier: +{int(player_object.class_multiplier * 100)}%"

        stats += f"\nCritical Chance: {int(player_object.critical_chance)}%"
        stats += f"\nCritical Damage: +{int(player_object.critical_multiplier * 100)}%"
        stats += f"\nSpecial Critical Multipliers: +{int(player_object.special_multipliers)}x"
        stats += f"\nHit Count: {int(player_object.hit_multiplier)}x"

        stats += f"\nElemental Penetration: +{int(player_object.elemental_penetration * 100)}%"
        stats += f"\nDefence Penetration: +{int(player_object.defence_penetration * 100)}%"
        stats += f"\nFinal Damage: +{int(player_object.final_damage * 100)}%"

        stats += f"\nTeam Aura: +{player_object.aura}x"
        stats += f"\nCurse Aura: +{player_object.curse}x"

        embed_msg = discord.Embed(colour=echelon_colour[0],
                                  title=player_object.player_username,
                                  description=id_msg)
        embed_msg.add_field(name=exp, value=stamina, inline=False)
        embed_msg.add_field(name="Player Stats", value=stats, inline=False)
        thumbnail_url = player.get_thumbnail_by_class(player_object.player_class)
        embed_msg.set_thumbnail(url=thumbnail_url)
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

    @pandora_bot.command(name='refinery', help="**!refinery** to go to the refinery")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def refinery(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title='Welcome to the Refinery!',
                                  description="Please select the item to refine")
        embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
        ref_view = menus.RefSelectView(command_user)
        await ctx.send(embed=embed_msg, view=ref_view)

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
        forge_view = menus.SelectView(player_object)
        await ctx.send(embed=embed_msg, view=forge_view)

    @pandora_bot.command(name='bind', help="**!bind** to perform a binding ritual")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def bind_ritual(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title="Pandora's Binding Ritual",
                                  description="Let me know if you've acquired any new essences!")
        embed_msg.set_image(url="")
        bind_view = menus.BindingTierView(player_object)
        await ctx.send(embed=embed_msg, view=bind_view)

    @pandora_bot.command(name='tarot', help="**!tarot** to check your tarot collection")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def tarot(ctx):
        user = ctx.author
        player_object = player.get_player_by_name(user)
        completion_count = 0
        card_num_list = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
        for x in card_num_list:
            for y in range(1, 4):
                check = f'{x}variant{y}'
                card_qty = inventory.check_tarot(player_object, check)
                if card_qty > 0:
                    completion_count += 1
        embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                  title=f"{player_object.player_username}'s Tarot Collection",
                                  description=f"Completion Total: {completion_count} / 66")
        embed_msg.set_image(url="")
        tarot_view = menus.CollectionView(player_object, embed_msg)
        await ctx.send(embed=embed_msg, view=tarot_view)

    @pandora_bot.command(name='credits', help="**!credits** to see the credits")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def forge(ctx):
        credit_list = "Game created by: Kyle Mistysyn (Archael)"
        # Artists
        credit_list += "\n@labcornerr - Emoji Artist (Fiverr)"
        credit_list += "\n@cactus21 - Tarot Artist (Fiverr)"
        # Programming
        credit_list += "\nBahamutt - Programming Assistance"
        credit_list += "\nPota - Programming Assistance"
        embed_msg = discord.Embed(colour=discord.Colour.light_gray(),
                                  title="Credits",
                                  description=credit_list)
        embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
        await ctx.send(embed=embed_msg)

    pandora_bot.run(TOKEN)
