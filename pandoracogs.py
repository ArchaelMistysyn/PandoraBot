import pandorabot
import player
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import bosses
import menus
import asyncio
import combat


class StaminaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.stamina_manager.start()

    def cog_unload(self):
        self.stamina_manager.cancel()

    @tasks.loop(seconds=600)
    async def stamina_manager(self):
        async with self.lock:
            print("Stamina Assignment Triggered!")
            player_list = player.get_all_users()
            if player_list:
                for player_user in player_list:
                    new_stamina_value = player_user.player_stamina + 10
                    if new_stamina_value > 5000:
                        new_stamina_value = 5000
                    player_user.set_player_field("player_stamina", new_stamina_value)


class RaidCog(commands.Cog):
    def __init__(self, bot, active_boss, channel_id, channel_num, sent_message, channel_object):
        self.bot = bot
        self.active_boss = active_boss
        self.channel_id = channel_id
        self.channel_num = channel_num
        self.sent_message = sent_message
        self.channel_object = channel_object
        self.combat_tracker_list = []
        self.lock = asyncio.Lock()
        self.raid_manager.start()
        print(f"Channel #{self.channel_num}: RaidCog Running")

    def cog_unload(self):
        self.raid_manager.cancel()

    @tasks.loop(seconds=60)
    async def raid_manager(self):
        async with self.lock:
            is_alive = await self.bot.raid_boss(self.combat_tracker_list, self.active_boss, self.channel_id, self.channel_num,
                                                self.sent_message, self.channel_object)
            if not is_alive:
                bosses.clear_boss_info(self.channel_id, 0)
                level, boss_type, boss_tier = bosses.get_boss_details(self.channel_num)
                active_boss = bosses.spawn_boss(self.channel_id, 0, boss_tier, boss_type, level, self.channel_num)
                self.active_boss = active_boss
                self.combat_tracker_list = []
                embed_msg = active_boss.create_boss_embed(0)
                raid_button = menus.RaidView()
                sent_message = await self.channel_object.send(embed=embed_msg, view=raid_button)
                self.sent_message = sent_message


class SoloCog(commands.Cog):
    def __init__(self, bot, player_object, active_boss, channel_id, sent_message, channel_object):
        self.bot = bot
        self.player_object = player_object
        self.active_boss = active_boss
        self.channel_id = channel_id
        self.sent_message = sent_message
        self.channel_object = channel_object
        self.combat_tracker = combat.CombatTracker()
        self.combat_tracker.player_cHP = player_object.player_mHP
        self.lock = asyncio.Lock()
        print(f"{self.player_object.player_username}: SoloCog Running")

    async def run(self):
        self.solo_manager.start()

    def cog_unload(self):
        self.solo_manager.cancel()

    @tasks.loop(seconds=60)
    async def solo_manager(self):
        async with self.lock:
            is_alive = await self.bot.solo_boss(self.combat_tracker, self.player_object, self.active_boss,
                                                self.channel_id, self.sent_message, self.channel_object)
            if not is_alive:
                self.cog_unload()
