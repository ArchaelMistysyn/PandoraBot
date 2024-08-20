# General imports
import discord
from discord.utils import get
import pandas as pd
import random
import re
from decimal import Decimal, getcontext

# Data imports
import globalitems as gli

# Core imports
import player
import inventory
import pilengine

ultra_id_list = ["Skull3", "EssenceXXX"]
ultra_id_list += [f"Lotus{x}" for x in range(1, 10)]
uber_id_list = ["Gemstone11", "DarkStar", "LightStar", "Nadir", "Lotus10"]
ultimate_id_list = ["Skull4", "Nephilim", "Sacred", "Ruler", "Pandora", "Lotus11"]
u_rarity_id_list = ultra_id_list + uber_id_list + ultimate_id_list
embed_colour_dict = {
    "red": discord.Colour(0xFF0000), "blue": discord.Colour(0x0000FF), "green": discord.Colour(0x00FF00),
    "purple": discord.Colour(0x800080), "orange": discord.Colour(0xFFA500), "gold": discord.Colour(0xFFD700),
    "magenta": discord.Colour(0xFF00FF), "teal": discord.Colour(0x008080), "yellow": discord.Colour(0xFFFF00),
    "cyan": discord.Colour(0x00FFFF), "pink": discord.Colour(0xFFC0CB), "brown": discord.Colour(0xA52A2A),
    "lime": discord.Colour(0x00FF00), "navy": discord.Colour(0x000080), "maroon": discord.Colour(0x800000),
    "sky_blue": discord.Colour(0x87CEEB), "indigo": discord.Colour(0x4B0082), "violet": discord.Colour(0xEE82EE),
    "turquoise": discord.Colour(0x40E0D0), "gray": discord.Colour(0x808080),
    "silver": discord.Colour(0xC0C0C0), "black": discord.Colour(0x000000), "white": discord.Colour(0xFFFFFF),
    1: 0x43B581, 2: 0x3498DB, 3: 0x9B59B6, 4: 0xF1C40F, 5: 0xCC0000,
    6: 0xE91E63, 7: 0xFFFFFF, 8: 0x000000, 9: 0x000000}


async def check_registration(ctx):
    if ctx.guild.id not in gli.servers.keys():
        await ctx.send("Server not active")
        return
    if ctx.channel.id not in gli.servers[int(ctx.guild.id)][0]:
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
    return True if item_id in u_rarity_id_list else False


async def send_notification(ctx_object, player_obj, notice_type, value):
    rarity = "Ultimate Rare" if value in ultimate_id_list else "Uber Rare" if value in uber_id_list else "Ultra Rare"
    item = inventory.BasicItem(value) if notice_type == "Item" and value is not None else None
    notification_dict = {
        "Level": [(f"Congratulations {player_obj.player_username}", f"Reached Level: {player_obj.player_level}"), 1],
        "Achievement": [(f"{player_obj.player_username} Unlocked", f"Achievement: {value}"), 20],
        "Item": [(f"{player_obj.player_username} Obtained {rarity}", f"{item.item_name}" if item is not None else ""),
                 5],
        "Sovereign": [(f"{player_obj.player_username} Obtained Sovereign Item", value), 10],
        "Sacred": [(f"{player_obj.player_username} Obtained Sacred Item", value), 100]}
    if notice_type not in notification_dict.keys():
        return
    num_coins = 50 if rarity == "Ultimate Rare" else 25 if rarity == "Uber Rare" else notification_dict[notice_type][1]
    await inventory.update_stock(player_obj, "RoyalCoin", num_coins)
    title, message = notification_dict[notice_type][0]
    filepath = await pilengine.build_notification(player_obj, message, notice_type, title, item, rarity)
    channels = ctx_object.guild.channels
    channel_object = discord.utils.get(channels, id=gli.servers[int(ctx_object.guild.id)][1])
    await ctx_object.send(file=discord.File(filepath))


def get_thumbnail_by_class(class_name):
    thumbnail_url = f"https://kyleportfolio.ca/botimages/classicon/{class_name}.png"
    return thumbnail_url


def get_gear_thumbnail(item):
    tag_dict = {"A": "Armour", "V": "Greaves", "Y": "Amulet", "R": "Ring", "G": "Wings", "C": "Crest"}
    folder = item_tag = item.item_base_type
    sub_folder, element = "", ""
    if item.item_base_type in gli.sovereign_item_list:
        folder = "Sovereign"
    elif item.item_type not in ["W", "R"]:
        item_tag = "Gem" if "D" in item.item_type else tag_dict[item.item_type]
        folder = item_tag
    elif item.item_type == "R":
        folder, sub_folder = "Ring", f"{gli.ring_item_type[item.item_tier - 1]}/"
        if item.item_tier in [4, 5]:
            item_tag, element = gli.ring_item_type[item.item_tier - 1], item.item_elements.index(1)
        else:
            return None
    # Ensure image is currently available.
    if item_tag not in gli.availability_list and item_tag not in gli.ring_item_type and item_tag not in gli.available_sovereign:
        return None
    new_tag = item_tag.replace(' ', '_')
    return f"{gli.web_url}Gear_Icon/{folder}/{sub_folder}Frame_{new_tag}{element}_{item.item_tier}.png"


def get_gear_tier_colours(base_tier):
    checked_tier = min(9, max(0, base_tier))
    return gli.tier_colors[checked_tier], gli.augment_icons[checked_tier - 1]


async def reset_all_cooldowns():
    raw_query = "DELETE FROM CommandCooldowns"
    await rqy(raw_query)


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
    for x in range(min(9, num_stars)):
        stars_msg += gli.star_icon[num_stars]
    for y in range(max(0, (8 - num_stars))):
        stars_msg += gli.star_icon[0]
    return stars_msg


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
    scaled_number = Decimal(input_number) / (10 ** (3 * idx))
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


def hide_text(msg, method="Shrouded"):
    if method == "Clear":
        return

    def enigma_transform(match):
        char = match.group(0)
        if method == "Enigma":
            return '?' if char.isalnum() else char
        elif method == "Shrouded":
            return '?' if char.isalnum() and random.random() > 0.5 else char
        return char

    parts = re.split(r'(<[^>]+>)', msg)
    adjusted = [part if part.startswith('<') and part.endswith('>') else re.sub(r'\w', enigma_transform, part)
                for part in parts]
    return ''.join(adjusted)


async def title_box(title_msg):
    return await pilengine.build_title_box(title_msg)


async def message_box(player_obj, message, header="", boxtype="default"):
    return await pilengine.build_message_box(player_obj, message, header, boxtype)


def easy_embed(colour, title, description):
    colour = colour.lower() if isinstance(colour, str) else colour
    colour = embed_colour_dict[colour] if colour in embed_colour_dict else discord.Colour.red()
    return discord.Embed(colour=colour, title=title, description=description)


async def cost_embed(player_obj, cost_items, cost_qty):
    cost_msg = ""
    if not isinstance(cost_items, list):
        item_stock = await inventory.check_stock(player_obj, cost_items)
        cost_msg = f"{cost_items.item_emoji} {cost_items.item_name}: {item_stock:,} / {cost_qty:,}\n"
        return cost_msg, item_stock >= cost_qty
    can_afford = True
    for item, qty in zip(cost_items, cost_qty):
        item_stock = await inventory.check_stock(player_obj, item.item_id)
        cost_msg += f"{item.item_emoji} {item.item_name}: {item_stock:,} / {qty:,}\n"
        can_afford = item_stock >= qty and can_afford
    return cost_msg, can_afford
