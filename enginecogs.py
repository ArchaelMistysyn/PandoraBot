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
            is_alive = await self.bot.solo_boss(self.combat_tracker, self.player_obj, self.active_boss,
                                                self.channel_id, self.sent_message, self.channel_object,
                                                gauntlet=self.gauntlet)
            if is_alive:
                return
            if "XXX" in self.active_boss.boss_name:
                await leaderboards.update_leaderboard(self.combat_tracker, self.player_obj, self.ctx_object)
            self.cog_unload()


class PvPCog(commands.Cog):
    def __init__(self, bot, player1, player2, channel_id, sent_message, channel_object):
        self.bot = bot
        self.player1 = player1
        self.player2 = player2
        self.channel_id = channel_id
        self.sent_message = sent_message
        self.channel_object = channel_object
        self.combat_tracker1 = combat.CombatTracker(self.player1)
        self.combat_tracker2 = combat.CombatTracker(self.player2)
        self.combat_tracker1.player_cHP = self.player1.player_mHP
        self.combat_tracker2.player_cHP = self.player2.player_mHP
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
        hit_list, is_alive_player1, is_alive_player2 = await self.calculate_cycle()
        if self.combat_tracker1.player_cHP <= 0:
            self.combat_tracker1.player_cHP = 0
        if self.combat_tracker2.player_cHP <= 0:
            self.combat_tracker2.player_cHP = 0
        pvp_embed = await self.update_combat_embed(hit_list)
        result_message = ""
        exp_msg = ""
        ended = False
        quantity = 2
        loot_item = inventory.BasicItem("i1r")
        if (not is_alive_player1 and not is_alive_player2) or self.combat_tracker1.total_cycles >= 50:
            result_message = "It's a draw!"
            exp_amount = random.randint(self.player1.player_echelon * 500, self.player1.player_echelon * 1000)
            ended = True
            quantity = 1
            inventory.update_stock(self.player1, "Crate", quantity)
            inventory.update_stock(self.player2, "Crate", quantity)
            loot_msg = f"Both Players {loot_item.item_emoji} {quantity}x crate(s) acquired!"
        elif not is_alive_player1:
            result_message = f"{self.player2.player_username} wins!"
            exp_amount = random.randint(self.player1.player_echelon * 100, self.player1.player_echelon * 500)
            ended = True
            inventory.update_stock(self.player2, "Crate", quantity)
            loot_msg = f"{self.player2.player_username} {loot_item.item_emoji} {quantity}x crates acquired!"
        elif not is_alive_player2:
            exp_amount = random.randint(self.player1.player_echelon * 1000, self.player1.player_echelon * 5000)
            result_message = f"{self.player1.player_username} wins!"
            ended = True
            inventory.update_stock(self.player1, "Crate", quantity)
            loot_msg = f"{self.player1.player_username} {loot_item.item_emoji} {quantity}x crates acquired!"
        if ended:
            exp_msg = self.player1.adjust_exp(exp_amount)
            exp_description = f"{globalitems.exp_icon} {exp_msg} EXP acquired!"
            pvp_embed.add_field(name=result_message, value=exp_description, inline=False)
            pvp_embed.add_field(name="", value=loot_msg, inline=False)
            await self.sent_message.edit(embed=pvp_embed)
            self.cog_unload()
        else:
            await self.sent_message.edit(embed=pvp_embed)

    async def update_combat_embed(self, hit_list):
        pvp_embed = discord.Embed(title="Arena PvP", description="", color=self.colour)
        # pvp_embed.set_thumbnail(url="")
        player_1_hp_msg = f"{sharedmethods.display_hp(self.combat_tracker1.player_cHP, self.player1.player_mHP)}"
        player_2_hp_msg = f"{sharedmethods.display_hp(self.combat_tracker2.player_cHP, self.player2.player_mHP)}"
        pvp_embed.add_field(name=self.player1.player_username, value=player_1_hp_msg, inline=True)
        pvp_embed.add_field(name=self.player2.player_username, value=player_2_hp_msg, inline=True)
        battle_msg = f"Cycle Count: {self.combat_tracker1.total_cycles}"
        pvp_embed.add_field(name="", value=battle_msg, inline=False)
        hit_field = ""
        for hit in hit_list:
            hit_field += f"{hit[1]}\n"
        pvp_embed.add_field(name="Hits", value=hit_field, inline=False)
        return pvp_embed

    async def calculate_cycle(self):
        self.combat_tracker1.total_cycles += 1
        hit_list = []
        combo_count = [0, 0]
        num_hits1, excess_hits1 = divmod(self.combat_tracker1.remaining_hits + self.player1.attack_speed, 1)
        num_hits2, excess_hits2 = divmod(self.combat_tracker2.remaining_hits + self.player2.attack_speed, 1)
        self.combat_tracker1.remaining_hits = excess_hits1
        self.combat_tracker2.remaining_hits = excess_hits2
        player_interval = [60 / num_hits1,
                           60 / num_hits2]
        attack_counter = player_interval
        while attack_counter[0] <= 60 or attack_counter[1] <= 60:
            await self.handle_pvp_attack(combo_count, attack_counter, player_interval, hit_list)
        combatants = [self.player1, self.player2]
        trackers = [self.combat_tracker1, self.combat_tracker2]
        if self.player1.bleed_application >= 1:
            roles = [0, 1]
            await self.handle_pvp_bleed(roles, combatants, trackers, hit_list, False)
        if self.player1.bleed_application >= 1:
            roles = [1, 0]
            await self.handle_pvp_bleed(roles, combatants, trackers, hit_list, False)
        is_alive_player1 = self.combat_tracker1.player_cHP > 0
        is_alive_player2 = self.combat_tracker2.player_cHP > 0
        return hit_list, is_alive_player1, is_alive_player2

    async def handle_pvp_attack(self, combo_count, attack_counter, player_interval, hit_list):
        combatant = [self.player1, self.player2]
        tracker = [self.combat_tracker1, self.combat_tracker2]
        attacker, defender = 1, 0
        if attack_counter[0] <= attack_counter[1]:
            attacker, defender = 0, 1
        role = [attacker, defender]
        hit_damage, critical_type = combat.pvp_attack(combatant[attacker], combatant[defender])
        combo_count[attacker] += 1 + combatant[attacker].combo_application
        hit_damage, skill_name = combat.skill_adjuster(combatant[attacker], tracker[attacker], hit_damage,
                                                       combo_count[attacker], False)
        scaled_damage = self.scale_damage(role, combatant, hit_damage)
        scaled_damage, status_msg = combat.check_lock(combatant[attacker], tracker[attacker], scaled_damage)
        scaled_damage, second_msg = combat.check_bloom(combatant[attacker], scaled_damage)
        hit_msg = f"{combatant[attacker].player_username} - {combo_count[attacker]}x Combo: {skill_name} {sharedmethods.number_conversion(scaled_damage)}"
        if status_msg != "":
            hit_msg += f" *{status_msg}*"
        if second_msg != "":
            hit_msg += f" *{second_msg}*"
        if critical_type != "":
            hit_msg += f" *{critical_type}*"
        hit_list.append([scaled_damage, hit_msg])
        attack_counter[attacker] += player_interval[attacker]
        tracker[defender].player_cHP -= scaled_damage
        if combatant[attacker].bleed_application >= 1:
            tracker[attacker].bleed_tracker += 0.05 * combatant[attacker].bleed_application
            if tracker[attacker].bleed_tracker >= 1:
                tracker[attacker].bleed_tracker = 1
        await self.handle_pvp_ultimate(role, combatant, tracker, combo_count, hit_list)

    async def handle_pvp_ultimate(self, role, combatant, tracker, combo_count, hit_list):
        attacker, defender = self.set_combat_roles(role)
        if tracker[attacker].charges >= 20:
            hit_damage, critical_type = combat.pvp_attack(combatant[attacker], combatant[defender])
            combo_count[attacker] += 1 + combatant[attacker].combo_application
            hit_damage, skill_name = combat.skill_adjuster(combatant[attacker], tracker[attacker], hit_damage,
                                                           combo_count[attacker], True)
            scaled_damage = self.scale_damage(role, combatant, hit_damage)
            scaled_damage, status_msg = combat.check_lock(combatant[attacker], tracker[attacker], scaled_damage)
            scaled_damage, second_msg = combat.check_bloom(combatant[attacker], scaled_damage)
            hit_msg = f"{combatant[attacker].player_username} - Ultimate: {skill_name} {sharedmethods.number_conversion(scaled_damage)}"
            if status_msg != "":
                hit_msg += f" *{status_msg}*"
            if second_msg != "":
                hit_msg += f" *{second_msg}*"
            if critical_type != "":
                hit_msg += f" *{critical_type}*"
            hit_list.append([scaled_damage, hit_msg])
            tracker[defender].player_cHP -= scaled_damage
            if combatant[attacker].bleed_application >= 1:
                await self.handle_pvp_bleed(role, combatant, tracker, hit_list, True)

    async def handle_pvp_bleed(self, role, combatant, tracker, hit_list, is_ultimate):
        attacker, defender = self.set_combat_roles(role)
        bleed_damage, bleed_type = combat.pvp_bleed_damage(combatant[attacker], combatant[defender])
        bleed_damage *= (tracker[attacker].bleed_tracker + 1)
        if is_ultimate:
            bleed_msg = "Sanguine Rupture"
            bleed_damage *= 1.5
        else:
            bleed_msg = "Blood Rupture"
            bleed_damage *= 0.75
        scaled_damage = self.scale_damage(role, combatant, bleed_damage)
        hit_msg = f"{combatant[attacker].player_username} - {bleed_msg}: {sharedmethods.number_conversion(scaled_damage)} *{bleed_type}*"
        for x in range(combatant[attacker].bleed_application):
            hit_list.append([scaled_damage, hit_msg])
            tracker[defender].player_cHP -= scaled_damage

    def set_combat_roles(self, role):
        return role[0], role[1]

    def scale_damage(self, role, combatants, hit_damage):
        attacker, defender = self.set_combat_roles(role)
        reduction = (combatants[defender].player_mHP // 100) * 0.002
        damage = (len(str(hit_damage)) - 1) * 0.02
        string_damage = str(hit_damage)
        first_number = int(string_damage[0])
        damage += first_number * 0.001
        damage -= reduction
        if damage <= 0:
            damage = 0.01
        scaled_damage = int(combatants[defender].player_mHP * damage)
        return scaled_damage
