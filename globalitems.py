# General imports
import discord
import random


# GENERAL DATA
# Date formatting
date_formatting = '%Y-%m-%d %H:%M:%S'
# Discord Menu Button Colours
button_colour_list = [discord.ButtonStyle.red, discord.ButtonStyle.green,
                      discord.ButtonStyle.blurple, discord.ButtonStyle.secondary]

# BOT DATA
# Discord Lists
bot_admin_ids = [185530717638230016]
channel_list = [1157937444931514408, 1157934010090131458, 1157935203394785291, 1157935449462013972, 1157935876853211186]
global_server_channels = [channel_list]
role_list = ["Player Echelon 1", "Player Echelon 2", "Player Echelon 3", "Player Echelon 4", "Player Echelon 5 (MAX)"]

# ICON DATA
# General Icons
stamina_icon = "<:estamina:1145534039684562994>"
exp_icon, coin_icon = "<:eexp:1148088187516891156>", "<:Lotus_Coin:1201568446136193125>"
# Class Data
class_icon_dict = {"Knight": "<:cK:1179727526290010183>", "Ranger": "<:cB:1179727597819662336>",
                   "Mage": "<:cM:1179727559173345280>", "Assassin": "<:cA:1179727392101634109>",
                   "Weaver": "<:cW:1179727433881092126>",
                   "Rider": "<:cR:1179727415157731388>", "Summoner": "<:cS:1179727626890399815>"}
class_name_list = list(class_icon_dict.keys())
class_icon_list = [class_icon_dict[class_name] for class_name in class_name_list]
# Path Icons
path_icon = ["<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>",
             "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>"]
# Icon Frames
frame_icon_list = ["https://kyleportfolio.ca/botimages/iconframes/Icon_border_Bronze.png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_border_Silver.png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_border_SilverPurple.png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_border_Goldblue.png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_border_Goldred.png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_border_Pink.png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_border_Black.png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_border_Black.png"]
# Star Icons
star_icon = ["<:SB:1201563579330076682>", "<:S1:1201563573202206910>", "<:S2:1201563575433576488>",
             "<:S3:1201563576494731285>", "<:S4:1201563578327633981>", "<:S5:1201815874978189362>",
             "<:S6:1201563580382859375>", "<:S7:1201563581615968296>", "<:S8:1201721242064011284>",
             "<:S9:1201563571788709908>"]
# Augment Icons
augment_icons = ["<:P1:1201567117414244372>", "<:P2:1201567119368798239>", "<:P3:1201567120669036554>",
                 "<:P4:1201567121411407944>", "<:P5:1201567122569048154>", "<:P6:1201567123999313930>",
                 "<:P7:1201567125035286628>", "<:P8:1201567126088056862>", "<:P9:1201567463859556503>"]
# Element Icons
global_element_list = ["<:e1:1179726491311947829>", "<:e2:1179726472995405854>", "<:e3:1179726450056761364>",
                       "<:e4:1179726402296221787>", "<:e5:1179726383224733706>", "<:e6:1179726426509946900>",
                       "<:e7:1179726335678107698>", "<:e8:1179726361049452554>", "<:e9:1179726302480183396>"]
omni_icon = "🌈"

# NAME LISTS
# Path Names
path_names = ["Storms", "Frostfire", "Horizon", "Eclipse", "Stars", "Confluence", "Solitude"]
# Element Names
element_names = ["Fire", "Water", "Lightning", "Earth", "Wind", "Ice", "Shadow", "Light", "Celestial"]
element_special_names = ["Volcanic", "Aquatic", "Voltaic", "Seismic", "Sonic", "Arctic", "Lunar", "Solar", "Cosmic"]
# Boss Types
boss_list = ["Fortress", "Dragon", "Demon", "Paragon", "Arbiter", "Incarnate"]

