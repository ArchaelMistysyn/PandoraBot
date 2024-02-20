import globalitems

itemdata_dict = {}


def build_item_dict(input_dict, input_data, starting_index):
    id_prefix = input_data[0]
    for row_index, current_row in enumerate(input_data[1:], starting_index):
        if id_prefix is not None:
            temp_id = f"{id_prefix}{row_index}"
        else:
            temp_id = current_row[0]
        new_data = {
            'item_id': temp_id, "name": current_row[1], "rate": current_row[2], "tier": current_row[3],
            "emoji": current_row[4], "description": current_row[5], "cost": current_row[6], "image": current_row[7]
        }
        input_dict[temp_id] = new_data
    return input_dict


# Fae Data List
fae_fire = "<:e1:1179726491311947829>"
fae_water = "<:e2:1179726472995405854>"
fae_lightning = "<:e3:1179726450056761364>"
fae_earth = "<:e4:1179726402296221787>"
fae_wind = "<:e5:1179726383224733706>"
fae_ice = "<:e6:1179726426509946900>"
fae_dark = "<:e7:1179726335678107698>"
fae_light = "<:e8:1179726361049452554>"
fae_celestial = "<:e9:1179726302480183396>"
fae_emoji_list = [fae_fire, fae_water, fae_lightning, fae_earth, fae_wind, fae_ice, fae_dark, fae_light, fae_celestial]
fae_data = [
    [None, f'Fae Core ({element})', 100, 1, emoji,
        f'The core harvested from a {element.lower()} fae spirit. Brimming with elemental energies.', 500, ""
    ] for i, element, emoji in zip(range(9), globalitems.element_names, fae_emoji_list)
]
fae_data.insert(0, "Fae")
itemdata_dict = build_item_dict(itemdata_dict, fae_data, 0)

# Elemental Origin Data List
fire_origin_emoji = "<a:eorigin:1145520263954440313>"
water_origin_emoji = "<a:eorigin:1145520263954440313>"
lightning_origin_emoji = "<a:eorigin:1145520263954440313>"
earth_origin_emoji = "<a:eorigin:1145520263954440313>"
wind_origin_emoji = "<a:eorigin:1145520263954440313>"
ice_origin_emoji = "<a:eorigin:1145520263954440313>"
shadow_origin_emoji = "<a:eorigin:1145520263954440313>"
light_origin_emoji = "<a:eorigin:1145520263954440313>"
celestial_origin_emoji = "<a:eorigin:1145520263954440313>"
origin_emoji_list = [fire_origin_emoji, water_origin_emoji, lightning_origin_emoji,
                     earth_origin_emoji, wind_origin_emoji, ice_origin_emoji,
                     shadow_origin_emoji, light_origin_emoji, celestial_origin_emoji]
origin_data = [
    [None, f'Elemental Origin ({element})', 90, 5, emoji,
     f'90% chance to add the {element.lower()} element to a gear item.', 0, ""]
    for element, emoji in zip(globalitems.element_names, origin_emoji_list)
]
origin_data.insert(0, "Origin")
itemdata_dict = build_item_dict(itemdata_dict, origin_data, 0)

