import pandorabot
import player
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import menus
import asyncio


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
