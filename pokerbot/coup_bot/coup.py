
import torch
from random import shuffle
import time
import sys
import numpy as np
import player

#some of this code was taken from https://github.com/IanSullivan/PokerCFR
#AND https://github.com/mirzakhalov/coup-ai/blob/master/game.py


#note this game is simplified in that challenges are always accepted if encountered and the first card in the hand is always lost
#note, coins max out at 9


class State:
    def __init__(self, players, history, player_count):
        self.player_info = [[0,0,0,0]]* player_count
        for i in range(len(players)):
            self.player_info[i][0] = players[i].coins
            self.player_info[i][1] = players[i].cards[0]
            self.player_info[i][2] = players[i].cards[1]
            self.player_info[i][3] = -1
        self.history = history
        
    def get_state(self, cur = None):
        players = self.player_info

        if cur != None:
            state += str(players[cur][1]) + str(players[cur][2]) + " "

        for i in range(len(players)):
            if players[i].coins > 9:
                raise Exception("More than 9 coins")
            if cur == None:
                state += str(players[i][0]) + str(players[i][1]) + str(players[i][2]) + " "
            else:
                #state += "-" + "-" + str(players[(i + cur) % self.player_count].coins) + " "
                state += str(players[i][0])
                if players[i][1] == 9:
                    state += "9" # card doesn't exist
                else:
                    state += "8" # card exists

                if players[i][2] == 9:
                    state += "9"
                else:
                    state += "8"

        state += self.history

        return state

    def get_reward(self, player_id):
        players = self.player_info
        if players[player_id][1] == 9 and player[player_id][2] == 9:
            # player is ded
            return players[i][3]
        return None


class gameState:
    def __init__(self, stid, n_actions=7):
        self.stid = stid
        self.n_actions = n_actions
        self.regret_sum = torch.zeros(n_actions)
        self.strat_sum = torch.zeros(n_actions)
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


class Game:

    def __init__(self, player_count):
        self.deck = [0,0,0,1,1,1,2,2,2,3,3,3,4,4,4]
        self.players = []
        self.round_count = 0
        self.player_count = player_count

        self.history = ""

        block = [1, -1, 6, 6, 4]

        self.actions['I', 'F', 'C', 'T', 'A', 'E', 'S']
        #             0    1    2    3    4    5    6



        shuffle(self.deck)

        # adding players to the game
        for i in range(0, player_count):
            # pull 2 cards from the deck and deal to each player
            cards = []
            cards.append(self.deck.pop())
            cards.append(self.deck.pop())

            # set the name for the player
            name = i
            agent = Agent(i)
            # create a player
            player = Player(cards, 2, i, True, agent)
            self.players.append(player)

        self.state = State(self.players, "", player_count)

    def add_card(self, card):
        self.deck.append(card)
        shuffle(self.deck)

    def remove_card(self, player, card):
        if player.cards[0] == 9:
            player.cards[1] = 9
        else:
            player.cards[0] = 9

    def get_node(self, state, me):
        stid = state.get_state(me)
        if stid not in self.nodes:
            #here
            info_set = gameState(stid)
            self.nodes[stid] = info_set
            return info_set
        return self.nodes[stid]


    def cfr(self, history, pr_1, pr_2):
        n = len(history)
        #each term action/target/block/challenge/by
        cur_player = (n//5)%self.player_count
        my_cards = self.players[cur_player].cards

        print(my_cards)

        term = self.state.get_reward(cur_player)
        if  term != -1:
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



