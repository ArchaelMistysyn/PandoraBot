# General imports
import pandas as pd
import discord
import random
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

import math

# Data imports
import globalitems as gli
import sharedmethods as sm
from pandoradb import run_query as rqy

# Core imports
import quest
import inventory
import combat

# Misc imports
import skillpaths

# Item/crafting imports
import loot
import itemrolls
import tarot
import insignia
import pact
import sovereignweapon as sw


class PlayerProfile:
    def __init__(self):

        # Initialize player base info.
        self.player_id, self.discord_id, self.player_username = 0, 0, ""
        self.player_exp, self.player_level, self.player_echelon = 0, 0, 0
        self.player_class = ""
        self.player_quest, self.quest_tokens = 0, [0 for x in range(30)]
        self.quest_tokens[1] = 1
        self.player_coins, self.player_stamina, self.vouch_points, self.luck_bonus = 0, 0, 0, 0
        # Initialize player gear/stats info.
        self.player_stats, self.gear_points, self.player_equipped = [0] * 9, [0] * 9, [0] * 7
        self.pact, self.insignia, self.equipped_tarot = "", "", ""

        # Initialize player health stats.
        self.player_mHP, self.player_cHP = 1000, 1000
        self.immortal = False
        # Initialize player damage values.
        self.player_damage_min, self.player_damage_max, self.total_damage = 0, 0, 0.0
        # Initialize elemental stats.
        self.elemental_damage = [0] * 9
        self.elemental_mult, self.elemental_pen, self.elemental_curse = [0.0] * 9, [0.0] * 9, [0.0] * 9
        self.elemental_conversion = [1.0] * 9
        self.all_elemental_mult, self.all_elemental_pen, self.all_elemental_curse = 0.0, 0.0, 0.0
        self.singularity_mult, self.singularity_pen, self.singularity_curse = 0.0, 0.0, 0.0
        # Initialize specialization stats.
        self.unique_glyph_ability = [False] * 9
        self.elemental_capacity = 3
        self.mana_mult, self.start_mana, self.mana_limit, self.mana_shatter = 1.0, 250, 250, False
        self.bleed_mult, self.bleed_pen = 0.0, 0.0
        self.combo_mult, self.combo_pen = 0.05, 0.0
        self.ultimate_mult, self.ultimate_pen, = 0.0, 0.0
        self.critical_mult, self.critical_pen = 1.0, 0.0
        self.bloom_mult = 10.0
        self.temporal_mult = 1.0
        self.trigger_rate = {"Fractal": 0.0, "Hyperbleed": 0.0, "Critical": 0.0, "Omega": 0.0,
                             "Temporal": 0.0, "Bloom": 0.0, "Status": 1.0}
        self.perfect_rate = {"Fractal": 0, "Hyperbleed": 0, "Critical": 0, "Temporal": 0, "Bloom": 0}
        self.appli = {"Critical": 0, "Bleed": 0, "Ultimate": 0, "Life": 0, "Mana": 0,
                      "Temporal": 0, "Elemental": 0, "Combo": 0, "Aqua": 0}
        # Initialize misc Datasets.
        self.resonance = [0] * 31
        self.banes = [0.0] * 7
        self.skill_damage_bonus = [0] * 4
        self.unique_conversion = [0.0] * 5
        self.spec_conv = {"Heavenly": 0.0, "Stygian": 0.0, "Calamity": 0.0}
        # Initialize misc stats.
        self.charge_generation = 1
        self.attack_speed = 0.0
        self.class_multiplier, self.final_damage, self.rng_bonus = 0.0, 0.0, 0.0
        self.defence_pen, self.resist_pen = 0.0, 0.0
        self.aqua_mode, self.aqua_points = 0, 0
        self.flare_type = ""
        # Initialize defensive stats.
        self.hp_bonus, self.hp_regen, self.hp_multiplier, self.recovery = 0.0, 0.0, 0.0, 3
        self.block, self.dodge = 0, 0
        self.damage_mitigation, self.mitigation_bonus = 0.0, 0.0
        self.elemental_res, self.all_elemental_res = [0.0] * 9, 0.1

    async def get_player_stats(self, method):
        await self.reload_player()
        # Construct the base embed.
        echelon_colour, _ = sm.get_gear_tier_colours((self.player_echelon + 1) // 2)
        resources = f'<:estamina:1145534039684562994> {self.player_username}\'s stamina: {self.player_stamina:,}'
        resources += f'\n{gli.coin_icon} Lotus Coins: {self.player_coins:,}'
        exp = f'Level: {self.player_level} Exp: ({self.player_exp:,} / {get_max_exp(self.player_level):,})'
        id_msg = f'User ID: {self.player_id}\nClass: {gli.class_icon_dict[self.player_class]}'
        embed_msg = discord.Embed(colour=echelon_colour, title=self.player_username, description=id_msg)
        embed_msg.add_field(name=exp, value=resources, inline=False)
        embed_msg.set_thumbnail(url=f"{sm.get_thumbnail_by_class(self.player_class)}")

        # Initialize the values.
        title_msg, stats = "", ""
        temp_embed = None

        if method in [1, 2]:
            # Calculate the damage spread.
            element_breakdown = []
            for x in range(9):
                total_multi = (1 + self.elemental_mult[x]) * (1 + self.elemental_pen[x])
                total_multi *= (1 + self.elemental_curse[x]) * self.elemental_conversion[x]
                element_breakdown.append((x, total_multi * 100))
            sorted_element_breakdown = sorted(element_breakdown, key=lambda v: v[1], reverse=True)
            for z, total_multi in sorted_element_breakdown:
                temp_icon = gli.ele_icon[z]
                temp_dmg_str = f"(Dmg: {int(round(self.elemental_mult[z] * 100)):,}%)"
                temp_pen_str = f"(Pen: {int(round(self.elemental_pen[z] * 100)):,}%)"
                temp_curse_str = f"(Curse: {int(round(self.elemental_curse[z] * 100)):,}%)"
                if method == 1:
                    stats += f"\n{temp_icon} Total Damage: {int(round(total_multi)):,}%"
                if method == 2:
                    stats += f"\n{temp_icon} {temp_dmg_str} - {temp_pen_str} - {temp_curse_str}"
            if method == 1:
                await self.get_player_base_damage()
                # Offensive Stat Display.
                base_stats = f"Item Base Damage: {self.player_damage_min:,} - {self.player_damage_max:,}"
                base_stats += f"\nAttack Speed: {round(math.floor(self.attack_speed * 10) / 10, 1)} / min"
                embed_msg.add_field(name="Offensive Stats", value=f"{base_stats}{stats}", inline=False)
                # Construct the damage spread field.
                if self.player_equipped[0] != 0:
                    stats = ""
                    e_weapon = await inventory.read_custom_item(self.player_equipped[0])
                    used_elements, used_multipliers = [], []
                    temp_element_list = combat.limit_elements(self, e_weapon)
                    # Build the list of used elements/multipliers.
                    for i, is_used in enumerate(temp_element_list):
                        if is_used:
                            used_elements.append(gli.ele_icon[i])
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
                        embed_msg.add_field(name="Damage Spread", value=stats, inline=False)
                return embed_msg
            if method == 2:
                # Stat Breakdown Display.
                embed_msg.add_field(name="Elemental Breakdown", value=stats, inline=False)
                return embed_msg
        if method == 3:
            # Defensive display.
            stats = f"Player HP: {self.player_mHP:,}\nRecovery: {self.recovery}"
            for idy, y in enumerate(self.elemental_res):
                stats += f"\n{gli.ele_icon[idy]} Resistance: {show_num(y)}%"
            stats += f"\nDamage Mitigation: {show_num(self.damage_mitigation, 1)}%"
            stats += f"\nBlock Rate: {show_num(self.block, 1)}%"
            stats += f"\nDodge Rate: {show_num(self.dodge, 1)}%"
            embed_msg.add_field(name="Defensive Stats", value=stats, inline=False)
            return embed_msg
        if method == 4:
            # Application Display.
            def set_appli(appli, data):
                if appli not in ["Elemental", "Critical"] and self.appli[appli] <= 0:
                    return ""
                section_string = f"**{appli} Application: {self.appli[appli]}**\n"
                for tag, value in data:
                    extension = "%" if tag not in ["Elemental Capacity"] else ""
                    section_string += f"{tag}: {value:,}{extension}\n"
                return f"{section_string}"

            stats += set_appli(appli="Elemental",
                               data=[("Elemental Capacity", self.elemental_capacity),
                                     ("Fractal Rate", self.trigger_rate["Fractal"])])
            stats += set_appli(appli="Critical",
                               data=[("Critical Rate", self.trigger_rate["Critical"]),
                                     ("Critical Damage", show_num(self.critical_mult)),
                                     ("Critical Penetration", show_num(self.critical_pen)),
                                     ("Omega Rate", self.trigger_rate["Omega"])])
            stats += set_appli(appli="Combo",
                               data=[("Combo Damage", show_num(self.combo_mult)),
                                     ("Combo Penetration", show_num(self.combo_pen))])
            stats += set_appli(appli="Ultimate",
                               data=[("Ultimate Damage", show_num(self.ultimate_mult)),
                                     ("Ultimate Penetration", show_num(self.ultimate_pen))])
            stats += set_appli(appli="Bleed",
                               data=[("Bleed Damage", show_num(self.bleed_mult)),
                                     ("Bleed Penetration", show_num(self.bleed_pen)),
                                     ("Hyperbleed Rate", self.trigger_rate["Hyperbleed"])])
            stats += set_appli(appli="Temporal",
                               data=[("Time Shatter Damage", show_num(self.temporal_mult)),
                                     ("Time Lock Rate", self.trigger_rate["Temporal"])])
            stats += set_appli(appli="Mana",
                               data=[("Mana Damage", show_num(self.mana_mult)),
                                     ("Mana Limit", self.mana_limit)])
            embed_msg.add_field(name="", value=stats, inline=False)
            return embed_msg
        if method == 5:
            # Points Display.
            temp_embed = await skillpaths.create_path_embed(self)
            if temp_embed is not None:
                for field in temp_embed.fields[:-1]:
                    embed_msg.add_field(name=field.name, value=field.value, inline=field.inline)
            embed_msg.add_field(name=title_msg, value=stats, inline=False)
            return embed_msg
        if method == 6:
            # Glyph Display.
            embed_msg.add_field(name=f"{self.player_username}'s Glyphs (Above tier 1)", value="", inline=False)
            if self.aqua_mode != 0:
                embed_msg = await skillpaths.display_glyph("Waterfalls", self.aqua_points, embed_msg)
                return embed_msg
            inline_count = 0
            for path_index, path_type in enumerate(gli.path_names):
                total_points = self.player_stats[path_index] + self.gear_points[path_index]
                if total_points >= 20:
                    inline_count += 1
                    embed_msg = await skillpaths.display_glyph(path_type, total_points, embed_msg, is_inline=True)
                    if inline_count % 2 == 0:
                        embed_msg.add_field(name="", value="", inline=False)
            return embed_msg
        if method == 7:
            # Misc Multipliers
            title_msg = "Misc Multipliers"
            for idh, h in enumerate(self.banes[:-1]):
                stats += f"\n{gli.boss_list[idh]} Bane: {show_num(h)}%" if idh < 5 else f"\nHuman Bane: {show_num(h)}%"
            stats += f"\nClass Mastery: {show_num(self.class_multiplier):,}%"
            stats += f"\nFinal Damage: {show_num(self.final_damage):,}%"
            stats += f"\nDefence Penetration: {show_num(self.defence_pen):,}%"
            stats += f"\nBloom Damage: {show_num(self.bloom_mult):,}%"
            stats += f"\nBloom Rate: {show_num(self.trigger_rate['Bloom']):,}%"
            embed_msg.add_field(name=title_msg, value=stats, inline=False)
            return embed_msg

    async def adjust_coins(self, coin_change, reduction=False, apply_pact=True):
        adjust_msg = ""
        coin_change *= -1 if reduction else 1
        if apply_pact and not reduction:
            pact_object = pact.Pact(self.pact)
            if pact_object.pact_variant == "Greed":
                coin_change *= 2
                adjust_msg = " [Greed Bonus]"
            elif pact_object.pact_variant == "Gluttony":
                coin_change = int(round(coin_change / 2))
                adjust_msg = " [Gluttony Penalty]"
        self.player_coins += coin_change
        await self.set_player_field("player_coins", self.player_coins)
        return f"{coin_change:,}x{adjust_msg}"

    async def adjust_exp(self, exp_change, apply_pact=True):
        adjust_msg = ""
        if apply_pact:
            pact_object = pact.Pact(self.pact)
            if pact_object.pact_variant == "Gluttony":
                exp_change *= 2
                adjust_msg = " [Gluttony Bonus]"
            elif pact_object.pact_variant == "Greed":
                exp_change = int(round(exp_change / 2))
                adjust_msg = " [Greed Penalty]"
        self.player_exp += exp_change
        # Handle Levels
        max_exp = get_max_exp(self.player_level)
        level_increase = 0
        max_level = 999 if self.player_quest > 53 else 200 if self.player_quest > 52 else 150 if self.player_quest > 50 else 100

        while self.player_exp > max_exp and self.player_level < max_level:
            self.player_exp -= max_exp
            level_increase += 1
        self.player_level += level_increase
        change_message = "" if level_increase == 0 else f"(Level +{level_increase}) "
        change_message += f"{exp_change:,}x{adjust_msg}"
        # This could be further improved to be one single adjustment.
        await self.set_player_field("player_level", self.player_level)
        await self.set_player_field("player_exp", self.player_exp)
        return change_message, level_increase

    async def set_player_field(self, field_name, field_value):
        raw_query = f"UPDATE PlayerList SET {field_name} = :input_1 WHERE player_id = :player_check"
        await rqy(raw_query, params={'player_check': int(self.player_id), 'input_1': field_value})

    async def unequip_item(self, item):
        self.player_equipped = [0 if element == item.item_id else element for element in self.player_equipped]
        equipped_gear = ";".join(map(str, self.player_equipped))
        await self.set_player_field("player_equipped", equipped_gear)

    async def add_new_player(self, selected_class, discord_id):
        self.discord_id = discord_id
        self.player_class = selected_class
        self.player_quest, self.player_level = 1, 1
        self.player_stamina = 5000
        player_stats, equipped_gear = "0;0;0;0;0;0;0;0;0", "0;0;0;0;0;0;0"
        quest_tokens = ";".join(map(str, self.quest_tokens))
        raw_query = "SELECT * FROM PlayerList WHERE discord_id = :id_check"
        df = await rqy(raw_query, return_value=True, params={'id_check': self.discord_id})

        if df is not None and len(df.index) != 0:
            return f"Player with discord ID: ({self.discord_id}) is already registered."
        raw_query = "SELECT * FROM PlayerList WHERE player_username = :username_check"
        df = await rqy(raw_query, return_value=True, params={'username_check': self.player_username})
        if df is not None and len(df.index) != 0:
            return f"Username {self.player_username} is taken. Please pick a new username."
        raw_query = ("INSERT INTO PlayerList "
                     "(discord_id, player_username, player_level, player_exp, player_echelon, player_quest, "
                     "quest_tokens, player_stamina, player_class, player_coins, player_stats, player_equipped, "
                     "player_tarot, player_insignia, player_pact, vouch_points) "
                     "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6,"
                     ":input_7, :input_8, :input_9, :input_10, :input_11, :input_12, :input_13, "
                     ":input_14, :input_15, :input_16)")
        params = {
            'input_1': str(self.discord_id), 'input_2': str(self.player_username), 'input_3': int(self.player_level),
            'input_4': int(self.player_exp), 'input_5': int(self.player_echelon),
            'input_6': int(self.player_quest), 'input_7': quest_tokens,
            'input_8': int(self.player_stamina), 'input_9': str(self.player_class), 'input_10': int(self.player_coins),
            'input_11': player_stats, 'input_12': equipped_gear, 'input_13': str(self.equipped_tarot),
            'input_14': str(self.insignia), 'input_15': str(self.pact), 'input_16': int(self.vouch_points)}
        await rqy(raw_query, params=params)
        registered_player = await get_player_by_discord(self.discord_id)
        raw_query = ("INSERT INTO MiscPlayerData (player_id, thana_visits, deaths, toggle_inv) "
                     "VALUES (:input_1, :input_2, :input_3, :input_4)")
        params = {"input_1": registered_player.player_id, "input_2": 0, "input_3": 0, "input_4": 0}
        await rqy(raw_query, params=params)
        return f"Welcome {self.player_username}!\nUse /quest to begin."

    async def update_misc_data(self, field_name, change, overwrite_value=False):
        raw_query = f"UPDATE MiscPlayerData SET {field_name} = {field_name} + :new_value WHERE player_id = :check"
        if overwrite_value:
            raw_query = f"UPDATE MiscPlayerData SET {field_name} = :new_value WHERE player_id = :check"
        params = {"new_value": change, "check": self.player_id}
        await rqy(raw_query, params=params)

    async def check_misc_data(self, field_name):
        raw_query = f"SELECT {field_name} FROM MiscPlayerData WHERE player_id = :player_check"
        params = {"player_check": self.player_id}
        result_df = await rqy(raw_query, params=params, return_value=True)
        return result_df[field_name].values[0]

    async def spend_stamina(self, cost) -> bool:
        is_spent = False
        if self.player_stamina >= cost:
            self.player_stamina -= cost
            await self.set_player_field("player_stamina", self.player_stamina)
            is_spent = True
        return is_spent

    async def get_equipped(self):
        raw_query = "SELECT * FROM PlayerList WHERE player_id = :player_check"
        df = await rqy(raw_query, return_value=True, params={'player_check': self.player_id})
        temp_equipped = list(df['player_equipped'].values[0].split(';'))
        self.player_equipped = list(map(int, temp_equipped))
        temp_stats = list(df['player_stats'].values[0].split(';'))
        self.player_stats = list(map(int, temp_stats))
        self.equipped_tarot = str(df['player_tarot'].values[0])
        self.insignia = str(df['player_insignia'].values[0])
        self.pact = str(df['player_pact'].values[0])

    async def reset_skill_points(self):
        self.player_stats = [0] * 9
        reset_points = "0;0;0;0;0;0;0;0;0"
        await self.set_player_field("player_stats", reset_points)

    async def reload_player(self):
        _ = await get_player_by_id(self.player_id, reloading=self)

    def apply_elemental_conversion(self, index_data, reduction_value, increase_value):
        # Apply more multipliers.
        if isinstance(index_data, (tuple, list)):
            other_positions = [i for i in range(len(self.elemental_conversion)) if i not in index_data]
            for position in index_data:
                self.elemental_conversion[position] += increase_value
        else:
            other_positions = [i for i in range(len(self.elemental_conversion)) if i != index_data]
            self.elemental_conversion[index_data] += increase_value
        # Apply less multipliers.
        for position in other_positions:
            self.elemental_conversion[position] -= reduction_value

    async def get_player_multipliers(self):
        base_critical_chance, base_attack_speed, base_mitigation = 10.0, 1.0, 0.0
        base_player_hp = 1000 + 50 * self.player_level
        # Class Multipliers
        class_bonus = {"Ranger": ["Critical", 1], "Weaver": ["Elemental", 2], "Assassin": ["Bleed", 1],
                       "Mage": ["Mana", 1], "Summoner": ["Combo", 1], "Knight": ["Ultimate", 1], "Rider": ["Life", 1]}
        self.appli[class_bonus[self.player_class][0]] += class_bonus[self.player_class][1]
        # Item Multipliers
        e_item = []
        for idx, x in enumerate(self.player_equipped):
            if x != 0:
                e_item.append(await inventory.read_custom_item(x))
                e_item[idx].update_damage()
                self.player_damage_min += e_item[idx].item_damage_min
                self.player_damage_max += e_item[idx].item_damage_max
                if e_item[idx].item_base_type in gli.sovereign_item_list:
                    await sw.assign_sovereign_values(self, e_item[idx])
                else:
                    await itemrolls.assign_roll_values(self, e_item[idx])
                itemrolls.assign_item_element_stats(self, e_item[idx])
                if e_item[idx].item_num_sockets == 1:
                    await itemrolls.assign_gem_values(self, e_item[idx])
            else:
                e_item.append(None)
        if e_item[0] is not None:
            base_attack_speed *= float(e_item[0].item_base_stat)
            if self.player_class == "Rider":
                base_attack_speed *= 1.25
        if e_item[1] is not None:
            base_mitigation = e_item[1].item_base_stat
        for y in range(1, 5):
            if e_item[y]:
                self.unique_ability_multipliers(e_item[y])
        # Non-Gear Item Multipliers
        insignia.assign_insignia_values(self)
        if self.equipped_tarot != "":
            e_tarot = await tarot.check_tarot(self.player_id, tarot.card_dict[self.equipped_tarot][0])
            await e_tarot.assign_tarot_values(self)
        # Assign Path Multipliers
        total_points = skillpaths.assign_path_multipliers(self)
        # Application Bonuses
        base_critical_chance += self.appli["Critical"]
        self.critical_mult += self.appli["Critical"]
        self.skill_damage_bonus[3] += self.appli["Ultimate"] * 0.25
        self.charge_generation += self.appli["Ultimate"]
        self.all_elemental_mult += self.appli["Elemental"] * 0.25
        self.hp_multiplier += 0.1 * self.appli["Life"]
        # Elemental Capacity
        self.elemental_capacity += max(0, self.appli["Elemental"])
        # Pact Bonus Multipliers (Occurs after stat adjustments, but before stat hard limits)
        pact.assign_pact_values(self)
        # Capacity Hard Limits
        self.elemental_capacity = min(9, self.elemental_capacity)
        self.mana_limit = max(10, self.mana_limit)
        # Match start mana to limit unless start has been defaulted to 0
        self.start_mana = self.mana_limit if self.start_mana != 0 else 0
        # Solitude/Frostfire and Aqua exceptions
        self.elemental_capacity = 1 if total_points[6] >= 100 or self.aqua_mode != 0 else 3 \
            if total_points[1] >= 80 else self.elemental_capacity
        # General Calculations
        self.trigger_rate["Critical"] = int((1 + self.trigger_rate["Critical"]) * base_critical_chance)
        self.attack_speed = (1 + self.attack_speed) * base_attack_speed
        self.damage_mitigation = min((1 + (self.mitigation_bonus + self.damage_mitigation)) * base_mitigation, 90)
        self.player_cHP = self.player_mHP = int((base_player_hp + self.hp_bonus) * (1 + self.hp_multiplier))
        # Trigger Rates
        self.trigger_rate["Omega"] = min(100, int(self.trigger_rate["Omega"] + round(self.appli["Critical"])) * 3)
        self.trigger_rate["Hyperbleed"] = min(100, int(round(self.trigger_rate["Hyperbleed"] + self.appli["Bleed"])) * 4)
        self.trigger_rate["Fractal"] = min(100, int(round(self.trigger_rate["Fractal"] + self.appli["Elemental"])) * 4)
        self.trigger_rate["Temporal"] = min(100, int(round(self.trigger_rate["Temporal"] + self.appli["Temporal"])) * 4)
        # Perfect Rates
        self.perfect_rate["Critical"] = 1 if self.aqua_points >= 80 else self.perfect_rate["Critical"]
        for mechanic in self.perfect_rate.keys():  
            self.trigger_rate[mechanic] = 100 if self.perfect_rate[mechanic] > 0 >= 80 else self.trigger_rate[mechanic]
        match_count = sum(1 for item in e_item if item is not None and item.item_damage_type == self.player_class)
        if self.unique_conversion[2] >= 1:
            unique_damage_types = {item.item_damage_type for item in e_item}
            match_count = len(unique_damage_types)
        self.class_multiplier += 0.05 + self.unique_conversion[2]
        self.class_multiplier *= match_count
        # Singularity multipliers
        apply_singularity(self.elemental_mult, self.singularity_mult)
        apply_singularity(self.elemental_pen, self.singularity_pen)
        apply_singularity(self.elemental_curse, self.singularity_curse)
        # Apply omni multipliers.
        for x in range(9):
            self.elemental_mult[x] += self.all_elemental_mult
            self.elemental_pen[x] += self.all_elemental_pen
            self.elemental_res[x] += self.all_elemental_res
            self.elemental_curse[x] += self.all_elemental_curse
            self.elemental_res[x] = min(0.9, self.elemental_res[x])
            # Apply unique resistance conversion.
            self.elemental_mult[x] += self.elemental_res[x] * self.unique_conversion[0]
        for y in range(6):
            self.banes[y] += self.banes[6]
        # Calculate unique conversions
        # Reduce Max HP convert to Final Damage (Unique Conversion 1)
        hp_reduction = int(self.player_mHP * self.unique_conversion[1])
        self.player_mHP = int(self.player_mHP - hp_reduction)
        self.final_damage += hp_reduction // 100
        # Mitigation convert to Final Damage (Unique Conversion 3)
        self.final_damage += self.damage_mitigation * self.unique_conversion[3]
        # Blood Blossom (Unique Conversion 4)
        if self.unique_conversion[4] >= 1:
            hp_blossom_bonus = self.player_mHP // 100
            self.bloom_mult, self.bleed_mult = self.bloom_mult + hp_blossom_bonus, self.bleed_mult + hp_blossom_bonus
            self.bleed_mult += hp_blossom_bonus
        # Divine Blossom (Unique Conversion 4)
        if self.unique_conversion[4] == 2:
            self.final_damage += hp_blossom_bonus
        # Aqua Mode critical bonus
        if self.aqua_mode != 0 and self.equipped_tarot != "" and e_tarot.card_numeral == "XIV":
            self.critical_mult += self.elemental_mult[1]
        # Flat Damage Bonuses
        self.player_damage_min += self.appli["Life"] * self.player_mHP * 5
        self.player_damage_max += self.appli["Life"] * self.player_mHP * 5
        # Attack speed hard cap
        self.attack_speed = min(10, self.attack_speed)

    async def get_player_base_damage(self):
        if self.player_equipped[0] == 0:
            return
        e_weapon = await inventory.read_custom_item(self.player_equipped[0])
        if e_weapon is not None and e_weapon.item_base_type in gli.sovereign_item_list:
            # Sovereign's Omniscience
            self.player_damage_min = self.player_damage_max

    async def get_player_initial_damage(self):
        await self.get_player_base_damage()
        random_damage = random.randint(self.player_damage_min, self.player_damage_max)
        return int(random_damage * (1 + self.class_multiplier) * (1 + self.final_damage))

    async def get_player_boss_damage(self, boss_object):
        e_weapon = await inventory.read_custom_item(self.player_equipped[0])
        num_elements = sum(e_weapon.item_elements)
        player_damage = await self.get_player_initial_damage()
        player_damage, critical_type = combat.check_critical(self, player_damage, num_elements)
        self.total_damage = self.boss_adjustments(player_damage, boss_object, e_weapon)
        return critical_type

    def boss_adjustments(self, player_damage, boss_obj, e_weapon):
        damage = player_damage
        if boss_obj.boss_type != "Ruler":
            damage *= 1 + self.banes[boss_obj.boss_type_num - 1]
        # Type Defences
        damage *= (combat.boss_defences("", self, boss_obj, -1, e_weapon) + self.defence_pen)
        # Elemental Defences
        highest = 0
        for idx, x in enumerate(combat.limit_elements(self, e_weapon)):
            if x == 1:
                resist_multi = combat.boss_defences("Element", self, boss_obj, idx, e_weapon) + self.resist_pen
                self.elemental_damage[idx] = damage * (1 + self.elemental_mult[idx])
                pen_mult, curse_mult = 1 + self.elemental_pen[idx], 1 + boss_obj.curse_debuffs[idx]
                self.elemental_damage[idx] *= resist_multi * pen_mult * curse_mult * self.elemental_conversion[idx]
                if self.elemental_damage[idx] > self.elemental_damage[highest]:
                    highest = idx
        # Apply status
        stun_status = gli.element_status_list[highest]
        if stun_status is not None and random.randint(1, 100) <= self.trigger_rate["Status"]:
            boss_obj.stun_status = stun_status
            boss_obj.stun_cycles += 1
        return int(sum(self.elemental_damage) * combat.boss_true_mitigation(boss_obj.boss_level))

    async def get_bleed_damage(self, boss_obj):
        weapon = await inventory.read_custom_item(self.player_equipped[0])
        player_damage = await self.get_player_initial_damage()
        self.total_damage = self.boss_adjustments(player_damage, boss_obj, weapon)

    async def equip(self, selected_item):
        if selected_item.item_type not in ["W", "A", "V", "Y", "R", "G", "C"]:
            return "Item is not equipable."
        # Equip the item and update the database.
        location = inventory.item_loc_dict[selected_item.item_type]
        item_type = inventory.item_type_dict[location]
        self.player_equipped[location] = selected_item.item_id
        equipped_gear = ";".join(map(str, self.player_equipped))
        raw_query = f"UPDATE PlayerList SET player_equipped = :input_1 WHERE player_id = :player_check"
        await rqy(raw_query, params={'player_check': int(self.player_id), 'input_1': equipped_gear})
        return f"{item_type} {selected_item.item_id} is now equipped."

    async def unequip(self, selected_item):
        # Unequip non-gem gear items
        if "D" not in selected_item.item_type:
            location = inventory.item_loc_dict[selected_item.item_type]
            self.player_equipped[location] = 0
            equipped_gear = ";".join(map(str, self.player_equipped))
            raw_query = f"UPDATE PlayerList SET player_equipped = :input_1 WHERE player_id = :player_check"
            await rqy(raw_query, params={'player_check': int(self.player_id), 'input_1': equipped_gear})
            return
        # Remove inlaid dragon gems
        item_list = await inventory.read_custom_item(fetch_equipped=self.player_equipped)
        for e_item in item_list:
            if selected_item.item_id == e_item.item_inlaid_gem_id:
                e_item.item_inlaid_gem_id = 0
                await e_item.update_stored_item()  # BATCH_REQUIRED

    async def check_equipped(self, item):
        response = ""
        await self.get_equipped()
        if item.item_type not in inventory.item_loc_dict and "D" not in item.item_type:
            return f"Item {item.item_id} is not recognized."
        if item.item_id in self.player_equipped:
            return f"Item {item.item_id} is equipped."
        elif "D" in item.item_type:
            item_list = await inventory.read_custom_item(None, fetch_equipped=self.player_equipped)
            for e_item in item_list:
                if item.item_id == e_item.item_inlaid_gem_id:
                    response = f"Dragon Heart Gem {item.item_id} is currently inlaid in item {e_item.item_id}."
        return response

    async def create_stamina_embed(self):
        potion_msg = ""
        for x in range(1, 5):
            loot_item = inventory.BasicItem(f"Potion{x}")
            potion_stock = await inventory.check_stock(self, loot_item.item_id)
            potion_msg += f"\n{loot_item.item_emoji} {potion_stock}x {loot_item.item_name}"
        pact_object = pact.Pact(self.pact)
        max_stamina = 5000 if pact_object.pact_variant != "Sloth" else 2500
        stamina_title = f"{self.player_username}\'s Stamina: {str(self.player_stamina)} / {max_stamina}"
        embed_msg = discord.Embed(colour=discord.Colour.green(), title=stamina_title, description="")
        embed_msg.add_field(name="", value=potion_msg)
        return embed_msg

    def unique_ability_multipliers(self, item):
        if item.item_bonus_stat == "":
            return
        if item.item_tier >= 5:
            current_ability = gli.rare_ability_dict[item.item_bonus_stat]
            self.final_damage += 0.25 * (item.item_tier - 4)
            if current_ability[0] in self.appli.keys():
                self.appli[current_ability[0]] += current_ability[1]
            else:
                setattr(self, current_ability[0], current_ability[1])
        else:
            keywords = item.item_bonus_stat.split()
            if item.item_type == "Y":
                if keywords[0] in gli.boss_list:
                    self.banes[gli.boss_list.index(keywords[0])] += 0.5
                elif keywords[0] == "Human":
                    self.banes[5] += 0.5
                return
            element_position = gli.element_special_names.index(keywords[0])
            if item.item_type == "G":
                self.elemental_mult[element_position] += 0.25
                return
            if item.item_type == "C":
                self.elemental_pen[element_position] += 0.25
                return

    async def check_cooldown(self, command_name):
        difference = None
        raw_query = "SELECT * FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check"
        params = {'player_check': self.player_id, 'cmd_check': command_name}
        df = await rqy(raw_query, return_value=True, params=params)
        method = ""
        if len(df) != 0:
            date_string = str(df["time_used"].values[0])
            previous = dt.strptime(date_string, gli.date_formatting)
            previous = previous.replace(tzinfo=ZoneInfo('America/Toronto'))
            now = dt.now(ZoneInfo('America/Toronto'))
            difference = now - previous
            method = str(df["method"].values[0])
        return difference, method

    async def set_cooldown(self, command_name, method, rewind_days=0):
        difference = None
        raw_query = "SELECT * FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check"
        params = {'player_check': self.player_id, 'cmd_check': command_name}
        df = await rqy(raw_query, return_value=True, params=params)
        raw_query = ("INSERT INTO CommandCooldowns (player_id, command_name, method, time_used) "
                     "VALUES (:player_check, :cmd_check, :method, :time_check)")
        if len(df) != 0:
            raw_query = ("UPDATE CommandCooldowns SET command_name = :cmd_check, time_used =:time_check "
                         "WHERE player_id = :player_check AND method = :method")
        timestamp = dt.now(ZoneInfo('America/Toronto')) - timedelta(days=rewind_days)
        current_time = timestamp.strftime(gli.date_formatting)
        params = {'player_check': self.player_id, 'cmd_check': command_name,
                  'method': method, 'time_check': current_time}
        await rqy(raw_query, params=params)
        return difference

    async def clear_cooldown(self, command_name):
        raw_query = "DELETE FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check"
        await rqy(raw_query, params={'player_check': self.player_id, 'cmd_check': command_name})


async def check_username(new_name: str):
    raw_query = "SELECT * FROM PlayerList WHERE player_username = :player_check"
    df = await rqy(raw_query, return_value=True, params={'player_check': new_name})
    return False if len(df) != 0 else True


async def get_player_by_id(player_id, reloading=None):
    raw_query = "SELECT * FROM PlayerList WHERE player_id = :id_check"
    df = await rqy(raw_query, return_value=True, params={'id_check': player_id})
    return None if len(df.index) == 0 else await df_to_player(df, reloading=reloading)


async def get_player_by_discord(discord_id, reloading=None):
    raw_query = "SELECT * FROM PlayerList WHERE discord_id = :id_check"
    df = await rqy(raw_query, return_value=True, params={'id_check': discord_id})
    return None if len(df.index) == 0 else await df_to_player(df, reloading=reloading)


async def df_to_player(row, reloading=None):
    temp = PlayerProfile()
    if isinstance(row, pd.Series):
        temp.player_id, temp.discord_id = int(row['player_id']), int(row['discord_id'])
        temp.player_username = str(row["player_username"])
        temp.player_level, temp.player_exp = int(row['player_level']), int(row['player_exp'])
        temp_string = str(row['quest_tokens'])
        temp.player_echelon, temp.player_quest = int(row['player_echelon']), int(row['player_quest'])
        temp.player_stamina, temp.player_coins = int(row['player_stamina']), int(row['player_coins'])
        temp.player_class = str(row['player_class'])
        temp.vouch_points = int(row['vouch_points'])
    else:
        temp.player_id, temp.discord_id = int(row['player_id'].values[0]), int(row['discord_id'].values[0])
        temp.player_username = str(row["player_username"].values[0])
        temp.player_level, temp.player_exp = int(row['player_level'].values[0]), int(row['player_exp'].values[0])
        temp_string = str(row['quest_tokens'].values[0])
        temp.player_echelon, temp.player_quest = int(row['player_echelon'].values[0]), int(row['player_quest'].values[0])
        temp.player_stamina, temp.player_coins = int(row['player_stamina'].values[0]), int(row['player_coins'].values[0])
        temp.player_class = str(row['player_class'].values[0])
        temp.vouch_points = int(row['vouch_points'].values[0])
    string_list = temp_string.split(';')
    temp.quest_tokens = list(map(int, string_list))
    await temp.get_equipped()
    await temp.get_player_multipliers()
    if reloading is not None:
        reloading.__dict__.update(temp.__dict__)
    return temp


async def get_players_by_echelon(player_echelon):
    user_list = []
    raw_query = "SELECT * FROM PlayerList WHERE player_echelon = :echelon_check"
    player_df = await rqy(raw_query, return_value=True, params={'echelon_check': player_echelon})
    if len(player_df.index) == 0:
        return None
    for index, row in player_df.iterrows():
        user_list.append(await df_to_player(row))
    return user_list


async def get_all_users():
    user_list = []
    raw_query = "SELECT * FROM PlayerList"
    df = await rqy(raw_query, return_value=True)
    if df is None or len(df.index) == 0:
        return None
    for index, row in df.iterrows():
        user_list.append(await df_to_player(row))
    return user_list


def get_max_exp(player_level):
    return int(1000 * player_level) if player_level < 100 else 100000 + (50000 * (player_level // 100))


def show_num(input_number, adjust=100):
    return int(round(input_number * adjust))


def apply_singularity(data_list, bonus):
    highest_index = data_list.index(max(data_list))
    data_list[highest_index] += bonus
