from random import shuffle

# TODO: allow user to choose symbols or letters for suits
# suits = ["\u2664", "\u2661", "\u2662", "\u2667"]
suits = ["C", "D", "S", "H"]
rank = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def line_break():
    print("\n", end="")


class Card:
    def __init__(self, suit: str, rank: tuple):
        # id is used to concisely display the card
        self.__rank = rank[1]
        self.__suit = suit
        self.__id = f"{rank[0]}{suit}"

    @property
    def suit(self):
        return self.__suit

    @property
    def rank(self):
        return self.__rank

    @property
    def id(self):
        return self.__id


class Deck:
    def __init__(self):
        self.__cards = self.initialize_deck()

    @property
    def cards(self):
        return self.__cards

    def initialize_deck(self):
        deck = []
        for suit in suits:
            for i in range(2, 15):
                card = Card(suit, (rank[i - 2], i))
                deck.append(card)
        shuffle(deck)
        return deck


class Player:
    unique_id = 1

    def __init__(self):
        self.__id = Player.unique_id
        self.__hole = ()
        # How many of each suit are in player's hand. Updated on each deal.
        Player.unique_id += 1
        return

    @property
    def hole(self):
        return self.__hole

    @hole.setter
    def hole(self, cards: tuple):
        self.__hole = cards

    @property
    def id(self):
        """The id property."""
        return self.__id


class Dealer:

    streets = {"3": "Flop", "4": "Turn", "5": "River"}

    def __init__(self, players=2):
        self.__deck = self.get_new_deck()
        self.__players = [Player() for i in range(players)]
        self.__community_cards = []

        self.deal_to_players()
        self.deal_flop()
        self.deal_turn()
        self.deal_river()
        return

    def burn_card(self):
        self.remaining_cards().pop()
        return

    def deal_card(self):
        card = self.remaining_cards().pop()
        return card

    def deal_flop(self):
        self.burn_card()
        [self.deal_to_community_cards() for i in range(3)]
        return

    def deal_river(self):
        self.burn_card()
        self.deal_to_community_cards()
        return

    def deal_to_community_cards(self):
        card = self.deal_card()
        self.__community_cards.append(card)

    def deal_to_players(self):
        for player in self.__players:
            hole = []
            for i in range(2):
                card = self.deal_card()
                hole.append(card)
            player.hole = tuple(sorted(hole, key=lambda card: card.rank, reverse=True))
        return

    def deal_turn(self):
        self.burn_card()
        self.deal_to_community_cards()
        return

    def get_new_deck(self):
        return Deck()

    def hand_calculator(self, player_id: int):
        return HandCalculator(
            self.__players[player_id - 1].hole, self.__community_cards, player_id
        )

    def remaining_cards(self):
        return self.__deck.cards

    def show_community_cards(self):
        cards = self.__community_cards
        print(f"{self.which_street(len(cards)):8}:", end="")
        [print(f" {card.id}", end="") for card in cards]
        line_break()
        return

    def show_players_hands(self):
        for player in self.__players:
            print(f"Player {player.id}:", end="")
            [print(f" {card.id:2}", end="") for card in player.hole]
            line_break()
        return

    def show_remaining_cards(self):
        [print(card.id) for card in self.remaining_cards()]
        return

    def which_street(self, length: int):
        """Return which street is on display based on length of community cards"""
        return self.streets.get(str(length))


