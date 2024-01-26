import mysql.connector
from mysql.connector.errors import Error
import sqlalchemy
from sqlalchemy import text
import mysql
import pymysql
from sqlalchemy import exc

import discord
import random

import itemdata
import itemrolls
import player
import inventory
import mydb
import pandas as pd
import pilengine
import globalitems

card_dict = {
    "0": ["Karma, The Reflection", 1],
    "I": ["Runa, The Magic", 1],
    "II": ["Pandora, The Celestial", 4],
    "III": ["Oblivia, The Void", 5],
    "IV": ["Akasha, The Infinite", 5],
    "V": ["Arkaya, The Duality", 1],
    "VI": ["Kama, The Love", 4],
    "VII": ["Astratha, The Dimensional", 4],
    "VIII": ["Tyra, The Behemoth", 4],
    "IX": ["Alaya, The Memory", 1],
    "X": ["Chrona, The Temporal", 3],
    "XI": ["Nua, The Heavens", 3],
    "XII": ["Rua, The Abyss", 3],
    "XIII": ["Thana, The Death", 3],
    "XIV": ["Arcelia, The Clarity", 2],
    "XV": ["Diabla, The Primordial", 4],
    "XVI": ["Aurora, The Fortress", 4],
    "XVII": ["Nova, The Star", 2],
    "XVIII": ["Luna, The Moon", 2],
    "XIX": ["Luma, The Sun", 2],
    "XX": ["Aria, The Requiem", 1],
    "XXI": ["Ultima, The Creation", 3],
    "XXII": ["Mysmiria, Changeling of the True Laws", 1],
    "XXIII": ["Avalon, Pathwalker of the True Laws", 2],
    "XXIV": ["Isolde, Soulweaver of the True Laws", 3],
    "XXV": ["Vexia, Scribe of the True Laws", 4],
    "XXVI": ["Kazyth, Lifeblood of the True Laws", 5],
    "XXVII": ["Fleur, Oracle of the True Laws", 6],
    "XXVIII": ["Yubelle, Adjudicator of the True Laws", 7],
    "XXIX": ["???, Bearer of the Lotus", 7],
    "XXX": ["Eleuia, The Wish", 6]
}

