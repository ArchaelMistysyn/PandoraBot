import pandas as pd
import csv
from csv import DictReader
import inventory
import damagecalc
import math
import random


class PlayerProfile:
    def __init__(self):
        self.player_id = 0
        self.player_name = ""
        self.player_username = ""
        self.equipped_weapon = ""
        self.equipped_armour = ""
        self.equipped_acc = ""
        self.equipped_wing = ""
        self.equipped_crest = ""
        self.player_mHP = 1000
        self.player_cHP = self.player_mHP
        self.player_stamina = 0
        self.player_exp = 0
        self.player_lvl = 0
        self.player_echelon = 0
        self.critical_chance = 0.0
        self.critical_multiplier = 0.0
        self.attack_speed = 0.0
        self.damage_mitigation = 0.0
        self.elemental_penetration = 0.0
        self.defence_penetration = 0.0
        self.final_damage = 0.0
        self.aura = 0.0
        self.curse = 0.0
        self.player_damage = 0.0
        self.hit_multiplier = 0.0
        self.special_multipliers = 0.0
        self.class_multiplier = 0.0
        self.hp_multiplier = 0.0
        self.player_coins = 0
        self.player_class = "Summoner"

    def __str__(self):
        return str(self.player_name)

    def update_player_name(self, new_name: str):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df['player_name'] = df['player_name'].replace(str(self.player_name), new_name)
        df.to_csv(filename, index=False)
        self.player_name = new_name

    def update_username(self, new_name: str):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df['player_username'] = df['player_username'].replace(str(self.player_username), new_name)
        df.to_csv(filename, index=False)
        self.player_username = new_name

    def add_new_player(self) -> str:
        item_id = []
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        if str(self.player_name) in df['player_name'].values:
            return "Player already exists."
        else:
            self.player_id = 10001 + df['player_id'].count()
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.player_id, self.player_name, self.player_name,
                                 2000, self.player_exp, self.player_lvl, self.player_echelon])
            filename = "itemlist.csv"
            with (open(filename, 'r') as f):
                for line in csv.DictReader(f):
                    item_id.append(str(line['item_id']))
            filename = "binventory.csv"
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                for x in item_id:
                    writer.writerow([self.player_id, x, 0])
            return "Player added"

    def spend_stamina(self, cost) -> bool:
        is_spent = False
        if self.player_stamina >= cost:
            self.player_stamina -= cost
            filename = "playerlist.csv"
            df = pd.read_csv(filename)
            df.loc[df['player_id'] == self.player_id, 'stamina'] = df['stamina'] - cost
            df.to_csv(filename, index=False)
            is_spent = True
        return is_spent

    def add_stamina(self, amount):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df.loc[df['player_id'] == self.player_id, 'stamina'] = df['stamina'] + int(amount)
        df.to_csv(filename, index=False)

    def add_exp(self, amount):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        new_exp = self.player_exp + int(amount)
        levelling = True
        while levelling:
            if new_exp >= get_max_exp(self.player_lvl):
                new_exp -= get_max_exp(self.player_lvl)
                self.player_lvl += 1
                df.loc[df['player_id'] == self.player_id, 'player_lvl'] = self.player_lvl
            else:
                levelling = False
        df.loc[df['player_id'] == self.player_id, 'player_exp'] = new_exp
        df.to_csv(filename, index=False)

    def add_level(self, amount):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df.loc[df['player_id'] == self.player_id, 'player_exp'] = df['player_lvl'] + int(amount)
        df.to_csv(filename, index=False)

    def add_echelon(self, amount):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df.loc[df['player_id'] == self.player_id, 'player_echelon'] = df['player_echelon'] + int(amount)
        df.to_csv(filename, index=False)

    def update_coins(self, amount):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df.loc[df['player_id'] == self.player_id, 'player_coins'] = df['player_coins'] + int(amount)
        df.to_csv(filename, index=False)

    def set_username(self, new_username):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df.loc[df['player_id'] == self.player_id, 'player_username'] = new_username
        df.to_csv(filename, index=False)

    def get_equipped(self):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        if str(self.player_name) in df['player_name'].values:
            temp = df.loc[df['player_id'] == self.player_id, ['equip_wpn_id']].values[0]
            if not checkNaN(temp):
                self.equipped_weapon = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_armour_id']].values[0]
            if not checkNaN(temp):
                self.equipped_armour = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_acc_id']].values[0]
            if not checkNaN(temp):
                self.equipped_acc = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_wing_id']].values[0]
            if not checkNaN(temp):
                self.equipped_wing = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_crest_id']].values[0]
            if not checkNaN(temp):
                self.equipped_crest = temp[0]

    def get_player_multipliers(self, boss_cHP, boss_mHP):
        self.get_equipped()

        base_critical_chance = 10.0
        base_attack_speed = 1.0
        base_damage_mitigation = 0.0
        base_player_hp = 1000
        sit_damage_multiplier = 0.0
        damage_multiplier = 0.0
        mitigation_multiplier = 0.0
        self.critical_chance = 0.0
        self.attack_speed = 0.0
        self.critical_multiplier = 0.0
        self.damage_mitigation = 0.0
        self.elemental_penetration = 0.0
        self.final_damage = 0.0
        self.aura = 0.0
        self.curse = 0.0
        self.hit_multiplier = 1.0
        self.player_damage = 0.0
        self.special_multipliers = 0.0
        self.class_multiplier = 0.0
        class_bonus = 0.0
        self.hp_multiplier = 0.0
        fractal = 1
        omega = 1
        is_mastery = False

        if self.equipped_weapon != "":
            e_weapon = inventory.read_custom_item(self.equipped_weapon)
            e_weapon.update_damage()
            self.player_damage += (e_weapon.item_damage_min + e_weapon.item_damage_max) / 2
            base_attack_speed = float(e_weapon.item_bonus_stat)
            self.assign_roll_values(e_weapon, "W")
            self.assign_gem_values(e_weapon)
        if self.equipped_armour != "":
            e_armour = inventory.read_custom_item(self.equipped_armour)
            e_armour.update_damage()
            self.player_damage += (e_armour.item_damage_min + e_armour.item_damage_max) / 2
            self.assign_roll_values(e_armour, "A")
            base_damage_mitigation = float(e_armour.item_bonus_stat)
            self.assign_gem_values(e_armour)
        if self.equipped_acc != "":
            e_acc = inventory.read_custom_item(self.equipped_acc)
            e_acc.update_damage()
            self.player_damage += (e_acc.item_damage_min + e_acc.item_damage_max) / 2
            self.assign_roll_values(e_acc, "Y")
            self.assign_gem_values(e_acc)
            x, y, z = damagecalc.accessory_ability_multipliers(
                                                     e_acc.item_bonus_stat,
                                                     boss_cHP,
                                                     boss_mHP,
                                                     self.player_cHP)
            damage_multiplier += x
            sit_damage_multiplier += y
            mitigation_multiplier += z
        if self.equipped_wing != "":
            e_wing = inventory.read_custom_item(self.equipped_wing)
            e_wing.update_damage()
            self.player_damage += (e_wing.item_damage_min + e_wing.item_damage_max) / 2
            self.assign_roll_values(e_wing, "G")
            self.assign_gem_values(e_wing)
            x, y, z = damagecalc.accessory_ability_multipliers(
                e_wing.item_bonus_stat,
                boss_cHP,
                boss_mHP,
                self.player_cHP)
            damage_multiplier += x
            sit_damage_multiplier += y
            mitigation_multiplier += z
        if self.equipped_crest != "":
            e_crest = inventory.read_custom_item(self.equipped_crest)
            e_crest.update_damage()
            match e_crest.item_bonus_stat:
                case "Elemental Fractal":
                    if self.equipped_weapon != "":
                        fractal = len(e_weapon.item_elements)
                case "Omega Critical":
                    omega = 5
                case "Specialized Mastery":
                    is_mastery = True
                case "Ignore Protection":
                    self.defence_penetration += 0.3
                    self.elemental_penetration += 0.4
                case "Perfect Precision":
                    base_critical_chance += 10
                case "Resistance Bypass":
                    self.elemental_penetration += 0.4
                case "Extreme Vitality":
                    self.hp_multiplier += 5
                case "Defence Bypass":
                    self.defence_penetration += 0.3
                case _:
                    nothing = 0
            self.player_damage += (e_crest.item_damage_min + e_crest.item_damage_max) / 2
            self.assign_roll_values(e_crest, "C")
            self.assign_gem_values(e_crest)

        self.critical_chance = (1 + self.critical_chance) * base_critical_chance
        self.attack_speed = (1 + self.attack_speed) * base_attack_speed
        self.damage_mitigation = (1 + (mitigation_multiplier + self.damage_mitigation)) * base_damage_mitigation
        self.player_mHP = int(base_player_hp * (1 + self.hp_multiplier))
        self.final_damage += damage_multiplier
        if boss_cHP != -1:
            self.final_damage += sit_damage_multiplier

        match self.player_class:
            case "Ranger":
                class_icon = '<:cA:1150195102589931641>'
            case "Knight":
                class_icon = '<:cB:1154266777396711424>'
            case "Mage":
                class_icon = "<:cC:1150195246588764201>"
            case _:
                class_icon = "<:cD:1150195280969478254>"

        if self.equipped_weapon != "":
            if e_weapon.item_damage_type == class_icon:
                class_bonus += 1
        if self.equipped_armour != "":
            if e_armour.item_damage_type == class_icon:
                class_bonus += 1
        if self.equipped_acc != "":
            if e_acc.item_damage_type == class_icon:
                class_bonus += 1
        if self.equipped_wing != "":
            if e_wing.item_damage_type == class_icon:
                class_bonus += 1
        if self.equipped_crest != "":
            if e_crest.item_damage_type == class_icon:
                class_bonus += 1
        self.class_multiplier = class_bonus * 0.05
        if is_mastery:
            self.class_multiplier += class_bonus

        self.special_multipliers = float(omega) * float(fractal)

    def assign_roll_values(self, equipped_item, item_type):
        for x in equipped_item.item_prefix_values:
            roll_tier = int(str(x)[1])
            match str(x)[2]:
                case "1":
                    self.critical_chance += 0.25 * float(roll_tier)
                case "2":
                    self.attack_speed += 0.25 * float(roll_tier)
                case "3":
                    self.elemental_penetration += 0.25 * float(roll_tier)
                case "4":
                    self.final_damage += 0.25 * float(roll_tier)
                case "5":
                    self.damage_mitigation += 0.05 * float(roll_tier)
                case _:
                    no_change = True
        for y in equipped_item.item_suffix_values:
            roll_tier = int(str(y)[1])
            match str(y)[2]:
                case "1":
                    self.critical_multiplier += 0.50 * float(roll_tier)
                case "2":
                    self.aura += 0.25 * float(roll_tier)
                case "3":
                    self.curse += 0.25 * float(roll_tier)
                case "4":
                    if item_type == "W":
                        self.hit_multiplier += float(roll_tier)
                    else:
                        self.hp_multiplier += 0.5 * float(roll_tier)
                case _:
                    no_change = True

    def assign_gem_values(self, e_item):
        gem_id = e_item.item_inlaid_gem_id
        if gem_id != "":
            e_gem = inventory.read_custom_item(gem_id)
            self.player_damage += (e_gem.item_damage_min + e_gem.item_damage_max) / 2
            for x in e_gem.item_prefix_values:
                buff_type, buff_value = inventory.gem_stat_reader(str(x))
                match buff_type:
                    case "HP":
                        self.hp_multiplier += float(buff_value) * 0.01
                    case "Critical Chance":
                        self.critical_chance += float(buff_value) * 0.01
                    case "Final Damage":
                        self.final_damage += float(buff_value) * 0.01
                    case _:
                        no_change = True
            for y in e_gem.item_suffix_values:
                buff_type, buff_value = inventory.gem_stat_reader(str(y))
                match buff_type:
                    case "Attack Speed":
                        self.attack_speed += float(buff_value) * 0.01
                    case "Damage Mitigation":
                        self.damage_mitigation += float(buff_value) * 0.01
                    case "Critical Damage":
                        self.critical_multiplier += float(buff_value) * 0.01
                    case _:
                        no_change = True

    def equip(self, item_identifier, item_id) -> str:
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        match item_identifier:
            case 'W':
                self.equipped_weapon = item_id
                response = f"Weapon {item_id} is now equipped."
                df.loc[df["player_name"] == str(self.player_name), "equip_wpn_id"] = item_id
            case 'A':
                self.equipped_armour = item_id
                response = f"Armour {item_id} is now equipped."
                df.loc[df["player_name"] == str(self.player_name), "equip_armour_id"] = item_id
            case 'Y':
                self.equipped_acc = item_id
                response = f"Accessory {item_id} is now equipped."
                df.loc[df["player_name"] == str(self.player_name), "equip_acc_id"] = item_id
            case 'G':
                self.equipped_wing = item_id
                response = f"Wing {item_id} is now equipped."
                df.loc[df["player_name"] == str(self.player_name), "equip_wing_id"] = item_id
            case 'C':
                self.equipped_crest = item_id
                response = f"Crest {item_id} is now equipped."
                df.loc[df["player_name"] == str(self.player_name), "equip_crest_id"] = item_id
            case _:
                response = "error"

        df.to_csv(filename, index=False)

        return response


