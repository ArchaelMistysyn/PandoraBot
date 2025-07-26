import globalitems as gli

itemdata_dict = {}


def build_item_dict(input_dict, input_data, starting_index=1, category="Misc", unique_index=False):
    for row_index, current_row in enumerate(input_data, starting_index):
        temp_id = f"{category}{row_index}" if not unique_index else current_row[0]
        data = {'item_id': temp_id, "name": current_row[1], "rate": current_row[2], "tier": current_row[3],
                "emoji": current_row[4], "description": current_row[5], "cost": current_row[6], "category": category}
        input_dict[temp_id] = data
    return input_dict


# Fae Data List
fae_emoji_list = ["<:Fae0:1274786282010316913>", "<:Fae1:1274786289782358097>", "<:Fae2:1274786296560091189>",
                  "<:Fae3:1274786324196364298>", "<:Fae4:1274786339065168078>", "<:Fae5:1274786346740879411>",
                  "<:Fae6:1274786355104186378>", "<:Fae7:1274786363052654777>", "<:Fae8:1274786370497417330>"]
fae_data = [[None, f'Fae Core ({element})', 100, 1, emoji,
             f'The core harvested from a {element.lower()} fae spirit. Brimming with elemental energies.', 500]
            for i, element, emoji in zip(range(9), gli.element_names, fae_emoji_list)]
itemdata_dict = build_item_dict(itemdata_dict, fae_data, starting_index=0, category="Fae")

# Token List Data
token_data = [[None, 'Changeling Token', 100, 1, '<a:elootitem:1144477550379274322>',
               'An ancient token. Can be used to change your class or username.', 100000],
              [None, 'Soulweaver Token', 100, 2, '<a:elootitem:1144477550379274322>',
               'An ancient token. Can be used for insignia engraving and upgrades.', 100000],
              [None, 'Pathwalker Token', 100, 3, '<a:elootitem:1144477550379274322>',
               'An ancient token. Can be used to reset all skill points.', 100000],
              [None, 'Lifeblood Token', 100, 4, '<a:elootitem:1144477550379274322>',
               'An ancient token. Can be used to reshape dragon heart gems.', 100000],
              [None, 'Scribe Token', 100, 5, '<a:elootitem:1144477550379274322>',
               'An ancient token. Can be used to enscribe weapons.', 250000],
              [None, 'Oracle Token', 100, 6, '<a:elootitem:1144477550379274322>',
               'An ancient token. Can be used to obtain lotus items.', 500000],
              [None, 'Adjudicator Token', 100, 7, '<a:elootitem:1144477550379274322>',
               'An ancient token. ???.', 500000]]
itemdata_dict = build_item_dict(itemdata_dict, token_data, category="Token")

# Summoning List Data
summon_data = [[None, 'Summoning Relic', 100, 5, '<a:elootitem:1144477550379274322>',
                'Perform a summoning ritual to summon a tier 5 paragon solo boss.', 50000],
               [None, 'Summoning Artifact', 100, 6, '<a:elootitem:1144477550379274322>',
                'Perform a summoning ritual to summon a tier 6 paragon solo boss.', 100000],
               [None, 'Summoning Prism', 100, 7, '<a:elootitem:1144477550379274322>',
                'Perform a summoning ritual to summon a tier 7 arbiter solo boss.', 500000]]
itemdata_dict = build_item_dict(itemdata_dict, summon_data, category="Summon")

# Stone List Data
stone_type = ["Fortress", "Dragon", "Demon", "Paragon", "Ruler", "Arbiter"]
stone_data = [[None, 'Fortress Stone', 100, 1, '<:St1:1398709966818381954>', None, 0],
              [None, 'Dragon Stone', 100, 2, '<:St2:1398709978126352504>', None, 0],
              [None, 'Demon Stone', 100, 3, '<:St3:1398709988423372970>', None, 0],
              [None, 'Paragon Stone', 100, 4, '<:St4:1398710000448176188>', None, 0],
              [None, "Ruler's Stone", 100, 8, '<:St5:1398710011366084670>', None, 0],
              [None, 'Arbiter Stone', 100, 6, '<:St6:1398710023055740988>', None, 0]]