# Key: [path, [description1, value1, reference1, location1], [description2, value2, reference2, location2]]
card_stat_dict = {
                  # Application Cards
                  "X": [6, ["Temporal Application", 1, "temporal_application", None],
                        ["Ultimate Application", 1, "ultimate_application", None]],
                  "III": [4, ["Critical Application", 1, "critical_application", None],
                          ["Critical Application", 1, "critical_application", None]],
                  "IV": [0, ["Critical Application", 1, "critical_application", None],
                         ["Critical Application", 1, "critical_application", None]],
                  # Lesser Path Cards
                  "XVII": [4, ["Celestial Damage", 25, "elemental_multiplier", 8],
                           ["Celestial Damage", 25, "elemental_multiplier", 8]],
                  "I": [5, ["Fire Damage", 25, "elemental_multiplier", 0],
                        ["Ice Damage", 25, "elemental_multiplier", 5]],
                  "XVIII": [3, ["Shadow Penetration", 20, "elemental_penetration", 6],
                            ["Light Penetration", 20, "elemental_penetration", 7]],
                  # Greater Path Cards
                  "XX": [0, ["Water Penetration", 0, "elemental_penetration", 0],
                         ["Lightning Penetration", 0, "elemental_penetration", 2]],
                  "XV": [1, ["Ice Penetration", 20, "elemental_penetration", 5],
                         ["Fire Penetration", 20, "elemental_penetration", 0]],
                  "XIX": [2, ["Earth Penetration", 0, "elemental_penetration", 3],
                          ["Wind Penetration", 0, "elemental_penetration", 4]],
                  "V": [3, ["Shadow Penetration", 20, "elemental_penetration", 6],
                        ["Light Penetration", 20, "elemental_penetration", 7]],
                  "II": [4, ["Celestial Penetration", 0, "elemental_penetration", 8],
                         ["Celestial Curse", 0, "elemental_curse", 8]],
                  "XXI": [6, ["Temporal Application", 1, "temporal_application", None],
                          ["Elemental Overflow", 1, "elemental_application", None]],
                  # Bane Cards
                  "XVI": [2, ["Fortress Bane", 25, "banes", 0],
                          ["Fortress Bane", 25, "banes", 0]],
                  "VII": [1, ["Dragon Bane", 25, "banes", 1],
                          ["Dragon Bane", 25, "banes", 1]],
                  "VIII": [3, ["Demon Bane", 25, "banes", 2],
                           ["Demon Bane", 25, "banes", 2]],
                  "0": [1, ["Paragon Bane", 25, "banes", 3],
                        ["Paragon Bane", 25, "banes", 3]],
                  "VI": [4, ["Human Bane", 25, "banes", 5],
                         ["Human Bane", 25, "banes", 5]],
                  # Solitude Cards
                  "IX": [6, ["Wind Penetration", 20, "elemental_penetration", 4],
                         ["Wind Curse", 15, "elemental_curse", 4]],
                  "XI": [6, ["Light Penetration", 20, "elemental_penetration", 7],
                         ["Light Curse", 15, "elemental_curse", 7]],
                  "XII": [6, ["Shadow Penetration", 20, "elemental_penetration", 6],
                          ["Shadow Curse", 15, "elemental_curse", 6]],
                  "XIII": [6, ["Ice Penetration", 20, "elemental_penetration", 5],
                           ["Ice Curse", 15, "elemental_curse", 5]],
                  "XIV": [6, ["Water Penetration", 20, "elemental_penetration", 1],
                          ["Water Curse", 15, "elemental_curse", 1]],
                  # Arbiter Cards
                  "XXII": [1, ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                           ["Arbiter Bane", 25, "banes", 4]],
                  "XXIII": [3, ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                            ["Ultimate Application", 1, "ultimate_application", None]],
                  "XXIV": [5, ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                           ["Elemental Overflow", 1, "elemental_application", None]],
                  "XXV": [0, ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                          ["Critical Application", 1, "critical_application", None]],
                  "XXVI": [2, ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                           ["Bleed Application", 1, "bleed_application", None]],
                  "XXVII": [6, ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                            ["Temporal Application", 1, "temporal_application", None]],
                  "XXVIII": ["All", ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                             ["Bloom Damage", 500, "bloom_multiplier", None]],
                  "XXIX": ["All", ["X% Chance to trigger Bloom on hit", 5, "specialty_rate", 0],
                            ["Bloom Damage", 1000, "bloom_multiplier", None]],
                  "XXX": ["All", ["Omni Aura", 25, "aura", None],
                          ["Omni Curse", 25, "all_elemental_curse", None]]
                  }
synthesis_success_rate = {0: 0, 1: 75, 2: 50, 3: 25, 4: 15, 5: 10, 6: 5, 7: 0}
card_variant = ["Empty", "Prelude", "Chromatic", "Prismatic", "Resplendent", "Iridescent", "Divine", "Transcendent"]
tarot_damage = [0, 5000, 25000, 50000, 100000, 500000, 1000000, 5000000]
tarot_hp = [0, 500, 1000, 1500, 2000, 2500, 5000, 10000]
tarot_fd = [0, 10, 20, 30, 40, 50, 70, 100]
path_point_values = [0, 1, 2, 3, 4, 5, 7, 10]


class SearchTierView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

        # Build the option list.
        select_options = [
            discord.SelectOption(
                label=f"Tier {tier} Tarot Cards", description="", value=f"{tier}"
            ) for tier in range(1, 8)]
        select_menu = discord.ui.Select(placeholder="Select Card Tier!",
                                        min_values=1, max_values=1, options=select_options)
        select_menu.callback = self.tier_select_callback
        self.add_item(select_menu)

    async def tier_select_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id == self.player_user.discord_id:
                selected_option = interaction.data['values'][0]
                new_view = SearchCardView(self.player_user, int(selected_option))
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class SearchCardView(discord.ui.View):
    def __init__(self, player_user, selected_tier):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_tier = selected_tier
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
        try:
            if interaction.user.id == self.player_user.discord_id:
                selected_numeral = interaction.data['values'][0]
                selected_card = get_index_by_key(selected_numeral)
                new_embed = tarot_menu_embed(self.player_user, selected_numeral)
                new_view = TarotView(self.player_user, selected_card)
                await interaction.response.edit_message(embed=new_embed, view=new_view)
        except Exception as e:
            print(e)


