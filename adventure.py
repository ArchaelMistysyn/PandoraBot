# General imports
import random
import discord
from discord.ext import commands
import numpy
from datetime import datetime as dt, timedelta

# Data imports
import globalitems
import sharedmethods
import adventuredata

# Core imports
import player
import quest
import inventory

# Item/crafting imports
import loot
import tarot
import pact


class Expedition:
    def __init__(self, ctx_object, player_obj, tier):
        self.ctx_object = ctx_object
        self.tier = tier
        self.colour, _ = sharedmethods.get_gear_tier_colours(self.tier)
        self.player_obj, self.luck = player_obj, player_obj.luck_bonus + 1
        self.length, self.room_num = 9 + tier, 0
        self.room, self.room_view = None, None

    def random_room(self):
        available_room_list = [data[0] for data in adventuredata.random_room_list[:-2] if self.tier >= data[1]]
        output_room_type = random.choice(available_room_list)
        if random.randint(1, 1000) <= (5 * self.luck):
            output_room_type = "jackpot_room"
        return output_room_type

    async def display_next_room(self, ctx_object, player_obj):
        new_room_num = self.room_num + 1
        # Handle completed expedition.
        if new_room_num >= self.length:
            title, description = "Expedition Completed!", "Would you like to embark on another expedition?"
            embed_msg = discord.Embed(colour=self.colour, title=title, description=description)
            await self.player_obj.reload_player()
            new_view = MapSelectView(self.ctx_object, self.player_obj, embed_msg)
            return embed_msg, new_view
        # Generate random room.
        new_room_type = self.random_room() if new_room_num != (self.length - 1) else "greater_treasure"
        self.room = Room(new_room_type, self.tier)
        await self.room.display_room_embed(self)
        self.room_view = AdventureRoomView(ctx_object, player_obj, self)
        status_msg = sharedmethods.display_hp(self.player_obj.player_cHP, self.player_obj.player_mHP)
        status_msg += f"\nLuck: {self.luck}"
        if player_obj.hp_regen > 0:
            status_msg = f"{self.handle_regen()}\n{status_msg}"
        self.room.embed.add_field(name="", value=status_msg, inline=False)
        return self.room.embed, self.room_view

    def teleport(self):
        self.room_num = random.randint(0, (self.length - 2))

    def take_damage(self, min_dmg, max_dmg, dmg_element, bypass_immortality=False):
        damage = random.randint(min_dmg, max_dmg) * self.tier
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

    def handle_regen(self):
        if self.player_obj.player_cHP >= self.player_obj.player_mHP:
            return ""
        regen_bonus = self.player_obj.hp_regen
        if regen_bonus == 0:
            return ""
        regen_amount = int(self.player_obj.player_cHP * regen_bonus)
        self.player_obj.player_cHP += regen_amount
        if self.player_obj.player_cHP > self.player_obj.player_mHP:
            self.player_obj.player_cHP = self.player_obj.player_mHP
        return f'Regen: +{regen_amount:,}'


class Room:
    def __init__(self, room_type, room_tier):
        self.room_type, self.room_tier = room_type, room_tier
        self.variant, self.reward_type = "", "W"
        self.room_element = random.randint(0, 8)
        self.room_deity = random.choice([key for key, value in tarot.card_dict.items() if value[1] <= room_tier])
        self.embed = None

    def get_rates(self, player_obj, luck, player_resist):
        scaling = adventuredata.adjuster_dict.get(self.room_type, 0)
        match self.room_type:
            case "trap_room":
                return [min(100, int(10 + luck + (player_resist * 100))), None]
            case "statue_room":
                return [min(90, 5 + luck), min(90, 50 + luck)]
            case "basic_monster" | "elite_monster" | "legend_monster":
                scaling = adventuredata.adjuster_dict[self.room_type]
                return [None, int(65 - (15 * scaling) + (luck / scaling))]
            case "epitaph_room":
                return [min(90, 50 + luck), min(90, 75 + luck)]
            case "penetralia_room" | "jackpot_room":
                return [min(90, (5 + (5 * scaling))), None]
            case "selection_room":
                return [None, None, min(75, (luck * 5))]
            case "crystal_room":
                return [(player_obj.player_echelon * 10), min(100, 30 + luck * 2)]
            case "pact_room":
                pact_details = self.variant.split(';')
                return [None, int(pact_details[0]) * 10]
            case "heart_room":
                return [50, 50]
            case _:
                return [None, None, None]

    async def display_room_embed(self, expedition):
        title = adventuredata.variant_details_dict[self.room_type][0]
        description = adventuredata.variant_details_dict[self.room_type][1]
        element_descriptor = adventuredata.element_descriptor_list[self.room_element]
        random_check = random.randint(1, 100)
        match self.room_type:
            case "trap_room":
                title = f"{adventuredata.trap_room_name_list[self.room_element]} Room"
            case "statue_room":
                description = f"A statue of {tarot.card_dict[self.room_deity][0]} stands before you."
            case "healing_room":
                description = random.choice(adventuredata.safe_msg_list)
            case "treasure" | "greater_treasure":
                details = adventuredata.treasure_details[self.room_type]
                self.reward_type = "A" if random_check <= details[0] else "W" if random_check <= details[1] else "Y"
                specifier = inventory.custom_item_dict[self.reward_type] if expedition.tier <= 5 else "Fragment"
                title_msg = f"{details[2]} {specifier} {title}"
            case "basic_monster":
                monster = random.choice(adventuredata.monster_dict[self.room_type])
                prefix = "An" if element_descriptor[0].lower() in adventuredata.vowel_list else "A"
                description = f"{prefix} {element_descriptor} {monster} blocks your path!"
            case "elite_monster":
                monster = adventuredata.monster_dict[self.room_type][self.room_element]
                description = f"**{monster}** spotted!! It won't be long before it notices you."
            case "legend_monster":
                monster = adventuredata.monster_dict[self.room_type][self.room_element]
                description = f"__**{monster}**__ the legendary titan comes into view!!! DANGER!!!"
            case "pact_room":
                demon_tier = inventory.generate_random_tier(max_tier=8)
                demon_type, pact_type = pact.demon_variants[demon_tier], random.choice(list(pact.pact_variants.keys()))
                self.variant = f"{demon_tier};{pact_type}"
                title = f"{title} [{pact_type}]"
            case "trial_room":
                self.variant = random.choice(list(adventuredata.trial_variants_dict.keys()))
                trial_type = adventuredata.trial_variants_dict[self.variant]
                title = f"Trial of {self.variant}"
                description = f"{trial_type[0]}\n{', '.join(trial_type[1])}"
                temp_player = await player.get_player_by_discord(expedition.player_obj.discord_id)
                if self.variant == "Greed":
                    description += f"\nCurrent Coins: {globalitems.coin_icon} {temp_player.player_coins:,}x"
                elif variant == "Soul":
                    description += f"\nCurrent Stamina: {globalitems.stamina_icon} {temp_player.player_stamina:,}"
            case "boss_shrine":
                self.variant = "Greater " if random_check <= (5 * expedition.luck) else ""
                target_list = globalitems.boss_list[1:-2] if self.variant == "" else globalitems.boss_list[1:-1]
                self.room_deity = random.choice(target_list)
                title = f"{self.variant}{element_descriptor} {self.room_deity} Shrine"
            case _:
                pass
        self.embed = discord.Embed(colour=expedition.colour, title=title, description=description)

    def check_trap(self, luck_value):
        trap_rates = {"trap_room": 100, "treasure": max(0, (25 - luck_value)),
                      "healing_room": max(0, (25 - luck_value)), "greater_treasure": max(0, (15 - luck_value))}
        return True if random.randint(1, 100) <= trap_rates[self.room_type] else False


