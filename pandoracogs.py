# General imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import asyncio
import traceback
from zoneinfo import ZoneInfo

# Core imports
import globalitems as gli
import sharedmethods as sm
from pandoradb import run_query as rqy
import player
from datetime import datetime as dt, timedelta

# Item/crafting imports
import pact


class HourCog(commands.Cog):
    def __init__(self, bot):
        self.bot, self.lock = bot, asyncio.Lock()
        self.bot.loop.create_task(self.align_hour())

    def cog_unload(self):
        self.hour_manager.cancel()

    @tasks.loop(hours=1)
    async def hour_manager(self):
        async with self.lock:
            await self.update_stamina()
            await self.send_reminders()

    async def update_stamina(self):
        player_list = await player.get_all_users()
        if player_list is None:
            return
        update_params = []
        for player_user in player_list:
            pact_object = pact.Pact(player_user.pact)
            max_stamina = 5000 if pact_object.pact_variant != "Sloth" else 2500
            new_stamina_value = min(player_user.player_stamina + 25, max_stamina)
            update_params.append({'player_check': player_user.player_id, 'input_1': new_stamina_value})
        if update_params:
            query = "UPDATE PlayerList SET player_stamina = :input_1 WHERE player_id = :player_check"
            await rqy(query, batch=True, params=update_params)

    async def send_reminders(self):
        now_utc = dt.now(ZoneInfo('UTC'))
        current_weekday = now_utc.weekday() + 1
        reminder_query = ("SELECT discord_id, message FROM UserReminders "
                          "WHERE hour = :current_hour AND (weekday = :current_weekday OR weekday = 0)")
        params = {'current_hour': now_utc.hour, 'current_weekday': current_weekday}
        df = await rqy(reminder_query, params=params, return_value=True)
        if df is None or len(df.index) == 0:
            return
        for _, row in df.iterrows():
            try:
                user_id = row["discord_id"]
                user = await self.bot.fetch_user(int(user_id))
                msg_file = await sm.message_box(None, [row['message']], "Reminder")
                await user.send(file=discord.File(msg_file))
            except (discord.Forbidden, discord.NotFound):
                continue

    async def align_hour(self):
        now = dt.utcnow()
        if now.minute >= 58:
            await asyncio.sleep(60 - now.second)
            now = dt.utcnow()
        seconds_until_next_hour = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(seconds_until_next_hour)
        self.hour_manager.start()

    @hour_manager.error
    async def hour_manager_error(self, e):
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

    async def run_credit(self):
        # Note for future self. This can be more efficient done via batches if needed.
        time_zone = ZoneInfo('America/Toronto')
        now = dt.now(time_zone)
        if now.day != 1:
            return
        eligible_roles = [role for role in self.guild.roles if "Subscriber" in role.name]
        credited_users = []
        for member in self.guild.members:
            if any(role in member.roles for role in eligible_roles):
                discord_id = member.id
                current = await player.check_credit(discord_id)
                credit_amount = 2 if any("Crowned" in role.name for role in member.roles) else 1
                if current is None:
                    await player.set_credit(discord_id, credit_amount)
                    new_credit = credit_amount
                else:
                    new_credit = current + credit_amount
                    await player.update_credit(discord_id, new_credit)
                credited_users.append((member, new_credit))
        for user, credit in credited_users:
            credit_msg = (f"You received {credit_amount} ArchDragon Store credit(s). Your new balance is {credit:,}.\n"
                          f"Credit is deducted as the highest eligible gift card value: 10, 25, 50, 100, 250, 500\n"
                          f"Message me 'checkout' or open a basic ticket in the server to request your gift card.")
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