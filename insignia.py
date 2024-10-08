# General imports
import discord
import random
from functools import reduce

# Data imports
import globalitems as gli
import sharedmethods as sm

# Core imports
import player
import inventory

# Item/crafting imports
import itemrolls
import loot

insignia_name_list = [None, "Monolith", "Dyadic", "Trinity", "Tetradic", "Pentagram",
                      None, None, None, "Refraction"]
insignia_description_list = [None, "One element: ", "Two elements: ", "Three elements: ",
                             "Four elements: ", "Five elements: ", None, None, None, "All elements: "]
insignia_multipliers = [[0, 0], [150, 25], [75, 25], [50, 25], [75, 10], [50, 10], [0, 0], [0, 0], [0, 0], [25, 10]]
insignia_hp_list = [0, 750, 1500, 2500, 5000, 7500, 10000, 15000, 25000, 50000]
insignia_damage = [0, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 750000, 1000000]
mutation_upgrade_data = {0: [5, 50], 1: [10, 25], 2: [20, 99], 3: [30, 100]}
insignia_prefix = ["Dormant", "Awakened", "Evolved", "Infused", "Symbiotic", "Resonating",
                   "Mutation: Wish", "Mutation: Abyss", "Mutation: Divine", "Mutation: Sacred"]
mutation_cost_list = ["Crystal2", "Crystal3", "Lotus8", "Sacred"]
NPC_name = "Isolde, The Soulweaver"


class Insignia:
    def __init__(self, player_obj, insignia_code=None):
        # Initializations.
        self.player_obj = player_obj
        self.insignia_code = player_obj.insignia if insignia_code is None else insignia_code
        temp_code = self.insignia_code.split(";")
        temp_elements, self.mutation_tier = temp_code[:9], int(temp_code[-1])
        mutation_adjust = max(1, self.mutation_tier)
        self.element_list = list(map(int, temp_elements))
        self.num_elements = self.element_list.count(1)
        echelon = self.player_obj.player_echelon
        self.stars = check_tier(self.player_obj.player_echelon, self.mutation_tier)
        _, pearl = sm.get_gear_tier_colours(self.stars)
        # Stats
        hp_bonus, luck_bonus = insignia_hp_list[self.stars], self.stars
        final_damage, attack_speed = self.player_obj.player_level * mutation_adjust, self.stars * 5
        self.insignia_damage = insignia_damage[self.stars]
        self.bonus_stats = {'hp_bonus': hp_bonus, 'luck_bonus': luck_bonus,
                            'final_damage': final_damage * 0.01, 'attack_speed': attack_speed * 0.01}
        # Build output.
        item_rolls = f"{pearl} HP Bonus +{hp_bonus:,}\n{pearl} Luck +{luck_bonus}"
        item_rolls += f"\n{pearl} Final Damage {final_damage:,}%\n{pearl} Attack Speed {attack_speed}%"
        self.name = f"{insignia_name_list[self.num_elements]} Insignia [{insignia_prefix[self.stars]}]"
        self.pen = insignia_multipliers[self.num_elements][0]
        self.pen += insignia_multipliers[self.num_elements][1] * self.stars * mutation_adjust
        element_icons = ""
        if self.num_elements == 9:
            icon_list = gli.omni_icon
            item_rolls += f"\n{pearl} Omni Penetration {self.pen:,}%"
        else:
            selected_elements_list = [ind for ind, x in enumerate(self.element_list) if x == 1]
            for y in selected_elements_list:
                element_icons += gli.ele_icon[y]
                item_rolls += f"\n{pearl} {gli.element_names[y]} Penetration {self.pen:,}%"
        damage_details = f"Base Damage: {self.insignia_damage:,} - {self.insignia_damage:,}"
        self.insignia_output = sm.easy_embed(self.stars, self.name, sm.display_stars(self.stars))
        self.insignia_output.add_field(name=element_icons, value=damage_details, inline=False)
        self.insignia_output.add_field(name="Insignia Bonus", value=item_rolls, inline=False)
        self.insignia_output.set_thumbnail(url=f"{gli.frame_icon_list[self.stars - 1].replace('[EXT]', gli.frame_extension[0])}")