def get_random_quantity(luck=1, is_lucky=False):
    num_attempts = 1 + (1 if is_lucky else 0) + (luck // 10)
    highest_quantity = 0
    for _ in range(num_attempts):
        check_value = random.randint(1, 100)
        cumulative_probability = 0
        for probability, quantity in adventuredata.reward_probabilities.items():
            cumulative_probability += probability
            if check_value <= cumulative_probability:
                if quantity > highest_quantity:
                    highest_quantity = quantity
                break
    return highest_quantity


async def handle_map_interaction(view_obj, interaction):
    if interaction.user.id != view_obj.expedition.player_obj.discord_id:
        return True
    if view_obj.embed is not None:
        await interaction.response.edit_message(embed=view_obj.embed, view=view_obj.new_view)
        return True
    view_obj.embed = view_obj.expedition.room.embed
    return False


class MapSelectView(discord.ui.View):
    def __init__(self, ctx_object, player_user, current_embed):
        super().__init__(timeout=None)
        self.ctx_object = ctx_object
        self.player_user = player_user
        self.current_embed = current_embed
        self.new_embed, self.new_view = None, None
        select_options = [
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label=map_name, description=f"Tier {index} Expedition"
            ) for index, map_name in enumerate(adventuredata.map_tier_dict.keys(), start=1)
        ]
        self.select_menu = discord.ui.Select(
            placeholder="Select an expedition!", min_values=1, max_values=1, options=select_options)
        self.select_menu.callback = self.map_select_callback
        self.add_item(self.select_menu)

    async def map_select_callback(self, interaction: discord.Interaction):
        await self.player_user.reload_player()
        if interaction.user.id != self.player_user.discord_id:
            return
        selected_map = interaction.data['values'][0]
        selected_tier = adventuredata.map_tier_dict[selected_map]
        # Handle already paid cost.
        if self.new_embed is not None:
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        # Confirm eligibility
        if self.player_user.player_echelon < (selected_tier - 1):
            self.current_embed.clear_fields()
            not_ready_msg = "You are only qualified for expeditions one tier above your echelon."
            self.current_embed.add_field(name="Too Perilous!", value=not_ready_msg, inline=False)
            await interaction.response.edit_message(embed=self.current_embed, view=self)
            return
        # Handle stamina cost
        if not self.player_user.spend_stamina((200 + selected_tier * 50)):
            self.current_embed.clear_fields()
            self.current_embed.add_field(name="Not Enough Stamina!", value="Please check your /stamina!", inline=False)
            await interaction.response.edit_message(embed=self.current_embed, view=self)
            return
        # Assign quest token
        if self.player_user.player_quest == 2:
            quest.assign_unique_tokens(self.player_user, "Map")
        # Begin expedition
        new_expedition = Expedition(self.ctx_object, self.player_user, selected_tier)
        self.new_embed, self.new_view = await new_expedition.display_next_room(self.ctx_object, self.player_user)
        await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)


