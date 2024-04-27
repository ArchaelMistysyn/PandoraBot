# General imports
import discord
from discord.utils import get
import pandas as pd
import random

# Data imports
import globalitems

# Core imports
import player
import inventory
import pilengine


async def check_registration(ctx):
    if not any(ctx.channel.id in sl for sl in globalitems.global_server_channels):
        await ctx.send("This command may not be used in this channel.")
        return None
    command_user = await player.get_player_by_discord(ctx.author.id)
    title, description = "Unregistered", "Please register using /register to play."
    register_embed = discord.Embed(colour=discord.Colour.dark_teal(), title=title, description=description)
    if command_user is None:
        await ctx.send(embed=register_embed)
        return None
    return command_user


async def check_click(interaction, player_obj, new_embed, new_view):
    if interaction.user.id != player_obj.discord_id:
        return True
    if new_embed is not None:
        await interaction.response.edit_message(embed=new_embed, view=new_view)
        return True
    return False


def check_rare_item(item_id):
    id_list = ["DarkStar", "LightStar", "Gemstone12"]
    return True if "Lotus" in item_id or item_id in id_list else False


async def send_notification(ctx_object, player_obj, notification_type, value):
    item = None
    match notification_type:
        case "Level":
            message = f"Level Up: {player_obj.player_level}"
        case "Achievement":
            message = f"Achievement Acquired: {value}"
        case "Item":
            item = inventory.BasicItem(value)
            message = f"Ultra Rare Item Acquired: {item.item_name}"
        case _:
            pass
    filepath = pilengine.build_notification(player_obj, message, notification_type, item=item)
    channels = ctx_object.guild.channels
    channel_object = discord.utils.get(channels, id=globalitems.channel_list[0])
    await ctx_object.send(file=discord.File(filepath))


def get_thumbnail_by_class(class_name):
    thumbnail_url = f"https://kyleportfolio.ca/botimages/classicon/{class_name}.png"
    return thumbnail_url


def get_gear_thumbnail(item):
    tag_dict = {"A": "Armour", "V": "Vambraces", "Y": "Amulet", "R": "Ring", "G": "Wings", "C": "Crest"}
    item_tag = item.item_base_type
    if item.item_type == "W":
        item_tag = globalitems.gear_category_dict[item.item_base_type]
    else:
        item_tag = "Jewel" if "D" in item.item_type else tag_dict[item.item_type]
    # Ensure image is currently available.
    if item_tag not in globalitems.availability_list:
        return None
    return f"https://kyleportfolio.ca/botimages/itemicons/{item_tag}/Framed_{item_tag}_{item.item_tier}.png"


def get_gear_tier_colours(base_tier):
    return globalitems.tier_colors[base_tier], globalitems.augment_icons[min(8, max(0, base_tier - 1))]


def reset_all_cooldowns():
    
    raw_query = "DELETE FROM CommandCooldowns"
    rq(raw_query)
    


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


def reward_message(item_obj, qty=1):
    return f"{item_obj.item_emoji} {qty:,}x {item_obj.item_name}"


def get_stock_msg(item_object, quantity, cost=1):
    stock_details = reward_message(item_object, quantity)
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

