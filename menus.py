# General imports
import discord
from discord.ui import Button, View
import asyncio
import random

# Data imports
import globalitems as gli
from questdata import reg_msg

# Core imports
from pandoradb import run_query as rqy
import player
import inventory
import quest
import combat
import sharedmethods as sm
import skillpaths
import bazaar
import market
import infuse
import questdata
import monument

# Item/crafting imports
import loot
import forge
import insignia
import pact
import tarot

starter_guide = "1. Use /quest to progress through the quest."
starter_guide += "\n2. Use /map to farm for tier 1-4 Weapons, Armour, Amulets, and EXP."
starter_guide += "\n3. Use /inv to check your inventory. Then click Toggle to check your gear."
starter_guide += "\n4. Use /display [item id] to view, sell, inlay, and equip items."
starter_guide += "\n5. Use /solo to farm tier 1-4 bosses for gear. Stones can be used to select the boss type."
starter_guide += "\n6. Use /stamina to check your stamina and consume stamina potions."
starter_guide += "\n7. Use /market to buy fae cores, stamina potions, crafting materials, and more."
starter_guide += "\n8. Use /gear to view your equipped gear, gems, pact, tarot, and insignia."
starter_guide += "\n9. Use /info for a command list."
starter_guide += "\n10. Use /profile to view your server card, level, and exp."

intermediate_guide = "1. Use /forge to craft your items. Details can be found in the wiki."
intermediate_guide += "\n2. Use /manifest to hunt monsters for more exp."
intermediate_guide += "\n3. Use /points to allocate skill points and acquire glyphs."
intermediate_guide += "\n4. Use /infuse to transmute new items."
intermediate_guide += "\n5. Use /stats to check your stats details and point glyphs."
intermediate_guide += "\n6. Use /engrave to engrave an insignia on your soul. Req Quest: 20"
intermediate_guide += "\n7. Use /refinery to refine powerful unprocessed gear items."
intermediate_guide += "\n8. Use /tarot [card number] to bind essence items to tarot cards."
intermediate_guide += "\n9. Use /bazaar, /sell, /give, /trade, and /buy to trade items."
intermediate_guide += "\n10. Use /fishmenu, /quickfish, /turbofishing, /ultimatefishing, and /omegafishing to fish."

advanced_guide = "1. Use /summon and spend summoning items to fight powerful opponents above tier 5!"
advanced_guide += "\n2. Use /gauntlet to challenge the difficult Spire of Illusions for great rewards!"
advanced_guide += "\n3. Use /abyss to upgrade gear items past tier 5. Req Quest: 38"
advanced_guide += "\n4. Use /scribe to attain perfect rolls on your items."
advanced_guide += "\n5. Use /meld to combine and upgrade heart jewels to higher tiers. Req Quest: 42"
advanced_guide += "\n6. Use /purge [itemtype] [Tier] to clear out useless low tier items."
advanced_guide += "\n7. Use /infuse to create ring gear items using rare materials."
advanced_guide += "\n8. Use /sanctuary and search everywhere for the rare and elusive lotus items."
advanced_guide += "\n9. Challenge /palace on higher difficulties to raise the level limit and reach alternate endings."
advanced_guide += "\n10. Fight for the top stop on the /leaderboard for unique roles."
guide_dict = {0: ["Beginner Guide", starter_guide],
              1: ["Intermediate Guide", intermediate_guide],
              2: ["Advanced Guide", advanced_guide]}

thana_title, eleuia_title = "Thana, The Death", "Echo of Eleuia, The Wish"
thana_img = f"{gli.web_gallery_url}/Tarot/Paragon/XIII - Thana, The Death.webp"


class GuideMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Beginner", style=discord.ButtonStyle.blurple, emoji="🌟")
    async def beginner_help_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title=guide_dict[0][0], description=guide_dict[0][1])
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Intermediate", style=discord.ButtonStyle.blurple, emoji="✨")
    async def intermediate_help_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title=guide_dict[1][0], description=guide_dict[1][1])
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Advanced", style=discord.ButtonStyle.blurple, emoji="🚀")
    async def advanced_help_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(),
                                  title=guide_dict[2][0], description=guide_dict[2][1])
        await interaction.response.edit_message(embed=embed_msg)


class HelpView(discord.ui.View):
    def __init__(self, category_dict):
        super().__init__(timeout=None)
        self.category_dict = category_dict

    @discord.ui.button(label="Game", style=discord.ButtonStyle.blurple, row=0, emoji="🐉")
    async def game_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'game')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Combat", style=discord.ButtonStyle.blurple, row=0, emoji="⚔️")
    async def combat_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'combat')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Gear", style=discord.ButtonStyle.blurple, row=0, emoji="⚔️")
    async def gear_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'gear')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Craft", style=discord.ButtonStyle.blurple, row=1, emoji="<:ehammer:1145520259248427069>")
    async def craft_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'craft')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Trade", style=discord.ButtonStyle.blurple, row=1, emoji="💲")
    async def trade_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'trade')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Areas", style=discord.ButtonStyle.blurple, row=1, emoji="ℹ️")
    async def location_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'location')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Info", style=discord.ButtonStyle.blurple, row=2, emoji="ℹ️")
    async def account_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'info')
        await interaction.response.edit_message(embed=embed_msg)

    @discord.ui.button(label="Admin", style=discord.ButtonStyle.red, row=2, emoji="⌨")
    async def admin_help_callback(self, interaction: discord.Interaction, button: discord.Button):
        embed_msg = build_help_embed(self.category_dict, 'admin')
        await interaction.response.edit_message(embed=embed_msg)


def build_help_embed(category_dict, category_name):
    display_category_name = category_name.capitalize()
    embed = sm.easy_embed("Orange", f"{display_category_name} Commands:", "")
    commands = category_dict[category_name]
    commands.sort(key=lambda x: x[2])
    for command_name, description, _ in commands:
        embed.add_field(name=f"/{command_name}", value=f"{description}", inline=False)
    return embed


class TownView(discord.ui.View):
    def __init__(self, ctx_obj, player_obj, monument_data):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_obj = ctx_obj, player_obj
        monument_claims = monument_data.split(';')
        if self.player_obj.player_level >= 15:
            self.monument_callback.label = "Monument"
            self.monument_callback.style = gli.button_colour_list[0]
            if not monument_claims[0] == "1":
                self.monument_callback.disabled = False
                self.monument_callback.style = gli.button_colour_list[1]

    @discord.ui.button(label="Refinery", style=discord.ButtonStyle.blurple, row=0)
    async def refinery_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title, description = "Refinery", "Please select the item to refine"
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        embed_msg.set_image(url=gli.refinery_img)
        await interaction.response.edit_message(embed=embed_msg, view=forge.RefSelectView(self.player_obj))

    @discord.ui.button(label="Alchemist", style=discord.ButtonStyle.blurple, row=0)
    async def alchemist_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title, description = "Cloaked Alchemist, Sangam", "I can make anything, if you bring the right stuff."
        embed_msg = discord.Embed(colour=discord.Colour.magenta(), title=title, description=description)
        embed_msg.set_image(url=gli.infuse_img)
        await interaction.response.edit_message(embed=embed_msg, view=infuse.InfuseView(self.ctx_obj, self.player_obj))

    @discord.ui.button(label="Market", style=discord.ButtonStyle.blurple, row=0)
    async def market_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title, description = "Black Market", "Everything has a price."
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        embed_msg.set_image(url=gli.market_img)
        fish_obj, trade_obj = await market.get_daily_fish_items()
        new_view = market.TierSelectView(self.player_obj, fish_obj, trade_obj)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Bazaar", style=discord.ButtonStyle.blurple, row=0)
    async def bazaar_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        embed_msg = await bazaar.show_bazaar_items(self.player_obj)
        embed_msg.set_image(url=gli.bazaar_img)
        await interaction.response.edit_message(embed=embed_msg, view=bazaar.BazaarView(self.player_obj))

    @discord.ui.button(label="?????", style=discord.ButtonStyle.secondary, disabled=True, row=1)
    async def monument_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        await monument.get_monument_embed(interaction, self.ctx_obj, self.player_obj, 0)


