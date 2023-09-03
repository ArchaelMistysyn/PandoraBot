import discord
import chatcommands
from discord.ext import commands
import csv
import random
import pandas as pd
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

# Boss class
class CurrentBoss:
    def __init__(self, boss_type, boss_name, boss_tier, boss_iteration,
                 boss_typeweak, boss_eleweak_a, boss_eleweak_b,
                 boss_message_id):
        self.boss_type = boss_type
        self.boss_name = boss_name
        self.boss_tier = boss_tier
        self.boss_mHP = int((1 + (boss_iteration * .5)) * boss_tier * get_base_hp(boss_type))
        self.boss_cHP = self.boss_mHP
        self.boss_iteration = boss_iteration
        self.boss_typeweak = boss_typeweak
        self.boss_eleweak_a = boss_eleweak_a
        self.boss_eleweak_b = boss_eleweak_b
        self.boss_message_id = boss_message_id
        self.participating_players = []
        self.player_dmg_min = []
        self.player_dmg_max = []

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

    def draw_boss_hp(self, percentage) -> str:
        # draw the boss hp bar
        out = Image.new("RGB", (150, 100), (255, 255, 255))
        d = ImageDraw.Draw(out)
        d = drawProgressBar(d, 10, 10, 100, 25, percentage)
        image_location = "boss_hp.jpg"
        out.save(image_location)
        return image_location


def spawn_boss(boss_type_num: int) -> CurrentBoss:
    # initialize boss information
    new_boss_tier = get_random_bosstier(boss_type_num)
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
    boss_typeweak = get_type()
    boss_eleweak_a = get_element()
    boss_eleweak_b = boss_eleweak_a
    while boss_eleweak_a == boss_eleweak_b:
        boss_eleweak_b = get_element()

    message_id = 0

    # create the boss object
    boss_object = CurrentBoss(boss_type, new_boss_name, new_boss_tier, boss_iteration,
                                       boss_typeweak, boss_eleweak_a, boss_eleweak_b, message_id)
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


def drawProgressBar(d, x, y, w, h, progress, bg="black", fg="red"):
    # draw background
    d.ellipse((x+w, y, x+h+w, y+h), fill=bg)
    d.ellipse((x, y, x+h, y+h), fill=bg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=bg)

    # draw progress bar
    w *= progress
    d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
    d.ellipse((x, y, x+h, y+h),fill=fg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

    return d


def get_random_bosstier(boss_type_num: int) -> int:
        random_number = random.randint(1, 100)
        if random_number <= 1:
            if boss_type_num == 4:
                boss_tier = 5
            else:
                boss_tier = 4
        elif random_number <= 5:
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
def get_element() -> str:
    # generate an element
    random_number = random.randint(1, 8)
    match random_number:
        case 1:
            element_temp = "<:efire:1141653476816986193>"
        case 2:
            element_temp = "<:ewater:1141653475059572779>"
        case 3:
            element_temp = "<:ewind:1141653474480767016>"
        case 4:
            element_temp = "<:eearth:1141653473528664126>"
        case 5:
            element_temp = "<:elightning:1141653471154671698>"
        case 6:
            element_temp = "<:elight:1141653466343800883>"
        case 7:
            element_temp = "<:eshadow:1141653468080242748>"
        case 8:
            element_temp = "<:ecelestial:1141653469938339971>"
        case _:
            element_temp = "<a:eshadow2:1141653468965257216>"

    return element_temp


# generate type weakness
def get_type() -> str:
    # generate a type
    random_number = random.randint(1, 4)
    match random_number:
        case 1:
            type_temp = '<:eranged:1141654478748135545>'
        case 2:
            type_temp = '<:emelee:1141654530619088906>'
        case 3:
            type_temp = "<:emagical:1143754281846059119>"
        case _:
           type_temp = "<:esummon:1143754335478616114>"

    return type_temp


# store boss channel and message ids
def store_channel_id(channel_id: int) -> str:
    # store channel id
    f = open("channelid.txt", "w")
    f.write(str(channel_id))
    f.close()

    return 'success'


def get_base_hp(base_type: str) -> int:
    match base_type:
        case "Fortress":
            base_hp = 1000
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
            boss_data = pd.read_csv("fortressname.csv")

            # generate Fortress descriptor
            random_number = random.randint(0, (boss_data['fortress_name_a'].count()-1))
            boss_descriptor = boss_data.fortress_name_a[random_number]
            random_number = random.randint(0, (boss_data['fortress_name_b'].count()-1))
            boss_descriptor += " " + boss_data.fortress_name_b[random_number] + ", "

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

