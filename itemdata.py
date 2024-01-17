itemdata_dict = {}
element_names = ["Fire", "Water", "Lightning", "Earth", "Wind", "Ice", "Shadow", "Light", "Celestial"]


def build_item_dict(input_dict, input_data, starting_index):
    id_prefix = input_data[0]
    for row_index, current_row in enumerate(input_data[1:], starting_index):
        if id_prefix is not None:
            temp_id = f"{id_prefix}{row_index}"
        else:
            temp_id = current_row[0]
        new_data = {
            'item_id': temp_id,
            "name": current_row[1],
            "rate": current_row[2],
            "tier": current_row[3],
            "emoji": current_row[4],
            "description": current_row[5],
            "cost": current_row[6],
            "image": current_row[7]
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
    ] for i, element, emoji in zip(range(9), element_names, fae_emoji_list)
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
    for element, emoji in zip(element_names, origin_emoji_list)
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
    [None, 'Placeholder Token', 100, 4, '<a:elootitem:1144477550379274322>',
     'An ancient token. ???.', 100000, ""],
    [None, 'Placeholder Token', 100, 5, '<a:elootitem:1144477550379274322>',
     'An ancient token. ???.', 100000, ""],
    [None, 'Scribe Token', 100, 6, '<a:elootitem:1144477550379274322>',
     'An ancient token. To one who knows its true purpose the value of this item is immeasurable.', 250000, ""],
    [None, '??? Token', 100, 7, '<a:elootitem:1144477550379274322>',
     'An ancient token. ???.', 500000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, token_data, 1)

