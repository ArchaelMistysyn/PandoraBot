import pandorabot
import player
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks


class StaminaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stamina_manager.start()

    def cog_unload(self):
        self.stamina_manager.cancel()

    @tasks.loop(seconds=600)
    async def stamina_manager(self):
        print("Stamina Assignment Triggered!")
        player_list = player.get_all_users()
        for player_user in player_list:
            new_stamina_value = player_user.player_stamina + 5
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
        self.raid_manager.start()
        print(f"Channel #{self.channel_num}: RaidCog Running")

    def cog_unload(self):
        self.raid_manager.cancel()

    @tasks.loop(seconds=60)
    async def raid_manager(self):
        is_alive = await self.bot.raid_boss(self.active_boss, self.channel_id, self.channel_num,
                                            self.sent_message, self.channel_object)
        if not is_alive:
            self.cog_unload()


class SoloCog(commands.Cog):
    def __init__(self, bot, player_object, active_boss, channel_id, sent_message, channel_object):
        self.bot = bot
        self.player_object = player_object
        self.active_boss = active_boss
        self.channel_id = channel_id
        self.sent_message = sent_message
        self.channel_object = channel_object
        self.solo_manager.start()
        print(f"{self.player_object.player_username}: SoloCog Running")

    def cog_unload(self):
        self.solo_manager.cancel()

    @tasks.loop(seconds=60)
    async def solo_manager(self):
        is_alive = await self.bot.solo_boss(self.player_object, self.active_boss,
                                            self.channel_id, self.sent_message, self.channel_object)
        if not is_alive:
            self.cog_unload()
