import discord
import chatcommands
from discord.ext import commands
import csv
import random
import pandas as pd
import player
import bosses
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


# Boss class
class CurrentBoss:
    def __init__(self, boss_type_num, boss_type, boss_tier, boss_level, boss_message_id):
        self.boss_type_num = boss_type_num
        self.boss_type = boss_type
        self.boss_tier = boss_tier
        self.boss_lvl = boss_level
        self.boss_message_id = boss_message_id

        self.boss_name = ""
        self.boss_image = ""
        self.boss_mHP = 0
        self.boss_cHP = 0
        self.boss_typeweak = []
        self.boss_eleweak = []
        self.participating_players = []

    # return the boss display string
    def __str__(self):
        return self.boss_name

    # calculate the bosses new hp
    def calculate_hp(self) -> bool:
        if self.boss_cHP <= 0:
            is_alive = False
        else:
            is_alive = True

        return is_alive

    def create_boss_msg(self, dps, is_alive):
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
        if not is_alive:
            self.boss_cHP = 0
        boss_hp = f'{life_emoji} ({int(self.boss_cHP):,} / {int(self.boss_mHP):,})'
        bar_length = int(self.boss_cHP / self.boss_mHP * 10)
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
        for y in self.boss_eleweak:
            boss_weakness += str(y)
        embed_msg = discord.Embed(colour=tier_colour,
                                  title=boss_title,
                                  description="")
        embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
        embed_msg.add_field(name=boss_weakness, value="", inline=False)
        embed_msg.add_field(name="Current DPS: ", value=dps_msg)
        embed_msg.set_image(url=img_link)

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
        paragon_list_t5 = ["III - Oblivia, The Void"]
        paragon_list_t6 = ["IV - Akasha, The Infinite"]
        paragon_names = [paragon_list_t1, paragon_list_t2, paragon_list_t3,
                         paragon_list_t4, paragon_list_t5, paragon_list_t6]

        boss_name = ""
        boss_image = ""
        match boss_type:
            case "Fortress":
                name_selector = random.randint(1, len(fortress_names[(boss_tier - 1)]))
                boss_suffix = fortress_names[(boss_tier - 1)][(name_selector - 1)]
                if boss_tier != 4:
                    boss_name = get_boss_descriptor(boss_type) + "the " + boss_suffix
                    boss_image = f'https://kyleportfolio.ca/botimages/tarot/{boss_type}{boss_tier}.png'
                else:
                    boss_image = ""
            case "Dragon":
                name_selector = random.randint(1, len(dragon_names[(boss_tier - 1)]))
                boss_name = dragon_names[(boss_tier - 1)][(name_selector - 1)]
                if boss_tier != 4:
                    boss_name += " Dragon"
                    boss_image = f'https://kyleportfolio.ca/botimages/tarot/{boss_type}{boss_tier}.png'
                else:
                    boss_image = ""
            case "Demon":
                name_selector = random.randint(1, len(demon_names[(boss_tier - 1)]))
                boss_name = demon_names[(boss_tier - 1)][(name_selector - 1)]
                if boss_tier != 4:
                    boss_colour = get_boss_descriptor(boss_type)
                    boss_name = f'{boss_colour} {boss_name}'
                    boss_image = f'https://kyleportfolio.ca/botimages/tarot/{boss_type}{boss_colour}{boss_tier}.png'
                else:
                    boss_image = ""
            case "Paragon":
                name_selector = random.randint(1, len(paragon_names[(boss_tier - 1)]))
                boss_name = paragon_names[(boss_tier - 1)][(name_selector - 1)]
                boss_image = f'https://kyleportfolio.ca/botimages/tarot/{boss_type}{boss_tier}.png'
            case _:
                boss_name = "error"
        self.boss_image = boss_image
        self.boss_name = boss_name


def spawn_boss(new_boss_tier, boss_type, boss_level):
    message_id = 0
    match boss_type:
        case "Fortress":
            boss_type_num = 1
        case "Dragon":
            boss_type_num = 2
        case "Demon":
            boss_type_num = 3
        case _:
            boss_type_num = 4

    boss_object = CurrentBoss(boss_type_num, boss_type, new_boss_tier, boss_level, message_id)
    boss_object.generate_boss_name_image(boss_type, new_boss_tier)

    num_eleweak = 3
    eleweak_list = random.sample(range(1, 10), num_eleweak)
    for x in eleweak_list:
        new_weakness = get_element(int(x))
        boss_object.boss_eleweak.append(new_weakness)
    num_typeweak = 2
    typeweak_list = random.sample(range(1, 5), num_typeweak)
    for y in typeweak_list:
        new_weakness = get_type(int(y))
        boss_object.boss_typeweak.append(new_weakness)

    if new_boss_tier <= 4:
        total_hp = get_base_hp(boss_type)
        total_hp *= new_boss_tier * (boss_level * 1.25)
    elif new_boss_tier == 5:
        total_hp = 10000000000000
    else:
        total_hp = 999999999999999
    boss_object.boss_mHP = total_hp
    boss_object.boss_cHP = boss_object.boss_mHP

    return boss_object


