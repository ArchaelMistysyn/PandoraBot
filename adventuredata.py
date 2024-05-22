# Data imports
import globalitems as gli

# Map data lists
map_tier_dict = {"Ancient Ruins": 1, "Spatial Dungeon": 2, "Celestial Labyrinth": 3,
                 "Starlit Grotto": 4, "Void Temple": 5, "Citadel of Miracles": 6,
                 "Abyssal Sanctum": 7, "Divine Ziggurat": 8, "Cradle of Samsara": 9, "Rift of the Chaos God": 10}
reverse_map_tier_dict = {v: k for k, v in map_tier_dict.items()}

random_room_list = [
    ["trap_room", 0], ["healing_room", 0], ["treasure", 0], ["trial_room", 0], ["statue_room", 0],
    ["epitaph_room", 0], ["selection_room", 0], ["sanctuary_room", 0], ["penetralia_room", 0],
    # These rooms have an echelon spawn restriction.
    ["boss_shrine", 3], ["crystal_room", 3], ["pact_room", 5], ["heart_room", 5],
    ["basic_monster", 0], ["basic_monster", 5], ["elite_monster", 0], ["legend_monster", 8],
    # These two rooms do not spawn normally.
    ["greater_treasure", 999], ["jackpot_room", 999]
]

adjuster_dict = {"basic_monster": 1, "elite_monster": 2, "legend_monster": 3, "penetralia_room": 1, "jackpot_room": 2}

shrine_dict = {1: ["Land", 3, "Sky", 4], 2: ["Fear", 6, "Suffering", 0],
               3: ["Illumination", 7, "Tranquility", 1], 4: ["Retribution", 2, "Imprisonment", 5]}

# {room_type: [num_buttons, [button_label], [button_icon], [button_colour], [button_callback]]}
room_data_dict = {
    "trap_room":
        [2, ["Salvage", "Bypass"],
         [None, "↩️"],
         [gli.button_colour_list[1], gli.button_colour_list[2]],
         "trap_callback"],
    "statue_room":
        [2, ["Pray", "Destroy"],
         [None, None],
         [gli.button_colour_list[1], gli.button_colour_list[0]],
         "statue_callback"],
    "healing_room":
        [2, ["Short Rest", "Long Rest"],
         [None, None],
         [gli.button_colour_list[1], gli.button_colour_list[2]],
         "rest_callback"],
    "basic_monster":
        [2, ["Fight", "Stealth"],
         ["⚔️", "↩️"],
         [gli.button_colour_list[0], gli.button_colour_list[2]],
         "basic_monster_callback"],
    "elite_monster":
        [2, ["Fight", "Stealth"],
         ["⚔️", "↩️"],
         [gli.button_colour_list[0], gli.button_colour_list[2]],
         "elite_monster_callback"],
    "legend_monster":
        [2, ["Fight", "Stealth"],
         ["⚔️", "↩️"],
         [gli.button_colour_list[0], gli.button_colour_list[2]],
         "legend_monster_callback"],
    "epitaph_room":
        [2, ["Search", "Decipher"],
         [None, "🧩"],
         [gli.button_colour_list[2], gli.button_colour_list[2]],
         "epitaph_callback"],
    "treasure":
        [2, ["Open Chest", "Bypass"],
         [None, None],
         [gli.button_colour_list[1], gli.button_colour_list[2]],
         "treasure_callback"],
    "greater_treasure":
        [2, ["Open Chest", "Bypass"],
         [None, None],
         [gli.button_colour_list[1], gli.button_colour_list[2]],
         "treasure_callback"],
    "penetralia_room":
        [2, ["Search", "Collect"],
         ["📿", "💲"],
         [gli.button_colour_list[1], gli.button_colour_list[2]],
         "penetralia_callback"],
    "jackpot_room":
        [2, ["Search", "Collect"],
         ["📿", "💲"],
         [gli.button_colour_list[1], gli.button_colour_list[2]],
         "penetralia_callback"],
    "selection_room":
        [3, ["Option1", "Option2", "Both"],
         [None, None, None],
         [gli.button_colour_list[2], gli.button_colour_list[2], gli.button_colour_list[0]],
         "selection_callback"],
    "boss_shrine":
        [3, ["Option1", "Option2", "Option3"],
         [None, None, None],
         [gli.button_colour_list[2], gli.button_colour_list[2], gli.button_colour_list[0]],
         "shrine_callback"],
    "trial_room":
        [3, ["Option1", "Option2", "Option3"],
         [None, None, None],
         [gli.button_colour_list[2], gli.button_colour_list[2], gli.button_colour_list[0]],
         "trial_callback"],
    "crystal_room":
        [2, ["Resonate", "Search"],
         ["🌟", "🔍"],
         [gli.button_colour_list[2], gli.button_colour_list[2]],
         "crystal_callback"],
    "sanctuary_room":
        [3, ["Option1", "Option2", "Option3"],
         [None, None, None],
         [gli.button_colour_list[2], gli.button_colour_list[2], gli.button_colour_list[2]],
         "sanctuary_callback"],
    "pact_room":
        [2, ["Refuse Pact", "Forge Pact"],
         [None, None],
         [gli.button_colour_list[0], gli.button_colour_list[1]],
         "pact_callback"],
    "heart_room":
        [2, ["Purify", "Taint"],
         [None, None],
         [gli.button_colour_list[1], gli.button_colour_list[0]],
         "heart_callback"]
}

