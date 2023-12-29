import pilengine
import random

# Global emojis
stamina_icon = "<:estamina:1145534039684562994>"
exp_icon = "<:eexp:1148088187516891156>"
coin_icon = "🤑"
class_knight = "<:cK:1179727526290010183>"
class_ranger = "<:cB:1179727597819662336>"
class_mage = "<:cM:1179727559173345280>"
class_assassin = "<:cA:1179727392101634109>"
class_weaver = "<:cW:1179727433881092126>"
class_rider = "<:cR:1179727415157731388>"
class_summoner = "<:cS:1179727626890399815>"
class_icon_list = [class_knight, class_ranger, class_mage, class_assassin, class_weaver, class_rider, class_summoner]
class_icon_dict = {"Knight": class_knight, "Ranger": class_ranger, "Mage": class_mage,
                   "Assassin": class_assassin, "Weaver": class_weaver,
                   "Rider": class_rider, "Summoner": class_summoner}
class_name_list = list(class_icon_dict.keys())
path_icon = ["<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>",
             "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>"]

star_icon = "<:Star_PinkBlue:1179736203013140480>"

# Global role list
role_list = ["Player Echelon 1", "Player Echelon 2", "Player Echelon 3", "Player Echelon 4", "Player Echelon 5 (MAX)"]

# Initialize server and channel list
channel_list_wiki = [1140841088005976124, 1141256419161673739, 1148155007305273344]
channel_list = [1157937444931514408, 1157934010090131458, 1157935203394785291, 1157935449462013972, 1157935876853211186]
channel_echelon_dict = {1: 1, 2: 2, 3: 3, 4: 5}
global_server_channels = [channel_list]

# Initialize damage_type lists
element_fire = "<:e1:1179726491311947829>"
element_water = "<:e2:1179726472995405854>"
element_lightning = "<:e3:1179726450056761364>"
element_earth = "<:e4:1179726402296221787>"
element_wind = "<:e5:1179726383224733706>"
element_ice = "<:e6:1179726426509946900>"
element_dark = "<:e7:1179726335678107698>"
element_light = "<:e8:1179726361049452554>"
element_celestial = "<:e9:1179726302480183396>"
omni_icon = "🌈"
global_element_list = [element_fire, element_water, element_lightning, element_earth, element_wind, element_ice,
                       element_dark, element_light, element_celestial]
element_names = ["Fire", "Water", "Lightning", "Earth", "Wind", "Ice", "Shadow", "Light", "Celestial"]
element_special_names = ["Volcanic", "Aquatic", "Voltaic", "Seismic", "Sonic", "Arctic", "Lunar", "Solar", "Cosmic"]
tier_5_ability_dict = {"Elemental Overflow": 2, "Specialist's Mastery": 0.1, "Curse of Immortality": True,
                       "Omega Critical": 1, "Endless Combo": 1, "Crimson Reaper": 1, "Overflowing Vitality": 5,
                       "Ultimate Overdrive": 1, "Unravel": 1}

not_owned_icon = "https://kyleportfolio.ca/botimages/profilecards/noachv.png"
owned_icon = "https://kyleportfolio.ca/botimages/profilecards/owned.png"

global_role_dict = {"Activity Echelon 5 (MAX)": pilengine.echelon_5,
                    "Player Echelon 5 (MAX)": pilengine.echelon_5,
                    "Exclusive Title Holder": pilengine.echelon_5flare}

# Date formatting
date_formatting = '%Y-%m-%d %H:%M:%S'

gem_list = [("Rock", 1), ("Bronze Chunk", 500), ("Silver Chunk", 1000),
            ("Gold Ore", 5000), ("Platinum Ore", 10000), ("Bismuth Ore", 20000),
            ("Silent Topaz", 30000), ("Mist Zircon", 40000), ("Prismatic Opal", 50000),
            ("Whispering Emerald", 75000), ("Drowned Sapphire", 100000), ("Blood Amethyst", 150000),
            ("Soul Diamond", 250000), ("Stygian Ruby", 500000), ("Aurora Tear", 1000000),
            ("Blood of God", 2500000), ("Universe Prism", 5000000), ("Stone of the True Void", 10000000)]


def generate_ramping_reward(success_rate, decay_rate, total_steps):
    current_step = 0
    decay_point = 15
    while current_step < total_steps:
        if random.randint(1, 100) <= success_rate:
            current_step += 1
            if current_step >= decay_point:
                success_rate -= (decay_rate * ((current_step + 1) - decay_point))
        else:
            return current_step
    return current_step


def number_conversion(input_number):
    labels = ['', 'K', 'M', 'B', 'T', 'Q', 'Q+', 'Q++', 'Q+++', 'Q++++']
    num_digits = len(str(input_number))
    index = max(0, (num_digits - 1) // 3)
    input_str = str(input_number)
    integer_digits = (num_digits - 1) % 3 + 1
    integer_part = input_str[:integer_digits]
    decimal_part = input_str[integer_digits:][:2]
    if decimal_part == "00":
        decimal_part = ""
    output_string = f"**{integer_part}.{decimal_part} {labels[index]}**" if decimal_part else f"**{integer_part} {labels[index]}**"

    return output_string


def display_hp(current_hp, max_hp):
    current_hp_converted = number_conversion(current_hp)
    max_hp_converted = number_conversion(max_hp)
    hp_msg = f"{current_hp_converted} / {max_hp_converted}"
    return hp_msg
