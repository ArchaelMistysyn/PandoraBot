import discord
from discord.ext import commands
import csv
import random
import pandas as pd
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

import globalitems
import sharedmethods
import player
import bosses
import os
import combat
import mydb

fortress_data = pd.read_csv("fortressname.csv")


# Boss class
class CurrentBoss:
    def __init__(self, boss_type_num, boss_type, boss_tier, boss_level):
        self.player_id = 0
        self.boss_type, self.boss_type_num = boss_type, boss_type_num
        self.boss_tier, self.boss_level = boss_tier, boss_level
        self.boss_name, self.boss_image = "", ""
        self.boss_cHP, self.boss_mHP = 0, 0
        self.boss_typeweak = [0, 0, 0, 0, 0, 0, 0]
        self.boss_eleweak = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.curse_debuffs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.aura = 0.0
        self.boss_element, self.damage_cap = 0, -1

    def reset_modifiers(self):
        self.curse_debuffs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.aura = 0.0

    def calculate_hp(self) -> bool:
        return self.boss_cHP > 0

    def create_boss_embed(self, dps=0):
        # img_link = self.boss_image
        img_link = "https://i.ibb.co/0ngNM7h/castle.png"
        tier_colour_dict = {
            1: [0x43B581, "💚"], 2: [0x3498DB, "💙"], 3: [0x9B59B6, "💜"], 4: [0xF1C40F, "💛"],
            5: [0xCC0000, "❤️"], 6: [0xE91E63, "🩷"],  7: [0xFFFFFF, "🖤"], 8: [0x000000, "🤍"]
        }
        tier_info = tier_colour_dict[self.boss_tier]
        tier_colour = tier_info[0]
        life_emoji = tier_info[1]
        # Set boss details
        dps_msg = f"{sharedmethods.number_conversion(dps)} / min"
        boss_title = f'{self.boss_name}'
        boss_field = f'Tier {self.boss_tier} {self.boss_type} - Level {self.boss_level}'
        # Set boss hp
        if not self.calculate_hp():
            self.boss_cHP = 0
        hp_bar_icons = combat.hp_bar_dict[self.boss_tier]
        boss_hp = f'{life_emoji} ({sharedmethods.display_hp(int(self.boss_cHP), int(self.boss_mHP))})'
        bar_length = 0
        if int(self.boss_cHP) >= 1:
            bar_percentage = (int(self.boss_cHP) / int(self.boss_mHP)) * 100
            hp_threshhold = 100 / 15
            bar_length = int(bar_percentage / hp_threshhold)
        filled_segments = hp_bar_icons[0][:bar_length]
        empty_segments = hp_bar_icons[1][bar_length:]
        hp_bar_string = ''.join(filled_segments + empty_segments)
        boss_hp += f'\n{hp_bar_string}'
        # Set boss weakness
        boss_weakness = f'Weakness: '
        for idx, x in enumerate(self.boss_typeweak):
            if x == 1:
                boss_weakness += globalitems.class_icon_list[idx]
        for idy, y in enumerate(self.boss_eleweak):
            if y == 1:
                boss_weakness += globalitems.global_element_list[idy]
        embed_msg = discord.Embed(colour=tier_colour, title=boss_title, description="")
        embed_msg.set_image(url=img_link)
        embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
        embed_msg.add_field(name=boss_weakness, value="", inline=False)
        embed_msg.add_field(name="Current DPS: ", value=dps_msg, inline=False)
        return embed_msg

    def generate_boss_name_image(self, boss_type, boss_tier):
        # Fortress names
        fortress_list_t1 = [("Ominous Keep", ""), ("Twisted Stronghold", "")]
        fortress_list_t2 = [("Malignant Fortress", ""), ("Malevolant Castle", "")]
        fortress_list_t3 = [("Sinful Spire", ""), ("Malefic Citadel", "")]
        fortress_list_t4 = [("XVI - Aurora, The Fortress", "")]
        fortress_names = [fortress_list_t1, fortress_list_t2, fortress_list_t3, fortress_list_t4]

        # Dragon names
        dragon_list_t1 = [("Zelphyros, Wind", ""), ("Sahjvadiir, Earth", "")]
        dragon_list_t2 = [("Arkadrya, Lightning", ""), ("Phyyratha, Fire", ""), ("Elyssrya, Water", "")]
        dragon_list_t3 = [("Y'thana, Light", ""), ("Rahk'vath, Shadow", "")]
        dragon_list_t4 = [("VII - Astratha, The Dimensional", "")]
        dragon_names = [dragon_list_t1, dragon_list_t2, dragon_list_t3, dragon_list_t4]

        # Demon names
        demon_list_t1 = [("Beelzebub", ""), ("Azazel", ""), ("Astaroth", ""), ("Belial", "")]
        demon_list_t2 = [("Abbadon", ""), ("Asura", ""), ("Baphomet", ""), ("Charybdis", "")]
        demon_list_t3 = [("Iblis", ""), ("Lilith", ""), ("Ifrit", ""), ("Scylla", "")]
        demon_list_t4 = [("VIII - Tyra, The Behemoth", "")]
        demon_names = [demon_list_t1, demon_list_t2, demon_list_t3, demon_list_t4]

        # Paragon names
        paragon_list_t1 = [("0 - Karma, The Reflection", ""), ("I - Runa, The Magic", ""), ("VI - Kama, The Love", ""),
                           ("IX - Alaya, The Memory", ""), ("XIV - Arcelia, The Clarity", "")]
        paragon_list_t2 = [("XVII - Nova, The Star", ""), ("XVIII - Luna, The Moon", ""), ("XIX - Luma, The Sun", ""),
                           ("XX - Aria, The Reqiuem", ""), ("XXI - Ultima, The Creation", "")]
        paragon_list_t3 = [("V - Arkaya, The Duality", ""), ("X - Chrona, The Temporal", ""),
                           ("XI - Nua, The Heavens", ""),
                           ("XII - Rua, The Abyss", ""), ("XIII - Thana, The Death", "")]
        paragon_list_t4 = [("II - Pandora, The Celestial", ""), ("XV - Diabla, The Primordial", "")]
        paragon_list_t5 = [("III - Oblivia, The Void", ""), ("IV - Akasha, The Infinite", "")]
        paragon_list_t6 = [("XXV - Eleuia, The Wish", "")]
        paragon_names = [paragon_list_t1, paragon_list_t2, paragon_list_t3, paragon_list_t4, paragon_list_t5,
                         paragon_list_t6]

        # Arbiter names
        arbiter_list_t1 = [("XXII - Mysmir, Changeling of the True Laws", "")]
        arbiter_list_t2 = [("XXIII - Avalon, Pathwalker of the True Laws", "")]
        arbiter_list_t3 = [("XXIV - Isolde, Soulweaver of the True Laws", "")]
        arbiter_list_t4 = [("XXVI - Vexia, Scribe of the True Laws", "")]
        arbiter_list_t5 = [("XXVII - Kazyth, Lifeblood of the True Laws", "")]
        arbiter_list_t6 = [("XXVIII - Fleur, Oracle of the True Laws", "")]
        arbiter_list_t7 = [("XXIX - Yubelle, Adjudicator of the True Laws", "")]
        arbiter_names = [arbiter_list_t1, arbiter_list_t2, arbiter_list_t3, arbiter_list_t4, arbiter_list_t5,
                         arbiter_list_t6, arbiter_list_t7]

        # Incarnate names
        incarnate_names = [[("XXX - Amaryllis, Incarnate of the Divine Lotus", "")]]

        # All names
        all_names_dict = {"Fortress": fortress_names, "Dragon": dragon_names, "Demon": demon_names,
                          "Paragon": paragon_names, "Arbiter": arbiter_names, "Incarnate": incarnate_names}

        # Assign a random boss default values.
        target_list = all_names_dict[boss_type][(boss_tier - 1)]
        self.boss_name, self.boss_image = random.choice(target_list)
        if self.boss_image == "":
            self.boss_image = f'https://kyleportfolio.ca/botimages/bosses/{boss_type}{boss_tier}.png'
        self.boss_element = 9

        # Handle boss type exceptions.
        match boss_type:
            case "Fortress":
                if boss_tier != 4:
                    boss_prefix, self.boss_element = get_boss_descriptor(boss_type)
                    self.boss_name = boss_prefix + "the " + self.boss_name
            case "Dragon":
                temp_name_split = self.boss_name.split()
                boss_element = temp_name_split[1]
                if boss_tier != 4:
                    self.boss_element = globalitems.element_names.index(boss_element)
                    self.boss_name += " Dragon"
                else:
                    self.boss_element = 8
            case "Demon":
                if boss_tier != 4:
                    boss_colour, self.boss_element = get_boss_descriptor(boss_type)
                    self.boss_name = f'{boss_colour} {self.boss_name}'
                    self.boss_image = f'https://kyleportfolio.ca/botimages/bosses/{boss_type}{boss_colour}{boss_tier}.png'
            case _:
                pass


