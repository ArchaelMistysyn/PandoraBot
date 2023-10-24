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
import tarot


class Quest:
    def __init__(self, quest_num, quest_title, story_message, cost, token_num, item_handin, quest_message,
                 award_exp, award_coins, award_item, award_qty, award_role):
        self.quest_num = quest_num
        self.quest_title = quest_title
        self.story_message = story_message
        self.cost = cost
        self.token_num = token_num
        self.item_handin = item_handin
        self.quest_message = quest_message
        self.quest_output = ""
        self.award_exp = award_exp
        self.award_coins = award_coins
        self.award_item = award_item
        self.award_qty = award_qty
        self.award_role = award_role

    def set_quest_output(self, progress_count):
        fake_level_tokens = get_fake_level_tokens(self.quest_num)
        self.quest_output = (f"{self.quest_message}: "
                             f"{progress_count + fake_level_tokens} / {self.cost + fake_level_tokens}")

    def hand_in(self, player_object):
        progress_count = 0
        is_completed = False
        if self.token_num == -1:
            progress_count = inventory.check_stock(player_object, self.item_handin)
            if progress_count >= self.cost:
                inventory.update_stock(player_object, self.item_handin, (0 - self.cost))
                is_completed = True
        elif self.token_num == 0:
            progress_count = tarot.collection_check(player_object.player_id)
            if progress_count == 46:
                is_completed = True
        elif self.token_num == 7:
            if player_object.equipped_wing != 0:
                e_wing = inventory.read_custom_item(player_object.equipped_wing)
                if e_wing.item_tier == 4:
                    is_completed = True
                    progress_count = 1
        elif self.token_num == 8:
            if player_object.equipped_crest != 0:
                e_crest = inventory.read_custom_item(player_object.equipped_crest)
                if e_crest.item_tier == 4:
                    is_completed = True
                    progress_count = 1
        else:
            token_type = self.quest_exceptions()
            progress_count = player_object.check_tokens(token_type)
            if progress_count >= self.cost:
                player_object.update_tokens(self.quest_num, (0 - self.cost))
                is_completed = True
        if is_completed:
            player_object.player_quest += 1
            player_object.set_player_field("player_quest", player_object.player_quest)
            player_object.player_exp += self.award_exp
            player_object.player_coins += self.award_coins
            player_object.set_player_field("player_exp", player_object.player_exp)
            player_object.set_player_field("player_coins", player_object.player_coins)
            reward_list = f"{pandorabot.exp_icon} {self.award_exp}x Exp\n"
            reward_list += f"{pandorabot.coin_icon} {self.award_coins}x Lotus Coins\n"
            if self.award_item != "":
                inventory.update_stock(player_object, self.award_item, self.award_qty)
                loot_item = loot.BasicItem(self.award_item)
                reward_list += f"{loot_item.item_emoji} {self.award_qty}x {loot_item.item_name}\n"
            if self.award_role != "":
                reward_list += f"New Role Achieved: {self.award_role}!"
                player_object.player_echelon += 1
                player_object.set_player_field("player_echelon", player_object.player_echelon)
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title="QUEST COMPLETED!",
                                      description=reward_list)
        else:
            self.set_quest_output(progress_count)
            embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                      title=self.quest_title,
                                      description=self.story_message)
        return embed_msg, is_completed

    def get_quest_embed(self, player_object):
        progress_count = 0
        if self.token_num == -1:
            progress_count = inventory.check_stock(player_object, self.item_handin)
        elif self.token_num == 0:
            progress_count = tarot.collection_check(player_object.player_id)
        elif self.token_num == 7:
            if player_object.equipped_wing != 0:
                e_wing = inventory.read_custom_item(player_object.equipped_wing)
                if e_wing.item_tier == 4:
                    progress_count = 1
        elif self.token_num == 8:
            if player_object.equipped_crest != 0:
                e_crest = inventory.read_custom_item(player_object.equipped_crest)
                if e_crest.item_tier == 4:
                    progress_count = 1
        else:
            token_check = self.quest_exceptions()
            progress_count = player_object.check_tokens(token_check)
        self.set_quest_output(progress_count)
        quest_embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                    title=self.quest_title,
                                    description=self.story_message)
        quest_embed.add_field(name=f"Quest", value=self.quest_output, inline=False)
        return quest_embed

    def quest_exceptions(self):
        if self.quest_num in [5, 8, 10, 14, 20, 22, 25, 27, 28, 29]:
            token_num = 3
        else:
            token_num = self.token_num
        return token_num


