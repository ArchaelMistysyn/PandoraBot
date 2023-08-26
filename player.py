import pandas as pd
import csv
from csv import DictReader
import inventory


class PlayerProfile:
    def __init__(self):
        self.player_id = 0
        self.player_name = ""
        self.equipped_weapon = ""
        self.equipped_armour = ""
        self.equipped_acc = ""
        self.equipped_wing = ""
        self.equipped_crest = ""

    def __str__(self):
        return str(self.player_name)

    def update_player_name(self, new_name: str):
        self.player_name = new_name
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        df['player_name'] = df['player_name'].str.replace(self.player_name, new_name)

    def add_new_player(self) -> str:
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        if str(self.player_name) in df['player_name'].values:
            return "Player already exists."
        else:
            self.player_id = 10001 + df['player_id'].count()
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.player_id, self.player_name])
            return "Player added"

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

    def equip(self, item_type, item_id) -> str:
        filename = "playerlist.csv"
        df = pd.read_csv(filename)
        match item_type:
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


def get_player_by_id(player_id: int) -> PlayerProfile:
    target_player = PlayerProfile()
    filename = "playerlist.csv"

    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['player_id']) == str(player_id):
                target_player.player_name = int(line["player_name"])

        target_player.player_id = player_id
    return target_player


"""def get_player_by_name(player_name: str) -> PlayerProfile:
    target_player = PlayerProfile()
    filename = "playerlist.csv"
    df = pd.read_csv(filename)
    target_player.player_name = player_name
    target_player.player_id = df.loc[df["player_name"] == str(player_name), "player_id"].values[0]
    print(target_player.player_id)
    return target_player"""

def get_player_by_name(player_name: str) -> PlayerProfile:
    target_player = PlayerProfile()
    filename = "playerlist.csv"

    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['player_name']) == str(player_name):
                target_player.player_id = int(line["player_id"])

        target_player.player_name = player_name
    return target_player
