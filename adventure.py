import random
import discord
import pandas as pd
import numpy

import globalitems
import inventory
import loot
import menus
import pandorabot
import player
import tarot

map_tier_dict = {"Ancient Ruins": 1, "Spatial Dungeon": 2, "Starlit Temple": 3,
                 "Celestial Labyrinth": 4, "Dimensional Spire": 5, "Chaos Rift": 6}
random_room_list = ["trap_room", "statue_room", "treasure", "trial_room", "sanctuary_room", "penetralia_room",
                    "healing_room", "greater_treasure", "basic_monster", "elite_monster", "jackpot_room"]
death_msg_list = ["Back so soon? I think I'll play with you a little longer.", "Death is not the end.",
                  "Can't have you dying before the prelude now can we?", "I will overlook this, just this once. "
                  "I'll have you repay this favour to me when the time is right.",
                  "I wouldn't mind helping you for a price, but does your life truly hold any value?"]
eleuia_msg_list = ["If you want something you need to wish for it. What is it you really want?",
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

trial_variants_dict = {"Offering": ["Pay with your life.", ["Pain (30%)", "Blood (60%)", "Death (90%)"],
                                    ["🗡️", "💧", "💀"]],
                       "Greed": ["Pay with your wealth.", ["Poor (1,000)", "Affluent (5,000)", "Rich (10,000)"],
                                    ["💸", "💍", "👑"]],
                       "Soul": ["Pay with your stamina.", ["Vitality (100)", "Spirit (300)", "Essence (500)"],
                                 ["🟢", "🟡", "🔴"]]
                       }

reward_probabilities = [1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10]


class Expedition:
    def __init__(self, player_object, expedition_tier, room_colour):
        self.expedition_tier = expedition_tier
        self.luck = self.expedition_tier
        self.player_object = player_object
        self.expedition_length = 8 + expedition_tier
        self.expedition_colour = room_colour
        self.current_room_num = 0
        self.current_room = None
        self.current_room_view = None

    def random_room(self):
        random_room = random.randint(0, (len(random_room_list) - 2))
        random_jackpot = random.randint(1, 1000)
        output_room_type = random_room_list[random_room]
        if random_jackpot <= (5 * self.luck):
            output_room_type = "jackpot_room"
        return output_room_type

    def generate_room_view(self, room_type, variant):
        match room_type:
            case "trap_room":
                new_view = TrapRoomView(self)
            case "statue_room":
                new_view = StatueRoomView(self)
            case "healing_room":
                new_view = HealRoomView(self)
            case "treasure" | "greater_treasure":
                new_view = TreasureRoomView(self)
            case "basic_monster" | "elite_monster":
                new_view = MonsterRoomView(self)
            case "sanctuary_room":
                new_view = SanctuaryRoomView(self)
            case "trial_room":
                new_view = TrialRoomView(self, variant)
            case "penetralia_room" | "jackpot_room":
                new_view = GoldenRoomView(self, room_type)
            case _:
                new_view = None
                print("Error!")
        return new_view

    def display_next_room(self):
        if self.current_room_num + 1 < self.expedition_length:
            new_room_num = self.current_room_num + 1
            # Generate Room
            new_room_type = self.random_room()
            new_room = Room(new_room_type, self.expedition_tier, self.expedition_colour)
            new_room.prepare_room(self)
            # Generate View
            new_view = self.generate_room_view(new_room_type, new_room.room_variant)
            # Build Embed
            embed_msg = new_room.embed
            hp_msg = globalitems.display_hp(self.player_object.player_cHP, self.player_object.player_mHP)
            embed_msg.add_field(name="", value=hp_msg, inline=False)
            # Store the new current room information
            self.current_room = new_room
            self.current_room_view = new_view
        else:
            embed_msg = discord.Embed(colour=self.expedition_colour,
                                      title="Expedition Completed!",
                                      description="Would you like to embark on another expedition?")
            reload_player = player.get_player_by_id(self.player_object.player_id)
            new_view = MapSelectView(reload_player, embed_msg)
        return embed_msg, new_view

    def teleport(self):
        self.current_room_num = random.randint(0, (self.expedition_length - 1))

    def take_damage(self, min_dmg, max_dmg, dmg_element):
        damage = random.randint(min_dmg, max_dmg) * self.expedition_tier
        player_mitigation = self.player_object.damage_mitigation
        player_resist = 0
        if dmg_element != -1:
            player_resist = self.player_object.elemental_resistance[dmg_element]
        damage -= damage * player_resist
        damage -= damage * player_mitigation * 0.01
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
        self.room_variant = ""
        self.reward_type = "W"
        self.room_element = random.randint(0, 8)
        random_deity = random.randint(0, 22)
        self.room_deity = tarot.tarot_card_list(random_deity)
        self.deity_tier = tarot.get_tarot_tier(self.room_deity)

    def prepare_room(self, expedition):
        random_check = random.randint(1, 100)
        match self.room_type:
            case "trap_room":
                title_msg = trap_roomname_list[self.room_element]
                description_msg = "Something about this room has you on edge."
            case "statue_room":
                title_msg = "Statue Room"
                description_msg = f"A statue of {self.room_deity} stands before you."
            case "healing_room":
                title_msg = "Safe Room"
                random_msg = safe_room_msg[random.randint(0, (len(safe_room_msg) - 1))]
                description_msg = random_msg
            case "treasure":
                if random_check <= 60:
                    self.reward_type = "A"
                elif random_check <= 90:
                    self.reward_type = "W"
                else:
                    self.reward_type = "Y"
                title_msg = f"Lesser {inventory.custom_item_dict[self.reward_type]} Treasure Chamber"
                description_msg = "The unopened chest calls to you."
            case "greater_treasure":
                if random_check < 50:
                    self.reward_type = "A"
                elif random_check < 80:
                    self.reward_type = "W"
                else:
                    self.reward_type = "Y"
                title_msg = f"Greater {inventory.custom_item_dict[self.reward_type]} Treasure Vault"
                description_msg = "The irresistible allure of treasure entices you."
            case "basic_monster":
                title_msg = "Monster Encounter"
                random_monster = random.randint(1, (len(basic_monster_list) - 1))
                monster = basic_monster_list[random_monster]
                element_descriptor = element_descriptor_list[self.room_element]
                if element_descriptor[0].lower() in vowel_list:
                    prefix = "An"
                else:
                    prefix = "A"
                description_msg = f"{prefix} {element_descriptor} {monster} blocks your path."
            case "elite_monster":
                title_msg = "Elite Monster Encounter"
                random_monster = random.randint(1, (len(elite_monster_list) - 1))
                monster = elite_monster_list[random_monster]
                element_descriptor = element_descriptor_list[self.room_element]
                if element_descriptor[0].lower() in vowel_list:
                    prefix = "An"
                else:
                    prefix = "A"
                description_msg = f"{prefix} {element_descriptor} {monster} blocks your path."
            case "penetralia_room":
                title_msg = "Secret Penetralia"
                description_msg = (f"This room is well hidden, "
                                   f"there must be something good inside somebody doesn't want you to find!")
            case "jackpot_room":
                title_msg = "Golden Penetralia!"
                description_msg = f"Riches spread all across the secret room. Ripe for the taking!"
            case "sanctuary_room":
                title_msg = "Butterfae Sanctuary"
                description_msg = "A wondrous room illuminated by the light of hundreds of elemental butterfaes"
            case "trial_room":
                self.room_variant = random.choice(list(trial_variants_dict.keys()))
                trial_type = trial_variants_dict[self.room_variant]
                title_msg = f"Trial of {self.room_variant}"
                description_msg = f"{trial_type[0]}\n{', '.join(trial_type[1])}"
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
            case "trap_room":
                is_trap = True
            case "treasure":
                if trap_check <= 25:
                    is_trap = True
            case "healing_room":
                if trap_check <= 25:
                    is_trap = True
            case "greater_treasure":
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
                        self.paid = True
                        if reload_user.player_echelon == 0:
                            reload_user.update_tokens(2, 1)
                        reload_user.get_equipped()
                        reload_user.get_player_multipliers()
                        new_expedition = Expedition(reload_user, self.selected_tier, self.colour)
                        new_expedition.display_next_room()
                        new_view = new_expedition.current_room_view
                        new_embed = new_expedition.current_room.embed
                        await interaction.response.edit_message(embed=new_embed, view=new_view)
                    else:
                        self.embed_msg.clear_fields()
                        self.embed_msg.add_field(name="Not Enough Stamina!", value="Please check your /stamina!")
                        await interaction.response.edit_message(embed=self.embed_msg, view=self)
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
                    regen_bonus = self.expedition.player_object.hp_regen
                    if regen_bonus > 0:
                        regen_amount = int(self.expedition.player_object.player_cHP * regen_bonus)
                        self.expedition.player_object.player_cHP += regen_amount
                        if self.expedition.player_object.player_cHP > self.expedition.player_object.player_mHP:
                            self.expedition.player_object.player_cHP = self.expedition.player_object.player_mHP
                        hp_msg = (f'Regen: +{regen_amount}\n'
                                  f'{globalitems.display_hp(self.expedition.player_object.player_cHP, self.expedition.player_object.player_mHP)} HP')
                        self.embed.add_field(name="", value=hp_msg, inline=False)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class HealRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Short Rest", style=discord.ButtonStyle.blurple, emoji="➕")
    async def short_rest_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    self.embed.clear_fields()
                    if active_room.check_trap():
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Recovery Failed!",
                                                   description="Nothing good will come from staying any longer.")
                        self.new_view = TransitionView(self.expedition)
                    else:
                        heal_amount = random.randint(self.expedition.expedition_tier, (10 + self.expedition.luck))
                        heal_total = int(self.expedition.player_object.player_mHP * (heal_amount * 0.01))
                        self.expedition.player_object.player_cHP += heal_total
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Recovery Successful!",
                                                   description=f"You restore {heal_total} HP.")
                        if self.expedition.player_object.player_cHP > self.expedition.player_object.player_mHP:
                            self.expedition.player_object.player_cHP = self.expedition.player_object.player_mHP
                        hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP, self.expedition.player_object.player_mHP)
                        self.embed.add_field(name="", value=hp_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Long Rest", style=discord.ButtonStyle.blurple, emoji="➕")
    async def long_rest_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    self.embed.clear_fields()
                    heal_amount = random.randint(self.expedition.expedition_tier, (10 + self.expedition.luck))
                    heal_total = int(self.expedition.player_object.player_mHP * (heal_amount * 0.01)) * 2
                    if active_room.check_trap():
                        damage = heal_total
                        damage = self.expedition.take_damage(damage, damage, active_room.room_element)
                        dmg_msg = f'You took {damage:,} damage.'
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Ambushed!",
                                                   description=f"You were attacked while resting! {dmg_msg}")
                        if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                            self.expedition.player_object.player_cHP = 0
                            hp_msg = globalitems.display_hp(0, self.expedition.player_object.player_mHP)
                            self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                        else:
                            if self.expedition.player_object.immortal and self.expedition.player_object.player_cHP < 1:
                                self.expedition.player_object.player_cHP = 1
                            hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP,
                                                            self.expedition.player_object.player_mHP)
                            self.embed.add_field(name="", value=hp_msg, inline=False)
                            self.new_view = TransitionView(self.expedition)
                    else:
                        self.expedition.player_object.player_cHP += heal_total
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Recovery Successful!",
                                                   description=f"You restore **{heal_total}** HP.")
                        if self.expedition.player_object.player_cHP > self.expedition.player_object.player_mHP:
                            self.expedition.player_object.player_cHP = self.expedition.player_object.player_mHP
                        hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP,
                                                        self.expedition.player_object.player_mHP)
                        self.embed.add_field(name="", value=hp_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
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
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    self.embed.clear_fields()
                    # Set modifiers
                    monster_adjuster = 1
                    if active_room.room_type == "elite_monster":
                        monster_adjuster = 2
                    min_dmg = 100 * monster_adjuster
                    max_dmg = 300 * monster_adjuster
                    luck_adjuster = 2 / monster_adjuster
                    exp_reward = 100 * monster_adjuster * self.expedition.expedition_tier
                    exp_reward += 25 * monster_adjuster * self.expedition.luck
                    unscathed_roll = random.randint(1, 100)
                    unscathed = int(self.expedition.luck * luck_adjuster)
                    # Check if unscathed
                    if unscathed_roll < unscathed:
                        dmg_msg = f'You emerge unscathed from combat.'
                        self.embed.add_field(name="Monster Defeated!", value=dmg_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
                    else:
                        # Handle damage
                        damage = self.expedition.take_damage(min_dmg, max_dmg, active_room.room_element)
                        dmg_msg = f'You took {damage:,} damage.'
                        if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                            self.expedition.player_object.player_cHP = 0
                            hp_msg = globalitems.display_hp(0, self.expedition.player_object.player_mHP)
                            self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                        else:
                            if self.expedition.player_object.immortal and self.expedition.player_object.player_cHP < 1:
                                self.expedition.player_object.player_cHP = 1
                            self.embed.add_field(name="Monster Defeated!", value=dmg_msg, inline=False)
                            hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP, self.expedition.player_object.player_mHP)
                            self.embed.add_field(name="", value=hp_msg, inline=False)
                            self.new_view = TransitionView(self.expedition)
                            # Award experience
                            user = player.get_player_by_id(self.expedition.player_object.player_id)
                            user.player_exp += exp_reward
                            user.set_player_field("player_exp", user.player_exp)
                            exp_msg = f"{globalitems.exp_icon} {exp_reward}x Exp Acquired."
                            self.embed.add_field(name="", value=exp_msg, inline=False)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Stealth", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def stealth_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    self.embed.clear_fields()
                    monster_adjuster = 1
                    if active_room.room_type == "elite_monster":
                        monster_adjuster = 2
                    min_dmg = 100 * monster_adjuster
                    max_dmg = 300 * monster_adjuster
                    stealth_success_rate = (50 / monster_adjuster) + (self.expedition.luck * (2 / monster_adjuster))
                    stealth_fail_multiplier = 1 + (0.5 * monster_adjuster)
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
                            hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP, self.expedition.player_object.player_mHP)
                            self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                            death_header, death_msg = death_embed()
                            self.embed.add_field(name=death_header, value=death_msg, inline=False)
                            self.new_view = None
                        else:
                            if self.expedition.player_object.immortal and self.expedition.player_object.player_cHP < 1:
                                self.expedition.player_object.player_cHP = 1
                            hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP,
                                                            self.expedition.player_object.player_mHP)
                            self.embed.add_field(name="Stealth Failed", value=f"{dmg_msg}\n{hp_msg}", inline=False)
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

    @discord.ui.button(label="Search", style=discord.ButtonStyle.success, emoji="⚔️")
    async def detect_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    self.embed.clear_fields()
                    player_resist = self.expedition.player_object.elemental_resistance[active_room.room_element]
                    player_resist += self.expedition.player_object.all_elemental_resistance
                    trap_trigger = random.randint(1, 100)
                    if trap_trigger <= player_resist + self.expedition.luck:
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Trap Detected!",
                                                   description="You become aware of the trap and avoid it.")
                        hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP, self.expedition.player_object.player_mHP)
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
                                self.expedition.teleport()
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
                                    if self.expedition.player_object.immortal and self.expedition.player_object.player_cHP < 1:
                                        self.expedition.player_object.player_cHP = 1
                                    hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP, self.expedition.player_object.player_mHP)
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
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    self.embed.clear_fields()
                    blessing_chance = random.randint(1, 100)
                    num_reward = 1
                    blessing_msg = ""
                    reward_id = ""
                    reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                    if active_room.deity_tier == 6:
                        if blessing_chance <= 5:
                            reward_id = f"i6x"
                            blessing_msg = "Miraculous Blessing\nLuck +7"
                            self.expedition.luck += 7
                        elif blessing_chance <= 10:
                            reward_id = "i6t"
                            blessing_msg = "Sovereign's Blessing!\nLuck +5"
                            self.expedition.luck += 5
                    if active_room.deity_tier == 5:
                        if blessing_chance <= 5:
                            reward_id = f"i5u"
                            blessing_msg = "Fabled Blessing\nLuck +3"
                            self.expedition.luck += 3
                        elif blessing_chance <= 10:
                            reward_id = "i5t"
                            blessing_msg = "Superior Blessing!\nLuck +2"
                            self.expedition.luck += 2
                    if reward_id == "":
                        blessing_chance = random.randint(1, 100)
                        if blessing_chance <= 5:
                            deity_numeral = tarot.tarot_numeral_list(tarot.get_number_by_tarot(active_room.room_deity))
                            reward_id = f"t{deity_numeral}"
                            blessing_msg = f"{active_room.room_deity}'s Blessing!\nLuck +2"
                            self.expedition.luck += 2
                        elif blessing_chance <= 30:
                            reward_id = "i4t"
                            blessing_msg = "Paragon's Blessing!\nLuck +1"
                            self.expedition.luck += 1
                    if reward_id != "":
                        loot_item = loot.BasicItem(reward_id)
                        item_msg = f"{loot_item.item_emoji} 1x {loot_item.item_name} received!"
                        self.embed.add_field(name=blessing_msg, value=item_msg, inline=False)
                        inventory.update_stock(reload_player, reward_id, num_reward)
                    else:
                        heal_amount = random.randint(self.expedition.expedition_tier, 10)
                        heal_total = int(self.expedition.player_object.player_mHP * (heal_amount * 0.01))
                        self.expedition.player_object.player_cHP += heal_total
                        if self.expedition.player_object.player_cHP > self.expedition.player_object.player_mHP:
                            self.expedition.player_object.player_cHP = self.expedition.player_object.player_mHP
                        hp_msg = f'{self.expedition.player_object.player_cHP} / {self.expedition.player_object.player_mHP} HP'
                        self.embed.add_field(name="Health Restored", value=hp_msg, inline=False)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Destroy", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def destroy_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    self.new_view = TransitionView(self.expedition)
                    event_chance = random.randint(1, 1000)
                    if event_chance <= 50:
                        embed_title = f"Incurred __{active_room.room_deity}'s__ wrath!"
                        wrath_msg = wrath_msg_list[tarot.get_number_by_tarot(active_room.room_deity)]
                        self.new_view = None
                        self.embed.add_field(name=f"{embed_title} - Run Ended", value=wrath_msg, inline=False)
                    elif event_chance <= 550 + (self.expedition.luck * 10):
                        reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                        reward_id, reward_qty = loot.generate_random_item()
                        loot_item = loot.BasicItem(reward_id)
                        embed_title = f"Excavated {loot_item.item_name}!"
                        item_msg = f"{loot_item.item_emoji} {reward_qty} {loot_item.item_name} found in the rubble!"
                        self.embed.add_field(name=embed_title, value=item_msg, inline=False)
                        inventory.update_stock(reload_player, reward_id, reward_qty)
                    else:
                        self.embed.add_field(name="Nothing happens.", value="Better keep moving.", inline=False)
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
                    active_room = self.expedition.current_room
                    self.embed = active_room.embed
                    if active_room.check_trap():
                        if active_room.room_type == "treasure":
                            damage = self.expedition.take_damage(100, 300, active_room.room_element)
                            if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                                self.expedition.player_object.player_cHP = 0
                                hp_msg = globalitems.display_hp(0, self.expedition.player_object.player_mHP)
                                self.embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                                death_header, death_msg = death_embed()
                                self.embed.add_field(name=death_header, value=death_msg, inline=False)
                                self.new_view = None
                            else:
                                if self.expedition.player_object.immortal and self.expedition.player_object.player_cHP < 1:
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
                        if self.expedition.expedition_tier >= 4:
                            fragment_roller = random.randint(0, (self.expedition.luck + 3))
                            if active_room.room_type == "greater_treasure":
                                bonus_check = random.randint(0, (self.expedition.luck + 3))
                                fragment_roller = max(fragment_roller, bonus_check)
                            if fragment_roller < len(reward_probabilities):
                                num_fragments = reward_probabilities[fragment_roller]
                            else:
                                num_fragments = 10
                            fragment_id = f"i5a{active_room.reward_type}"
                            reward_item = loot.BasicItem(fragment_id)
                            loot_msg = f"{reward_item.item_emoji} {num_fragments}x {reward_item.item_name}"
                            self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                       title="Fragments Acquired!",
                                                       description=loot_msg)
                            update_stock = inventory.update_stock(self.expedition.player_object,
                                                                  reward_item.item_id, num_fragments)
                            self.new_view = TransitionView(self.expedition)
                        else:
                            reward_tier = inventory.generate_random_tier()
                            for x in range(1, self.expedition.luck):
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
                        if result_id == 0:
                            self.embed = inventory.full_inventory_embed(self.item, self.expedition.expedition_colour)
                        else:
                            self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                       title=f"Item Claimed!",
                                                       description=f"The item ID:{result_id} has been placed in your inventory.")
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Sell Item", style=discord.ButtonStyle.success, emoji="💲")
    async def sell_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.new_view = TransitionView(self.expedition)
                    sell_value = self.item.item_tier * 500
                    user = player.get_player_by_id(self.expedition.player_object.player_id)
                    user.player_coins += sell_value
                    user.set_player_field("player_coins", user.player_coins)
                    self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                               title="Item Sold!",
                                               description=f"{globalitems.coin_icon} {sell_value}x Lotus coins acquired.")
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class TrialRoomView(discord.ui.View):
    def __init__(self, expedition, variant):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None
        self.variant = variant
        trial_details = trial_variants_dict[variant]
        variant_index = list(trial_variants_dict.keys()).index(variant)
        self.option1.label = trial_details[1][0]
        self.option1.emoji = trial_details[2][0]
        self.option1.style = globalitems.button_colour_list[variant_index]
        self.option2.label = trial_details[1][1]
        self.option2.emoji = trial_details[2][1]
        self.option2.style = globalitems.button_colour_list[variant_index]
        self.option3.label = trial_details[1][2]
        self.option3.emoji = trial_details[2][2]
        self.option3.style = globalitems.button_colour_list[variant_index]

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.option1_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.option2_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.option3_callback(interaction, button)

    async def option1_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                    self.embed = self.run_option_button(reload_player, 1)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def option2_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                    self.embed = self.run_option_button(reload_player, 2)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def option3_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    reload_player = player.get_player_by_id(self.expedition.player_object.player_id)
                    self.embed = self.run_option_button(reload_player, 3)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    def run_option_button(self, reload_player, option_selected):
        completed_msg = "Cost could not be paid. Nothing Gained."
        output_msg = ""
        match self.expedition.current_room.room_variant:
            case "Offering":
                cost = int(0.3 * option_selected * self.expedition.player_object.player_mHP)
                if cost < self.expedition.player_object.player_cHP:
                    self.expedition.player_object.player_cHP -= cost
                    completed_msg = ""
                    hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP,
                                                    self.expedition.player_object.player_mHP)
                    output_msg = f"Sacrificed {cost} HP\n{hp_msg}\nGained +{(1 + 2 * (option_selected - 1))} luck!"
            case "Greed":
                cost_list = [1000, 5000, 10000]
                cost = cost_list[(option_selected - 1)]
                if reload_player.player_coins >= cost:
                    reload_player.player_coins -= cost
                    reload_player.set_player_field("player_coins", reload_player.player_coins)
                    completed_msg = ""
                    output_msg = (f"Sacrificed {cost} lotus coins\nRemaining: {reload_player.player_coins}\n"
                                  f"Gained +{(1 + 2 * (option_selected - 1))} luck!")
            case "Soul":
                cost = int(100 + 200 * (option_selected - 1))
                if reload_player.player_stamina >= cost:
                    reload_player.player_stamina -= cost
                    reload_player.set_player_field("player_stamina", reload_player.player_stamina)
                    completed_msg = ""
                    output_msg = (f"Sacrificed {cost} stamina\nRemaining: {reload_player.player_stamina}\n"
                                  f"Gained +{(1 + 2 * (option_selected - 1))} luck!")
            case _:
                pass
        if completed_msg == "":
            embed_msg = discord.Embed(colour=self.expedition.expedition_colour,
                                      title="Trial Passed!", description=output_msg)
        else:
            embed_msg = discord.Embed(colour=self.expedition.expedition_colour,
                                      title="Trial Failed!", description=completed_msg)
        return embed_msg


class SanctuaryRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None
        self.random_numbers = random.sample(range(9), 3)
        rare_occurrence = random.randint(1, 1000)
        if rare_occurrence <= self.expedition.luck:
            self.item_type = "Origin"
            item_icon = [globalitems.global_element_list[self.random_numbers[0]],
                         globalitems.global_element_list[self.random_numbers[1]],
                         globalitems.global_element_list[self.random_numbers[2]]]
        else:
            self.item_type = "Cores"
            item_icon = [globalitems.global_element_list[self.random_numbers[0]],
                         globalitems.global_element_list[self.random_numbers[1]],
                         globalitems.global_element_list[self.random_numbers[2]]]
        self.option1.label = f"{globalitems.element_names[self.random_numbers[0]]} {self.item_type}"
        self.option1.emoji = item_icon[0]
        self.option2.label = f"{globalitems.element_names[self.random_numbers[1]]} {self.item_type}"
        self.option2.emoji = item_icon[1]
        self.option3.label = f"{globalitems.element_names[self.random_numbers[2]]} {self.item_type}"
        self.option3.emoji = item_icon[2]

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.option1_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.option2_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.option3_callback(interaction, button)

    async def option1_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.run_option_button(0)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def option2_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.run_option_button(1)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def option3_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.run_option_button(2)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    def run_option_button(self, option_selected):
        id_type = ""
        if self.item_type == "Cores":
            id_type = "Fae"
            quantity = random.randint((1 + self.expedition.luck), (5 + self.expedition.luck))
        elif self.item_type == "Origin":
            id_type = "Origin"
            quantity = 1
        item_id = f"{id_type}{self.random_numbers[option_selected]}"
        inventory.update_stock(self.expedition.player_object, item_id, quantity)
        output_msg = (f"{globalitems.global_element_list[self.random_numbers[option_selected]]} "
                      f"{quantity}x Fae Core ({globalitems.element_names[self.random_numbers[option_selected]]})")
        embed_msg = discord.Embed(colour=self.expedition.expedition_colour,
                                  title="Cores Collected!", description=output_msg)
        return embed_msg