class AdventureRoomView(discord.ui.View):
    def __init__(self, ctx_object, player_obj, expedition_obj):
        super().__init__(timeout=None)
        self.ctx_object = ctx_object
        self.player_obj, self.expedition = player_obj, expedition_obj
        self.embed, self.new_view = None, None

        # Stored information
        self.room_element = self.expedition.room.room_element
        self.player_resist = self.expedition.player_obj.elemental_resistance[self.room_element]
        self.reward_items = [None, None, None]

        # Set room details
        room_details = adventuredata.room_data_dict[self.expedition.room.room_type]
        self.success_rates = self.expedition.room.get_rates(self.player_obj, self.expedition.luck, self.player_resist)
        num_buttons, button_labels, button_icons, button_colours, button_callback = room_details
        self.selected_callback = getattr(self, button_callback)
        # Handle button assignment
        for button_num in range(num_buttons):
            button_object = self.children[button_num]
            button_object.custom_id = str(button_num)
            button_label = button_labels[button_num]
            if self.success_rates[button_num] is not None:
                button_label = f"{button_label} ({self.success_rates[button_num]}%)"
            button_object.label = button_label
            button_object.style = button_colours[button_num]
            if button_icons[button_num] is not None:
                button_object.emoji = button_icons[button_num]
        # Remove unused buttons
        buttons_to_remove = []
        for button_index, button_object in enumerate(self.children):
            if button_index >= num_buttons:
                buttons_to_remove.append(button_object)
        for button_object in buttons_to_remove:
            self.remove_item(button_object)
        self.custom_assignments()

    @discord.ui.button(label="Blank", style=discord.ButtonStyle.success, row=1)
    async def option1(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_button(interaction, int(button.custom_id))

    @discord.ui.button(label="Blank", style=discord.ButtonStyle.success, row=1)
    async def option2(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_button(interaction, int(button.custom_id))

    @discord.ui.button(label="Blank", style=discord.ButtonStyle.success, row=1)
    async def option3(self, interaction: discord.Interaction, button: discord.Button):
        await self.run_button(interaction, int(button.custom_id))

    async def run_button(self, interaction, variant):
        try:
            if await handle_map_interaction(self, interaction):
                return
            self.new_view = TransitionView(self.expedition)
            await self.selected_callback(interaction, variant, self.expedition.room)
        except discord.ext.commands.errors.CommandInvokeError as e:
            # Handle CommandInvokeError
            print(f"CommandInvokeError occurred: {e}")
            # To further catch and handle the specific NotFound exception
            if isinstance(e.original, discord.NotFound):
                print(f"NotFound error occurred: {e.original}")
            return
        except discord.NotFound as e:
            # Directly catching NotFound exceptions that are not wrapped in a CommandInvokeError
            print(f"NotFound error occurred: {e}")
            return
        except Exception as e:
            # Catch all other exceptions
            print(f"An unexpected error occurred: {e}")
            return

    async def bypass_callback(self, interaction):
        self.embed, self.new_view = await self.expedition.display_next_room(self.expedition.ctx_object, self.expedition.player_obj)
        self.expedition.room_num += 1
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    async def trap_callback(self, interaction, variant, active_room):
        if variant != 0:
            await self.bypass_callback(interaction)
            return
        if random.randint(1, 100) <= self.success_rates[0]:
            await self.treasure_found(interaction, "A")
            return
        await self.trap_triggered(interaction)

    async def statue_callback(self, interaction_obj, variant, active_room):
        deity = active_room.room_deity

        async def pray_callback():
            # Handle blessing occurrence.
            if random.randint(1, 100) <= self.success_rates[0]:
                boss_type, deity_tier = tarot.card_type_dict[deity], tarot.card_dict[deity][1]
                matching_rewards = adventuredata.blessing_rewards.get((boss_type, deity_tier), None)
                if matching_rewards is None:
                    matching_rewards = adventuredata.blessing_rewards.get((boss_type, 0), None)
                print(f"Matching reward: {matching_rewards} - Boss type: {boss_type}")
                reward_item = inventory.BasicItem(matching_rewards[1])
                if random.randint(1, 100) <= 10:
                    reward_item = inventory.BasicItem(f"Essence{deity}")
                blessing_msg = f"{matching_rewards[0]} Blessing\nLuck +{matching_rewards[2]}"
                if matching_rewards[0] in ["PARAGON", "ARBITER"]:
                    blessing_msg = blessing_msg.replace(matching_rewards[0], f"{tarot.card_dict[deity][0]}'s")
                item_msg = f"{reward_item.item_emoji} 1x {reward_item.item_name} received!"
                inventory.update_stock(self.expedition.player_obj, reward_item.item_id, 1)
                self.expedition.luck += matching_rewards[2]
                self.embed.add_field(name=blessing_msg, value=item_msg, inline=False)
                await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                return
            # Handle heal occurrence
            heal_total = int(self.expedition.player_obj.player_mHP * (random.randint(self.expedition.tier, 10) * 0.01))
            self.expedition.player_obj.player_cHP += heal_total
            hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP,
                                              self.expedition.player_obj.player_mHP)
            self.embed.add_field(name="Health Restored", value=hp_msg, inline=False)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

        async def destroy_callback():
            # Handle wrath outcome
            if random.randint(1, 100) <= 1:
                self.embed = active_room.embed
                embed_title = f"Incurred __{tarot.card_dict[deity][0]}'s__ wrath!"
                wrath_msg, outcome = adventuredata.wrath_msg_list[deity][0], adventuredata.wrath_msg_list[deity][1]
                # Handle Death
                if outcome == 1:
                    self.new_view = None
                    await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                    self.embed.add_field(name=f"{embed_title} - Run Ended", value=wrath_msg, inline=False)
                    return
                # Handle Regular/Teleport
                elif outcome in [0, 2]:
                    if outcome == 2:
                        self.expedition.teleport()
                    self.embed.add_field(name=embed_title, value=wrath_msg, inline=False)
                    await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                    return
                # Handle Damage
                await self.expedition.take_damage(outcome, outcome, -1, True)
                hp_msg = sharedmethods.display_hp(self.player_obj.player_cHP, self.player_obj.player_mHP)
                wrath_msg += f"\nYou took {outcome:,} damage!\n{hp_msg}"
                if await self.check_death(interaction_obj, result_msg=wrath_msg, title_msg=embed_title):
                    return
                self.embed.add_field(name=embed_title, value=wrath_msg, inline=False)
                await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                return

            # Handle no item outcome
            if random.randint(1, 100) > self.success_rates[1]:
                self.embed.add_field(name="Nothing happens.", value="Better keep moving.", inline=False)
                await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                return
            # Handle excavation outcome
            reward_list = loot.generate_random_item()
            reward_id, reward_qty = reward_list[0][0], reward_list[0][1]
            loot_item = inventory.BasicItem(reward_id)
            embed_title = f"Excavated {loot_item.item_name}!"
            item_msg = f"{loot_item.item_emoji} {reward_qty} {loot_item.item_name} found in the rubble!"
            inventory.update_stock(self.expedition.player_obj, reward_id, reward_qty)
            self.embed.add_field(name=embed_title, value=item_msg, inline=False)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

        # Run the selected option
        callbacks = {0: pray_callback, 1: destroy_callback}
        await callbacks[variant]()

    async def rest_callback(self, interaction_obj, variant, active_room):
        heal_amount = random.randint(self.expedition.tier, (10 + self.expedition.luck))
        heal_total = int(self.expedition.player_obj.player_mHP * (heal_amount * 0.01))
        if variant == 1:
            heal_total *= 2
        # Handle fail outcome
        if active_room.check_trap(self.expedition.luck):
            if variant == 1:
                damage = self.expedition.take_damage(heal_total, heal_total, active_room.room_element)
                hp = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
                title, description = "Ambushed!", f"You were attacked while resting! You took {damage:,} damage."
                if await self.check_death(interaction_obj, result_msg=description):
                    return
                self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
                self.embed.add_field(name="", value=hp, inline=False)
                return
            title, description = "Recovery Failed!", "Nothing good will come from staying any longer."
            self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle healing
        title, description = "Recovery Successful!", f"You restore **{heal_total:,}** HP."
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
        self.expedition.player_obj.player_cHP += heal_total
        hp = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.add_field(name="", value=hp, inline=False)
        await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

    async def basic_monster_callback(self, interaction_obj, variant, active_room):
        await self.monster_callback(interaction_obj, variant, active_room, adventuredata.adjuster_dict["basic_monster"])

    async def elite_monster_callback(self, interaction_obj, variant, active_room):
        await self.monster_callback(interaction_obj, variant, active_room, adventuredata.adjuster_dict["elite_monster"])

    async def legend_monster_callback(self, interaction_obj, variant, active_room):
        await self.monster_callback(interaction_obj, variant, active_room, adventuredata.adjuster_dict["legend_monster"])

    async def monster_callback(self, interaction_obj, variant, active_room, adjuster):
        self.new_view = TransitionView(self.expedition)
        min_dmg, max_dmg = (100 * adjuster), (300 * adjuster)
        min_dmg, max_dmg = (min_dmg, max_dmg) if adjuster != 3 else (min_dmg * 5, max_dmg * 5)

        async def fight_callback():
            temp_user = await player.get_player_by_id(self.expedition.player_obj.player_id)
            exp_reward = (500 + (100 * self.expedition.tier) + (25 * self.expedition.luck)) * adjuster
            trigger, msg = await self.handle_combat(interaction_obj, min_dmg, max_dmg, int(self.expedition.luck * 2 / adjuster))
            if trigger:
                return
            hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
            exp_msg, lvl_change = temp_user.adjust_exp(exp_reward)
            self.embed.add_field(name="Monster Defeated!", value=msg, inline=False)
            self.embed.add_field(name="", value=f"{hp_msg}\n{globalitems.exp_icon} {exp_msg} Exp Acquired.", inline=False)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
            if lvl_change != 0:
                await sharedmethods.send_notification(self.expedition.ctx_object, temp_user, "Level", lvl_change)

        async def stealth_callback():
            # Handle stealth success
            if random.randint(1, 100) <= self.success_rates[1]:
                title, description = "Stealth Successful!", "You have successfully avoided the encounter."
                self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
                await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                return
            # Handle stealth failure
            damage = self.expedition.take_damage(min_dmg, max_dmg, active_room.room_element)
            hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
            dmg_msg = f'You take {damage:,} damage!'
            self.embed.add_field(name="Stealth Failed", value=f"{dmg_msg}\n{hp_msg}", inline=False)
            if await self.check_death(interaction_obj):
                return
            self.new_view = AdventureRoomView(self.ctx_object, self.player_obj, self.expedition)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

        # Run the selected option
        callbacks = {0: fight_callback, 1: stealth_callback}
        await callbacks[variant]()

    async def epitaph_callback(self, interaction_obj, variant, active_room):
        async def search_callback():
            # Handle search success
            if random.randint(1, 100) <= self.success_rates[0]:
                await self.treasure_found(interaction_obj, "W")
                return
            # Handle search failure
            title, description = "Search Failed!", "You leave empty handed."
            self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

        async def decipher_callback():
            # Handle decryption success
            if random.randint(1, 100) <= self.success_rates[1]:
                luck_gained = random.randint(1, 3)
                self.expedition.luck += luck_gained
                title, description = "Decryption Success!", f"**+{luck_gained} Luck**"
                self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
                await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                return
            # Handle decryption failure
            title, description = "Decryption Failed!", "You leave empty handed."
            self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

        # Run the selected option
        callbacks = {0: search_callback, 1: decipher_callback}
        await callbacks[variant]()

    async def penetralia_callback(self, interaction_obj, variant, active_room):
        async def search_callback():
            if random.randint(1, 100) > self.success_rates[0]:
                title, description = "Search Failed!", "No amulets found!"
                self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
                await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                return
            await self.treasure_found(interaction_obj, "Y")

        async def collect_callback():
            base_coins, jackpot_chance, trove_rate = random.randint(1000, 2000), 5 * self.expedition.luck, 1
            if self.expedition.room.room_type == "jackpot_room":
                base_coins, jackpot_chance, trove_rate = 10000, (50 * self.expedition.luck), 5
            reward_coins, bonus_coins = (base_coins * self.expedition.luck), 0
            # Handle jackpots.
            if random.randint(1, 1000) <= jackpot_chance:
                base_rate = [level[0] for level in adventuredata.jackpot_levels]
                jackpot_check = [sum(base_rate[:i + 1]) + (i + 1) * self.expedition.luck for i in range(len(base_rate))]
                random_num = random.randint(1, 1000)
                for i, (threshold, title, coin_range) in enumerate(adventuredata.jackpot_levels):
                    if random_num <= jackpot_check[i]:
                        bonus_coins, reward_title = random.randint(*coin_range), title
                        break
            # Build the embed.
            temp_player = await player.get_player_by_id(self.expedition.player_obj.player_id)
            reward_msg = temp_player.adjust_coins(reward_coins + bonus_coins)
            title, description = "Treasures Obtained!", f"You acquired {globalitems.coin_icon} {reward_msg} lotus coins!"
            # Check for trove drops
            if random.randint(1, 100) <= trove_rate:
                trove_tier = inventory.generate_random_tier(max_tier=8, luck_bonus=self.expedition.luck)
                trove_item = inventory.BasicItem(f"Trove{trove_tier}")
                inventory.update_stock(self.player_obj, trove_item.item_id, 1)
                description += f"\n{sharedmethods.reward_message(trove_item)} acquired!"
            self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
            # Add jackpot message.
            if bonus_coins > 0:
                bonus_msg = f"Acquired {globalitems.coin_icon} {bonus_coins:,} bonus lotus coins!"
                self.embed.add_field(name=reward_title, value=bonus_msg, inline=False)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

        callbacks = {0: search_callback, 1: collect_callback}
        await callbacks[variant]()

    async def heart_callback(self, interaction_obj, variant, active_room):
        target_item = inventory.BasicItem(f"Heart{variant + 1}")
        luck_value = -1
        title, description = "Magical Overload!", f"The creature's heart was destroyed.\nLuck {luck_value}"
        if random.randint(1, 100) <= self.success_rates[variant]:
            inventory.update_stock(self.expedition.player_obj, target_item.item_id, 1)
            luck_value = 1
            title = "Heart Preserved!"
            description = f"{sharedmethods.reward_message(target_item)} acquired!\n Luck +{luck_value}"
        self.expedition.luck = max(1, self.expedition.luck + luck_value)
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
        await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

    async def selection_callback(self, interaction_obj, variant, active_room):
        async def option_callback():
            target_item = self.reward_items[variant]
            inventory.update_stock(self.expedition.player_obj, target_item.item_id, 1)
            title, description = "Item Selected!", f"{target_item.item_emoji} 1x {target_item.item_name} acquired!"
            self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
            if "Lotus" in target_item.item_id or target_item.item_id in ["DarkStar", "LightStar"]:
                await sharedmethods.send_notification(self.expedition.ctx_object, self.expedition.player_obj,
                                                      "Item", target_item.item_id)

        async def speed_callback():
            # Handle trap
            if random.randint(1, 100) > self.speed_check:
                await self.trap_triggered(interaction_obj)
                return
            # Award both items
            inventory.update_stock(self.expedition.player_obj, self.reward_items[0].item_id, 1)
            inventory.update_stock(self.expedition.player_obj, self.reward_items[1].item_id, 1)
            output_msg = f"{self.reward_items[0].item_emoji} 1x {self.reward_items[0].item_name} acquired!\n"
            output_msg += f"{self.reward_items[1].item_emoji} 1x {self.reward_items[1].item_name} acquired!"
            title = "Received Both Items!"
            self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=output_msg)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
            if "Lotus" in self.reward_items[0].item_id or self.reward_items[0].item_id in ["DarkStar", "LightStar"]:
                await sharedmethods.send_notification(self.expedition.ctx_object, self.expedition.player_obj,
                                                      "Item", self.reward_items[0].item_id)
            if "Lotus" in choice_items[1].item_id or choice_items[1].item_id in ["DarkStar", "LightStar"]:
                await sharedmethods.send_notification(self.expedition.ctx_object, self.expedition.player_obj,
                                                      "Item", self.reward_items[1].item_id)
        callbacks = {0: option_callback, 1: option_callback, 2: speed_callback}
        await callbacks[variant]()

    async def shrine_callback(self, interaction_obj, variant, active_room):
        adjuster = 1 if active_room.variant == "" else 2
        # Handle regular success
        self.embed = discord.Embed(colour=self.expedition.colour, title="Ritual Success!", description="")
        if random.randint(1, 100) <= self.success_rates[variant]:
            if self.reward_items[variant] is not None:
                item_id = self.reward_items[variant].item_id
                quantity = get_random_quantity(luck=self.expedition.luck, is_lucky=(adjuster == 2))
                inventory.update_stock(self.expedition.player_obj, item_id, quantity)
                self.embed.description = (f"{self.reward_items[variant].item_emoji} {quantity}x "
                                          f"{self.reward_items[variant].item_name}")
                await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
                return
            # Handle chaos success
            quantity = random.randint(1, 3) * adjuster
            self.expedition.luck += quantity
            self.embed.description = f"**Gained +{quantity} Luck**"
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle failure
        damage = self.expedition.take_damage((adjuster * 100), (adjuster * 300), active_room.room_element)
        dmg_msg = f'Unable to hold out you took {damage:,} damage.'
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.title, self.embed.description = "Ritual Failed!", dmg_msg
        if await self.check_death(interaction_obj):
            return
        self.expedition.luck = max(1, (self.expedition.luck - adjuster))
        output_msg = f"**Lost -{adjuster} Luck**\n{hp_msg}"
        self.embed.add_field(name="", value=output_msg, inline=False)
        await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

    async def trial_callback(self, interaction_obj, variant, active_room):
        player_obj = self.expedition.player_obj
        temp_player = await player.get_player_by_id(player_obj.player_id)
        output_msg = "Cost could not be paid. Nothing Gained."
        reward = 2 * (variant + 1) - 1

        async def offering_callback():
            cost = int(0.1 * reward * player_obj.player_mHP)
            if cost < player_obj.player_cHP:
                player_obj.player_cHP -= cost
                hp_msg = sharedmethods.display_hp(player_obj.player_cHP, player_obj.player_mHP)
                return True, f"Sacrificed {cost:,} HP\n{hp_msg}\nGained +{reward} luck!"
            return False, output_msg

        async def greed_callback():
            cost = adventuredata.greed_cost_list[variant]
            if temp_player.player_coins >= cost:
                cost_msg = temp_player.adjust_coins(cost, True)
                return True, f"Sacrificed {cost_msg} lotus coins\nRemaining: {temp_player.player_coins}\nGained +{reward} luck!"
            return False, output_msg

        async def soul_callback():
            cost = int(200 * variant - 100)
            if temp_player.player_stamina >= cost:
                temp_player.player_stamina -= cost
                temp_player.set_player_field("player_stamina", temp_player.player_stamina)
                return True, f"Sacrificed {cost} stamina\nRemaining: {temp_player.player_stamina}\nGained +{reward} luck!"
            return False, output_msg,

        callbacks = {"Offering": offering_callback, "Greed": greed_callback, "Soul": soul_callback}
        is_success, output_msg = await callbacks[self.expedition.room.variant]()
        title = "Trial Failed!"
        if is_success:
            title = "Trial Passed!"
            self.expedition.luck += reward
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=output_msg)
        await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

    async def crystal_callback(self, interaction_obj, variant, active_room):
        reward_id = "Scrap"
        prefix = ""
        if self.expedition.tier > 5:
            prefix = "Fragment" if random.randint(1, 1000) > self.expedition.luck else "Core"
            reward_id = f"{prefix}{min(4, self.expedition.tier - 4)}"
        reward = inventory.BasicItem(reward_id)
        luck_qty = ((self.expedition.tier // 4) + 1) * (variant + 1)
        item_qty = luck_qty if prefix != "Core" else 1
        # Handle failure
        if random.randint(1, 100) > self.success_rates[variant]:
            title_msg, output_msg = f"Nothing Found!", f"You leave empty handed.\n**Luck -{luck_qty}**"
            self.expedition.luck = max(1, self.expedition.luck - luck_qty)
            self.embed = discord.Embed(colour=self.expedition.colour, title=title_msg, description=output_msg)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle success
        title, output_msg = "Found Materials!", f"{reward.item_emoji} {item_qty}x {reward.item_name}\n**Luck +1**"
        inventory.update_stock(self.expedition.player_obj, reward.item_id, item_qty)
        self.expedition.luck += luck_qty
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=output_msg)
        await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

    async def sanctuary_callback(self, interaction_obj, variant, active_room):
        item_type = "Origin" if "Origin" in self.reward_items[variant].item_id else "Cores"
        qty = 1 if item_type == "Origin" else random.randint((1 + self.expedition.luck), (10 + self.expedition.luck))
        inventory.update_stock(self.expedition.player_obj, self.reward_items[variant].item_id, qty)
        title = f"{item_type} Collected!"
        output_msg = f"{self.reward_items[variant].item_emoji} {qty}x {self.reward_items[variant].item_name}"
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=output_msg)
        await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

    async def pact_callback(self, interaction_obj, variant, active_room):
        pact_details = active_room.variant.split(';')
        demon_type = pact.demon_variants[int(pact_details[0])]

        async def forge_pact():
            blood_cost = int(self.expedition.player_obj.player_mHP * (self.success_rates[variant] * 0.01))
            # Handle insufficient hp.
            if self.expedition.player_obj.player_cHP <= blood_cost:
                output = f"Unable to provide sufficient blood to forge the pact, the {demon_type} consumes you."
                self.expedition.player_obj.player_cHP = 0
                if await self.check_death(interaction_obj, result_msg=output):
                    return
            # Pay the cost. Forge the pact.
            self.expedition.player_obj.player_cHP -= blood_cost
            temp_user = await player.get_player_by_discord(self.expedition.player_obj.discord_id)
            temp_user.pact = active_room.variant
            temp_user.set_player_field("player_pact", temp_user.pact)
            self.embed = pact.display_pact(temp_user)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

        async def refuse_pact():
            trigger_return, description = await self.handle_combat(interaction_obj, 200, 600, self.expedition.luck)
            if trigger_return:
                return
            hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
            temp_user = await player.get_player_by_id(self.expedition.player_obj.player_id)
            exp_value = 500 + (100 * self.expedition.tier) + (25 * self.expedition.luck)
            exp_message, lvl_change = temp_user.adjust_exp(exp_value)
            description = f"{description}\n{hp_msg}\n{globalitems.exp_icon} {exp_message} Exp Acquired."
            self.embed.add_field(name=f"{demon_type} Defeated!", value=description, inline=False)
            await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)
            if lvl_change == 0:
                return
            await sharedmethods.send_notification(self.expedition.ctx_object, temp_user, "Level", lvl_change)
        callbacks = {0: refuse_pact, 1: forge_pact}
        await callbacks[variant]()

    async def treasure_callback(self, interaction_obj, variant, active_room):
        # Handle bypass option
        if variant == 1:
            await self.bypass_callback(interaction_obj)
            return
        # Handle treasure outcome.
        if not active_room.check_trap(self.expedition.luck):
            await self.treasure_found(interaction_obj, active_room.reward_type)
            return
        # Handle greater trap outcome.
        if active_room.room_type != "treasure":
            trap_msg = "You have fallen for the ultimate elder mimic's clever ruse!"
            self.embed.add_field(name="Eaten - Run Ended", value=trap_msg, inline=False)
            self.expedition.player_obj.player_cHP = 0
            if await self.check_death(interaction_obj):
                return
        # Handle regular trap outcome
        damage = self.expedition.take_damage(100, 300, active_room.room_element)
        if await self.check_death(interaction_obj):
            return
        dmg_msg = f'The mimic bites you dealing {damage:,} damage.'
        hp_msg = f'{self.expedition.player_obj.player_cHP} / {self.expedition.player_obj.player_mHP} HP'
        self.embed.add_field(name="", value=f"{dmg_msg}\n{hp_msg}", inline=False)
        await interaction_obj.response.edit_message(embed=self.embed, view=self.new_view)

    async def trap_triggered(self, interaction):
        self.embed = self.expedition.room.embed
        room_element = self.expedition.room.room_element
        # Handle fatal trap
        if random.randint(1, 100) <= max(0, (15 - self.expedition.luck)):
            trap_msg = adventuredata.trap_trigger2_list[room_element]
            self.expedition.player_obj.player_cHP = 0
            _ = await self.check_death(interaction, result_msg=trap_msg)
            return
        # Handle regular traps
        self.embed.add_field(name="Trap Triggered!", value=adventuredata.trap_trigger1_list[room_element], inline=False)
        # Handle teleport
        if self.expedition.room.room_element >= 6:
            self.expedition.teleport()
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        # Handle damage
        dmg_msg = f'You took {self.expedition.take_damage(100, 300, room_element):,} damage.'
        self.embed.add_field(name="", value=dmg_msg, inline=False)
        if await self.check_death(interaction):
            return
        hp_msg = sharedmethods.display_hp(self.expedition.player_obj.player_cHP, self.expedition.player_obj.player_mHP)
        self.embed.add_field(name="", value=hp_msg, inline=False)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        return

    async def handle_combat(self, interaction, min_dmg, max_dmg, unscathed_rate):
        if random.randint(1, 100) < unscathed_rate:
            description_msg = f'You emerge unscathed from combat.'
            return False, description_msg
        # Handle regular damage.
        damage = self.expedition.take_damage(min_dmg, max_dmg, self.expedition.room.room_element)
        description_msg = f'You took {damage:,} damage.'
        if await self.check_death(interaction):
            return True, description_msg
        return False, description_msg

    async def check_death(self, interaction, result_msg="", title_msg=""):
        if title_msg == "":
            title_msg = "Slain"
        if self.expedition.player_obj.player_cHP > 0:
            return False
        death_header, death_msg = "__Thana, The Death__", random.choice(adventuredata.death_msg_list)
        self.embed = discord.Embed(colour=self.expedition.colour, title=title_msg, description=result_msg)
        self.embed.add_field(name=death_header, value=death_msg, inline=False)
        self.new_view = None
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        return True

    async def treasure_found(self, interaction, treasure_type):
        bonus = 0
        # Handle fragment rewards.
        if self.expedition.tier > 4:
            qty = get_random_quantity(luck=self.expedition.luck, is_lucky=self.expedition.room.variant == "Greater")
            reward = inventory.BasicItem(f"Fragment{min((self.expedition.tier - 4), 4)}")
            loot_msg = f"{reward.item_emoji} {qty}x {reward.item_name}"
            self.embed = discord.Embed(colour=self.expedition.colour, title="Fragments Acquired!", description=loot_msg)
            update_stock = inventory.update_stock(self.expedition.player_obj, reward.item_id, qty)
            return
        # Handle gear item rewards.
        reward_tier = inventory.generate_random_tier(luck_bonus=(self.expedition.luck + bonus))
        reward_item = inventory.CustomItem(self.expedition.player_obj.player_id, treasure_type, reward_tier)
        self.embed, self.new_view = await reward_item.create_citem_embed(), ItemView(self.expedition, reward_item)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)
        return

    def custom_assignments(self):
        match self.expedition.room.room_type:
            case "selection_room":
                self.assign_selection_data()
            case "boss_shrine":
                self.assign_shrine_data()
            case "trial_room":
                self.assign_trial_data()
            case "sanctuary_room":
                self.assign_sanctuary_data()
            case _:
                pass

    def assign_selection_data(self):
        reward_tier = 6 if random.randint(1, 10000) <= self.expedition.luck else min(5, self.expedition.luck // 5)
        selected_pool = adventuredata.selection_pools[reward_tier]
        item_location = random.sample(range(0, (len(selected_pool) - 1)), 2)
        selected_set = [selected_pool[item_location[0]], selected_pool[item_location[1]]]
        selected_set = check_essence(selected_set, reward_tier)
        self.reward_items = [inventory.BasicItem(selected_set[0]), inventory.BasicItem(selected_set[1])]
        self.option1.label = f"{self.reward_items[0].item_name}"
        self.option1.emoji = self.reward_items[0].item_emoji
        self.option2.label = f"{self.reward_items[1].item_name}"
        self.option2.emoji = self.reward_items[1].item_emoji

    def assign_shrine_data(self):
        player_obj, active_room = self.expedition.player_obj, self.expedition.room
        boss_num = 3
        if self.expedition.room.room_deity not in tarot.card_dict.keys():
            boss_num = globalitems.boss_list.index(self.expedition.room.room_deity)
        shrine_data = adventuredata.shrine_dict[boss_num]
        reward_2_id = f"Unrefined{boss_num}" if boss_num != 4 else f"Token{inventory.generate_random_tier(max_tier=7)}"
        self.reward_items = [inventory.BasicItem(f"Gem{boss_num}"), inventory.BasicItem(reward_2_id), None]
        res_list = [player_obj.elemental_resistance[3], player_obj.elemental_resistance[4],
                    player_obj.elemental_resistance[active_room.room_element]]
        selected_elements = [shrine_data[1], shrine_data[3], active_room.room_element]
        self.success_rates = [min(100, int(resistance * 100) + 5) for resistance in res_list]
        self.option1.label = f"Ritual of {shrine_data[0]} ({self.success_rates[0]}%)"
        self.option2.label = f"Ritual of {shrine_data[2]} ({self.success_rates[1]}%)"
        self.option3.label = f"Ritual of Chaos ({self.success_rates[2]}%)"
        self.option1.emoji = globalitems.global_element_list[selected_elements[0]]
        self.option2.emoji = globalitems.global_element_list[selected_elements[1]]
        self.option3.emoji = globalitems.global_element_list[selected_elements[2]]

    def assign_trial_data(self):
        variant = self.expedition.room.variant
        trial_details = adventuredata.trial_variants_dict[variant]
        variant_index = list(adventuredata.trial_variants_dict.keys()).index(variant)
        self.option1.label = trial_details[1][0]
        self.option1.emoji = trial_details[2][0]
        self.option1.style = globalitems.button_colour_list[variant_index]
        self.option2.label = trial_details[1][1]
        self.option2.emoji = trial_details[2][1]
        self.option2.style = globalitems.button_colour_list[variant_index]
        self.option3.label = trial_details[1][2]
        self.option3.emoji = trial_details[2][2]
        self.option3.style = globalitems.button_colour_list[variant_index]

    def assign_sanctuary_data(self):
        random_numbers = random.sample(range(9), 3)
        item_type = "Fae" if random.randint(1, 1000) > self.expedition.luck else "Origin"
        self.reward_items = [inventory.BasicItem(f"{item_type}{random_numbers[0]}"),
                             inventory.BasicItem(f"{item_type}{random_numbers[1]}"),
                             inventory.BasicItem(f"{item_type}{random_numbers[2]}")]
        for i in range(3):
            option = getattr(self, f'option{i + 1}')
            setattr(option, 'label', f"{self.reward_items[i].item_name}")
            setattr(option, 'emoji', self.reward_items[i].item_emoji)


class TransitionView(discord.ui.View):
    def __init__(self, expedition):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.embed, self.new_view = None, None

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.blurple, emoji="⬆️")
    async def proceed_callback(self, interaction: discord.Interaction, button: discord.Button):
        if await handle_map_interaction(self, interaction):
            return
        self.embed, self.new_view = await self.expedition.display_next_room(self.expedition.ctx_object, self.expedition.player_obj)
        self.expedition.room_num += 1
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


