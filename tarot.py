# General imports
import discord
import random
import pandas as pd

# Data imports
import globalitems as gli
import market
import sharedmethods as sm
import itemdata

# Core imports
import player
import inventory
import pilengine
from pandoradb import run_query as rq

# Item/crafting imports
import itemrolls

card_dict = {
    "0": ["Karma, The Reflection", 1], "I": ["Runa, The Magic", 1], "II": ["Pandora, The Celestial", 4],
    "III": ["Oblivia, The Void", 5], "IV": ["Akasha, The Infinite", 5], "V": ["Arkaya, The Duality", 1],
    "VI": ["Kama, The Love", 1], "VII": ["Astratha, The Dimensional", 4], "VIII": ["Tyra, The Behemoth", 4],
    "IX": ["Alaya, The Memory", 1], "X": ["Chrona, The Temporal", 3], "XI": ["Nua, The Heavens", 3],
    "XII": ["Rua, The Abyss", 3], "XIII": ["Thana, The Death", 3], "XIV": ["Arcelia, The Clarity", 2],
    "XV": ["Diabla, The Primordial", 4], "XVI": ["Aurora, The Fortress", 4], "XVII": ["Nova, The Star", 2],
    "XVIII": ["Luna, The Moon", 2], "XIX": ["Luma, The Sun", 2], "XX": ["Aria, The Requiem", 2],
    "XXI": ["Ultima, The Creation", 3], "XXII": ["Mysmir, Changeling of the True Laws", 1],
    "XXIII": ["Avalon, Pathwalker of the True Laws", 2], "XXIV": ["Isolde, Soulweaver of the True Laws", 3],
    "XXV": ["Eleuia, The Wish", 6], "XXVI": ["Kazyth, Lifeblood of the True Laws", 4],
    "XXVII": ["Vexia, Scribe of the True Laws", 5], "XXVIII": ["Fleur, Oracle of the True Laws", 6],
    "XXIX": ["Yubelle, Adjudicator of the True Laws", 7], "XXX": ["Nephilim, Incarnate of the Divine Lotus", 8]}
card_type_dict = {
    "0": "Paragon", "I": "Paragon", "II": "Paragon", "III": "Paragon", "IV": "Paragon", "V": "Paragon",
    "VI": "Paragon", "VII": "Paragon", "VIII": "Paragon", "IX": "Paragon", "X": "Paragon",
    "XI": "Paragon", "XII": "Paragon", "XIII": "Paragon", "XIV": "Paragon", "XV": "Paragon",
    "XVI": "Paragon", "XVII": "Paragon", "XVIII": "Paragon", "XIX": "Paragon", "XX": "Paragon",
    "XXI": "Paragon", "XXII": "Arbiter", "XXIII": "Arbiter", "XXIV": "Arbiter", "XXV": "Paragon",
    "XXVI": "Arbiter", "XXVII": "Arbiter", "XXVIII": "Arbiter", "XXIX": "Arbiter", "XXX": "Incarnate"}

