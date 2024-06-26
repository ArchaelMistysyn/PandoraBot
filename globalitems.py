# General imports
import discord
import random

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
bot_admin_ids = [185530717638230016]
# Server ID: ([command channels], raid channel, notification channel, announcement channel)
servers = {1011375205999968427: ([1157937444931514408],
                                 1252681803916116211, 1157937444931514408, 1157937444931514408)}
GM_id_dict = {185530717638230016: "Archael", 141837266866667520: "Zweii", 353090154044325906: "Viper",
              1177738094666059877: "Eleuia"}
web_url = "https://kyleportfolio.ca/botimages/"

# IMAGE DATA
forge_img, refinery_img = f"{web_url}scenes/Forge.png", f"{web_url}scenes/Refinery.png"
abyss_img = f"{web_url}scenes/Abyss.png"
planetarium_img = f"{web_url}scenes/Tarot_Planetarium.png"
market_img, bazaar_img = "", ""
infuse_img = f"{web_url}scenes/Infuse.png"
sanctuary_img, cathedral_img = "", ""
archdragon_logo = f"{web_url}ArchDragon.png"

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
star_icon = ["<:SB:1201563579330076682>", "<:S1:1201563573202206910>", "<:S2:1201563575433576488>",
             "<:S3:1201563576494731285>", "<:S4:1201563578327633981>", "<:S5:1201815874978189362>",
             "<:S6:1201563580382859375>", "<:S7:1201563581615968296>", "<:S8:1201721242064011284>",
             "<:S9:1201563571788709908>"]
# Augment Icons
augment_icons = ["<:P1:1201567117414244372>", "<:P2:1201567119368798239>", "<:P3:1201567120669036554>",
                 "<:P4:1201567121411407944>", "<:P5:1201567122569048154>", "<:P6:1201567123999313930>",
                 "<:P7:1201567125035286628>", "<:P8:1201567463859556503>", "<:PX:1201567126088056862>"]
# Element Icons
ele_icon = ["<:e1:1179726491311947829>", "<:e2:1179726472995405854>", "<:e3:1179726450056761364>",
            "<:e4:1179726402296221787>", "<:e5:1179726383224733706>", "<:e6:1179726426509946900>",
            "<:e7:1179726335678107698>", "<:e8:1179726361049452554>", "<:e9:1179726302480183396>"]
omni_icon = "🌈"
element_dict = {
    'Fire': [0], 'Water': [1], 'Lightning': [2], 'Earth': [3], 'Wind': [4],
    'Ice': [5], 'Shadow': [6], 'Light': [7], 'Celestial': [8],
    'Storms': [1, 2], 'Frostfire': [0, 5], 'Eclipse': [7, 6], 'Horizon': [3, 4], 'Stars': [8],
    'Solar': [0, 7, 4], 'Lunar': [1, 5, 6], 'Terrestria': [2, 3, 8], 'Chaos': [0, 6, 2, 3], 'Holy': [1, 7, 4, 5],
    'Confluence': [0, 1, 2, 3, 4, 5, 6, 7, 8]}

# NAME LISTS
# Path Names
path_names = ["Storms", "Frostfire", "Horizon", "Eclipse", "Stars",
              "Solar Flux", "Lunar Tides", "Terrestria", "Confluence"]
# Element Names
element_names = ["Fire", "Water", "Lightning", "Earth", "Wind", "Ice", "Shadow", "Light", "Celestial"]
element_special_names = ["Volcanic", "Aquatic", "Voltaic", "Seismic", "Sonic", "Arctic", "Lunar", "Solar", "Cosmic"]
element_status_list = [None, None, "paralyzed", "petrified", None, "frozen", None, "blinded", "disoriented"]

# Boss Types
boss_list = ["Fortress", "Dragon", "Demon", "Paragon", "Arbiter", "Incarnate", "Ruler"]

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
availability_list_nongear = ["Fae"]
availability_list = ["Sword", "Saber", "Bow", "Threads", "Armour", "Wings", "Amulet", "Crest", "Greaves",
                     "Ring", "Gem", "Pact"]

