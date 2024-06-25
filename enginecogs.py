# General imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import asyncio
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime as dt
from zoneinfo import ZoneInfo

# Bot imports
import battleengine

# Data Imports
import globalitems as gli
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


class RaidSchedularCog(commands.Cog):
    def __init__(self, bot, channel_obj, channel_id):
        self.bot, self.scheduler = bot, AsyncIOScheduler(timezone=ZoneInfo('America/Toronto'))
        self.channel_obj, self.channel_id = channel_obj, channel_id
        self.current_raid, self.boss_obj, self.active_message = None, None, None
        self.raid_manager()
        self.bot.loop.create_task(self.trigger_raid())
        print("Raid Cog Active")

    def raid_manager(self):
        self.scheduler.add_job(self.trigger_raid, CronTrigger(hour=0, minute=0))
        self.scheduler.start()

    async def trigger_raid(self):
        print("Triggered: New Raid")
        if self.current_raid:
            await self.end_current_raid()
        player_id, level, boss_type, boss_tier = None, 99, "Ruler", 9
        self.boss_obj = await bosses.spawn_boss(self.channel_id, player_id, boss_tier, boss_type, level)
        embed_msg = self.boss_obj.create_boss_embed()
        file_obj = discord.File(await sm.title_box(f'Raid Boss: {self.boss_obj.boss_name.split()[0].rstrip(",")}'))
        self.active_message = await self.channel_obj.send(file=file_obj, embed=embed_msg, view=RaidView())
        self.current_raid = RaidCog(self.bot, self.boss_obj, self.channel_obj, self.channel_id, self.active_message)

    async def end_current_raid(self):
        if self.current_raid:
            if self.boss_obj.boss_cHP > 0:
                embed_msg = self.boss_obj.create_boss_embed()
                embed_msg.add_field(name="Time's Up", value="The raid encounter has failed", inline=False)
                await self.active_message.edit(embed=embed_msg)
            self.current_raid.end_cog()
            await self.bot.remove_cog('RaidCog')
            self.current_raid = None


class RaidCog(commands.Cog):
    def __init__(self, bot, boss_obj, channel_obj, channel_id, sent_message):
        self.boss_obj = boss_obj
        self.channel_obj, self.channel_id, self.sent_message = channel_obj, channel_id, sent_message
        self.tracker_list = []
        self.lock = asyncio.Lock()
        self.raid_boss_manager.start()

    def end_cog(self):
        self.raid_boss_manager.cancel()

    @tasks.loop(seconds=60)
    async def raid_boss_manager(self):
        async with self.lock:
            time_now = dt.now(ZoneInfo('America/Toronto'))
            if time_now.hour == 23 and time_now.minute >= 58:
                return
            is_alive = await self.raid_boss()
            if is_alive:
                return
            await encounters.clear_boss_encounter_info(self.channel_id)
            self.end_cog()
            
    async def raid_boss(self):
        player_list, damage_list = await bosses.get_damage_list(self.channel_id)
        self.boss_obj.curse_debuffs = [0.0] * 9
        temp_user, dps = [], 0
        for idy, player_id in enumerate(player_list):
            temp_user.append(await player.get_player_by_id(player_id))
            await temp_user[idy].get_player_multipliers()
            curse_lists = [self.boss_obj.curse_debuffs, temp_user[idy].elemental_curse]
            self.boss_obj.curse_debuffs = [sum(z) for z in zip(*curse_lists)]
            if idy >= len(self.tracker_list):
                self.tracker_list.append(combat.CombatTracker(temp_user[idy]))
        # Determine raid boss attack for the cycle
        skill_list = combat.boss_attack_dict[self.boss_obj.boss_name]
        skill_index = random.randint(0, len(skill_list) - 1)
        raid_atk = (skill_list[skill_index], skill_index)
        # Run a cycle for every player
        player_msg_list = []
        for idx, temp_player in enumerate(temp_user):
            p_msg, damage = await combat.run_raid_cycle(self.tracker_list[idx], self.boss_obj, temp_player, raid_atk)
            new_player_damage = int(damage_list[idx]) + damage
            dps += int(self.tracker_list[idx].total_dps / self.tracker_list[idx].total_cycles)
            await encounters.update_player_raid_damage(self.channel_id, temp_player.player_id, new_player_damage)
            player_msg_list.append(p_msg)
        await bosses.update_boss_cHP(self.channel_id, None, self.boss_obj)
        if self.boss_obj.boss_cHP > 0:
            embed_msg, is_alive = self.boss_obj.create_boss_embed(dps=dps), True
        else:
            embed_msg, is_alive = bosses.create_dead_boss_embed(self.channel_id, self.boss_obj, dps), False
            loot_embed = await loot.create_loot_embed(embed_msg, self.boss_obj, player_list, loot_mult=5)
        skill_msg = f"{self.boss_obj.boss_name} uses {skill_list[skill_index]} on all players\n"
        skill_msg += f"{self.boss_obj.boss_name} regenerates 1% HP"
        embed_msg.add_field(name="", value=skill_msg, inline=False)
        for player_msg in player_msg_list:
            embed_msg.add_field(name="", value=player_msg, inline=False)
        await self.sent_message.edit(embed=embed_msg)
        if not is_alive:
            message = f"{self.boss_obj.boss_name} Slain"
            await self.channel_obj.send(file=discord.File(await sm.title_box(message)))
            await self.channel_obj.send(embed=loot_embed)
        return is_alive
        
            
