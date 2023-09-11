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

    class ExploreView(discord.ui.View):
        def __init__(self, user, new_item, msg, item_type):
            super().__init__(timeout=None)
            self.user = user
            self.new_item = new_item
            self.msg = msg
            self.item_type = item_type

        @discord.ui.button(label="Keep", style=discord.ButtonStyle.success, emoji="✅")
        async def keep_callback(self, interaction: discord.Interaction, choice_select: discord.ui.Select):
            if not inventory.if_custom_exists(self.new_item.item_id):
                message = inventory.inventory_add_custom_item(self.new_item)
                self.msg.add_field(name="", value=message, inline=False)
            await interaction.response.edit_message(embed=self.msg, view=None)

        @discord.ui.button(label="Discard", style=discord.ButtonStyle.red, emoji="✖️")
        async def discard_callback(self, interaction: discord.Interaction, choice_select: discord.ui.Select):
            message = f'You have discarded the {self.item_type}'
            self.msg.add_field(name="", value=message, inline=False)
            await interaction.response.edit_message(embed=self.msg, view=None)

        @discord.ui.button(label="Try Again", style=discord.ButtonStyle.blurple, emoji="↪️")
        async def again_callback(self, interaction: discord.Interaction, choice_select: discord.ui.Select):
            if self.user.spend_stamina(25):
                match self.item_type:
                    case "weapon":
                        self.new_item = inventory.CustomWeapon(self.user.player_id)
                    case "armour":
                        self.new_item = inventory.CustomArmour(self.user.player_id)
                    case "accessory":
                        self.new_item = inventory.CustomAccessory(self.user.player_id)
                    case _:
                        self.new_item = inventory.CustomWeapon(self.user.player_id)
                self.embed_msg = self.new_item.create_citem_embed()
                inquiry = f"Would you like to keep or discard this {self.item_type}?"
                gear_colours = inventory.get_gear_tier_colours(self.new_item.item_base_tier)
                tier_emoji = gear_colours[1]
                self.embed_msg.add_field(name=f'{tier_emoji} Tier {str(self.new_item.item_base_tier)} item found!',
                                    value=inquiry, inline=False)
                await interaction.response.edit_message(embed=self.embed_msg, view=self)
            else:
                await interaction.response.send_message('Not enough !stamina')

    @pandora_bot.command(name='lab', help="**!lab** to run a daily labyrinth")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def lab(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(25):
            item_object = inventory.CustomWeapon(command_user.player_id)
            embed_msg = item_object.create_citem_embed()
            gear_colours = inventory.get_gear_tier_colours(item_object.item_base_tier)
            tier_emoji = gear_colours[1]
            inquiry = "Would you like to keep or discard this weapon?"
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(item_object.item_base_tier)} item found!',
                                value=inquiry,
                                inline=False)
            lab_view = ExploreView(command_user, item_object, embed_msg, "weapon")
            await ctx.send(embed=embed_msg, view=lab_view)
        else:
            await ctx.send('Not enough !stamina')

    @pandora_bot.command(name='dung', help="**!dung** to run a daily dungeon")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def dung(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(25):
            item_object = inventory.CustomArmour(command_user.player_id)
            embed_msg = item_object.create_citem_embed()
            gear_colours = inventory.get_gear_tier_colours(item_object.item_base_tier)
            tier_emoji = gear_colours[1]
            inquiry = "Would you like to keep or discard this armour?"
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(item_object.item_base_tier)} item found!',
                                value=inquiry,
                                inline=False)
            lab_view = ExploreView(command_user, item_object, embed_msg, "armour")
            await ctx.send(embed=embed_msg, view=lab_view)
        else:
            await ctx.send('Not enough !stamina')

    @pandora_bot.command(name='tow', help="**!tow** to run a daily tower")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def tow(ctx):
        player_name = str(ctx.author)
        command_user = player.get_player_by_name(player_name)
        if command_user.spend_stamina(25):
            item_object = inventory.CustomAccessory(command_user.player_id)
            embed_msg = item_object.create_citem_embed()
            gear_colours = inventory.get_gear_tier_colours(item_object.item_base_tier)
            tier_emoji = gear_colours[1]
            inquiry = "Would you like to keep or discard this accessory?"
            embed_msg.add_field(name=f'{tier_emoji} Tier {str(item_object.item_base_tier)} item found!',
                                value=inquiry,
                                inline=False)
            lab_view = ExploreView(command_user, item_object, embed_msg, "accessory")
            await ctx.send(embed=embed_msg, view=lab_view)
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

    class InventoryView(discord.ui.View):
        def __init__(self, user):
            super().__init__(timeout=None)
            self.user = user

        @discord.ui.select(
            placeholder="Select crafting method!",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Equipment", description="Stored Equipment"),
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Items", description="Regular Items")
            ]
        )
        async def inventory_callback(self, interaction: discord.Interaction, inventory_select: discord.ui.Select):
            if inventory_select.values[0] == "Equipment":
                inventory_title = f'{self.user.player_username}\'s Equipment:\n'
                player_inventory = inventory.display_cinventory(self.user.player_id)
            else:
                inventory_title = f'{self.user.player_username}\'s Inventory:\n'
                player_inventory = inventory.display_binventory(self.user.player_id)

            new_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title=inventory_title,
                                      description=player_inventory)
            await interaction.response.edit_message(embed=new_embed)

    @pandora_bot.command(name='inv', help="**!inv** to display your gear and item inventory")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def inv(ctx):
        user = player.get_player_by_name(str(ctx.author))
        inventory_view = InventoryView(user)

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
        id_msg = f'User ID: {player_object.player_id}\nClass: {player_object.player_class}'
        player_object.get_player_multipliers()

        stats = f"Player Item Base Damage: {int(player_object.player_damage):,}"
        stats += f"\nPlayer HP: {player_object.player_hp:,}"
        stats += f"\nAttack Speed: {player_object.attack_speed} / min"
        stats += f"\nDamage Mitigation: +{player_object.damage_mitigation}%"
        stats += f"\nCritical Chance: +{int(player_object.critical_chance)}%"
        stats += f"\nCritical Damage: +{int(player_object.critical_multiplier * 100)}%"
        stats += f"\nElemental Penetration: +{int(player_object.elemental_penetration * 100)}%"
        stats += f"\nFinal Damage: +{int(player_object.final_damage * 100)}%"
        stats += f"\nHit Count: {int(player_object.hit_multiplier)}x"
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

    @pandora_bot.command(name='ref', help="**!ref** to go to the refinery")
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
            self.selected_id = self.selected_item.item_id
            self.player_object = player_object
            self.letter = "a"
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
                    emoji="<a:eenergy:1145534127349706772>", label="Enhance", description="Enhance the item"),
                discord.SelectOption(
                    emoji="<:eore:1145534835507593236>", label="Upgrade", description="Upgrade the item"),
                discord.SelectOption(
                    emoji="<:esoul:1145520258241806466>", label="Bestow", description="Bless the item"),
                discord.SelectOption(
                    emoji="<:ehammer:1145520259248427069>", label="Open", description="Open a socket"),
                discord.SelectOption(
                    emoji="<a:ematrix:1145520262268325919>", label="Imbue", description="Add new rolls"),
                discord.SelectOption(
                    emoji="<a:eshadow2:1141653468965257216>", label="Cleanse", description="Remove random rolls"),
                discord.SelectOption(
                    emoji="<:eprl:1148390531345432647>", label="Augment", description="Augment existing rolls"),
                discord.SelectOption(
                    emoji="<a:eorigin:1145520263954440313>", label="Implant", description="Gain new elements"),
                discord.SelectOption(
                    emoji="<a:evoid:1145520260573827134>",label="Voidforge", description="Upgrade to a void weapon")
            ]
        )
        async def forge_callback(self, interaction: discord.Interaction, forge_select: discord.ui.Select):
            self.clear_items()
            match forge_select.values[0]:
                case "Enhance":
                    self.letter = "a"
                    self.num_buttons = 5
                case "Upgrade":
                    self.letter = "b"
                    self.button_emoji.append(loot.get_loot_emoji("I1b"))
                    self.button_emoji.append(loot.get_loot_emoji("I2b"))
                    self.button_emoji.append(loot.get_loot_emoji("I3b"))
                    self.button_emoji.append(loot.get_loot_emoji("I4b"))
                    self.num_buttons = 5
                case "Bestow":
                    self.letter = "c"
                    self.button_emoji.append(loot.get_loot_emoji("I1c"))
                    self.button_emoji.append(loot.get_loot_emoji("I2c"))
                    self.button_emoji.append(loot.get_loot_emoji("I3c"))
                    self.button_emoji.append(loot.get_loot_emoji("I4c"))
                    self.num_buttons = 5
                case "Open":
                    self.letter = "d"
                    self.button_emoji.append(loot.get_loot_emoji("I1d"))
                    self.button_emoji.append(loot.get_loot_emoji("I2d"))
                    self.button_emoji.append(loot.get_loot_emoji("I3d"))
                    self.button_emoji.append(loot.get_loot_emoji("I4d"))
                    self.num_buttons = 5
                case "Imbue":
                    self.letter = "h"
                    self.button_emoji.append(loot.get_loot_emoji("I1h"))
                    self.button_emoji.append(loot.get_loot_emoji("I2h"))
                    self.button_emoji.append(loot.get_loot_emoji("I3h"))
                    self.button_emoji.append(loot.get_loot_emoji("I4h"))
                    self.num_buttons = 5
                case "Cleanse":
                    self.letter = "i"
                    self.button_emoji.append(loot.get_loot_emoji("I1i"))
                    self.button_emoji.append(loot.get_loot_emoji("I2i"))
                    self.button_emoji.append(loot.get_loot_emoji("I3i"))
                    self.button_emoji.append(loot.get_loot_emoji("I4i"))
                    self.num_buttons = 5
                case "Augment":
                    self.letter = "j"
                    self.button_emoji.append(loot.get_loot_emoji("I1j"))
                    self.button_emoji.append(loot.get_loot_emoji("I2j"))
                    self.button_emoji.append(loot.get_loot_emoji("I3j"))
                    self.button_emoji.append(loot.get_loot_emoji("I4j"))
                    self.num_buttons = 5
                case "Implant":
                    self.letter = "k"
                    self.button_emoji.append(loot.get_loot_emoji("I4k"))
                    self.num_buttons = 2
                case "Voidforge":
                    self.letter = "l"
                    self.button_emoji.append(loot.get_loot_emoji("I4l"))
                    self.num_buttons = 2
                case _:
                    self.num_buttons = 0

            # Assign response
            async def first_button_callback(button_interaction: discord.Interaction):
                item_code = f'I1{self.letter}'
                new_embed_msg = run_button(item_code)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            async def second_button_callback(button_interaction: discord.Interaction):
                item_code = f'I2{self.letter}'
                new_embed_msg = run_button(item_code)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            async def third_button_callback(button_interaction: discord.Interaction):
                item_code = f'I3{self.letter}'
                new_embed_msg = run_button(item_code)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            async def fourth_button_callback(button_interaction: discord.Interaction):
                item_code = f'I4{self.letter}'
                new_embed_msg = run_button(item_code)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            def run_button(item_code):
                method = forge_select.values[0]
                self.selected_item = inventory.read_custom_item(self.selected_id)
                result = inventory.craft_item(self.player_object, self.selected_item, item_code, method)
                if result == "0":
                    outcome = "Failed!"
                elif result == "1":
                    outcome = "Success!"
                elif result == "3":
                    outcome = "Cannot upgrade further"
                elif result == "4":
                    outcome = "Item not ready for upgrade"
                elif result == "5":
                    outcome = "A roll has been successfully removed!"
                elif result == "6":
                    outcome = "Item not eligible!"
                else:
                    outcome = f"Out of Stock: {loot.get_loot_emoji(str(item_code))}"
                new_embed_msg = self.selected_item.create_citem_embed()
                new_embed_msg.add_field(name=outcome, value="", inline=False)
                return new_embed_msg

            async def button_multi_callback(button_interaction: discord.Interaction):
                self.selected_item = inventory.read_custom_item(self.selected_id)
                result = "0"
                overall = ""
                outcome = ""
                count = 0
                method = forge_select.values[0]
                match method:
                    case "Enhance":
                        item_id_list = ["I1a", "I2a", "I3a"]
                    case "Upgrade":
                        item_id_list = ["I1b", "I2b", "I3b"]
                    case "Bestow":
                        item_id_list = ["I1c", "I2c", "I3c"]
                    case "Open":
                        item_id_list = ["I1d", "I2d", "I3d"]
                    case "Imbue":
                        item_id_list = ["I1h", "I2h", "I3h"]
                    case "Cleanse":
                        item_id_list = ["I1i", "I2i", "I3i"]
                    case "Augment":
                        item_id_list = ["I1j", "I2j", "I3j"]
                    case "Implant":
                        item_id_list = ["I4k"]
                    case "Voidforge":
                        item_id_list = ["I4l"]
                    case _:
                        item_id_list = ["error"]
                for x in item_id_list:
                    running = True
                    while running and count < 50:
                        count += 1
                        result = inventory.craft_item(self.player_object, self.selected_item, x, method)
                        if result != "0" and result != "1":
                            running = False
                        elif result == "0" and overall == "":
                            overall = "All Failed"
                        elif result == "1":
                            if overall == "Success!":
                                overall = "!!MULTI-SUCCESS!!"
                            elif overall != "!!MULTI-SUCCESS!!":
                                overall = "Success!"
                    if result == "3":
                        outcome = "Cannot upgrade further"
                        break
                    elif result == "5":
                        overall = "Success!"
                        outcome = "A roll has been successfully removed!"
                        break
                    elif result == "6":
                        overall = "Cannot Continue"
                        outcome = "Item not eligible!"
                    elif count == 50:
                        outcome = f"Used: 50x{loot.get_loot_emoji(str(x))}"
                    else:
                        outcome = f"Out of Stock: {loot.get_loot_emoji(str(x))}"
                new_embed_msg = self.selected_item.create_citem_embed()
                new_embed_msg.add_field(name=overall, value=outcome, inline=False)
                await button_interaction.response.edit_message(embed=new_embed_msg)

            async def button_cancel_callback(button_interaction: discord.Interaction):
                # cancel here
                await button_interaction.response.edit_message(view=None)

            self.button_label.append(f"T1 {forge_select.values[0]}")
            self.button_label.append(f"T2 {forge_select.values[0]}")
            self.button_label.append(f"T3 {forge_select.values[0]}")
            self.button_label.append(f"T4 {forge_select.values[0]}")
            self.button_label.append(f"Multi {forge_select.values[0]}")

            if self.num_buttons == 5:
                code = "I1" + self.letter
                self.button_emoji.append(loot.get_loot_emoji(code))
                code = "I2" + self.letter
                self.button_emoji.append(loot.get_loot_emoji(code))
                code = "I3" + self.letter
                self.button_emoji.append(loot.get_loot_emoji(code))
                code = "I4" + self.letter
                self.button_emoji.append(loot.get_loot_emoji(code))
                button_1 = Button(label=self.button_label[0], style=discord.ButtonStyle.success, emoji=self.button_emoji[0])
                button_2 = Button(label=self.button_label[1], style=discord.ButtonStyle.success, emoji=self.button_emoji[1])
                button_3 = Button(label=self.button_label[2], style=discord.ButtonStyle.success, emoji=self.button_emoji[2])
                button_4 = Button(label=self.button_label[3], style=discord.ButtonStyle.success, emoji=self.button_emoji[3])
                self.add_item(button_1)
                self.add_item(button_2)
                self.add_item(button_3)
                self.add_item(button_4)
                button_1.callback = first_button_callback
                button_2.callback = second_button_callback
                button_3.callback = third_button_callback
                button_4.callback = fourth_button_callback
            else:
                code = "I4" + self.letter
                self.button_emoji.append(loot.get_loot_emoji(code))
                button_4 = Button(label=self.button_label[3], style=discord.ButtonStyle.success, emoji=self.button_emoji[0])
                self.add_item(button_4)
                button_4.callback = fourth_button_callback

            button_multi = Button(label=self.button_label[4], style=discord.ButtonStyle.blurple, emoji="⬆️", row=1)
            button_cancel = Button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=1)
            self.add_item(button_multi)
            button_multi.callback = button_multi_callback
            self.add_item(button_cancel)
            button_cancel.callback = button_cancel_callback
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
                    emoji="<a:eenergy:1145534127349706772>", label="Accessory", description="Equipped Accessory"),
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Wing", description="Equipped Wing"),
                discord.SelectOption(
                    emoji="<a:eenergy:1145534127349706772>", label="Crest", description="Equipped Paragon Crest")
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
                case "Wing":
                    if self.player_object.equipped_wing != "":
                        self.selected_item = inventory.read_custom_item(self.player_object.equipped_wing)
                    else:
                        error_msg = "Not equipped"
                case "Crest":
                    if self.player_object.equipped_crest != "":
                        self.selected_item = inventory.read_custom_item(self.player_object.equipped_crest)
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
