# General imports
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
import discord
from discord.ui import Button, View
import pandas as pd

# Data imports
import globalitems as gli
import sharedmethods as sm
from pandoradb import run_query as rqy

# Core imports
import player


class LeaderbaordView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.button(label="DPS", style=discord.ButtonStyle.blurple)
    async def dps_leaderboard(self, interaction: discord.Interaction, button: discord.Button):
        try:
            embed_msg = await display_leaderboard("DPS", self.player_user.player_id)
            await interaction.response.edit_message(embed=embed_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Damage", style=discord.ButtonStyle.blurple)
    async def damage_leaderboard(self, interaction: discord.Interaction, button: discord.Button):
        try:
            embed_msg = await display_leaderboard("Damage", self.player_user.player_id)
            await interaction.response.edit_message(embed=embed_msg)
        except Exception as e:
            print(e)


async def update_leaderboard(combat_tracker, player_obj, ctx_object):
    # Pull the user data.
    raw_query = "SELECT * FROM Leaderboard WHERE player_id = :player_check"
    df = await rqy(raw_query, return_value=True, params={'player_check': player_obj.player_id})
    true_dps = int(combat_tracker.total_dps / combat_tracker.total_cycles)
    high_dmg = combat_tracker.highest_damage
    now = dt.now(ZoneInfo('America/Toronto'))
    if not df.empty:
        # Update DPS ranking.
        if true_dps > int(df['player_dps'].values[0]):
            raw_query = ("UPDATE Leaderboard SET player_dps = :new_dps, dps_record_time = :current_time "
                         "WHERE player_id = :player_check")
            params = {'new_dps': true_dps, 'current_time': now, 'player_check': player_obj.player_id}
            await rqy(raw_query, params=params)
        # Update Damage ranking.
        if high_dmg > int(df['player_damage'].values[0]):
            raw_query = ("UPDATE Leaderboard SET player_damage = :new_dmg, damage_record_time = :current_time "
                         "WHERE player_id = :player_check")
            params = {'new_dmg': high_dmg, 'current_time': now, 'player_check': player_obj.player_id}
            await rqy(raw_query, params=params)
    else:
        # Add the player to the leaderboard if new.
        raw_query = ("INSERT INTO Leaderboard (player_id, player_dps_rank, player_dps, dps_record_time, "
                     "player_damage_rank, player_damage, damage_record_time) "
                     "VALUES (:player_id, :player_dps_rank, :player_dps, :dps_record_time, "
                     ":player_damage_rank, :player_damage, :damage_record_time)")
        params = {
            'player_id': player_obj.player_id, 'dps_record_time': now, 'damage_record_time': now,
            'player_dps_rank': 999999, 'player_dps': true_dps, 'player_damage_rank': 999999, 'player_damage': high_dmg
        }
        await rqy(raw_query, params=params)
    await rerank_leaderboard(ctx_object)


async def rerank_leaderboard(ctx_object):
    # Fetch the damage leaderboard, update the rankings.
    damage_query = "SELECT * FROM Leaderboard ORDER BY player_damage DESC, damage_record_time ASC"
    damage_df = await rqy(damage_query, return_value=True)
    damage_df['player_damage_rank'] = range(1, len(damage_df) + 1)
    damage_df = damage_df[['player_id', 'player_damage_rank']]
    # Fetch the dps leaderboard, update the rankings.
    dps_query = "SELECT * FROM Leaderboard ORDER BY player_dps DESC, dps_record_time ASC"
    dps_df = await rqy(dps_query, return_value=True)
    dps_df['player_dps_rank'] = range(1, len(dps_df) + 1)
    dps_df = dps_df[['player_id', 'player_dps_rank']]

    # Retrieve the current roles for rank 1 players
    raw_query = ("SELECT player_id, player_damage_rank, player_dps_rank "
                 "FROM Leaderboard WHERE player_damage_rank = 1 OR player_dps_rank = 1")
    original_df = await rqy(raw_query, return_value=True)

    # Handle rank changes and role assignment.
    async def handle_rank_changes(ctx, original_id, new_id, role_name):
        if original_id != new_id:
            role_object = discord.utils.get(ctx.guild.roles, name=role_name)
            # Assign the role to the new top ranker.
            new_player_obj = await player.get_player_by_id(new_id)
            new_user = ctx.guild.get_member(new_player_obj.discord_id)
            await new_user.add_roles(role_object)
            await sm.send_notification(ctx_object, new_player_obj, "Achievement", role_name)
            # If previous ranker exists remove their role.
            if original_id != -1:
                original_player_obj = await player.get_player_by_id(original_id)
                original_user = ctx.guild.get_member(original_player_obj.discord_id)
                if original_user and new_user and role_object:
                    await original_user.remove_roles(role_object)

    original_damage_id, original_dps_id = -1, -1
    if len(original_df[original_df['player_damage_rank'] == 1]) != 0:
        original_damage_id = int(original_df[original_df['player_damage_rank'] == 1]['player_id'].values[0])
    if len(original_df[original_df['player_dps_rank'] == 1]) != 0:
        original_dps_id = int(original_df[original_df['player_dps_rank'] == 1]['player_id'].values[0])
    new_damage_id = int(damage_df[damage_df['player_damage_rank'] == 1]['player_id'].values[0])
    new_dps_id = int(dps_df[dps_df['player_dps_rank'] == 1]['player_id'].values[0])
    damage_role = "Ranking Title - Damage Rank #1"
    await handle_rank_changes(ctx_object, original_damage_id, new_damage_id, damage_role)
    dps_role = "Ranking Title - DPS Rank #1"
    await handle_rank_changes(ctx_object, original_dps_id, new_dps_id, dps_role)

    # Update the ranks in the database for DPS leaderboard
    combined_df = pd.merge(damage_df, dps_df, on='player_id')
    combined_dict = combined_df.to_dict(orient='records')
    for record in combined_dict:
        player_id = record['player_id']
        damage_rank = record['player_damage_rank']
        dps_rank = record['player_dps_rank']
        raw_query = ("UPDATE Leaderboard "
                     "SET player_damage_rank = :damage_rank, player_dps_rank = :dps_rank WHERE player_id = :id")
        await rqy(raw_query, params={'damage_rank': damage_rank, 'dps_rank': dps_rank, 'id': player_id})
    


async def display_leaderboard(leaderboard_title, player_id):
    leaderboard_type = leaderboard_title.lower()
    raw_query = (f"SELECT player_id, player_{leaderboard_type}_rank, player_{leaderboard_type} "
                 f"FROM Leaderboard ORDER BY player_{leaderboard_type}_rank ASC, player_id DESC")
    rank_df = await rqy(raw_query, return_value=True)
    
    # Build ranking embed.
    embed = discord.Embed(color=discord.Color.blue(), title=f"{leaderboard_title} Leaderboard", description="")
    if len(rank_df) != 0:
        for index, row in rank_df.iterrows():
            current_player = await player.get_player_by_id(int(row['player_id']))
            current_rank = row[f'player_{leaderboard_type}_rank']
            current_stat = sm.number_conversion(int(row[f'player_{leaderboard_type}']))
            class_icon = gli.class_icon_dict[current_player.player_class]
            ranking_row = f"{class_icon} Rank {current_rank}: {current_player.player_username} ({current_stat})"
            if current_player.player_id == player_id:
                ranking_row = f"**{ranking_row}**"
            embed.add_field(name="", value=ranking_row, inline=False)
    else:
        embed.description = "No rankings posted."
    return embed

