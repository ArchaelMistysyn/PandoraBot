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
    id_list = ["DarkStar", "LightStar", "Gemstone12", "Skull4"]
    return True if "Lotus" in item_id or item_id in id_list else False


async def send_notification(ctx_object, player_obj, notification_type, value):
    item = inventory.BasicItem(value) if notification_type == "Item" and value is not None else None
    notification_dict = {"Level": [(f"Congratulations {player_obj.player_username}",
                                   f"Reached Level: {player_obj.player_level}"), 1],
                         "Achievement": [(f"{player_obj.player_username} Unlocked", f"Achievement: {value}"), 10],
                         "Item": [(f"{player_obj.player_username} Obtained Ultra Rare",
                                  f"{item.item_name}" if item is not None else ""), 5]}
    if notification_type not in notification_dict.keys():
        return
    await inventory.update_stock(player_obj, "RoyalCoin", notification_dict[notification_type][1])
    title, message = notification_dict[notification_type][0]
    filepath = pilengine.build_notification(player_obj, message, notification_type, title, item=item)
    channels = ctx_object.guild.channels
    channel_object = discord.utils.get(channels, id=globalitems.channel_list[0])
    await ctx_object.send(file=discord.File(filepath))


def get_thumbnail_by_class(class_name):
    thumbnail_url = f"https://kyleportfolio.ca/botimages/classicon/{class_name}.png"
    return thumbnail_url


def get_gear_thumbnail(item):
    tag_dict = {"A": "Armour", "V": "Greaves", "Y": "Amulet", "R": "Ring", "G": "Wings", "C": "Crest"}
    item_tag = item.item_base_type
    if item.item_type == "W":
        item_tag = globalitems.gear_category_dict[item.item_base_type]
    else:
        item_tag = "Gem" if "D" in item.item_type else tag_dict[item.item_type]
    # Ensure image is currently available.
    if item_tag not in globalitems.availability_list:
        return None
    return f"https://kyleportfolio.ca/botimages/itemicons/{item_tag}/Frame_{item_tag}_{item.item_tier}.png"


def get_gear_tier_colours(base_tier):
    checked_tier = min(9, max(0, base_tier))
    return globalitems.tier_colors[checked_tier], globalitems.augment_icons[checked_tier - 1]


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
    if input_number < 1000:
        return f"{input_number}"
    num_digits = len(str(int(input_number)))
    idx = (num_digits - 1) // 3
    scaled_number = input_number / (10 ** (3 * idx))
    truncated_scaled_number = int(scaled_number * 100) / 100.0
    number_msg = f"{int(scaled_number)}" if scaled_number == int(scaled_number) else f"{truncated_scaled_number:.2f}"
    if idx != 0:
        number_msg = f"**{number_msg} {labels[idx]}**"
    return number_msg


def list_to_batch(player_obj, item_list):
    labels = ['player_id', 'item_id', 'item_qty']
    batch_df = pd.DataFrame(columns=labels)
    for item_id, item_qty in item_list:
        batch_df.loc[len(batch_df)] = [player_obj.player_id, item_id, item_qty]
    return batch_df

