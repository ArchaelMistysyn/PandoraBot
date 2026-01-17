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

# Item/crafting imports
import pact

# Misc Imports
import timezone
import datetime, calendar
dt = datetime.datetime
timedelta = datetime.timedelta
tz = datetime.timezone


class HourCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.execution_count = 0

    @tasks.loop(hours=1)
    async def hour_manager(self):
        self.execution_count += 1
        async with self.lock:
            await self.send_reminders()
            await self.update_stamina()

    @hour_manager.before_loop
    async def _align_to_hour(self):
        await self.bot.wait_until_ready()
        now = dt.utcnow()
        next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        delay = (next_hour - now).total_seconds()
        print(f"[HourCog] Delaying first run for {delay / 60:.1f} minutes.")
        await asyncio.sleep(delay)

    def cog_load(self):
        print("Inner Check")
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
            new_stamina_value = min(player_user.player_stamina + 500, max_stamina)
            update_params.append({'player_check': player_user.player_id, 'input_1': new_stamina_value})
        if update_params:
            query = "UPDATE PlayerList SET player_stamina = :input_1 WHERE player_id = :player_check"
            await rqy(query, batch=True, params=update_params)

    async def send_reminders(self):
        print("Check Reminders")
        try:
            now_utc = dt.now(ZoneInfo('UTC'))
            current_weekday = now_utc.weekday() + 1
            reminder_query = ("SELECT discord_id, message, hour FROM UserReminders "
                              "WHERE (weekday = :current_weekday OR weekday = 0)")
            prev_day = 7 if current_weekday == 1 else current_weekday - 1
            params = {'current_weekday': current_weekday}
            df = await rqy(reminder_query, params=params, return_value=True)
            dst_query = ("SELECT discord_id, message, hour FROM UserReminders "
                         "WHERE (weekday = :prev_day)")
            params = {'prev_day': prev_day}
            dst_df = await rqy(dst_query, params=params, return_value=True)
            if df is None or len(df.index) == 0:
                print("0 reminders sent")
                return
            for _, row in df.iterrows():
                try:
                    if not (now_utc.hour <= int(row["hour"]) <= now_utc.hour + 1):
                        continue
                    user_id = row["discord_id"]
                    tz_code, dst_offset = await timezone.get_user_timezone(user_id)
                    if not (((now_utc.hour == int(row["hour"]) and dst_offset == 0) or
                            (now_utc.hour != int(row["hour"]) and dst_offset == 1))):
                        continue
                    user = await self.bot.fetch_user(int(user_id))
                    msg_file = await sm.message_box(None, [row['message']], "Reminder")
                    await user.send(file=discord.File(msg_file))
                except (discord.Forbidden, discord.NotFound):
                    continue
            # DST adjusted check ONLY
            if dst_df is None or len(dst_df.index) == 0:
                print("All reminders sent")
                return
            for _, row in dst_df.iterrows():
                try:
                    user_id = row["discord_id"]
                    tz_code, dst_offset = await timezone.get_user_timezone(user_id)
                    if not (dst_offset == 1 and int(row["hour"]) == 23 and now_utc.hour == 0):
                        continue
                    user = await self.bot.fetch_user(int(user_id))
                    msg_file = await sm.message_box(None, [row['message']], "Reminder")
                    await user.send(file=discord.File(msg_file))
                except (discord.Forbidden, discord.NotFound):
                    continue
        except Exception as e:
            print(F"EXCEPTION: {e}")
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
        online_members = sum(1 for m in self.guild.members if m.status == discord.Status.online)
        offline_members = sum(1 for m in self.guild.members if m.status == discord.Status.offline)
        # List of (label, role_id) pairs
        role_checks = [
            ("Server Guild Member", 1140738057381871707),
            ("Private Access Member", 1076760869620437002),
            ("Gem Title Holder", 1415355530729361528),
            ("Relic Title Holder", 1157565406366666792),
            ("ArchDragon Partner", 1411594840793288815),
            ("ArchDragon Moderator", 1134293907136585769),
            ("ArchDragon Administrator", 1134301246648488097)
        ]
        # reaction_msg = await self.get_top_reactions_week()
        # Build output text
        metrics_text = f"Total Members: {total_members:,}\n"
        for label, role_id in role_checks:
            role = self.guild.get_role(role_id)
            if role:
                metrics_text += f"{label}: {len(role.members):,}\n"
            else:
                metrics_text += f"{label}: Role not found\n"
        # metrics_text += f"\nTop Reactions (7d):\n{reaction_msg}\n"
        metrics_channel = self.bot.get_channel(gli.metrics_channel)
        if metrics_channel:
            message_obj = await metrics_channel.fetch_message(gli.metrics_message_id)
            await message_obj.edit(content=metrics_text)
        print("Metrics Updated")

    async def get_top_reactions_week(self, days=7, limit=5):
        reaction_counts = {}
        time_threshold = dt.now(tz.utc) - timedelta(days=days)
        for channel in self.guild.text_channels:
            try:
                async for message in channel.history(after=time_threshold, limit=None):
                    for reaction in message.reactions:
                        emoji_key = str(reaction.emoji)
                        reaction_counts[emoji_key] = reaction_counts.get(emoji_key, 0) + reaction.count
            except Exception:
                # Skip channels the bot has no access to
                continue
        sorted_reactions = sorted(reaction_counts.items(), key=lambda x: x[1], reverse=True)
        top_reactions = sorted_reactions[:limit]
        reaction_msg = ""
        if top_reactions:
            for emoji, count in top_reactions:
                reaction_msg += f"{emoji}: {count:,}\n"
        return reaction_msg

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

