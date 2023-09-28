import pandas as pd
import csv
from csv import DictReader
import inventory
import damagecalc
import math
import loot
import discord
import random
import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import mydb


class PlayerProfile:
    def __init__(self):
        self.player_id = 0
        self.player_name = ""
        self.player_username = ""
        self.player_stamina = 0
        self.player_exp = 0
        self.player_lvl = 0
        self.player_echelon = 0
        self.equipped_weapon = 0
        self.equipped_armour = 0
        self.equipped_acc = 0
        self.equipped_wing = 0
        self.equipped_crest = 0
        self.player_coins = 0
        self.player_class = ""
        self.player_quest = 0

        self.player_mHP = 1000
        self.player_cHP = self.player_mHP

        self.critical_chance = 0.0
        self.critical_multiplier = 0.0
        self.attack_speed = 0.0
        self.damage_mitigation = 0.0
        self.elemental_penetration = 0.0
        self.defence_penetration = 0.0
        self.final_damage = 0.0
        self.aura = 0.0
        self.curse = 0.0
        self.player_damage = 0.0
        self.hit_multiplier = 0.0
        self.special_multipliers = 0.0
        self.class_multiplier = 0.0
        self.hp_multiplier = 0.0

    def __str__(self):
        return str(self.player_name)

    def set_player_field(self, field_name, field_value):
        if field_name == "exp":
            max_exp = get_max_exp(self.player_lvl)
            while field_value > max_exp and self.player_lvl < 100:
                field_value -= max_exp
                self.player_exp = field_value
                self.player_lvl += 1
                query = text(f"UPDATE PlayerList SET player_lvl = :input_1 WHERE player_id = :player_check")
                query = query.bindparams(player_check=int(self.player_id), input_1=self.player_lvl)
                pandora_db.execute(query)
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text(f"UPDATE PlayerList SET {field_name} = :input_1 WHERE player_id = :player_check")
            query = query.bindparams(player_check=int(self.player_id), input_1=field_value)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))

    def add_new_player(self, selected_class):
        self.player_class = selected_class
        self.player_quest = 1
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("SELECT * FROM PlayerList WHERE player_name = :player_check")
            query = query.bindparams(player_check=self.player_name)
            df = pd.read_sql(query, pandora_db)

            if not df.empty:
                response = f"Player {self.player_name} is already registered."
            else:
                query = text("SELECT * FROM PlayerList WHERE player_username = :username_check")
                query = query.bindparams(username_check=self.player_username)
                df = pd.read_sql(query, pandora_db)

                if not df.empty:
                    response = f"Username {self.player_username} is taken. Please pick a new username."
                else:
                    query = text("INSERT INTO PlayerList "
                                 "(player_name, player_username, player_lvl, player_exp, player_echelon, player_quest, "
                                 "player_stamina, player_class, player_coins, player_equip_weapon, "
                                 "player_equip_armour, player_equip_acc, player_equip_wing, player_equip_crest) "
                                 "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6,"
                                 ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, :input_13, :input_14)")
                    query = query.bindparams(input_1=str(self.player_name), input_2=str(self.player_username),
                                             input_3=int(self.player_lvl), input_4=int(self.player_exp),
                                             input_5=int(self.player_echelon), input_6=int(self.player_quest),
                                             input_7=int(self.player_stamina), input_8=str(self.player_class),
                                             input_9=int(self.player_coins), input_10=int(self.equipped_weapon),
                                             input_11=int(self.equipped_armour), input_12=int(self.equipped_acc),
                                             input_13=int(self.equipped_wing), input_14=int(self.equipped_crest))
                    pandora_db.execute(query)
                    response = f"Player {self.player_name} has been registered to play. Welcome {self.player_username}!"
                    response += f"\nPlease use the !quest command to proceed."

                    registered_player = get_player_by_name(self.player_name)

                    query = text("INSERT INTO QuestTokens (player_id, token_1) VALUES(:player_id, :input_1)")
                    query = query.bindparams(player_id=registered_player.player_id, input_1=1)
                    pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
            response = "Error!"
        return response

    def update_tokens(self, quest_num, new_token_count):
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            field_name = f"token_{quest_num}"
            query = text(f"UPDATE QuestTokens SET {field_name} = :field_value WHERE player_id = :player_check")
            query = query.bindparams(field_value=int(new_token_count), player_check=self.player_id)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
            response = "Error!"

    def check_tokens(self, quest_num):
        num_tokens = 0
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            token_field = f"token_{quest_num}"
            query = text(f"SELECT {token_field} FROM QuestTokens WHERE player_id = :player_check")
            query = query.bindparams(player_check=int(self.player_id))
            df = pd.read_sql(query, pandora_db)
            pandora_db.close()
            engine.dispose()
            num_tokens = int(df[token_field].values[0])
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
            response = "Error!"
        return num_tokens

    def spend_stamina(self, cost) -> bool:
        is_spent = False
        if self.player_stamina >= cost:
            self.player_stamina -= cost
            self.set_player_field("player_stamina", self.player_stamina)
            is_spent = True
        return is_spent

    def get_equipped(self):
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("SELECT * FROM PlayerList WHERE player_id = :player_check")
            query = query.bindparams(player_check=self.player_id)
            df = pd.read_sql(query, pandora_db)
            pandora_db.close()
            engine.dispose()
            self.equipped_weapon = int(df['player_equip_weapon'].values[0])
            self.equipped_armour = int(df['player_equip_armour'].values[0])
            self.equipped_acc = int(df['player_equip_acc'].values[0])
            self.equipped_wing = int(df['player_equip_wing'].values[0])
            self.equipped_crest = int(df['player_equip_crest'].values[0])
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))

    def get_player_multipliers(self, boss_cHP, boss_mHP):
        self.get_equipped()

        base_critical_chance = 10.0
        base_attack_speed = 1.0
        base_damage_mitigation = 0.0
        base_player_hp = 1000
        sit_damage_multiplier = 0.0
        damage_multiplier = 0.0
        mitigation_multiplier = 0.0
        self.critical_chance = 0.0
        self.attack_speed = 0.0
        self.critical_multiplier = 0.0
        self.damage_mitigation = 0.0
        self.elemental_penetration = 0.0
        self.final_damage = 0.0
        self.aura = 0.0
        self.curse = 0.0
        self.hit_multiplier = 1.0
        self.player_damage = 0.0
        self.special_multipliers = 0.0
        self.class_multiplier = 0.0
        class_bonus = 0.0
        self.hp_multiplier = 0.0
        is_mastery = False

        if self.equipped_weapon != 0:
            e_weapon = inventory.read_custom_item(self.equipped_weapon)
            e_weapon.update_damage()
            self.player_damage += (e_weapon.item_damage_min + e_weapon.item_damage_max) / 2
            base_attack_speed = float(e_weapon.item_bonus_stat)
            self.assign_roll_values(e_weapon, "W")
            self.assign_gem_values(e_weapon)
        if self.equipped_armour != 0:
            e_armour = inventory.read_custom_item(self.equipped_armour)
            e_armour.update_damage()
            self.player_damage += (e_armour.item_damage_min + e_armour.item_damage_max) / 2
            self.assign_roll_values(e_armour, "A")
            base_damage_mitigation = float(e_armour.item_bonus_stat)
            self.assign_gem_values(e_armour)
        if self.equipped_acc != 0:
            e_acc = inventory.read_custom_item(self.equipped_acc)
            e_acc.update_damage()
            self.player_damage += (e_acc.item_damage_min + e_acc.item_damage_max) / 2
            self.assign_roll_values(e_acc, "Y")
            self.assign_gem_values(e_acc)
            x, y, z = damagecalc.accessory_ability_multipliers(
                                                     e_acc.item_bonus_stat,
                                                     boss_cHP,
                                                     boss_mHP,
                                                     self.player_cHP)
            damage_multiplier += x
            sit_damage_multiplier += y
            mitigation_multiplier += z
        if self.equipped_wing != 0:
            e_wing = inventory.read_custom_item(self.equipped_wing)
            e_wing.update_damage()
            self.player_damage += (e_wing.item_damage_min + e_wing.item_damage_max) / 2
            self.assign_roll_values(e_wing, "G")
            self.assign_gem_values(e_wing)
            x, y, z = damagecalc.accessory_ability_multipliers(
                e_wing.item_bonus_stat,
                boss_cHP,
                boss_mHP,
                self.player_cHP)
            damage_multiplier += x
            sit_damage_multiplier += y
            mitigation_multiplier += z
        if self.equipped_crest != 0:
            e_crest = inventory.read_custom_item(self.equipped_crest)
            e_crest.update_damage()
            match e_crest.item_bonus_stat:
                case "Elemental Fractal":
                    if self.equipped_weapon != 0:
                        self.special_multipliers += len(e_weapon.item_elements)
                case "Omega Critical":
                    self.special_multipliers += 5
                case "Specialized Mastery":
                    is_mastery = True
                case "Ignore Protection":
                    self.defence_penetration += 0.3
                    self.elemental_penetration += 0.4
                case "Perfect Precision":
                    base_critical_chance += 10
                case "Resistance Bypass":
                    self.elemental_penetration += 0.4
                case "Extreme Vitality":
                    self.hp_multiplier += 5
                case "Defence Bypass":
                    self.defence_penetration += 0.3
                case _:
                    nothing = 0
            self.player_damage += (e_crest.item_damage_min + e_crest.item_damage_max) / 2
            self.assign_roll_values(e_crest, "C")
            self.assign_gem_values(e_crest)

        self.critical_chance = (1 + self.critical_chance) * base_critical_chance
        self.attack_speed = (1 + self.attack_speed) * base_attack_speed
        self.damage_mitigation = (1 + (mitigation_multiplier + self.damage_mitigation)) * base_damage_mitigation
        self.player_mHP = int(base_player_hp * (1 + self.hp_multiplier))
        self.final_damage += damage_multiplier
        if boss_cHP != -1:
            self.final_damage += sit_damage_multiplier

        if self.equipped_weapon != 0:
            if e_weapon.item_damage_type == self.player_class:
                class_bonus += 1
        if self.equipped_armour != 0:
            if e_armour.item_damage_type == self.player_class:
                class_bonus += 1
        if self.equipped_acc != 0:
            if e_acc.item_damage_type == self.player_class:
                class_bonus += 1
        if self.equipped_wing != 0:
            if e_wing.item_damage_type == self.player_class:
                class_bonus += 1
        if self.equipped_crest != 0:
            if e_crest.item_damage_type == self.player_class:
                class_bonus += 1
        self.class_multiplier = class_bonus * 0.05
        if is_mastery:
            self.class_multiplier += class_bonus

    def assign_roll_values(self, equipped_item, item_type):
        for x in equipped_item.item_prefix_values:
            roll_tier = int(str(x)[1])
            match str(x)[2]:
                case "1":
                    self.critical_chance += 0.25 * float(roll_tier)
                case "2":
                    self.attack_speed += 0.25 * float(roll_tier)
                case "3":
                    self.elemental_penetration += 0.25 * float(roll_tier)
                case "4":
                    self.final_damage += 0.25 * float(roll_tier)
                case "5":
                    self.damage_mitigation += 0.05 * float(roll_tier)
                case _:
                    no_change = True
        for y in equipped_item.item_suffix_values:
            roll_tier = int(str(y)[1])
            match str(y)[2]:
                case "1":
                    self.critical_multiplier += 0.50 * float(roll_tier)
                case "2":
                    self.aura += 0.25 * float(roll_tier)
                case "3":
                    self.curse += 0.25 * float(roll_tier)
                case "4":
                    if item_type == "W":
                        self.hit_multiplier += float(roll_tier)
                    else:
                        self.hp_multiplier += 0.5 * float(roll_tier)
                case _:
                    no_change = True

    def assign_gem_values(self, e_item):
        gem_id = e_item.item_inlaid_gem_id
        if gem_id != 0:
            e_gem = inventory.read_custom_item(gem_id)
            self.player_damage += (e_gem.item_damage_min + e_gem.item_damage_max) / 2
            for x in e_gem.item_prefix_values:
                buff_type, buff_value = inventory.gem_stat_reader(str(x))
                match buff_type:
                    case "HP":
                        self.hp_multiplier += float(buff_value) * 0.01
                    case "Critical Chance":
                        self.critical_chance += float(buff_value) * 0.01
                    case "Final Damage":
                        self.final_damage += float(buff_value) * 0.01
                    case _:
                        no_change = True
            for y in e_gem.item_suffix_values:
                buff_type, buff_value = inventory.gem_stat_reader(str(y))
                match buff_type:
                    case "Attack Speed":
                        self.attack_speed += float(buff_value) * 0.01
                    case "Damage Mitigation":
                        self.damage_mitigation += float(buff_value) * 0.01
                    case "Critical Damage":
                        self.critical_multiplier += float(buff_value) * 0.01
                    case _:
                        no_change = True

    def equip(self, selected_item) -> str:
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            run_query = True
            match selected_item.item_type:
                case 'W':
                    self.equipped_weapon = selected_item.item_id
                    response = f"Weapon {selected_item.item_id} is now equipped."
                    query_setter = "player_equip_weapon"
                case 'A':
                    self.equipped_armour = selected_item.item_id
                    response = f"Armour {selected_item.item_id} is now equipped."
                    query_setter = "player_equip_armour"
                case 'Y':
                    self.equipped_acc = selected_item.item_id
                    response = f"Accessory {selected_item.item_id} is now equipped."
                    query_setter = "player_equip_acc"
                case 'G':
                    self.equipped_wing = selected_item.item_id
                    response = f"Wing {selected_item.item_id} is now equipped."
                    query_setter = "player_equip_wing"
                case 'C':
                    self.equipped_crest = selected_item.item_id
                    response = f"Crest {selected_item.item_id} is now equipped."
                    query_setter = "player_equip_crest"
                case _:
                    run_query = False
                    response = "Item is not equipable."
            if run_query:
                query = text(f"UPDATE PlayerList SET  {query_setter} = :input_1 WHERE player_id = :player_check")
                query = query.bindparams(player_check=int(self.player_id), input_1=int(selected_item.item_id))
                pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))

        return response

    def check_equipped(self, user, item):
        response = ""
        user.get_equipped()

        match item.item_type:
            case 'W':
                check = self.equipped_weapon
            case 'A':
                check = self.equipped_armour
            case 'Y':
                check = self.equipped_acc
            case 'G':
                check = self.equipped_wing
            case 'C':
                check = self.equipped_crest
            case 'D':
                item_list = []
                if self.equipped_weapon != 0:
                    item_list.append(inventory.read_custom_item(self.equipped_weapon))
                if self.equipped_armour != 0:
                    item_list.append(inventory.read_custom_item(self.equipped_armour))
                if self.equipped_acc != 0:
                    item_list.append(inventory.read_custom_item(self.equipped_acc))
                if self.equipped_wing != 0:
                    item_list.append(inventory.read_custom_item(self.equipped_wing))
                if self.equipped_crest != 0:
                    item_list.append(inventory.read_custom_item(self.equipped_crest))

                for x in item_list:
                    check = x.item_inlaid_gem_id
                    if item.item_id == check:
                        response = f"Dragon Heart Gem {item.item_id} is already inlaid."
            case _:
                response = f"Item {item.item_id} is not recognized."
        if item.item_id == check:
            response = f"Item {item.item_id} is equipped."
        return response

    def create_stamina_embed(self):
        potion_list = ["I1s", "I2s", "I3s", "I4s"]
        potion_msg = ""
        for x in potion_list:
            potion_stock = inventory.check_stock(self, str(x))
            potion_msg += f"\n{loot.get_loot_emoji(str(x))} {potion_stock}x {loot.get_loot_name(str(x))}"
        output = f'<:estamina:1145534039684562994> {self.player_username}\'s stamina: '
        output += str(self.player_stamina)
        embed_msg = discord.Embed(colour=discord.Colour.green(), title="Stamina", description=output)
        embed_msg.add_field(name="", value=potion_msg)
        return embed_msg


