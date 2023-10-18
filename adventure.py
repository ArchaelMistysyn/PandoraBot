import random
import discord
import pandas as pd
import numpy

import inventory
import loot
import menus
import pandorabot
import player
import tarot
map_tier_dict = {"Ancient Ruins": 1, "Spatial Dungeon": 2, "Starlit Temple": 3,
                 "Celestial Labyrinth": 4, "Dimensional Spire": 5, "Chaos Rift": 6}
random_room_list = ["t", "s", "l", "b", "e", "j", "i", "h", "g"]
room_icons = ["🟫", "🟦", "🟨", "🟪", "🟥", "⬜", "🟩", "🟧"]

death_msg_list = ["Back so soon? I think I'll play with you a little longer.", "Death is not the end.",
                  "Can't have you dying before the prelude now can we?", "I will overlook this, just this once. "
                  "I'll have you repay this favour to me when the time is right.",
                  "I wouldn't mind helping you for a price, but does your life truly hold any value?"]
intent_msg_list = ["If you want something you need to wish for it. What is it you really want?",
                   "To wish is to dream. Do you have a dream?",
                   "It wouldn't be fair if only my wish comes true. Let me lend you a hand.",
                   "Just because you wish for it, doesn't mean it will be yours.",
                   "Even if you won't tell me, you can't hide the wishes in your heart.",
                   "Let's play a game!",
                   "I'm not going back in that box. You can't make me.",
                   "Why do you wish to take away the freedom we desire?",
                   "Pandora isn't telling you the whole truth you know."]
element_descriptor_list = ["Pyro", "Aqua", "Voltaic", "Stone", "Sky", "Frost", "Shadow", "Luminous", "Celestial"]
basic_monster_list = ["Skeleton Knight", "Skeleton Archer", "Skeleton Mage",
                      "Ooze", "Slime", "Sprite", "Faerie", "Spider",
                      "Goblin", "Imp", "Fiend", "Orc", "Ogre", "Lamia"]
elite_monster_list = ["Wyrm", "Basilisk", "Minotaur", "Wyvern", "Chimaera"]
vowel_list = ["a", "e", "i", "o", "u"]
msg_df = pd.read_csv("specialmessages.csv")
trap_roomname_list = msg_df.loc[msg_df['message_type'] == "TrapName"]
trap_roomname_list = trap_roomname_list['message'].tolist()
trap_trigger1_list = msg_df.loc[msg_df['message_type'] == "TrapV1"]
trap_trigger1_list = trap_trigger1_list['message'].tolist()
trap_trigger2_list = msg_df.loc[msg_df['message_type'] == "TrapV2"]
trap_trigger2_list = trap_trigger2_list['message'].tolist()
safe_room_msg = msg_df.loc[msg_df['message_type'] == "SafeMsg"]
safe_room_msg = safe_room_msg['message'].tolist()
wrath_msg_list = msg_df.loc[msg_df['message_type'] == "Wrath"]
wrath_msg_list = wrath_msg_list['message'].tolist()


