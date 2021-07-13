import torch 



class Node:
    def __init__(self, state)
        self.state = state
        self.n_actions = state.count(' ')
        self.regret_sum = torch.zeros(n_actions)
        self.strat_sum = torch.zeros(n_actions)
        self.strategy=torch.tensor(1/n_actions).repeat(n_actions)
        self.reach_pr = 0
        self.reach_pr_sum = 0

    def get_strat(self):
        regrets = self.regret_sum
        regrets[regrets < 0] = 0
        normalize = sum(regrets)

class Game:

    def init():
        self.board="         "
        self.nodes = {}
        self.n_action=9

    def reward(self, state):
        if state[0] == state[1] and state[1] == state[2]: # first row
            return state[0]
        elif state[3] == state[4] and state[4] == state[5]: # second row
            return state[3]
        elif state[6] == state[7] and state[7] == state[8]: # third row
            return state[6]
        elif state[0] == state[4] and state[4] == state[8]: # diag 2
            return state[0]
        elif state[2] == state[4] and state[4] == state[6]: # diag 1
            return state[2]
        elif state[0] == state[3] and state[3] == state[6]: # first column 
            return state[0]
        elif state[1] == state[4] and state[4] == state[7]: # second column
            return state[1]
        elif state[2] == state[5] and state[5] == state[8]: # third column
            return state[2]

    def get_node(self, state):
        if state not in self.nodes:
            self.nodes[state] = Node(state)
            return self.nodes[state] 
        return self.nodes[state]
        






        


