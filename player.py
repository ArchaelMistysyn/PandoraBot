import pandas as pd
import csv
from csv import DictReader
import inventory
import combat
import math
import loot
import bosses
import combat
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
from datetime import datetime as dt
import quest
import tarot
import globalitems
from unidecode import unidecode

path_names = ["Storms", "Frostfire", "Horizon", "Eclipse", "Stars", "Confluence"]


def normalize_username(unfiltered_username):
    if any(ord(char) > 127 for char in unfiltered_username):
        normalized_username = unidecode(unfiltered_username)
    else:
        normalized_username = unfiltered_username
    return normalized_username


class PlayerProfile:
    def __init__(self):
        self.player_id = 0
        self.player_name = ""
        self.player_username = ""
        self.player_stamina = 0
        self.player_exp = 0
        self.player_lvl = 0
        self.player_echelon = 0
        self.player_stats = [0, 0, 0, 0, 0, 0]
        self.player_glyphs = ""
        self.player_equipped = [0, 0, 0, 0, 0]
        self.equipped_tarot = ""
        self.insignia = ""
        self.player_coins = 0
        self.player_class = ""
        self.player_quest = 0
        self.vouch_points = 0

        self.player_mHP = 1000
        self.player_cHP = self.player_mHP
        self.immortal = False

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

        self.elemental_capacity = 3
        self.elemental_application = 0

        self.combo_multiplier = 0.05
        self.combo_penetration = 0.0
        self.combo_application = 0

        self.bleed_application = 0
        self.bleed_multiplier = 0.0
        self.bleed_penetration = 0.0

        self.glyph_of_eclipse = False
        self.ultimate_multiplier = 0.0
        self.ultimate_penetration = 0.0
        self.ultimate_application = 0

        self.temporal_application = 0

        self.banes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.skill_base_damage_bonus = [0, 0, 0, 0]

        self.critical_chance = 0.0
        self.critical_multiplier = 0.0
        self.critical_penetration = 0.0
        self.critical_application = 0

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
        self.all_elemental_resistance = 0.1

    def __str__(self):
        return str(self.player_name)

    def reset_multipliers(self):
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

        self.elemental_capacity = 3
        self.elemental_application = 0

        self.combo_multiplier = 0.05
        self.combo_penetration = 0.0
        self.combo_application = 0

        self.bleed_application = 0
        self.bleed_multiplier = 0.00
        self.bleed_penetration = 0.0

        self.glyph_of_eclipse = False
        self.ultimate_multiplier = 0.0
        self.ultimate_penetration = 0.0
        self.ultimate_application = 0

        self.temporal_application = 0

        self.banes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.skill_base_damage_bonus = [0, 0, 0, 0]

        self.critical_chance = 0.0
        self.critical_multiplier = 1.0
        self.critical_penetration = 0.0
        self.critical_application = 0

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
        self.all_elemental_resistance = 0.1

    def get_player_stats(self, method):
        echelon_colour = inventory.get_gear_tier_colours(self.player_echelon)
        resources = f'<:estamina:1145534039684562994> {self.player_username}\'s stamina: '
        resources += str(self.player_stamina)
        resources += f'\nLotus Coins: {self.player_coins}'
        exp = f'Level: {self.player_lvl} Exp: ({self.player_exp} / '
        exp += f'{get_max_exp(self.player_lvl)})'
        id_msg = f'User ID: {self.player_id}\nClass: {globalitems.class_icon_dict[self.player_class]}'
        self.get_player_multipliers()
        element_multipliers = []
        spread = []
        second_title = ""
        second_msg = ""
        if method == 1:
            title_msg = "Offensive Stats"
            stats = f"Item Base Damage: {int(round(self.player_damage)):,}"
            stats += f"\nAttack Speed: {round(math.floor(self.attack_speed * 10) / 10, 1)} / min"
            for x in range(9):
                total_multi = (1 + self.elemental_damage_multiplier[x]) * (1 + self.elemental_penetration[x])
                total_multi *= (1 + self.elemental_curse[x]) * (1 + self.aura)
                element_multipliers.append((x, total_multi * 100))
            spread = sorted(element_multipliers, key=lambda k: k[1], reverse=True)
            for y, total_multi in spread:
                temp_icon = globalitems.global_element_list[y]
                stats += f"\n{temp_icon} Total Damage: {int(round(total_multi)):,}%"
            if self.player_equipped[0] != 0:
                second_title = "Damage Spread"
                e_weapon = inventory.read_custom_item(self.player_equipped[0])
                used_elements = []
                used_multipliers = []
                if self.elemental_capacity < 9:
                    temp_element_list = combat.limit_elements(self, e_weapon)
                else:
                    temp_element_list = e_weapon.item_elements.copy()
                for i, is_used in enumerate(temp_element_list):
                    if is_used:
                        used_elements.append(globalitems.global_element_list[i])
                        used_multipliers.append(element_multipliers[i][1] / 100)
                used_elements, used_multipliers = zip(*sorted(zip(used_elements, used_multipliers),
                                                              key=lambda e: e[1], reverse=True))
                if used_multipliers:
                    total_contribution = sum(used_multipliers)
                    for index, (element, multiplier) in enumerate(zip(used_elements, used_multipliers), 1):
                        contribution = round((multiplier / total_contribution) * 100)
                        second_msg += f"{element} {int(contribution)}% "
                        if index % 3 == 0:
                            second_msg += "\n"
        elif method == 2:
            title_msg = "Elemental Breakdown"
            stats = ""
            element_breakdown = []
            for x in range(9):
                total_multi = (1 + self.elemental_damage_multiplier[x]) * (1 + self.elemental_penetration[x])
                total_multi *= (1 + self.elemental_curse[x])
                element_breakdown.append((x, total_multi * 100))
            sorted_element_breakdown = sorted(element_breakdown, key=lambda v: v[1], reverse=True)
            for z, total_multi in sorted_element_breakdown:
                temp_icon = globalitems.global_element_list[z]
                temp_dmg_str = f"(Dmg: {int(round(self.elemental_damage_multiplier[z] * 100)):,}%)"
                temp_pen_str = f"(Pen: {int(round(self.elemental_penetration[z] * 100)):,}%)"
                temp_curse_str = f"(Curse: {int(round(self.elemental_curse[z] * 100)):,}%)"
                stats += f"{temp_icon} {temp_dmg_str} - {temp_pen_str} - {temp_curse_str}\n"
            stats += f"Elemental Details: (Cap: {self.elemental_capacity}) - (App: {self.elemental_application}) - "
            stats += f"(Frc: {self.elemental_application * 5}%)"
            second_title = "Special Breakdown"
            second_msg = f"Critical Chance: (Reg: {int(round(self.critical_chance))}%) - "
            second_msg += f"(Omg: {int(round(self.critical_application * 10))}%)"
            second_msg += f"\nCritical Multiplier: (Dmg: {int(round(self.critical_multiplier * 100))}%) - "
            second_msg += f"(Pen: {int(round(self.critical_penetration * 100))}%) - "
            second_msg += f"(App: {self.critical_application})"
            second_msg += f"\nBleed Multiplier: (Dmg: {int(round(self.bleed_multiplier * 100))}%) - "
            second_msg += f"(Pen: {int(round(self.bleed_penetration * 100))}%) - "
            second_msg += f"(App: {self.bleed_application})"
            second_msg += f"\nCombo Multiplier: (Dmg: {int(round(self.combo_multiplier * 100))}%) - "
            second_msg += f"(Pen: {int(round(self.combo_penetration * 100))}%) - "
            second_msg += f"(App: {self.combo_application})"
            second_msg += f"\nUltimate Multiplier: (Dmg: {int(round(self.ultimate_multiplier * 100))}%) - "
            second_msg += f"(Pen: {int(round(self.ultimate_penetration * 100))}%) - "
            second_msg += f"(App: {self.ultimate_application})"
            second_msg += f"\nTime Multiplier: (Dmg: {(self.temporal_application + 1) * 100}%) - "
            second_msg += f"(LCK: {self.temporal_application * 5}%) - "
            second_msg += f"(App: {self.temporal_application})"
        elif method == 3:
            title_msg = "Defensive Stats"
            stats = f"Player HP: {self.player_mHP:,}"
            for idy, y in enumerate(self.elemental_resistance):
                stats += f"\n{globalitems.global_element_list[idy]} Resistance: {int(y * 100)}%"
            stats += f"\nDamage Mitigation: {int(round(self.damage_mitigation))}%"
        else:
            title_msg = "Multipliers"
            stats = ""
            for idh, h in enumerate(self.banes):
                if idh < 4:
                    stats += f"\n{bosses.boss_list[idh]} Bane: {int(h * 100)}%"
                elif idh == 4:
                    stats += f"\nHuman Bane: {int(h * 100)}%"
            stats += f"\nClass Mastery: {int(round(self.class_multiplier * 100))}%"
            stats += f"\nFinal Damage: {int(round(self.final_damage * 100))}%"
            stats += f"\nDefence Penetration: {int(round(self.defence_penetration * 100))}%"
            stats += f"\nOmni Aura: {int(round(self.aura * 100))}%"
        embed_msg = discord.Embed(colour=echelon_colour[0],
                                  title=self.player_username,
                                  description=id_msg)
        embed_msg.add_field(name=exp, value=resources, inline=False)
        embed_msg.add_field(name=title_msg, value=stats, inline=False)
        if second_title != "":
            embed_msg.add_field(name=second_title, value=second_msg, inline=False)
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
                    self.update_tokens(5, 1)
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
        self.player_stamina = 5000
        player_stats = "0;0;0;0;0;0"
        equipped_gear = "0;0;0;0;0"
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
                                 "player_stamina, player_class, player_coins, player_stats, "
                                 "player_glyphs, player_equipped, player_equip_tarot, player_equip_insignia, "
                                 "vouch_points) "
                                 "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6,"
                                 ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, :input_13, "
                                 ":input_14, :input_15)")
                    query = query.bindparams(input_1=str(self.player_name), input_2=str(self.player_username),
                                             input_3=int(self.player_lvl), input_4=int(self.player_exp),
                                             input_5=int(self.player_echelon), input_6=int(self.player_quest),
                                             input_7=int(self.player_stamina), input_8=str(self.player_class),
                                             input_9=int(self.player_coins), input_10=str(player_stats),
                                             input_11=str(self.player_glyphs), input_12=str(equipped_gear),
                                             input_13=str(self.equipped_tarot), input_14=str(self.insignia),
                                             input_15=int(self.vouch_points))
                    pandora_db.execute(query)
                    response = f"Player {self.player_name} has been registered to play. Welcome {self.player_username}!"
                    response += f"\nPlease use the !quest command to proceed."
                    registered_player = get_player_by_name(self.player_name)
                    query = text("INSERT INTO QuestTokens (player_id, token_1, token_3) "
                                 "VALUES(:player_id, :input_1, :input_2)")
                    query = query.bindparams(player_id=registered_player.player_id, input_1=1, input_2=1)
                    pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
            response = "Error!"
        return response

    def update_tokens(self, quest_num, change):
        current_quest = quest.quest_list[quest_num - 1]
        current_tokens = self.check_tokens(current_quest.token_num)
        new_token_count = current_tokens + change
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            field_name = f"token_{current_quest.token_num}"
            query = text(f"UPDATE QuestTokens SET {field_name} = :field_value WHERE player_id = :player_check")
            query = query.bindparams(field_value=int(new_token_count), player_check=self.player_id)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
            response = "Error!"

    def check_tokens(self, token_num):
        num_tokens = 0
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            token_field = f"token_{token_num}"
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
            temp_equipped = list(df['player_equipped'].values[0].split(';'))
            self.player_equipped = list(map(int, temp_equipped))
            temp_stats = list(df['player_stats'].values[0].split(';'))
            self.player_stats = list(map(int, temp_stats))
            self.player_glyphs = str(df['player_glyphs'].values[0])
            self.equipped_tarot = str(df['player_equip_tarot'].values[0])
            self.insignia = str(df['player_equip_insignia'].values[0])
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))

    def allocate_points(self, selected_path, num_change):
        path_type = selected_path.split(" ")[-1]
        path_location = path_names.index(path_type)
        spent_points = sum(self.player_stats)
        available_points = self.player_lvl - spent_points
        if available_points >= num_change:
            self.player_stats[path_location] += num_change
            condensed_stats = ';'.join(map(str, self.player_stats))
            self.set_player_field("player_stats", condensed_stats)
            response = "Skill point has been allocated!"
        else:
            response = "Not enough remaining skill points to allocate!"
        return response

    def reset_skill_points(self):
        self.player_stats = [0, 0, 0, 0, 0, 0]
        reset_points = "0;0;0;0;0;0"
        self.set_player_field("player_stats", reset_points)

    def create_path_embed(self):
        colour, icon = inventory.get_gear_tier_colours(self.player_echelon)
        points_msg = "Your shiny toys are useless if you don't know how to use them."
        embed = discord.Embed(color=colour, title="Lyra, Head Instructor", description=points_msg)
        embed.add_field(name=f"{self.player_username}'s Skill Points", value="", inline=False)
        for path_label, points in zip(path_names, self.player_stats):
            embed.add_field(name=f"Path of {path_label}", value=f"Points: {points}", inline=True)
        spent_points = sum(self.player_stats)
        remaining_points = self.player_lvl - spent_points
        embed.add_field(name=f"Unspent Points: {remaining_points}", value="", inline=False)
        return embed

    def build_points_embed(self, selected_path):
        colour, icon = inventory.get_gear_tier_colours(self.player_echelon)
        embed = discord.Embed(color=colour, title=f"{selected_path}", description="")
        perks = {
            "Storms": ["Water Damage: 5%", "Lightning Damage: 5%", "Water Resistance: 1%", "Lightning Resistance: 1%",
                       "Critical Damage: 3%"],
            "Frostfire": ["Ice Damage: 5%", "Fire Damage: 5%", "Ice Resistance: 1%", "Fire Resistance: 1%",
                          "Class Mastery: 1%"],
            "Horizon": ["Earth Damage: 5%", "Wind Damage: 5%", "Earth Resistance: 1%", "Wind Resistance: 1%",
                        "Bleed Damage: 10%"],
            "Eclipse": ["Dark Damage: 5%", "Light Damage: 5%", "Dark Resistance: 1%", "Light Resistance: 1%",
                        "Ultimate Damage: 10%"],
            "Stars": ["Celestial Damage: 7%", "Celestial Resistance: 1%", "Combo Damage: 3%"],
            "Time": ["???%"],
            "Confluence": ["Omni Aura 1%"]
        }
        glyph_data = {
            "Storms": ["Cyclone", "Critical Application +1", 20,
                       "Vortex", "Critical Application +1", 40,
                       "Tempest", "Critical Application +1", 60,
                       "Maelstrom", "Critical Application +2", 80],
            "Frostfire": ["Iceburn", "Grants Cascade Damage", 20,
                          "Glacial Flame", "Grants Cascade Penetration", 40,
                          "Snowy Blaze", "Grants Cascade Curse", 60,
                          "Subzero Inferno", "Triple your fire/ice damage, penetration, and curse", 80],
            "Horizon": ["Red Skies", "Bleed Application +1", 20,
                        "Vermilion Dawn", "Bleed Application +1", 40,
                        "Scarlet Sunset", "Bleed Application +1", 60,
                        "Ruby Tears", "Bleed Application +2", 80],
            "Eclipse": ["Umbra", "Ultimate Application +1", 20,
                        "Shadowfall", "Ultimate Application +1", 40,
                        "Eventide", "Ultimate Application +1", 60,
                        "Twilight", "Basic Skills are affected by Ultimate Damage and Penetration multipliers", 80],
            "Stars": ["Nebulas", "Basic Attack 1 Base Damage +50%", 20,
                      "Galaxies", "Basic Attack 2 Base Damage +75%", 40,
                      "Superclusters", "Basic Attack 3 Base Damage +100%", 60,
                      "Universes", "Basic Attack 3 Base Damage +150%", 80],
            "Confluence": ["Unity", "Elemental Overflow +2", 20,
                           "Harmony", "Elemental Overflow +2", 40,
                           "Synergy", "Elemental Overflow +2", 60,
                           "Equilibrium", "Elemental Overflow +3", 80],
            "Time": ["a", "Temporal Application +1", 20,
                     "b", "Temporal Application +1", 40,
                     "c", "Temporal Application +1", 60,
                     "d", "Temporal Application +2", 80]
        }
        path_type = selected_path.split(" ")[-1]
        embed.description = "Stats per point:\n" + '\n'.join(perks[path_type])
        points_field = self.player_stats[path_names.index(path_type)]
        embed.add_field(name="", value=f"{self.player_username}'s {selected_path} Points: {points_field}", inline=False)
        glyph_data_list = glyph_data.get(path_type, [])
        for name, details, value in zip(glyph_data_list[::3], glyph_data_list[1::3], glyph_data_list[2::3]):
            embed.add_field(name=f"Glyph of {name} - {value} Points", value=f"{details}", inline=False)
        spent_points = sum(self.player_stats)
        remaining_points = self.player_lvl - spent_points
        embed.add_field(name="", value=f"Remaining Points: {remaining_points}", inline=False)
        return embed

    def get_player_multipliers(self):
        self.reset_multipliers()
        self.get_equipped()
        base_critical_chance = 10.0
        base_attack_speed = 1.0
        base_damage_mitigation = 0.0
        base_player_hp = 1000
        base_player_hp += 10 * self.player_lvl

        # Class Multipliers
        match self.player_class:
            case "Ranger":
                self.critical_application += 1
            case "Weaver":
                self.elemental_application += 2
            case "Assassin":
                self.bleed_application += 1
            case "Mage":
                self.temporal_application += 1
            case "Summoner":
                self.combo_application += 1
            case "Knight":
                self.ultimate_application += 1
            case _:
                pass

        # Path Multipliers
        storm_bonus = self.player_stats[0]
        self.elemental_damage_multiplier[1] += 0.05 * storm_bonus
        self.elemental_damage_multiplier[2] += 0.05 * storm_bonus
        self.elemental_resistance[1] += 0.01 * storm_bonus
        self.elemental_resistance[2] += 0.01 * storm_bonus
        self.critical_multiplier += 0.03 * storm_bonus
        if storm_bonus >= 20:
            self.critical_application += 1
            if storm_bonus >= 40:
                self.critical_application += 1
                if storm_bonus >= 60:
                    self.critical_application += 1
                    if storm_bonus >= 80:
                        self.critical_application += 2
        frostfire_bonus = self.player_stats[1]
        self.elemental_damage_multiplier[5] += 0.05 * frostfire_bonus
        self.elemental_damage_multiplier[0] += 0.05 * frostfire_bonus
        self.elemental_resistance[5] += 0.01 * frostfire_bonus
        self.elemental_resistance[0] += 0.01 * frostfire_bonus
        self.class_multiplier += 0.01 * frostfire_bonus
        horizon_bonus = self.player_stats[2]
        self.elemental_damage_multiplier[3] += 0.05 * horizon_bonus
        self.elemental_damage_multiplier[4] += 0.05 * horizon_bonus
        self.elemental_resistance[3] += 0.01 * horizon_bonus
        self.elemental_resistance[4] += 0.01 * horizon_bonus
        self.bleed_multiplier += 0.1 * horizon_bonus
        if horizon_bonus >= 20:
            self.bleed_application += 1
            if horizon_bonus >= 40:
                self.bleed_application += 1
                if horizon_bonus >= 60:
                    self.bleed_application += 1
                    if horizon_bonus >= 80:
                        self.bleed_application += 2
        eclipse_bonus = self.player_stats[3]
        self.elemental_damage_multiplier[6] += 0.05 * eclipse_bonus
        self.elemental_damage_multiplier[7] += 0.05 * eclipse_bonus
        self.elemental_resistance[6] += 0.01 * eclipse_bonus
        self.elemental_resistance[7] += 0.01 * eclipse_bonus
        self.ultimate_multiplier += 0.1 * eclipse_bonus
        if eclipse_bonus >= 20:
            self.ultimate_application += 1
            if eclipse_bonus >= 40:
                self.ultimate_application += 1
                if eclipse_bonus >= 60:
                    self.ultimate_application += 1
                    if eclipse_bonus >= 80:
                        self.glyph_of_eclipse = True
        star_bonus = self.player_stats[4]
        self.elemental_damage_multiplier[8] += 0.07 * star_bonus
        self.elemental_resistance[8] += 0.01 * star_bonus
        self.combo_multiplier += 0.03 * star_bonus
        if star_bonus >= 20:
            self.skill_base_damage_bonus[0] += 0.5
            if star_bonus >= 40:
                self.skill_base_damage_bonus[1] += 0.75
                if star_bonus >= 60:
                    self.skill_base_damage_bonus[2] += 1
                    if star_bonus >= 80:
                        self.skill_base_damage_bonus[2] += 1.5
        confluence_bonus = self.player_stats[5]
        self.aura += 0.01 * confluence_bonus
        if confluence_bonus >= 20:
            self.elemental_application += 2
            if confluence_bonus >= 40:
                self.elemental_application += 2
                if confluence_bonus >= 60:
                    self.elemental_application += 2
                    if confluence_bonus >= 80:
                        self.elemental_application += 3

        # Item Multipliers
        e_item = []
        for idx, x in enumerate(self.player_equipped):
            if x != 0:
                e_item.append(inventory.read_custom_item(x))
                e_item[idx].update_damage()
                self.player_damage += random.randint(e_item[idx].item_damage_min, e_item[idx].item_damage_max)
                self.assign_roll_values(e_item[idx])
                if e_item[idx].item_num_sockets == 1:
                    self.assign_gem_values(e_item[idx])
            else:
                e_item.append(None)
        if e_item[0]:
            base_attack_speed *= float(e_item[0].item_bonus_stat)
            if self.player_class == "Rider":
                base_attack_speed *= 1.25
        if e_item[1]:
            base_damage_mitigation = float(e_item[1].item_bonus_stat)
        for y in range(2, 5):
            if e_item[y]:
                self.unique_ability_multipliers(e_item[y])
        if self.equipped_tarot != "":
            tarot_info = self.equipped_tarot.split(";")
            e_tarot = tarot.check_tarot(self.player_id, tarot.tarot_card_list(int(tarot_info[0])), int(tarot_info[1]))
            base_damage = e_tarot.get_base_damage()
            self.player_damage += base_damage
            self.assign_tarot_values(e_tarot)
        if self.insignia != "":
            self.assign_insignia_values(self.insignia)

        # Application Calculations
        base_critical_chance += self.critical_application * 5
        self.critical_multiplier += self.critical_application * 1.5
        self.skill_base_damage_bonus[3] += self.ultimate_application * 0.25
        self.all_elemental_multiplier += self.elemental_application * 0.25

        # General Calculations
        self.critical_chance = (1 + self.critical_chance) * base_critical_chance
        self.attack_speed = (1 + self.attack_speed) * base_attack_speed
        self.damage_mitigation = (1 + (self.mitigation_multiplier + self.damage_mitigation)) * base_damage_mitigation
        if self.damage_mitigation >= 90:
            self.damage_mitigation = 90
        self.player_mHP = int((base_player_hp + self.hp_bonus) * (1 + self.hp_multiplier))
        self.player_cHP = self.player_mHP

        match_count = 0
        for x in e_item:
            if x:
                if x.item_damage_type == globalitems.class_icon_dict[self.player_class]:
                    match_count += 1
        self.class_multiplier += 0.05
        self.class_multiplier *= match_count

        # Elemental Calculations
        def check_cascade(input_list):
            temp_list = input_list.copy()
            temp_list[0] = 0
            temp_list[5] = 0
            highest_index = temp_list.index(max(temp_list))
            return highest_index
        if frostfire_bonus >= 80:
            self.elemental_damage_multiplier[0] *= 3
            self.elemental_damage_multiplier[5] *= 3
            self.elemental_penetration[0] *= 3
            self.elemental_penetration[5] *= 3
            self.elemental_curse[0] *= 3
            self.elemental_curse[5] *= 3
        if frostfire_bonus >= 20:
            location = check_cascade(self.elemental_damage_multiplier)
            self.elemental_damage_multiplier[location] += self.elemental_damage_multiplier[0]
            self.elemental_damage_multiplier[location] += self.elemental_damage_multiplier[5]
        if frostfire_bonus >= 40:
            location = check_cascade(self.elemental_penetration)
            self.elemental_penetration[location] += self.elemental_penetration[0]
            self.elemental_penetration[location] += self.elemental_penetration[5]
        if frostfire_bonus >= 60:
            location = check_cascade(self.elemental_curse)
            self.elemental_curse[location] += self.elemental_curse[0]
            self.elemental_curse[location] += self.elemental_curse[5]
        if self.elemental_application > 0:
            self.elemental_capacity += self.elemental_application
            if self.elemental_capacity > 9:
                self.elemental_capacity = 9
        elemental_breakdown = []
        for x in range(9):
            self.elemental_damage_multiplier[x] += self.all_elemental_multiplier
            self.elemental_penetration[x] += self.all_elemental_penetration
            self.elemental_resistance[x] += self.all_elemental_resistance
            self.elemental_curse[x] += self.all_elemental_curse
            if self.elemental_resistance[x] >= 0.9:
                self.elemental_resistance[x] = 0.9
        for y in range(5):
            self.banes[y] += self.banes[5]

    def get_player_initial_damage(self):
        initial_damage = self.player_damage
        additional_multiplier = 1.0
        # Class Multiplier
        initial_damage *= (1 + self.class_multiplier)
        # Additional multipliers
        additional_multiplier *= (1 + self.final_damage)
        initial_damage *= additional_multiplier
        return initial_damage

    def get_player_boss_damage(self, boss_object):
        e_weapon = inventory.read_custom_item(self.player_equipped[0])
        num_elements = sum(e_weapon.item_elements)
        player_damage = self.get_player_initial_damage()
        player_damage, critical_type = combat.critical_check(self, player_damage, num_elements)
        self.player_total_damage = self.boss_adjustments(player_damage, boss_object, e_weapon)
        return self.player_total_damage, critical_type

    def boss_adjustments(self, player_damage, boss_object, e_weapon):
        # Boss type multipliers
        boss_type = boss_object.boss_type_num - 1
        adjusted_damage = player_damage * (1 + self.banes[boss_type])
        # Type Defences
        defences_multiplier = (combat.boss_defences("", self, boss_object, -1) + self.defence_penetration)
        adjusted_damage *= defences_multiplier
        # Elemental Defences
        if self.elemental_capacity < 9:
            temp_element_list = combat.limit_elements(self, e_weapon)
        else:
            temp_element_list = e_weapon.item_elements.copy()
        for idx, x in enumerate(temp_element_list):
            if x == 1:
                self.elemental_damage[idx] = adjusted_damage * (1 + self.elemental_damage_multiplier[idx])
                resist_multi = combat.boss_defences("Element", self, boss_object, idx)
                penetration_multi = 1 + self.elemental_penetration[idx]
                self.elemental_damage[idx] *= resist_multi * penetration_multi
        subtotal_damage = sum(self.elemental_damage) * (1 + boss_object.aura)
        subtotal_damage *= combat.boss_true_mitigation(boss_object)
        adjusted_damage = int(subtotal_damage)
        return adjusted_damage

    def get_bleed_damage(self, boss_object):
        e_weapon = inventory.read_custom_item(self.player_equipped[0])
        player_damage = self.get_player_initial_damage()
        self.player_total_damage = self.boss_adjustments(player_damage, boss_object, e_weapon)
        self.player_total_damage *= (1 + self.bleed_multiplier)
        return self.player_total_damage

    def assign_insignia_values(self, insignia_code):
        temp_elements = insignia_code.split(";")
        element_list = list(map(int, temp_elements))
        num_elements = element_list.count(1)
        self.final_damage += self.player_lvl * 0.01
        self.attack_speed += self.player_echelon * 0.1
        if num_elements != 9:
            selected_elements_list = [ind for ind, x in enumerate(element_list) if x == 1]
            for y in selected_elements_list:
                self.elemental_penetration[y] += (150 / num_elements + 25 * self.player_echelon) * 0.01
        else:
            self.all_elemental_penetration += 0.25 + 0.25 * self.player_echelon
        self.hp_bonus += 500 * self.player_echelon

    def assign_tarot_values(self, tarot_card):
        card_num = tarot.get_number_by_tarot(tarot_card.card_name)
        card_multiplier = tarot_card.num_stars * 0.01
        match card_num:
            case 0:
                if tarot_card.card_variant == 1:
                    self.elemental_resistance[5] += card_multiplier * 15
                else:
                    self.elemental_damage_multiplier[5] += card_multiplier * 25
            case 1:
                if tarot_card.card_variant == 1:
                    self.elemental_resistance[0] += card_multiplier * 10
                    self.elemental_resistance[5] += card_multiplier * 10
                else:
                    self.elemental_damage_multiplier[0] += card_multiplier * 15
                    self.elemental_damage_multiplier[5] += card_multiplier * 15
            case 2:
                if tarot_card.card_variant == 1:
                    self.elemental_penetration[8] += card_multiplier * 25
                else:
                    self.elemental_curse[8] += card_multiplier * 30
            case 3:
                if tarot_card.card_variant == 1:
                    self.defence_penetration += card_multiplier * 25
                else:
                    self.attack_speed += card_multiplier * 10
            case 4:
                if tarot_card.card_variant == 1:
                    self.critical_multiplier += card_multiplier * 30
                else:
                    self.critical_penetration += card_multiplier * 40
            case 5:
                if tarot_card.card_variant == 1:
                    self.elemental_penetration[2] += card_multiplier * 25
                else:
                    self.elemental_curse[2] += card_multiplier * 30
            case 6:
                if tarot_card.card_variant == 1:
                    self.all_elemental_resistance += card_multiplier * 10
                else:
                    self.banes[4] += card_multiplier * 40
            case 7:
                if tarot_card.card_variant == 1:
                    self.ultimate_multiplier += card_multiplier * 25
                else:
                    self.ultimate_penetration += card_multiplier * 30
            case 8:
                if tarot_card.card_variant == 1:
                    self.bleed_multiplier += card_multiplier * 25
                else:
                    self.bleed_penetration += card_multiplier * 30
            case 9:
                if tarot_card.card_variant == 1:
                    self.elemental_resistance[2] += card_multiplier * 15
                else:
                    self.elemental_damage_multiplier[2] += card_multiplier * 25
            case 10:
                if tarot_card.card_variant == 1:
                    self.combo_multiplier += card_multiplier * 25
                else:
                    self.combo_penetration += card_multiplier * 30
            case 11:
                if tarot_card.card_variant == 1:
                    self.elemental_penetration[7] += card_multiplier * 25
                else:
                    self.elemental_curse[7] += card_multiplier * 30
            case 12:
                if tarot_card.card_variant == 1:
                    self.elemental_penetration[6] += card_multiplier * 25
                else:
                    self.elemental_curse[6] += card_multiplier * 30
            case 13:
                if tarot_card.card_variant == 1:
                    self.elemental_penetration[5] += card_multiplier * 25
                else:
                    self.elemental_curse[5] += card_multiplier * 30
            case 14:
                if tarot_card.card_variant == 1:
                    self.elemental_penetration[1] += card_multiplier * 25
                else:
                    self.elemental_curse[1] += card_multiplier * 30
            case 15:
                if tarot_card.card_variant == 1:
                    self.elemental_penetration[0] += card_multiplier * 15
                    self.elemental_penetration[5] += card_multiplier * 15
                else:
                    self.elemental_curse[0] += card_multiplier * 20
                    self.elemental_curse[5] += card_multiplier * 20
            case 16:
                if tarot_card.card_variant == 1:
                    self.damage_mitigation += card_multiplier * 15
                else:
                    self.banes[5] += card_multiplier * 10
            case 17:
                if tarot_card.card_variant == 1:
                    self.elemental_resistance[8] += card_multiplier * 15
                else:
                    self.elemental_damage_multiplier[8] += card_multiplier * 25
            case 18:
                if tarot_card.card_variant == 1:
                    self.elemental_resistance[6] += card_multiplier * 15
                else:
                    self.elemental_damage_multiplier[6] += card_multiplier * 25
            case 19:
                if tarot_card.card_variant == 1:
                    self.elemental_resistance[7] += card_multiplier * 15
                else:
                    self.elemental_damage_multiplier[7] += card_multiplier * 25
            case 20:
                if tarot_card.card_variant == 1:
                    self.elemental_damage_multiplier[4] += card_multiplier * 15
                    self.elemental_damage_multiplier[3] += card_multiplier * 15
                else:
                    self.elemental_penetration[4] += card_multiplier * 20
                    self.elemental_penetration[3] += card_multiplier * 20
            case 21:
                if tarot_card.card_variant == 1:
                    self.elemental_resistance[3] += card_multiplier * 15
                else:
                    self.elemental_damage_multiplier[3] += card_multiplier * 25
            case 22:
                if tarot_card.card_variant == 1:
                    self.all_elemental_curse += card_multiplier * 30
                else:
                    self.aura += card_multiplier * 40

    def assign_roll_values(self, equipped_item):
        for x in equipped_item.item_prefix_values:
            roll_tier = int(str(x)[1])
            check_roll = ord(str(x[2]))
            roll_adjust = 0.01 * (1 + roll_tier)
            if check_roll <= 68:
                if check_roll == 65:
                    bonus = roll_adjust * 25
                    self.critical_penetration += bonus
                elif check_roll == 66:
                    bonus = roll_adjust * 20
                    self.ultimate_penetration += bonus
                elif check_roll == 67:
                    bonus = roll_adjust * 25
                    self.bleed_penetration += bonus
                elif check_roll == 68:
                    bonus = roll_adjust * 20
                    self.combo_penetration += bonus
            elif check_roll <= 106:
                roll_num = check_roll - 97
                if roll_num == 9:
                    bonus = roll_adjust * 15
                    self.all_elemental_multiplier += bonus
                else:
                    bonus = roll_adjust * 25
                    self.elemental_damage_multiplier[roll_num] += bonus
            elif check_roll <= 116:
                roll_num = check_roll - 97 - 10
                if roll_num == 9:
                    bonus = roll_adjust * 10
                    self.all_elemental_penetration += bonus
                else:
                    bonus = roll_adjust * 15
                    self.elemental_penetration[roll_num] += bonus
            else:
                match check_roll:
                    case 117:
                        bonus = roll_adjust * 15
                        self.damage_mitigation += bonus
                    case 118:
                        bonus = roll_adjust * 25
                        self.banes[4] += bonus
                    case 119:
                        bonus = roll_adjust * 1
                        self.hp_regen += bonus
                    case 120:
                        bonus = roll_adjust * 15
                        self.hp_multiplier += bonus
                    case 121:
                        bonus = roll_adjust * 5
                        self.aura += bonus
                    case _:
                        bonus = roll_adjust * 3
                        self.class_multiplier += bonus

        for y in equipped_item.item_suffix_values:
            roll_tier = int(str(y)[1])
            check_roll = ord(str(y[2]))
            roll_adjust = 0.01 * (1 + roll_tier)
            if check_roll <= 68:
                if check_roll == 65:
                    bonus = roll_adjust * 25
                    self.ultimate_multiplier += bonus
                elif check_roll == 66:
                    bonus = roll_adjust * 25
                    self.bleed_multiplier += bonus
                elif check_roll == 67:
                    bonus = roll_adjust * 10
                    self.combo_multiplier += bonus
                elif check_roll == 68:
                    bonus = roll_adjust * 5
                    self.attack_speed += bonus
            elif check_roll <= 106:
                roll_num = check_roll - 97
                if roll_num == 9:
                    bonus = roll_adjust * 5
                    self.all_elemental_resistance += bonus
                else:
                    bonus = roll_adjust * 15
                    self.elemental_resistance[roll_num] += bonus
            elif check_roll <= 116:
                roll_num = check_roll - 97 - 10
                if roll_num == 9:
                    bonus = roll_adjust * 8
                    self.all_elemental_curse += bonus
                else:
                    bonus = roll_adjust * 15
                    self.elemental_curse[roll_num] += bonus
            elif check_roll >= 119:
                roll_num = check_roll - 119
                bonus = roll_adjust * 25
                self.banes[roll_num] += bonus
            else:
                match check_roll:
                    case 117:
                        bonus = roll_adjust * 20
                        self.critical_chance += bonus
                    case 118:
                        bonus = roll_adjust * 25
                        self.critical_multiplier += bonus
                    case _:
                        no_change = True

        for idz, z in enumerate(equipped_item.item_elements):
            if z == 1:
                match equipped_item.item_type:
                    case "A":
                        self.elemental_resistance[idz] += 0.15
                    case "Y":
                        self.elemental_damage[idz] += 0.25
                    case "G":
                        self.elemental_penetration[idz] += 0.15
                    case "C":
                        self.elemental_curse[idz] += 0.1
                    case _:
                        no_change = True

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
            if selected_item.item_type in ["W", "A", "Y", "G", "C"]:
                location = inventory.item_loc_dict[selected_item.item_type]
                item_type = inventory.item_type_dict[location]
            else:
                run_query = False
                response = "Item is not equipable."
            if run_query:
                self.player_equipped[location] = selected_item.item_id
                response = f"{item_type} {selected_item.item_id} is now equipped."
                equipped_gear = ";".join(map(str, self.player_equipped))
                query = text(f"UPDATE PlayerList SET player_equipped = :input_1 WHERE player_id = :player_check")
                query = query.bindparams(player_check=int(self.player_id), input_1=equipped_gear)
                pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))

        return response

    def check_equipped(self, item):
        response = ""
        self.get_equipped()
        if item.item_id in self.player_equipped:
            return f"Item {item.item_id} is equipped."
        elif item.item_type in inventory.item_loc_dict:
            if item.item_type == "D":
                for x in self.player_equipped:
                    if x != 0:
                        e_item = inventory.read_custom_item(x)
                        check = e_item.item_inlaid_gem_id
                        if item.item_id == check:
                            response = f"Dragon Heart Gem {item.item_id} is currently inlaid in item {e_item.item_id}."
            return response
        else:
            return f"Item {item.item_id} is not recognized."

    def create_stamina_embed(self):
        potion_list = ["i1y", "i2y", "i3y", "i4y"]
        potion_msg = ""
        for x in potion_list:
            loot_item = loot.BasicItem(str(x))
            potion_stock = inventory.check_stock(self, loot_item.item_id)
            potion_msg += f"\n{loot_item.item_emoji} {potion_stock}x {loot_item.item_name}"
        stamina_title = f"{self.player_username}\'s Stamina: "
        stamina_title += f"{str(self.player_stamina)} / 5000"
        embed_msg = discord.Embed(colour=discord.Colour.green(), title=stamina_title, description="")
        embed_msg.add_field(name="", value=potion_msg)
        return embed_msg

    def unique_ability_multipliers(self, item):
        unique_ability = item.item_bonus_stat
        item_type = item.item_type
        if item.item_tier >= 5:
            match unique_ability:
                case "Curse of Immortality":
                    self.immortal = globalitems.tier_5_ability_dict[unique_ability]
                case "Elemental Overflow":
                    self.elemental_application += globalitems.tier_5_ability_dict[unique_ability]
                case "Omega Critical":
                    self.critical_application += globalitems.tier_5_ability_dict[unique_ability]
                case "Specialist's Mastery":
                    self.class_multiplier += globalitems.tier_5_ability_dict[unique_ability]
                case "Endless Combo":
                    self.combo_application += globalitems.tier_5_ability_dict[unique_ability]
                case "Ultimate Overdrive":
                    self.ultimate_application += globalitems.tier_5_ability_dict[unique_ability]
                case "Crimson Reaper":
                    self.bleed_application += globalitems.tier_5_ability_dict[unique_ability]
                case "Overflowing Vitality":
                    self.hp_multiplier += globalitems.tier_5_ability_dict[unique_ability]
                case "Unravel":
                    self.temporal_application += globalitems.tier_5_ability_dict[unique_ability]
                case _:
                    nothing = False
        else:
            keywords = unique_ability.split()
            match item_type:
                case "Y":
                    if keywords[0] in bosses.boss_list:
                        buff_type_loc = bosses.boss_list.index(keywords[0])
                        self.banes[buff_type_loc] += 0.5
                    elif keywords[0] == "Human":
                        self.banes[4] += 0.5
                case "G":
                    buff_type_loc = globalitems.element_special_names.index(keywords[0])
                    self.elemental_damage_multiplier[buff_type_loc] += 0.25
                case "C":
                    buff_type_loc = globalitems.element_special_names.index(keywords[0])
                    self.elemental_penetration[buff_type_loc] += 0.25
                case _:
                    nothing = False

    def check_cooldown(self, command_name):
        difference = None
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("SELECT * FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check")
            query = query.bindparams(player_check=self.player_id, cmd_check=command_name)
            df = pd.read_sql(query, pandora_db)
            if len(df) != 0:
                date_string = str(df["time_used"].values[0])
                previous = dt.strptime(date_string, globalitems.date_formatting)
                now = dt.now()
                difference = now - previous
                method = str(df["method"].values[0])
            else:
                method = ""
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
            difference = 0
            method = ""
        return difference, method

    def set_cooldown(self, command_name, method):
        difference = None
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("SELECT * FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check")
            query = query.bindparams(player_check=self.player_id, cmd_check=command_name)
            df = pd.read_sql(query, pandora_db)
            if len(df) != 0:
                query = text("UPDATE CommandCooldowns SET command_name = :cmd_check, time_used =:time_check "
                             "WHERE player_id = :player_check AND method = :method")
            else:
                query = text("INSERT INTO CommandCooldowns (player_id, command_name, method, time_used) "
                             "VALUES (:player_check, :cmd_check, :method, :time_check)")
            timestamp = dt.now()
            current_time = timestamp.strftime(globalitems.date_formatting)
            query = query.bindparams(player_check=self.player_id, cmd_check=command_name,
                                     method=method, time_check=current_time)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))
        return difference

    def clear_cooldown(self, command_name):
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("DELETE FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check")
            query = query.bindparams(player_check=self.player_id, cmd_check=command_name)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except mysql.connector.Error as err:
            print("Database Error: {}".format(err))