for index, row in enumerate(stone_data):
    row[5] = f'Obtained from {stone_type[index].lower()} bosses. It\'s a stone.'
itemdata_dict = build_item_dict(itemdata_dict, stone_data, category="Stone")

# Stamina Potion Data
potion_values = [500, 1000, 2500, 5000]
stamina_data = [[None, 'Lesser Stamina Potion', 100, 1, "<:Pot1:1388915732863258774>", None, 2500],
                [None, 'Standard Stamina Potion', 100, 2, "<:Pot2:1388915746226049165>", None, 5000],
                [None, 'Greater Stamina Potion', 100, 3, "<:Pot3:1388915758939246612>", None, 10000],
                [None, 'Ultimate Stamina Potion', 100, 4, "<:Pot4:1388915769756352583>", None, 20000]]
for index, row in enumerate(stamina_data):
    row[5] = f'Consume to restore {potion_values[index]} stamina.'
itemdata_dict = build_item_dict(itemdata_dict, stamina_data, category="Potion")

# Trove Data
trove_rewards = {1: [1000, 5000, 1], 2: [5000, 10000, 10], 3: [10000, 20000, 50], 4: [20000, 35000, 100],
                 5: [35000, 50000, 500], 6: [50000, 75000, 1000], 7: [75000, 100000, 2000],
                 8: [100000, 1000000, 3000], 9: [1000000, 10000000, 25000]}
trove_data = [[None, 'Lesser Lotus Trove', 100, 1, '<:T1:1381687964215677028>', None, 0],
              [None, 'Standard Lotus Trove', 100, 2, '<:T2:1381687990400581743>', None, 0],
              [None, 'Greater Lotus Trove', 100, 3, '<:T3:1381688005156143216>', None, 0],
              [None, 'Ultimate Lotus Trove', 100, 4, '<:T4:1381688022210445454>', None, 0],
              [None, 'Voidworn Lotus Trove', 100, 5, '<:T5:1381688061104095394>', None, 0],
              [None, 'Miraculous Lotus Trove', 100, 6, '<:T6:1381688080838164490>', None, 0],
              [None, 'Abyssal Lotus Trove', 100, 7, '<:T7:1381688095296196618>', None, 0],
              [None, 'Divine Lotus Trove', 100, 8, '<:T8:1381688107853676554>', None, 0],
              [None, 'Sacred Lotus Trove', 100, 9, '<:T9:1381688120231067749>', None, 0]]
for row in trove_data:
    tier = row[3]
    bounds = trove_rewards[tier]
    lotus_rate = f"{bounds[2] / 1000:.4f}".rstrip('0').rstrip('.')
    row[5] = f'Open to receive {bounds[0]:,} - {bounds[1]:,} lotus coins.\nSpecial reward rates: '
    if tier == 9:
        t9_msg = f'\n50% Base Lotus\n15% Seal of Salvation\n15% Sacred Blood\n15% Divine Lotus\n5% Rainbow Lotus'
        row[5] += t9_msg
    else:
        row[5] += f'{lotus_rate}%'
itemdata_dict = build_item_dict(itemdata_dict, trove_data, category="Trove")

# Ore and Soul List Data in the new structure
heaven_ore = ("A fully purified ore chunk. It shines with the same spectacular light as the most exceptional of items. "
              "Used for reinforcing gear items. Increasing the quality.")
