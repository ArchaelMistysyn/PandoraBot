import pandas as pd
import csv
from csv import DictReader

import insignia
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
import itemrolls
import skillpaths
import globalitems


class PlayerProfile:
    def __init__(self):

        # Initialize player base info.
        self.player_id, self.discord_id, self.player_username = 0, 0, ""
        self.player_exp, self.player_lvl, self.player_echelon = 0, 0, 0
        self.player_class = ""
        self.player_quest = 0
        self.player_coins, self.player_stamina, self.vouch_points = 0, 0, 0

        # Initialize player gear/stats info.
        self.player_stats, self.gear_points = [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]
        self.player_glyphs = ""
        self.player_equipped = [0, 0, 0, 0, 0]
        self.equipped_tarot, self.insignia = "", ""

        # Initialize player health stats.
        self.player_mHP = 1000
        self.player_cHP = self.player_mHP
        self.immortal = False

        # Initialize player damage values.
        self.player_damage, self.player_total_damage = 0.0, 0.0

        # Initialize elemental stats.
        self.elemental_damage = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.elemental_multiplier = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_penetration = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_curse = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_conversion = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.all_elemental_multiplier, self.all_elemental_penetration, self.all_elemental_curse = 0.0, 0.0, 0.0
        self.aura = 0.0

        # Initialize class specialization stats.
        self.unique_glyph_ability = [False, False, False, False, False, False, False]
        self.temporal_application = 0
        self.elemental_capacity, self.elemental_application = 3, 0
        self.bleed_multiplier, self.bleed_penetration, self.bleed_application = 0.0, 0.0, 0
        self.combo_multiplier, self.combo_penetration, self.combo_application = 0.05, 0.0, 0
        self.ultimate_multiplier, self.ultimate_penetration, self.ultimate_application = 0.0, 0.0, 0
        self.critical_chance, self.critical_multiplier = 0.0, 1.0
        self.critical_penetration, self.critical_application = 0.0, 0

        # Initialize misc stats.
        self.banes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.skill_base_damage_bonus = [0, 0, 0, 0]
        self.specialty_rate = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.bloom_multiplier = 10.0
        self.unique_conversion = [0.0, 0.0]
        self.attack_speed = 0.0
        self.bonus_hits = 0.0
        self.defence_penetration = 0.0
        self.class_multiplier = 0.0
        self.final_damage = 0.0

        # Initialize defensive stats.
        self.hp_bonus, self.hp_regen, self.hp_multiplier = 0.0, 0.0, 0.0
        self.damage_mitigation = 0.0
        self.mitigation_multiplier = 0.0
        self.elemental_resistance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_resistance = 0.1

    def reset_multipliers(self):
        self.player_damage, self.player_total_damage = 0.0, 0.0
        self.gear_points = [0, 0, 0, 0, 0, 0, 0]

        # Initialize elemental stats.
        self.elemental_damage = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.elemental_multiplier = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_penetration = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_curse = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.elemental_conversion = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.all_elemental_multiplier, self.all_elemental_penetration, self.all_elemental_curse = 0.0, 0.0, 0.0
        self.aura = 0.0

        # Initialize class specialization stats.
        self.unique_glyph_ability = [False, False, False, False, False, False, False]
        self.temporal_application = 0
        self.elemental_capacity, self.elemental_application = 3, 0
        self.bleed_multiplier, self.bleed_penetration, self.bleed_application = 0.0, 0.0, 0
        self.combo_multiplier, self.combo_penetration, self.combo_application = 0.05, 0.0, 0
        self.ultimate_multiplier, self.ultimate_penetration, self.ultimate_application = 0.0, 0.0, 0
        self.critical_chance, self.critical_multiplier = 0.0, 1.0
        self.critical_penetration, self.critical_application = 0.0, 0

        # Initialize misc stats.
        self.banes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.skill_base_damage_bonus = [0, 0, 0, 0]
        self.specialty_rate = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.bloom_multiplier = 10.0
        self.unique_conversion = [0.0, 0.0]
        self.attack_speed = 0.0
        self.bonus_hits = 0.0
        self.defence_penetration = 0.0
        self.class_multiplier = 0.0
        self.final_damage = 0.0

        # Initialize defensive stats.
        self.hp_bonus, self.hp_regen, self.hp_multiplier = 0.0, 0.0, 0.0
        self.damage_mitigation = 0.0
        self.mitigation_multiplier = 0.0
        self.elemental_resistance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_resistance = 0.1

    def get_player_stats(self, method):
        # Construct the base embed.
        echelon_colour = inventory.get_gear_tier_colours(self.player_echelon)
        resources = f'<:estamina:1145534039684562994> {self.player_username}\'s stamina: {self.player_stamina:,}'
        resources += f'\nLotus Coins: {self.player_coins:,}'
        exp = f'Level: {self.player_lvl} Exp: ({self.player_exp:,} / {get_max_exp(self.player_lvl):,}'
        id_msg = f'User ID: {self.player_id}\nClass: {globalitems.class_icon_dict[self.player_class]}'
        embed_msg = discord.Embed(colour=echelon_colour[0], title=self.player_username, description=id_msg)
        embed_msg.add_field(name=exp, value=resources, inline=False)
        embed_msg.set_thumbnail(url=f"{get_thumbnail_by_class(self.player_class)}")

        # Initialize the values.
        self.get_player_multipliers()
        title_msg, stats = "", ""
        temp_embed = None

        if method in [1, 2]:
            # Offensive Stat Display.
            title_msg = "Offensive Stats"
            stats = f"Item Base Damage: {int(round(self.player_damage)):,}"
            stats += f"\nAttack Speed: {round(math.floor(self.attack_speed * 10) / 10, 1)} / min"

            # Calculate the damage spread.
            element_breakdown = []
            for x in range(9):
                total_multi = (1 + self.elemental_multiplier[x]) * (1 + self.elemental_penetration[x])
                total_multi *= (1 + self.elemental_curse[x]) * self.elemental_conversion[x]
                element_breakdown.append((x, total_multi * 100))
            sorted_element_breakdown = sorted(element_breakdown, key=lambda v: v[1], reverse=True)
            for z, total_multi in sorted_element_breakdown:
                temp_icon = globalitems.global_element_list[z]
                temp_dmg_str = f"(Dmg: {int(round(self.elemental_multiplier[z] * 100)):,}%)"
                temp_pen_str = f"(Pen: {int(round(self.elemental_penetration[z] * 100)):,}%)"
                temp_curse_str = f"(Curse: {int(round(self.elemental_curse[z] * 100)):,}%)"
                if method == 1:
                    stats += f"\n{temp_icon} Total Damage: {int(round(total_multi)):,}%"
                if method == 2:
                    stats += f"{temp_icon} {temp_dmg_str} - {temp_pen_str} - {temp_curse_str}\n"
            embed_msg.add_field(name=title_msg, value=stats, inline=False)

            if method == 1:
                # Construct the damage spread field.
                if self.player_equipped[0] != 0:
                    title_msg, stats = "Damage Spread", ""
                    e_weapon = inventory.read_custom_item(self.player_equipped[0])
                    used_elements, used_multipliers = [], []
                    temp_element_list = combat.limit_elements(self, e_weapon)
                    # Build the list of used elements/multipliers.
                    for i, is_used in enumerate(temp_element_list):
                        if is_used:
                            used_elements.append(globalitems.global_element_list[i])
                            used_multipliers.append(element_breakdown[i][1] / 100)
                    used_elements, used_multipliers = zip(*sorted(zip(used_elements, used_multipliers),
                                                                  key=lambda e: e[1], reverse=True))
                    # Build the breakdown message.
                    if used_multipliers:
                        total_contribution = sum(used_multipliers)
                        for index, (element, multiplier) in enumerate(zip(used_elements, used_multipliers), 1):
                            contribution = round((multiplier / total_contribution) * 100)
                            stats += f"{element} {int(contribution)}% "
                            if index % 3 == 0:
                                stats += "\n"
                        embed_msg.add_field(name=title_msg, value=stats, inline=False)
                return embed_msg
            if method == 2:
                # Stat Breakdown Display.
                def set_section(header, tag_list, value_list):
                    section_string = f"\n{header}: "
                    for tag_index, (tag, value) in enumerate(zip(tag_list, value_list)):
                        section_string += f"({tag}: {value}%)"
                        if (tag_index + 1) < len(tag_list):
                            section_string += " - "
                    return f"{section_string}"
                title_msg = "Elemental Breakdown"
                stats += set_section("Elemental Details", ["Cap", "App", "FRC"],
                                     [self.elemental_capacity, self.elemental_application,
                                     (self.elemental_application * 5 + show_num(self.specialty_rate[3]))])
                stats = set_section("Critical Details", ["CRT", "Dmg", "Pen", "App", "OMG"],
                                     [show_num(self.critical_chance, 0), show_num(self.critical_multiplier),
                                      show_num(self.critical_penetration),
                                      (self.critical_application * 10 + show_num(self.specialty_rate[2]))])
                stats += set_section("Combo Details", ["Dmg", "Pen", "App"],
                                     [show_num(self.combo_multiplier), show_num(self.combo_penetration),
                                      self.combo_application])
                stats += set_section("Ultimate Details", ["Dmg", "Pen", "App"],
                                     [show_num(self.ultimate_multiplier), show_num(self.ultimate_penetration),
                                      self.ultimate_application])
                stats += set_section("Bleed Details", ["Dmg", "Pen", "App", "HPR"],
                                     [show_num(self.bleed_multiplier), show_num(self.bleed_penetration),
                                      self.bleed_application,
                                     (self.bleed_application * 10 + show_num(self.specialty_rate[1]))])
                stats += set_section("Time Details", ["Dmg", "App", "LCK"],
                                     [((self.temporal_application + 1) * 100), self.temporal_application,
                                      (self.temporal_application * 5 + show_num(self.specialty_rate[4]))])
                stats += set_section("Bloom Details", ["BLM", "Dmg"],
                                     [show_num(self.specialty_rate[0]), show_num(self.bloom_multiplier)])
                embed_msg.add_field(name=title_msg, value=stats, inline=False)
                return embed_msg
        if method == 3:
            # Defensive display.
            title_msg = "Defensive Stats"
            stats = f"Player HP: {self.player_mHP:,}"
            for idy, y in enumerate(self.elemental_resistance):
                stats += f"\n{globalitems.global_element_list[idy]} Resistance: {show_num(y)}%"
            stats += f"\nDamage Mitigation: {show_num(self.damage_mitigation, 0)}%"
            embed_msg.add_field(name=title_msg, value=stats, inline=False)
            return embed_msg
        if method == 4:
            # Multiplier Display.
            title_msg = "Multipliers"
            for idh, h in enumerate(self.banes):
                stats += f"\n{bosses.boss_list[idh]} Bane: {show_num(h)}%" if idh < 5 else f"\nHuman Bane: {show_num(h)}%"
            stats += f"\nClass Mastery: {show_num(self.class_multiplier)}%"
            stats += f"\nFinal Damage: {show_num(self.final_damage)}%"
            stats += f"\nDefence Penetration: {show_num(self.defence_penetration)}%"
            stats += f"\nOmni Aura: {show_num(self.aura)}%"
            embed_msg.add_field(name=title_msg, value=stats, inline=False)
            return embed_msg
        if method == 5:
            # Points Display.
            temp_embed = self.create_path_embed()
            if temp_embed is not None:
                for field in temp_embed.fields[:-1]:
                    embed_msg.add_field(name=field.name, value=field.value, inline=field.inline)
            embed_msg.add_field(name=title_msg, value=stats, inline=False)
            return embed_msg
        if method == 6:
            # Glyph Display.
            embed_msg.add_field(name=f"{self.player_username}'s Glyphs (Above tier 1)", value="", inline=False)
            for path_index, path_type in enumerate(globalitems.path_names):
                total_points = self.player_stats[path_index] + self.gear_points[path_index]
                if total_points >= 20:
                    embed_msg = skillpaths.display_glyph(path_type, total_points, embed_msg)
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

    def unequip_item(self, item):
        self.player_equipped = [0 if element == item.item_id else element for element in self.player_equipped]
        equipped_gear = ";".join(map(str, self.player_equipped))
        self.set_player_field("player_equipped", equipped_gear)

    def add_new_player(self, selected_class, discord_id):
        self.discord_id = discord_id
        self.player_class = selected_class
        self.player_quest = 1
        self.player_lvl = 1
        self.player_stamina = 5000
        player_stats = "0;0;0;0;0;0;0"
        equipped_gear = "0;0;0;0;0"
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            query = text("SELECT * FROM PlayerList WHERE discord_id = :id_check")
            query = query.bindparams(id_check=self.discord_id)
            df = pd.read_sql(query, pandora_db)

            if len(df.index) != 0:
                response = f"Player with discord ID: ({self.discord_id}) is already registered."
            else:
                query = text("SELECT * FROM PlayerList WHERE player_username = :username_check")
                query = query.bindparams(username_check=self.player_username)
                df = pd.read_sql(query, pandora_db)

                if len(df.index) != 0:
                    response = f"Username {self.player_username} is taken. Please pick a new username."
                else:
                    query = text("INSERT INTO PlayerList "
                                 "(discord_id, player_username, player_lvl, player_exp, player_echelon, "
                                 "player_quest, player_stamina, player_class, player_coins, player_stats, "
                                 "player_glyphs, player_equipped, player_equip_tarot, player_equip_insignia, "
                                 "vouch_points) "
                                 "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6,"
                                 ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, :input_13, "
                                 ":input_14, :input_15)")
                    query = query.bindparams(input_1=str(self.discord_id), input_2=str(self.player_username),
                                             input_3=int(self.player_lvl), input_4=int(self.player_exp),
                                             input_5=int(self.player_echelon), input_6=int(self.player_quest),
                                             input_7=int(self.player_stamina), input_8=str(self.player_class),
                                             input_9=int(self.player_coins), input_10=str(player_stats),
                                             input_11=str(self.player_glyphs), input_12=str(equipped_gear),
                                             input_13=str(self.equipped_tarot), input_14=str(self.insignia),
                                             input_15=int(self.vouch_points))
                    pandora_db.execute(query)
                    response = f"Player registration completed!\n Welcome {self.player_username}!"
                    response += f"\nPlease use the !quest command to proceed."
                    registered_player = get_player_by_discord(self.discord_id)
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
        path_location = globalitems.path_names.index(path_type)
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
        self.player_stats = [0, 0, 0, 0, 0, 0, 0]
        reset_points = "0;0;0;0;0;0;0"
        self.set_player_field("player_stats", reset_points)

    def create_path_embed(self):
        colour, icon = inventory.get_gear_tier_colours(self.player_echelon)
        points_msg = "Your shiny toys are useless if you don't know how to use them."
        embed = discord.Embed(color=colour, title="Avalon, Pathwalker of the True Laws", description=points_msg)
        embed.add_field(name=f"{self.player_username}'s Skill Points", value="", inline=False)
        for path_label, points, gear_points in zip(globalitems.path_names, self.player_stats, self.gear_points):
            value_msg = f"Points: {points}"
            if gear_points > 0:
                value_msg += f" (+{gear_points})"
            embed.add_field(name=f"Path of {path_label}", value=value_msg, inline=True)
        spent_points = sum(self.player_stats)
        remaining_points = self.player_lvl - spent_points
        embed.add_field(name=f"Unspent Points: {remaining_points}", value="", inline=False)
        return embed

    def build_points_embed(self, selected_path):
        colour, icon = inventory.get_gear_tier_colours(self.player_echelon)
        embed = discord.Embed(color=colour, title=f"{selected_path}", description="Stats per point:\n")
        
        path_type = selected_path.split(" ")[-1]
        for modifier in skillpaths.path_perks[path_type]:
            embed.description += f'{modifier[0].replace("X", str(modifier[1]))}\n'

        # Calculate the points.
        points_field = self.player_stats[globalitems.path_names.index(path_type)]
        gear_points = self.gear_points[globalitems.path_names.index(path_type)]
        points_msg = f"{self.player_username}'s {selected_path} points: {points_field}"
        total_points = points_field + gear_points
        if gear_points > 0:
            points_msg += f" (+{gear_points})"
        embed.add_field(name="", value=points_msg, inline=False)

        # Build the embed.
        embed = skillpaths.display_glyph(path_type, total_points, embed)
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

        # Item Multipliers
        e_item = []
        for idx, x in enumerate(self.player_equipped):
            if x != 0:
                e_item.append(inventory.read_custom_item(x))
                e_item[idx].update_damage()
                self.player_damage += random.randint(e_item[idx].item_damage_min, e_item[idx].item_damage_max)
                itemrolls.assign_roll_values(self, e_item[idx])
                if e_item[idx].item_num_sockets == 1:
                    itemrolls.assign_gem_values(self, e_item[idx])
            else:
                e_item.append(None)
        if e_item[0]:
            base_attack_speed *= float(e_item[0].item_base_stat)
            if self.player_class == "Rider":
                base_attack_speed *= 1.25
        if e_item[1]:
            base_damage_mitigation = float(e_item[1].item_base_stat)
        for y in range(1, 5):
            if e_item[y]:
                self.unique_ability_multipliers(e_item[y])
        if self.equipped_tarot != "":
            e_tarot = tarot.check_tarot(self.player_id, tarot.card_dict[self.equipped_tarot][0])
            e_tarot.assign_tarot_values(self)
        if self.insignia != "":
            insignia.assign_insignia_values(self)

        # Path Multipliers
        total_points = [x + y for x, y in zip(self.player_stats, self.gear_points)]
        unique_breakpoints = [80, 80, 80, 80, 100, 80, 100]
        for glyph, (points, unique_breakpoint) in enumerate(zip(total_points, unique_breakpoints)):
            if points >= unique_breakpoint:
                self.unique_glyph_ability[glyph] = True

        # Storm Path
        storm_bonus = total_points[0]
        self.elemental_multiplier[1] += 0.05 * storm_bonus
        self.elemental_multiplier[2] += 0.05 * storm_bonus
        self.elemental_resistance[1] += 0.01 * storm_bonus
        self.elemental_resistance[2] += 0.01 * storm_bonus
        self.critical_multiplier += 0.03 * storm_bonus
        self.critical_application += storm_bonus // 20

        # Horizon Path
        horizon_bonus = total_points[2]
        self.elemental_multiplier[3] += 0.05 * horizon_bonus
        self.elemental_multiplier[4] += 0.05 * horizon_bonus
        self.elemental_resistance[3] += 0.01 * horizon_bonus
        self.elemental_resistance[4] += 0.01 * horizon_bonus
        self.bleed_multiplier += 0.1 * horizon_bonus
        self.bleed_application += horizon_bonus // 20

        # Frostfire Path
        frostfire_bonus = total_points[1]
        self.elemental_multiplier[5] += 0.05 * frostfire_bonus
        self.elemental_multiplier[0] += 0.05 * frostfire_bonus
        self.elemental_resistance[5] += 0.01 * frostfire_bonus
        self.elemental_resistance[0] += 0.01 * frostfire_bonus
        self.class_multiplier += 0.01 * frostfire_bonus

        # Eclipse Path
        eclipse_bonus = total_points[3]
        self.elemental_multiplier[6] += 0.05 * eclipse_bonus
        self.elemental_multiplier[7] += 0.05 * eclipse_bonus
        self.elemental_resistance[6] += 0.01 * eclipse_bonus
        self.elemental_resistance[7] += 0.01 * eclipse_bonus
        self.ultimate_multiplier += 0.1 * eclipse_bonus
        self.ultimate_application += eclipse_bonus // 20
        if eclipse_bonus >= 100:
            self.skill_base_damage_bonus[3] += 3

        # Confluence Path
        confluence_bonus = total_points[5]
        self.aura += 0.01 * confluence_bonus
        self.all_elemental_curse += 0.01 * confluence_bonus
        self.elemental_application += 2 * confluence_bonus // 20
        if confluence_bonus >= 80:
            self.all_elemental_multiplier *= 2
        if confluence_bonus >= 100:
            self.all_elemental_penetration *= 2
            self.all_elemental_curse *= 2

        # Star Path
        star_bonus = total_points[4]
        self.elemental_multiplier[8] += 0.07 * star_bonus
        self.elemental_resistance[8] += 0.01 * star_bonus
        self.combo_multiplier += 0.03 * star_bonus
        star_skill_bonus = 0.25 * star_bonus // 20
        self.skill_base_damage_bonus[0] += star_skill_bonus
        if star_bonus >= 80:
            self.skill_base_damage_bonus[1] += star_skill_bonus
        if star_bonus >= 100:
            self.skill_base_damage_bonus[2] += star_skill_bonus

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

        # Frostfire Path
        def apply_cascade(bonus, data_list):
            temp_list = data_list.copy()
            temp_list[0], temp_list[5] = 0, 0
            highest_index = temp_list.index(max(temp_list))
            data_list[highest_index] += data_list[0] + data_list[5]
        # self.??? += 0.01 * frostfire_bonus
        if frostfire_bonus >= 80:
            apply_cascade(self.elemental_multiplier, frostfire_bonus)
            apply_cascade(self.elemental_penetration, frostfire_bonus)
            apply_cascade(self.elemental_curse, frostfire_bonus)
        if frostfire_bonus >= 100:
            self.elemental_multiplier[0] *= 3
            self.elemental_multiplier[5] *= 3
            self.elemental_penetration[0] *= 3
            self.elemental_penetration[5] *= 3
            self.elemental_curse[0] *= 3
            self.elemental_curse[5] *= 3

        # Solitude Path
        def apply_singularity(data_list, bonus):
            highest_index = data_list.index(max(data_list))
            data_list[highest_index] += bonus

        solitude_bonus = total_points[6] * 2 if total_points[6] >= 100 else total_points[6]
        apply_singularity(self.elemental_multiplier, (0.10 * solitude_bonus))
        apply_singularity(self.elemental_penetration, (0.05 * solitude_bonus))
        apply_singularity(self.elemental_curse, (0.01 * solitude_bonus))
        self.temporal_application += solitude_bonus // 20

        # Elemental Calculations
        if self.elemental_application > 0:
            self.elemental_capacity += self.elemental_application
            if self.elemental_capacity > 9:
                self.elemental_capacity = 9
        # Hard limitation exceptions.
        if frostfire_bonus >= 80:
            self.elemental_capacity = 3
        if solitude_bonus >= 100:
            self.elemental_capacity = 1

        # Apply omni multipliers.
        for x in range(9):
            self.elemental_multiplier[x] += self.all_elemental_multiplier
            self.elemental_penetration[x] += self.all_elemental_penetration
            self.elemental_resistance[x] += self.all_elemental_resistance
            self.elemental_curse[x] += self.all_elemental_curse
            if self.elemental_resistance[x] >= 0.9:
                self.elemental_resistance[x] = 0.9
            # Apply unique resistance conversion.
            self.elemental_multiplier[x] += self.elemental_resistance[x] * int(round(self.unique_conversion[0] * 100))
        for y in range(6):
            self.banes[y] += self.banes[6]
        # Calculate unique conversions
        for x in range(9):
            self.final_damage += int(round(self.player_mHP / 100)) * self.unique_conversion[1]

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
                self.elemental_damage[idx] = adjusted_damage * (1 + self.elemental_multiplier[idx])
                resist_multi = combat.boss_defences("Element", self, boss_object, idx)
                penetration_multi = 1 + self.elemental_penetration[idx]
                self.elemental_damage[idx] *= resist_multi * penetration_multi * self.elemental_conversion[idx]
        subtotal_damage = sum(self.elemental_damage) * (1 + boss_object.aura)
        subtotal_damage *= combat.boss_true_mitigation(boss_object.boss_lvl)
        adjusted_damage = int(subtotal_damage)
        return adjusted_damage

    def get_bleed_damage(self, boss_object):
        e_weapon = inventory.read_custom_item(self.player_equipped[0])
        player_damage = self.get_player_initial_damage()
        self.player_total_damage = self.boss_adjustments(player_damage, boss_object, e_weapon)
        self.player_total_damage *= (1 + self.bleed_multiplier)
        return self.player_total_damage

    def equip(self, selected_item) -> str:
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            if selected_item.item_type not in ["W", "A", "Y", "G", "C"]:
                response = "Item is not equipable."
                return response
            # Equip the item and update the database.
            location = inventory.item_loc_dict[selected_item.item_type]
            item_type = inventory.item_type_dict[location]
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
        potion_msg = ""
        for x in range(1, 5):
            loot_item = inventory.BasicItem(f"Potion{x}")
            potion_stock = inventory.check_stock(self, loot_item.item_id)
            potion_msg += f"\n{loot_item.item_emoji} {potion_stock}x {loot_item.item_name}"
        stamina_title = f"{self.player_username}\'s Stamina: "
        stamina_title += f"{str(self.player_stamina)} / 5000"
        embed_msg = discord.Embed(colour=discord.Colour.green(), title=stamina_title, description="")
        embed_msg.add_field(name="", value=potion_msg)
        return embed_msg

    def unique_ability_multipliers(self, item):
        if item.item_bonus_stat == "":
            return
        item_type = item.item_type
        if item.item_tier >= 5:
            if item.item_bonus_stat in globalitems.tier_5_ability_dict:
                unique_ability = item.item_bonus_stat
            else:
                unique_ability = globalitems.void_ability_dict[item.item_bonus_stat]
                self.final_damage += 0.5
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
                case "Blooming Vitality":
                    self.hp_multiplier += globalitems.tier_5_ability_dict[unique_ability]
                case "Unravel":
                    self.temporal_application += globalitems.tier_5_ability_dict[unique_ability]
                case _:
                    pass
        else:
            keywords = item.item_bonus_stat.split()
            match item_type:
                case "Y":
                    if keywords[0] in bosses.boss_list:
                        buff_type_loc = bosses.boss_list.index(keywords[0])
                        self.banes[buff_type_loc] += 0.5
                    elif keywords[0] == "Human":
                        self.banes[5] += 0.5
                case "G":
                    buff_type_loc = globalitems.element_special_names.index(keywords[0])
                    self.elemental_multiplier[buff_type_loc] += 0.25
                case "C":
                    buff_type_loc = globalitems.element_special_names.index(keywords[0])
                    self.elemental_penetration[buff_type_loc] += 0.25
                case _:
                    pass

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
        return False
    return True


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
            target_player.discord_id = int(df["discord_id"].values[0])
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
    return target_player


def get_player_by_discord(discord_id) -> PlayerProfile:
    target_player = PlayerProfile()
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM PlayerList WHERE discord_id = :id_check")
        query = query.bindparams(id_check=str(discord_id))
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            target_player.player_id = int(df["player_id"].values[0])
            target_player.discord_id = int(df["discord_id"].values[0])
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
                target_player.discord_id = int(row["discord_id"])
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
                target_player.discord_id = int(row["discord_id"])
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


def show_num(input_number, adjust=100):
    return int(round(input_number * adjust))


def get_thumbnail_by_class(class_name):
    thumbnail_url = f"https://kyleportfolio.ca/botimages/classicon/{class_name}.png"
    return thumbnail_url
