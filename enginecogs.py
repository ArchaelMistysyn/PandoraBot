# General imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import asyncio
import random

# Bot imports
import battleengine

# Data Imports
import globalitems as gli
import pilengine
import sharedmethods as sm
import adventuredata

# Core imports
import player
import inventory
import menus

# Combat imports
import combat
import bosses
import encounters

# Item/crafting imports
import loot
import tarot


class RaidCog(commands.Cog):
    def __init__(self, bot, active_boss, channel_id, channel_num, sent_message, channel_object):
        self.bot = bot
        self.active_boss = active_boss
        self.channel_id = channel_id
        self.channel_num = channel_num
        self.sent_message = sent_message
        self.channel_object = channel_object
        self.combat_tracker_list = []
        self.lock = asyncio.Lock()
        self.raid_manager.start()

    def cog_unload(self):
        self.raid_manager.cancel()

    @tasks.loop(seconds=60)
    async def raid_manager(self):
        async with self.lock:
            is_alive = await self.bot.raid_boss(self.combat_tracker_list, self.active_boss,
                                                self.channel_id, self.channel_num,
                                                self.sent_message, self.channel_object)
            if is_alive:
                return
            await bosses.clear_boss_info(self.channel_id, 0)
            level, boss_type, boss_tier = encounters.get_raid_boss_details(self.channel_num)
            active_boss = await bosses.spawn_boss(self.channel_id, 0, boss_tier, boss_type, level, self.channel_num)
            self.active_boss = active_boss
            self.combat_tracker_list = []
            embed_msg = active_boss.create_boss_embed()
            raid_button = battleengine.RaidView(self.channel_num)
            sent_message = await self.channel_object.send(embed=embed_msg, view=raid_button)
            self.sent_message = sent_message


class SoloCog(commands.Cog):
    def __init__(self, bot, player_obj, active_boss, channel_id, sent_message, ctx_object, gauntlet=False, mode=0):
        self.bot = bot
        self.player_obj, self.active_boss = player_obj, active_boss
        self.channel_id, self.sent_message = channel_id, sent_message
        self.ctx_object, self.channel_object = ctx_object, ctx_object.channel
        self.combat_tracker = combat.CombatTracker(player_obj)
        self.gauntlet, self.mode = gauntlet, mode
        self.lock = asyncio.Lock()

    async def run(self):
        self.solo_manager.start()

    def cog_unload(self):
        self.solo_manager.cancel()

    @tasks.loop(seconds=60)
    async def solo_manager(self):
        async with self.lock:
            # Handle abandon
            if combat.check_flag(self.player_obj):
                combat.toggle_flag(self.player_obj)
                await bosses.clear_boss_info(self.channel_id, self.player_obj.player_id)
                self.cog_unload()
                return
            is_alive, self.active_boss = await self.bot.solo_boss(
                self.combat_tracker, self.player_obj, self.active_boss,
                self.channel_id, self.sent_message, self.channel_object, gauntlet=self.gauntlet, mode=self.mode)
            if is_alive:
                return
            self.cog_unload()


