# General imports
import discord
import random

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import player
import encounters
from pandoradb import run_query as rqy

fortress_variants = [['Devouring', 0], ['Vengeful', 0], ['Blighted', 1], ['Plagued', 1],
                     ['Writhing', 2], ['Agony', 2], ['Overgrown', 3], ['Man-Eating', 3],
                     ['Shrieking', 4], ['Howling', 4]]
fortress_types = ['Nirvana', 'Paradise', 'Arcadia', 'Eden', 'Dream',
                  'Elysium', 'Sanctuary', 'Domain', 'Oblivion', 'Cradle']

demon_colours = ["Crimson", "Azure", "Violet", "Bronze", "Jade", "Ivory", "Stygian", "Gold", "Rose"]


# Boss class
class CurrentBoss:
    def __init__(self, boss_type_num, boss_type, boss_tier, boss_level):
        self.player_id = 0
        self.boss_type, self.boss_type_num = boss_type, boss_type_num
        self.boss_tier, self.boss_level = boss_tier, boss_level
        self.boss_name, self.boss_image = "", ""
        self.boss_cHP, self.boss_mHP = 0, 0
        self.boss_typeweak = [0, 0, 0, 0, 0, 0, 0]
        self.boss_eleweak = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.curse_debuffs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.boss_element, self.damage_cap = 0, -1
        self.stun_cycles, self.stun_status = 0, ""

    def reset_modifiers(self):
        self.curse_debuffs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def calculate_hp(self) -> bool:
        return self.boss_cHP > 0

    def create_boss_embed(self, dps=0, extension=""):
        img_link = "https://i.ibb.co/0ngNM7h/castle.png"
        if "Demon" in self.boss_image or "Dragon" in self.boss_image:
            img_link = self.boss_image
        tier_colour_dict = {1: [0x43B581, "<:Gem1:1242206599481659442>"], 2: [0x3498DB, "<:Gem2:1242206600555532421>"],
                            3: [0x9B59B6, "<:Gem3:1242206601385873498>"], 4: [0xF1C40F, "<:Gem4:1242206602405347459>"],
                            5: [0xCC0000, "<:Gem5:1242206603441078363>"], 6: [0xE91E63, "<:Gem6:1242206603953049721>"],
                            7: [0xFFFFFF, "<:Gem7:1248490896379478129>"], 8: [0x000000, "<:Gem8:1242206660513108029>"]}
        tier_info = tier_colour_dict[self.boss_tier]
        tier_colour = tier_info[0]
        life_emoji = tier_info[1]
        # Set boss details
        dps_msg = f"{sm.number_conversion(dps)} / min"
        boss_title = f'{self.boss_name}{extension}'
        boss_field = f'Tier {self.boss_tier} {self.boss_type} - Level {self.boss_level}'
        # Set boss hp
        if not self.calculate_hp():
            self.boss_cHP = 0
        hp_bar_icons = gli.hp_bar_dict[min(8, self.boss_tier)]
        boss_hp = f'{life_emoji} ({sm.display_hp(int(self.boss_cHP), int(self.boss_mHP))})'
        bar_length = 0
        if int(self.boss_cHP) >= 1:
            bar_percentage = (int(self.boss_cHP) / int(self.boss_mHP)) * 100
            hp_threshhold = 100 / 15
            bar_length = int(bar_percentage / hp_threshhold)
        filled_segments = hp_bar_icons[0][:bar_length]
        empty_segments = hp_bar_icons[1][bar_length:]
        hp_bar_string = ''.join(filled_segments + empty_segments)
        boss_hp += f'\n{hp_bar_string}'
        # Set boss weakness
        boss_weakness = f'Weakness: '
        for idx, x in enumerate(self.boss_typeweak):
            if x == 1:
                boss_weakness += gli.class_icon_list[idx]
        for idy, y in enumerate(self.boss_eleweak):
            if y == 1:
                boss_weakness += gli.ele_icon[idy]
        embed_msg = discord.Embed(colour=tier_colour, title=boss_title, description="")
        embed_msg.set_image(url=img_link)
        embed_msg.add_field(name=boss_field, value=boss_hp, inline=False)
        embed_msg.add_field(name=boss_weakness, value="", inline=False)
        embed_msg.add_field(name="Current DPS: ", value=dps_msg, inline=False)
        return embed_msg

    def generate_boss_name_image(self, boss_type, boss_tier):
        # Fortress names
        fortress_list_t1 = [("Ominous Keep", ""), ("Twisted Stronghold", "")]
        fortress_list_t2 = [("Malignant Fortress", ""), ("Malevolant Castle", "")]
        fortress_list_t3 = [("Sinful Spire", ""), ("Malefic Citadel", "")]
        fortress_list_t4 = [("XVI - Aurora, The Fortress", "")]
        fortress_names = [fortress_list_t1, fortress_list_t2, fortress_list_t3, fortress_list_t4]

        # Dragon names
        dragon_list_t1 = ["Zelphyros, Wind", "Sahjvadiir, Earth", "Cyries'vael, Ice"]
        dragon_list_t2 = ["Arkadrya, Lightning", "Phyyratha, Fire", "Elyssrya, Water"]
        dragon_list_t3 = ["Y'thana, Light", "Rahk'vath, Shadow"]
        dragon_list_t4 = ["VII - Astratha, The Dimensional"]
        dragon_names = [dragon_list_t1, dragon_list_t2, dragon_list_t3, dragon_list_t4]

        # Demon names
        demon_list_t1 = ["Beelzebub", "Azazel", "Astaroth", "Belial"]
        demon_list_t2 = ["Abbadon", "Asura", "Baphomet", "Charybdis"]
        demon_list_t3 = ["Iblis", "Lilith", "Ifrit", "Scylla"]
        demon_list_t4 = ["VIII - Tyra, The Behemoth"]
        demon_names = [demon_list_t1, demon_list_t2, demon_list_t3, demon_list_t4]

        # Paragon names
        paragon_list_t1 = ["0 - Karma, The Reflection", "I - Runa, The Magic", "VI - Kama, The Love",
                           "IX - Alaya, The Memory", "XIV - Arcelia, The Clarity"]
        paragon_list_t2 = ["XVII - Nova, The Star", "XVIII - Luna, The Moon", "XIX - Luma, The Sun",
                           "XX - Aria, The Reqiuem", "XXI - Ultima, The Creation"]
        paragon_list_t3 = ["V - Arkaya, The Duality", "X - Chrona, The Temporal", "XI - Nua, The Heavens",
                           "XII - Rua, The Abyss", "XIII - Thana, The Death"]
        paragon_list_t4 = ["II - Pandora, The Celestial", "XV - Diabla, The Primordial"]
        paragon_list_t5 = ["III - Oblivia, The Void", "IV - Akasha, The Infinite"]
        paragon_list_t6 = ["XXV - Eleuia, The Wish"]
        paragon_names = [paragon_list_t1, paragon_list_t2, paragon_list_t3, paragon_list_t4, paragon_list_t5,
                         paragon_list_t6]

        # Arbiter names
        arbiter_list_t1 = ["XXII - Mysmir, Changeling of the True Laws"]
        arbiter_list_t2 = ["XXIII - Avalon, Pathwalker of the True Laws"]
        arbiter_list_t3 = ["XXIV - Isolde, Soulweaver of the True Laws"]
        arbiter_list_t4 = ["XXVI - Vexia, Scribe of the True Laws"]
        arbiter_list_t5 = ["XXVII - Kazyth, Lifeblood of the True Laws"]
        arbiter_list_t6 = ["XXVIII - Fleur, Oracle of the True Laws"]
        arbiter_list_t7 = ["XXIX - Yubelle, Adjudicator of the True Laws"]
        arbiter_names = [arbiter_list_t1, arbiter_list_t2, arbiter_list_t3, arbiter_list_t4, arbiter_list_t5,
                         arbiter_list_t6, arbiter_list_t7]

        # Incarnate names
        incarnate_names = [("XXX - Nephilim, Incarnate of the Divine Lotus", "")]

        # All names
        all_names_dict = {"Fortress": fortress_names, "Dragon": dragon_names, "Demon": demon_names,
                          "Paragon": paragon_names, "Arbiter": arbiter_names, "Incarnate": incarnate_names}

        # Assign a random boss default values.
        target_list = all_names_dict[boss_type][(boss_tier - 1)] if boss_tier < 8 else incarnate_names
        if boss_type in ["Paragon", "Arbiter"]:
            self.boss_name = random.choice(target_list)
            numeral = self.boss_name.split()[0]
            self.boss_image = f'{gli.web_url}tarot/{numeral}/{numeral}_8.png'
        elif boss_type not in ["Demon", "Dragon"]:
            self.boss_name, self.boss_image = random.choice(target_list)
            self.boss_image = f'{gli.web_url}bosses/{boss_type}/{boss_tier}.png' if self.boss_image == "" else f'{gli.web_url}{boss_type}/{self.boss_image}.png'
        else:
            self.boss_name = random.choice(target_list)
        self.boss_element = 9

        # Handle boss type exceptions.
        match boss_type:
            case "Fortress":
                if boss_tier != 4:
                    boss_prefix, self.boss_element = random.choice(fortress_variants)
                    boss_prefix += f" {random.choice(fortress_types)}, "
                    self.boss_name = boss_prefix + "the " + self.boss_name
            case "Dragon":
                temp_name_split = self.boss_name.split()
                boss_element = temp_name_split[1]
                self.boss_element = 8
                if boss_tier != 4:
                    self.boss_element = gli.element_names.index(boss_element)
                    self.boss_name += " Dragon"
                self.boss_image = f'{gli.web_url}bosses/{boss_type}/{gli.element_names[self.boss_element]}_Dragon.png'
            case "Demon":
                if boss_tier != 4:
                    self.boss_element = random.randint(0, 8)
                    boss_colour = demon_colours[self.boss_element]
                    if boss_colour not in ["Crimson", "Azure", "Jade", "Violet", "Gold"]:
                        self.boss_image = ""
                    self.boss_image = f'{gli.web_url}bosses/Demon/{boss_colour}/{self.boss_name}_{boss_colour}.png'
                    self.boss_name = f'{boss_colour} {self.boss_name}'
            case _:
                pass


