# General imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import asyncio
import random

# Bot imports
import battleengine

# Data Imports
import globalitems
import sharedmethods
import leaderboards

# Core imports
import player
import inventory
import menus

# Combat imports
import combat
import bosses

# Item/crafting imports
import loot


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
            bosses.clear_boss_info(self.channel_id, 0)
            level, boss_type, boss_tier = bosses.get_raid_boss_details(self.channel_num)
            active_boss = bosses.spawn_boss(self.channel_id, 0, boss_tier, boss_type, level, self.channel_num)
            self.active_boss = active_boss
            self.combat_tracker_list = []
            embed_msg = active_boss.create_boss_embed()
            raid_button = battleengine.RaidView(self.channel_num)
            sent_message = await self.channel_object.send(embed=embed_msg, view=raid_button)
            self.sent_message = sent_message


class SoloCog(commands.Cog):
    def __init__(self, bot, player_obj, active_boss, channel_id, sent_message, ctx_object, gauntlet=False):
        self.bot = bot
        self.player_obj, self.active_boss = player_obj, active_boss
        self.channel_id, self.sent_message = channel_id, sent_message
        self.ctx_object, self.channel_object = ctx_object, ctx_object.channel
        self.combat_tracker = combat.CombatTracker(player_obj)
        self.gauntlet = gauntlet
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
                bosses.clear_boss_info(self.channel_id, self.player_obj.player_id)
                self.cog_unload()
                return
            is_alive, self.active_boss = await self.bot.solo_boss(
                self.combat_tracker, self.player_obj, self.active_boss,
                self.channel_id, self.sent_message, self.channel_object,
                gauntlet=self.gauntlet
            )
            if is_alive:
                return
            if "XXX" in self.active_boss.boss_name:
                await leaderboards.update_leaderboard(self.combat_tracker, self.player_obj, self.ctx_object)
            self.cog_unload()


class PvPCog(commands.Cog):
    def __init__(self, bot, ctx_obj, player1, player2, channel_id, sent_message, channel_object):
        self.bot, self.ctx_obj = bot, ctx_obj
        self.channel_object, self.channel_id = channel_object, channel_id
        self.player1, self.player2 = player1, player2
        self.sent_message = sent_message
        self.combat_tracker1, self.combat_tracker2 = combat.CombatTracker(self.player1), combat.CombatTracker(self.player2)
        self.combat_tracker1.player_cHP, self.combat_tracker2.player_cHP = self.player1.player_mHP, self.player2.player_mHP
        self.colour, _ = sharedmethods.get_gear_tier_colours(self.player1.player_echelon)
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
        loot_item = inventory.BasicItem("Crate")
        # Determine winners.
        if (not is_alive_player1 and not is_alive_player2) or self.combat_tracker1.total_cycles >= 50:
            winner, result_message, quantity = "Draw", "It's a draw!", 1
            exp_amount *= 5
            inventory.update_stock(self.player1, "Crate", quantity)
            inventory.update_stock(self.player2, "Crate", quantity)
            loot_msg = f"Both Players {loot_item.item_emoji} {quantity}x crate(s) acquired!"
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
            inventory.update_stock(winner, "Crate", quantity)
            loot_msg = f"{winner.player_username} {loot_item.item_emoji} {quantity}x crates acquired!"
        exp_msg, lvl_adjust = self.player1.adjust_exp(exp_amount)
        exp_description = f"{exp_msg} EXP acquired!"
        pvp_embed.add_field(name=result_message, value=f"{exp_description}\n{loot_msg}", inline=False)
        await self.sent_message.edit(embed=pvp_embed)
        if lvl_adjust != 0:
            await sharedmethods.send_notification(self.ctx_obj, self.player1, "Level", lvl_adjust)
        self.cog_unload()

    async def update_combat_embed(self, stun_list, hit_list):
        pvp_embed = discord.Embed(title="Arena PvP", description="", color=self.colour)
        # pvp_embed.set_thumbnail(url="")
        player_1_hp_msg = f"{sharedmethods.display_hp(self.combat_tracker1.player_cHP, self.player1.player_mHP)}"
        player_2_hp_msg = f"{sharedmethods.display_hp(self.combat_tracker2.player_cHP, self.player2.player_mHP)}"
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
        if self.player1.bleed_application >= 1:
            await self.handle_pvp_bleed([0, 1], combatants, trackers, hit_list, False)
        if self.player1.bleed_application >= 1:
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
        scaled_dmg = combat.pvp_scale_damage(role_order, combatants, hit_damage)
        hit_msg = f"{combatants[attacker].player_username} - {combo_count[attacker]}x Combo: {skill_name} {sharedmethods.number_conversion(scaled_dmg)}"
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
        hit_msg = f"{combatant[attacker].player_username} - Ultimate: {skill_name} {sharedmethods.number_conversion(scaled_dmg)}"
        hit_msg += f"{status_msg}{second_msg}{critical_type}{evade}"
        hit_list.append([scaled_dmg, hit_msg])
        tracker[defender].player_cHP -= scaled_dmg
        if combatant[attacker].bleed_application >= 1:
            await self.handle_pvp_bleed(role_order, combatant, tracker, hit_list, True)

    async def handle_pvp_bleed(self, role_order, combatant, tracker, hit_list, is_ultimate):
        attacker, defender = role_order[0], role_order[1]
        e_weapon = await inventory.read_custom_item(combatant[attacker].player_equipped[0])
        bleed_damage = combatant[attacker].get_player_initial_damage()
        _, bleed_damage = combat.pvp_defences(combatant[attacker], combatant[defender], bleed_damage, e_weapon)
        bleed_data = await combat.trigger_bleed(tracker[attacker], combatant[attacker],
                                          pvp_data=[role_order, combatant, bleed_damage])
        hit_list.append([bleed_data[0], f"{combatant[attacker].player_username} - {bleed_data[1]}"])

