import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc
import pandas as pd
import inventory
import loot
import mydb
import pandorabot
import discord
import player


class Quest:
    def __init__(self, quest_num, quest_title, story_message, token_cost, quest_message,
                 award_exp, award_coins, award_item, award_qty, award_role):
        self.quest_num = quest_num
        self.quest_title = quest_title
        self.story_message = story_message
        self.token_cost = token_cost
        self.quest_message = quest_message
        self.quest_output = ""
        self.award_exp = award_exp
        self.award_coins = award_coins
        self.award_item = award_item
        self.award_qty = award_qty
        self.award_role = award_role

    def set_quest_output(self, token_count):
        fake_level_tokens = get_fake_level_tokens(self.quest_num)
        self.quest_output = (f"{self.quest_message}: "
                             f"{token_count + fake_level_tokens} / {self.token_cost + fake_level_tokens}")

    def hand_in(self, current_player):
        player_object = player.get_player_by_id(current_player.player_id)
        token_type = quest_exceptions(self.quest_num)
        token_count = player_object.check_tokens(token_type)
        if token_count >= self.token_cost:
            new_token_count = token_count - self.token_cost
            player_object.update_tokens(token_type, new_token_count)
            player_object.player_quest += 1
            player_object.set_player_field("player_quest", player_object.player_quest)
            is_completed = True
            player_object.player_exp += self.award_exp
            player_object.player_coins += self.award_coins
            player_object.set_player_field("player_exp", player_object.player_exp)
            player_object.set_player_field("player_coins", player_object.player_coins)
            reward_list = f"{pandorabot.exp_icon} {self.award_exp}x Exp\n"
            reward_list += f"{pandorabot.coin_icon} {self.award_coins}x Lotus Coins\n"
            if self.award_item != "":
                inventory.update_stock(player_object, self.award_item, self.award_qty)
                item_emoji = loot.get_loot_emoji(self.award_item)
                item_name = loot.get_loot_name(self.award_item)
                reward_list += f"{item_emoji} {self.award_qty}x {item_name}\n"
            if self.award_role != "":
                reward_list += f"New Role Achieved: {self.award_role}!"
                player_object.player_echelon += 1
                player_object.set_player_field("player_echelon", player_object.player_echelon)
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title="QUEST COMPLETED!",
                                      description=reward_list)
        else:
            is_completed = False
            self.set_quest_output(token_count)
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title=self.quest_title,
                                      description=self.story_message)
        return embed_msg, is_completed

    def get_quest_embed(self, player_object):
        token_check = quest_exceptions(self.quest_num)
        if token_check == 5 and self.quest_num != 5:
            token_count = player_object.check_tokens(token_check)
        else:
            token_count = player_object.check_tokens(token_check)
        self.set_quest_output(token_count)
        quest_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                    title=self.quest_title,
                                    description=self.story_message)
        quest_embed.add_field(name=f"Quest", value=self.quest_output, inline=False)
        return quest_embed


def get_quest(quest_num, player_user):
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM QuestList WHERE quest_num = :current_quest")
        query = query.bindparams(current_quest=quest_num)
        quest_info = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        quest_num = int(quest_info['quest_num'].values[0])
        quest_title = f"{quest_num}: {str(quest_info['quest_title'].values[0])}"
        story_message = str(quest_info['story_message'].values[0])
        token_cost = int(quest_info['token_cost'].values[0])
        quest_message = str(quest_info['quest_message'].values[0])
        award_exp = int(quest_info['award_exp'].values[0])
        award_coins = int(quest_info['award_coins'].values[0])
        award_item = str(quest_info['award_item'].values[0])
        award_qty = int(quest_info['award_qty'].values[0])
        award_role = str(quest_info['award_role'].values[0])
        quest = Quest(quest_num, quest_title, story_message, token_cost, quest_message,
                      award_exp, award_coins, award_item, award_qty, award_role)
    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))
        quest = None
    return quest


def quest_exceptions(quest_num):
    match quest_num:
        case 4:
            token_check = 3
        case 6 | 7:
            token_check = 6
        case 8 | 10 | 14 | 20 | 22 | 25 | 27 | 28 | 29:
            token_check = 5
        case _:
            token_check = quest_num
    return token_check


def assign_tokens(player_object, boss_object):
    if player_object.player_quest <= 4 and boss_object.boss_type == "Fortress":
        player_object.check_and_update_tokens(3, 1)
    elif player_object.player_quest <= 7 and boss_object.boss_type == "Dragon":
        player_object.check_and_update_tokens(6, 1)
    elif player_object.player_quest <= 11 and boss_object.boss_type == "Demon":
        player_object.check_and_update_tokens(11, 1)
    elif player_object.player_quest <= 16 and boss_object.boss_type == "Paragon":
        player_object.check_and_update_tokens(16, 1)
    elif player_object.player_quest <= 18 and boss_object.boss_type == "Paragon":
        player_object.check_and_update_tokens(18, 1)
    elif player_object.player_quest <= 19 and boss_object.boss_type == "Paragon":
        player_object.check_and_update_tokens(19, 1)
    elif player_object.player_quest <= 9 and boss_object.boss_name == "XVI - Aurora, the Fortress":
        player_object.check_and_update_tokens(9, 1)
    elif player_object.player_quest <= 12 and boss_object.boss_name == "VII - Astratha the Dimensional":
        player_object.check_and_update_tokens(12, 1)
    elif player_object.player_quest <= 13 and boss_object.boss_name == "VIII - Tyra, the Behemoth":
        player_object.check_and_update_tokens(13, 1)
    elif player_object.player_quest <= 21 and boss_object.boss_name == "II - Pandora, The Celestial":
        player_object.check_and_update_tokens(21, 1)
    elif player_object.player_quest <= 23 and boss_object.boss_name == "III - Oblivia, The Void":
        player_object.check_and_update_tokens(23, 1)
    elif player_object.player_quest <= 24 and boss_object.boss_name == "IV - Akasha, The Infinite":
        player_object.check_and_update_tokens(24, 1)


def get_fake_level_tokens(quest_num):
    fake_tokens = 0
    match quest_num:
        case 8:
            fake_tokens = 10
        case 10:
            fake_tokens = 20
        case 14:
            fake_tokens = 30
        case 20:
            fake_tokens = 50
        case 22:
            fake_tokens = 60
        case 25:
            fake_tokens = 70
        case 27:
            fake_tokens = 80
        case 28:
            fake_tokens = 90
        case 29:
            fake_tokens = 95
        case _:
            fake_tokens = 0
    return fake_tokens


