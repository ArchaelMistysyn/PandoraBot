# General imports
import pandas as pd

# Data imports
import globalitems

# Map data lists
map_tier_dict = {"Ancient Ruins": 1, "Spatial Dungeon": 2, "Celestial Labyrinth": 3,
                 "Starlit Grotto": 4, "Void Temple": 5, "Citadel of Miracles": 6,
                 "Abyssal Sanctum": 7, "Divine Ziggurat": 8, "Cradle of Samsara": 9, "Rift of the Chaos God": 10}

random_room_list = [
    ["trap_room", 0], ["healing_room", 0], ["treasure", 0], ["trial_room", 0], ["statue_room", 0],
    ["epitaph_room", 0], ["selection_room", 0], ["sanctuary_room", 0], ["penetralia_room", 0],
    # These rooms have an echelon spawn restriction.
    ["boss_shrine", 3], ["crystal_room", 3], ["pact_room", 5],
    ["basic_monster", 0], ["basic_monster", 5], ["elite_monster", 0], ["legend_monster", 8],
    # These two rooms do not spawn normally.
    ["greater_treasure", 999], ["jackpot_room", 999]
]

adjuster_dict = {"basic_monster": 1, "elite_monster": 2, "legend_monster": 3,
                 "penetralia_room": 1, "jackpot_room": 2}

shrine_dict = {1: ["Land", 3, "Sky", 4], 2: ["Fear", 6, "Suffering", 0],
               3: ["Illumination", 7, "Tranquility", 1], 4: ["Retribution", 2, "Imprisonment", 5]}

# {room_type: [num_buttons, [button_label], [button_icon], [button_colour], [button_callback]]}
room_data_dict = {
    "trap_room":
        [2, ["Salvage", "Bypass"],
         [None, "↩️"],
         [globalitems.button_colour_list[1], globalitems.button_colour_list[2]],
         "trap_callback"],
    "statue_room":
        [2, ["Pray", "Destroy"],
         [None, None],
         [globalitems.button_colour_list[1], globalitems.button_colour_list[0]],
         "statue_callback"],
    "healing_room":
        [2, ["Short Rest", "Long Rest"],
         [None, None],
         [globalitems.button_colour_list[1], globalitems.button_colour_list[2]],
         "rest_callback"],
    "basic_monster":
        [2, ["Fight", "Stealth"],
         ["⚔️", "↩️"],
         [globalitems.button_colour_list[0], globalitems.button_colour_list[2]],
         "basic_monster_callback"],
    "elite_monster":
        [2, ["Fight", "Stealth"],
         ["⚔️", "↩️"],
         [globalitems.button_colour_list[0], globalitems.button_colour_list[2]],
         "elite_monster_callback"],
    "legend_monster":
        [2, ["Fight", "Stealth"],
         ["⚔️", "↩️"],
         [globalitems.button_colour_list[0], globalitems.button_colour_list[2]],
         "legend_monster_callback"],
    "epitaph_room":
        [2, ["Search", "Decipher"],
         [None, "🧩"],
         [globalitems.button_colour_list[2], globalitems.button_colour_list[2]],
         "epitaph_callback"],
    "treasure":
        [2, ["Open Chest", "Bypass"],
         [None, None],
         [globalitems.button_colour_list[1], globalitems.button_colour_list[2]],
         "treasure_callback"],
    "greater_treasure":
        [2, ["Open Chest", "Bypass"],
         [None, None],
         [globalitems.button_colour_list[1], globalitems.button_colour_list[2]],
         "treasure_callback"],
    "penetralia_room":
        [2, ["Search", "Collect"],
         ["📿", "💲"],
         [globalitems.button_colour_list[1], globalitems.button_colour_list[2]],
         "penetralia_callback"],
    "jackpot_room":
        [2, ["Search", "Collect"],
         ["📿", "💲"],
         [globalitems.button_colour_list[1], globalitems.button_colour_list[2]],
         "penetralia_callback"],
    "selection_room":
        [3, ["Option1", "Option2", "Both"],
         [None, None, None],
         [globalitems.button_colour_list[2], globalitems.button_colour_list[2], globalitems.button_colour_list[0]],
         "selection_callback"],
    "boss_shrine":
        [3, ["Option1", "Option2", "Option3"],
         [None, None, None],
         [globalitems.button_colour_list[2], globalitems.button_colour_list[2], globalitems.button_colour_list[0]],
         "shrine_callback"],
    "trial_room":
        [3, ["Option1", "Option2", "Option3"],
         [None, None, None],
         [globalitems.button_colour_list[2], globalitems.button_colour_list[2], globalitems.button_colour_list[0]],
         "trial_callback"],
    "crystal_room":
        [2, ["Resonate", "Search"],
         ["🌟", "🔍"],
         [globalitems.button_colour_list[2], globalitems.button_colour_list[2]],
         "crystal_callback"],
    "sanctuary_room":
        [3, ["Option1", "Option2", "Option3"],
         [None, None, None],
         [globalitems.button_colour_list[2], globalitems.button_colour_list[2], globalitems.button_colour_list[2]],
         "sanctuary_callback"],
    "pact_room":
        [2, ["Refuse Pact", "Forge Pact"],
         [None, None],
         [globalitems.button_colour_list[0], globalitems.button_colour_list[1]],
         "pact_callback"]
}