def check_tier(echelon, mutation_tier):
    return 1 + (echelon >= 5) + (echelon >= 7) + (echelon >= 8) + (echelon >= 9) + mutation_tier


class InsigniaView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

        insignia_options = [(index, name, description, values) for index, (name, description, values) in
                            enumerate(zip(insignia_name_list, insignia_description_list, insignia_multipliers))
                            if name is not None and values[0] != 0]
        options = [discord.SelectOption(
            emoji="<a:eenergy:1145534127349706772>", label=f"{name} Insignia", value=f"{index}",
            description=f"{description} (Base: {values[0]}%) (Scaling: {values[1]}%)")
            for index, name, description, values in insignia_options]
        custom_option = discord.SelectOption(emoji="<a:eenergy:1145534127349706772>", label="Mutation",
                                             value="10", description="Mutate an insignia")
        options.append(custom_option)
        self.select_menu = discord.ui.Select(placeholder="Select an insignia type.",
                                             min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.insignia_select_callback
        self.add_item(self.select_menu)

    async def insignia_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_user.discord_id:
            return
        num_elements = int(interaction.data['values'][0])
        token_item = inventory.BasicItem("Token2")
        embed_msg = sm.easy_embed("green", NPC_name, "")
        # Proceed to element selection for regular options.
        if num_elements < 9:
            current_selection, num_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0], 0
            new_view = ElementSelectView(self.player_user, num_elements, num_selected, current_selection)
            embed_msg.description = "What is the desired affinity?"
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
            return
        # Proceed directly to confirmation for omni option.
        if num_elements == 9:
            current_selection, num_selected = [1, 1, 1, 1, 1, 1, 1, 1, 1], 9
            new_view = ConfirmSelectionView(self.player_user, num_selected, current_selection)
            embed_msg.description = ("I applaud your greed. In addition to the payment I hope your "
                                     "sanity can afford the cost.")
            cost_msg = await payment_embed(self.player_user, num_elements, current_selection)
            embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
            return
        # Confirm eligibility for mutation
        if self.player_user.insignia == "" or self.player_user.player_echelon < 10:
            embed_msg.description = "Sweetie you'll break if I do that. Maybe get a bit stronger first?"
            await interaction.response.edit_message(embed=embed_msg)
            return
        # Determine mutation cost and proceed to confirmation.
        mutation_tier = int(self.player_user.insignia[-1])
        embed_msg.description = "Do you not value the sanctity of your soul?"
        if mutation_tier in mutation_upgrade_data:
            token_cost = mutation_upgrade_data[mutation_tier][0]
            cost_msg = await payment_embed(self.player_user, token_cost, mutation_cost_list[mutation_tier])
            embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
            new_view = ConfirmSelectionView(self.player_user, 0, "mutation")
            await interaction.response.edit_message(embed=embed_msg, view=new_view)
            return
        embed_msg.description = "You seek the impossible, there's nothing else I can engrave on your soul."
        await interaction.response.edit_message(embed=embed_msg, view=self)