class CollectionView(discord.ui.View):
    def __init__(self, player_user, start_location):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.current_position = start_location

    @discord.ui.button(label="View Collection", style=discord.ButtonStyle.blurple)
    async def view_collection(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                selected_numeral = get_key_by_index(self.current_position)
                new_msg = tarot_menu_embed(self.player_user, selected_numeral)
                new_view = TarotView(self.player_user, self.current_position)
                await interaction.response.edit_message(embed=new_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Search Card", style=discord.ButtonStyle.blurple, emoji="🔎")
    async def search_collection(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                new_view = SearchTierView(self.player_user)
                await interaction.response.edit_message(view=new_view)
        except Exception as e:
            print(e)


class TarotView(discord.ui.View):
    def __init__(self, player_user, starting_location):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.current_position = starting_location
        self.embed = None
        self.selected_numeral = get_key_by_index(self.current_position)

        # Adjust non-positional buttons.
        tarot = check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
        self.bind_success_rate = 90 - (card_dict[self.selected_numeral][1] * 5)
        self.attempt_bind.label = f"Bind ({self.bind_success_rate}%)"
        if tarot is not None:
            synthesis_rate = synthesis_success_rate[tarot.num_stars]
            if tarot.num_stars != 7:
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

    def cycle_tarot(self, direction):
        max_position = 30
        self.current_position = (self.current_position + direction) % (max_position + 1)
        self.selected_numeral = get_key_by_index(self.current_position)
        tarot = check_tarot(self.player_user, self.selected_numeral)
        # Display the tarot card.
        embed_msg = tarot_menu_embed(self.player_user, self.selected_numeral)
        return embed_msg

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, row=1)
    async def previous_card(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                new_msg = self.cycle_tarot(-1)
                reload_view = TarotView(self.player_user, self.current_position)
                await interaction.response.edit_message(embed=new_msg, view=reload_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Search", style=discord.ButtonStyle.blurple, emoji="🔎", row=1)
    async def search_card(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                completion_count = collection_check(self.player_user.player_id)
                embed_msg = discord.Embed(colour=discord.Colour.magenta(),
                                          title=f"{self.player_user.player_username}'s Tarot Collection",
                                          description=f"Completion Total: {completion_count} / 31")
                embed_msg.set_image(url="")
                new_view = SearchTierView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=1)
    async def next_card(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                new_msg = self.cycle_tarot(1)
                reload_view = TarotView(self.player_user, self.current_position)
                await interaction.response.edit_message(embed=new_msg, view=reload_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Equip", style=discord.ButtonStyle.success, row=2)
    async def equip(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                embed_msg = tarot_menu_embed(self.player_user, self.selected_numeral)
                active_card = check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
                if active_card:
                    self.player_user = player.get_player_by_id(self.player_user.player_id)
                    self.player_user.equipped_tarot = f"{active_card.card_numeral}"
                    self.player_user.set_player_field("player_equip_tarot", self.player_user.equipped_tarot)
                    embed_msg.add_field(name="Equipped!", value="", inline=False)
                else:
                    embed_msg.add_field(name="Cannot Equip!", value="You do not own this card.", inline=False)
                reload_view = TarotView(self.player_user, self.current_position)
                await interaction.response.edit_message(embed=embed_msg, view=reload_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Bind", style=discord.ButtonStyle.success, row=2)
    async def attempt_bind(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                if not self.embed:
                    self.embed = binding_ritual(self.player_user, self.selected_numeral, self.bind_success_rate)
                reload_view = TarotView(self.player_user, self.current_position)
                await interaction.response.edit_message(embed=self.embed, view=reload_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Synthesis", style=discord.ButtonStyle.success, row=2)
    async def synthesize(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                active_card = check_tarot(self.player_user.player_id, card_dict[self.selected_numeral][0])
                if not self.embed:
                    self.embed = tarot_menu_embed(self.player_user, self.selected_numeral)
                    title, description = "", ""
                    if not active_card:
                        description = "You do not own this card."
                    if active_card.card_qty <= 1:
                        description = "Not enough cards in possession."
                    title = "" if description == "" else "Cannot Synthesize!"
                    if active_card.num_stars >= 7:
                        description = "Card cannot be upgraded further."
                    if description != "":
                        title = "Cannot Synthesize!"
                    else:
                        title, description = active_card.synthesize_tarot()
                        self.embed = self.cycle_tarot(0)
                    self.embed.add_field(name=title, value=description, inline=False)
                reload_view = TarotView(self.player_user, self.current_position)
                await interaction.response.edit_message(embed=self.embed, view=reload_view)
        except Exception as e:
            print(e)


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
            self.card_image_link = "https://kyleportfolio.ca/botimages/tarot/cardback.png"
        else:
            self.card_image_link = f"https://kyleportfolio.ca/botimages/tarot/{self.card_numeral}.png"

    def create_tarot_embed(self):
        gear_colour, gear_emoji = inventory.get_gear_tier_colours(self.num_stars)
        display_stars = globalitems.display_stars(self.num_stars)
        card_title = f"{self.card_numeral} - {self.card_name}"
        card_title += f" [{card_variant[self.num_stars]}]"
        tarot_embed = discord.Embed(colour=gear_colour, title=card_title, description=display_stars)
        if self.num_stars != 0:
            tarot_embed.add_field(name=f"", value=self.display_tarot_stats(), inline=False)
        tarot_embed.set_image(url=self.card_image_link)
        return tarot_embed

    def display_tarot_stats(self):
        card_data = card_stat_dict[self.card_numeral]
        pearl = itemrolls.augment_icons[self.num_stars - 1]
        path_string = f"Path of {globalitems.path_names[card_data[0]]}" if card_data[0] != "All" else "All Paths"
        stat_string = f"{path_string} +{path_point_values[self.num_stars]}\n"
        stat_string += (f"{pearl} Base Damage {self.damage:,} - {self.damage:,}\n"
                        f"{pearl} HP Bonus +{self.hp:,}\n"
                        f"{pearl} Final Damage {self.fd:,}%")
        for ability_data in card_data[1:]:
            if "X" in ability_data[0]:
                stat_string += f'\n{pearl} {ability_data[0].replace("X", str(ability_data[1] * self.num_stars))}'
            else:
                stat_string += f"\n{pearl} {ability_data[0]} {ability_data[1] * self.num_stars}%"
        return stat_string

    def assign_tarot_values(self, player_object):
        card_data = card_stat_dict[self.card_numeral]
        # Apply Path bonuses
        path_bonus = path_point_values[self.num_stars]
        if card_data[0] != "All":
            player_object.gear_points[card_data[0]] += path_bonus
        else:
            player_object.gear_points = [path + path_bonus for path in player_object.gear_points]
        # Apply modifier bonuses
        player_object.player_damage += self.damage
        player_object.hp_bonus += self.hp
        player_object.final_damage += self.fd * 0.01
        card_multiplier = self.num_stars * 0.01
        for bonus_roll in card_data[1:]:
            attribute_name, attribute_position = bonus_roll[2], bonus_roll[3]
            if "application" not in attribute_name:
                attribute_value = (bonus_roll[1] * card_multiplier)
            if attribute_position is None:
                setattr(player_object, attribute_name, getattr(player_object, attribute_name) + attribute_value)
            else:
                target_list = getattr(player_object, attribute_name)
                target_list[attribute_position] += attribute_value

    def synthesize_tarot(self):
        new_qty = self.card_qty - 1
        self.set_tarot_field("card_qty", new_qty)
        random_num = random.randint(1, 100)
        success_rate = synthesis_success_rate[self.num_stars]
        if random_num > success_rate:
            return "Synthesis Failed!", "One of the cards dissipates."
        self.num_stars += 1
        self.set_tarot_field("num_stars", self.num_stars)
        return "Synthesis Success!", "The two cards combine into one."

    def set_tarot_field(self, field_name, field_value):
        tarot_check = check_tarot(self.player_id, self.card_name)
        if tarot_check:
            try:
                engine_url = mydb.get_engine_url()
                engine = sqlalchemy.create_engine(engine_url)
                pandora_db = engine.connect()
                query = text(f"UPDATE TarotInventory SET {field_name} = :input_1 "
                             f"WHERE player_id = :player_check AND card_numeral = :numeral_check ")
                query = query.bindparams(input_1=field_value, player_check=self.player_id,
                                         numeral_check=self.card_numeral)
                pandora_db.execute(query)
                pandora_db.close()
                engine.dispose()
            except exc.SQLAlchemyError as error:
                print(error)

    def add_tarot_card(self):
        tarot_check = check_tarot(self.player_id, self.card_name)
        try:
            engine_url = mydb.get_engine_url()
            engine = sqlalchemy.create_engine(engine_url)
            pandora_db = engine.connect()
            if tarot_check:
                already_exists = True
            else:
                query = text("INSERT INTO TarotInventory (player_id, card_numeral, "
                             "card_name, card_qty, num_stars, card_enhancement) "
                             "VALUES (:input_1, :input_2, :input_3, :input_4, :input_5, :input_6)")
                query = query.bindparams(input_1=self.player_id, input_2=self.card_numeral,
                                         input_3=self.card_name, input_4=self.card_qty,
                                         input_5=self.num_stars, input_6=self.card_enhancement)
            pandora_db.execute(query)
            pandora_db.close()
            engine.dispose()
        except exc.SQLAlchemyError as error:
            print(error)


def check_tarot(player_id, card_name):
    selected_tarot = None
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM TarotInventory WHERE player_id = :id_check "
                     "AND card_name = :card_check")
        query = query.bindparams(id_check=player_id, card_check=card_name)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            player_id = int(df['player_id'].values[0])
            card_numeral = str(df['card_numeral'].values[0])
            card_qty = int(df['card_qty'].values[0])
            num_stars = int(df['num_stars'].values[0])
            card_enhancement = int(df['card_enhancement'].values[0])
            selected_tarot = TarotCard(player_id, card_numeral, card_qty, num_stars, card_enhancement)
    except exc.SQLAlchemyError as error:
        print(error)
    return selected_tarot


def tarot_menu_embed(player_object, card_numeral):
    # Pull the card information
    tarot_card = check_tarot(player_object.player_id, card_dict[card_numeral][0])
    if tarot_card is None:
        tarot_card = TarotCard(player_object.player_id, card_numeral, 0, 0, 0)
    # Build the card embed message.
    embed_msg = tarot_card.create_tarot_embed()
    embed_msg.add_field(name=f"", value=f"Quantity: {tarot_card.card_qty}", inline=False)
    embed_msg.set_image(url=tarot_card.card_image_link)
    return embed_msg


def get_index_by_key(numeral):
    keys_list = list(card_dict.keys())
    key_index = keys_list.index(numeral)
    return key_index


def get_key_by_index(key_index):
    keys_list = list(card_dict.keys())
    key_value = keys_list[key_index]
    return key_value


def get_resonance(card_num):
    resonance_list = ['The Reflection', 'The Magic', 'The Celestial', 'The Void', 'The Infinite',
                      'The Duality', 'The Love', 'The Dragon', 'The Behemoth', 'The Memory',
                      'The Temporal', 'The Heavens', 'The Abyss', 'The Death', 'The Clarity',
                      'The Primordial', 'The Fortress', 'The Star', 'The Moon', 'The Sun',
                      'The Requiem', 'The Creation', 'The Creation', 'The Changeling', 'The Pathwalker',
                      'The Soulweaver', 'The Scribe', 'The Oracle', 'The Adjudicator', 'The Lotus',
                      'The Wish']
    if card_num == -1:
        random.choice(resonance_list)
    return resonance_list[card_num]


def collection_check(player_id):
    collection_count = 0
    try:
        engine_url = mydb.get_engine_url()
        engine = sqlalchemy.create_engine(engine_url)
        pandora_db = engine.connect()
        query = text("SELECT * FROM TarotInventory WHERE player_id = :id_check")
        query = query.bindparams(id_check=player_id)
        df = pd.read_sql(query, pandora_db)
        pandora_db.close()
        engine.dispose()
        if len(df.index) != 0:
            collection_count = df.shape[0]
    except exc.SQLAlchemyError as error:
        print(error)
    return collection_count


def binding_ritual(player_object, essence_type, success_rate):
    essence_id = f'Essence{essence_type}'
    essence_stock = inventory.check_stock(player_object, essence_id)
    loot_item = inventory.BasicItem(essence_id)
    embed_msg = tarot_menu_embed(player_object, essence_type)
    # Confirm stock is available
    if essence_stock == 0:
        description_msg = f"Out of stock: {loot_item.item_emoji}!"
        embed_msg.add_field(name="Ritual Failed!", value=description_msg)
        return embed_msg
    # Pay the cost and attempt the binding.
    inventory.update_stock(player_object, essence_id, -1)
    random_roll = random.randint(1, 100)
    if random_roll > success_rate:
        description_msg = "The essence dissipates."
        embed_msg.add_field(name="Ritual Failed!", value=description_msg)
        return embed_msg
    # Update the tarot inventory.
    card_name = card_dict[essence_type][0]
    tarot_check = check_tarot(player_object.player_id, card_name)
    if tarot_check:
        new_qty = tarot_check.card_qty + 1
        tarot_check.set_tarot_field("card_qty", new_qty)
    else:
        new_tarot = TarotCard(player_object.player_id, essence_type, 1, 1, 0)
        new_tarot.add_tarot_card()
    embed_msg = tarot_menu_embed(player_object, essence_type)
    description_msg = "The sealed tarot card has been added to your collection."
    embed_msg.add_field(name="Ritual Successful!", value=description_msg)
    return embed_msg


