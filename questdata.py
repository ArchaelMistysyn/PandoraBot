reg_msg = ('In an ancient ruin, you come across an empty room in which sits a peculiar sealed box. '
           'Hesitating briefly at the possibility of a trap or mimic, you cautiously reach forward and open the box.\n'
           'A flurry of souls floods the room spilling out into the corridor. '
           'One pauses and speaks softly into your mind, "All begins and ends with a wish. What do you wish to be?" '
           'You think it for only a second and the voice responds with a playful laugh, "Let it be so." '
           'Then the voice disappears without a trace amidst the fleeing spirits. '
           'Silence falls and all that remains is an otherworldly girl staring at you in confusion.')

# Key (Quest Num): Quest Type Num, Quest Title,
# Story Message,
# Cost Num, Token Num, Item Hand-in,
# Quest Message,
# Award Item, Award QTY, Award Role
quests_data = {
    1: [0, "Who Are You?", "Pandora, the Celestial",
        "You're a naughty one going around taking what isn't yours. I suppose it cannot be helped now. "
        "Assist me in sealing the *contents* back inside, and in return I'll bestow upon you the power of the stars."
        "\nBut first, could you tell me your name little one?",
        1, 1, None,
        "Use the /register command",
        'Potion4', 1, None],
    2: [0, "Definitely Not Lost", "Pandora, the Celestial",
        "Pleasure to make your acquaintance, [USER]. For starters, do you have a map with you? "
        "It really would be a shame if we got lost in here and met an unfortunate end. "
        "\nPerhaps we might find some treasures as we go.",
        1, 2, None,
        "Use the /map command",
        'Potion4', 1, None],
    3: [2, "Plunder The Keep", "Pandora, the Celestial",
        "I'm delighted to see you're still in one piece. Although, we may have to explore further to procure a weapon. "
        "I can sense a monster's stronghold nearby. I'd like for you to pilfer something notable and return. "
        "\nThat should suffice to prove both your loyalty and ability.",
        1, None, 'Stone1',
        "Use /map to acquire a weapon and /display [Item ID] to equip it. Then retrieve a Fortress Stone using /solo",
        'Chest', 5, None],
    4: [1, "Initiate the Ascent", "Pandora, the Celestial",
        "You've exceeded my expectations with your findings. This stone contains remnants of my paragon energy. "
        "However I'm disappointed with your current ability. Perhaps you should train a bit more in the ruins. "
        "\nThe challenges that lie ahead will not be quite so simple.",
        5, None, None,
        "Breakthrough to level 5",
        'Chest', 5, None],
    5: [1, "Pursuit Of Power", "Pandora, the Celestial",
        "You're still not anywhere near strong enough. I can help you improve your equipment, "
        "but first you need to show me that you are qualified to wield it."
        "\nNote: /manifest can be used to have Pandora hunt monsters for you and acquire EXP.",
        10, None, None,
        "Breakthrough to level 10",
        'Chest', 10, 'Echelon 1'],
    6: [2, "Out Of Reach", "Pandora, the Celestial",
        "I'm glad to see you can now hold your own in combat, but can you say the same in the skies? "
        "The False Paragon, Astratha, has brought a scourge of dragons upon your world. "
        "\nShow me you can hunt them down.",
        1, None, 'Stone2',
        "Retrieve a Dragon Stone",
        'Chest', 5, None],
    7: [2, "Crush The Castles", "Pandora, the Celestial",
        "It would seem these stones harbour a fraction of my celestial energy. We must reclaim them with haste."
        "\nI will be able to regain some of my lost power.",
        5, None, 'Stone1',
        "Retrieve 5 Fortress Stones using /solo",
        'Chest', 5, None],
    8: [1, "Unveil Hidden Potential", "Pandora, the Celestial",
        "You've hardly scratched the surface of your true potential. Master the abilities that lie dormant within you. "
        "\nDo you think you can do that for me?",
        15, None, None,
        "Breakthrough to level 15",
        'Chest', 5, None],
    9: [1, "A Way Forward", "Pandora, the Celestial",
        "You're still not ready, but perhaps I owe you an explanation about the Paragons released from my seal. "
        "Those that have escaped into the celestial plane and begun reclaiming their power are the True Paragons. "
        "The False Paragons are the 3 that got stuck in the mortal plane in a weakened state. "
        "\nIn other words, in spite of their immense power we still have a chance to stop them.",
        20, None, None,
        "Breakthrough to level 20",
        'Chest', 5, None],
    10: [3, "A False Deity", "Pandora, the Celestial",
         "Even in this greatly weakened state, Aurora still poses a major threat to this world. "
         "However, if we act with haste he may not be strong enough to fight back yet. "
         "\nQuickly, let's seal him while we still can.",
         1, 4, None,
         "Defeat the Fortress Paragon",
         'Chest', 10, 'Echelon 2'],
    11: [0, "Explore New Locations", "Pandora, the Celestial",
         "The threat from Aurora has been quelled thanks to your efforts. "
         "You should stock up on and refine items in town for the trials ahead. "
         "\nI'll also take you to my refuge in the celestial plane. ",
         1, 5, None,
         "Use the /town or /celestial commands",
         'Chest', 5, None],
    12: [2, "Clear The Skies", "Pandora, the Celestial",
         "Dragons are an elemental blight from the outer dimensions. "
         "We must protect the town from the approaching invaders before we can go hunt down Astratha. "
         "\nLet's act swiftly!",
         5, None, 'Stone2',
         "Retrieve 5 Dragon Stones",
         'Chest', 5, None],
    13: [1, "The Enemy Ahead", "Pandora, the Celestial",
         "Astratha may also be a False Paragon, but she has stolen a significant amount of my celestial power. "
         "She is far more powerful than Aurora and you will need to prepare your defences to withstand her attacks. "
         "\nSpare no coin, your life is precious to me. ",
         25, None, None,
         "Breakthrough to level 25",
         'Chest', 5, None],
    14: [3, "Fearless Before Fire", "Pandora, the Celestial",
         "Astratha aims to tear open a rift between the planes allowing the True Paragons to cross over. "
         "At all costs we cannot allow them entry into the mortal plane. "
         "\nAgainst the celestial flames we will make our stand here.",
         1, 6, None,
         "Defeat the Dragon Paragon",
         'Chest', 5, None],
    15: [1, "Into The Depths", "Pandora, the Celestial",
         "You've done well, but there is still one more False Paragon in the mortal plane. "
         "Take this opportunity to further hone your skills before we set off for the Fiend's Abyss. "
         "\nRemember, this is a one-way trip and there's no turning back.",
         30, None, None,
         "Breakthrough to level 30",
         'Catalyst', 1, 'Echelon 3'],
    16: [2, "Enter The Hellscape", "Pandora, the Celestial",
         "The situation is far worse then I initially thought and I can feel my power being suppressed here. "
         "As things stand I'll be a hindrance in combat, but I can still help with forging your equipment. "
         "\nUse the gear I've enchanted for you and purge these horrors.",
         5, None, 'Stone3',
         "Retrieve 5 Demon Stones",
         'Chest', 5, None],
    17: [0, "An Arbiter's Assistance", "Pandora, the Celestial",
         "I'm not fond of the idea, but we should seek aid from the Arbiters of the divine plane. "
         "They are a corrupt existence who control both reality and the laws that hold it together. "
         "\nThere are risks, but their power is undeniable.",
         1, 7, None,
         "Use the /divine command",
         'Chest', 5, None],
    18: [1, "Carve The Soul", "Pandora, the Celestial",
         "That damned Isolde just wants to watch you suffer as she plays with your soul. "
         "If there was any other choice I would never ask this of you. "
         "\nTrain your fortitude and prove to her your worth.",
         35, None, None,
         "Breakthrough to level 35",
         'Chest', 5, None],
    19: [1, "Question Your Resolve", "Pandora, the Celestial",
         "Soul carving is an excruciatingly painful process so I just want to make sure... "
         "Your soul is all that you are and you needn't do this for my sake. "
         "\nNo one will fault you for backing down... take your time and consider carefully.",
         40, None, None,
         "Breakthrough to level 40",
         'Chest', 5, None],
    20: [0, "Price Of Power", "Pandora, the Celestial",
         "So you've already steeled yourself. I'm glad, but I feel I should still apologize to you. "
         "Even if you did release the Paragons, this was my responsibility. So... I'm sorry. "
         "\nIsolde is exceptionally skilled. No matter the pain your soul won't crumble or break.",
         1, 8, None,
         "Engrave your soul with an Insignia",
         'Catalyst', 1, 'Echelon 4'],
    21: [0, "Cursed By Contract", "Pandora, the Celestial",
         "Was it painful? The mark on your soul is beautiful and brimming with vitality. "
         "Not only will it be easier to defeat the demons, but you may be able to forge a pact with one. "
         "\nTake caution, they are still demons after all.",
         1, 9, None,
         "Forge a pact at a demonic altar in /map",
         'Crystal1', 2, None],
    22: [0, "Spoils of Steel", "Pandora, the Celestial",
         "The colourful 'flames' that envelop demons are produced by the ignition of colliding metallic dust. "
         "Their metallic dust, heart gem, and other components make great crafting materials. "
         "\nBring some back with you and we'll try to get something nice refined for you.",
         1, 10, None,
         "Equip a pair of Demon Greaves",
         'Chest', 5, None],
    23: [1, "Body and Mind", "Pandora, the Celestial",
         "You've gained great strength in such a short time and that takes a significant toll. "
         "Make sure to train your mind just as much as your body. "
         "\nYou must maintain full control over every aspect of yourself.",
         45, None, None,
         "Breakthrough to level 45",
         'Chest', 5, None],
    24: [1, "Omen of Thunder", "Pandora, the Celestial",
         "The abyss trembles as the storm approaches. We have a few days at most before Tyra reaches us. "
         "Close your eyes to the lightning and let my voice drown out the thunder.  "
         "\nSleep soundly tonight, I promise I'll keep you safe. ",
         50, None, None,
         "Breakthrough to level 50",
         'Chest', 5, None],
    25: [3, "The First Monster", "Pandora, the Celestial",
         "Tyra is the progenitor of monsters. In brute strength even Astratha is not his match. "
         "However, this is ultimately just a misdirection. The real threat is the electricity. "
         "I've seen firsthand the concentrated destruction a single of his thunderbolts can cause. "
         "\nI pray you don't find yourself on the receiving end.",
         1, 11, None,
         "Defeat the Demon Paragon",
         'Catalyst', 1, 'Echelon 5'],
    26: [1, "Crossing Of Worlds", "Pandora, the Celestial",
         "Tyra may be sealed, but the floodgates have opened. We failed to stop him from opening the celestial rift. "
         "As things stand my power is not enough to close it. The best course of action now is to attack first. "
         "\nWe've come this far... You will go with me won't you?",
         55, None, None,
         "Breakthrough to level 55",
         'Chest', 5, None],
    27: [2, "Encounter On Arrival", "Pandora, the Celestial",
         "No human has ventured into the celestial plane without my protection before. "
         "To withstand it through training alone is an incredible accomplishment and you should be proud. "
         "\nThey are aware of our presence, prepare to engage the enemy.",
         1, None, 'Stone4',
         "Retrieve a Paragon Stone",
         'Chest', 5, None],
    28: [5, "Harness Paragon Essence", "Pandora, the Celestial",
         "A paragon crest is the source of a True Paragon's divine essence. "
         "With my help you can claim this power as your own to fight them on equal footing. "
         "\nAre you ready to try?",
         1, 12, None,
         "Equip a Paragon Crest",
         'Chest', 5, None],
    29: [1, "Cultivate Divinity (Part 1)", "Pandora, the Celestial",
         "By taking in some of my divine essence you claim my authority as a deity over celestia. "
         "Over time my stars will become one with your domain. You must practice gathering your essence daily. "
         "\nTake great effort not to lose yourself along the way.",
         60, None, None,
         "Breakthrough to level 60",
         'Crystal2', 2, None],
    30: [2, "Messenger Of Celestia", "Pandora, the Celestial",
         "Until the time is right you must avoid the High Three at all costs. "
         "Continue to seal the True Paragons and recover my divine essence. "
         "You wield their power, but they are not like you. "
         "\nRemember. The paragons have never been human.",
         5, None, 'Stone4',
         "Retrieve 5 Paragon Stones",
         'Chest', 5, 'Echelon 6'],
    31: [2, "The Echoes Within", "Pandora, the Celestial",
         "When a significant gap in power exists you can exert direct control over an entity with lesser essence. "
         "For now just focus on manifesting the bound essences you've taken thus far. "
         "\nUse the cards and manifest it's essence.",
         1, 13, None,
         "Equip a tarot card with /tarot.",
         'Essence0', 5, None],
    32: [1, "Cultivate Divinity (Part 2)", "Pandora, the Celestial",
         "Channelling the essence of other paragons will give you a glimpse into their mind. "
         "Avoid temptations and don't spend too much time in that state. "
         "\nManifestation can be a double edged sword.",
         65, None, None,
         "Breakthrough to level 65",
         'Chest', 5, None],
    33: [2, "Shatter The Cycle", "Pandora, the Celestial",
         "It is no exaggeration to say that any of the High Three can bring an end to the mortal plane. "
         "If they were to combine their powers perhaps they could even overthrow the Arbiters. "
         "\nA delightful thought, but it will never come to pass.",
         10, None, 'Stone4',
         "Retrieve 10 Paragon Stones",
         'Chest', 5, None],
    34: [1, "Cultivate Divinity (Part 3)", "Pandora, the Celestial",
         "I sense something's not right. Stay here and continue to accumulate essence. "
         "Please... await my return and do not try to follow me. I'll return safe and sound. "
         "\nI promise.",
         70, None, None,
         "Breakthrough to level 70",
         'Chest', 5, None],
    35: [3, "A Promise Broken", "Pandora, the Celestial",
         "Oblivia has taken over my essence. I can't stop her. You can't stop her. All is lost."
         "\nPlease... while I'm still in control of myself... Kill me.",
         1, 14, None,
         "Defeat II - Pandora, the Celestial",
         'EssenceII', 3, 'Echelon 7'],
    36: [1, "Cultivate Divinity (Part 4)", "Pandora, the Celestial",
         "I could not have imagined you would be able to safely sever Oblivia's hold. "
         "It's not yet my time to reunite with Thana and return to the Samsara. "
         "\nThank you. For saving me.",
         75, None, None,
         "Breakthrough to level 75",
         'Chest', 5, None],
    37: [3, "Charge Into Terminus", "Oblivia, the Void",
         "So the new heir of Celestia wants to play the hero? I suppose I can give you a little attention. "
         "You rescued Pandora and now you think you can stand against erasure. "
         "\nBehold all consuming annihilation. ",
         1, 16, None,
         "Defeat III - Oblivia, The Void",
         'EssenceIII', 3, None],
    38: [0, "The Deep Void", "Pandora, the Celestial",
         "Accepting defeat Oblivia chose to expose the deep void. Perhaps she is extending an invitation. "
         "We must immediately investigate the gateway to the abyssal plane. "
         "\nNot even the Arbiters know what lies beyond.",
         1, 18, None,
         "Visit the abyssal plane using /abyss",
         'Crystal3', 2, None],
    39: [1, "Cultivate Divinity (Part 5)", "Pandora, the Celestial",
         "I don't want to admit that Oblivia is right, but I'm approaching my limits. "
         "Your growth is exceeding my craftsmanship and I won't be able to keep pace with you for much longer. "
         "\nI'll protect you from the pull of the abyss while you temper your gear.",
         80, None, None,
         "Breakthrough to level 80",
         'Chest', 5, None],
    40: [3, "All Or Nothing", "Pandora, the Celestial",
         "Akasha's strength is immeasurable, boundless, and unfathomable, but not unmatched. "
         "Render his advantage meaningless with Oblivia's essence and overcome him with your own ability. "
         "\nCreate a second miracle my child of the stars.",
         1, 17, None,
         "Defeat IV - Akasha, The Infinite",
         'EssenceIV', 3, 'Echelon 8'],
    41: [1, "The Endgame Beyond", "Pandora, the Celestial",
         "You're now the harbinger of two miracles. Eleuia won't ignore you any longer. "
         "Among the Paragons and even the High Three, she's... special. "
         "Her essence renders all things meaningless and yet she is unable to overcome her own nemesis. "
         "\nHer story is a sad one, but now is simply not the time.",
         85, None, None,
         "Breakthrough to level 85",
         'Chest', 5, None],
    42: [0, "A Justified Blasphemy", "Pandora, the Celestial",
         "As a baseline, you'll need to use every option available to you, no matter the cost. "
         "There will surely be more repercussions, but if we can't stop Eleuia the outcome will be far worse."
         "\nLet's go pay Kazyth a visit.",
         1, 19, None,
         "Use /meld to have the affinity of two jewels appraised",
         'Chest', 5, None],
    43: [0, "Spire of Illusions", "Pandora, the Celestial",
         "To overcome Eleuia's unique ability we set off for the Spire of Illusions. "
         "The tower will test you in ways you cannot imagine. My hammer was sealed there in the last Paragon War. "
         "\nI can fight beside you if we are able reclaim it. ",
         1, 15, None,
         "Attempt the Spire of Illusions with /gauntlet",
         'Shard', 5, None],
    44: [1, "Cultivate Divinity (Part 6)", "Pandora, the Celestial",
         "I'm sorry for getting mad at you earlier. I know it's not your fault that they shattered my precious hammer. "
         "Even if we gathered all the shards, it's beyond my power now to reforge it. "
         "\nYou should hold onto them. Maybe you can find a way. ",
         90, None, None,
         "Breakthrough to level 90",
         'Chest', 10, None],
    45: [3, "Ending A Wish", "Eleuia, the Wish",
         "Has my blessing has served you well, Child of Celestia?  Have you come to end my wish or to grant it? "
         "Or perhaps you aren't even aware my desire? What I want was never once a part of your decision to seal me. "
         "A mere primeval atom cannot stop me, let alone uproot the Divine Lotus.. "
         "\nIf we must fight, will you first hear my wish? "
         "\n**WARNING: IRREVERSIBLE DECISION**",
         1, 20, None,
         "Defeat XXV - Eleuia, The Wish",
         'Gemstone10', 1, 'Echelon 9'],
    46: [1, "Through The Ether", "Pandora, the Celestial",
         "It almost seemed like Eleuia didn't actually want to stop us. "
         "The primeval atom has given birth to a new reality free from the grip of the divine. "
         "The Arbiters will see this as a transgression against the divine laws. "
         "\nConflict is inevitable.",
         95, None, None,
         "Breakthrough to level 95",
         'Crystal4', 2, None],
    47: [3, "A Flower Foregone", "Fleur, Oracle of the True Laws",
         "At last you've come for me. Just as I have already foretold your demise, I have seen my own. "
         "I am aware that I cannot best you, but I will not go down easily. "
         "\nOnce I am gone, Yubelle will take from you what matters most. ",
         1, 21, None,
         "Defeat XXVIII - Fleur, Oracle of the True Laws",
         'Summon3', 5, None],
    48: [3, "A God's Judgement", "Yubelle, Adjudicator of the True Laws",
         "You turn against the Arbiters? You seek to steal from God? You defy the Divine Lotus? "
         "I name your crimes. Subversion. Betrayal. Theft. Heresy. Sacrilege. "
         "\nI grant you judgement for your sins.",
         1, 22, None,
         "Defeat XXIX - Yubelle, Adjudicator of the True Laws",
         'EssenceXXIX', 1, None],
    49: [1, "Unshackled By Mortality", "Pandora, the Celestial",
         "In these final moments I offer to you my heartfelt appreciation. "
         "My remaining essence is weak and I can feel it being consumed as he siphons energy to sustain his form. "
         "Stop this divine coronation before he assimilates with the Divine Lotus and ascends to the god plane. "
         "\nI will always..."
         "\n*Pandora Smiles*"
         "\nFarewell",
         100, None, None,
         "Breakthrough to level 100",
         'Lotus10', 1, None],
    50: [3, "Root Of Reality", "Echo of Thana, the Death",
         "All this power, but you let her slip through your fingers. What little essence she had left is all but gone. "
         "Lamenting my sister can wait, the divine palace beckons as Yubelle assumes a new form. "
         "\nWhy are you still here? Did you have something to say? "
         "\n**WARNING: IRREVERSIBLE DECISION**",
         1, 23, None,
         "Defeat XXX - Nephilim, Incarnate of the Divine Lotus [Challenger] (/palace)",
         'Chest', 50, 'Echelon 10 (MAX)'],
    51: [10, "Pandora's Box", "Echo of Eleuia, the Wish",
         "A hollow victory. Pandora's essence is lost and Yubelle has only been temporarily sealed away. "
         "You look distraught, what will you do now that you possess a fraction of the true divinity? "
         "I see... so you would still endeavor to fulfill a now meaningless promise. "
         "\nPerhaps in that little box, you can finally find peace.",
         31, 24, None,
         "Complete the Tarot Collection",
         'Chest', 50, None],
    52: [3, "Dance With Despair", "Echo of Eleuia, the Wish",
         "Can you see now why Fleur foresaw the futility in your future? She wasn't wrong, she only lacks the context. "
         "This form Yubelle has taken is recursive and growing in a pursuit of victory through fate and inevitability. "
         "\nKnowing this, will you still chase after your demise?",
         1, 25, None,
         "Defeat XXX - Nephilim, Incarnate of the Divine Lotus [Usurper]",
         'Chest', 50, None],
    53: [3, "A Heartfelt Wish", "Echo of Eleuia, the Wish",
         "I had resigned to my fate believing that gods could not be slain, but now I see even divinity has a limit. "
         "Perhaps, as Yubelle approaches the apex, I can finally entrust to you my true wish."
         "\nPlease, save us all.",
         1, 26, None,
         "Defeat XXX - Nephilim, Incarnate of the Divine Lotus [Samsara]",
         'Chest', 50, None],
    54: [2, "A Moment Forever", "Pandora, the Celestial",
         "Just how far have you come just to see me again? Alas, you of all people should know this form is temporary. "
         "My essence is fragmented beyond repair, and I can't hold the pieces together. "
         "\nBut maybe... we can enjoy this moment a little longer."
         "\n**WARNING: IRREVERSIBLE DECISION**",
         1, None, 'Rings',
         "Choose a special gift.",
         'Chest', 100, None],
    55: [1, "A New Life", "[OATH]",
         "In the times to come... for better and for worse."
         "\nI will stay by your side.",
         None, None, None,
         "The End",
         None, 1, None]}

