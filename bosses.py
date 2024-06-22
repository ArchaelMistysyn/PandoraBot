# General imports
import discord
import random
from datetime import datetime as dt
from zoneinfo import ZoneInfo

# Data imports
import globalitems as gli
import sharedmethods as sm
from tarot import card_dict, card_type_dict

# Core imports
import player
import encounters
from pandoradb import run_query as rqy

fortress_list_t1 = [("Ominous Keep", ""), ("Twisted Stronghold", "")]
fortress_list_t2 = [("Malignant Fortress", ""), ("Malevolant Castle", "")]
fortress_list_t3 = [("Sinful Spire", ""), ("Malefic Citadel", "")]
fortress_list_t4 = [("XVI - Aurora, The Fortress", "")]
fortress_names = [fortress_list_t1, fortress_list_t2, fortress_list_t3, fortress_list_t4]
fortress_types = ['Nirvana', 'Paradise', 'Arcadia', 'Eden', 'Dream',
                  'Elysium', 'Sanctuary', 'Domain', 'Oblivion', 'Cradle']
fortress_variants = [['Devouring', 0], ['Vengeful', 0], ['Blighted', 1], ['Plagued', 1],
                     ['Writhing', 2], ['Agony', 2], ['Overgrown', 3], ['Man-Eating', 3],
                     ['Shrieking', 4], ['Howling', 4]]
dragon_list_t1 = ["Zelphyros, Wind", "Sahjvadiir, Earth", "Cyries'vael, Ice"]
dragon_list_t2 = ["Arkadrya, Lightning", "Phyyratha, Fire", "Elyssrya, Water"]
dragon_list_t3 = ["Y'thana, Light", "Rahk'vath, Shadow"]
dragon_list_t4 = ["VII - Astratha, The Dimensional"]
dragon_names = [dragon_list_t1, dragon_list_t2, dragon_list_t3, dragon_list_t4]
demon_list_t1 = ["Beelzebub", "Azazel", "Astaroth", "Belial"]
demon_list_t2 = ["Abbadon", "Asura", "Baphomet", "Charybdis"]
demon_list_t3 = ["Iblis", "Lilith", "Ifrit", "Scylla"]
demon_list_t4 = ["VIII - Tyra, The Behemoth"]
demon_names = [demon_list_t1, demon_list_t2, demon_list_t3, demon_list_t4]
demon_colours = ["Crimson", "Azure", "Violet", "Bronze", "Jade", "Ivory", "Stygian", "Gold", "Rose"]
paragon_names, arbiter_names, incarnate_names = [[] for _ in range(6)], [[] for _ in range(7)], [[] for _ in range(8)]
for numeral, (name, tier) in card_dict.items():
    card_type = card_type_dict.get(numeral)
    if card_type == "Paragon":
        paragon_names[tier - 1].append(f"{numeral} - {name}")
    elif card_type == "Arbiter":
        arbiter_names[tier - 1].append(f"{numeral} - {name}")
    elif card_type == "Incarnate":
        incarnate_names[tier - 1].append(f"{numeral} - {name}")
all_names_dict = {"Fortress": fortress_names, "Dragon": dragon_names, "Demon": demon_names,
                  "Paragon": paragon_names, "Arbiter": arbiter_names, "Incarnate": incarnate_names}
raid_bosses = {0: "Geb, Sacred Ruler of Sin", 1: "Tiamat, Sacred Ruler of Fury", 2: "Veritas, Sacred Ruler of Prophecy",
               3: "Geb, Sacred Ruler of Sin", 4: "Tiamat, Sacred Ruler of Fury", 5: "Veritas, Sacred Ruler of Prophecy",
               6: "Alaric, Sacred Ruler of Totality"}