# Message Lists
vowel_list = ["a", "e", "i", "o", "u"]

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

safe_msg_list = ["You happen across a rare carbuncle. It's gentle aura heals your wounds.",
                 "You drink from the nearby magical fountain and it restores your vitality",
                 "Taking advantage of the protective barriers surrounding the room, you rest your weary body."]

trap_room_name_list = ["Warm", "Damp", "Charged", "Unstable", "Breezy", "Cold", "Dim", "Bright", "Disorienting"]
trap_trigger1_list = [
    "Magma streams out from jets hidden in the wall.",
    "A pit opens, plunging you into a whirling vortex. Despite your injuries you pull yourself back up.",
    "Lightning bolts and surges through you at full force before the room becomes silent once more.",
    "Boulders and debris roll through the passageway smashing you around as they pass by.",
    "The sharp winds cut and tear at your skin as you push forward.",
    "Icicles fall from the ceiling in great number. Injury is unavoidable.",
    "Blinded by the darkness, you lose your way and arrive at another location.",
    "Blinded by a flash of light, you lose your way and arrive at another location.",
    "Feeling space itself shift around you, you find yourself in an entirely new location."
]

trap_trigger2_list = [
    "The ground opens beneath you and the last thing you feel is lava melting your skin and bones.",
    "The doors of the room slam closed and water floods the room. Unable to find an escape, your lungs fill with water.",
    "Paralyzed by high voltage energy, you collapse. Never to stand again.",
    "Your movement slows and an uneasy feeling creeps up your leg. Within mere moments you are fully petrified.",
    "Winds howl from all directions and the strong gusts swiftly tear you apart.",
    "The cold stops you in your tracks. Slowly you find yourself unable to move at all, fully entombed in ice.",
    "Dark smoke fills the room. As you breath it in you feel your mind melting until nothing remains.",
    "Light particles gather and condense. Within moments, multiple lasers slash through your feeble armour and body.",
    "A celestial miasma permeates the room. Unable to prevent exposure your body disintegrates."
]

wrath_msg_dict = {
    # 0 = Nothing, 1 = Death, 2 = Teleport, X = Damage (X)
    "0": ["To reverse your actions onto yourself is a basic preservation of the balance.", 1],
    "I": ["May your unworthy eyes be blessed by the sight of my magic as it tears you apart.", 1],
    "II": ["Why would you do that? What is wrong with you? How can you be so cruel...", 0],
    "III": ["I see somebody wants to help me test my new obliteration magic. How kind of you.", 1],
    "IV": ["I praise you for being so bold as to draw my ire. However, your transgression will not go unpunished.",
           999999999],
    "V": ["There is balance to all things. Can you bear the weight of your sins?", 5000],
    "VI": ["Heartless.\nHow empty are you, that you can be so cold?", 0],
    "VII": ["The celestial dragon manifests atop the statue's rubble. "
            "The last thing you feel is the feeling of it's dimensional claws tearing you apart.", 1],
    "VIII": ["A powerful roar shakes the room. You flee from the great beast.", 2],
    "IX": ["You will forget what you have done, but I will remember. Begone.", 2],
    "X": ["I will undo your mistake. Choose more wisely this time if you value the time you have remaining.", 2],
    "XI": ["Unfathomable, to enact such sacrilege in my presence. I will judge your actions before the eyes of god.", 1],
    "XII": ["Gaze too deep into the abyss, and I will gaze back.", 1],
    "XIII": ["Mortality is as frail as this statue, but to openly invite death is the height of foolishness.", 1],
    "XIV": ["Your actions muddy the waters and cloud the sky. To restore purity you must be purged.", 1],
    "XV": ["You think I am beneath you, human!? You will burn where you stand.", 1],
    "XVI": ["If pandora wants to reclaim her authority she should've sent someone stronger.", 5000],
    "XVII": ["A shooting star sails across the silent sky to strike the sinner where they stand.", 1],
    "XVIII": ["You're lucky Luma isn't here. Leave before I change my mind.", 0],
    "XIX": ["Feel the fury of 10,000 suns!", 10000],
    "XX": ["Listen closely, and you can hear the sounds of your beating heart fade away.", 1],
    "XXI": ["Just because I am The Creation does not mean I am incapable of destruction.", 1],
    "XXII": ["You've crossed the point of no return. Be undone by the very laws you sought to defy.", 1],
    "XXIII": ["I will set you back onto the right path.", 2],
    "XXIV": ["These are the threads of your soul. Any last words before I snap them?", 1],
    "XXV": ["I see now that I was wrong. My only wish in this moment is that you never existed.", 1],
    "XXVI": ["You will replay this debt in blood!", 1],
    "XXVII": ["I will now read the verdict. Death.", 1],
    "XXVIII": ["Just as this was destined, so is your resulting demise.", 1],
    "XXIX": ["It is your right to take action, however it is divine right to make you bear the consequences.", 1],
    "XXX": ["???", 1],
}