class GoldenRoomView(discord.ui.View):
    def __init__(self,  expedition, room_type):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.room_type = room_type
        self.embed = None
        self.new_view = None

    @discord.ui.button(label="Collect", style=discord.ButtonStyle.success, emoji="💲")
    async def collect(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    active_room = self.expedition.current_room
                    if self.room_type == "jackpot_room":
                        base_coins = 10000
                        jackpot_chance = 50 * self.expedition.luck
                    else:
                        base_coins = random.randint(100, 2000)
                        jackpot_chance = 5 * self.expedition.luck
                    reward_coins = base_coins * self.expedition.luck
                    title_msg = "Treasures Obtained!"
                    description_msg = f"You acquired {globalitems.coin_icon} {reward_coins}x lotus coins!"
                    bonus_coins = 0
                    random_num = random.randint(1, 1000)
                    reward_title = ""
                    jackpot_available = random.randint(1, 1000)
                    if jackpot_available <= jackpot_chance:
                        jackpot_rates = [1, 10, 30, 50]
                        jackpot_check = [sum(jackpot_rates[:i+1]) + (i + 1) * self.expedition.luck for i in range(len(jackpot_rates))]
                        if random_num <= jackpot_check[0]:
                            bonus_coins = random.randint(500000, 1000000)
                            reward_title = "Ultimate Jackpot!!!!"
                        elif random_num <= jackpot_check[1]:
                            bonus_coins = random.randint(100000, 250000)
                            reward_title = "Greater Jackpot!!!"
                        elif random_num <= jackpot_check[2]:
                            bonus_coins = random.randint(50000, 100000)
                            reward_title = "Standard Jackpot!!"
                        elif random_num <= jackpot_check[3]:
                            bonus_coins = random.randint(10000, 50000)
                            reward_title = "Lesser Jackpot!"
                    self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                               title=title_msg, description=description_msg)
                    if reward_title != "":
                        reward_msg = f"Acquired {globalitems.coin_icon} {bonus_coins}x bonus lotus coins!"
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


