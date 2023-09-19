import random
import discord
import inventory
import menus


class Room:
    def __init__(self, room_type, room_tier, room_description, room_colour, embed_msg):
        self.room_type = room_type
        self.room_tier = room_tier
        self.room_description = room_description
        self.room_colour = room_colour
        self.embed = embed_msg
        self.room_view = None

        self.monster_damage = 0
        self.trap_damage = 0
        self.room_image = ""
        self.is_trap = False


def generate_new_room(player):
    next_room = random.randint(1, 4)
    room_tier = random.randint(1, 4)
    random_trap = random.randint(1, 2)
    monster_damage = 0
    image = ""
    dmg_msg = ""
    room_colour, colour_icon = inventory.get_gear_tier_colours(room_tier)
    is_trap = False
    match next_room:
        case 1:
            if random_trap == 1:
                is_trap = True
            room_type = "Empty Room"
            room_colour = discord.Colour.light_gray()
            room_description = "You come across an empty room."
            image = "https://kyleportfolio.ca/botimages/Empty.png"
        case 2:
            if random_trap == 1:
                is_trap = True
            room_type = "Safe Zone"
            match room_tier:
                case 1:
                    room_description = "The empty room is surrounded by a barrier. It seems safe at a glance."
                    image = "https://kyleportfolio.ca/botimages/heal.jpg"
                case 2:
                    room_description = "A fountain built into the wall emanates a mysterious energy."
                    image = "https://kyleportfolio.ca/botimages/heal.jpg"
                case 3:
                    room_description = "A magic circle glows in the center of the room warding off monsters."
                    image = "https://kyleportfolio.ca/botimages/heal.jpg"
                case _:
                    room_description = "A carbuncle lies asleep in the corner of the room."
                    image = "https://kyleportfolio.ca/botimages/heal.jpg"
        case 3:
            room_type = "Monster Encounter"
            random_monster = random.randint(1, 4)
            match room_tier:
                case 1:
                    match random_monster:
                        case 1:
                            room_description = "You are chased by a group of skeletons!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 2:
                            room_description = "A few playful sprites decide to mess with you."
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 3:
                            room_description = "The room is full of oozes. Clearing them all out is rough work."
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case _:
                            room_description = "A goblin sneaks up and lightly wounds you from behind."
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                case 2:
                    match random_monster:
                        case 1:
                            room_description = "Ack! Blood spiders!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 2:
                            room_description = "Faeries are not to be messed with. They don't go down easy."
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 3:
                            room_description = "What's worse then one orc? Two!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case _:
                            room_description = "A spooky wight gives you quite the fright."
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                case 3:
                    match random_monster:
                        case 1:
                            room_description = "Did that statue just... move?! Running is highly advised!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 2:
                            room_description = "A wyrm emerges from the ground! Prepare for combat!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 3:
                            room_description = "A lamia warrior decides to test your strength!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case _:
                            room_description = "Why is there a demon here?! It cannot be allowed to escape!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                case _:
                    match random_monster:
                        case 1:
                            room_description = "Quickly cover your eyes! A fully grown basilisk has appeared!!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 2:
                            room_description = "Such misfortune to encounter the minotaur in his domain!!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case 3:
                            room_description = "This wyvern is looking for it's next meal! Beware the breath!!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
                        case _:
                            room_description = "Is this a chimaera?! Who could have made such a thing?!!"
                            image = "https://kyleportfolio.ca/botimages/test.jpg"
            random_damage = random.randint(50, 250)
            monster_damage = random_damage * room_tier
            monster_damage = int(monster_damage * (1 - 0.01 * player.damage_mitigation))
            player.player_cHP -= monster_damage
        case _:
            room_type = "Treasure Room"
            if random_trap == 1:
                is_trap = True
            match room_tier:
                case 1:
                    room_description = "Before you lies a lesser treasure chest. Will you open it?"
                    image = "https://kyleportfolio.ca/botimages/T1Chest.png"
                case 2:
                    room_description = "Before you lies a greater treasure chest. Will you open it?"
                    image = "https://kyleportfolio.ca/botimages/T1Chest.png"
                case 3:
                    room_description = "Before you lies a superior treasure chest. Will you open it?"
                    image = "https://kyleportfolio.ca/botimages/T1Chest.png"
                case _:
                    room_description = "Just ahead is an ultimate treasure chest. Will you open it?"
                    image = "https://kyleportfolio.ca/botimages/T1Chest.png"
    room_description += "\nHow will you proceed?"

    embed_msg = discord.Embed(colour=room_colour,
                              title=room_type,
                              description=room_description)
    embed_msg.set_image(url=image)

    new_room = Room(room_type, room_tier, room_description, room_colour, embed_msg)
    new_room.monster_damage = monster_damage
    new_room.is_trap = is_trap
    new_room.room_view = generate_room_view(player, new_room)
    if image != "":
        new_room.image = image

    return new_room


