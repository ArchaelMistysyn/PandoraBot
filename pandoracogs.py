# General imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import asyncio

# Core imports
import mydb
import player

# Item/crafting imports
import pact


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
            player_list = await player.get_all_users()
            if player_list is not None:
                update_params = []
                for player_user in player_list:
                    pact_object = pact.Pact(player_user.pact)
                    max_stamina = 5000 if pact_object.pact_variant != "Sloth" else 2500
                    new_stamina_value = min(player_user.player_stamina + 25, max_stamina)
                    update_params.append({'player_check': player_user.player_id, 'input_1': new_stamina_value})
                if update_params:
                    raw_query = "UPDATE PlayerList SET player_stamina = :input_1 WHERE player_id = :player_check"
                    mydb.run_single_query(raw_query, batch=True, params=update_params)
