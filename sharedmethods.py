# General import
import discord
from discord.utils import get
import pandas as pd

# Data imports
import globalitems

# Core imports
import player
import inventory
import pilengine


async def check_registration(ctx):
    if not any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
        return None
    command_user = player.get_player_by_discord(ctx.author.id)
    title, description = "Unregistered", "Please register using /register to play."
    register_embed = discord.Embed(colour=discord.Colour.dark_teal(), title=title, description=description)
    if command_user is None:
        await ctx.send(embed=register_embed)
        return None
    await ctx.defer()
    return command_user


async def send_notification(ctx_object, player_obj, notification_type, value):
    channels = ctx_object.guild.channels
    channel_object = discord.utils.get(channels, id=globalitems.channel_list[0])
    match notification_type:
        case "Level":
            message = f"{player_obj.player_username} - Level Up: Level {player_obj.player_lvl}!"
        case "Achievement":
            message = f"{player_obj.player_username} - Achievement Acquired: {value}!"
        case "Item":
            item = inventory.BasicItem(value)
            message = f"{player_obj.player_username} - Ultra Rare Item Acquired: {item.item_name}"
        case _:
            pass
    await channel_object.send(message)


def get_thumbnail_by_class(class_name):
    thumbnail_url = f"https://kyleportfolio.ca/botimages/classicon/{class_name}.png"
    return thumbnail_url


def get_gear_thumbnail(item):
    item_tag = item.item_base_type
    if item.item_tier <= 4 and item.item_type == "W":
        item_tag = globalitems.gear_category_dict[item.item_base_type]
    elif item.item_type == "A":
        item_tag = "Armour"
    elif item.item_type == "V":
        item_tag = "Vambraces"
    elif item.item_type == "Y":
        item_tag = "Amulet"
    elif item.item_type == "G":
        item_tag = "Wings"
    elif item.item_type == "C":
        item_tag = "Crest"
    elif "D" in item.item_type:
        item_tag = "Jewel"
    # Ensure image is currently available.
    if item_tag not in globalitems.availability_list:
        return None
    return f"https://kyleportfolio.ca/botimages/itemicons/{item_tag}/Framed_{item_tag}_{item.item_tier}.png"


def get_gear_tier_colours(base_tier):
    return globalitems.tier_colors[base_tier], globalitems.augment_icons[min(8, max(0, base_tier - 1))]


def reset_all_cooldowns():
    pandora_db = mydb.start_engine()
    raw_query = "DELETE FROM CommandCooldowns"
    pandora_db.run_query(raw_query)
    pandora_db.close_engine()


def display_hp(current_hp, max_hp):
    if current_hp > max_hp:
        current_hp = max_hp
    elif current_hp < 0:
        current_hp = 0
    current_hp_converted = number_conversion(current_hp)
    max_hp_converted = number_conversion(max_hp)
    hp_msg = f"{current_hp_converted} / {max_hp_converted}"
    return hp_msg


def display_stars(num_stars):
    stars_msg = ""
    for x in range(num_stars):
        stars_msg += globalitems.star_icon[min(8, num_stars)]
    for y in range(max(0, (8 - num_stars))):
        stars_msg += globalitems.star_icon[0]
    return stars_msg


def generate_ramping_reward(success_rate, decay_rate, total_steps):
    current_step, decay_point = 0, 14
    while current_step < (total_steps - 1):
        if random.randint(1, 100) <= success_rate:
            current_step += 1
            if current_step >= decay_point:
                success_rate -= (decay_rate * ((current_step + 1) - decay_rate))
        else:
            return current_step
    return current_step


def get_stock_msg(item_object, quantity, cost=1):
    stock_details = f"{item_object.item_emoji} {quantity}x {item_object.item_name}"
    if quantity < cost:
        return f'Insufficient Stock: {stock_details}'
    return f'Remaining Stock: {stock_details}'


def number_conversion(input_number):
    labels = ['', 'K', 'M', 'B', 'T', 'Q', 'Qt',
              'Z', 'Z+', 'Z++', 'Z+++', 'ZZ', 'ZZ+', 'ZZ++', 'ZZ+++',
              'ZZZ', 'ZZZ+', 'ZZZ++', 'ZZZ+++']
    num_digits = len(str(int(input_number)))
    idx = max(0, (num_digits - 1) // 3)
    input_str = str(input_number)
    integer_digits = (num_digits - 1) % 3 + 1
    integer_part = input_str[:integer_digits]
    decimal_part = input_str[integer_digits:][:2]
    if decimal_part == "00":
        decimal_part = ""
    number_msg = f"{integer_part}.{decimal_part}" if decimal_part else f"{integer_part}"
    if idx != 0:
        number_msg = f"**{number_msg} {labels[idx]}**"
    return number_msg


def list_to_batch(player_obj, item_list):
    labels = ['player_id', 'item_id', 'item_qty']
    batch_df = pd.DataFrame(columns=labels)
    for item_id, item_qty in item_list:
        batch_df.loc[len(batch_df)] = [player_obj.player_id, item_id, item_qty]
    return batch_df

