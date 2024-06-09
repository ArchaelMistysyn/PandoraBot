# General imports
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.ui import Button, View
from discord import app_commands
import asyncio
import pandas as pd
import re
import sys
import random
from datetime import datetime as dt, timedelta

import globalitems
# Data imports
import globalitems as gli
import sharedmethods as sm
import itemdata
from pandoradb import run_query as rq

# Core imports
import player
import quest
import inventory
import menus

# Combat imports
import encounters
import bosses

# Misc imports
import leaderboards
import skillpaths
import pilengine
import adventure
import fishing

# Item/crafting imports
import loot
import itemrolls
import tarot
import insignia
import forge
import trading

# Trade imports
import market
import bazaar
import infuse

# Cog imports
import pandoracogs

# Database imports
from pandoradb import close_database_session

guild_id = 1011375205999968427

# Get Bot Token
token_info = None
with open("pandora_bot_token.txt", 'r') as token_file:
    for line in token_file:
        token_info = line
TOKEN = token_info


class PandoraBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())


def run_discord_bot():
    print(sys.version)
    pandora_bot = PandoraBot()

    class CommandPlaceholder:
        def __init__(self, category):
            self.category = category

    @pandora_bot.event
    async def on_ready():
        print(f'{pandora_bot.user} Online!')
        pandoracogs.StaminaCog(pandora_bot)
        pandora_bot.help_command = CustomHelpCommand()

    def set_command_category(category, command_position):
        def decorator(func):
            func.category_type, func.position = category, command_position
            return func
        return decorator

    async def on_shutdown():
        print("Pandora Bot Off")
        try:
            await close_database_session()
            await pandora_bot.close()
        except Exception as e:
            print(f"Shutdown Error: {e}")

    class CustomHelpCommand(commands.DefaultHelpCommand):
        def __init__(self):
            super().__init__()

        async def send_bot_help(self, mapping):
            embed = discord.Embed(title="Help Command Menu")
            embed_msg = menus.build_help_embed(category_dict, 'info')
            help_view = menus.HelpView(category_dict)
            await self.get_destination().send(embed=embed_msg, view=help_view)

        async def send_command_help(self, command):
            # Customize the help message when !help <command> is used
            embed = discord.Embed(title=f"Help for (/{command.name}) Command")
            embed.add_field(name="Usage", value=f"```{self.get_command_signature(command)}```", inline=False)
            embed.add_field(name="Description", value=command.help, inline=False)
            await self.get_destination().send(embed=embed)

    # Admin Commands
    async def admin_verification(ctx_object, return_target: discord.User = None, auth="GameAdmin"):
        auth_dict = {"GameAdmin": gli.GM_id_dict.keys(), "Archael": gli.bot_admin_ids}
        if ctx_object.author.id not in auth_dict[auth]:
            await ctx.send("Only game admins can use this command.")
            return True, None, None
        player_obj = await sm.check_registration(ctx_object)
        if player_obj is None:
            return True, None, None
        target_player = player_obj
        if return_target is not None:
            target_player = await player.get_player_by_discord(return_target.id)
        if target_player.player_id == 0:
            await ctx.send(f"Selected user is not registered.")
            return True, None, None
        return False, player_obj, target_player

    async def validate_admin_inputs(ctx_obj, item_id, value, id_check="nocheck", value_check="nocheck"):
        if (id_check == "NonGear" and item_id == "") or (id_check == "gear" and item_id == 0):
            await ctx_obj.send(f"Item ID not recognized.")
            return True
        if (value_check == "numeric" and not value.isnumeric()) or (value_check == "alpha" and not value.isalnum()):
            await ctx_obj.send(f"Value {value} must be a(n) {value_check} data type.")
            return True
        return False

    @set_command_category('admin', 0)
    @pandora_bot.command(name='sync', help="Run with ! to sync. Archael Only.")
    async def sync(ctx, method="default"):
        await ctx.defer()
        trigger_return, _, _ = await admin_verification(ctx)
        if trigger_return:
            return
        if method == "reset":
            global_sync = await pandora_bot.tree.sync(guild=None)
            print(f"Pandora Bot Synced! {len(global_sync)} global command(s)")
        synced = await pandora_bot.tree.sync(guild=discord.Object(id=guild_id))
        print(f"Pandora Bot Synced! {len(synced)} command(s)")
        await ctx.send('Pandora Bot commands synced!')

    @set_command_category('admin', 1)
    @pandora_bot.hybrid_command(name='generategear', help="Admin gear item generation.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def GenerateGear(ctx, target_user: discord.User = None, tier=1, elements="0;0;0;0;0;0;0;0;0", item_type="W",
                           base_type="", class_name="Knight", enhance=0, quality=1,
                           base_stat=1.0, bonus_stat=None, base_dmg_min=0, base_dmg_max=0, num_sockets=0,
                           roll1="", roll2="", roll3="", roll4="", roll5="", roll6=""):
        trigger_return, player_obj, target_player = await admin_verification(ctx, return_target=target_user)
        await ctx.defer()
        if trigger_return:
            return
        rolls, base_dmg = [roll1, roll2, roll3, roll4, roll5, roll6], [base_dmg_min, base_dmg_max]
        new_item = await inventory.generate_item(ctx, target_player, tier, elements, item_type, base_type, class_name,
                                                 enhance, quality, base_stat, bonus_stat, base_dmg, num_sockets, rolls)
        if new_item is not None:
            await ctx.send(f'Admin task completed. Created item id: {new_item.item_id}')

    @set_command_category('admin', 2)
    @pandora_bot.hybrid_command(name='itemmanager', help="Admin item commands [SetQTY, Delete]")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def ItemManager(ctx, method="", target_user: discord.User = None, item_id="", value="0"):
        await ctx.defer()
        trigger_return, player_obj, target_player = await admin_verification(ctx, return_target=target_user)
        if trigger_return:
            return
        if method == "SetQTY":
            target_item = inventory.BasicItem(item_id)
            if await validate_admin_inputs(ctx, target_item.item_id, value, id_check="NonGear", value_check="numeric"):
                return
            stock = await inventory.check_stock(target_player, target_item.item_id)
            await inventory.update_stock(target_player, target_item.item_id, (int(value) - stock))
        if method == "Delete":
            target_item = await inventory.read_custom_item(item_id)
            if await validate_admin_inputs(ctx, target_item.item_id, None, id_check="gear"):
                return
            await target_player.unequip(target_item)
            inventory.delete_item(target_player, target_item)
        await ctx.send('Admin task completed.')

    @set_command_category('admin', 3)
    @pandora_bot.hybrid_command(name='playermanager', help="Admin player commands. [See admin wiki for options]")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def PlayerManager(ctx, method="", target_user: discord.User = None, value="0"):
        await ctx.defer()
        trigger_return, player_obj, target_player = await admin_verification(ctx, return_target=target_user)
        if trigger_return:
            return
        if method in ["coins", "level", "echelon", "quest", "exp"]:
            if await validate_admin_inputs(ctx, None, value, value_check="numeric"):
                return
            target_player.set_player_field(f"player_{method}", int(value))
        elif method in ["class", "name"]:
            if await validate_admin_inputs(ctx, None, value, value_check="alpha"):
                return
            target_player.set_player_field(f"player_{method}", int(value))
        elif method in ["cooldown"]:
            if await validate_admin_inputs(ctx, None, value, value_check="alpha"):
                return
            if value not in ["manifest", "arena", "fishing"]:
                await ctx.send(f'Cooldown value "{value}" not recognized.')
                return
            target_player.clear_cooldown(value)
        await ctx.send('Admin task completed.')

    @set_command_category('admin', 4)
    @pandora_bot.hybrid_command(name='archcommand', help="Admin player commands. See admin wiki for options.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def ArchCommand(ctx, keyword="", value="0"):
        await ctx.defer()
        trigger_return, player_obj, _ = await admin_verification(ctx, auth="Archael")
        if trigger_return:
            return
        if keyword == "LBrerank":
            await leaderboards.rerank_leaderboard(ctx)
            await ctx.send(f"Admin leaderboard task completed.")
        elif keyword == "MergeGear":
            count = 0
            for (_, low_types), high_types in zip(gli.category_names.items(), gli.weapon_list_high):
                for _, name in low_types.items():
                    count += pilengine.generate_and_combine_gear(name, end_tier=4)
                for name in high_types:
                    count += pilengine.generate_and_combine_gear(name, start_tier=5, fetch_type=True)
            non_weapon_list = ["Armour", "Greaves", "Amulet", "Wings", "Crest", "Gem", "Pact"]
            for gear_type in non_weapon_list:
                count += pilengine.generate_and_combine_gear(gear_type)
            await ctx.send(f"Admin item task completed. Task Count: {count}")
        elif keyword == "MergeNongear":
            count = pilengine.generate_and_combine_images()
            await ctx.send(f"Admin item task completed. Task Count: {count}")
        elif keyword == "TestNotification":
            test_dict = {"Level": 1, "Achievement": "Echelon 9", "Item": "LightStar"}
            if value not in test_dict:
                await ctx.send("Invalid notification type")
                return
            await sm.send_notification(ctx, player_obj, value, test_dict[value])
        elif keyword == "Sync":
            synced = await pandora_bot.tree.sync(guild=discord.Object(id=guild_id))
            print(f"Pandora Bot Synced! {len(synced)} command(s)")
            await ctx.send('Pandora Bot commands synced!')
        elif keyword == "Startup":
            await encounters.startup_clear_automaps()
            await bosses.clear_boss_info(ctx.channel.id, "All")
            await ctx.send('Pandora Bot startup tasks completed!')
        elif keyword == "Test":
            title = ""
            description = gli.t57_hpbar_empty[0]
            print(description)
            test_embed = discord.Embed(colour=discord.Colour.red(), title=title, description=description)
            await ctx.send(embed=test_embed)

    @set_command_category('admin', 5)
    @pandora_bot.hybrid_command(name='shutdown', help="Admin shutdown command. Admin Only.")
    @app_commands.guilds(discord.Object(id=1011375205999968427))
    async def shutdown(ctx):
        await ctx.defer()
        trigger_return, player_obj, _ = await admin_verification(ctx)
        if trigger_return:
            return
        message, header = f"Turned off by Admin: {player_obj.player_username}", "Pandora Bot Shutdown"
        file_path = pilengine.build_message_box(player_obj, message, header=header)
        await ctx.send(file=discord.File(file_path))
        await on_shutdown()

    # Game Commands
    @set_command_category('game', 0)
    @pandora_bot.hybrid_command(name='map', help="Explore! Stamina Cost: 200 + 50/map tier")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def expedition(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        title, description = "Map Exploration", "Please select an expedition."
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        embed_msg.set_image(url="")
        map_select_view = adventure.MapSelectView(ctx, player_obj, embed_msg)
        await ctx.send(embed=embed_msg, view=map_select_view)

    @set_command_category('game', 1)
    @pandora_bot.hybrid_command(name='quest', help="Check and hand-in quests.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def story_quest(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        current_quest = player_obj.player_quest
        if current_quest <= 55:
            quest_object = quest.quest_list[player_obj.player_quest]
            quest_message = await quest_object.get_quest_embed(player_obj)
            quest_view = quest.QuestView(ctx, player_obj, quest_object)
            await ctx.send(embed=quest_message, view=quest_view)
            return
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title="Quests", description="All Clear!")
        await ctx.send(embed=embed_msg)

    @set_command_category('game', 2)
    @pandora_bot.hybrid_command(name='stamina', help="Display your stamina and use potions.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def stamina(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        embed_msg = await player_obj.create_stamina_embed()
        stamina_view = menus.StaminaView(player_obj)
        await ctx.send(embed=embed_msg, view=stamina_view)

    @set_command_category('game', 3)
    @pandora_bot.hybrid_command(name='points', help="Assign your skill points.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def points(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        embed_msg = await skillpaths.create_path_embed(player_obj)
        if player_obj.player_quest == 17:
            quest.assign_unique_tokens(player_obj, "Arbiter")
        points_view = menus.PointsView(player_obj)
        await ctx.send(embed=embed_msg, view=points_view)

    @set_command_category('game', 4)
    @pandora_bot.hybrid_command(name='manifest', help="Manifest an echo to perform a task. Cost: 500 Stamina")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def manifest(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        difference, method_info = player_obj.check_cooldown("manifest")
        colour, _ = sm.get_gear_tier_colours(player_obj.player_echelon)
        num_hours = 14 + player_obj.player_echelon

        # Handle existing cooldown.
        if difference:
            wait_time = timedelta(hours=num_hours)
            cooldown = wait_time - difference
            if difference <= wait_time:
                cooldown_timer = int(cooldown.total_seconds() / 60 / 60)
                time_msg = f"Your manifestation will return in {cooldown_timer} hours."
                embed_msg = discord.Embed(colour=colour, title="Echo Manifestation", description=time_msg)
                new_view = adventure.SkipView(ctx, player_obj, method_info)
            else:
                player_obj.clear_cooldown("manifest")
                embed_msg = await adventure.build_manifest_return_embed(ctx, player_obj, method_info, colour)
                new_view = adventure.RepeatView(ctx, player_obj, method_info)
            await ctx.send(embed=embed_msg, view=new_view)
            return

        # Load card or handle proxy. Build the embed.
        embed_msg = discord.Embed(colour=colour)
        e_tarot = tarot.TarotCard(player_obj.player_id, "II", 0, 0, 0)
        if player_obj.equipped_tarot == "":
            embed_msg.title = "Pandora, The Celestial"
            embed_msg.description = ("You don't seem to have any tarot cards set to perform echo manifestation. "
                                     "Let's divide and conquer. I'll handle the task for you. What would you "
                                     "like me to help with?")
            new_view = adventure.ManifestView(ctx, player_obj, embed_msg, e_tarot, colour, num_hours)
            await ctx.send(embed=embed_msg, view=new_view)
            return
        e_tarot = await tarot.check_tarot(player_obj.player_id, tarot.card_dict[player_obj.equipped_tarot][0])
        embed_msg.set_image(url=e_tarot.card_image_link)
        embed_msg.title = f"Echo of {e_tarot.card_name}"
        embed_msg.description = "What do you need me to help you with?"
        display_stars = sm.display_stars(e_tarot.num_stars)
        embed_msg.description += f"\nSelected Tarot Rating: {display_stars}"
        new_view = adventure.ManifestView(ctx, player_obj, embed_msg, e_tarot, colour, num_hours)
        await ctx.send(embed=embed_msg, view=new_view)

    @set_command_category('game', 5)
    @pandora_bot.hybrid_command(name='chest', help="Open Chests.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def open_chest(ctx, quantity="1"):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        Chest_id = "Chest"
        loot_item = inventory.BasicItem(Chest_id)
        Chest_stock = await inventory.check_stock(player_obj, Chest_id)
        if not quantity.isnumeric():
            if quantity != "all":
                await ctx.send("Enter a valid number or 'all' in the quantity field.")
                return
            quantity = min(50, Chest_stock)
        else:
            quantity = int(quantity)
        if quantity <= 0:
            await ctx.send(sm.get_stock_msg(loot_item, 0))
            return
        if Chest_stock < quantity:
            stock_msg = sm.get_stock_msg(loot_item, Chest_stock, quantity)
            await ctx.send(stock_msg)
            return
        await inventory.update_stock(player_obj, Chest_id, (-1 * quantity))
        extension = f"Chest{'s' if quantity > 1 else ''}"
        title_msg = f"{player_obj.player_username}: Opening {quantity} {extension}!"
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title=title_msg, description="Feeling lucky?")
        reward_list = loot.generate_random_item(quantity=quantity)
        description, highest_tier, notifications = "", 1, []
        for (reward_id, item_qty) in reward_list:
            reward_object = inventory.BasicItem(reward_id)
            highest_tier = max(highest_tier, reward_object.item_tier)
            description += f"{reward_object.item_emoji} {item_qty}x {reward_object.item_name}\n"
            if sm.check_rare_item(reward_object.item_id):
                notifications.append((reward_object.item_id, player_obj))
        # Update the data and messages.
        batch_df = sm.list_to_batch(player_obj, reward_list)
        await inventory.update_stock(None, None, None, batch=batch_df)

        # Open the chests.
        sent_msg = await ctx.send(embed=embed_msg)
        opening_chest = ""
        for t in range(1, highest_tier + 1):
            embed_msg.clear_fields()
            tier_colour, tier_icon = sm.get_gear_tier_colours(t)
            opening_chest += tier_icon
            embed_msg.add_field(name="", value=opening_chest)
            await sent_msg.edit(embed=embed_msg)
            await asyncio.sleep(1)
        title = f"{player_obj.player_username}: {quantity} {extension} Opened!"
        embed_msg = discord.Embed(colour=discord.Colour.gold(), title=title, description=description)
        await sent_msg.edit(embed=embed_msg)
        for item_id, player_obj in notifications:
            await sm.send_notification(ctx, player_obj, "Item", item_id)

    @set_command_category('game', 6)
    @pandora_bot.hybrid_command(name='trove', help="Open all troves!")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def trove(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        trove_details = []
        total_stock = 0
        # Get the trove data.
        for trove_tier in range(8):
            trove_id = f"Trove{trove_tier + 1}"
            stock_count = await inventory.check_stock(player_obj, trove_id)
            total_stock += stock_count
            trove_details.append((trove_id, (-1 * stock_count)))
        # Check that there are troves before consuming the trove items.
        if total_stock <= 0:
            await ctx.send(f"No troves in inventory.")
            return
        trove_df = sm.list_to_batch(player_obj, trove_details)
        await inventory.update_stock(None, None, None, batch=trove_df)
        # Build the message.
        extension = f"Trove{'s' if total_stock > 1 else ''}"
        title_msg = f"{player_obj.player_username}: Opening {total_stock:,} {extension}!"
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title=title_msg,  description="Feeling lucky?")
        message = await ctx.send(embed=embed_msg)
        # Handle the opening.
        reward_coins = 0
        for trove_index, (trove_id, trove_qty) in enumerate(trove_details):
            if trove_qty != 0:
                _, tier_icon = sm.get_gear_tier_colours(trove_index + 1)
                loot_msg = tier_icon
                trove_object = inventory.BasicItem(trove_id)
                trove_coins, trove_msg = loot.generate_trove_reward(trove_object, abs(trove_qty))
                reward_coins += trove_coins
                coin_msg = player_obj.adjust_coins(trove_coins)
                loot_msg += f" {trove_msg}{gli.coin_icon} {coin_msg} lotus coins!\n"
                embed_msg.add_field(name="", value=loot_msg, inline=False)
                await message.edit(embed=embed_msg)
                await asyncio.sleep(2)
        # Finalize the output.
        title_msg = f"{player_obj.player_username}: {total_stock:,} {extension} Opened!"
        loot_msg = f"TOTAL: {gli.coin_icon} {reward_coins:,}x lotus coins!\n"
        embed_msg.title = title_msg
        embed_msg.add_field(name="", value=loot_msg, inline=False)
        await message.edit(embed=embed_msg)

    @set_command_category('game', 7)
    @pandora_bot.hybrid_command(name='sanctuary', help="Speak with Fleur in the lotus sanctuary of the divine plane.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def sanctuary(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        title = "Fleur, Oracle of the True Laws"
        if player_obj.player_quest < 48:
            denial_msg = "The sanctuary radiates with divinity. Entry is impossible."
            embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="???", description=denial_msg)
            await ctx.send(embed=embed_msg)
            return
        entry_msg = ("Have you come to desecrate my holy gardens once more? Well, I suppose it no longer matters, "
                     "I know you will inevitably find what you desire even without my guidance. "
                     "If you intend to sever the divine lotus, then I suppose the rest are nothing but pretty flowers.")
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=title, description=entry_msg)
        embed_msg.set_image(url=gli.sanctuary_img)
        await ctx.send(embed=embed_msg, view=market.LotusSelectView(player_obj))

    @set_command_category('game', 8)
    @pandora_bot.hybrid_command(name='cathedral', help="Speak with Yubelle in the cathedral of the divine plane.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def cathedral(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        title = "Yubelle, Adjudicator the True Laws"
        if player_obj.player_quest < 51:
            denial_msg = "The cathedral radiates with divinity. Entry is impossible."
            embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="???", description=denial_msg)
            await ctx.send(embed=embed_msg)
            return
        entry_msg = ("You would still follow Pandora's path in her place? Very well, I am no longer in a position "
                     "to object. I suppose such things do indeed fall within my purview.")
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=title, description=entry_msg)
        embed_msg.set_image(url=gli.cathedral_img)
        await ctx.send(embed=embed_msg, view=tarot.SearchTierView(player_obj, cathedral=True))

    @set_command_category('fish', 9)
    @pandora_bot.hybrid_command(name='fishing', help="Catch a fish! Consumes 250 stamina.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def catch_fish(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        await fishing.go_fishing(ctx, player_obj)

    # Location Commands
    @set_command_category('location', 0)
    @pandora_bot.hybrid_command(name='town', help="Go into town [Refinery, Alchemist, Market, Bazaar]")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def enter_town(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_quest == 11:
            quest.assign_unique_tokens(player_obj, "Town")
        location_view = menus.TownView(player_obj)
        title, description = "Nearby Town", "A bustling town thriving with opportunity."
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        embed_msg.set_image(url="")
        await ctx.send(embed=embed_msg, view=location_view)

    @set_command_category('location', 1)
    @pandora_bot.hybrid_command(name='celestial', help="Enter Pandora's Celestial Realm [Forge, Planetarium]")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def enter_celestial(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        location_view = menus.CelestialView(player_obj)
        title, description = "Celestial Realm", "Pandora's domain and home to her celestial forge."
        embed_msg = discord.Embed(colour=discord.Colour.dark_purple(), title=title, description=description)
        embed_msg.set_image(url="")
        await ctx.send(embed=embed_msg, view=location_view)

    @set_command_category('location', 2)
    @pandora_bot.hybrid_command(name='divine', help="Cross into the Divine Plane [Arbiters, Sanctuary]")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def enter_divine(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        location_view = menus.DivineView(player_obj)
        title, description = "Divine Plane", "You are permitted to visit the higher plane by the grace of the arbiters."
        embed_msg = discord.Embed(colour=discord.Colour.gold(), title=title, description=description)
        embed_msg.set_image(url="")
        await ctx.send(embed=embed_msg, view=location_view)

    # Gear commands
    @set_command_category('gear', 0)
    @pandora_bot.hybrid_command(name='gear', help="Display your equipped gear items.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def gear(ctx, user: discord.User = None):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        target_user = await player.get_player_by_discord(user.id) if user else player_obj
        if target_user.player_class == "":
            await ctx.send("Target user is not registered.")
            return
        if target_user.player_equipped[0] == 0:
            embed_msg = discord.Embed(colour=discord.Colour.dark_gray(),
                                      title="Equipped weapon", description="No weapon is equipped")
            await ctx.send(embed=embed_msg)
            return
        equipped_item = await inventory.read_custom_item(target_user.player_equipped[0])
        embed_msg = await equipped_item.create_citem_embed()
        gear_view = menus.GearView(player_obj, target_user, 0, "Gear")
        await ctx.send(embed=embed_msg, view=gear_view)

    @set_command_category('gear', 1)
    @pandora_bot.hybrid_command(name='inv', help="Display your item and gear inventories.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def inv(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        inventory_view = inventory.BInventoryView(player_obj)
        inv_title = f'{player_obj.player_username}\'s Crafting Inventory:\n'
        player_inventory = inventory.display_binventory(player_obj.player_id, "Crafting")
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=inv_title, description=player_inventory)
        await ctx.send(embed=embed_msg, view=inventory_view)

    @set_command_category('gear', 2)
    @pandora_bot.hybrid_command(name='display', help="Display a specific item.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def display_item(ctx, item_id: str):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        # Assign default outputs.
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title="An item with this ID does not exist.", description=f"Inputted ID: {item_id}")
        if item_id.isnumeric():
            gear_id = int(item_id)
            # Check the item exists
            if not inventory.if_custom_exists(gear_id):
                await ctx.send(embed=embed_msg)
                return
            selected_item = await inventory.read_custom_item(gear_id)
            embed_msg = await selected_item.create_citem_embed()
            # Check if item is on the bazaar.
            if selected_item.player_owner == -1:
                seller_id = bazaar.get_seller_by_item(gear_id)
                seller_object = await player.get_player_by_id(seller_id)
                owner_msg = f"Listed for sale by: {seller_object.player_username}"
                embed_msg.add_field(name="", value=owner_msg)
                await ctx.send(embed=embed_msg)
                return
            item_owner = await player.get_player_by_id(selected_item.player_owner)
            owner_msg = f"Owned by: {item_owner.player_username}"
            embed_msg.add_field(name="", value=owner_msg)
            # Confirm ownership.
            new_view = None
            if player_obj.player_id == selected_item.player_owner:
                new_view = menus.ManageCustomItemView(player_obj, selected_item)
            await ctx.send(embed=embed_msg, view=new_view)
        elif item_id.isalnum():
            # Check if item exists
            if item_id not in itemdata.itemdata_dict:
                await ctx.send(embed=embed_msg)
                return
            selected_item = inventory.BasicItem(item_id)
            embed_msg = await selected_item.create_bitem_embed(player_obj)
            # item_view = menus.ManageBasicItem(player_obj, selected_item)
            await ctx.send(embed=embed_msg)
            return

    @set_command_category('gear', 3)
    @pandora_bot.hybrid_command(name='tarot', help="View your tarot collection.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def tarot_collection(ctx, specific_card_number: str = ""):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        elif specific_card_number.isdigit():
            card_num = int(specific_card_number)
        elif specific_card_number == "":
            card_num = None
        else:
            card_num = await tarot.get_index_by_key(specific_card_number)
        if card_num is not None and card_num not in range(31):
            await ctx.send("Please enter a valid number or numeral from 0-30. Blank input is accepted.")
            return
        if card_num is not None:
            selected_numeral = tarot.get_key_by_index(card_num)
            embed_msg = await tarot.tarot_menu_embed(player_obj, selected_numeral)
            tarot_card = await tarot.check_tarot(player_obj.player_id, tarot.card_dict[selected_numeral][0])
            tarot_view = tarot.TarotView(player_obj, card_num, tarot_card)
            await ctx.send(embed=embed_msg, view=tarot_view)
            return
        title, description = "Pandora, The Celestial", "Welcome to the planetarium. Sealed tarots are stored here."
        embed_msg = discord.Embed(colour=discord.Colour.magenta(), title=title, description=description)
        completion_count = await tarot.collection_check(player_obj)
        name, value = f"{player_obj.player_username}'s Tarot Collection", f"Completion Total: {completion_count} / 31"
        embed_msg.add_field(name=name, value=value, inline=False)
        embed_msg.set_image(url=gli.planetarium_img)
        tarot_view = tarot.CollectionView(player_obj)
        await ctx.send(embed=embed_msg, view=tarot_view)

    @set_command_category('gear', 4)
    @pandora_bot.hybrid_command(name='engrave', help="Engrave an insignia on your soul.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def engrave(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if player_obj.player_quest == 17:
            quest.assign_unique_tokens(player_obj, "Arbiter")
        title = "Isolde, Soulweaver of the True Laws"
        if player_obj.player_quest < 20:
            description = "You can't yet handle my threads. This is no place for the weak."
            embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
            await ctx.send(embed=embed_msg)
            return
        description = "You've come a long way from home child. Tell me, what kind of power do you seek?"
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        insignia_view = insignia.InsigniaView(player_obj)
        await ctx.send(embed=embed_msg, view=insignia_view)

    @set_command_category('gear', 5)
    @pandora_bot.hybrid_command(name='meld', help="Meld tier 5+ heart jewels.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def meld_item(ctx, base_gem_id: int, secondary_gem_id: int):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        # Initialize default embed
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="Kazyth, Lifeblood of the True Laws",
                                  description="")
        if player_obj.player_quest < 42:
            denial_msg = "Tread carefully adventurer. Drawing too much attention to yourself can prove fatal."
            embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="???", description=denial_msg)
            await ctx.send(embed=embed_msg)
            return
        if player_obj.player_quest == 42:
            quest.assign_unique_tokens(player_obj, "Meld")

        # Confirm gems are valid.
        async def can_meld(input_gem_id, command_user):
            if not inventory.if_custom_exists(input_gem_id):
                description = f"Gem id not recognized.\nID: {input_gem_id}"
                return False, None, description
            gem_object = await inventory.read_custom_item(input_gem_id)
            if gem_object.item_tier < 5 or gem_object.item_tier > 8:
                description = f"Gem is not eligible for melding.\nID: {input_gem_id}"
                return False, None, description
            if gem_object.player_owner != command_user.player_id:
                item_owner = await player.get_player_by_id(gem_object.player_owner)
                description = f"Owned by: {item_owner.player_username}"
                return False, None, description
            if gem_object.player_owner == -1:
                seller_id = bazaar.get_seller_by_item(input_gem_id)
                seller_object = await player.get_player_by_id(seller_id)
                description = (f"Jewel item currently listed for sale by: {seller_object.player_username}"
                               f"\nID: {input_gem_id}")
                return False, None, description
            return True, gem_object, None

        # Handle eligibility.
        is_eligible, gem_1, embed_message = await can_meld(base_gem_id, player_obj)
        if not is_eligible:
            embed_msg.description = embed_message
            await ctx.send(embed=embed_msg)
            return
        is_eligible, gem_2, embed_message = await can_meld(secondary_gem_id, player_obj)
        if not is_eligible:
            embed_msg.description = embed_message
            await ctx.send(embed=embed_msg)
            return
        # Build the meld details display.
        embed_msg.description = ("The jewelled heart of greater beings continues to beat long after extraction. "
                                 "Refining living things is not a request to be taken lightly. "
                                 "Will you bear the sins of such blasphemy?\n")
        path_location = int(gem_1.item_bonus_stat[0])
        target_tier = gem_1.item_tier if gem_1.item_tier > gem_2.item_tier else (gem_1.item_tier + 1)
        target_info = f"\nTarget Tier: {target_tier}\nTarget Path: {gli.path_names[path_location]}"
        embed_msg.add_field(name="", value=target_info, inline=False)
        primary_gem_info = itemrolls.display_rolls(gem_1)
        embed_msg.add_field(name=f"Primary Jewel - ID: {base_gem_id}", value=primary_gem_info, inline=False)
        embed_msg.add_field(name="", value="------------------------------", inline=False)
        secondary_gem_info = itemrolls.display_rolls(gem_2)
        embed_msg.add_field(name=f"Secondary Jewel - ID: {secondary_gem_id}", value=secondary_gem_info, inline=False)
        # Build the cost display.
        stock, token_obj = await inventory.check_stock(player_obj, "Token4"), inventory.BasicItem("Token4")
        cost = gem_1.item_tier + gem_2.item_tier - 8
        cost_msg = f"{token_obj.item_emoji} {token_obj.item_name}: {stock}/{cost}"
        embed_msg.add_field(name="Token Cost", value=cost_msg, inline=False)
        # Display the view.
        new_view = forge.MeldView(player_obj, gem_1, gem_2, cost)
        await ctx.send(embed=embed_msg, view=new_view)

    # Trading Commands
    @set_command_category('trade', 0)
    @pandora_bot.hybrid_command(name='sell', help="List a gear item for sale in the bazaar.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def sell(ctx, item_id: int, cost: int):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        num_listings = bazaar.check_num_listings(player_obj)
        if num_listings >= 5:
            await ctx.send("Already at maximum allowed listings.")
            return
        if not inventory.if_custom_exists(item_id):
            await ctx.send(f"Item {item_id} could not be listed.")
            return
        selected_item = await inventory.read_custom_item(item_id)
        if selected_item.item_tier < 5:
            await ctx.send(f"Only tier 5 or higher gear items can be listed at the Bazaar.")
            return
        response = await player_obj.check_equipped(selected_item)
        if response != "":
            await ctx.send(response)
            return
        await bazaar.list_custom_item(selected_item, cost)
        await ctx.send(f"Item {item_id} has been listed for {cost} lotus coins.")

    @set_command_category('trade', 1)
    @pandora_bot.hybrid_command(name='buy', help="Buy an item that is listed on the Bazaar.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def buy(ctx, item_id: int):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if not inventory.if_custom_exists(item_id):
            await ctx.send(f"Item {item_id} does not exist.")
            return
        selected_item = await inventory.read_custom_item(item_id)
        if selected_item.player_owner != -1:
            await ctx.send(f"Item {item_id} is not for sale.")
            return
        embed_msg = await selected_item.create_citem_embed()
        buy_view = menus.BuyView(player_obj, selected_item)
        await ctx.send(embed=embed_msg, view=buy_view)

    @set_command_category('trade', 3)
    @pandora_bot.hybrid_command(name='trade', help="Create a trade offer. [To trade with coins, leave the item blank]")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def trade(ctx, receiving_player: discord.User, offer_item="", offer_qty=0, receive_item="", receive_qty=0):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        target = await player.get_player_by_discord(receiving_player.id)
        if target is None:
            await ctx.send(f"{receiving_player.display_name} is not registered.")
            return
        trade_obj, err_msg = await trading.create_trade(player_obj, target, offer_item, offer_qty, receive_item, receive_qty)
        trade_view = trading.TradeView(trade_obj)
        if err_msg != "":
            await ctx.send(err_msg)
            return
        await ctx.send(embed=trade_obj.trade_msg, view=trade_view)

    @set_command_category('trade', 3)
    @pandora_bot.hybrid_command(name='retrieve', help="Retrieve your items listed on the Bazaar.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def retrieve(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        num_items = await bazaar.retrieve_items(player_obj.player_id)
        await ctx.send(f"{num_items} unsold items retrieved.")

    @set_command_category('trade', 4)
    @pandora_bot.hybrid_command(name='bazaar', help="View the Bazaar.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def view_bazaar(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        embed_msg = await bazaar.show_bazaar_items(player_obj)
        embed_msg.set_image(url=gli.bazaar_img)
        await ctx.send(embed=embed_msg, view=bazaar.BazaarView(player_obj))

    @set_command_category('trade', 5)
    @pandora_bot.hybrid_command(name='market', help="Visit the black market item shop.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def black_market(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        title, description = "Black Market", "Everything has a price."
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        embed_msg.set_image(url=gli.market_img)
        await ctx.send(embed=embed_msg, view=market.TierSelectView(player_obj))

    @set_command_category('trade', 6)
    @pandora_bot.hybrid_command(name='give', help="Transfer ownership of a gear item.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def give(ctx, item_id: int, receiving_player: discord.User):
        await ctx.defer()
        # Confirm registration and allowed channel.
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        # Load item. Check transfer eligibility (Item must exist)
        selected_item = await inventory.read_custom_item(item_id)
        if selected_item is None:
            await ctx.send(f"Transfer Incomplete! Item ID: {item_id} not found!")
            return
        # Check transfer eligibility (Item cannot be equipped)
        check_result = await player_obj.check_equipped(selected_item)
        if check_result != "":
            await ctx.send(f"Transfer Incomplete! {check_result}")
            return
        # Check transfer eligibility (Target user must be registered)
        target_player = await player.get_player_by_discord(receiving_player.id)
        if target_player is None:
            await ctx.send(f"Transfer Incomplete! Target user {receiving_player.name} is not registered.")
            return
        # Check transfer eligibility (Item cannot be listed)
        if selected_item.player_owner == -1:
            await ctx.send(f"Transfer Incomplete! Item ID: {item_id} is currently listed for sale.")
            return
        # Check transfer eligibility (Ownership)
        if player_obj.player_id != selected_item.player_owner:
            owner_player = await player.get_player_by_id(selected_item.player_owner)
            await ctx.send(f"Transfer Incomplete! Item ID: {item_id} owned by {owner_player.player_username}.")
            return
        # Transfer and display item.
        await selected_item.give_item(target_player.player_id)
        header, message = "Transfer Complete!", f"{target_player.player_username} has received Item ID: {item_id}!"
        file_path = pilengine.build_message_box(player_obj, message, header=header)
        await ctx.send(file=discord.File(file_path))

    @set_command_category('trade', 7)
    @pandora_bot.hybrid_command(name='purge', help="Sells all gear in or below a tier. "
                                "Types: [Weapon, Armour, Greaves, Amulet, Wings, Crest, Gems]")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def purge(ctx, tier: int, item_type=""):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        if tier not in range(1, 9):
            await ctx.send("The tier must be between 1 and 8.")
            return
        if item_type not in ["Weapon", "Armour", "Greaves", "Amulet", "Wings", "Crest", "Gems", ""]:
            await ctx.send("Valid Types: [Weapon, Armour, Greaves, Amulet, Wings, Crest, Gems]")
            return
        result_msg = await inventory.purge(player_obj, item_type, tier)
        await ctx.send(result_msg)

    # Crafting Commands
    @set_command_category('craft', 0)
    @pandora_bot.hybrid_command(name='forge', help="Go to Pandora's Celestial Forge")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def celestial_forge(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="Pandora's Celestial Forge", description="")
        name, value = "Pandora, The Celestial", "Let me know what you'd like me to upgrade!"
        embed_msg.add_field(name=name, value=value, inline=False)
        embed_msg.set_image(url=gli.forge_img)
        await ctx.send(embed=embed_msg, view=forge.SelectView(player_obj, "celestial"))

    @set_command_category('craft', 1)
    @pandora_bot.hybrid_command(name='refinery', help="Go to the refinery.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def refinery(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        title, description = "Refinery", "Please select the item to refine"
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        embed_msg.set_image(url=gli.refinery_img)
        await ctx.send(embed=embed_msg, view=forge.RefSelectView(player_obj))

    @set_command_category('craft', 2)
    @pandora_bot.hybrid_command(name='infuse', help="Infuse items using alchemy.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def infusion(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        title, description = "Cloaked Alchemist, Sangam", "I can make anything, if you bring the right stuff."
        embed_msg = discord.Embed(colour=discord.Colour.magenta(), title=title, description=description)
        embed_msg.set_image(url=gli.infuse_img)
        infuse_view = infuse.InfuseView(player_obj)
        await ctx.send(embed=embed_msg, view=infuse_view)

        # Crafting Commands
    @set_command_category('craft', 3)
    @pandora_bot.hybrid_command(name='abyss', help="Go to the ???")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def void_purification(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        e_weapon = await inventory.read_custom_item(player_obj.player_equipped[0])
        if player_obj.player_quest < 38:
            embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="???",
                                      description="A great darkness clouds your path. Entry is impossible.")
            await ctx.send(embed=embed_msg)
            return
        if player_obj.player_quest == 38:
            quest.assign_unique_tokens(player_obj, "Abyss")
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="Echo of Oblivia", description=gli.abyss_msg)
        embed_msg.set_image(url=gli.abyss_img)
        new_view = forge.SelectView(player_obj, "purify")
        await ctx.send(embed=embed_msg, view=new_view)

    @set_command_category('craft', 4)
    @pandora_bot.hybrid_command(name='scribe', help="Speak with Vexia in the divine plane.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def scribe(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        e_weapon = await inventory.read_custom_item(player_obj.player_equipped[0])
        title = "Vexia, Scribe of the True Laws"
        if player_obj.player_quest < 46:
            denial_msg = "I have permitted your passage, but you are not yet qualified to speak with me. Begone."
            embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=title, description=denial_msg)
            await ctx.send(embed=embed_msg)
            return
        entry_msg = ("You are the only recorded mortal to have entered the divine plane. "
                     "We are not your allies, but we will not treat you unfairly."
                     "\nThe oracle has already foretold your failure. Now it need only be written into truth.")
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=title, description=entry_msg)
        embed_msg.set_image(url=gli.forge_img)
        await ctx.send(embed=embed_msg, view=forge.SelectView(player_obj, "custom"))

    # Info commands
    @set_command_category('info', 0)
    @pandora_bot.hybrid_command(name='info', help="Display the help menu.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def help_menu(ctx):
        await ctx.defer()
        embed = discord.Embed(title="Help Command Menu")
        embed_msg = menus.build_help_embed(category_dict, 'info')
        help_view = menus.HelpView(category_dict)
        await ctx.send(embed=embed_msg, view=help_view)

    @set_command_category('info', 1)
    @pandora_bot.hybrid_command(name='register', help="Register a new user.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def play(ctx, username: str):
        await ctx.defer()
        if not any(ctx.channel.id in sl for sl in gli.global_server_channels):
            await ctx.send("You may not run this command in this channel.")
            return
        check_player = await player.get_player_by_discord(ctx.author.id)
        if check_player is not None:
            await ctx.send("You are already registered.")
            return
        if not username.isalpha():
            await ctx.send("Please enter a valid username.")
            return
        if not player.check_username(username):
            await ctx.send("Username already in use.")
            return
        if len(username) > 10:
            await ctx.send("Please enter a username 10 or less characters.")
            return
        register_msg = ('In an ancient ruin, you come across an empty room in which sits a peculiar box. '
                        'Hesitating at first you consider the possibility of a trap or mimic. '
                        'Without a trap in sight, you reach forward and open the box.\n'
                        'A flurry of souls flood the room and spill out into the corridor. '
                        'One pauses and speaks softly into your mind. '
                        '"Everything begins and ends with a wish. What do you wish to be?" '
                        'You think it for only a second and the voice responds with a playful laugh, '
                        '"Let it be so." Then the voice disappears without a trace. '
                        'Silence falls and then all that remains is an '
                        'otherworldly girl staring at you in confusion.')
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title="Register - Select Class",
                                  description=register_msg)
        class_view = menus.ClassSelect(ctx.author.id, username)
        await ctx.send(embed=embed_msg, view=class_view)

    @set_command_category('info', 2)
    @pandora_bot.hybrid_command(name='guide', help="Display basic starter guide.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def guide(ctx):
        await ctx.defer()
        if not any(ctx.channel.id in sl for sl in gli.global_server_channels):
            await ctx.send("You may not run this command in this channel.")
            return
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title=menus.guide_dict[0][0], description=menus.guide_dict[0][1])
        current_guide = "Beginner"
        guide_view = menus.GuideMenu()
        await ctx.send(embed=embed_msg, view=guide_view)

    @set_command_category('info', 3)
    @pandora_bot.hybrid_command(name='stats', help="Display your stats page.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def stats(ctx, user: discord.User = None):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        target_user = player_obj if user is None else await player.get_player_by_discord(user.id)
        if target_user.player_class == "":
            await ctx.send("Selected user is not registered.")
            return
        embed_msg = await target_user.get_player_stats(1)
        stat_view = menus.StatView(player_obj, target_user)
        await ctx.send(embed=embed_msg, view=stat_view)

    @set_command_category('info', 4)
    @pandora_bot.hybrid_command(name='profile', help="View profile rank card.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def profile(ctx, user: discord.User = None):
        await ctx.defer()
        command_user = ctx.author
        achv_list = []
        target_id, user_object = command_user.id, command_user
        if user is not None:
            target_id, user_object = user.id, user
            target_id = user.id
        achv_list = [role.name for role in user_object.roles if "Holder" in role.name or "Herrscher" in role.name]
        target_user = await player.get_player_by_discord(target_id)
        if target_user.player_class == "":
            await ctx.send(f"Target user {user_object.name} is not registered.")
            return
        filepath = pilengine.get_player_profile(target_user, achv_list)
        file_object = discord.File(filepath)
        await ctx.send(file=file_object)

    @set_command_category('info', 4)
    @pandora_bot.hybrid_command(name='leaderboard', help="View the leaderboard.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def leaderboard(ctx):
        await ctx.defer()
        player_obj = await player.get_player_by_discord(ctx.author.id)
        embed_msg = await leaderboards.display_leaderboard("DPS", player_obj.player_id)
        new_view = leaderboards.LeaderbaordView(player_obj)
        await ctx.send(embed=embed_msg, view=new_view)

    @set_command_category('info', 5)
    @pandora_bot.hybrid_command(name='changer', help="Change your class.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def changer(ctx):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        stock = await inventory.check_stock(player_obj, "Token1")
        description = f"Bring me enough tokens and even you can be rewritten.\n{stock} / 50"
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title="Mysmir, Changeling of the True Laws", description=description)
        new_view = menus.ClassChangeView(player_obj)
        await ctx.send(embed=embed_msg, view=new_view)

    @set_command_category('info', 6)
    @pandora_bot.hybrid_command(name='who', help="Set a new username.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def who(ctx, new_username: str):
        await ctx.defer()
        player_obj = await sm.check_registration(ctx)
        if player_obj is None:
            return
        Mysmir_title = "Mysmir, Changeling of the True Laws"
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=Mysmir_title, description="")
        if not new_username.isalpha():
            embed_msg.description = "This name is unacceptable. I refuse."
            await ctx.send(embed=embed_msg)
            return
        if not player.check_username(new_username):
            embed_msg.description = "This name belongs to another. I refuse."
            await ctx.send(embed=embed_msg)
            return
        if len(new_username) > 10:
            embed_msg.description = "This name is too long. I refuse."
            await ctx.send(embed=embed_msg)
            return
        token_stock = await inventory.check_stock(player_obj, "Token1")
        if token_stock < 50:
            embed_msg.description = f"I will only help those with sufficient tokens. I refuse.\n{token_stock} / 50"
            await ctx.send(embed=embed_msg)
            return
        else:
            await inventory.update_stock(player_obj, "Token1", -50)
            player_obj.player_username = new_username
            player_obj.set_player_field("player_username", new_username)
            embed_msg.description = f'{player_obj.player_username} you say? Fine, I accept.'
            await ctx.send(embed=embed_msg)

    @set_command_category('info', 8)
    @pandora_bot.hybrid_command(name='credits', help="Displays the game credits.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def credits_list(ctx):
        await ctx.defer()
        title = "Game created by: Kyle Mistysyn (Archael)"
        artist_data = [
            ("Daerun", "Character Illustrator (Upwork)"),
            ("Nong Dit @Nong Dit", "Frame Artist (Fiverr)"),
            ("Aztra.studio @Artherrera", "Emoji/Icon Artist (Fiverr)"),
            ("Labs @labcornerr", "Emoji/Icon Artist (Fiverr)"),
            ("Daimiuk @daimiuk", "Scene/Icon Artist (Fiverr)"),
            ("Faris @bigbullmonk", "Icon Artist (Fiverr)"),
            ("Claudia", "Scene Artist (Volunteer)"),
            ("Volff", "Photoshop Editing (Volunteer)")
        ]
        programming_data = [
            ("Archael", "Programmer")
        ]
        tester_data = [
            ("Zweii", "Alpha Tester"),
            ("SoulViper", "Alpha Tester"),
            ("Kaelen", "Alpha Tester"),
            ("Volff", "Alpha Tester")
        ]
        misc_data = [
            ("Bahamutt", "Programming Support"),
            ("Pota", "Programming Support")]
        artist_list = "\n".join(f"**{name}** - {role}" for name, role in artist_data)
        programmer_list = "\n".join(f"**{name}** - {role}" for name, role in programming_data)
        tester_list = "\n".join(f"**{name}** - {role}" for name, role in tester_data)
        misc_list = "\n".join(f"**{name}** - {role}" for name, role in misc_data)
        # Unauthorized use of this bot, it's associated contents, code, and assets are strictly prohibited.
        copy_msg = f"© 2024 Kyle Mistysyn. All rights reserved."
        embed_msg = discord.Embed(colour=discord.Colour.light_gray(), title=title, description="")
        embed_msg.add_field(name="__Artists__", value=artist_list.rstrip(), inline=False)
        embed_msg.add_field(name="__Programmers__", value=programmer_list.rstrip(), inline=False)
        embed_msg.add_field(name="__Testers__", value=tester_list.rstrip(), inline=False)
        embed_msg.add_field(name="__Misc__", value=misc_list.rstrip(), inline=False)
        embed_msg.set_footer(text=f"Copyright: {copy_msg}")
        embed_msg.set_thumbnail(url=gli.archdragon_logo)
        file_path = pilengine.build_title_box("Pandora Bot Credits")
        await ctx.send(file=discord.File(file_path))
        await ctx.send(embed=embed_msg)

    @set_command_category('misc', 0)
    @pandora_bot.hybrid_command(name='savequote', help="Add a quote to the quote database")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def add_quote(ctx: commands.Context, message_id: str = None):
        await ctx.defer()
        if message_id:
            if not message_id.isnumeric():
                await ctx.send("Message ID must be numeric")
                return
            try:
                message = await ctx.channel.fetch_message(message_id)
            except discord.NotFound:
                await ctx.send("Message not found.")
                return
        elif ctx.message.reference:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        else:
            await ctx.send("You need to reply to a message (! only) or provide a message ID to add a quote.")
            return

        def insert_quote(quote_id, user_discord_id, user_quote, quote_date):
            raw_query = ("INSERT INTO UserQuotes (message_id, user_discord_id, user_quote, quote_date) "
                         "VALUES (:message_id, :discord_id, :quote, :date) "
                         "ON DUPLICATE KEY UPDATE user_discord_id=VALUES(user_discord_id), "
                         "user_quote=VALUES(user_quote), quote_date=VALUES(quote_date)")
            rq(raw_query, params={'message_id': quote_id, 'discord_id': user_discord_id,
                                  'quote': user_quote, 'date': quote_date})

        insert_quote(message.id, message.author.id, message.content, message.created_at.strftime('%Y-%m-%d'))
        await ctx.send(f"Quote successfully added.")

    @set_command_category('misc', 1)
    @pandora_bot.hybrid_command(name='deletequote', help="Remove a quote by message id.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def delete_quote(ctx: commands.Context, message_id: str):
        await ctx.defer()
        if ctx.author.id not in gli.GM_id_dict.keys():
            await ctx.send("Only game admins can execute this command.")
            return
        if not message_id.isnumeric():
            await ctx.send("Message ID must be numeric")
            return
        raw_query = "DELETE FROM UserQuotes WHERE message_id = :message_id"
        rq(raw_query, params={'message_id': message_id})
        await ctx.send(f"Quote {message_id} successfully removed.")

    @set_command_category('misc', 2)
    @pandora_bot.hybrid_command(name='quote', help="Send a random quote. Specific user or quote can be selected.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def post_quote(ctx: commands.Context, target_user: discord.User = None, message_id: str = None):
        await ctx.defer()
        if message_id is not None:
            if not message_id.isnumeric():
                await ctx.send("Message ID must be numeric")
                return
            raw_query = "SELECT * FROM UserQuotes WHERE message_id = :message_id"
            quote_df = rq(raw_query, params={'message_id': message_id}, return_value=True)
        elif target_user is not None:
            raw_query = "SELECT * FROM UserQuotes WHERE user_discord_id = :discord_id"
            quote_df = rq(raw_query, params={'discord_id': target_user.id}, return_value=True)
        else:
            raw_query = "SELECT * FROM UserQuotes"
            quote_df = rq(raw_query, return_value=True)
        if quote_df.empty:
            await ctx.send("No quotes available with these inputs.")
            return
        quote_list = quote_df.to_dict(orient='records')
        selected_quote = random.choice(quote_list)
        user_discord_id = selected_quote['user_discord_id']
        user_quote, message_id = selected_quote['user_quote'], selected_quote['message_id']
        quote_date = selected_quote['quote_date']
        user = await pandora_bot.fetch_user(user_discord_id)
        if not user:
            await ctx.send("User not found in the server.")
            return
        quote_embed = discord.Embed(title=user.display_name, description=user_quote, color=discord.Color.blue())
        quote_embed.add_field(name="", value=f"Quoted from {quote_date} [ID: {message_id}]", inline=True)
        quote_embed.set_thumbnail(url=user.avatar)
        await ctx.send(embed=quote_embed)

    @set_command_category('misc', 3)
    @pandora_bot.hybrid_command(name='listquotes', help="List all quotes from a selected user.")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def list_quotes(ctx: commands.Context, target_user: discord.User):
        await ctx.defer()
        raw_query = "SELECT * FROM UserQuotes WHERE user_discord_id = :discord_id"
        quote_df = rq(raw_query, params={'discord_id': target_user.id}, return_value=True)
        if quote_df.empty:
            await ctx.send("No quotes available for this user.")
            return
        quote_list = quote_df.to_dict(orient='records')
        random_quote = random.choice(quote_list)
        user_discord_id = random_quote['user_discord_id']
        user = await pandora_bot.fetch_user(user_discord_id)
        if not user:
            await ctx.send("User not found in the server.")
            return
        max_fields_per_embed = 25
        embed_list = []
        total_quotes = len(quote_list)

        for i in range(0, total_quotes, max_fields_per_embed):
            chunk = quote_list[i:i + max_fields_per_embed]
            title, description = user.display_name, f"Quotes {i + 1}-{i + len(chunk)} of {total_quotes}"
            quote_embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
            for selected_quote in chunk:
                user_quote, message_id = selected_quote['user_quote'], selected_quote['message_id']
                quote_date = selected_quote['quote_date']
                quote_embed.add_field(name=f"Date: {quote_date} [ID: {message_id}]", value=user_quote, inline=False)
            quote_embed.set_thumbnail(url=user.avatar.url if user.avatar else discord.Embed.Empty)
            embed_list.append(quote_embed)
        for embed in embed_list:
            await ctx.send(embed=embed)

    def build_category_dict():
        temp_dict = {}
        for command in pandora_bot.walk_commands():
            if hasattr(command, 'category_type'):
                category_name = command.category_type
                if category_name not in temp_dict:
                    temp_dict[category_name] = []
                temp_dict[category_name].append((command.name, command.help, command.position))
        return temp_dict

    category_dict = build_category_dict()
    pandora_bot.run(TOKEN)
