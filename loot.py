# General imports
import discord
import pandas as pd
import random

# Data imports
import globalitems
import itemdata
import sharedmethods
from pandoradb import run_query as rq

# Core imports
import player
import inventory


boss_loot_dict = {
    "All": [[0, "Crate", 25], [0, "Matrix1", 15], [0, "Core1", 1], [0, "OriginZ", 1],
            [0, "Hammer", 25], [0, "Pearl", 15], [0, "Heart1", 2], [0, "Heart2", 1],
            [1, "Ore1", 25], [2, "Ore2", 25], [3, "Ore3", 25], [4, "Ore4", 25],
            [1, "Potion1", 5], [2, "Potion2", 5], [3, "Potion3", 5], [4, "Potion4", 5],
            [5, "Potion4", 10], [6, "Potion4", 15], [7, "Potion4", 25], [8, "Potion4", 25],
            [5, "Core1", 3], [6, "Core2", 3], [7, "Core3", 3], [8, "Core4", 3],
            [5, "Crystal1", 1], [6, "Crystal2", 1], [7, "Crystal3", 1], [8, "Crystal4", 1],
            [5, "Fragment1", 75], [6, "Fragment2", 75], [7, "Fragment3", 99], [8, "Fragment4", 99]],
    "Fortress": [[0, "Scrap", 100], [0, "Stone1", 60],
                 [1, "Trove1", 5], [2, "Trove2", 5], [3, "Trove3", 5], [4, "Trove4", 5], [0, "Ore5", 5]],
    "Dragon": [[0, "Unrefined1", 25], [0, "Stone2", 55],
               [1, "Gem1", 10], [2, "Gem1", 20], [3, "Gem1", 30], [4, "Jewel1", 40]],
    "Demon": [[0, "Flame1", 10], [0, "Flame2", 1], [0, "Stone3", 50],
              [1, "Gem2", 10], [2, "Gem2", 20], [3, "Gem2", 30], [4, "Jewel2", 40]],
    "Paragon": [[0, "Summon1", 5], [0, "Summon2", 1], [0, "Unrefined3", 25], [0, "Stone4", 45],
                [1, "Gem3", 10], [2, "Gem3", 20], [3, "Gem3", 30],
                [4, "Jewel3", 40], [5, "Jewel3", 50], [6, "Jewel3", 60]],
    "Arbiter": [[0, "Summon3", 5], [0, "Stone6", 40], [7, "Lotus4", 1],
                [1, "Token1", 5], [2, "Token2", 5], [3, "Token3", 5], [4, "Token4", 5],
                [5, "Token5", 5], [6, "Token6", 5], [7, "Token7", 5],
                [1, "Jewel4", 10], [2, "Jewel4", 20], [3, "Jewel4", 30], [4, "Jewel4", 40],
                [5, "Jewel4", 50], [6, "Jewel4", 60], [7, "Jewel4", 70]],
    "Incarnate": [[8, "Core3", 50], [8, "Core4", 25], [8, "Jewel5", 80],
                  [8, "Lotus1", 5], [8, "Lotus2", 5], [8, "Lotus3", 5], [8, "Lotus4", 5], [8, "Lotus5", 5],
                  [8, "Lotus6", 5], [8, "Lotus7", 5], [8, "Lotus8", 5], [8, "Lotus9", 5],
                  [8, "Lotus10", 1], [8, "DarkStar", 1], [8, "EssenceXXX", 99]]}
incarnate_attempts_dict = {700: 1, 800: 2, 999: 5}


def update_loot_and_df(player_obj, item_id, quantity, loot_msg, counter, batch_df):
    temp_item = inventory.BasicItem(item_id)
    loot_msg[counter] += f"{temp_item.item_emoji} {quantity}x {temp_item.item_name}\n"
    batch_df.loc[len(batch_df)] = [player_obj.player_id, temp_item.item_id, quantity]
    return loot_msg, batch_df


async def create_loot_embed(current_embed, active_boss, player_list, ctx=None, loot_multiplier=1, gauntlet=False):
    type_bonus = (active_boss.boss_type_num + 1) * 100
    level_bonus = random.randint(active_boss.boss_level, (active_boss.boss_level * 10))
    multiplier_bonus = 2 if active_boss.player_id != 0 else loot_multiplier
    total = (1000 + type_bonus + level_bonus) * multiplier_bonus
    exp_amount, coin_amount = total, total * active_boss.boss_tier
    # Build and return the loot output.
    loot_output = await award_loot(active_boss, player_list, exp_amount, coin_amount, loot_multiplier, gauntlet, ctx)
    for counter, loot_section in enumerate(loot_output):
        temp_player = await player.get_player_by_id(player_list[counter])
        loot_msg = f'{temp_player.player_username} received:'
        current_embed.add_field(name=loot_msg, value=loot_section, inline=False)
    return current_embed


