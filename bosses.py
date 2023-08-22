import discord
import chatcommands
from discord.ext import commands
import csv
import random
import pandas as pd
import os


# Boss class
class CurrentBoss:
    def __init__(self, boss_type, boss_name, boss_tier, boss_iteration,
                 boss_typeweak, boss_eleweak_a, boss_eleweak_b,
                 boss_channel_id, boss_message_id):
        self.boss_type = boss_type
        self.boss_name = boss_name
        self.tier = boss_tier
        self.boss_mHP = (1 + (boss_iteration * .5)) * boss_tier * get_base_hp(boss_type)
        self.boss_cHP = self.boss_mHP
        self.boss_iteration = boss_iteration
        self.boss_typeweak = boss_typeweak
        self.boss_eleweak_a = boss_eleweak_a
        self.boss_eleweak_b = boss_eleweak_b
        self.boss_channel_id = boss_channel_id
        self.boss_message_id = boss_message_id

    # return the boss display string
    def __str__(self):
        boss_output = f"{self.boss_name}\n {self.boss_type}\n ({self.boss_cHP} / {self.boss_mHP})\n"
        boss_output += f"\n Weakness: {self.boss_typeweak}   "
        boss_output += str(self.boss_eleweak_a) + str(self.boss_eleweak_b)
        return boss_output
    # store the boss data in a csv
    def save_boss(self):
        x = 0

    # calculate the bosses new hp
    def calculate_hp(self):
        x = 0


def spawn_boss(channel_id: int, message_id: int, boss_type_num: int) -> CurrentBoss:
    # initialize boss information
    new_boss_tier = get_random_bosstier()
    match boss_type_num:
        case 1:
            boss_type = "Fortress"
        case 2:
            boss_type = "Dragon"
        case 3:
            boss_type = "Primordial"
        case 4:
            boss_type = "Paragon"
        case _:
            boss_type = "error"

    new_boss_name = get_boss_name(boss_type, new_boss_tier)

    boss_iteration = 0
    boss_type_weak = get_boss_typeweak()
    boss_eleweak_a = get_boss_eleweak()
    boss_eleweak_b = boss_eleweak_a
    while boss_eleweak_a == boss_eleweak_b:
        boss_eleweak_b = get_boss_eleweak()

    # create the boss object
    boss_object = CurrentBoss(boss_type, new_boss_name, new_boss_tier, boss_iteration,
                                       boss_type_weak, boss_eleweak_a, boss_eleweak_b, channel_id, message_id)
    return boss_object


def check_existing_boss(message_id: int) -> bool:
    if message_id == 0:
        return False
    else:
        return True


def get_channel_id() -> int:
    try:
        f = open("channelid.txt", "r")
    except Exception as e:
        print(e)
        channel_value = 0
    else:
        channel_value = int(f.read())
    return channel_value


def get_message_id() -> int:
    try:
        f = open("messageid.txt", "r")
    except Exception as e:
        print(e)
        message_value = 0
    else:
        if os.path.getsize('messageid.txt') == 0:
            message_value = 0
        else:
            message_value = int(f.read())
    return message_value


def get_random_bosstier() -> int:
        random_number = random.randint(1, 100)
        if random_number <= 1:
            boss_tier = 5
        elif random_number <= 10:
            boss_tier = 4
        elif random_number <= 30:
            boss_tier = 3
        elif random_number <= 60:
            boss_tier = 2
        elif random_number <= 100:
            boss_tier = 1
        else:
            boss_tier = 0

        return boss_tier


# generate ele weakness
def get_boss_eleweak() -> str:
    random_number = random.randint(1, 8)
    match random_number:
        case 1:
            boss_weakness_temp = "<:efire:1141653476816986193>"
        case 2:
            boss_weakness_temp = "<:ewater:1141653475059572779>"
        case 3:
            boss_weakness_temp = "<:ewind:1141653474480767016>"
        case 4:
            boss_weakness_temp = "<:eearth:1141653473528664126>"
        case 5:
            boss_weakness_temp = "<:elightning:1141653471154671698>"
        case 6:
            boss_weakness_temp = "<:elight:1141653466343800883>"
        case 7:
            boss_weakness_temp = "<:eshadow:1141653468080242748>"
        case 8:
            boss_weakness_temp = "<:ecelestial:1141653469938339971>"
        case _:
            boss_weakness_temp = "<a:eshadow2:1141653468965257216>"

    return boss_weakness_temp


# generate type weakness
def get_boss_typeweak() -> str:
    # generate weaknesses
    random_number = random.randint(1, 2)
    match random_number:
        case 1:
            boss_type_defence = '<:eranged:1141654478748135545>'
        case 2:
            boss_type_defence = '<:emelee:1141654530619088906>'
        case _:
            boss_type_defence = 'error'
    return boss_type_defence


# store boss channel and message ids
def store_boss_ids(channel_id: int, message_id: int) -> str:
    # store channel id
    f = open("channelid.txt", "w")
    f.write(str(channel_id))
    f.close()
    # store message id
    f = open("messageid.txt", "w")
    f.write(str(message_id))
    f.close()
    # store boss information
    filename = 'bosstest.csv'
    boss_id = 1
    return 'success'


def get_base_hp(base_type: str) -> int:
    match base_type:
        case "Fortress":
            base_hp = 25000
        case "Dragon":
            base_hp = 50000
        case "Primordial":
            base_hp = 100000
        case "Paragon":
            base_hp = 1000000
        case _:
            base_hp = 0

    return base_hp


