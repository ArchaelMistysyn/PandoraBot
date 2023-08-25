import pandas as pd
import csv
import random
import player


class basicItem:
    def __init__(self, item_id):
        self.item_id = item_id
        self.item_name = ""
        self.item_tier = ""
        self.item_base_rate = 0
        self.item_description = ""

        filename = "itemlist.csv"

        with (open(filename, 'r') as f):
            for line in csv.DictReader(f):
                if str(line['item_id']) == str(item_id):
                    self.item_name = str(line["item_name"])
                    self.item_tier = int(line["item_tier"])
                    self.item_base_rate = int(line["item_base_rate"])
                    self.item_description = str(line["item_description"])
                    self.item_emoji = str(line["item_emoji"])

    def __str__(self):
        return self.item_name


def award_loot(boss_type, boss_tier, player_list) -> str:
    filename = "droptable.csv"
    loot_msg = ""
    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line['boss_type']) == str(boss_type) and int(line['boss_tier']) <= int(boss_tier):
                dropped_item = str(line["item_id"])
                drop_rate = str(line["drop_rate"])
                for x in player_list:
                    if is_dropped(drop_rate):
                        # store dropped_item in craft inventory where player_name = x
                        loot_msg += x + " has received: " + get_item_emoji(dropped_item) + "\n"

    return loot_msg


def is_dropped(drop_rate) -> bool:
    random_num = random.randint(1, 100)

    if random_num <= drop_rate:
        return True
    else:
        return False


def get_item_emoji(item_id) -> str:
    filename = "itemlist.csv"

    with (open(filename, 'r') as f):
        for line in csv.DictReader(f):
            if str(line["item_id"]) == str(item_id):
                str_emoji = str(line["item_emoji"])

    return str_emoji
