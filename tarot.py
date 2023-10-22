import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc

import discord
import random
import inventory
import mydb
import pandas as pd
import pandorabot

paragon_t1 = ["Karma, The Reflection", "Runa, The Magic",
              "Arkaya, The Duality", "Alaya, The Memory", "Aria, The Requiem"]
paragon_t2 = ["Nova, The Star", "Luna, The Moon", "Luma, The Sun", "Arcelia, The Clarity", "Kama, The Love"]
paragon_t3 = ["Thana, The Death", "Chrona, The Temporal", "Rua, The Abyss", "Nua, The Heavens", "Ultima, The Creation"]
paragon_t4 = ["Pandora, The Celestial", "Diabla, The Primordial",
              "Tyra, The Behemoth", "Astratha, The Dragon", "Aurora, The Fortress"]
paragon_t5 = ["Oblivia, The Void", "Akasha, The Infinite"]
paragon_t6 = ["Eleuia, The Wish"]
paragon_list = [paragon_t1, paragon_t2, paragon_t3, paragon_t4, paragon_t5, paragon_t6]


class TarotCard:
    def __init__(self, player_id, card_numeral, card_variant, card_name, card_qty,
                 num_stars, card_enhancement):
        self.player_id = player_id
        self.card_numeral = card_numeral
        self.card_variant = card_variant
        self.card_name = card_name
        self.card_qty = card_qty
        self.num_stars = num_stars
        self.card_tier = 1
        self.card_enhancement = card_enhancement
        card_file = f'{self.card_numeral}variant{self.card_variant}'
        self.card_image_link = f"https://kyleportfolio.ca/botimages/tarot/{card_file}.png"

    def get_base_damage(self):
        damage_value = 10000
        if self.card_tier == 5:
            damage_value = 25000
        elif self.card_tier == 6:
            damage_value = 50000
        if self.card_variant == 2:
            damage_value *= 2
        base_damage = damage_value * self.num_stars
        return base_damage

    def display_tarot_bonus_stat(self):
        display_method = 1
        buff_type = ""
        buff_value = 0
        card_num = get_number_by_tarot(self.card_name)
        match card_num:
            case 0:
                if self.card_variant == 1:
                    buff_type = "Ice Resistance"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Ice Damage"
                    buff_value = self.num_stars * 20
            case 1:
                if self.card_variant == 1:
                    buff_type = "Fire Resistance"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Fire Damage"
                    buff_value = self.num_stars * 20
            case 2:
                if self.card_variant == 1:
                    buff_type = "Celestial Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Celestial Curse"
                    buff_value = self.num_stars * 30
            case 3:
                if self.card_variant == 1:
                    buff_type = "Defence Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Class Mastery"
                    buff_value = self.num_stars * 8
            case 4:
                if self.card_variant == 1:
                    buff_type = "Critical Chance"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Critical Strike Multiplier"
                    buff_value = self.num_stars * 40
            case 5:
                if self.card_variant == 1:
                    buff_type = "Lightning Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Lightning Curse"
                    buff_value = self.num_stars * 30
            case 6:
                if self.card_variant == 1:
                    buff_type = "Health Multiplier"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Omni Resistance"
                    buff_value = self.num_stars * 10
            case 7:
                if self.card_variant == 1:
                    buff_type = "Final Damage"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Dragon Bane"
                    buff_value = self.num_stars * 40
            case 8:
                if self.card_variant == 1:
                    display_method = 2
                    buff_type = "Health Bonus"
                    buff_value = 250 * self.num_stars
                else:
                    buff_type = "Demon Bane"
                    buff_value = self.num_stars * 40
            case 9:
                if self.card_variant == 1:
                    buff_type = "Lightning Resistance"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Lightning Damage"
                    buff_value = self.num_stars * 20
            case 10:
                if self.card_variant == 1:
                    buff_type = "Earth Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Earth Curse"
                    buff_value = self.num_stars * 30
            case 11:
                if self.card_variant == 1:
                    buff_type = "Light Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Light Curse"
                    buff_value = self.num_stars * 30
            case 12:
                if self.card_variant == 1:
                    buff_type = "Shadow Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Shadow Curse"
                    buff_value = self.num_stars * 30
            case 13:
                if self.card_variant == 1:
                    buff_type = "Ice Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Ice Penetration"
                    buff_value = self.num_stars * 30
            case 14:
                if self.card_variant == 1:
                    buff_type = "Water Penetration"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Water Curse"
                    buff_value = self.num_stars * 20
            case 15:
                if self.card_variant == 1:
                    buff_type = "Fire Penetration"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Fire Curse"
                    buff_value = self.num_stars * 30
            case 16:
                if self.card_variant == 1:
                    buff_type = "Damage Mitigation"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Fortress Bane"
                    buff_value = self.num_stars * 40
            case 17:
                if self.card_variant == 1:
                    buff_type = "Health Regen"
                    buff_value = self.num_stars * 25
                else:
                    buff_type = "Omni Damage"
                    buff_value = self.num_stars * 20
            case 18:
                if self.card_variant == 1:
                    buff_type = "Shadow Resistance"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Shadow Damage"
                    buff_value = self.num_stars * 20
            case 19:
                if self.card_variant == 1:
                    buff_type = "Light Resistance"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Light Damage"
                    buff_value = self.num_stars * 20
            case 20:
                if self.card_variant == 1:
                    buff_type = "Wind Resistance"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Wind Damage"
                    buff_value = self.num_stars * 20
            case 21:
                if self.card_variant == 1:
                    buff_type = "Earth Resistance"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Earth Damage"
                    buff_value = self.num_stars * 20
            case 22:
                if self.card_variant == 1:
                    buff_type = "Omni Curse"
                    buff_value = self.num_stars * 15
                else:
                    buff_type = "Omni Aura"
                    buff_value = self.num_stars * 20
        bonus_stat_string = f"{buff_type} +{buff_value}"
        if display_method == 1:
            bonus_stat_string += "%"
        return bonus_stat_string

    def synthesize_tarot(self):
        new_qty = self.card_qty - 1
        self.set_tarot_field("card_qty", new_qty)
        random_num = random.randint(1, 100)
        success = False
        match self.num_stars:
            case 1:
                if random_num <= 50:
                    success = True
            case 2:
                if random_num <= 30:
                    success = True
            case 3:
                if random_num <= 15:
                    success = True
            case 4:
                if random_num <= 5:
                    success = True
        if success:
            self.num_stars += 1
            self.set_tarot_field("num_stars", self.num_stars)
            outcome = "Synthesis Success!"
        else:
            outcome = "Synthesis Failed!"
        return outcome

    def set_tarot_field(self, field_name, field_value):
        tarot_check = check_tarot(self.player_id, self.card_name, self.card_variant)
        if tarot_check:
            try:
                engine_url = mydb.get_engine_url()
                engine = sqlalchemy.create_engine(engine_url)
                pandora_db = engine.connect()
                query = text(f"UPDATE TarotInventory SET {field_name} = :input_1 "
                             f"WHERE player_id = :player_check AND card_numeral = :numeral_check "
                             f"AND card_variant = :variant_check")
                query = query.bindparams(input_1=field_value, player_check=self.player_id,
                                         numeral_check=self.card_numeral, variant_check=self.card_variant)
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
                query = text("INSERT INTO TarotInventory (player_id, card_numeral, card_variant, "
                             "card_name, card_qty, num_stars, card_enhancement) "
                             "VALUES (:input_1, :input_2, :input_3, :input_4, "
                             ":input_5, :input_6, :input_7)")
                query = query.bindparams(input_1=self.player_id, input_2=self.card_numeral, input_3=self.card_variant,
                                         input_4=self.card_name, input_5=self.card_qty, input_6=self.num_stars,
                                         input_7=self.card_enhancement)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except exc.SQLAlchemyError as error:
            print(error)


