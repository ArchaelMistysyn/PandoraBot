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
import timezone

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
        self.credit_manager.start()

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
        metrics_channel = self.bot.get_channel(gli.metrics_channel)
        if metrics_channel:
            message_obj = await metrics_channel.fetch_message(gli.metrics_message_id)
            await message_obj.edit(content=message)

    import datetime

    async def run_credit(self):
        # Note for future self. This can be more efficient done via batches if needed.
        now = timezone.get_now()
        if now.day != 1:
            return
        eligible_roles = [role for role in self.guild.roles if "Subscriber" in role.name]
        credited_users = []
        for member in self.guild.members:
            if any(role in member.roles for role in eligible_roles):
                discord_id = member.id
                current = await player.check_credit(discord_id)
                if current is None:
                    await player.set_credit(discord_id, 1)
                    new_credit = 1
                else:
                    new_credit = current + 1
                    await player.update_credit(discord_id, new_credit)
                credited_users.append((member, new_credit))
        for user, credit in credited_users:
            credit_msg = (f"You've received 1 ArchDragon Store credit. Your new balance is {credit:,}.\n"
                          f"Credit is deducted as the highest eligible gift card value: 10, 25, 50, 100, 250, 500\n"
                          f"Message me 'cashout' or open a basic ticket in the server to request your gift card.")
            await user.send(credit_msg)

    @tasks.loop(seconds=3600)
    async def metrics_manager(self):
        async with self.lock:
            await self.run_metrics()

    @tasks.loop(seconds=86401)
    async def credit_manager(self):
        async with self.lock:
            await self.run_credit()

    @metrics_manager.error
    async def metrics_manager_error(self, e):
        error_channel = self.bot.get_channel(gli.bot_logging_channel)
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        await error_channel.send(f'An error occurred:\n{e}\n```{tb_str}```')