# Key: [path, [description1, value1, reference1, location1], [description2, value2, reference2, location2]]
card_stat_dict = {
    # Application Cards
    "I": [1, ["Fire Damage", 1, "elemental_mult", 0], ["Mana Damage", 25, "mana_mult", 5]],
    "X": [7, ["Temporal Application", 1, "appli", "Temporal"], ["Ultimate Application", 1, "appli", "Ultimate"]],
    "III": [6, ["Mana Application", 1, "appli", "Mana"], ["Critical Application", 1, "appli", "Critical"]],
    "IV": [5, ["Life Application", 1, "appli", "Life"], ["Critical Application", 1, "appli", "Critical"]],
    # Lesser Path Cards
    "XVII": [4, ["Celestial Damage", 25, "elemental_mult", 8], ["Celestial Damage", 25, "elemental_mult", 8]],
    "V": [2, ["Bleed Penetration", 20, "bleed_pen", 6], ["Bleed Application", 1, "appli", "Bleed"]],
    # Greater Path Cards
    "XX": [0, ["Water Penetration", 20, "elemental_pen", 0], ["Lightning Penetration", 20, "elemental_pen", 2]],
    "XV": [1, ["Ice Penetration", 20, "elemental_pen", 5], ["Fire Penetration", 20, "elemental_pen", 0]],
    "XVIII": [6, ["Water Penetration", 20, "elemental_pen", 1], ["Ice Penetration", 20, "elemental_pen", 5],
              ["Shadow Penetration", 20, "elemental_pen", 6]], "XIX": [5, ["Fire Penetration", 20, "elemental_pen", 0],
            ["Wind Penetration", 20, "elemental_pen", 4], ["Light Penetration", 20, "elemental_pen", 7]],
    "II": [4, ["Celestial Penetration", 20, "elemental_pen", 8], ["Celestial Curse", 15, "elemental_curse", 8]],
    "XXI": [6, ["Singularity Penetration", 20, "singularity_pen", None],
            ["Singularity Curse", 15, "singularity_curse", None]],
    # Bane Cards
    "XVI": [2, ["Earth Curse", 15, "elemental_curse", 3], ["Fortress Bane", 25, "banes", 0]],
    "VII": [7, ["Celestial Curse", 15, "elemental_curse", 8], ["Dragon Bane", 25, "banes", 1]],
    "VIII": [3, ["Lightning Curse", 15, "elemental_curse", 2], ["Demon Bane", 25, "banes", 2]],
    "0": [1, ["Arbiter Bane", 25, "banes", 4], ["Paragon Bane", 25, "banes", 3]],
    "VI": [4, ["Omni Damage", 25, "all_elemental_mult", None], ["Human Bane", 25, "banes", 5]],
    # Solitude Cards
    "IX": [5, ["Wind Penetration", 20, "elemental_pen", 4], ["Wind Curse", 15, "elemental_curse", 4]],
    "XI": [2, ["Earth Penetration", 20, "elemental_pen", 3], ["Wind Penetration", 20, "elemental_pen", 4]],
    "XII": [3, ["Shadow Penetration", 20, "elemental_pen", 6], ["Light Penetration", 20, "elemental_pen", 7]],
    "XIII": [6, ["Ice Penetration", 20, "elemental_pen", 5], ["Ice Curse", 15, "elemental_curse", 5]],
    "XIV": [6, ["Water Penetration", 20, "elemental_pen", 1], ["Water Curse", 15, "elemental_curse", 1]],
    # Arbiter Cards
    "XXII": [7, ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
             ["Arbiter Bane", 25, "banes", 4]],
    "XXIII": [3, ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
              ["Ultimate Application", 1, "appli", "Ultimate"]],
    "XXIV": [8, ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
             ["Elemental Overflow", 1, "appli", "Elemental"]],
    "XXVI": [2, ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
             ["Bleed Application", 1, "appli", "Bleed"]],
    "XXVII": [0, ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
              ["Critical Application", 1, "appli", "Critical"]],
    "XXVIII": [7, ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
               ["Temporal Application", 1, "appli", "Temporal"]],
    "XXIX": ["All", ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
             ["Bloom Damage", 500, "bloom_mult", None]],
    "XXX": ["All", ["X% Chance to trigger Bloom on hit", 5, "trigger_rate", "Bloom"],
            ["Bloom Damage", 1000, "bloom_mult", None]],
    "XXV": ["All", ["Omni Damage", 25, "all_elemental_mult", None],
            ["Omni Curse", 25, "all_elemental_curse", None]]}
synthesis_success_rate = {0: 0, 1: 75, 2: 50, 3: 40, 4: 30, 5: 20, 6: 10, 7: 99, 8: 0}
card_variant = ["Empty", "Prelude", "Emergence", "Chromatic", "Prismatic",
                "Resplendent", "Iridescent", "Transcendent", "Masterpiece"]