class ItemView(discord.ui.View):
    def __init__(self, expedition, item):
        super().__init__(timeout=None)
        self.expedition = expedition
        self.item = item
        self.embed, self.new_view = None, None

    @discord.ui.button(label="Claim Item", style=discord.ButtonStyle.blurple)
    async def claim_callback(self, interaction: discord.Interaction, button: discord.Button):
        if await handle_map_interaction(self, interaction):
            return
        self.item.item_id = inventory.add_custom_item(self.item)
        self.new_view = TransitionView(self.expedition)
        if self.item.item_id == 0:
            self.embed = inventory.full_inventory_embed(self.item, self.expedition.colour)
            await interaction.response.edit_message(embed=self.embed, view=self.new_view)
            return
        title, description = "Item Claimed!", f"Item ID: {self.item.item_id} has been placed in your gear inventory."
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(label="Sell Item", style=discord.ButtonStyle.success)
    async def sell_callback(self, interaction: discord.Interaction, button: discord.Button):
        if await handle_map_interaction(self, interaction):
            return
        self.new_view = TransitionView(self.expedition)
        sell_value = inventory.sell_value_by_tier[self.item.item_tier]
        temp_user = await player.get_player_by_id(self.expedition.player_obj.player_id)
        sell_msg = temp_user.adjust_coins(sell_value)
        title, description = "Item Sold!", f"{globalitems.coin_icon} {sell_msg} lotus coins acquired."
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)

    @discord.ui.button(label="Scrap Item", style=discord.ButtonStyle.success)
    async def scrap_callback(self, interaction: discord.Interaction, button: discord.Button):
        if await handle_map_interaction(self, interaction):
            return
        self.new_view = TransitionView(self.expedition)
        scrap_item = inventory.BasicItem("Scrap")
        inventory.update_stock(self.expedition.player_obj, scrap_item.item_id, self.item.item_tier)
        title, description = "Item Scrapped!", f"{scrap_item.item_emoji} {self.item.item_tier}x {scrap_item.item_name}"
        self.embed = discord.Embed(colour=self.expedition.colour, title=title, description=description)
        await interaction.response.edit_message(embed=self.embed, view=self.new_view)


