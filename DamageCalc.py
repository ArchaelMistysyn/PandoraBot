import csv
"""
def calc_dps(player_id, weapon_id) -> int:
    # DPS Formula
    # base damage and attack speed
    DPS = random(wpn_base_damage_min, wpn_base_damage_max) * (wpn_atk_spd)
    # Elemental Penetration
    DPS *= (0.01 * (boss_ele_resist_lowestmatch - roll_ele_pen))
    # void weapon penetration
    if wpn_void:
         DPS *= (0.01 * (boss_type_resist_lowestmatch - 50))
    else:
         DPS *=  (0.01 * (boss_type_resist_lowestmatch))
    # role and activity multipliers
    DPS *= 1 + (0.1 * num_achievment_roles + 0.01 * num_player_level)
    # extra hit/projectiles
    DPS *= 1 + (1 * num_bonus_hits)
    # team debuffs
    DPS *= 1 + (1 * total_damage_aura_debuff)
    # team buffs
    DPS *= 1 + (1 * total_damage_aura_buff)
    # critical multipliers non-random application
    DPS += DPS * (0.01 * crit_rate) * critical_damage_multiplier
    # total damage buff
    DPS *= 1 + (1 * total_damage_multiplier)


    # BIG PROBLEM Need to solve: negative values should multiply as increases instead
    # Smaller problem, unsure hwo order of operations counts for *= if more bracketing is required
"""