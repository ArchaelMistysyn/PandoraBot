import discord
import chatcommands
from discord.ext import commands
import csv
import random
import pandas as pd
import os


# manage fortress bosses
def spawn_boss() -> str:
    # return a random boss object?
    return f'`{get_random_bossname()} \n has appeared!`'


def update_existing_boss() -> str:
    # existing boss post details will update.
    return f'`{get_random_bossname()} \n has appeared!`'


def check_existing_boss(message_id: int) -> bool:
    boss_hp = 1
    # this will need to change to allow loot to be awarded
    if message_id == 0 or boss_hp == 0:
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


def get_random_bossname() -> str:
    boss_name = ""

    boss_data = pd.read_csv("fortressname.csv")

    # generate boss name
    random_number = random.randint(0, boss_data['fortress_name_a'].count())
    boss_name = boss_data.fortress_name_a[random_number]
    random_number = random.randint(0, boss_data['fortress_name_b'].count())
    boss_name += " " + boss_data.fortress_name_b[random_number] + ", "
    random_number = random.randint(1, 100)
    # print(random_number)
    checker = 1
    z1 = 0
    z2 = 0
    if random_number == 1:
        boss_name = "Starlit Fortune, Heavenly Treasury"
    else:
        for x in boss_data['spawn_rate']:
            checker += x
            if random_number <= checker:
                break
            else:
                z1 += 1

        for y in boss_data['fortress_tier']:
            if z1 == z2:
                boss_tier = y
                boss_name += boss_tier
                break
            else:
                z2 += 1

    return boss_name


def store_boss_details(channel_id: int, message_id: int) -> str:
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

    # generate weaknesses
    if random.randint(1, 2):
        boss_type_defence = 'ranged'
    else:
        boss_type_defence = 'melee'

    # generate weaknesses
    boss_elemental_weakness = ["Fire", "Water"]
    weakness_count = 0
    while weakness_count < 2:
        boss_weakness_temp = random.randint(1, 8)
        match boss_weakness_temp:
            case 1:
                boss_weakness_temp = "Fire"
            case 2:
                boss_weakness_temp = "Water"
            case 3:
                boss_weakness_temp = "Wind"
            case 4:
                boss_weakness_temp = "Earth"
            case 5:
                boss_weakness_temp = "Lightning"
            case 6:
                boss_weakness_temp = "Light"
            case 7:
                boss_weakness_temp = "Shadow"
            case 8:
                boss_weakness_temp = "celestial"
            case _:
                boss_weakness_temp = "Blood"
        if weakness_count == 0:
            boss_elemental_weakness[weakness_count] = boss_weakness_temp
            weakness_count += 1
        elif weakness_count == 1 and boss_weakness_temp != boss_elemental_weakness[0]:
            boss_elemental_weakness[weakness_count] = boss_weakness_temp
            weakness_count += 1
        else:
            weakness_count += 1

    boss_name = get_random_bossname()
    """
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["boss_id", "boss_name",
                 "boss_type_defence", "boss_weakness_a", "boss_weakness_b",
                 "boss_tier", "boss_base_hp", "boss_current_hp", "boss_regen_rate",
                 "boss_active_duration", "boss_received_damage_byplayer", "boss_received_damage_rate"]

        writer.writerow(field)
        writer.writerow([boss_id, boss_name,
                         boss_type_defence, boss_weakness_a, boss_weakness_b,
                         boss_tier, boss_base_hp, boss_current_hp, boss_regen_rate,
                         boss_active_duration, boss_received_damage_byplayer, boss_received_damage_rate])"""

    return 'success'