def get_quest(quest_num, player_user):
    return quest_list[quest_num - 1]


def assign_tokens(player_object, boss_object):
    match player_object.player_quest:
        case 9:
            if boss_object.boss_name == "XVI - Aurora, The Fortress":
                player_object.update_tokens(4, 1)
        case 12:
            if boss_object.boss_name == "VII - Astratha, The Dimensional":
                player_object.update_tokens(5, 1)
        case 13:
            if boss_object.boss_name == "VIII - Tyra, The Behemoth":
                player_object.update_tokens(6, 1)
        case 21:
            if boss_object.boss_name == "II - Pandora, The Celestial":
                player_object.update_tokens(9, 1)
        case 23:
            if boss_object.boss_name == "III - Oblivia, The Void":
                player_object.update_tokens(10, 1)
        case 24:
            if boss_object.boss_name == "IV - Akasha, The Infinite":
                player_object.update_tokens(11, 1)
        case 26:
            if boss_object.boss_name == "XXX - Eleuia, The Wish":
                player_object.update_tokens(12, 1)
        case _:
            nothing = True


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


def initialize_quest_list():
    filename = "questlist.csv"
    df = pd.read_csv(filename)
    df['award_role'] = df['award_role'].fillna("")
    main_quest = []
    if len(df.index) != 0:
        for index, row in df.iterrows():
            quest_num = int(row['quest_num'])
            quest_title = f"{quest_num}: {str(row['quest_title'])}"
            story_message = str(row['story_message'])
            cost = int(row['cost_num'])
            token_num = int(row['token_num'])
            item_handin = str(row['item_handin'])
            quest_message = str(row['quest_message'])
            award_exp = int(row['award_exp'])
            award_coins = int(row['award_coins'])
            award_item = str(row['award_item'])
            award_qty = int(row['award_qty'])
            award_role = str(row['award_role'])
            current_quest = Quest(quest_num, quest_title, story_message, cost, token_num, item_handin, quest_message,
                                  award_exp, award_coins, award_item, award_qty, award_role)
            main_quest.append(current_quest)
    return main_quest


class QuestView(discord.ui.View):
    def __init__(self, player_user, quest_object):
        super().__init__(timeout=None)
        self.player_object = player_user
        self.quest_object = quest_object
        self.embed_msg = None

    @discord.ui.button(label="Hand In", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def hand_in(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_object.player_name:
                if not self.embed_msg:
                    reload_player = player.get_player_by_id(self.player_object.player_id)
                    self.embed_msg, is_completed = self.quest_object.hand_in(reload_player)
                    if is_completed:
                        reward_view = RewardView(reload_player)
                        if self.quest_object.award_role != "":
                            add_role = discord.utils.get(interaction.guild.roles, name=self.quest_object.award_role)
                            await interaction.user.add_roles(add_role)
                            if reload_player.player_echelon >= 2:
                                previous_rolename = pandorabot.role_list[(reload_player.player_echelon - 2)]
                                remove_role = discord.utils.get(interaction.guild.roles, name=previous_rolename)
                                await interaction.user.remove_roles(remove_role)
                    else:
                        self.embed_msg.add_field(name="", value="Quest is not yet completed!", inline=False)
                        reward_view = None
                await interaction.response.edit_message(embed=self.embed_msg, view=reward_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_object.player_name:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class RewardView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_object = player_user

    @discord.ui.button(label="Next Quest", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def next_quest(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_object.player_name:
                end_quest = 30
                if self.player_object.player_quest <= end_quest:
                    current_quest = self.player_object.player_quest
                    quest_object = get_quest(current_quest, self.player_object)
                    embed_msg = quest_object.get_quest_embed(self.player_object)
                    quest_view = QuestView(self.player_object, quest_object)
                else:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                              title="All quests completed!",
                                              description="")
                    quest_view = None
                await interaction.response.edit_message(embed=embed_msg, view=quest_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_object.player_name:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


quest_list = initialize_quest_list()