class CelestialView(discord.ui.View):
    def __init__(self, ctx_obj, player_obj, num_visits, monument_data):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_obj, self.num_visits = ctx_obj, player_obj, num_visits
        monument_claims = monument_data.split(';')
        if self.num_visits > 0:
            self.summon_callback.label = "Call Thana"
        if self.player_obj.player_level >= 30:
            self.monument_callback.label = "Monument"
            self.monument_callback.style = gli.button_colour_list[0]
            if not monument_claims[1] == "1":
                self.monument_callback.disabled = False
                self.monument_callback.style = gli.button_colour_list[1]

    @discord.ui.button(label="Forge", style=discord.ButtonStyle.blurple, row=0)
    async def forge_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title="Pandora's Celestial Forge", description="")
        name, value = "Pandora, The Celestial", "Let me know what you'd like me to upgrade!"
        embed_msg.add_field(name=name, value=value, inline=False)
        embed_msg.set_image(url=gli.forge_img)
        await interaction.response.edit_message(embed=embed_msg, view=forge.SelectView(self.player_obj, "celestial"))

    @discord.ui.button(label="Tarot", style=discord.ButtonStyle.blurple, row=0)
    async def planetarium_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        completion_count = await tarot.collection_check(self.player_obj)
        title, description = "Pandora, The Celestial", "Welcome to the planetarium. Sealed tarots are stored here."
        embed_msg = discord.Embed(colour=discord.Colour.magenta(), title=title, description=description)
        name, value = f"{self.player_obj.player_username}'s Tarot Collection", f"Completion Total: {completion_count} / 31"
        embed_msg.add_field(name=name, value=value, inline=False)
        embed_msg.set_image(url=gli.planetarium_img)
        await interaction.response.edit_message(embed=embed_msg, view=tarot.CollectionView(self.player_obj))

    @discord.ui.button(label="?????", style=discord.ButtonStyle.blurple, row=0)
    async def summon_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        item_obj = inventory.BasicItem("Skull2")
        if self.num_visits == 0:
            description = (f"Ah so you're Pandora's new pet. One ought to be more cautious when speaking my name. "
                           f"You never know when death is waiting just around the corner. "
                           f"Or were you perhaps dissatisfied with awaiting your scheduled departure? "
                           f"I jest. Unlike the others, I alone will support you {self.player_obj.player_username}. "
                           f"In exchange for your kind invitation to my little sister's abode I offer you a gift.\n"
                           f"Thana hands you a valuable item: {item_obj.item_emoji} 1x {item_obj.item_name}\n"
                           f"This skull belonged to a general of my fallen undead legion during the last paragon war. "
                           f"Their remains have been stolen and scattered. Return them to me and I shall reward you.\n")
            await inventory.update_stock(self.player_obj, item_obj.item_id, 1)
            await self.player_obj.update_misc_data("thana_visits", 1)
            name = f"Heed my words human. I will not tolerate disobedience."
            value = (f"If you overestimate yourself and try to seal me, I will *KILL* you.\n"
                     f"If tell anyone I was here, I will *KILL* you.\n"
                     f"If you hurt my little sister, I will *KILL* you.\n")
        else:
            player_deaths = int(await self.player_obj.check_misc_data('deaths'))
            description = (f"I will continue to revive your mortal body so long as you continue to aid me. "
                           f"Though, should you ever want to remain dead you are more than welcome to stay by my side. "
                           f"You've died {player_deaths} times you know. It'd save me quite the hassle. "
                           f"I must confess, the mere thought of my sister's jealousy, every time you call my name "
                           f"fills me with immeasurable pleasure.\n")
            name, value = "", "Out with it now, what can the embodiment of death do for you today?"
        embed_msg = discord.Embed(colour=discord.Colour.dark_purple(), title=thana_title, description=description)
        embed_msg.add_field(name=name, value=value, inline=False)
        embed_msg.set_image(url=thana_img.replace(' ', "%20"))
        skull_ring = False
        if self.player_obj.player_equipped[4] != 0:
            e_ring = await inventory.read_custom_item(self.player_obj.player_equipped[4])
            if e_ring.item_base_type == "Crown of Skulls":
                skull_ring = True
        await interaction.response.edit_message(embed=embed_msg, view=SkullSelectView(self.player_obj, skull_ring))

    @discord.ui.button(label="?????", style=discord.ButtonStyle.secondary, disabled=True, row=1)
    async def monument_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        await monument.get_monument_embed(interaction, self.ctx_obj, self.player_obj, 1)