def get_tarot_tier(card_name):
    for idx, x in enumerate(paragon_list):
        if card_name in x:
            tarot_tier = idx + 1
            return tarot_tier


def create_tarot_embed(tarot_card):
    gear_colour, gear_emoji = inventory.get_gear_tier_colours(tarot_card.card_tier)
    display_stars = ""
    for x in range(tarot_card.num_stars):
        display_stars += "<:estar1:1143756443967819906>"
    for y in range((5 - tarot_card.num_stars)):
        display_stars += "<:ebstar2:1144826056222724106>"
    card_title = f"{tarot_card.card_numeral} - {tarot_card.card_name}"
    if tarot_card.card_variant == 1:
        card_title += " [Standard]"
    else:
        card_title += " [Premium]"
    tarot_embed = discord.Embed(colour=gear_colour,
                                title=card_title,
                                description=display_stars)
    base_damage = tarot_card.get_base_damage()
    tarot_embed.add_field(name=f"",
                          value=f"Base Damage: {base_damage:,} - {base_damage:,}",
                          inline=False)
    tarot_embed.add_field(name=f"",
                          value=tarot_card.display_tarot_bonus_stat(),
                          inline=False)
    tarot_embed.set_image(url=tarot_card.card_image_link)
    return tarot_embed


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
            selected_tarot = TarotCard(player_id, card_numeral, card_variant, card_name, card_qty,
                                       num_stars, card_enhancement)
            selected_tarot.card_tier = get_tarot_tier(selected_tarot.card_name)
        else:
            selected_tarot = None
    except exc.SQLAlchemyError as error:
        print(error)
        selected_tarot = None
    return selected_tarot


def tarot_numeral_list(position):
    card_num_list = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                     "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXX"]
    return card_num_list[position]


def get_number_by_numeral(roman_numeral):
    card_num_list = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                     "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXX"]
    return card_num_list.index(roman_numeral)


def tarot_card_list(position):
    card_name_list = ["Karma, The Reflection", "Runa, The Magic", "Pandora, The Celestial", "Oblivia, The Void",
                      "Akasha, The Infinite", "Arkaya, The Duality", "Kama, The Love", "Astratha, The Dragon",
                      "Tyra, The Behemoth", "Alaya, The Memory", "Chrona, The Temporal", "Nua, The Heavens",
                      "Rua, The Abyss", "Thana, The Death", "Arcelia, The Clarity", "Diabla, The Primordial",
                      "Aurora, The Fortress", "Nova, The Star", "Luna, The Moon", "Luma, The Sun",
                      "Aria, The Requiem", "Ultima, The Creation", "Eleuia, The Wish"]
    return card_name_list[position]


def get_number_by_tarot(card_name):
    card_name_list = ["Karma, The Reflection", "Runa, The Magic", "Pandora, The Celestial", "Oblivia, The Void",
                      "Akasha, The Infinite", "Arkaya, The Duality", "Kama, The Love", "Astratha, The Dragon",
                      "Tyra, The Behemoth", "Alaya, The Memory", "Chrona, The Temporal", "Nua, The Heavens",
                      "Rua, The Abyss", "Thana, The Death", "Arcelia, The Clarity", "Diabla, The Primordial",
                      "Aurora, The Fortress", "Nova, The Star", "Luna, The Moon", "Luma, The Sun",
                      "Aria, The Requiem", "Ultima, The Creation", "Eleuia, The Wish"]
    position = card_name_list.index(card_name)
    return position


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