class HandCalculator:
    """This object should only exist after a flop and it should not persist
    for more than one street to prevent duplicate counts."""

    def __init__(self, hole: tuple, community_cards: list, player_id: int):
        self.__player_id = player_id
        self.__hole = hole
        self.__community_cards = community_cards
        self.__hand = self.sort_hand_by_rank()
        self.__suit_count = self.set_suit_count()
        self.__hands = {
            "high card": self.__hand[0],
            "kicker": self.__hand[1],
            "one pair": 0,
            "two pair": 0,
            "set": 0,
            # "straight": 0,
            # "flush": 0,
            "full house": 0,
            "quads": 0,
            # "staight flush": 0,
            # "royal flush": 0,
        }

        self.__flush = []
        # Set None or a str value with a suit name to has_flush
        has_flush = self.check_for_flush()
        self.__straight = []
        has_straight = self.check_for_straight()
        self.__straight_flush = False
        self.__royal_flush = False

        if has_straight:
            # set_straight() needs to be called before alert_straight()
            self.set_straight(has_straight[0], has_straight[1])
            if self.__straight[0].rank == 14 and has_flush:
                self.alert_straight("royal flush", "650,000")
                self.__royal_flush = True
            elif has_flush:
                self.__straight_flush = True
                self.alert_straight("straight flush", "65,000")
            self.alert_straight()
        # We only call set_flush() and alert_flush() if has_flush and
        # not has_straight.
        elif has_flush:
            self.set_flush(has_flush)
            self.alert_flush(has_flush)

    def alert_flush(self, suit):
        print(f"Player {self.__player_id} hit a flush! 1/500 chance")

        print(f"From player hole :", end="")
        [print(f" {card.id}", end="") for card in self.__hole if card.suit == suit]
        line_break()

        print(f"{'From board cards':} :", end="")
        [
            print(f" {card.id}", end="")
            for card in self.__community_cards
            if card.suit == suit
        ]
        line_break()

        print(f"{'Sorted flush':17}:", end="")
        [print(f" {card.id}", end="") for card in self.__flush]
        line_break()
        return

    def alert_straight(self, type="straight", chance="250"):
        print(f"Player {self.__player_id} hit a {type}! 1/{chance} chance")

        print(f"From player hole :", end="")
        [
            print(f" {card.id}", end="")
            for card in self.__hole
            if card in self.__straight
        ]
        line_break()

        print(f"From board cards :", end="")
        [
            print(f" {card.id}", end="")
            for card in self.__community_cards
            if card in self.__straight
        ]
        line_break()

        print(f"{'Sorted straight':17}:", end="")
        [print(f" {card.id}", end="") for card in self.__straight]
        line_break()
        return

    def check_for_flush(self):
        for suit, count in self.__suit_count.items():
            if count >= 5:
                return suit

    def check_for_straight(self):
        for i in range(0, 2):
            temp = [card.rank for card in self.__hand[i : i + 5]]
            high = self.__hand[i].rank
            low = self.__hand[i + 5].rank
            # Must be a unique set of five ranks with a difference of 4
            if high - low == 4 and len(set(temp)) == 5:
                return i, i + 5

    def print_hand(self):
        print(f"Player {self.__player_id} hand:")
        [print(card.id, end="") for card in self.__hand]
        return

    def print_suit_count(self):
        print(f"Player {self.__player_id} Suit Count:")
        for k, v in self.__suit_count.items():
            print(f"{k}: {v}")

    def set_flush(self, suit: str):
        [self.__flush.append(card) for card in self.__hand if card.suit == suit]
        # If there are 6 or 7 of the same suit in the hand, only keep top 5
        if len(self.__flush) > 5:
            self.__flush = self.__flush[:5]
        return

    def set_straight(self, low: int, high: int):
        self.__straight = self.__hand[low:high]
        return

    def set_suit_count(self):
        temp_suit_count = {suit: 0 for suit in suits}
        for card in self.__hand:
            temp_suit_count[card.suit] += 1
        return temp_suit_count

    def sort_hand_by_rank(self):
        temp = list(self.__hole) + self.__community_cards
        sorted_hand = sorted(temp, key=lambda card: card.rank, reverse=True)
        return sorted_hand


def main():
    d = Dealer()

    # d.deal_to_players()
    # d.show_players_hands()
    # d.deal_flop()
    # d.show_community_cards()
    # d.deal_turn()
    # d.show_community_cards()
    # d.deal_river()
    # d.show_community_cards()
    h = d.hand_calculator(1)
    h = d.hand_calculator(2)
    # h.print_suit_count()


for i in range(100):
    # print(i)
    main()
