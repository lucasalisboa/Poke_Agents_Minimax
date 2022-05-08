import asyncio
from random import random
import time
import sys

sys.path.append("..")

import BattleUtilities
#from Minimax_Compton import Minimax_Compton
#from MiniMax_Lee_Togelius import MiniMax_Lee_Togelius
#from MiniMax_Ho_Ramesh import MiniMax_Ho_Ramesh
from MiniMax_Pmariglia import MiniMax_Pmariglia
from poke_env.player.random_player import RandomPlayer
from MaxDamagePlayer import MaxDamagePlayer
from poke_env.player.player import Player
from poke_env.environment.move_category import MoveCategory
from GameNode import GameNode
from poke_env.environment.pokemon import Pokemon

class MiniMax_Montes(Player): 

    previous_action = None
    maxDepth = 1
    def choose_move(self, battle):
        current_hp = {}
        for pokemon in battle.team.values():
            current_hp.update({pokemon : pokemon.current_hp})
        opponent_hp = {}
        for pokemon in battle.opponent_team.values():
            opponent_hp.update({pokemon : pokemon.current_hp})
        starting_node = GameNode(battle, battle.active_pokemon, current_hp, battle.opponent_active_pokemon, opponent_hp, None, not battle.can_dynamax, battle.active_pokemon.is_dynamaxed, not battle.opponent_can_dynamax, battle.opponent_active_pokemon.is_dynamaxed, float('-inf'), None, self.previous_action)
        if battle.active_pokemon.current_hp <= 0: 
            self.pick_best_switch(starting_node, 0)
        else: 
            self.minimax(starting_node, 0, True)
        child_nodes = starting_node.children
        best_score = float('-inf')
        best_node = None
        for child in child_nodes:
            if child.score >= best_score: 
                best_score = child.score
                best_node = child
        if best_node == None: 
            self.previous_action = None
            return self.choose_default_move(battle)
        self.previous_action = best_node.action
        return self.create_order(best_node.action)

    def minimax(self, node, depth, is_bot_turn):
        if depth == self.maxDepth or self.is_terminal(node): 
            self.score(node,depth)
            return node.score
        if is_bot_turn:
            score = float('-inf')
            bot_moves = node.generate_bot_moves()
            for move in bot_moves: 
                child_score = self.minimax(move, depth, False)
                score = max(score, child_score)
                print
            node.score = score
            return score
        else: 
            score = float('inf')
            opponent_moves = node.generate_opponent_moves()
            if len(opponent_moves) > 0:
                for move in opponent_moves: 
                    child_score = self.minimax(move, depth + 1, True)
                    score = min(score, child_score)
            else: 
                score = float('-inf')
            node.score = score
            return score



    def pick_best_switch(self, node, depth): 
        switches = node.add_bot_switches()
        score = float('-inf')
        for switch in switches:
            child_score = self.minimax(switch, depth, False)
            score = max(score, child_score)
        node.score = score
        return score



    def is_terminal(self, node):
        all_fainted = True
        for pokemon in node.current_HP.keys(): 
            if node.current_HP[pokemon] > 0:
                all_fainted = False
        if all_fainted: 
            return True
        all_fainted = True
        for pokemon in node.opponent_HP.keys():
            if node.opponent_HP[pokemon]:
                all_fainted = False
        if all_fainted: 
            return True
        return False



    def score(self, node, depth):
        current_HP = 0
        max_current_HP = 0
        opponent_HP = 0
        max_opponent_HP = 0
        
        for pokemon in node.opponent_HP.keys():
            if pokemon.current_hp is not None and pokemon.max_hp is not None:
                opponent_HP += node.opponent_HP[pokemon]
                max_opponent_HP += pokemon.max_hp
            
        for pokemon in node.current_HP.keys():
            if pokemon.current_hp is not None and pokemon.max_hp is not None:
                current_HP += node.current_HP[pokemon]
                max_current_HP += pokemon.max_hp
   
        myPoke = 100*(current_HP/max_current_HP)
        opPoke = 100*(opponent_HP/max_opponent_HP)
        score = myPoke - opPoke
        node.score = score
        return score
    
async def main():
    start = time.time()

    enemy = RandomPlayer(
        battle_format="gen8randombattle",
    )
    minimax_player1 = MiniMax_Montes(
        battle_format="gen8randombattle",
    )

    await minimax_player1.battle_against(enemy, n_battles=500)

    print(
        "minimax_player1 won %d / 500 battles against RandomPlayer (this took %f seconds)"
        % (
            minimax_player1.n_won_battles, time.time() - start
        )
    )

if __name__ == "__main__":
        asyncio.get_event_loop().run_until_complete(main())