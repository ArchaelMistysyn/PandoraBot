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
channel_list_2 = [1156308986065338448, 1156309099970048070, 1156318343180071014]
global_server_channels = [channel_list_wiki, channel_list_2]


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
        
        for server in global_server_channels:
            command_channel_id = server[0]
            cmd_ctx = pandora_bot.get_channel(command_channel_id)
            raid_channel_id = server[1]
            raid_ctx = pandora_bot.get_channel(raid_channel_id)
            pandora_bot.loop.create_task(stamina_manager(600, cmd_ctx))
            pandora_bot.loop.create_task(timed_task(60, raid_channel_id, raid_ctx))

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
            outcome += bosses.add_participating_player(clicked_by.player_id)

            await interaction.response.send_message(outcome)

    @pandora_bot.event
    async def timed_task(duration_seconds, channel_id, ctx):
        # initialize the boss post
        boss_type = "Dragon"
        new_boss_tier = bosses.get_random_bosstier(boss_type)
        level = random.randint(0, 9)
        level += new_boss_tier * 10
        active_boss = bosses.spawn_boss(new_boss_tier, boss_type, level)
        embed_msg = active_boss.create_boss_msg(0, True)
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
                embed_msg = active_boss.create_boss_msg(dps, True)
                await sent_message.edit(embed=embed_msg)
            else:
                embed_msg = bosses.create_dead_boss_embed(active_boss, dps)
                loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                await sent_message.edit(embed=loot_embed)

                # spawn a new boss
                random_number = random.randint(0, 1)
                if active_boss.boss_type_num == 3 or random_number == 0:
                    boss_type = "Dragon"
                else:
                    boss_type = "Demon"
                new_boss_tier = bosses.get_random_bosstier(boss_type)
                level = random.randint(0, 9)
                level += new_boss_tier * 10
                active_boss = bosses.spawn_boss(new_boss_tier, boss_type, level)
                bosses.clear_list()
                player_list.clear()
                embed_msg = active_boss.create_boss_msg(0, True)
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

    @pandora_bot.command(name='register', help="**!register [USERNAME]** Register a username to begin playing!")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def play(ctx, username):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title="Register",
                                      description="Starting story goes here - Select Class")
            player_name = str(ctx.author)
            class_view = menus.ClassSelect(player_name, username)
            await ctx.send(embed=embed_msg, view=class_view)

    @pandora_bot.command(name='explore', help="**!explore** to go on an an exploration")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def adventure(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_name = str(ctx.author)
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                player_object.get_equipped()
                player_object.get_player_multipliers(-1, -1)
                if player_object.spend_stamina(25):
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def fort(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_name = ctx.author
            player_object = player.get_player_by_name(player_name)
            if player_object.player_class != "":
                if player_object.spend_stamina(50):
                    # initialize the boss post
                    boss_type = "Fortress"
                    new_boss_tier = bosses.get_random_bosstier(boss_type)
                    active_boss = bosses.spawn_boss(new_boss_tier, boss_type, player_object.player_lvl)
                    is_alive = True
                    embed_msg = active_boss.create_boss_msg(0, is_alive)
                    sent_message = await ctx.send(embed=embed_msg)
                    while is_alive:
                        await asyncio.sleep(60)
                        dps, critical_type = damagecalc.get_player_damage(player_object, active_boss)
                        active_boss.boss_cHP -= dps
                        if active_boss.calculate_hp():
                            embed_msg = active_boss.create_boss_embed(dps, is_alive)
                            await sent_message.edit(embed=embed_msg)
                        else:
                            is_alive = False
                            embed_msg = bosses.create_dead_boss_embed(active_boss, dps)
                            player_list = [player_object.player_id]
                            loot_embed = loot.create_loot_embed(embed_msg, active_boss, player_list)
                            await sent_message.edit(embed=loot_embed)
                else:
                    await ctx.send("Not enough stamina.")
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='quest', help="**!quest** to start the story quest")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def story_quest(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            # quest progression
            player_object = player.get_player_by_name(str(ctx.author))
            current_quest = player_object.player_quest
            if current_quest != 0:
                current_quest = player_object.player_quest
                quest_object = quest.get_quest(current_quest, player_object)
                token_count = player_object.check_tokens(current_quest)
                quest_object.set_quest_output(token_count)
                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                          title=quest_object.quest_title,
                                          description=quest_object.story_message)
                embed_msg.add_field(name=f"Quest", value=quest_object.quest_output, inline=False)
                quest_view = menus.QuestView(player_object, quest_object)
                await ctx.send(embed=embed_msg, view=quest_view)
            elif current_quest >= 50:
                embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                          title="Quests",
                                          description="All quests completed!")
                await ctx.send(embed=embed_msg)
            else:
                embed_msg = unregistered_message()
                await ctx.send(embed=embed_msg)

    @pandora_bot.command(name='gear', help="**!inv** to display your equipped gear")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def gear(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                player_object.get_equipped()
                if player_object.equipped_weapon != 0:
                    equipped_item = inventory.read_custom_item(user.equipped_weapon)
                    embed_msg = equipped_item.create_citem_embed()
                    gear_view = menus.GearView(user)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def inv(ctx):
        if any(ctx.channel.id in sl for sl in global_server_channels):
            player_object = player.get_player_by_name(str(ctx.author))
            if player_object.player_class != "":
                inventory_view = menus.InventoryView(user)

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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
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

    pandora_bot.run(TOKEN)
