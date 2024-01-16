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
                    "healing_room", "greater_treasure", "dragon_shrine", "epitaph_room", "selection_room",
                    "basic_monster", "basic_monster", "elite_monster", "jackpot_room"]
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
        self.player_object = player_object
        self.luck = 1 + self.player_object.player_echelon
        self.expedition_length = 9 + expedition_tier
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
            case "dragon_shrine":
                new_view = DragonRoomView(self)
            case "epitaph_room":
                new_view = EpitaphRoomView(self)
            case "selection_room":
                new_view = SelectionRoomView(self)
            case "trial_room":
                new_view = TrialRoomView(self, variant)
            case "penetralia_room" | "jackpot_room":
                new_view = GoldenRoomView(self, room_type)
            case _:
                new_view = None
                print("Error!")
        return new_view

    def display_next_room(self):
        new_room_num = self.current_room_num + 1
        if new_room_num < self.expedition_length:
            # Generate Room
            if new_room_num == (self.expedition_length - 1):
                new_room_type = "greater_treasure"
            else:
                new_room_type = self.random_room()
            new_room = Room(new_room_type, self.expedition_tier, self.expedition_colour)
            new_room.prepare_room(self)
            self.current_room = new_room
            # Generate View
            new_view = self.generate_room_view(new_room_type, new_room.room_variant)
            self.current_room_view = new_view
            # Build Embed
            embed_msg = new_room.embed
            status_msg = globalitems.display_hp(self.player_object.player_cHP, self.player_object.player_mHP)
            status_msg += f"\nLuck: {self.luck}"
            embed_msg.add_field(name="", value=status_msg, inline=False)
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

    def handle_regen(self, embed_msg):
        regen_bonus = self.player_object.hp_regen
        if regen_bonus > 0:
            regen_amount = int(self.player_object.player_cHP * regen_bonus)
            self.player_object.player_cHP += regen_amount
            if self.player_object.player_cHP > self.player_object.player_mHP:
                self.player_object.player_cHP = self.player_object.player_mHP
            hp_msg = (f'Regen: +{regen_amount}\n'
                      f'{globalitems.display_hp(self.player_object.player_cHP, self.player_object.player_mHP)} HP')
            embed_msg.add_field(name="", value=hp_msg, inline=False)
        return embed_msg


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
                description_msg = ("The remains of other fallen adventurers are clearly visible here. "
                                   "Perhaps you can salvage their armour, however the room is making you feel uneasy.")
            case "statue_room":
                title_msg = "Statue Room"
                description_msg = f"A statue of {self.room_deity} stands before you."
            case "healing_room":
                title_msg = "Safe Room"
                random_msg = safe_room_msg[random.randint(0, (len(safe_room_msg) - 1))]
                description_msg = random_msg
            case "treasure":
                if random_check <= 50:
                    self.reward_type = "A"
                elif random_check <= 80:
                    self.reward_type = "W"
                else:
                    self.reward_type = "Y"
                title_msg = f"Lesser {inventory.custom_item_dict[self.reward_type]} Treasure Chamber"
                description_msg = "The unopened chest calls to you."
            case "greater_treasure":
                self.room_variant = "Greater"
                if random_check < 33:
                    self.reward_type = "A"
                elif random_check < 67:
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
                description_msg = "This room is well hidden. Perhaps there are valuable items here."
            case "jackpot_room":
                self.room_variant = "Greater"
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
            case "dragon_shrine":
                element_descriptor = element_descriptor_list[self.room_element]
                self.room_variant = ""
                room_type = random.randint(1, 10)
                if room_type <= 1:
                    self.room_variant = "Greater "
                title_msg = f"{self.room_variant}{element_descriptor} Dragon Shrine"
                description_msg = (f"The shrine awaits the ritual of the challenger. Those who can withstand the "
                                   f"elemental power of a dragon and complete the ritual shall be granted passage.")
            case "epitaph_room":
                title_msg = f"Epitaph Room"
                description_msg = ("You see a tablet inscribed with glowing letters. It will take some time to uncover"
                                   "the message.")
            case "selection_room":
                title_msg = f"Selection Room"
                description_msg = ("Two items sit precariously atop podiums, but it's obviously a trap. "
                                   "Trying to take both seems extremely dangerous.")
            case _:
                title_msg = "ERROR"
                description_msg = "ERROR"
        self.embed = discord.Embed(colour=self.room_colour,
                                   title=title_msg,
                                   description=description_msg)
        return self.embed

    def check_trap(self, luck_value):
        trap_check = random.randint(1, 100)
        is_trap = False
        match self.room_type:
            case "trap_room":
                is_trap = True
            case "treasure":
                if trap_check <= max(0, (25 - luck_value)):
                    is_trap = True
            case "healing_room":
                if trap_check <= max(0, (25 - luck_value)):
                    is_trap = True
            case "greater_treasure":
                if trap_check <= max(0, (15 - luck_value)):
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
        self.new_view = self
        self.selected_tier = selected_tier
        self.colour = colour
        self.paid = None

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
                        self.new_view = new_expedition.current_room_view
                        self.embed_msg = new_expedition.current_room.embed
                    else:
                        self.embed_msg.clear_fields()
                        self.embed_msg.add_field(name="Not Enough Stamina!", value="Please check your /stamina!")
                await interaction.response.edit_message(embed=self.embed_msg, view=self.new_view)
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
                    self.embed = self.expedition.handle_regen(self.embed)
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
                    if active_room.check_trap(self.expedition.luck):
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
                    if active_room.check_trap(self.expedition.luck):
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
        self.monster_adjuster = 1
        self.active_room = self.expedition.current_room
        if self.active_room.room_type == "elite_monster":
            self.monster_adjuster = 2
        self.stealth_chance = int(50 / self.monster_adjuster + (self.expedition.luck * (2 / self.monster_adjuster)))
        self.stealth.label = f"Stealth ({self.stealth_chance}%)"
        self.stealth.emoji = "↩️"
        self.fight.label = "Fight"
        self.fight.emoji = "⚔️"

    @discord.ui.button(style=discord.ButtonStyle.red)
    async def fight(self, interaction: discord.Interaction, button: discord.Button):
        await self.fight_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def stealth(self, interaction: discord.Interaction, button: discord.Button):
        await self.stealth_callback(interaction, button)

    async def stealth_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    min_dmg = 100 * self.monster_adjuster
                    max_dmg = 300 * self.monster_adjuster
                    stealth_fail_multiplier = 1 + (0.5 * self.monster_adjuster)
                    stealth_attempt = random.randint(1, 100)
                    if stealth_attempt <= self.stealth_chance:
                        self.new_view = TransitionView(self.expedition)
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Stealth Successful!",
                                                   description="You have successfully avoided the encounter.")
                    else:
                        damage = self.expedition.take_damage(min_dmg, max_dmg, self.active_room.room_element)
                        dmg_msg = f'You take {damage:,} damage!'
                        if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                            self.expedition.player_object.player_cHP = 0
                            hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP,
                                                            self.expedition.player_object.player_mHP)
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

    async def fight_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    min_dmg = 100 * self.monster_adjuster
                    max_dmg = 300 * self.monster_adjuster
                    luck_adjuster = 2 / self.monster_adjuster
                    exp_reward = 100 * self.monster_adjuster * self.expedition.expedition_tier
                    exp_reward += 25 * self.monster_adjuster * self.expedition.luck
                    unscathed_roll = random.randint(1, 100)
                    unscathed = int(self.expedition.luck * luck_adjuster)
                    # Check if unscathed
                    if unscathed_roll < unscathed:
                        dmg_msg = f'You emerge unscathed from combat.'
                        self.embed.add_field(name="Monster Defeated!", value=dmg_msg, inline=False)
                        self.new_view = TransitionView(self.expedition)
                    else:
                        # Handle damage
                        damage = self.expedition.take_damage(min_dmg, max_dmg, self.active_room.room_element)
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


class TrapRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None
        self.active_room = self.expedition.current_room
        self.player_resist = self.expedition.player_object.elemental_resistance[self.active_room.room_element]
        self.trap_check = min(100, int(self.expedition.luck + (self.player_resist * 100)))
        self.salvage.label = f"Search ({self.trap_check}%)"
        self.bypass.label = f"Bypass"

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def salvage(self, interaction: discord.Interaction, button: discord.Button):
        await self.salvage_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def bypass(self, interaction: discord.Interaction, button: discord.Button):
        await self.bypass_callback(interaction, button)

    async def salvage_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    trap_trigger = random.randint(1, 100)
                    if trap_trigger <= self.trap_check:
                        self.embed, self.new_view = treasure_found(self.expedition, "A")
                    else:
                        self.embed, self.new_view = trap_triggered(self.expedition, self.active_room, self.embed)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def bypass_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed, self.new_view = self.expedition.display_next_room()
                    self.expedition.current_room_num += 1
                    self.embed = self.expedition.handle_regen(self.embed)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class EpitaphRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None
        self.active_room = self.expedition.current_room
        self.item_check = 100
        self.search.label = f"Search ({self.item_check}%)"
        self.decipher_check = 100
        self.decipher.label = f"Decipher ({self.decipher_check}%)"

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def search(self, interaction: discord.Interaction, button: discord.Button):
        await self.search_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="🧩")
    async def decipher(self, interaction: discord.Interaction, button: discord.Button):
        await self.decipher_callback(interaction, button)

    async def search_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    random_num = random.randint(1, 100)
                    if random_num <= self.item_check:
                        self.embed, self.new_view = treasure_found(self.expedition, "W")
                    else:
                        output_msg = "You leave empty handed."
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Search Failed!", description=output_msg)
                        self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def decipher_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    random_num = random.randint(1, 100)
                    if random_num <= self.decipher_check:
                        luck_gained = random.randint(1, 3)
                        self.expedition.luck += luck_gained
                        output_msg = f"**+{luck_gained} Luck**"
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Decryption Success!", description=output_msg)
                        self.new_view = TransitionView(self.expedition)
                    else:
                        output_msg = "You leave empty handed."
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Decryption Failed!", description=output_msg)
                        self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)


class SelectionRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None
        self.active_room = self.expedition.current_room
        self.item_pools = [["i2h", "i1o", "i1s", "i2o", "i2s", "STONE3", "STONE4", "i2y", "i2j", "ESS"],
                           ["i2h", "i3h", "i3o", "i3s", "i3k", "i3f", "i3y", "i3j", "i4t", "i1r", "STONE5", "ESS"],
                           ["i4hA", "i4hB", "i4o", "i4s", "i4p", "i4z", "i4y", "i4w", "i4g", "i4c", "i5t", "i4j", "ESS"],
                           ["i5o", "i5s", "i5l", "i5hA", "i5hB", "i6hZ", "i5u", "i5f", "i6t", "i6m", "i5v", "ESS"],
                           ["i6x", "i5xW", "i5xA", "i5xY", "i5xG", "i5xC", "v6f", "v6p", "v6h", "i5xD", "ESS"],
                           ["m6o", "m6s", "m6z", "m6f", "m6k", "m6h", "m6l", "i6uD", "ESS"],
                           ["v7x", "i6uW"]]
        random_num = random.randint(1, 100000)
        if random_num <= self.expedition.luck:
            reward_tier = 6
        else:
            reward_tier = min(5, self.expedition.luck // 5)
        selected_pool = self.item_pools[reward_tier]
        item_location = random.sample(range(0, (len(selected_pool) - 1)), 2)
        selected_set = [selected_pool[item_location[0]], selected_pool[item_location[1]]]
        selected_set = check_essence(selected_set, reward_tier)
        self.choice_items = [inventory.BasicItem(selected_set[0]),
                             inventory.BasicItem(selected_set[1])]
        self.option1.label = f"{self.choice_items[0].item_name}"
        self.option1.emoji = self.choice_items[0].item_emoji
        self.option1.custom_id = "1"
        self.option2.label = f"{self.choice_items[1].item_name}"
        self.option2.emoji = self.choice_items[1].item_emoji
        self.option2.custom_id = "2"
        self.speed_check = min((self.expedition.luck * 5), 75)
        self.speed.label = f"Both ({self.speed_check}%)"

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.option_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.option_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="🐦")
    async def speed(self, interaction: discord.Interaction, button: discord.Button):
        await self.speed_callback(interaction, button)

    async def option_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    button_id = int(button.custom_id)
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    target_item = self.choice_items[(button_id - 1)]
                    inventory.update_stock(self.expedition.player_object, target_item.item_id, 1)
                    output_msg = f"{target_item.item_emoji} 1x {target_item.item_name} acquired!"
                    self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                               title="Item Selected!", description=output_msg)
                    self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def speed_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    random_outcome = random.randint(1, 100)
                    if random_outcome <= self.speed_check:
                        inventory.update_stock(self.expedition.player_object, self.choice_items[0].item_id, 1)
                        inventory.update_stock(self.expedition.player_object, self.choice_items[1].item_id, 1)
                        output_msg = f"{self.choice_items[0].item_emoji} 1x {self.choice_items[0].item_name} acquired!\n"
                        output_msg += f"{self.choice_items[1].item_emoji} 1x {self.choice_items[1].item_name} acquired!"
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Received Both Items!", description=output_msg)
                        self.new_view = TransitionView(self.expedition)
                    else:
                        self.embed, self.new_view = trap_triggered(self.expedition, self.active_room, self.embed)
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
                            reward_id = f"Crystal1"
                            blessing_msg = "Miraculous Blessing\nLuck +7"
                            self.expedition.luck += 7
                        elif blessing_chance <= 10:
                            reward_id = "Token3"
                            blessing_msg = "Sovereign's Blessing!\nLuck +5"
                            self.expedition.luck += 5
                    if active_room.deity_tier == 5:
                        if blessing_chance <= 5:
                            reward_id = f"Core1"
                            blessing_msg = "Fabled Blessing\nLuck +3"
                            self.expedition.luck += 3
                        elif blessing_chance <= 10:
                            reward_id = "Token2"
                            blessing_msg = "Superior Blessing!\nLuck +2"
                            self.expedition.luck += 2
                    if reward_id == "":
                        blessing_chance = random.randint(1, 100)
                        if blessing_chance <= 5:
                            deity_numeral = tarot.tarot_numeral_list(tarot.get_number_by_tarot(active_room.room_deity))
                            reward_id = f"Essence{deity_numeral}"
                            blessing_msg = f"{active_room.room_deity}'s Blessing!\nLuck +2"
                            self.expedition.luck += 2
                        elif blessing_chance <= 30:
                            reward_id = "Token1"
                            blessing_msg = "Paragon's Blessing!\nLuck +1"
                            self.expedition.luck += 1
                    if reward_id != "":
                        loot_item = inventory.BasicItem(reward_id)
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
                        loot_item = inventory.BasicItem(reward_id)
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
                    if active_room.check_trap(self.expedition.luck):
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
                        self.embed, self.new_view = treasure_found(self.expedition,
                                                                   self.expedition.current_room.reward_type)
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
        luck_gained = 1 + 2 * (option_selected - 1)
        match self.expedition.current_room.room_variant:
            case "Offering":
                cost = int(0.3 * option_selected * self.expedition.player_object.player_mHP)
                if cost < self.expedition.player_object.player_cHP:
                    self.expedition.player_object.player_cHP -= cost
                    completed_msg = ""
                    hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP,
                                                    self.expedition.player_object.player_mHP)
                    output_msg = f"Sacrificed {cost} HP\n{hp_msg}\nGained +{luck_gained} luck!"
            case "Greed":
                cost_list = [1000, 5000, 10000]
                cost = cost_list[(option_selected - 1)]
                if reload_player.player_coins >= cost:
                    reload_player.player_coins -= cost
                    reload_player.set_player_field("player_coins", reload_player.player_coins)
                    completed_msg = ""
                    output_msg = (f"Sacrificed {cost} lotus coins\nRemaining: {reload_player.player_coins}\n"
                                  f"Gained +{luck_gained} luck!")
            case "Soul":
                cost = int(100 + 200 * (option_selected - 1))
                if reload_player.player_stamina >= cost:
                    reload_player.player_stamina -= cost
                    reload_player.set_player_field("player_stamina", reload_player.player_stamina)
                    completed_msg = ""
                    output_msg = (f"Sacrificed {cost} stamina\nRemaining: {reload_player.player_stamina}\n"
                                  f"Gained +{luck_gained} luck!")
            case _:
                pass
        if completed_msg == "":
            self.expedition.luck += luck_gained
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
            quantity = random.randint((1 + self.expedition.luck), (10 + self.expedition.luck))
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


class DragonRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed = None
        self.new_view = None
        self.reward_multiplier = 1
        if self.expedition.current_room.room_variant != "":
            self.reward_multiplier = 2
        self.item = [inventory.BasicItem("Unrefined2"), inventory.BasicItem("Unrefined1"), None]
        self.resistance = [self.expedition.player_object.elemental_resistance[3],
                           self.expedition.player_object.elemental_resistance[4],
                           self.expedition.player_object.elemental_resistance[self.expedition.current_room.room_element]]
        self.success_rate = [min(100, int(resistance * 100) + 5) for resistance in self.resistance]
        self.option1.label = f"Ritual of Land ({self.success_rate[0]}%)"
        self.option1.emoji = globalitems.global_element_list[3]
        self.option2.label = f"Ritual of Sky ({self.success_rate[1]}%)"
        self.option2.emoji = globalitems.global_element_list[4]
        self.option3.label = f"Ritual of Chaos ({self.success_rate[2]}%)"
        self.option3.emoji = globalitems.global_element_list[self.expedition.current_room.room_element]

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
                    self.embed = self.run_option_button(1)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def option2_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.run_option_button(2)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def option3_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.run_option_button(3)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    def run_option_button(self, option_selected):
        current_item = option_selected - 1
        check_success = random.randint(1, 100)
        if check_success <= self.success_rate[current_item]:
            if self.item[current_item] is not None:
                item_id = self.item[current_item].item_id
                reward_location = random.randint(0, (self.expedition.luck + 3))
                quantity = reward_probabilities[reward_location] * self.reward_multiplier
                inventory.update_stock(self.expedition.player_object, item_id, quantity)
                output_msg = f"{self.item[current_item].item_emoji} {quantity}x {self.item[current_item].item_name}"
            else:
                quantity = random.randint(1, 3) * self.reward_multiplier
                self.expedition.luck += quantity
                output_msg = f"**+{quantity} Luck**"
            embed_msg = discord.Embed(colour=self.expedition.expedition_colour,
                                      title="Ritual Success!", description=output_msg)
            self.new_view = TransitionView(self.expedition)
        else:
            damage = self.expedition.take_damage((self.reward_multiplier * 100), (self.reward_multiplier * 300),
                                                 self.expedition.current_room.room_element)
            dmg_msg = f'Unable to hold out you took {damage:,} damage.'
            embed_msg = discord.Embed(colour=self.expedition.expedition_colour,
                                      title="Ritual Failed!", description=dmg_msg)
            if self.expedition.player_object.player_cHP <= 0 and not self.expedition.player_object.immortal:
                self.expedition.player_object.player_cHP = 0
                hp_msg = globalitems.display_hp(0, self.expedition.player_object.player_mHP)
                embed_msg.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                death_header, death_msg = death_embed()
                embed_msg.add_field(name=death_header, value=death_msg, inline=False)
                self.new_view = None
            else:
                self.expedition.luck -= self.reward_multiplier
                if self.expedition.luck <= 1:
                    self.expedition.luck = 1
                luck_msg = f"**-{self.reward_multiplier} Luck**"
                embed_msg.add_field(name="", value=luck_msg, inline=False)
                if self.expedition.player_object.immortal and self.expedition.player_object.player_cHP < 1:
                    self.expedition.player_object.player_cHP = 1
                hp_msg = globalitems.display_hp(self.expedition.player_object.player_cHP,
                                                self.expedition.player_object.player_mHP)
                embed_msg.add_field(name="", value=hp_msg, inline=False)
                self.new_view = TransitionView(self.expedition)
        return embed_msg