def reset_all_cooldowns():
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("DELETE FROM CommandCooldowns")
        pandora_db.execute(query)
        pandora_db.close()
        engine.dispose()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))


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
    if len(df) != 0:
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
            target_player.vouch_points = int(df["vouch_points"].values[0])
            target_player.get_equipped()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
        target_player.player_name = player_name
    return target_player


def get_player_by_name(player_name) -> PlayerProfile:
    target_player = PlayerProfile()
    normalized_player_name = normalize_username(str(player_name))
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList WHERE player_name = :player_check")
        query = query.bindparams(player_check=normalized_player_name)
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
            target_player.vouch_points = int(df["vouch_points"].values[0])
            target_player.get_equipped()
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
        target_player.player_name = normalized_player_name
    return target_player


def get_players_by_echelon(player_echelon):
    user_list = []
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList WHERE player_echelon = :echelon_check")
        query = query.bindparams(echelon_check=player_echelon)
        player_df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(player_df.index) != 0:
            for index, row in player_df.iterrows():
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
                target_player.player_quest = int(row["player_quest"])
                target_player.vouch_points = int(row["vouch_points"])
                user_list.append(target_player)
        else:
            user_list = None
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
    return user_list


def check_user_exists(user_id):
    user_exists = False
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList WHERE player_id = :player_check")
        query = query.bindparams(player_check=user_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            user_exists = True
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
    return user_exists


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
                target_player.player_quest = int(row["player_quest"])
                target_player.vouch_points = int(row["vouch_points"])
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
    thumbnail_url = f"https://kyleportfolio.ca/botimages/classicon/{class_name}.png"
    return thumbnail_url
