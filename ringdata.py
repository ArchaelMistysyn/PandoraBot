ring_values_dict = {
    # Elemental Rings
    "Elemental Ring of Fire": [[("Fire Curse X%", "elemental_curse", 100, 0)], (0, None)],
    "Elemental Ring of Water": [[("Water Curse X%", "elemental_curse", 100, 1)], (0, None)],
    "Elemental Ring of Lightning": [[("Lightning Curse X%", "elemental_curse", 100, 2)], (0, None)],
    "Elemental Ring of Earth": [[("Earth Curse X%", "elemental_curse", 100, 3)], (0, None)],
    "Elemental Ring of Wind": [[("Wind Curse X%", "elemental_curse", 100, 4)], (0, None)],
    "Elemental Ring of Ice": [[("Ice Curse X%", "elemental_curse", 100, 5)], (0, None)],
    "Elemental Ring of Shadow": [[("Shadow Curse X%", "elemental_curse", 100, 6)], (0, None)],
    "Elemental Ring of Light": [[("Light Curse X%", "elemental_curse", 100, 7)], (0, None)],
    "Elemental Ring of Celestial": [[("Celestial Curse X%", "elemental_curse", 100, 8)], (0, None)],
    # Primordial Signet
    "Ruby Signet of Incineration": [[("Fire Curse X%", "elemental_curse", 500, 0),
                                     ("[RESONANCE]", "resonance", 100, 1)], (0, None)],
    "Sapphire Signet of Atlantis": [[("Water Curse X%", "elemental_curse", 500, 1),
                                     ("[RESONANCE]", "resonance", 100, 14)], (0, None)],
    "Topaz Signet of Dancing Thunder": [[("Lightning Curse X%", "elemental_curse", 500, 2),
                                         ("[RESONANCE]", "resonance", 100, 8)], (0, None)],
    "Agate Signet of Seismic Tremors": [[("Earth Curse X%", "elemental_curse", 500, 3),
                                         ("[RESONANCE]", "resonance", 100, 16)], (0, None)],
    "Emerald Signet of Wailing Winds": [[("Wind Curse X%", "elemental_curse", 500, 4),
                                         ("[RESONANCE]", "resonance", 100, 9)], (0, None)],
    "Zircon Signet of the Frozen Castle": [[("Ice Curse X%", "elemental_curse", 500, 5),
                                            ("[RESONANCE]", "resonance", 100, 13)], (0, None)],
    "Obsidian Signet of Tormented Souls": [[("Shadow Curse X%", "elemental_curse", 500, 6),
                                            ("[RESONANCE]", "resonance", 100, 12)], (0, None)],
    "Opal Signet of Scintillation": [[("Light Curse X%", "elemental_curse", 500, 7),
                                      ("[RESONANCE]", "resonance", 100, 11)], (0, None)],
    "Amethyst Signet of Shifting Stars": [[("Celestial Curse X%", "elemental_curse", 500, 8),
                                           ("[RESONANCE]", "resonance", 100, 17)], (0, None)],
    # Path Rings
    "Invoking Ring of Storms": [[("Water Curse X%", "elemental_curse", 250, 1),
                                 ("Lightning Curse X%", "elemental_curse", 250, 2),
                                 ("[RESONANCE]", "resonance", 100, 20)], (10, 0)],
    "Primordial Ring of Frostfire": [[("Fire Curse X%", "elemental_curse", 250, 0),
                                      ("Ice Curse X%", "elemental_curse", 250, 5),
                                      ("[RESONANCE]", "resonance", 100, 15)], (10, 1)],
    "Boundary Ring of Horizon": [[("Earth Curse X%", "elemental_curse", 250, 3),
                                  ("Wind Curse X%", "elemental_curse", 250, 4),
                                  ("[RESONANCE]", "resonance", 100, 19)], (10, 2)],
    "Hidden Ring of Eclipse": [[("Shadow Curse X%", "elemental_curse", 250, 6),
                                ("Light Curse X%", "elemental_curse", 250, 7),
                                ("[RESONANCE]", "resonance", 100, 18)], (10, 3)],
    "Cosmic Ring of Stars": [[("Celestial Curse X%", "elemental_curse", 1000, 8),
                              ("[RESONANCE]", "resonance", 100, 2)], (10, 4)],
    "Rainbow Ring of Confluence": [[("Omni Curse X%", "all_elemental_curse", 200, None),
                                    ("[RESONANCE]", "resonance", 100, 6)], (10, 5)],
    "Lonely Ring of Solitude": [[("Singularity Curse X%", "singularity_curse", 750, None),
                                 ("[RESONANCE]", "resonance", 100, 21)], (10, 6)],
    # Legendary Rings
    "Dragon's Eye Diamond": [[("Critical Rate is always X%", "perfect_crit", 100, None),
                              ("Critical Damage X%", "critical_multiplier", 500, None),
                              ("[RESONANCE]", "resonance", 100, 4)], (100, None)],
    "Chromatic Tears": [[("Omni Curse X%", "all_elemental_curse", 500, None),
                         ("[RESONANCE]", "resonance", 100, 25)], (0, None)],
    "Bleeding Hearts": [[("Bleed Application +X", "bleed_app", 5, None),
                         ("[RESONANCE]", "resonance", 100, 5)], (0, None)],
    "Gambler's Masterpiece": [[("All-In!", "rng_bonus", 777, None),
                               ("[RESONANCE]", "resonance", 100, 0)], (0, None)],
    # Sovereign Rings
    "Stygian Calamity": [[("X% chance for Non-Bloom hits to trigger Calamity", "spec_conv", 99, 2)],
                         [("X% Hybrid Curse (Chaos)", "elemental_curse", 999, (0, 2, 3, 6))], (0, None)],
    "Heavenly Calamity": [[("X% chance for Non-Bloom hits to trigger Calamity", "spec_conv", 99, 2)],
                          [("X% Hybrid Curse (Holy)", "elemental_curse", 999, (1, 4, 5, 7))], (0, None)],
    "Hadal's Raindrop": [[("Aqua Cascade", "aqua_mode", 100, None)], [("Aqua Conversion", None, 0, None)],
                         [("Aqua Manifestation", None, 0, None)], (0, None)],
    "Sacred Ring of Divergent Stars": [[("X% chance for Bloom hits to trigger Sacred Bloom", "spec_conv", 50, 0)],
                                       [("X% chance for Non-Bloom hits to trigger Abyssal Bloom", "spec_conv", 50, 1)],
                                       [("Omni Curse X%", "all_elemental_curse", 300, None)], (0, None)],
    "Crown of Skulls": [["Avaricious Ruin", "Banquet of Bones"], (0, None)]
}

ring_resonance_dict = {}

for ring_name, attributes in ring_values_dict.items():
    for attribute_set in attributes[0]:
        resonance_index = attribute_set[3] if "[RESONANCE]" in attribute_set else 0
    ring_resonance_dict[ring_name] = resonance_index