class GoldenRoomView(discord.ui.View):
    def __init__(self, expedition, room_type):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.room_type = room_type
        self.embed = None
        self.new_view = None
        self.active_room = self.expedition.current_room
        self.reward_adjuster = 1
        if self.active_room.room_variant == "Greater":
            self.reward_adjuster = 2
        self.success_rate = [min(100, (5 + 5 * self.reward_adjuster) +
                                 (self.expedition.luck * (5 * self.reward_adjuster))), 100]
        self.search.label = f"Search ({self.success_rate[0]}%)"
        self.search.emoji = "📿"
        self.collect.label = f"Collect"
        self.collect.emoji = "💲"

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def search(self, interaction: discord.Interaction, button: discord.Button):
        await self.jewellery_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def collect(self, interaction: discord.Interaction, button: discord.Button):
        await self.collect_callback(interaction, button)

    async def jewellery_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.expedition.player_object.player_name:
                if not self.embed:
                    self.embed = self.active_room.embed
                    self.embed.clear_fields()
                    check_success = random.randint(1, 100)
                    if check_success <= self.success_rate[0]:
                        self.embed, self.new_view = treasure_found(self.expedition, "Y")
                    else:
                        output_msg = "No accessories found!"
                        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                                   title="Search Failed!", description=output_msg)
                        self.new_view = TransitionView(self.expedition)
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        except Exception as e:
            print(e)

    async def collect_callback(self, interaction: discord.Interaction, button: discord.Button):
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
                        jackpot_check = [sum(jackpot_rates[:i + 1]) + (i + 1) * self.expedition.luck for i in
                                         range(len(jackpot_rates))]
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


