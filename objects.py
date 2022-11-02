# TODO: are you using this? Doesn't seem like it
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

    def deal_test_hands(self):
        """To test specific hands."""

        def get_user_card_input(j: int) -> list:
            some_list = []
            for i in range(j):
                c = input(f"  Card {i+1}:")
                r = c[0]
                s = c[1]
                rank = Deck.rank.index(r)
                card = Card(s, (r, rank + 2))
                print(card)
                print(card.rank)
                some_list.append(card)
            return some_list

        for player in self.players:
            print(f"Player {player.id}:")
            hole = get_user_card_input(2)
            player.hole = sorted(hole, reverse=True)

        print("Board Cards:")
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


class HandCalculator:
    """Takes a Player object and a deck of dealt cards and calculates the
    Player's valid hands and ranks them."""

    def __init__(self, community_cards: list, player: Player):
        # The order of these attributes should be fixed, as calculating the
        # value of one usually depends on calculating the previous ones.
        self.player = player
        self.hole = player.hole
        # TODO:: Might not need the comm_cards attr
        self.comm_cards = community_cards
        self.dealt = sorted(self.hole + self.comm_cards, reverse=True)

        self.report_hands_to_player()

    def report_hands_to_player(self):
        self.player.hands = self.get_hands(self.dealt)

    def get_hands(self, cards: list) -> dict:
        hands = self.matches_check(cards)
        hands = self.sort_matches(hands)
        hands = self.full_house_check(hands)
        hands = self.two_pair_check(hands)

        straight = self.straight_check(cards)
        flush = self.flush_check(cards)
        straight_or_flush = self.which_straight_or_flush(straight, flush)
        if straight_or_flush:
            hands = straight_or_flush
        return hands

    def which_straight_or_flush(self, straight: int, flush: int) -> dict:
        if flush and straight == flush[-1] and straight - 4 == flush[0]:
            if straight == 14:
                return {"Royal Flush": straight}
            return {"Straight Flush": straight}
        elif straight:
            return {"Straight": straight}
        elif flush:
            return {"Flush": flush[-1]}
        return

    def straight_check(self, cards: list) -> int:
        ranks = [card.rank for card in cards]
        for rank in ranks:
            test_range = range(rank, rank - 5, -1)
            if set(test_range).issubset(ranks):
                return max(test_range)

        ace_five = [2, 3, 4, 5, 14]
        if set(ace_five).issubset(ranks):
            return 5

    def flush_check(self, cards: list) -> list:
        suited_count = {}
        for card in cards:
            suit = card.suit
            if suit in suited_count:
                suited_count[suit] += 1
            else:
                suited_count[suit] = 1
        flush = None
        for suit, count in suited_count.items():
            if count >= 5:
                ranks = [card.rank for card in cards if card.suit == suit]
                flush = sorted(ranks)
        return flush

    def two_pair_check(self, hands: dict) -> dict:
        if "Set" not in hands and "High Pair" in hands and "Low Pair" in hands:
            hands["Two Pair"] = hands.get("High Pair")
        return hands

    def full_house_check(self, hands: dict) -> dict:
        if "Set" in hands and "High Pair" in hands:
            hands["Full House"] = hands.get("Set")
        return hands

    def matches_check(self, cards: list) -> dict:
        """Check for which cards match among the hole and comm cards."""

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

    def sort_matches(self, matches: dict) -> dict:
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
                low_pair = hands.get("Low Pair")
                # Ensure a third pair doesn't overwrite the lower of first two
                if low_pair == 0 or (low_pair != 0 and rank > low_pair):
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

        hands = self.add_high_and_low_cards_to_hands(hands)

        return hands

    def add_high_and_low_cards_to_hands(self, hands: dict) -> dict:
        # We only check against the matched ranks (ranks that are in pairs,
        # sets, or quads) because kickers are irrelevant in straights/flushes.
        matched_ranks = hands.values()
        dealt_ranks = []
        for card in self.dealt:
            if card.rank not in matched_ranks:
                dealt_ranks.append(card.rank)

        dealt_ranks.sort(reverse=True)
        length = len(dealt_ranks)
        hands["High Card"] = dealt_ranks[0] if dealt_ranks else 0
        hands["Second Kicker"] = dealt_ranks[1] if length > 1 else 0
        hands["Third Kicker"] = dealt_ranks[2] if length > 2 else 0

        return {k: v for k, v in hands.items() if v > 0}

