import logging

from random import shuffle

# TODO: allow user to choose symbols or letters for suits and maybe mess with
# ANSI escape sequences for colors
# suits = ["\u2664", "\u2661", "\u2662", "\u2667"]
suits = ["C", "D", "S", "H"]
# suits = ["\033[94mC\033[00m", "\033[91mD\033[00m", "\033[94mS\033[00m", "\033[91mH\033[00m"]
rank = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

# Helper functions
# def prRed(skk):
#     print("\033[91m {}\033[00m".format(skk), end="")
#
#
# def prGreen(skk):
#     print("\033[92m {}\033[00m".format(skk), end="")
#
#
# def prYellow(skk):
#     print("\033[93m {}\033[00m".format(skk), end="")
#
#
# def prLightPurple(skk):
#     print("\033[94m {}\033[00m".format(skk), end="")
#
#
# def prPurple(skk):
#     print("\033[95m {}\033[00m".format(skk), end="")
#
#
# def prCyan(skk):
#     print("\033[96m {}\033[00m".format(skk), end="")
#
#
# def prLightGray(skk):
#     print("\033[97m {}\033[00m".format(skk), end="")
#
#
# def prBlack(skk):
#     print("\033[98m {}\033[00m".format(skk), end="")
#
# prColor = {
#         1: prYellow,
#         2: prPurple,
#         3: prGreen,
#         4: prRed,
#         5: prCyan,
#         }


def line_break():
    print("\n", end="")


def get_rank(card):
    """Used to sort lists of cards by rank in sorted() functs."""
    return card.rank


def debug_print(string):
    print(string)


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
        self.__hole = []
        # How many of each suit are in player's hand. Updated on each deal.
        return

    @property
    def hole(self):
        return self.__hole

    @hole.setter
    def hole(self, cards: list):
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
            player.hole = sorted(hole, key=get_rank, reverse=True)
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