def build_manifest_return_embed(player_object, method, colour):
    temp_dict = {}
    method_info = method.split(";")
    description_msg = ""
    card_stars = int(method_info[2])
    success_rate = 50 + card_stars * 5
    if method_info[1] != "-1":
        title_msg = f"Echo of __{method_info[1]}__ - Returns ({method_info[0]})"
    else:
        title_msg = f"Pandora, The Celestial Returns"
    if method_info[0] == "Hunt":
        total_exp_gained = 0
        monster_dict = {
            "slime": 50, "bat": 100, "spider": 200, "wolf": 300, "goblin": 400,
            "skeleton": 500, "faerie": 600, "ogre": 700, "harpy": 800, "wraith": 900,
            "lamia": 1000, "lich": 1500, "teyeger": 2000, "minotaur": 2500, "basilisk": 3000,
            "wyrm": 3500, "phoenix": 4000, "chimaera": 4500, "hydra": 5000, "dragon": 9999
        }
        death_dict = {1: "defeated", 2: "slain", 3: "slaughtered", 4: "massacred"}
        for encounter in range(player_object.player_echelon + 5):
            is_success = random.randint(1, 100)
            if is_success <= success_rate:
                enemy_num = random.randint(0, 14)
                enemy_num += random.randint(0, player_object.player_echelon)
                enemy_list = list(monster_dict.keys())
                random_enemy = enemy_list[enemy_num]
                temp_dict[random_enemy] = temp_dict.get(random_enemy, 0) + 1
        temp_dict = dict(sorted(temp_dict.items(), key=lambda m: monster_dict.get(m[0], 0) * m[1], reverse=True))
        for monster_type, num_slain in temp_dict.items():
            exp_total = num_slain * monster_dict.get(monster_type, 0)
            total_exp_gained += exp_total
            if num_slain <= 3:
                death_type = death_dict[num_slain]
            else:
                death_type = death_dict[4]
            monster_line = f"{num_slain}x {monster_type}{'s' if num_slain > 1 else ''} {death_type}!"
            if exp_total > 2000:
                monster_line = f"**{monster_line}**"
            monster_line += "\n"
            description_msg += monster_line
        if not temp_dict:
            description_msg += "No monsters were slain.\n"
        else:
            total_exp_gained += player_object.player_echelon * 500
        description_msg += f"{globalitems.exp_icon} {total_exp_gained:,}x EXP awarded!\n"
        player_object.player_exp += total_exp_gained
        player_object.set_player_field("player_exp", player_object.player_exp)
    elif method_info[0] == "Mine":
        outcome = globalitems.generate_ramping_reward(success_rate, 15, 18)
        if outcome <= player_object.player_echelon:
            outcome = player_object.player_echelon
        outcome_item = globalitems.gem_list[outcome][0]
        outcome_coins = globalitems.gem_list[outcome][1]
        player_object.player_coins += outcome_coins
        player_object.set_player_field("player_coins", player_object.player_coins)
        description_msg += (f"You found a {outcome_item}!"
                            f"\nSold for {globalitems.coin_icon} {outcome_coins}x Lotus Coins!")
    else:
        for x in range(player_object.player_echelon + 4):
            random_attempt = random.randint(1, 100)
            if success_rate <= random_attempt:
                reward_id, num_reward = loot.generate_random_item()
                temp_dict[reward_id] = temp_dict.get(reward_id, 0) + num_reward
        if temp_dict:
            for item_id, item_quantity in temp_dict.items():
                loot_item = loot.BasicItem(item_id)
                inventory.update_stock(player_object, item_id, item_quantity)
                description_msg += f"{loot_item.item_emoji} {item_quantity}x {loot_item.item_name} received!\n"
        else:
            description_msg = "No items found."
    embed_msg = discord.Embed(colour=colour, title=title_msg, description=description_msg)
    return embed_msg


