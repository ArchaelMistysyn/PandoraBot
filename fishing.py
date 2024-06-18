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

water_blue, water_green, water_red = "🟦", "🟩", "🟥"
fish_blue, fish_green, fish_red = "🐠", "🐠", "🐠"
mine_blue, mine_green = "💣", "✅"
boom_red, chest_blue = "💥", "💎"
worm_blue, worm_green = "🪱", "✅"
star_blue, star_green = "<:S1:1201563573202206910>", "✅"
color_emojis = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]

# Default Datasets
directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
opposite_directions = {(1, 0): (-1, 0), (-1, 0): (1, 0), (0, 1): (0, -1), (0, -1): (0, 1),
                       (1, 1): (-1, -1), (-1, -1): (1, 1), (1, -1): (-1, 1), (-1, 1): (1, -1)}
grid_x, grid_y, num_worms, num_chests, num_mines, num_random_stars = 10, 10, 12, 2, 2, 0


async def go_fishing(ctx, player_obj):
    colour, title = discord.Colour.blue(), f"{player_obj.player_username} Goes Fishing!"
    difference, _ = await player_obj.check_cooldown("fishing")
    boosted_rate_fish = await daily_fish(fish_only=True)
    # Handle existing cooldown.
    if difference:
        wait_time = timedelta(minutes=5)
        cooldown = wait_time - difference
        if difference <= wait_time:
            cooldown_timer = int(cooldown.total_seconds() / 60)
            time_msg = f"You can fish again in {cooldown_timer} minutes."
            embed_msg = discord.Embed(colour=colour, title="Fish On Vacation!", description=time_msg)
            await ctx.send(embed=embed_msg)
            return
        await player_obj.clear_cooldown("fishing")
    if not await player_obj.spend_stamina(250):
        await ctx.send("Insufficient stamina to go fishing.")
        return
    await player_obj.set_cooldown("fishing", "")
    # Initialize the fishing grid
    grid = [[water_blue for _ in range(grid_x)] for _ in range(grid_y)]
    fish_pos = [grid_x // 2, grid_y // 2]
    star_positions = [(0, 0), (0, grid_y - 1), (grid_x - 1, 0), (grid_x - 1, grid_y - 1)]
    no_mine_zone = [(fish_pos[0] + dx, fish_pos[1] + dy) for dx in range(-1, 2) for dy in range(-1, 2)]
    potential_positions = [(x, y) for x in range(grid_x) for y in range(grid_y)
                           if (x, y) not in no_mine_zone and (x, y) not in star_positions]
    worm_positions = random.sample(potential_positions, num_worms)
    remaining_positions = [pos for pos in potential_positions if pos not in worm_positions]
    mine_positions = random.sample(remaining_positions, num_mines)
    remaining_positions = [pos for pos in remaining_positions if pos not in mine_positions]
    chest_positions = random.sample(remaining_positions, num_chests)
    remaining_positions = [pos for pos in remaining_positions if pos not in chest_positions]
    for x, y in worm_positions:
        grid[y][x] = worm_blue
    for x, y in chest_positions:
        grid[y][x] = chest_blue
    for x, y in mine_positions:
        grid[y][x] = mine_blue
    for x, y in star_positions:
        grid[y][x] = star_blue
    grid[fish_pos[1]][fish_pos[0]] = fish_blue

    sent_msg = await ctx.send(f"**{title}**\n{display_grid(grid)}")
    # Run the fishing animation
    moves, move_limit, worm_count, caught_fish = 0, 50, 0, {}
    last_move = None
    while moves < move_limit:
        moves += 1
        await asyncio.sleep(1)
        if grid[fish_pos[1]][fish_pos[0]] == fish_blue:
            grid[fish_pos[1]][fish_pos[0]] = water_blue
        valid_moves = [move for move in directions if move != opposite_directions.get(last_move)]
        move = random.choice(valid_moves)
        new_x, new_y = fish_pos[0] + move[0], fish_pos[1] + move[1]
        if (new_x < 0 or new_x >= grid_x or new_y < 0 or new_y >= grid_y
                or moves >= move_limit or worm_count >= num_worms):
            title = f"{player_obj.player_username} Caught {worm_count:,} Fish!"
            if not caught_fish:
                colour, title = discord.Colour.brand_red(), f"{player_obj.player_username} Caught No Fish!"
            break
        fish_pos = [new_x, new_y]
        last_move = move
        if grid[fish_pos[1]][fish_pos[0]] == mine_blue:
            colour, title = discord.Colour.brand_red(), f"{player_obj.player_username} Hit a Mine!"
            grid = [[boom_red if cell in {mine_blue, worm_blue, star_blue} else water_red
                    if cell == water_blue else cell for cell in row] for row in grid]
            break
        elif grid[fish_pos[1]][fish_pos[0]] in [worm_blue, chest_blue]:
            worm_count += 1
            qty = 1
            if random.randint(1, 1000) <= 1:
                fish_id, fish_tier = f"Lotus{random.randint(1, 10)}", 8
            elif grid[fish_pos[1]][fish_pos[0]] == chest_blue:
                reward_list = loot.generate_random_item(1)
                fish_id, qty = reward_list[0]
                reward_obj = inventory.BasicItem(fish_id)
                fish_tier = reward_obj.item_tier
            else:
                fish_tier = inventory.generate_random_tier(max_tier=8)
                fish_id = "Nadir"
                if fish_tier != 8:
                    fish_id = f"Fish{random.randint((fish_tier - 1) * 4 + 1, fish_tier * 4)}"
                    if random.randint(1, 100) <= 25:
                        fish_id, fish_tier = boosted_rate_fish.item_id, boosted_rate_fish.item_tier
            caught_fish[fish_id] = caught_fish.get(fish_id, 0) + qty
            grid[fish_pos[1]][fish_pos[0]] = gli.augment_icons[fish_tier - 1]
        elif grid[fish_pos[1]][fish_pos[0]] == water_blue:
            grid[fish_pos[1]][fish_pos[0]] = fish_blue
        elif grid[fish_pos[1]][fish_pos[0]] == star_blue:
            for _ in range(5):
                random_grid = generate_random_colored_grid(grid_x, grid_y)
                fish_grid = "\n".join("".join(row) for row in random_grid)
                await sent_msg.edit(content=f"**{title}**\n{fish_grid}")
                await asyncio.sleep(1)
            grid, caught_fish = [[await star_process_cell(cell, boosted_rate_fish, caught_fish) for cell in row]
                                 for row in grid]
            colour = discord.Colour.green()
            title = f"{player_obj.player_username} Caught All {num_worms:,} Fish!"
            break
        await sent_msg.edit(content=f"**{title}**\n{display_grid(grid)}")

    # Finalize the output
    if not caught_fish:
        await sent_msg.edit(content=f"**{title}**\n{display_grid(grid)}")
        return
    fish_output = ""
    for fish_id, fish_qty in caught_fish.items():
        fish = inventory.BasicItem(fish_id)
        fish_output += f"🪝 Caught: {fish.item_emoji} {fish_qty}x {fish.item_name}\n"
        if sm.check_rare_item(fish_id):
            await sm.send_notification(ctx, player_obj, "Item", fish_id)
    batch_df = sm.list_to_batch(player_obj, [(fish_id, fish_qty) for fish_id, fish_qty in caught_fish.items()])
    await inventory.update_stock(None, None, None, batch=batch_df)
    await sent_msg.edit(content=f"**{title}**\n{display_grid(grid)}\n**Fish Caught**\n{fish_output}")


async def star_process_cell(cell, boosted_rate_fish, caught_fish):
    if cell in [worm_blue, chest_blue] + gli.augment_icons:
        item_qty = 1
        if random.randint(1, 1000) <= 1:
            item_id, tier = f"Lotus{random.randint(1, 10)}", 8
        elif cell == chest_blue:
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
        return star_green
    return water_green if cell == water_blue else cell, caught_fish


def display_grid(grid):
    return "\n".join("".join(row) for row in grid)


def generate_random_colored_grid(grid_x, grid_y):
    return [[random.choice(color_emojis) for _ in range(grid_x)] for _ in range(grid_y)]