def check_essence(selected_items, pool_tier):
    checked_items = selected_items.copy()
    for item_index, item in enumerate(selected_items):
        if item == "ESS":
            selected_data = [card_number for card_number, data in tarot.card_dict.items() if data[1] == pool_tier]
            essence_id = f"Essence{random.choice(selected_data)}"
            checked_items[item_index] = essence_id
    return checked_items


monster_dict = {
    "slime": 50, "bat": 100, "spider": 200, "wolf": 300, "goblin": 400,
    "skeleton": 500, "faerie": 600, "ogre": 700, "harpy": 800, "fiend": 900,
    "lamia": 1000, "lich": 1500, "teyeger": 2000, "minotaur": 2500, "basilisk": 3000,
    "sky manta": 3500, "phoenix": 4000, "chimaera": 4500, "hydra": 5000, "dragon": 9999
}
gem_list = [("Rock", 1), ("Bronze Chunk", 500), ("Silver Chunk", 1000),
            ("Gold Ore", 5000), ("Platinum Ore", 10000), ("Bismuth Ore", 20000),
            ("GEMSTONE", 30000), ("GEMSTONE", 40000), ("GEMSTONE", 50000),
            ("GEMSTONE", 75000), ("GEMSTONE", 100000), ("GEMSTONE", 150000),
            ("Aurora Tear", 250000), ("Aurora Tear", 500000), ("Aurora Tear", 1000000),
            ("Aurora Tear", 2500000), ("Lotus of Abundance", 5000000), ("Stone of the True Void", 10000000)]


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
        output_msg = await handle_hunt(ctx_object, player_obj, success_rate)
    elif method_info[0] == "Mine":
        output_msg = await handle_mine(ctx_object, player_obj, success_rate)
    else:
        output_msg = await handle_gather(ctx_object, player_obj, success_rate)
    embed_msg = discord.Embed(colour=colour, title=title_msg, description=output_msg)
    return embed_msg


