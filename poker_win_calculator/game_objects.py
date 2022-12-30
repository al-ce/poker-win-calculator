from poker_win_calculator.helpers import (
    all_card_combos,
    debug_print,
    line_break,
)
from random import shuffle


class Card:
    def __init__(self, suit: str, rank: tuple):
        # id is used to concisely display the card
        self.rank = rank[1]
        self.suit = suit
        self.location = -1
        self.id = f"{rank[0]}{suit}"

    def __lt__(self, other):
        return self.rank < other.rank

    def __repr__(self):
        return f"{self.id}"


class Deck:
    rank = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["C", "D", "S", "H"]

    def __init__(self):
        self.cards = self.initialize_deck()

    def initialize_deck(self) -> list:
        """Return a shuffled deck (randomized list of Cards). Called on each
        round."""
        deck = []
        for suit in self.suits:
            for i in range(2, 15):
                card = Card(suit, (self.rank[i - 2], i))
                deck.append(card)
        shuffle(deck)
        return deck


class Player:
    def __init__(self, id: int):
        self.id = id
        self.hole = []
        # Hands are given to this object by the HandCalculator
        self.hands = None
        self.highest_hand = None

    def __repr__(self):
        return f"Player {self.id}: {self.hole}"


class Dealer:

    streets = {"3": "Flop", "4": "Turn", "5": "River"}

    def __init__(self, players: list):
        self.deck = self.get_new_deck()
        # List of Player() objects
        self.players = players
        self.community_cards = []

    def get_round_info(self):
        info = (
            "----------------------------------------\n"
            f"Board:    {self.community_cards}\n"
        )
        for player in self.players:
            info += f"{player}\n"
        return info

    def print_round(self):
        print("----------------------------------------")
        print(f"Board:    {self.community_cards}")
        [print(player) for player in self.players]
        line_break()

    def burn_card(self):
        self.deck.pop()

    def deal_test_hands(self):
        """Allow user to test specific hands."""

        # Temp list to test for duplicate entries by user
        test_list = []

        def get_user_card_input(j: int) -> list:
            usr_list = []
            for i in range(j):
                while True:
                    c = input(f"  Card {i+1}: ")
                    c = c.upper()
                    if c not in all_card_combos():
                        print("Invalid Card")
                    elif c in test_list:
                        print("Duplicate Card")
                    else:
                        test_list.append(c)
                        break
                r = "10" if c[0] == "1" else c[0]
                s = c[2] if c[1] == "0" else c[1]
                rank = Deck.rank.index(r)
                card = Card(s, (r, rank + 2))
                usr_list.append(card)
            return usr_list

        for player in self.players:
            debug_print(f"Player {player.id}:")
            hole = get_user_card_input(2)
            player.hole = sorted(hole, reverse=True)

        debug_print("Board Cards:")
        comm_cards = get_user_card_input(5)
        self.community_cards = comm_cards

    def deal_card(self, location=0) -> Card:
        card = self.deck.pop()
        card.location = location
        # Place card at the "bottom" of the deck so it can be used in
        # calculating odds. Since it's marked by the location attribute, we
        # know whether it's really in the deck (-1) or elsewhere (0, 1, 2, ...)
        self.deck.insert(0, card)
        return card

    def deal_full_round(self):
        """Deal to all players, deal all community cards to the board."""
        self.deal_to_players()
        self.deal_flop()
        self.deal_turn()
        self.deal_river()

    def deal_flop(self):
        self.burn_card()
        [self.deal_to_community_cards() for i in range(3)]

    def deal_river(self):
        self.deal_to_community_cards()

    def deal_to_community_cards(self):
        card = self.deal_card()
        self.community_cards.append(card)

    def deal_to_players(self):
        for player in self.players:
            hole = []
            for _ in range(2):
                card = self.deal_card(player.id)
                hole.append(card)
            player.hole = sorted(hole, reverse=True)

    def deal_turn(self):
        self.burn_card()
        self.deal_to_community_cards()

    def get_new_deck(self) -> list:
        """Returns a shuffled Deck of Cards."""
        return Deck().cards

    def which_street(self, length: int) -> str:
        """Return which street is on display based on len of community cards"""
        return self.streets.get(str(length))