ore_data = [[None, 'Crude Ore', 2, 1, '<:O1:1381693225697284287>', None, 2500],
            [None, 'Cosmite Ore', 5, 2, '<:O2:1381693241543495831>', None, 5000],
            [None, 'Celestite Ore', 10, 3, '<:O3:1381693256311509142>', None, 10000],
            [None, 'Crystallite Ore', 50, 4, '<:O4:1381693272195600576>', None, 50000],
            [None, 'Heavenly Ore', 100, 5, '<:O5:1381693284014882846>', heaven_ore, 1000000]]
for row in ore_data:
    row[5] = f'Ore with {row[2]}% purity. With enough samples, perhaps the purity can be raised.'
itemdata_dict = build_item_dict(itemdata_dict, ore_data, category="Ore")

# Flame Items
flame_data = [[None, 'Purgatorial Flame', 50, 3, '<a:eshadow2:1141653468965257216>',
               '75% chance to reforge the base stats and unique ability of a gear item within its tier.', 5000],
              [None, 'Abyss Flame', 75, 7, '<a:evoid:1145520260573827134>',
               '50% chance to reroll a unique ability on tier 5+ gear.', 0]]
itemdata_dict = build_item_dict(itemdata_dict, flame_data, category="Flame")

# Fragment Item Data
fragment_data = [[None, 'Fragmentized Void', 100, 5, '<:Frag1:1274785172658847816>',
                  'A fragment containing the essence of the void. Used for forging, infusion and crafting.', 0],
                 [None, 'Fragmentized Wish', 100, 6, '<:Frag2:1274785184692306092>',
                  'A fragment containing the essence of a wish. Used for forging, infusion and crafting.', 0],
                 [None, 'Fragmentized Abyss', 100, 7, '<:Frag3:1274785194192408631>',
                  'A fragment containing the essence of the abyss. Used for forging, infusion and crafting.', 0],
                 [None, 'Fragmentized Divinity', 100, 8, '<:Frag4:1274785216380272690>',
                  'A fragment containing the essence of divinity. Used for forging, infusion and crafting.', 0]]
itemdata_dict = build_item_dict(itemdata_dict, fragment_data, category="Fragment")

# Crystallized List Data
crystallized_data = [
    [None, 'Crystallized Void', 100, 5, '<:Cry1:1274785116572614856>',
     'A crystal containing the essence of the void. Used for forging, infusion and crafting.', 0],
    [None, 'Crystallized Wish', 100, 6, '<:Cry2:1274785124491460738>',
     'A crystal containing the essence of a wish. Used for forging, infusion and crafting.', 0],
    [None, 'Crystallized Abyss', 100, 7, '<:Cry3:1274785135081820170>',
     'A crystal containing the essence of the abyss. Used for forging, infusion and crafting.', 0],
    [None, 'Crystallized Divinity', 100, 8, '<:Cry4:1274785143218769981>',
     'A crystal containing the essence of divinity. Used for forging, infusion and crafting.', 0]]
itemdata_dict = build_item_dict(itemdata_dict, crystallized_data, category="Crystal")

# Skull List Data
skull_data = [[None, 'Cursed Golden Skull', 1, 5, '<:Skull1:1274786865211244575>',
               'A skull of pure gold that whispers to you softly.', 100000],
              [None, 'Haunted Golden Skull', 10, 6, '<:Skull2:1274786874355093514>',
               "A golden skull that exudes darkness. Placing it against your ear is clearly a bad idea.", 1000000],
              [None, 'Radiant Golden Skull', 100, 7, '<:Skull3:1274786883771301941>',
               "A golden skull with a serene aura. Yet screaming can occasionally be heard from within."
               " [Ultra Rare]", 10000000],
              [None, 'Prismatic Golden Skull', 1000, 9, '<:Skull4:1274786891677302784>',
               "A golden skull that sparkles extraordinarily. Beware the lustful voices calling your name."
               " [Ultimate Rare]", 100000000]]
itemdata_dict = build_item_dict(itemdata_dict, skull_data, category="Skull")