# Token List Data
token_data = [
    "Token",
    [None, 'Changeling Token', 100, 1, '<a:elootitem:1144477550379274322>',
     'An ancient token. Can be used to change your class or username.', 100000, ""],
    [None, 'Soulweaver Token', 100, 2, '<a:elootitem:1144477550379274322>',
     'An ancient token. Can be used for insignia engraving and upgrades.', 100000, ""],
    [None, 'Pathwalker Token', 100, 3, '<a:elootitem:1144477550379274322>',
     'An ancient token. Can be used to reset all skill points.', 100000, ""],
    [None, 'Lifeblood Token', 100, 4, '<a:elootitem:1144477550379274322>',
     'An ancient token. Can be used to reshape dragon heart gems.', 100000, ""],
    [None, 'Scribe Token', 100, 5, '<a:elootitem:1144477550379274322>',
     'An ancient token. Can be used to enscribe weapons.', 250000, ""],
    [None, 'Oracle Token', 100, 6, '<a:elootitem:1144477550379274322>',
     'An ancient token. Can be used to obtain lotus items.', 100000, ""],
    [None, 'Adjudicator Token', 100, 7, '<a:elootitem:1144477550379274322>',
     'An ancient token. ???.', 500000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, token_data, 1)

# Summoning List Data
summon_data = [
    "Summon",
    [None, 'Summoning Sigil', 100, 4, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 1-4 paragon solo boss.', 10000, ""],
    [None, 'Summoning Relic', 100, 5, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 4-5 paragon solo boss.', 50000, ""],
    [None, 'Summoning Artifact', 100, 6, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 6 paragon solo boss.', 100000, ""],
    [None, 'Summoning Crystal', 100, 7, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 1-6 arbiter solo boss.', 250000, ""],
    [None, 'Summoning Prism', 100, 8, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 7 arbiter solo boss.', 500000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, summon_data, 1)

# Stone List Data
stone_type = ["Fortress", "Dragon", "Demon", "Paragon", "Raid", "Arbiter"]
stone_data = [
    "Stone",
    [None, 'Fortress Stone', 100, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Dragon Stone', 100, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Demon Stone', 100, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Paragon Stone', 100, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Raid Stone', 100, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Arbiter Stone', 100, 6, '<a:elootitem:1144477550379274322>', None, 0, ""]
]
for index, row in enumerate(stone_data[1:]):
    row[5] = f'Obtained from {stone_type[index].lower()}. It\'s a stone.'
itemdata_dict = build_item_dict(itemdata_dict, stone_data, 1)

# Stamina Potion Data
potion_values = [500, 1000, 2500, 5000]
stamina_data = [
    "Potion",
    [None, 'Lesser Stamina Potion', 100, 1, '<:estamina:1145534039684562994>', None, 2500, ""],
    [None, 'Standard Stamina Potion', 100, 2, '<:estamina:1145534039684562994>', None, 5000, ""],
    [None, 'Greater Stamina Potion', 100, 3, '<:estamina:1145534039684562994>', None, 10000, ""],
    [None, 'Ultimate Stamina Potion', 100, 4, '<:estamina:1145534039684562994>', None, 20000, ""]
]
for index, row in enumerate(stamina_data[1:]):
    row[5] = f'Consume to restore {potion_values[index]} stamina.'
itemdata_dict = build_item_dict(itemdata_dict, stamina_data, 1)

# Trove Data
trove_rewards = {
        1: [1000, 10000], 2: [10000, 25000], 3: [25000, 50000], 4: [50000, 100000],
        5: [100000, 250000], 6: [250000, 500000], 7: [500000, 750000], 8: [750000, 1000000]
    }
trove_data = [
    "Trove",
    [None, 'Lesser Golden Trove', 100, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Standard Golden Trove', 100, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Greater Golden Trove', 100, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Ultimate Golden Trove', 100, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Voidworn Golden Trove', 100, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Miraculous Golden Trove', 100, 6, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Abyssal Golden Trove', 100, 7, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Divine Golden Trove', 100, 8, '<a:elootitem:1144477550379274322>', None, 0, ""]
]
for row in trove_data[1:]:
    tier = row[3]
    bounds = trove_rewards[tier]
    row[5] = f'Open to receive {bounds[0]:,} - {bounds[1]:,} lotus coins.'
itemdata_dict = build_item_dict(itemdata_dict, trove_data, 1)

# Ore and Soul List Data in the new structure
ore_data = [
    "Ore",
    [None, 'Crude Ore', 2, 1, '<:eore:1145534835507593236>', None, 1500, ""],
    [None, 'Cosmite Ore', 5, 2, '<:eore:1145534835507593236>', None, 5000, ""],
    [None, 'Celestite Ore', 10, 3, '<:eore:1145534835507593236>', None, 10000, ""],
    [None, 'Crystallite Ore', 50, 4, '<:eore:1145534835507593236>', None, 40000, ""],
    [None, 'Heavenly Ore', 100, 5, '<:eore:1145534835507593236>', None, 75000, ""],
    [None, 'Abyss Ore', 100, 6, '<:eore:1145534835507593236>', None, 0, ""]
]
for row in ore_data[1:]:
    row[5] = f'Ore with {row[2]}% purity. Used for reinforcing gear items. Increasing the quality.'
itemdata_dict = build_item_dict(itemdata_dict, ore_data, 1)

# Hammer List Data
hammer_data = [
    "Hammer",
    [None, 'Astral Hammer', 33, 2, '<:ehammer:1145520259248427069>',
     'Used to reroll specific item rolls. Works on tier 4 and lower gear items.', 0, ""],
    [None, 'Void Hammer', 50, 5, '<:ehammer:1145520259248427069>',
     'Used to add or reroll item rolls. Works on tier 6 and abov gear items.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, hammer_data, 1)

# Matrix List Data
matrix_data = [
    "Matrix",
    [None, 'Socket Matrix', 5, 3, '<a:elootitem:1144477550379274322>',
     '5% Chance to add a socket to a gear item.', 5000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, matrix_data, 1)

# Pearl List Data
pearl_data = [
    "Pearl",
    [None, 'Stellar Pearl', 75, 4, '<:eprl:1148390531345432647>',
     'Augments an item roll. Increases the tier by 1.', 50000, ""],
    [None, 'Void Pearl', 95, 6, '<:eprl:1148390531345432647>',
     'Augments an item roll of a tier 5 or higher item. Increases the tier by 1.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, pearl_data, 1)

# Flame Items
flame_data = [
    "Flame",
    [None, 'Purgatorial Flame', 50, 3, '<a:eshadow2:1141653468965257216>',
     '75% chance to reforge the base stats and unique ability of a gear item within its tier.', 5000, ""],
    [None, 'Void Flame', 75, 7, '<a:evoid:1145520260573827134>',
     '50% chance to reroll a unique ability that has been void locked.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, flame_data, 1)

# Core/Traces List Data
core_data = [
    "Core",
    [None, 'Void Core', 50, 5, '<a:evoid:1145520260573827134>',
     'A core used for void infusion and purification.', 0, ""],
    [None, 'Wish Core', 90, 6, '<a:elootitem:1144477550379274322>',
     'A core used for wish infusion and purification.', 0, ""],
    [None, 'Abyss Core', 90, 7, '<a:elootitem:1144477550379274322>',
     'A core used for abyss infusion and purification.', 0, ""],
    [None, 'Divine Core', 90, 8, '<a:elootitem:1144477550379274322>',
     'A core used for divine infusion and purification.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, core_data, 1)


# Unrefined Void Items List Data
unrefined_item_types = ['Weapon', 'Armour', 'Amulet', 'Wing', 'Crest', 'Gem']
unrefined_fabled_data = [
    "Void",
    [None, "Unrefined Void Item (Weapon)", 75, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, "Unrefined Void Item (Armour)", 75, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, "Unrefined Void Item (Vambraces)", 75, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, "Unrefined Void Item (Amulet)", 75, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, "Unrefined Void Item (Wing)", 75, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, "Unrefined Void Item (Crest)", 75, 5, '<a:elootitem:1144477550379274322>', None, 0, ""]
]
for index, row in enumerate(unrefined_fabled_data[1:]):
    row[5] = f'Refine for 50% chance to receive a tier 5 {unrefined_item_types[index].lower()}.'
itemdata_dict = build_item_dict(itemdata_dict, unrefined_fabled_data, 1)

# Unrefined Misc Items List Data
unrefined_misc_data = [
    "Unrefined",
    [None, 'Unrefined Dragon Wings', 75, 4, '<a:elootitem:1144477550379274322>',
     'Refine for 75% chance to receive tier 2-4 dragon wings.', 10000, ""],
    [None, 'Unrefined Demon Vambraces', 75, 4, '<a:elootitem:1144477550379274322>',
     'Refine for 75% chance to receive a tier 2-4 demon vambraces.', 10000, ""],
    [None, 'Unrefined Paragon Crest', 75, 4, '<a:elootitem:1144477550379274322>',
     'Refine for 75% chance to receive a tier 2-4 paragon crest.', 10000, ""]
]

# Unrefined Gems List Data
unrefined_gem_data = [
    "Gem",
    [None, 'Unrefined Dragon Gem', 75, 3, '<a:elootitem:1144477550379274322>',
     'Refine for 75% chance to receive tier 2-4 dragon gem.', 10000, ""],
    [None, 'Unrefined Demon Gem', 75, 4, '<a:elootitem:1144477550379274322>',
     'Refine for 75% chance to receive a tier 2-4 demon gem.', 15000, ""],
    [None, 'Unrefined Paragon Gem', 75, 5, '<a:elootitem:1144477550379274322>',
     'Refine for 75% chance to receive a tier 2-4 paragon gem.', 25000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, unrefined_gem_data, 1)

# Unrefined Jewel List Data
unrefined_jewel_data = [
    "Jewel",
    [None, 'Unrefined Dragon Jewel', 75, 5, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive tier 5-8 dragon jewel.', 100000, ""],
    [None, 'Unrefined Demon Jewel', 75, 5, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive a tier 5-8 demon jewel.', 150000, ""],
    [None, 'Unrefined Paragon Jewel', 75, 6, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive a tier 5-8 paragon jewel.', 250000, ""],
    [None, 'Unrefined Arbiter Jewel', 75, 7, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive a tier 6-8 arbiter jewel.', 500000, ""],
    [None, 'Unrefined Incarnate Jewel', 75, 8, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive a tier 7-8 incarnate jewel.', 1000000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, unrefined_jewel_data, 1)

# Essence List Data
essence_data = [
    None,
    ['Essence0', 'Essence of The Reflection', 10, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceI', 'Essence of The Magic', 10, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceII', 'Essence of The Celestial', 10, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceIII', 'Essence Of The Void', 10, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceIV', 'Essence Of The Infinite', 10, 6, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceV', 'Essence of The Duality', 10, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceVI', 'Essence of The Love', 10, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceVII', 'Essence of The Dragon', 10, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceVIII', 'Essence of The Behemoth', 10, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceIX', 'Essence of The Memory', 10, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceX', 'Essence of The Temporal', 10, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXI', 'Essence of The Heavens', 10, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXII', 'Essence of The Abyss', 10, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXIII', 'Essence of The Death', 10, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXIV', 'Essence of The Clarity', 10, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXV', 'Essence of The Primordial', 10, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXVI', 'Essence of The Fortress', 10, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXVII', 'Essence of The Star', 10, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXVIII', 'Essence of The Moon', 10, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXIX', 'Essence of The Sun', 10, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXX', 'Essence of The Requiem', 10, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXI', 'Essence of The Creation', 10, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXII', 'Essence of The Changeling', 10, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXIII', 'Essence of The Pathwalker', 10, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXIV', 'Essence of The Soulweaver', 10, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXV', 'Essence of The Wish', 10, 6, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXVI', 'Essence of The Lifeblood', 10, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXVII', 'Essence of The Scribe', 10, 5, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXVIII', 'Essence of The Oracle', 10, 6, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['XXIX', 'Essence of The Adjudicator', 10, 7, '<a:elootitem:1144477550379274322>', None, 0, ""],
    ['EssenceXXX', 'Essence of The Lotus', 10, 8, '<a:elootitem:1144477550379274322>', None, 0, ""],

]
for index, row in enumerate(essence_data[1:]):
    row[5] = f'Perform a binding ritual to attempt to seal this essence into card form.'
itemdata_dict = build_item_dict(itemdata_dict, essence_data, 1)

# Crystallized List Data
crystallized_data = [
    "Crystal",
    [None, 'Crystallized Void', 100, 5, '<a:elootitem:1144477550379274322>',
     'Used to craft tier 5 weapons.', 500000, ""],
    [None, 'Crystallized Wish', 100, 6, '<a:evoid:1145520260573827134>',
     'UUsed to upgrade weapons to tier 6.', 1000000, ""],
    [None, 'Crystallized Abyss', 100, 7, '<a:elootitem:1144477550379274322>',
     'Used to upgrade weapons to tier 7.', 10000000, ""],
    [None, 'Crystallized Void', 100, 8, '<a:evoid:1145520260573827134>',
     'Used to upgrade weapons to tier 8.', 100000000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, crystallized_data, 1)

# Lotus List Data
lotus_data = [
    "Lotus",
    [None, 'Lotus of Prosperity', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Purification (Amulet). Increases the tier to 8. ', 99999999, ""],
    [None, 'Lotus of Serenity', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Purification (Vambraces).  Increases the tier to 8.', 0, ""],
    [None, 'Lotus of Freedom', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Purification (Wings). Increases the tier to 8. ', 0, ""],
    [None, 'Lotus of Eternity', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Melding (Jewels). Increases the tier to 8.', 0, ""],
    [None, 'Lotus of Abundance', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Purification (Armour). Increases the tier to 8.', 0, ""],
    [None, 'Lotus of Domincation', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Purification (Crest).  Increases the tier to 8.', 0, ""],
    [None, 'Lotus of Divergence', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Mutation (Insignia).  Increases the tier to 8.', 0, ""],
    [None, 'Lotus of Revelations', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Synthesis (Tarot).  Increases the tier to 8.', 0, ""],
    [None, 'Lotus of Nightmares', 100, 7, '<a:eorigin:1145520263954440313>',
     'Used for Divine Synthesis (Weapon).  Increases the tier to 8.', 0, ""],
    [None, 'Divine Lotus', 100, 8, '<a:eorigin:1145520263954440313>',
     '???', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, lotus_data, 1)

# Fragment Item Data
fragment_data = [
    "Fragment",
    [None, 'Fragmentized Void', 100, 5, '<a:elootitem:1144477550379274322>',
     'Used for void infusion and crafting.', 0, ""],
    [None, 'Fragmentized Wish', 100, 6, '<a:elootitem:1144477550379274322>',
     'Used for wish infusion and crafting.', 0, ""],
    [None, 'Fragmentized Abyss', 100, 7, '<a:elootitem:1144477550379274322>',
     'Used for abyss infusion and crafting.', 0, ""],
    [None, 'Fragmentized Divinity', 100, 8, '<a:elootitem:1144477550379274322>',
     'Used for divine infusion and crafting.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, fragment_data, 1)

# Heart Item Data
heart_data = [
    "Heart",
    [None, 'Radiant Heart', 100, 6, '<a:elootitem:1144477550379274322>', 'Used for various infusions.', 100000, ""],
    [None, 'Chaos Heart', 100, 7, '<a:elootitem:1144477550379274322>', 'Used for various infusions.', 100000, ""]]
itemdata_dict = build_item_dict(itemdata_dict, heart_data, 1)

# Uncategorized Item Data
uncategorized_data = [
    None,
    ['OriginZ', 'Origin Catalyst', 100, 4, '<a:eorigin:1145520263954440313>',
     'Used for elemental infusion.', 100000, ""],
    ['Crate', 'Crate', 100, 1, '<a:elootitem:1144477550379274322>',
     'Contains a random item.', 10000, ""],
    ['Scrap', 'Equipment Scrap', 100, 1, '<a:elootitem:1144477550379274322>',
     'A scrap from some broken equipment.', 5000, ""],
    ['Compass', 'Illusory Compass', 100, 6, '<a:elootitem:1144477550379274322>',
     'An enigmatic compass said to be capable of locating the Spire of Illusions.', 500000, ""],
    ['DarkStar', 'Dark Star of Shattered Dreams', 100, 1, '<a:elootitem:1144477550379274322>',
     "Legend tells of a star engulfed in black flames that heralds great disasters. "
     "The old records describe visions of the dark star blocking out the sun leaving chaos in it's wake.", 0, ""],
    ['LightStar', 'Glittering Star of Fractured Hearts', 100, 1, '<a:elootitem:1144477550379274322>',
     "Legend tells of a star often spotted by lovers as it dazzles and sparkles amidst the black night. "
     "The old records indicate that the star was so beautiful it would steal the hearts of those who saw it.", 0, ""],
    ['TwinRings', 'Twin Rings of Divergent Stars', 100, 1, '<a:elootitem:1144477550379274322>',
     "A pair of rings with unique gemstones that twinkle like stars in the night sky and "
     "shine brightly like the brilliant sun.", 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, uncategorized_data, 1)