# Button Name, Variant Reward, Unique Text
quest_options = {
    45: [
        # Enables Eleuia ending.
        ["Accept", "EssenceXXV",
         "I am a fake, a Paragon of curses. I need only wish you gone and it will be so. But, this is a false wish. "
         "Have you any idea the disparity of a real wish and a desire? It is a cursed desire that cannot be reached. "
         "Every passing moment I shed tears for a dream of freedom that I alone cannot make into reality. "
         "\nI cannot tell you my wish yet. It is enough that you were willing to listen, Child of Celestia"],
        ["Refuse", "Gemstone10",
         "It matters not. Although it pains me to hear you say that, the truth is that I cannot tell you anyways. "
         "It is not your burden to cry my tears. It is not your duty to fulfill my wish. "
         "\nEnough talk, I will see for myself if you are worthy of my blessing, Child of Celestia."]],
    50: [
        ["Request Help", "EssenceII",
         "Pandora is not dead, but her essence has been absorbed by the Divine Lotus. "
         "I preside solely over the Samsara and have no means to restore my sister's lost essence. "
         "Defeating Yubelle is also insufficient. Do you understand now? Let's not dwell on this any longer. "
         "\nFinish what you started. I'll be watching."],
        ["Do Nothing", "Gemstone10",
         "Very well. The time for talking is over. "
         "\nFinish what you started. I'll be watching."],
        # Enables Thana Ending
        ["Profess Love", "EssenceXIII",
         "Huh!? My sister is gone and that's what you have to say to me? This isn't the time or the place for jokes. "
         "You're really serious? Fine, if you feel that way then restore my sister's essence and I will hear you out. "
         "\nUntil then don't talk to me."]],
    54: [
        ["Pandora's Gift", "Blood",
         "Rings faceted with gems forged from the twin mystical stars. "
         "It is said that the two stars used to be lovers, but were forced apart by god. "
         "The star of light exists only at night in the physical world, "
         "meanwhile the star of darkness traverses the spiritual world during the daytime."
         "The misfortune they bring is a manifestation of their anguish as they cry amidst the lonely sky. "
         "Now reunited, not a trace of malice remains. They radiate with the power of rebirth and a new life. "
         "\nA lovely tale is it not? Do you think we too could start anew?"],
        ["Thana's Gift", "Blood",
         "A ring of golden skulls belonging to those of my ancient legion. Unable to find rest, but free from misuse. "
         "They can continue to serve me for eternity, how very fitting. I will accept this gift, but are you certain? "
         "You've fulfilled your promise and I have said my farewells, but I can't replace my sister. "
         "Is it really me that you want? Can you accept who I am? Can you accept the things I've done? "
         "\n...\nI love you too."],
        ["Eleuia's Gift", "Blood",
         ""]],
}

# Quest Number, Oath Position, Choice Adjustment
eligibility_dict = {45: [2, {0: 1, 1: 0}], 50: [1, {0: 0, 1: 0, 2: 1}]}
oath_dict = ["Pandora, the Celestial", "Thana, the Death", "Eleuia, the Wish"]