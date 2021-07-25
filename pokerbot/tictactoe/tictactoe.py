import torch 
import time
import sys
import pickle


class Node:
    def __init__(self, state):
        self.state = state
        self.n_actions = state.count(' ')
        if self.n_actions == 0:
            print(state)
            
        self.regret_sum = torch.zeros(self.n_actions)
        self.strat_sum = torch.zeros(self.n_actions)
        self.strategy=torch.tensor(1/self.n_actions).repeat(self.n_actions)
        self.reach_pr = 0
        self.reach_pr_sum = 0
    
    def update_strat(self):
        self.strat_sum += self.reach_pr * self.strategy
        self.reach_pr_sum += self.reach_pr
        self.strategy = self.get_strat()
        self.reach_pr = 0

    def get_strat(self):
        regrets = self.regret_sum
        regrets[regrets < 0] = 0
        normalize = sum(regrets)
        if normalize > 0:
            return regrets / normalize
        else:
            return torch.tensor(1/self.n_actions).repeat(self.n_actions)


    def get_actions(self):
        return self.n_actions

class Trainer:

    def __init__(self):
        self.board="         "
        self.nodes = {}
        self.n_players = 2
    
    def reward(self, state):

        n_actions = state.count(' ')

        if state[0] == state[1] and state[1] == state[2] and state[0] != ' ': # first row
            return state[0]
        elif state[3] == state[4] and state[4] == state[5] and state[3] != ' ': # second row
            return state[3]
        elif state[6] == state[7] and state[7] == state[8] and state[6] != ' ': # third row
            return state[6]
        elif state[0] == state[4] and state[4] == state[8] and state[0] != ' ': # diag 2
            return state[0]
        elif state[2] == state[4] and state[4] == state[6] and state[2] != ' ': # diag 1
            return state[2]
        elif state[0] == state[3] and state[3] == state[6] and state[0] != ' ': # first column 
            return state[0]
        elif state[1] == state[4] and state[4] == state[7] and state[1] != ' ': # second column
            return state[1]
        elif state[2] == state[5] and state[5] == state[8] and state[2] != ' ': # third column
            return state[2]
        if n_actions == 0:
            return -2
        return -1

    def get_node(self, state):
        if state not in self.nodes:
            self.nodes[state] = Node(state)
            return self.nodes[state] 
        return self.nodes[state]
        
    def cfr(self, state, turn, prob):
        n = turn 
        turn+=1
        cur_player = n % self.n_players
        #print(cur_player)
        reward = self.reward(state)
        #print(reward)
        reward = int(reward)
        if reward != -1:
            if reward == cur_player:
                return 20
            elif reward >= 0: 
                return -20
            elif reward == -2:
                return 0

        node = self.get_node(state)
        strat = node.strategy
        #print("strategy:", strat)
        
        action_utils = torch.zeros(node.n_actions)
        
        for act in range(len(state)):
            #find next space
            cur_action = 0
            if state[act] == ' ':
                new_state = state[:act] + str(cur_player) + state[act+1:]
                onny = torch.ones(self.n_players)
                onny[cur_player] = strat[cur_action]
                
                #print(onny)
                #print(prob)
                new_prob = onny * prob
                action_utils[cur_action] = -1 * self.cfr(new_state, turn, new_prob)

                cur_action +=1

        util = sum (action_utils * strat)
        regret = action_utils - util # 1xn_action 

        node.reach_pr += prob[cur_player]
        node.reach_pr += prob[(cur_player-1)%self.n_players]

        return util

    def train(self, n_iterations=50000):
        expected_game_value = 0
        for i in range(n_iterations):
            if i%5 == 0:
                print(i)
            expected_game_value += self.cfr('         ', 0, torch.tensor([1,1]))
            for _, v in self.nodes.items():
                v.update_strat()
        expected_game_value /= n_iterations
        #display_results(expected_game_value, self.nodes)

def save_obj(obj, name):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)



if __name__ == "__main__":
    time1 = time.time()
    train = 1
    trainer = None 

    if train == 1:
        trainer = Trainer()
        trainer.train(n_iterations=100)
        save_obj(trainer.nodes, "cfr_save")
        print(trainer.nodes['1   0  10'].strategy)
    else:
        nodes = load_obj("cfr_save")
        print(nodes['1   0  10'].strategy)

    print(abs(time1 - time.time()))
    print("Done")