def check_username(new_name: str):
    filename = "playerlist.csv"
    df = pd.read_csv(filename)
    if new_name in df['player_username'].values:
        can_proceed = False
    else:
        can_proceed = True
    return can_proceed


def get_player_by_id(player_id: int) -> PlayerProfile:
    target_player = PlayerProfile()
    filename = "playerlist.csv"

    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['player_id']) == str(player_id):
                target_player.player_name = str(line["player_name"])
                target_player.player_username = str(line["player_username"])
                target_player.player_stamina = int(line["stamina"])
                target_player.player_exp = int(line["player_exp"])
                target_player.player_lvl = int(line["player_lvl"])
                target_player.player_echelon = int(line["player_echelon"])
                target_player.player_class = str(line["player_class"])
                target_player.player_coins = int(line["player_coins"])
        target_player.player_id = player_id
    return target_player


def get_player_by_name(player_name: str) -> PlayerProfile:
    target_player = PlayerProfile()
    filename = "playerlist.csv"
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['player_name']) == str(player_name):
                target_player.player_id = int(line["player_id"])
                target_player.player_username = str(line["player_username"])
                target_player.player_stamina = int(line["stamina"])
                target_player.player_exp = int(line["player_exp"])
                target_player.player_lvl = int(line["player_lvl"])
                target_player.player_echelon = int(line["player_echelon"])
                target_player.player_class = str(line["player_class"])
                target_player.player_coins = int(line["player_coins"])
        target_player.player_name = player_name
    return target_player


def get_max_exp(player_lvl):
    exp_required = int(1000 * (1.1 ** player_lvl))
    return exp_required


def checkNaN(str):
    try:
        result = math.isnan(float(str))
        return result
    except Exception as e:
        return False


def get_thumbnail_by_class(class_name):
    match class_name:
        case "Ranger":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Ranger.png'
        case "Knight":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Knight.png'
        case "Mage":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Mage.png'
        case "Summoner":
            thumbnail_url = 'https://kyleportfolio.ca/botimages/Summoner.png'
        case _:
            thumbnail_url = "error"

    return thumbnail_url
