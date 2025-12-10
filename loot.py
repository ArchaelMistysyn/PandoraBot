# General imports
import discord
import pandas as pd
import random

# Data imports
import globalitems as gli
import itemdata
import sharedmethods as sm
from pandoradb import run_query as rqy

# Core imports
import player
import inventory


boss_loot_dict = {
    "All": [[0, "Chest", 25], [0, "Matrix", 15], [0, "Crystal1", 1], [0, "Catalyst", 1],
            [0, "Skull4", 0.005], [0, "Skull3", 0.05], [0, "Skull2", 0.5], [0, "Skull1", 5],
            [0, "Hammer", 25], [0, "Pearl", 15], [0, "Heart1", 2], [0, "Heart2", 1],
            [1, "Ore1", 25], [2, "Ore2", 25], [3, "Ore3", 25], [4, "Ore4", 25],
            [1, "Potion1", 5], [2, "Potion2", 5], [3, "Potion3", 5], [4, "Potion4", 5],
            [5, "Potion4", 10], [6, "Potion4", 15], [7, "Potion4", 25], [8, "Potion4", 25],
            [6, "Crystal2", 1], [7, "Crystal3", 1], [8, "Crystal4", 1],
            [5, "Fragment1", 75], [6, "Fragment2", 75], [7, "Fragment3", 99], [8, "Fragment4", 99]],
    "Fortress": [[0, "Scrap", 100], [0, "Stone1", 60],
                 [1, "Trove1", 5], [2, "Trove2", 5], [3, "Trove3", 5], [4, "Trove4", 5], [0, "Ore5", 5]],
    "Dragon": [[0, "Unrefined1", 25], [0, "Stone2", 55],
               [1, "Gem1", 10], [2, "Gem1", 20], [3, "Gem1", 30], [4, "Jewel1", 40]],
    "Demon": [[0, "Flame1", 10], [0, "Flame2", 1], [0, "Stone3", 50], [0, "Unrefined2", 25],
              [1, "Gem2", 10], [2, "Gem2", 20], [3, "Gem2", 30], [4, "Jewel2", 40]],
    "Paragon": [[0, "Summon1", 5], [0, "Summon2", 1], [0, "Unrefined3", 25], [0, "Stone4", 45],
                [1, "Gem3", 10], [2, "Gem3", 20], [3, "Gem3", 30],
                [4, "Jewel3", 40], [5, "Jewel3", 50], [6, "Jewel3", 60], [6, "Gemstone10", 5]],
    "Arbiter": [[0, "Summon3", 5], [0, "Stone5", 40], [7, "Lotus5", 5],
                [1, "Token1", 5], [2, "Token2", 5], [3, "Token3", 5], [4, "Token4", 5],
                [5, "Token5", 5], [6, "Token6", 5], [7, "Token7", 5],
                [1, "Jewel4", 10], [2, "Jewel4", 20], [3, "Jewel4", 30], [4, "Jewel4", 40],
                [5, "Jewel4", 50], [6, "Jewel4", 60], [7, "Jewel4", 70]],
    "Incarnate": [[8, "Crystal3", 10], [8, "Crystal4", 5], [8, "Jewel5", 80], [8, "Trove8", 99],
                  [8, "Lotus2", 5], [8, "Lotus3", 5], [8, "Lotus4", 5], [8, "Lotus5", 5], [8, "Lotus6", 5],
                  [8, "Lotus7", 5], [8, "Lotus8", 5], [8, "Lotus9", 5], [8, "Lotus1", 5],
                  [8, "Lotus10", 1], [8, "DarkStar", 2], [8, "Nephilim", 1], [8, "EssenceXXX", 99]],
    "Ruler": [[9, "Stone6", 33], [9, "Crystal4", 1], [9, "Trove9", 0.5],
              [9, "Salvation", 0.2], [9, "Ruler", 0.01], [9, "Sacred", 0.05]]}
incarnate_attempts_dict = {300: 1, 600: 2, 999: 5}


def update_loot_and_df(player_obj, item_id, quantity, msg, counter, batch_df):
    temp_item = inventory.BasicItem(item_id)
    msg[counter] += f"{temp_item.item_emoji} {quantity}x {temp_item.item_name}\n"
    batch_df.loc[len(batch_df)] = [player_obj.player_id, temp_item.item_id, quantity]
    return msg, batch_df


async def create_loot_embed(current_embed, active_boss, player_list, ctx=None, loot_mult=1, gauntlet=False, magni=0):
    type_bonus = (active_boss.boss_type_num + 1) * 100
    level_bonus = random.randint(active_boss.boss_level, (active_boss.boss_level * 10))
    multiplier_bonus = 2 if active_boss.player_id != 0 else loot_mult
    total = (1000 + type_bonus + level_bonus) * multiplier_bonus
    exp_amount, coin_amount = total * (1 + 2 * magni), total * active_boss.boss_tier * (1 + magni)
    # Build and return the loot output.
    loot_output = await award_loot(active_boss, player_list, exp_amount, coin_amount, loot_mult, gauntlet, ctx, magni)
    for counter, loot_section in enumerate(loot_output):
        temp_player = await player.get_player_by_id(player_list[counter])
        msg = f'{temp_player.player_username} received:'
        current_embed.add_field(name=msg, value=loot_section, inline=False)
    return current_embed


