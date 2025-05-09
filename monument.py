# General imports
import discord
from discord.ui import Button, View
import asyncio

# Data imports
import globalitems as gli

# Core imports
from pandoradb import run_query as rqy
import sharedmethods as sm
import player
import inventory


async def get_monument_embed(interaction, ctx_obj, player_obj, monument_num):
    monument_title = ["Monument of Beginnings", "Monument of Journeys",
                      "Monument of Providence", "Monument of Endings",
                      "Monument of Apotheosis"]
    monument_description = ["The immaculate monument resonates with life and hope.\n"
                            "The unfamiliar markings grant you new perspective and understanding.",
                            "The abstract monument resonates with passion and freedom.\n"
                            "The ambiguous markings grant you new perspective and understanding.",
                            "The pristine monument resonates with power and control.\n"
                            "The elegant markings grant you new perspective and understanding.",
                            "The ominous monument resonates with death and despair.\n"
                            "The sinister markings grant you the last of their dark wisdom.",
                            "The exalted monument emanates with an overpowering and devouring presence.\n"
                            "The resplendent markings recognize your strength and grant you sacred authority."]
    monument_rewards = [(inventory.BasicItem("Hammer"), 10, 25000), (inventory.BasicItem("Fragment1"), 20, 50000),
                        (inventory.BasicItem("Stone5"), 10, 75000), (inventory.BasicItem("Skull2"), 5, 100000),
                        (inventory.BasicItem("Sacred"), 1, 1000000)]
    monument_data = await player_obj.check_misc_data('monument_data')
    monument_claims = monument_data.split(';')
    if monument_claims[monument_num] == "1":
        embed_msg = sm.easy_embed("Red", monument_title[monument_num], "Already Claimed")
        return
    monument_claims[monument_num] = "1"
    new_data = ';'.join(monument_claims)
    await player_obj.update_misc_data('monument_data', new_data, overwrite_value=True)
    reward, qty, exp_value = monument_rewards[monument_num]
    embed_msg = sm.easy_embed("Green", monument_title[monument_num], monument_description[monument_num])
    exp_msg, lvl_change = await player_obj.adjust_exp(exp_value)
    loot_msg = f"{reward.item_emoji} {qty}x {reward.item_name}"
    embed_msg.add_field(name="", value=f"{gli.exp_icon} {exp_msg} Exp Acquired.\n{loot_msg}", inline=False)
    update_stock = await inventory.update_stock(player_obj, reward.item_id, qty)
    spaced_title = monument_title[monument_num].replace(' ', '%20')
    embed_msg.set_image(url=f"{gli.web_gallery_url}Displays/Locations/{spaced_title}.webp")
    await interaction.response.edit_message(embed=embed_msg, view=None)
    if lvl_change != 0:
        await sm.send_notification(ctx_obj, player_obj, "Level", lvl_change)
    if sm.check_rare_item(reward.item_id):
        await sm.send_notification(ctx_obj, player_obj, "Item", reward.item_id)
