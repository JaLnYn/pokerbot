import torch 
import time
import sys
import pickle


debug = 0

class Node:
    def __init__(self, state):
        self.state = state
        self.n_actions = state.count(' ')

        self.regret_sum = torch.zeros(self.n_actions)
        
        self.strategy_sum = torch.zeros(self.n_actions,1)


        self.strategy = torch.ones(self.n_actions,1)/self.n_actions
    
    def update_strat(self, weight):
        

        regrets = self.regret_sum
        #print(regrets)
        regrets[regrets < 0] = 0
        normalize = sum(regrets)
        #print(regrets)
        if normalize > 0:
            self.strategy[:,0] = regrets / normalize
        else:
            self.strategy = torch.ones(self.n_actions,1)/self.n_actions

        self.strategy_sum += self.strategy * weight

    def get_average_strategy(self):
        strategy = self.strategy_sum 

        total = sum(strategy)
        strategy /= total
        return strategy

    def get_actions(self):
        return self.n_actions

class Trainer:

    def __init__(self):
        self.board="         "
        self.nodes = {}
        self.n_players = 2
        
    
    def reward(self, state):

        n_actions = state.count(' ')
        winner = None
        if state[0] == state[1] and state[1] == state[2] and state[0] != ' ': # first row
            winner = state[0]
        elif state[3] == state[4] and state[4] == state[5] and state[3] != ' ': # second row
            winner = state[3]
        elif state[6] == state[7] and state[7] == state[8] and state[6] != ' ': # third row
            winner = state[6]
        elif state[0] == state[4] and state[4] == state[8] and state[0] != ' ': # diag 2
            winner = state[0]
        elif state[2] == state[4] and state[4] == state[6] and state[2] != ' ': # diag 1
            winner = state[2]
        elif state[0] == state[3] and state[3] == state[6] and state[0] != ' ': # first column 
            winner = state[0]
        elif state[1] == state[4] and state[4] == state[7] and state[1] != ' ': # second column
            winner = state[1]
        elif state[2] == state[5] and state[5] == state[8] and state[2] != ' ': # third column
            winner = state[2]
        if n_actions == 0:
            return torch.zeros(1, self.n_players)

        if winner != None:
            winner = int(winner)
            x = -torch.ones(1,self.n_players)
            x[0][winner] = self.n_players -1
            #print("x",x)
            return x

        return None

    def get_node(self, state):
        
        if state not in self.nodes:
          
          self.nodes[state] = Node(state)
          return self.nodes[state] 
        return self.nodes[state]
        
    def cfr(self, state, turn, prob_get_to):
        n = turn 
        turn+=1
        cur_player = n % self.n_players
        reward = self.reward(state)
        #print(reward)
        if reward != None:
            #print("resard,", reward)
            return reward

        node = self.get_node(state)
        strat = node.strategy
        #print("strategy:", strat)
        
        action_utils = torch.zeros(node.n_actions, self.n_players)
        
        cur_action = 0
        for act in range(len(state)):
            #find next space
            
            if state[act] == ' ':
                new_state = state[:act] + str(cur_player) + state[act+1:]
                

                #onny = torch.ones(self.n_players)
                #onny[cur_player] = strat[cur_action]
                
                #print(onny)
                #print(prob)

                
                next_cfr = self.cfr(new_state, turn, prob_get_to * strat[cur_action,0])
                #if debug > 1:
                #if state == '1   0  10':
                #  print ("|"+new_state+"|","cfr ret", next_cfr)
                #  print(cur_action)
                action_utils[cur_action,:] = next_cfr #1xnplayers
                #if state == '1   0  10':
                #  print("in",action_utils,strat)
                cur_action += 1

        #print("action, strat", action_utils, strat)
        util = torch.sum(torch.mul(action_utils, strat), dim=0, keepdim=True)
        if state == '1   0  10' and False:
          print(action_utils,strat)
          print(torch.mul(action_utils, strat))
          print(util)
          print("-----------------------")
        regret = action_utils[:,cur_player] - util[0,cur_player] # 1xn_action 
        #if state == '1   0  10' or state == '1 01 0   ':
        #  print (state)
        #  print(node.strategy)
        #  print(node.regret_sum)
        if debug > 1:
            print("util",util)
            print("actionutil",action_utils)
            print("actionutil2",action_utils[:,cur_player])
            print("reg",regret)

        node.regret_sum += regret*prob_get_to
        #print("util", util)
        return util 

    def train(self, n_iterations=50000):
        expected_game_value = 0
        for i in range(n_iterations):
            if i%3 == 1:
                print(i)
            
            expected_game_value += self.cfr('         ', 0, 1)
            
            #print(self.nodes['1   0  10'].regret_sum)
            #print(self.nodes['1 01 0   '].regret_sum)

            for _, v in self.nodes.items():
                v.update_strat(1)
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
        trainer.train(n_iterations=10)
        save_obj(trainer.nodes, "cfr_save")
        print(trainer.nodes['1   0  10'].get_average_strategy())
        print(trainer.nodes['1   0  10'].strategy)
        print(trainer.nodes['1 01 0   '].get_average_strategy())    
        print(trainer.nodes['1 01 0   '].strategy)
    else:
        nodes = load_obj("cfr_save")
        print(nodes['1   0  10'].get_average_strategy())
        print(nodes['1   0  10'].strategy)
        print(nodes['1 01 0   '].get_average_strategy())
        print(nodes['1 01 0   '].strategy)

    print(abs(time1 - time.time()))
    print("Done")


