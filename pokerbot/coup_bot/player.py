from pokerbot.coup_bot.card import Character
from pokerbot.coup_bot.coup import State


class Agent:
    def action(self, state, player):
        toDo = nn.forward(state, player)
        Action.action(action)


class Player:
    """
    coins: The number of coins owned by a player. Should be 2 when the game starts
    cards: The
    """
    def __init__(self, cards, name="Bot", agent=None):
        self.coins = 2
        self.cards = cards
        self.name = name
        self.agent = agent
        self.dead = False

    def action(self, state):
        if self.dead:
            return -1

        action = self.agent.action(state, self)
        return action
    
    def block(self, state):
        if self.dead:
            return -1

        action = self.agent.block(state, self)
        return action

    def challenge(self, state: State):
        if self.dead:
            return -1

        challenge = self.agent.challenge(state, self)
        return self.challenge()

    def lose_card(self):
        # this function returns if dead
        del self.cards[0]
        if len(self.cards) == 0:
            dead = 1






