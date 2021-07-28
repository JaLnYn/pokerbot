
import torch
from random import shuffle
import time
import sys
import numpy as np

#Most of this code was taken from https://github.com/IanSullivan/PokerCFR
class Game:

    def __init__(self):
        self.nodes = {}
        self.expected_game_value = 0
        self.n_cards = 3
        self.nash_equilibrium = dict()
        self.cur_player = 0
        self.deck = np.array([0,1,2])
        self.n_actions = 2

    def is_term(self,history):
        if history[-2:] == 'pp' or history[-2:] == 'bb' or history[-2:] == 'bp':
            return True
    
    def reward(self, history, player_card, opp_card):
        term = history[-1] == 'p'
        double_bet = history[-2:] == 'bb'
        if term: 
            if history[-2:] == 'pp':
                if player_card > opp_card: 
                    return 1
                else: 
                    return -1
            else:
                return 1
        elif double_bet:
            if player_card > opp_card: 
                return 2
            else: 
                return -2
        
    def get_node(self, card, history):
        stid = str(card) + " " + history
        if stid not in self.nodes:
            action_dict = {0: 'p', 1: 'b'}
            print("creating: ", stid)
            info_set = gameState(stid, action_dict)
            self.nodes[stid] = info_set
            return info_set
        return self.nodes[stid]



    def cfr(self, history, pr_1, pr_2):
        n = len(history)
        cur_player = n%2
        player_card = self.deck[cur_player]

        if self.is_term(history):
            player = self.deck[cur_player]
            op = self.deck[(cur_player+1)%2]
            reward = self.reward(history, player, op)
            return reward

        node = self.get_node(player_card, history)
        strat = node.strategy
        
        action_utils = torch.zeros(self.n_actions)

        for act in range(self.n_actions):
            next_hist = history + node.action_dict[act]
            if cur_player == 0:
                action_utils[act] = -1 * self.cfr(next_hist, pr_1 * strat[act], pr_2)
            else:
                action_utils[act] = -1 * self.cfr(next_hist, pr_1 , pr_2* strat[act])

        util = sum (action_utils * strat)
        regret = action_utils - util

        if cur_player == 0:
            node.reach_pr += pr_1
            node.regret_sum += pr_2 * regret
        else:
            node.reach_pr += pr_2
            node.regret_sum += pr_1 * regret

        return util


        #HERERERERE 
        


    def train(self, n_iterations=50000):
        expected_game_value = 0
        for _ in range(n_iterations):
            shuffle(self.deck)
            expected_game_value += self.cfr('', 1, 1)
            for _, v in self.nodes.items():
                v.update_strat()

        expected_game_value /= n_iterations
        display_results(expected_game_value, self.nodes)




class gameState:
    def __init__(self, stid, action_dict, n_actions=2):
        self.stid = stid
        self.n_actions = n_actions
        self.regret_sum = torch.zeros(n_actions)
        self.strat_sum = torch.zeros(n_actions)
        self.action_dict = action_dict
        self.strategy=torch.tensor(1/n_actions).repeat(n_actions)
        self.reach_pr = 0
        self.reach_pr_sum = 0

        
    def get_strat(self):
        regrets = self.regret_sum
        regrets[regrets < 0] = 0
        normalize = sum(regrets)
        if normalize > 0:
            return regrets / normalize
        else:
            return torch.tensor(1/self.n_actions).repeat(self.n_actions)

    def update_strat(self):
        self.strat_sum += self.reach_pr * self.strategy
        self.reach_pr_sum += self.reach_pr
        self.strategy = self.get_strat()
        self.reach_pr = 0

    def get_average_strategy(self):
        strategy = self.strat_sum / self.reach_pr_sum
        # Re-normalize
        total = sum(strategy)
        strategy /= total
        return strategy

    def __str__(self):
        strategies = ['{:03.2f}'.format(x)
            for x in self.get_average_strategy()]
        return '{} {}'.format(self.stid.ljust(6), strategies)

def display_results(ev, i_map):
    print('player 1 expected value: {}'.format(ev))
    print('player 2 expected value: {}'.format(-1 * ev))

    print()
    print('player 1 strategies:')
    sorted_items = sorted(i_map.items(), key=lambda x: x[0])
    for _, v in filter(lambda x: len(x[0]) % 2 == 0, sorted_items):
        print(v)
    print()
    print('player 2 strategies:')
    for _, v in filter(lambda x: len(x[0]) % 2 == 1, sorted_items):
        print(v)


if __name__ == "__main__":
    time1 = time.time()
    trainer = Game()
    trainer.train(n_iterations=25000)
    print(abs(time1 - time.time()))
    print(sys.getsizeof(trainer))
