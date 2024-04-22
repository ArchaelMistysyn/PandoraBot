# General imports
import discord

# Data imports
import globalitems
import sharedmethods

# Core imports
from pandoradb import run_query as rq
import player
import inventory


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


async def show_bazaar_items(filtertype=None):
    raw_query = ("SELECT CustomBazaar.item_id, CustomBazaar.seller_id, CustomBazaar.cost, "
                 "CustomInventory.item_name, CustomInventory.item_type, "
                 "CustomInventory.item_damage_type, CustomInventory.item_elements, "
                 "CustomInventory.item_tier, CustomInventory.item_bonus_stat, "
                 "CustomInventory.item_base_dmg_min, CustomInventory.item_base_dmg_max "
                 "FROM CustomBazaar "
                 "INNER JOIN CustomInventory ON CustomBazaar.item_id = CustomInventory.item_id "
                 "ORDER BY CustomInventory.item_tier DESC, CustomInventory.item_base_dmg_max DESC, "
                 "CustomBazaar.cost ASC")
    df = rq(raw_query, return_value=True)
    bazaar_embed = discord.Embed(colour=discord.Colour.dark_orange(), title="The Bazaar", description="Open Marketplace")
    if len(df.index) == 0:
        return None
    for index, row in df.iterrows():
        item_id, seller_id = int(row["item_id"]), int(row["seller_id"])
        cost = int(row["cost"])
        item_name, item_tier = str(row["item_name"]), int(row["item_tier"])
        temp_elements = list(str(row['item_elements']).split(';'))
        item_elements, item_damage_type = list(map(int, temp_elements)), str(row["item_damage_type"])
        item_bonus_stat = str(row["item_bonus_stat"])
        item_base_dmg_min, item_base_dmg_max = int(row["item_base_dmg_min"]), int(row["item_base_dmg_max"])

        # Construct the listing output.
        item_cost = f"Cost: {globalitems.coin_icon} {cost}x"
        item_damage = f"Average Damage: {int((item_base_dmg_min + item_base_dmg_max) / 2):,}"
        item_main_info = f"{item_damage}"
        if item_bonus_stat:
            item_main_info = f"{item_main_info} -- Skill: {item_bonus_stat}"
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
