from enum import Enum
from typing import Optional

from pokerbot.coup_bot.player import Player


class Character(Enum):
    Duke = "duke"
    Assassin = "assassin"
    Captain = "captain"
    Ambassador = "ambassador"
    Contessa = "contessa"


class Card:
    """
    The card in the game represents a character.
    Each card has a owner, set to be None if it is in the deck.
    If the card's owner is not None, the card is alive if card.alive is True.
    """

    def __init__(self, character: Character, owner: Player):
        self.character = character
        self.owner = owner
        self.alive = True


