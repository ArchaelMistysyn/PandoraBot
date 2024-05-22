# General imports
import pandas as pd
import discord
import random
from datetime import datetime as dt, timedelta

import math

# Data imports
import globalitems as gli
import sharedmethods as sm
from pandoradb import run_query as rq

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


class PlayerProfile:
    def __init__(self):

        # Initialize player base info.
        self.player_id, self.discord_id, self.player_username = 0, 0, ""
        self.player_exp, self.player_level, self.player_echelon = 0, 0, 0
        self.player_class = ""
        self.player_quest, self.quest_tokens = 0, [0 for x in range(30)]
        self.quest_tokens[1] = 1
        self.player_coins, self.player_stamina, self.vouch_points = 0, 0, 0
        self.luck_bonus = 0

        # Initialize player gear/stats info.
        self.player_stats, self.gear_points = [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]
        self.player_equipped = [0, 0, 0, 0, 0, 0, 0]
        self.pact, self.insignia, self.equipped_tarot = "", "", ""

        # Initialize player health stats.
        self.player_mHP, self.player_cHP = 1000, 1000
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
        self.singularity_damage, self.singularity_penetration, self.singularity_curse = 0.0, 0.0, 0.0
        self.aura = 0.0

        # Initialize class specialization stats.
        self.unique_glyph_ability = [False, False, False, False, False, False, False]
        self.temporal_app = 0
        self.elemental_capacity, self.elemental_app = 3, 0
        self.bleed_mult, self.bleed_penetration, self.bleed_app = 0.0, 0.0, 0
        self.combo_mult, self.combo_penetration, self.combo_application = 0.05, 0.0, 0
        self.ultimate_mult, self.ultimate_penetration, self.ultimate_app = 0.0, 0.0, 0
        self.perfect_crit, self.critical_chance, self.critical_multiplier = 0, 0.0, 1.0
        self.critical_penetration, self.critical_app = 0.0, 0

        # Initialize misc stats.
        self.charge_generation = 1
        self.banes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.skill_damage_bonus = [0, 0, 0, 0]
        self.spec_rate, self.spec_conv = [0.0, 0.0, 0.0, 0.0, 0.0], [0, 0, 0, 0]
        self.bloom_multiplier = 10.0
        self.unique_conversion = [0.0, 0.0, 0.0, 0.0]
        self.attack_speed = 0.0
        self.bonus_hits = 0.0
        self.defence_penetration = 0.0
        self.class_multiplier = 0.0
        self.final_damage = 0.0
        self.rng_bonus = 0
        self.aqua_mode, self.aqua_points, self.aqua_app = 0, 0, 0

        # Initialize defensive stats.
        self.hp_bonus, self.hp_regen, self.hp_multiplier = 0.0, 0.0, 0.0
        self.recovery = 3
        self.block, self.dodge = 0, 0
        self.damage_mitigation, self.mitigation_bonus = 0.0, 0.0
        self.elemental_resistance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.all_elemental_resistance = 0.1

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
            if method == 1:
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
                temp_icon = gli.global_element_list[z]
                temp_dmg_str = f"(Dmg: {int(round(self.elemental_multiplier[z] * 100)):,}%)"
                temp_pen_str = f"(Pen: {int(round(self.elemental_penetration[z] * 100)):,}%)"
                temp_curse_str = f"(Curse: {int(round(self.elemental_curse[z] * 100)):,}%)"
                if method == 1:
                    stats += f"\n{temp_icon} Total Damage: {int(round(total_multi)):,}%"
                if method == 2:
                    stats += f"\n{temp_icon} {temp_dmg_str} - {temp_pen_str} - {temp_curse_str}"
            if method == 1:
                embed_msg.add_field(name=title_msg, value=stats, inline=False)
                # Construct the damage spread field.
                if self.player_equipped[0] != 0:
                    title_msg, stats = "Damage Spread", ""
                    e_weapon = await inventory.read_custom_item(self.player_equipped[0])
                    used_elements, used_multipliers = [], []
                    temp_element_list = combat.limit_elements(self, e_weapon)
                    # Build the list of used elements/multipliers.
                    for i, is_used in enumerate(temp_element_list):
                        if is_used:
                            used_elements.append(gli.global_element_list[i])
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
                        extension = "%" if tag not in ["App", "Cap"] else ""
                        section_string += f"({tag}: {value}{extension})"
                        if (tag_index + 1) < len(tag_list):
                            section_string += " - "
                    return f"{section_string}"

                title_msg = "Elemental Breakdown"
                embed_msg.add_field(name=title_msg, value=stats, inline=False)
                title_msg, stats = "Application Details", ""
                stats += set_section("Elemental Details", ["Cap", "App", "FRC"],
                                     [self.elemental_capacity, self.elemental_app,
                                     (self.elemental_app * 5 + show_num(self.spec_rate[3]))])
                stats += set_section("Critical Details", ["CRT", "Dmg", "Pen", "App", "OMG"],
                                     [show_num(self.critical_chance, 1), show_num(self.critical_multiplier),
                                     show_num(self.critical_penetration), show_num(self.critical_app),
                                     (self.critical_app * 10 + show_num(self.spec_rate[2]))])
                stats += set_section("Combo Details", ["Dmg", "Pen", "App"],
                                     [show_num(self.combo_mult), show_num(self.combo_penetration),
                                     self.combo_application])
                stats += set_section("Ultimate Details", ["Dmg", "Pen", "App"],
                                     [show_num(self.ultimate_mult), show_num(self.ultimate_penetration),
                                     self.ultimate_app])
                stats += set_section("Bleed Details", ["Dmg", "Pen", "App", "HPR"],
                                     [show_num(self.bleed_mult), show_num(self.bleed_penetration),
                                     self.bleed_app,
                                     (self.bleed_app * 10 + show_num(self.spec_rate[1]))])
                stats += set_section("Time Details", ["Dmg", "App", "LCK"],
                                     [((self.temporal_app + 1) * 100), self.temporal_app,
                                     (self.temporal_app * 5 + show_num(self.spec_rate[4]))])
                stats += set_section("Bloom Details", ["BLM", "Dmg"],
                                     [show_num(self.spec_rate[0]), show_num(self.bloom_multiplier)])
                embed_msg.add_field(name=title_msg, value=stats, inline=False)
                return embed_msg
        if method == 3:
            # Defensive display.
            title_msg = "Defensive Stats"
            stats = f"Player HP: {self.player_mHP:,}\nRecovery: {self.recovery}"
            for idy, y in enumerate(self.elemental_resistance):
                stats += f"\n{gli.global_element_list[idy]} Resistance: {show_num(y)}%"
            stats += f"\nDamage Mitigation: {show_num(self.damage_mitigation, 1)}%"
            stats += f"\nBlock Rate: {show_num(self.block, 1)}%"
            stats += f"\nDodge Rate: {show_num(self.dodge, 1)}%"
            embed_msg.add_field(name=title_msg, value=stats, inline=False)
            return embed_msg
        if method == 4:
            # Multiplier Display.
            title_msg = "Multipliers"
            for idh, h in enumerate(self.banes):
                stats += f"\n{gli.boss_list[idh]} Bane: {show_num(h)}%" if idh < 5 else f"\nHuman Bane: {show_num(h)}%"
            stats += f"\nClass Mastery: {show_num(self.class_multiplier)}%"
            stats += f"\nFinal Damage: {show_num(self.final_damage)}%"
            stats += f"\nDefence Penetration: {show_num(self.defence_penetration)}%"
            stats += f"\nOmni Aura: {show_num(self.aura)}%"
            embed_msg.add_field(name=title_msg, value=stats, inline=False)
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
            for path_index, path_type in enumerate(gli.path_names):
                total_points = self.player_stats[path_index] + self.gear_points[path_index]
                if total_points >= 20:
                    embed_msg = await skillpaths.display_glyph(path_type, total_points, embed_msg)
            return embed_msg

    def adjust_coins(self, coin_change, reduction=False, apply_pact=True):
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
        self.set_player_field("player_coins", self.player_coins)
        return f"{coin_change:,}x{adjust_msg}"

    def adjust_exp(self, exp_change, apply_pact=True):
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
        self.set_player_field("player_level", self.player_level)
        self.set_player_field("player_exp", self.player_exp)
        return change_message, level_increase

    def set_player_field(self, field_name, field_value):
        raw_query = f"UPDATE PlayerList SET {field_name} = :input_1 WHERE player_id = :player_check"
        rq(raw_query, params={'player_check': int(self.player_id), 'input_1': field_value})

    def unequip_item(self, item):
        self.player_equipped = [0 if element == item.item_id else element for element in self.player_equipped]
        equipped_gear = ";".join(map(str, self.player_equipped))
        self.set_player_field("player_equipped", equipped_gear)

    async def add_new_player(self, selected_class, discord_id):
        self.discord_id = discord_id
        self.player_class = selected_class
        self.player_quest, self.player_level = 1, 1
        self.player_stamina = 5000
        player_stats, equipped_gear = "0;0;0;0;0;0;0", "0;0;0;0;0;0;0"
        quest_tokens = ";".join(map(str, self.quest_tokens))
        raw_query = "SELECT * FROM PlayerList WHERE discord_id = :id_check"
        df = rq(raw_query, return_value=True, params={'id_check': self.discord_id})

        if len(df.index) != 0:
            return f"Player with discord ID: ({self.discord_id}) is already registered."
        raw_query = "SELECT * FROM PlayerList WHERE player_username = :username_check"
        df = rq(raw_query, return_value=True, params={'username_check': self.player_username})
        if len(df.index) != 0:
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
            'input_14': str(self.insignia), 'input_15': str(self.pact), 'input_16': int(self.vouch_points)
        }
        rq(raw_query, params=params)
        registered_player = await get_player_by_discord(self.discord_id)
        raw_query = "INSERT INTO MiscPlayerData (player_id, thana_visits, deaths) VALUES (:input_1, :input_2, :input_3)"
        params = {"input_1": registered_player.player_id, "input_2": 0, "input_3": 0}
        rq(raw_query, params=params)
        return f"Welcome {self.player_username}!\nUse /quest to begin."

    def update_misc_data(self, field_name, change, overwrite_value=False):
        raw_query = f"UPDATE MiscPlayerData SET {field_name} = {field_name} + :new_value WHERE player_id = :player_check"
        if overwrite_value:
            raw_query = f"UPDATE MiscPlayerData SET {field_name} = :new_value WHERE player_id = :player_check"
        params = {"new_value": change, "player_check": self.player_id}
        rq(raw_query, params=params)

    def check_misc_data(self, field_name):
        raw_query = f"SELECT {field_name} FROM MiscPlayerData WHERE player_id = :player_check"
        params = {"player_check": self.player_id}
        result_df = rq(raw_query, params=params, return_value=True)
        return result_df[field_name].values[0]

    def spend_stamina(self, cost) -> bool:
        is_spent = False
        if self.player_stamina >= cost:
            self.player_stamina -= cost
            self.set_player_field("player_stamina", self.player_stamina)
            is_spent = True
        return is_spent

    def get_equipped(self):
        raw_query = "SELECT * FROM PlayerList WHERE player_id = :player_check"
        df = rq(raw_query, return_value=True, params={'player_check': self.player_id})
        temp_equipped = list(df['player_equipped'].values[0].split(';'))
        self.player_equipped = list(map(int, temp_equipped))
        temp_stats = list(df['player_stats'].values[0].split(';'))
        self.player_stats = list(map(int, temp_stats))
        self.equipped_tarot = str(df['player_tarot'].values[0])
        self.insignia = str(df['player_insignia'].values[0])
        self.pact = str(df['player_pact'].values[0])

    def reset_skill_points(self):
        self.player_stats = [0, 0, 0, 0, 0, 0, 0]
        reset_points = "0;0;0;0;0;0;0"
        self.set_player_field("player_stats", reset_points)

    async def reload_player(self):
        _ = await get_player_by_id(self.player_id, reloading=self)

    async def get_player_multipliers(self):
        base_critical_chance, base_attack_speed, base_mitigation = 10.0, 1.0, 0.0
        base_player_hp = 1000 + 10 * self.player_level

        # Class Multipliers
        class_multipliers = {
            "Ranger": ["critical_app", 1], "Weaver": ["elemental_app", 2],
            "Assassin": ["bleed_app", 1], "Mage": ["temporal_app", 1],
            "Summoner": ["combo_application", 1], "Knight": ["ultimate_app", 1]
        }
        if self.player_class in class_multipliers:
            setattr(self, class_multipliers[self.player_class][0], class_multipliers[self.player_class][1])

        # Item Multipliers
        e_item = []
        for idx, x in enumerate(self.player_equipped):
            if x != 0:
                e_item.append(await inventory.read_custom_item(x))
                e_item[idx].update_damage()
                self.player_damage += random.randint(e_item[idx].item_damage_min, e_item[idx].item_damage_max)
                itemrolls.assign_roll_values(self, e_item[idx])
                itemrolls.assign_item_element_stats(self, e_item[idx])
                if e_item[idx].item_num_sockets == 1:
                    await itemrolls.assign_gem_values(self, e_item[idx])
            else:
                e_item.append(None)
        if e_item[0]:
            base_attack_speed *= float(e_item[0].item_base_stat)
            if self.player_class == "Rider":
                base_attack_speed *= 1.25
        if e_item[1]:
            base_mitigation = e_item[1].item_base_stat
        for y in range(1, 5):
            if e_item[y]:
                self.unique_ability_multipliers(e_item[y])

        # Non-Gear Item Multipliers
        insignia.assign_insignia_values(self)
        if self.equipped_tarot != "":
            e_tarot = tarot.check_tarot(self.player_id, tarot.card_dict[self.equipped_tarot][0])
            e_tarot.assign_tarot_values(self)

        # Assign Path Multipliers
        total_points = skillpaths.assign_path_multipliers(self)

        # Application Calculations
        base_critical_chance += self.critical_app
        self.critical_multiplier += self.critical_app
        self.skill_damage_bonus[3] += self.ultimate_app * 0.25
        self.charge_generation += self.ultimate_app
        self.all_elemental_multiplier += self.elemental_app * 0.25

        # Elemental Capacity
        self.elemental_capacity += max(0, self.elemental_app)

        # Pact Bonus Multipliers (Occurs after stat adjustments, but before stat hard limits)
        pact.assign_pact_values(self)

        # Capacity Hard Limits
        self.elemental_capacity = min(self.elemental_capacity, 9)
        # Solitude/Frostfire and Aqua exceptions
        self.elemental_capacity = 1 if total_points[6] >= 100 or self.aqua_mode != 0 else 3 if total_points[1] >= 80 else self.elemental_capacity

        # General Calculations
        self.critical_chance = (1 + self.critical_chance) * base_critical_chance
        self.critical_chance = 100.00 if self.perfect_crit > 0 or self.aqua_points >= 80 else self.critical_chance
        self.attack_speed = (1 + self.attack_speed) * base_attack_speed
        self.damage_mitigation = min((1 + (self.mitigation_bonus + self.damage_mitigation)) * base_mitigation, 90)
        self.player_cHP = self.player_mHP = int((base_player_hp + self.hp_bonus) * (1 + self.hp_multiplier))

        match_count = sum(1 for item in e_item if item is not None and item.item_damage_type == self.player_class)
        if self.unique_conversion[2] >= 1:
            unique_damage_types = {item.item_damage_type for item in e_item}
            match_count = len(unique_damage_types)
        self.class_multiplier += 0.05 + self.unique_conversion[2]
        self.class_multiplier *= match_count

        # Singularity multipliers
        apply_singularity(self.elemental_multiplier, self.singularity_damage)
        apply_singularity(self.elemental_penetration, self.singularity_penetration)
        apply_singularity(self.elemental_curse, self.singularity_curse)

        # Apply omni multipliers.
        for x in range(9):
            self.elemental_multiplier[x] += self.all_elemental_multiplier
            self.elemental_penetration[x] += self.all_elemental_penetration
            self.elemental_resistance[x] += self.all_elemental_resistance
            self.elemental_curse[x] += self.all_elemental_curse
            if self.elemental_resistance[x] >= 0.9:
                self.elemental_resistance[x] = 0.9
            # Apply unique resistance conversion.
            self.elemental_multiplier[x] += self.elemental_resistance[x] * self.unique_conversion[0]
        for y in range(6):
            self.banes[y] += self.banes[6]
        # Calculate unique conversions
        hp_reduction = self.player_mHP * self.unique_conversion[1]
        self.player_mHP = int(self.player_mHP - hp_reduction)
        self.final_damage += int(round(hp_reduction / 100)) / 100
        self.final_damage += self.unique_conversion[3]
        if self.aqua_mode != 0 and self.equipped_tarot != "" and e_tarot.card_numeral == "XIV":
            self.critical_multiplier += self.elemental_multiplier[1]

    def get_player_initial_damage(self):
        return self.player_damage * (1 + self.class_multiplier) * (1 + self.final_damage)

    async def get_player_boss_damage(self, boss_object):
        e_weapon = await inventory.read_custom_item(self.player_equipped[0])
        num_elements = sum(e_weapon.item_elements)
        player_damage = self.get_player_initial_damage()
        player_damage, critical_type = combat.critical_check(self, player_damage, num_elements)
        self.player_total_damage = self.boss_adjustments(player_damage, boss_object, e_weapon)
        return self.player_total_damage, critical_type

    def boss_adjustments(self, player_damage, boss_obj, e_weapon):
        # Boss type multipliers
        damage = player_damage * (1 + self.banes[boss_obj.boss_type_num - 1])
        # Type Defences
        defences_multiplier = (combat.boss_defences("", self, boss_obj, -1) + self.defence_penetration)
        damage *= defences_multiplier
        # Elemental Defences
        highest = 0
        for idx, x in enumerate(combat.limit_elements(self, e_weapon)):
            if x == 1:
                self.elemental_damage[idx] = damage * (1 + self.elemental_multiplier[idx])
                resist_multi = combat.boss_defences("Element", self, boss_obj, idx)
                penetration_multi = 1 + self.elemental_penetration[idx]
                self.elemental_damage[idx] *= resist_multi * penetration_multi * self.elemental_conversion[idx]
                if self.elemental_damage[idx] > self.elemental_damage[highest]:
                    highest = idx
        damage = sum(self.elemental_damage) * (1 + boss_obj.aura) * combat.boss_true_mitigation(boss_obj.boss_level)
        # Apply status
        stun_status = gli.element_status_list[highest]
        if stun_status is not None and random.randint(1, 100) <= 1:
            boss_obj.stun_status = stun_status
            boss_obj.stun_cycles += 1
        return int(damage)

    async def get_bleed_damage(self, boss_obj):
        weapon = await inventory.read_custom_item(self.player_equipped[0])
        player_damage = self.get_player_initial_damage()
        self.player_total_damage = self.boss_adjustments(player_damage, boss_obj, weapon) * (1 + self.bleed_mult)
        return self.player_total_damage

    def equip(self, selected_item):
        if selected_item.item_type not in ["W", "A", "V", "Y", "R", "G", "C"]:
            return "Item is not equipable."
        # Equip the item and update the database.
        location = inventory.item_loc_dict[selected_item.item_type]
        item_type = inventory.item_type_dict[location]
        self.player_equipped[location] = selected_item.item_id
        equipped_gear = ";".join(map(str, self.player_equipped))
        raw_query = f"UPDATE PlayerList SET player_equipped = :input_1 WHERE player_id = :player_check"
        rq(raw_query, params={'player_check': int(self.player_id), 'input_1': equipped_gear})
        return f"{item_type} {selected_item.item_id} is now equipped."

    async def unequip(self, selected_item):
        # Unequip non-gem gear items
        if "D" not in selected_item.item_type:
            location = inventory.item_loc_dict[selected_item.item_type]
            self.player_equipped[location] = 0
            equipped_gear = ";".join(map(str, self.player_equipped))
            raw_query = f"UPDATE PlayerList SET player_equipped = :input_1 WHERE player_id = :player_check"
            rq(raw_query, params={'player_check': int(self.player_id), 'input_1': equipped_gear})
            return
        # Remove inlaid dragon gems
        for item_id in [x for x in self.player_equipped if x != 0]:
            e_item = await inventory.read_custom_item(item_id)
            if selected_item.item_id == e_item.item_inlaid_gem_id:
                e_item.item_inlaid_gem_id = 0
                await e_item.update_stored_item()

    async def check_equipped(self, item):
        response = ""
        self.get_equipped()
        if item.item_type not in inventory.item_loc_dict and "D" not in item.item_type:
            return f"Item {item.item_id} is not recognized."
        if item.item_id in self.player_equipped:
            return f"Item {item.item_id} is equipped."
        elif "D" in item.item_type:
            for item_id in [x for x in self.player_equipped if x != 0]:
                e_item = await inventory.read_custom_item(item_id)
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
                self.elemental_multiplier[element_position] += 0.25
                return
            if item.item_type == "C":
                self.elemental_penetration[element_position] += 0.25
                return

    def check_cooldown(self, command_name):
        difference = None
        raw_query = "SELECT * FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check"
        params = {'player_check': self.player_id, 'cmd_check': command_name}
        df = rq(raw_query, return_value=True, params=params)
        method = ""
        if len(df) != 0:
            date_string = str(df["time_used"].values[0])
            previous = dt.strptime(date_string, gli.date_formatting)
            now = dt.now()
            difference = now - previous
            method = str(df["method"].values[0])
        return difference, method

    def set_cooldown(self, command_name, method, rewind_days=0):
        difference = None
        raw_query = "SELECT * FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check"
        params = {'player_check': self.player_id, 'cmd_check': command_name}
        df = rq(raw_query, return_value=True, params=params)
        raw_query = ("INSERT INTO CommandCooldowns (player_id, command_name, method, time_used) "
                     "VALUES (:player_check, :cmd_check, :method, :time_check)")
        if len(df) != 0:
            raw_query = ("UPDATE CommandCooldowns SET command_name = :cmd_check, time_used =:time_check "
                         "WHERE player_id = :player_check AND method = :method")
        timestamp = dt.now() - timedelta(days=rewind_days)
        current_time = timestamp.strftime(gli.date_formatting)
        params = {'player_check': self.player_id, 'cmd_check': command_name,
                  'method': method, 'time_check': current_time}
        rq(raw_query, params=params)
        return difference

    def clear_cooldown(self, command_name):
        raw_query = "DELETE FROM CommandCooldowns WHERE player_id = :player_check AND command_name = :cmd_check"
        rq(raw_query, params={'player_check': self.player_id, 'cmd_check': command_name})