sovereign_item_list = ["Crown of Skulls", "Twin Rings of Divergent Stars", "Hadal's Raindrop", "Heavenly Calamity",
                       "Stygian Calamity", "Pandora's Universe Hammer", "Solar Flare Blaster",
                       "Bathyal, Enigmatic Chasm Bauble", "Fallen Lotus of Nephilim"]
ring_item_type = [None, None, None, "Signet", "Element_Ring", "Path_Ring", "Fabled_Ring", "Sovereign_Ring", "Sacred_Ring"]
sovereign_batch_data = ', '.join([str(base_type) for base_type in sovereign_item_list])

# WEAPON LISTS
# Class: [[tier 1-4 bases], [tier 1-8 bases], [tier 5-8 bases]]
weapon_type_dict = {"Knight": [["Sword"], [], ["Saber", "Scythe"]],
                    "Ranger": [[], ["Bow"], ["Blaster"]],
                    "Assassin": [[], ["Dagger"], ["Claws"]],
                    "Mage": [[], ["Rod"], ["Codex"]],
                    "Weaver": [[], ["Threads"], []],
                    "Rider": [["Hatchling", "Mare"], [], ["Dragon", "Pegasus"]],
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
                    (1.50, 2.00), (2.00, 2.50), (2.50, 3.00), (3.00, 3.50), (3.50, 4.00)]
# Damage tier list
damage_tier_list = [[500, 5000], [5000, 7500], [7500, 10000], [10000, 15000],
                    [15000, 25000], [25000, 50000], [50000, 100000], [100000, 200000], [250000, 250000]]

# HP Bars
t1_hpbar_full = ['<:t1f_01:1248467244422402101>', '<:t1f_02:1248467245294944257>', '<:t1f_03:1248467246368423966>',
                 '<:t1f_04:1248467246997573654>', '<:t1f_05:1248467243063312414>', '<:t1f_06:1248467281563095110>',
                 '<:t1f_07:1248467282355687508>', '<:t1f_08:1248467283291017247>', '<:t1f_09:1248467283999985756>',
                 '<:t1f_10:1248467280434565121>', '<:t1f_11:1248467296834424914>', '<:t1f_12:1248467297467891724>',
                 '<:t1f_13:1248467298818199695>', '<:t1f_14:1248467299598336001>', '<:t1f_15:1248467296037503108>']
t1_hpbar_empty = ['<:t1e_01:1248099751703089214>', '<:t1e_02:1248099752588087318>', '<:t1e_03:1248099753435201576>',
                  '<:t1e_04:1248099754605416518>', '<:t1e_05:1248099750805504120>', '<:t1e_06:1248099774037626931>',
                  '<:t1e_07:1248099775379935234>', '<:t1e_08:1248099776939954176>', '<:t1e_09:1248099778001240188>',
                  '<:t1e_10:1248099773492367431>', '<:t1e_11:1248099801833275514>', '<:t1e_12:1248099803762659328>',
                  '<:t1e_13:1248099804286943345>', '<:t1e_14:1248099805616668703>', '<:t1e_15:1248099801082626109>']
t2_hpbar_full = ['<:t2f_01:1248099939238674432>', '<:t2f_02:1248099940371005542>', '<:t2f_03:1248099941004349492>',
                 '<:t2f_04:1248099942074155140>', '<:t2f_05:1248099936927744093>', '<:t2f_06:1248099983232602223>',
                 '<:t2f_07:1248099984084176948>', '<:t2f_08:1248099984897740903>', '<:t2f_09:1248099980766613504>',
                 '<:t2f_10:1248099982288879646>', '<:t2f_11:1248100009501786112>', '<:t2f_12:1248100010436857869>',
                 '<:t2f_13:1248100011552673853>', '<:t2f_14:1248471244320280676>', '<:t2f_15:1248471244802883646>']
t2_hpbar_empty = ['<:t2e_01:1248371642464338052>', '<:t2e_02:1248371644058173501>', '<:t2e_03:1248371645039771709>',
                  '<:t2e_04:1248371646226763877>', '<:t2e_05:1248371641944248402>', '<:t2e_06:1248371665105191034>',
                  '<:t2e_07:1248371665872617583>', '<:t2e_08:1248371667202215976>', '<:t2e_09:1248371668133478512>',
                  '<:t2e_10:1248371664295559168>', '<:t2e_11:1248471640522625085>', '<:t2e_12:1248371681840332821>',
                  '<:t2e_13:1248371682855616532>', '<:t2e_14:1248371683811917834>', '<:t2e_15:1248371680380850297>']
