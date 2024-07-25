# General imports
import discord

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import inventory

# Item/crafting imports
import itemrolls


pact_variants = {"Wrath": [["Attack Speed Bonus", "Elemental Capacity"], ["Mitigation Bonus", "Luck Bonus"]],
                 "Sloth": [["Recovery", "Max HP"], ["Attack Speed", "Max Stamina"]],
                 "Greed": [["Specialty Rate Bonus", "Coin Acquisition"], ["Charge Generation", "EXP Acquisition"]],
                 "Gluttony": [["Charge Generation", "EXP Acquisition"], ["Elemental Capacity", "Coin Acquisition"]],
                 "Envy": [["Final Damage", "Base Luck"], ["Max HP", "Recovery"]],
                 "Pride": [["Singularity Damage", "Human Bane"], ["Dodge Rate", "Block Rate"]],
                 "Lust": [["Class Mastery Bonus", "Bleed Damage"], ["Singularity Damage", "Mana Damage"]]}

demon_variants = {1: "Lesser Incubus", 2: "Shadow Fiend", 3: "Cursed Defiler", 4: "Death Shade",
                  5: "Void Devourer", 6: "Arch Demon", 7: "Abyssal Monarch", 8: "Stygian Reaver"}


class Pact:
    def __init__(self, pact_code):
        self.pact_tier = 0
        self.pact_variant, self.pact_demon = "", ""
        self.pact_name = ""
        self.pact_bonuses = ""
        self.pact_colour, self.pact_augment_icon = None, None

        if pact_code == "":
            return
        pact_data = pact_code.split(";")
        self.pact_tier = int(pact_data[0])
        self.pact_demon = demon_variants[self.pact_tier]
        self.pact_variant = pact_data[1]
        self.pact_name = f"{self.pact_demon} Pact [{self.pact_variant}]"
        for bonus in pact_variants[self.pact_variant][0]:
            self.pact_bonuses += f"Double {bonus}\n"
        for penalty in pact_variants[self.pact_variant][1]:
            self.pact_bonuses += f"Halve {penalty}\n"
        self.roll_1 = itemrolls.ItemRoll(f"{self.pact_tier}-damage-13")
        self.roll_2 = itemrolls.ItemRoll(f"{self.pact_tier}-unique-4-s")
        self.pact_bonuses += f"{self.roll_1.roll_msg}\n{self.roll_2.roll_msg}"
        self.pact_colour, self.pact_augment_icon = sm.get_gear_tier_colours(self.pact_tier)


def assign_pact_values(player_obj):
    if player_obj.pact == "":
        return
    pact_object = Pact(player_obj.pact)
    match pact_object.pact_variant:
        case "Wrath":
            player_obj.attack_speed *= 2
            player_obj.elemental_capacity *= 2
            player_obj.luck_bonus = int(round(player_obj.luck_bonus / 2)) if player_obj.luck_bonus != 0 else 0
            player_obj.mitigation_bonus = int(round(player_obj.mitigation_bonus / 2)) if player_obj.mitigation_bonus != 0 else 0
        case "Sloth":
            player_obj.player_mHP *= 2
            player_obj.recovery *= 2
            player_obj.attack_speed = int(round(player_obj.attack_speed / 2)) if player_obj.attack_speed != 0 else 0
        case "Greed":
            for key in ["Omega", "Hyperbleed", "Fractal", "Time Lock", "Bloom"]:
                player_obj.trigger_rate[key] *= 2
            player_obj.charge_generation = int(round(player_obj.charge_generation / 2))
        case "Gluttony":
            player_obj.charge_generation *= 2
            player_obj.elemental_capacity = int(round(player_obj.elemental_capacity / 2))
        case "Envy":
            player_obj.final_damage *= 2
            player_obj.luck_bonus *= 2
            player_obj.player_mHP = int(round(player_obj.player_mHP / 2))
            player_obj.recovery = int(round(player_obj.recovery / 2)) if player_obj.recovery != 0 else 0
        case "Pride":
            player_obj.singularity_mult *= 2
            player_obj.banes[5] *= 2
            player_obj.dodge = int(round(player_obj.dodge / 2)) if player_obj.dodge != 0 else 0
            player_obj.block = int(round(player_obj.block / 2)) if player_obj.block != 0 else 0
        case "Lust":
            player_obj.bleed_mult *= 2
            player_obj.class_multiplier *= 2
            player_obj.singularity_mult = int(round(player_obj.singularity_mult / 2))
            player_obj.mana_mult = int(round(player_obj.mana_mult / 2))
        case _:
            pass


def display_pact(player_obj):
    pact_object = Pact(player_obj.pact)
    pact_stars = sm.display_stars(pact_object.pact_tier)
    pact_embed = discord.Embed(colour=pact_object.pact_colour, title=pact_object.pact_name, description=pact_stars)
    pact_embed.add_field(name="Pact Bonuses", value=pact_object.pact_bonuses, inline=False)
    file_name = f"Frame_Pact_{pact_object.pact_tier}_{pact_object.pact_variant}.png"
    pact_embed.set_thumbnail(url=f"{gli.web_url}Gear_Icon/Pact/{file_name}")
    return pact_embed

