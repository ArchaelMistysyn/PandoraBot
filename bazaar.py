import pandorabot
import discord
import inventory
import player
import globalitems

import pandas as pd
import mydb
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc


def check_num_listings(player_obj):
    pandora_db = mydb.start_engine()
    raw_query = "SELECT * FROM CustomBazaar WHERE seller_id = :id_check"
    params = {'id_check': player_obj.player_id}
    df = pandora_db.run_query(raw_query, return_value=True, params=params)
    pandora_db.close_engine()
    return len(df)


def list_custom_item(item, cost):
    pandora_db = mydb.start_engine()
    raw_query = "INSERT INTO CustomBazaar (item_id, seller_id, cost) VALUES (:item_id, :seller_id, :cost)"
    params = {'item_id': item.item_id, 'seller_id': item.player_owner, 'cost': cost}
    pandora_db.run_query(raw_query, params=params)
    pandora_db.close_engine()
    item.item_inlaid_gem_id, item.player_owner = 0, -1
    item.update_stored_item()


def retrieve_items(player_id):
    pandora_db = mydb.start_engine()
    raw_query = "SELECT item_id FROM CustomBazaar WHERE seller_id = :player_id"
    df = pandora_db.run_query(raw_query, return_value=True, params={'player_id': player_id})
    item_ids = []
    if len(df) != 0:
        item_ids = df['item_id'].tolist()
        update_query = "UPDATE CustomInventory SET player_id = :player_id WHERE item_id IN :item_ids"
        delete_query = "DELETE FROM CustomBazaar WHERE item_id IN :item_ids"
        pandora_db.run_query(update_query, params={'player_id': player_id, 'item_ids': tuple(item_ids)})
        pandora_db.run_query(delete_query, params={'item_ids': tuple(item_ids)})
    pandora_db.close_engine()
    return len(item_ids) if item_ids else 0


def show_bazaar_items():
    pandora_db = mydb.start_engine()
    raw_query = ("SELECT CustomBazaar.item_id, CustomBazaar.seller_id, CustomBazaar.cost, "
                 "CustomInventory.item_name, CustomInventory.item_type, "
                 "CustomInventory.item_damage_type, CustomInventory.item_elements, "
                 "CustomInventory.item_tier, CustomInventory.item_bonus_stat, "
                 "CustomInventory.item_base_dmg_min, CustomInventory.item_base_dmg_max "
                 "FROM CustomBazaar "
                 "INNER JOIN CustomInventory ON CustomBazaar.item_id = CustomInventory.item_id "
                 "ORDER BY CustomInventory.item_tier DESC, CustomInventory.item_base_dmg_max DESC, "
                 "CustomBazaar.cost ASC")
    df = pandora_db.run_query(raw_query, return_value=True)
    pandora_db.close_engine()

    bazaar_embed = discord.Embed(colour=discord.Colour.dark_orange(), title="The Bazaar", description="Open Marketplace")
    if len(df.index) != 0:
        for index, row in df.iterrows():
            item_id, seller_id = int(row["item_id"]), int(row["seller_id"])
            cost = int(row["cost"])
            item_name = str(row["item_name"])
            temp_elements = list(str(row['item_elements']).split(';'))
            item_elements, item_damage_type = list(map(int, temp_elements)), str(row["item_damage_type"])
            item_tier = int(row["item_tier"])
            item_bonus_stat = str(row["item_bonus_stat"])
            item_base_dmg_min, item_base_dmg_max = int(row["item_base_dmg_min"]), int(row["item_base_dmg_max"])

            item_cost = f"Cost: {cost} Lotus Coins"
            item_damage = f"Average Damage: {int((item_base_dmg_min + item_base_dmg_max) / 2)}"
            if item_bonus_stat:
                if item_bonus_stat[0].isalpha():
                    item_main_info = f"{item_damage} || Skill: {item_bonus_stat}"
                else:
                    item_main_info = f"{item_damage} || Base Stat: {item_bonus_stat}"
            else:
                item_main_info = f"{item_damage}"

            display_stars = sharedmethods.display_stars(item_tier)
            item_types = f'{item_damage_type}'
            for idz, z in enumerate(item_elements):
                if z == 1:
                    item_types += f'{globalitems.global_element_list[idz]}'

            seller = player.get_player_by_id(seller_id)
            bazaar_embed.add_field(name=f"{item_name}", value=f"{item_cost} || Item ID: {item_id}", inline=False)
            bazaar_embed.add_field(name="", value=f"{display_stars} {item_types}", inline=False)
            bazaar_embed.add_field(name="", value=item_main_info, inline=False)
            bazaar_embed.add_field(name="", value=f"Listed by: {seller.player_username}", inline=False)
        bazaar_embed = None
    return bazaar_embed


def get_seller_by_item(item_id):
    pandora_db = mydb.start_engine()
    raw_query = "SELECT seller_id FROM CustomBazaar WHERE item_id = :item_check"
    df = pandora_db.run_query(raw_query, return_value=True, params={'item_check': item_id})
    pandora_db.close_engine()
    seller_id = 0
    if len(df.index) != 0:
        seller_id = int(df['seller_id'].values[0])
    return seller_id


def get_item_cost(item_id):
    pandora_db = mydb.start_engine()
    raw_query = "SELECT cost FROM CustomBazaar WHERE item_id = :item_check"
    df = pandora_db.run_query(raw_query, return_value=True, params={'item_check': item_id})
    pandora_db.close_engine()
    item_cost = 0
    if len(df.index) != 0:
        item_cost = int(df['cost'].values[0])
    return item_cost


def buy_item(item_id):
    pandora_db = mydb.start_engine()
    raw_query = "DELETE FROM CustomBazaar WHERE item_id = :item_check"
    pandora_db.run_query(raw_query, params={'item_check': item_id})
    pandora_db.close_engine()
    seller_id = get_seller_by_item(item_id)
    seller_object = player.get_player_by_id(seller_id)
    if seller_object is not None:
        item_cost = get_item_cost(item_id)
        _ = seller_object.adjust_coins(item_cost)