t3_hpbar_full = ['<:t3f_01:1248102694573576295>', '<:t3f_02:1248102695588462664>', '<:t3f_03:1248102696330989630>',
                 '<:t3f_04:1248471868915060776>', '<:t3f_05:1248102693331800148>', '<:t3f_06:1248102712420208703>',
                 '<:t3f_07:1248102713338761216>', '<:t3f_08:1248102714605572116>', '<:t3f_09:1248102715738030120>',
                 '<:t3f_10:1248102711396929537>', '<:t3f_11:1248471867933720678>', '<:t3f_12:1248102742485106718>',
                 '<:t3f_13:1248102743369973770>', '<:t3f_14:1248102744489984120>', '<:t3f_15:1248102740870037575>']
t3_hpbar_empty = ['<:t3e_01:1248371730897047592>', '<:t3e_02:1248371731773784277>', '<:t3e_03:1250830258668568637>',
                  '<:t3e_04:1248371733497511936>', '<:t3e_05:1248371730104455320>', '<:t3e_06:1248371884370690058>',
                  '<:t3e_07:1248371885259882599>', '<:t3e_08:1248371881606774855>', '<:t3e_09:1248371882575794326>',
                  '<:t3e_10:1248371883498410054>', '<:t3e_11:1248371901508882534>', '<:t3e_12:1248371902754455622>',
                  '<:t3e_13:1248371903366824009>', '<:t3e_14:1248475598590836797>', '<:t3e_15:1248371900606844969>']
t4_hpbar_full = ['<:t4f_01:1248102798697168908>', '<:t4f_02:1248102799640760413>', '<:t4f_03:1248102800504655933>',
                 '<:t4f_04:1248102800999845889>', '<:t4f_05:1248102797380026451>', '<:t4f_06:1248103029358460959>',
                 '<:t4f_07:1248103030109503540>', '<:t4f_08:1248103031355211848>', '<:t4f_09:1248103027370627154>',
                 '<:t4f_10:1248103028314210425>', '<:t4f_11:1248103052301303839>', '<:t4f_12:1248103052871729255>',
                 '<:t4f_13:1248103053618446381>', '<:t4f_14:1248103054788792342>', '<:t4f_15:1248103051307515954>']
t4_hpbar_empty = ['<:t4e_01:1248103130281934968>', '<:t4e_02:1248103131124989994>', '<:t4e_03:1248103132030832731>',
                  '<:t4e_04:1248103132886597675>', '<:t4e_05:1248103129216454727>', '<:t4e_06:1248103151903572022>',
                  '<:t4e_07:1248103152994091080>', '<:t4e_08:1248103154151718932>', '<:t4e_09:1248103154931994634>',
                  '<:t4e_10:1248103151131955201>', '<:t4e_11:1248103174770921482>', '<:t4e_12:1248103175496536077>',
                  '<:t4e_13:1248103176654295040>', '<:t4e_14:1248472210373480568>', '<:t4e_15:1248103173839786005>']
t5_hpbar_full = ['<:t5f_01:1248103266202681357>', '<:t5f_02:1248103267850911764>', '<:t5f_03:1248103268752691261>',
                 '<:t5f_04:1248103269637820426>', '<:t5f_05:1248103265204441161>', '<:t5f_06:1248103279418806353>',
                 '<:t5f_07:1248103280400273428>', '<:t5f_08:1248103281452908544>', '<:t5f_09:1248103282707136552>',
                 '<:t5f_10:1248103278051459224>', '<:t5f_11:1248103296351211540>', '<:t5f_12:1248103297181548595>',
                 '<:t5f_13:1248103298083323976>', '<:t5f_14:1248103294262575185>', '<:t5f_15:1248103295311151206>']
