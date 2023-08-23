def weapon_damage_calc(base_damage: int, material_tier: str, blessing_tier: str, attack_speed: float) -> int:

    material_damage = get_weapon_tier_damage(material_tier)
    blessing_damage = get_weapon_tier_damage(blessing_tier)
    weapon_damage_temp = (base_damage + material_damage + blessing_damage) * attack_speed

    return int(weapon_damage_temp)


def get_weapon_tier_damage(material_tier: str) -> int:
        match material_tier:
            case "Wood" | "Sturdy" | "Faint" | "Essence":
                damage_temp = 10
            case "Steel" | "Enhanced" | "Luminous" | "Spirit":
                damage_temp = 50
            case "Silver" | "Magic" | "Lustrous" | "Soulbound":
                damage_temp = 100
            case "Mithril" | "Runic" | "Radiant" | "Phantasmal":
                damage_temp = 200
            case _:
                damage_temp = 400

        return damage_temp

