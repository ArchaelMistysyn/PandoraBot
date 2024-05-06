# General imports
import discord

# Data imports
import globalitems
import sharedmethods

# Core imports
from pandoradb import run_query as rq
import player
import inventory


class BazaarView(discord.ui.View):
    def __init__(self, player_obj, sort_type="Tier", filter_type=""):
        super().__init__(timeout=None)
        self.player_obj = player_obj
        self.sort_type, self.filter_type = sort_type, filter_type

    async def handle_sort_and_filter(self, interaction, sort_type=None, filter_type=None):
        if sort_type is not None:
            self.sort_type = sort_type
        if filter_type is not None:
            self.filter_type = filter_type
        new_embed = await show_bazaar_items(self.player_obj, sort_type=self.sort_type, filter_type=self.filter_type)
        new_view = BazaarView(self.player_obj, sort_type=self.sort_type, filter_type=self.filter_type)
        await interaction.response.edit_message(embed=new_embed, view=new_view)

    @discord.ui.button(label="Sort: Tier", style=discord.ButtonStyle.blurple, row=1)
    async def tier_sort(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_sort_and_filter(interaction, sort_type="Tier")

    @discord.ui.button(label="Sort: Cost", style=discord.ButtonStyle.blurple, row=1)
    async def cost_sort(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_sort_and_filter(interaction, sort_type="Cost")

    @discord.ui.button(label="Filter: None", style=discord.ButtonStyle.blurple, row=2)
    async def clear_filters(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_sort_and_filter(interaction, filter_type=None)

    @discord.ui.button(label="Filter: Class", style=discord.ButtonStyle.blurple, row=2)
    async def class_filter(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_sort_and_filter(interaction, filter_type="Class")


def check_num_listings(player_obj):
    raw_query = "SELECT * FROM CustomBazaar WHERE seller_id = :id_check"
    params = {'id_check': player_obj.player_id}
    df = rq(raw_query, return_value=True, params=params)
    return len(df)


def list_custom_item(item, cost):
    raw_query = "INSERT INTO CustomBazaar (item_id, seller_id, cost) VALUES (:item_id, :seller_id, :cost)"
    params = {'item_id': item.item_id, 'seller_id': item.player_owner, 'cost': cost}
    rq(raw_query, params=params)
    item.item_inlaid_gem_id, item.player_owner = 0, -1
    item.update_stored_item()


def retrieve_items(player_id):
    
    raw_query = "SELECT item_id FROM CustomBazaar WHERE seller_id = :player_id"
    df = rq(raw_query, return_value=True, params={'player_id': player_id})
    item_ids = []
    if len(df) != 0:
        item_ids = df['item_id'].tolist()
        update_query = "UPDATE CustomInventory SET player_id = :player_id WHERE item_id IN :item_ids"
        delete_query = "DELETE FROM CustomBazaar WHERE item_id IN :item_ids"
        rq(update_query, params={'player_id': player_id, 'item_ids': tuple(item_ids)})
        rq(delete_query, params={'item_ids': tuple(item_ids)})
    
    return len(item_ids) if item_ids else 0


async def show_bazaar_items(player_obj, sort_type="Tier", filter_type=""):
    sort_dict = {"Cost": " ORDER BY CustomBazaar.cost DESC",
                 "Tier": " ORDER BY CustomInventory.item_tier DESC, CustomInventory.item_base_dmg_max DESC"}
    filter_dict = {"Class": f" WHERE CustomInventory.item_damage_type = '{player_obj.player_class}' "}
    if sort_type in sort_dict:
        sort_type = sort_dict[sort_type]
    if filter_type in filter_dict:
        filter_type = filter_dict[filter_type]
    raw_query = (f"SELECT CustomBazaar.item_id, CustomBazaar.seller_id, CustomBazaar.cost, "
                 f"CustomInventory.item_name, CustomInventory.item_type, "
                 f"CustomInventory.item_damage_type, CustomInventory.item_elements, "
                 f"CustomInventory.item_tier, CustomInventory.item_bonus_stat, "
                 f"CustomInventory.item_base_dmg_min, CustomInventory.item_base_dmg_max "
                 f"FROM CustomBazaar "
                 f"INNER JOIN CustomInventory ON CustomBazaar.item_id = CustomInventory.item_id"
                 f"{filter_type}"
                 f"{sort_type}")
    df = rq(raw_query, return_value=True)
    bazaar_embed = discord.Embed(colour=discord.Colour.dark_orange(), title="The Bazaar", description="Open Marketplace")
    if df is None or len(df.index) == 0:
        return None
    for index, row in df.iterrows():
        item_id, seller_id = int(row["item_id"]), int(row["seller_id"])
        cost = int(row["cost"])
        item_name, item_tier, item_type = str(row["item_name"]), int(row["item_tier"]), str(row["item_type"])
        temp_elements = list(str(row['item_elements']).split(';'))
        item_elements, item_damage_type = list(map(int, temp_elements)), str(row["item_damage_type"])
        item_bonus_stat = str(row["item_bonus_stat"])
        item_base_dmg_min, item_base_dmg_max = int(row["item_base_dmg_min"]), int(row["item_base_dmg_max"])

        # Construct the listing output.
        item_cost = f"Cost: {globalitems.coin_icon} {cost}x"
        item_damage = f"Average Damage: {int((item_base_dmg_min + item_base_dmg_max) / 2):,}"
        item_main_info = f"{item_damage}"
        if item_bonus_stat:
            bonus_stat = item_bonus_stat if 'D' not in item_type else globalitems.path_names[int(item_bonus_stat)]
            item_main_info = f"{item_main_info} -- Skill: {bonus_stat}"
        seller = await player.get_player_by_id(seller_id)
        display_stars = sharedmethods.display_stars(item_tier)
        item_type = f'{globalitems.class_icon_dict[item_damage_type]}'
        # elements = ''.join(globalitems.global_element_list[idz] for idz, z in enumerate(item_elements) if z == 1)
        sub_data = f"{display_stars}\nCost: {globalitems.coin_icon} {cost:,}x -- Item ID: {item_id}"
        sub_data += f"\n{item_main_info}\nListed by: {seller.player_username}"
        bazaar_embed.add_field(name=f"{item_name} {item_type}", value=sub_data, inline=False)
    return bazaar_embed


def get_seller_by_item(item_id):
    raw_query = "SELECT seller_id FROM CustomBazaar WHERE item_id = :item_check"
    df = rq(raw_query, return_value=True, params={'item_check': item_id})
    return int(df['seller_id'].values[0]) if len(df.index) != 0 else 0


def get_item_cost(item_id):
    raw_query = "SELECT cost FROM CustomBazaar WHERE item_id = :item_check"
    df = rq(raw_query, return_value=True, params={'item_check': item_id})
    return int(df['cost'].values[0]) if len(df.index) != 0 else 0


async def buy_item(item_id):
    raw_query = "DELETE FROM CustomBazaar WHERE item_id = :item_check"
    rq(raw_query, params={'item_check': item_id})
    seller_id = get_seller_by_item(item_id)
    seller_object = await player.get_player_by_id(seller_id)
    if seller_object is not None:
        item_cost = get_item_cost(item_id)
        _ = seller_object.adjust_coins(item_cost)
