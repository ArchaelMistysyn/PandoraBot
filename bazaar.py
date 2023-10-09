import pandorabot
import discord
import inventory
import player

import pandas as pd
import mydb
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc


def list_custom_item(item, cost):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("INSERT INTO CustomBazaar (item_id, seller_id, cost) "
                     "VALUES (:item_id, :seller_id, :cost)")
        query = query.bindparams(item_id=item.item_id, seller_id=item.player_owner, cost=cost)
        pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
        item.player_owner = -1
        item.item_inlaid_gem_id = 0
        item.update_stored_item()
    except exc.SQLAlchemyError as error:
        print(error)


def show_bazaar_items(item_id):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT CustomBazaar.item_id, CustomBazaar.player_id, CustomBazaar.cost, "
                     "CustomInventory.item_name, CustomInventory.item_type, "
                     "CustomInventory.item_damage_type, CustomInventory.item_elements, "
                     "CustomInventory.item_num_stars, CustomInventory.item_bonus_stat, "
                     "CustomInventory.item_base_dmg_min, CustomInventory.item_base_dmg_max "
                     "FROM CustomBazaar"
                     "INNER JOIN CustomInventory ON CustomBazaar.item_id = CustomInventory.item_id")
        query = query.bindparams(item_id=item.item_id, seller_id=item.player_owner, cost=cost)
        df = pd.read_sql(pandora_db, query)
        pandora_db.close()
        engine.dispose()

        bazaar_embed = None
    except exc.SQLAlchemyError as error:
        print(error)
        bazaar_embed = None
    return bazaar_embed