def check_existing_boss(message_id: int) -> bool:
    if message_id == 0:
        return False
    else:
        return True


def get_channel_id() -> int:
    # this needs to be updated for multiple values
    try:
        f = open("channelid.txt", "r")
    except Exception as e:
        print(e)
        channel_value = 0
    else:
        channel_value = int(f.read())
    return channel_value


def get_random_bosstier(boss_type):
    random_number = random.randint(1, 100)
    if random_number <= 1:
        boss_tier = 6
    elif random_number <= 3:
        boss_tier = 5
    elif random_number <= 8:
        boss_tier = 4
    elif random_number <= 35:
        boss_tier = 3
    elif random_number <= 65:
        boss_tier = 2
    elif random_number <= 100:
        boss_tier = 1
    else:
        boss_tier = 0

    if boss_tier > 4:
        if boss_type != "Paragon":
            boss_tier = 4

    return boss_tier


# generate ele weakness
def get_element(chosen_weakness):
    if chosen_weakness == 0:
        random_number = random.randint(1, 9)
    else:
        random_number = chosen_weakness
    match random_number:
        case 1:
            element_temp = "<:ef:1141653475059572779>"
        case 2:
            element_temp = "<:eg:1141653474480767016>"
        case 3:
            element_temp = "<:eh:1141653473528664126>"
        case 4:
            element_temp = "<:ei:1141653471154671698>"
        case 5:
            element_temp = "<:ej:1141653469938339971>"
        case 6:
            element_temp = "<:ek:1141653468080242748>"
        case 7:
            element_temp = "<:el:1141653466343800883>"
        case 8:
            element_temp = "<:em:1141647050342146118>"
        case _:
            element_temp = "<:ee:1141653476816986193>"

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


# store boss channel and message ids
def store_channel_id(channel_id: int) -> str:
    # store channel id
    f = open("channelid.txt", "w")
    f.write(str(channel_id))
    f.close()

    return 'success'


def get_base_hp(base_type):
    match base_type:
        case "Fortress":
            base_hp = 1000
        case "Dragon":
            base_hp = 500000
        case "Demon":
            base_hp = 5000000
        case "Paragon":
            base_hp = 1000000000
        case _:
            base_hp = 0

    return base_hp


def get_boss_descriptor(boss_type):
    match boss_type:
        case "Fortress":
            boss_data = pd.read_csv("fortressname.csv")

            # generate Fortress descriptor
            random_number = random.randint(0, (boss_data['fortress_name_a'].count()-1))
            boss_descriptor = boss_data.fortress_name_a[random_number]
            random_number = random.randint(0, (boss_data['fortress_name_b'].count()-1))
            boss_descriptor += " " + boss_data.fortress_name_b[random_number] + ", "

        case "Demon":
            random_number = random.randint(1, 9)
            match random_number:
                case 1:
                    boss_descriptor = "Crimson"
                case 2:
                    boss_descriptor = "Azure"
                case 3:
                    boss_descriptor = "Jade"
                case 4:
                    boss_descriptor = "Violet"
                case 5:
                    boss_descriptor = "Ivory"
                case 6:
                    boss_descriptor = "Rose"
                case 7:
                    boss_descriptor = "Gold"
                case 8:
                    boss_descriptor = "Silver"
                case 9:
                    boss_descriptor = "Stygian"
                case _:
                    boss_descriptor = "Error"
        case _:
            boss_descriptor = "error"

    return boss_descriptor


def add_participating_player(player_id):
    filename = "raidplayers.csv"
    df = pd.read_csv(filename)

    if player_id in df['player_id'].values:
        return " is already in the raid."
    else:
        with open(filename, 'a', newline='') as file:
            dps = 0
            writer = csv.writer(file)
            writer.writerow([player_id, dps])
            return " joined the raid"


def update_player_damage(player_id, player_damage):
    filename = "raidplayers.csv"
    df = pd.read_csv(filename)
    df.loc[df['player_id'] == player_id, 'dps_dealt'] = df['dps_dealt'] + player_damage
    df.to_csv(filename, index=False)


def get_players():
    filename = "raidplayers.csv"
    df = pd.read_csv(filename)
    player_list = df['player_id']
    return list(player_list)


def get_damage_list():
    filename = "raidplayers.csv"
    output = ""
    username = []
    damage = []
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            user_id = int(line['player_id'])
            player_object = player.get_player_by_id(user_id)
            username.append(player_object.player_username)
            damage.append(int(line['dps_dealt']))
    for idx, x in enumerate(username):
        output += f'{str(x)}: {damage[idx]:,}\n'

    return output


def clear_list():
    filename = "raidplayers.csv"
    df = pd.read_csv(filename)
    df = pd.DataFrame(columns=df.columns)
    df.to_csv(filename, index=False)


def create_dead_boss_embed(active_boss, dps):
    active_boss.boss_cHP = 0
    dead_embed = active_boss.create_boss_msg(dps, False)
    damage_list = bosses.get_damage_list()
    dead_embed.add_field(name="SLAIN", value=damage_list, inline=False)
    return dead_embed
