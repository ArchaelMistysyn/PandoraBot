# General imports
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter
import requests
import os
from ftplib import FTP
import aiohttp
from io import BytesIO

# Data imports
import globalitems as gli
import inventory
import itemdata
import sharedmethods as sm

# Core imports
import player

web_url = f"https://PandoraPortal.ca"
generic_frame_url = f"{web_url}/botimages/iconframes/Iconframe.png"
rank_colour = ["Green", "Blue", "Purple", "Gold", "Red", "Magenta"]
profile_url = f"{web_url}/botimages/profilecards/"
card_url = "cardBG/Rankcard_card_"
exp_url = "expbar/Rankcard_Expbar_"
wing_gem_url = "wing_gem/Rankcard_wing_"
metal_url = "metal/Rankcard_metal_"
rank_card_url_list = [f"{profile_url}{card_url}Teal.png", f"{profile_url}{card_url}Emerald.png",
                      f"{profile_url}{card_url}Azure.png", f"{profile_url}{card_url}Amethyst.png",
                      f"{profile_url}{card_url}Cobalt.png", f"{profile_url}{card_url}Rainbow.png",
                      f"{profile_url}{card_url}Ruby.png", f"{profile_url}{card_url}Pink.png"]
exp_bar_url_list = [f"{profile_url}{exp_url}Teal.png", f"{profile_url}{exp_url}Emerald.png",
                    f"{profile_url}{exp_url}Cobalt.png", f"{profile_url}{exp_url}Amethyst.png",
                    f"{profile_url}{exp_url}Azure.png", f"{profile_url}{exp_url}Rainbow.png",
                    f"{profile_url}{exp_url}Ruby.png", f"{profile_url}{exp_url}Pink.png"]
wing_gem_url_list = [f"{profile_url}{wing_gem_url}Teal.png", f"{profile_url}{wing_gem_url}Emerald.png",
                     f"{profile_url}{wing_gem_url}Cobalt.png", f"{profile_url}{wing_gem_url}Amethyst.png",
                     f"{profile_url}{wing_gem_url}Azure.png", f"{profile_url}{wing_gem_url}Rainbow.png",
                     f"{profile_url}{wing_gem_url}Ruby.png", f"{profile_url}{wing_gem_url}Pink.png"]
metal_url_list = [f"{profile_url}{metal_url}Bronze.png", f"{profile_url}{metal_url}Bronze.png",
                  f"{profile_url}{metal_url}Silver.png", f"{profile_url}{metal_url}SilverPlus.png",
                  f"{profile_url}{metal_url}Gold.png", f"{profile_url}{metal_url}GoldPlus.png",
                  f"{profile_url}{metal_url}Stygian.png"]
url_dict = {'cardBG': rank_card_url_list, 'metal': metal_url_list, 'wing': wing_gem_url_list,
            'exp_bar': exp_bar_url_list, 'frame_icon': gli.frame_icon_list}
url_index_dict = {'cardBG': 0, 'metal': 1, 'wing': 2, 'exp_bar': 3, 'frame_icon': 4}
# Load Resources
font_base_url = f"{web_url}//botimages/profilecards/fonts/"
my_font_url = "PandoraDiamond/PandoraDiamond.ttf"


# COLOURS
def hex_to_rgba(hex_value, alpha=255):
    red = (hex_value >> 16) & 0xFF
    green = (hex_value >> 8) & 0xFF
    blue = hex_value & 0xFF
    return red, green, blue


GoldColour = hex_to_rgba(0xD4931A)
CyanColour = hex_to_rgba(0x00FFFF)
BrandBlue = hex_to_rgba(0x007BFF)
BrandPurple = hex_to_rgba(0x780AC3)
BrandRed = hex_to_rgba(0xFF0000)

# Web Data for FTP Login
web_data = None
with open("web_login_data.txt", 'r') as data_file:
    for line in data_file:
        web_data = line.split(";")