class PvPCog(commands.Cog):
    def __init__(self, bot, ctx_obj, player1, player2, sent_message, channel_object):
        self.bot, self.ctx_obj = bot, ctx_obj
        self.channel_object = channel_object
        self.player1, self.player2 = player1, player2
        self.sent_message = sent_message
        self.combat_tracker1, self.combat_tracker2 = combat.CombatTracker(self.player1), combat.CombatTracker(self.player2)
        self.combat_tracker1.player_cHP, self.combat_tracker2.player_cHP = self.player1.player_mHP, self.player2.player_mHP
        self.colour, _ = sm.get_gear_tier_colours(self.player1.player_echelon)
        self.hit_list = []
        self.lock = asyncio.Lock()

    async def run(self):
        self.pvp_manager.start()

    def cog_unload(self):
        self.pvp_manager.cancel()

    @tasks.loop(seconds=30)
    async def pvp_manager(self):
        async with self.lock:
            await self.run_pvp_cycle()

    async def run_pvp_cycle(self):
        stun_list, hit_list, is_alive_player1, is_alive_player2 = await self.calculate_pvp_cycle()
        pvp_embed = await self.update_combat_embed(stun_list, hit_list)
        winner, quantity = None, 2
        exp_amount = random.randint(self.player1.player_echelon * 100, self.player1.player_echelon * 200)
        loot_item = inventory.BasicItem("Chest")
        # Determine winners.
        if (not is_alive_player1 and not is_alive_player2) or self.combat_tracker1.total_cycles >= 50:
            winner, result_message, quantity = "Draw", "It's a draw!", 1
            exp_amount *= 5
            await inventory.update_stock(self.player1, "Chest", quantity)
            await inventory.update_stock(self.player2, "Chest", quantity)
            loot_msg = f"Both Players {loot_item.item_emoji} {quantity}x Chest(s) acquired!"
        elif not is_alive_player1:
            winner = self.player2
        elif not is_alive_player2:
            winner = self.player1
            exp_amount *= 10
        # Continue the combat.
        if winner is None:
            await self.sent_message.edit(embed=pvp_embed)
            return
        # End the combat.
        if not isinstance(winner, str):
            result_message = f"{winner.player_username} wins!"
            await inventory.update_stock(winner, "Chest", quantity)
            loot_msg = f"{winner.player_username} {loot_item.item_emoji} {quantity}x Chests acquired!"
        exp_msg, lvl_adjust = self.player1.adjust_exp(exp_amount)
        exp_description = f"{exp_msg} EXP acquired!"
        pvp_embed.add_field(name=result_message, value=f"{exp_description}\n{loot_msg}", inline=False)
        await self.sent_message.edit(embed=pvp_embed)
        if lvl_adjust != 0:
            await sm.send_notification(self.ctx_obj, self.player1, "Level", lvl_adjust)
        self.cog_unload()

    async def update_combat_embed(self, stun_list, hit_list):
        pvp_embed = discord.Embed(title="Arena PvP", description="", color=self.colour)
        # pvp_embed.set_thumbnail(url="")
        player_1_hp_msg = f"{sm.display_hp(self.combat_tracker1.player_cHP, self.player1.player_mHP)}"
        player_2_hp_msg = f"{sm.display_hp(self.combat_tracker2.player_cHP, self.player2.player_mHP)}"
        pvp_embed.add_field(name=self.player1.player_username, value=player_1_hp_msg, inline=True)
        pvp_embed.add_field(name=self.player2.player_username, value=player_2_hp_msg, inline=True)
        battle_msg = f"Cycle Count: {self.combat_tracker1.total_cycles}"
        pvp_embed.add_field(name="", value=battle_msg, inline=False)
        hit_field, stun_field = "", ""
        for stun_msg in stun_list:
            stun_field += f"{stun_msg}\n"
        for hit in hit_list:
            hit_field += f"{hit[1]}\n"
        if stun_field != "":
            pvp_embed.add_field(name="Status", value=stun_field, inline=False)
        pvp_embed.add_field(name="Hits", value=hit_field, inline=False)
        return pvp_embed

    async def calculate_pvp_cycle(self):
        self.combat_tracker1.total_cycles += 1
        hit_list, stun_list = [], []
        combo_count = [0, 0]
        num_hits1, excess_hits1 = divmod(self.combat_tracker1.remaining_hits + self.player1.attack_speed, 1)
        num_hits2, excess_hits2 = divmod(self.combat_tracker2.remaining_hits + self.player2.attack_speed, 1)
        self.combat_tracker1.remaining_hits, self.combat_tracker2.remaining_hits = excess_hits1, excess_hits2
        # Apply status effects
        stun_msg1 = combat.handle_status(self.combat_tracker1, self.player1)
        stun_msg2 = combat.handle_status(self.combat_tracker2, self.player2)
        if stun_msg1 is not None:
            stun_list.append(stun_msg1)
            num_hits1 = 0
        if stun_msg2 is not None:
            stun_list.append(stun_msg2)
            num_hits2 = 0

        player_interval = [60 / num_hits1, 60 / num_hits2]
        attack_counter = player_interval
        combatants, trackers = [self.player1, self.player2], [self.combat_tracker1, self.combat_tracker2]
        while attack_counter[0] <= 60 or attack_counter[1] <= 60:
            await self.handle_pvp_attack(combatants, trackers, combo_count, attack_counter, player_interval, hit_list)
        if self.player1.bleed_app >= 1:
            await self.handle_pvp_bleed([0, 1], combatants, trackers, hit_list, False)
        if self.player1.bleed_app >= 1:
            await self.handle_pvp_bleed([1, 0], combatants, trackers, hit_list, False)
        return stun_list, hit_list, self.combat_tracker1.player_cHP > 0, self.combat_tracker2.player_cHP > 0

    async def handle_pvp_attack(self, combatants, trackers, combo_count, attack_counter, player_interval, hit_list):
        attacker, defender = (0, 1) if attack_counter[0] <= attack_counter[1] else (1, 0)
        role_order = [attacker, defender]
        stun_status, hit_damage, critical_type = await combat.pvp_attack(combatants[attacker], combatants[defender])
        if stun_status is not None:
            trackers[defender].stun_status = stun_status
            trackers[defender].stun_cycles += 1
        combo_count[attacker] += 1 + combatants[attacker].combo_application
        hit_damage, skill_name = combat.skill_adjuster(combatants[attacker], trackers[attacker], hit_damage,
                                                       combo_count[attacker], False)
        hit_damage, status_msg = combat.check_lock(combatants[attacker], trackers[attacker], hit_damage)
        hit_damage, second_msg = combat.check_bloom(combatants[attacker], hit_damage)
        hit_damage, evade = combat.handle_evasions(combatants[defender].block, combatants[defender].dodge, hit_damage)
        if status_msg == " *TIME SHATTER*" or critical_type != "":
            hit_damage *= random.randint(1, combatants[attacker].rng_bonus)
        scaled_dmg = combat.pvp_scale_damage(role_order, combatants, hit_damage)
        hit_msg = f"{combatants[attacker].player_username} - {combo_count[attacker]}x Combo: {skill_name} {sm.number_conversion(scaled_dmg)}"
        hit_msg += f"{status_msg}{second_msg}{critical_type}{evade}"
        hit_list.append([scaled_dmg, hit_msg])
        attack_counter[attacker] += player_interval[attacker]
        trackers[defender].player_cHP -= scaled_dmg
        combat.update_bleed(trackers[attacker], combatants[attacker])
        await self.handle_pvp_ultimate(role_order, combatants, trackers, combo_count, hit_list)

    async def handle_pvp_ultimate(self, role_order, combatant, tracker, combo_count, hit_list):
        attacker, defender = role_order[0], role_order[1]
        if tracker[attacker].charges < 20:
            return
        stun_status, hit_damage, critical_type = await combat.pvp_attack(combatant[attacker], combatant[defender])
        if stun_status is not None:
            tracker[defender].stun_status = stun_status
            tracker[defender].stun_cycles += 1
        combo_count[attacker] += 1 + combatant[attacker].combo_application
        hit_damage, skill_name = combat.skill_adjuster(combatant[attacker], tracker[attacker], hit_damage,
                                                       combo_count[attacker], True)
        scaled_dmg = combat.pvp_scale_damage(role_order, combatant, hit_damage)
        scaled_dmg, status_msg = combat.check_lock(combatant[attacker], tracker[attacker], scaled_dmg)
        scaled_dmg, second_msg = combat.check_bloom(combatant[attacker], scaled_dmg)
        scaled_dmg, evade = combat.handle_evasions(combatant[defender].block, combatant[defender].dodge, scaled_dmg)
        hit_msg = f"{combatant[attacker].player_username} - Ultimate: {skill_name} {sm.number_conversion(scaled_dmg)}"
        hit_msg += f"{status_msg}{second_msg}{critical_type}{evade}"
        hit_list.append([scaled_dmg, hit_msg])
        tracker[defender].player_cHP -= scaled_dmg
        if combatant[attacker].bleed_app >= 1:
            await self.handle_pvp_bleed(role_order, combatant, tracker, hit_list, True)

    async def handle_pvp_bleed(self, role_order, combatant, tracker, hit_list, is_ultimate):
        attacker, defender = role_order[0], role_order[1]
        e_weapon = await inventory.read_custom_item(combatant[attacker].player_equipped[0])
        bleed_damage = combatant[attacker].get_player_initial_damage()
        _, bleed_damage = combat.pvp_defences(combatant[attacker], combatant[defender], bleed_damage, e_weapon)
        bleed_data = await combat.trigger_bleed(tracker[attacker], combatant[attacker],
                                                pvp_data=[role_order, combatant, bleed_damage])
        hit_list.append([bleed_data[0], f"{combatant[attacker].player_username} - {bleed_data[1]}"])


