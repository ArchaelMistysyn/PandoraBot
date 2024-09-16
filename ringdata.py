import globalitems as gli

ring_icons = {0: None, 1: None, 2: None, 3: None,
              "Elemental Signet Infusion": [
                  "<:Signet0:1275564530088415242>",
                  "<:Signet1:1275564538451726347>",
                  "<:Signet2:1275564547058438228>",
                  "<:Signet3:127556455937358881>",
                  "<:Signet4:1275564560941715486>",
                  "<:Signet5:127556457736352809>",
                  "<:Signet6:1275564574787113063>",
                  "<:Signet7:1275564582018224223>",
                  "<:Signet8:1275564589366444849>"
              ],
              "Primordial Ring Infusion": [
                  "<:E_Ring0:1275563705911906190>",
                  "<:E_Ring1:12755637321183303366>",
                  "<:E_Ring2:1275563735607672904>",
                  "<:E_Ring3:1275563746769876413>",
                  "<:E_Ring4:12755637553501034905>",
                  "<:E_Ring5:1275563762593828914>",
                  "<:E_Ring6:1275563771531987079>",
                  "<:E_Ring7:1275563777169587263>",
                  "<:E_Ring8:1275563788867250861>"
              ],
              6: [],
              7: ["<:lone_ring1:1275566085101326569>", "<:lone_ring2:1275566092504404038>"],
              "Sovereign Ring Infusion": ["<:sc_ring:1275566074779275426>", "<:hc_ring:1275566068466847776>",
                                          "<:hadal_ring:1275566060447207558>", "<:twin_rings:1275566143238836295>",
                                          "<:skull_ring:1275566027429773352>", "<:skull_ring:1275566027429773352>"]}

ring_values_dict = {
    # Fabled Rings
    "Dragon's Eye Diamond": [[("Critical Eye", "perfect_rate", 100, ["Critical"]),
                              ("Critical Damage X%", "critical_mult", 500, None),
                              ("[RESONANCE]", "resonance", 100, 4)], (0, None), [0]],
    "Bleeding Hearts": [[("Bleed Application +X", "appli", 5, None),
                         ("[RESONANCE]", "resonance", 100, 5)], (0, None), [3, 4]],
    "Gambler's Masterpiece": [[("All-In!", "rng_bonus", 777, None),
                               ("[RESONANCE]", "resonance", 100, 0)], (0, None), ["all"]],
    "Lonely Ring of the Dark Star": [[
        ("Dark Dream", "spec_conv", 300, "DarkDream"),
        ("X% chance Non-Bloom hits trigger Stygian Bloom", "spec_conv", 25, "Stygian"),
        ("[RESONANCE]", "resonance", 100, 2)], (0, None), [0, 2, 3, 6, 8]],
    "Lonely Ring of the Light Star": [[
        ("Light Dream", "spec_conv", 300, "LightDream"),
        ("X% chance Bloom hits trigger Heavenly Bloom", "spec_conv", 25, "Heavenly"),
        ("[RESONANCE]", "resonance", 100, 2)], (0, None), [1, 4, 5, 7, 8]],
    # Sovereign Rings
    "Stygian Calamity": [[("X% chance for Non-Bloom hits to trigger Calamity", "spec_conv", 90, "Calamity"),
                          ("X% Hybrid Curse (Chaos)", "elemental_curse", 999, (0, 2, 3, 6))], (0, None), [0, 2, 3, 6]],
    "Heavenly Calamity": [[("X% chance for Non-Bloom hits to trigger Calamity", "spec_conv", 90, "Calamity"),
                           ("X% Hybrid Curse (Holy)", "elemental_curse", 999, (1, 4, 5, 7))], (0, None), [1, 4, 5, 7]],
    "Hadal's Raindrop": [[("Aqua Cascade", "aqua_mode", 100, None), ("Aqua Conversion", None, 0, None),
                          ("Aqua Manifestation", None, 0, None)], (0, None), [1]],
    "Twin Rings of Divergent Stars":
        [[("Heavenly Star", "spec_conv", 50, "Heavenly"), ("Stygian Star", "spec_conv", 50, "Stygian"),
          ("Omni Curse X%", "all_elemental_curse", 300, None)], (0, None), [6, 7, 8]],
    "Crown of Skulls": [["Avaricious Ruin", "Banquet of Bones"], (0, None), [5]],
    "Chromatic Tears": [["Rainbow's End", "Cursed Wish", "Resonance [The Wish]"], (0, None), ["all"]]}

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
    path_value = 10 if ring_suffix != "Celestia" else 20
    ring_values_dict[f"{ring_prefix} Ring of {ring_suffix}"] = [abilities, (path_value, path_index), element_indices]

ring_resonance_dict, ring_element_dict = {}, {}
for ring_name, attributes in ring_values_dict.items():
    for attribute_set in attributes[0]:
        resonance_index = attribute_set[3] if "[RESONANCE]" in attribute_set else 0
    ring_resonance_dict[ring_name] = resonance_index
    ring_element_dict[ring_name] = attributes[2]