tarot_damage = [0, 5000, 25000, 50000, 100000, 250000, 500000, 750000, 1000000]
tarot_hp = [0, 500, 1000, 1500, 2000, 2500, 5000, 10000, 20000]
tarot_fd = [0, 10, 20, 30, 40, 50, 70, 100, 200]
path_point_values = [0, 1, 2, 3, 4, 5, 7, 10, 20]


class SearchTierView(discord.ui.View):
    def __init__(self, player_user, cathedral=False):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.cathedral = cathedral

        # Build the option list.
        select_options = [
            discord.SelectOption(
                label=f"Tier {tier} Tarot Cards", description="", value=f"{tier}"
            ) for tier in range(1, 9) if tier != 8 or (tier == 8 and not self.cathedral)]
        select_menu = discord.ui.Select(placeholder="Select Card Tier!",
                                        min_values=1, max_values=1, options=select_options)
        select_menu.callback = self.tier_select_callback
        self.add_item(select_menu)

    async def tier_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.player_user.discord_id:
            selected_option = interaction.data['values'][0]
            new_view = SearchCardView(self.player_user, int(selected_option), cathedral=self.cathedral)
            await interaction.response.edit_message(view=new_view)


class SearchCardView(discord.ui.View):
    def __init__(self, player_user, selected_tier, cathedral):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_tier = selected_tier
        self.cathedral = cathedral
        selected_data = [(card_number, card_name) for card_number, (card_name, tier) in card_dict.items() if
                         tier == selected_tier]

        # Build the option list.
        select_options = [
            discord.SelectOption(
                label=f"{card_number} - {card_name}",
                description="",
                value=f"{card_number}"
            ) for card_number, card_name in selected_data]
        select_menu = discord.ui.Select(placeholder="Search Card!", min_values=1, max_values=1, options=select_options)
        select_menu.callback = self.card_select_callback
        self.add_item(select_menu)

    async def card_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_user.discord_id:
            return
        selected_numeral = interaction.data['values'][0]
        selected_card = await get_index_by_key(selected_numeral)
        tarot = await check_tarot(self.player_user.player_id, card_dict[selected_numeral][0])
        new_view = TarotView(self.player_user, selected_card, tarot)
        if self.cathedral:
            essence_obj = inventory.BasicItem(f"Essence{selected_numeral}")
            token_obj = inventory.BasicItem("Token7")
            token_stock = await inventory.check_stock(self.player_user, token_obj.item_id)
            new_embed = await market.cathedral_cost_msg(token_obj, token_stock, essence_obj)
            new_view = market.EssencePurchaseView(self.player_user, token_obj, essence_obj)
        else:
            new_embed = await tarot_menu_embed(self.player_user, selected_numeral)
        await interaction.response.edit_message(embed=new_embed, view=new_view)


