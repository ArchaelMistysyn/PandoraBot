import discord
from discord.ext import commands
import csv
import random
import pandas as pd
import player
import bosses
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import mydb
import globalitems

boss_list = ["Fortress", "Dragon", "Demon", "Paragon"]
fortress_data = pd.read_csv("fortressname.csv")


# Boss class
class CurrentBoss:
    def __init__(self, boss_type_num, boss_type, boss_tier, boss_level):
        self.player_id = 0
        self.boss_type_num = boss_type_num
        self.boss_type = boss_type
        self.boss_tier = boss_tier
        self.boss_lvl = boss_level
        self.boss_name = ""
        self.boss_image = ""
        self.boss_mHP = 0
        self.boss_cHP = 0
        self.boss_typeweak = []
        self.boss_eleweak = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.curse_debuffs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.aura = 0.0
        self.boss_element = 0

    def __str__(self):
        return self.boss_name

    def reset_modifiers(self):
        self.curse_debuffs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.aura = 0.0

    def calculate_hp(self) -> bool:
        if self.boss_cHP <= 0:
            is_alive = False
        else:
            is_alive = True

        return is_alive

    def create_boss_embed(self, dps):
        # img_link = self.boss_image
        img_link = "https://i.ibb.co/0ngNM7h/castle.png"
        match self.boss_tier:
            case 1:
                tier_colour = discord.Colour.green()
                life_emoji = "💚"
                life_bar_middle = "🟩"
            case 2:
                tier_colour = discord.Colour.blue()
                life_emoji = "💙"
                life_bar_middle = "🟦"
            case 3:
                tier_colour = discord.Colour.purple()
                life_emoji = "💜"
                life_bar_middle = "🟪"
            case 4:
                tier_colour = discord.Colour.gold()
                life_emoji = "💛"
                life_bar_middle = "🟧"
            case _:
                tier_colour = discord.Colour.red()
                life_emoji = "❤️"
                life_bar_middle = "🟥"
        life_bar_left = "⬅️"
        life_bar_right = "➡️"
        dps_msg = f"{dps:,} / min"
        boss_title = f'{self.boss_name}'
        boss_field = f'Tier {self.boss_tier} {self.boss_type} - Level {self.boss_lvl}'
        if not self.calculate_hp():
            self.boss_cHP = 0
        boss_hp = f'{life_emoji} ({int(self.boss_cHP):,} / {int(self.boss_mHP):,})'
        bar_length = int(int(self.boss_cHP) / int(self.boss_mHP) * 10)
        hp_bar = life_bar_left
        for x in range(bar_length):
            hp_bar += life_bar_middle
        for y in range(10 - bar_length):
            hp_bar += "⬛"
        hp_bar += life_bar_right
        boss_hp += f'\n{hp_bar}'
        boss_weakness = f'Weakness: '
        for x in self.boss_typeweak:
            boss_weakness += str(x)
        for idy, y in enumerate(self.boss_eleweak):
            if y == 1:
                boss_weakness += globalitems.global_element_list[idy]
        embed_msg = discord.Embed(colour=tier_colour,
                                  title=boss_title,
                                  description="")
        embed_msg.set_image(url=img_link)
        embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
        embed_msg.add_field(name=boss_weakness, value="", inline=False)
        embed_msg.add_field(name="Current DPS: ", value=dps_msg, inline=False)
        return embed_msg

    def generate_boss_name_image(self, boss_type, boss_tier):
        fortress_list_t1 = ["Ominous Keep", "Twisted Stronghold"]
        fortress_list_t2 = ["Malignant Fortress", "Malevolant Castle"]
        fortress_list_t3 = ["Sinful Spire", "Malefic Citadel"]
        fortress_list_t4 = ["XVI - Aurora, The Fortress"]
        fortress_names = [fortress_list_t1, fortress_list_t2, fortress_list_t3, fortress_list_t4]

        dragon_list_t1 = ["Zelphyros, Wind", "Sahjvadiir, Earth"]
        dragon_list_t2 = ["Arkadrya, Lightning", "Phyyratha, Fire", "Elyssrya, Water"]
        dragon_list_t3 = ["Y'thana, Light", "Rahk'vath, Shadow"]
        dragon_list_t4 = ["VII - Astratha, The Dimensional"]
        dragon_names = [dragon_list_t1, dragon_list_t2, dragon_list_t3, dragon_list_t4]

        demon_list_t1 = ["Beelzebub", "Azazel", "Astaroth", "Belial"]
        demon_list_t2 = ["Abbadon", "Asura", "Baphomet", "Charybdis"]
        demon_list_t3 = ["Iblis", "Lilith", "Ifrit", "Scylla"]
        demon_list_t4 = ["VIII - Tyra, The Behemoth"]
        demon_names = [demon_list_t1, demon_list_t2, demon_list_t3, demon_list_t4]

        paragon_list_t1 = ["0 - Karma, The Reflection", "I - Runa, The Magic", "VI - Kama, The Love",
                           "IX - Alaya, The Memory", "XIV - Arcelia, The Clarity"]
        paragon_list_t2 = ["XVII - Nova, The Star", "XVIII - Luna, The Moon", "XIX - Luma, The Sun",
                           "XX - Aria, The Reqiuem", "XXI - Ultima, The Creation"]
        paragon_list_t3 = ["V - Arkaya, The Duality", "X - Chrona, The Temporal", "XI - Nua, The Heavens",
                           "XII - Rua, The Abyss", "XIII - Thana, The Death"]
        paragon_list_t4 = ["II - Pandora, The Celestial", "XV - Diabla, The Primordial"]
        paragon_list_t5 = ["III - Oblivia, The Void", "IV - Akasha, The Infinite"]
        paragon_list_t6 = ["XXX - Eleuia, The Wish"]
        paragon_names = [paragon_list_t1, paragon_list_t2, paragon_list_t3,
                         paragon_list_t4, paragon_list_t5, paragon_list_t6]

        boss_name = ""
        boss_image = ""
        match boss_type:
            case "Fortress":
                name_selector = random.randint(1, len(fortress_names[(boss_tier - 1)]))
                boss_suffix = fortress_names[(boss_tier - 1)][(name_selector - 1)]
                if boss_tier != 4:
                    boss_prefix, boss_element = get_boss_descriptor(boss_type)
                    boss_name = boss_prefix + "the " + boss_suffix
                    boss_image = f'https://kyleportfolio.ca/botimages/bosses/{boss_type}{boss_tier}.png'
                    self.boss_element = boss_element
                else:
                    boss_name = boss_suffix
                    boss_image = ""
                    self.boss_element = 9
            case "Dragon":
                name_selector = random.randint(1, len(dragon_names[(boss_tier - 1)]))
                boss_name = dragon_names[(boss_tier - 1)][(name_selector - 1)]
                temp_name_split = boss_name.split()
                boss_element = temp_name_split[1]
                if boss_tier != 4:
                    self.boss_element = globalitems.element_names.index(boss_element)
                    boss_name += " Dragon"
                    boss_image = f'https://kyleportfolio.ca/botimages/bosses/{boss_type}{boss_tier}.png'
                else:
                    self.boss_element = 8
                    boss_image = ""
            case "Demon":
                name_selector = random.randint(1, len(demon_names[(boss_tier - 1)]))
                boss_name = demon_names[(boss_tier - 1)][(name_selector - 1)]
                if boss_tier != 4:
                    boss_colour, boss_element = get_boss_descriptor(boss_type)
                    boss_name = f'{boss_colour} {boss_name}'
                    self.boss_element = boss_element
                    boss_image = f'https://kyleportfolio.ca/botimages/bosses/{boss_type}{boss_colour}{boss_tier}.png'
                else:
                    boss_name = demon_list_t4[0]
                    boss_image = ""
                    self.boss_element = 9
            case "Paragon":
                name_selector = random.randint(1, len(paragon_names[(boss_tier - 1)]))
                boss_name = paragon_names[(boss_tier - 1)][(name_selector - 1)]
                boss_image = f'https://kyleportfolio.ca/botimages/bosses/{boss_type}{boss_tier}.png'
                self.boss_element = 9
            case _:
                boss_name = "error"
        self.boss_image = boss_image
        self.boss_name = boss_name