# NPC Message Lists
death_msg_list = ["Back so soon? I think I'll play with you a little longer.", "Death is not the end.",
                  "Can't have you dying before the prelude now can we?",
                  "I will overlook this, just this once. ",
                  "I'll have you repay this favour to me when the time is right.",
                  "I wouldn't mind helping you for a price, but does your life truly hold any value?"]
eleuia_msg_list = ["If you want something you need to wish for it. What is it you really want?",
                   "To wish is to dream. Do you have a dream?",
                   "It wouldn't be fair if only my wish comes true. Let me lend you a hand.",
                   "Just because you wish for it, doesn't mean it will be yours.",
                   "Even if you won't tell me, you can't hide the wishes in your heart.",
                   "Let's play a game!",
                   "I'm not going back in that box. You can't make me.",
                   "Why do you wish to take away the freedom we desire?",
                   "Pandora isn't telling you the whole truth you know."]

# Monster data lists
element_descriptor_list = ["Pyro", "Aqua", "Voltaic", "Stone", "Sky", "Frost", "Shadow", "Luminous", "Celestial"]
basic_monsters = ["Skeleton Knight", "Skeleton Archer", "Skeleton Mage", "Ooze", "Slime", "Sprite", "Faerie",
                  "Spider", "Goblin", "Imp", "Fiend", "Orc", "Ogre", "Lamia"]
elite_monsters = ["Salamander", "Undine", "Raiju", "Construct", "Sylph", "Ursa", "Wraith", "Seraph", "Void Drifter"]
legendary_monsters = ["Inferno-Imperator Hydra", "Ocean-Overlord Kraken", "Electric-Emperor Phoenix",
                      "Time-Transgressor Wurm", "Sky-Sovereign Manta", "Winter-Warden Fenrir",
                      "Underworld-Usurper Cerberus", "Crystal Conqueror Simurgh", "Eon-Eater Jormungarr"]
monster_dict = {"basic_monster": basic_monsters, "elite_monster": elite_monsters, "legend_monster": legendary_monsters}

# Message data lists
vowel_list = ["a", "e", "i", "o", "u"]
msg_df = pd.read_csv("specialmessages.csv")
trap_roomname_list = msg_df.loc[msg_df['message_type'] == "TrapName"]
trap_roomname_list = trap_roomname_list['message'].tolist()
trap_trigger1_list = msg_df.loc[msg_df['message_type'] == "TrapV1"]
trap_trigger1_list = trap_trigger1_list['message'].tolist()
trap_trigger2_list = msg_df.loc[msg_df['message_type'] == "TrapV2"]
trap_trigger2_list = trap_trigger2_list['message'].tolist()
safe_room_msg = msg_df.loc[msg_df['message_type'] == "SafeMsg"]
safe_room_msg = safe_room_msg['message'].tolist()
wrath_msg_list = msg_df.loc[msg_df['message_type'] == "Wrath"]
wrath_msg_list = wrath_msg_list['message'].tolist()