class DivineView(discord.ui.View):
    def __init__(self, ctx_obj, player_obj, monument_data):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_obj = ctx_obj, player_obj
        monument_claims = monument_data.split(';')
        if self.player_obj.player_quest < 10:
            self.changeling_callback.disabled, self.changeling_callback.style = True, gli.button_colour_list[3]
            self.points_callback.disabled, self.points_callback.style = True, gli.button_colour_list[3]
        if self.player_obj.player_quest < 20:
            self.engrave_callback.disabled, self.engrave_callback.style = True, gli.button_colour_list[3]
        if self.player_obj.player_quest < 46:
            self.scribe_callback.disabled, self.scribe_callback.style = True, gli.button_colour_list[3]
        if self.player_obj.player_quest < 48:
            self.sanctuary_callback.disabled, self.sanctuary_callback.style = True, gli.button_colour_list[3]
        if self.player_obj.player_quest < 51:
            self.cathedral_callback.disabled, self.cathedral_callback.style = True, gli.button_colour_list[3]
        if self.player_obj.player_level >= 45:
            self.monument_callback.label = "Monument"
            self.monument_callback.style = gli.button_colour_list[0]
            if not monument_claims[2] == "1":
                self.monument_callback.disabled = False
                self.monument_callback.style = gli.button_colour_list[1]

    @discord.ui.button(label="Mysmir", style=discord.ButtonStyle.blurple, row=0)
    async def changeling_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title = "Mysmir, The Changeling"
        token_obj, ore_obj = inventory.BasicItem("Token1"), inventory.BasicItem("Metamorphite")
        token_stock = await inventory.check_stock(self.player_obj, token_obj.item_id)
        embed_msg = await market.changeling_cost_msg(token_obj, token_stock, ore_obj)
        new_view = market.ChangelingShopView(self.player_obj, token_obj, ore_obj)
        embed_msg.set_image(url=gli.cathedral_img)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="Avalon", style=discord.ButtonStyle.blurple, row=0)
    async def points_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        embed_msg = await skillpaths.create_path_embed(self.player_obj)
        await interaction.response.edit_message(embed=embed_msg, view=PointsView(self.player_obj))

    @discord.ui.button(label="Isolde", style=discord.ButtonStyle.blurple, row=0)
    async def engrave_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title = "Isolde, The Soulweaver"
        description = "You've come a long way from home child. Tell me, what kind of power do you seek?"
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title, description=description)
        await interaction.response.edit_message(embed=embed_msg, view=insignia.InsigniaView(self.player_obj))

    @discord.ui.button(label="Vexia", style=discord.ButtonStyle.blurple, row=1)
    async def scribe_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        e_weapon = await inventory.read_custom_item(self.player_obj.player_equipped[0])
        title = "Vexia, The Scribe"
        entry_msg = ("We need not turn you away, mortal."
                     "\nThe oracle has already foretold your failure. Now it need only be written into truth.")
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=title, description=entry_msg)
        embed_msg.set_image(url=gli.cathedral_img)
        await interaction.response.edit_message(embed=embed_msg, view=forge.SelectView(self.player_obj, "custom"))

    @discord.ui.button(label="Fleur", style=discord.ButtonStyle.blurple, row=1)
    async def sanctuary_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title = "Fleur, The Oracle"
        entry_msg = ("Have you come to desecrate my holy gardens once more? Well, I suppose it no longer matters, "
                     "I know you will inevitably find what you desire even without my guidance. "
                     "If you intend to sever the divine lotus, then I suppose the rest are nothing but pretty flowers.")
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=title, description=entry_msg)
        embed_msg.set_image(url=gli.sanctuary_img)
        await interaction.response.edit_message(embed=embed_msg, view=market.LotusSelectView(self.player_obj))

    @discord.ui.button(label="Yubelle", style=discord.ButtonStyle.blurple, row=1)
    async def cathedral_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        title = "Yubelle, The Adjudicator"
        entry_msg = ("You would still follow Pandora's path in her place? Very well, I am no longer in a position "
                     "to object. I suppose, even as an echo, such things do indeed fall within my purview.")
        embed_msg = discord.Embed(colour=discord.Colour.blurple(), title=title, description=entry_msg)
        embed_msg.set_image(url=gli.cathedral_img)
        new_view = tarot.SearchTierView(self.player_obj, cathedral=True)
        await interaction.response.edit_message(embed=embed_msg, view=new_view)

    @discord.ui.button(label="?????", style=discord.ButtonStyle.secondary, disabled=True, row=2)
    async def monument_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        await monument.get_monument_embed(interaction, self.ctx_obj, self.player_obj, 2)


class AbyssView(discord.ui.View):
    def __init__(self, ctx_obj, player_obj, num_visits, monument_data, gear_score):
        super().__init__(timeout=None)
        self.ctx_obj, self.player_obj, self.num_visits = ctx_obj, player_obj, num_visits
        monument_claims = monument_data.split(';')
        if self.player_obj.player_quest < 47:
            self.summon_callback.disabled = True
        if self.num_visits > 0:
            self.summon_callback.label = "Call Eleuia"
        if self.player_obj.player_level >= 60:
            self.monument_callback.label = "Monument"
            self.monument_callback.style = gli.button_colour_list[0]
            if not monument_claims[3] == "1":
                self.monument_callback.disabled = False
                self.monument_callback.style = gli.button_colour_list[1]
        self.gear_monument_callback.label = f"★{gear_score:,}"
        if gear_score > 99999:
            self.gear_monument_callback.label = f"☆{gear_score}"
            self.gear_monument_callback.style = gli.button_colour_list[0]
            if not monument_claims[4] == "1":
                self.gear_monument_callback.disabled = False
                self.gear_monument_callback.style = gli.button_colour_list[1]

    @discord.ui.button(label="Deep Void", style=discord.ButtonStyle.blurple, row=0)
    async def purify_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        embed_msg = sm.easy_embed("Black", "Echo of Oblivia, The Void", gli.abyss_msg)
        embed_msg.set_image(url=gli.abyss_img)
        await interaction.response.edit_message(embed=embed_msg, view=forge.SelectView(self.player_obj, "purify"))

    @discord.ui.button(label="?????", style=discord.ButtonStyle.blurple, row=0)
    async def summon_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = (f"Honestly, I'd like to get to know you better. "
                       f"I know the abyssal plane isn't the safest of places to sit and have a discussion. "
                       f"Still, I'm glad that you came. Would you like to know about the past? "
                       f"Or perhaps did you have something else in mind?")
        if self.num_visits == 0:
            description = (f"Oh, {self.player_obj.player_username}, I didn't think you'd find me here. "
                           f"The silence, the darkness, the soft longing pull of the abyss, I find it... relaxing. "
                           f"I don't like the celestial plane much, it reminds me of the war. "
                           f"It reminds me that I'm just a piece of the real Pandora, except for Thana, all of us are. "
                           f"Most of all it reminds me of the Paragon War. In the end it was all my fault. "
                           f"Pandora isn't here, she can't enter the abyssal plane, so I'll tell you. "
                           f"\nShe feels the same way we do. She's afraid of losing herself to become whole again. "
                           f"The original girl named Pandora is gone, maybe if you tell her that she'll listen. "
                           f"She is Pandora now, and she's the only one who doesn't understand that. "
                           f"No, she knows that better than anyone, she just refuses to accept herself. "
                           f"\nDuty be damned. She has a right to live for herself. "
                           f"I wish I'd been brave enough to tell her that. I wish I could've told her I'm sorry. "
                           f"But we can only wish for the future, even Chrona cannot rewrite the past. "
                           f"Once again my own wishes elude me. Why was I given this power at all? "
                           f"\nShould you want to talk to me again, just call my name.")
            await self.player_obj.update_misc_data("eleuia_visits", 1)
        embed_msg = sm.easy_embed("Pink", eleuia_title, description)
        embed_msg.set_image(url="")
        tears_ring = False
        if self.player_obj.player_equipped[4] != 0:
            e_ring = await inventory.read_custom_item(self.player_obj.player_equipped[4])
            if e_ring.item_base_type == "Chromatic Tears":
                tears_ring = True
        await interaction.response.edit_message(embed=embed_msg, view=TearLoreView(self.player_obj, tears_ring))

    @discord.ui.button(label="?????", style=discord.ButtonStyle.secondary, disabled=True, row=1)
    async def monument_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        await monument.get_monument_embed(interaction, self.ctx_obj, self.player_obj, 3)

    @discord.ui.button(label="★", style=discord.ButtonStyle.secondary, disabled=True, row=1)
    async def gear_monument_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        await monument.get_monument_embed(interaction, self.ctx_obj, self.player_obj, 4)


