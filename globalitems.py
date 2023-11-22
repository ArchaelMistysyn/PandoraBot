import pilengine
import random

# Global emojis
stamina_icon = "<:estamina:1145534039684562994>"
exp_icon = "<:eexp:1148088187516891156>"
coin_icon = "🤑"
class_knight = "<:cB:1154266777396711424>"
class_ranger = "<:cA:1150195102589931641>"
class_mage = "<:cC:1150195246588764201>"
class_assassin = "❌"
class_weaver = "❌"
class_rider = "❌"
class_summoner = "<:cD:1150195280969478254>"
class_icon_list = [class_knight, class_ranger, class_mage, class_assassin, class_weaver, class_rider, class_summoner]
class_icon_dict = {"Knight": class_knight, "Ranger": class_ranger, "Mage": class_mage,
                   "Assassin": class_assassin, "Weaver": class_weaver,
                   "Rider": class_rider, "Summoner": class_summoner}
path_icon = ["<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>",
             "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>"]

# Global role list
role_list = ["Player Echelon 1", "Player Echelon 2", "Player Echelon 3", "Player Echelon 4", "Player Echelon 5 (MAX)"]

# Initialize server and channel list
channel_list_wiki = [1140841088005976124, 1141256419161673739, 1148155007305273344]
channel_list = [1157937444931514408, 1157934010090131458, 1157935203394785291, 1157935449462013972, 1157935876853211186]
channel_echelon_dict = {1: 1, 2: 2, 3: 3, 4: 5}
global_server_channels = [channel_list]

# Initialize damage_type lists
element_fire = "<:ee:1141653476816986193>"
element_water = "<:ef:1141653475059572779>"
element_lightning = "<:ei:1141653471154671698>"
element_earth = "<:eh:1141653473528664126>"
element_wind = "<:eg:1141653474480767016>"
element_ice = "<:em:1141647050342146118>"
element_dark = "<:ek:1141653468080242748>"
element_light = "<:el:1141653466343800883>"
element_celestial = "<:ej:1141653469938339971>"
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