class ManifestView1(discord.ui.View):
    def __init__(self, player_user, embed_msg, e_tarot, colour, num_hours):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg
        self.e_tarot = e_tarot
        self.colour = colour
        self.num_hours = num_hours
        self.paid = False

    @discord.ui.button(label="Hunt", style=discord.ButtonStyle.success, emoji="⚔️")
    async def hunt_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Hunt")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Gather", style=discord.ButtonStyle.secondary, emoji="⚔️", disabled=True)
    async def gather_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Gather")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Mine", style=discord.ButtonStyle.secondary, emoji="⚔️", disabled=True)
    async def mine_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Mine")
        await interaction.response.edit_message(embed=result[0], view=result[1])


class ManifestView2(discord.ui.View):
    def __init__(self, player_user, embed_msg, e_tarot, colour, num_hours):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg
        self.e_tarot = e_tarot
        self.colour = colour
        self.num_hours = num_hours
        self.paid = False

    @discord.ui.button(label="Hunt", style=discord.ButtonStyle.success, emoji="⚔️")
    async def hunt_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Hunt")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Gather", style=discord.ButtonStyle.success, emoji="⚔️")
    async def gather_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Gather")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Mine", style=discord.ButtonStyle.secondary, emoji="⚔️", disabled=True)
    async def mine_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours,
                                 "Mine")
        await interaction.response.edit_message(embed=result[0], view=result[1])


