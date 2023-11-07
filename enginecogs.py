import battleengine
import bosses
import player
import combat
import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands, tasks


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
        print(f"Running channel {self.channel_num} raid cycle")
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
        print(f"Running {self.player_object.player_username} solo cycle")
        async with self.lock:
            is_alive = await self.bot.solo_boss(self.combat_tracker, self.player_object, self.active_boss,
                                                self.channel_id, self.sent_message, self.channel_object)
            if not is_alive:
                self.cog_unload()