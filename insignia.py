import loot
import inventory
import player
import pandorabot
import discord
import globalitems
from functools import reduce
insignia_prefix = ["Dormant", "Awoken", "Evolved", "Infused", "Symbiotic"]


def display_insignia(player_object, insignia_code, output_type):
    tier_colour, tier_icon = inventory.get_gear_tier_colours(player_object.player_echelon)
    hp_bonus = 500 * player_object.player_echelon
    item_rolls = f"+{hp_bonus} HP Bonus"
    item_rolls += f"\n{player_object.player_lvl}% Final Damage"
    item_rolls += f"\n{player_object.player_echelon * 10}% Attack Speed"
    temp_elements = insignia_code.split(";")
    element_list = list(map(int, temp_elements))
    num_elements = element_list.count(1)
    display_stars = ""
    for x in range(player_object.player_echelon):
        display_stars += globalitems.star_icon
    for y in range((5 - player_object.player_echelon)):
        display_stars += "<:ebstar2:1144826056222724106>"
        item_types = ""
    insignia_name = f"{insignia_prefix[player_object.player_echelon]} "
    match num_elements:
        case 1:
            insignia_name += "Monolith"
        case 2:
            insignia_name += "Dyadic"
        case 3:
            insignia_name += "Trinity"
        case 9:
            insignia_name += "Refraction"
            icon_list = globalitems.omni_icon
            bonus = 25 + 25 * player_object.player_echelon
            item_rolls += f"\n{int(bonus)}% Omni Penetration"
        case _:
            insignia_name = "ERROR"
    insignia_name += " Insignia"
    if num_elements != 9:
        selected_elements_list = [ind for ind, x in enumerate(element_list) if x == 1]
        bonus = 150 / num_elements + 25 * player_object.player_echelon
        for y in selected_elements_list:
            item_rolls += f"\n{int(bonus)}% {globalitems.element_names[y]} Penetration"
    if output_type == "Embed":
        insignia_output = discord.Embed(colour=tier_colour,
                                        title=insignia_name,
                                        description=display_stars)
        insignia_output.add_field(name="", value=item_rolls, inline=False)
    else:
        insignia_output = insignia_name
        insignia_output += f"\n{display_stars}"
        insignia_output += f"\n{item_rolls}"

    return insignia_output


class InsigniaView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

    @discord.ui.select(
        placeholder="Select an insignia type.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Monolith Insignia",
                value="1", description="One element. 150%"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Dyadic Insignia",
                value="2", description="Two elements. 75%"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Trinity Insignia",
                value="3", description="Three elements. 50%"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Refraction Insignia",
                value="9", description="All elements. 25%")
        ]
    )
    async def insignia_select_callback(self, interaction: discord.Interaction, insignia_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                num_elements = int(insignia_select.values[0])
                if num_elements != 9:
                    current_selection = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    num_selected = 0
                    new_view = ElementSelectView(self.player_user, num_elements, num_selected, current_selection)
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Weaver Lord, Isabelle",
                                              description="What is the desired affinity?")
                else:
                    current_selection = [1, 1, 1, 1, 1, 1, 1, 1, 1]
                    num_selected = 9
                    new_view = ConfirmSelectionView(self.player_user, num_selected, current_selection)
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Weaver Lord, Isabelle",
                                              description="I applaud your greed. In addition to the payment "
                                                          "I hope your sanity can afford the cost.")
                    cost = num_selected * 5000
                    cost_msg = f"{globalitems.coin_icon} {cost}x Lotus Coins\n"
                    fae_cost = payment_embed(current_selection)
                    cost_msg += fae_cost
                    embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class ElementSelectView(discord.ui.View):
    def __init__(self, player_user, num_elements, num_selected, current_selection):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.num_elements = num_elements
        self.num_selected = num_selected
        self.current_selection = current_selection

    @discord.ui.select(
        placeholder="Select an elemental affinity.",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Fire",
                value="0", description="Fire Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Water",
                value="1", description="Water Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Lighting",
                value="2", description="Lighting Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Earth",
                value="3", description="Earth Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Wind",
                value="4", description="Wind Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Ice",
                value="5", description="Ice Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Shadow",
                value="6", description="Shadow Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Light",
                value="7", description="Light Affinity"),
            discord.SelectOption(
                emoji="<a:eenergy:1145534127349706772>", label="Celestial",
                value="8", description="Celestial Affinity")
        ]
    )
    async def element_select_callback(self, interaction: discord.Interaction, element_select: discord.ui.Select):
        try:
            if interaction.user.name == self.player_user.player_name:
                selected_element = int(element_select.values[0])
                if self.current_selection[selected_element] == 1:
                    embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                              title="Weaver Lord, Isabelle",
                                              description="What are you playing at? You've already picked that one.")
                    new_view = self
                else:
                    current_selection = self.current_selection
                    current_selection[selected_element] = 1
                    num_selected = self.num_selected + 1
                    if num_selected == self.num_elements:
                        new_view = ConfirmSelectionView(self.player_user, num_selected, current_selection)
                        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                                  title="Weaver Lord, Isabelle",
                                                  description="How entertaining. I am willing to engrave your soul, "
                                                              "but my services are as expensive as they are painful.")
                        cost = num_selected * 10000
                        cost_msg = f"{globalitems.coin_icon} {cost}x Lotus Coins\n"
                        fae_cost = payment_embed(current_selection)
                        cost_msg += fae_cost
                        embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
                    else:
                        new_view = ElementSelectView(self.player_user, self.num_elements, num_selected, current_selection)
                        embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                                  title="Weaver Lord, Isabelle",
                                                  description="What is the next desired affinity?")
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