async def handle_hunt(ctx_object, player_obj, success_rate):
    death_dict = {1: "defeated", 2: "slain", 3: "slaughtered", 4: "massacred"}
    temp_dict = {}
    total_exp = 0
    output_msg = ""
    # Build the result dict.
    for _ in range(player_obj.player_echelon + 5):
        if random.randint(1, 100) <= success_rate:
            enemy_num = random.randint(0, 9) + random.randint(0, player_obj.player_echelon)
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
    item_obj, item_icon = None, " "
    item_id_dict = {"GEMSTONE": f"Gemstone{random.randint(1, 10)}", "Bismuth Ore": "Gemstone0",
                    "Lotus of Abundance": "Lotus5", "Aurora Tear": "Gemstone11", "Stone of the True Void": "Gemstone12"}
    outcome_index = sharedmethods.generate_ramping_reward(success_rate, 15, 18)
    outcome_index = max(outcome_index, player_obj.player_echelon)
    outcome_item, outcome_coins = gem_list[outcome_index][0], gem_list[outcome_index][1]
    if outcome_item in item_id_dict.keys():
        item_obj = inventory.BasicItem(item_id_dict[outcome_item])
        item_icon = f" {item_obj.item_emoji}"
    if outcome_item == "Lotus of Abundance":
        await sharedmethods.send_notification(ctx_object, player_obj, "Item", item_obj.item_id)
    inventory.update_stock(player_obj, item_obj.item_id, 1)
    coin_msg = player_obj.adjust_coins(outcome_coins)
    item_name = item_obj.item_name if item_obj is not None else outcome_item
    return f"You found{item_icon} 1x {item_name}!\nReceived {globalitems.coin_icon} {coin_msg} Lotus Coins!"