# Unrefined Void Items List Data
gear_types = [geartype for geartype in gli.gear_types if geartype not in ["Ring", "Gem"]]
gear_icons = [icon for icon in gli.gear_icons if "Ring" not in icon and "Gem" not in icon]
unrefined_void_data = []
for index in range(6):
    success_rate = 80 if index != 0 else 100
    temp_list = [None, f"Unrefined Void Item ({gear_types[index]})", success_rate, 5, gear_icons[index],
                 f'Refine for 50% chance to receive a tier 5 {gli.gear_types[:6][index].lower()}.', 0]
    unrefined_void_data.append(temp_list)
itemdata_dict = build_item_dict(itemdata_dict, unrefined_void_data, category="Void")

# Unrefined Misc Items List Data
unrefined_misc_data = [[None, 'Unrefined Dragon Wings', 75, 4, '<:Wings4:1275576140202770536>',
                        'Refine for 75% chance to receive tier 2-4 dragon wings.', 0],
                       [None, 'Unrefined Demon Greaves', 75, 4, '<:Greaves4:1275575740036812830>',
                        'Refine for 75% chance to receive a tier 2-4 demon Greaves.', 0],
                       [None, 'Unrefined Paragon Crest', 75, 4, '<:Crest4:1275576371053203526>',
                        'Refine for 75% chance to receive a tier 2-4 paragon crest.', 0]]
itemdata_dict = build_item_dict(itemdata_dict, unrefined_misc_data, category="Unrefined")

# Unrefined Gems List Data
unrefined_gem_data = [[None, 'Unrefined Dragon Gem', 75, 2, '<:Gem_2:1275569715078627359>',
                       'Refine for 75% chance to receive tier 2-4 dragon gem.', 0],
                      [None, 'Unrefined Demon Gem', 75, 3, '<:Gem_3:1275569723568029786>',
                       'Refine for 75% chance to receive a tier 2-4 demon gem.', 0],
                      [None, 'Unrefined Paragon Gem', 75, 4, '<:Gem_4:1275569729737719879>',
                       'Refine for 75% chance to receive a tier 2-4 paragon gem.', 0]]
itemdata_dict = build_item_dict(itemdata_dict, unrefined_gem_data, category="Gem")

# Unrefined Jewel List Data
unrefined_jewel_data = [[None, 'Unrefined Dragon Jewel', 75, 5, '<:Gem_5:1275569736205340773>',
                         'Refine for 50% chance to receive tier 5-8 dragon jewel.', 0],
                        [None, 'Unrefined Demon Jewel', 75, 5, '<:Gem_5:1275569736205340773>',
                         'Refine for 50% chance to receive a tier 5-8 demon jewel.', 0],
                        [None, 'Unrefined Paragon Jewel', 75, 5, '<:Gem_5:1275569736205340773>',
                         'Refine for 50% chance to receive a tier 5-8 paragon jewel.', 0],
                        [None, 'Unrefined Arbiter Jewel', 75, 7, '<:Gem_7:1275569749173993503>',
                         'Refine for 50% chance to receive a tier 6-8 arbiter jewel.', 0],
                        [None, 'Unrefined Incarnate Jewel', 75, 8, '<:Gem_8:1275569754932777072>',
                         'Refine for 50% chance to receive a tier 7-8 incarnate jewel.', 0]]
itemdata_dict = build_item_dict(itemdata_dict, unrefined_jewel_data, category="Jewel")