async def spawn_boss(channel_id, player_id, new_boss_tier, selected_boss_type, boss_level, channel_num,
                     gauntlet=False, magnitude=0):
    raid_id = await encounters.get_raid_id(channel_id, player_id)

    # Handle existing boss.
    if raid_id != 0:
        raw_query = "SELECT * FROM BossList WHERE raid_id = :id_check"
        df = await rqy(raw_query, return_value=True, params={'id_check': raid_id})
        player_id = int(df["player_id"].values[0])
        boss_tier, boss_level = int(df["boss_tier"].values[0]), int(df["boss_level"].values[0])
        boss_type, boss_type_num = str(df["boss_type"].values[0]), int(df["boss_type_num"].values[0])
        boss_object = CurrentBoss(boss_type_num, boss_type, boss_tier, boss_level)
        boss_object.boss_name = str(df["boss_name"].values[0])
        boss_object.boss_cHP, boss_object.boss_mHP = int(df["boss_cHP"].values[0]), int(df["boss_mHP"].values[0])
        temp_t, temp_e = list(df['boss_typeweak'].values[0].split(';')), list(df['boss_eleweak'].values[0].split(';'))
        boss_object.boss_typeweak, boss_object.boss_eleweak = list(map(int, temp_t)), list(map(int, temp_e))
        boss_object.boss_image = str(df["boss_image"].values[0])

        # Set the damage cap.
        boss_object.damage_cap = -1
        if boss_object.boss_tier <= 4:
            boss_object.damage_cap = (10 ** int(boss_level / 10 + 4) - 1)
        return boss_object
    # Create the boss object if it doesn't exist.
    raid_type = "solo"
    boss_type_num = gli.boss_list.index(selected_boss_type)
    if new_boss_tier == 7:
        boss_level += 150
    elif new_boss_tier == 6:
        boss_level += 10
    elif selected_boss_type == "Arbiter":
        boss_level += 10
    boss_object = CurrentBoss(boss_type_num, selected_boss_type, new_boss_tier, boss_level)

    # Assign elemental weaknesses.
    eleweak_list = random.sample(range(9), 3)
    for x in eleweak_list:
        boss_object.boss_eleweak[x] = 1
    boss_eleweak = ";".join(str(y) for y in boss_object.boss_eleweak)
    boss_eleweak = boss_eleweak.rstrip(';')

    # Assign type weaknesses.
    typeweak_list = random.sample(range(7), 2)
    for x in typeweak_list:
        boss_object.boss_typeweak[x] = 1
    boss_typeweak = ";".join(str(y) for y in boss_object.boss_typeweak)
    boss_typeweak = boss_typeweak.rstrip(';')

    # Set boss hp and damage cap.
    total_hp = int(10 ** (min(100, boss_object.boss_level) // 10 + 5)) * (10 ** magnitude)
    if boss_object.boss_level >= 100:
        multiplier_count = (boss_object.boss_level - 100) // 100 + 1
        total_hp *= (10 ** multiplier_count)
    boss_object.damage_cap = total_hp // 10 - 1
    if boss_object.boss_type == "Incarnate":
        boss_object.damage_cap = -1

    # Increase raid boss hp and damage cap.
    if channel_num != 0:
        raid_type = "raid"
        raid_hp_dict = {1: 100, 2: 10000, 3: 1000000, 4: 100000000}
        total_hp *= raid_hp_dict[channel_num]

    # Assign remaining boss details.
    boss_object.generate_boss_name_image(boss_object.boss_type, boss_object.boss_tier)
    boss_object.boss_mHP = total_hp
    boss_object.boss_cHP = boss_object.boss_mHP

    # Apply the new boss to the database.
    raw_query = ("INSERT INTO ActiveRaids (channel_id, player_id, encounter_type) "
                 "VALUES (:input_1, :player_id, :raid_type)")
    await rqy(raw_query, params={'input_1': str(channel_id), 'player_id': player_id, 'raid_type': raid_type})
    raid_id = await encounters.get_raid_id(channel_id, player_id)
    raw_query = ("INSERT INTO BossList "
                 "(raid_id, player_id, boss_name, boss_tier, boss_level, boss_type_num, boss_type, "
                 "boss_cHP, boss_mHP, boss_typeweak, boss_eleweak, boss_image) "
                 "VALUES (:raid_id, :player_id, :input_1, :input_2, :input_3, :input_4, :input_5, "
                 ":input_6, :input_7, :input_8, :input_9, :input_10)")
    params = {'raid_id': raid_id, 'player_id': player_id, 'input_1': boss_object.boss_name, 'input_2': new_boss_tier,
              'input_3': boss_level, 'input_4': boss_type_num, 'input_5': selected_boss_type,
              'input_6': str(int(total_hp)), 'input_7': str(int(total_hp)), 'input_8': boss_typeweak,
              'input_9': boss_eleweak, 'input_10': boss_object.boss_image}
    await rqy(raw_query, params=params)
    return boss_object


def get_random_bosstier(boss_type):
    # Assign tier rates.
    tier_breakpoint_list = {3: 6, 10: 5, 20: 4, 40: 3, 65: 2, 100: 1}
    if boss_type != "Arbiter":
        tier_breakpoint_list = {10: 4, 35: 3, 65: 2, 100: 1}
    # Determine the tier.
    random_number = random.randint(1, 100)
    for rate_breakpoint, tier_value in tier_breakpoint_list.items():
        if random_number <= rate_breakpoint:
            boss_tier = tier_value
            break
    # Handle non-paragon exceptions for pseudo-paragon type bosses.
    if boss_tier == 4 and boss_type == "Paragon":
        paragon_exceptions = [0, 1, 2, 3, 3]
        boss_type = gli.boss_list[random.choice(paragon_exceptions)]
    return boss_tier, boss_type


# generate ele weakness
def get_element(chosen_weakness):
    random_number = chosen_weakness if chosen_weakness == 0 else random.randint(0, 8)
    element_temp = gli.ele_icon[random_number]
    return element_temp


async def update_player_damage(channel_id, player_id, player_damage):
    raid_id = await encounters.get_raid_id(channel_id, 0)
    raw_query = "UPDATE RaidPlayers SET player_dps = :new_dps WHERE raid_id = :id_check AND player_id = :player_check"
    await rqy(raw_query, params={'new_dps': player_damage, 'id_check': raid_id, 'player_check': player_id})


async def update_boss_cHP(channel_id, player_id, new_boss_cHP):
    raid_id = await encounters.get_raid_id(channel_id, player_id)
    raw_query = "UPDATE BossList SET boss_cHP = :new_cHP WHERE raid_id = :id_check"
    await rqy(raw_query, params={'new_cHP': str(int(new_boss_cHP)), 'id_check': raid_id})


async def get_damage_list(channel_id):
    raid_id = await encounters.get_raid_id(channel_id, 0)
    raw_query = "SELECT player_id, player_dps FROM RaidPlayers WHERE raid_id = :id_check"
    df = await rqy(raw_query, True, params={'id_check': raid_id})
    if df is None or len(df.index) == 0:
        return [], []
    username = df["player_id"].values.tolist()
    damage = df["player_dps"].values.tolist()
    return username, damage


async def clear_boss_info(channel_id, player_id):
    if player_id == "All":
        raw_queries = ["DELETE FROM ActiveRaids WHERE encounter_type = 'solo' or encounter_type = 'gauntlet'",
                       "DELETE FROM BossList WHERE player_id <> 0"]
        params = None
    else:
        raid_id = await encounters.get_raid_id(channel_id, player_id)
        raw_queries = ["DELETE FROM ActiveRaids WHERE raid_id = :id_check",
                       "DELETE FROM BossList WHERE raid_id = :id_check",
                       "DELETE FROM RaidPlayers WHERE raid_id = :id_check"]
        params = {'id_check': raid_id}
    for query in raw_queries:
        await rqy(query, params=params)


async def create_dead_boss_embed(channel_id, active_boss, dps, extension=""):
    active_boss.boss_cHP = 0
    dead_embed = active_boss.create_boss_embed(dps, extension=extension)
    player_list, damage_list = await get_damage_list(channel_id)
    output_list = ""
    for idx, x in enumerate(player_list):
        player_obj = await player.get_player_by_id(x)
        output_list += f'{str(player_obj.player_username)}: {sm.number_conversion(int(damage_list[idx]))}\n'
    dead_embed.add_field(name="SLAIN", value=output_list, inline=False)
    return dead_embed
