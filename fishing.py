# General imports
import discord
import random
import asyncio
from datetime import datetime as dt, timedelta

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import player
import inventory

# Trade imports
from market import get_daily_fish_items as daily_fish

# Gear/item imports
import loot

b_water, g_water, r_water = "<:bw:1275581533582790656>", "<:gw:1275581540738535474>", "<:rw:127558154948899356>"
b_fish, g_fish, r_fish = "<:bf:1275581608337870898>", "<:gf:1275581618857443338>", "<:rf:1275581625500958791>"
b_dia, g_dia, r_dia = "<:bd:1275581729163448440>", "<:gd:1275581722205097995>", "<:rd:1275581714206560400>"
b_worm, b_chest = "<:bm:1275581779067146260>", "<:bc:12755821770701893694>"
b_mine, g_mine, r_boom = "<:bb:1275582245339533382>", "<:gb:1275582236854452244>", "<:rx:1275582291820675194>"
b_star, g_star = "<:bs:1275582378282319974>", "<:gs:1275582416999940239>"
color_emojis = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]

star_mapping = {b_fish: g_fish, b_water: g_water, b_worm: g_dia, b_chest: g_dia, b_dia: g_dia,
                b_mine: g_mine, b_star: g_star}
boom_mapping = {b_fish: r_fish, b_water: r_water, b_worm: r_boom, b_chest: r_boom, b_dia: r_dia,
                b_mine: r_boom, b_star: r_boom}

# Default Datasets
directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
opposite_directions = {(1, 0): (-1, 0), (-1, 0): (1, 0), (0, 1): (0, -1), (0, -1): (0, 1),
                       (1, 1): (-1, -1), (-1, -1): (1, 1), (1, -1): (-1, 1), (-1, 1): (1, -1)}
default_data = [5, 5, 3, 6, 0, 2, 0, 2, 0, 1]
turbo_data = [8, 8, 8, 15, 3, 5, 0, 3, 1, 2]