def generate_trap_room(player_user, room, method):
    random_damage = random.randint(50, 250)
    trap_damage = random_damage * room.room_tier
    trap_image = ""
    pressure_plate = False
    match room.room_type:
        case "Empty Room":
            trap_trigger = random.randint(1, 6)
            trap_tier = random.randint(1, 4)
            room_colour, colour_icon = inventory.get_gear_tier_colours(trap_tier)
            match trap_trigger:
                case 1:
                    if method == "middle":
                        trap_description = "The floor gives way and you fall into a pit!\n"
                        match trap_tier:
                            case 1:
                                trap_description += "An endless entanglement of snakes surrounds you."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                            case 2:
                                trap_description += "Stuck in the moving sand below, you desperately reach for a hold."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                            case 3:
                                trap_description += "You feel the strong stinging sensation of a scorpion swarm."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                            case _:
                                trap_description += "Spikes from the pit pierce your armour and gravely injure you."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                    else:
                        trap_description = "You progress safely!"
                        trap_damage = 0
                case 2:
                    if method == "middle":
                        trap_description = "You've triggered a pressure plate on the floor! A trap is sprung!\n"
                        pressure_plate = True
                    else:
                        trap_description = "You progress safely!"
                        trap_damage = 0
                case 3:
                    if method == "middle":
                        trap_description = "You've tripped a wire and sprung a trap!\n"
                        match trap_tier:
                            case 1:
                                trap_description += "A giant boulder comes crashing through. Knocking you to the side."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                            case 2:
                                trap_description += "A wave of darts fire from all directions catching you off guard."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                            case 3:
                                trap_description += "A cloud of poison spreads and a couple breaths leave you in pain."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                            case _:
                                trap_description += "The walls are closing in, quickly you squeeze free from the crush."
                                trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                    else:
                        trap_description = "You progress safely!"
                        trap_damage = 0
                case _:
                    if method == "side":
                        trap_description = "You've triggered a pressure plate on the wall! A trap is sprung!\n"
                        pressure_plate = True
                    else:
                        trap_description = "You progress safely!"
                        trap_damage = 0
            if pressure_plate:
                match trap_tier:
                    case 1:
                        trap_description += "Fire consumes the surrounding area burning and searing your skin."
                        trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                    case 2:
                        trap_description += "Water pours into the room and the corridor becomes blocked."
                        trap_description += " Gasping for breath you break down the wall and re-enter the passageway."
                        trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                    case 3:
                        trap_description += "Electricity bolts around wildly. Honing in on your metal equipment."
                        trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                    case _:
                        trap_description += "Magical lasers flash and melt through anything that meets their path."
                        trap_image = "https://kyleportfolio.ca/botimages/trap.png"
        case "Safe Zone":
            room_colour, colour_icon = inventory.get_gear_tier_colours(room.room_tier)
            match room.room_tier:
                case 4:
                    trap_description = "This healing carbuncle is corrupted by a strong celestial miasma."
                    trap_description += " Being near it will only harm you further."
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                case 3:
                    trap_description = "Crackles of red lightning all around. This faulty circle is dangerous!"
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                case 2:
                    trap_description = "You've been poisoned! Even after drinking an antidote you don't feel so good."
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                case _:
                    trap_description = "IT'S A TRAP!\nOn second glance you realize it was just your imagination."
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                    trap_damage = 0
        case _:
            room_colour, colour_icon = inventory.get_gear_tier_colours(room.room_tier)
            match room.room_tier:
                case 1:
                    trap_description = "The chest turns out to be a lesser mimic!"
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                case 2:
                    trap_description = "The chest is actually a greater mimic!"
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                case 3:
                    trap_description = "The well disguised chest is an elder mimic!"
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
                case _:
                    trap_description = "Such misfortune! You've fallen for the ultimate mimic's clever ruse!!"
                    trap_image = "https://kyleportfolio.ca/botimages/trap.png"
    trap_damage = int(trap_damage * (1 - 0.01 * player_user.damage_mitigation))
    embed_msg = discord.Embed(colour=room_colour,
                              title=room.room_type,
                              description=trap_description)
    embed_msg.set_image(url=trap_image)
    dmg_msg = f'You take {trap_damage} damage!'
    player_user.player_cHP -= trap_damage
    if player_user.player_cHP <= 0:
        player_user.player_cHP = 0
        over_msg = "EXPLORATION OVER"
        over_description = "Having taken too much damage, you are forced to return from your exploration."
        embed_msg.add_field(name=over_msg, value=over_description, inline=False)
    player_hp = f'{player_user.player_cHP} / {player_user.player_mHP} HP'
    embed_msg.insert_field_at(0, name=player_hp, value=dmg_msg, inline=False)
    new_room = Room(room.room_type, room.room_tier, trap_description, room_colour, embed_msg)
    if player_user.player_cHP == 0:
        new_room.room_view = None
    else:
        new_room.room_view = menus.TrapRoomView(player_user, new_room)
    new_room.trap_damage = trap_damage

    return new_room


def generate_room_view(player, room):
    match room.room_type:
        case "Empty Room":
            new_view = menus.EmptyRoomView(player, room)
        case "Safe Zone":
            new_view = menus.SafeRoomView(player, room)
        case "Trap Room":
            new_view = menus.TrapRoomView(player, room)
        case "Monster Encounter":
            new_view = menus.MonsterRoomView(player, room)
        case "Transition Room":
            new_view = menus.TransitionRoomView(player, room)
        case _:
            new_view = menus.TreasureRoomView(player, room)

    return new_view
