# General imports
import discord
import random

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import player
import bosses
from pandoradb import run_query as rqy


async def add_participating_player(channel_id, player_obj):
    raid_id = await get_encounter_id(channel_id, None)
    if raid_id is None:
        return " - Error: No raid found."
    # Check if player is already part of the raid
    raw_query = "SELECT * FROM RaidPlayers WHERE raid_id = :id_check AND player_id = :player_check"
    df_check = await rqy(raw_query, True, params={'id_check': raid_id, 'player_check': player_obj.player_id})
    if len(df_check.index) != 0:
        return " is already in the raid."
    # Add player to the raid
    raw_query = ("INSERT INTO RaidPlayers (raid_id, player_id, channel_id, player_dps) "
                 "VALUES(:raid_id, :player_id, :channel_id, :player_dps)")
    params = {'raid_id': raid_id, 'player_id': player_obj.player_id, 'channel_id': str(channel_id), 'player_dps': 0}
    await rqy(raw_query, params=params)
    return f"{player_obj.player_username} joined the raid"


async def add_automapper(channel_id, player_id):
    raw_query = ("INSERT INTO EncounterList (channel_id, player_id, encounter) "
                 "VALUES (:channel_id, :player_id, :encounter_type)")
    await rqy(raw_query, params={'channel_id': channel_id, 'player_id': player_id, 'encounter_type': "automap"})


async def clear_automapper(player_id, startup=False):
    extension, params = (" AND player_id = :player_id", {'player_id': player_id}) if not startup else ("", None)
    raw_query = f"DELETE FROM EncounterList WHERE encounter = 'automap'{extension}"
    await rqy(raw_query, params=params)


async def clear_boss_encounter_info(channel_id, player_id=None):
    if player_id is not None:
        await rqy("DELETE FROM EncounterList WHERE player_id = :id_check", params={"id_check": player_id})
        return
    raid_id = await get_encounter_id(channel_id, player_id)
    if raid_id is None:
        return
    params = {'id_check': raid_id}
    await rqy("DELETE FROM EncounterList WHERE encounter_id = :id_check", params=params)
    await rqy("DELETE FROM RaidPlayers WHERE raid_id = :id_check", params=params)


async def clear_all_encounter_info(server_id):
    params_list = [{'id_check': str(gli.servers[server_id][1])}]
    for channel_id in gli.servers[server_id][0]:
        params_list.append({'id_check': str(channel_id)})
    await rqy("DELETE FROM EncounterList WHERE channel_id = :id_check", batch=True, params=params_list)
    await rqy("DELETE FROM RaidPlayers WHERE channel_id = :id_check", batch=True, params=params_list)


async def update_player_raid_damage(channel_id, player_id, player_damage):
    raid_id = await get_encounter_id(channel_id, None)
    if raid_id is None:
        return
    raw_query = "UPDATE RaidPlayers SET player_dps = :new_dps WHERE raid_id = :id_check AND player_id = :player_check"
    await rqy(raw_query, params={'new_dps': player_damage, 'id_check': raid_id, 'player_check': player_id})


async def get_encounter_id(channel_id, player_id=None, id_only=True):
    raw_query = f"SELECT * FROM EncounterList WHERE encounter = 'Raid' AND channel_id = :channel_id"
    params = {'channel_id': str(channel_id)}
    if player_id is not None:
        raw_query = f"SELECT * FROM EncounterList WHERE channel_id = :channel_id AND player_id = :player_id"
        params['player_id'] = player_id
    df = await rqy(raw_query, return_value=True, params=params)
    if df is None or len(df) == 0:
        return None
    return int(df['encounter_id'].values[0]) if id_only else df