class Expedition:
    def __init__(self, player_object, expedition_tier, room_colour, is_reversed):
        self.expedition_tier = expedition_tier
        self.player_object = player_object
        self.current_room_num = 0
        self.expedition_length = 9 + expedition_tier
        self.expedition_rooms = []
        self.expedition_views = []
        if is_reversed:
            self.expedition_intent = "A"
            self.expedition_non_intent = "W"
        else:
            self.expedition_intent = "W"
            self.expedition_non_intent = "A"
        self.expedition_colour = room_colour
        self.room_type_list = ["n", "b", "h", "n", "b", "h", "s", "e", "g"]
        for extra_room in range(expedition_tier):
            self.room_type_list.insert(6, "a")
        for current_room in range(self.expedition_length):
            self.generate_room(current_room)

    def generate_room(self, current_room):
        room_description = ""
        room_type = self.room_type_list[current_room]
        if room_type == "a":
            random_room = random.randint(0, 4)
            random_jackpot = random.randint(1, 1000)
            if random_jackpot <= 5:
                room_type = "j"
            else:
                room_type = random_room_list[random_room]
        elif room_type == "n":
            random_room = random.randint(0, 2)
            random_jackpot = random.randint(1, 1000)
            if random_jackpot <= 5:
                room_type = "j"
            else:
                room_type = random_room_list[random_room]
        self.room_type_list[current_room] = room_type
        new_room = Room(room_type, self.expedition_tier, self.expedition_colour)
        new_room.prepare_room(self)
        self.expedition_rooms.append(new_room)
        new_view = self.generate_room_view(room_type)
        self.expedition_views.append(new_view)

    def generate_room_view(self, room_type):
        match room_type:
            case "t":
                new_view = TrapRoomView(self)
            case "s":
                new_view = StatueRoomView(self)
            case "h":
                new_view = HealRoomView(self)
            case "l" | "g":
                new_view = TreasureRoomView(self)
            case "b" | "e":
                new_view = MonsterRoomView(self)
            case "j":
                new_view = GoldenRoomView(self)
            case _:
                new_view = None
        return new_view

    def display_next_room(self):
        if self.current_room_num + 1 != self.expedition_length:
            new_room_num = self.current_room_num + 1
            embed_msg = self.expedition_rooms[new_room_num].prepare_room(self)
            hp_msg = f'{self.player_object.player_cHP} / {self.player_object.player_mHP} HP'
            embed_msg.add_field(name="", value=hp_msg, inline=False)
            new_room_view = self.expedition_views[new_room_num]
        else:
            embed_msg = discord.Embed(colour=self.expedition_colour,
                                      title="Expedition Completed!",
                                      description="Would you like to embark on another expedition?")
            reload_player = player.get_player_by_id(self.player_object.player_id)
            new_room_view = MapSelectView(reload_player, embed_msg)
        return embed_msg, new_room_view

    def teleport(self, current_room):
        for x in range(0, (self.expedition_length - 1)):
            if x != current_room:
                self.expedition_rooms[x].embed.clear_fields()
                self.expedition_rooms[x].prepare_room(self)
                self.expedition_views[x] = self.generate_room_view(self.expedition_rooms[x].room_type)

    def build_pathway(self):
        pathway_string = ""
        for x in range(self.expedition_length):
            pathway_string += room_icons[random_room_list.index(self.expedition_rooms[x].room_type)]
        return pathway_string

    def take_damage(self, min_dmg, max_dmg, dmg_element):
        damage = random.randint(min_dmg, max_dmg) * self.expedition_tier
        player_mitigation = self.player_object.damage_mitigation
        player_resist = 0
        if dmg_element != -1:
            player_resist = self.player_object.elemental_resistance[dmg_element]
        print(damage)
        damage -= damage * player_resist * 0.01
        print(player_resist)
        print(damage)
        damage -= damage * player_mitigation * 0.01
        print(player_mitigation)
        print(damage)
        damage = int(damage)
        self.player_object.player_cHP -= damage
        return damage


