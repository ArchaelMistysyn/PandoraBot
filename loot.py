import pandas as pd
import csv
import random

import globalitems
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


class BasicItem:
    def __init__(self, item_id):
        self.item_id = item_id
        self.item_name = ""
        self.item_tier = ""
        self.item_base_rate = 0
        self.item_description = ""
        self.item_emoji = ""
        self.get_bitem_by_id()

    def __str__(self):
        return self.item_name

    def get_bitem_by_id(self):
        filename = "itemlist.csv"
        df = pd.read_csv(filename)
        df = df.loc[df['item_id'] == self.item_id]
        self.item_name = str(df["item_name"].values[0])
        self.item_tier = int(df["item_tier"].values[0])
        self.item_base_rate = int(df["item_base_rate"].values[0])
        self.item_description = str(df["item_description"].values[0])
        self.item_emoji = str(df["item_emoji"].values[0])


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
        loot_msg.append(f"{globalitems.exp_icon} {exp_amount}x\n{globalitems.coin_icon} {temp_coin_amount}x\n")
        # Check fae core drops
        if boss_object.boss_element != 9:
            core_element = boss_object.boss_element
        else:
            core_element = random.randint(0, 8)
        fae_item = BasicItem(f"Fae{core_element}")
        loot_msg[counter] += f"{fae_item.item_emoji} {boss_tier}x {fae_item.item_name}\n"
        df_change.loc[len(df_change)] = [temp_player.player_id, fae_item.item_id, boss_tier]
        # Check essence drops
        tarot_check_num = random.randint(1, 10)
        if tarot_check_num <= 1:
            tarot_qty = 1
            if boss_object.player_id == 0:
                try_again = random.randint(1, 10)
                if try_again <= 1:
                    tarot_qty = 2
            if ' - ' in boss_object.boss_name:
                temp = boss_object.boss_name.split(" ", 1)
                tarot_id = f"t{temp[0]}"
                filename = "itemlist.csv"
                with (open(filename, 'r') as f):
                    for line in csv.DictReader(f):
                        if str(line['item_id']) == tarot_id:
                            loot_msg[counter] += f"{str(line['item_emoji'])} {tarot_qty}x {str(line['item_name'])}\n"
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
                        num_attempts = 2
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
    exp_amount = (active_boss.boss_tier * 250) + (active_boss.boss_type_num * 50)
    level_bonus = random.randint((active_boss.boss_lvl * 25), (active_boss.boss_lvl * 50))
    exp_amount += level_bonus
    coin_amount = active_boss.boss_type_num * active_boss.boss_tier * 250
    coin_amount += int(level_bonus / 10)
    loot_output = award_loot(active_boss, player_list, exp_amount, coin_amount)
    for counter, loot_section in enumerate(loot_output):
        temp_player = player.get_player_by_id(player_list[counter])
        loot_msg = f'{temp_player.player_username} received:'
        loot_embed.add_field(name=loot_msg, value=loot_section, inline=False)
    return loot_embed


def generate_random_item():
    quantity = 1
    random_reward = random.randint(1, 1000000)
    if random_reward <= 1:
        reward_id = "v7x"
    elif random_reward <= 101:
        reward_id = "i6x"
    elif random_reward <= 1101:
        reward_id = "i5x"
    elif random_reward <= 11101:
        item_tier = 4
        reward_types = ["h", "j", "z", "s", "o", "t", "g", "w", "c", "j", "y", "Fae"]
        item_type = reward_types[(random.randint(1, len(reward_types)) - 1)]
        reward_id = f"i{item_tier}{item_type}"
    else:
        quantity = random.randint(1, 3)
        if random_reward <= 261101:
            item_tier = 3
            reward_types = ["s", "o", "k", "f", "j", "y", "Fae", "Fae"]
        elif random_reward <= 611101:
            reward_types = ["s", "o", "j", "y", "Fae", "Fae", "Fae"]
            item_tier = 2
        else:
            reward_types = ["s", "o", "j", "y", "Fae", "Fae", "Fae", "Fae"]
            item_tier = 1
        item_type = reward_types[(random.randint(1, len(reward_types)) - 1)]
        reward_id = f"i{item_tier}{item_type}"
    if item_type == "Fae":
        random_element = random.randint(0, 8)
        reward_id = f"Fae{random_element}"
        reward_id = f"Fae{random_element}"
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