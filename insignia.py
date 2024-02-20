import itemrolls
import loot
import inventory
import player
import pandorabot
import discord
import random
import globalitems
from functools import reduce
insignia_name_list = [None, "Monolith", "Dyadic", "Trinity", "Tetradic", "Pentagram",
                      None, None, None, "Refraction"]
insignia_description_list = [None, "One element: ", "Two elements: ", "Three elements: ",
                             "Four elements: ", "Five elements: ", None, None, None, "All elements: "]
insignia_multiplier_list = [[0, 0], [150, 25], [75, 25], [50, 25], [75, 10], [50, 10], [0, 0], [0, 0], [0, 0], [25, 10]]
insignia_hp_list = [0, 500, 1000, 1500, 2000, 2500, 5000, 10000, 20000]
mutation_upgrade_data = {0: [5, 33], 1: [10, 11], 2: [50, 99]}
insignia_prefix = ["Dormant", "Awakened", "Evolved", "Infused", "Symbiotic", "Resonating",
                   "Mutation: Void", "Mutation: Wish", "Mutation: Divine"]
mutation_cost_list = ["OriginV", "OriginM", "Lotus7"]


def display_insignia(player_obj, insignia_code):
    # Extract insignia data
    temp_code = insignia_code.split(";")
    temp_elements, mutation_tier = temp_code[:9], int(temp_code[-1])
    insignia_stars = player_obj.player_echelon // 2 + mutation_tier
    mutation_adjust = max(1, mutation_tier)
    element_list = list(map(int, temp_elements))
    num_elements = element_list.count(1)

    # Build the stats message.
    tier_colour, pearl = sharedmethods.get_gear_tier_colours(player_obj.player_echelon // 2)
    hp_bonus = insignia_hp_list[insignia_stars]
    item_rolls = f"{pearl} HP Bonus +{hp_bonus:,}"
    item_rolls += f"\n{pearl} Luck +{insignia_stars}"
    item_rolls += f"\n{pearl} Final Damage {player_obj.player_lvl * mutation_adjust:,}%"
    item_rolls += f"\n{pearl} Attack Speed {insignia_stars * 10:,}%"

    # Build the embed message.
    display_stars = sharedmethods.display_stars(insignia_stars)
    insignia_name = f"{insignia_name_list[num_elements]} Insignia [{insignia_prefix[insignia_stars - 1]}]"
    bonus = insignia_multiplier_list[num_elements][0] + insignia_multiplier_list[num_elements][1] * insignia_stars
    if num_elements == 9:
        icon_list = globalitems.omni_icon
        item_rolls += f"\n{pearl} Omni Penetration {int(bonus) * mutation_adjust:,}%"
    else:
        selected_elements_list = [ind for ind, x in enumerate(element_list) if x == 1]
        for y in selected_elements_list:
            item_rolls += f"\n{pearl} {globalitems.element_names[y]} Penetration {int(bonus) * mutation_adjust:,}%"
    insignia_output = discord.Embed(colour=tier_colour, title=insignia_name, description=display_stars)
    insignia_output.add_field(name="", value=item_rolls, inline=False)
    return insignia_output


class InsigniaView(discord.ui.View):
    def __init__(self, player_user):
        super().__init__(timeout=None)
        self.player_user = player_user

        insignia_options = [(index, name, description, values) for index, (name, description, values) in
                            enumerate(zip(insignia_name_list, insignia_description_list, insignia_multiplier_list))
                            if name is not None and values[0] != 0]
        options = [discord.SelectOption(
            emoji="<a:eenergy:1145534127349706772>", label=f"{name} Insignia", value=f"{index}",
            description=f"{description} (Base: {values[0]}%) (Scaling: {values[1]}%)")
            for index, name, description, values in insignia_options
        ]
        custom_option = discord.SelectOption(emoji="<a:eenergy:1145534127349706772>", label="Mutation",
                                             value="10", description="Mutate an insignia")
        options.append(custom_option)
        self.select_menu = discord.ui.Select(placeholder="Select an insignia type.",
                                             min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.insignia_select_callback
        self.add_item(self.select_menu)

    async def insignia_select_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id == self.player_user.discord_id:
                num_elements = int(interaction.data['values'][0])
                token_item = inventory.BasicItem("Token2")
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Isolde, Soulweaver of the True Laws", description="")
                # Proceed to element selection for regular options.
                if num_elements < 9:
                    current_selection = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    num_selected = 0
                    new_view = ElementSelectView(self.player_user, num_elements, num_selected, current_selection)
                    embed_msg.description = "What is the desired affinity?"
                    await interaction.response.edit_message(embed=embed_msg, view=new_view)
                    return
                # Proceed directly to confirmation for omni option.
                if num_elements == 9:
                    current_selection = [1, 1, 1, 1, 1, 1, 1, 1, 1]
                    num_selected = 9
                    new_view = ConfirmSelectionView(self.player_user, num_selected, current_selection)
                    embed_msg.description = ("I applaud your greed. In addition to the payment I hope your "
                                             "sanity can afford the cost.")
                    cost_msg = payment_embed(self.player_user, num_elements, current_selection)
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
                embed_msg.description = "You would value the sanctity of your soul so little?"
                if mutation_tier in mutation_upgrade_data:
                    token_cost = mutation_upgrade_data[mutation_tier][0]
                    cost_msg = payment_embed(self.player_user, token_cost, mutation_cost_list[mutation_tier])
                    embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
                new_view = ConfirmSelectionView(self.player_user, 0, "mutation")
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
        self.embed = None
        available_options = [(index, (name, emoji)) for index, (name, emoji, selection) in
                             enumerate(zip(globalitems.element_names, globalitems.global_element_list,
                                           self.current_selection)) if selection != 1]

        options = [discord.SelectOption(
            emoji=emoji, label=option, value=str(i),
            description=f"{option} affinity")
            for (i, (option, emoji)) in available_options
        ]
        self.select_menu = discord.ui.Select(placeholder="Select the element add.",
                                             min_values=1, max_values=1, options=options)
        self.select_menu.callback = self.element_select_callback
        self.add_item(self.select_menu)

    async def element_select_callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id == self.player_user.discord_id:
                selected_element = int(interaction.data['values'][0])
                if not self.embed:
                    current_selection = self.current_selection
                    current_selection[selected_element] = 1
                    num_selected = self.num_selected + 1
                    if num_selected == self.num_elements:
                        new_view = ConfirmSelectionView(self.player_user, num_selected, current_selection)
                        self.embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                                   title="Isolde, Soulweaver of the True Laws",
                                                   description="How entertaining. I am willing to engrave your soul, "
                                                               "but my services are as expensive as they are painful.")
                        cost_msg = payment_embed(self.player_user, self.num_elements, self.current_selection)
                        self.embed.add_field(name="Cost:", value=cost_msg, inline=False)
                    else:
                        new_view = ElementSelectView(self.player_user, self.num_elements, num_selected, current_selection)
                        self.embed = discord.Embed(colour=discord.Colour.dark_orange(),
                                                   title="Isolde, Soulweaver of the True Laws",
                                                   description="What is the next desired affinity?")
                await interaction.response.edit_message(embed=self.embed, view=new_view)
        except Exception as e:
            print(e)


class ConfirmSelectionView(discord.ui.View):
    def __init__(self, player_user, num_selected, current_selection):
        super().__init__(timeout=None)
        self.player_user = player_user
        self.num_selected = num_selected
        self.current_selection = current_selection
        mutation_tier = int(self.player_user.insignia[-1])
        self.mutation_rate = mutation_upgrade_data[mutation_tier][1]
        if self.current_selection == "mutation":
            if mutation_tier < 3:
                self.engrave.label = f"{insignia_prefix[(5 + mutation_tier)]} ({self.mutation_rate}%)"
            else:
                self.engrave.label = f"Mutation [MAX]"
                self.engrave.disabled = True
                self.engrave.style = discord.ButtonStyle.secondary
        self.embed_msg = None

    @discord.ui.button(label="Engrave", style=discord.ButtonStyle.success, emoji="🔯")
    async def engrave(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id != self.player_user.discord_id:
                return
            if self.embed_msg:
                await interaction.response.edit_message(embed=self.embed_msg, view=None)
                return

            # Initialize the data.
            self.player_user = player.get_player_by_id(self.player_user.player_id)
            token_stock = inventory.check_stock(self.player_user, "Token2")
            title_msg = "Isolde, Soulweaver of the True Laws"
            self.embed_msg = discord.Embed(colour=discord.Colour.dark_orange(), title=title_msg, description="")

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
                    fae_check = inventory.check_stock(self.player_user, f"Fae{x}")
                    if fae_check < 100:
                        self.embed_msg.description = ("Weaving requires a lot of fae energy. "
                                                      "I'll need you to bring me more cores.")
                        await interaction.response.edit_message(embed=self.embed_msg, view=None)
                        return

                # Pay the costs and engrave the insignia.
                inventory.update_stock(self.player_user, "Token2", (token_cost * -1))
                for z in selected_elements_list:
                    inventory.update_stock(self.player_user, f"Fae{z}", -100)
                delim = ";"
                insignia_code = reduce(lambda full, new: str(full) + delim + str(new), self.current_selection)
                insignia_code += ";0"
                self.embed_msg = display_insignia(self.player_user, insignia_code)
                self.player_user.set_player_field("player_equip_insignia", insignia_code)
                await interaction.response.edit_message(embed=self.embed_msg, view=None)
                return

            # Reconfirm mutation eligibility.
            mutation_tier = int(self.player_user.insignia[-1])
            if mutation_tier >= 3:
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
            secondary_stock = inventory.check_stock(self.player_user, secondary_item.item_id)
            if secondary_stock < 1:
                self.embed_msg.description = ("Such gall to request my services without a sufficient offering. "
                                              "Bring me tokens or don't come back.")
                await interaction.response.edit_message(embed=self.embed_msg, view=None)
                return

            # Handle unsuccessful mutation.
            if random.randint(1, 100) > self.mutation_rate:
                self.embed_msg.description = "The mutation failed, but I managed to keep your soul intact."
                cost_msg = payment_embed(self.player_user, token_cost, mutation_cost_list[mutation_tier])
                self.embed_msg.add_field(name="Cost:", value=cost_msg, inline=False)
                reload_view = ConfirmSelectionView(self.player_user, 0, "mutation")
                await interaction.response.edit_message(embed=self.embed_msg, view=reload_view)
                return

            # Pay the costs and handle the successful mutation.
            inventory.update_stock(self.player_user, "Token2", (token_cost * -1))
            inventory.update_stock(self.player_user, secondary_item.item_id, -1)
            new_tier = int(self.player_user.insignia[-1]) + 1
            self.player_user.insignia = f"{self.player_user.insignia[:-1]}{new_tier}"
            self.player_user.set_player_field("player_equip_insignia", self.player_user.insignia)
            self.embed_msg = display_insignia(self.player_user, self.player_user.insignia)
            reload_view = ConfirmSelectionView(self.player_user, 0, "mutation")
            await interaction.response.edit_message(embed=self.embed_msg, view=reload_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Reselect", style=discord.ButtonStyle.blurple, emoji="↩️")
    async def reselect_callback(self, interaction: discord.Interaction, button: discord.Button):
        try:
            if interaction.user.id == self.player_user.discord_id:
                engrave_msg = "My patience wears thin. Tell me, what kind of power do you seek?"
                embed_msg = discord.Embed(colour=discord.Colour.dark_orange(),
                                          title="Isolde, Soulweaver of the True Laws", description=engrave_msg)
                new_view = InsigniaView(self.player_user)
                await interaction.response.edit_message(embed=embed_msg, view=new_view)
        except Exception as e:
            print(e)


def payment_embed(player_obj, token_cost, current_selection):
    token_item = inventory.BasicItem("Token2")
    token_stock = inventory.check_stock(player_obj, token_item.item_id)
    cost_msg = f"{token_item.item_emoji} {token_item.item_name}: {token_stock} / {token_cost}\n"
    # Create non mutation cost message.
    if type(current_selection) is list:
        for idx, x in enumerate(current_selection):
            if x != 0:
                loot_item = inventory.BasicItem(f"Fae{idx}")
                stock = inventory.check_stock(player_obj, loot_item.item_id)
                cost_msg += f"{loot_item.item_emoji} {loot_item.item_name}: {stock} / 100\n"
        return cost_msg
    # Create mutation cost message.
    secondary_item = inventory.BasicItem(current_selection)
    secondary_stock = inventory.check_stock(player_obj, secondary_item.item_id)
    cost_msg += f"{secondary_item.item_emoji} {secondary_item.item_name}: {secondary_stock} / 1"
    return cost_msg


def assign_insignia_values(player_obj):
    if player_obj.insignia == "":
        return
    # Data handling.
    temp_code = player_obj.insignia.split(";")
    temp_elements, mutation_tier = temp_code[:9], int(temp_code[-1])
    insignia_stars = player_obj.player_echelon // 2 + mutation_tier
    mutation_adjust = max(1, mutation_tier)
    element_list = list(map(int, temp_elements))
    num_elements = element_list.count(1)
    # Apply bonus stats.
    player_obj.final_damage += player_obj.player_lvl * 0.01 * mutation_adjust
    player_obj.attack_speed += insignia_stars * 0.1
    player_obj.hp_bonus += insignia_hp_list[insignia_stars]
    # Apply Elemental Penetration
    if num_elements != 9:
        selected_elements_list = [ind for ind, x in enumerate(element_list) if x == 1]
        for y in selected_elements_list:
            player_obj.elemental_penetration[y] += insignia_multiplier_list[num_elements][0] * 0.01
            player_obj.elemental_penetration[y] += (insignia_multiplier_list[num_elements][1]
                                                    * insignia_stars * mutation_adjust * 0.01)
    # Omni exception for faster runtime and separate stat assignment.
    else:
        player_obj.all_elemental_penetration += insignia_multiplier_list[num_elements][0] * 0.01
        player_obj.all_elemental_penetration += (insignia_multiplier_list[num_elements][1]
                                                 * insignia_stars * mutation_adjust * 0.01)