class MapCog(commands.Cog):
    def __init__(self, bot, ctx_obj, player_obj, map_tier, sent_message, colour):
        self.bot, self.ctx_obj = bot, ctx_obj
        self.player_obj, self.player_cHP, self.player_mHP = player_obj, player_obj.player_mHP, player_obj.player_mHP
        self.player_regen = int(self.player_mHP * player_obj.hp_regen)
        self.sent_message, self.colour = sent_message, colour
        self.room_num, self.map_tier, self.map_title = 0, map_tier, adventuredata.reverse_map_tier_dict[map_tier]
        self.colour, _ = sm.get_gear_tier_colours(map_tier)
        self.hit_list = []
        self.lock = asyncio.Lock()
        self.exp_accumulated, self.coins_accumulated, self.items_accumulated = 0, 0, {}

    async def run(self):
        self.map_manager.start()

    def cog_unload(self):
        self.map_manager.cancel()

    @tasks.loop(seconds=120)
    async def map_manager(self):
        async with self.lock:
            status = await self.run_map_cycle()
            if status != "Continue":
                end_embed = self.build_base_embed()
                end_embed.description = "Expedition Completed!"
                if random.randint(1, 2000) <= self.map_tier:
                    reward_object = inventory.BasicItem("Lotus7")
                    current_qty = self.items_accumulated.get(reward_object.item_id, (reward_object, 0))[1]
                    self.items_accumulated[reward_object.item_id] = (reward_object, current_qty + 1)
                    await inventory.update_stock(self.player_obj, reward_object.item_id, 1)
                    if sm.check_rare_item(reward_object.item_id):
                        await sm.send_notification(self.ctx_obj, self.player_obj, "Item", reward_object.item_id)
                end_embed = await self.accumulated_output(end_embed)
                await self.sent_message.edit(embed=end_embed)
                await encounters.clear_automapper(self.player_obj.player_id)
                self.cog_unload()
            self.room_num += 1

    async def accumulated_output(self, embed_obj):
        accumulated_msg = ""
        if self.coins_accumulated != 0:
            accumulated_msg += f"{gli.coin_icon} {self.coins_accumulated:,}x Lotus Coins\n"
        if self.exp_accumulated != 0:
            accumulated_msg += f"{gli.exp_icon} {self.exp_accumulated:,}x EXP Acquired\n"
        if self.items_accumulated:
            for item_id, (item, qty) in self.items_accumulated.items():
                accumulated_msg += f"{item.item_emoji} {qty:,}x {item.item_name}\n"
        if accumulated_msg != "":
            embed_obj.add_field(name="Total Accumulated Rewards", value=accumulated_msg, inline=False)
        return embed_obj

    async def run_map_cycle(self):
        if self.room_num == max(8, self.map_tier * 2):
            return "Clear"
        # Trigger occurrence/deal damage to player
        room_type = random.choices(['Combat', 'Treasure', 'Mining', 'Storage', 'Fountain'],
                                   weights=[5, 4, 4, 3, 2], k=1)[0]
        room_embed, status = await self.run_room(room_type)
        await self.sent_message.edit(embed=room_embed)
        return status

    async def run_room(self, room_type):
        room_handlers = {'Combat': self.handle_combat_room, 'Treasure': self.handle_treasure_room,
                         'Mining': self.handle_mining_room, 'Storage': self.handle_storage_room,
                         'Fountain': self.handle_token_room}
        self.player_cHP = min(self.player_cHP + self.player_regen, self.player_obj.player_mHP)
        room_embed = await room_handlers[room_type]()
        return room_embed, ("Dead" if self.player_cHP <= 0 else "Continue")

    def build_base_embed(self):
        title = f"{self.player_obj.player_username} - {adventuredata.reverse_map_tier_dict[self.map_tier]} [AUTO]"
        return discord.Embed(colour=self.colour, title=title, description="")

    async def handle_combat_room(self):
        base_embed = self.build_base_embed()
        hp_msg = sm.display_hp(self.player_cHP, self.player_mHP)
        monster_data = [('basic_monster', 1), ('elite_monster', 2), ('legend_monster', 3)]
        threat, adjust = random.choices(monster_data, weights=[60, 30, 10], k=1)[0]
        dmg_element = random.randint(0, 8)
        element_descriptor = adventuredata.element_descriptor_list[dmg_element]
        match threat:
            case "basic_monster":
                monster = random.choice(adventuredata.monster_dict[threat])
                prefix = "An" if element_descriptor[0].lower() in adventuredata.vowel_list else "A"
                base_embed.description = f"{prefix} {element_descriptor} {monster} blocks your path!"
            case "elite_monster":
                monster = adventuredata.monster_dict[threat][dmg_element]
                base_embed.description = f"**{monster}** spotted!! It won't be long before it notices you."
                dmg_element = -1
            case "legend_monster":
                monster = adventuredata.monster_dict[threat][dmg_element]
                base_embed.description = f"__**{monster}**__ the legendary titan comes into view!!! DANGER!!!"
                dmg_element = -1
            case _:
                pass
        new_embed = base_embed.copy()
        base_embed.add_field(name="", value=hp_msg, inline=False)
        await self.sent_message.edit(embed=base_embed)
        await asyncio.sleep(60)
        # Damage Handling
        base_damage = random.randint(1000 * self.map_tier, 2000 * self.map_tier) * adjust
        damage = base_damage - base_damage * (self.player_obj.elemental_resistance[dmg_element] if dmg_element != -1 else 0)
        damage = int(damage - damage * self.player_obj.damage_mitigation * 0.01)
        self.player_cHP -= damage
        self.player_cHP = 1 if self.player_cHP <= 0 and adjust < 3 else max(0, self.player_cHP)
        hp_msg = sm.display_hp(self.player_cHP, self.player_mHP)
        dmg_msg = f"{self.player_obj.player_username} took {damage:,} damage!\n{hp_msg} HP"
        if self.player_cHP <= 0:
            new_embed.add_field(name="SLAIN", value=hp_msg, inline=False)
            return new_embed

        await self.player_obj.reload_player()

        # Handle ring souls
        if self.player_obj.player_equipped[4] != 0:
            e_ring = await inventory.read_custom_item(self.player_obj.player_equipped[4])
            if e_ring.item_base_type == "Crown of Skulls":
                e_ring.roll_values[1] = str(int(e_ring.roll_values[1]) + adjust)
                await e_ring.update_stored_item()

        # EXP Handling
        exp_awarded = int(base_damage / 10)
        self.exp_accumulated += exp_awarded
        exp_msg, lvl_adjust = self.player_obj.adjust_exp(exp_awarded)
        combined_msg = f"{dmg_msg}\n{gli.exp_icon} {exp_msg} Exp Acquired."
        new_embed.add_field(name="Monster Defeated", value=combined_msg, inline=False)
        if lvl_adjust != 0:
            await sm.send_notification(self.ctx_obj, self.player_obj, "Level", lvl_adjust)
        return new_embed

    async def handle_treasure_room(self):
        base_embed = self.build_base_embed()
        outcome, bonus = random.choices([(1, 1), (2, 5), (3, 10)], weights=[60, 30, 10], k=1)[0]
        hp_msg = sm.display_hp(self.player_cHP, self.player_mHP)
        base_embed.description = "Uncovered a treasure chamber!"
        new_embed = base_embed.copy()
        base_embed.add_field(name="", value=hp_msg, inline=False)
        await self.sent_message.edit(embed=base_embed)
        await asyncio.sleep(60)
        if outcome == 3 and self.map_tier >= 3:
            reward_object = inventory.BasicItem(f"Trove{self.map_tier - 2}")
            current_qty = self.items_accumulated.get(reward_object.item_id, (reward_object, 0))[1]
            self.items_accumulated[reward_object.item_id] = (reward_object, current_qty + 1)
            await inventory.update_stock(self.player_obj, reward_object.item_id, 1)
            field_value = f"{hp_msg} HP\n{reward_object.item_emoji} 1x {reward_object.item_name}"
        else:
            self.coins_accumulated += 1000 * bonus
            coin_msg = self.player_obj.adjust_coins(1000 * bonus)
            field_value = f"Acquired {gli.coin_icon} {coin_msg} lotus coins!"
        new_embed.add_field(name="", value=field_value, inline=False)
        return new_embed

    async def handle_mining_room(self):
        base_embed = self.build_base_embed()
        hp_msg = sm.display_hp(self.player_cHP, self.player_mHP)
        reward_list = loot.generate_random_item()
        reward_id = f"Fragment{min(4, self.map_tier - 4)}" if self.map_tier >= 5 else "Scrap"
        item_qty = self.map_tier if self.map_tier <= 4 else 1 if self.map_tier <= 8 else self.map_tier - 7
        reward_object = inventory.BasicItem(reward_id)
        current_qty = self.items_accumulated.get(reward_object.item_id, (reward_object, 0))[1]
        self.items_accumulated[reward_object.item_id] = (reward_object, current_qty + item_qty)
        base_embed.description = "Discovered a mining chamber!"
        new_embed = base_embed.copy()
        base_embed.add_field(name="", value=hp_msg, inline=False)
        await self.sent_message.edit(embed=base_embed)
        await asyncio.sleep(60)
        await inventory.update_stock(self.player_obj, reward_object.item_id, item_qty)
        field_value = f"{hp_msg} HP\n{reward_object.item_emoji} {item_qty}x {reward_object.item_name}"
        new_embed.add_field(name="", value=field_value, inline=False)
        return new_embed

    async def handle_storage_room(self):
        base_embed = self.build_base_embed()
        hp_msg = sm.display_hp(self.player_cHP, self.player_mHP)
        reward_list = loot.generate_random_item()
        reward_id, item_qty = reward_list[0]
        reward_object = inventory.BasicItem(reward_id)
        current_qty = self.items_accumulated.get(reward_object.item_id, (reward_object, 0))[1]
        self.items_accumulated[reward_object.item_id] = (reward_object, current_qty + item_qty)
        base_embed.description = "Found a storage chamber!"
        new_embed = base_embed.copy()
        base_embed.add_field(name="", value=hp_msg, inline=False)
        await self.sent_message.edit(embed=base_embed)
        await asyncio.sleep(60)
        await inventory.update_stock(self.player_obj, reward_object.item_id, item_qty)
        field_value = f"{hp_msg} HP\n{reward_object.item_emoji} {item_qty}x {reward_object.item_name}"
        new_embed.add_field(name="", value=field_value, inline=False)
        if sm.check_rare_item(reward_object.item_id):
            await sm.send_notification(self.ctx_obj, self.player_obj, "Item", reward_object.item_id)
        return new_embed

    async def handle_token_room(self):
        base_embed = self.build_base_embed()
        hp_msg = sm.display_hp(self.player_cHP, self.player_mHP)
        base_embed.description = "Entered a Spiritual Chamber!"
        new_embed = base_embed.copy()
        base_embed.add_field(name="", value=hp_msg, inline=False)
        await self.sent_message.edit(embed=base_embed)
        await asyncio.sleep(60)
        card_dict_copy = tarot.card_dict.copy()
        card_dict_copy.pop("XXX")
        essence_weight_data = [(f"Essence{id_key}", 8 - tier)
                               for id_key, (name, tier) in card_dict_copy.items() if tier <= self.map_tier]
        token_weight_data = [(f"Token{tier}", 8 - tier) for tier in range(1, 8) if tier <= self.map_tier]
        selected_data = token_weight_data if random.randint(1, 100) <= 75 else essence_weight_data
        weighted_list = [item for item, weight in selected_data for _ in range(weight)]
        new_embed.description = "The spiritual energy gathers and condenses into a new form."
        reward_object = inventory.BasicItem(random.choice(weighted_list))
        current_qty = self.items_accumulated.get(reward_object.item_id, (reward_object, 0))[1]
        self.items_accumulated[reward_object.item_id] = (reward_object, current_qty + 1)
        await inventory.update_stock(self.player_obj, reward_object.item_id, 1)
        field_value = f"{hp_msg} HP\n{reward_object.item_emoji} 1x {reward_object.item_name}"
        new_embed.add_field(name="", value=field_value, inline=False)
        return new_embed