# Room variant details
variant_details_dict = {
    'trap_room': ['Trap Encounter',
                  "The remains of other fallen adventurers are clearly visible here. "
                  "Perhaps their equipment is salvageable, however you feel uneasy."],
    'statue_room': ['Foreboding Statue', None],
    'basic_monster': ['Basic Monster Encounter', None],
    'elite_monster': ['Elite Monster Encounter', None],
    'legendary_monster': ['Legendary Titan Encounter', None],
    'healing_room': ['Safe Zone', None],
    'treasure': ['Treasure Chamber', "The unopened chest calls to you."],
    'greater_treasure': ['Treasure Vault', "The irresistible allure of treasure entices you."],
    'penetralia_room': ['Secret Penetralia', "This room is well hidden. Perhaps there are valuable items here."],
    'jackpot_room': ['Golden Penetralia!', f"Riches spread all across the secret room. Ripe for the taking!"],
    'crystal_room': ['Crystal Cave',
                     "Crystals are overly abundant in this cave. It is said that the rarest items are "
                     "drawn to each other. Those adorned in precious metals may fare better then those "
                     "who search blindly."],
    'sanctuary_room': ['Butterfae Sanctuary',
                       "A wondrous room illuminated by the sparkling lights of countless elemental butterfaes"],
    'epitaph_room': ['Lone Epitaph',
                     "You see a tablet inscribed with glowing letters. It will take some time to uncover the message."],
    'selection_room': ['Selection Trap',
                       "Two items sit precariously atop podiums, but it's obviously a trap. "
                       "Trying to take both seems extremely dangerous."],
    'pact_room': ['Demonic Alter',
                  "As you examine the alter a demonic creature materializes. "
                  "It requests you to prove yourself with blood and offers to forge a pact."],
    'trial_room': ['Trial Room', None],
    'boss_shrine': ['Shrine Room',
                    "The shrine awaits the ritual of the challenger. Those who can endure the raw "
                    "elemental power and complete the ritual shall be granted rewards and passage."],
}

trial_variants_dict = {"Offering": ["Pay with your life.", ["Pain (10%)", "Blood (20%)", "Death (30%)"],
                                    ["🗡️", "💧", "💀"]],
                       "Greed": ["Pay with your wealth.", ["Poor (1,000)", "Affluent (5,000)", "Rich (10,000)"],
                                 ["💸", "💍", "👑"]],
                       "Soul": ["Pay with your stamina.", ["Vitality (100)", "Spirit (300)", "Essence (500)"],
                                ["🟢", "🟡", "🔴"]]}
greed_cost_list = [1000, 5000, 10000]

treasure_details = {"treasure": [50, 80, "Lesser"], "greater_treasure": [33, 67, "Greater"]}

# Probability data lists
reward_probabilities = {45: 1, 30: 2, 20: 3, 5: 5}

# Reward data lists
blessing_rewards = {("Incarnate", 8): ["Divine", "Core4", 15],
                    ("Arbiter", 7): ["Prismatic", "Summon5", 10],
                    ("Arbiter", 0): ["ARBITER", "Summon4", 7],
                    ("Paragon", 6): ["Miraculous", "Summon3", 5],
                    ("Paragon", 5): ["Sovereign's", "Summon2", 3],
                    ("Paragon", 0): ["PARAGON", "Summon1", 2]}

jackpot_levels = [
    (1, "Ultimate Jackpot!!!!", (1000000, 5000000)),
    (10, "Greater Jackpot!!!", (500000, 1000000)),
    (30, "Standard Jackpot!!", (100000, 500000)),
    (50, "Lesser Jackpot!", (10000, 100000))
]

selection_pools = [
    ["Hammer1", "Ore1", "Trove1", "Potion1", "Scrap", "ESS"],
    ["Hammer1", "Pearl1", "Ore2", "Token1", "Trove2", "Flame1", "Matrix1", "Trove2", "Summon1", "Potion2", "ESS"],
    ["Hammer1", "Pearl1", "Ore3", "Token2", "Trove3", "Summon1", "Gem1", "Gem2", "Gem3", "Potion3", "ESS"],
    ["Hammer2", "Pearl2", "Ore4", "Token3", "Token4", "Trove4", "Summon2", "Summon3",
     "Core1", "Jewel1", "Jewel2", "Potion4", "ESS"],
    ["Hammer2", "Pearl2", "Ore5", "Token5", "Trove5", "Summon4", "Crystal2", "Core2", "Flame2", "Jewel3", "ESS"],
    ["Hammer2", "Pearl2", "Ore6", "Token7", "Token6", "Trove7", "Trove6", "Summon5", "Crystal3",
     "Core3", "Jewel4", "Compass", "ESS"],
    ["Lotus1", "Lotus2", "Lotus3", "Lotus4", "Lotus5", "Lotus6", "Lotus7", "Lotus8", "Lotus9",
     "Lotus10", "DarkStar", "LightStar", "Core4", "Trove8", "Crystal4", "Jewel5", "ESS"]]
