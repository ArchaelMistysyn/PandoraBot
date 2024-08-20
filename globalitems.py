# General imports
import discord
import random
import hp_bars

# GENERAL DATA
# Date formatting
date_formatting = '%Y-%m-%d %H:%M:%S'
# Discord Menu Button Colours
button_colour_list = [discord.ButtonStyle.red, discord.ButtonStyle.green,
                      discord.ButtonStyle.blurple, discord.ButtonStyle.secondary]
# Hex color codes for each tier: [Dark Gray, Green, Blue, Purple, Gold, Red, Pink, Black, White]
tier_colors = {0: 0x2C2F33, 1: 0x43B581, 2: 0x3498DB, 3: 0x9B59B6, 4: 0xF1C40F,
               5: 0xCC0000, 6: 0xE91E63, 7: 0x000000, 8: 0xFFFFFF, 9: 0xFFFFFF}

# BOT DATA
# Discord Lists
# Server ID: ([command channels], raid channel, notification channel, announcement channel)
servers = {1011375205999968427: ([1157937444931514408],
                                 1252681803916116211, 1157937444931514408, 1157937444931514408)}
GM_id_dict = {185530717638230016: "Archael", 141837266866667520: "Zweii", 353090154044325906: "Viper",
              1177738094666059877: "Eleuia"}
bot_logging_channel = 1266478401846247454
reverse_GM_id_dict = {value: key for key, value in GM_id_dict.items()}
web_url = "https://kyleportfolio.ca/botimages/"
store_link = "https://ArchDragonStore.ca"

# IMAGE DATA
forge_img, refinery_img = f"{web_url}scenes/Forge.png", f"{web_url}scenes/Refinery.png"
abyss_img = f"{web_url}scenes/Abyss.png"
planetarium_img = f"{web_url}scenes/Tarot_Planetarium.png"
market_img, bazaar_img = "", ""
infuse_img = f"{web_url}scenes/Infuse.png"
sanctuary_img, cathedral_img = f"{web_url}scenes/Sanctuary.png", f"{web_url}scenes/Cathedral.png"
palace_night_img, palace_day_img = f"{web_url}scenes/Palace1.png", f"{web_url}scenes/Palace2.png"
map_img = f"{web_url}scenes/Map.png"
archdragon_logo = f"{web_url}ArchDragon.png"

# ICON DATA
# General Icons
archdragon_emoji = "<:ArchDragon:1274784590715686953>"
stamina_icon = "<:estamina:1145534039684562994>"
exp_icon, coin_icon = "<:eexp:1148088187516891156>", "<:Coin:1274784200133705830>"
# Class Data
class_icon_dict = {
    "Knight": "<:c1:1274783624834711685>",
    "Ranger": "<:c2:1274783343338193027>",
    "Mage": "<:c3:1274783722625054510>",
    "Assassin": "<:c4:1274784066012708979>",
    "Weaver": "<:c5:1274784117640265739>",
    "Rider": "<:c6:1274784093665628161>",
    "Summoner": "<:c7:1274784040997884068>"
}
class_names = list(class_icon_dict.keys())
class_icon_list = [class_icon_dict[class_name] for class_name in class_names]
# Path Icons
path_icon = ["<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>",
             "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>",
             "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>", "<a:eenergy:1145534127349706772>"]
# Icon Frames
frame_icon_list = [f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_Bronze_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_Silver_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_SilverPurple_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_Goldblue_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_Goldred_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_Pink_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_Black_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_white_[EXT].png",
                   f"{web_url}iconframes/Icon_Border_[EXT]/Icon_border_Ruby_[EXT].png"]
frame_extension = ["106px", "1484px"]
# Star Icons
star_icon = ["<:SB:1274787239473315942>", "<:S1:1274787087375270020>", "<:S2:1274787094476230779>",
             "<:S3:1274787131922841724>", "<:S4:1274787139942613002>", "<:S5:1274787147588567132>",
             "<:S6:1274787156912504912>", "<:S7:1274787187975786528>", "<:S8:1274787195865272451>",
             "<:S9:1274787218980077569>"]
# Augment Icons
augment_icons = ["<:P1:1274786991954727034>", "<:P2:1274786999089365093>", "<:P3:1274787006391652513>",
                 "<:P4:1274787012385181697>", "<:P5:1274787019918282846>", "<:P6:1274787027610636400>",
                 "<:P7:1274787035797917837>", "<:P8:1274787043007795210>", "<:P9:1274787052109430824>"]
