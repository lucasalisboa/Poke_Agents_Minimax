from poke_env.environment.move_category import MoveCategory

def calculate_damage(move, attacker, defender, pessimistic, is_bot_turn):
    if move is None:
        print("Why is move none?")
        return 0
    if move.category == MoveCategory.STATUS:
        return 0
    damage = move.base_power
    ratio = 1
    if move.category == MoveCategory.PHYSICAL:
        ratio = calculate_physical_ratio(attacker, defender, is_bot_turn)
    elif move.category == MoveCategory.SPECIAL:
        ratio = calculate_special_ratio(attacker, defender, is_bot_turn)
    damage = damage * ratio
    level_multiplier = ((2 * attacker.level) / 5 ) + 2
    damage = damage * level_multiplier
    damage = (damage / 50) + 2;
    if pessimistic:
        damage = damage * 0.85
    if move.type == attacker.type_1 or move.type == attacker.type_2:
        damage = damage * 1.5
    type_multiplier = defender.damage_multiplier(move)
    damage = damage * type_multiplier
    return damage

def calculate_physical_ratio(attacker, defender, is_bot_turn):
    if is_bot_turn:
        attack = attacker.stats["atk"]
        defense = 2 * defender.base_stats["def"]
        defense = defense + 36
        defense = ((defense * defender.level) / 100 ) + 5
    else:
        defense = defender.stats["def"]
        attack = 2 * attacker.base_stats["atk"]
        attack = attack + 36
        attack = ((attack * attacker.level) / 100) + 5
    return attack / defense   

def calculate_special_ratio(attacker, defender, is_bot_turn):
    if is_bot_turn:
        spatk = attacker.stats["spa"]
        spdef = 2 * defender.base_stats["spd"]
        spdef = spdef + 36
        spdef = ((spdef * defender.level) / 100 ) + 5
    else: 
        spdef = defender.stats["spd"]
        spatk = 2 * attacker.base_stats["spa"]
        spatk = spatk + 36
        spatk = ((spatk * attacker.level) / 100) + 5
    return spatk / spdef

def opponent_can_outspeed(my_pokemon, opponent_pokemon):
    my_speed = my_pokemon.stats["spe"]
    opponent_max_speed = 2 * opponent_pokemon.base_stats["spe"]
    opponent_max_speed = opponent_max_speed + 52
    opponent_max_speed = ((opponent_max_speed * opponent_pokemon.level) / 100) + 5
    if opponent_max_speed > my_speed: 
        return True
    else: 
        return False

def calculate_total_HP(pokemon, is_dynamaxed): 
    HP = pokemon.base_stats["hp"] * 2
    HP = HP + 36
    HP = ((HP * pokemon.level) / 100)
    HP = HP + pokemon.level + 10
    if is_dynamaxed: 
        HP = HP * 2
    return HP

def get_defensive_type_multiplier(my_pokemon, opponent_pokemon):
    multiplier = 1
    first_type = opponent_pokemon.type_1
    first_multiplier = my_pokemon.damage_multiplier(first_type)
    second_type = opponent_pokemon.type_2
    if second_type is None:
        return first_multiplier
    second_multiplier = my_pokemon.damage_multiplier(second_type)
    multiplier = first_multiplier if first_multiplier > second_multiplier else second_multiplier
    return  multiplier