async def go_fishing(ctx, player_obj, method="default"):
    data_value = default_data if method == "default" else turbo_data
    size_x, size_y = data_value[0], data_value[1]
    num_worms, num_chests = random.randint(data_value[2], data_value[3]), random.randint(data_value[4], data_value[5])
    num_mines, num_stars = random.randint(data_value[6], data_value[7]), random.randint(data_value[8], data_value[9])
    difference, _ = await player_obj.check_cooldown("fishing")
    boosted_rate_fish = await daily_fish(fish_only=True)
    # Handle existing cooldown.
    if difference:
        wait_time = timedelta(minutes=5)
        cooldown = wait_time - difference
        if difference <= wait_time:
            time_msg = f"You can fish again in {int(cooldown.total_seconds() / 60)} minutes."
            embed_msg = sm.easy_embed("blue", "Fish on Vacation!", time_msg)
            await ctx.send(embed=embed_msg)
            return
        await player_obj.clear_cooldown("fishing")
    if not await player_obj.spend_stamina(250 if method == "default" else 1000):
        await ctx.send("Insufficient stamina to go fishing.")
        return
    await player_obj.set_cooldown("fishing", "")
    # Initialize the fishing grid
    grid = [[b_water for _ in range(size_x)] for _ in range(size_y)]
    fish_pos = [size_x // 2, size_y // 2]
    potential_positions = [(x, y) for x in range(size_x) for y in range(size_y) if (x, y) != fish_pos]
    worm_positions = random.sample(potential_positions, num_worms)
    remaining_positions = [pos for pos in potential_positions if pos not in worm_positions]
    mine_positions = random.sample(remaining_positions, num_mines)
    remaining_positions = [pos for pos in remaining_positions if pos not in mine_positions]
    chest_positions = random.sample(remaining_positions, num_chests)
    remaining_positions = [pos for pos in remaining_positions if pos not in chest_positions]
    star_positions = random.sample(remaining_positions, num_stars)
    for x, y in worm_positions:
        grid[y][x] = b_worm
    for x, y in chest_positions:
        grid[y][x] = b_chest
    for x, y in mine_positions:
        grid[y][x] = b_mine
    for x, y in star_positions:
        grid[y][x] = b_star
    grid[fish_pos[1]][fish_pos[0]] = b_fish
    sent_msg = await ctx.send(f"{display_grid(grid)}")
    # Run the fishing animation
    moves, move_limit, worm_count, chest_count, caught_fish = 0, 50, 0, 0, {}
    last_move = None
    while moves < move_limit:
        moves += 1
        await asyncio.sleep(1)
        if grid[fish_pos[1]][fish_pos[0]] == b_fish:
            grid[fish_pos[1]][fish_pos[0]] = b_water
        valid_moves = [move for move in directions if move != opposite_directions.get(last_move)]
        move = random.choice(valid_moves)
        new_x, new_y = fish_pos[0] + move[0], fish_pos[1] + move[1]
        if (new_x < 0 or new_x >= size_x or new_y < 0 or new_y >= size_y
                or moves >= move_limit or worm_count >= num_worms):
            title = f"{player_obj.player_username} Caught {worm_count + chest_count:,} Fish!"
            if worm_count == 0 and chest_count == 0:
                title = f"{player_obj.player_username} Caught No Fish!"
            break
        fish_pos = [new_x, new_y]
        last_move, current_cell = move, grid[fish_pos[1]][fish_pos[0]]
        if current_cell == b_mine:
            title = f"{player_obj.player_username} Hit a Mine!"
            grid = [[boom_mapping.get(cell, cell) for cell in row] for row in grid]
            break
        elif current_cell == b_worm:
            worm_count += 1
            grid[fish_pos[1]][fish_pos[0]] = b_dia
        elif current_cell == b_chest:
            chest_count += 1
            grid[fish_pos[1]][fish_pos[0]] = b_dia
        elif current_cell == b_water:
            grid[fish_pos[1]][fish_pos[0]] = b_fish
        elif current_cell == b_star:
            worm_count, chest_count, total_items = num_worms, num_chests, num_worms + num_chests
            for _ in range(5):
                random_grid = generate_random_colored_grid(size_x, size_y)
                fish_grid = "\n".join("".join(row) for row in random_grid)
                await sent_msg.edit(content=f"{fish_grid}")
                await asyncio.sleep(1)
            grid = [[star_mapping.get(cell, cell) for cell in row] for row in grid]
            title = f"{player_obj.player_username} Caught All {total_items:,} Fish!"
            break
        await sent_msg.edit(content=f"{display_grid(grid)}")
    for _ in range(worm_count):
        caught_fish = await assign_fish_loot(b_worm, boosted_rate_fish, caught_fish)
    for _ in range(chest_count):
        caught_fish = await assign_fish_loot(b_chest, boosted_rate_fish, caught_fish)
    # Finalize the output
    if not caught_fish:
        await sent_msg.edit(content=f"{display_grid(grid)}")
        await ctx.send(f"**{title}**")
        return
    fish_output = ""
    for fish_id, fish_qty in caught_fish.items():
        fish = inventory.BasicItem(fish_id)
        fish_output += f"🪝 Caught: {fish.item_emoji} {fish_qty}x {fish.item_name}\n"
        if sm.check_rare_item(fish_id):
            await sm.send_notification(ctx, player_obj, "Item", fish_id)
    batch_df = sm.list_to_batch(player_obj, [(fish_id, fish_qty) for fish_id, fish_qty in caught_fish.items()])
    await inventory.update_stock(None, None, None, batch=batch_df)
    await sent_msg.edit(content=f"{display_grid(grid)}")
    await ctx.send(content=f"**{title}**\n{fish_output}")


async def assign_fish_loot(cell, boosted_rate_fish, caught_fish):
    item_qty = 1
    if random.randint(1, 1000) <= 1:
        item_id, tier = f"Lotus{random.randint(1, 10)}", 8
    elif cell == b_chest:
        reward_data = loot.generate_random_item(1)
        item_id, item_qty = reward_data[0]
        reward_object = inventory.BasicItem(item_id)
        tier = reward_object.item_tier
    else:
        tier = inventory.generate_random_tier(max_tier=8)
        item_id = "Nadir"
        if tier != 8:
            item_id = f"Fish{random.randint((tier - 1) * 4 + 1, tier * 4)}"
            if random.randint(1, 100) <= 25:
                item_id, tier = boosted_rate_fish.item_id, boosted_rate_fish.item_tier
    caught_fish[item_id] = caught_fish.get(item_id, 0) + item_qty
    return caught_fish


def display_grid(grid):
    return "\n".join("".join(row) for row in grid)


def generate_random_colored_grid(grid_x, grid_y):
    return [[random.choice(color_emojis) for _ in range(grid_x)] for _ in range(grid_y)]
