import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ui import Button, View
from discord import app_commands
import asyncio
import csv
import pandas as pd
import mysql.connector
from mysql.connector.errors import Error
import sys

import explore
import inventory
import bosses
import random
import loot
import player
import damagecalc
import menus
import quest
import tarot
import bazaar
import pilengine

# Get Bot Token
token_info = None
with open("bot_token.txt", 'r') as token_file:
    for line in token_file:
        token_info = line
TOKEN = token_info

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

not_owned_icon = "https://kyleportfolio.ca/botimages/profilecards/noachv.png"
owned_icon = "https://kyleportfolio.ca/botimages/profilecards/owned.png"
global_role_dict = {"Achv Role - ???": owned_icon,
                    "Achv Role - Got Cake?": owned_icon,
                    "Achv Role - The Milkman": owned_icon,
                    "Achv Role - Knife Rat": owned_icon,
                    "Achv Role - Try Again": owned_icon,
                    "Achv Role - All Nighter": owned_icon,
                    "Achv Role - Reactive": owned_icon,
                    "Achv Role - Message Master": owned_icon,
                    "Achv Role - Door Greeter": owned_icon,
                    "Achv Role - Koin Kollektor": owned_icon,
                    "Achv Role - Endless Gaming": owned_icon,
                    "Achv Role - Max Activity": owned_icon,
                    "Achv Role - Infinite Time": owned_icon,
                    "Achv Role - Feng Hao Dou Luo": owned_icon}


class PandoraBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)