def get_raid_boss_details(channel_num):
    random_boss_type = random.randint(0, channel_num)
    selected_boss_type = globalitems.boss_list[random_boss_type]
    boss_tier, selected_boss_type = get_random_bosstier(selected_boss_type)
    level = 500
    if boss_tier < 5 and selected_boss_type not in ["Arbiter", "Incarnate"]:
        channel_level_dict = {1: 40, 2: 60, 3: 80, 4: 199}
        level = channel_level_dict[channel_num]
        if channel_num < 4:
            level += + random.randint(1, 9)
    return level, selected_boss_type, boss_tier


def restore_solo_bosses(channel_id):
    raid_id_df = get_raid_id(channel_id, -1, return_multiple=True)
    restore_raid_list = []
    pandora_db = mydb.start_engine()
    if len(raid_id_df.index) == 0:
        pandora_db.close_engine()
        return restore_raid_list
    for index, row in raid_id_df.iterrows():
        raw_query = "SELECT * FROM BossList WHERE raid_id = :id_check"
        df = pandora_db.run_query(raw_query, return_value=True, params={'id_check': int(row["raid_id"])})
        boss_tier, boss_level = int(df["boss_tier"].values[0]), int(df["boss_level"].values[0])
        boss_type, boss_type_num = str(df["boss_type"].values[0]), int(df["boss_type_num"].values[0])
        boss_object = CurrentBoss(boss_type_num, boss_type, boss_tier, boss_level)
        boss_object.player_id, boss_object.boss_name = int(df["player_id"].values[0]), str(df["boss_name"].values[0])
        boss_object.boss_cHP, boss_object.boss_mHP = int(df["boss_cHP"].values[0]), int(df["boss_mHP"].values[0])
        temp_t, temp_e = list(df['boss_typeweak'].values[0].split(';')), list(df['boss_eleweak'].values[0].split(';'))
        boss_object.boss_typeweak, boss_object.boss_eleweak = list(map(int, temp_t)), list(map(int, temp_e))
        boss_object.boss_image = str(df["boss_image"].values[0])
        restore_raid_list.append(boss_object)
    pandora_db.close_engine()
    return restore_raid_list


