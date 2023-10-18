import pandas as pd
import csv
import random
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

        filename = "itemlist.csv"

        with (open(filename, 'r') as f):
            for line in csv.DictReader(f):
                if str(line['item_id']) == str(item_id):
                    self.item_name = str(line["item_name"])
                    self.item_tier = int(line["item_tier"])
                    self.item_base_rate = int(line["item_base_rate"])
                    self.item_description = str(line["item_description"])
                    self.item_emoji = str(line["item_emoji"])

    def __str__(self):
        return self.item_name


def award_loot(boss_object, player_list, exp_amount):
    boss_tier = boss_object.boss_tier
    coin_amount = boss_object.boss_type_num * boss_tier * 250
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
        loot_msg.append(f"{pandorabot.exp_icon} {exp_amount}x\n{pandorabot.coin_icon} {temp_coin_amount}x\n")
        tarot_check_num = random.randint(1, 10)
        if tarot_check_num == 1:
            if ' - ' in boss_object.boss_name:
                temp = boss_object.boss_name.split(" ", 1)
                tarot_id = f"t{temp[0]}"
                filename = "itemlist.csv"
                with (open(filename, 'r') as f):
                    for line in csv.DictReader(f):
                        if str(line['item_id']) == tarot_id:
                            loot_msg[counter] += f"{str(line['item_emoji'])} 1x {str(line['item_name'])}\n"
                            df_change.loc[len(df_change)] = [temp_player.player_id, tarot_id, 1]
        filename = "droptable.csv"
        with (open(filename, 'r') as f):
            for line in csv.DictReader(f):
                if str(line['boss_type']) == str(boss_object.boss_type) and int(line['boss_tier']) == int(boss_tier):
                    dropped_item = str(line["item_id"])
                    drop_rate = int(line["drop_rate"])
                    item_name = get_loot_name(dropped_item)
                    item_emoji = get_loot_emoji(dropped_item)
                    qty = 0
                    item_tier = int(dropped_item[1])
                    if item_tier < 4:
                        num_attempts = 3
                    else:
                        num_attempts = 1
                    for y in range(num_attempts):
                        if is_dropped(drop_rate):
                            qty += 1
                    if qty != 0:
                        df_change.loc[len(df_change)] = [temp_player.player_id, dropped_item, qty]
                        loot_msg[counter] += f'{item_emoji} {str(qty)}x {item_name}\n'
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text(f"SELECT * FROM BasicInventory")
        df_existing = pd.read_sql(query, pandora_db)
        df_updated = pd.concat([df_existing, df_change]).groupby(['player_id', 'item_id']).sum().reset_index()
        df_updated.to_sql("BasicInventory", pandora_db, index=False, if_exists='replace')
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)

    return loot_msg


def is_dropped(drop_rate) -> bool:
    random_num = random.randint(1, 100)
    if random_num <= int(drop_rate):
        return True
    else:
        return False


def get_loot_emoji(item_id) -> str:
    filename = "itemlist.csv"
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line["item_id"]) == str(item_id):
                str_emoji = str(line["item_emoji"])

    return str_emoji


def get_loot_name(item_id) -> str:
    filename = "itemlist.csv"
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line["item_id"]) == str(item_id):
                str_name = str(line["item_name"])
    return str_name


def create_loot_embed(current_embed, active_boss, player_list):
    loot_embed = current_embed
    exp_amount = active_boss.boss_tier * active_boss.boss_type_num * active_boss.boss_lvl * 100
    loot_output = award_loot(active_boss, player_list, exp_amount)
    for counter, loot_section in enumerate(loot_output):
        temp_player = player.get_player_by_id(player_list[counter])
        loot_msg = f'{temp_player.player_username} received:'
        loot_embed.add_field(name=loot_msg, value=loot_section, inline=False)
    return loot_embed


def generate_random_item():
    quantity = 1
    random_reward = random.randint(1, 1000000)
    reward_types = ["a", "b", "c", "d", "h", "i", "j", "m", "n", "s", "t"]
    if random_reward <= 1:
        reward_id = "I7x"
    elif random_reward <= 101:
        reward_id = "I6x"
    elif random_reward <= 1101:
        reward_id = "I5x"
    elif random_reward <= 51101:
        item_tier = 4
        item_type = reward_types[(random.randint(1, len(reward_types)) - 1)]
        reward_id = f"I{item_tier}{item_type}"
    else:
        quantity = random.randint(1, 3)
        if random_reward <= 301101:
            item_tier = 3
        elif random_reward <= 601101:
            item_tier = 2
        else:
            item_tier = 1
        item_type = reward_types[(random.randint(1, len(reward_types)) - 1)]
        reward_id = f"I{item_tier}{item_type}"
    return reward_id, quantity