# Element Icons
ele_icon = [
    "<:e0:1274784343268655206>",
    "<:e1:1274784381931753585>",
    "<:e2:1274784367247622234>",
    "<:e3:1274784335010070598>",
    "<:e4:1274784388915134495>",
    "<:e5:1274784350977658924>",
    "<:e6:1274784375271198771>",
    "<:e7:1274784358603161730>",
    "<:e8:1274784236876075068>"
]
omni_icon = "🌈"
element_dict = {
    'Fire': [0], 'Water': [1], 'Lightning': [2], 'Earth': [3], 'Wind': [4],
    'Ice': [5], 'Shadow': [6], 'Light': [7], 'Celestial': [8],
    'Storms': [1, 2], 'Frostfire': [0, 5], 'Eclipse': [7, 6], 'Horizon': [3, 4], 'Stars': [8],
    'Solar': [0, 7, 4], 'Lunar': [1, 5, 6], 'Terrestria': [2, 3, 8], 'Chaos': [0, 6, 2, 3], 'Holy': [1, 7, 4, 5],
    'Confluence': [0, 1, 2, 3, 4, 5, 6, 7, 8]}
gear_types = ['Weapon', 'Armour', 'Greaves', 'Amulet', 'Ring', 'Wings', 'Crest', 'Gem']
gear_icons = ['<:Sword5:1246945708939022367>', '<:Armour5:1246945463630823438>', '<:Greaves5:1246945410707095565>',
              '<:Amulet5:1246945347637346315>', '<:E_Ring0:1253839617799487568>', '<:Wings5:1246945596821082197>',
              '<:Crest5:1246945508048637972>', '<:Gem5:1242206603441078363>']

# NAME LISTS
# Path Names
path_names = ["Storms", "Frostfire", "Horizon", "Eclipse", "Stars",
              "Solar Flux", "Lunar Tides", "Terrestria", "Confluence"]
# Element Names
element_names = ["Fire", "Water", "Lightning", "Earth", "Wind", "Ice", "Shadow", "Light", "Celestial"]
element_special_names = ["Volcanic", "Aquatic", "Voltaic", "Seismic", "Cyclonic", "Arctic", "Lunar", "Solar", "Cosmic"]
element_status_list = [None, None, "paralyzed", "petrified", None, "frozen", None, "blinded", "disoriented"]

# Boss Types
boss_list = ["Fortress", "Dragon", "Demon", "Paragon", "Arbiter", "Incarnate", "Ruler"]
raid_bosstype_list = ["Ruler"]
# DATA STRUCTURES
# Unique Ability Data
rare_ability_dict = {"Overflow": ["Elemental", 2], "Mastery": ["class_multiplier", 0.1],
                     "Immortality": ["immortal", True], "Omega": ["Critical", 1],
                     "Combo": ["Combo", 1], "Reaper": ["Bleed", 1],
                     "Overdrive": ["Ultimate", 1], "Unravel": ["Temporal", 1],
                     "Vitality": ["Life", 1], "Manatide": ["Mana", 1]}
# Skill Names
skill_names_dict = {
    "Knight": ["Destructive Cleave", "Merciless Blade", "Ruinous Slash", "Destiny Divider"],
    "Ranger": ["Viper Shot", "Comet Arrow", "Meteor Volley", "Blitz Barrage"],
    "Assassin": ["Wound Carver", "Exploit Injury", "Eternal Laceration", "Blood Recursion"],
    "Mage": ["Magical Bolt", "Aether Blast", "Mystic Maelstrom", "Astral Convergence"],
    "Weaver": ["Power Stitch", "Infused Slice", "Multithreading", "Reality Fabricator"],
    "Rider": ["Valiant Charge", "Surge Dash", "Mounted Onslaught", "Chaos Rampage"],
    "Summoner": ["Savage Blows", "Moonlit Hunt", "Berserk Frenzy", "Synchronized Wrath"]}

# ITEM LISTS
crafting_gem = ["Blazing Ruby", "Drowned Sapphire", "Silent Topaz", "Ancient Agate", "Whispering Emerald",
                "Arctic Zircon", "Haunted Obsidian", "Prismatic Opal", "Spatial Lapis", "Soul Diamond"]
availability_list_nongear = ["Gemstone", "Fragment", "Crystal", "Heart", "Skull", "Misc"]
availability_list = ["Sword", "Saber", "Bow", "Threads", "Armour", "Wings", "Amulet", "Crest", "Greaves",
                     "Ring", "Gem", "Pact", "Dagger", "Mirrorblades", "Wand", "Caduceus Rod", "Mare", "Unicorn"]

