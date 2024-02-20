import random
import discord
import pandas as pd
import numpy

import bosses
import globalitems
import inventory
import loot
import menus
import pandorabot
import player
import tarot
import quest
import pact
import sharedmethods

map_tier_dict = {"Ancient Ruins": 1, "Spatial Dungeon": 2, "Celestial Labyrinth": 3,
                 "Starlit Grotto": 4, "Void Rift": 5, "Citadel of Miracles": 6,
                 "Temple of the True Abyss": 7, "The Divine Palace": 8, "Spire of the Chaos God": 9}
random_room_list = [
    ["trap_room", 0], ["healing_room", 0], ["treasure", 0], ["trial_room", 0], ["statue_room", 0],
    ["epitaph_room", 0], ["selection_room", 0], ["sanctuary_room", 0], ["penetralia_room", 0],
    # These rooms have an echelon spawn restriction.
    ["boss_shrine", 2], ["crystal_room", 2], ["pact_room", 4],
    ["basic_monster", 0], ["basic_monster", 4], ["elite_monster", 0], ["elite_monster", 8],
    # These two rooms do not spawn normally.
    ["greater_treasure", 999], ["jackpot_room", 999]
]

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
basic_monster_list = ["Skeleton Knight", "Skeleton Archer", "Skeleton Mage", "Ooze", "Slime", "Sprite", "Faerie",
                      "Spider", "Goblin", "Imp", "Fiend", "Orc", "Ogre", "Lamia"]
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
                                 ["🟢", "🟡", "🔴"]]}

reward_probabilities = [1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10]


class Expedition:
    def __init__(self, ctx_object, player_obj, expedition_tier, expedition_colour):
        self.ctx_object = ctx_object
        self.expedition_tier, self.expedition_colour = expedition_tier, expedition_colour
        self.player_obj, self.luck = player_obj, (1 + player_obj.player_echelon)
        self.expedition_length, self.current_room_num = 9 + expedition_tier, 0
        self.current_room, self.current_room_view = None, None

    def random_room(self):
        available_room_list = random_room_list[:-2]
        available_room_list = [data[0] for data in available_room_list if self.player_obj.player_echelon >= data[1]]
        output_room_type = random.choice(available_room_list)
        if random.randint(1, 1000) <= (5 * self.luck):
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
            case "boss_shrine":
                new_view = ShrineRoomView(self)
            case "epitaph_room":
                new_view = EpitaphRoomView(self)
            case "crystal_room":
                new_view = CrystalRoomView(self)
            case "selection_room":
                new_view = SelectionRoomView(self)
            case "pact_room":
                new_view = PactRoomView(self)
            case "trial_room":
                new_view = TrialRoomView(self, variant)
            case "penetralia_room" | "jackpot_room":
                new_view = GoldenRoomView(self, room_type)
            case _:
                return None
        return new_view

    def display_next_room(self):
        new_room_num = self.current_room_num + 1
        if new_room_num < self.expedition_length:
            # Generate Room
            new_room_type = self.random_room()
            if new_room_num == (self.expedition_length - 1):
                new_room_type = "greater_treasure"
            new_room = Room(new_room_type, self.expedition_tier)
            embed_msg = new_room.display_room_embed(self)
            self.current_room = new_room
            # Generate View
            new_view = self.generate_room_view(new_room_type, new_room.room_variant)
            self.current_room_view = new_view
            # Build Embed
            status_msg = sharedmethods.display_hp(self.player_obj.player_cHP, self.player_obj.player_mHP)
            status_msg += f"\nLuck: {self.luck}"
            embed_msg.add_field(name="", value=status_msg, inline=False)
            return embed_msg, new_view
        # Handle Completed Expedition
        embed_msg = discord.Embed(colour=self.expedition_colour, title="Expedition Completed!",
                                  description="Would you like to embark on another expedition?")
        self.player_obj.reload_player()
        new_view = MapSelectView(self.ctx_object, self.player_obj, embed_msg)
        return embed_msg, new_view

    def teleport(self):
        self.current_room_num = random.randint(0, (self.expedition_length - 1))

    def take_damage(self, min_dmg, max_dmg, dmg_element, bypass_immortality=False):
        damage = random.randint(min_dmg, max_dmg) * self.expedition_tier
        player_mitigation = self.player_obj.damage_mitigation
        player_resist = 0
        if dmg_element != -1:
            player_resist = self.player_obj.elemental_resistance[dmg_element]
        damage -= damage * player_resist
        damage -= damage * player_mitigation * 0.01
        damage = int(damage)
        self.player_obj.player_cHP -= damage
        if self.player_obj.player_cHP < 0:
            self.player_obj.player_cHP = 0
            if self.player_obj.immortal and not bypass_immortality:
                self.player_obj.player_cHP = 1
        return damage

    def handle_regen(self, embed_msg):
        regen_bonus = self.player_obj.hp_regen
        if regen_bonus > 0:
            regen_amount = int(self.player_obj.player_cHP * regen_bonus)
            self.player_obj.player_cHP += regen_amount
            if self.player_obj.player_cHP > self.player_obj.player_mHP:
                self.player_obj.player_cHP = self.player_obj.player_mHP
            hp_msg = (f'Regen: +{regen_amount}\n'
                      f'{sharedmethods.display_hp(self.player_obj.player_cHP, self.player_obj.player_mHP)} HP')
            embed_msg.add_field(name="", value=hp_msg, inline=False)
        return embed_msg