def get_boss_details(channel_num):
    if channel_num < 4:
        max_types = channel_num
    else:
        max_types = 3
    random_boss_type = random.randint(0, max_types)
    selected_boss_type = boss_list[random_boss_type]
    boss_tier = get_random_bosstier(selected_boss_type)
    if boss_tier < 5:
        level = random.randint(1, 9)
        if channel_num == 1:
            channel_bonus = 30
        elif channel_num == 2:
            channel_bonus = 50
        elif channel_num == 3:
            channel_bonus = 60
        elif channel_num == 4:
            channel_bonus = 80
        level += channel_bonus
    else:
        level = 99
    return level, selected_boss_type, boss_tier


def restore_solo_bosses(channel_id):
    raid_id_df = get_raid_id(channel_id, -1)
    restore_raid_list = []
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        if len(raid_id_df.index) != 0:
            for index, row in raid_id_df.iterrows():
                raid_id = int(row["raid_id"])
                query = text("SELECT * FROM BossList WHERE raid_id = :id_check")
                query = query.bindparams(id_check=raid_id)
                df = pd.read_sql(query, pandora_db)
                player_id = int(df["player_id"].values[0])
                boss_name = str(df["boss_name"].values[0])
                boss_tier = int(df["boss_tier"].values[0])
                boss_level = int(df["boss_level"].values[0])
                boss_type_num = int(df["boss_type_num"].values[0])
                boss_type = str(df["boss_type"].values[0])
                boss_mHP = int(df["boss_mHP"].values[0])
                boss_cHP = int(df["boss_cHP"].values[0])
                temp_types = list(df['boss_typeweak'].values[0].split(';'))
                boss_typeweak = temp_types
                temp_elements = list(df['boss_eleweak'].values[0].split(';'))
                boss_eleweak = list(map(int, temp_elements))
                boss_image = str(df["boss_image"].values[0])
                boss_object = CurrentBoss(boss_type_num, boss_type, boss_tier, boss_level)
                boss_object.player_id=player_id
                boss_object.boss_name = boss_name
                boss_object.boss_mHP = boss_mHP
                boss_object.boss_cHP = boss_cHP
                boss_object.boss_typeweak = boss_typeweak
                boss_object.boss_eleweak = boss_eleweak
                boss_object.boss_image = boss_image
                restore_raid_list.append(boss_object)
        pandora_db.close()
        engine.dispose()
        return restore_raid_list
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
        return restore_raid_list


