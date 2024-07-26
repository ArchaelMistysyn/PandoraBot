import globalitems as gli

ring_icons = {0: None, 1: None, 2: None, 3: None,
              "Elemental Signet Infusion":
                  ["<:Signet0:1253839691736678440>", "<:Signet1:1253839692865077319>", "<:Signet2:1253839693477318718>",
                   "<:Signet3:1253839694488408144>", "<:Signet4:1253839730177736736>", "<:Signet5:1253839731133911118>",
                   "<:Signet6:1253839732434141275>", "<:Signet7:1253839733210218527>", "<:Signet8:1253839734073987072>"],
              "Primordial Ring Infusion":
                  ["<:E_Ring0:1253839617799487568>", "<:E_Ring1:1253839618315522119>", "<:E_Ring2:1253839619804369028>",
                   "<:E_Ring3:1253839620710596669>", "<:E_Ring4:1253839646098587690>", "<:E_Ring5:1253839646824333364>",
                   "<:E_Ring6:1253839647637770332>", "<:E_Ring7:1253839648535347230>", "<:E_Ring8:1253839649835716680>"],
              6: [],
              7: [],
              8: [],
              "Sovereign Ring Infusion": ["<:sc_ring:1266169348465365072>", "<:hc_ring:1266169384024670381>",
                                          "<:hadal_ring:1266169382971641867>", "<:twin_rings:1266169349366874204>",
                                          "<:skull_ring:1266169381663015146>"]}

ring_values_dict = {
    # Legendary Rings
    "Dragon's Eye Diamond": [[("Critical Rate Becomes X%", "perfect_rate", 100, ["Critical"]),
                              ("Critical Damage X%", "critical_mult", 500, None),
                              ("[RESONANCE]", "resonance", 100, 4)], (0, None), [0]],
    "Chromatic Tears": [[("Omni Curse X%", "all_elemental_curse", 500, None),
                         ("[RESONANCE]", "resonance", 100, 25)], (0, None), ["all"]],
    "Bleeding Hearts": [[("Bleed Application +X", "appli", 5, None),
                         ("[RESONANCE]", "resonance", 100, 5)], (0, None), [3, 4]],
    "Gambler's Masterpiece": [[("All-In!", "rng_bonus", 777, None),
                               ("[RESONANCE]", "resonance", 100, 0)], (0, None), ["all"]],
    # Sovereign Rings
    "Stygian Calamity": [[("X% chance for Non-Bloom hits to trigger Calamity", "spec_conv", 99, "Calamity"),
                          ("X% Hybrid Curse (Chaos)", "elemental_curse", 999, (0, 2, 3, 6))], (0, None), [0, 2, 3, 6]],
    "Heavenly Calamity": [[("X% chance for Non-Bloom hits to trigger Calamity", "spec_conv", 99, "Calamity"),
                           ("X% Hybrid Curse (Holy)", "elemental_curse", 999, (1, 4, 5, 7))], (0, None), [1, 4, 5, 7]],
    "Hadal's Raindrop": [[("Aqua Cascade", "aqua_mode", 100, None), ("Aqua Conversion", None, 0, None),
                          ("Aqua Manifestation", None, 0, None)], (0, None), [1]],
    "Twin Rings of Divergent Stars":
        [[("X% chance for Bloom hits to trigger Heavenly Bloom", "spec_conv", 50, "Heavenly"),
          ("X% chance for Non-Bloom hits to trigger Stygian Bloom", "spec_conv", 50, "Stygian"),
          ("Omni Curse X%", "all_elemental_curse", 300, None)], (0, None), [6, 7, 8]],
    "Crown of Skulls": [["Avaricious Ruin", "Banquet of Bones"], (0, None), [5]]}

# Elemental Signets
for i, element in enumerate(gli.element_names):
    ring_data = [[(f"{element} Curse X%", "elemental_curse", 200, i)], (0, None), [i]]
    ring_values_dict[f"Elemental Signet of {element}"] = ring_data
# Primordial Rings
ele_rings = [("Ruby", "Incineration", 1), ("Sapphire", "Atlantis", 14), ("Topaz", "Dancing Thunder", 8),
             ("Agate", "Seismic Tremors", 16), ("Emerald", "Wailing Winds", 9), ("Zircon", "Frozen Castle", 13),
             ("Obsidian", "Tormented Souls", 12), ("Opal", "Scintillation", 11), ("Amethyst", "Shifting Stars", 17)]
for elemental_index, (ring_prefix, ring_suffix, resonance_index) in enumerate(ele_rings):
    abilities = [(f"{gli.element_names[elemental_index]} Curse X%", "elemental_curse", 500, elemental_index),
                 ("[RESONANCE]", "resonance", 100, resonance_index)]
    ring_data = [abilities, (0, None), [elemental_index]]
    ring_values_dict[f"{ring_prefix} Ring of {ring_suffix}"] = ring_data
# Path Rings
path_rings = [("Invoking", "Storms", 20), ("Primordial", "Frostfire", 15), ("Boundary", "Horizon", 11),
              ("Hidden", "Eclipse", 12), ("Cosmic", "Stars", 2), ("Orbital", "Solar Flux", 19),
              ("Orbital", "Lunar Tides", 18), ("Orbital", "Terrestria", 21), ("Rainbow", "Confluence", 6)]
for path_index, (ring_prefix, ring_suffix, resonance_index) in enumerate(path_rings):
    element_indices, abilities = gli.element_dict[ring_suffix.split()[0]], []
    if ring_suffix == "Terrestria":
        abilities.append((f"Singularity Curse X%", "singularity_curse", 750, None))
    elif ring_suffix == "Confluence":
        abilities.append((f"Omni Curse X%", "all_elemental_curse", 200, None))
        element_indices = ["all"]
    else:
        for idx in element_indices:
            abilities.append((f"{gli.element_names[idx]} Curse X%", "elemental_curse", 250, idx))
    abilities.append(("[RESONANCE]", "resonance", 100, resonance_index))
    ring_values_dict[f"{ring_prefix} Ring of {ring_suffix}"] = [abilities, (10, path_index), element_indices]

ring_resonance_dict, ring_element_dict = {}, {}
for ring_name, attributes in ring_values_dict.items():
    for attribute_set in attributes[0]:
        resonance_index = attribute_set[3] if "[RESONANCE]" in attribute_set else 0
    ring_resonance_dict[ring_name] = resonance_index
    ring_element_dict[ring_name] = attributes[2]