async def handle_gather(ctx_object, player_obj, success_rate):
    output_msg = ""
    num_items = sum(success_rate >= random.randint(1, 100) for _ in range(player_obj.player_echelon + 4))
    if num_items == 0:
        return "No items found."
    reward_list = loot.generate_random_item(quantity=num_items)
    for (reward_id, item_qty) in reward_list:
        reward_object = inventory.BasicItem(reward_id)
        output_msg += f"{reward_object.item_emoji} {item_qty}x {reward_object.item_name} received!\n"
        if "Lotus" in reward_object.item_id or reward_object.item_id in ["DarkStar", "LightStar"]:
            await sharedmethods.send_notification(ctx_object, player_obj, "Item", reward_object.item_id)
    batch_df = sharedmethods.list_to_batch(player_obj, reward_list)
    inventory.update_stock(None, None, None, batch=batch_df)
    return output_msg


class ManifestView(discord.ui.View):
    def __init__(self, ctx_obj, player_user, current_embed, e_tarot, colour, num_hours):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_user = ctx_obj, player_user
        self.e_tarot = e_tarot
        self.colour, self.num_hours = colour, num_hours
        self.current_embed = current_embed
        self.new_embed, self.new_view = None, None

        if self.player_user.player_echelon < 2:
            self.gather_callback.style = discord.ButtonStyle.secondary
            self.gather_callback.disabled = True
        if self.player_user.player_echelon < 4:
            self.mine_callback.style = discord.ButtonStyle.secondary
            self.mine_callback.disabled = True

    @discord.ui.button(label="Hunt", style=discord.ButtonStyle.success, emoji="⚔️")
    async def hunt_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        await self.manifest_callback(interaction, "Hunt")

    @discord.ui.button(label="Gather", style=discord.ButtonStyle.success, emoji="⚔️")
    async def gather_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        await self.manifest_callback(interaction, "Gather")

    @discord.ui.button(label="Mine", style=discord.ButtonStyle.success, emoji="⚔️")
    async def mine_callback(self, interaction: discord.Interaction, map_select: discord.ui.Select):
        await self.manifest_callback(interaction, "Mine")

    async def manifest_callback(self, interaction, method):
        if await sharedmethods.check_click(interaction, self.player_user, self.new_embed, self.new_view):
            return
        await self.player_user.reload_player()
        existing_timestamp, _ = self.player_user.check_cooldown("manifest")
        # Check existing manifestation
        if existing_timestamp:
            self.current_embed.clear_fields()
            self.current_embed.add_field(name="In Progress!", value="You've already got a manifestation running!")
            await interaction.response.edit_message(embed=self.current_embed, view=self.new_view)
            return
        # Handle successful embark
        if self.player_user.spend_stamina(500):
            method_info = f"{method};{self.e_tarot.card_numeral};{self.e_tarot.num_stars}"
            self.player_user.set_cooldown("manifest", method_info)
            self.new_embed = discord.Embed(colour=self.colour, title=f"{self.e_tarot.card_name} Embarks [{method}]",
                                           description=f"Expected return time: {self.num_hours} hours.")
            self.new_view = SkipView(self.ctx_obj, self.player_user, method_info)
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        # Handle insufficient stamina
        self.current_embed.clear_fields()
        self.current_embed.add_field(name="Not Enough Stamina!", value="Please check your /stamina!")
        await interaction.response.edit_message(embed=self.current_embed, view=self)