# Summoning List Data
summon_data = [
    "Summon",
    [None, 'Summoning Token', 100, 4, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 1-4 paragon solo boss.', 10000, ""],
    [None, 'Summoning Relic', 100, 5, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 4-5 paragon solo boss.', 25000, ""],
    [None, 'Summoning Artifact', 100, 6, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon a tier 6 paragon solo boss.', 100000, ""],
    [None, 'Summoning Crystal', 100, 7, '<a:elootitem:1144477550379274322>',
     'Perform a summoning ritual to summon ???.', 1000000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, summon_data, 1)

# Stone List Data
stone_type = ["Fortress", "Dragon", "Demon", "Paragon", "Raid"]
stone_data = [
    "Stone",
    [None, 'Fortress Stone', 100, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Dragon Stone', 100, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Demon Stone', 100, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Paragon Stone', 100, 4, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Raid Stone', 100, 5, '<a:elootitem:1144477550379274322>', None, 0, ""]
]
for index, row in enumerate(stone_data[1:]):
    row[5] = f'Obtained from {stone_type[index].lower()}. It\'s a stone.'
itemdata_dict = build_item_dict(itemdata_dict, stone_data, 1)

# Stamina Potion Data
potion_values = [500, 1000, 2500, 5000]
stamina_data = [
    "Potion",
    [None, 'Lesser Stamina Potion', None, None, '<:estamina:1145534039684562994>', None, 2500, ""],
    [None, 'Standard Stamina Potion', None, None, '<:estamina:1145534039684562994>', None, 5000, ""],
    [None, 'Greater Stamina Potion', None, None, '<:estamina:1145534039684562994>', None, 10000, ""],
    [None, 'Ultimate Stamina Potion', None, None, '<:estamina:1145534039684562994>', None, 20000, ""]
]
for index, row in enumerate(stamina_data[1:]):
    row[5] = f'Consume to restore {potion_values[index]} stamina.'
itemdata_dict = build_item_dict(itemdata_dict, stamina_data, 1)

# Trove Data
trove_values = [(1000, 10000), (10000, 25000), (25000, 50000), (50000, 250000)]
trove_data = [
    "Trove",
    [None, 'Lesser Golden Trove', None, 1, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Standard Golden Trove', None, 2, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Greater Golden Trove', None, 3, '<a:elootitem:1144477550379274322>', None, 0, ""],
    [None, 'Ultimate Golden Trove', None, 4, '<a:elootitem:1144477550379274322>', None, 0, ""]
]
for index, (min_value, max_value) in enumerate(trove_values):
    row = trove_data[index + 1]
    row[5] = f'Open to receive {min_value:,} - {max_value:,} lotus coins.'
itemdata_dict = build_item_dict(itemdata_dict, trove_data, 1)

# Ore and Soul List Data in the new structure
ore_data = [
    "Ore",
    [None, 'Crude Ore', 2, 1, '<:eore:1145534835507593236>', None, 1500, ""],
    [None, 'Cosmite Ore', 5, 2, '<:eore:1145534835507593236>', None, 5000, ""],
    [None, 'Celestite Ore', 10, 3, '<:eore:1145534835507593236>', None, 10000, ""],
    [None, 'Crystallite Ore', 50, 4, '<:eore:1145534835507593236>', None, 40000, ""],
    [None, 'Heavenly Ore', 100, 5, '<:eore:1145534835507593236>', None, 75000, ""],
    [None, 'Miracle Ore', 100, 6, '<:eore:1145534835507593236>', None, 0, ""]
]

soul_data = [
    "Soul",
    [None, 'Light Soul', 2, 1, '<:esoul:1145520258241806466>', None, 1500, ""],
    [None, 'Luminous Soul', 5, 2, '<:esoul:1145520258241806466>', None, 5000, ""],
    [None, 'Lucent Soul', 10, 3, '<:esoul:1145520258241806466>', None, 10000, ""],
    [None, 'Lustrous Soul', 50, 4, '<:esoul:1145520258241806466>', None, 40000, ""],
    [None, 'Heavenly Soul', 100, 5, '<:esoul:1145520258241806466>', None, 75000, ""],
    [None, 'Miracle Soul', 100, 6, '<:esoul:1145520258241806466>', None, 0, ""]
]

for row_ore, row_soul in zip(ore_data[1:], soul_data[1:]):
    row_ore[5] = f'Ore with {row_ore[2]}% purity. Used for reinforcing gear items.'
    row_soul[5] = f'Soul with {row_soul[2]}% purity. Used for enchanting gear items.'
itemdata_dict = build_item_dict(itemdata_dict, ore_data, 1)
itemdata_dict = build_item_dict(itemdata_dict, soul_data, 1)

# Hammer List Data
hammer_data = [
    "Hammer",
    [None, 'Star Hammer', 50, 3, '<:ehammer:1145520259248427069>',
     'Adds an item roll or rerolls one if at capacity. Works on tier 5 and lower gear items.', 25000, ""],
    [None, 'Astral Hammer', 33, 4, '<:ehammer:1145520259248427069>',
     'Used to reroll specific item rolls. Works on tier 4 and lower gear items.', 0, ""],
    [None, 'Fabled Hammer', 50, 5, '<:ehammer:1145520259248427069>',
     'Used to reroll specific item rolls. Works on tier 5 and lower gear items.', 0, ""],
    [None, 'Miracle Hammer', 50, 6, '<:ehammer:1145520259248427069>',
     'Used to add or reroll item rolls. Works on tier 6 and abov gear items.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, hammer_data, 1)

# Matrix List Data
matrix_data = [
    "Matrix",
    [None, 'Socket Matrix', 5, 3, '<a:elootitem:1144477550379274322>',
     '5% Chance to add a socket to a gear item.', 5000, ""],
    [None, 'Fabled Matrix', 100, 5, '<a:elootitem:1144477550379274322>',
     'Used to add a socket to a tier 5 gear item.', 100000, ""],
    [None, 'Miracle Matrix', 100, 6, '<a:elootitem:1144477550379274322>',
     'Used to add a socket to a tier 6+ gear item.', 250000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, matrix_data, 1)

# Pearl List Data
pearl_data = [
    "Pearl",
    [None, 'Stellar Pearl', 75, 4, '<:eprl:1148390531345432647>',
     'Augments an item roll. Increases the tier by 1.', 50000, ""],
    [None, 'Fabled Pearl', 75, 5, '<:eprl:1148390531345432647>',
     'Augments an item roll of a tier 5 gear item. Increases the tier by 1.', 0, ""],
    [None, 'Void Pearl', 85, 6, '<a:evoid:1145520260573827134>',
     'Augments an item roll of a void gear item. Increases the tier from 4 to 5.', 0, ""],
    [None, 'Miracle Pearl', 95, 6, '<:eprl:1148390531345432647>',
     'Augments an item roll of a tier 6 gear item. Increases the tier by 1.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, pearl_data, 1)

# Flame Items
flame_data = [
    "Flame",
    [None, 'Purgatorial Flame', 50, 3, '<a:eshadow2:1141653468965257216>',
     '50% chance to reforge the base stats and unique ability of a gear item within its tier.', 5000, ""],
    [None, 'Fabled Flame', 80, 5, '<a:eshadow2:1141653468965257216>',
     '80% chance to reforge the base stats and unique ability of a tier 5 gear item.', 0, ""],
    [None, 'Void Flame', 75, 6, '<a:evoid:1145520260573827134>',
     '75% chance to reroll a unique ability that has been void locked.', 0, ""],
    [None, 'Miracle Flame', 100, 6, '<a:eshadow2:1141653468965257216>',
     'Used to reforge the base stats and unique ability of a tier 6 item. Cannot reroll void abilities.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, flame_data, 1)

# Core/Traces List Data
core_data = [
    "Core",
    [None, 'Fabled Core', 100, 5, '<a:elootitem:1144477550379274322>', 'A core used for fabled infusion.', 250000, ""],
    [None, 'Void Core', 50, 5, '<a:evoid:1145520260573827134>',
     'A core used for to convert a tier 5 item into a void item.', 0, ""],
    [None, 'Wish Core', 90, 6, '<a:elootitem:1144477550379274322>', 'A core used for void purification.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, core_data, 1)

# Heart List Data
heart_data = [
    "Heart",
    [None, 'Astral Heart', 100, 5, '<a:elootitem:1144477550379274322>', 'Used in various infusions.', 100000, ""],
    [None, 'Miracle Heart', 100, 6, '<a:elootitem:1144477550379274322>', 'Used in miracle infusion.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, heart_data, 1)


# Fabled Fragments List Data
fragment_type = ['Weapon', 'Armour', 'Accessory']
fabled_fragment_data = [
    "Fragment",
    [None, "Fabled Weapon Fragment", 100, 5, '<a:elootitem:1144477550379274322>', None, 5000, ""],
    [None, "Fabled Armour Fragment", 100, 5, '<a:elootitem:1144477550379274322>', None, 5000, ""],
    [None, "Fabled Accessory Fragment", 100, 5, '<a:elootitem:1144477550379274322>', None, 5000, ""]
]
for index, row in enumerate(fabled_fragment_data[1:]):
    row[5] = f'Used for infusing fabled {fragment_type[index].lower()}s.'
itemdata_dict = build_item_dict(itemdata_dict, fabled_fragment_data, 1)


# Unrefined Fabled Items List Data
unrefined_item_types = ['Weapon', 'Armour', 'Accessory', 'Wing', 'Crest', 'Gem']
unrefined_fabled_data = [
    "Fabled",
    [None, "Unrefined Fabled Item (Weapon)", 50, 5, '<a:elootitem:1144477550379274322>', None, 500000, ""],
    [None, "Unrefined Fabled Item (Armour)", 50, 5, '<a:elootitem:1144477550379274322>', None, 500000, ""],
    [None, "Unrefined Fabled Item (Accessory)", 50, 5, '<a:elootitem:1144477550379274322>', None, 500000, ""],
    [None, "Unrefined Fabled Item (Wing)", 50, 5, '<a:elootitem:1144477550379274322>', None, 500000, ""],
    [None, "Unrefined Fabled Item (Crest)", 50, 5, '<a:elootitem:1144477550379274322>', None, 500000, ""],
    [None, "Unrefined Fabled Item (Gem)", 50, 5, '<a:elootitem:1144477550379274322>', None, 500000, ""]
]
for index, row in enumerate(unrefined_fabled_data[1:]):
    row[5] = f'Refine for 50% chance to receive a tier 5 {unrefined_item_types[index].lower()}s.'
itemdata_dict = build_item_dict(itemdata_dict, unrefined_fabled_data, 1)

# Unrefined Misc Items List Data
unrefined_misc_data = [
    "Unrefined",
    [None, 'Unrefined Dragon Wings', 50, 4, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive tier 2-4 dragon wings.', 10000, ""],
    [None, 'Unrefined Dragon Jewel', 50, 4, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive a tier 2-4 dragon jewel.', 10000, ""],
    [None, 'Unrefined Paragon Crest', 50, 4, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive a tier 2-4 paragon crest.', 10000, ""],
    [None, 'Unrefined Dragon Heart Gem', 50, 6, '<a:elootitem:1144477550379274322>',
     'Refine for 50% chance to receive a tier 6 dragon heart gem.', 1500000, ""],
    [None, 'Unrefined Wish Item (Weapon)', 100, 6, '<a:elootitem:1144477550379274322>',
     'Refine to acquire a tier 6 weapon.', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, unrefined_misc_data, 1)

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
    ['EssenceXXX', 'Essence of The Wish', 10, 6, '<a:elootitem:1144477550379274322>', None, 0, ""]
]
for index, row in enumerate(essence_data[1:]):
    row[5] = f'Perform a binding ritual to attempt to seal this essence into card form.'
itemdata_dict = build_item_dict(itemdata_dict, essence_data, 1)

# Crystallized List Data
crystallized_data = [
    "Crystal",
    [None, 'Crystallized Wish', 100, 6, '<a:elootitem:1144477550379274322>',
     'Used for miracle infusion.', 0, ""],
    [None, 'Crystallized Void', 100, 7, '<a:evoid:1145520260573827134>',
     'Used to transcend tier 6 gear items.', 99999999, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, crystallized_data, 1)

# Lotus List Data
lotus_data = [
    "Lotus",
    [None, 'Lotus of Prosperity', 100, 7, '<a:eorigin:1145520263954440313>',
     '???', 99999999, ""],
    [None, 'Lotus of Miracles', 100, 7, '<a:eorigin:1145520263954440313>',
     '???', 0, ""],
    [None, 'Lotus of Revelations', 100, 7, '<a:eorigin:1145520263954440313>',
     '???', 0, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, lotus_data, 1)

# Uncategorized Item Data
uncategorized_data = [
    None,
    ['OriginZ', 'Origin Catalyst', 100, 4, '<a:eorigin:1145520263954440313>',
     'Used for elemental infusion.', 100000, ""],
    ['OriginV', 'Void Origin', 100, 6, '<a:eorigin:1145520263954440313>',
     'Void corrupts a fully augmented void gear item.', 0, ""],
    ['OriginM', 'Miracle Origin', 100, 6, '<a:eorigin:1145520263954440313>',
     'Used to add an element to a tier 6 gear item.', 0, ""],
    ['FragmentM', 'Fragmentized Wish', 100, 6, '<a:elootitem:1144477550379274322>',
     'Used to enhance a tier 6 gear item.', 0, ""],
    ['Crate', 'Crate', 100, 1, '<a:elootitem:1144477550379274322>',
     'Contains a random item.', 10000, ""],
    ['Trace1', 'Void Traces', 10, 5, '<a:evoid:1145520260573827134>', 'Used for void infusion.', 50000, ""]
]
itemdata_dict = build_item_dict(itemdata_dict, uncategorized_data, 1)