# Boss class
class CurrentBoss:
    def __init__(self):
        self.player_id = 0
        self.boss_type, self.boss_type_num = "", 0
        self.boss_tier, self.boss_level = 0, 0
        self.boss_name, self.boss_image = "", ""
        self.boss_cHP, self.boss_mHP = 0, 0
        self.boss_typeweak, self.boss_eleweak, self.curse_debuffs = [0] * 7, [0] * 9, [0.0] * 9
        self.boss_element, self.damage_cap = 0, -1
        self.stun_cycles, self.stun_status = 0, ""

    def create_boss_embed(self, dps=0, extension=""):
        img_link = "https://i.ibb.co/0ngNM7h/castle.png"
        if "Demon" in self.boss_image or "Dragon" in self.boss_image:
            img_link = self.boss_image
        tier_hearts = ["<:Gem1:1242206599481659442>", "<:Gem2:1242206600555532421>", "<:Gem3:1242206601385873498>",
                       "<:Gem4:1242206602405347459>", "<:Gem5:1242206603441078363>", "<:Gem6:1242206603953049721>",
                       "<:Gem7:1248490896379478129>", "<:Gem8:1242206660513108029>", "<:Gem8:1242206660513108029>"]
        # Set boss details
        dps_msg = f"{sm.number_conversion(dps)} / min"
        boss_title = f'{self.boss_name}{extension}'
        boss_field = f'Tier {self.boss_tier} {self.boss_type} - Level {self.boss_level}'
        # Set boss hp
        self.boss_cHP = max(0, self.boss_cHP)
        hp_bar_icons = gli.hp_bar_dict[min(8, self.boss_tier)]
        boss_hp = f'{tier_heart_dict[self.boss_tier -1]} ({sm.display_hp(int(self.boss_cHP), int(self.boss_mHP))})'
        bar_length = 0
        if int(self.boss_cHP) >= 1:
            bar_percentage = (int(self.boss_cHP) / int(self.boss_mHP)) * 100
            hp_threshhold = 100 / 15
            bar_length = int(bar_percentage / hp_threshhold)
        filled_segments, empty_segments = hp_bar_icons[0][:bar_length], hp_bar_icons[1][bar_length:]
        boss_hp += f"\n{''.join(filled_segments + empty_segments)}"
        # Set boss weakness
        type_weak = ''.join(gli.class_icon_list[idx] for idx, x in enumerate(self.boss_typeweak) if x == 1)
        ele_weak = ''.join(gli.ele_icon[idx] for idx, x in enumerate(self.boss_eleweak) if x == 1)
        boss_weakness = f'Weakness: {type_weak}{ele_weak}'
        embed_msg = sm.EasyEmbed(self.boss_tier, boss_title, "")
        embed_msg.set_image(url=img_link)
        embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
        embed_msg.add_field(name=boss_weakness, value="", inline=False)
        embed_msg.add_field(name="Current DPS: ", value=dps_msg, inline=False)
        return embed_msg

    def generate_boss_name_image(self, boss_type, boss_tier):
        if boss_type == "raid":
            self.boss_name = raid_bosses[dt.now(ZoneInfo('America/Toronto')).weekday()]
            return
        target_list = all_names_dict[boss_type][(boss_tier - 1)]
        if boss_type in ["Paragon", "Arbiter", "Incarnate"]:
            self.boss_name = random.choice(target_list)
            boss_numeral = self.boss_name.split()[0]
            self.boss_image = f'{gli.web_url}tarot/{boss_numeral}/{boss_numeral}_8.png'
        elif boss_type not in ["Demon", "Dragon"]:
            self.boss_name, self.boss_image = random.choice(target_list)
            self.boss_image = f'{gli.web_url}bosses/{boss_type}/{boss_tier}.png' if self.boss_image == "" else f'{gli.web_url}{boss_type}/{self.boss_image}.png'
        else:
            self.boss_name = random.choice(target_list)
        self.boss_element = 9

        # Handle boss type exceptions.
        match boss_type:
            case "Fortress":
                if boss_tier != 4:
                    boss_prefix, self.boss_element = random.choice(fortress_variants)
                    boss_prefix += f" {random.choice(fortress_types)}, "
                    self.boss_name = boss_prefix + "the " + self.boss_name
            case "Dragon":
                temp_name_split = self.boss_name.split()
                boss_element = temp_name_split[1]
                self.boss_element = 8
                if boss_tier != 4:
                    self.boss_element = gli.element_names.index(boss_element)
                    self.boss_name += " Dragon"
                self.boss_image = f'{gli.web_url}bosses/{boss_type}/{gli.element_names[self.boss_element]}_Dragon.png'
            case "Demon":
                if boss_tier != 4:
                    self.boss_element = random.randint(0, 8)
                    boss_colour = demon_colours[self.boss_element]
                    if boss_colour not in ["Crimson", "Azure", "Jade", "Violet", "Gold"]:
                        self.boss_image = ""
                    self.boss_image = f'{gli.web_url}bosses/Demon/{boss_colour}/{self.boss_name}_{boss_colour}.png'
                    self.boss_name = f'{boss_colour} {self.boss_name}'
            case _:
                pass


