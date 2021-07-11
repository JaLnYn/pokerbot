
Class Agent:





Class Player:
    def __init__(self, cards, name="Bot", agent=None)
        self.coins = 2
        self.cards = cards
        self.name = name
        self.agent = agent
        self.ded = 0

    def action(self, state):
        action = self.agent.action(state, self)
        return action
    
    def block(self, state):
        action = self.agent.block(state, self)
        return action

    def challange(self, state):
        challenge = self.agent.challenge(state, self)
        return challenege

    def lose_card(self):
        # this function returns if ded
        del self.cards[0]
        if len(self.cards) == 0:
            ded = 1