class TearLoreView(discord.ui.View):
    def __init__(self, player_obj, tears_ring):
        super().__init__(timeout=None)
        self.player_obj, self.num_visits = player_obj, tears_ring

    @discord.ui.button(label="Talk", style=discord.ButtonStyle.blurple, row=0)
    async def eleuia_lore_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = f"Lore will go here"
        embed_msg = sm.easy_embed("Pink", eleuia_title, description)
        lore_view = None
        await interaction.response.edit_message(embed=embed_msg, view=lore_view)

    @discord.ui.button(label="Imbue", style=discord.ButtonStyle.blurple, row=0)
    async def imbue_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = "You've collected more of my teardrops?\nYou really don't need to do this, but I'm glad you did."
        embed_msg = sm.easy_embed("Pink", eleuia_title, description)
        await interaction.response.edit_message(embed=embed_msg, view=ImbueView(self.player_obj))


class ImbueView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.embed = None

    @discord.ui.button(label="1 Tear", style=discord.ButtonStyle.primary, emoji=gli.tears_icon)
    async def submit_one_tear(self, interaction: discord.Interaction, button: discord.Button):
        await self.imbue_callback(interaction, 1)

    @discord.ui.button(label="5 Tears", style=discord.ButtonStyle.primary, emoji=gli.tears_icon)
    async def submit_five_tears(self, interaction: discord.Interaction, button: discord.Button):
        await self.imbue_callback(interaction, 5)

    @discord.ui.button(label="10 Tears", style=discord.ButtonStyle.primary, emoji=gli.tears_icon)
    async def submit_ten_tears(self, interaction: discord.Interaction, button: discord.Button):
        await self.imbue_callback(interaction, 10)

    async def imbue_callback(self, interaction: discord.Interaction, num_tears):
        if interaction.user.id != self.player_obj.discord_id:
            return
        reload_view = ImbueView(self.player_obj)
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=reload_view)
            return
        await self.player_obj.reload_player()
        equipped_ring_id = self.player_obj.player_equipped[4]
        self.embed = sm.easy_embed("Pink", eleuia_title, "Could you put the ring back on for me? Please.")
        if equipped_ring_id == 0:
            await interaction.response.edit_message(embed=self.embed, view=reload_view)
            return
        equipped_ring = await inventory.read_custom_item(equipped_ring_id)
        if equipped_ring.item_base_type != "Chromatic Tears":
            await interaction.response.edit_message(embed=self.embed, view=reload_view)
            return
        tears_stock = await inventory.check_stock(self.player_obj, "Gemstone10")
        if tears_stock < num_tears:
            self.embed.description = "I don't think you have that many."
            await interaction.response.edit_message(embed=self.embed, view=reload_view)
            return
        await inventory.update_stock(self.player_obj, "Gemstone10", (-1 * num_tears))
        equipped_ring.roll_values[0] = str(int(equipped_ring.roll_values[0]) + num_tears)
        await equipped_ring.update_stored_item()
        description = "Such a beautiful glow. I've imbued it for you, may it keep you safe until you return."
        self.embed = await equipped_ring.create_citem_embed()
        self.embed.add_field(name="", value=description, inline=False)
        await interaction.response.edit_message(embed=self.embed, view=reload_view)


async def add_skull_fields(player_obj, embed_msg, method="Return"):
    await player_obj.reload_player()
    skull_items = [inventory.BasicItem(f"Skull{i}") for i in range(1, 5)]
    field_value = ""
    if method != "Sacrifice":
        coin_msg = f"{gli.coin_icon} {player_obj.player_coins:,}x Lotus Coins"
        embed_msg.add_field(name=f"Current Coins", value=coin_msg, inline=False)
    for item in skull_items:
        price = item.item_cost // 2 if method == "Return" else item.item_cost
        skull_stock = await inventory.check_stock(player_obj, item.item_id)
        coin_msg = f"{gli.coin_icon} {price:,}x Lotus Coins\n"
        if method == "Return":
            field_value += f"{item.item_emoji} {skull_stock}x __**{item.item_name}**__: {coin_msg}"
        elif method == "Purchase":
            field_value += f"{item.item_emoji} __**{item.item_name}**__: {coin_msg}"
        else:
            field_value += f"{item.item_emoji} {skull_stock}x __**{item.item_name}**__\n"
    embed_msg.add_field(name=f"{method} Value", value=field_value, inline=False)
    return embed_msg


class SkullSelectView(discord.ui.View):
    def __init__(self, player_obj, skull_ring):
        super().__init__(timeout=None)
        self.player_obj, self.skull_ring = player_obj, skull_ring
        if skull_ring:
            self.feed_ring_callback.disabled = False
            self.feed_ring_callback.style = gli.button_colour_list[2]

    @discord.ui.button(label="Talk", style=discord.ButtonStyle.blurple, row=0)
    async def thana_lore_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = f"Lore will go here"
        embed_msg = discord.Embed(colour=discord.Colour.dark_purple(), title=thana_title, description=description)
        lore_view = None
        await interaction.response.edit_message(embed=embed_msg, view=lore_view)

    @discord.ui.button(label="Return Skulls", style=discord.ButtonStyle.blurple, row=0)
    async def return_skulls_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = f"Did you bring skulls for me {self.player_obj.player_username}? I shall reward you."
        embed_msg = discord.Embed(colour=discord.Colour.dark_purple(), title=thana_title, description=description)
        embed_msg = await add_skull_fields(self.player_obj, embed_msg, method="Return")
        await interaction.response.edit_message(embed=embed_msg, view=SkullsView(self.player_obj, method="Return"))

    @discord.ui.button(label="Buy Skulls", style=discord.ButtonStyle.blurple, row=0)
    async def buy_skulls_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = ("I'm not really sure...\nOh fine, I suppose you were the one who returned them after all. "
                       "If you're willing to compensate me appropriately, I suppose I can let you have some.")
        embed_msg = discord.Embed(colour=discord.Colour.dark_purple(), title=thana_title, description=description)
        embed_msg = await add_skull_fields(self.player_obj, embed_msg, method="Purchase")
        await interaction.response.edit_message(embed=embed_msg, view=SkullsView(self.player_obj, method="Purchase"))

    @discord.ui.button(label="Upgrade Ring", style=discord.ButtonStyle.secondary, row=0, disabled=True)
    async def feed_ring_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        description = ("Did you bring me more skulls so that I can imbue your ring with more of my love? "
                       "Take off your clothes and lie down for me. I'll be with you in a moment once I'm ready."
                       "Place the hand with the ring against my chest.\n"
                       "Now close your eyes, I'll begin the ritual...")
        embed_msg = discord.Embed(colour=discord.Colour.dark_purple(), title=thana_title, description=description)
        embed_msg = await add_skull_fields(self.player_obj, embed_msg, method="Sacrifice")
        await interaction.response.edit_message(embed=embed_msg, view=SkullsView(self.player_obj, method="Sacrifice"))


