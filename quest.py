# General imports
import pandas as pd
import discord

# Data imports
import globalitems
import sharedmethods
import questdata
from pandoradb import run_query as rq

# Core imports
import player
import inventory

# Item/crafting imports
import loot
import tarot


class Quest:
    def __init__(self, quest_num, quest_type, quest_title, story_message,
                 cost, token_num, item_handin, quest_message,
                 award_item, award_qty, award_role):
        self.quest_num, self.quest_type = quest_num, quest_type
        self.colour = globalitems.tier_colors[(min(8, quest_num // 5))]
        self.story_message = story_message
        self.cost, self.token_num, self.item_handin = cost, token_num, item_handin
        self.quest_message = quest_message
        quest_section = (self.quest_num // 5) + 1
        self.award_exp, self.award_coins = quest_section * 1000, quest_section * 5000
        self.award_item, self.award_qty, self.award_role = award_item, award_qty, award_role
        self.quest_title = f"#{self.quest_num}: {quest_title}"

    async def hand_in(self, ctx_object, player_obj):
        is_completed, progress_count = await self.calculate_progress(player_obj)
        if is_completed:
            # Pay cost if required
            if self.quest_type == 2:
                await inventory.update_stock(player_obj, self.item_handin, self.cost)
            embed_msg = await self.handle_completion(ctx_object, player_obj, progress_count)
            return embed_msg, is_completed
        # Handle incomplete quest hand-in.
        embed_msg = discord.Embed(colour=self.colour, title=self.quest_title, description=self.story_message)
        progress_msg = f"{self.quest_message}: {progress_count} / {self.cost}"
        embed_msg.add_field(name="Quest Incomplete", value=progress_msg, inline=False)
        return embed_msg, is_completed

    async def calculate_progress(self, player_obj):
        # Handle Specific Quest Exceptions
        if player_obj.player_quest == 20:
            return (False, 0) if player_obj.insignia == "" else (True, 1)
        elif player_obj.player_quest == 21:
            return (False, 0) if player_obj.pact == "" else (True, 1)
        elif player_obj.player_quest == 22:
            return (False, 0) if player_obj.player_equipped[2] == 0 else True, 1
        elif player_obj.player_quest == 28:
            return (False, 0) if player_obj.player_equipped[5] == 0 else True, 1
        elif player_obj.player_quest == 31:
            return (False, 0) if player_obj.equipped_tarot == "" else (True, 1)
        elif player_obj.player_quest == 51:
            collection_count = tarot.collection_check(player_obj)
            return (True, collection_count) if collection_count == 31 else (False, collection_count)

        # Token, Feature Token, or Boss Token Quests.
        if self.quest_type == 0 or self.quest_type == 3:
            progress_count = player_obj.quest_tokens[self.token_num]
            return (progress_count >= self.cost), progress_count
        # Level Quests.
        if self.quest_type == 1:
            current_level = player_obj.player_level
            return (True, current_level) if current_level >= self.cost else (False, current_level)
        # Hand-In Quests.
        if self.quest_type == 2:
            progress_count = await inventory.check_stock(player_obj, self.item_handin)
            return (progress_count >= self.cost), progress_count

    async def handle_completion(self, ctx_object, player_obj, progress_count):
        # Update player data. Handle EXP/Coin Awards.
        player_obj.player_quest += 1
        player_obj.set_player_field("player_quest", player_obj.player_quest)
        exp_msg, lvl_change = player_obj.adjust_exp(self.award_exp)
        coin_msg = player_obj.adjust_coins(self.award_coins)
        rewards = f"{globalitems.exp_icon} {exp_msg} EXP\n"
        rewards += f"{globalitems.coin_icon} {coin_msg} Lotus Coins\n"
        if lvl_change != 0:
            await sharedmethods.send_notification(ctx_object, player_obj, "Level", lvl_change)
        # Handle Item/Role Awards.
        if self.award_item:
            await inventory.update_stock(player_obj, self.award_item, self.award_qty)
            loot_item = inventory.BasicItem(self.award_item)
            rewards += f"{loot_item.item_emoji} {self.award_qty}x {loot_item.item_name}\n"
        if sharedmethods.check_rare_item(loot_item.item_id):
            await sharedmethods.send_notification(ctx_object, player_obj, "Item", loot_item.item_id)
        if self.award_role:
            rewards += f"New Role Achieved: {self.award_role}!"
            player_obj.player_echelon += 1
            player_obj.set_player_field("player_echelon", player_obj.player_echelon)
            await sharedmethods.send_notification(ctx_object, player_obj, "Achievement", self.award_role)
        return discord.Embed(colour=self.colour, title="QUEST COMPLETED!", description=rewards)

    async def get_quest_embed(self, player_obj):
        is_completed, progress_count = await self.calculate_progress(player_obj)
        quest_details = f"{self.quest_message}: {progress_count} / {self.cost}"
        quest_embed = discord.Embed(colour=self.colour, title=self.quest_title, description="")
        quest_giver = "Pandora, The Celestial"
        if player_obj.player_quest in range(50, 54):
            quest_giver = "Echo of __Eleuia, The Wish__"
        quest_embed.add_field(name=quest_giver, value=self.story_message, inline=False)
        quest_embed.add_field(name=f"Quest Details", value=quest_details, inline=False)
        return quest_embed


def assign_unique_tokens(player_obj, token_string, mode=0):
    token_quest_dict = {
        # Boss Tokens
        "XVI - Aurora, The Fortress": 4, "VII - Astratha, The Dimensional": 6, "VIII - Tyra, The Behemoth": 11,
        "II - Pandora, The Celestial": 14, "III - Oblivia, The Void": 16, "IV - Akasha, The Infinite": 17,
        "XXV - Eleuia, The Wish": 19,
        "XXVIII - Fleur, Oracle of the True Laws": 21, "XXIX - Yubelle, Adjudicator of the True Laws": 22,
        1: 23, 2: 25, 3: 26,
        # Feature Tokens
        "Register": 1, "Map": 2, "Town": 5, "Arbiter": 7, "Insignia": 8, "Contract": 9, "Greaves": 10,
        "Crest": 12, "Tarot": 13, "Gauntlet": 15, "Abyss": 18, "Meld": 19, "Tarot Completion": 24}
    token_string = token_string.replace(" [Gauntlet]", "")
    if mode != 0:
        location = token_quest_dict[mode]
    elif token_string in token_quest_dict:
        location = token_quest_dict[token_string]
    player_obj.quest_tokens[location] += 1
    quest_tokens = ";".join(map(str, player_obj.quest_tokens))
    player_obj.set_player_field("quest_tokens", quest_tokens)


def initialize_quest_list():
    quest_object_list = [None]
    for quest_num, values in questdata.quests_data.items():
        current_quest = Quest(quest_num, *values)
        quest_object_list.append(current_quest)
    return quest_object_list


class QuestView(discord.ui.View):
    def __init__(self, ctx_object, player_user, quest_object):
        super().__init__(timeout=None)
        self.ctx_object = ctx_object
        self.player_obj = player_user
        self.quest_object = quest_object
        self.embed_msg, self.new_view = None, None

    @discord.ui.button(label="Hand In", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def handin_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        await self.player_obj.reload_player()
        temp_embed, is_completed = await self.quest_object.hand_in(self.ctx_object, self.player_obj)
        if not is_completed:
            temp_embed.add_field(name="", value="Quest is not completed!", inline=False)
            quest_view = QuestView(self.ctx_object, self.player_obj, self.quest_object)
            await interaction.response.edit_message(embed=temp_embed, view=quest_view)
            return
        # Handle completed quest.
        self.embed_msg = temp_embed
        self.new_view = RewardView(self.ctx_object, self.player_obj)
        await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
        if self.quest_object.award_role is not None:
            add_role = discord.utils.get(interaction.guild.roles, name=self.quest_object.award_role)
            await interaction.user.add_roles(add_role)
            if self.player_obj.player_echelon >= 2:
                previous_rolename = f"Echelon {self.player_obj.player_echelon - 1}"
                remove_role = discord.utils.get(interaction.guild.roles, name=previous_rolename)
                await interaction.user.remove_roles(remove_role)


class RewardView(discord.ui.View):
    def __init__(self, ctx_object, player_user):
        super().__init__(timeout=None)
        self.ctx_object = ctx_object
        self.player_obj = player_user

    @discord.ui.button(label="Next Quest", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def next_quest(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.player_obj.player_quest > 55:
            embed_msg = discord.Embed(colour=discord.Colour.gold(), title="All Clear!", description="")
            await interaction.response.edit_message(embed=embed_msg, view=None)
            return
        current_quest = self.player_obj.player_quest
        quest_object = quest_list[self.player_obj.player_quest]
        embed_msg = await quest_object.get_quest_embed(self.player_obj)
        quest_view = QuestView(self.ctx_object, self.player_obj, quest_object)
        await interaction.response.edit_message(embed=embed_msg, view=quest_view)


# Initialize the quest list.
quest_list = initialize_quest_list()