# Essence List Data
essence_data = [['Essence0', 'Essence of The Reflection', 10, 1, '<:Essence1:1297651488432062585>', None, 0],
                ['EssenceI', 'Essence of The Magic', 10, 1, '<:Essence1:1297651488432062585>', None, 0],
                ['EssenceII', 'Essence of The Celestial', 10, 4, '<:Essence4:1297651533139411024>', None, 0],
                ['EssenceIII', 'Essence Of The Void', 10, 5, '<:Essence5:1297651547186139206>', None, 0],
                ['EssenceIV', 'Essence Of The Infinite', 10, 5, '<:Essence5:1297651547186139206>', None, 0],
                ['EssenceV', 'Essence of The Duality', 10, 3, '<:Essence3:1297651518320807997>', None, 0],
                ['EssenceVI', 'Essence of The Love', 10, 1, '<:Essence1:1297651488432062585>', None, 0],
                ['EssenceVII', 'Essence of The Dragon', 10, 4, '<:Essence4:1297651533139411024>', None, 0],
                ['EssenceVIII', 'Essence of The Behemoth', 10, 4, '<:Essence4:1297651533139411024>', None, 0],
                ['EssenceIX', 'Essence of The Memory', 10, 1, '<:Essence1:1297651488432062585>', None, 0],
                ['EssenceX', 'Essence of The Temporal', 10, 3, '<:Essence3:1297651518320807997>', None, 0],
                ['EssenceXI', 'Essence of The Heavens', 10, 3, '<:Essence3:1297651518320807997>', None, 0],
                ['EssenceXII', 'Essence of The Abyss', 10, 3, '<:Essence3:1297651518320807997>', None, 0],
                ['EssenceXIII', 'Essence of The Death', 10, 3, '<:Essence3:1297651518320807997>', None, 0],
                ['EssenceXIV', 'Essence of The Clarity', 10, 1, '<:Essence1:1297651488432062585>', None, 0],
                ['EssenceXV', 'Essence of The Primordial', 10, 4, '<:Essence4:1297651533139411024>', None, 0],
                ['EssenceXVI', 'Essence of The Fortress', 10, 4, '<:Essence4:1297651533139411024>', None, 0],
                ['EssenceXVII', 'Essence of The Starlight', 10, 2, '<:Essence2:1297651504416817162>', None, 0],
                ['EssenceXVIII', 'Essence of The Moon', 10, 2, '<:Essence2:1297651504416817162>', None, 0],
                ['EssenceXIX', 'Essence of The Sun', 10, 2, '<:Essence2:1297651504416817162>', None, 0],
                ['EssenceXX', 'Essence of The Requiem', 10, 2, '<:Essence2:1297651504416817162>', None, 0],
                ['EssenceXXI', 'Essence of The Creation', 10, 2, '<:Essence2:1297651504416817162>', None, 0],
                ['EssenceXXII', 'Essence of The Changeling', 10, 1, '<:Essence1:1297651488432062585>', None, 0],
                ['EssenceXXIII', 'Essence of The Pathwalker', 10, 2, '<:Essence2:1297651504416817162>', None, 0],
                ['EssenceXXIV', 'Essence of The Soulweaver', 10, 3, '<:Essence3:1297651518320807997>', None, 0],
                ['EssenceXXV', 'Essence of The Wish', 10, 6, '<:Essence6:1297651560972812309>', None, 0],
                ['EssenceXXVI', 'Essence of The Lifeblood', 10, 4, '<:Essence4:1297651533139411024>', None, 0],
                ['EssenceXXVII', 'Essence of The Scribe', 10, 5, '<:Essence5:1297651547186139206>', None, 0],
                ['EssenceXXVIII', 'Essence of The Oracle', 10, 6, '<:Essence6:1297651560972812309>', None, 0],
                ['EssenceXXIX', 'Essence of The Adjudicator', 10, 7, '<:Essence7:1297651572905480203>', None, 0],
                ['EssenceXXX', 'Essence of The Lotus', 10, 8, '<:Essence8:1297651586834632724>', None, 0]]
for index, row in enumerate(essence_data):
    row[5] = f'Perform a binding ritual to attempt to seal this essence into card form.'
    if row[0] == "EssenceXXX":
        row[5] += " [Ultimate Rare]"
itemdata_dict = build_item_dict(itemdata_dict, essence_data, category="Essence", unique_index=True)

