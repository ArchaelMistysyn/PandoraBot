from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter
import requests
import player
import os
import globalitems

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
        echelon = self.user.player_echelon
        card_loc = echelon
        metal_loc = echelon
        wing_loc = echelon
        exp_bar_loc = echelon
        icon_loc = echelon
        if "Exclusive Title Holder" in achievement_list:
            self.fill_colour = "white"
            card_loc = 6
            metal_loc = 6
            wing_loc = 6
            exp_bar_loc = 6
            icon_loc = 7
            if echelon == 5:
                card_loc = 5
                exp_bar_loc = 5
                wing_loc = 5
            if "Herrscher - Subscriber" in achievement_list:
                icon_loc = 8
        elif "Herrscher - Subscriber" in achievement_list:
            if echelon < 5:
                card_loc = 7
                exp_bar_loc = 7
                wing_loc = 7
            elif echelon == 5:
                icon_loc = 6
        self.cardBG = rank_card_url_list[card_loc]
        self.metal = metal_url_list[metal_loc]
        self.wing = wing_gem_url_list[wing_loc]
        self.exp_bar = exp_bar_url_list[exp_bar_loc]
        self.role_icon = rank_url_list[icon_loc]
        self.class_icon = player.get_thumbnail_by_class(self.user.player_class)
        self.fill_percent = round(self.user.player_exp / player.get_max_exp(self.user.player_lvl), 2)


def get_player_profile(player_object, achievement_list):
    rank_card = RankCard(player_object, achievement_list)
    image_path = 'C:\\Users\\GamerTech\\PycharmProjects\\PandoraBot\\profilecard'
    font_url = "https://kyleportfolio.ca//botimages/profilecards/fonts/"
    # chosen_font = "aerolite/Aerolite.otf"
    # chosen_font = "oranienbaum/Oranienbaum.ttf"
    chosen_font = "blackchancery/BLKCHCRY.TTF"
    font_url += chosen_font
    font_file = requests.get(font_url, stream=True).raw
    cardBG = Image.open(requests.get(rank_card.cardBG, stream=True).raw)
    metal = Image.open(requests.get(rank_card.metal, stream=True).raw)
    wing = Image.open(requests.get(rank_card.wing, stream=True).raw)
    rank_icon = Image.open(requests.get(rank_card.role_icon, stream=True).raw)
    class_icon = Image.open(requests.get(rank_card.class_icon, stream=True).raw)
    exp_bar_image = Image.open(requests.get(rank_card.exp_bar, stream=True).raw)
    result = Image.new("RGBA", cardBG.size)
    result.paste(cardBG, (0, 0), cardBG)
    result.paste(metal, (0, 0), metal)
    result.paste(wing, (0, 0), wing)

    # Username
    title_font = ImageFont.truetype(font_file, 54)
    title_text = player_object.player_username
    image_editable = ImageDraw.Draw(result)
    fill_colour = rank_card.fill_colour
    image_editable.text((195, 215), title_text, fill=fill_colour, font=title_font)

    # Class Icon
    new_size = (64, 64)
    class_icon = class_icon.resize(new_size)
    result.paste(class_icon, (128, 216), mask=class_icon)

    # Rank Icon
    new_size = (120, 120)
    rank_icon = rank_icon.resize(new_size)
    result.paste(rank_icon, (629, 215), mask=rank_icon)

    # Exp Bar
    exp_bar_start = 197
    exp_bar_end = 750
    exp_bar_result = generate_exp_bar(exp_bar_image, exp_bar_start, exp_bar_end, rank_card.fill_percent)
    result.paste(exp_bar_result, (exp_bar_start, 0), mask=exp_bar_result)
    file_path = f"{image_path}\\ProfileCard{player_object.player_id}.png"
    result.save(file_path)
    return file_path


def generate_exp_bar(exp_bar_image, exp_bar_start, exp_bar_end, fill_percent):
    card_height = exp_bar_image.height
    exp_width = int((exp_bar_end - exp_bar_start) * fill_percent)
    exp_bar_cropped = exp_bar_image.crop((exp_bar_start, 0, exp_bar_start + exp_width, card_height))
    exp_bar_result = Image.new("RGBA", exp_bar_cropped.size)
    exp_bar_result.paste(exp_bar_cropped, (0, 0), mask=exp_bar_cropped)
    return exp_bar_result