async def award_loot(boss_object, player_list, exp_amount, coin_amount, loot_multiplier, gauntlet, ctx):
    boss_tier = boss_object.boss_tier
    loot_msg = []
    labels = ['player_id', 'item_id', 'item_qty']
    batch_df = pd.DataFrame(columns=labels)
    for counter, x in enumerate(player_list):
        # Handle coins and exp.
        temp_player = await player.get_player_by_id(x)
        coin_msg = temp_player.adjust_coins(coin_amount)
        exp_msg, lvl_change = temp_player.adjust_exp(exp_amount)
        if lvl_change != 0 and boss_object.player_id != 0:
            await sharedmethods.send_notification(ctx, temp_player, "Level", lvl_change)
        base_reward_msg = f"{globalitems.exp_icon} {exp_msg} EXP\n"
        base_reward_msg += f"{globalitems.coin_icon} {coin_msg} lotus coins\n"
        loot_msg.append(base_reward_msg)

        # Check unscaled drops.
        core_element = boss_object.boss_element if boss_object.boss_element != 9 else random.randint(0, 8)
        fae_id, fae_qty = f"Fae{core_element}", random.randint(5, max(5, min(100, boss_object.boss_level)))
        fae_qty *= loot_multiplier
        loot_msg, batch_df = update_loot_and_df(temp_player, fae_id, fae_qty, loot_msg, counter, batch_df)
        if boss_object.player_id == 0 and is_dropped(75):
            loot_msg, batch_df = update_loot_and_df(temp_player, "Stone5", 1,
                                                    loot_msg, counter, batch_df)
        # Check essence drops.
        if ' - ' in boss_object.boss_name:
            card_qty = sum(is_dropped(20) for attempt in range(loot_multiplier))
            if card_qty > 0:
                numeral = boss_object.boss_name.split(" ", 1)
                loot_msg, batch_df = update_loot_and_df(temp_player, f"Essence{numeral[0]}",
                                                        card_qty, loot_msg, counter, batch_df)
        # Check gauntlet drops.
        if gauntlet:
            loot_msg, batch_df = update_loot_and_df(temp_player, f"Shard", 1, loot_msg, counter, batch_df)
            if "XXVIII" in boss_object.boss_name and is_dropped(5):
                loot_msg, batch_df = update_loot_and_df(temp_player, f"Lotus9", 1, loot_msg, counter, batch_df)
                await sharedmethods.send_notification(ctx, temp_player, "Item", "Lotus9")
            elif "XXV" in boss_object.boss_name and is_dropped(5):
                loot_msg, batch_df = update_loot_and_df(temp_player, f"Lotus8", 1, loot_msg, counter, batch_df)
                await sharedmethods.send_notification(ctx, temp_player, "Item", "Lotus8")

        # Handle boss drops.
        possible_loot = boss_loot_dict[boss_object.boss_type] + boss_loot_dict['All']
        possible_loot = [loot_entry for loot_entry in possible_loot if loot_entry[0] == boss_tier or loot_entry[0] == 0]
        for _, drop_id, drop_rate in possible_loot:
            qty = sum(is_dropped(drop_rate) for attempt in range(loot_multiplier))
            if qty > 0:
                loot_msg, batch_df = update_loot_and_df(temp_player, drop_id, qty, loot_msg, counter, batch_df)
                if sharedmethods.check_rare_item(drop_id):
                    await sharedmethods.send_notification(ctx, temp_player, "Item", drop_id)
    # Update the database.
    inventory.update_stock(None, None, None, batch=batch_df)
    return loot_msg


def is_dropped(drop_rate):
    random_num = random.randint(1, 10000)
    return True if random_num <= int(round((drop_rate * 100))) else False


def generate_random_item(quantity=1):
    # Initialize the quantity and data.
    rewards = {}
    quantity_table = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3]
    probability_rewards = [
        [10, None, "Lotus"], [1, "DarkStar", None], [1, "LightStar", None], [24, None, "Gemstone"],
        [100, None, "Essence"], [100, None, "Trove"], [100, None, "Origin"], [50, None, "Core"], [50, None, "Crystal"],
        [100, None, "Token"], [100, None, "Jewel"], [50, None, "Heart"], [200, None, "Summon"], [50, "Compass", None],
        [1000, "Pearl", None], [1000, "Hammer", None], [500, None, "Gem"], [1500, None, "Ore"],
        [500, None, "Fragment"], [500, "Flame1", None], [1000, "Matrix1", None], [1000, None, "Potion"],
        [2064, None, "Fae"]]
    max_reward = 10000  # sum(item[0] for item in probability_rewards)
    # Assign a reward id based on the probability, set id, or id prefix.
    for _ in range(quantity):
        current_breakpoint, random_item = 0, random.randint(1, max_reward)
        for item in probability_rewards:
            current_breakpoint += item[0]
            if random_item <= current_breakpoint:
                reward_id, prefix = item[1], item[2]
                if prefix is not None:
                    reward_types = [key for key in itemdata.itemdata_dict.keys() if key is not None and prefix in key]
                    reward_id = random.choice(reward_types)
                break
        # Handle quantity exceptions
        reward = inventory.BasicItem(reward_id)
        item_qty = 1 if reward.item_tier >= 4 else random.choice(quantity_table)
        if "Fae" in reward_id:
            item_qty = random.randint(5, (50 * item_qty))
        elif "Fragment" in reward_id:
            item_qty = 5
        # Update quantity on duplicate entries
        rewards[reward_id] = (rewards[reward_id] + item_qty) if reward_id in rewards else item_qty
    return [(reward_id, qty) for reward_id, qty in rewards.items()]


def generate_trove_reward(trove_object, trove_stock):
    num_coins, trove_msg = 0, ""
    bounds = itemdata.trove_rewards[trove_object.item_tier]
    for _ in range(trove_stock):
        num_coins += random.randint(bounds[0], bounds[1])
    trove_msg += f"{trove_object.item_emoji} {trove_stock}x {trove_object.item_name} opened: "
    return num_coins, trove_msg
