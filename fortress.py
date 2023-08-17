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
        self.boss_mHP = (1 + (boss_iteration * .5)) * boss_tier * 25000
        self.boss_cHP = self.boss_mHP
        self.boss_iteration = boss_iteration
        self.boss_typeweak = boss_typeweak
        self.boss_eleweak_a = boss_eleweak_a
        self.boss_eleweak_b = boss_eleweak_b
        self.boss_channel_id = boss_channel_id
        self.boss_message_id = boss_message_id

    # return the boss display string
    def __str__(self):
        boss_output = f"{self.boss_name}\n `({self.boss_cHP} / {self.boss_mHP})"
        boss_output += f"\n Type Weakness: {self.boss_typeweak}"
        boss_output += f"\n Elemental Weakness 1: {self.boss_eleweak_a}"
        boss_output += f"\n Elemental Weakness 2: {self.boss_eleweak_b}'"
        return boss_output
    # store the boss data in a csv
    def save_boss(self):
        x = 0

    # calculate the bosses new hp
    def calculate_hp(self):
        x = 0


def spawn_boss(channel_id: int, message_id: int) -> CurrentBoss:
    # initialize boss information
    new_boss_tier = get_random_bosstier()
    new_boss_name = get_random_prefix() + get_boss_suffix(new_boss_tier)
    boss_iteration = 0
    boss_type_weak = get_boss_typeweak()
    boss_eleweak_a = get_boss_eleweak()
    boss_eleweak_b = boss_eleweak_a
    while boss_eleweak_a == boss_eleweak_b:
        boss_eleweak_b = get_boss_eleweak()

    # create the boss object
    boss_object = CurrentBoss('fortress', new_boss_name, new_boss_tier, boss_iteration,
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
            boss_tier = 7
        elif random_number <= 5:
            boss_tier = 6
        elif random_number <= 10:
            boss_tier = 5
        elif random_number <= 20:
            boss_tier = 4
        elif random_number <= 40:
            boss_tier = 3
        elif random_number <= 65:
            boss_tier = 2
        elif random_number <= 100:
            boss_tier = 1
        else:
            boss_tier = 0

        return boss_tier


def get_boss_suffix(bosstier: int) -> str:
    match bosstier:
        case 1:
            boss_suffix = "Ominous Keep"
        case 2:
            boss_suffix = "Twisted Stronghold"
        case 3:
            boss_suffix = "Malignant Fortress"
        case 4:
            boss_suffix = "Malevolant Castle"
        case 5:
            boss_suffix = "Malefic Citadel"
        case 6:
            boss_suffix = "Starlit Fortune"
        case 7:
            boss_suffix = "Heavenly Treasure"
        case _:
            boss_suffix = "error"

    return boss_suffix


def get_random_prefix() -> str:
    boss_name = ""

    boss_data = pd.read_csv("fortressname.csv")

    # generate boss name
    random_number = random.randint(0, boss_data['fortress_name_a'].count())
    boss_name = boss_data.fortress_name_a[random_number]
    random_number = random.randint(0, boss_data['fortress_name_b'].count())
    boss_name += " " + boss_data.fortress_name_b[random_number] + ", "

    return boss_name


# generate ele weakness
def get_boss_eleweak() -> str:
    random_number = random.randint(1, 8)
    match random_number:
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
            boss_weakness_temp = "Celestial"
        case _:
            boss_weakness_temp = "Omni"

    return boss_weakness_temp


# generate type weakness
def get_boss_typeweak() -> str:
    # generate weaknesses
    random_number = random.randint(1, 2)
    match random_number:
        case 1:
            boss_type_defence = 'ranged'
        case 2:
            boss_type_defence = 'melee'
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