def check_username(new_name: str):
    raw_query = "SELECT * FROM PlayerList WHERE player_username = :player_check"
    df = rq(raw_query, return_value=True, params={'player_check': new_name})
    return False if len(df) != 0 else True


async def get_player_by_id(player_id, reloading=None):
    raw_query = "SELECT * FROM PlayerList WHERE player_id = :id_check"
    df = rq(raw_query, return_value=True, params={'id_check': player_id})
    return None if len(df.index) == 0 else await df_to_player(df, reloading=reloading)


async def get_player_by_discord(discord_id, reloading=None):
    raw_query = "SELECT * FROM PlayerList WHERE discord_id = :id_check"
    df = rq(raw_query, return_value=True, params={'id_check': discord_id})
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
    temp.get_equipped()
    await temp.get_player_multipliers()
    if reloading is not None:
        reloading.__dict__.update(temp.__dict__)
    return temp


async def get_players_by_echelon(player_echelon):
    user_list = []
    raw_query = "SELECT * FROM PlayerList WHERE player_echelon = :echelon_check"
    player_df = rq(raw_query, return_value=True, params={'echelon_check': player_echelon})
    if len(player_df.index) == 0:
        return None
    for index, row in player_df.iterrows():
        user_list.append(await df_to_player(row))
    return user_list


async def get_all_users():
    user_list = []
    raw_query = "SELECT * FROM PlayerList"
    df = rq(raw_query, return_value=True)
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
