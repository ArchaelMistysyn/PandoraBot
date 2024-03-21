# General imports
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter
import requests
import os

# Data imports
import globalitems
import sharedmethods

# Core imports
import player

image_path = 'C:\\Users\\GamerTech\\PycharmProjects\\PandoraBot\\'

echelon_0 = "https://kyleportfolio.ca/botimages/roleicon/echelon1.png"
echelon_1 = "https://kyleportfolio.ca/botimages/roleicon/echelon1.png"
echelon_2 = "https://kyleportfolio.ca/botimages/roleicon/echelon2.png"
echelon_3 = "https://kyleportfolio.ca/botimages/roleicon/echelon3.png"
echelon_4 = "https://kyleportfolio.ca/botimages/roleicon/echelon4.png"
echelon_5 = "https://kyleportfolio.ca/botimages/roleicon/echelon5noflare.png"
echelon_5flare = "https://kyleportfolio.ca/botimages/roleicon/echelon5flare.png"
special_icon = "https://kyleportfolio.ca/botimages/roleicon/exclusivenoflare.png"
special_iconflare = "https://kyleportfolio.ca/botimages/roleicon/exclusiveflare.png"
rank_url_list = [echelon_0, echelon_1, echelon_2, echelon_3, echelon_4, echelon_5, echelon_5flare,
                 special_icon, special_iconflare]
generic_frame_url = "https://kyleportfolio.ca/botimages/iconframes/Iconframe.png"

rank_colour = ["Green", "Blue", "Purple", "Gold", "Red", "Magenta"]
profile_url = "https://kyleportfolio.ca/botimages/profilecards/"
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
                     f"{profile_url}{wing_gem_url}Azure.png", f"{profile_url}{wing_gem_url}Amethyst.png",
                     f"{profile_url}{wing_gem_url}Cobalt.png", f"{profile_url}{wing_gem_url}Rainbow.png",
                     f"{profile_url}{wing_gem_url}Ruby.png", f"{profile_url}{wing_gem_url}Pink.png"]
metal_url_list = [f"{profile_url}{metal_url}Bronze.png", f"{profile_url}{metal_url}Bronze.png",
                  f"{profile_url}{metal_url}Silver.png", f"{profile_url}{metal_url}SilverPlus.png",
                  f"{profile_url}{metal_url}Gold.png", f"{profile_url}{metal_url}GoldPlus.png",
                  f"{profile_url}{metal_url}Stygian.png"]


class RankCard:
    def __init__(self, user, achievement_list):
        self.user = user
        self.fill_colour = "black"
        echelon = (self.user.player_echelon + 1) // 2
        card_loc, metal_loc, wing_loc, exp_bar_loc, icon_loc, frame_loc = (
            echelon, echelon, echelon, echelon, echelon, echelon)
        if "Exclusive Title Holder" in achievement_list:
            self.fill_colour = "white"
            card_loc, metal_loc, wing_loc, exp_bar_loc = 6, 6, 6, 6
            icon_loc, frame_loc = 7, 7
            # Check if titleholder is echelon 5.
            if echelon == 5:
                card_loc = 5
                exp_bar_loc = 5
                wing_loc = 5
            # Check if titleholder is subscriber.
            if "Herrscher - Subscriber" in achievement_list:
                icon_loc = 8
        # Check if non titleholder is subscriber
        elif "Herrscher - Subscriber" in achievement_list:
            frame_loc = 5
            if echelon < 5:
                card_loc, exp_bar_loc, wing_loc = 7, 7, 7
            # Check if subscriber is echelon 5.
            elif echelon == 5:
                icon_loc = 6
        self.cardBG = rank_card_url_list[card_loc]
        self.metal = metal_url_list[metal_loc]
        self.wing = wing_gem_url_list[wing_loc]
        self.exp_bar = exp_bar_url_list[exp_bar_loc]
        self.role_icon = rank_url_list[icon_loc]
        self.frame_icon = globalitems.frame_icon_list[frame_loc]
        self.frame_icon = self.frame_icon.replace("[EXT]", globalitems.frame_extension[1])
        self.class_icon = sharedmethods.get_thumbnail_by_class(self.user.player_class)
        self.fill_percent = round(self.user.player_exp / player.get_max_exp(self.user.player_lvl), 2)