def spawn_boss(channel_id, player_id, new_boss_tier, selected_boss_type, boss_level, channel_num, gauntlet=False):
    raid_id = get_raid_id(channel_id, player_id)
    pandora_db = mydb.start_engine()
    # Handle existing boss.
    if raid_id != 0:
        raw_query = "SELECT * FROM BossList WHERE raid_id = :id_check"
        df = pandora_db.run_query(raw_query, return_value=True, params={'id_check': raid_id})
        player_id = int(df["player_id"].values[0])
        boss_tier, boss_level = int(df["boss_tier"].values[0]), int(df["boss_level"].values[0])
        boss_type, boss_type_num = str(df["boss_type"].values[0]), int(df["boss_type_num"].values[0])
        boss_object = CurrentBoss(boss_type_num, boss_type, boss_tier, boss_level)
        boss_object.boss_name = str(df["boss_name"].values[0])
        boss_object.boss_cHP, boss_object.boss_mHP = int(df["boss_cHP"].values[0]), int(df["boss_mHP"].values[0])
        temp_t, temp_e = list(df['boss_typeweak'].values[0].split(';')), list(df['boss_eleweak'].values[0].split(';'))
        boss_object.boss_typeweak, boss_object.boss_eleweak = list(map(int, temp_t)), list(map(int, temp_e))
        boss_object.boss_image = str(df["boss_image"].values[0])
        pandora_db.close_engine()
        # Set the damage cap.
        boss_object.damage_cap = -1
        if boss_object.boss_tier <= 4:
            boss_object.damage_cap = (10 ** int(boss_level / 10 + 4) - 1)
        return boss_object

    # Create the boss object if it doesn't exist.
    boss_type_num = globalitems.boss_list.index(selected_boss_type)

    # Handle boss level exceptions:
    if selected_boss_type == "Paragon" and new_boss_tier == 6:
        boss_level = 200
    elif selected_boss_type == "Arbiter":
        boss_level = 300 if new_boss_tier != 7 else 500
    elif boss_level == 900:
        boss_level = 999
    boss_object = CurrentBoss(boss_type_num, selected_boss_type, new_boss_tier, boss_level)

    # Assign elemental weaknesses.
    num_eleweak = 3
    eleweak_list = random.sample(range(9), num_eleweak)
    for x in eleweak_list:
        boss_object.boss_eleweak[x] = 1
    boss_eleweak = ";".join(str(y) for y in boss_object.boss_eleweak)
    boss_eleweak = boss_eleweak.rstrip(';')

    # Assign type weaknesses.
    num_typeweak = 2
    typeweak_list = random.sample(range(7), num_typeweak)
    for x in typeweak_list:
        boss_object.boss_typeweak[x] = 1
    boss_typeweak = ";".join(str(y) for y in boss_object.boss_typeweak)
    boss_typeweak = boss_typeweak.rstrip(';')

    # Set boss hp and damage cap.
    level_check = (min(boss_level, 100))
    subtotal_hp = 10 ** (level_check // 10 + 5)
    total_hp = int(subtotal_hp)
    if gauntlet:
        total_hp *= 10
    boss_object.damage_cap = (10 ** int(level_check / 10 + 4) - 1)
    # Eleuia Magnitude 1 HP
    if new_boss_tier == 6 and boss_object.boss_type != "Arbiter":
        total_hp *= 10
    # Arbiter magnitude 3 HP
    elif boss_object.boss_type == "Arbiter":
        total_hp *= 1000
        # Yubelle magnitude 4 HP
        if new_boss_tier == 7:
            total_hp *= 10
    boss_object.damage_cap = (10 ** int(level_check / 10 + 4) - 1)
    # Incarnate Magnitude 6/9/12 HP
    if boss_object.boss_type == "Incarnate":
        total_hp *= 1000000
        incarnate_hp_dict = {700: 1000000, 800: 1000000000, 999: 1000000000000}
        total_hp *= incarnate_hp_dict[boss_level]
        boss_object.damage_cap = -1

    # Increase raid boss hp and damage cap.
    if channel_num != 0:
        raid_hp_dict = {1: 100, 2: 10000, 3: 1000000, 4: 100000000}
        total_hp *= raid_hp_dict[channel_num]

    # Assign remaining boss details.
    boss_object.generate_boss_name_image(boss_object.boss_type, boss_object.boss_tier)
    boss_object.boss_mHP = total_hp
    boss_object.boss_cHP = boss_object.boss_mHP

    # Apply the new boss to the database.
    raw_query = "INSERT INTO ActiveRaids (channel_id, player_id) VALUES (:input_1, :player_id)"
    pandora_db.run_query(raw_query, params={'input_1': str(channel_id), 'player_id': player_id})
    raid_id = get_raid_id(channel_id, player_id)
    raw_query = ("INSERT INTO BossList "
                 "(raid_id, player_id, boss_name, boss_tier, boss_level, boss_type_num, boss_type, "
                 "boss_cHP, boss_mHP, boss_typeweak, boss_eleweak, boss_image) "
                 "VALUES (:raid_id, :player_id, :input_1, :input_2, :input_3, :input_4, :input_5, "
                 ":input_6, :input_7, :input_8, :input_9, :input_10)")
    params = {'raid_id': raid_id, 'player_id': player_id, 'input_1': boss_object.boss_name, 'input_2': new_boss_tier,
              'input_3': boss_level, 'input_4': boss_type_num, 'input_5': selected_boss_type,
              'input_6': str(int(total_hp)), 'input_7': str(int(total_hp)), 'input_8': boss_typeweak,
              'input_9': boss_eleweak, 'input_10': boss_object.boss_image}
    pandora_db.run_query(raw_query, params=params)
    pandora_db.close_engine()
    return boss_object


def get_random_bosstier(boss_type):
    # Assign tier rates.
    tier_breakpoint_list = {3: 6, 10: 5, 20: 4, 40: 3, 65: 2, 100: 1}
    if boss_type != "Arbiter":
        tier_breakpoint_list = {10: 4, 35: 3, 65: 2, 100: 1}
    # Determine the tier.
    random_number = random.randint(1, 100)
    for rate_breakpoint, tier_value in tier_breakpoint_list.items():
        if random_number <= rate_breakpoint:
            boss_tier = tier_value
            break
    # Handle non-paragon exceptions for pseudo-paragon type bosses.
    if boss_tier == 4 and boss_type == "Paragon":
        paragon_exceptions = [0, 1, 2, 3, 3]
        boss_type = globalitems.boss_list[random.choice(paragon_exceptions)]
    return boss_tier, boss_type


# generate ele weakness
def get_element(chosen_weakness):
    random_number = chosen_weakness if chosen_weakness == 0 else random.randint(0, 8)
    element_temp = globalitems.global_element_list[random_number]
    return element_temp


def get_boss_descriptor(boss_type):
    match boss_type:
        case "Fortress":
            boss_info = random.choice(fortress_data.fortress_name_a).split(";")
            boss_descriptor, boss_element = str(boss_info[0]), int(boss_info[1])
            boss_descriptor += f" {str(random.choice(fortress_data.fortress_name_b))}, "
        case "Demon":
            demon_colours = ["Crimson", "Azure", "Violet", "Bronze", "Jade", "Ivory", "Stygian", "Gold", "Rose"]
            boss_element = random.randint(0, 8)
            boss_descriptor = demon_colours[boss_element]
    return boss_descriptor, boss_element


def add_participating_player(channel_id, player_id):
    raid_id = get_raid_id(channel_id, 0)
    pandora_db = mydb.start_engine()
    # Check if player is already part of the raid
    raw_query = "SELECT * FROM RaidPlayers WHERE raid_id = :id_check AND player_id = :player_check"
    df_check = pandora_db.run_query(raw_query, True, params={'id_check': raid_id, 'player_check': player_id})
    if len(df_check.index) != 0:
        pandora_db.close_engine()
        return " is already in the raid."
    # Add player to the raid
    raw_query = "INSERT INTO RaidPlayers (raid_id, player_id, player_dps) VALUES(:raid_id, :player_id, :player_dps)"
    pandora_db.run_query(raw_query, params={'raid_id': raid_id, 'player_id': player_id, 'player_dps': 0})
    pandora_db.close_engine()
    return " joined the raid"


def update_player_damage(channel_id, player_id, player_damage):
    raid_id = get_raid_id(channel_id, 0)
    pandora_db = mydb.start_engine()
    raw_query = "UPDATE RaidPlayers SET player_dps = :new_dps WHERE raid_id = :id_check AND player_id = :player_check"
    pandora_db.run_query(raw_query, params={'new_dps': player_damage, 'id_check': raid_id, 'player_check': player_id})
    pandora_db.close_engine()


def update_boss_cHP(channel_id, player_id, new_boss_cHP):
    raid_id = get_raid_id(channel_id, player_id)
    pandora_db = mydb.start_engine()
    raw_query = "UPDATE BossList SET boss_cHP = :new_cHP WHERE raid_id = :id_check"
    pandora_db.run_query(raw_query, params={'new_cHP': str(int(new_boss_cHP)), 'id_check': raid_id})
    pandora_db.close_engine()


def get_damage_list(channel_id):
    raid_id = get_raid_id(channel_id, 0)
    pandora_db = mydb.start_engine()
    raw_query = "SELECT player_id, player_dps FROM RaidPlayers WHERE raid_id = :id_check"
    df = pandora_db.run_query(raw_query, True, params={'id_check': raid_id})
    pandora_db.close_engine()
    username = df["player_id"].values.tolist()
    damage = df["player_dps"].values.tolist()
    return username, damage


def clear_boss_info(channel_id, player_id):
    raid_id = get_raid_id(channel_id, player_id)
    pandora_db = mydb.start_engine()
    raw_queries = [
        "DELETE FROM ActiveRaids WHERE raid_id = :id_check",
        "DELETE FROM BossList WHERE raid_id = :id_check",
        "DELETE FROM RaidPlayers WHERE raid_id = :id_check"
    ]
    for query in raw_queries:
        pandora_db.run_query(query, params={'id_check': raid_id})
    pandora_db.close_engine()


def get_raid_id(channel_id, player_id, return_multiple=False):
    pandora_db = mydb.start_engine()
    if player_id == -1:
        raw_query = "SELECT raid_id FROM ActiveRaids WHERE channel_id = :id_check"
        params = {'id_check': str(channel_id)}
    else:
        raw_query = "SELECT raid_id FROM ActiveRaids WHERE channel_id = :id_check AND player_id = :player_check"
        params = {'id_check': str(channel_id), 'player_check': player_id}
    df_check = pandora_db.run_query(raw_query, return_value=True, params=params)
    pandora_db.close_engine()
    if return_multiple:
        return df_check
    if len(df_check) == 0:
        return 0
    return int(df_check['raid_id'].values[0])


def create_dead_boss_embed(channel_id, active_boss, dps):
    active_boss.boss_cHP = 0
    dead_embed = active_boss.create_boss_embed(dps)
    player_list, damage_list = bosses.get_damage_list(channel_id)
    output_list = ""
    for idx, x in enumerate(player_list):
        player_obj = player.get_player_by_id(x)
        output_list += f'{str(player_obj.player_username)}: {sharedmethods.number_conversion(int(damage_list[idx]))}\n'
    dead_embed.add_field(name="SLAIN", value=output_list, inline=False)
    return dead_embed
