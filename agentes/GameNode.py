import BattleUtilities

from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon

class GameNode: 
    battle = None
    current_pokemon = None
    current_HP = {}
    opponent_pokemon = None
    opponent_HP = {}
    action = None
    has_dynamaxed = False
    currently_dynamaxed = False
    opponent_has_dynamaxed = False
    opponent_currently_dynamaxed = False
    children = []
    score = float('-inf')
    parent_node = None
    previous_action = None

    def __init__(self, battle, current_pokemon, current_HP, opponent_pokemon, opponent_HP, action, has_dynamaxed, currently_dynamaxed, opponent_has_dynamaxed, opponent_currently_dynamaxed, score, parent_node, previous_action):
        self.battle = battle
        self.current_pokemon = current_pokemon
        self.current_HP = current_HP
        self.opponent_pokemon = opponent_pokemon
        self.opponent_HP = opponent_HP
        self.action = action
        self.has_dynamaxed = has_dynamaxed
        self.currently_dynamaxed = currently_dynamaxed
        self.opponent_has_dynamaxed = opponent_has_dynamaxed
        self.opponent_currently_dynamaxed = opponent_currently_dynamaxed
        self.score = score
        self.parent_node = parent_node
        self.children = []
        self.previous_action = previous_action


    def generate_bot_moves(self):
        self.add_bot_moves()
        if not self.battle.trapped and (not isinstance(self.previous_action, Pokemon) or self.battle.active_pokemon.current_hp <= 0):
            self.add_bot_switches()
        return self.children
		
    def add_bot_moves(self):
        i = 0
        if self.battle.active_pokemon is self.current_pokemon: 
            for move in self.battle.available_moves:
                if move.current_pp > 0:
                    i = i + 1
                    self.children.append(GameNode(self.battle, self.current_pokemon, self.current_HP.copy(), self.opponent_pokemon, self.opponent_HP.copy(), move, self.has_dynamaxed, self.currently_dynamaxed, self.opponent_has_dynamaxed, self.opponent_currently_dynamaxed, self.score, self, self.previous_action))
        else: 
            for move in self.current_pokemon.moves.values():
                if move.current_pp > 0: 
                    i = i + 1
                    self.children.append(GameNode(self.battle, self.current_pokemon, self.current_HP.copy(), self.opponent_pokemon, self.opponent_HP.copy(), move, self.has_dynamaxed, self.currently_dynamaxed, self.opponent_has_dynamaxed, self.opponent_currently_dynamaxed, self.score, self, self.previous_action)) 
		
		
    def add_bot_dynamax_moves(self):
        i = 0
        if self.battle.can_dynamax and not self.has_dynamaxed:
            for move in self.battle.available_moves:
                if move.current_pp > 0:
                    self.children.append(GameNode(self.battle, self.current_pokemon, self.current_HP.copy(), self.opponent_pokemon, self.opponent_HP.copy(), move.dynamaxed, True, True, self.opponent_has_dynamaxed, self.opponent_currently_dynamaxed, self.score, self, self.previous_action))
		

    def add_bot_switches(self): 
        i = 0
        for switch in self.battle.team.values():
            if switch.current_hp > 0 and switch is not self.current_pokemon:
                i = i + 1
                self.children.append(GameNode(self.battle, switch, self.current_HP.copy(), self.opponent_pokemon, self.opponent_HP.copy(), switch, self.has_dynamaxed, False, self.opponent_has_dynamaxed, self.opponent_currently_dynamaxed, self.score, self, self.previous_action))
        return self.children

    def generate_opponent_moves(self): 
        self.add_opponent_moves()
        self.add_opponent_switches()
        if len(self.children) == 0:
            self.add_opponent_default()
        return self.children
		
    def add_opponent_moves(self):
        for move in self.opponent_pokemon.moves.values():
            updated_current_HP = self.current_HP.copy()
            updated_opponent_HP = self.opponent_HP.copy()
            if BattleUtilities.opponent_can_outspeed(self.current_pokemon, self.opponent_pokemon) or isinstance(self.action, Pokemon):
                damage = BattleUtilities.calculate_damage(move, self.opponent_pokemon, self.current_pokemon, False, False)
                damage_percentage = (damage / BattleUtilities.calculate_total_HP(self.current_pokemon, self.currently_dynamaxed)) * 100
                updated_current_HP.update({self.current_pokemon : self.current_HP[self.current_pokemon] - damage })
                if isinstance(self.action, Move) and updated_current_HP[self.current_pokemon] > 0:
                    damage = BattleUtilities.calculate_damage(self.action, self.current_pokemon, self.opponent_pokemon, True, True)
                    damage_percentage = (damage / BattleUtilities.calculate_total_HP(self.opponent_pokemon, self.opponent_currently_dynamaxed)) * 100
                    updated_opponent_HP.update({self.opponent_pokemon : self.opponent_HP[self.opponent_pokemon] - damage_percentage })
            else: 
                damage = BattleUtilities.calculate_damage(self.action, self.current_pokemon, self.opponent_pokemon, True, True)
                damage_percentage = (damage / BattleUtilities.calculate_total_HP(self.opponent_pokemon, self.opponent_currently_dynamaxed)) * 100
                updated_opponent_HP.update({self.opponent_pokemon : self.opponent_HP[self.opponent_pokemon] - damage_percentage})
                if updated_opponent_HP[self.opponent_pokemon] > 0: 
                    damage = BattleUtilities.calculate_damage(move, self.opponent_pokemon, self.current_pokemon, False, False)
                    damage_percentage = (damage / BattleUtilities.calculate_total_HP(self.current_pokemon, self.currently_dynamaxed)) * 100
                    updated_current_HP.update({self.current_pokemon : self.current_HP[self.current_pokemon] - damage_percentage})
            self.children.append(GameNode(self.battle, self.current_pokemon, updated_current_HP, self.opponent_pokemon, updated_opponent_HP, move, self.has_dynamaxed, self.currently_dynamaxed, self.opponent_has_dynamaxed, self.opponent_currently_dynamaxed, self.score, self, self.previous_action))

    def add_opponent_dynamax_moves(self):
        i = 0

    def add_opponent_switches(self):
        for switch in self.battle.opponent_team.values():
            if switch is not None and switch is not self.opponent_pokemon and switch.current_hp:
                if isinstance(self.action, Move):
                    damage = BattleUtilities.calculate_damage(self.action, self.current_pokemon, switch, True, True)
                    damage_percentage = (damage / BattleUtilities.calculate_total_HP(self.opponent_pokemon, False)) * 100
                    updated_opponent_HP = switch.current_hp - damage_percentage
                self.children.append(GameNode(self.battle, self.current_pokemon, self.current_HP.copy(), switch, self.opponent_HP.copy(), switch, self.has_dynamaxed, self.currently_dynamaxed, self.opponent_has_dynamaxed, False, self.score, self, self.previous_action))
    
    def add_opponent_default(self):        
        updated_opponent_HP = self.opponent_HP.copy()
        if isinstance(self.action, Move):
            damage = BattleUtilities.calculate_damage(self.action, self.current_pokemon, self.opponent_pokemon, True, True)
            damage_percentage = (damage / BattleUtilities.calculate_total_HP(self.opponent_pokemon, True)) * 100
            updated_opponent_HP.update({self.opponent_pokemon : self.opponent_HP[self.opponent_pokemon] - damage_percentage})
            self.children.append(GameNode(self.battle, self.current_pokemon, self.current_HP.copy(), self.opponent_pokemon, updated_opponent_HP, None, self.has_dynamaxed, self.currently_dynamaxed, self.opponent_has_dynamaxed, self.opponent_currently_dynamaxed, self.score, self, self.previous_action))