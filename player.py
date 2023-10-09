import pandas as pd
import csv
from csv import DictReader
import inventory
import damagecalc
import math
import loot
import bosses
import damagecalc
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
import pandorabot


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
        self.equipped_tarot = 0
        self.player_coins = 0
        self.player_class = ""
        self.player_quest = 0

        self.player_mHP = 1000
        self.player_cHP = self.player_mHP

        self.player_damage = 0.0
        self.player_total_damage = 0.0
        self.elemental_damage = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.elemental_damage_multiplier = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_penetration = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_multiplier = 0.0
        self.all_elemental_penetration = 0.0
        self.defence_penetration = 0.0
        self.class_multiplier = 0.0
        self.final_damage = 0.0

        self.critical_chance = 0.0
        self.critical_multiplier = 0.0

        self.attack_speed = 0.0
        self.bonus_hits = 0.0

        self.aura = 0.0
        self.elemental_curse = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_curse = 0.0

        self.hp_bonus = 0.0
        self.hp_regen = 0.0
        self.hp_multiplier = 0.0
        self.damage_mitigation = 0.0
        self.mitigation_multiplier = 0.0
        self.elemental_resistance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_resistance = 0.0

    def __str__(self):
        return str(self.player_name)

    def reset_multipliers(self):
        self.player_mHP = 1000
        self.player_cHP = self.player_mHP

        self.player_damage = 0.0
        self.player_total_damage = 0.0
        self.elemental_damage = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.elemental_damage_multiplier = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_penetration = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_multiplier = 0.0
        self.all_elemental_penetration = 0.0
        self.defence_penetration = 0.0
        self.class_multiplier = 0.0
        self.final_damage = 0.0

        self.critical_chance = 0.0
        self.critical_multiplier = 0.0

        self.attack_speed = 0.0
        self.bonus_hits = 0.0

        self.aura = 0.0
        self.elemental_curse = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_curse = 0.0

        self.hp_bonus = 0.0
        self.hp_regen = 0.0
        self.hp_multiplier = 0.0
        self.damage_mitigation = 0.0
        self.mitigation_multiplier = 0.0
        self.elemental_resistance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_resistance = 0.0

    def get_player_stats(self, method):
        echelon_colour = inventory.get_gear_tier_colours(self.player_echelon)
        resources = f'<:estamina:1145534039684562994> {self.player_username}\'s stamina: '
        resources += str(self.player_stamina)
        resources += f'\nLotus Coins: {self.player_coins}'
        exp = f'Level: {self.player_lvl} Exp: ({self.player_exp} / '
        exp += f'{get_max_exp(self.player_lvl)})'
        id_msg = f'User ID: {self.player_id}\nClass: {self.player_class}'
        self.get_player_multipliers()
        if method == 1:
            stats = f"Item Base Damage: {int(self.player_damage):,}"
            stats += f"\nAttack Speed: {self.attack_speed} / min"
            stats += f"\nCritical Chance: {int(self.critical_chance)}%"
            stats += f"\nCritical Damage: +{int(self.critical_multiplier * 100)}%"
            for idw, w in enumerate(self.elemental_damage_multiplier):
                stats += f"\n{pandorabot.global_element_list[idw]} Damage: {int(w * 100)}%"
            stats += f"\nOmni Damage: {int(self.all_elemental_multiplier * 100)}%"
            stats += f"\nBonus Hit Count: +{int(self.bonus_hits)}x"
            stats += f"\nClass Multiplier: {int(self.class_multiplier * 100)}%"
            stats += f"\nFinal Damage: {int(self.final_damage * 100)}%"
        elif method == 2:
            stats = f"Player HP: {self.player_mHP:,}"
            for idy, y in enumerate(self.elemental_resistance):
                stats += f"\n{pandorabot.global_element_list[idy]} Resistance: {int(y * 100)}%"
            stats += f"\nOmni Resistance: {int(self.all_elemental_resistance * 100)}%"
            stats += f"\nDamage Mitigation: {self.damage_mitigation}%"
        elif method == 3:
            stats = f"\nDefence Penetration: {int(self.defence_penetration * 100)}%"
            for idx, x in enumerate(self.elemental_penetration):
                stats += f"\n{pandorabot.global_element_list[idx]} Penetration: {int(x * 100)}%"
            stats += f"\nOmni Penetration: {int(self.all_elemental_penetration * 100)}%"
        else:
            stats = f"Omni Aura: {int(self.aura)}%"
            for idz, z in enumerate(self.elemental_curse):
                stats += f"\n{pandorabot.global_element_list[idz]} Curse: {int(z * 100)}%"
            stats += f"\nOmni Curse: {int(self.all_elemental_curse * 100)}%"


        embed_msg = discord.Embed(colour=echelon_colour[0],
                                  title=self.player_username,
                                  description=id_msg)
        embed_msg.add_field(name=exp, value=resources, inline=False)
        embed_msg.add_field(name="Player Stats", value=stats, inline=False)
        thumbnail_url = get_thumbnail_by_class(self.player_class)
        embed_msg.set_thumbnail(url=thumbnail_url)
        return embed_msg

    def set_player_field(self, field_name, field_value):
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            if field_name == "player_exp":
                max_exp = get_max_exp(self.player_lvl)
                while field_value > max_exp and self.player_lvl < 100:
                    field_value -= max_exp
                    self.player_exp = field_value
                    self.player_lvl += 1
                    query = text(f"UPDATE PlayerList SET player_lvl = :input_1 WHERE player_id = :player_check")
                    query = query.bindparams(player_check=int(self.player_id), input_1=self.player_lvl)
                    pandora_db.execute(query)
                    self.check_and_update_tokens(5, 1)
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
        self.player_lvl = 1
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("SELECT * FROM PlayerList WHERE player_name = :player_check")
            query = query.bindparams(player_check=self.player_name)
            df = pd.read_sql(query, pandora_db)

            if len(df.index) != 0:
                response = f"Player {self.player_name} is already registered."
            else:
                query = text("SELECT * FROM PlayerList WHERE player_username = :username_check")
                query = query.bindparams(username_check=self.player_username)
                df = pd.read_sql(query, pandora_db)

                if len(df.index) != 0:
                    response = f"Username {self.player_username} is taken. Please pick a new username."
                else:
                    query = text("INSERT INTO PlayerList "
                                 "(player_name, player_username, player_lvl, player_exp, player_echelon, player_quest, "
                                 "player_stamina, player_class, player_coins, player_equip_weapon, "
                                 "player_equip_armour, player_equip_acc, player_equip_wing, player_equip_crest) "
                                 "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6,"
                                 ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, :input_13, "
                                 ":input_14, :input_15)")
                    query = query.bindparams(input_1=str(self.player_name), input_2=str(self.player_username),
                                             input_3=int(self.player_lvl), input_4=int(self.player_exp),
                                             input_5=int(self.player_echelon), input_6=int(self.player_quest),
                                             input_7=int(self.player_stamina), input_8=str(self.player_class),
                                             input_9=int(self.player_coins), input_10=int(self.equipped_weapon),
                                             input_11=int(self.equipped_armour), input_12=int(self.equipped_acc),
                                             input_13=int(self.equipped_wing), input_14=int(self.equipped_crest),
                                             input_15=int(self.equipped_tarot))
                    pandora_db.execute(query)
                    response = f"Player {self.player_name} has been registered to play. Welcome {self.player_username}!"
                    response += f"\nPlease use the !quest command to proceed."
                    registered_player = get_player_by_name(self.player_name)
                    query = text("INSERT INTO QuestTokens (player_id, token_1, token_5) "
                                 "VALUES(:player_id, :input_1, :input_5)")
                    query = query.bindparams(player_id=registered_player.player_id, input_1=1, input_5=1)
                    pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
            response = "Error!"
        return response

    def check_and_update_tokens(self, quest_num, change):
        current_tokens = self.check_tokens(quest_num)
        new_tokens = current_tokens + change
        self.update_tokens(quest_num, new_tokens)

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
            self.equipped_tarot = int(df['player_equip_tarot'].values[0])
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))

    def get_player_multipliers(self):
        self.reset_multipliers()
        self.get_equipped()
        base_critical_chance = 10.0
        base_attack_speed = 1.0
        base_damage_mitigation = 0.0
        base_player_hp = 1000

        if self.equipped_weapon != 0:
            e_weapon = inventory.read_custom_item(self.equipped_weapon)
            e_weapon.update_damage()
            self.player_damage += random.randint(e_weapon.item_damage_min, e_weapon.item_damage_max)
            base_attack_speed = float(e_weapon.item_bonus_stat)
            self.assign_roll_values(e_weapon)
            self.assign_gem_values(e_weapon)
        if self.equipped_armour != 0:
            e_armour = inventory.read_custom_item(self.equipped_armour)
            e_armour.update_damage()
            self.player_damage += random.randint(e_armour.item_damage_min, e_armour.item_damage_max)
            self.assign_roll_values(e_armour)
            base_damage_mitigation = float(e_armour.item_bonus_stat)
            self.assign_gem_values(e_armour)
        if self.equipped_acc != 0:
            e_acc = inventory.read_custom_item(self.equipped_acc)
            e_acc.update_damage()
            self.player_damage += random.randint(e_acc.item_damage_min, e_acc.item_damage_max)
            self.assign_roll_values(e_acc)
            self.assign_gem_values(e_acc)
            self.unique_ability_multipliers(e_acc.item_bonus_stat)
        if self.equipped_wing != 0:
            e_wing = inventory.read_custom_item(self.equipped_wing)
            e_wing.update_damage()
            self.player_damage += random.randint(e_wing.item_damage_min, e_wing.item_damage_max)
            self.assign_roll_values(e_wing)
            self.assign_gem_values(e_wing)
            self.unique_ability_multipliers(e_wing.item_bonus_stat)
        if self.equipped_crest != 0:
            e_crest = inventory.read_custom_item(self.equipped_crest)
            e_crest.update_damage()
            self.player_damage += random.randint(e_crest.item_damage_min, e_crest.item_damage_max)
            self.assign_roll_values(e_crest)
            self.assign_gem_values(e_crest)
            self.unique_ability_multipliers(e_crest.item_bonus_stat)

        self.critical_chance = (1 + self.critical_chance) * base_critical_chance
        self.attack_speed = (1 + self.attack_speed) * base_attack_speed
        self.damage_mitigation = (1 + (self.mitigation_multiplier + self.damage_mitigation)) * base_damage_mitigation
        self.player_mHP = int((base_player_hp + self.hp_bonus) * (1 + self.hp_multiplier))

        match_count = 0
        if self.equipped_weapon != 0:
            if e_weapon.item_damage_type == self.player_class:
                match_count += 1
        if self.equipped_armour != 0:
            if e_armour.item_damage_type == self.player_class:
                match_count += 1
        if self.equipped_acc != 0:
            if e_acc.item_damage_type == self.player_class:
                match_count += 1
        if self.equipped_wing != 0:
            if e_wing.item_damage_type == self.player_class:
                match_count += 1
        if self.equipped_crest != 0:
            if e_crest.item_damage_type == self.player_class:
                match_count += 1
        self.class_multiplier += 0.05
        self.class_multiplier *= match_count

    def get_player_damage(self, boss_object):
        additional_multiplier = 1.0
        self.get_player_multipliers()
        e_weapon = inventory.read_custom_item(self.equipped_weapon)
        # Critical hits
        random_num = random.randint(1, 100)
        if random_num < self.critical_chance:
            self.player_damage *= (1 + self.critical_multiplier)
        # Attack Speed
        self.player_damage *= self.attack_speed
        # Hit Multiplier
        self.player_damage *= (1 + self.bonus_hits)
        # Class Multiplier
        self.player_damage *= (1 + self.class_multiplier)
        # Additional multipliers
        additional_multiplier *= (1 + self.aura)
        additional_multiplier *= (1 + self.all_elemental_curse + sum(self.elemental_curse))
        additional_multiplier *= (1 + self.final_damage)
        self.player_damage *= additional_multiplier
        # Type Defences
        defences_multiplier = (damagecalc.boss_defences("", self, boss_object, -1, e_weapon) + self.defence_penetration)
        self.player_damage *= defences_multiplier
        # Elemental Defences
        for idx, x in enumerate(e_weapon.item_elements):
            if x == 1:
                self.elemental_damage[idx] = self.player_damage * (1 + self.elemental_damage_multiplier[idx])
                self.elemental_damage[idx] *= (1 + self.all_elemental_multiplier)
                location = int(idx)
                resist_multi = damagecalc.boss_defences("Element", self, boss_object, location, e_weapon)
                resist_multi += self.elemental_penetration[idx] + self.all_elemental_penetration
                self.elemental_damage[idx] *= resist_multi
        self.player_total_damage = int(sum(self.elemental_damage))
        return self.player_total_damage

    def assign_roll_values(self, equipped_item):
        for x in equipped_item.item_prefix_values:
            roll_adjust = 5
            roll_tier = int(str(x)[1])
            check_roll = ord(str(x[2]))
            bonus = 0.01 * roll_tier * roll_adjust * (1 + equipped_item.item_tier)
            if check_roll <= 106:
                roll_num = check_roll - 97
                if roll_num == 9:
                    self.all_elemental_multiplier += bonus
                else:
                    self.elemental_damage_multiplier[roll_num] += bonus
            elif check_roll <= 116:
                roll_num = check_roll - 97 - 10
                if roll_num == 9:
                    self.all_elemental_penetration += bonus
                else:
                    self.elemental_penetration[roll_num] += bonus
            else:
                match check_roll:
                    case "u":
                        self.defence_penetration += bonus
                    case "v":
                        self.attack_speed += bonus
                    case "w":
                        self.critical_multiplier += bonus
                    case "x":
                        self.final_damage += bonus
                    case "y":
                        self.multi_hit += bonus
                    case _:
                        self.class_multiplier += bonus
        for y in equipped_item.item_suffix_values:
            roll_adjust = 5
            roll_tier = int(str(y)[1])
            check_roll = ord(str(y[2]))
            bonus = 0.01 * roll_tier * roll_adjust * (1 + equipped_item.item_tier)
            if check_roll <= 106:
                roll_num = check_roll - 97
                if roll_num == 9:
                    self.all_elemental_resistance += bonus
                else:
                    self.elemental_resistance[roll_num] += bonus
            elif check_roll <= 116:
                roll_num = check_roll - 97 - 10
                if roll_num == 9:
                    self.all_elemental_curse += bonus
                else:
                    self.elemental_curse[roll_num] += bonus
            else:
                match check_roll:
                    case "u":
                        self.damage_mitigation += bonus
                    case "v":
                        self.hp_regen += bonus
                    case "w":
                        roll_adjust = 100
                        bonus = roll_tier * roll_adjust * (1 + equipped_item.item_tier)
                        self.hp_bonus += bonus
                    case "x":
                        self.hp_multiplier += bonus
                    case "y":
                        self.critical_chance += bonus
                    case _:
                        self.aura += bonus

    def assign_gem_values(self, e_item):
        gem_id = e_item.item_inlaid_gem_id
        if gem_id != 0:
            e_gem = inventory.read_custom_item(gem_id)
            self.player_damage += (e_gem.item_damage_min + e_gem.item_damage_max) / 2
            self.assign_roll_values(e_gem)

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

    def check_equipped(self, item):
        response = ""
        self.get_equipped()

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

    def unique_ability_multipliers(self, unique_ability):
        damage_multiplier = 0.0
        damage_mitigation = 0.0
        level_bonus = 0.01 * self.player_lvl
        if unique_ability in pandorabot.global_unique_ability_list[3]:
            match unique_ability:
                case "Curse of Immortality":
                    nothing = True
                case "Elemental Fractal":
                    self.all_elemental_multiplier += 2 * level_bonus
                case "Bahamut's Trinity":
                    self.mitigation_multiplier += level_bonus
                    self.final_damage += level_bonus
                    self.hp_multiplier += level_bonus
                case "Omega Critical":
                    self.critical_multiplier += 2 * level_bonus
                case "Perfect Precision":
                    self.critical_chance += level_bonus
                case "Overflowing Vitality":
                    self.hp_multiplier += 5 * level_bonus
                case "Specialist's Mastery":
                    self.class_multiplier += level_bonus
                case "Shatter Barrier":
                    self.all_elemental_penetration += level_bonus
                case _:
                    damage_multiplier = 0.0
        else:
            keywords = unique_ability.split()
            buff_tier = pandorabot.global_descriptor_list.index(keywords[2])
            buff_type_loc = pandorabot.global_unique_ability_list[buff_tier].index(keywords[0])
            match keywords[1]:
                case "Hero's":
                    self.elemental_damage_multiplier[buff_type_loc] += round(level_bonus / 2, 2)
                    self.elemental_resistance[buff_type_loc] += round(level_bonus / 2, 2)
                case "Guardian's":
                    self.elemental_resistance[buff_type_loc] += level_bonus
                case "Aggressor's":
                    self.elemental_damage_multiplier[buff_type_loc] += level_bonus
                case "Breaker's":
                    self.elemental_penetration[buff_type_loc] += level_bonus
                case _:
                    nothing = True


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
        if len(df.index) != 0:
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
        if len(df.index) != 0:
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
        if len(df.index) != 0:
            for index, row in df.iterrows():
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
        else:
            user_list = None
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