t57_hpbar_empty = ['<:t57e_01:1248861341981347880>', '<:t57e_02:1248861343004753980>', '<:t57e_03:1248861344275632219>',
                   '<:t57e_04:1248861345445576796>', '<:t57e_05:1248861340601159713>', '<:t57e_06:1248861373589491722>',
                   '<:t57e_07:1248861374508044440>', '<:t57e_08:1248861375476797521>', '<:t57e_09:1248861376315916308>',
                   '<:t57e_10:1248861372822061096>', '<:t57e_11:1248861420465164318>', '<:t57e_12:1248861421408616518>',
                   '<:t57e_13:1248861421777719369>', '<:t57e_14:1248861423032074371>', '<:t57e_15:1248861424114204764>']
t6_hpbar_full = ['<:t6f_01:1248103331008610304>', '<:t6f_02:1248103331877093427>', '<:t6f_03:1248103332753440830>',
                 '<:t6f_04:1248103333718265866>', '<:t6f_05:1248103330115485736>', '<:t6f_06:1248103343440789526>',
                 '<:t6f_07:1248103344707338332>', '<:t6f_08:1248103345684480030>', '<:t6f_09:1248103346641047623>',
                 '<:t6f_10:1248103342841008221>', '<:t6f_11:1248103415587012608>', '<:t6f_12:1248103356216508448>',
                 '<:t6f_13:1248103356690599978>', '<:t6f_14:1248103357969596527>', '<:t6f_15:1248472998974066688>']
t7_hpbar_full = ['<:t7f_01:1248103659343052870>', '<:t7f_02:1248103660387303455>', '<:t7f_03:1248482190879100928>',
                 '<:t7f_04:1248103667769278586>', '<:t7f_05:1248482189881118780>', '<:t7f_06:1248103680109182976>',
                 '<:t7f_07:1248103680679612429>', '<:t7f_08:1248103681908412477>', '<:t7f_09:1248103682831028389>',
                 '<:t7f_10:1248103674702598206>', '<:t7f_11:1248103703114940458>', '<:t7f_12:1248103703488106550>',
                 '<:t7f_13:1250826236499071060>', '<:t7f_14:1248103700963004508>', '<:t7f_15:1248103702347124748>']
t68_hpbar_empty = ['<:t68e_01:1248104171614376078>', '<:t68e_02:1248104172734255184>', '<:t68e_03:1248104173354881087>',
                   '<:t68e_04:1248472662959984751>', '<:t68e_05:1248104170301554730>', '<:t68e_06:1248104185346658406>',
                   '<:t68e_07:1248104186240045086>', '<:t68e_08:1248104187225702422>', '<:t68e_09:1248104187867168810>',
                   '<:t68e_10:1248104184516055061>', '<:t68e_11:1248104201129558066>', '<:t68e_12:1248104201964355726>',
                   '<:t68e_13:1248104203260264519>', '<:t68e_14:1248472661399699539>', '<:t68e_15:1248104199904956449>']
t8_hpbar_full = ['<:t8f_01:1248103735411081326>', '<:t8f_02:1248103736639885343>', '<:t8f_03:1248103737440862341>',
                 '<:t8f_04:1248103738175127673>', '<:t8f_05:1248103734454517862>', '<:t8f_06:1248103752544682098>',
                 '<:t8f_07:1248103753417228430>', '<:t8f_08:1248103754033528844>', '<:t8f_09:1248103759741980752>',
                 '<:t8f_10:1248103751772803112>', '<:t8f_11:1248103769032495114>', '<:t8f_12:1248103769858904085>',
                 '<:t8f_13:1248103770819133450>', '<:t8f_14:1248103766813704202>', '<:t8f_15:1248103767916679168>']
hp_bar_dict = {1: [t1_hpbar_full, t1_hpbar_empty], 2: [t2_hpbar_full, t2_hpbar_empty],
               3: [t3_hpbar_full, t3_hpbar_empty], 4: [t4_hpbar_full, t4_hpbar_empty],
               5: [t5_hpbar_full, t57_hpbar_empty], 6: [t6_hpbar_full, t68_hpbar_empty],
               7: [t7_hpbar_full, t57_hpbar_empty], 8: [t8_hpbar_full, t68_hpbar_empty]}

# MESSAGES
abyss_msg = ("Within this cavern resides the true abyss. The taint of the void can only be purified "
             "through a more powerful darkness. Take great caution, there is nothing which can save you down there.")
