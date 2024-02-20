# General imports
import discord
import pandas as pd
import random

# Data imports
import globalitems
import itemdata
import sharedmethods
import mydb

# Core imports
import player
import inventory


boss_loot_dict = {
    "All": [
        [0, "Crate", 10], [0, "Matrix1", 15],
        [0, "Hammer1", 20], [0, "Pearl1", 10], [0, "Heart1", 2], [0, "Heart2", 1],
        [1, "Ore1", 25], [2, "Ore2", 25], [3, "Ore3", 25], [4, "Ore4", 25],
        [1, "Potion1", 5], [2, "Potion2", 5], [3, "Potion3", 5], [4, "Potion4", 5],
        [5, "Potion4", 10], [6, "Potion4", 15], [7, "Potion4", 25],
        [4, "OriginZ", 10], [5, "OriginZ", 10], [6, "OriginZ", 10], [7, "OriginZ", 25],
        [5, "Core1", 25], [6, "Core2", 1], [7, "Core1", 50], [7, "Core2", 10], [7, "Core3", 5],
        [5, "Fragment1", 75], [6, "Fragment2", 75], [7, "Fragment3", 99],
        [6, "Crystal1", 2], [6, "Crystal2", 0.1],  [7, "Crystal1", 5], [7, "Crystal2", 0.2]
    ],
    "Fortress": [
        [0, "Scrap", 100], [0, "Summon1", 5], [0, "Stone1", 75],
        [0, "Trove1", 5], [0, "Trove2", 1], [0, "Trove3", 0.1], [0, "Trove4", 0.01]
    ],
    "Dragon": [
        [0, "Summon2", 5], [0, "Unrefined1", 25], [0, "Stone2", 75],
        [1, "Gem1", 10], [2, "Gem1", 20], [3, "Gem1", 30], [4, "Jewel1", 40]
    ],
    "Demon": [
        [0, "Summon3", 5], [0, "Flame1", 10], [0, "Stone3", 75], [0, "Core1", 3],
        [1, "Gem2", 10], [2, "Gem2", 20], [3, "Gem2", 30], [4, "Jewel2", 40]
    ],
    "Paragon": [
        [0, "Summon4", 5], [0, "Unrefined3", 25], [0, "Stone4", 75], [0, "Core1", 5],
        [1, "Gem3", 10], [2, "Gem3", 20], [3, "Gem3", 30],
        [4, "Jewel3", 40], [5, "Jewel3", 50], [6, "Jewel3", 60]
    ],
    "Arbiter": [
        [0, "Summon5", 5], [0, "Stone6", 75], [7, "Lotus4", 1],
        [1, "Token1", 5], [2, "Token2", 5], [3, "Token3", 5], [4, "Token4", 5],
        [5, "Token5", 5], [6, "Token6", 5], [7, "Token7", 5],
        [1, "Jewel4", 10], [2, "Jewel4", 20], [3, "Jewel4", 30], [4, "Jewel4", 40],
        [5, "Jewel4", 50], [6, "Jewel4", 60], [7, "Jewel4", 70]
    ],
    "Incarnate": [
        [8, "Core3", 50], [8, "Core4", 25], [8, "Jewel5", 80],
        [8, "Lotus1", 5], [8, "Lotus2", 5], [8, "Lotus3", 5], [8, "Lotus4", 5], [8, "Lotus5", 5],
        [8, "Lotus6", 5], [8, "Lotus7", 5], [8, "Lotus8", 5], [8, "Lotus9", 5],
        [8, "Lotus10", 1], [8, "DarkStar", 1], [8, "EssenceXXX", 99]
    ]
}
incarnate_attempts_dict = {700: 1, 800: 2, 999: 5}


def update_loot_and_df(player_obj, item_id, quantity, loot_msg, counter, df_change):
    temp_item = inventory.BasicItem(item_id)
    loot_msg[counter] += f"{item_object.item_emoji} {quantity}x {item_object.item_name}\n"
    df_change.loc[len(df_change)] = [player_obj.player_id, item_object.item_id, quantity]
    return loot_msg, df_change


async def create_loot_embed(current_embed, active_boss, player_list, ctx=None, loot_multiplier=1, gauntlet=False):
    # Calculate the base exp and coins. Calculate level bonuses.
    exp_amount = (active_boss.boss_tier * 250) + (active_boss.boss_type_num * 100)
    level_bonus = random.randint((active_boss.boss_level * 25), (active_boss.boss_level * 100))
    exp_amount += level_bonus
    coin_amount = active_boss.boss_type_num * active_boss.boss_tier * 250
    coin_amount += int(level_bonus / 10)
    # Raid boss awards 5x exp and coins, regular boss awards 2x exp and coins.
    exp_coin_bonus = 2 if active_boss.player_id == 0 else loot_multiplier
    exp_amount *= exp_coin_bonus
    coin_amount *= exp_coin_bonus
    # Build and return the loot output.
    loot_output = await award_loot(active_boss, player_list, exp_amount, coin_amount, loot_multiplier, gauntlet, ctx)
    for counter, loot_section in enumerate(loot_output):
        temp_player = player.get_player_by_id(player_list[counter])
        loot_msg = f'{temp_player.player_username} received:'
        current_embed.add_field(name=loot_msg, value=loot_section, inline=False)
    return current_embed


