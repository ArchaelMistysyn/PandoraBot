from datetime import datetime as dt, timedelta
import discord
from discord.ui import Button, View
import pandas as pd

import globalitems
import player
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import mydb


class LeaderbaordView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.button(label="DPS", style=discord.ButtonStyle.blurple)
    async def dps_leaderboard(self, interaction: discord.Interaction, button: discord.Button):
        try:
            player_object = player.get_player_by_id(self.player_user.player_id)
            embed_msg = display_leaderboard("DPS", player_object.player_id)
            await interaction.response.edit_message(embed=embed_msg)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Damage", style=discord.ButtonStyle.blurple)
    async def damage_leaderboard(self, interaction: discord.Interaction, button: discord.Button):
        try:
            player_object = player.get_player_by_id(self.player_user.player_id)
            embed_msg = display_leaderboard("Damage", player_object.player_id)
            await interaction.response.edit_message(embed=embed_msg)
        except Exception as e:
            print(e)


def update_leaderboard(combat_tracker, player_object):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()

        # Pull the user data.
        query = text(f"SELECT * FROM Leaderboard WHERE player_id = :player_check")
        query = query.bindparams(player_check=player_object.player_id)
        df = pd.read_sql(query, pandora_db)
        true_dps = int(combat_tracker.total_dps / combat_tracker.total_cycles)
        high_dmg = combat_tracker.highest_damage
        now = dt.now()

        if len(df) != 0:
            # Update DPS ranking.
            if true_dps > int(df['player_dps'].values[0]):
                query = text(f"UPDATE Leaderboard SET player_dps = :new_dps, dps_record_time = :current_time "
                             f"WHERE player_id = :player_check")
                now = dt.now()
                query = query.bindparams(new_dps=true_dps, current_time=now, player_check=player_object.player_id)
                pandora_db.execute(query)
            # Update Damage ranking.
            if high_dmg > int(df['player_damage'].values[0]):
                query = text(f"UPDATE Leaderboard SET player_damage = :new_dmg, dps_record_time = :current_time "
                             f"WHERE player_id = :player_check")
                query = query.bindparams(new_dmg=high_dmg, current_time=now, player_check=player_object.player_id)
                pandora_db.execute(query)
        else:
            # Add the player to the leaderboard if new.
            query = text(f"INSERT INTO Leaderboard (player_id, player_dps_rank, player_dps, dps_record_time, "
                         f"player_damage_rank, player_damage, damage_record_time) "
                         f"VALUES (:player_id, :player_dps_rank, :player_dps, :dps_record_time, "
                         f":player_damage_rank, :player_damage, :damage_record_time)")
            query = query.bindparams(player_id=player_object.player_id,
                                     player_dps_rank=999999, player_dps=true_dps, dps_record_time=now,
                                     player_damage_rank=999999, player_damage=high_dmg, damage_record_time=now)
            pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()

        rerank_leaderboard()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))


def rerank_leaderboard():
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()

        # Fetch the damage leaderboard, update the rankings.
        damage_query = text("SELECT * FROM Leaderboard ORDER BY player_damage DESC, damage_record_time ASC")
        damage_df = pd.read_sql(damage_query, pandora_db)
        damage_df['player_damage_rank'] = range(1, len(damage_df) + 1)
        damage_df = damage_df[['player_id', 'player_damage_rank']]

        # Fetch the dps leaderboard, update the rankings.
        dps_query = text("SELECT * FROM Leaderboard ORDER BY player_dps DESC, dps_record_time ASC")
        dps_df = pd.read_sql(dps_query, pandora_db)
        dps_df['player_dps_rank'] = range(1, len(dps_df) + 1)
        dps_df = dps_df[['player_id', 'player_dps_rank']]

        # Update the ranks in the database for DPS leaderboard
        combined_df = pd.merge(damage_df, dps_df, on='player_id')
        combined_dict = combined_df.to_dict(orient='records')
        for record in combined_dict:
            player_id = record['player_id']
            damage_rank = record['player_damage_rank']
            dps_rank = record['player_dps_rank']
            query = text("UPDATE Leaderboard "
                         "SET player_damage_rank = :damage_rank, player_dps_rank = :dps_rank "
                         "WHERE player_id = :id")
            query = query.bindparams(damage_rank=damage_rank, dps_rank=dps_rank, id=player_id)
            pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))


def display_leaderboard(leaderboard_title, player_id):
    leaderboard_type = leaderboard_title.lower()
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text(f"SELECT player_id, player_{leaderboard_type}_rank, player_{leaderboard_type} "
                     f"FROM Leaderboard ORDER BY player_{leaderboard_type}_rank ASC, player_id DESC")
        rank_df = pd.read_sql(query, pandora_db)

        # Build ranking embed.
        embed = discord.Embed(color=discord.Color.blue(), title=f"{leaderboard_title} Leaderboard", description="")
        if len(rank_df) != 0:
            # Add leaderboard data to the embed
            for index, row in rank_df.iterrows():
                # Player data.
                current_player = player.get_player_by_id(int(row['player_id']))
                current_rank = row[f'player_{leaderboard_type}_rank']
                current_stat = globalitems.number_conversion(int(row[f'player_{leaderboard_type}']))
                # Display output.
                class_icon = globalitems.class_icon_dict[current_player.player_class]
                ranking_row = f"{class_icon} Rank {current_rank}: {current_player.player_username} ({current_stat})"
                if current_player.player_id == player_id:
                    ranking_row = f"**{ranking_row}**"
                embed.add_field(name="", value=ranking_row, inline=False)
        else:
            embed.description = "No rankings posted."
        pandora_db.close()
        engine.dispose()
        return embed
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
