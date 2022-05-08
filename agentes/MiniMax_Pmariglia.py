import asyncio
from random import random
import time
import sys

sys.path.append("..")

import BattleUtilities
#from MiniMax_Montes import MiniMax_Montes
#from MiniMax_Lee_Togelius import MiniMax_Lee_Togelius
#from Minimax_Compton import Minimax_Compton
#from MiniMax_Ho_Ramesh import MiniMax_Ho_Ramesh
from poke_env.player.random_player import RandomPlayer
from MaxDamagePlayer import MaxDamagePlayer
from poke_env.player.player import Player
from poke_env.environment.move_category import MoveCategory
from GameNode import GameNode
from poke_env.environment.pokemon import Pokemon

class MiniMax_Pmariglia(Player): 

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
            self.score(node)
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



    def score(self, node):
        score = 0
        current_HP = 0
        max_current_HP = 0
        opponent_HP = 0
        max_opponent_HP = 0

        for sc in node.battle.side_conditions:
            if sc.value == 13:
                score += 20
            if sc.value == 15:
                score += -7
            if sc.value == 16:
                score += -10
            if sc.value == 17:
                score += -25
            if sc.value == 19:
                score += -7
            if sc.value == 10:
                score += 20
            if sc.value == 18:
                score += 7
            if sc.value == 2:
                score += 40
            if sc.value == 14:
                score += 5

        for sc in node.battle.opponent_side_conditions:
            if sc.value == 13:
                score += -20
            if sc.value == 15:
                score += 7
            if sc.value == 16:
                score += 10
            if sc.value == 17:
                score += 25
            if sc.value == 19:
                score += 7
            if sc.value == 10:
                score += -20
            if sc.value == 18:
                score += -7
            if sc.value == 2:
                score += -40
            if sc.value == 14:
                score += -5

        for poke in node.current_HP.keys():
            if poke.current_hp is not None and poke.max_hp is not None:
                current_HP += node.current_HP[poke]
                max_current_HP += poke.max_hp
            for effect in poke.effects:
                    if effect.value == 136:
                        score += 40
                    if effect.value == 18:
                        score += -20
                    if effect.value == 69:
                        score += -30
            for boost in poke.boosts:
                if boost == 'atk':
                    score += 15
                if boost == 'def':
                    score += 15
                if boost == 'spa':
                    score += 15
                if boost == 'spd':
                    score += 15
                if boost == 'spe':
                    score += 25
                if boost == 'accuracy':
                    score += 3
                if boost == 'evasion':
                    score += 3    
            if poke.status is not None:
                    if poke.status.value == 5:
                        score += -10
                    if poke.status.value == 7:
                        score += -30
                    if poke.status.value == 6:
                        score += -25
                    if poke.status.value == 1:
                        score += -25
                    if poke.status.value == 3:
                        score += -40
                    if poke.status.value == 4:
                        score += -25

        for poke in node.opponent_HP.keys():
            if poke.current_hp is not None and poke.max_hp is not None:
                opponent_HP += node.opponent_HP[poke]
                max_opponent_HP += poke.max_hp
            for effect in poke.effects:
                    if effect.value == 136:
                        score += -40
                    if effect.value == 18:
                        score += 20
                    if effect.value == 69:
                        score += 30
            for boost in poke.boosts:
                if boost == 'atk':
                    score += -15
                if boost == 'def':
                    score += -15
                if boost == 'spa':
                    score += -15
                if boost == 'spd':
                    score += -15
                if boost == 'spe':
                    score += -25
                if boost == 'accuracy':
                    score += -3
                if boost == 'evasion':
                    score += -3
            if poke.status is not None:
                    if poke.status.value == 5:
                        score += 10
                    if poke.status.value == 7:
                        score += 30
                    if poke.status.value == 6:
                        score += 25
                    if poke.status.value == 1:
                        score += 25
                    if poke.status.value == 3:
                        score += 40
                    if poke.status.value == 4:
                        score += 25 
            
        myPoke = 100*(current_HP/max_current_HP)
        opPoke = 100*(opponent_HP/max_opponent_HP)
        score = score + (myPoke - opPoke)
        node.score = score
        return score
    
async def main():
    start = time.time()

    enemy = RandomPlayer(
        battle_format="gen8randombattle",
    )
    minimax_player1 = MiniMax_Pmariglia(
        battle_format="gen8randombattle",
    )

    await minimax_player1.battle_against(enemy, n_battles=500)

    print(
        "minimax player won %d / 500 battles against RandomPlayer (this took %f seconds)"
        % (
            minimax_player1.n_won_battles, time.time() - start
        )
    )

if __name__ == "__main__":
        asyncio.get_event_loop().run_until_complete(main())