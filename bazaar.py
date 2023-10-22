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


def show_bazaar_items():
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT CustomBazaar.item_id, CustomBazaar.seller_id, CustomBazaar.cost, "
                     "CustomInventory.item_name, CustomInventory.item_type, "
                     "CustomInventory.item_damage_type, CustomInventory.item_elements, "
                     "CustomInventory.item_num_stars, CustomInventory.item_bonus_stat, "
                     "CustomInventory.item_base_dmg_min, CustomInventory.item_base_dmg_max "
                     "FROM CustomBazaar "
                     "INNER JOIN CustomInventory ON CustomBazaar.item_id = CustomInventory.item_id "
                     "ORDER BY CustomInventory.item_tier DESC, CustomInventory.item_base_dmg_max DESC, "
                     "CustomBazaar.cost ASC")
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()

        bazaar_embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                     title="The Bazaar",
                                     description="Open Marketplace")
        if len(df.index) != 0:
            for index, row in df.iterrows():
                item_id = int(row["item_id"])
                seller_id = int(row["seller_id"])
                cost = int(row["cost"])
                item_name = str(row["item_name"])
                item_damage_type = str(row["item_damage_type"])
                temp_elements = list(str(row['item_elements']).split(';'))
                item_elements = list(map(int, temp_elements))
                item_num_stars = int(row["item_num_stars"])
                item_bonus_stat = str(row["item_bonus_stat"])
                item_base_dmg_min = int(row["item_base_dmg_min"])
                item_base_dmg_max = int(row["item_base_dmg_max"])

                item_cost = f"Cost: {cost} Lotus Coins"
                item_damage = f"Average Damage: {int((item_base_dmg_min + item_base_dmg_max) / 2)}"
                if item_bonus_stat:
                    if item_bonus_stat[0].isalpha():
                        item_main_info = f"{item_damage} || Skill: {item_bonus_stat}"
                    else:
                        item_main_info = f"{item_damage} || Base Stat: {item_bonus_stat}"
                else:
                    item_main_info = f"{item_damage}"

                display_stars = ""
                for x in range(item_num_stars):
                    display_stars += "<:estar1:1143756443967819906>"
                for y in range((5 - item_num_stars)):
                    display_stars += "<:ebstar2:1144826056222724106>"

                item_types = f'{item_damage_type}'
                for idz, z in enumerate(item_elements):
                    if z == 1:
                        item_types += f'{pandorabot.global_element_list[idz]}'

                seller = player.get_player_by_id(seller_id)
                bazaar_embed.add_field(name=f"{item_name}", value=f"{item_cost} || Item ID: {item_id}", inline=False)
                bazaar_embed.add_field(name="", value=f"{display_stars} {item_types}", inline=False)
                bazaar_embed.add_field(name="", value=item_main_info, inline=False)
                bazaar_embed.add_field(name="", value=f"Listed by: {seller.player_username}", inline=False)
    except exc.SQLAlchemyError as error:
        print(error)
        bazaar_embed = None
    return bazaar_embed


def get_seller_by_item(item_id):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT seller_id FROM CustomBazaar WHERE item_id = :item_check")
        query = query.bindparams(item_check=item_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            seller_id = int(df['seller_id'].values[0])
        else:
            seller_id = 0
    except exc.SQLAlchemyError as error:
        print(error)
        seller_id = 0
    return seller_id


def get_item_cost(item_id):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT cost FROM CustomBazaar WHERE item_id = :item_check")
        query = query.bindparams(item_check=item_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            item_cost = int(df['cost'].values[0])
        else:
            item_cost = 0
    except exc.SQLAlchemyError as error:
        print(error)
        item_cost = 0
    return item_cost


def buy_item(item_id):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("DELETE FROM CustomBazaar WHERE item_id = :item_check")
        query = query.bindparams(item_check=item_id)
        pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()

        seller_id = get_seller_by_item(item_id)
        seller_object = player.get_player_by_id(seller_id)
        item_cost = get_item_cost(item_id)
        seller_object.player_coins += item_cost
        seller_object.set_player_field("player_coins", seller_object.player_coins)

    except exc.SQLAlchemyError as error:
        print(error)