class SkullsView(discord.ui.View):
    def __init__(self, player_obj, method="Return"):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.method = method
        self.new_embed, self.new_view = None, None
        self.skull_items = [inventory.BasicItem(f"Skull{i}") for i in range(1, 5)]
        for index, button in enumerate(self.children[:-1]):
            skull_parts = self.skull_items[index].item_name.split()
            button.label = f"{skull_parts[0]}"
            button.emoji = self.skull_items[index].item_emoji

    async def handle_skull_interaction(self, interaction_obj, item):
        if interaction_obj.user.id != self.player_obj.discord_id:
            return
        if self.new_embed is not None:
            await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)
        await self.player_obj.reload_player()
        self.new_embed = discord.Embed(colour=discord.Colour.dark_purple(), title=thana_title, description="")
        self.new_view = SkullsView(self.player_obj, method=self.method)
        skull_stock = await inventory.check_stock(self.player_obj, item.item_id)
        # Ring upgrading
        if self.method == "Sacrifice":
            ring_id = self.player_obj.player_equipped[4]
            e_ring = await inventory.read_custom_item(ring_id) if ring_id != 0 else None
            if e_ring is None or e_ring.item_base_type != "Crown of Skulls":
                self.new_embed.description = "Put the ring back on or I will *END* you. Okay darling?"
                await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)
                return
            if skull_stock <= 0:
                self.new_embed = await e_ring.create_citem_embed()
                self.new_embed = await add_skull_fields(self.player_obj, self.new_embed, self.method)
                stock_msg = sm.get_stock_msg(item, skull_stock)
                self.new_embed.add_field(name="", value=stock_msg, inline=False)
                await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)
                return
            await inventory.update_stock(self.player_obj, item.item_id, -1)
            e_ring.roll_values[0] = str(int(e_ring.roll_values[0]) + item.item_base_rate)
            await e_ring.update_stored_item()
            self.new_embed = await e_ring.create_citem_embed()
            self.new_embed = await add_skull_fields(self.player_obj, self.new_embed, self.method)
            await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)
        # Buy skulls
        elif self.method == "Purchase":
            if self.player_obj.player_coins <= item.item_cost:
                self.new_embed.description = "You'll need more coins than that to convince me to part with these."
                self.new_embed = await add_skull_fields(self.player_obj, self.new_embed, method=self.method)
                await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)
                return
            _ = await self.player_obj.adjust_coins(item.item_cost, reduction=True)
            self.new_embed.description = (f"Alright, please take good care of it. Each one is precious to me.\n"
                                          f"Thana hands you a valuable item: {item.item_emoji} 1x {item.item_name}")
            self.new_embed = await add_skull_fields(self.player_obj, self.new_embed, method=self.method)
            await inventory.update_stock(self.player_obj, item.item_id, 1)
            await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)
        # Sell skulls
        elif self.method == "Return":
            if skull_stock <= 0:
                self.new_embed.description = ("Stop messing around, I might get the wrong idea. "
                                              "Or... is there actually another reason that you called for me?\n")
                self.new_embed.description += sm.get_stock_msg(item, skull_stock)
                self.new_embed = await add_skull_fields(self.player_obj, self.new_embed, method=self.method)
                await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)
                return
            await inventory.update_stock(self.player_obj, item.item_id, -1)
            coin_msg = await self.player_obj.adjust_coins(item.item_cost // 2, apply_pact=False)
            self.new_embed.description = (f"Thank you for bringing him home. As promised here's your reward.\n"
                                          f"Thana hands you {gli.coin_icon} {coin_msg} Lotus Coins")
            self.new_embed = await add_skull_fields(self.player_obj, self.new_embed, method=self.method)
            await interaction_obj.response.edit_message(embed=self.new_embed, view=self.new_view)

    @discord.ui.button(label="Skull1", style=discord.ButtonStyle.blurple, row=0)
    async def skull1_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_skull_interaction(interaction, self.skull_items[0])

    @discord.ui.button(label="Skull2", style=discord.ButtonStyle.blurple, row=0)
    async def skull2_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_skull_interaction(interaction, self.skull_items[1])

    @discord.ui.button(label="Skull3", style=discord.ButtonStyle.blurple, row=0)
    async def skull3_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_skull_interaction(interaction, self.skull_items[2])

    @discord.ui.button(label="Skull4", style=discord.ButtonStyle.blurple, row=0)
    async def skull4_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_skull_interaction(interaction, self.skull_items[3])

    @discord.ui.button(label="Return", style=discord.ButtonStyle.blurple, row=0)
    async def return_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_obj.discord_id:
            return
        player_deaths = int(await self.player_obj.check_misc_data('deaths'))
        description = (f"I will continue to revive your mortal body so long as you continue to aid me. "
                       f"Though, should you ever want to remain dead you are more than welcome to stay by my side. "
                       f"You've died {player_deaths} times you know. It'd save me quite the hassle. "
                       f"I must confess, the mere thought of my sister's jealousy, every time you call my name "
                       f"fills me with immeasurable pleasure.\n")
        name, value = "", "Out with it now, what can the embodiment of death do for you today?"
        embed_msg = discord.Embed(colour=discord.Colour.dark_purple(), title=thana_title, description=description)
        embed_msg.add_field(name=name, value=value, inline=False)
        embed_msg.set_image(url=f"{gli.web_gallery_url}Tarot/Arbiter/XIII - Thana, The Death.webp")
        skull_ring = False
        if self.player_obj.player_equipped[4] != 0:
            e_ring = await inventory.read_custom_item(self.player_obj.player_equipped[4])
            if e_ring.item_base_type == "Crown of Skulls":
                skull_ring = True
        await interaction.response.edit_message(embed=embed_msg, view=SkullSelectView(self.player_obj, skull_ring))


class InlaySelectView(discord.ui.View):
    def __init__(self, player_user, gem_id):
        super().__init__(timeout=None)
        self.player_user, self.gem_id = player_user, gem_id
        gear_types = [geartype for geartype in gli.gear_types if geartype != "Gem"]
        gear_icons = [icon for icon in gli.gear_icons if "Gem" not in icon]
        options = [discord.SelectOption(
            emoji=icon, label=label, value=f"{idx}", description=f"Inlay gem in your {label.lower()}")
            for idx, (label, icon) in enumerate(zip(gear_types, gear_icons))]
        self.select_menu = discord.ui.Select(placeholder="Select an item!", min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.inlay_select_callback
        self.add_item(self.select_menu)

    async def inlay_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_user.discord_id:
            return
        selected_type = int(interaction.data['values'][0])
        # Set default embed.
        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                  title="Inlay Failed.", description="No item equipped in this slot")
        await self.player_user.reload_player()
        # Confirm an item is equipped in the selected slot.
        if self.player_user.player_equipped[selected_type] == 0:
            await interaction.response.edit_message(embed=embed_msg)
            return
        e_item, gem_item = await asyncio.gather(
            inventory.read_custom_item(self.player_user.player_equipped[selected_type]),
            inventory.read_custom_item(self.gem_id))
        if e_item is None or gem_item is None:
            embed_msg.description = "Cannot load items."
            await interaction.response.edit_message(embed=embed_msg)
            return
        # Confirm the item has sockets available.
        if e_item.item_num_sockets != 1:
            embed_msg.description = "The equipped item has no available sockets."
            await interaction.response.edit_message(embed=embed_msg)
            return
        # Confirm the tier is eligible
        if e_item.item_tier < gem_item.item_tier:
            embed_msg.description = "Gem must be inlaid in an equal or higher tier item."
            await interaction.response.edit_message(embed=embed_msg)
            return
        # Display confirmation menu.
        embed_msg = await e_item.create_citem_embed()
        confirm_view = ConfirmInlayView(self.player_user, e_item, self.gem_id)
        await interaction.response.edit_message(embed=embed_msg, view=confirm_view)


class ConfirmInlayView(discord.ui.View):
    def __init__(self, player_user, e_item, gem_id):
        super().__init__(timeout=None)
        self.e_item, self.player_user, self.gem_id = e_item, player_user,  gem_id

    @discord.ui.button(label="Inlay Gem", style=discord.ButtonStyle.success, emoji="✅")
    async def tier_one_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        if not await inventory.if_custom_exists(self.e_item.item_id):
            embed_msg = await self.e_item.create_citem_embed()
            embed_msg.add_field(name="Inlay Failed!", value=f"Item with id {self.e_item.item_id}", inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=None)
            return
        if not await inventory.if_custom_exists(self.gem_id):
            embed_msg = await self.e_item.create_citem_embed()
            embed_msg.add_field(name="Inlay Failed!", value=f"Item with id {self.gem_id}", inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=None)
            return
        # Update the inlaid gem and re-display the item.
        self.e_item.item_inlaid_gem_id = self.gem_id
        await self.e_item.update_stored_item()
        embed_msg = await self.e_item.create_citem_embed()
        await interaction.response.edit_message(embed=embed_msg, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        await interaction.response.edit_message(view=None)


class StaminaView(discord.ui.View):
    def __init__(self, ctx_obj, player_user, mode="Basic"):
        super().__init__(timeout=None)
        self.ctx_obj, self.player, self.mode = ctx_obj, player_user, mode
        if mode != "Basic":
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    if "Potion" in child.label:
                        child.style = discord.ButtonStyle.blurple
                        child.emoji = gli.exp_icon
                    else:
                        child.emoji = gli.stamina_icon
                        child.label = "Return"

    @discord.ui.button(label="Lesser Potion", style=discord.ButtonStyle.success, emoji=gli.stamina_icon, row=1)
    async def t1_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 1, 500)

    @discord.ui.button(label="Standard Potion", style=discord.ButtonStyle.success, emoji=gli.stamina_icon, row=1)
    async def t2_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 2, 1000)

    @discord.ui.button(label="Greater Potion", style=discord.ButtonStyle.success, emoji=gli.stamina_icon, row=2)
    async def t3_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 3, 2500)

    @discord.ui.button(label="Ultimate Potion", style=discord.ButtonStyle.success, emoji=gli.stamina_icon, row=2)
    async def t4_stamina_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.drink_potion(interaction, 4, 5000)

    @discord.ui.button(label="EXP Transmutation", style=discord.ButtonStyle.red, emoji=gli.exp_icon, row=3)
    async def transmute_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player.discord_id:
            return
        await self.player.reload_player()
        stamina_embed = await self.player.create_stamina_embed()
        new_mode = "Basic"
        if self.mode == "Basic":
            new_mode = "EXP"
            description = "Potions will be consumed at 10x the rate, to grant EXP instead of stamina."
            stamina_embed.add_field(name="EXP Transmutation", value=description, inline=False)
        new_view = StaminaView(self.ctx_obj, self.player, new_mode)
        await interaction.response.edit_message(embed=stamina_embed, view=new_view)

    async def drink_potion(self, interaction, potion_version, potion_value):
        if interaction.user.id != self.player.discord_id:
            return
        await self.player.reload_player()
        embed_msg, lvl_change = await self.use_stamina_potion(f"Potion{potion_version}", potion_value)
        await interaction.response.edit_message(embed=embed_msg)
        if lvl_change == 0:
            return
        await sm.send_notification(self.ctx_obj, self.player, "Level", lvl_change)

    async def use_stamina_potion(self, item_id, restore_amount):
        potion_stock = await inventory.check_stock(self.player, item_id)
        if potion_stock > 0 or (potion_stock >= 10 and self.mode != "Basic"):
            pact_object = pact.Pact(self.player.pact)
            max_stamina = 5000 if pact_object.pact_variant != "Sloth" else 2500
            await inventory.update_stock(self.player, item_id, (-1 if self.mode == "Basic" else -10))
            if self.mode != "Basic":
                exp_message, lvl_change = await self.player.adjust_exp(restore_amount)
                embed_msg = await self.player.create_stamina_embed()
                embed_msg.add_field(name="", value=f"{gli.exp_icon} {exp_message} Exp Acquired.", inline=False)
                return embed_msg, lvl_change
            self.player.player_stamina += restore_amount
            if self.player.player_stamina > max_stamina:
                self.player.player_stamina = max_stamina
            await self.player.set_player_field("player_stamina", self.player.player_stamina)
        embed_msg = await self.player.create_stamina_embed()
        return embed_msg, 0