class RankCard:
    def __init__(self, user, achievement_list):
        self.user, self.echelon = user, user.player_echelon
        self.cardBG, self.metal, self.wing, self.exp_bar, self.frame_icon = "", "", "", "", ""
        scaled_echelon = (self.echelon // 2)
        loc = [scaled_echelon for _ in range(6)]
        self.fill_colour = [BrandBlue, "black"]
        if "Exclusive Title Holder" in achievement_list:
            self.fill_colour = [BrandRed, "black"]
            loc = [6, 6, 6, 6, 6] if scaled_echelon < 5 else [5, 6, 5, 5, 6]
        elif "Subscriber - Star Supporter" in achievement_list or "Subscriber - Crowned Supporter" in achievement_list:
            loc = [7, loc[1], 7, 7, 5] if scaled_echelon < 5 else [5, 5, 5, 5, 5]
        for attr, url_list in url_dict.items():
            if attr != 'frame_icon':
                index = loc[url_index_dict[attr]]
                setattr(self, attr, url_list[index])
        self.frame_icon = gli.frame_icon_list[loc[4]].replace("[EXT]", gli.frame_extension[1])
        self.class_icon = sm.get_thumbnail_by_class(self.user.player_class)
        self.fill_percent = round(self.user.player_exp / player.get_max_exp(self.user.player_level), 2)


async def get_player_profile(player_obj, achievement_list):
    rank_card = RankCard(player_obj, achievement_list)
    temp_path = f'{gli.image_path}profilecard/'
    cardBG = Image.open(requests.get(rank_card.cardBG, stream=True).raw)
    metal = Image.open(requests.get(rank_card.metal, stream=True).raw)
    wing = Image.open(requests.get(rank_card.wing, stream=True).raw)
    rank_icon_frame = Image.open(requests.get(rank_card.frame_icon, stream=True).raw)
    class_icon_frame = Image.open(requests.get(generic_frame_url, stream=True).raw)
    class_icon = Image.open(requests.get(rank_card.class_icon, stream=True).raw)
    exp_bar_image = Image.open(requests.get(rank_card.exp_bar, stream=True).raw)
    font_file_small = requests.get((font_base_url + my_font_url), stream=True).raw
    font_file_big = requests.get((font_base_url + my_font_url), stream=True).raw
    result = Image.new("RGBA", cardBG.size)
    result.paste(cardBG, (0, 0), cardBG)
    result.paste(metal, (0, 0), metal)
    result.paste(wing, (0, 0), wing)
    title_font = ImageFont.truetype(font_file_small, 46)
    level_font = ImageFont.truetype(font_file_big, 48)
    fill_colour = rank_card.fill_colour
    # Username
    title_text = player_obj.player_username
    image_editable = ImageDraw.Draw(result)
    text_bbox = image_editable.textbbox((0, 0), title_text, font=title_font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    center_x, center_y = 326, 242
    position_x, position_y = center_x - text_width // 2, center_y - text_height // 2
    image_editable.text((position_x + 2, position_y + 2), title_text, fill=fill_colour[1], font=title_font)
    image_editable.text((position_x, position_y), title_text, fill=fill_colour[0], font=title_font)
    # Class Icon
    new_size = (68, 68)
    class_icon = class_icon.resize(new_size)
    result.paste(class_icon, (130, 214), mask=class_icon)
    # Class Icon Frame
    new_size = (68, 68)
    class_icon_frame = class_icon_frame.resize(new_size)
    result.paste(class_icon_frame, (131, 214), mask=class_icon_frame)
    # Rank Icon Frame
    new_size = (125, 125)
    rank_icon_frame = rank_icon_frame.resize(new_size)
    result.paste(rank_icon_frame, (627, 215), mask=rank_icon_frame)
    # Exp Bar
    exp_bar_start = 197
    exp_bar_end = 750
    exp_bar_result = await generate_exp_bar(exp_bar_image, exp_bar_start, exp_bar_end, rank_card.fill_percent)
    result.paste(exp_bar_result, (exp_bar_start, 0), mask=exp_bar_result)
    # Level and Exp Text
    image_editable = ImageDraw.Draw(result)
    level_text = f"{player_obj.player_level}"
    text_position = (688, 270)
    text_bbox = image_editable.textbbox((0, 0), level_text, font=level_font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    center_x, center_y = text_position[0] - text_width // 2, text_position[1] - text_height // 2
    image_editable.text((center_x + 2, center_y + 2), level_text, font=level_font, fill=fill_colour[1])
    image_editable.text((center_x, center_y), level_text, font=level_font, fill=fill_colour[0])
    # Save File
    file_path = f"{temp_path}ProfileCard{player_obj.player_id}.png"
    result.save(file_path)
    return file_path


async def generate_exp_bar(exp_bar_image, exp_bar_start, exp_bar_end, fill_percent):
    card_height = exp_bar_image.height
    exp_width = int((exp_bar_end - exp_bar_start) * fill_percent)
    exp_bar_cropped = exp_bar_image.crop((exp_bar_start, 0, exp_bar_start + exp_width, card_height))
    exp_bar_result = Image.new("RGBA", exp_bar_cropped.size)
    exp_bar_result.paste(exp_bar_cropped, (0, 0), mask=exp_bar_cropped)
    return exp_bar_result


async def generate_and_combine_gear(item_type, start_tier=1, end_tier=8, element=""):
    # Ensure image is currently available.
    if item_type not in item_type not in gli.sovereign_item_list:
        return 0
    ftp = await create_ftp_connection(web_data[0], web_data[1], web_data[2])
    folder, sub_dir = item_type, ""
    if item_type in gli.sovereign_item_list:
        folder = "Sovereign"
    async with aiohttp.ClientSession() as session:
        for item_tier in range(start_tier, end_tier + 1):
            # Handle the urls and paths.
            frame_url = gli.frame_icon_list[item_tier - 1]
            frame_url = frame_url.replace("[EXT]", gli.frame_extension[0])
            icon_url = f"{web_url}/botimages/Gear_Icon/{folder}/{item_type.replace(' ', '_')}"
            if item_type not in gli.sovereign_item_list and item_type not in gli.fabled_ringtypes:
                icon_url = f"{icon_url}{item_tier}.png"
            else:
                icon_url = f"{icon_url}.png"
            if item_tier == 9 and item_type not in gli.sovereign_item_list:
                icon_url = f"{web_url}/botimages/Gear_Icon/{folder}/{item_type.replace(' ', '_')}8.png"
            elif item_tier == 7 and item_type in gli.fabled_ringtypes:
                folder, sub_dir = "Ring", "Fabled_Ring"
                icon_url = f"{web_url}/botimages/Gear_Icon/{folder}/{sub_dir}/{item_type.replace(' ', '_')}.png"
            elif item_type == "Ring" or item_type in gli.ring_item_type:
                item_type = gli.ring_item_type[item_tier - 1]
                sub_dir = f"{item_type}/"
                icon_url = f"{web_url}/botimages/Gear_Icon/{folder}/{sub_dir}{item_type}{element}.png"
            output_dir = f"{gli.image_path}Gear_Icon/{folder}/{sub_dir}"
            file_name = f"Frame_{item_type.replace(' ', '_')}{element}_{item_tier}.png"
            file_path = f"{output_dir}{file_name}"
            frame, icon = await fetch_image(session, frame_url), await fetch_image(session, icon_url)
            if icon is None:
                print(f"Failed to load icon for {item_type} at tier {item_tier}")
                continue
            # Handle Pact Variants
            if item_type == "Pact":
                # Skip pacts for now doesn't need to be redone, reduce load.
                return 0
            if item_type == "Pact":
                for variant in ["Wrath", "Sloth", "Greed", "Envy", "Pride", "Lust", "Gluttony"]:
                    variant_url = f"{web_url}/botimages/Gear_Icon/Pact_Variants/{variant}.png"
                    variant_img = Image.open(requests.get(variant_url, stream=True).raw)
                    output_dir = f'{gli.image_path}Gear_Icon/{item_type}/'
                    file_name = f"Frame_{item_type}_{item_tier}_{variant}.png"
                    remote_dir = f"/botimages/Gear_Icon/{item_type}/"
                    result = Image.new("RGBA", (106, 106))
                    result.paste(frame, (0, 0), frame)
                    result.paste(icon, (17, 16), icon)
                    result.paste(variant_img, (17, 16), variant_img)
                    result.save(file_path, format="PNG")
                    await upload_file_to_ftp(ftp, file_path, remote_dir, file_name)
            # Construct the new image
            result = Image.new("RGBA", (106, 106))
            result.paste(frame, (0, 0), frame)
            result.paste(icon, (17, 16), icon)
            result.save(file_path, format="PNG")
            # Upload the file.
            remote_dir = f"/botimages/Gear_Icon/{folder}/{sub_dir}"
            await upload_file_to_ftp(ftp, file_path, remote_dir, file_name)
    ftp.quit()
    return end_tier + 1 - start_tier


async def generate_and_combine_images():
    count = 0
    ftp = await create_ftp_connection(web_data[0], web_data[1], web_data[2])
    async with (aiohttp.ClientSession() as session):
        for item_id in itemdata.itemdata_dict.keys():
            # Ensure image is currently available.
            temp_item = inventory.BasicItem(item_id)
            if temp_item.item_category not in gli.availability_list_nongear:
                continue
            set_items = []
            if temp_item.item_category == "Misc" and item_id not in set_items:
                continue
            count += 1
            # Handle the urls and paths.
            frame_url = gli.frame_icon_list[temp_item.item_tier - 1]
            frame_url = frame_url.replace("[EXT]", gli.frame_extension[0])
            icon_url = f"{web_url}/botimages/NonGear_Icon/{temp_item.item_category}/{item_id}.png"
            output_dir, file_name = f'{gli.image_path}NonGear_Icon/{temp_item.item_category}/', f"Frame_{item_id}.png"
            if "Essence" in item_id:
                # Could be improved since this is tier based, but no point.
                icon_url = f"{web_url}/botimages/NonGear_Icon/{temp_item.item_category}/Essence{temp_item.item_tier}.png"
                file_name = f"Frame_Essence_{temp_item.item_tier}.png"
            file_path = f"{output_dir}{file_name}"
            frame, icon = await fetch_image(session, frame_url), await fetch_image(session, icon_url)
            # Construct the new image
            # result = pixel_blend(frame, icon)
            result = Image.new("RGBA", (106, 106))
            result.paste(frame, (0, 0), frame)
            result.paste(icon, (17, 16), icon)
            result.save(file_path, format="PNG")
            # Upload the file.
            remote_dir = f"/botimages/NonGear_Icon/{temp_item.item_category}/"
            await upload_file_to_ftp(ftp, file_path, remote_dir, file_name)
    ftp.quit()
    return count


def pixel_blend(image_1, image_2):
    result_img = image_1.copy()
    size_x, size_y = image_2.size
    for x in range(size_x):
        for y in range(size_y):
            image_pixel = image_2.getpixel((x, y))
            if image_pixel[3] > 0:  # If the pixel is not fully transparent
                result_img.putpixel((17 + x, 16 + y), image_pixel)
    return result_img


async def fetch_image(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        data = await response.read()
        if not data:
            print(f"Failed to load image data from {url}")
        return Image.open(BytesIO(data))


async def create_ftp_connection(hostname, username, password):
    try:
        ftp = FTP(hostname)
        ftp.login(user=username, passwd=password)
        return ftp
    except Exception as e:
        print(f"Failed to connect to FTP: {e}")
        print(f"HOST: {hostname} USER: {username}")
        return None


async def upload_file_to_ftp(ftp, local_path, remote_directory, remote_filename):
    try:
        ftp.cwd(remote_directory)
        with open(local_path, 'rb') as file:
            ftp.storbinary('STOR ' + remote_filename, file)
    except Exception as e:
        print(f"An error occurred while uploading {remote_filename}: {e}")


async def build_notification(player_obj, message, notification_type, title_msg, item=None, rarity=None):
    # Initializations.
    width, height = 800, 200
    title_colour, banner = CyanColour, "blank_banner_1"
    if rarity == "Uber Rare" or notification_type == "Sovereign":
        title_colour, banner = CyanColour, "blank_banner_2"
    elif rarity == "Ultimate Rare" or notification_type == "Sacred":
        title_colour, banner = CyanColour, "blank_banner_3"
    banner_url = f"{web_url}/botimages/banners/{banner}.png"
    cardBG = Image.open(requests.get(banner_url, stream=True).raw)
    result = Image.new("RGBA", (width, height))
    result.paste(cardBG, (0, 0), cardBG)
    font_file_small = requests.get((font_base_url + my_font_url), stream=True).raw
    font_file_big = requests.get((font_base_url + my_font_url), stream=True).raw
    image_editable = ImageDraw.Draw(result)
    # Apply Title and Message Text.
    title_font = ImageFont.truetype(font_file_small, 34)
    text_font = ImageFont.truetype(font_file_big, 38)
    message_colour = "White"
    image_editable.text((55 + 2, 50 + 2), title_msg, fill="black", font=title_font)
    image_editable.text((55, 50), title_msg, fill=title_colour, font=title_font)
    image_editable.text((115, 100), message, fill=message_colour, font=text_font)
    # Achievement Icon Loading.
    if notification_type == "Achievement":
        icon_size = (54, 54)
        star_code = "Alt" if player_obj.player_echelon == 9 else 9 if player_obj.player_echelon == 10 else player_obj.player_echelon
        icon_url = f"https://PandoraPortal.ca/gallery/Icons/Stars/Original/Star{star_code}.png"
        role_icon = Image.open(requests.get(icon_url, stream=True).raw)
        role_icon = role_icon.resize(icon_size)
        result.paste(role_icon, (42, 90), mask=role_icon)
    elif notification_type == "Item":
        if item.item_image != "":
            image_url = item.item_image.replace("Frame_", "")
            item_icon = Image.open(requests.get(image_url, stream=True).raw)
            result.paste(item_icon, (35, 85), mask=item_icon)
    elif notification_type == "Sacred":
        pass
    # Save and return image.
    file_path = f'{gli.image_path}notification/Notification{player_obj.player_id}.png'
    result.save(file_path)
    return file_path


async def build_message_box(player_obj, message, header="", boxtype="default"):
    width, height = 800, 200
    modspeak_size_title, modspeak_size_msg = 38, 38
    title_size, msg_size = (54, 36) if boxtype == "default" else (44, 36)
    type_dict = {"default": "game_banner", "mod": "blank_banner_1", "admin": "blank_banner_2", "arch": "blank_banner_3"}
    # Load background image and fonts
    cardBG = Image.open(requests.get(f"{web_url}/botimages/banners/{type_dict[boxtype]}.png", stream=True).raw)
    result = Image.new("RGBA", (width, height))
    result.paste(cardBG, (0, 0), cardBG)
    image_editable = ImageDraw.Draw(result)
    font_file_small = requests.get((font_base_url + my_font_url), stream=True).raw
    font_object = ImageFont.truetype(font_file_small, msg_size)
    # Calculate positions for the message lines
    text_x = image_editable.textlength(message[0], font=font_object)
    position_x, position_y = ((width - text_x) / 2 if boxtype == "default" else 60), [98, 136]
    # Draw message text
    for idx, line_text in enumerate(message):
        image_editable.text((position_x, position_y[idx]), line_text, fill="White", font=font_object)
    # Build the header
    if header != "":
        font_file_big = requests.get((font_base_url + my_font_url), stream=True).raw
        title_font = ImageFont.truetype(font_file_big, title_size)
        if boxtype != "default":
            guild_icon = Image.open(requests.get(gli.archdragon_logo, stream=True).raw)
            guild_icon = guild_icon.resize((60, 60))
            result.paste(guild_icon, (50, 32), mask=guild_icon)
        text_x = image_editable.textlength(header, font=title_font)
        header_position = ((width - text_x) / 2, 35) if boxtype == "default" else (130, 45)
        shadow_position = (header_position[0] + 2, header_position[1] + 2)
        image_editable.text(shadow_position, header, fill="black", font=title_font)
        image_editable.text(header_position, header, fill=CyanColour, font=title_font)
    # Save and return image.
    file_path = f'{gli.image_path}notification/Notification{"TEMP" if player_obj is None else player_obj.player_id}.png'
    result.save(file_path)
    return file_path


async def build_title_box(message):
    width, height = 800, 200
    cardBG = Image.open(requests.get(f"{web_url}/botimages/banners/game_banner.png", stream=True).raw)
    result = Image.new("RGBA", (width, height))
    result.paste(cardBG, (0, 0), cardBG)
    image_editable = ImageDraw.Draw(result)
    font_file = requests.get((font_base_url + my_font_url), stream=True).raw
    title_font = ImageFont.truetype(font_file, 64)
    text_x = image_editable.textlength(message, font=title_font)
    image_editable.text(((width - text_x) / 2 + 2, 60 + 2), message, fill="black", font=title_font)
    image_editable.text(((width - text_x) / 2, 60), message, fill=GoldColour, font=title_font)
    # Save and return image.
    file_path = f'{gli.image_path}notification/Title_Notification.png'
    result.save(file_path)
    return file_path

