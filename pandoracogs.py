import pandorabot
import player
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import menus
import pact
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
            if player_list is not None:
                for player_user in player_list:
                    pact_object = pact.Pact(player_user.pact)
                    max_stamina = 5000 if pact_object.pact_variant != "Sloth" else 2500
                    new_stamina_value = player_user.player_stamina + 25
                    if new_stamina_value > max_stamina:
                        new_stamina_value = max_stamina
                    player_user.set_player_field("player_stamina", new_stamina_value)