class RaidView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join the raid!", style=discord.ButtonStyle.success, emoji="<:Sword5:1246945708939022367>")
    async def raid_callback(self, interaction: discord.Interaction, raid_select: discord.ui.Select):
        clicked_by = await player.get_player_by_discord(interaction.user.id)
        if clicked_by.player_echelon < 5:
            outcome = f"{clicked_by.player_username}: Echelon 5 required to join a raid."
            await interaction.response.send_message(outcome)
            return
        if clicked_by.player_equipped[0] == 0:
            outcome = f"{clicked_by.player_username}: Weapon required to join a raid."
            await interaction.response.send_message(outcome)
            return
        outcome = await encounters.add_participating_player(interaction.channel.id, clicked_by)
        await interaction.response.send_message(outcome)


class SoloCog(commands.Cog):
    def __init__(self, bot, player_obj, boss_obj, channel_id, sent_message, ctx_object,
                 gauntlet=False, mode=0, magnitude=0):
        self.bot = bot
        self.player_obj, self.boss_obj = player_obj, boss_obj
        self.sent_message, self.embed = sent_message, None
        self.ctx_object, self.channel_obj, self.channel_id = ctx_object, ctx_object.channel, channel_id
        self.tracker_obj = combat.CombatTracker(player_obj)
        self.gauntlet, self.mode, self.magnitude = gauntlet, mode, magnitude
        self.lock = asyncio.Lock()

    async def run(self):
        self.solo_manager.start()

    def cog_unload(self):
        self.solo_manager.cancel()

    @tasks.loop(seconds=60)
    async def solo_manager(self):
        async with self.lock:
            if await combat.abandon_flag(self.player_obj) == 1:
                await encounters.clear_boss_encounter_info(self.channel_id, self.player_obj.player_id)
                await self.ctx.send(f"{self.player_obj.player_username} Abandon successful.")
                self.cog_unload()
                return
            continue_encounter = await self.bot.solo_boss()
            if continue_encounter:
                return
            self.cog_unload()
    
    async def solo_boss(self):
        self.boss_obj.curse_debuffs = self.player_obj.elemental_curse
        self.embed, p_alive, boss_alive = await combat.run_solo_cycle(self.tracker_obj, self.boss_obj, self.player_obj)
        await bosses.update_boss_cHP(self.channel_id, self.player_obj.player_id, self.boss_obj)
        if not p_alive:
            await self.sent_message.edit(embed=self.embed)
            await encounters.clear_boss_encounter_info(self.channel_id, self.player_obj.player_id)
            return False
        if boss_alive:
            status = await self.handle_cycle_limit()
            await sent_message.edit(embed=self.embed)
            return status
        if self.boss_obj.boss_tier >= 4:
            await quest.assign_unique_tokens(self.player_obj, self.boss_obj.boss_name, mode=self.mode)
        extension = " [Gauntlet]" if self.gauntlet else ""
        if self.gauntlet and self.boss_obj.boss_tier != 6:
            await encounters.clear_boss_encounter_info(self.channel_id, self.player_obj.player_id)
            boss_type, new_tier = random.choice(["Paragon", "Arbiter"]), self.boss_obj.boss_tier + 1
            if self.boss_obj.boss_tier < 4:
                boss_type = random.choice(["Fortress", "Dragon", "Demon", "Paragon"])
            self.boss_obj = await bosses.spawn_boss(self.channel_id, self.player_obj.player_id, new_tier,
                                                    boss_type, self.player_obj.player_level, gauntlet=self.gauntlet)
            current_dps = int(self.tracker_obj.total_dps / self.tracker_obj.total_cycles)
            self.embed = boss_obj.create_boss_embed(dps=current_dps, extension=extension)
            await sent_message.edit(embed=self.embed)
            return True
        # Handle dead boss
        player_list = [player_obj.player_id]
        loot_bonus = 5 if self.gauntlet else 1
        if "XXX" in self.boss_obj.boss_name:
            loot_bonus = loot.incarnate_attempts_dict[self.boss_obj.boss_level]
            await leaderboards.update_leaderboard(self.tracker_obj, self.player_obj, self.ctx_object)
        loot_embed = await loot.create_loot_embed(self.embed, self.boss_obj, player_list, ctx=self.ctx_object,
                                                  loot_mult=loot_bonus, gauntlet=self.gauntlet, magni=self.magnitude)
        await encounters.clear_boss_encounter_info(self.channel_id, self.player_obj.player_id)
        if self.tracker_obj.total_cycles <= 5:
            await sent_message.edit(embed=loot_embed)
            return False
        await sent_message.edit(embed=self.embed)
        await ctx_object.send(embed=loot_embed)
        return False

    async def handle_cycle_limit(self):
        hp_percent = self.boss_obj.boss_cHP / self.boss_obj.boss_mHP
        if not (self.gauntlet or self.tracker_obj.total_cycles < 30 or hp_percent <= 0.95):
            fail_msg = f"{self.tracker_obj.total_cycles:,} cycles elapsed. Encounter ended as HP threshhold not met."
        elif self.gauntlet and self.tracker_obj.total_cycles >= 999:
            fail_msg = f"999 cycles elapsed. Encounter ended as maximum cycle limit exceeded."
        else:
            return True
        self.embed.add_field(name="Encounter Failed!", value=fail_msg, inline=False)
        await encounters.clear_boss_encounter_info(self.channel_id, self.player_obj.player_id)
        return False