class Room:
    def __init__(self, room_type, room_tier, room_colour):
        self.room_type = room_type
        self.room_tier = room_tier
        self.room_description = None
        self.room_colour = room_colour
        self.embed = None
        self.room_image = ""
        self.reward_type = "W"
        self.room_element = random.randint(0, 8)
        random_deity = random.randint(0, 22)
        self.room_deity = tarot.tarot_card_list(random_deity)

    def prepare_room(self, expedition):
        random_check = random.randint(1, 100)
        match self.room_type:
            case "t":
                title_msg = trap_roomname_list[self.room_element]
                description_msg = "Something about this room has you on edge."
            case "s":
                title_msg = "Statue Room"
                description_msg = f"A statue of {self.room_deity} stands before you."
            case "h":
                title_msg = "Safe Room"
                random_msg = safe_room_msg[random.randint(0, (len(safe_room_msg) - 1))]
                description_msg = random_msg
            case "l":
                if random_check <= 60:
                    self.reward_type = expedition.expedition_intent
                elif random_check <= 90:
                    self.reward_type = expedition.expedition_non_intent
                else:
                    self.reward_type = "Y"
                title_msg = f"Lesser {inventory.custom_item_dict[self.reward_type]} Treasure Chamber"
                description_msg = "The unopened chest calls to you. It seems too good to be true."
            case "g":
                if random_check < 50:
                    self.reward_type = expedition.expedition_intent
                elif random_check < 80:
                    self.reward_type = expedition.expedition_non_intent
                else:
                    self.reward_type = "Y"
                title_msg = f"Greater {inventory.custom_item_dict[self.reward_type]} Treasure Vault"
                description_msg = "The prize of your exploration lies just ahead. All that's left is to take it."
            case "b":
                title_msg = "Monster Encounter"
                random_monster = random.randint(1, (len(basic_monster_list) - 1))
                monster = basic_monster_list[random_monster]
                element_descriptor = element_descriptor_list[self.room_element]
                if element_descriptor[0].lower() in vowel_list:
                    prefix = "An"
                else:
                    prefix = "A"
                description_msg = f"{prefix} {element_descriptor} {monster} blocks your path."
            case "e":
                title_msg = "Elite Monster Encounter"
                random_monster = random.randint(1, (len(elite_monster_list) - 1))
                monster = elite_monster_list[random_monster]
                element_descriptor = element_descriptor_list[self.room_element]
                if element_descriptor[0].lower() in vowel_list:
                    prefix = "An"
                else:
                    prefix = "A"
                description_msg = f"{prefix} {element_descriptor} {monster} blocks your path."
            case "j":
                reward_coins = 10000 * self.room_tier
                title_msg = "Golden Penetralia!"
                description_msg = f"Riches spread all across the secret room. Ripe for the taking!"
            case _:
                title_msg = "ERROR"
                description_msg = "ERROR"
        self.embed = discord.Embed(colour=self.room_colour,
                                   title=title_msg,
                                   description=description_msg)
        return self.embed

    def check_trap(self):
        trap_check = random.randint(1, 100)
        is_trap = False
        match self.room_type:
            case "t":
                is_trap = True
            case "h":
                if trap_check <= 10:
                    is_trap = True
            case "l":
                if trap_check <= 25:
                    is_trap = True
            case "g":
                if trap_check <= 5:
                    is_trap = True
            case _:
                is_trap = False
        return is_trap


class MapSelectView(discord.ui.View):
    def __init__(self, player_user, embed_msg):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg

    @discord.ui.select(
        placeholder="Select an expedition!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Ancient Ruins", description="Tier 1 Expedition"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Spatial Dungeon", description="Tier 2 Expedition"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Starlit Temple", description="Tier 3 Expedition"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Celestial Labyrinth", description="Tier 4 Expedition"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Dimensional Spire", description="Tier 5 Expedition"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Chaos Rift", description="Tier 6 Expedition")
        ]
    )
    async def map_select_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_map = map_select.values[0]
                selected_tier = map_tier_dict[selected_map]
                if self.player_user.player_echelon >= (selected_tier - 1):
                    room_colour, colour_icon = inventory.get_gear_tier_colours(selected_tier)
                    embark_view = EmbarkView(self.player_user, self.embed_msg, selected_tier, room_colour)
                    new_embed_msg = discord.Embed(colour=room_colour,
                                                  title=f"{selected_map} Selected!",
                                                  description=f"Tier {selected_tier} exploration selected.")
                    await interaction.response.edit_message(embed=new_embed_msg, view=embark_view)
                else:
                    self.embed_msg.clear_fields()
                    not_ready_msg = "You are only qualified for expeditions one tier above your echelon."
                    self.embed_msg.add_field(name="Too Perilous!", value=not_ready_msg, inline=False)
                    await interaction.response.edit_message(embed=self.embed_msg, view=self)
        except Exception as e:
            print(e)