def check_essence(selected_items, pool_tier):
    checked_items = selected_items.copy()
    for item_index, item in enumerate(selected_items):
        if item == "ESS":
            random_paragon = random.choice(tarot.paragon_list[pool_tier])
            essence_id = f"Essence{tarot.tarot_numeral_list(tarot.get_number_by_tarot(random_paragon))}"
            checked_items[item_index] = essence_id
    return checked_items


def trap_triggered(expedition, active_room, embed):
    lethality = random.randint(1, 100)
    if lethality <= max(0, (15 - expedition.luck)):
        trap_msg = trap_trigger2_list[active_room.room_element]
        embed.add_field(name="Fatal Trap - Run Ended", value=trap_msg, inline=False)
        death_header, death_msg = death_embed()
        embed.add_field(name=death_header, value=death_msg, inline=False)
        new_view = None
    else:
        trap_msg = trap_trigger1_list[active_room.room_element]
        embed.add_field(name="Trap Triggered!", value=trap_msg, inline=False)
        if active_room.room_element >= 6:
            teleport_room = random.randint(0, (expedition.expedition_length - 2))
            expedition.teleport()
            new_view = TransitionView(expedition)
        else:
            damage = expedition.take_damage(100, 300, active_room.room_element)
            dmg_msg = f'You took {damage:,} damage.'
            embed.add_field(name="", value=dmg_msg, inline=False)
            if expedition.player_object.player_cHP <= 0 and not expedition.player_object.immortal:
                expedition.player_object.player_cHP = 0
                hp_msg = f'0 / {expedition.player_object.player_mHP} HP'
                embed.add_field(name="Dead - Run Ended", value=hp_msg, inline=False)
                death_header, death_msg = death_embed()
                embed.add_field(name=death_header, value=death_msg, inline=False)
                new_view = None
            else:
                if expedition.player_object.immortal and expedition.player_object.player_cHP < 1:
                    expedition.player_object.player_cHP = 1
                hp_msg = globalitems.display_hp(expedition.player_object.player_cHP,
                                                expedition.player_object.player_mHP)
                embed.add_field(name="", value=hp_msg, inline=False)
                new_view = TransitionView(expedition)
    return embed, new_view


def treasure_found(expedition, treasure_type):
    type_num = {"W": 1, "A": 2, "Y": 3}
    active_room = expedition.current_room
    check_num = expedition.luck
    if active_room.room_variant == "Greater":
        check_num += 3
    if expedition.expedition_tier >= 4:
        check_num += 3
        fragment_roller = min((len(reward_probabilities) - 1), random.randint(0, check_num))
        num_fragments = reward_probabilities[fragment_roller]
        fragment_id = f"Fragment{type_num[treasure_type]}"
        reward_item = inventory.BasicItem(fragment_id)
        loot_msg = f"{reward_item.item_emoji} {num_fragments}x {reward_item.item_name}"
        embed = discord.Embed(colour=expedition.expedition_colour,
                              title="Fragments Acquired!",
                              description=loot_msg)
        update_stock = inventory.update_stock(expedition.player_object,
                                              reward_item.item_id, num_fragments)
        new_view = TransitionView(expedition)
    else:
        reward_tier = inventory.generate_random_tier()
        for x in range(check_num):
            random_tier = inventory.generate_random_tier()
            if random_tier > reward_tier:
                reward_tier = random_tier
                if reward_tier == 4:
                    break
        reward_item = inventory.CustomItem(expedition.player_object.player_id,
                                           treasure_type, reward_tier)
        embed = reward_item.create_citem_embed()
        new_view = ItemView(expedition, reward_item)
    return embed, new_view


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
        total_monsters_slain = sum(temp_dict.values())
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
        total_exp_gained *= (1 + (0.1 * total_monsters_slain))
        total_exp_gained = int(total_exp_gained)
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
                loot_item = inventory.BasicItem(item_id)
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


