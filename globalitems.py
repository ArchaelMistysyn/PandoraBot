# General imports
import discord
import random


# GENERAL DATA
# Date formatting
date_formatting = '%Y-%m-%d %H:%M:%S'
# Discord Menu Button Colours
button_colour_list = [discord.ButtonStyle.red, discord.ButtonStyle.green,
                      discord.ButtonStyle.blurple, discord.ButtonStyle.secondary]
# Hex color codes for each tier: [Dark Gray, Green, Blue, Purple, Gold, Red, Pink, White, Black]
tier_colors = {0: 0x2C2F33, 1: 0x43B581, 2: 0x3498DB, 3: 0x9B59B6, 4: 0xF1C40F,
               5: 0xCC0000, 6: 0xE91E63, 7: 0xFFFFFF, 8: 0x000000, 9: 0x000000}

# BOT DATA
# Discord Lists
bot_admin_ids = [185530717638230016]
channel_list = [1157937444931514408, 1157934010090131458, 1157935203394785291, 1157935449462013972, 1157935876853211186]
global_server_channels = [channel_list]

# ICON DATA
# General Icons
stamina_icon = "<:estamina:1145534039684562994>"
exp_icon, coin_icon = "<:eexp:1148088187516891156>", "<:Lotus_Coin:1201568446136193125>"
# Class Data
class_icon_dict = {"Knight": "<:cK:1179727526290010183>", "Ranger": "<:cB:1179727597819662336>",
                   "Mage": "<:cM:1179727559173345280>", "Assassin": "<:cA:1179727392101634109>",
                   "Weaver": "<:cW:1179727433881092126>",
                   "Rider": "<:cR:1179727415157731388>", "Summoner": "<:cS:1179727626890399815>"}
class_names = list(class_icon_dict.keys())
class_icon_list = [class_icon_dict[class_name] for class_name in class_names]
# Path Icons
path_icon = ["<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>",
             "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>"]
# Icon Frames
frame_icon_list = ["https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_Bronze_[EXT].png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_Silver_[EXT].png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_SilverPurple_[EXT].png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_Goldblue_[EXT].png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_Goldred_[EXT].png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_Pink_[EXT].png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_Black_[EXT].png",
                   "https://kyleportfolio.ca/botimages/iconframes/Icon_Border_[EXT]/Icon_border_white_[EXT].png"]
frame_extension = ["106px", "1484px"]
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
    ["Cerberus", "Dragon"],
    ["Sky Manta", "Leviathan"]
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

# Quality Map
quality_damage_map = {
    (4, 1): "Prelude", (4, 2): "Fabled", (4, 3): "Heroic", (4, 4): "Mythic", (4, 5): "Legendary",
    (5, 1): "Prelude", (5, 2): "Abject", (5, 3): "Hollow", (5, 4): "Abyssal", (5, 5): "Emptiness",
    (6, 1): "Prelude", (6, 2): "Opalescent", (6, 3): "Prismatic", (6, 4): "Resplendent", (6, 5): "Iridescent",
    (7, 1): "Prelude", (7, 2): "Tainted", (7, 3): "Cursed", (7, 4): "Corrupt", (7, 5): "Fallen",
    (8, 1): "Prelude", (8, 2): "Majestic", (8, 3): "Sanctified", (8, 4): "Radiant", (8, 5): "Transcendent",
}


# HP Bars
t5_hp_bar_empty = ["<:HP_Bar_Empty_03:1176059083204337744>", "<:HP_Bar_Empty_04:1176059084840124458>",
                   "<:HP_Bar_Empty_05:1176059085951606856>", "<:HP_Bar_Empty_06:1176059046617428039>",
                   "<:HP_Bar_Empty_07:1176059047607287888>", "<:HP_Bar_Empty_08:1176059049293393930>",
                   "<:HP_Bar_Empty_09:1176059050186788934>", "<:HP_Bar_Empty_10:1176059050979512370>",
                   "<:HP_Bar_Empty_11:1176059052325879879>", "<:HP_Bar_Empty_12:1176059019119558776>",
                   "<:HP_Bar_Empty_13:1176059020365266995>", "<:HP_Bar_Empty_14:1176059021724237895>",
                   "<:HP_Bar_Empty_15:1176059022802161694>", "<:HP_Bar_Empty_16:1176059023599075328>",
                   "<:HP_Bar_Empty_17:1176059025721393162>"]
t5_hp_bar_full = ["<:HP_Bar_Full_03:1176053423049822219>", "<:HP_Bar_Full_04:1176053419346235403>",
                  "<:HP_Bar_Full_05:1176053420914905139>", "<:HP_Bar_Full_06:1176053422127054888>",
                  "<:HP_Bar_Full_07:1176053399561711626>", "<:HP_Bar_Full_08:1176053401029718036>",
                  "<:HP_Bar_Full_09:1176053402132820048>", "<:HP_Bar_Full_10:1176053403193987133>",
                  "<:HP_Bar_Full_11:1176056919396470824>", "<:HP_Bar_Full_12:1176053365298450526>",
                  "<:HP_Bar_Full_13:1176053366321852416>", "<:HP_Bar_Full_14:1176053367563362354>",
                  "<:HP_Bar_Full_15:1176053368293175346>", "<:HP_Bar_Full_16:1176053369320775761>",
                  "<:HP_Bar_Full_17:1176053370876870659>"]
hp_bar_dict = {1: [t5_hp_bar_full, t5_hp_bar_empty], 2: [t5_hp_bar_full, t5_hp_bar_empty],
               3: [t5_hp_bar_full, t5_hp_bar_empty], 4: [t5_hp_bar_full, t5_hp_bar_empty],
               5: [t5_hp_bar_full, t5_hp_bar_empty], 6: [t5_hp_bar_full, t5_hp_bar_empty],
               7: [t5_hp_bar_full, t5_hp_bar_empty]}