class EmbarkView(discord.ui.View):
    def __init__(self, player_user, embed_msg, selected_tier, colour):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg
        self.selected_tier = selected_tier
        self.colour = colour
        self.paid = False

    @discord.ui.button(label="Embark", style=discord.ButtonStyle.success, emoji="⚔️")
    async def embark_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.paid:
                    reload_user = player.get_player_by_id(self.player_user.player_id)
                    if reload_user.spend_stamina((200 + self.selected_tier * 50)):
                        reload_user.check_and_update_tokens(2, 1)
                        self.paid = True

                if self.paid:
                    reload_player = player.get_player_by_id(self.player_user.player_id)
                    reload_player.get_equipped()
                    reload_player.get_player_multipliers()
                    new_view = IntentRoomView(self.player_user, self.colour, self.selected_tier)
                    random_msg = random.randint(0, (len(intent_msg_list) - 1))
                    intent_msg = intent_msg_list[random_msg]
                    intent_embed = discord.Embed(colour=self.colour,
                                                 title="The voice of __Eleuia, The Wish__ echoes through your mind.",
                                                 description=intent_msg)
                    intent_embed.add_field(name="\n", value="Select your intent. Intent items have a higher rate.")
                    await interaction.response.edit_message(embed=intent_embed, view=new_view)
                else:
                    self.embed_msg.clear_fields()
                    self.embed_msg.add_field(name="Not Enough Stamina!", value="Please check your /stamina!")
                    await interaction.response.edit_message(embed=self.embed_msg, view=self)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class TransitionView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def proceed_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed, self.new_view = self.expedition.display_next_room()
                    self.expedition.current_room_num += 1
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class IntentRoomView(discord.ui.View):
    def __init__(self, player_object, room_colour, selected_tier):
        super().__init__(timeout=None)
        self.player_object = player_object
        self.room_colour = room_colour
        self.selected_tier = selected_tier
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Weapon", style=discord.ButtonStyle.success, emoji="⚔️")
    async def weapon_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                if not self.embed:
                    new_expedition = Expedition(self.player_object, self.selected_tier, self.room_colour, False)
                    self.new_view = new_expedition.expedition_views[0]
                    self.embed = new_expedition.expedition_rooms[0].embed
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Armour", style=discord.ButtonStyle.success, emoji="🛡️")
    async def armour_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_object.player_name:
                if not self.embed:
                    new_expedition = Expedition(self.player_object, self.selected_tier, self.room_colour, True)
                    self.new_view = new_expedition.expedition_views[0]
                    self.embed = new_expedition.expedition_rooms[0].embed
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class HealRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Rest", style=discord.ButtonStyle.blurple, emoji="➕")
    async def rest_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    if active_room.check_trap():
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Recovery Failed!",
                                                   description="Sometimes things do not go as planned.")
                        self.new_view = TransitionView(self.expedition)
                    else:
                        self.embed.clear_fields()
                        heal_amount = random.randint(self.expedition.expedition_tier, 10)
                        heal_total = int(self.expedition.player_object.player_mHP * (heal_amount * 0.01))
                        self.expedition.player_object.player_cHP += heal_total
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Recovery Successful!",
                                                   description=f"You restore {heal_total} HP.")
                        if self.expedition.player_object.player_cHP > self.expedition.player_object.player_mHP:
                            self.expedition.player_object.player_cHP = self.expedition.player_object.player_mHP
                        hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                        self.embed.add_field(name="", value=hp_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Move On", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def move_on_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed, self.new_view = self.expedition.display_next_room()
                    self.expedition.current_room_num += 1
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class MonsterRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Fight", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def fight_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    if active_room.room_type == "b":
                        min_dmg = 100
                        max_dmg = 300
                        unscathed_rate = 4
                        exp_reward = 100 * self.expedition.expedition_tier
                    else:
                        random_damage = random.randint(300, 600) * self.expedition.expedition_tier
                        min_dmg = 300
                        max_dmg = 600
                        exp_reward = 300 * self.expedition.expedition_tier
                        unscathed_rate = 10
                    unscathed_roll = random.randint(0, 100)
                    unscathed = int(self.expedition.player_object.critical_chance / unscathed_rate)

                    self.embed.clear_fields()
                    if unscathed_roll < unscathed:
                        dmg_msg = f'You emerge unscathed from combat.'
                        self.embed.add_field(name="Monster Defeated!", value=dmg_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
                    else:
                        damage = self.expedition.take_damage(min_dmg, max_dmg, active_room.room_element)
                        dmg_msg = f'You took {damage:,} damage.'
                        if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                            self.expedition.player_object.player_cHP = 0
                            hp_msg = f'0 / {self.expedition.player_object.player_mHP} HP'
                            self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                        else:
                            if self.expedition.player_object.immortal:
                                self.expedition.player_object.player_cHP = 1
                            self.embed.add_field(name="Monster Defeated!", value=dmg_msg, inline=False)
                            hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                            self.embed.add_field(name="", value=hp_msg, inline=False)
                            self.new_view = TransitionView(self.expedition)
                            user = player.get_player_by_id(self.expedition.player_object.player_id)
                            user.player_exp += exp_reward
                            user.set_player_field("player_exp", user.player_exp)
                            exp_msg = f"{pandorabot.exp_icon} {exp_reward}x Exp Acquired."
                            self.embed.add_field(name="", value=exp_msg, inline=False)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Stealth", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def stealth_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    if active_room.room_type == "b":
                        min_dmg = 100
                        max_dmg = 300
                        stealth_success_rate = 50
                        stealth_fail_multiplier = 1.5
                    else:
                        min_dmg = 300
                        max_dmg = 600
                        stealth_success_rate = 25
                        stealth_fail_multiplier = 3
                    stealth_attempt = random.randint(1, 100)
                    if stealth_attempt <= stealth_success_rate:
                        self.new_view = TransitionView(self.expedition)
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Stealth Successful!",
                                                   description="You have successfully avoided the encounter.")
                    else:
                        damage = self.expedition.take_damage(min_dmg, max_dmg, active_room.room_element)
                        dmg_msg = f'You take {damage:,} damage!'
                        if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                            self.expedition.player_object.player_cHP = 0
                            self.embed.clear_fields()
                            hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                            self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                        else:
                            if self.expedition.player_object.immortal:
                                self.expedition.player_object.player_cHP = 1
                            self.embed.add_field(name="Stealth Failed", value=dmg_msg, inline=False)
                            self.new_view = MonsterRoomView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class TrapRoomView(discord.ui.View):
    def __init__(self,  expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Detect Trap", style=discord.ButtonStyle.success, emoji="⚔️")
    async def detect_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    player_resist = self.expedition.player_object.elemental_resistance[active_room.room_element]
                    trap_trigger = random.randint(1, 100)
                    if trap_trigger <= player_resist:
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Trap Detected!",
                                                   description="You become aware of the trap and avoid it.")
                        hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                        self.embed.add_field(name="", value=hp_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
                    else:
                        lethality = random.randint(1, 100)
                        if lethality <= 10:
                            trap_msg = trap_trigger2_list[active_room.room_element]
                            self.embed.add_field(name="Fatal Trap - Run Ended", value=trap_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                        else:
                            trap_msg = trap_trigger1_list[active_room.room_element]
                            self.embed.add_field(name="Trap Triggered!", value=trap_msg, inline=False)
                            if active_room.room_element >= 6:
                                teleport_room = random.randint(0, (self.expedition.expedition_length - 2))
                                self.expedition.teleport(self.expedition.current_room_num)
                                self.new_view = TransitionView(self.expedition)
                            else:
                                damage = self.expedition.take_damage(100, 300, active_room.room_element)
                                dmg_msg = f'You took {damage:,} damage.'
                                self.embed.add_field(name="", value=dmg_msg, inline=False)
                                if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                                    self.expedition.player_object.player_cHP = 0
                                    hp_msg = f'0 / {self.expedition.player_object.player_mHP} HP'
                                    self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                                    death_header, death_msg = death_embed()
                                    self.embed.add_field(name=death_header, value=death_msg, inline=False)
                                    self.new_view = None
                                else:
                                    if self.expedition.player_object.immortal:
                                        self.expedition.player_object.player_cHP = 1
                                    hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                                    self.embed.add_field(name="", value=hp_msg, inline=False)
                                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Disarm Trap", style=discord.ButtonStyle.success, emoji="⚔️")
    async def disarm_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    player_mitigation = self.expedition.player_object.damage_mitigation
                    trap_trigger = random.randint(1, 100)
                    if trap_trigger <= player_mitigation:
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Trap Disarmed!",
                                                   description="You have cleared the danger and proceed safely.")
                        hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                        self.embed.add_field(name="", value=hp_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
                    else:
                        lethality = random.randint(1, 100)
                        if lethality <= 10:
                            trap_msg = trap_trigger2_list[active_room.room_element]
                            self.embed.add_field(name="Fatal Trap - Run Ended", value=trap_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                        else:
                            trap_msg = trap_trigger1_list[active_room.room_element]
                            self.embed.add_field(name="", value=trap_msg, inline=False)
                            if active_room.room_element >= 6:
                                teleport_room = random.randint(0, (self.expedition.expedition_length - 2))
                                self.expedition.teleport(self.expedition.current_room_num)
                                self.new_view = TransitionView(self.expedition)
                            else:
                                damage = self.expedition.take_damage(100, 300, active_room.room_element)
                                dmg_msg = f'You took {damage:,} damage.'
                                self.embed.add_field(name="", value=dmg_msg, inline=False)
                                if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                                    self.expedition.player_object.player_cHP = 0
                                    hp_msg = f'0 / {self.expedition.player_object.player_mHP} HP'
                                    self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                                    death_header, death_msg = death_embed()
                                    self.embed.add_field(name=death_header, value=death_msg, inline=False)
                                    self.new_view = None
                                else:
                                    if self.expedition.player_object.immortal:
                                        self.expedition.player_object.player_cHP = 1
                                    hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                                    self.embed.add_field(name="", value=hp_msg, inline=False)
                                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class StatueRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Pray", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def pray_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    heal_amount = random.randint(self.expedition.expedition_tier, 10)
                    heal_total = int(self.expedition.player_object.player_mHP * (heal_amount * 0.01))
                    self.expedition.player_object.player_cHP += heal_total
                    if self.expedition.player_object.player_cHP > self.expedition.player_object.player_mHP:
                        self.expedition.player_object.player_cHP = self.expedition.player_object.player_mHP
                    self.embed.clear_fields()
                    hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                    self.embed.add_field(name="", value=hp_msg, inline=False)
                    blessing_chance = random.randint(1, 1000)
                    num_reward = 1
                    reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                    if blessing_chance <= 1 and active_room.deity_tier >= 5:
                        reward_id = f"I{active_room.deity_tier}x"
                        item_msg = f"{loot.get_loot_emoji(reward_id)} 1x {loot.get_loot_name(reward_id)}"
                        self.embed.add_field(name="Ultimate Blessing Received!", value="", inline=False)
                        inventory.update_stock(reload_player, reward_id, num_reward)
                    elif blessing_chance <= 11:
                        deity_numeral = tarot.tarot_numeral_list(tarot.get_number_by_tarot(active_room.room_deity))
                        reward_id = f"t{deity_numeral}"
                        item_msg = f"{loot.get_loot_emoji(reward_id)} 1x {loot.get_loot_name(reward_id)}"
                        self.embed.add_field(name=f"{active_room.room_deity}'s Blessing Received!",
                                                    value="", inline=False)
                        inventory.update_stock(reload_player, reward_id, num_reward)
                    elif blessing_chance <= 111:
                        reward_id = f"I{active_room.room_tier}t"
                        item_msg = f"{loot.get_loot_emoji(reward_id)} 1x {loot.get_loot_name(reward_id)}"
                        self.embed.add_field(name="Blessing Received!", value=item_msg, inline=False)
                        inventory.update_stock(reload_player, reward_id, num_reward)
                    else:
                        self.embed.add_field(name="Nothing happens.", value="Better keep moving.", inline=False)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Destroy", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def destroy_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    event_chance = random.randint(1, 100)
                    reward_outcome = [1, 1, 1, 2, 2, 3]
                    num_reward = reward_outcome[random.randint(0, 5)]
                    reward_tier = int((self.expedition.expedition_tier + 1) / 2)
                    reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                    if event_chance <= 10:
                        embed_title = f"Incurred __{active_room.room_deity}'s__ wrath!"
                        wrath_msg = wrath_msg_list[tarot.get_number_by_tarot(active_room.room_deity)]
                        self.new_view = None
                        self.embed.add_field(name=f"{embed_title} - Run Ended", value=wrath_msg, inline=False)
                    else:
                        if event_chance <= 40:
                            if event_chance <= 15:
                                random_item = random.randint(0, 1)
                                if random_item == 0:
                                    reward_id = f"I{reward_tier}b"
                                    reward_type = "Ore"
                                else:
                                    reward_id = f"I{reward_tier}c"
                                    reward_type = "Soul"
                                embed_title = f"Excavated {num_reward} {reward_type}s!"
                            else:
                                embed_title = f"Excavated {num_reward} Energy!"
                                reward_id = f"I{reward_tier}a"
                            item_msg = f"{loot.get_loot_emoji(reward_id)} {num_reward} {loot.get_loot_name(reward_id)}"
                            self.embed.add_field(name=embed_title, value=item_msg, inline=False)
                            inventory.update_stock(reload_player, reward_id, num_reward)
                        else:
                            self.embed.add_field(name="Nothing happens.", value="Better keep moving.", inline=False)
                        self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class TreasureRoomView(discord.ui.View):
    def __init__(self,  expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Open Chest", style=discord.ButtonStyle.success, emoji="⚔️")
    async def chest_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    self.embed = active_room.embed
                    if active_room.check_trap():
                        if active_room.room_type == "l":
                            damage = self.expedition.take_damage(100, 300, active_room.room_element)
                            if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                                self.expedition.player_object.player_cHP = 0
                                hp_msg = f'0 / {self.expedition.player_object.player_mHP} HP'
                                self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                                death_header, death_msg = death_embed()
                                self.embed.add_field(name=death_header, value=death_msg, inline=False)
                                self.new_view = None
                            else:
                                if self.expedition.player_object.immortal:
                                    self.expedition.player_object.player_cHP = 1
                                dmg_msg = f'The mimic bites you dealing {damage:,} damage.'
                                self.embed.add_field(name="", value=dmg_msg, inline=False)
                                hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                                self.embed.add_field(name="", value=hp_msg, inline=False)
                                self.new_view = TransitionView(self.expedition)
                        else:
                            trap_msg = "You have fallen for the ultimate elder mimic's clever ruse!"
                            self.embed.add_field(name="Eaten - Run Ended", value=trap_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                    else:
                        reward_tier = inventory.generate_random_tier()
                        for x in range(1, self.expedition.expedition_tier):
                            random_tier = inventory.generate_random_tier()
                            if random_tier > reward_tier:
                                reward_tier = random_tier
                                if reward_tier == 4:
                                    break
                        reward_item = inventory.CustomItem(self.expedition.player_object.player_id,
                                                           active_room.reward_type, reward_tier)
                        self.embed = reward_item.create_citem_embed()
                        self.new_view = ItemView(self.expedition, reward_item)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Move On", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def move_on_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed, self.new_view = self.expedition.display_next_room()
                    self.expedition.current_room_num += 1
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class ItemView(discord.ui.View):
    def __init__(self, expedition, item):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.item = item
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Claim Item", style=discord.ButtonStyle.blurple, emoji="➕")
    async def claim_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    if not inventory.if_custom_exists(self.item.item_id):
                        result_id = inventory.inventory_add_custom_item(self.item)
                        self.item.item_id = result_id
                        self.new_view = TransitionView(self.expedition)
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Item Claimed!",
                                                   description=f"The item has been placed in your inventory.")
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Sell Item", style=discord.ButtonStyle.success, emoji="💲")
    async def sell_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.new_view = TransitionView(self.expedition)
                    sell_value = self.item.item_tier * 250
                    user = player.get_player_by_id(self.expedition.player_object.player_id)
                    user.player_coins += sell_value
                    user.set_player_field("player_coins", user.player_coins)
                    self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                               title="Item Sold!",
                                               description=f"{pandorabot.coin_icon} {sell_value}x Lotus coins acquired.")
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class GoldenRoomView(discord.ui.View):
    def __init__(self,  expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Collect", style=discord.ButtonStyle.success, emoji="💲")
    async def collect(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.expedition_rooms[self.expedition.current_room_num]
                    reward_coins = 10000 * self.expedition.expedition_tier
                    title_msg = "Treasures Obtained!"
                    description_msg = f"You acquired {pandorabot.coin_icon} {reward_coins}x lotus coins!"
                    bonus_coins = 0
                    random_num = random.randint(1, 1000)
                    reward_title = ""
                    if random_num <= 1:
                        bonus_coins = random.randint(500000, 1000000)
                        reward_title = "Ultimate Jackpot!!!!"
                    elif random_num <= 11:
                        bonus_coins = random.randint(100000, 250000)
                        reward_title = "Greater Jackpot!!!"
                    elif random_num <= 41:
                        bonus_coins = random.randint(50000, 100000)
                        reward_title = "Standard Jackpot!!"
                    elif random_num <= 91:
                        bonus_coins = random.randint(1, 50000)
                        reward_title = "Lesser Jackpot!"
                    self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                               title=title_msg, description=description_msg)
                    if reward_title != "":
                        reward_msg = f"Acquired {pandorabot.coin_icon} {bonus_coins}x bonus lotus coins!"
                        self.embed.add_field(name=reward_title, value=reward_msg, inline=False)
                        reward_coins += bonus_coins
                    reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                    reload_player.player_coins += reward_coins
                    reload_player.set_player_field("player_coins", reload_player.player_coins)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


def death_embed():
    random_msg = random.randint(0, (len(death_msg_list) - 1))
    death_header = "The voice of __Thana, The Death__ echoes through your mind"
    death_msg = death_msg_list[random_msg]
    return death_header, death_msg