def run_discord_bot():
    print(sys.version)
    pandora_bot = PandoraBot()

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

    @pandora_bot.command(name='sync', description='Owner only')
    async def sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                synced = await pandora_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @pandora_bot.command(name='reset_sync', description='Owner only')
    async def reset_sync(ctx):
        if ctx.message.author.id == 185530717638230016:
            try:
                global_sync = await pandora_bot.tree.sync(guild=None)
                print(f"Synced! {len(global_sync)} global command(s)")
                synced = await pandora_bot.tree.sync(guild=discord.Object(id=1011375205999968427))
                print(f"Synced! {len(synced)} command(s)")
                await ctx.send('commands synced!')
            except Exception as e:
                print(e)
        else:
            await ctx.send('You must be the owner to use this command!')

    @pandora_bot.event
    async def on_user_update(before, after):
        if before.name != after.name:
            temp_player = player.get_player_by_name(before.name)
            temp_player.player_name = after.name
            temp_player.set_player_field("player_name", after.name)

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
                quest.assign_tokens(player_object, active_boss)
                is_alive = False
                embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
                player_list = [player_object.player_id]
                await sent_message.edit(embed=embed_msg)
                loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                bosses.clear_boss_info(channel_id, player_object.player_id)
                await ctx.send(embed=loot_embed)

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
                    quest.assign_tokens(temp_user, active_boss)
                embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
                await sent_message.edit(embed=embed_msg)
                loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                await ctx.send(embed=loot_embed)

                level, boss_type, boss_tier = bosses.get_boss_details(channel_num)
                bosses.clear_boss_info(channel_id, 0)
                active_boss = bosses.spawn_boss(channel_id, 0, boss_tier, boss_type, level, channel_num)
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

    @pandora_bot.hybrid_command(name='register',
                                description="**/register [USERNAME]** Register a username to begin playing!")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def play(ctx, username: str = "Enter a new username!"):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title="Register",
                                      description="Starting story goes here - Select Class")
            user = ctx.author
            player_name = str(user)
            class_view = menus.ClassSelect(player_name, username)
            await ctx.send(embed=embed_msg, view=class_view)

    @pandora_bot.hybrid_command(name='explore',
                                help="**/explore** Go on an exploration. Costs 25 stamina.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='inlay', help="**/inlay [itemID]** to inlay a specific gem into an equipped item")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def inlay(ctx, item_id: str = "Enter the item ID of the gem"):
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

    @pandora_bot.hybrid_command(name='fort', help="**/fort** to challenge a fortress. Costs 50 stamina.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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
                                try:
                                    await asyncio.sleep(60)
                                    dps = player_object.get_player_damage(active_boss)
                                    active_boss.boss_cHP -= dps
                                    bosses.update_boss_cHP(channel_id, active_boss.player_id, active_boss.boss_cHP)
                                    if active_boss.calculate_hp():
                                        embed_msg = active_boss.create_boss_msg(dps, is_alive)
                                        await sent_message.edit(embed=embed_msg)
                                    else:
                                        quest.assign_tokens(player_object, active_boss)
                                        is_alive = False
                                        embed_msg = bosses.create_dead_boss_embed(channel_id, active_boss, dps)
                                        await sent_message.edit(embed=embed_msg)
                                        player_list = [player_object.player_id]
                                        loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                                        bosses.clear_boss_info(channel_id, player_object.player_id)
                                        await ctx.send(embed=loot_embed)
                                except Exception as e:
                                    print(e)
                        else:
                            await ctx.send("Not enough stamina.")
                    else:
                        await ctx.send("You already have a fortress encounter running.")

                else:
                    await ctx.send("You must have a weapon equipped.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.hybrid_command(name='quest', help="**/quest** to start the story quest")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='gear', help="**/gear** to display your equipped gear")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='inv', help="**/inv** to display your gear and item inventory")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='stamina', help="**/stamina** to display your stamina total")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='stats', help="**/stats** to display your stats")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def stats(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                embed_msg = player_object.get_player_stats(1)
                stat_view = menus.StatView(player_object)
                await ctx.send(embed=embed_msg, view=stat_view)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.hybrid_command(name='admin', help="**/admin** inputs")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='item', help="**/item** to display your item details")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='who', help="**/who [NewUsername]** to set your username")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def who(ctx, new_username: str = "Enter a new username"):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            existing_user = player.get_player_by_name(ctx.author)
            if player.check_username(new_username):
                existing_user.player_username = new_username
                existing_user.set_player_field("player_username", new_username)
                message = f'Got it! I\'ll call you {existing_user.player_username} from now on!'
            else:
                message = f'Sorry that username is taken.'
            await ctx.send(message)

    @pandora_bot.hybrid_command(name='refinery', help="**/refinery** to go to the refinery")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='forge', help="**/forge** to enter the celestial forge")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='bind', help="**/bind** to perform a binding ritual")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='tarot', help="**/tarot** to check your tarot collection")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
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

    @pandora_bot.hybrid_command(name='credits', help="**/credits** to see the credits")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def forge(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            credit_list = "Game created by: Kyle Mistysyn (Archael)"
            # Artists
            credit_list += "\n@labcornerr - Emoji Artist (Fiverr)"
            credit_list += "\n@Nong Dit - Artist (Fiverr)"
            # Programming
            credit_list += "\nBahamutt - Programming Assistance"
            credit_list += "\nPota - Programming Assistance"
            # Testers
            credit_list += "\nZweii - Alpha Tester"
            credit_list += "\nSoulViper - Alpha Tester"
            embed_msg = discord.Embed(colour=discord.Colour.light_gray(),
                                      title="Credits",
                                      description=credit_list)
            embed_msg.set_image(url="https://i.ibb.co/QjWDYG3/forge.jpg")
            await ctx.send(embed=embed_msg)

    @pandora_bot.hybrid_command(name='profile', help="**/profile** to view profile rank card")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def profile(ctx):
        user = ctx.author
        achievement_list = []
        roles_list = [r.name for r in user.roles]
        for role in roles_list:
            if "Achv" in role:
                achievement_list.append(role)
            if "Holder" in role:
                achievement_list.append(role)
        player_object = player.get_player_by_name(user)
        if player_object.player_class != "":
            filepath = pilengine.get_player_profile(player_object, achievement_list)
            file_object = discord.File(filepath)
            await ctx.send(file=file_object)
        else:
            embed_msg = unregistered_message()
            await ctx.send(embed=embed_msg)

    @pandora_bot.hybrid_command(name='sell', help="**/sell [item id] [cost]** to list your item for sale at the bazaar")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def sell(ctx, item_id, cost):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            user = ctx.author
            player_object = player.get_player_by_name(user)
            if player_object.player_class != "":
                if inventory.if_custom_exists(item_id):
                    selected_item = inventory.read_custom_item(item_id)
                    response = player_object.check_equipped(selected_item)
                    if response == "":
                        bazaar.list_custom_item(selected_item, cost)
                        await ctx.send(f"Item {item_id} has been listed for {cost} lotus coins.")
                    else:
                        await ctx.send(response)
                else:
                    await ctx.send(f"Item {item_id} could not be listed.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    def unregistered_message():
        register_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                       title="Unregistered",
                                       description="Please register using !register to play.")
        return register_embed

    pandora_bot.run(TOKEN)
