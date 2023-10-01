import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import mydb
import pandas as pd
import pandorabot


class TarotCard:
    def __init__(self, player_id, card_numeral, card_variant, card_name, card_qty,
                 num_stars, card_enhancement, card_bonus_stat):
        self.player_id = player_id
        self.card_numeral = card_numeral
        self.card_variant = card_variant
        self.card_name = card_name
        self.card_qty = card_qty
        self.num_stars = num_stars
        self.card_enhancement = card_enhancement
        self.card_bonus_stat = card_bonus_stat
        card_file = f'{self.card_numeral}variant{self.card_variant}'
        self.card_image_link = f"https://kyleportfolio.ca/botimages/tarot/{card_file}.png"

    def set_tarot_field(self, field_name, field_value):
        tarot_check = check_tarot(self.player_id, self.card_name, self.card_variant)
        if tarot_check:
            try:
                engine_url = mydb.get_engine_url()
                engine = sqlalchemy.create_engine(engine_url)
                pandora_db = engine.connect()
                query = text(f"UPDATE TarotInventory SET {field_name} = :input_1 WHERE player_id = :player_check")
                query = query.bindparams(player_check=self.player_id, input_1=field_value)
                pandora_db.execute(query)
                pandora_db.close()
                engine.dispose()
            except exc.SQLAlchemyError as error:
                print(error)

    def add_tarot_card(self):
        tarot_check = check_tarot(self.player_id, self.card_name, self.card_variant)
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            if tarot_check:
                already_exists = True
            else:
                query = text("INSERT INTO TarotInventory "
                             "VALUES (:input_1, :input_2, :input_3, :input_4,"
                             ":input_5, :input_6, :input_7, :input_8)")
                query = query.bindparams(input_1=player_id, input_2=card_numeral, input_3=card_variant,
                                         input_4=card_name, input_5=card_qty, input_6=num_stars,
                                         input_7=card_enhancement, input_8=card_bonus_stat)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except exc.SQLAlchemyError as error:
            print(error)


def check_tarot(player_id, card_name, card_variant):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM TarotInventory WHERE player_id = :id_check "
                     "AND card_name = :card_check AND card_variant = :card_variant")
        query = query.bindparams(id_check=player_id, card_check=card_name, card_variant=card_variant)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            player_id = int(df['player_id'].values[0])
            card_numeral = str(df['card_numeral'].values[0])
            card_variant = int(df['card_variant'].values[0])
            card_name = str(df['card_name'].values[0])
            card_qty = int(df['card_qty'].values[0])
            num_stars = int(df['num_stars'].values[0])
            card_enhancement = int(df['card_enhancement'].values[0])
            card_bonus_stat = int(df['card_bonus_stat'].values[0])
            selected_tarot = TarotCard(player_id, card_numeral, card_variant, card_name, card_qty,
                                       num_stars, card_enhancement, card_bonus_stat)
        else:
            selected_tarot = None
    except exc.SQLAlchemyError as error:
        print(error)
        selected_tarot = None
    return selected_tarot


def tarot_numeral_list(position):
    card_num_list = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                     "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
    return card_num_list[position]


def get_numeral_by_number(roman_numeral):
    card_num_list = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                     "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
    return card_num_list.index(roman_numeral)


def tarot_card_list(position):
    card_name_list = ["Karma, The Reflection", "Runa, The Magic", "Pandora, The Celestial", "Oblivia, The Void",
                      "Akasha, The Infinite", "Arkaya, The Duality", "Kama, The Love", "Astratha, The Dragon",
                      "Tyra, The Behemoth", "Alaya, The Memory", "Chrona, The Temporal", "Nua, The Heavens",
                      "Rua, The Abyss", "Thana, The Death", "Arcelia, The Clarity", "Diabla, The Primordial",
                      "Aurora, The Fortress", "Nova, The Star", "Luna, The Moon", "Luma, The Sun",
                      "Aria, The Requiem", "Ultima, The Creation"]
    return card_name_list[position]


def collection_check(player_id):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM TarotInventory WHERE player_id = :id_check")
        query = query.bindparams(id_check=player_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            collection_count = df.shape[0]
        else:
            collection_count = 0
    except exc.SQLAlchemyError as error:
        print(error)
        collection_count = 0
    return collection_count