class WinCalculator:

    rank_types = [
        "Royal Flush",
        "Straight Flush",
        "Quads",
        "Full House",
        "Flush",
        "Straight",
        "Set",
        "Two Pair",
        "High Pair",
        "High Card",
    ]

    def __init__(self, players: list):
        self.players = players
        self.hands = sorted([(player.id, player.hands) for player in players])

        top_hands = self.get_top_hands(self.hands)
        for pid, pdata in top_hands:
            print(pid)
            print(f"  {pdata}\n")
            # input("")

        win = self.determine_winner(top_hands)
        if win:
            print("--------")
            print(win)
            print("--------")
            # input("")
        # self.determine_winner(top_hands)

    def determine_winner(self, top_hands: list) -> list:
        def royal_flush_tie(top_hands: list, hand_type: str) -> list:
            """Multiple players have a royal flush can occur only if the royal
            flush is entirely on the board. So, there is no winner."""
            winners = []
            for pid, data in top_hands:
                winners.append((pid, "Royal Flush"))
            return winners

        def straight_flush_tie(top_hands: list, hand_type: str) -> list:
            """If multiple players have a straight, a flush, or a straight
            flush, the player(s) with the highest card in the hand win(s).
            So, return a list of all players that have the highest card."""
            high_card = 0

            for pid, data in top_hands:
                if data.get(hand_type) and data.get(hand_type) > high_card:
                    high_card = data.get(hand_type)
                    hand_type = hand_type

            winners = []
            for pid, data in top_hands:
                if data.get(hand_type) == high_card:
                    winners.append((pid, f"{hand_type}, {high_card} High"))
            return winners

        func_call = {
            "Royal Flush": royal_flush_tie,
            "Straight Flush": straight_flush_tie,
            "Quads": print,
            "Full House": print,
            "Flush": straight_flush_tie,
            "Straight": straight_flush_tie,
            "Set": print,
            "Two Pair": print,
            "High Pair": print,
            "High Card": print,
        }

        sample = top_hands[0][1]
        for rank in self.rank_types:
            if rank in sample:
                winners = func_call[rank](top_hands, rank)
                return winners

    def get_top_hands(self, hands: list) -> dict:
        sorted_players = {rank: [] for rank in self.rank_types}

        for p_id, p_data in self.hands:
            for rank in sorted_players:
                if rank in p_data:
                    sorted_players[rank].append((p_id, p_data))
                    break
        # Remove empty keys
        sorted_players = {k: v for k, v in sorted_players.items() if v}
        # Only return highest ranked players/top hands
        for rank in self.rank_types:
            if rank in sorted_players:
                top_hands = sorted_players.get(rank)
                return top_hands


def main(d: Dealer):

    # TODO: make an 'auto-deal' func that automates these
    d.deal_to_players()
    d.deal_flop()
    d.deal_turn()
    d.deal_river()

    # d.deal_test_hands()

    for player in d.players:
        h = HandCalculator(d.community_cards, player)

        print(h.hole)
        print(h.comm_cards)
        print("**********")
        # hands = h.get_hands(h.dealt)

    w = WinCalculator(d.players)
    print("----------")

    # print(hands)
    # if "Two Pair" in hands:
    #     input("")
    # print("**********")

    # s = h.straight_check(h.dealt)
    # if s:
    #     print(s)
    #     input("")
    #
    # f = h.flush_check(h.dealt)
    # if f:
    #     print(f)
    #     input("")

    # matches = h.matches_check(h.dealt)
    # print(matches)
    # sorted_matches = h.sort_matches(matches)

    # for k, v in sorted_matches.items():
    #     print(k, ':', v)

    # if "Low Pair" in sorted_matches:
    #     input("")
    # if "Set" in sorted_matches and "High Pair" in sorted_matches:
    #     input("")
    # if "Set" in sorted_matches and "Low Pair" in sorted_matches:
    #     input("")
    # if "Quads" in sorted_matches:
    #     input("")

    line_break()
    line_break()


i = 2
players = [Player(i + 1) for i in range(i)]

for i in range(200000):
    d = Dealer(players)
    main(d)
