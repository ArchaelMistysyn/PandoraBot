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
        self.bot = bot
        self.lock = asyncio.Lock()

    @tasks.loop(hours=1)
    async def hour_manager(self):
        async with self.lock:
            await self.update_stamina()
            await self.send_reminders()

    @hour_manager.before_loop
    async def _align_to_hour(self):
        await self.bot.wait_until_ready()
        while True:
            now = dt.utcnow()
            nxt = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
            await asyncio.sleep((nxt - now).total_seconds())
            return

    def cog_load(self):
        if not self.hour_manager.is_running():
            self.hour_manager.start()

    def cog_unload(self):
        if self.hour_manager.is_running():
            self.hour_manager.cancel()

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
        print("Check Reminders")
        now_utc = dt.now(ZoneInfo('UTC'))
        current_weekday = now_utc.weekday() + 1
        reminder_query = ("SELECT discord_id, message FROM UserReminders "
                          "WHERE hour = :current_hour AND (weekday = :current_weekday OR weekday = 0)")
        params = {'current_hour': now_utc.hour, 'current_weekday': current_weekday}
        df = await rqy(reminder_query, params=params, return_value=True)
        if df is None or len(df.index) == 0:
            print("0 reminders sent")
            return
        for _, row in df.iterrows():
            try:
                user_id = row["discord_id"]
                user = await self.bot.fetch_user(int(user_id))
                msg_file = await sm.message_box(None, [row['message']], "Reminder")
                await user.send(file=discord.File(msg_file))
            except (discord.Forbidden, discord.NotFound):
                continue
        print("All reminders sent")

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
        self.guild = None

    def cog_load(self):
        if not self.metrics_manager.is_running():
            self.metrics_manager.start()
        if not self.credit_manager.is_running():
            self.credit_manager.start()

    def cog_unload(self):
        if self.metrics_manager.is_running():
            self.metrics_manager.cancel()
        if self.credit_manager.is_running():
            self.credit_manager.cancel()

    async def run_metrics(self):
        print("Updating Metrics")
        total_members = self.guild.member_count
        online_members = sum(1 for member in self.guild.members if member.status == discord.Status.online)
        offline_members = sum(1 for member in self.guild.members if member.status == discord.Status.offline)
        role_counts = {role.name: len(role.members) for role in self.guild.roles if role.name != "@everyone"}
        metrics_channel = self.bot.get_channel(gli.metrics_channel)
        if metrics_channel:
            message_obj = await metrics_channel.fetch_message(gli.metrics_message_id)
            await message_obj.edit(content=f"Total Members: {total_members:,}\n")
        print("Metrics Updated")

    async def run_credit(self):
        # Note for future self. This can be more efficient done via batches if needed.
        time_zone = ZoneInfo('America/Toronto')
        now = dt.now(time_zone)
        if now.day != 1:
            return
        print("Updating Credits")
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
        print("Credits Updated")

    @tasks.loop(seconds=3600)
    async def metrics_manager(self):
        async with self.lock:
            await self.run_metrics()

    @metrics_manager.before_loop
    async def _metrics_wait_ready(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(1011375205999968427)

    @tasks.loop(seconds=86401)
    async def credit_manager(self):
        async with self.lock:
            await self.run_credit()

    @credit_manager.before_loop
    async def _credit_wait_ready(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(1011375205999968427)

    @metrics_manager.error
    async def metrics_manager_error(self, e):
        error_channel = self.bot.get_channel(gli.bot_logging_channel)
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        await error_channel.send(f'An error occurred:\n{e}\n```{tb_str}```')