class SkipView(discord.ui.View):
    def __init__(self, ctx_obj, player_user, method_info):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_user = ctx_obj, player_user
        self.method_info = method_info
        self.new_embed, self.new_view = None, None
        self.cost_item = inventory.BasicItem("Token7")
        self.skip_cooldown.emoji = self.cost_item.item_emoji

    @discord.ui.button(label="Advance Cooldown", style=discord.ButtonStyle.danger, emoji="⏩")
    async def skip_cooldown(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await sharedmethods.check_click(interaction, self.player_user, self.new_embed, self.new_view):
            return
        colour, _ = sharedmethods.get_gear_tier_colours(self.player_user.player_echelon)
        self.new_embed = discord.Embed(colour=colour, title="", description="")
        cost_stock = inventory.check_stock(self.player_user, self.cost_item.item_id)
        if cost_stock <= 0:
            self.new_embed.title = "Manifest - Out of Stock"
            self.new_embed.description = sharedmethods.get_stock_msg(self.cost_item, cost_stock)
            self.new_view = SkipView(self.ctx_obj, self.player_user, self.method_info)
            await interaction.response.edit_message(embed=self.new_embed, view=self)
            return
        difference, method_info = self.player_user.check_cooldown("manifest")
        if not difference:
            await interaction.response.edit_message(view=self.new_view)
            return
        wait_time = timedelta(hours=(14 + self.player_user.player_echelon))
        if difference <= wait_time:
            inventory.update_stock(self.player_user, self.cost_item.item_id, -1)
            self.player_user.set_cooldown("manifest", "", rewind_days=2)
        self.new_embed = await build_manifest_return_embed(self.ctx_obj, self.player_user, method_info, colour)
        self.new_view = RepeatView(self.ctx_obj, self.player_user, self.method_info)
        self.player_user.clear_cooldown("manifest")
        await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)


class RepeatView(discord.ui.View):
    def __init__(self, ctx_obj, player_user, method_info):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_user = ctx_obj, player_user
        self.method_info = method_info
        self.new_embed, self.new_view = None, None

    @discord.ui.button(label="Repeat Last Manifest", style=discord.ButtonStyle.primary, emoji="🔁")
    async def repeat_manifest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await sharedmethods.check_click(interaction, self.player_user, self.new_embed, self.new_view):
            return
        await self.player_user.reload_player()
        colour, _ = sharedmethods.get_gear_tier_colours(self.player_user.player_echelon)
        self.new_embed = discord.Embed(colour=colour, title="", description="")

        # Check existing manifestation
        existing_timestamp, _ = self.player_user.check_cooldown("manifest")
        if existing_timestamp:
            self.new_embed.title = "In Progress!"
            self.new_embed.description = "You've already got a manifestation running!"
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        # Ensure there's enough stamina to perform the action
        if not self.player_user.spend_stamina(500):
            self.new_embed.title = "Insufficient Stamina"
            self.new_embed.description = "You do not have enough stamina to repeat the action."
            self.new_view = RepeatView(self.ctx_obj, self.player_user, self.method_info)
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return

        # Handle successful embark
        method, card_numeral, num_stars = self.method_info.split(';')
        card_name = "Pandora, The Celestial"
        if self.player_user.equipped_tarot != "":
            e_tarot = tarot.check_tarot(self.player_user.player_id, tarot.card_dict[self.player_user.equipped_tarot][0])
            card_name, num_stars = e_tarot.card_name, e_tarot.num_stars
        new_method_info = f"{method};{card_numeral};{num_stars}"
        self.player_user.set_cooldown("manifest", new_method_info)
        self.new_embed = discord.Embed(colour=colour, title=f"{card_name} Embarks [{method}]",
                                       description=f"Expected return time: {14 + self.player_user.player_echelon} hours.")
        self.new_view = SkipView(self.ctx_obj, self.player_user, new_method_info)
        await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
        return




