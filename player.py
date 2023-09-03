import pandas as pd
import csv
from csv import DictReader
import inventory
import damagecalc


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
        self.player_hp = 100
        self.player_stamina = 0
        self.player_exp = 0
        self.player_lvl = 0
        self.player_echelon = 0

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
        df['player_username'] = df['player_username'].replace(str(self.player_name), new_name)
        df.to_csv(filename, index=False)
        self.player_username = new_name

    def add_new_player(self) -> str:
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        if str(self.player_name) in df['player_name'].values:
            return "Player already exists."
        else:
            self.player_id = 10001 + df['player_id'].count()
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.player_id, self.player_name, self.player_username,
                                 self.player_stamina, self.player_exp, self.player_lvl, self.player_echelon])
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
        df.loc[df['player_id'] == self.player_id, 'player_exp'] = df['player_exp'] + int(amount)
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

    def set_username(self, new_username):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df.loc[df['player_id'] == self.player_id, 'player_username'] = new_username
        df.to_csv(filename, index=False)

    def get_player_damage(self, boss_object) -> int:
        player_damage = 0
        self.get_equipped()
        e_weapon = inventory.read_custom_item(self.equipped_weapon)
        player_damage += (e_weapon.item_damage_min + e_weapon.item_damage_max) / 2
        e_armour = inventory.read_custom_item(self.equipped_armour)
        player_damage += (e_armour.item_damage_min + e_armour.item_damage_max) / 2
        e_acc = inventory.read_custom_item(self.equipped_acc)
        player_damage += (e_acc.item_damage_min + e_acc.item_damage_max) / 2

        # bonus stats
        float_damage = float(player_damage) * float(e_weapon.item_bonus_stat)
        float_damage *= damagecalc.accessory_ability_damage(e_acc.item_bonus_stat,
                                                            boss_object.boss_cHP, boss_object.boss_mHP, self.player_hp)

        float_damage *= damagecalc.boss_weakness_multiplier(e_weapon,
                                                            boss_object.boss_typeweak,
                                                            boss_object.boss_eleweak_a,
                                                            boss_object.boss_eleweak_b)

        player_damage = int(float_damage)

        return player_damage

    def get_equipped(self):
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        if str(self.player_name) in df['player_name'].values:
            temp = df.loc[df['player_id'] == self.player_id, ['equip_wpn_id']].values[0]
            self.equipped_weapon = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_armour_id']].values[0]
            self.equipped_armour = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_acc_id']].values[0]
            self.equipped_acc = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_wing_id']].values[0]
            self.equipped_wing = temp[0]
            temp = df.loc[df['player_id'] == self.player_id, ['equip_crest_id']].values[0]
            self.equipped_crest = temp[0]

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
                target_player.player_name = int(line["player_name"])
                target_player.player_username = str(line["player_username"])
                target_player.player_stamina = int(line["stamina"])
                target_player.player_exp = int(line["player_exp"])
                target_player.player_lvl = int(line["player_lvl"])
                target_player.player_echelon = int(line["player_echelon"])

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

        target_player.player_name = player_name
    return target_player