class Room:
    def __init__(self, room_type, room_tier):
        self.room_type, self.room_tier = room_type, room_tier
        self.room_variant, self.reward_type = "", "W"
        self.room_element, self.room_deity = random.randint(0, 8), random.choice(list(tarot.card_dict.keys()))
        self.embed = None

    def display_room_embed(self, expedition):
        match self.room_type:
            case "trap_room":
                title_msg = trap_roomname_list[self.room_element]
                description_msg = ("The remains of other fallen adventurers are clearly visible here. "
                                   "Perhaps their equipment is salvageable, however you feel uneasy.")
            case "statue_room":
                title_msg = "Statue Room"
                description_msg = f"A statue of {tarot.card_dict[self.room_deity][0]} stands before you."
            case "healing_room":
                title_msg = "Safe Room"
                description_msg = random.choice(safe_room_msg)
            case "treasure" | "greater_treasure":
                random_check = random.randint(1, 100)
                treasure_details = {"treasure": [50, 80, "Lesser", "Chamber", "The unopened chest calls to you."],
                                    "greater_treasure": [33, 67, "Greater", "Vault",
                                                         "The irresistible allure of treasure entices you."]}
                details = treasure_details[self.room_type]
                self.reward_type = "Y"
                if random_check <= details[0]:
                    self.reward_type = "A"
                elif random_check <= details[1]:
                    self.reward_type = "W"
                title_msg = f"{details[2]} {inventory.custom_item_dict[self.reward_type]} Treasure {details[3]}"
                description_msg = details[4]
            case "basic_monster" | "elite_monster":
                title_msg, monster = "Monster Encounter", random.choice(basic_monster_list)
                if self.room_type == "elite_monster":
                    title_msg, monster = "Elite Monster Encounter", random.choice(elite_monster_list)
                element_descriptor = element_descriptor_list[self.room_element]
                prefix = "A"
                if element_descriptor[0].lower() in vowel_list:
                    prefix = "An"
                description_msg = f"{prefix} {element_descriptor} {monster} blocks your path."
            case "penetralia_room":
                title_msg = "Secret Penetralia"
                description_msg = "This room is well hidden. Perhaps there are valuable items here."
            case "jackpot_room":
                self.room_variant = "Greater"
                title_msg = "Golden Penetralia!"
                description_msg = f"Riches spread all across the secret room. Ripe for the taking!"
            case "crystal_room":
                title_msg = "Crystal Cave"
                description_msg = (f"Crystals are overly abundant in this cave. It is said that the rarest items are "
                                   f"drawn to each other. Those adorned in precious metals may fare better then those "
                                   f"who search blindly.")
            case "pact_room":
                title_msg = "Demonic Alter"
                pact_types = list(pact.pact_variants.keys())
                demon_tier = inventory.generate_random_tier(max_tier=8)
                demon_type, pact_type = pact.demon_variants[demon_tier], random.choice(pact_types)
                room_variant = f"{demon_tier};{pact_type}"
                description_msg = (f"As you examine the alter of {pact_type.lower()} a {demon_type} materializes. "
                                   f"It requests you to prove yourself with blood and offers to forge a pact.")
            case "sanctuary_room":
                title_msg = "Butterfae Sanctuary"
                description_msg = "A wondrous room illuminated by the light of hundreds of elemental butterfaes"
            case "trial_room":
                self.room_variant = random.choice(list(trial_variants_dict.keys()))
                trial_type = trial_variants_dict[self.room_variant]
                title_msg = f"Trial of {self.room_variant}"
                description_msg = f"{trial_type[0]}\n{', '.join(trial_type[1])}"
            case "boss_shrine":
                element_descriptor = element_descriptor_list[self.room_element]
                self.room_variant = "Greater " if random.randint(1, 100) <= (5 * expedition.luck) else ""
                target_list = globalitems.boss_list[1:-1] if self.room_variant == "" else globalitems.boss_list[1:-2]
                self.room_deity = random.choice(target_list)
                title_msg = f"{self.room_variant}{element_descriptor} {self.room_deity} Shrine"
                description_msg = (f"The shrine awaits the ritual of the challenger. Those who can endure the raw "
                                   f"elemental power and complete the ritual shall be granted rewards and passage.")
            case "epitaph_room":
                title_msg = f"Epitaph Room"
                description_msg = ("You see a tablet inscribed with glowing letters. It will take some time to uncover"
                                   "the message.")
            case "selection_room":
                title_msg = f"Selection Room"
                description_msg = ("Two items sit precariously atop podiums, but it's obviously a trap. "
                                   "Trying to take both seems extremely dangerous.")
            case _:
                pass
        self.embed = discord.Embed(colour=expedition.expedition_colour, title=title_msg, description=description_msg)
        return self.embed

    def check_trap(self, luck_value):
        is_trap, trap_check = False, random.randint(1, 100)
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
                pass
        return is_trap


async def handle_map_interaction(view_obj, interaction):
    if interaction.user.id != view_obj.expedition.player_obj.discord_id:
        return None, True
    if view_obj.embed is not None:
        await interaction.response.edit_message(embed=view_obj.embed)
        return None, True
    view_obj.embed = view_obj.expedition.current_room.embed
    return view_obj.expedition.current_room, False


async def handle_combat(interaction, view_obj, min_dmg, max_dmg, unscathed_rate):
    if random.randint(1, 100) < unscathed_rate:
        description_msg = f'You emerge unscathed from combat.'
    else:
        damage = view_obj.expedition.take_damage(min_dmg, max_dmg, view_obj.active_room.room_element)
        description_msg = f'You took {damage:,} damage.'
        if await check_death(view_obj.expedition.player_obj, view_obj.embed, view_obj.new_view, interaction):
            return True, description_msg
    return False, description_msg


class MapSelectView(discord.ui.View):
    def __init__(self, ctx_object, player_user, embed_msg):
        super().__init__(timeout=None)
        self.ctx_object = ctx_object
        self.player_user = player_user
        self.embed_msg = embed_msg
        select_options = [
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label=map_name, description=f"Tier {index} Expedition"
            ) for index, map_name in enumerate(map_tier_dict.keys(), start=1)
        ]
        self.select_menu = discord.ui.Select(
            placeholder="Select an expedition!", min_values=1, max_values=1, options=select_options)
        self.select_menu.callback = self.map_select_callback
        self.add_item(self.select_menu)

    async def map_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_user.discord_id:
            return
        selected_map = interaction.data['values'][0]
        selected_tier = map_tier_dict[selected_map]
        # Confirm eligibility
        if self.player_user.player_echelon < (selected_tier - 1):
            self.embed_msg.clear_fields()
            not_ready_msg = "You are only qualified for expeditions one tier above your echelon."
            self.embed_msg.add_field(name="Too Perilous!", value=not_ready_msg, inline=False)
            await interaction.response.edit_message(embed=self.embed_msg, view=self)
            return
        # Move to confirmation view
        expedition_colour, _ = sharedmethods.get_gear_tier_colours(selected_tier)
        embark_view = EmbarkView(self.ctx_object, self.player_user, self.embed_msg, selected_tier, expedition_colour)
        new_embed_msg = discord.Embed(colour=expedition_colour, title=f"{selected_map} Selected!",
                                      description=f"Tier {selected_tier} exploration selected.")
        await interaction.response.edit_message(embed=new_embed_msg, view=embark_view)


