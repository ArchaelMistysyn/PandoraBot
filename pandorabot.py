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
from discord.ui import Button, View
import csv
import menus
import mysql.connector
from mysql.connector.errors import Error
import tarot
import quest

# Initialize database
db_info = None
with open("bot_db_login.txt", 'r') as data_file:
    for line in data_file:
        db_info = line.split(";")

# Global emojis
exp_icon = "<:eexp:1148088187516891156>"
coin_icon = "🤑"
class_knight = "<:cB:1154266777396711424>"
class_ranger = "<:cA:1150195102589931641>"
class_mage = "<:cC:1150195246588764201>"
class_assassin = "❌"
class_weaver = "❌"
class_rider = "❌"
class_summoner = "<:cD:1150195280969478254>"
class_icon_list = [class_knight, class_ranger, class_mage, class_assassin, class_weaver, class_rider, class_summoner]
class_icon_dict = {"Knight": class_knight, "Ranger": class_ranger, "Mage": class_mage,
                   "Assassin": class_assassin, "Weaver": class_weaver,
                   "Rider": class_rider, "Summoner": class_summoner}

# Global role list
role_list = ["Player Echelon 1", "Player Echelon 2", "Player Echelon 3", "Player Echelon 4", "Player Echelon 5 (MAX)"]

# Initialize server and channel list
channel_list_wiki = [1140841088005976124, 1141256419161673739, 1148155007305273344]
channel_list = [1157937444931514408, 1157934010090131458, 1157935203394785291, 1157935449462013972, 1157935876853211186]
global_server_channels = [channel_list]

# Initialize damage_type lists
element_fire = "<:ee:1141653476816986193>"
element_water = "<:ef:1141653475059572779>"
element_lightning = "<:ei:1141653471154671698>"
element_earth = "<:eh:1141653473528664126>"
element_wind = "<:eg:1141653474480767016>"
element_ice = "<:em:1141647050342146118>"
element_dark = "<:ek:1141653468080242748>"
element_light = "<:el:1141653466343800883>"
element_celestial = "<:ej:1141653469938339971>"
global_element_list = [element_fire, element_water, element_lightning, element_earth, element_wind, element_ice,
                       element_dark, element_light, element_celestial]
element_names = ["Fire", "Water", "Lightning", "Earth", "Wind", "Ice", "Dark", "Light", "Celestial"]

tier_2_abilities = ["Molten", "Aquatic", "Electric", "Mountain", "Gust", "Frost", "Shadow", "Flash", "Star"]
tier_3_abilities = ["Blazing", "Drowning", "Bolting", "Crushing", "Whirling",
                    "Freezing", "Shrouding", "Shining", "Twinkling"]
tier_4_abilities = ["Curse of Immortality", "Elemental Fractal", "Bahamut's Trinity",
                    "Omega Critical", "Perfect Precision", "Overflowing Vitality",
                    "Specialist's Mastery", "Shatter Barrier", "Divine Protection"]
