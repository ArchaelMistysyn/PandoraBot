import discord
import pandas as pd
import csv
import random

import itemdata
import globalitems
import inventory
import loot
import player
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import mydb
import pandorabot


def award_loot(boss_object, player_list, exp_amount, coin_amount):
    boss_tier = boss_object.boss_tier
    loot_msg = []
    labels = ['player_id', 'item_id', 'item_qty']
    df_change = pd.DataFrame(columns=labels)
    for counter, x in enumerate(player_list):
        temp_player = player.get_player_by_id(x)
        temp_player.player_exp += exp_amount
        temp_coin_amount = coin_amount + temp_player.player_lvl
        temp_player.player_coins += temp_coin_amount
        temp_player.set_player_field("player_exp", temp_player.player_exp)
        temp_player.set_player_field("player_coins", temp_player.player_coins)
        loot_msg.append(f"{globalitems.exp_icon} {exp_amount:,}x\n{globalitems.coin_icon} {temp_coin_amount:,}x\n")
        # Check fae core drops
        if boss_object.boss_element != 9:
            core_element = boss_object.boss_element
        else:
            core_element = random.randint(0, 8)
        fae_qty = random.randint(1, boss_object.boss_lvl)
        fae_item = BasicItem(f"Fae{core_element}")
        loot_msg[counter] += f"{fae_item.item_emoji} {fae_qty}x {fae_item.item_name}\n"
        df_change.loc[len(df_change)] = [temp_player.player_id, fae_item.item_id, fae_qty]
        # Check raid stone drops.
        if boss_object.player_id == 0:
            random_check = random.randint(1, 100)
            if random_check <= 75:
                raid_item = BasicItem(f"Stone5")
                loot_msg[counter] += f"{raid_item.item_emoji} 1x {raid_item.item_name}\n"
                df_change.loc[len(df_change)] = [temp_player.player_id, raid_item.item_id, 1]
        # Check essence drops
        tarot_qty = 0
        if ' - ' in boss_object.boss_name:
            if boss_object.player_id == 0:
                attempts = 5
            else:
                attempts = 1
            for y in range(0, attempts):
                tarot_check_num = random.randint(1, 100)
                if tarot_check_num <= 20:
                    tarot_qty += 1
            if tarot_qty > 0:
                temp = boss_object.boss_name.split(" ", 1)
                tarot_id = f"Essence{temp[0]}"
                tarot_item = inventory.BasicItem(tarot_id)
                loot_msg[counter] += f"{tarot_item.item_emoji} {tarot_qty}x {tarot_item.item_name}\n"
                df_change.loc[len(df_change)] = [temp_player.player_id, tarot_id, tarot_qty]
        filename = "droptable.csv"
        with open(filename, 'r') as f:
            for line in csv.DictReader(f):
                if str(line['boss_type']) == str(boss_object.boss_type) and int(line['boss_tier']) == int(boss_tier):
                    loot_qualifies = True
                elif str(line['boss_type']) == str(boss_object.boss_type) and int(line['boss_tier']) == 0:
                    loot_qualifies = True
                elif str(line['boss_type']) == "All" and int(line['boss_tier']) == int(boss_tier):
                    loot_qualifies = True
                elif str(line['boss_type']) == "All" and int(line['boss_tier']) == 0:
                    loot_qualifies = True
                else:
                    loot_qualifies = False

                if loot_qualifies:
                    dropped_item = str(line["item_id"])
                    drop_rate = float(line["drop_rate"])
                    loot_item = BasicItem(dropped_item)
                    qty = 0
                    num_attempts = 1
                    if boss_object.player_id == 0:
                        num_attempts = 5
                    for y in range(num_attempts):
                        if is_dropped(drop_rate):
                            qty += 1
                    if qty != 0:
                        df_change.loc[len(df_change)] = [temp_player.player_id, dropped_item, qty]
                        loot_msg[counter] += f'{loot_item.item_emoji} {str(qty)}x {loot_item.item_name}\n'
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        temp_table_name = 'temp_basic_inventory'
        df_change.to_sql(temp_table_name, engine, if_exists="replace", index=False)

        # Define the SQL statement
        query = text('''INSERT INTO BasicInventory (player_id, item_id, item_qty)
                        VALUES (:player_id, :item_id, :item_qty)
                        ON DUPLICATE KEY UPDATE item_qty = item_qty + VALUES(item_qty);''')

        # Bind the parameters and execute the query
        for index, row in df_change.iterrows():
            parameters = {
                'player_id': row['player_id'],
                'item_id': row['item_id'],
                'item_qty': row['item_qty']
            }
            pandora_db.execute(query, parameters)
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)

    return loot_msg


def is_dropped(drop_rate):
    random_num = round(random.random() * 100, 2)
    if random_num <= drop_rate:
        return True
    else:
        return False


def create_loot_embed(current_embed, active_boss, player_list):
    loot_embed = current_embed
    exp_amount = (active_boss.boss_tier * 250) + (active_boss.boss_type_num * 100)
    level_bonus = random.randint((active_boss.boss_lvl * 25), (active_boss.boss_lvl * 100))
    exp_amount += level_bonus
    coin_amount = active_boss.boss_type_num * active_boss.boss_tier * 250
    coin_amount += int(level_bonus / 10)
    if active_boss.player_id == 0:
        exp_amount *= 5
        coin_amount *= 5
    else:
        exp_amount *= 2
        coin_amount *= 2
    loot_output = award_loot(active_boss, player_list, exp_amount, coin_amount)
    for counter, loot_section in enumerate(loot_output):
        temp_player = player.get_player_by_id(player_list[counter])
        loot_msg = f'{temp_player.player_username} received:'
        loot_embed.add_field(name=loot_msg, value=loot_section, inline=False)
    return loot_embed


def generate_random_item():
    # Initialize the quantity and data.
    quantity_table = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3]
    quantity = random.choice(quantity_table)
    random_reward = random.randint(1, 10000)
    reward_id = None

    probability_rewards = {
        1: ("Crystal2", None), 11: ("Crystal1", None), 61: ("OriginZ", None),
        111: ("Core1", None), 211: ("Heart1", None), 411: (None, "Summon"),
        511: (None, "Token"), 1011: (None, "Pearl"), 1511: (None, "Hammer"),
        2511: ("Flame1", None), 3511: ("Matrix1", None), 4511: (None, "Trove"),
        5511: (None, "Potion"), 6511: (None, "Soul"), 7511: (None, "Ore"),
        10000: (None, "Fae")
    }

    # Assign a reward id based on the probability, set id, or id prefix.
    for upper_limit, (specific_reward, prefix) in probability_rewards.items():
        if random_reward <= upper_limit:
            if specific_reward:
                reward_id = specific_reward
            elif prefix is not None:
                reward_types = [key for key in itemdata.itemdata_dict.keys() if key is not None and prefix in key]
                reward_id = random.choice(reward_types)
            break

    # Quantity Exceptions
    print(reward_id)
    if reward_id == "Crystal2":
        quantity = 1
    elif "Fae" in reward_id:
        quantity = random.randint(5, (50 * quantity))

    return reward_id, quantity


def generate_trove_reward(item_tier):
    match item_tier:
        case 4:
            num_coins = random.randint(50000,250000)
        case 3:
            num_coins = random.randint(25000, 50000)
        case 2:
            num_coins = random.randint(10000, 25000)
        case _:
            num_coins = random.randint(1000, 10000)
    return num_coins