def spawn_boss(channel_id, player_id, new_boss_tier, selected_boss_type, boss_level, channel_num):
    raid_id = get_raid_id(channel_id, player_id)
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        if raid_id != 0:
            query = text("SELECT * FROM BossList WHERE raid_id = :id_check")
            query = query.bindparams(id_check=raid_id)
            df = pd.read_sql(query, pandora_db)
            player_id = int(df["player_id"].values[0])
            boss_name = str(df["boss_name"].values[0])
            boss_tier = int(df["boss_tier"].values[0])
            boss_level = int(df["boss_level"].values[0])
            boss_type_num = int(df["boss_type_num"].values[0])
            boss_type = str(df["boss_type"].values[0])
            boss_mHP = int(df["boss_mHP"].values[0])
            boss_cHP = int(df["boss_cHP"].values[0])
            temp_types = list(df['boss_typeweak'].values[0].split(';'))
            boss_typeweak = temp_types
            temp_elements = list(df['boss_eleweak'].values[0].split(';'))
            boss_eleweak = list(map(int, temp_elements))
            boss_image = str(df["boss_image"].values[0])
            boss_object = CurrentBoss(boss_type_num, boss_type, boss_tier, boss_level)
            boss_object.boss_name = boss_name
            boss_object.boss_mHP = boss_mHP
            boss_object.boss_cHP = boss_cHP
            boss_object.boss_typeweak = boss_typeweak
            boss_object.boss_eleweak = boss_eleweak
            boss_object.boss_image = boss_image
        else:
            match selected_boss_type:
                case "Fortress":
                    boss_type_num = 1
                case "Dragon":
                    boss_type_num = 2
                case "Demon":
                    boss_type_num = 3
                case _:
                    boss_type_num = 4

            boss_object = CurrentBoss(boss_type_num, selected_boss_type, new_boss_tier, boss_level)
            boss_object.generate_boss_name_image(selected_boss_type, new_boss_tier)

            boss_eleweak = ""
            num_eleweak = 3
            eleweak_list = random.sample(range(9), num_eleweak)
            for x in eleweak_list:
                boss_object.boss_eleweak[x] = 1
            for y in boss_object.boss_eleweak:
                boss_eleweak += f"{str(y)};"

            num_typeweak = 2
            typeweak_list = random.sample(range(0, 4), num_typeweak)
            boss_typeweak = ""
            for y in typeweak_list:
                new_weakness = get_type(int(y))
                boss_object.boss_typeweak.append(new_weakness)
                boss_typeweak += f"{new_weakness};"
            boss_eleweak = boss_eleweak[:-1]
            boss_typeweak = boss_typeweak[:-1]

            if new_boss_tier <= 4:
                hp_min = get_base_hp(selected_boss_type, channel_num)
                hp_max = int(hp_min * (boss_level * 0.01 + 1))
                subtotal_hp = random.randint(hp_min, hp_max)
                subtotal_hp *= 10 ** int(boss_level / 10)
                subtotal_hp += (new_boss_tier * 0.1) * subtotal_hp
                total_hp = int(subtotal_hp)
            elif new_boss_tier == 5:
                total_hp = 10000000000000
            else:
                total_hp = 999999999999999
            boss_object.boss_mHP = total_hp
            boss_object.boss_cHP = boss_object.boss_mHP
            query = text("INSERT INTO ActiveRaids (channel_id, player_id) VALUES (:input_1, :player_id)")
            query = query.bindparams(input_1=str(channel_id), player_id=player_id)
            pandora_db.execute(query)
            raid_id = get_raid_id(channel_id, player_id)
            query = text("INSERT INTO BossList"
                         "(raid_id, player_id, boss_name, boss_tier, boss_level, boss_type_num, boss_type, "
                         "boss_cHP, boss_mHP, boss_typeweak, boss_eleweak, boss_image) "
                         "VALUES (:raid_id, :player_id, :input_1, :input_2, :input_3, :input_4, :input_5,"
                         ":input_6, :input_7, :input_8, :input_9, :input_10)")
            query = query.bindparams(raid_id=raid_id, player_id=player_id, input_1=boss_object.boss_name,
                                     input_2=new_boss_tier, input_3=boss_level, input_4=boss_type_num,
                                     input_5=selected_boss_type, input_6=str(int(total_hp)), input_7=str(int(total_hp)),
                                     input_8=boss_typeweak, input_9=boss_eleweak, input_10=boss_object.boss_image)
            pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()

    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))

    return boss_object


