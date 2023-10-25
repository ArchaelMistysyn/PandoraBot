import pilengine

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

# Global role list
role_list = ["Player Echelon 1", "Player Echelon 2", "Player Echelon 3", "Player Echelon 4", "Player Echelon 5 (MAX)"]

# Initialize server and channel list
channel_list_wiki = [1140841088005976124, 1141256419161673739, 1148155007305273344]
channel_list = [1157937444931514408, 1157934010090131458, 1157935203394785291, 1157935449462013972, 1157935876853211186]
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
tier_5_ability_list = ["Elemental Fractal", "Specialist's Mastery", "Curse of Immortality", "Omega Critical"]

not_owned_icon = "https://kyleportfolio.ca/botimages/profilecards/noachv.png"
owned_icon = "https://kyleportfolio.ca/botimages/profilecards/owned.png"
global_role_dict = {"Achv Role - Knife Rat": owned_icon,
                    "Achv Role - Koin Kollektor": owned_icon,
                    "Notification Role - Movie Lover": owned_icon,
                    "Notification Role - Signal Flare": owned_icon,
                    "Achv Role - All Nighter": owned_icon,
                    "Achv Role - Reactive": owned_icon,
                    "Achv Role - Message Master": owned_icon,
                    "Achv Role - Endless Gaming": owned_icon,
                    "Achv Role - Infinite Time": owned_icon,
                    "Achv Role - Feng Hao Dou Luo": owned_icon,
                    "Achv Role - ": owned_icon,
                    "Activity Echelon 5 (MAX)": pilengine.echelon_5,
                    "Player Echelon 5 (MAX)": pilengine.echelon_5,
                    "Achv Role - Exclusive Title Holder": pilengine.echelon_5flare}

# Date formatting
date_formatting = '%Y-%m-%d %H:%M:%S'