class ManifestView3(discord.ui.View):
    def __init__(self, player_user, embed_msg, e_tarot, colour, num_hours):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg
        self.e_tarot = e_tarot
        self.colour = colour
        self.num_hours = num_hours
        self.paid = False

    @discord.ui.button(label="Hunt", style=discord.ButtonStyle.success, emoji="⚔️")
    async def hunt_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Hunt")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Gather", style=discord.ButtonStyle.success, emoji="⚔️")
    async def gather_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Gather")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Mine", style=discord.ButtonStyle.success, emoji="⚔️")
    async def mine_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = common_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours,
                                 "Mine")
        await interaction.response.edit_message(embed=result[0], view=result[1])


def common_callback(view, player_user, embed_msg, e_tarot, colour, num_hours, method):
    try:
        if not view.paid:
            reload_user = player.get_player_by_id(player_user.player_id)
            existing_timestamp, _ = reload_user.check_cooldown("manifest")
            if existing_timestamp:
                embed_msg.clear_fields()
                embed_msg.add_field(name="In Progress!", value="You've already got a manifestation running!")
                new_view = None
            elif reload_user.spend_stamina(500):
                view.paid = True
                method_info = f"{method};{e_tarot.card_name};{e_tarot.num_stars}"
                reload_user.set_cooldown("manifest", method_info)
                embed_msg = discord.Embed(colour=colour,
                                          title=f"{e_tarot.card_name} Embarks - {method}",
                                          description=f"Expected return time: {num_hours} hours.")
                new_view = None
            else:
                embed_msg.clear_fields()
                embed_msg.add_field(name="Not Enough Stamina!", value="Please check your /stamina!")
                new_view = view
        return embed_msg, new_view
    except Exception as e:
        print(e)