class CollectionView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.button(label="View Collection", style=discord.ButtonStyle.blurple)
    async def view_collection(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            new_msg = await tarot_menu_embed(self.player_user, "0")
            tarot = await check_tarot(self.player_user.player_id, card_dict["0"][0])
            new_view = TarotView(self.player_user, 0, tarot)
            await interaction.response.edit_message(embed=new_msg, view=new_view)

    @discord.ui.button(label="Search Card", style=discord.ButtonStyle.blurple, emoji="🔎")
    async def search_collection(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            new_view = SearchTierView(self.player_user)
            await interaction.response.edit_message(view=new_view)


class TarotView(discord.ui.View):
    def __init__(self, player_user, starting_location, tarot):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.current_position = starting_location
        self.embed = None
        self.selected_numeral = get_key_by_index(self.current_position)

        # Adjust non-positional buttons.
        self.bind_success_rate = 90 - (card_dict[self.selected_numeral][1] * 5)
        self.attempt_bind.label = f"Bind ({self.bind_success_rate}%)"
        if tarot is not None:
            synthesis_rate = synthesis_success_rate[tarot.num_stars]
            if tarot.num_stars != 8:
                self.synthesize.label = f"Synth ({synthesis_success_rate[tarot.num_stars]}%)"
            else:
                self.synthesize.label = "Synth [MAX]"
                self.synthesize.disabled = True
                self.synthesize.style = discord.ButtonStyle.secondary
            if self.player_user.equipped_tarot == self.selected_numeral:
                self.equip.disabled = True
                self.equip.style = discord.ButtonStyle.secondary
        else:
            self.equip.disabled = True
            self.equip.style = discord.ButtonStyle.secondary
            self.synthesize.disabled = True
            self.synthesize.style = discord.ButtonStyle.secondary

        # Adjust positional button labels.
        previous_position = self.current_position - 1 if self.current_position != 0 else 30
        next_position = self.current_position + 1 if self.current_position != 30 else 0
        previous_numeral = get_key_by_index(self.current_position - 1)
        next_numeral = get_key_by_index(next_position)
        self.previous_card.label = f"Prev: {previous_numeral}"
        self.next_card.label = f"Next: {next_numeral}"

    async def cycle_tarot(self, direction):
        max_position = 30
        self.current_position = (self.current_position + direction) % (max_position + 1)
        self.selected_numeral = get_key_by_index(self.current_position)
        tarot = await check_tarot(self.player_user, card_dict[self.selected_numeral][0])
        # Display the tarot card.
        embed_msg = await tarot_menu_embed(self.player_user, self.selected_numeral)
        return embed_msg

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, row=1)
    async def previous_card(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            new_msg = await self.cycle_tarot(-1)
            tarot = await check_tarot(self.player_user, card_dict[self.selected_numeral][0])
            reload_view = TarotView(self.player_user, self.current_position, tarot)
            await interaction.response.edit_message(embed=new_msg, view=reload_view)

    @discord.ui.button(label="Search", style=discord.ButtonStyle.blurple, emoji="🔎", row=1)
    async def search_card(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            completion_count = await collection_check(self.player_user)
            embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                      title=f"{self.player_user.player_username}'s Tarot Collection",
                                      description=f"Completion Total: {completion_count} / 31")
            embed_msg.set_image(url=gli.planetarium_img)
            new_view = SearchTierView(self.player_user)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=1)
    async def next_card(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            new_msg = await self.cycle_tarot(1)
            tarot = await check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
            reload_view = TarotView(self.player_user, self.current_position, tarot)
            await interaction.response.edit_message(embed=new_msg, view=reload_view)

    @discord.ui.button(label="Equip", style=discord.ButtonStyle.success, row=2)
    async def equip(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            embed_msg = await tarot_menu_embed(self.player_user, self.selected_numeral)
            active_card = await check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
            if active_card:
                await self.player_user.reload_player()
                self.player_user.equipped_tarot = f"{active_card.card_numeral}"
                self.player_user.set_player_field("player_tarot", self.player_user.equipped_tarot)
                embed_msg.add_field(name="Equipped!", value="", inline=False)
            else:
                embed_msg.add_field(name="Cannot Equip!", value="You do not own this card.", inline=False)
            tarot = await check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
            reload_view = TarotView(self.player_user, self.current_position, tarot)
            await interaction.response.edit_message(embed=embed_msg, view=reload_view)

    @discord.ui.button(label="Bind", style=discord.ButtonStyle.success, row=2)
    async def attempt_bind(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                if not self.embed:
                    self.embed = await binding_ritual(self.player_user, self.selected_numeral, self.bind_success_rate)
                tarot = await check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
                reload_view = TarotView(self.player_user, self.current_position, tarot)
                await interaction.response.edit_message(embed=self.embed, view=reload_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Synthesis", style=discord.ButtonStyle.success, row=2)
    async def synthesize(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        active_card = await check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
        reload_view = TarotView(self.player_user, self.current_position, active_card)
        title = "Cannot Synthesize!"
        if not self.embed:
            self.embed = await tarot_menu_embed(self.player_user, self.selected_numeral)
            if not active_card:
                self.embed.title, self.embed.description = title, "You do not own this card."
                await interaction.response.edit_message(embed=self.embed, view=reload_view)
                return
            if active_card.card_qty <= 1:
                self.embed.title, self.embed.description = title, "Not enough cards in possession."
                await interaction.response.edit_message(embed=self.embed, view=reload_view)
                return
            if active_card.num_stars >= 8:
                self.embed.title, self.embed.description = title, "Card cannot be upgraded further."
                await interaction.response.edit_message(embed=self.embed, view=reload_view)
                return
            # Handle tier 7 exception.
            if active_card.num_stars == 7:
                lotus_item = inventory.BasicItem("Lotus8")
                player_stock = await inventory.check_stock(self.player_user, lotus_item.item_id)
                if player_stock < 1:
                    description = f"Divine Synthesis requires: {lotus_item.item_emoji} 1x {lotus_item.item_name}"
                    self.embed.title, self.embed.description = title, description
                    await interaction.response.edit_message(embed=self.embed, view=reload_view)
                    return
                await inventory.update_stock(self.player_user, lotus_item.item_id, -1)
            # Attempt Synthesis
            title, description = await active_card.synthesize_tarot()
            self.embed = await self.cycle_tarot(0)
            self.embed.add_field(name=title, value=description, inline=False)
            tarot = await check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
            reload_view = TarotView(self.player_user, self.current_position, tarot)
        await interaction.response.edit_message(embed=self.embed, view=reload_view)


class TarotCard:
    def __init__(self, player_id, card_numeral, card_qty, num_stars, card_enhancement):
        self.player_id = player_id
        self.card_numeral = card_numeral
        self.card_name, self.card_tier = card_dict[card_numeral][0], card_dict[card_numeral][1]
        self.card_qty = card_qty
        self.num_stars = num_stars
        self.damage, self.hp, self.fd = tarot_damage[self.num_stars], tarot_hp[self.num_stars], tarot_fd[self.num_stars]
        self.card_enhancement = card_enhancement
        if self.card_qty == 0:
            self.card_image_link = f"{gli.web_url}tarot/cardback.png"
        else:
            self.card_image_link = f"{gli.web_url}tarot/{self.card_numeral}/{self.card_numeral}_{self.num_stars}.png"

    async def create_tarot_embed(self):
        gear_colour, _ = sm.get_gear_tier_colours(self.num_stars)
        display_stars = sm.display_stars(self.num_stars)
        card_title = f"{self.card_numeral} - {self.card_name}"
        card_title += f" [{card_variant[self.num_stars]}]"
        tarot_embed = discord.Embed(colour=gear_colour, title=card_title, description=display_stars)
        if self.num_stars != 0:
            tarot_embed.add_field(name=f"", value=await self.display_tarot_stats(), inline=False)
        tarot_embed.set_image(url=self.card_image_link)
        return tarot_embed

    async def display_tarot_stats(self):
        player_obj = await player.get_player_by_id(self.player_id)
        resonance_bonus = await self.check_resonance(player_obj)
        card_data = card_stat_dict[self.card_numeral]
        pearl = gli.augment_icons[self.num_stars - 1]
        path_string = "**Active Resonance**\n" if resonance_bonus == 2 else ""
        path_string += f"Path of {gli.path_names[card_data[0]]}" if card_data[0] != "All" else "All Paths"
        stat_string = f"{path_string} +{path_point_values[self.num_stars] * resonance_bonus}\n"
        stat_string += (f"{pearl} Base Damage {self.damage * resonance_bonus:,} - {self.damage * resonance_bonus:,}\n"
                        f"{pearl} HP Bonus +{self.hp * resonance_bonus:,}\n"
                        f"{pearl} Final Damage {self.fd * resonance_bonus:,}%")
        for ability_data in card_data[1:]:
            ability_value = ability_data[1] * self.num_stars * resonance_bonus
            if "X" in ability_data[0]:
                stat_string += f'\n{pearl} {ability_data[0].replace("X", str(ability_value))}'
            else:
                stat_string += f"\n{pearl} {ability_data[0]}"
                stat_string += f" +{ability_value}" if "Application" in ability_data[0] else f" {ability_value}%"
        return stat_string

    async def assign_tarot_values(self, player_obj):
        resonance_bonus = await self.check_resonance(player_obj)
        card_data = card_stat_dict[self.card_numeral]
        # Apply Path bonuses
        path_bonus = path_point_values[self.num_stars] * resonance_bonus
        if card_data[0] != "All":
            player_obj.gear_points[card_data[0]] += path_bonus
        else:
            player_obj.gear_points = [path + path_bonus for path in player_obj.gear_points]
        # Apply modifier bonuses
        player_obj.player_damage += self.damage * resonance_bonus
        player_obj.hp_bonus += self.hp * resonance_bonus
        player_obj.final_damage += self.fd * 0.01 * resonance_bonus
        card_multiplier = self.num_stars * 0.01 * resonance_bonus
        for bonus_roll in card_data[1:]:
            attribute_value, attribute_name, attribute_position = bonus_roll[1], bonus_roll[2], bonus_roll[3]
            if "appli" not in attribute_name:
                attribute_value *= 0.01
            attribute_value *= self.num_stars * resonance_bonus
            if attribute_position is None:
                setattr(player_obj, attribute_name, getattr(player_obj, attribute_name) + attribute_value)
            else:
                target_list = getattr(player_obj, attribute_name)
                target_list[attribute_position] += attribute_value

    async def check_resonance(self, player_obj):
        if player_obj.player_equipped[4] == 0:
            return 1
        e_ring = await inventory.read_custom_item(player_obj.player_equipped[4])
        index = e_ring.roll_values[0] if e_ring.item_base_type != "Crown of Skulls" else e_ring.roll_values[2]
        numeral_key = get_key_by_index(int(index))
        return 2 if numeral_key == self.card_numeral else 1

    async def synthesize_tarot(self):
        new_qty = self.card_qty - 1
        await self.set_tarot_field("card_qty", new_qty)
        random_num = random.randint(1, 100)
        success_rate = synthesis_success_rate[self.num_stars]
        if random_num > success_rate:
            return "Synthesis Failed!", "One of the cards dissipates."
        self.num_stars += 1
        await self.set_tarot_field("num_stars", self.num_stars)
        return "Synthesis Success!", "The two cards combine into one."

    async def set_tarot_field(self, field_name, field_value):
        tarot_check = await check_tarot(self.player_id, self.card_name)
        if tarot_check:
            raw_query = (f"UPDATE TarotInventory SET {field_name} = :input_1 "
                         f"WHERE player_id = :player_check AND card_numeral = :numeral_check ")
            params = {'input_1': field_value, 'player_check': self.player_id, 'numeral_check': self.card_numeral}
            rq(raw_query, params=params)

    async def add_tarot_card(self):
        tarot_check = await check_tarot(self.player_id, self.card_name)
        if tarot_check:
            return
        raw_query = ("INSERT INTO TarotInventory (player_id, card_numeral, "
                     "card_name, card_qty, num_stars, card_enhancement) "
                     "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6)")
        params = {'input_1': self.player_id, 'input_2': self.card_numeral, 'input_3': self.card_name,
                  'input_4': self.card_qty, 'input_5': self.num_stars, 'input_6': self.card_enhancement}
        rq(raw_query, params=params)


async def check_tarot(player_id, card_name):
    selected_tarot = None
    raw_query = "SELECT * FROM TarotInventory WHERE player_id = :id_check AND card_name = :card_check"
    df = rq(raw_query, return_value=True, params={'id_check': player_id, 'card_check': card_name})
    if df is not None and len(df.index) != 0:
        player_id = int(df['player_id'].values[0])
        card_numeral, card_qty = str(df['card_numeral'].values[0]), int(df['card_qty'].values[0])
        num_stars, card_enhancement = int(df['num_stars'].values[0]), int(df['card_enhancement'].values[0])
        selected_tarot = TarotCard(player_id, card_numeral, card_qty, num_stars, card_enhancement)
    return selected_tarot


async def tarot_menu_embed(player_obj, card_numeral):
    # Pull the card information
    tarot_card = await check_tarot(player_obj.player_id, card_dict[card_numeral][0])
    if tarot_card is None:
        tarot_card = TarotCard(player_obj.player_id, card_numeral, 0, 0, 0)
    # Build the card embed message.
    embed_msg = await tarot_card.create_tarot_embed()
    loot_item = inventory.BasicItem(f"Essence{card_numeral}")
    essence_stock = await inventory.check_stock(player_obj, loot_item.item_id)
    description = f"Card Quantity: {tarot_card.card_qty}\nEssence Quantity: {essence_stock}"
    embed_msg.add_field(name=f"", value=description, inline=False)
    embed_msg.set_image(url=tarot_card.card_image_link)
    return embed_msg


async def get_index_by_key(numeral):
    keys_list = list(card_dict.keys())
    if numeral not in keys_list:
        return -1
    key_index = keys_list.index(numeral)
    return key_index


def get_key_by_index(key_index):
    keys_list = list(card_dict.keys())
    key_value = keys_list[key_index]
    return key_value


async def get_resonance(card_num):
    resonance_list = ['The Reflection', 'The Magic', 'The Celestial', 'The Void', 'The Infinite',
                      'The Duality', 'The Love', 'The Dragon', 'The Behemoth', 'The Memory',
                      'The Temporal', 'The Heavens', 'The Abyss', 'The Death', 'The Clarity',
                      'The Primordial', 'The Fortress', 'The Star', 'The Moon', 'The Sun',
                      'The Requiem', 'The Creation', 'The Changeling', 'The Pathwalker', 'The Soulweaver',
                      'The Wish', 'The Lifeblood', 'The Scribe', 'The Oracle', 'The Adjudicator', 'The Lotus']
    if card_num == -1:
        random.choice(resonance_list)
    return resonance_list[card_num]


async def collection_check(player_obj):
    collection_count = 0
    raw_query = "SELECT * FROM TarotInventory WHERE player_id = :id_check"
    df = rq(raw_query, return_value=True, params={'id_check': player_obj.player_id})
    if len(df.index) != 0:
        collection_count = df.shape[0]
    return collection_count


async def binding_ritual(player_obj, essence_type, success_rate):
    essence_id = f'Essence{essence_type}'
    essence_stock = await inventory.check_stock(player_obj, essence_id)
    loot_item = inventory.BasicItem(essence_id)
    # Confirm stock is available
    if essence_stock == 0:
        embed_msg = await tarot_menu_embed(player_obj, essence_type)
        stock_msg = sm.get_stock_msg(loot_item, essence_stock)
        embed_msg.add_field(name="Ritual Failed!", value=stock_msg)
        return embed_msg
    # Pay the cost and attempt the binding.
    await inventory.update_stock(player_obj, essence_id, -1)
    random_roll = random.randint(1, 100)
    if random_roll > success_rate:
        embed_msg = await tarot_menu_embed(player_obj, essence_type)
        description_msg = "The essence dissipates."
        embed_msg.add_field(name="Ritual Failed!", value=description_msg)
        return embed_msg
    # Update the tarot inventory.
    card_name = card_dict[essence_type][0]
    tarot_check = await check_tarot(player_obj.player_id, card_name)
    if tarot_check:
        new_qty = tarot_check.card_qty + 1
        await tarot_check.set_tarot_field("card_qty", new_qty)
    else:
        new_tarot = TarotCard(player_obj.player_id, essence_type, 1, 1, 0)
        await new_tarot.add_tarot_card()
    embed_msg = await tarot_menu_embed(player_obj, essence_type)
    description_msg = "The sealed tarot card has been added to your collection."
    embed_msg.add_field(name="Ritual Successful!", value=description_msg)
    return embed_msg
