# Key (Quest Num): Quest Type Num, Quest Title,
# Story Message,
# Cost Num, Token Num, Item Hand-in,
# Quest Message
# Award Item, Award QTY, Award Role

quests_data = {
    1: [0, "Who Are You?",
        "You're a naughty one going around opening chests and boxes that aren't yours. How about a deal? "
        "Assist me in sealing the contents back inside, and in return, I'll bestow upon you the power of the stars."
        "\nBut first, could you tell me your name little one?",
        1, 1, None,
        "Use the /register command",
        'Potion4', 1, None],

    2: [0, "Definitely Not Lost",
        "Pleasure doing business with you. I do hope you have a map of this labyrinth. "
        "It really would be a shame if we got lost in here and met an unfortunate end. "
        "Perhaps we will even find some treasure.",
        1, 2, None,
        "Use the /map command",
        'Potion4', 1, None],

    3: [2, "Plunder The Keep",
        "I'm delighted to see you're still here in one piece. "
        "You may have to venture back into those ruins to procure a weapon. "
        "I sense a fortress nearby. I'd like you to pilfer something notable and come back. "
        "That will do nicely to prove both your loyalty and ability.",
        1, None, 'Stone1',
        "Retrieve a Fortress Stone using /solo",
        'Crate', 5, None],

    4: [1, "Initiate the Ascent",
        "I'm impressed with your findings. This stone contains remnants of my celestial energy. "
        "For now, how about we venture back into the ruins and see if we can get some proper equipment. "
        "The challenges that lie ahead are not something we can run into bare-handed."
        "\n What are you waiting for let's go!",
        5, None, None,
        "Breakthrough to level 5",
        'Crate', 5, None],

    5: [1, "Pursuit Of Power",
        "You're not anywhere near strong enough yet. I can help you improve your equipment, "
        "but first you need to show me that you are qualified to wield it."
        "\nNote: You can use /manifest to help you hunt monsters.",
        10, None, None,
        "Breakthrough to level 10",
        'Crate', 10, 'Echelon 1'],

    6: [2, "Out Of Reach",
        "Glad to see you can hold your own in combat, but can you also battle through the skies? "
        "Astratha will bring the dragons upon your world. "
        "You'll need to acquire a pair of wings if you intend to contend.",
        1, None, 'Stone2',
        "Retrieve a Dragon Stone",
        'Crate', 5, None],

    7: [2, "Crush The Castles",
        "It would seem these stones all harbor a fraction of my power. "
        "Now scattered, they are mutating your world. "
        "Bring me any more of these stones you find that are infused with traces of my energy."
        "\nThis should assist me in regaining my power.",
        5, None, 'Stone1',
        "Retrieve 5 Fortress Stones using /solo",
        'Crate', 5, None],

    8: [1, "Unveiling Hidden Potential",
        "You've hardly scratched the surface of your true potential. "
        "Seek to master the abilities that lie dormant within you. "
        "\nDo you think you can do that for me?",
        15, None, None,
        "Breakthrough to level 15",
        'Crate', 5, None],

    9: [1, "A Way Forward",
        "A False Paragon will be here soon, but you're still not ready. "
        "Make sure to use all of the resources at your disposal and get as strong as you can."
        "\nAurora doesn't yet have the power to become a True Paragon. We can still stop him.",
        20, None, None,
        "Breakthrough to level 20",
        'Crate', 5, None],

    10: [3, "A False Deity",
         "Aurora is nearby and commands a mobile fortress that poses a dire threat to this world. "
         "We must put a stop to him and seal away his power before he can ascend."
         "\nQuickly! He is almost here!",
         1, 4, None,
         "Defeat the Fortress Paragon",
         'Crate', 10, 'Echelon 2'],

    11: [0, "On Borrowed Wings",
         "The threat from Aurora has been quelled thanks to your efforts. "
         "Why don't you let me take a look at your gear or we can stock up in on resources in town. "
         "\nNobody around here will refuse to help you now.",
         1, 5, None,
         "Use any of the /forge, /refinery, or /market commands",
         'Crate', 5, None],

    12: [2, "Clear The Skies",
         "Hopefully, you've refined some wings. "
         "More dragons are already inbound and they don't plan to wait around."
         "\nLet's act swiftly!",
         5, None, 'Stone2',
         "Retrieve 5 Dragon Stones",
         'Crate', 5, None],

    13: [1, "Prepare For War",
         "I sense Astratha is nearby. "
         "Astratha may also be a False Paragon, but she has stolen a significant amount of my celestial power. "
         "She will be far more powerful than Aurora was. "
         "\nBegin preparations and bring every weapon you've got. ",
         25, None, None,
         "Breakthrough to level 25",
         'Crate', 5, None],

    14: [3, "Fearless Before Fire",
         "The dragons are an elemental blight invading from the outer dimensions. "
         "They aim to tear open the gate between worlds, allowing the True Paragons free reign."
         "\nWe will make our stand here. \nThey do not feel. \nShow them no mercy.",
         1, 6, None,
         "Defeat the Dragon Paragon",
         'Crate', 5, None],

    15: [1, "Into The Depths",
         "The mortal plane is safe for now, thanks to you. "
         "Let's take this opportunity to further hone your skills before we head to our next destination. "
         "Once you're ready, we can head into the fiends abyss. "
         "Remember this is a one-way trip and there is no turning back.",
         30, None, None,
         "Breakthrough to level 30",
         'OriginZ', 1, 'Echelon 3'],

    16: [2, "Enter The Hellscape",
         "The situation is worse then we thought and the mortal plane faces danger yet again. "
         "Despite reclaiming most of my power from Astratha I can feel it being suppressed. "
         "Rest assured, this hindrance in combat won't be enough to stop me from forging your equipment. "
         "\nUse the gear I have enchanted for you and purge these horrors.",
         5, None, 'Stone3',
         "Retrieve 5 Demon Stones",
         'Crate', 5, None],

    17: [0, "An Arbiter's Assistance",
         "If you are to stand a chance, you will need to find new sources of strength. "
         "I'm not fond of the idea, but we should seek assistance from the Arbiters. "
         "They are unfathomable existences who uphold both reality and the laws that bind it together. "
         "\nAs long as we bring them a sufficient offering they will surely help us.",
         1, 7, None,
         "Talk to an Arbiter using the /engrave or /points command",
         'Crate', 5, None],

    18: [1, "Carve The Soul",
         "That damned Isolde just wants to watch you suffer as she tears into your soul. "
         "If there was any other choice I would never ask this of you. "
         "\nTrain your fortitude to prove to her that you are worthy of this power.",
         35, None, None,
         "Breakthrough to level 35",
         'Crate', 5, None],

    19: [1, "Iron Resolve",
         "Steel yourself for this will be an excruciatingly painful process. "
         "No one could fault you for backing down... "
         "\nBut you'll do it for me, won't you?",
         40, None, None,
         "Breakthrough to level 40",
         'Crate', 5, None],

    20: [0, "Price Of Power",
         "I know you can do it! Show her your resolve!",
         1, 8, None,
         "Engrave an Insignia",
         'OriginZ', 1, 'Echelon 4'],

    21: [0, "Cursed By Contract",
         "With your newfound power not only will defeating the demons be easier, but you might be able to forge "
         "a pact with one. I'm sure there'll be strings attached, but we need all the help we can get."
         "\nWhat could possibly go wrong?",
         1, 9, None,
         "Forge a pact at the demonic altar in /map",
         'Core1', 5, None],

    22: [0, "Arms of Steel",
         "The 'black flames' that shroud demons are actually comprised of metallic dust or shrapnel. "
         "Once their heart gem is extracted the dust can be collected and used to make sturdy armour parts. "
         "\nBring some back with you and we'll try to get something nice refined for you.",
         1, 10, None,
         "Equip a pair of Demon Vambraces",
         'Crate', 5, None],

    23: [1, "Body and Mind",
         "You've become very strong very quickly. "
         "Take care to ensure you are keeping up both physically and mentally with the powers you are wielding. "
         "\nWe'll continue your training at dawn.",
         45, None, None,
         "Breakthrough to level 45",
         'Crate', 5, None],

    24: [1, "The Journey Continues",
         "No need to rush. We've got lots of time to prepare before the other paragons can cross into this world."
         "Take your time, gather your strength."
         "\nThere is no such thing as an easy challenge.",
         50, None, None,
         "Breakthrough to level 50",
         'Crate', 5, None],

    25: [3, "The First Monster",
         "I'm sorry… I've miscalculated. I did not think Tyra would be able to manifest in this plane. "
         "This is a disaster. If Tyra has come here then it's only a matter of time until the others make their move.",
         1, 11, None,
         "Defeat the Demon Paragon",
         'OriginZ', 1, 'Echelon 5'],

    26: [1, "Crossing Of Worlds",
         "Tyra may be gone, but the floodgates have opened. We failed to stop him from opening the celestial rift. "
         "My power is not enough to close it. We have to cross over and stop the paragons. "
         "\nWe've come this far. You will go with me won't you?",
         55, None, None,
         "Breakthrough to level 55",
         'Crate', 5, None],

    27: [2, "Encounter On Arrival",
         "To my knowledge, no human has ventured into the celestial plane before. "
         "This is an incredible accomplishment and you should be proud. "
         "\nThey are aware of our presence, prepare to engage the enemy.",
         1, None, 'Stone4',
         "Retrieve a Paragon Stone",
         'Crate', 5, None],

    28: [5, "Harness Paragon Essence",
         "This is the power of a True Paragon. Claim it as your own and ascend to new heights. "
         "\nWe can use their power against them and fight on equal footing.",
         1, 12, None,
         "Equip a Paragon Crest",
         'Crate', 5, None],

    29: [1, "Cultivate Divinity (Part 1)",
         "By taking in this power you have now become a deity yourself. "
         "As the stars begin to become part of your domain so too will you find yourself becoming one with celestia. "
         "You need to spend time gathering your essence and cultivating your divinity. "
         "\nIf you pursue this path you must take great effort not to lose yourself in the process.",
         60, None, None,
         "Breakthrough to level 60",
         'Core2', 5, None],

    30: [2, "Messenger Of Celestia",
         "We must continue to seal as many of the True Paragons as we can. "
         "If we cannot reclaim enough of my power before we meet one of the High Three then all is lost."
         "\nRemember they are not like you. The paragons have never been human.",
         5, None, 'Stone4',
         "Retrieve 5 Paragon Stones",
         'Crate', 5, 'Echelon 6'],

    31: [2, "The Echoes Within",
         "It's impossible to truly kill a deity. That's why we gather and seal their essence. "
         "When we manifest an echo of a paragon we are summoning their power and form in a controlled way. "
         "There is another method to control the power of those with significantly lesser essence than oneself. "
         "\nTry channelling their power within yourself using one of the cards.",
         1, 13, None,
         "Equip a tarot card with /tarot.",
         'Essence0', 5, None],

    32: [1, "Cultivate Divinity (Part 2)",
         "The temptations of those you channel within yourself will take over if you spend too long in such a state. "
         "Use this power carefully and make sure to collect yourself regularly."
         "\nThis power is a double edged sword if used incorrectly.",
         65, None, None,
         "Breakthrough to level 65",
         'Crate', 5, None],

    33: [2, "Shatter The Cycle",
         "It is not an exaggeration to say that any one of the High Three can bring an end to all things. "
         "If they were to combine their powers perhaps they could overthrow the Arbiters. "
         "\nI relish the thought, but them working together is just as impossible.",
         10, None, 'Stone4',
         "Retrieve 10 Paragon Stones",
         'Crate', 5, None],

    34: [1, "Cultivate Divinity (Part 3)",
         "Something's not right. Stay here, gather yourself. "
         "Please await my return and do not try to follow me. I won't be gone long. "
         "\nI promise.",
         70, None, None,
         "Breakthrough to level 70",
         'Crate', 5, None],

    35: [3, "Free From Possession",
         "Oblivia has seized my mind. I can't stop them. You can't stop them. All is lost."
         "\nPlease... while I'm still in control of myself. Kill me.",
         1, 14, None,
         "Defeat II - Pandora, The Celestial",
         'EssenceII', 3, 'Echelon 7'],

    36: [1, "Cultivate Divinity (Part 4)",
         "Remarkable. I could not have imagined you would be able to sever Oblivia's hold over me. "
         "\nThank you. For saving me.",
         75, None, None,
         "Breakthrough to level 75",
         'Crate', 5, None],

    37: [3, "Charge Into Terminus",
         "The void is an annihilator of all. "
         "To conquer the power of a black hole is an impossibility. "
         "\nI trust that you will find a way.",
         1, 16, None,
         "Defeat III - Oblivia, The Void",
         'EssenceIII', 3, None],

    38: [0, "The True Abyss",
         "During your battle, Oblivia opened the Gateway of the True Abyss. Before we can challenge Eleuia "
         "and bring an end to her games we must seal the gate."
         "\nPerhaps in those depths we may find the power we seek.",
         1, 18, None,
         "Visit the Gateway of the True Abyss using /abyss",
         'Core3', 5, None],

    39: [1, "Cultivate Divinity (Part 5)",
         "Oblivia is right. We're approaching the limits of what I can forge for you. "
         "You need further improvements to your equipment if it's going to be able to keep pace with you. "
         "\nI'll do my best to keep you safe from the pull of the abyss whilst you temper your gear.",
         80, None, None,
         "Breakthrough to level 80",
         'Crate', 5, None],

    40: [3, "Challenge The Omniscia",
         "Akasha has come. To overcome destruction is a miracle. Now you must claim authority over creation."
         "\nCreate a second miracle my child of the stars.",
         1, 17, None,
         "Defeat IV - Akasha, The Infinite",
         'EssenceIV', 3, 'Echelon 8'],

    41: [1, "The Endgame Beyond",
         "You are the harbinger of two miracles and have earned sovereignty over the stars."
         "\nEleuia won't ignore you as a threat any longer.",
         85, None, None,
         "Breakthrough to level 85",
         'Crate', 5, None],

    42: [0, "A Justified Blasphemy",
         "We should probably try visiting some of the other arbiters. "
         "There will surely be more repercussions, but if we can't stop Eleuia the outcome will be far worse."
         "\nLet's go pay Kazyth a visit.",
         1, 19, None,
         "Use /meld to have the affinity of two jewels appraised",
         'Crate', 5, None],

    43: [0, "Spire of Illusions",
         "To overcome Eleuia's boundless power and overwhelming advantage we will go to the Spire of Illusions. "
         "Only by facing the imaginary, will you be able to safely prepare for the battle ahead. "
         "\nIt's also where my legendary hammer is sealed. You'll help me get it back right? ",
         1, 15, None,
         "Attempt the Spire of Illusions with /gauntlet",
         'Shard', 5, None],

    44: [1, "Cultivate Divinity (Part 6)",
         "I can't believe they shattered my precious hammer. "
         "I know it's not your fault, I'm sorry for getting mad at you earlier. If you find more shards let me know. "
         "\nMaybe one day I'll be able to reforge it.",
         90, None, None,
         "Breakthrough to level 90",
         'Crate', 10, None],

    45: [3, "Ending A Wish",
         "I feel the fading of reality. Eleuia wishes for finality, but you can rewrite this world. "
         "Create the third miracle and harness the primeval atom."
         "\nInvert her wish for the end into a new beginning.",
         1, 20, None,
         "Defeat XXV - Eleuia, The Wish",
         'EssenceXXV', 3, 'Echelon 9'],

    46: [1, "Through The Ether",
         "Our efforts were not in vain. You have crossed planes, realms, and dimensions. "
         "You've managed to birth a new reality."
         "\nThe arbiters won't overlook this, but this time, I know you'll be strong enough to face them.",
         95, None, None,
         "Breakthrough to level 95",
         'Core4', 2, None],

    47: [3, "A Flower Foregone",
         "This reality belongs to no one. We will usurp those who seek to control and manipulate it."
         "They underestimated you and let your potential fully blossom. "
         "Even so we cannot challenge the rule of Divine Lotus while the Oracle still draws breath."
         "\nIf we're lucky she's already foreseen her demise.",
         1, 21, None,
         "Defeat XXVIII - Fleur, Oracle of the True Laws",
         'Summon3', 5, None],

    48: [3, "A God's Judgement",
         "Only Yubelle remains to protect the Divine Lotus and bring judgement upon us for opposing it."
         "It's been a long journey, my cherished champion."
         "\nLet's finish what we started.",
         1, 22, None,
         "Defeat XXIX - Yubelle, Adjudicator of the True Laws",
         'EssenceXXIX', 1, None],

    49: [1, "Unshackled By Mortality",
         "In these final moments I offer to you my heartfelt congratulations on your victory against Yubelle. "
         "I can feel myself being consumed as he siphons energy to sustain his form. "
         "If you do not stop her, she will merge with the Divine Lotus and ascend to the god plane. "
         "I wish I could help you to stop this divine coronation, but this time it will be a final farewell."
         "\nI will always..."
         "\nUnable to finish speaking, Pandora fades away."
         "\nShe's gone.",
         5, None, None,
         "Breakthrough to level 100",
         'Lotus10', 1, None],

    50: [3, "Root Of Reality",
         "All this power, but in the end you could not save the only thing that truly mattered. "
         "Your divinity surges as your cultivation brings you to the apex. "
         "Lamenting will have to wait, the divine palace beckons."
         "\nAscend, and face the finale! (/palace)",
         1, 23, None,
         "Defeat XXX - Amaryllis, Incarnate of the Divine Lotus [Challenger]",
         'Core4', 2, 'Echelon 10 (MAX)'],

    51: [10, "Pandora's Box",
         "The one left standing ascends to take their place as the new high arbiter of the divine plane. "
         "Pandora is gone, but you would still endeavor to fulfill a now meaningless promise. "
         "\nPerhaps in this little box, you can finally find peace.",
         31, 24, None,
         "Complete the Tarot Collection",
         'Crate', 10, None],

    52: [3, "Dance With Divinity",
         "Do you see now why the arbiters foresaw your failure and the futility of your actions? "
         "They were not wrong, they simply misinterpreted the context. "
         "Even knowing this, will you still chase after your demise? "
         "\nAscend, and face the trial of the usurper!",
         1, 25, None,
         "Defeat XXX - Amaryllis, Incarnate of the Divine Lotus [Usurper]",
         'Crate', 20, None],

    53: [3, "A Heartfelt Wish",
         "I was wrong. I had resigned to my fate believing that gods could not be slain. "
         "I thought that while god reigns the only path to salvation was destruction. "
         "Perhaps, I can entrust to you my true wish."
         "\nPlease, save us all.",
         1, 26, None,
         "Defeat XXX - Amaryllis, Incarnate of the Divine Lotus [Samsara]",
         'Crate', 30, None],

    54: [2, "A Moment Forever",
         "Just how far have you come just to see me again? Alas, you of all people should know I cannot stay. "
         "Even if you shatter the samsara, I still belong with Thana now. It is not my place to return. "
         "But maybe, we can enjoy this moment a little longer.",
         1, None, 'Rings',
         "Give Pandora a special gift",
         'Crate', 50, None],

    55: [1, "Resurrection And Rebirth",
         "Rings faceted with gems forged from the twin mystical stars. "
         "It is said that the two stars used to be lovers, but were forced apart by god. "
         "The star of light only exists at night in the physical world, "
         "while the star of darkness travels through the mind during the daytime."
         "The misfortune they bring is a manifestation of their anguish as they cry through the lonely sky. "
         "Now reunited, not a trace of malice remains. They radiate with the power of rebirth. "
         "\nA lovely tale. Do you think we too could start anew? "
         "\nWould you stay by my side?",
         None, None, None,
         "The End",
         None, 1, None]
}