# Lotus List Data
lotus_data = [[None, 'Lotus of Nightmares', 100, 8, '<:Lotus1:1274786435869704275>',
               'Used for Divine Synthesis (Weapon).  Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Lotus of Prosperity', 100, 8, '<:Lotus2:1274786443558129745>',
               'Used for Divine Purification (Amulet). Increases the tier to 8. [Ultra Rare]', 9999999],
              [None, 'Lotus of Serenity', 100, 8, '<:Lotus3:1274786460486336605>',
               'Used for Divine Purification (Greaves).  Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Lotus of Freedom', 100, 8, '<:Lotus4:1274786468577021982>',
               'Used for Divine Purification (Wings). Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Lotus of Eternity', 100, 8, '<:Lotus5:1274786474994176051>',
               'Used for Divine Melding (Jewels). Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Lotus of Abundance', 100, 8, '<:Lotus6:1274786482141270036>',
               'Used for Divine Purification (Armour). Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Lotus of Domination', 100, 8, '<:Lotus7:1274786490790187192>',
               'Used for Divine Purification (Crest).  Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Lotus of Divergence', 100, 8, '<:Lotus8:1274786498218299546>',
               'Used for Divine Mutation (Insignia).  Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Lotus of Revelations', 100, 8, '<:Lotus9:1274786511023378482>',
               'Used for Divine Synthesis (Tarot).  Increases the tier to 8. [Ultra Rare]', 0],
              [None, 'Divine Lotus', 100, 8, '<:Lotus10:1274786518111748177>',
               "The key to divinity and the object of the Arbiter's worship. [Uber Rare]", 0],
              [None, 'Rainbow Lotus', 100, 8, '<:Lotus11:1274786525560701132>',
               'A mythical lotus dyed by the colours of fate. [Ultimate Rare]', 0]]
itemdata_dict = build_item_dict(itemdata_dict, lotus_data, category="Lotus")

# Gemstone Item Data
gemstone_data = [
    [None, 'Blazing Ruby', 100, 6, '<:Gem0:1274785255819317299>',
     "Pulsing with volcanic force, this gem radiates with an intense heat.", 0],
    [None, 'Drowned Sapphire', 100, 6, '<:Gem1:1274785264396402798>',
     "Formed from colliding waves and tides, this gem holds the depths of the ocean within.", 0],
    [None, 'Silent Topaz', 100, 6, '<:Gem2:1274785278053060771>',
     "Crackling with electricity, this gem is often used as an energy source.", 0],
    [None, 'Ancient Agate', 100, 6, '<:Gem3:1274785287939166313>',
     "Hardened by the earth, this gem has a high density and is exceptionally sturdy.", 0],
    [None, 'Whispering Emerald', 100, 6, '<:Gem4:1274785308189393048>',
     "A destructive gale condensed into a single stone, air leaks out from this gem creating a gentle breeze.", 0],
    [None, 'Arctic Zircon', 100, 6, '<:Gem5:1274785316858757307>',
     "Despite the chilling aura, this gem's pure surface mirrors it's surroundings.", 0],
    [None, 'Haunted Obsidian', 100, 6, '<:Gem6:1274785324819812413>',
     "Dark and ominous, this small gem casts a foreboding shadow.", 0],
    [None, 'Prismatic Opal', 100, 6, '<:Gem7:1274785332465762375>',
     "Gleaming with radiance, it shines with all kinds of vibrant colours.", 0],
    [None, 'Spatial Lapis', 100, 6, '<:Gem8:1274785341081124915>',
     "Shimmering endlessly, the inside of this gem is boundless like the starry night.", 0],
    [None, 'Soul Diamond', 100, 6, '<:Gem9:1274785353299136542>',
     "A gem of crystallized soul, a priceless treasure.", 0],
    [None, 'Aurora Tear', 100, 7, '<:Gem10:1274786217375830027>',
     "If you gaze within you can make out the remnants of the dream from which it was formed.", 2000000],
    [None, 'Stone of the True Void', 100, 8, '<:Gem11:1274786225978609764>',
     "An impossible gem, it embodies the infinite nothingness within the depths of the void. [Uber Rare]", 0]]
