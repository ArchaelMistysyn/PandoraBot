from PIL import Image, ImageFont, ImageDraw, ImageOps
import requests
import pandorabot
import player
import os
import globalitems

echelon_1 = "https://kyleportfolio.ca/botimages/roleicon/echelon1.png"
echelon_2 = "https://kyleportfolio.ca/botimages/roleicon/echelon2.png"
echelon_3 = "https://kyleportfolio.ca/botimages/roleicon/echelon3.png"
echelon_4 = "https://kyleportfolio.ca/botimages/roleicon/echelon4.png"
echelon_5 = "https://kyleportfolio.ca/botimages/roleicon/echelon5noflare.png"
echelon_5flare = "https://kyleportfolio.ca/botimages/roleicon/echelon5flare.png"
special_icon = ""
rank_url_list = [echelon_1, echelon_2, echelon_3, echelon_4, echelon_5, echelon_5flare, special_icon]

rank_colour = ["Green", "Blue", "Purple", "Gold", "Red", "Magenta"]


def get_player_profile(player_object, achievement_list):
    image_path = 'C:\\Users\\GamerTech\\PycharmProjects\\PandoraBot\\profilecard'
    font_url = "https://kyleportfolio.ca//botimages/profilecards/fonts/aerolite/Aerolite.otf"
    profile_url = "https://kyleportfolio.ca/botimages/profilecards/bg.png"
    profile_card = Image.open(requests.get(profile_url, stream=True).raw)
    w, h = 500, 280
    new_size = (w, h)
    profile_card = profile_card.resize(new_size)
    font_file = requests.get(font_url, stream=True).raw

    # Exp Bar
    current_lvl = player_object.player_lvl
    current_exp = player_object.player_exp
    max_exp = player.get_max_exp(current_lvl)

    frame_url = "https://kyleportfolio.ca/botimages/profilecards/frame.png"
    frame_bar = Image.open(requests.get(frame_url, stream=True).raw)
    new_size = (420, 35)
    frame_bar = frame_bar.resize(new_size)
    profile_card.paste(frame_bar, (40, 240), mask=frame_bar)

    exp_url = "https://kyleportfolio.ca/botimages/profilecards/expbar.png"
    exp_bar = Image.open(requests.get(exp_url, stream=True).raw)
    new_size = (400, 20)
    exp_bar = exp_bar.resize(new_size)
    profile_card.paste(exp_bar, (50, 250))

    # Achievements
    for idr, role in enumerate(globalitems.global_role_dict):
        if role in achievement_list:
            achv_url = globalitems.global_role_dict[role]
        else:
            achv_url = globalitems.not_owned_icon
        achv_icon = Image.open(requests.get(achv_url, stream=True).raw)
        new_size = (30, 30)
        wloc = 40
        hloc = 40
        row = int(idr / 7)
        achv_icon = achv_icon.resize(new_size)
        profile_card.paste(achv_icon, ((30 + (wloc * idr) - (wloc * 7 * row)), (140 + hloc * row)), mask=achv_icon)

    # Main Card
    title_font = ImageFont.truetype(font_file, 50)
    title_text = player_object.player_username
    image_editable = ImageDraw.Draw(profile_card)
    fill_colour = rank_colour[player_object.player_echelon - 1]
    image_editable.text((20, 20), title_text, fill=fill_colour, font=title_font)

    # Class icon
    class_name = player_object.player_class
    class_url = player.get_thumbnail_by_class(class_name)
    class_icon = Image.open(requests.get(class_url, stream=True).raw)
    new_size = (40, 40)
    class_icon = class_icon.resize(new_size)
    profile_card.paste(class_icon, (180, 22), mask=class_icon)

    # Rank icon
    rank_url = rank_url_list[player_object.player_echelon - 1]
    rank_icon = Image.open(requests.get(rank_url, stream=True).raw)
    new_size = (130, 130)
    rank_icon = rank_icon.resize(new_size)
    profile_card.paste(rank_icon, (335, 65), mask=rank_icon)

    # Finalize
    filepath = f"{image_path}\\ProfileCard{player_object.player_id}.png"
    profile_card.save(filepath)
    return filepath