global_buff_type_list = ["Hero's", "Guardian's", "Aggressor's", "Breaker's"]
global_descriptor_list = ["Pose", "Stance", "Will", ""]
global_unique_ability_list = [element_names, tier_2_abilities, tier_3_abilities, tier_4_abilities]


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
            temp_player.player_name = after.name
            temp_player.set_player_field("player_name", after.name)

    # bot startup actions
    @pandora_bot.event
    async def on_ready():
        print(f'{pandora_bot.user} Online!')
        timer = 60
        for server in global_server_channels:
            command_channel_id = server[0]
            cmd_ctx = pandora_bot.get_channel(command_channel_id)
            pandora_bot.loop.create_task(stamina_manager(600, cmd_ctx))
            for x in range(1, 5):
                raid_channel_id = server[x]
                raid_ctx = pandora_bot.get_channel(raid_channel_id)
                pandora_bot.loop.create_task(timed_task(timer, raid_channel_id, x, raid_ctx))
            restore_boss_list, raid_id_list = bosses.restore_solo_bosses(command_channel_id)
            for idy, y in enumerate(restore_boss_list):
                player_object = player.get_player_by_id(y.player_id)
                pandora_bot.loop.create_task(restore_boss_task(timer, player_object, y,
                                                               raid_id_list[idy], command_channel_id, cmd_ctx))

    @pandora_bot.event
    async def stamina_manager(duration_seconds, ctx):
        while True:
            await asyncio.sleep(duration_seconds)
            player_list = player.get_all_users()
            for player_user in player_list:
                new_stamina_value = player_user.player_stamina + 2
                if new_stamina_value > 2000:
                    new_stamina_value = 2000
                player_user.set_player_field("player_stamina", new_stamina_value)

    class RaidView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Join the raid!", style=discord.ButtonStyle.success, emoji="⚔️")
        async def raid_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
            clicked_by = player.get_player_by_name(str(interaction.user))
            outcome = clicked_by.player_username
            outcome += bosses.add_participating_player(interaction.channel.id, clicked_by.player_id)

            await interaction.response.send_message(outcome)

    @pandora_bot.event
    async def restore_boss_task(duration_seconds, player_object, active_boss, raid_id, channel_id, ctx):
        is_alive = True
        embed_msg = active_boss.create_boss_msg(0, is_alive)
        sent_message = await ctx.send(embed=embed_msg)
        while is_alive:
            await asyncio.sleep(duration_seconds)
            player_object.get_equipped()
            dps = player_object.get_player_damage(active_boss)
            active_boss.boss_cHP -= dps
            bosses.update_boss_cHP(channel_id, active_boss.player_id, active_boss.boss_cHP)
            if active_boss.calculate_hp():
                embed_msg = active_boss.create_boss_msg(dps, is_alive)
                await sent_message.edit(embed=embed_msg)
            else:
                if player_object.player_quest <= 4:
                    player_object.check_and_update_tokens(3, 1)
                if player_object.player_quest <= 9 and active_boss.boss_tier == 4:
                    player_object.check_and_update_tokens(9, 1)
                is_alive = False
                embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
                player_list = [player_object.player_id]
                loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                bosses.clear_boss_info(channel_id, player_object.player_id)
                await sent_message.edit(embed=loot_embed)

    @pandora_bot.event
    async def timed_task(duration_seconds, channel_id, channel_num, ctx):
        level, boss_type, boss_tier = bosses.get_boss_details(channel_num)
        active_boss = bosses.spawn_boss(channel_id, 0, boss_tier, boss_type, level, channel_num)
        embed_msg = active_boss.create_boss_msg(0, True)
        raid_button = RaidView()
        sent_message = await ctx.send(embed=embed_msg, view=raid_button)
        while True:
            await asyncio.sleep(duration_seconds)
            player_list, damage_list = bosses.get_damage_list(channel_id)
            dps = 0
            for idx, x in enumerate(player_list):
                temp_user = player.get_player_by_id(int(x))
                player_dps = temp_user.get_player_damage(active_boss)
                dps += player_dps
                new_player_dps = int(damage_list[idx]) + player_dps
                bosses.update_player_damage(channel_id, int(x), new_player_dps)
            active_boss.boss_cHP -= dps
            bosses.update_boss_cHP(channel_id, 0, active_boss.boss_cHP)
            if active_boss.calculate_hp():
                embed_msg = active_boss.create_boss_msg(dps, True)
                await sent_message.edit(embed=embed_msg)
            else:
                for x in player_list:
                    temp_user = player.get_player_by_id(int(x))
                    # Set tokens based on boss type will need to add case statement here
                    if temp_user.player_quest <= 7:
                        temp_user.check_and_update_tokens(6, 1)
                embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
                loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                await sent_message.edit(embed=loot_embed)

                level, boss_type, boss_tier = bosses.get_boss_details(channel_num)
                active_boss = bosses.spawn_boss(channel_id, 0, boss_tier, boss_type, level, channel_num)
                bosses.clear_boss_info(channel_id, 0)
                player_list.clear()
                embed_msg = active_boss.create_boss_msg(0, True)
                sent_message = await ctx.send(embed=embed_msg, view=raid_button)

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

    @pandora_bot.command(name='register', help="**!register [USERNAME]** Register a username to begin playing!")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def play(ctx, username):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title="Register",
                                      description="Starting story goes here - Select Class")
            user = ctx.author
            player_name = str(user)
            class_view = menus.ClassSelect(player_name, username)
            await ctx.send(embed=embed_msg, view=class_view)

    @pandora_bot.command(name='explore', help="**!explore** to go on an an exploration")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def adventure(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_name = str(ctx.author)
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                player_object.get_equipped()
                player_object.get_player_multipliers()
                if player_object.spend_stamina(25):
                    player_object.check_and_update_tokens(2, 1)
                    starting_room = explore.generate_new_room(player_object)
                    embed_msg = starting_room.embed
                    starting_view = starting_room.room_view
                    await ctx.send(embed=embed_msg, view=starting_view)
                else:
                    await ctx.send('Not enough !stamina')
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='inlay', help="**!inlay [itemID]** to inlay a specific gem into an equipped item")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def inlay(ctx, item_id):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            if inventory.if_custom_exists(item_id):
                selected_item = inventory.read_custom_item(item_id)
                player_object = player.get_player_by_name(str(ctx.author))
                if player_object.player_class != "":
                    if current_user.player_id == selected_item.player_owner:
                        embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                                  title="Inlay Gem",
                                                  description="Let me know what item you'd like to inlay this gem into!")
                        embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                        view = menus.InlaySelectView(player_object, selected_item.item_id)
                        view.embed = await ctx.send(embed=embed_msg, view=view)

                    else:
                        response = "wrong item id"
                        await ctx.send(response)
                else:
                    embed_msg = unregistered_message()
                    await ctx.send(embed=embed_msg)
            else:
                response = "wrong item id"
                await ctx.send(response)

    @pandora_bot.command(name='fort', help="**!fort** to challenge a fortress")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def fort(ctx):
        channel_id = ctx.channel.id
        if any(channel_id in sl for sl in global_server_channels):
            player_name = ctx.author
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                if player_object.equipped_weapon != 0:
                    existing_id = bosses.get_raid_id(channel_id, player_object.player_id)
                    if existing_id == 0:
                        if player_object.spend_stamina(50):
                            # initialize the boss post
                            boss_type = "Fortress"
                            new_boss_tier = bosses.get_random_bosstier(boss_type)
                            active_boss = bosses.spawn_boss(channel_id, player_object.player_id, new_boss_tier,
                                                            boss_type, player_object.player_lvl, 0)
                            active_boss.player_id = player_object.player_id
                            is_alive = True
                            embed_msg = active_boss.create_boss_msg(0, is_alive)
                            sent_message = await ctx.send(embed=embed_msg)
                            while is_alive:
                                await asyncio.sleep(60)
                                dps = player_object.get_player_damage(active_boss)
                                active_boss.boss_cHP -= dps
                                bosses.update_boss_cHP(channel_id, active_boss.player_id, active_boss.boss_cHP)
                                if active_boss.calculate_hp():
                                    embed_msg = active_boss.create_boss_msg(dps, is_alive)
                                    await sent_message.edit(embed=embed_msg)
                                else:
                                    if player_object.player_quest <= 4:
                                        player_object.check_and_update_tokens(3, 1)
                                    if player_object.player_quest <= 9 and active_boss.boss_tier == 4:
                                        player_object.check_and_update_tokens(9, 1)
                                    is_alive = False
                                    embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
                                    player_list = [player_object.player_id]
                                    loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                                    bosses.clear_boss_info(channel_id, player_object.player_id)
                                    await sent_message.edit(embed=loot_embed)
                        else:
                            await ctx.send("Not enough stamina.")
                    else:
                        await ctx.send("You already have a fortress encounter running.")
                        
                else:
                    await ctx.send("You must have a weapon equipped.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='quest', help="**!quest** to start the story quest")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def story_quest(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(str(user))
            current_quest = player_object.player_quest
            if current_quest != 0:
                current_quest = player_object.player_quest
                quest_object = quest.get_quest(current_quest, player_object)
                quest_message = quest_object.get_quest_embed(player_object)
                quest_view = menus.QuestView(player_object, quest_object)
                await ctx.send(embed=quest_message, view=quest_view)
            elif current_quest > 30:
                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                          title="Quests",
                                          description="All quests completed!")
                await ctx.send(embed=embed_msg)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='gear', help="**!inv** to display your equipped gear")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def gear(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                player_object.get_equipped()
                if player_object.equipped_weapon != 0:
                    equipped_item = inventory.read_custom_item(player_object.equipped_weapon)
                    embed_msg = equipped_item.create_citem_embed()
                    gear_view = menus.GearView(player_object)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_gray(),
                                              title="Equipped weapon",
                                              description="No weapon is equipped")
                    gear_view = None
                await ctx.send(embed=embed_msg, view=gear_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='inv', help="**!inv** to display your gear and item inventory")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def inv(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                inventory_view = menus.InventoryView(player_object)

                inventory_title = f'{player_object.player_username}\'s Equipment:\n'
                player_inventory = inventory.display_cinventory(player_object.player_id)

                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title=inventory_title,
                                          description=player_inventory)
                await ctx.send(embed=embed_msg, view=inventory_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='stamina', help="**!stamina** to display your stamina total")
    async def stamina(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = player_object.create_stamina_embed()
                stamina_view = menus.StaminaView(player_object)
                await ctx.send(embed=embed_msg, view=stamina_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='profile', help="**!profile** to display your profile")
    async def profile(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                echelon_colour = inventory.get_gear_tier_colours(player_object.player_echelon)
                resources = f'<:estamina:1145534039684562994> {player_object.player_username}\'s stamina: '
                resources += str(player_object.player_stamina)
                resources += f'\nLotus Coins: {player_object.player_coins}'
                exp = f'Level: {player_object.player_lvl} Exp: ({player_object.player_exp} / '
                exp += f'{player.get_max_exp(player_object.player_lvl)})'
                id_msg = f'User ID: {player_object.player_id}\nClass: {player_object.player_class}'
                player_object.get_player_multipliers()
                stats = f"Player HP: {player_object.player_mHP:,}"
                stats += f"\nDamage Mitigation: +{player_object.damage_mitigation}%"
                stats += f"\nItem Base Damage: {int(player_object.player_damage):,}"
                stats += f"\nAttack Speed: {player_object.attack_speed} / min"
                stats += f"\nClass Multiplier: +{int(player_object.class_multiplier * 100)}%"

                stats += f"\nCritical Chance: {int(player_object.critical_chance)}%"
                stats += f"\nCritical Damage: +{int(player_object.critical_multiplier * 100)}%"
                stats += f"\nHit Count: {int(player_object.hit_multiplier)}x"

                stats += f"\nElemental Penetration: +{int(player_object.elemental_penetration * 100)}%"
                stats += f"\nDefence Penetration: +{int(player_object.defence_penetration * 100)}%"
                stats += f"\nFinal Damage: +{int(player_object.final_damage * 100)}%"

                stats += f"\nTeam Aura: +{player_object.aura}x"
                stats += f"\nCurse Aura: +{player_object.curse}x"

                embed_msg = discord.Embed(colour=echelon_colour[0],
                                          title=player_object.player_username,
                                          description=id_msg)
                embed_msg.add_field(name=exp, value=resources, inline=False)
                embed_msg.add_field(name="Player Stats", value=stats, inline=False)
                thumbnail_url = player.get_thumbnail_by_class(player_object.player_class)
                embed_msg.set_thumbnail(url=thumbnail_url)
                await ctx.send(embed=embed_msg)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='admin', help="**!admin** inputs")
    async def admin(ctx, backdoor, value):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if backdoor == "stamina_hack":
                player_object.set_player_field("player_stamina", value)
            if backdoor == "item_hack":
                inventory.update_stock(player_object, value, 10)
            if backdoor == "item_hack_all":
                filename = "itemlist.csv"
                with (open(filename, 'r') as f):
                    for line in csv.DictReader(f):
                        inventory.update_stock(player_object, str(line['item_id']), int(value))

    @pandora_bot.command(name='item', help="**!item** to display your item details")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def item(ctx, item_id):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                if inventory.if_custom_exists(item_id):
                    selected_item = inventory.read_custom_item(item_id)
                    if player_object.player_id == selected_item.player_owner:
                        embed_msg = selected_item.create_citem_embed()
                        manage_item_view = menus.ManageCustomItemView(player_object, item_id)
                        await ctx.send(embed=embed_msg, view=manage_item_view)
                    else:
                        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                                  title="You do not own an item with this ID.",
                                                  description=f"Inputted ID: {item_id}")
                        await ctx.send(embed=embed_msg)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="An item with this ID does not exist.",
                                              description=f"Inputted ID: {item_id}")
                    await ctx.send(embed=embed_msg)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='who', help="**!who [NewUsername]** to set your username")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def who(ctx, new_username):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            existing_user = player.get_player_by_name(ctx.author)
            if player.check_username(new_username):
                existing_user.player_username = new_username
                existing_user.set_player_field("player_username", new_username)
                message = f'Got it! I\'ll call you {existing_user.player_username} from now on!'
            else:
                message = f'Sorry that username is taken.'
            await ctx.send(message)

    @pandora_bot.command(name='refinery', help="**!refinery** to go to the refinery")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def refinery(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_name = str(ctx.author)
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title='Welcome to the Refinery!',
                                          description="Please select the item to refine")
                embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                ref_view = menus.RefSelectView(player_object)
                await ctx.send(embed=embed_msg, view=ref_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='forge', help="**!forge** to enter the celestial forge")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def forge(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                player_object.get_equipped()
                embed_msg = discord.Embed(colour=discord.Colour.blurple(),
                                          title="Pandora's Celestial Forge",
                                          description="Let me know what you'd like me to upgrade today!")
                embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
                forge_view = menus.SelectView(player_object)
                await ctx.send(embed=embed_msg, view=forge_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='bind', help="**!bind** to perform a binding ritual")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def bind_ritual(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title="Pandora's Binding Ritual",
                                          description="Let me know if you've acquired any new essences!")
                embed_msg.set_image(url="")
                bind_view = menus.BindingTierView(player_object)
                await ctx.send(embed=embed_msg, view=bind_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='tarot', help="**!tarot** to check your tarot collection")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def tarot_collection(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                completion_count = tarot.collection_check(player_object.player_id)
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title=f"{player_object.player_username}'s Tarot Collection",
                                          description=f"Completion Total: {completion_count} / 66")
                embed_msg.set_image(url="")
                tarot_view = menus.CollectionView(player_object, embed_msg)
                await ctx.send(embed=embed_msg, view=tarot_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='credits', help="**!credits** to see the credits")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def forge(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
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

    @pandora_bot.command(name='sell', help="**!sell [item_id]** to sell an unequipped item")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def sell(ctx, item_id):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title="An item with this ID does not exist.",
                                      description=f"Inputted ID: {item_id}")
            await ctx.send(embed=embed_msg)

    def unregistered_message():
        register_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                       title="Unregistered",
                                       description="Please register using !register to play.")
        return register_embed

    # NOT PANDORA GAME RELATED

    @pandora_bot.command(name='simulateCEOD', help="**!simulateCEOD [num +10s]: simulate gold cost to make a +10 ceod")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def simulateCEOD(ctx, num_eods):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            gold_cost = 0
            count = 0
            lowest = 999999999999999999
            highest = 0
            total_eods = 0

            def roll_ceod():
                spent_gold = 0
                total_nines = 0
                go_again = 0
                current_item = 0
                item_1_enhancement = 0
                item_2_enhancement = 0
                items = [item_1_enhancement, item_2_enhancement]
                while go_again == 0:
                    attempt_outcome = try_enhance()
                    spent_gold += 10000
                    if attempt_outcome == 0:
                        items[current_item] += 1
                        if items[0] == 9:
                            current_item = 1
                            if items[1] == 9:
                                for x in range(2):
                                    outcome = 2
                                    while outcome != 0 and outcome != 1:
                                        spent_gold += 10000
                                        outcome = try_enhance()
                                        if outcome == 0:
                                            go_again += 1
                                        elif outcome == 1:
                                            items[x] = 0
                        else:
                            current_item = 0
                    elif attempt_outcome == 1:
                        items[current_item] = 0
                return spent_gold, go_again

            def try_enhance():
                random_result = random.randint(1, 1000)
                if random_result <= 403:
                    result = 0
                elif random_result >= 500:
                    result = 1
                else:
                    result = 2
                return result

            new_eod = True
            while new_eod:
                temp_gold, eod_count = roll_ceod()
                total_eods += eod_count
                gold_cost += temp_gold
                if temp_gold > highest:
                    highest = temp_gold
                if temp_gold < lowest:
                    lowest = temp_gold
                if total_eods >= int(num_eods):
                    new_eod = False
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                      title=f"{total_eods} Successes!",
                                      description=f"The total cost was {gold_cost:,} gold!")
            average_cost = int(gold_cost / int(total_eods))
            embed_msg.add_field(name="Average", value=f"The average cost was {average_cost:,} gold!")
            embed_msg.add_field(name="Lowest", value=f"The lowest cost was {lowest:,} gold!")
            embed_msg.add_field(name="Highest", value=f"The highest cost was {highest:,} gold!")
            await ctx.send(embed=embed_msg)

    pandora_bot.run(TOKEN)