itemdata_dict = build_item_dict(itemdata_dict, gemstone_data, starting_index=0, category="Gemstone")

# Fish Item Data
fish_list = [("**Sawshark** [Pristiophoridae]", 1), ("**Slippery Dick** [Halichoeres bivittatus]", 1),
             ("**Scorpionfish** [Scorpaenidae]", 1), ("**Clownfish** [Amphiprioninae]", 1),
             ("**Hammerhead Shark** [Sphyrnidae]", 2), ("**Old Wife** [Enoplosus armatus]", 2),
             ("**Glass Catfish** [Kryptopterus vitreolus]", 2), ("**Jellyfish** [Scyphozoa]", 2),
             ("**Nurse Shark** [Ginglymostoma cirratum]", 3), ("**Wahoo** [Acanthocybium solandri]", 3),
             ("**Frogfish** [Antennariidae]", 3), ("**Butterflyfish** [Chaetodontidae]", 3),
             ("**Cookiecutter Shark** [Isistius brasiliensis]", 4), ("**Four-Eyed Fish** [Anableps anableps]", 4),
             ("**Coffinfish** [Chaunax endeavouri]", 4), ("**BoxFish** [Ostraciidae]", 4),
             ("**Goblin Shark** [Mitsukurina owstoni]", 5), ("**Obese Dragonfish** [Opostomias micripnus]", 5),
             ("**Anglerfish** [Lophiiformes]", 5), ("**Swordfish** [Xiphias gladius]", 5),
             ("**Zebra Shark** [Stegostoma fasciatum]", 6), ("**Blue Bastard** [Plectorhinchus caeruleonothus]", 6),
             ("**Sunfish** [Mola mola]", 6), ("**Angelfish** [Pomacanthidae]", 6),
             ("**Whale Shark** [Rhincodon typus]", 7), ("**Whitemargin Stargazer** [Uranoscopus sulphureus]", 7),
             ("**Viperfish** [Chauliodus sloani]", 7), ("**Spookfish** [Opisthoproctidae]", 7)]
fish_description = 'Amazing! What a cute fish. So adorable!'
fish_data = []
fish_icon_list = ["<:F1:1398709770147467347>", "<:F2:1398709784412291102>", "<:F3:1398709795636379748>",
                  "<:F4:1398709807556460634>", "<:F5:1398709820466659471>", "<:F6:1398709831476711586>",
                  "<:F7:1398709857573535867>"]
for (fish_name, fish_tier) in fish_list:
    fish_data.append([None, fish_name, 100, fish_tier, fish_icon_list[fish_tier - 1], fish_description, 0])
itemdata_dict = build_item_dict(itemdata_dict, fish_data, starting_index=1, category="Fish")

# Heart Item Data
heart_data = [[None, 'Radiant Heart', 100, 6, '<:Heart1:1274786406182420615>', 'Used for various infusions.', 0],
              [None, 'Chaos Heart', 100, 7, '<:Heart2:1274786413434507266>', 'Used for various infusions.', 0]]
itemdata_dict = build_item_dict(itemdata_dict, heart_data, category="Heart")