async def award_loot(boss_object, player_list, exp_amount, coin_amount, loot_multiplier, gauntlet, ctx):
    boss_tier = boss_object.boss_tier
    loot_msg = []
    labels = ['player_id', 'item_id', 'item_qty']
    df_change = pd.DataFrame(columns=labels)
    for counter, x in enumerate(player_list):
        # Handle coins and exp.
        temp_player = player.get_player_by_id(x)
        temp_coin_amount = coin_amount + temp_player.player_lvl
        coin_msg = temp_player.adjust_coins(temp_coin_amount)
        exp_msg, lvl_change = temp_player.adjust_exp(exp_amount)
        if lvl_change != 0 and boss_object.player_id != 0:
            await sharedmethods.send_notification(self.expedition.ctx_object, temp_player, "Level", lvl_change)
        loot_msg.append(f"{globalitems.exp_icon} {exp_msg}\n{globalitems.coin_icon} {coin_msg}\n")

        # Check unscaled drops.
        core_element = boss_object.boss_element if boss_object.boss_element != 9 else random.randint(0, 8)
        fae_id, fae_qty = f"Fae{core_element}", random.randint(1, min(100, boss_object.boss_level))
        fae_qty = loot_multiplier
        loot_msg, df_change = update_loot_and_df(temp_player, fae_id, fae_qty, loot_msg, counter, df_change)
        if boss_object.player_id == 0 and is_dropped(75):
            loot_msg, df_change = update_loot_and_df(temp_player, "Stone5", 1,
                                                     loot_msg, counter, df_change)
        # Check essence drops.
        if ' - ' in boss_object.boss_name:
            card_qty = sum(is_dropped(20) for attempt in range(loot_multiplier))
            if card_qty > 0:
                numeral = boss_object.boss_name.split(" ", 1)
                loot_msg, df_change = update_loot_and_df(temp_player, f"Essence{numeral[0]}",
                                                         card_qty, loot_msg, counter, df_change)
        # Check gauntlet drops.
        if gauntlet:
            if "XXVIII" in boss_object.boss_name and is_dropped(5):
                loot_msg, df_change = update_loot_and_df(temp_player, f"Lotus9", 1, loot_msg, counter, df_change)
                await sharedmethods.send_notification(ctx, temp_player, "Item", "Lotus9")
            elif "XXV" in boss_object.boss_name and is_dropped(5):
                loot_msg, df_change = update_loot_and_df(temp_player, f"Lotus8", 1, loot_msg, counter, df_change)
                await sharedmethods.send_notification(ctx, temp_player, "Item", "Lotus8")

        # Handle boss drops.
        possible_loot = boss_loot_dict[boss_object.boss_type] + boss_loot_dict['All']
        possible_loot = [loot_entry for loot_entry in possible_loot if loot_entry[0] == boss_tier or loot_entry[0] == 0]
        for _, drop_id, drop_rate in possible_loot:
            qty = sum(is_dropped(drop_rate) for attempt in range(loot_multiplier))
            if qty > 0:
                loot_msg, df_change = update_loot_and_df(temp_player, loot_item, qty, loot_msg, counter, df_change)
                if "Lotus" in drop_id or drop_id in ["DarkStar", "LightStar"]:
                    await sharedmethods.send_notification(ctx, temp_player, "Item", drop_id)
    # Update the database.
    pandora_db = mydb.start_engine()
    df_params = df_change.to_dict('records')
    base_query = ('''INSERT INTO BasicInventory (player_id, item_id, item_qty)
                  VALUES (:player_id, :item_id, :item_qty)
                  ON DUPLICATE KEY UPDATE item_qty = item_qty + VALUES(item_qty);''')
    pandora_db.run_query(query, batch=True, params=df_params)
    pandora_db.close_engine()
    return loot_msg


def is_dropped(drop_rate):
    random_num = random.randint(1, 10000)
    return True if random_num <= int(round((drop_rate * 100))) else False


def generate_random_item():
    # Initialize the quantity and data.
    quantity_table = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3]
    probability_rewards = [
        [10, None, "Lotus"], [1, "DarkStar", None], [1, "LightStar", None],
        [100, None, "Essence"], [18, "Trove8", None], [100, None, "Origin"], [50, None, "Core"], [50, None, "Crystal"],
        [100, None, "Token"], [100, None, "Jewel"], [50, None, "Heart"], [200, None, "Summon"], [50, "Compass", None],
        [50, "Ore6", None], [50, "Trove7", None],  [70, "Trove6", None],
        [200, "Pearl2", None], [200, "Hammer2", None], [500, "Pearl1", None], [500, "Hammer1", None],
        [100, "Trove5", None],  [100, "Trove4", None], [100, "Trove3", None],
        [100, "Trove2", None], [100, "Trove1", None], [500, None, "Gem"], [100, "Ore5", None],
        [500, None, "Fragment"], [500, "Flame1", None], [1000, "Matrix1", None], [1000, None, "Potion"],
        [250, "Ore4", None], [250, "Ore3", None], [250, "Ore2", None], [250, "Ore1", None],
        [2500, None, "Fae"]
    ]
    random_reward = random.randint(1, 10000)  # sum(item[0] for item in probability_rewards)
    # Assign a reward id based on the probability, set id, or id prefix.
    current_breakpoint = 0
    for item in probability_rewards:
        current_breakpoint += item[0]
        if random_reward <= current_breakpoint:
            reward_id = item[1]
            if prefix is not None:
                reward_types = [key for key in itemdata.itemdata_dict.keys() if key is not None and prefix in key]
                reward_id = random.choice(reward_types)
            break
    # Handle quantity
    reward = inventory.BasicItem(reward_id)
    quantity = 1 if reward.item_tier >= 4 else random.choice(quantity_table)
    if "Fae" in reward_id:
        quantity = random.randint(5, (50 * quantity))
    return reward, quantity


def generate_trove_reward(item_tier):
    bounds = itemdata.trove_rewards[item_tier]
    num_coins = random.randint(bounds[0], bounds[1])
    return num_coins