def get_boss_name(boss_type: str, boss_tier: int) -> str:
    boss_name = ""

    match boss_type:
        case "Fortress":
            name_selector= random.randint(1,2)
            match boss_tier:
                case 1:
                    if name_selector == 1:
                        boss_suffix = "Ominous Keep"
                    else:
                        boss_suffix = "Twisted Stronghold"
                case 2:
                    if name_selector == 1:
                        boss_suffix = "Malignant Fortress"
                    else:
                        boss_suffix = "Malevolant Castle"
                case 3:
                    if name_selector == 1:
                        boss_suffix = "Sinful Spire"
                    else:
                        boss_suffix = "Malefic Citadel"
                case 4:
                    if name_selector == 1:
                        boss_suffix = "Heavenly Treasure Trove"
                    else:
                        boss_suffix = "Starlit Fortune"
                case _:
                    boss_suffix = "error"
            boss_name = get_boss_descriptor(boss_type) + "the " + boss_suffix
        case "Dragon":
            match boss_tier:
                case 1:
                    name_selector = random.randint(1, 2)
                    if name_selector == 1:
                        boss_name = "Zelphyros, Wind"
                    else:
                        boss_name = "Sahjvadiir, Earth"
                case 2:
                    name_selector = random.randint(1, 3)
                    if name_selector == 1:
                        boss_name = "Arkadrya, Lightning"
                    elif name_selector == 2:
                        boss_name = "Phyyratha, Fire"
                    else:
                        boss_name = "Elyssrya, Water"
                case 3:
                    name_selector = random.randint(1, 2)
                    if name_selector == 1:
                        boss_name = "Y'thana, Light"
                    else:
                        boss_name = "Rahk'vath, Shadow"
                case 4:
                    boss_name = "Astratha, Celestial"
                case _:
                    boss_name = "error"
            boss_name += " Dragon"
        case "Primordial":
            match boss_tier:
                case 1:
                    name_selector = random.randint(1, 5)
                    if name_selector == 1:
                        boss_name = "Beelzebub"
                    elif name_selector == 2:
                        boss_name = "Azazel"
                    elif name_selector == 3:
                        boss_name = "Astaroth"
                    elif name_selector == 4:
                        boss_name = "Iblis"
                    else:
                        boss_name = "Belial"
                case 2:
                    name_selector = random.randint(1, 5)
                    if name_selector == 1:
                        boss_name = "Abbadon"
                    elif name_selector == 2:
                        boss_name = "Asura"
                    elif name_selector == 3:
                        boss_name = "Ifrit"
                    elif name_selector == 4:
                        boss_name = "Lilith"
                    else:
                        boss_name = "Baphomet"
                case 3:
                    name_selector = random.randint(1, 2)
                    if name_selector == 1:
                        boss_name = "Diablo"
                    else:
                        boss_name = "Diabla"
                case 4:
                    boss_name = "Behemoth"
                case _:
                    boss_name = "error"
            boss_name = get_boss_descriptor(boss_type) + boss_name
        case "Paragon":
            match boss_tier:
                case 1:
                    name_selector = random.randint(1, 6)
                    if name_selector == 1:
                        boss_name = "Akasha, The Fool"
                    elif name_selector == 2:
                        boss_name = "Alaya, The Memory"
                    elif name_selector == 3:
                        boss_name = "Kama, The Love"
                    elif name_selector == 4:
                        boss_name = "Luna, The Moon"
                    elif name_selector == 5:
                        boss_name = "Luma, The Sun"
                    else:
                        boss_name = "Runa, The Magic"
                case 2:
                    name_selector = random.randint(1, 3)
                    if name_selector == 1:
                        boss_name = "Rua, The Abyss"
                    elif name_selector == 2:
                        boss_name = "Nua, The Heavens"
                    else:
                        boss_name = "Nova, the Star"
                case 3:
                    name_selector = random.randint(1, 3)
                    if name_selector == 1:
                        boss_name = "Ultima, The Creation"
                    elif name_selector == 2:
                        boss_name = "Thana, The Death"
                    else:
                        boss_name = "Chrona, The Time"
                case 4:
                    boss_name = "Pandora, The Celestial"
                case 5:
                    boss_name = "Oblivia, The Void"
                case _:
                    boss_name = "error"
        case _:
            boss_name = "error"

    return boss_name


def get_boss_descriptor(boss_type: str) -> str:
    boss_descriptor = ""

    match boss_type:
        case "Fortress":
            boss_data = pd.read_csv("Fortressname.csv")

            # generate Fortress descriptor
            random_number = random.randint(0, boss_data['Fortress_name_a'].count())
            boss_descriptor = boss_data.Fortress_name_a[random_number]
            random_number = random.randint(0, boss_data['Fortress_name_b'].count())
            boss_descriptor += " " + boss_data.Fortress_name_b[random_number] + ", "

        case "Primordial":
            random_number = random.randint(1,10)
            match random_number:
                case 1:
                    boss_descriptor = "Crimson "
                case 2:
                    boss_descriptor = "Azure "
                case 3:
                    boss_descriptor = "Jade "
                case 4:
                    boss_descriptor = "Violet "
                case 5:
                    boss_descriptor = "Ivory "
                case 6:
                    boss_descriptor = "Rose "
                case 7:
                    boss_descriptor = "Gold "
                case 8:
                    boss_descriptor = "Silver "
                case 9:
                    boss_descriptor = "Stygian "
                case _:
                    boss_descriptor = "Void "
        case _:
            boss_descriptor = "error"

    return boss_descriptor
