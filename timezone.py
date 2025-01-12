# General imports
import discord
from discord.ui import Button, View
import traceback
import asyncio
from datetime import datetime as dt, timedelta

# Data imports
import globalitems as gli

# Core imports
from pandoradb import run_query as rqy
import sharedmethods as sm


class TimeZoneMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        options = [
            discord.SelectOption(emoji="🌍", label=timezone, description=timezone_detail, value=timezone_code)
            for timezone, timezone_detail, timezone_code in gli.timezone_list]
        self.select_menu =\
            discord.ui.Select(placeholder="Other Timezones", min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.timezone_callback
        self.add_item(self.select_menu)

    @discord.ui.button(label="EST", style=discord.ButtonStyle.success)
    async def est_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await timezone_handler(interaction, code="UTC-5")

    @discord.ui.button(label="PST", style=discord.ButtonStyle.blurple)
    async def pst_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await timezone_handler(interaction, code="UTC-8")

    @discord.ui.button(label="Exception", style=discord.ButtonStyle.red)
    async def exception_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = str(interaction.user.id)
        select_query = "SELECT tz_code FROM timezone_handler WHERE discord_id = :discord_id"
        user_df = await rqy(select_query, return_value=True, params={"discord_id": discord_id})
        if user_df is None or len(user_df.index) == 0 or user_df['tz_code'].values[0] == "None":
            # User has not selected a timezone
            description = "You need to select a timezone before setting region exceptions."
            no_timezone_embed = sm.easy_embed("Red", "No Timezone Selected", description)
            await interaction.response.send_message(embed=no_timezone_embed, ephemeral=True)
            return
        # User has selected a timezone, show the region exception menu
        description = ("Please disable DST or select a region-specific exception below.\n"
                       "If your region is not included, please submit a PandoraBot ticket from the #info channel.")
        exception_embed = sm.easy_embed("Red", "Region Exceptions", description)
        await interaction.response.send_message(embed=exception_embed, view=RegionExceptionMenu(), ephemeral=True)

    async def timezone_callback(self, interaction: discord.Interaction):
        selected_code = interaction.data['values'][0]
        await timezone_handler(interaction, selected_code)


class RegionExceptionMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        options = [
            discord.SelectOption(label="Reset", description="Clear all timezone data", value="Reset"),
            discord.SelectOption(label="Disable DST", description="Daylight Savings Time not observed",
                                 value="Disabled")
        ]
        for region, dates in gli.dst_regions.items():
            if region not in ["None"]:
                options.append(discord.SelectOption(label=region, description=f"Region Exception", value=region))
        self.select_menu = discord.ui.Select(placeholder="Select an option", options=options)
        self.select_menu.callback = self.region_exception_callback
        self.add_item(self.select_menu)

    async def region_exception_callback(self, interaction: discord.Interaction):
        selected_option = interaction.data['values'][0]
        await timezone_handler(interaction, region_exception=selected_option)


async def timezone_handler(interaction: discord.Interaction, code=None, region_exception="None"):
    discord_id = str(interaction.user.id)
    message, color = "Your timezone settings have been updated.", "Green"
    select_query = f"SELECT * FROM timezone_handler WHERE discord_id = :discord_id"
    user_df = await rqy(select_query, return_value=True, params={"discord_id": discord_id})
    if region_exception:
        if region_exception == "Reset":
            update_query = "DELETE FROM timezone_handler WHERE discord_id = :discord_id"
            params = {"discord_id": discord_id}
            message = "Your timezone settings have been reset."
            if user_df is None or not len(user_df.index) == 0:
                message, color = "No timezone data found.", "Red"
                update_query, params = None, None
        else:
            if user_df is not None and len(user_df.index) > 0:
                update_query = "UPDATE timezone_handler SET region_exception = :exception WHERE discord_id = :discord_id"
                params = {"exception": region_exception, "discord_id": discord_id}
            else:
                message, color = "You need to select a timezone before setting region exceptions.", "Red"
                update_query, params = None, None
    else:
        if user_df is not None and len(user_df.index) > 0:
            update_query = "UPDATE timezone_handler SET tz_code = :tz_code WHERE discord_id = :discord_id"
            params = {"tz_code": code, "discord_id": discord_id}
        else:
            update_query = ("INSERT INTO timezone_handler (discord_id, tz_code, region_exception) "
                            "VALUES (:discord_id, :tz_code, :region_exception)")
            params = {"discord_id": discord_id, "tz_code": code, "region_exception": "None"}
    if update_query is not None:
        await rqy(update_query, params=params)
    confirmation_embed = sm.easy_embed(color, "Time Zone Settings Changed", message)
    await interaction.response.send_message(embed=confirmation_embed, ephemeral=True)


async def get_time_embed(user):
    raw_query = "SELECT tz_code, region_exception FROM timezone_handler WHERE discord_id = :input1"
    timezone_df = await rqy(raw_query, return_value=True, params={"input1": str(user.id)})
    if timezone_df is None or len(timezone_df) == 0:
        return sm.easy_embed("Red", f"{user.display_name} - Time Check", "This user has not set a timezone.")
    tz_code = timezone_df['tz_code'].values[0]
    region_exception = timezone_df['region_exception'].values[0]
    if tz_code == "None":
        return sm.easy_embed("Red", f"{user.display_name} - Time Check", "This user has not set a valid timezone.")
    now = dt.utcnow()
    offset_hours, sign = 0, 0
    if tz_code != "UTC":
        offset_hours = int(tz_code.replace("UTC", "").replace("+", "").replace("-", "0"))
        sign = 1 if "+" in tz_code else -1
    now += timedelta(hours=sign * offset_hours)
    # Handle DST and Region Exceptions
    if region_exception != "Disable":
        dst_data = gli.dst_regions[region_exception]
        start_month, start_day = dst_data["start"]
        end_month, end_day = dst_data["end"]
        if start_month <= end_month:
            is_dst_active = (
                    (start_month < now.month < end_month) or
                    (now.month == start_month and now.day >= start_day) or
                    (now.month == end_month and now.day <= end_day)
            )
        else:
            is_dst_active = (
                    (now.month > start_month or now.month < end_month) or
                    (now.month == start_month and now.day >= start_day) or
                    (now.month == end_month and now.day <= end_day)
            )
        if is_dst_active:
            now += timedelta(hours=1)
    f_time = now.strftime("**%-I:%M%p**, %b %-d")
    timezone_name = gli.timezone_map[tz_code]
    description = f"{f_time}\n{timezone_name}\n{f'DST Exception ({region_exception})' if region_exception else ''}"
    return sm.easy_embed("Blue", f"{user.display_name} - Time Check", description)


async def init_time_menu(bot):
    try:
        timezone_channel = bot.get_channel(gli.time_zone_channel)
        if not timezone_channel:
            raise ValueError(f"Channel with ID {gli.time_zone_channel} not found.")
        # timezone_embed = sm.easy_embed("Gold", "Time Zone Manager", "Please select your time zone below.")
        # await timezone_channel.send(embed=timezone_embed, view=TimeZoneMenu())
        message_obj = await timezone_channel.fetch_message(gli.time_zone_message_id)
        await message_obj.edit(view=TimeZoneMenu())
    except Exception as e:
        error_channel = bot.get_channel(gli.bot_logging_channel)
        if error_channel:
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            await error_channel.send(f"An error occurred:\n{e}\n```{tb_str}```")