gear_button_list = ["Weapon", "Armour", "Greaves", "Amulet", "Ring", "Wing", "Crest", "Pact", "Insignia", "Tarot"]


class GearView(discord.ui.View):
    def __init__(self, player_user, target_user, current_position, view_type):
        super().__init__(timeout=None)
        self.player_user, self.target_user = player_user, target_user
        self.new_embed, self.new_view, self.view_type = None, None, view_type
        self.current_position = current_position
        self.previous_button.label, self.next_button.label = self.get_positional_label(-1), self.get_positional_label(1)

        if self.current_position <= 6:
            toggle_type = "Gem" if self.view_type == "Gear" else "Gear"
            self.toggle_view_button.label = f"Toggle View ({toggle_type})"
        else:
            self.remove_item(self.children[1])

    def get_positional_label(self, direction):
        max_position = 9 if self.view_type == "Gear" else 6
        new_position = (self.current_position + direction) % (max_position + 1)
        button_label = gear_button_list[new_position]
        return f"{button_label} Gem" if self.view_type == "Gem" else button_label

    async def cycle_gear(self, direction):
        await self.target_user.reload_player()
        max_position = 9 if self.view_type == "Gear" else 6
        self.current_position = (self.current_position + direction) % (max_position + 1)
        # Build no item return message
        item_type = gear_button_list[self.current_position]
        no_item = item_type.lower()
        gem_msg = "" if self.view_type == "Gear" else " Gem"
        title, description = f"Equipped {item_type}{gem_msg}", f"No {no_item}{gem_msg.lower()} is equipped"
        no_item_msg = sm.easy_embed("gray", title, description)
        # Handle gear positions.
        if self.current_position <= 6:
            item_type = inventory.item_type_dict[self.current_position]
            selected_id = self.target_user.player_equipped[self.current_position]
            if selected_id is None or selected_id == 0:
                return no_item_msg
            # Handle the view variations.
            equipped_item = await inventory.read_custom_item(selected_id)
            if self.view_type == "Gem":
                if equipped_item.item_inlaid_gem_id == 0:
                    return no_item_msg
                equipped_gem = await inventory.read_custom_item(equipped_item.item_inlaid_gem_id)
                return await equipped_gem.create_citem_embed()
            return await equipped_item.create_citem_embed()
        # Handle tarot position.
        elif self.current_position == 9:
            tarot_item = self.target_user.equipped_tarot
            if tarot_item == "":
                return no_item_msg
            card_obj = await tarot.check_tarot(self.target_user.player_id, tarot.card_dict[self.target_user.equipped_tarot][0])
            return await card_obj.create_tarot_embed()
        # Handle insignia position.
        if self.current_position == 8:
            insignia_item = self.target_user.insignia
            if insignia_item == "":
                return no_item_msg
            insignia_obj = insignia.Insignia(self.target_user, insignia_code=insignia_item)
            return insignia_obj.insignia_output
        # Handle pact position.
        if self.current_position == 7:
            if self.target_user.pact == "":
                return no_item_msg
            return pact.display_pact(self.target_user)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id and interaction.user.id != self.target_user.discord_id:
            return
        if self.new_embed is not None:
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        self.new_embed = await self.cycle_gear(-1)
        self.new_view = GearView(self.player_user, self.target_user, self.current_position, self.view_type)
        await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def toggle_view_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id and interaction.user.id != self.target_user.discord_id:
            return
        if self.new_embed is not None:
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        self.view_type = "Gear" if self.view_type == "Gem" else "Gem"
        self.new_embed = await self.cycle_gear(0)
        self.new_view = GearView(self.player_user, self.target_user, self.current_position, self.view_type)
        await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id and interaction.user.id != self.target_user.discord_id:
            return
        if self.new_embed is not None:
            await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)
            return
        self.new_embed = await self.cycle_gear(1)
        self.new_view = GearView(self.player_user, self.target_user, self.current_position, self.view_type)
        await interaction.response.edit_message(embed=self.new_embed, view=self.new_view)