async def spawn_boss(channel_id, player_id, boss_tier, boss_type, boss_level, gauntlet=False, magnitude=0):
    df = await encounters.get_encounter_id(channel_id, player_id, id_only=False)
    # Load existing boss.
    if df is not None:
        raid_id, encounter = int(df["raid_id"].values[0]), str(df["encounter"].values[0])
        player_id, channel_id = int(df["player_id"].values[0]), int(df["channel_id"].values[0])
        boss_info, boss_data = str(df["boss_info"].values[0]), str(df["boss_data"].values[0])
        boss_weakness = str(df["boss_weakness"].values[0])
        boss_obj = CurrentBoss()
        boss_obj.boss_name, boss_obj.boss_image, boss_type_num = boss_info.split(";")
        boss_obj.boss_type_num, boss_obj.boss_type = int(boss_type_num), gli.boss_list[int(boss_type_num)]
        boss_obj.boss_level, boss_obj.boss_tier, boss_obj.boss_cHP, boss_obj.boss_mHP = map(int, boss_data.split(";"))
        temp_t, temp_e = boss_weakness.split('/')
        type_list, ele_list = temp_t.split(';'), temp_e.split(';')
        boss_obj.boss_typeweak, boss_obj.boss_eleweak = list(map(int, type_list)), list(map(int, ele_list))
        # Set the damage cap.
        boss_obj.damage_cap = -1
        if boss_obj.boss_tier <= 4:
            boss_obj.damage_cap = (10 ** int(boss_level / 10 + 4) - 1)
        return boss_obj
    # Create the boss object if it doesn't exist.
    if boss_type == "raid":
        pass
    elif boss_tier == 7:
        boss_level += 150
    elif boss_tier == 6:
        boss_level += 10
    elif boss_type == "Arbiter":
        boss_level += 10
    boss_obj = CurrentBoss()
    boss_obj.player_id = player_id
    boss_obj.boss_type, boss_obj.boss_type_num = boss_type, gli.boss_list.index(boss_type)
    boss_obj.boss_level, boss_obj.boss_tier = boss_level, boss_tier
    boss_obj.generate_boss_name_image(boss_obj.boss_type, boss_obj.boss_tier)
    # Assign element and type weaknesses.
    for x in random.sample(range(9), 3):
        boss_obj.boss_eleweak[x] = 1
    boss_eleweak = ";".join(str(y) for y in boss_obj.boss_eleweak)
    boss_eleweak = boss_eleweak.rstrip(';')
    for x in random.sample(range(7), 2):
        boss_obj.boss_typeweak[x] = 1
    boss_typeweak = ";".join(str(y) for y in boss_obj.boss_typeweak)
    boss_typeweak = boss_typeweak.rstrip(';')
    # Set boss hp and damage cap.
    total_hp = int(10 ** (min(100, boss_obj.boss_level) // 10 + 5)) * (10 ** magnitude)
    if boss_obj.boss_level >= 100:
        multiplier_count = (boss_obj.boss_level - 100) // 100 + 1
        total_hp *= (10 ** multiplier_count)
    encounter_type = "solo" if not gauntlet else "gauntlet"
    boss_obj.damage_cap = total_hp // 10 - 1
    if boss_type == "raid":
        encounter_type, boss_obj.damage_cap = "raid", (total_hp // 1000 - 1)
    elif boss_obj.boss_type == "Incarnate":
        boss_obj.damage_cap = -1
    boss_obj.boss_cHP = boss_obj.boss_mHP = total_hp
    # Add the new boss to the database.
    boss_info = f"{boss_obj.boss_name};{boss_obj.boss_image};{boss_obj.boss_type_num}"
    boss_data = f"{boss_level};{boss_tier};{str(int(boss_obj.boss_cHP))};{str(int(boss_obj.boss_mHP))}"
    boss_weakness = f"{boss_typeweak}/{boss_eleweak}"
    raw_query = ("INSERT INTO EncounterList "
                 "(channel_id, player_id, encounter, boss_info, boss_data, boss_weakness, abandon) "
                 "VALUES (:channel_id, :player_id, :encounter, :boss_info, :boss_data, :boss_weakness, :abandon)")
    params = {'channel_id': str(channel_id), 'player_id': player_id, 'encounter': encounter_type,
              'boss_info': boss_info,
              'boss_data': boss_data, 'boss_weakness': boss_weakness, 'abandon': 0}
    await rqy(raw_query, params=params)
    return boss_obj


def get_random_bosstier(boss_type):
    tier_list, weight_list = [1, 2, 3, 4, 5, 6], [35, 25, 20, 10, 7, 3]
    if boss_type != "Arbiter":
        tier_list, weight_list = [1, 2, 3, 4], [35, 30, 25, 10]
    boss_tier = random.choices(tier_list, weights=weight_list, k=1)[0]
    return boss_tier


async def update_boss_cHP(channel_id, player_id, boss_obj):
    raid_id = await encounters.get_encounter_id(channel_id, player_id)
    if raid_id is None:
        return
    new_data = f"{boss_obj.boss_level};{boss_obj.boss_tier};{str(int(boss_obj.boss_cHP))};{str(int(boss_obj.boss_mHP))}"
    raw_query = "UPDATE EncounterList SET boss_data = :new_data WHERE encounter_id = :id_check"
    await rqy(raw_query, params={'new_data': new_data, 'id_check': raid_id})


async def get_damage_list(channel_id):
    raid_id = await encounters.get_encounter_id(channel_id, None)
    if raid_id is None:
        return None
    raw_query = "SELECT player_id, player_dps FROM RaidPlayers WHERE raid_id = :id_check"
    df = await rqy(raw_query, True, params={'id_check': raid_id})
    return ([], []) if df is None else (df["player_id"].values.tolist(), df["player_dps"].values.tolist())


async def create_dead_boss_embed(channel_id, active_boss, dps, extension=""):
    active_boss.boss_cHP = 0
    dead_embed = active_boss.create_boss_embed(dps, extension=extension)
    player_list, damage_list = await get_damage_list(channel_id)
    output_list = ""
    for idx, x in enumerate(player_list):
        player_obj = await player.get_player_by_id(x)
        output_list += f'{str(player_obj.player_username)}: {sm.number_conversion(int(damage_list[idx]))}\n'
    dead_embed.add_field(name="SLAIN", value=output_list, inline=False)
    return dead_embed
