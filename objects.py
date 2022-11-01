from functools import total_ordering
from random import shuffle


def line_break():
    print("\n", end="")


def debug_print(string):
    print(string)


@total_ordering
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

    def initialize_deck(self):
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

    def __repr__(self):
        return f"Player {self.id}: {self.hole}"


class Dealer:

    streets = {"3": "Flop", "4": "Turn", "5": "River"}

    def __init__(self, players: list):
        self.deck = self.get_new_deck()
        # List of Player() objects
        self.players = [player for player in players]
        self.community_cards = []

    def burn_card(self):
        self.deck.pop()

    def deal_card(self, location=0):
        card = self.deck.pop()
        card.location = location
        # Place card at the "bottom" of the deck so it can be used in
        # calculating odds. Since it's marked by the location attribute, we
        # know whether it's really in the deck (-1) or elsewhere (0, 1, 2, ...)
        self.deck.insert(0, card)
        return card

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
            for i in range(2):
                card = self.deal_card(player.id)
                hole.append(card)
            player.hole = sorted(hole, reverse=True)

    def deal_turn(self):
        self.burn_card()
        self.deal_to_community_cards()

    def get_new_deck(self):
        """Returns a shuffled Deck of Cards."""
        return Deck().cards

    def which_street(self, length: int):
        """Return which street is on display based on length of community cards"""
        return self.streets.get(str(length))


class HandRanker:
    """Takes a Player object and a deck of dealt cards and calculates the
    Player's valid hands and ranks them."""

    def __init__(self, community_cards: list, player: Player):
        # The order of these attributes should be fixed, as calculating the
        # value of one usually depends on calculating the previous ones.
        self.player = player
        self.hole = player.hole
        self.comm_cards = community_cards
        # NOTE: Do you need this?
        self.dealt = sorted(self.hole + self.comm_cards, reverse=True)

        self.matches = self.matches_check(self.dealt)

        # TODO: Just make the dict all at once from functions
        self.hands = {}

    def matches_check(self, cards: list):
        """Check for which cards match in among the hole and comm cards."""

        matches = {}
        for card in cards:
            rank = card.rank
            if rank in matches:
                matches[rank] += 1
            else:
                matches[rank] = 1
        # Return a copy of matches dict with only keys with list of len 2+
        matches = {rank: size for rank, size in matches.items() if size > 1}
        return matches

    def sort_matches(self, matches: dict):
        match_types = {2: "High Pair", 3: "Set", 4: "Quads"}
        hands = {
            "Low Pair": 0,
            "High Pair": 0,
            "Set": 0,
            "Quads": 0,
        }
        for rank, size in matches.items():
            match_type = match_types[size]
            temp = hands.get(match_type)
            if size == 2 and rank > temp:
                hands[match_type] = rank
                hands["Low Pair"] = temp
            elif size == 2 and rank < temp:
                hands["Low Pair"] = rank

            elif size == 3 and rank > hands.get("Set") and temp > 0:
                hands["Low Pair"] = hands.get("High Pair")
                hands["High Pair"] = temp
                hands["Set"] = rank
            elif size == 3 and rank < temp:
                hands["Low Pair"] = hands.get("High Pair")
                hands["High Pair"] = rank

            elif rank > temp:
                hands[match_type] = rank

        hands = self.add_hole_cards_to_hands(hands)

        return hands

    def add_hole_cards_to_hands(self, hands: dict):
        matched_ranks = hands.values()
        high_card = self.player.hole[0].rank
        low_card = self.player.hole[1].rank
        if low_card not in matched_ranks:
            hands["Low Card"] = low_card
        if high_card not in matched_ranks:
            hands["High Card"] = high_card

        return {k: v for k, v in hands.items() if v > 0}


def main(d: Dealer):

    d.deal_to_players()
    d.deal_flop()
    # d.show_community_cards()
    d.deal_turn()
    # d.show_community_cards()
    d.deal_river()

    for player in d.players:
        h = HandRanker(d.community_cards, player)
        print(h.hole)
        print(h.comm_cards)
        matches = h.matches_check(h.dealt)
        print(matches)
        sorted_matches = h.sort_matches(matches)

        for k, v in sorted_matches.items():
            print(k, ':', v)

        # if "Low Pair" in sorted_matches:
        #     input("")
        # if "Set" in sorted_matches and "High Pair" in sorted_matches:
        #     input("")
        if "Set" in sorted_matches and "Low Pair" in sorted_matches:
            input("")
        # if "Quads" in sorted_matches:
        #     input("")

        line_break()
    line_break()
    line_break()


i = 2
players = [Player(i + 1) for i in range(i)]

for i in range(200000):
    d = Dealer(players)
    main(d)