class ManageCustomItemView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user, self.selected_item = player_user, selected_item
        if "D" in self.selected_item.item_type:
            self.equip_item.label, self.equip_item.emoji = "Inlay", "🔱"
        self.stored_embed = None

    @discord.ui.button(label="Equip", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def equip_item(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            new_msg = await self.selected_item.create_citem_embed()
            if "D" in self.selected_item.item_type:
                new_view = InlaySelectView(self.player_user, self.selected_item.item_id)
                await interaction.response.edit_message(view=new_view)
            else:
                response = await self.player_user.equip(self.selected_item)
                new_msg.add_field(name=response, value="", inline=False)
                await interaction.response.edit_message(embed=new_msg, view=None)

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.success, emoji="💲")
    async def sell_item(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            selected_item = await inventory.read_custom_item(self.selected_item.item_id)
            if not self.stored_embed:
                if selected_item.player_owner == self.player_user.player_id:
                    embed_msg = await selected_item.create_citem_embed()
                    new_embed = await inventory.sell(self.player_user, selected_item, embed_msg)
                    self.stored_embed = new_embed
                else:
                    new_embed = await selected_item.create_citem_embed()
                    new_embed.add_field(name="Cannot Sell Item!",
                                        value="Item is not owned or currently listed on the bazaar.", inline=False)
            else:
                new_embed = self.stored_embed
            await interaction.response.edit_message(embed=new_embed, view=None)


class TermsOfServiceView(discord.ui.View):
    def __init__(self, discord_id, username):
        super().__init__(timeout=None)
        self.username, self.discord_id = username, discord_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_tos(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.discord_id:
            return
        title = "Register - Select Class"
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title=title, description=questdata.reg_msg)
        embed_msg.set_image(url="https://www.pandoraportal.ca/gallery/Displays/Banners/Pandora%20Awoken.png")
        await interaction.response.edit_message(embed=embed_msg, view=ClassSelect(self.discord_id, self.username))

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny_tos(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.discord_id:
            return
        await interaction.response.edit_message(view=None)


class ClassSelect(discord.ui.View):
    def __init__(self, discord_id, username):
        super().__init__(timeout=None)
        self.username, self.discord_id = username, discord_id
        descriptor = ["Valiant", "Precise", "Arcane", "Stealthy", "Mysterious", "Mounted", "Trusted"]
        opt = [discord.SelectOption(
            emoji=gli.class_icon_list[idx], label=class_name, description=f"The {descriptor[idx]} {class_name}"
        ) for idx, class_name in enumerate(gli.class_names)]
        self.select_menu = discord.ui.Select(placeholder="Select a class!", min_values=1, max_values=1, options=opt)
        self.select_menu.callback = self.class_callback
        self.add_item(self.select_menu)

    async def class_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.discord_id:
            return
        new_player = player.PlayerProfile()
        new_player.player_username = self.username
        chosen_class = interaction.data['values'][0]
        msg = await new_player.add_new_player(chosen_class, interaction.user.id)
        chosen_class_role = f"Class Role - {chosen_class}"
        add_role = discord.utils.get(interaction.guild.roles, name=chosen_class_role)
        remove_role = discord.utils.get(interaction.guild.roles, name="Class Role - Rat")
        await interaction.user.add_roles(add_role)
        await asyncio.sleep(1)
        await interaction.user.remove_roles(remove_role)
        embed_msg = discord.Embed(colour=discord.Colour.dark_teal(), title="Registration Complete!", description=msg)
        await interaction.response.edit_message(embed=embed_msg, view=None)


class ClassChangeView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.embed = False

    @discord.ui.select(
        placeholder="Select a new class!", min_values=1, max_values=1,
        options=[
            discord.SelectOption(
                emoji=gli.class_icon_list[0], label="Knight", description="The Valiant Knight"),
            discord.SelectOption(
                emoji=gli.class_icon_list[1], label="Ranger", description="The Precise Ranger"),
            discord.SelectOption(
                emoji=gli.class_icon_list[2], label="Mage", description="The Arcane Mage"),
            discord.SelectOption(
                emoji=gli.class_icon_list[3], label="Assassin", description="The Stealthy Assassin"),
            discord.SelectOption(
                emoji=gli.class_icon_list[4], label="Weaver", description="The Mysterious Weaver"),
            discord.SelectOption(
                emoji=gli.class_icon_list[5], label="Rider", description="The Mounted Rider"),
            discord.SelectOption(
                emoji=gli.class_icon_list[6], label="Summoner", description="The Trusted Summoner")
        ]
    )
    async def change_callback(self, interaction: discord.Interaction, class_select: discord.ui.Select):
        if interaction.user.id != self.player_obj.discord_id:
            return
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=None)
            return
        await self.player_obj.reload_player()
        current_class = self.player_obj.player_class
        chosen_class = class_select.values[0]
        token_stock = await inventory.check_stock(self.player_obj, "Token1")
        if token_stock >= 50:
            token_stock = await inventory.update_stock(self.player_obj, "Token1", -50)
            await self.player_obj.set_player_field("player_class", chosen_class)
            add_role = discord.utils.get(interaction.guild.roles, name=f"Class Role - {chosen_class}")
            remove_role = discord.utils.get(interaction.guild.roles, name=f"Class Role - {current_class}")
            await interaction.user.add_roles(add_role)
            await asyncio.sleep(1)
            await interaction.user.remove_roles(remove_role)
            response = f"{self.player_obj.player_username} you are a {chosen_class} now."
        else:
            response = "Not enough tokens. I refuse."
        self.embed = discord.Embed(colour=discord.Colour.dark_teal(),
                                   title="Mysmir, The Changer", description=response)
        await interaction.response.edit_message(embed=self.embed, view=None)


class StatView(discord.ui.View):
    def __init__(self, player_user, target_user):
        super().__init__(timeout=None)
        self.player_user, self.target_user = player_user, target_user

    @discord.ui.button(label="Offence", style=discord.ButtonStyle.blurple, row=1)
    async def offensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(1)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Defence", style=discord.ButtonStyle.blurple, row=1)
    async def defensive_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(3)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Details", style=discord.ButtonStyle.blurple, row=1)
    async def breakdown(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(2)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Application", style=discord.ButtonStyle.blurple, row=1)
    async def appli_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(4)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Points", style=discord.ButtonStyle.blurple, row=2)
    async def bonus_stats(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(5)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Glyphs", style=discord.ButtonStyle.blurple, row=2)
    async def glyphs(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(6)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Misc", style=discord.ButtonStyle.blurple, row=2)
    async def misc(self, interaction: discord.Interaction, button: discord.Button):
        new_msg = await self.target_user.get_player_stats(7)
        await interaction.response.edit_message(embed=new_msg)

    @discord.ui.button(label="Webpage", style=discord.ButtonStyle.success, row=2)
    async def webpage(self, interaction: discord.Interaction, button: discord.Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        link_message = f"https://pandoraportal.ca/characters.php?search_input={self.target_user.player_id}"
        await interaction.followup.send(link_message)


class BuyView(discord.ui.View):
    def __init__(self, player_user, selected_item):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.selected_item = selected_item

    @discord.ui.button(label="Confirm Purchase", style=discord.ButtonStyle.success, emoji="⚔️")
    async def confirm(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                if self.selected_item.player_owner == -1:
                    # COMBINE LATER
                    item_cost = await bazaar.get_item_cost(self.selected_item.item_id)
                    seller_id = await bazaar.get_seller_by_item(self.selected_item.item_id)
                    display_msg = "Cannot Purchase!"
                    if self.player_user.player_coins >= item_cost and self.player_user.player_id != seller_id:
                        # Process purchase
                        await bazaar.buy_item(self.player_user, self.selected_item.item_id, item_cost, seller_id)
                        self.selected_item.player_owner = self.player_user.player_id
                        await self.selected_item.update_stored_item()
                        display_msg = "PURCHASE COMPLETED!"
                embed_msg = await self.selected_item.create_citem_embed()
                embed_msg.add_field(name=display_msg, value="", inline=False)
                await interaction.response.edit_message(embed=embed_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                await interaction.response.edit_message(view=None)
        except Exception as e:
            print(e)


class PointsView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__()
        self.path_names = gli.path_names
        self.player_obj = player_obj
        icon_strings = [", ".join(gli.element_names[idx] for idx in gli.element_dict[path.split()[0]])
                        for path in gli.path_names if path.split()[0] in gli.element_dict]
        icon_strings[8] = f"Multi Element"
        # Build the option menu dynamically based on recipe categories.
        opt = [discord.SelectOption(
            emoji=gli.path_icon[idx], label=f"Path of {path_name}", description=icon_strings[idx]
            ) for idx, path_name in enumerate(gli.path_names)]
        opt.append(discord.SelectOption(emoji="✖️", label="Reset", description="Reset all skill points"))
        self.select_menu = discord.ui.Select(placeholder="Select a Path", min_values=1, max_values=1, options=opt)
        self.select_menu.callback = self.path_select_callback
        self.add_item(self.select_menu)

    async def path_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.player_obj.discord_id:
            await self.player_obj.reload_player()
            selected_path = interaction.data['values'][0]
            if selected_path == "Reset":
                token_obj = inventory.BasicItem("Token3")
                token_cost = sum(self.player_obj.player_stats) // 10
                token_stock = await inventory.check_stock(self.player_obj, "Token3")
                response = (f"The farther you walk your path, the harder it is to change what you've become.\nReset Cost:\n "
                            f"{token_obj.item_emoji} {token_obj.item_name}: {token_stock} / {token_cost}")
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Avalon, The Pathwalker",
                                          description=response)
                new_view = ResetView(self.player_obj)
            else:
                embed_msg = await skillpaths.build_points_embed(self.player_obj, selected_path)
                new_view = PointsMenu(self.player_obj, selected_path)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)


class PointsMenu(discord.ui.View):
    def __init__(self, player_obj, selected_path):
        super().__init__()
        self.player_obj = player_obj
        self.selected_path = selected_path
        self.embed_msg = None
        self.view = None

    @discord.ui.button(emoji="1️⃣", label="Allocate 1", style=discord.ButtonStyle.primary)
    async def add_one_point(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.allocate_callback(1)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    @discord.ui.button(emoji="5️⃣", label="Allocate 5", style=discord.ButtonStyle.primary)
    async def add_five_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.allocate_callback(5)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    @discord.ui.button(emoji="🔟", label="Allocate 10", style=discord.ButtonStyle.primary)
    async def add_ten_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.allocate_callback(10)
            await interaction.response.edit_message(embed=self.embed_msg, view=self.view)

    async def allocate_callback(self, num_points):
        if not self.embed_msg:
            await self.player_obj.reload_player()
            response = await skillpaths.allocate_points(self.player_obj, self.selected_path, num_points)
            self.embed_msg = await skillpaths.build_points_embed(self.player_obj, self.selected_path)
            self.embed_msg.add_field(name="", value=response, inline=False)
            self.view = PointsMenu(self.player_obj, self.selected_path)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.secondary)
    async def reselect_path_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.player_obj.reload_player()
            embed_msg = await skillpaths.create_path_embed(self.player_obj)
            points_view = PointsView(self.player_obj)
            await interaction.response.edit_message(embed=embed_msg, view=points_view)


class ResetView(discord.ui.View):
    def __init__(self, player_obj):
        super().__init__()
        self.player_obj = player_obj
        self.embed_msg = None

    @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            if not self.embed_msg:
                await self.player_obj.reload_player()
                token_cost = sum(self.player_obj.player_stats) // 10
                token_stock = await inventory.check_stock(self.player_obj, "Token3")
                if token_stock >= token_cost:
                    await inventory.update_stock(self.player_obj, "Token3", -1)
                    await self.player_obj.reset_skill_points()
                    result_msg = "ALL SKILL POINTS RESET!"
                else:
                    result_msg = "Come back when you have a token."
                await self.player_obj.reload_player()
                self.embed_msg = await skillpaths.create_path_embed(self.player_obj)
                self.embed_msg.add_field(name=result_msg, value="", inline=False)
            points_view = PointsView(self.player_obj)
            await interaction.response.edit_message(embed=self.embed_msg, view=points_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.secondary)
    async def reselect_path_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player_obj.discord_id:
            await self.player_obj.reload_player()
            embed_msg = await skillpaths.create_path_embed(self.player_obj)
            points_view = PointsView(self.player_obj)
            if self.embed_msg:
                embed_msg.add_field(name="ALL SKILL POINTS RESET!", value="", inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=points_view)