# Uncategorized Item Data
uncategorized_data = [
    ['Catalyst', 'Gemstone Catalyst', 100, 5, '<:Cata:1274786559996198944>',
     "A hollow transparent gemstone. It's true nature can be revealed through elemental infusion.", 500000],
    ["Hammer", 'Astral Hammer', 80, 2, '<:Hmr:1388913551443361872>',
     'Used to reroll specific item rolls. Works on tier 4 and lower gear items.', 50000],
    ["Pearl", 'Stellar Pearl', 75, 4, '<:Prl:1388913620775076000>',
     'Augments an item roll. Increases the tier by 1.', 50000],
    ["Matrix", 'Socket Matrix', 5, 3, '<a:elootitem:1144477550379274322>',
     '5% Chance to add a socket to a gear item.', 5000],
    ['Chest', 'Chest', 100, 1, '<:Chest:1398709914381324318>', 'Contains a random item.', 50000],
    ['Shard', "Sovereign Shard", 100, 7, '<a:elootitem:1144477550379274322>',
     "A fragment of an ancient weapon. Perhaps it can be reforged.", 0],
    ['Scrap', 'Equipment Scrap', 100, 1, '<:Scrap:1274787448681005158>',
     "One of many countless pieces of Pandora's Legendary Hammer.", 0],
    ['Compass', 'Illusory Compass', 100, 6, '<:Cmps:1388913589535899758>',
     'An enigmatic compass said to be capable of locating the Spire of Illusions.', 500000],
    ['DarkStar', 'Dark Star of Shattered Dreams', 100, 8, '<:DarkStar:1274786619446267954>',
     "Legend tells of a star engulfed in black flames that heralds great disasters. "
     "The old records describe visions of the dark star blocking out the sun leaving chaos in it's wake."
     " [Uber Rare]", 0],
    ['LightStar', 'Glittering Star of Fractured Hearts', 100, 8, '<:LightStar:1274786610411475105>',
     "Legend tells of a star often spotted by lovers as it dazzles and sparkles amidst the black night. "
     "The old records indicate that the star was so beautiful it would steal the hearts of those who saw it."
     " [Uber Rare]", 0],
    ['Nadir', 'Phantasm of Nadir', 100, 8, '<:Nadir:1398709896697872435>',
     "Amidst the vastest oceans, this tiny fish is exceedingly elusive. They dwell in the deepest trenches. "
     "Their pitch-black scales conceal precious and unique gems that grow inside their small bodies. [Ultimate Rare]", 0],
    ['RoyalCoin', 'Royal Lotus Coin', 100, 8, '<:rCoin:1274786667277848657>',
     "A sacred coin blessed by gods. It is said to be indestructible.", 0],
    ['Nephilim', "Nephilim's Wicked Heart", 100, 8, '<:Nephilim:1274786631903084646>',
     "The heart of the lotus incarnate. It's divine luster has long since withered away "
     "leaving a lingering resentment in it's place. [Ultimate Rare]", 0],
    ['Pandora', "Pandora's Twinkling Heart", 100, 8, '<:Pandora:1274786639754952746>',
     "The spiritual heart of the celestial paragon. "
     "At the dawn of creation Pandora bore her celestial heart as a power source for her hammer. [Ultimate Rare]", 0],
    ['Ruler', "Ruler's Crown Jewel", 100, 9, '<:r_jewel:1274786590216159422>',
     "A jewel of unmatched quality, unparalleled value, and unfathomable beauty. A truly unique treasure."
     " [Ultimate Rare]", 0],
    ['Sacred', "Sacred Blood", 100, 9, '<:Sacred:1274786598336331807>',
     "Rare drop from raid bosses. Can be optionally consumed as an additional cost to guarantee a 'Sacred' "
     "outcome during infusion. It can also be used to upgrade tier 8 gear to tier 9."
     " [Ultimate Rare]", 0],
    ['Salvation', "Seal of Salvation", 100, 9, '<:Sacred:1274786598336331807>',
     "Rare drop from raid bosses. Can be consumed to guarantee an on-class skill roll on an Amulet."
     " [Ultimate Rare]", 0],
    ['Metamorphite', 'Metamorphite Ore', 100, 7, '<:O6:1388913354113945680>',
     "A mysterious ore that can drastically change an item.", 0]]
itemdata_dict = build_item_dict(itemdata_dict, uncategorized_data, unique_index=True)
