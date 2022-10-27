from random import shuffle

# TODO: allow user to choose symbols or letters for suits and maybe mess with
# ANSI escape sequences for colors
# suits = ["\u2664", "\u2661", "\u2662", "\u2667"]
suits = ["C", "D", "S", "H"]
# suits = ["\033[94mC\033[00m", "\033[91mD\033[00m", "\033[94mS\033[00m", "\033[91mH\033[00m"]
rank = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def line_break():
    print("\n", end="")


class Card:
    def __init__(self, suit: str, rank: tuple):
        # id is used to concisely display the card
        self.__rank = rank[1]
        self.__suit = suit
        self.__location = -1
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

    @property
    def location(self):
        """Where the card belongs, e.g. the deck (-1), the community cards (0),
        player 1 (1), etc."""
        return self.__location

    @location.setter
    def location(self, value):
        self.__location = value

    def __repr__(self):
        return f"{self.id}"


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
    def __init__(self, id: int):
        self.__id = id
        self.__hole = ()
        # How many of each suit are in player's hand. Updated on each deal.
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

    def __repr__(self):
        return f"Player {self.id}: {self.hole}"


class Dealer:

    streets = {"3": "Flop", "4": "Turn", "5": "River"}

    def __init__(self, players: list):
        self.__deck = self.get_new_deck().cards
        # List of Player() objects
        self.__players = [player for player in players]
        self.__community_cards = []

        return

    @property
    def deck(self):
        return self.__deck

    def burn_card(self):
        self.deck.pop()
        return

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
                card = self.deal_card(player.id)
                hole.append(card)
            player.hole = tuple(sorted(hole, key=lambda card: card.rank, reverse=True))
        return

    def deal_turn(self):
        self.burn_card()
        self.deal_to_community_cards()
        return

    def get_new_deck(self):
        return Deck()

    def show_community_cards(self):
        cards = self.__community_cards
        print(f"{self.which_street(len(cards)):8}:", end="")
        [print(f" {card.id}", end="") for card in cards]
        line_break()
        return

    def show_all_players_hands(self):
        for player in self.__players:
            print(f"Player {player.id}:", end="")
            [print(f" {card.id:2}", end="") for card in player.hole]
            line_break()
        return

    def show_remaining_cards(self):
        [print(card.id) for card in self.deck]
        return

    def which_street(self, length: int):
        """Return which street is on display based on length of community cards"""
        return self.streets.get(str(length))


class HandCalculator:
    """This object should only exist after a flop and it should not persist
    for more than one street to prevent duplicate counts."""

    match_dict = {2: "pair", 3: "set", 4: "quads"}

    # @param deck: list of all Card objects minus burned ones
    # @param player: Player object with unique id and copy of hole cards.
    # Note that the deck has the hole cards as well, with location attribute.
    def __init__(self, deck: list, player: Player):
        # The order of these attributes should be fixed, as calculating the
        # value of one usually depends on calculating the previous ones.
        self.__player = player
        self.__deck = deck
        self.__hole = [card for card in self.deck if card.location == self.player.id]
        self.__comm_cards = [card for card in self.deck if card.location == 0]

        self.__suited = self.count_suited_cards()
        self.__flush = self.flush_check()



    @property
    def player(self):
        return self.__player

    @property
    def deck(self):
        return self.__deck

    @property
    def hole(self):
        return self.__hole

    @property
    def comm_cards(self):
        return self.__comm_cards

    @property
    def suited(self):
        return self.__suited

    @property
    def flush(self):
        return self.__flush

    def count_suited_cards(self):
        suit_count = {}
        # Which suits does the player have in their hand?
        player_suits = [card.suit for card in self.hole]
        for suit in suits:
            # Only add community cards to the suit count if those cards match a
            # suit the player is holding. So, the dictionary can only have 1 to
            # 2 keys in it.
            if suit in player_suits:
                suited = [
                    card for card in self.hole if card.suit == suit
                ]
                suited += [
                    card
                    for card in self.comm_cards
                    if card.suit == suit
                ]
                suited.sort(key=lambda card: card.rank, reverse=True)
                length = len(suited)
                # If there are six or seven suited cards in the hand for the
                # player, only keep the top five.
                if length > 5:
                    suited = suited[:5]
                suit_count[suit] = (length, suited)
        return suit_count

    def flush_check(self):
        for cards in self.suited.values():
            # If the length (cards[0]) of the suit count is 5, return the flush
            if cards[0] == 5:
                return cards[1]
        return


def main(d: Dealer):
    d.deal_to_players()
    d.show_all_players_hands()
    d.deal_flop()
    d.show_community_cards()
    d.deal_turn()
    d.show_community_cards()
    d.deal_river()
    d.show_community_cards()

    h = HandCalculator(d.deck, players[0])


i = 2
players = [Player(i + 1) for i in range(i)]

for i in range(100):
    d = Dealer(players)
    # print(i)
    main(d)
