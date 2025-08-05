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
import menus

# Trade imports
from market import get_daily_fish_items as daily_fish

# Gear/item imports
import loot


class FishView(discord.ui.View):
    def __init__(self, ctx, player_obj, fish_level):
        super().__init__(timeout=None)
        self.ctx, self.player_obj, self.fish_level = ctx, player_obj, fish_level
        fishing_labels = {"Basic Fish": 0, "Quick Fish": 2, "Turbo Fish": 4, "Ultimate Fish": 6, "Omega Fish": 8}
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                required_level = fishing_labels[child.label]
                if self.fish_level < required_level:
                    child.disabled = True
                    child.style = discord.ButtonStyle.secondary

    @discord.ui.button(label="Basic Fish", style=discord.ButtonStyle.success, emoji="🐟")
    async def default_fish(self, interaction: discord.Interaction, button: discord.Button):
        await self.fishing(interaction, "fish", 250)

    @discord.ui.button(label="Quick Fish", style=discord.ButtonStyle.blurple, emoji="🐟")
    async def quick_fish(self, interaction: discord.Interaction, button: discord.Button):
        await self.fishing(interaction, "quickfish", 500)

    @discord.ui.button(label="Turbo Fish", style=discord.ButtonStyle.blurple, emoji="🐟")
    async def turbo_fish(self, interaction: discord.Interaction, button: discord.Button):
        await self.fishing(interaction, "turbofishing", 1000)

    @discord.ui.button(label="Ultimate Fish", style=discord.ButtonStyle.blurple, emoji="🐟")
    async def ultimate_fish(self, interaction: discord.Interaction, button: discord.Button):
        await self.fishing(interaction, "ultimatefishing", 2500)

    @discord.ui.button(label="Omega Fish", style=discord.ButtonStyle.red, emoji="🐟")
    async def omega_fish(self, interaction: discord.Interaction, button: discord.Button):
        await self.fishing(interaction, "omegafishing", 5000)

    async def fishing(self, interaction, fish_method, stamina_cost):
        if interaction.user.id != self.player.discord_id:
            return
        await self.player.reload_player()
        if self.player_obj.player_stamina < stamina_cost:
            stamina_menu = menus.StaminaView(self.player_obj)
            stamina_embed = await self.player_obj.create_stamina_embed()
            await interaction.response.edit_message(embed=stamina_embed, view=stamina_menu)
            return
        await interaction.response.edit_message(embed=None, view=None)
        await go_fishing(self.ctx, self.player_obj, method=fish_method)


fish_levels = ["Fishless Loser", "Fish Owner", "Fishing Adept", "Fishing Pro", "Fishing Master",
               "Fishing Legend", "Fish King", "Fish Wizard", "God of Fish", "Progenitor of Fish", "Bathyal's Chosen"]


async def check_fish_level(player_obj):
    fish_points = await player_obj.check_misc_data("fish_points")
    total_fish_points = int(fish_points)
    if total_fish_points < 1:
        return 0, 0, fish_levels[0]
    fish_level = len(str(total_fish_points)) - 1
    fish_level = min(fish_level, len(fish_levels) - 1)
    return total_fish_points, fish_level, fish_levels[fish_level]


async def update_fish_points(player_obj, points, overwrite=False):
    await player_obj.update_misc_data("fish_points", points, overwrite_value=overwrite)


b_water, g_water, r_water = "<:bw:1275581533582790656>", "<:gw:1275581540738535474>", "<:rw:1275581594848989356>"
b_fish, g_fish, r_fish = "<:bf:1275581608337870898>", "<:gf:1275581618857443338>", "<:rf:1275581625500958791>"
b_dia, g_dia, r_dia = "<:bd:1275581714206560400>", "<:gd:1275581722205097995>", "<:rd:1275581729163448440>"
b_worm, b_chest = "<:bm:1275581779067146260>", "<:bc:1275582170701893694>"
b_mine, g_mine, r_boom = "<:bb:1275582230160474194>", "<:gb:1275582236854452244>", "<:rx:1275582291820675194>"
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
fishing_sets = {"fish": [5, 5, 3, 6, 0, 2, 0, 2, 0, 1], "quickfishing": [5, 5, 3, 6, 0, 2, 0, 2, 0, 1],
                "turbofishing": [5, 5, 3, 6, 0, 2, 0, 2, 0, 1], "ultimatefishing": [8, 8, 8, 15, 3, 5, 0, 3, 1, 2],
                "omegafishing": [8, 8, 8, 15, 3, 5, 0, 3, 1, 2]}
fishing_stamina = {"fish": 250, "quickfishing": 500, "turbofishing": 1000, "ultimatefishing": 2500, "omegafishing": 5000}


async def go_fishing(ctx, player_obj, method="fish"):
    data_value = fishing_sets[method]
    size_x, size_y = data_value[0], data_value[1]
    num_worms, num_chests = random.randint(data_value[2], data_value[3]), random.randint(data_value[4], data_value[5])
    num_mines, num_stars = random.randint(data_value[6], data_value[7]), random.randint(data_value[8], data_value[9])
    difference, _ = await player_obj.check_cooldown("fishing")
    boosted_rate_fish = await daily_fish(fish_only=True)
    _, fish_level, _ = await check_fish_level(player_obj)
    fish_cooldown = 22 - fish_level
    # Handle existing cooldown.
    if difference:
        wait_time = timedelta(minutes=fish_cooldown)
        cooldown = wait_time - difference
        if difference <= wait_time:
            time_msg = f"You can fish again in {int(cooldown.total_seconds() / 60)} minutes."
            embed_msg = sm.easy_embed("blue", "Fish on Vacation!", time_msg)
            await ctx.send(embed=embed_msg)
            return
        await player_obj.clear_cooldown("fishing")
    if not await player_obj.spend_stamina(fishing_stamina[method]):
        embed_msg = await player_obj.create_stamina_embed()
        stamina_view = menus.StaminaView(player_obj)
        await ctx.send(embed=embed_msg, view=stamina_view)
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
    _, fish_level, _ = await check_fish_level(player_obj)
    fishing_bonus = fish_level + 1
    total_points = 0
    for fish_id, fish_qty in caught_fish.items():
        fish = inventory.BasicItem(fish_id)
        is_fish = fish_id.startswith("Fish")
        base_points = (fish.item_tier + gli.fishing_modes[method]) * fish_qty
        if is_fish:
            base_points *= 2
        base_points *= fishing_bonus
        total_points += base_points
        fish_output += f"🪝 Caught: {fish.item_emoji} {fish_qty}x {fish.item_name}\n"
        if sm.check_rare_item(fish_id):
            await sm.send_notification(ctx, player_obj, "Item", fish_id)
    await update_fish_points(player_obj, total_points)
    fish_points, fish_level, fish_title = await check_fish_level(player_obj)
    fish_pts_max = 10 ** (fish_level + 1) if fish_level + 1 < len(fish_levels) else "MAX"
    fish_output += f"{fish_title}\n🎣 Fish EXP: {fish_points} / {fish_pts_max}\n"
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
