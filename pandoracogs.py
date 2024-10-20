# General imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import asyncio
import traceback

# Core imports
import globalitems as gli
from pandoradb import run_query as rqy
import player

# Item/crafting imports
import pact


class StaminaCog(commands.Cog):
    def __init__(self, bot):
        self.bot, self.lock = bot, asyncio.Lock()
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
                    await rqy(raw_query, batch=True, params=update_params)

    @stamina_manager.error
    async def stamina_manager_error(self, e):
        error_channel = self.bot.get_channel(gli.bot_logging_channel)
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        await error_channel.send(f'An error occurred:\n{e}\n```{tb_str}```')


class MetricsCog(commands.Cog):
    def __init__(self, bot):
        self.bot, self.lock = bot, asyncio.Lock()
        self.guild = self.bot.get_guild(1011375205999968427)
        self.metrics_manager.start()

    def cog_unload(self):
        self.metrics_manager.cancel()

    async def run_metrics(self):
        total_members = self.guild.member_count
        online_members = sum(1 for member in self.guild.members if member.status == discord.Status.online)
        offline_members = sum(1 for member in self.guild.members if member.status == discord.Status.offline)
        role_counts = {role.name: len(role.members) for role in self.guild.roles if role.name != "@everyone"}
        message = (
            f"Total Members: {total_members:,}\n"
        )
        metrics_channel = self.bot.get_channel(1156267612783779901)
        if metrics_channel:
            message_obj = await metrics_channel.fetch_message(1296207066284953664)
            await message_obj.edit(content=message)

    @tasks.loop(seconds=3600)
    async def metrics_manager(self):
        async with self.lock:
            await self.run_metrics()

    @metrics_manager.error
    async def metrics_manager_error(self, e):
        error_channel = self.bot.get_channel(gli.bot_logging_channel)
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        await error_channel.send(f'An error occurred:\n{e}\n```{tb_str}```')