async def award_loot(boss_object, player_list, exp_amount, coin_amount, loot_mult, gauntlet, ctx, magni=0):
    boss_tier = boss_object.boss_tier
    msg = []
    labels = ['player_id', 'item_id', 'item_qty']
    batch_df = pd.DataFrame(columns=labels)
    for counter, player_id in enumerate(player_list):
        # Handle coins and exp.
        temp_player = await player.get_player_by_id(player_id)
        coin_msg = await temp_player.adjust_coins(coin_amount)
        exp_amount = 200000 if 'XXX' in boss_object.boss_name else exp_amount
        exp_msg, lvl_change = await temp_player.adjust_exp(exp_amount)
        if lvl_change != 0 and boss_object.player_id != 0:
            await sm.send_notification(ctx, temp_player, "Level", lvl_change)
        base_reward_msg = f"{gli.exp_icon} {exp_msg} EXP\n"
        base_reward_msg += f"{gli.coin_icon} {coin_msg} lotus coins\n"
        msg.append(base_reward_msg)

        # Handle ring souls
        if temp_player.player_equipped[4] != 0:
            e_ring = await inventory.read_custom_item(temp_player.player_equipped[4])
            if e_ring.item_base_type == "Crown of Skulls":
                e_ring.roll_values[1] = str(int(e_ring.roll_values[1]) + 1)
                await e_ring.update_stored_item()

        # Check unscaled drops.
        core_element = boss_object.boss_element if boss_object.boss_element != 9 else random.randint(0, 8)
        fae_id, fae_qty = f"Fae{core_element}", random.randint(5, max(5, min(100, boss_object.boss_level)))
        fae_qty *= loot_mult
        msg, batch_df = update_loot_and_df(temp_player, fae_id, fae_qty, msg, counter, batch_df)
        min_shards, max_shards = (1 if magni != 0 else 0), magni
        # Check essence drops.
        if ' - ' in boss_object.boss_name and "XXX" not in boss_object.boss_name:
            qty = sum(is_dropped(25) for attempt in range(loot_mult))
            if qty > 0:
                numeral = boss_object.boss_name.split(" ", 1)
                msg, batch_df = update_loot_and_df(temp_player, f"Essence{numeral[0]}", qty, msg, counter, batch_df)
        elif "XXX" in boss_object.boss_name:
            min_shards, max_shards = min_shards + (1 * loot_mult), max_shards + (5 * loot_mult)
        # Check gauntlet drops.
        if gauntlet:
            min_shards, max_shards = min_shards + 1, max_shards + 5
            if "XXVIII" in boss_object.boss_name and is_dropped(5):
                msg, batch_df = update_loot_and_df(temp_player, f"Lotus1", 1, msg, counter, batch_df)
                await sm.send_notification(ctx, temp_player, "Item", "Lotus1")
            elif "XXV" in boss_object.boss_name and is_dropped(5):
                msg, batch_df = update_loot_and_df(temp_player, f"Lotus9", 1, msg, counter, batch_df)
                await sm.send_notification(ctx, temp_player, "Item", "Lotus9")
        if "Pandora" in boss_object.boss_name and is_dropped(0.1):
            msg, batch_df = update_loot_and_df(temp_player, f"Pandora", 1, msg, counter, batch_df)
        if min_shards > 0:
            num_shards = random.randint(min_shards, max_shards)
            msg, batch_df = update_loot_and_df(temp_player, f"Shard", num_shards, msg, counter, batch_df)

        # Handle boss drops.
        possible_loot = boss_loot_dict[boss_object.boss_type] + boss_loot_dict['All']
        possible_loot = [loot_entry for loot_entry in possible_loot if loot_entry[0] == boss_tier or loot_entry[0] == 0]
        for _, drop_id, drop_rate in possible_loot:
            qty = sum(is_dropped(drop_rate) for attempt in range(loot_mult))
            if qty > 0:
                msg, batch_df = update_loot_and_df(temp_player, drop_id, qty, msg, counter, batch_df)
                if sm.check_rare_item(drop_id):
                    await sm.send_notification(ctx, temp_player, "Item", drop_id)
    # Update the database.
    await inventory.update_stock(None, None, None, batch=batch_df)
    return msg


def is_dropped(drop_rate):
    return True if random.randint(1, 100000) <= int(round((drop_rate * 1000))) else False


def generate_random_item(quantity=1):
    # Initialize the quantity and data.
    rewards = {}
    quantity_table = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3]
    probability_rewards = [
        [10, None, "Lotus"], [1, "DarkStar", None], [1, "LightStar", None], [1, None, "Skull"], [22, None, "Gemstone"],
        [99, None, "Essence"], [200, None, "Trove"], [100, "Catalyst", None], [50, None, "Crystal"],
        [5, None, "Skull3"], [30, None, "Skull2"], [67, None, "Skull1"],
        [200, None, "Token"], [100, None, "Jewel"], [200, None, "Summon"], [50, "Compass", None],
        [1000, "Pearl", None], [2000, "Hammer", None], [250, None, "Gem"], [2600, None, "Ore"],
        [750, None, "Fragment"], [500, "Flame1", None], [500, "Matrix", None], [400, None, "Potion"],
        [864, None, "Fae"]]
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
    lotus_rate_dict = {}
    num_coins, num_reward = 0, 0
    bounds = itemdata.trove_rewards[trove_object.item_tier]
    for _ in range(trove_stock):
        num_coins += random.randint(bounds[0], bounds[1])
        if random.randint(1, 100000) <= bounds[2] or trove_object.item_tier == 9:
            num_reward += 1
    return num_reward, num_coins, f"{trove_object.item_emoji} {trove_stock:,}x {trove_object.item_name} opened: "