# DATA STRUCTURES
# Unique Ability Data
rare_ability_dict = {"X Application (Overflow)": ["elemental_application", 2],
                     "X Application (Mastery)": ["class_multiplier", 0.1],
                     "X Application (Immortality)": ["immortal", True],
                     "X Application (Omega)": ["critical_application", 1],
                     "X Application (Combo)": ["combo_application", 1],
                     "X Application (Reaper)": ["bleed_application", 1],
                     "X Application (Overdrive)": ["ultimate_application", 1],
                     "X Application (Unravel)": ["temporal_application", 1],
                     "X Application (Vitality)": ["hp_multiplier", 5]}
# Skill Names
skill_names_dict = {
    "Knight": ["Destructive Cleave", "Merciless Blade", "Ruinous Slash", "Destiny Divider"],
    "Ranger": ["Viper Shot", "Comet Arrow", "Meteor Volley", "Blitz Barrage"],
    "Assassin": ["Wound Carver", "Exploit Injury", "Eternal Laceration", "Blood Recursion"],
    "Mage": ["Magical Bolt", "Aether Blast", "Mystic Maelstrom", "Astral Convergence"],
    "Weaver": ["Power Stitch", "Infused Slice", "Multithreading", "Reality Fabricator"],
    "Rider": ["Valiant Charge", "Surge Dash", "Mounted Onslaught", "Chaos Rampage"],
    "Summoner": ["Savage Blows", "Moonlit Hunt", "Berserk Frenzy", "Synchronized Wrath"]
}
# Weapon lists
availability_list = ["Sword", "Bow", "Threads", "Armour", "Wings", "Amulet"]  # Currently available icons
weapon_list_low = [
    [["Shortsword", "Javelin"],
     ["Sword", "Spear"],
     ["Longsword", "Longspear"],
     ["Greatsword", "Trident"]],
    [["Shortbow", "Ballista"],
     ["Longbow", "Arbalest"],
     ["Recurve Bow", "Gun"],
     ["Greatbow", "Blaster"]],
    [["Staff", "Tome"],
     ["Magic Staff", "Magic Tome"],
     ["Quarterstaff", "Grimoire"],
     ["Crescent Staff", "Spellbook"]],
    [["Dagger", "Claws"],
     ["Stiletto", "Tiger Claws"],
     ["Kris", "Eagle Claws"],
     ["Sai", "Dragon Claws"]],
    [["Steel String"],
     ["Cutting Wire"],
     ["Razor Threads"],
     ["Infused Threads"]],
    [["Pegacorn", "Hatchling"],
     ["Night Mare", "Wyvern"],
     ["Unicorn", "Wyrm"],
     ["Pegasus", "Couatl"]],
    [["Roc", "Viper"],
     ["Garuda", "Cobra"],
     ["Gryphon", "Serpent"],
     ["Horus", "Basilisk"]]
]
weapon_list_high = [
    ["Saber", "Scythe"],
    ["Bow", "Cannon"],
    ["Rod", "Codex"],
    ["Bloodletter", "Talons"],
    ["Threads"],
    ["Underworld-Usurper Cerberus", "Time-Transgressor Dragon"],
    ["Sky-Sovereign Manta", "Eon-Eater Leviathan"]
]
# Build Category Dictionary
category_names = {
    0: {0: "Sword", 1: "Spear"},
    1: {0: "Bow", 1: "Launcher"},
    2: {0: "Staff", 1: "Tome"},
    3: {0: "Dagger", 1: "Claws"},
    4: {0: "Threads"},
    5: {0: "Ground", 1: "Dragon"},
    6: {0: "Flying", 1: "Serpent"}
}
gear_category_dict = {}
for class_index, (low_type, high_type) in enumerate(zip(weapon_list_low, weapon_list_high)):
    categories = category_names[class_index]
    for tier_list in low_type:
        for idx, item in enumerate(tier_list):
            if idx in categories:
                gear_category_dict[item] = categories[idx]
    for idx, variant in enumerate(high_type):
        if idx in categories:
            gear_category_dict[variant] = categories[idx]