class HandRanker:
    # This object should only exist after a flop and it should not persist
    # for more than one street to prevent duplicate counts.

    match_dict = {2: "pair", 3: "set", 4: "quads"}

    # @param deck: list of all Card objects minus burned ones
    # @param player: Player object with unique id and copy of hole cards.
    # Note that the deck has the hole cards as well, with location attribute.
    def __init__(self, deck: list, player: Player):
        # The order of these attributes should be fixed, as calculating the
        # value of one usually depends on calculating the previous ones.
        self.__player = player
        self.__deck = deck
        self.__hole = player.hole
        self.__high_card = player.hole[0], player.hole[0].rank
        self.__kicker = player.hole[1], player.hole[1].rank
        self.__comm_cards = [card for card in self.deck if card.location == 0]
        self.__dealt = sorted(self.hole + self.comm_cards, key=get_rank, reverse=True)

        # Matches made by the table, either a pair in hand, or pairs, sets,
        # quads made with or by the community cards
        self.__table_matches = self.matches_check(self.dealt)

        # Dict of only the highest matches + low pair.
        self.__table_highest_matches = (
            self.get_highest_matches(self.table_matches) if self.table_matches else None
        )

        self.__high_pair = self.check_pair()
        self.__low_pair = self.check_low_pair()
        self.__two_pair = self.check_two_pair()
        self.__set = self.check_set()
        self.__full_house = self.check_full_house()
        self.__quads = self.check_quads()

        self.__suited = self.count_suited_cards()
        self.__flush = self.check_flush()
        self.__straight = self.check_straight()
        self.__straight_flush = self.check_straight_flush()
        self.__royal_fush = self.check_royal_flush()

    def __repr__(self) -> str:
        # TODO: make some functions to help you format these correctly
        hbr = self.hands_by_rank()
        message = f"{str(self.comm_cards)}\n{str(self.hole)}\n"
        if not hbr:
            return f"Player {self.player.id} made no hands."
        message += f"Player {self.player.id}'s hands:\n"
        for k, v in hbr.items():
            message += f"{k}: "
            message += str(v)
            message += "\n"

        return message

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
    def high_card(self):
        return self.__high_card

    @property
    def kicker(self):
        return self.__kicker

    @property
    def comm_cards(self):
        return self.__comm_cards

    @property
    def suited(self):
        return self.__suited

    @property
    def dealt(self):
        return self.__dealt

    @property
    def flush(self):
        return self.__flush

    @property
    def high_pair(self):
        return self.__high_pair

    @property
    def low_pair(self):
        return self.__low_pair

    @property
    def two_pair(self):
        return self.__two_pair

    @property
    def set(self):
        return self.__set

    @property
    def quads(self):
        return self.__quads

    @property
    def full_house(self):
        return self.__full_house

    @property
    def straight(self):
        return self.__straight

    @property
    def straight_flush(self):
        return self.__straight_flush

    @property
    def royal_flush(self):
        return self.__royal_fush

    @property
    def table_matches(self):
        return self.__table_matches

    @property
    def table_highest_matches(self):
        return self.__table_highest_matches

    def check_pair(self):
        thm = self.table_highest_matches
        if thm and "pair" in thm:
            return thm["pair"]
        return

    def check_low_pair(self):
        thm = self.table_highest_matches
        if thm and "low pair" in thm:
            return thm["low pair"]
        return

    def check_set(self):
        thm = self.table_highest_matches
        if thm and "set" in thm:
            return thm["set"]
        return

    def check_quads(self):
        thm = self.table_highest_matches
        if thm and "quads" in thm:
            return thm["quads"]
        return

    def check_full_house(self):
        thm = self.table_highest_matches
        if not thm:
            return
        set = self.set
        high_pair = self.high_pair
        if set and high_pair:
            full_house = (high_pair, set)
        else:
            return
        return full_house

    def check_two_pair(self):
        thm = self.table_highest_matches
        if not thm:
            return
        if self.low_pair and self.high_pair:
            two_pair = (self.high_pair, self.low_pair)
        else:
            return
        return two_pair

    def hands_by_rank(self):
        # TODO: Change the data types for some of these so they're more easily
        # accessible. e.g. nested dicts? might be bettes than nested tuples
        hands = {
            "Kicker": (self.kicker, 0),
            "High Card": (self.high_card, 1),
            "Pair": (self.high_pair, 2),
            "Two Pair": (self.two_pair, 3),
            "Set": (self.set, 4),
            "Straight": (self.straight, 5),
            "Flush": (self.flush, 6),
            "Full House": (self.full_house, 7),
            "Quads": (self.quads, 8),
            "Straight Flush": (self.straight_flush, 9),
            "Royal Flush": (self.royal_flush, 10),
        }

        # Only return actual winning hands, not "None".
        hands = {k: hands[k] for k, v in hands.items() if v[0]}
        return hands

    def get_highest_matches(self, matches: dict):
        """From a dict of all matches, return a dict of only the highest and the low pair."""
        temp = {}
        for rank, card_data in matches.items():
            cards = card_data[0]
            match_type = card_data[1]

            # If we haven't entered this match yet, enter it and continue.
            if match_type not in temp:
                temp[match_type] = cards, rank
                continue

            # If we have entered it but its rank is lower, set it as the low
            # pair unless it's quads, which makes it irrelevant.

            # NOTE: If the "low pair" is a pair, the length of the list of its
            # cards will be 2, but 3 if the "low pair" is a set (e.g. if the
            # player makes two sets with the boards high and low pair)

            if rank <= temp[match_type][1]:
                if match_type != "quads":
                    temp["low pair"] = cards, rank
        return temp

    def matches_check(self, cards: list, *args: list):
        """Check for which cards match in a list. If more than one list is
        passed to the function, check which cards from those lists match the
        rank of the original list."""

        match_types = ["pair", "set", "quads"]
        matches = {}

        for card in cards:
            rank = card.rank

            if rank in matches:
                matches[rank][0].append(card)
            else:
                matches[rank] = [[card], ""]

            # Update the type of match based on length of matching cards
            cards = matches[rank][0]
            matches[rank][1] = match_types[len(cards) - 2]

            if not args:
                continue

            card_lists = [card for arg in args for card in arg]
            for other_card in card_lists:
                if other_card.rank == rank and other_card not in matches[rank][0]:
                    matches[rank][0].append(other_card)

            # Update the type of match based on length of matching cards
            matches[rank][1] = match_types[len(cards) - 2]

        # Return a copy of matches dict with only keys with list of len 2+
        matches = {
            key: matches[key] for key, cards in matches.items() if len(cards[0]) > 1
        }
        return matches

    def is_ace_five_straight(self, card_ranks: list):
        ace_five = [2, 3, 4, 5, 14]
        if sorted(card_ranks) == ace_five:
            return True
        return

    def check_straight(self):
        straights = []
        # The dealt list is sorted low to high. We need a unique set of min five
        # consecutive numbers that includes at least one card from the hole.
        # We check each of the three sets of cards of length 5 in ascending
        # order.
        for i in range(3):
            # Since we're copying the list, we don't have to worry about
            # IndexErrors if we try to copy beyond the original list.
            temp = self.dealt[i : i + 5]
            temp = list(sorted(set(temp), key=get_rank))
            temp_ranks = [card.rank for card in temp]

            # Check if it's a special case of A5 straight
            if self.is_ace_five_straight(temp_ranks):
                ace = [temp[-1]]
                five_to_two = sorted(temp, key=get_rank, reverse=True)[1:]
                ace_five_straight = five_to_two + ace
                straights.append(ace_five_straight)
                continue

            # We know what a straight would look like, starting from the known
            # low. Check that against the current set of 5 cards.
            low = temp_ranks[0]
            high = low + 5
            would_be_straight = list(range(low, high))
            if temp_ranks == would_be_straight:
                straights.append(temp)

        # If more than one straight was found, return the highest one.
        if len(straights) > 1:
            g = lambda cards: sum([card.rank for card in cards])
            highest_straight = sorted(straights, key=g, reverse=True)[0]
            return highest_straight
        elif straights:
            return straights[0]
        return

    def check_straight_flush(self):
        if self.straight and self.flush and self.straight == self.flush:
            # Get rid of straight and flush to avoid redundant hands.
            self.__straight = None
            self.__flush = None
            return self.straight
        return

    def check_royal_flush(self):
        sf = self.straight_flush
        if sf and sf[0].rank == 14:
            # Get rid of straight flush to avoid redundant hands.
            self.__straight_flush = None
            return sf
        return

    def count_suited_cards(self):
        suit_count = {}
        # Which suits does the player have in their hand?
        dealt_suits = [card.suit for card in self.dealt]
        for suit in suits:
            if suit in dealt_suits:
                suited = [card for card in self.dealt if card.suit == suit]
                suited.sort(key=get_rank, reverse=True)
                length = len(suited)
                # If there are six or seven suited cards in the hand for the
                # player, only keep the top five.
                if length > 5:
                    suited = suited[:5]
                suit_count[suit] = (length, suited)
        return suit_count

    def check_flush(self):
        for cards in self.suited.values():
            # If the length (cards[0]) of the suit count is 5, return the flush
            if cards[0] == 5:
                return cards[1]
        return


def main(d: Dealer):

    # syntax: logging.debug/info/error("your statement here")
    level = logging.DEBUG
    fmt = "[%(levelname)s] %(asctime)s - %(message)s"
    logging.basicConfig(level=level, format=fmt)

    d.deal_to_players()
    # d.show_all_players_hands()
    d.deal_flop()
    # d.show_community_cards()
    d.deal_turn()
    # d.show_community_cards()
    d.deal_river()
    # d.show_community_cards()
    h = HandRanker(d.deck, players[0])

    line_break()
    print(h)
    line_break()


i = 2
players = [Player(i + 1) for i in range(i)]

for i in range(200000):
    d = Dealer(players)
    main(d)