def get_random_bosstier(boss_type):
    random_number = random.randint(1, 100)
    if random_number <= 10:
        boss_tier = 4
    elif random_number <= 35:
        boss_tier = 3
    elif random_number <= 65:
        boss_tier = 2
    elif random_number <= 100:
        boss_tier = 1
    else:
        boss_tier = 0
    return boss_tier


# generate ele weakness
def get_element(chosen_weakness):
    if chosen_weakness == 0:
        random_number = random.randint(0, 8)
    else:
        random_number = chosen_weakness
    element_temp = globalitems.global_element_list[random_number]

    return element_temp


# generate type weakness
def get_type(chosen_weakness):
    if chosen_weakness == 0:
        random_number = random.randint(1, 4)
    else:
        random_number = chosen_weakness
    match random_number:
        case 1:
            type_temp = '<:cA:1150195102589931641>'
        case 2:
            type_temp = '<:cB:1154266777396711424>'
        case 3:
            type_temp = "<:cC:1150195246588764201>"
        case _:
            type_temp = "<:cD:1150195280969478254>"

    return type_temp


def get_base_hp(base_type, channel_num):
    if channel_num < 4:
        match base_type:
            case "Fortress":
                base_hp = 50000
            case "Dragon":
                base_hp = 60000
            case "Demon":
                base_hp = 75000
            case "Paragon":
                base_hp = 100000
            case _:
                base_hp = 0
    else:
        match base_type:
            case "Fortress":
                base_hp = 1000000
            case "Dragon":
                base_hp = 2000000
            case "Demon":
                base_hp = 3000000
            case "Paragon":
                base_hp = 5000000
            case _:
                base_hp = 0

    return base_hp


def get_boss_descriptor(boss_type):
    match boss_type:
        case "Fortress":
            random_number = random.randint(0, (fortress_data['fortress_name_a'].count()-1))
            boss_info = fortress_data.fortress_name_a[random_number].split(";")
            boss_descriptor = str(boss_info[0])
            boss_element = int(boss_info[1])
            random_number = random.randint(0, (fortress_data['fortress_name_b'].count()-1))
            boss_descriptor += " " + fortress_data.fortress_name_b[random_number] + ", "
        case "Demon":
            demon_colours = ["Crimson", "Azure", "Violet", "Bronze", "Jade", "Ivory", "Stygian", "Gold", "Rose"]
            boss_element = random.randint(0, 8)
            boss_descriptor = demon_colours[boss_element]
    return boss_descriptor, boss_element