# Monster data lists
element_descriptor_list = ["Pyro", "Aqua", "Voltaic", "Stone", "Sky", "Frost", "Shadow", "Luminous", "Celestial"]
basic_monsters = ["Skeleton Knight", "Skeleton Archer", "Skeleton Mage", "Ooze", "Slime", "Sprite", "Faerie",
                  "Spider", "Goblin", "Imp", "Fiend", "Orc", "Ogre", "Lamia"]
elite_monsters = ["Salamander", "Undine", "Raiju", "Construct", "Sylph", "Ursa", "Wraith", "Seraph", "Void Drifter"]
legendary_monsters = ["Inferno-Imperator Hydra", "Ocean-Overlord Kraken", "Electric-Emperor Phoenix",
                      "Time-Transgressor Wurm", "Sky-Sovereign Manta", "Winter-Warden Fenrir",
                      "Underworld-Usurper Cerberus", "Crystal Conqueror Simurgh", "Eon-Eater Jormungarr"]
monster_dict = {"basic_monster": basic_monsters, "elite_monster": elite_monsters, "legend_monster": legendary_monsters}

# Room variant details
variant_details_dict = {
    'trap_room': ['Trap Encounter',
                  "The remains of other fallen adventurers are clearly visible here. "
                  "Perhaps their equipment is salvageable, however you feel uneasy."],
    'statue_room': ['Foreboding Statue', None],
    'basic_monster': ['Basic Monster Encounter', None],
    'elite_monster': ['Elite Monster Encounter', None],
    'legend_monster': ['Legendary Titan Encounter', None],
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
    'heart_room': ['Judgement Room',
                   "It's heart barely beating, the poor creature on the ground beneath you is beyond help. "
                   "Living hearts are extremely valuable if preserved correctly with magic. "
                   "Will you imbue the heart with light magic and cleanse it's dying soul. "
                   "Or will you corrupt it with dark magic destroying the soul."]
}

trial_variants_dict = {"Offering": ["Pay with your life.", ["Pain (10%)", "Blood (30%)", "Death (50%)"],
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
                    ("Arbiter", 7): ["Prismatic", "Summon3", 10],
                    ("Arbiter", 0): ["ARBITER", "Stone6", 7],
                    ("Paragon", 6): ["Miraculous", "Summon2", 5],
                    ("Paragon", 5): ["Sovereign's", "Summon1", 3],
                    ("Paragon", 0): ["PARAGON", "Stone4", 2]}

jackpot_levels = [
    (1, "Ultimate Jackpot!!!!", (1000000, 5000000)),
    (10, "Greater Jackpot!!!", (500000, 1000000)),
    (30, "Standard Jackpot!!", (100000, 500000)),
    (50, "Lesser Jackpot!", (10000, 100000))
]

selection_pools = [
    ["Hammer", "Pearl", "Ore1", "Trove1", "Potion1", "Scrap", "ESS"],
    ["Hammer", "Pearl", "Ore2", "Token1", "Trove2", "Flame1", "Matrix", "Trove2", "Summon1", "Potion2", "ESS"],
    ["Hammer", "Pearl", "Ore3", "Token2", "Trove3", "Stone4", "Gem1", "Gem2", "Gem3", "Potion3", "ESS"],
    ["Hammer", "Pearl", "Ore4", "Token3", "Token4", "Trove4", "Summon1", "Core1", "Jewel1", "Jewel2", "Potion4", "ESS"],
    ["Skull1", "Hammer", "Pearl", "Ore5", "Token5", "Trove5", "Summon2", "Crystal2", "Core2", "Flame2", "Jewel3", "ESS"],
    ["Skull2", "Hammer", "Pearl", "Ore5", "Token7", "Token6", "Trove7", "Trove6", "Summon3", "Crystal3",
     "Core3", "Jewel4", "Compass", "ESS"],
    ["Skull3", "Lotus1", "Lotus2", "Lotus3", "Lotus4", "Lotus5", "Lotus6", "Lotus7", "Lotus8", "Lotus9",
     "Lotus10", "DarkStar", "LightStar", "Core4", "Trove8", "Crystal4", "Jewel5", "ESS"]]