class EmbarkView(discord.ui.View):
    def __init__(self, ctx_object, player_user, embed_msg, selected_tier, colour):
        super().__init__(timeout=None)
        self.ctx_object = ctx_object
        self.player_user = player_user
        self.current_embed = embed_msg
        self.embed, self.new_view = None, None
        self.selected_tier, self.colour = selected_tier, colour

    @discord.ui.button(label="Embark", style=discord.ButtonStyle.success, emoji="⚔️")
    async def embark_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        if interaction.user.id != self.player_user.discord_id:
            return
        self.player_user.reload_player()
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        if not self.player_user.spend_stamina((200 + self.selected_tier * 50)):
            self.current_embed.clear_fields()
            self.current_embed.add_field(name="Not Enough Stamina!", value="Please check your /stamina!")
            await interaction.response.edit_message(embed=self.current_embed, view=self)
            return
        if self.player_user.player_quest == 2:
            quest.assign_unique_tokens(self.player_user, "Map")
        new_expedition = Expedition(self.ctx_object, self.player_user, self.selected_tier, self.colour)
        self.embed, self.new_view = new_expedition.display_next_room()
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class TransitionView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def proceed_callback(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        self.embed, self.new_view = self.expedition.display_next_room()
        self.expedition.current_room_num += 1
        self.embed = self.expedition.handle_regen(self.embed)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    
class HealRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None

    @discord.ui.button(label="Short Rest", style=discord.ButtonStyle.blurple, emoji="➕")
    async def short_rest_callback(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        # Handle trap
        if active_room.check_trap(self.expedition.luck):
            self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Recovery Failed!",
                                       description="Nothing good will come from staying any longer.")
            self.new_view = TransitionView(self.expedition)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle healing
        heal_amount = random.randint(self.expedition.expedition_tier, (10 + self.expedition.luck))
        heal_total = int(self.expedition.player_obj.player_mHP * (heal_amount * 0.01))
        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                   title="Recovery Successful!", description=f"You restore **{heal_total:,}** HP.")
        self.expedition.player_obj.player_cHP += heal_total
        hp = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.add_field(name="", value=hp, inline=False)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(label="Long Rest", style=discord.ButtonStyle.blurple, emoji="➕")
    async def long_rest_callback(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        heal_amount = random.randint(self.expedition.expedition_tier, (10 + self.expedition.luck))
        heal_total = int(self.expedition.player_obj.player_mHP * (heal_amount * 0.01)) * 2
        # Handle trap
        if active_room.check_trap(self.expedition.luck):
            damage = heal_total
            damage = self.expedition.take_damage(damage, damage, active_room.room_element)
            dmg_msg = f'You took {damage:,} damage.'
            self.embed = discord.Embed(colour=self.expedition.expedition_colour, 
                                       title="Ambushed!", description=f"You were attacked while resting! {dmg_msg}")
            hp = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
            if await check_death(self.expedition.player_obj, self.embed, self.new_view, interaction):
                return
            self.embed.add_field(name="", value=hp, inline=False)
            self.new_view = TransitionView(self.expedition)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle healing
        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                   title="Recovery Successful!", description=f"You restore **{heal_total:,}** HP.")
        self.expedition.player_obj.player_cHP += heal_total
        hp = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.add_field(name="", value=hp, inline=False)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class MonsterRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        self.monster_adjuster = 1
        self.active_room = self.expedition.current_room
        if self.active_room.room_type == "elite_monster":
            self.monster_adjuster = 2
        self.stealth_chance = int(50 / self.monster_adjuster + (self.expedition.luck * (2 / self.monster_adjuster)))
        self.stealth.label, self.stealth.emoji = f"Stealth ({self.stealth_chance}%)", "↩️"
        self.fight.label, self.fight.emoji = "Fight", "⚔️"

    @discord.ui.button(style=discord.ButtonStyle.red)
    async def fight(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        min_dmg, max_dmg = (100 * self.monster_adjuster), (300 * self.monster_adjuster)
        adjust = 2 / self.monster_adjuster
        # Check if unscathed
        if random.randint(1, 100) < int(self.expedition.luck * adjust):
            self.embed.add_field(name="Monster Defeated!", value=f'You emerge unscathed from combat.', inline=False)
            self.new_view = TransitionView(self.expedition)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        trigger_return, msg = await handle_combat(interaction, self, min_dmg, max_dmg, int(self.expedition.luck * adjust))
        if trigger_return:
            return
        self.embed.add_field(name="Monster Defeated!", value=msg, inline=False)
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.add_field(name="", value=hp_msg, inline=False)
        self.new_view = TransitionView(self.expedition)
        # Award experience without resetting the player object.
        temp_user = player.get_player_by_id(self.expedition.player_obj.player_id)
        exp_reward = 100 * self.monster_adjuster * self.expedition.expedition_tier
        exp_reward += 25 * self.monster_adjuster * self.expedition.luck
        exp_message, lvl_change = temp_user.adjust_exp(exp_reward)
        self.embed.add_field(name="", value=f"{globalitems.exp_icon} {exp_message} Exp Acquired.", inline=False)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        if lvl_change == 0:
            return
        await sharedmethods.send_notification(self.expedition.ctx_object, temp_user, "Level", lvl_change)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def stealth(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        min_dmg, max_dmg = (100 * self.monster_adjuster), (300 * self.monster_adjuster)
        stealth_fail_multiplier = 1 + (0.5 * self.monster_adjuster)
        # Handle stealth success
        if random.randint(1, 100) <= self.stealth_chance:
            self.new_view = TransitionView(self.expedition)
            self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Stealth Successful!",
                                       description="You have successfully avoided the encounter.")
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle stealth failure
        damage = self.expedition.take_damage(min_dmg, max_dmg, self.active_room.room_element)
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        dmg_msg = f'You take {damage:,} damage!'
        self.embed.add_field(name="Stealth Failed", value=f"{dmg_msg}\n{hp_msg}", inline=False)
        if await check_death(self.expedition.player_obj, self.embed, self.new_view, interaction):
            return
        self.new_view = MonsterRoomView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class TrapRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        self.active_room = self.expedition.current_room
        self.player_resist = self.expedition.player_obj.elemental_resistance[self.active_room.room_element]
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
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        if random.randint(1, 100) <= self.trap_check:
            self.embed, self.new_view = treasure_found(self.expedition, active_room, "A")
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        self.embed, self.new_view = await trap_triggered(self.expedition, self.active_room, self.embed, interaction)

    async def bypass_callback(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        self.embed, self.new_view = self.expedition.display_next_room()
        self.expedition.current_room_num += 1
        self.embed = self.expedition.handle_regen(self.embed)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class EpitaphRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        self.active_room = self.expedition.current_room
        self.item_check = 100
        self.decipher_check = 100
        self.search.label = f"Search ({self.item_check}%)"
        self.decipher.label = f"Decipher ({self.decipher_check}%)"

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def search(self, interaction: discord.Interaction, button: discord.Button):
        await self.search_callback(interaction, button)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="🧩")
    async def decipher(self, interaction: discord.Interaction, button: discord.Button):
        await self.decipher_callback(interaction, button)

    async def search_callback(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        # Handle search success
        if random.randint(1, 100) <= self.item_check:
            self.embed, self.new_view = treasure_found(self.expedition, active_room, "W")
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle search failure
        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                   title="Search Failed!", description="You leave empty handed.")
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    async def decipher_callback(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        # Handle decryption success
        if random.randint(1, 100) <= self.decipher_check:
            luck_gained = random.randint(1, 3)
            self.expedition.luck += luck_gained
            self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                       title="Decryption Success!", description=f"**+{luck_gained} Luck**")
            self.new_view = TransitionView(self.expedition)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle decryption failure
        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                   title="Decryption Failed!", description="You leave empty handed.")
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class SelectionRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        self.active_room = self.expedition.current_room
        self.item_pools = [["Hammer1", "Ore1", "Trove1", "Potion1", "Scrap", "ESS"],
                           ["Hammer1", "Pearl1", "Ore2", "Token1", "Trove2", "Flame1", "Matrix1", "Trove2",
                            "Summon1", "Potion2", "ESS"],
                           ["Hammer1", "Pearl1", "Ore3", "Token2", "Trove3", "Summon1", "Gem1", "Gem2", "Gem3",
                            "Potion3", "ESS"],
                           ["Hammer2", "Pearl2", "Ore4", "Token3", "Token4", "Trove4", "Summon2", "Summon3", "Core1",
                            "Jewel1", "Jewel2", "Potion4", "ESS"],
                           ["Hammer2", "Pearl2", "Ore5", "Token5", "Trove5", "Summon4", "Crystal2",
                            "Core2", "Flame2", "Jewel3", "ESS"],
                           ["Hammer2", "Pearl2", "Ore6", "Token7", "Token6", "Trove7", "Trove6", "Summon5", "Crystal3",
                            "Core3", "Jewel4", "Compass", "ESS"],
                           ["Lotus1", "Lotus2", "Lotus3", "Lotus4", "Lotus5", "Lotus6", "Lotus7", "Lotus8", "Lotus9",
                            "Lotus10", "DarkStar", "LightStar", "Core4", "Trove8", "Crystal4", "Jewel5", "ESS"]]
        reward_tier = 6 if random.randint(1, 10000) <= self.expedition.luck else min(5, self.expedition.luck // 5)
        selected_pool = self.item_pools[reward_tier]
        item_location = random.sample(range(0, (len(selected_pool) - 1)), 2)
        selected_set = [selected_pool[item_location[0]], selected_pool[item_location[1]]]
        selected_set = check_essence(selected_set, reward_tier)
        self.choice_items = [inventory.BasicItem(selected_set[0]), inventory.BasicItem(selected_set[1])]
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
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        button_id = int(button.custom_id)
        target_item = self.choice_items[(button_id - 1)]
        inventory.update_stock(self.expedition.player_obj, target_item.item_id, 1)
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Item Selected!",
                                   description=f"{target_item.item_emoji} 1x {target_item.item_name} acquired!")
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        if "Lotus" in target_item.item_id or target_item.item_id in ["DarkStar", "LightStar"]:
            await sharedmethods.send_notification(self.expedition.ctx_object, self.expedition.player_obj,
                                                  "Item", target_item.item_id)

    async def speed_callback(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        # Handle trap
        if random.randint(1, 100) > self.speed_check:
            self.embed, self.new_view = await trap_triggered(self.expedition, self.active_room, self.embed, interaction)
            return
        # Award both items
        inventory.update_stock(self.expedition.player_obj, self.choice_items[0].item_id, 1)
        inventory.update_stock(self.expedition.player_obj, self.choice_items[1].item_id, 1)
        output_msg = f"{self.choice_items[0].item_emoji} 1x {self.choice_items[0].item_name} acquired!\n"
        output_msg += f"{self.choice_items[1].item_emoji} 1x {self.choice_items[1].item_name} acquired!"
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Received Both Items!",
                                   description=output_msg)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        if "Lotus" in choice_items[0].item_id or choice_items[0].item_id in ["DarkStar", "LightStar"]:
            await sharedmethods.send_notification(self.expedition.ctx_object, self.expedition.player_obj,
                                                  "Item", choice_items[0].item_id)
        if "Lotus" in choice_items[1].item_id or choice_items[1].item_id in ["DarkStar", "LightStar"]:
            await sharedmethods.send_notification(self.expedition.ctx_object, self.expedition.player_obj,
                                                  "Item", choice_items[1].item_id)


class StatueRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None

    @discord.ui.button(label="Pray", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def pray_callback(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        blessing_rewards = {("Incarnate", 8): ["Divine Blessing", "Core4", 15],
                            ("Arbiter", 7): ["Prismatic Blessing", "Summon5", 10],
                            ("Arbiter", 0): ["ARBITER", "Summon4", 7],
                            ("Paragon", 6): ["Miraculous Blessing", "Summon3", 5],
                            ("Paragon", 5): ["Sovereign's Blessing", "Summon2", 3],
                            ("Paragon", 0): ["PARAGON", "Summon1", 2]}
        # Handle blessing occurrence.
        if random.randint(1, 100) <= self.expedition.luck:
            boss_type, deity_tier = (tarot.card_type_dict[active_room.room_deity],
                                     tarot.card_dict[active_room.room_deity][1])
            matching_rewards = blessing_rewards.get((boss_type, deity_tier), None)
            if matching_rewards is None:
                matching_rewards = blessing_rewards.get((boss_type, 0), None)
            reward_item = inventory.BasicItem(matching_rewards[1])
            if random.randint(1, 100) <= 10:
                reward_item = inventory.BasicItem(f"Essence{active_room.room_deity}")
            blessing_msg = f"{matching_rewards[0]}\nLuck +{matching_rewards[2]}"
            if matching_rewards[0] in ["PARAGON", "ARBITER"]:
                blessing_msg = f"{tarot.card_dict[active_room.room_deity][0]}\nLuck +{matching_rewards[2]}"
            item_msg = f"{reward_item.item_emoji} 1x {reward_item.item_name} received!"
            inventory.update_stock(self.expedition.player_obj, reward_item.item_id, 1)
            self.expedition.luck += matching_rewards[2]
            self.new_view = TransitionView(self.expedition)
            self.embed.add_field(name=blessing_msg, value=item_msg, inline=False)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle regular occurrence.
        heal_amount = random.randint(self.expedition.expedition_tier, 10)
        heal_total = int(self.expedition.player_obj.player_mHP * (heal_amount * 0.01))
        self.expedition.player_obj.player_cHP += heal_total
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.new_view = TransitionView(self.expedition)
        self.embed.add_field(name="Health Restored", value=hp_msg, inline=False)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(label="Destroy", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def destroy_callback(self, interaction: discord.Interaction, button: discord.Button):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        # Handle wrath outcome
        if random.randint(1, 100) <= 1:
            embed_title = f"Incurred __{tarot.card_dict[active_room.room_deity][0]}'s__ wrath!"
            wrath_msg = wrath_msg_list[tarot.get_index_by_key(active_room.room_deity)]
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            self.embed.add_field(name=f"{embed_title} - Run Ended", value=wrath_msg, inline=False)
            return
        # Handle no item outcome
        if random.randint(1, 100) > 50 + self.expedition.luck:
            self.embed.add_field(name="Nothing happens.", value="Better keep moving.", inline=False)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle excavation outcome
        reward_id, reward_qty = loot.generate_random_item()
        loot_item = inventory.BasicItem(reward_id)
        embed_title = f"Excavated {loot_item.item_name}!"
        item_msg = f"{loot_item.item_emoji} {reward_qty} {loot_item.item_name} found in the rubble!"
        inventory.update_stock(self.expedition.player_obj, reward_id, reward_qty)
        self.new_view = TransitionView(self.expedition)
        self.embed.add_field(name=embed_title, value=item_msg, inline=False)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class TreasureRoomView(discord.ui.View):
    def __init__(self,  expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None

    @discord.ui.button(label="Open Chest", style=discord.ButtonStyle.success, emoji="⚔️")
    async def chest_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        active_room, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        # Handle treasure outcome.
        if not active_room.check_trap(self.expedition.luck):
            self.embed, self.new_view = treasure_found(self.expedition, active_room, active_room.reward_type)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle greater trap outcome.
        if active_room.room_type != "treasure":
            trap_msg = "You have fallen for the ultimate elder mimic's clever ruse!"
            self.embed.add_field(name="Eaten - Run Ended", value=trap_msg, inline=False)
            self.expedition.player_obj.player_cHP = 0
            _ = await check_death(self.expedition.player_obj, self.embed, self.new_view, interaction)
            return
        # Handle regular trap outcome
        damage = self.expedition.take_damage(100, 300, active_room.room_element)
        if await check_death(self.expedition.player_obj, self.embed, self.new_view, interaction):
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        dmg_msg = f'The mimic bites you dealing {damage:,} damage.'
        hp_msg = f'{self.expedition.player_obj.player_cHP} / {self.expedition.player_obj.player_mHP} HP'
        self.embed.add_field(name="", value=dmg_msg, inline=False)
        self.embed.add_field(name="", value=hp_msg, inline=False)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class ItemView(discord.ui.View):
    def __init__(self, expedition, item):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.item = item
        self.embed, self.new_view = None, None

    @discord.ui.button(label="Claim Item", style=discord.ButtonStyle.blurple)
    async def claim_callback(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        self.item.item_id = inventory.inventory_add_custom_item(self.item)
        self.new_view = TransitionView(self.expedition)
        if self.item.item_id == 0:
            self.embed = inventory.full_inventory_embed(self.item, self.expedition.expedition_colour)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title=f"Item Claimed!",
                                   description=f"Item ID: {self.item.item_id} has been placed in your gear inventory.")
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(label="Sell Item", style=discord.ButtonStyle.success)
    async def sell_callback(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        self.new_view = TransitionView(self.expedition)
        sell_value = inventory.sell_value_by_tier[self.item.item_tier]
        temp_user = player.get_player_by_id(self.expedition.player_obj.player_id)
        sell_msg = temp_user.adjust_coins(sell_value)
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Item Sold!",
                                   description=f"{globalitems.coin_icon} {sell_msg} lotus coins acquired.")
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(label="Scrap Item", style=discord.ButtonStyle.success)
    async def scrap_callback(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        self.new_view = TransitionView(self.expedition)
        scrap_item = inventory.BasicItem("Scrap")
        inventory.update_stock(self.expedition.player_obj, scrap_item.item_id, self.item.item_tier)
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Item Scrapped!",
                                   description=f"{scrap_item.item_emoji} {self.item.item_tier}x {scrap_item.item_name}")
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class TrialRoomView(discord.ui.View):
    def __init__(self, expedition, variant):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
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
        await self.run_option_button(1, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(2, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(3, interaction)

    async def run_option_button(self, option_selected, interaction):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        temp_player = player.get_player_by_id(self.expedition.player_obj.player_id)
        failed_msg, output_msg = "Cost could not be paid. Nothing Gained.", ""
        luck_gained = 1 + 2 * (option_selected - 1)
        match self.expedition.current_room.room_variant:
            case "Offering":
                cost = int(0.3 * option_selected * self.expedition.player_obj.player_mHP)
                if cost < self.expedition.player_obj.player_cHP:
                    self.expedition.player_obj.player_cHP -= cost
                    failed_msg = ""
                    hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP,
                                                      self.expedition.player_obj.player_mHP)
                    output_msg = f"Sacrificed {cost} HP\n{hp_msg}\nGained +{luck_gained} luck!"
            case "Greed":
                cost_list = [1000, 5000, 10000]
                cost = cost_list[(option_selected - 1)]
                if temp_player.player_coins >= cost:
                    cost_msg = temp_player.adjust_coins(cost, True)
                    failed_msg = ""
                    output_msg = (f"Sacrificed {cost_msg} lotus coins\nRemaining: {temp_player.player_coins}\n"
                                  f"Gained +{luck_gained} luck!")
            case "Soul":
                cost = int(100 + 200 * (option_selected - 1))
                if temp_player.player_stamina >= cost:
                    temp_player.player_stamina -= cost
                    temp_player.set_player_field("player_stamina", temp_player.player_stamina)
                    failed_msg = ""
                    output_msg = (f"Sacrificed {cost} stamina\nRemaining: {temp_player.player_stamina}\n"
                                  f"Gained +{luck_gained} luck!")
            case _:
                pass
        self.new_view = TransitionView(self.expedition)
        if failed_msg != "":
            self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                       title="Trial Failed!", description=completed_msg)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        self.expedition.luck += luck_gained
        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                  title="Trial Passed!", description=output_msg)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class CrystalRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        random_item = f"Fragment{min((self.expedition.expedition_tier - 4), 4)}"
        if random.randint(1, 1000) <= self.expedition.luck:
            random_item = f"Core{min((self.expedition.expedition_tier - 4), 4)}"
        if self.expedition.tier < 5:
            random_item = "Scrap"
        self.dropped_item = inventory.BasicItem(random_item)
        # Calculate the total tier of all equipped gear.
        gear_tier_total = 0
        for item_id in self.expedition.player_obj.player_equipped:
            if item_id != 0:
                e_item = inventory.read_custom_item(item_id)
                gear_tier_total += e_item.item_tier
                if e_item.item_inlaid_gem_id != 0:
                    e_gem = inventory.read_custom_item(e_item.item_inlaid_gem_id)
                    gear_tier_total += e_gem.item_tier
        self.success_rate = [min(100, gear_tier_total), min(100, self.expedition.luck * 2)]
        self.option1.label = f"Resonate ({self.success_rate[0]}%)"
        self.option1.emoji = "🌟"
        self.option2.label = f"Search ({self.success_rate[1]}%)"
        self.option2.emoji = "🔍"

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(0, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(1, interaction)

    async def run_option_button(self, option_selected, interaction):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        quantity = 2 - option_selected
        self.new_view = TransitionView(self.expedition)
        # Handle failure
        if random.randint(1, 100) > self.success_rate[option_selected]:
            title_msg, output_msg = f"Nothing Found!", f"You leave empty handed.\n**Luck -{quantity}**"
            self.expedition.luck = min(0, self.expedition.luck - quantity)
            self.embed = discord.Embed(colour=self.expedition.expedition_colour, title=title_msg, description=output_msg)
            return
        # Handle success
        title_msg = "Found Materials!"
        output_msg = f"{self.dropped_item.item_emoji} {quantity}x {self.dropped_item.item_name}"
        output_msg += f"\n**Luck +1**"
        inventory.update_stock(self.expedition.player_obj, self.dropped_item.item_id, quantity)
        self.expedition.luck += quantity
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title=title_msg, description=output_msg)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class PactRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        self.active_room = self.expedition.current_room
        pact_details = self.active_room.room_variant.split(';')
        self.demon_type = pact.demon_variants[int(pact_details[0])]
        self.blood_percentage = int(pact_details[0]) * 10
        self.option1.label = f"Forge Blood Pact ({self.blood_percentage[0]}%)"
        self.option2.label, self.option3.label = f"Refuse", "Fight"

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        blood_cost = int(self.expedition.player_obj.player_mHP * (self.blood_percentage * 0.01))
        # Handle insufficient hp.
        if self.expedition.player_obj.player_cHP <= blood_cost:
            title_msg = "Fatal Pact"
            output_msg = f"Unable to provide sufficient blood to forge the pact, the {self.demon_type} consumes you."
            self.embed = discord.Embed(colour=self.expedition.expedition_colour, title=title_msg, description=output_msg)
            self.expedition.player_obj.player_cHP = 0
            _ = await check_death(expedition.player_obj, self.embed, self.new_view, interaction)
            return
        # Forge the pact.
        self.expedition.player_obj.player_cHP -= blood_cost
        temp_user = player.get_player_by_discord(self.expedition.player_obj.discord_id)
        temp_user.pact = self.active_room.room_variant
        self.embed = pact.display_pact(temp_user)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(style=discord.ButtonStyle.red)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        min_dmg, max_dmg = (100 * self.expedition.expedition_tier), (300 * self.expedition.expedition_tier)
        trigger_return, description_msg = await handle_combat(interaction, self, min_dmg, max_dmg, self.expedition.luck)
        if trigger_return:
            return
        self.embed.add_field(name=f"{self.demon_type} Attacks!", value=description_msg, inline=False)
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.add_field(name="", value=hp_msg, inline=False)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(style=discord.ButtonStyle.red)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        min_dmg, max_dmg = (200 * self.expedition.expedition_tier), (600 * self.expedition.expedition_tier)
        trigger_return, description_msg = await handle_combat(interaction, self, min_dmg, max_dmg, self.expedition.luck)
        if trigger_return:
            return
        self.embed.add_field(name=f"{self.demon_type} Defeated!", value=description_msg, inline=False)
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.add_field(name="", value=hp_msg, inline=False)
        self.new_view = TransitionView(self.expedition)
        temp_user = player.get_player_by_id(self.expedition.player_obj.player_id)
        exp_message, lvl_change = temp_user.adjust_exp((100 * self.expedition.expedition_tier) + (25 * self.expedition.luck))
        self.embed.add_field(name="", value=f"{globalitems.exp_icon} {exp_message} Exp Acquired.", inline=False)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        if lvl_change == 0:
            return
        await sharedmethods.send_notification(self.expedition.ctx_object, temp_user, "Level", lvl_change)


class SanctuaryRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        self.random_numbers = random.sample(range(9), 3)
        self.item_type = "Fae"
        if random.randint(1, 1000) <= self.expedition.luck:
            self.item_type = "Origin"
        self.item_list = [inventory.BasicItem(f"{self.item_type}{self.random_numbers[0]}"),
                          inventory.BasicItem(f"{self.item_type}{self.random_numbers[1]}"),
                          inventory.BasicItem(f"{self.item_type}{self.random_numbers[2]}")]
        for i in range(3):
            option = getattr(self, f'option{i + 1}')
            setattr(option, 'label', f"{self.item_list[i].item_name}")
            setattr(option, 'emoji', self.item_list[i].item_emoji)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(0, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(1, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(2, interaction)

    async def run_option_button(self, option_selected, interaction):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        quantity = 1
        if self.item_type == "Fae":
            quantity = random.randint((1 + self.expedition.luck), (10 + self.expedition.luck))
        inventory.update_stock(self.expedition.player_obj, self.item_list[option_selected].item_id, quantity)
        output_msg = (f"{self.item_list[option_selected].item_emoji} {quantity}x "
                      f"{self.item_list[option_selected].item_name}")
        self.new_view = TransitionView(self.expedition)
        self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                   title=f"{self.item_type} Collected!", description=output_msg)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class ShrineRoomView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None
        self.reward_multiplier = 1 if self.expedition.current_room.room_variant == "" else 2
        boss_num = globalitems.boss_list.index(self.expedition)
        shrine_dict = {1: ["Land", 3, "Sky", 4], 2: ["Fear", 6, "Suffering", 0],
                       3: ["Illumination", 7, "Tranquility", 1], 4: ["Retribution", 2, "Imprisonment", 5]}
        self.item = [inventory.BasicItem(f"Gem{boss_num}"), inventory.BasicItem(f"Unrefined{boss_num}"), None]
        self.resistance = [self.expedition.player_obj.elemental_resistance[3],
                           self.expedition.player_obj.elemental_resistance[4],
                           self.expedition.player_obj.elemental_resistance[self.expedition.current_room.room_element]]
        self.selected_elements = [shrine_dict[boss_num][2], shrine_dict[boss_num][4],
                                  self.expedition.current_room.room_element]
        self.success_rate = [min(100, int(resistance * 100) + 5) for resistance in self.resistance]
        self.option1.label = f"Ritual of {shrine_dict[boss_num][0]} ({self.success_rate[self.selected_elements[0]]}%)"
        self.option2.label = f"Ritual of {shrine_dict[boss_num][3]} ({self.success_rate[self.selected_elements[1]]}%)"
        self.option3.label = f"Ritual of Chaos ({self.success_rate[self.selected_elements[2]]}%)"
        self.option1.emoji = globalitems.global_element_list[self.selected_elements[0]]
        self.option2.emoji = globalitems.global_element_list[self.selected_elemens[1]]
        self.option3.emoji = globalitems.global_element_list[self.selected_elements[2]]

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(0, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(1, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_option_button(2, interaction)

    async def run_option_button(self, option_selected, interaction):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        self.new_view = TransitionView(self.expedition)
        # Handle regular success
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Ritual Success!", description="")
        if random.randint(1, 100) <= self.success_rate[option_selected]:
            if self.item[option_selected] is not None:
                item_id = self.item[option_selected].item_id
                reward_location = random.randint(0, (self.expedition.luck + 3))
                quantity = reward_probabilities[reward_location] * self.reward_multiplier
                inventory.update_stock(self.expedition.player_obj, item_id, quantity)
                self.embed.description = (f"{self.item[option_selected].item_emoji} {quantity}x "
                                          f"{self.item[option_selected].item_name}")
                await interaction.response.edit_message(embed=self.embed, view=self.new_view)
                return
            # Handle chaos success
            quantity = random.randint(1, 3) * self.reward_multiplier
            self.expedition.luck += quantity
            self.embed.description = f"**Gained +{quantity} Luck**"
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle failure
        damage = self.expedition.take_damage((self.reward_multiplier * 100), (self.reward_multiplier * 300),
                                             self.expedition.current_room.room_element)
        dmg_msg = f'Unable to hold out you took {damage:,} damage.'
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.title, self.embed.description = "Ritual Failed!", dmg_msg
        if await check_death(self.expedition.player_obj, self.embed, self.new_view, interaction):
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        self.expedition.luck = max(1, (self.expedition.luck - self.reward_multiplier))
        luck_msg = f"**Lost -{self.reward_multiplier} Luck**"
        self.embed.add_field(name="", value=luck_msg, inline=False)
        self.embed.add_field(name="", value=hp_msg, inline=False)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class GoldenRoomView(discord.ui.View):
    def __init__(self, expedition, room_type):
        super().__init__(timeout=None)
        self.expedition, self.room_type = expedition, room_type
        self.embed, self.new_view = None, None
        self.active_room = self.expedition.current_room
        self.reward_adjuster = 1
        if self.active_room.room_variant == "Greater":
            self.reward_adjuster = 2
        self.success_rate = [min(100, (5 + 5 * self.reward_adjuster) +
                                 (self.expedition.luck * (5 * self.reward_adjuster))), 100]
        self.search.label, self.collect.label = f"Search ({self.success_rate[0]}%)", f"Collect"
        self.search.emoji, self.collect.emoji = "📿", "💲"

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def search(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        if random.randint(1, 100) > self.success_rate[0]:
            self.new_view = TransitionView(self.expedition)
            self.embed = discord.Embed(colour=self.expedition.expedition_colour,
                                       title="Search Failed!", description="No amulets found!")
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        self.embed, self.new_view = treasure_found(self.expedition, self.active_room, "Y")
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def collect(self, interaction: discord.Interaction, button: discord.Button):
        _, trigger_return = await handle_map_interaction(self, interaction)
        if trigger_return:
            return
        base_coins, jackpot_chance = random.randint(1000, 2000), 5 * self.expedition.luck
        if self.room_type == "jackpot_room":
            base_coins, jackpot_chance = 10000, (50 * self.expedition.luck)
        reward_coins, bonus_coins = (base_coins * self.expedition.luck), 0
        # Handle jackpots.
        jackpot_available, random_num = random.randint(1, 1000), random.randint(1, 1000)
        if jackpot_available <= jackpot_chance:
            jackpot_rates = [1, 10, 30, 50]
            jackpot_check = [sum(jackpot_rates[:i + 1]) + (i + 1) * self.expedition.luck for i in
                             range(len(jackpot_rates))]
            if random_num <= jackpot_check[0]:
                reward_title, bonus_coins = "Ultimate Jackpot!!!!", random.randint(1000000, 5000000)
            elif random_num <= jackpot_check[1]:
                reward_title, bonus_coins = "Greater Jackpot!!!", random.randint(500000, 1000000)
            elif random_num <= jackpot_check[2]:
                reward_title, bonus_coins = "Standard Jackpot!!", random.randint(100000, 500000)
            elif random_num <= jackpot_check[3]:
                reward_title, bonus_coins = "Lesser Jackpot!", random.randint(10000, 100000)
        # Build the embed.
        temp_player = player.get_player_by_id(self.expedition.player_obj.player_id)
        reward_msg = temp_player.adjust_coins(reward_coins + bonus_coins)
        self.embed = discord.Embed(colour=self.expedition.expedition_colour, title="Treasures Obtained!",
                                   description=f"You acquired {globalitems.coin_icon} {reward_msg} lotus coins!")
        # Add jackpot message.
        if bonus_coins != 0:
            bonus_msg = f"Acquired {globalitems.coin_icon} {bonus_coins:,} bonus lotus coins!"
            self.embed.add_field(name=reward_title, value=reward_msg, inline=False)
        self.new_view = TransitionView(self.expedition)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


async def check_death(player_object, embed_msg, view, interaction):
    if player_object.player_cHP > 0:
        return False
    death_header = "The voice of __Thana, The Death__ echoes through your mind"
    death_msg = random.choice(death_msg_list)
    embed_msg.add_field(name=death_header, value=death_msg, inline=False)
    view = None
    await interaction.response.edit_message(embed=embed_msg, view=view)
    return True


def check_essence(selected_items, pool_tier):
    checked_items = selected_items.copy()
    for item_index, item in enumerate(selected_items):
        if item == "ESS":
            selected_data = [card_number for card_number, data in tarot.card_dict.items() if data[1] == pool_tier]
            essence_id = f"Essence{random.choice(selected_data)}"
            checked_items[item_index] = essence_id
    return checked_items


async def trap_triggered(expedition, active_room, embed, interaction):
    blank_view = None
    # Handle fatal trap
    if random.randint(1, 100) <= max(0, (15 - expedition.luck)):
        embed.add_field(name="Fatal Trap - Run Ended", value=trap_trigger2_list[active_room.room_element], inline=False)
        expedition.player_obj.player_cHP = 0
        _ = await check_death(expedition.player_obj, embed, blank_view, interaction)
        return embed, blank_view
    # Handle regular traps
    trap_msg = trap_trigger1_list[active_room.room_element]
    embed.add_field(name="Trap Triggered!", value=trap_msg, inline=False)
    # Handle teleport
    if active_room.room_element >= 6:
        teleport_room = random.randint(0, (expedition.expedition_length - 2))
        expedition.teleport()
        new_view = TransitionView(expedition)
        await interaction.response.edit_message(embed=embed, view=new_view)
        return embed, new_view
    # Handle damage
    damage = expedition.take_damage(100, 300, active_room.room_element)
    dmg_msg = f'You took {damage:,} damage.'
    hp_msg = sharedmethods.display_hp(expedition.player_obj.player_cHP, expedition.player_obj.player_mHP)
    embed.add_field(name="", value=dmg_msg, inline=False)
    if await check_death(expedition.player_obj, embed, blank_view, interaction):
        return embed, blank_view
    embed.add_field(name="", value=hp_msg, inline=False)
    new_view = TransitionView(expedition)
    await interaction.response.edit_message(embed=embed, view=new_view)
    return embed, new_view


def treasure_found(expedition, active_room, treasure_type):
    type_num = {"W": 1, "A": 2, "Y": 3}
    bonus = 0
    if active_room.room_variant == "Greater":
        bonus = 3 if expedition.expedition_tier >= 4 else 10
    # Handle fragment rewards.
    if expedition.expedition_tier >= 4:
        fragment_roller = min((len(reward_probabilities) - 1), random.randint(0, (expedition.luck + bonus)))
        num_fragments = reward_probabilities[fragment_roller]
        fragment_item = inventory.BasicItem(f"Fragment{min((expedition.expedition_tier - 4), 4)}")
        loot_msg = f"{fragment_item.item_emoji} {num_fragments}x {fragment_item.item_name}"
        embed = discord.Embed(colour=expedition.expedition_colour, title="Fragments Acquired!", description=loot_msg)
        update_stock = inventory.update_stock(expedition.player_obj, reward_item.item_id, num_fragments)
        return embed, TransitionView(expedition)
    # Handle gear item rewards.
    reward_tier = inventory.generate_random_tier(luck_bonus=(expedition.luck + bonus))
    reward_item = inventory.CustomItem(expedition.player_obj.player_id, treasure_type, reward_tier)
    embed = reward_item.create_citem_embed()
    return embed, ItemView(expedition, reward_item)


monster_dict = {
        "slime": 50, "bat": 100, "spider": 200, "wolf": 300, "goblin": 400,
        "skeleton": 500, "faerie": 600, "ogre": 700, "harpy": 800, "wraith": 900,
        "lamia": 1000, "lich": 1500, "teyeger": 2000, "minotaur": 2500, "basilisk": 3000,
        "wyrm": 3500, "phoenix": 4000, "chimaera": 4500, "hydra": 5000, "dragon": 9999
    }
gem_list = [("Rock", 1), ("Bronze Chunk", 500), ("Silver Chunk", 1000),
            ("Gold Ore", 5000), ("Platinum Ore", 10000), ("Bismuth Ore", 20000),
            ("Silent Topaz", 30000), ("Mist Zircon", 40000), ("Prismatic Opal", 50000),
            ("Whispering Emerald", 75000), ("Drowned Sapphire", 100000), ("Blood Amethyst", 150000),
            ("Soul Diamond", 250000), ("Stygian Ruby", 500000), ("Aurora Tear", 1000000),
            ("Spatial Prism", 2500000), ("Lotus of Abundance", 0), ("Stone of the True Void", 10000000)]


async def build_manifest_return_embed(ctx_object, player_obj, method, colour):
    temp_dict = {}
    method_info = method.split(";")
    card_stars = int(method_info[2])
    success_rate = 64 + card_stars * 2
    card_name = tarot.card_dict[method_info[1]][0]
    title_msg = f"Pandora, The Celestial Returns"
    if method_info[2] != "0":
        title_msg = f"Echo of __{card_name}__ - Returns ({method_info[0]})"
    if method_info[0] == "Hunt":
        title_msg, output_msg = await handle_hunt(ctx_object, player_obj, success_rate)
    elif method_info[0] == "Mine":
        title_msg, output_msg = await handle_mine(ctx_object, player_obj, success_rate)
    else:
        title_msg, output_msg = await handle_gather(ctx_object, player_obj, success_rate)
    embed_msg = discord.Embed(colour=colour, title=title_msg, description=output_msg)
    return embed_msg


async def handle_hunt(ctx_object, player_obj, success_rate):
    death_dict = {1: "defeated", 2: "slain", 3: "slaughtered", 4: "massacred"}
    total_exp = 0
    output_msg = ""
    # Build the result dict.
    for _ in range(player_obj.player_echelon + 5):
        if random.randint(1, 100) <= success_rate:
            enemy_num = random.randint(0, 14) + random.randint(0, player_obj.player_echelon)
            random_enemy = list(monster_dict.keys())[enemy_num]
            temp_dict[random_enemy] = temp_dict.get(random_enemy, 0) + 1
    temp_dict = dict(sorted(temp_dict.items(), key=lambda m: monster_dict.get(m[0], 0) * m[1], reverse=True))
    # Build the monster output.
    for monster_type, num_slain in temp_dict.items():
        death_type = death_dict[min(num_slain, 4)]
        monster_line = f"{num_slain}x {monster_type}{'s' if num_slain > 1 else ''} {death_type}!"
        if num_slain * monster_dict.get(monster_type, 0) > 2000:
            monster_line = f"**{monster_line}**"
        output_msg += f"{monster_line}\n"
    # Handle the exp
    total_monsters_slain = sum(temp_dict.values())
    total_exp = sum(num_slain * monster_dict.get(monster_type, 0) for monster_type, num_slain in temp_dict.items())
    total_exp *= (1 + (0.1 * total_monsters_slain))
    if total_monsters_slain >= 1:
        total_exp += (player_obj.player_echelon * 500)
    total_exp = int(total_exp)
    exp_msg, lvl_change = player_obj.adjust_exp(total_exp)
    output_msg += f"{globalitems.exp_icon} {exp_msg} EXP awarded!\n" if temp_dict else "No monsters were slain.\n"
    if lvl_change == 0:
        return output_msg
    await sharedmethods.send_notification(ctx_object, player_obj, "Level", lvl_change)
    return output_msg


async def handle_mine(ctx_object, player_obj, success_rate):
    outcome_index = sharedmethods.generate_ramping_reward(success_rate, 15, 18)
    outcome_index = max(outcome_index, player_obj.player_echelon)
    outcome_item, outcome_coins = gem_list[outcome_index][0], gem_list[outcome_index][1]
    if outcome_coins != 0:
        coin_msg = player_obj.adjust_coins(outcome_coins)
        return f"You found a {outcome_item}!\nSold for {globalitems.coin_icon} {coin_msg} Lotus Coins!"
    # Handle lotus item exception
    inventory.update_stock(player_obj, "Lotus5", 1)
    lotus_item = inventory.BasicItem("Lotus5")
    output_msg = f"{lotus_item.item_emoji} 1x {lotus_item.item_name} found!"
    await sharedmethods.send_notification(ctx_object, player_obj, "Item", lotus_item.item_id)
    return output_msg


async def handle_gather(ctx_object, player_obj, success_rate):
    temp_dict = None
    output_msg = ""
    for _ in range(player_obj.player_echelon + 4):
        if success_rate <= random.randint(1, 100):
            reward_id, num_reward = loot.generate_random_item()
            temp_dict[reward_id] = temp_dict.get(reward_id, 0) + num_reward
    if temp_dict is None:
        return "No items found."
    for item_id, item_quantity in temp_dict.items():
        inventory.update_stock(player_obj, item_id, item_quantity)
        loot_item = inventory.BasicItem(item_id)
        output_msg += f"{loot_item.item_emoji} {item_quantity}x {loot_item.item_name} received!\n"
        if "Lotus" in item_id or item_id in ["DarkStar", "LightStar"]:
            await sharedmethods.send_notification(ctx_object, player_obj, "Item", item_id)
    return output_msg


class ManifestView(discord.ui.View):
    def __init__(self, player_user, embed_msg, e_tarot, colour, num_hours):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.embed_msg = embed_msg
        self.e_tarot = e_tarot
        self.colour = colour
        self.num_hours = num_hours
        self.paid = False
        if self.player_user.player_echelon < 2:
            self.gather_callback.style = discord.ButtonStyle.secondary
            self.gather_callback.disabled = True
        if self.player_user.player_echelon < 4:
            self.mine_callback.style = discord.ButtonStyle.secondary
            self.mine_callback.disabled = True

    @discord.ui.button(label="Hunt", style=discord.ButtonStyle.success, emoji="⚔️")
    async def hunt_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = manifest_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Hunt")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Gather", style=discord.ButtonStyle.success, emoji="⚔️")
    async def gather_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = manifest_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Gather")
        await interaction.response.edit_message(embed=result[0], view=result[1])

    @discord.ui.button(label="Mine", style=discord.ButtonStyle.success, emoji="⚔️")
    async def mine_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        result = manifest_callback(self, self.player_user, self.embed_msg, self.e_tarot, self.colour, self.num_hours, "Mine")
        await interaction.response.edit_message(embed=result[0], view=result[1])


def manifest_callback(view, player_user, embed_msg, e_tarot, colour, num_hours, method):
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
                method_info = f"{method};{e_tarot.card_numeral};{e_tarot.num_stars}"
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