sovereign_item_list = ["Crown of Skulls", "Twin Rings of Divergent Stars", "Hadal's Raindrop", "Heavenly Calamity",
                       "Stygian Calamity", "Pandora's Universe Hammer", "Solar Flare Blaster", "Ruler's Crest",
                       "Bathyal, Enigmatic Chasm Bauble", "Fallen Lotus of Nephilim", "Chromatic Tears"]
available_sovereign = ["Crown of Skulls", "Twin Rings of Divergent Stars", "Hadal's Raindrop", "Heavenly Calamity",
                       "Stygian Calamity", "Pandora's Universe Hammer", "Ruler's Crest", "Fallen Lotus of Nephilim"]
ring_item_type = [None, None, None, "Signet", "Element_Ring", "Path_Ring", "Fabled_Ring", "Sovereign_Ring", "Sacred_Ring"]
sovereign_batch_data = ', '.join([str(base_type) for base_type in sovereign_item_list])

# WEAPON LISTS
# Class: [[tier 1-4 bases], [tier 1-8 bases], [tier 5-8 bases]]
weapon_type_dict = {"Knight": [["Sword"], [], ["Saber", "Scythe"]],
                    "Ranger": [[], ["Bow"], ["Blaster"]],
                    "Assassin": [["Dagger"], [], ["Mirrorblades", "Claws"]],
                    "Mage": [["Wand"], [], ["Codex", "Caduceus Rod"]],
                    "Weaver": [[], ["Threads"], []],
                    "Rider": [["Hatchling", "Mare"], [], ["Dragon", "Unicorn"]],
                    "Summoner": [["Serpent"], [], ["Basilisk", "Cerberus"]]}

# Quality Map
quality_damage_map = {
    (4, 1): "Prelude", (4, 2): "Fabled", (4, 3): "Heroic", (4, 4): "Mythic", (4, 5): "Legendary",
    (5, 1): "Prelude", (5, 2): "Abject", (5, 3): "Hollow", (5, 4): "Abyssal", (5, 5): "Emptiness",
    (6, 1): "Prelude", (6, 2): "Opalescent", (6, 3): "Prismatic", (6, 4): "Resplendent", (6, 5): "Iridescent",
    (7, 1): "Prelude", (7, 2): "Tainted", (7, 3): "Cursed", (7, 4): "Corrupt", (7, 5): "Fallen",
    (8, 1): "Prelude", (8, 2): "Majestic", (8, 3): "Sanctified", (8, 4): "Radiant", (8, 5): "Transcendent",
    (9, 1): "MAX", (9, 2): "MAX", (9, 3): "MAX", (9, 4): "MAX", (9, 5): "MAX"}

# Max Enhancement by Tier
max_enhancement = [10, 20, 30, 40, 50, 100, 150, 200, 200]
# Attack Speed Ranges by Tier
speed_range_list = [(1.00, 1.10), (1.10, 1.20), (1.20, 1.30), (1.30, 1.50),
                    (1.50, 2.00), (2.00, 2.50), (2.50, 3.00), (3.00, 3.50), (4.00, 4.00)]
# Damage tier list
damage_tier_list = [[500, 5000], [5000, 7500], [7500, 10000], [10000, 15000],
                    [15000, 25000], [25000, 50000], [50000, 100000], [100000, 200000], [250000, 250000]]

# HP Bars
hp_bar_dict = {1: [hp_bars.t1_hpbar_full, hp_bars.t1_hpbar_empty], 2: [hp_bars.t2_hpbar_full, hp_bars.t2_hpbar_empty],
               3: [hp_bars.t3_hpbar_full, hp_bars.t3_hpbar_empty], 4: [hp_bars.t4_hpbar_full, hp_bars.t4_hpbar_empty],
               5: [hp_bars.t5_hpbar_full, hp_bars.t57_hpbar_empty], 6: [hp_bars.t6_hpbar_full, hp_bars.t68_hpbar_empty],
               7: [hp_bars.t7_hpbar_full, hp_bars.t57_hpbar_empty], 8: [hp_bars.t8_hpbar_full, hp_bars.t68_hpbar_empty]}

# MESSAGES
abyss_msg = ("Within the abyssal plane resides the Deep Void. The taint of the void can only be purified "
             "through a more powerful darkness. Take great caution, dive too deep and nothing can pull you back out.")