class ConfirmSelectionView(discord.ui.View):
    def __init__(self, player_user, num_selected, current_selection):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.num_selected = num_selected
        self.current_selection = current_selection
        self.embed_msg = None

    @discord.ui.button(label="Engrave", style=discord.ButtonStyle.success, emoji="🔯")
    async def engrave(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                if not self.embed_msg:
                    reload_player = player.get_player_by_id(self.player_user.player_id)
                    cannot_afford_description = ""
                    cost = self.num_selected * 10000
                    enough_fae = True
                    selected_elements_list = [ind for ind, y in enumerate(self.current_selection) if y == 1]
                    for x in selected_elements_list:
                        fae_id = f"Fae{x}"
                        fae_check = inventory.check_stock(reload_player, fae_id)
                        if fae_check < 50:
                            enough_fae = False
                    if cost <= reload_player.player_coins:
                        if enough_fae:
                            reload_player.player_coins -= cost
                            reload_player.set_player_field("player_coins", reload_player.player_coins)
                            for z in selected_elements_list:
                                fae_id = fae_id = f"Fae{z}"
                                inventory.update_stock(reload_player, fae_id, -50)
                            delim = ";"
                            insignia_code = reduce(lambda full, new: str(full) + delim + str(new), self.current_selection)
                            insignia_description = display_insignia(reload_player, insignia_code, "Description")
                            reload_player.set_player_field("player_equip_insignia", insignia_code)
                            embed_title = "Insignia Engraved!"
                            embed_description = f"Engraved {insignia_description}"
                            embed_description += f"\nRemaining lotus coins: {reload_player.player_coins}."
                            self.embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                                           title=embed_title,
                                                           description=embed_description)
                        else:
                            cannot_afford_description = ("Weaving requires a lot of fae energy. "
                                                         "I'll need you to bring me more cores.")
                    else:
                        cannot_afford_description = "I'm not going to work for free. Come back with more coins."
                    if cannot_afford_description != "":
                        self.embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                                       title="Weaver Lord, Isabelle",
                                                       description=cannot_afford_description)
                await interaction.response.edit_message(embed=self.embed_msg, view=None)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.name == self.player_user.player_name:
                engrave_msg = "My patience wears thin. Tell me, what kind of power do you seek?"
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Weaver Lord, Isabelle",
                                          description=engrave_msg)
                new_view = InsigniaView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


def payment_embed(current_selection):
    cost_msg = ""
    for idx, x in enumerate(current_selection):
        if x != 0:
            fae_id = f"Fae{idx}"
            loot_item = loot.BasicItem(fae_id)
            cost_msg += f"{loot_item.item_emoji} 50x {loot_item.item_name}\n"
    return cost_msg
