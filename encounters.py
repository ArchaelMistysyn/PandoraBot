# General imports
import discord
import random

# Data imports
import globalitems
import sharedmethods

# Core imports
import player
import bosses
from pandoradb import run_query as rq


async def restore_solo_bosses(channel_id):
    raid_id_df = await get_raid_id(channel_id, -1, return_multiple=True)
    restore_raid_list = []
    if len(raid_id_df.index) == 0:
        return restore_raid_list
    for index, row in raid_id_df.iterrows():
        raw_query = "SELECT * FROM BossList WHERE raid_id = :id_check"
        df = rq(raw_query, return_value=True, params={'id_check': int(row["raid_id"])})
        boss_tier, boss_level = int(df["boss_tier"].values[0]), int(df["boss_level"].values[0])
        boss_type, boss_type_num = str(df["boss_type"].values[0]), int(df["boss_type_num"].values[0])
        boss_object = CurrentBoss(boss_type_num, boss_type, boss_tier, boss_level)
        boss_object.player_id, boss_object.boss_name = int(df["player_id"].values[0]), str(df["boss_name"].values[0])
        boss_object.boss_cHP, boss_object.boss_mHP = int(df["boss_cHP"].values[0]), int(df["boss_mHP"].values[0])
        temp_t, temp_e = list(df['boss_typeweak'].values[0].split(';')), list(df['boss_eleweak'].values[0].split(';'))
        boss_object.boss_typeweak, boss_object.boss_eleweak = list(map(int, temp_t)), list(map(int, temp_e))
        boss_object.boss_image = str(df["boss_image"].values[0])
        restore_raid_list.append(boss_object)
    return restore_raid_list


def get_raid_boss_details(channel_num):
    random_boss_type = random.randint(0, channel_num)
    selected_boss_type = globalitems.boss_list[random_boss_type]
    boss_tier, selected_boss_type = bosses.get_random_bosstier(selected_boss_type)
    level = 500
    if boss_tier < 5 and selected_boss_type not in ["Arbiter", "Incarnate"]:
        channel_level_dict = {1: 40, 2: 60, 3: 80, 4: 199}
        level = channel_level_dict[channel_num]
        if channel_num < 4:
            level += + random.randint(1, 9)
    return level, selected_boss_type, boss_tier


async def add_participating_player(channel_id, player_obj):
    raid_id = await get_raid_id(channel_id, 0)
    # Check if player is already part of the raid
    raw_query = "SELECT * FROM RaidPlayers WHERE raid_id = :id_check AND player_id = :player_check"
    df_check = rq(raw_query, True, params={'id_check': raid_id, 'player_check': player_obj.player_id})
    if len(df_check.index) != 0:
        return " is already in the raid."
    # Add player to the raid
    raw_query = "INSERT INTO RaidPlayers (raid_id, player_id, player_dps) VALUES(:raid_id, :player_id, :player_dps)"
    rq(raw_query, params={'raid_id': raid_id, 'player_id': player_obj.player_id, 'player_dps': 0})
    return f"{player_obj.player_username} joined the raid"


async def add_automapper(channel_id, player_id):
    raw_query = ("INSERT INTO ActiveRaids (channel_id, player_id, encounter_type) "
                 "VALUES (:input_1, :player_id, :raid_type)")
    rq(raw_query, params={'input_1': str(channel_id), 'player_id': player_id, 'raid_type': "automap"})


async def clear_automapper(player_id):
    raw_query = "DELETE FROM ActiveRaids WHERE player_id = :player_id AND encounter_type = 'automap'"
    rq(raw_query, params={'player_id': player_id})


async def startup_clear_automaps():
    rq("DELETE FROM ActiveRaids WHERE encounter_type = 'automap'")


async def get_raid_id(channel_id, player_id, return_multiple=False):
    if player_id == -1:
        raw_query = "SELECT raid_id FROM ActiveRaids WHERE channel_id = :id_check"
        params = {'id_check': str(channel_id)}
    else:
        raw_query = "SELECT raid_id FROM ActiveRaids WHERE player_id = :player_check"
        params = {'player_check': player_id}
    df_check = rq(raw_query, return_value=True, params=params)
    if df_check is None or len(df_check) == 0:
        return 0
    if return_multiple:
        return df_check
    return int(df_check['raid_id'].values[0])