def get_player_profile(player_obj, achievement_list):
    rank_card = RankCard(player_obj, achievement_list)
    temp_path = f'{image_path}profilecard\\'
    font_url = "https://kyleportfolio.ca//botimages/profilecards/fonts/"
    level_font_url = "aerolite/Aerolite.otf"
    # level_font_url = "oranienbaum/Oranienbaum.ttf"
    chosen_font = "blackchancery/BLKCHCRY.TTF"
    font_file = requests.get((font_url + chosen_font), stream=True).raw
    level_font_file = requests.get((font_url + level_font_url), stream=True).raw
    cardBG = Image.open(requests.get(rank_card.cardBG, stream=True).raw)
    metal = Image.open(requests.get(rank_card.metal, stream=True).raw)
    wing = Image.open(requests.get(rank_card.wing, stream=True).raw)
    rank_icon = Image.open(requests.get(rank_card.role_icon, stream=True).raw)
    rank_icon_frame = Image.open(requests.get(rank_card.frame_icon, stream=True).raw)
    class_icon_frame = Image.open(requests.get(generic_frame_url, stream=True).raw)
    class_icon = Image.open(requests.get(rank_card.class_icon, stream=True).raw)
    exp_bar_image = Image.open(requests.get(rank_card.exp_bar, stream=True).raw)
    result = Image.new("RGBA", cardBG.size)
    result.paste(cardBG, (0, 0), cardBG)
    result.paste(metal, (0, 0), metal)
    result.paste(wing, (0, 0), wing)

    # Username
    title_font = ImageFont.truetype(font_file, 54)
    level_font = ImageFont.truetype(level_font_file, 40)

    title_text = player_obj.player_username
    title_text = title_text.center(10)
    image_editable = ImageDraw.Draw(result)
    fill_colour = rank_card.fill_colour
    image_editable.text((200, 215), title_text, fill=fill_colour, font=title_font)

    # Class Icon
    new_size = (68, 68)
    class_icon = class_icon.resize(new_size)
    result.paste(class_icon, (130, 214), mask=class_icon)

    # Class Icon Frame
    new_size = (68, 68)
    class_icon_frame = class_icon_frame.resize(new_size)
    result.paste(class_icon_frame, (131, 214), mask=class_icon_frame)

    # Rank Icon
    new_size = (120, 120)
    rank_icon = rank_icon.resize(new_size)
    result.paste(rank_icon, (629, 215), mask=rank_icon)

    # Rank Icon Frame
    new_size = (125, 125)
    rank_icon_frame = rank_icon_frame.resize(new_size)
    result.paste(rank_icon_frame, (627, 215), mask=rank_icon_frame)

    # Exp Bar
    exp_bar_start = 197
    exp_bar_end = 750
    exp_bar_result = generate_exp_bar(exp_bar_image, exp_bar_start, exp_bar_end, rank_card.fill_percent)
    result.paste(exp_bar_result, (exp_bar_start, 0), mask=exp_bar_result)

    # Level and Exp Text
    level_text = f"{player_obj.player_lvl}"
    level_text_position = (90, 230)
    image_editable.text(level_text_position, level_text, fill=fill_colour, font=level_font)

    # Save File
    file_path = f"{temp_path}ProfileCard{player_obj.player_id}.png"
    result.save(file_path)
    return file_path


def generate_exp_bar(exp_bar_image, exp_bar_start, exp_bar_end, fill_percent):
    card_height = exp_bar_image.height
    exp_width = int((exp_bar_end - exp_bar_start) * fill_percent)
    exp_bar_cropped = exp_bar_image.crop((exp_bar_start, 0, exp_bar_start + exp_width, card_height))
    exp_bar_result = Image.new("RGBA", exp_bar_cropped.size)
    exp_bar_result.paste(exp_bar_cropped, (0, 0), mask=exp_bar_cropped)
    return exp_bar_result


def generate_and_combine_images(item_type, start_tier=1, end_tier=8, fetch_type=False):
    if fetch_type:
        item_type = globalitems.gear_category_dict[item_type]
    # Ensure image is currently available.
    availability_list = ["Sword", "Bow", "Threads", "Armour", "Wings", "Amulet"]
    if item_type not in globalitems.availability_list:
        return 0
    for item_tier in range(start_tier, end_tier + 1):
        # Handle the urls and paths.
        frame_url = globalitems.frame_icon_list[item_tier - 1]
        frame_url = frame_url.replace("[EXT]", globalitems.frame_extension[0])
        icon_url = f"https://kyleportfolio.ca/botimages/itemicons/{item_type}/{item_type}{item_tier}.png"
        output_dir, file_name = f'{image_path}itemicons\\{item_type}\\', f"Framed_{item_type}_{item_tier}.png"
        file_path = f"{output_dir}{file_name}"
        frame = Image.open(requests.get(frame_url, stream=True).raw)
        icon = Image.open(requests.get(icon_url, stream=True).raw)
        # Construct the new image
        result = Image.new("RGBA", (106, 106))
        result.paste(frame, (0, 0), frame)
        result.paste(icon, (17, 16), icon)
        result.save(file_path, format="PNG")
    return end_tier + 1 - start_tier

