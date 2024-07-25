# General imports
import pandas as pd
import discord

# Data imports
import globalitems as gli
import sharedmethods as sm
import questdata
from pandoradb import run_query as rqy

# Core imports
import player
import inventory

# Item/crafting imports
import loot
import tarot


class Quest:
    def __init__(self, quest_num, quest_type, quest_title, quest_giver, story_message,
                 cost, token_num, item_handin, quest_message,
                 award_item, award_qty, award_role):
        self.quest_num, self.quest_type = quest_num, quest_type
        self.colour = gli.tier_colors[(min(8, quest_num // 5))]
        self.quest_giver, self.story_message = quest_giver, story_message
        self.cost, self.token_num, self.item_handin = cost, token_num, item_handin
        self.quest_message = quest_message
        quest_section = (self.quest_num // 5) + 1
        self.award_exp, self.award_coins = quest_section * 1000, quest_section * 5000
        self.award_item, self.award_qty, self.award_role = award_item, award_qty, award_role
        self.quest_title = f"#{self.quest_num}: {quest_title}"

    async def hand_in(self, ctx_object, player_obj, choice_num, choice_reward):
        is_completed, progress_count = await self.calculate_progress(player_obj)
        if is_completed:
            # Pay cost if required
            if self.quest_type == 2:
                await inventory.update_stock(player_obj, self.item_handin, self.cost)
            embed_msg = await self.handle_completion(ctx_object, player_obj, progress_count, choice_num, choice_reward)
            return embed_msg, is_completed
        # Handle incomplete quest hand-in.
        embed_msg = discord.Embed(colour=self.colour, title=self.quest_title, description=self.story_message)
        quest_message = self.quest_message.replace('[USER]', player_obj.player_username)
        progress_msg = f"{quest_message}: {progress_count} / {self.cost}"
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
            collection_count = await tarot.collection_check(player_obj)
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

    async def handle_completion(self, ctx_object, player_obj, progress_count, choice_num, choice_reward):
        # Update player data. Handle EXP/Coin Awards.
        player_obj.player_quest += 1
        await player_obj.set_player_field("player_quest", player_obj.player_quest)
        exp_msg, lvl_change = await player_obj.adjust_exp(self.award_exp)
        coin_msg = await player_obj.adjust_coins(self.award_coins)
        rewards = f"{gli.exp_icon} {exp_msg} EXP\n"
        rewards += f"{gli.coin_icon} {coin_msg} Lotus Coins\n"
        if lvl_change != 0:
            await sm.send_notification(ctx_object, player_obj, "Level", lvl_change)
        # Handle Item/Role Awards.
        reward_id = self.award_item if choice_reward is None else choice_reward
        await inventory.update_stock(player_obj, reward_item, self.award_qty)
        item_obj = inventory.BasicItem(reward_id)
        rewards += f"{item_obj.item_emoji} {self.award_qty}x {item_obj.item_name}\n"
        if sm.check_rare_item(item_obj.item_id):
            await sm.send_notification(ctx_object, player_obj, "Item", item_obj.item_id)
        if self.award_role:
            rewards += f"New Role Achieved: {self.award_role}!"
            player_obj.player_echelon += 1
            await player_obj.set_player_field("player_echelon", player_obj.player_echelon)
            await sm.send_notification(ctx_object, player_obj, "Achievement", self.award_role)
        # Update oath data.
        await player_obj.update_misc_data("quest_choice", 0, overwrite_value=True)
        if self.quest_num in questdata.eligibility_dict or self.quest_num == 54:
            oath_char, update_points = choice_num, 1
            if self.quest_num != 54:
                oath_char = questdata.eligibility_dict[self.quest_num][0]
                update_points = questdata.eligibility_dict[self.quest_num][1][choice_num]
            data_list = await get_oath_data(player_obj)
            data_list[oath_char] += update_points
            await player_obj.update_misc_data("oath_data", ';'.join(map(str, data_list)), overwrite_value=True)
        return discord.Embed(colour=self.colour, title="QUEST COMPLETED!", description=rewards)

    async def get_quest_embed(self, player_obj, choice_message=None):
        is_completed, progress_count = await self.calculate_progress(player_obj)
        quest_message = self.quest_message if choice_message is None else choice_message
        quest_message = quest_message.replace('[USER]', player_obj.player_username)
        oath_char = ""
        if '[OATH]' in self.quest_giver:
            data_list = await get_oath_data(player_obj)
            if 2 in data_list:
                oath_char = questdata.oath_dict[data_list.index(2)]
        quest_giver = self.quest_giver.replace('[OATH]', oath_char)
        quest_details = f"{quest_message}: {progress_count} / {self.cost}"
        quest_embed = discord.Embed(colour=self.colour, title=self.quest_title, description="")
        quest_embed.add_field(name=quest_giver, value=self.story_message, inline=False)
        quest_embed.add_field(name=f"Quest Details", value=quest_details, inline=False)
        return quest_embed


async def assign_unique_tokens(player_obj, token_string, mode=0):
    token_quest_dict = {
        # Boss Tokens
        "XVI - Aurora, The Fortress": 4, "VII - Astratha, The Dimensional": 6, "VIII - Tyra, The Behemoth": 11,
        "II - Pandora, The Celestial": 14, "III - Oblivia, The Void": 16, "IV - Akasha, The Infinite": 17,
        "XXV - Eleuia, The Wish": 19,
        "XXVIII - Fleur, Oracle of the True Laws": 21, "XXIX - Yubelle, Adjudicator of the True Laws": 22,
        1: 23, 2: 25, 3: 26,
        # Feature Tokens
        "Register": 1, "Map": 2, "Town": 5, "Divine": 7, "Insignia": 8, "Contract": 9, "Greaves": 10,
        "Crest": 12, "Tarot": 13, "Gauntlet": 15, "Abyss": 18, "Meld": 19, "Tarot Completion": 24}
    token_string = token_string.replace(" [Gauntlet]", "")
    if mode != 0:
        location = token_quest_dict[mode]
    elif token_string in token_quest_dict:
        location = token_quest_dict[token_string]
    else:
        return
    player_obj.quest_tokens[location] += 1
    quest_tokens = ";".join(map(str, player_obj.quest_tokens))
    await player_obj.set_player_field("quest_tokens", quest_tokens)


def initialize_quest_list():
    quest_obj_list = [None]
    for quest_num, values in questdata.quests_data.items():
        current_quest = Quest(quest_num, *values)
        quest_obj_list.append(current_quest)
    return quest_obj_list


async def get_oath_data(player_obj):
    oath_data = await player_obj.check_misc_data("oath_data")
    return list(map(int, oath_data.split(';')))


class ChoiceView(discord.ui.View):
    def __init__(self, ctx_object, player_obj, quest_obj, oath_data, choices, e_ring):
        super().__init__(timeout=None)
        self.ctx_object, self.player_obj, self.quest_obj = ctx_object, player_obj, quest_obj
        self.choices = choices
        for idx, button in enumerate(self.children):
            if idx <= len(choices):
                button.label = choices[idx][0]
                if quest_obj.quest_num == 54 and oath_data[idx] != 2 and e_ring != questdata.ring_required[idx]:
                    button.disabled = True
            else:
                self.remove_item(button)

    @discord.ui.button(label="Choice1", style=discord.ButtonStyle.success)
    async def choice1_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_choice(interaction, choice=0)

    @discord.ui.button(label="Choice2", style=discord.ButtonStyle.red)
    async def choice2_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_choice(interaction, choice=1)

    @discord.ui.button(label="Choice3", style=discord.ButtonStyle.blurple)
    async def choice3_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_choice(interaction, 2)

    async def handle_choice(self, interaction, choice):
        if interaction.user.id != self.player_obj.discord_id:
            return
        await self.player_obj.update_misc_data("quest_choice", choice, overwrite_value=True)
        quest_view = QuestView(self.ctx_object, self.player_obj, self.quest_obj, choice, self.choices[choice][1])
        embed = await self.quest_obj.get_quest_embed(player_obj, self.choices[choice][2])
        await interaction.response.edit_message(embed=embed, view=quest_view)


class QuestView(discord.ui.View):
    def __init__(self, ctx_object, player_obj, quest_obj, choice_num, choice_reward):
        super().__init__(timeout=None)
        self.ctx_object, self.player_obj, self.quest_obj = ctx_object, player_obj, quest_obj
        self.embed_msg, self.new_view = None, None
        self.choice_num, self.choice_reward = choice_num, choice_reward

    @discord.ui.button(label="Hand In", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def handin_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
            return
        await self.player_obj.reload_player()
        temp_embed, is_completed = \
            await self.quest_obj.hand_in(self.ctx_object, self.player_obj, self.choice_num, self.choice_reward)
        if not is_completed:
            temp_embed.add_field(name="", value="Quest is not completed!", inline=False)
            quest_view = QuestView(self.ctx_object, self.player_obj, self.quest_obj, self.choice_num, self.choice_reward)
            await interaction.response.edit_message(embed=temp_embed, view=quest_view)
            return
        # Handle completed quest.
        self.embed_msg = temp_embed
        self.new_view = RewardView(self.ctx_object, self.player_obj)
        await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
        if self.quest_obj.award_role is not None:
            add_role = discord.utils.get(interaction.guild.roles, name=self.quest_obj.award_role)
            await interaction.user.add_roles(add_role)
            if self.player_obj.player_echelon >= 2:
                previous_rolename = f"Echelon {self.player_obj.player_echelon - 1}"
                remove_role = discord.utils.get(interaction.guild.roles, name=previous_rolename)
                await interaction.user.remove_roles(remove_role)


class RewardView(discord.ui.View):
    def __init__(self, ctx_object, player_obj):
        super().__init__(timeout=None)
        self.ctx_object, self.player_obj = ctx_object, player_obj

    @discord.ui.button(label="Next Quest", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def next_quest(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        self.player_obj.reload_player()
        player_choice, reward, choice_message = None, None, None
        c_quest, quest_obj = self.player_obj.player_quest, quest_list[self.player_obj.player_quest]
        if c_quest in questdata.quest_options:
            choice_data = questdata.quest_options[c_quest]
            oath_data = await get_oath_data(self.player_obj)
            player_choice = await self.player_obj.check_misc_data("quest_choice")
            if player_choice == 0:
                ring_id = self.player_obj.player_equipped[4]
                e_ring = None if c_quest != 54 else await inventory.read_custom_item(ring_id)
                new_view = ChoiceView(self.ctx_object, self.player_obj, quest_obj, oath_data, choice_data, e_ring)
                quest_message = await quest_obj.get_quest_embed(self.player_obj, choice_message)
                # output
                return
            else:
                reward, choice_message = choice_data[1], choice_data[2]
        embed_msg = await quest_obj.get_quest_embed(self.player_obj)
        new_view = QuestView(self.ctx_object, self.player_obj, quest_obj, player_choice, reward) if c_quest < 55 else None
        await interaction.response.edit_message(embed=embed_msg, view=new_view)


# Initialize the quest list.
quest_list = initialize_quest_list()