class ElementSelectView(discord.ui.View):
    def __init__(self, player_user, num_elements, num_selected, current_selection):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.num_elements, self.num_selected, self.current_selection = num_elements, num_selected, current_selection
        self.embed = None
        available_options = [
            (index, (name, emoji)) for index, (name, emoji, selection) in
            enumerate(zip(gli.element_names, gli.ele_icon, self.current_selection)) if selection != 1]
        options = [discord.SelectOption(emoji=emoji, label=option, value=str(i), description=f"{option} affinity")
                   for (i, (option, emoji)) in available_options]
        self.select_menu = discord.ui.Select(placeholder="Select the element add.",
                                             min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.element_select_callback
        self.add_item(self.select_menu)

    async def element_select_callback(self, interaction: discord.Interaction):
        base_embed = sm.easy_embed("green", NPC_name, "")
        if interaction.user.id != self.player_user.discord_id:
            return
        selected_element = int(interaction.data['values'][0])
        if self.embed is not None:
            await interaction.response.edit_message(embed=self.embed, view=new_view)
            return
        self.current_selection[selected_element] = 1
        num_selected = self.num_selected + 1
        self.embed = base_embed
        if num_selected == self.num_elements:
            new_view = ConfirmSelectionView(self.player_user, num_selected, self.current_selection)
            self.embed.description = ("How entertaining. I am willing to engrave your soul, "
                                      "but my services are as expensive as they are painful.")
            cost_msg = await payment_embed(self.player_user, self.num_elements, self.current_selection)
            self.embed.add_field(name="Cost:", value=cost_msg, inline=False)
            await interaction.response.edit_message(embed=self.embed, view=new_view)
            return
        new_view = ElementSelectView(self.player_user, self.num_elements, num_selected, self.current_selection)
        self.embed.description = "What is the next desired affinity?"
        await interaction.response.edit_message(embed=self.embed, view=new_view)


class ConfirmSelectionView(discord.ui.View):
    def __init__(self, player_user, num_selected, current_selection):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.num_selected, self.current_selection = num_selected, current_selection
        mutation_tier = int(self.player_user.insignia[-1]) if self.player_user.insignia != "" else 0
        self.mutation_rate = mutation_upgrade_data[mutation_tier][1]
        if self.current_selection == "mutation":
            if mutation_tier < 4:
                self.engrave.label = f"{insignia_prefix[(6 + mutation_tier)]} ({self.mutation_rate}%)"
            else:
                self.engrave.label = f"Mutation [MAX]"
                self.engrave.disabled = True
                self.engrave.style = discord.ButtonStyle.secondary
        self.embed_msg = None

    @discord.ui.button(label="Engrave", style=discord.ButtonStyle.success, emoji="🔯")
    async def engrave(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.player_user.discord_id:
            return
        if self.embed_msg is not None:
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        # Initialize the data.
        await self.player_user.reload_player()
        token_stock = await inventory.check_stock(self.player_user, "Token2")
        self.embed_msg = sm.easy_embed("green", NPC_name, "")
        # Handle regular engravings.
        if self.current_selection != "mutation":
            # Confirm the token cost can be paid.
            token_cost = self.num_selected
            if token_cost > token_stock:
                self.embed_msg.description = ("Such gall to request my services without a sufficient offering. "
                                              "Bring me tokens or don't come back.")
                await interaction.response.edit_message(embed=self.embed_msg, view=None)
                return
            # Confirm the material core cost can be paid.
            selected_elements_list = [ind for ind, y in enumerate(self.current_selection) if y == 1]
            for x in selected_elements_list:
                fae_check = await inventory.check_stock(self.player_user, f"Fae{x}")
                if fae_check < 100:
                    self.embed_msg.description = ("Weaving requires a lot of fae energy. "
                                                  "I'll need you to bring me more cores.")
                    await interaction.response.edit_message(embed=self.embed_msg, view=None)
                    return
            # Pay the costs and engrave the insignia.
            await inventory.update_stock(self.player_user, "Token2", (token_cost * -1))
            for z in selected_elements_list:
                await inventory.update_stock(self.player_user, f"Fae{z}", -100)
            delim = ";"
            insignia_code = reduce(lambda full, new: str(full) + delim + str(new), self.current_selection)
            insignia_code += ";0"
            insignia_obj = Insignia(self.player_user, insignia_code=insignia_code)
            self.embed_msg = insignia_obj.insignia_output
            await self.player_user.set_player_field("player_insignia", insignia_code)
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        # Reconfirm mutation eligibility.
        mutation_tier = int(self.player_user.insignia[-1])
        if mutation_tier >= 4:
            self.embed_msg.description = "There's nothing further I can do to improve your soul through mutation."
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        if self.player_user.player_echelon < 10:
            self.embed_msg.description = "There's nothing further I can do to improve your soul through mutation."
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        # Confirm the token cost can be paid.
        token_cost = mutation_upgrade_data[mutation_tier][0]
        if token_cost > token_stock:
            self.embed_msg.description = ("Such gall to request my services without a sufficient offering. "
                                          "Bring me tokens or don't come back.")
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        # Confirm the secondary cost can be paid.
        secondary_item = inventory.BasicItem(mutation_cost_list[mutation_tier])
        secondary_stock = await inventory.check_stock(self.player_user, secondary_item.item_id)
        if secondary_stock < 1:
            self.embed_msg.description = ("Such gall to request my services without a sufficient offering. "
                                          "Bring me tokens or don't come back.")
            await interaction.response.edit_message(embed=self.embed_msg, view=None)
            return
        # Pay the costs
        await inventory.update_stock(self.player_user, "Token2", (token_cost * -1))
        await inventory.update_stock(self.player_user, secondary_item.item_id, -1)
        # Handle unsuccessful mutation.
        if random.randint(1, 100) > self.mutation_rate:
            self.embed_msg.description = "The mutation failed, but I managed to keep your soul intact."
            cost_msg = await payment_embed(self.player_user, token_cost, mutation_cost_list[mutation_tier + 1])
            self.embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
            reload_view = ConfirmSelectionView(self.player_user, 0, "mutation")
            await interaction.response.edit_message(embed=self.embed_msg, view=reload_view)
            return
        # Handle the successful mutation.
        new_tier = int(self.player_user.insignia[-1]) + 1
        self.player_user.insignia = f"{self.player_user.insignia[:-1]}{new_tier}"
        await self.player_user.set_player_field("player_insignia", self.player_user.insignia)
        insignia_obj = Insignia(self.player_user)
        self.embed_msg = insignia_obj.insignia_output
        self.embed_msg.add_field(name=NPC_name, value="Mutation Successful!", inline=False)
        if new_tier != 4:
            cost_msg = await payment_embed(self.player_user, token_cost, mutation_cost_list[mutation_tier + 1])
            self.embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
        reload_view = ConfirmSelectionView(self.player_user, 0, "mutation")
        await interaction.response.edit_message(embed=self.embed_msg, view=reload_view)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.player_user.discord_id:
            engrave_msg = "My patience wears thin. Tell me, what kind of power do you seek?"
            embed_msg = sm.easy_embed("green", NPC_name, engrave_msg)
            new_view = InsigniaView(self.player_user)
            await interaction.response.edit_message(embed=embed_msg, view=new_view)


async def payment_embed(player_obj, token_cost, current_selection):
    token_item = inventory.BasicItem("Token2")
    token_stock = await inventory.check_stock(player_obj, token_item.item_id)
    cost_msg = f"{token_item.item_emoji} {token_item.item_name}: {token_stock} / {token_cost}\n"
    # Create non mutation cost message.
    if type(current_selection) is list:
        for idx, x in enumerate(current_selection):
            if x != 0:
                loot_item = inventory.BasicItem(f"Fae{idx}")
                stock = await inventory.check_stock(player_obj, loot_item.item_id)
                cost_msg += f"{loot_item.item_emoji} {loot_item.item_name}: {stock} / 100\n"
        return cost_msg
    # Create mutation cost message.
    secondary_item = inventory.BasicItem(current_selection)
    secondary_stock = await inventory.check_stock(player_obj, secondary_item.item_id)
    cost_msg += f"{secondary_item.item_emoji} {secondary_item.item_name}: {secondary_stock} / 1"
    return cost_msg


def assign_insignia_values(player_obj):
    if player_obj.insignia == "":
        return
    insignia_obj = Insignia(player_obj)
    # Apply bonus stats.
    player_obj.player_damage_min += insignia_obj.insignia_damage
    player_obj.player_damage_max += insignia_obj.insignia_damage
    player_obj.final_damage += insignia_obj.bonus_stats["final_damage"]
    player_obj.attack_speed += insignia_obj.bonus_stats["attack_speed"]
    player_obj.luck_bonus += insignia_obj.bonus_stats["luck_bonus"]
    player_obj.hp_bonus += insignia_obj.bonus_stats["hp_bonus"]
    # Apply Elemental Penetration
    adjusted_penetration = insignia_obj.pen * 0.01
    if insignia_obj.num_elements != 9:
        for y, has_element in enumerate(insignia_obj.element_list):
            if has_element:
                player_obj.elemental_pen[y] += adjusted_penetration
    else:
        player_obj.all_elemental_pen += adjusted_penetration