def add_participating_player(channel_id, player_id):
    raid_id = get_raid_id(channel_id, 0)
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM RaidPlayers "
                     "WHERE raid_id = :id_check AND player_id = :player_check")
        query = query.bindparams(id_check=raid_id, player_check=player_id)
        df_check = pd.read_sql(query, pandora_db)
        if len(df_check.index) != 0:
            response = " is already in the raid."
        else:
            query = text("INSERT INTO RaidPlayers "
                         "(raid_id, player_id, player_dps)"
                         "VALUES(:raid_id, :player_id, :player_dps)")
            query = query.bindparams(raid_id=raid_id, player_id=player_id, player_dps=0)
            pandora_db.execute(query)
            response = " joined the raid"
        pandora_db.close()
        engine.dispose()
        return response
    except exc.SQLAlchemyError as error:
        print(error)


def update_player_damage(channel_id, player_id, player_damage):
    raid_id = get_raid_id(channel_id, 0)
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("UPDATE RaidPlayers SET player_dps = :new_dps "
                     "WHERE raid_id = :id_check AND player_id = :player_check")
        query = query.bindparams(new_dps=player_damage, id_check=raid_id, player_check=player_id)
        pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)


def update_boss_cHP(channel_id, player_id, new_boss_cHP):
    raid_id = get_raid_id(channel_id, player_id)
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("UPDATE BossList SET boss_cHP = :new_cHP "
                     "WHERE raid_id = :id_check")
        query = query.bindparams(new_cHP=str(int(new_boss_cHP)), id_check=raid_id)
        pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)


def get_damage_list(channel_id):
    raid_id = get_raid_id(channel_id, 0)
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT player_id, player_dps FROM RaidPlayers "
                     "WHERE raid_id = :id_check")
        query = query.bindparams(id_check=raid_id)
        df = pd.read_sql(query, pandora_db)
        username = df["player_id"].values.tolist()
        damage = df["player_dps"].values.tolist()
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)

    return username, damage


def clear_boss_info(channel_id, player_id):
    raid_id = get_raid_id(channel_id, player_id)
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("DELETE FROM ActiveRaids "
                     "WHERE raid_id = :id_check")
        query = query.bindparams(id_check=raid_id)
        pandora_db.execute(query)
        query = text("DELETE FROM BossList "
                     "WHERE raid_id = :id_check")
        query = query.bindparams(id_check=raid_id)
        pandora_db.execute(query)
        query = text("DELETE FROM RaidPlayers "
                     "WHERE raid_id = :id_check")
        query = query.bindparams(id_check=raid_id)
        pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)


def get_raid_id(channel_id, player_id):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        if player_id == -1:
            query = text("SELECT raid_id FROM ActiveRaids "
                         "WHERE channel_id = :id_check")
            query = query.bindparams(id_check=str(channel_id))
            df_check = pd.read_sql(query, pandora_db)
            raid_id = df_check
        else:
            query = text("SELECT raid_id FROM ActiveRaids "
                         "WHERE channel_id = :id_check AND player_id = :player_check")
            query = query.bindparams(id_check=str(channel_id), player_check=player_id)
            df_check = pd.read_sql(query, pandora_db)
            if len(df_check.values) == 0:
                raid_id = 0
            else:
                raid_id = df_check["raid_id"].values[0]
        pandora_db.close()
        engine.dispose()
    except exc.SQLAlchemyError as error:
        print(error)
        raid_id = 0
    return raid_id


def create_dead_boss_embed(channel_id, active_boss, dps):
    active_boss.boss_cHP = 0
    dead_embed = active_boss.create_boss_embed(dps)
    player_list, damage_list = bosses.get_damage_list(channel_id)
    output_list = ""
    for idx, x in enumerate(player_list):
        player_object = player.get_player_by_id(x)
        output_list += f'{str(player_object.player_username)}: {int(damage_list[idx]):,}\n'
    dead_embed.add_field(name="SLAIN", value=output_list, inline=False)
    return dead_embed
