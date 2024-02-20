import discord
import globalitems
import inventory
import itemrolls

pact_variants = {"Wrath": [["Attack Speed Bonus", "Elemental Capacity"], ["Mitigation Bonus", "Base Luck"]],
                 "Sloth": [["Recovery", "Max HP"], ["Attack Speed", "Max Stamina"]],
                 "Greed": [["Specialty Rate Bonus", "Coin Acquisition"], ["Charge Generation", "EXP Acquisition"]],
                 "Gluttony": [["Charge Generation", "EXP Acquisition"], ["Elemental Capacity", "Coin Acquisition"]],
                 "Envy": [["Final Damage", "Base Luck"], ["Max HP", "Recovery"]],
                 "Pride": [["Singularity Damage", "Human Bane"], ["", ""]],
                 "Lust": [["Class Mastery Bonus", "Bleed Damage"], ["Singularity Damage", ""]]}

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
        for bonus_index, bonus in enumerate(pact_variants[self.pact_variant][0]):
            self.pact_bonuses += f"Double {bonus[bonus_index]}\n"
        for penalty_index, penalty in enumerate(pact_variants[self.pact_variant][1]):
            self.pact_bonuses += f"Halve {penalty[penalty_index]}\n"
        self.roll_1 = itemrolls.ItemRoll(f"{self.pact_tier}-damage-13")
        self.roll_2 = itemrolls.ItemRoll(f"{self.pact_tier}-unique-4-s")
        self.pact_bonuses += f"{self.roll_1.roll_msg}\n{self.roll_2.roll_msg}"
        self.pact_colour, self.pact_augment_icon = sharedmethods.get_gear_tier_colours(self.pact_tier)


def assign_pact_values(player_obj):
    if player_obj.pact == "":
        return
    pact_object = Pact(player_obj.pact)
    match pact_object.pact_variant:
        case "Wrath":
            player_obj.attack_speed *= 2
            player_obj.elemental_capacity *= 2
            player_obj.luck = int(round(player_obj.luck / 2))
            player_obj.mitigation_bonus = int(round(player_obj.mitigation_bonus / 2))
        case "Sloth":
            player_obj.player_mHP *= 2
            player_obj.recovery *= 2
            player_obj.attack_speed = int(round(player_obj.attack_speed / 2))
        case "Greed":
            player_obj.specialty_rate = [rate * 2 for rate in player_obj.specialty_rate]
            player_obj.charge_generation = int(round(player_obj.charge_generation / 2))
        case "Gluttony":
            player_obj.charge_generation *= 2
            player_obj.elemental_capacity = int(round(player_obj.elemental_capacity / 2))
        case "Envy":
            player_obj.final_damage *= 2
            player_obj.luck *= 2
            player_obj.player_mHP = int(round(player_obj.player_mHP / 2))
            player_obj.recovery = int(round(player_obj.recovery / 2))
        case "Pride":
            player_obj.singularity_damage *= 2
            player_obj.banes[5] *= 2
        case "Lust":
            player_obj.singularity_damage = int(round(player_obj.singularity_damage / 2))
            player_obj.bleed_multiplier *= 2
        case _:
            pass


def display_pact(player_obj):
    pact_object = Pact(player_obj.pact)
    pact_stars = sharedmethods.display_stars(pact_object.pact_tier)
    pact_embed = discord.Embed(colour=pact_object.pact_colour, title=pact_object.pact_name, description=pact_stars)
    pact_embed.add_field(name="Pact Bonuses", value=pact_object.pact_bonuses, inline=False)
    return pact_embed