def check_username(new_name: str):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList WHERE player_username = :player_check")
        query = query.bindparams(player_check=new_name)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
    if new_name in df['player_username'].values:
        can_proceed = False
    else:
        can_proceed = True
    return can_proceed


def get_player_by_id(player_id: int) -> PlayerProfile:
    target_player = PlayerProfile()
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList WHERE player_id = :player_check")
        query = query.bindparams(player_check=player_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if not df.empty:
            target_player.player_id = int(df["player_id"].values[0])
            target_player.player_name = str(df["player_name"].values[0])
            target_player.player_username = str(df["player_username"].values[0])
            target_player.player_lvl = int(df["player_lvl"].values[0])
            target_player.player_exp = int(df["player_exp"].values[0])
            target_player.player_echelon = int(df["player_echelon"].values[0])
            target_player.player_stamina = int(df["player_stamina"].values[0])
            target_player.player_class = str(df["player_class"].values[0])
            target_player.player_coins = int(df["player_coins"].values[0])
            target_player.player_quest = int(df["player_quest"].values[0])
            target_player.get_equipped()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
        target_player.player_name = player_name
    return target_player


def get_player_by_name(player_name: str) -> PlayerProfile:
    target_player = PlayerProfile()
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList WHERE player_name = :player_check")
        query = query.bindparams(player_check=player_name)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if not df.empty:
            target_player.player_name = str(df["player_name"].values[0])
            target_player.player_id = int(df["player_id"].values[0])
            target_player.player_username = str(df["player_username"].values[0])
            target_player.player_lvl = int(df["player_lvl"].values[0])
            target_player.player_exp = int(df["player_exp"].values[0])
            target_player.player_echelon = int(df["player_echelon"].values[0])
            target_player.player_stamina = int(df["player_stamina"].values[0])
            target_player.player_class = str(df["player_class"].values[0])
            target_player.player_coins = int(df["player_coins"].values[0])
            target_player.player_quest = int(df["player_quest"].values[0])
            target_player.get_equipped()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
        target_player.player_name = player_name
    return target_player


def get_all_users():
    user_list = []
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList")
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        for row in df.iterrows():
            target_player = PlayerProfile()
            target_player.player_id = int(row["player_id"])
            target_player.player_name = str(row["player_name"])
            target_player.player_username = str(row["player_username"])
            target_player.player_lvl = int(row["player_lvl"])
            target_player.player_exp = int(row["player_exp"])
            target_player.player_echelon = int(row["player_echelon"])
            target_player.player_stamina = int(row["player_stamina"])
            target_player.player_class = str(row["player_class"])
            target_player.player_coins = int(row["player_coins"])
            target_player.player_quest = int(df["player_quest"].values[0])
            target_player.get_equipped()
            user_list.append(target_player)
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
    return user_list


def get_max_exp(player_lvl):
    exp_required = int(1000 * player_lvl)
    return exp_required


def checkNaN(test_string):
    try:
        result = math.isnan(float(test_string))
        return result
    except Exception as e:
        return False


def get_thumbnail_by_class(class_name):
    match class_name:
        case "<:cA:1150195102589931641>":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Ranger.png'
        case "<:cB:1154266777396711424>":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Knight.png'
        case "<:cC:1150195246588764201>":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Mage.png'
        case "<:cD:1150195280969478254>":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Summoner.png'
        case _:
            thumbnail_url = "https://kyleportfolio.ca/botimages/Summoner.png"

    return thumbnail_url