class PvPCog(commands.Cog):
    def __init__(self, bot, ctx_obj, player1, player2, sent_message, channel_obj):
        self.bot, self.ctx_obj = bot, ctx_obj
        self.channel_obj = channel_obj
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
        exp_msg, lvl_adjust = await self.player1.adjust_exp(exp_amount)
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
        combo_count = [self.player1.appli["Combo"], self.player2.appli["Combo"]]
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
        if self.player1.appli["Bleed"] >= 1:
            await self.handle_pvp_bleed([0, 1], combatants, trackers, hit_list, False)
        if self.player1.appli["Bleed"] >= 1:
            await self.handle_pvp_bleed([1, 0], combatants, trackers, hit_list, False)
        return stun_list, hit_list, self.combat_tracker1.player_cHP > 0, self.combat_tracker2.player_cHP > 0

    async def handle_pvp_attack(self, combatants, trackers, combo_count, attack_counter, player_interval, hit_list):
        attacker, defender = (0, 1) if attack_counter[0] <= attack_counter[1] else (1, 0)
        role_order = [attacker, defender]
        hit_data = await self.handle_pvp_hit_damage(role_order, combatants, trackers, combo_count, hit_list)
        scaled_dmg, skill_name, mana_msg, status_msg, second_msg, critical_type, evade = hit_data
        hit_msg = f"{combatants[attacker].player_username} - {combo_count[attacker]}x Combo: {skill_name} {sm.number_conversion(scaled_dmg)}"
        hit_msg += f"{mana_msg}{status_msg}{second_msg}{critical_type}{evade}"
        hit_list.append([scaled_dmg, hit_msg])
        attack_counter[attacker] += player_interval[attacker]
        trackers[defender].player_cHP -= scaled_dmg
        combat.update_bleed(trackers[attacker], combatants[attacker])
        if trackers[attacker].solar_stacks >= 35:
            flare_data = await combat.trigger_flare(trackers[attacker], combatants[attacker], pvp_data=trackers[defender])
            hit_list.append(flare_data)
        await self.handle_pvp_ultimate(role_order, combatants, trackers, combo_count, hit_list)
        if trackers[attacker].solar_stacks >= 35:
            flare_data = await combat.trigger_flare(trackers[attacker], combatants[attacker], pvp_data=trackers[defender])
            hit_list.append(flare_data)

    async def handle_pvp_ultimate(self, role_order, combatant, tracker, combo_count, hit_list):
        attacker, defender = role_order[0], role_order[1]
        if tracker[attacker].charges < 20:
            return
        hit_data = await self.handle_pvp_hit_damage(role_order, combatants, trackers, combo_count, hit_list, True)
        scaled_dmg, skill_name, mana_msg, status_msg, second_msg, critical_type, evade = hit_data
        hit_msg = f"{combatant[attacker].player_username} - Ultimate: {skill_name} {sm.number_conversion(scaled_dmg)}"
        hit_msg += f"{mana_msg}{status_msg}{second_msg}{critical_type}{evade}"
        hit_list.append([scaled_dmg, hit_msg])
        tracker[defender].player_cHP -= scaled_dmg
        if combatant[attacker].appli["Bleed"] >= 1:
            await self.handle_pvp_bleed(role_order, combatant, tracker, hit_list, True)

    async def handle_pvp_hit_damage(self, role_order, combatants, trackers, combo_count, hit_list, is_ultimate=False):
        attacker, defender = role_order[0], role_order[1]
        stun_status, hit_damage, critical_type = await combat.pvp_attack(combatants[attacker], combatants[defender])
        if stun_status is not None:
            trackers[defender].stun_status = stun_status
            trackers[defender].stun_cycles += 1
        combo_count[attacker] += 1
        hit_damage, skill_name = combat.skill_adjuster(combatants[attacker], trackers[attacker], hit_damage,
                                                       combo_count[attacker], is_ultimate)
        hit_damage, mana_msg = combat.check_mana(combatants[attacker], trackers[attacker], hit_damage)
        hit_damage, status_msg = combat.check_lock(combatants[attacker], trackers[attacker], hit_damage)
        hit_damage, second_msg = combat.check_bloom(combatants[attacker], hit_damage)
        hit_damage, evade = combat.handle_evasions(combatants[defender].block, combatants[defender].dodge, hit_damage)
        if combatants[attacker].unique_glyph_ability[2]:
            hit_damage *= (1 + combatants[attacker].bleed_mult)
        if status_msg == " *TIME SHATTER*" or critical_type != "":
            hit_damage *= random.randint(1, combatants[attacker].rng_bonus)
        scaled_dmg = combat.pvp_scale_damage(role_order, combatants, hit_damage)
        return scaled_dmg, skill_name, mana_msg, status_msg, second_msg, critical_type, evade

    async def handle_pvp_bleed(self, role_order, combatant, tracker, hit_list, is_ultimate):
        attacker, defender = role_order[0], role_order[1]
        e_weapon = await inventory.read_custom_item(combatant[attacker].player_equipped[0])
        bleed_damage = await combatant[attacker].get_player_initial_damage()
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
        damage = base_damage - base_damage * (self.player_obj.elemental_res[dmg_element] if dmg_element != -1 else 0)
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
        exp_msg, lvl_adjust = await self.player_obj.adjust_exp(exp_awarded)
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
            coin_msg = await self.player_obj.adjust_coins(1000 * bonus)
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
