
# TODO: are you using this? Doesn't seem like it
from functools import total_ordering
from random import shuffle


# Helper Functions
def line_break():
    print("\n", end="")


def any_in(items: list, container: iter, are_in: bool) -> bool:
    # Checks if any item from list 'items' is in list 'container'. Returns
    # True of False based on are_in param (are ANY items in/not here?)
    for item in items:
        if item in container and are_in:
            return True
    return False


def all_in(items: list, container: iter, are_in: bool) -> bool:
    # Checks if all items from list 'items' are in list 'container'. Returns
    # True of False based on are_in param (are ALL items in/not here?)
    for item in items:
        if item not in container and are_in:
            return False
    return True


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
    rank = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    suits = ["C", "D", "S", "H"]

    def __init__(self):
        self.cards = self.initialize_deck()

    def initialize_deck(self) -> list:
        # Return a shuffled deck (randomized list of Cards). Called on each
        # round.
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
        # Allow user to test specific hands.

        def get_user_card_input(j: int) -> list:
            some_list = []
            for i in range(j):
                c = input(f"  Card {i+1}:")
                r = c[0]
                s = c[1]
                rank = Deck.rank.index(r)
                card = Card(s, (r, rank + 2))
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
        # Returns a shuffled Deck of Cards.
        return Deck().cards

    def which_street(self, length: int) -> str:
        # Return which street is on display based on len of community cards
        # Useful for printing community cards one street at a time.
        return self.streets.get(str(length))


class HandCalculator:
    # Takes a Player object and a deck of dealt cards and calculates the
    # Player's valid hands and ranks them.

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
        _sf = self.which_straight_or_flush(straight, flush)

        # Return a simplified dict for untie-able/split-pot hands
        rare_flushes = ["Royal Flush", "Straight Flush"]
        if _sf and any_in(rare_flushes, _sf, True):
            return _sf
        elif "Quads" in hands:
            return {"Quads": hands.get("Quads")}
        elif _sf:
            return _sf

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
        pairs = ["One Pair", "Low Pair"]
        if "Set" not in hands and all_in(pairs, hands, True):
            hands["Two Pair"] = hands.get("One Pair")
        return hands

    def full_house_check(self, hands: dict) -> dict:
        full_house = ["Set", "One Pair"]
        if all_in(full_house, hands, True):
            hands["Full House"] = hands.get("Set")
        return hands

    def matches_check(self, cards: list) -> dict:
        # Check for which cards match among the hole and comm cards.

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
        match_types = {2: "One Pair", 3: "Set", 4: "Quads"}
        hands = {
            "Low Pair": 0,
            "One Pair": 0,
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
                hands["Low Pair"] = hands.get("One Pair")
                hands["One Pair"] = temp
                hands["Set"] = rank
            elif size == 3 and rank < temp:
                hands["Low Pair"] = hands.get("One Pair")
                hands["One Pair"] = rank

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
        "One Pair",
        "High Card",
    ]

    card_ranks = [
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "Jack",
        "Queen",
        "King",
        "Ace",
    ]

    def __init__(self, players: list):
        self.players = players
        self.hands = sorted([(player.id, player.hands) for player in players])

        top_hands = self.get_top_hands(self.hands)

        # for pid, pdata in top_hands:
        #     print("1++--++")
        #     print(pid)
        #     print(f"  {pdata}\n")
        #     print("2++--++")

        win = self.determine_winners(top_hands)
        if win:
            print("1--****--")
            print(win)
            print("2--------")
        # self.determine_winner(top_hands)

    def determine_winners(self, top_hands: list) -> str:
        def get_highest_ranked_hand(pdata: list, hand_type: str) -> list:
            # Return the highest rank of a given hand type.
            # top_hands = [(int, {hand_type: rank})]

            _list = sorted(pdata, key=lambda d: d[1][hand_type], reverse=True)
            high_card = _list[0][1].get(hand_type)
            return high_card

        def get_winners(top_hands: list, hand_type: str, high_card: int) -> list:
            # Return a list of all players that have the highest ranking card
            # of a given hand type.
            winners = []
            for pid, data in top_hands:
                if data.get(hand_type) == high_card:
                    winners.append(pid)
            return winners

        def split_pot_msg(winners: list) -> str:
            msg = "Split Pot -"
            for pid in winners:
                msg += f" Player {pid},"
            return msg[:-1]

        def no_kicker_ties(top_hands: list, hand_type: str) -> str:
            # Return the winner/winners for hands that can't be tie-broken by a
            # kicker. Includes Royal + Straight Flush, Quads, Straights, Flush
            high_card = get_highest_ranked_hand(top_hands, hand_type)
            winners = get_winners(top_hands, hand_type, high_card)
            card_rank_str = self.card_ranks[high_card - 2]

            # Tags to put at the end of the message based on hand type
            highs = ["Straight Flush", "Straight", "Flush"]
            tag = " high" if hand_type in highs else "s"
            tag = f"\n{hand_type}, {card_rank_str}{tag}"
            tag = f"\n{hand_type}" if hand_type == "Royal Flush" else tag

            if len(winners) > 1:
                msg = split_pot_msg(winners)
            else:
                msg = f"Player {winners[0]} wins!"

            # NOTE: might want to return a list of winners in addition to this
            # string in case you want to log wins, split a pot, etc.
            return f"{msg}{tag}"


        def one_pair_ties(top_hands: list, hand_type: str) -> str:
            # NOTE: note this is a simpler returned str than no_kicker_ties
            high_card = get_highest_ranked_hand(top_hands, hand_type)
            winners = get_winners(top_hands, hand_type, high_card)
            card_rank_str = self.card_ranks[high_card - 2]
            if len(winners) > 1:
                msg = split_pot_msg(winners)
            else:
                msg = f"Player {winners[0]} wins!"
            return msg


        def full_house_ties(top_hands: list, hand_type: str) -> str:
            # Return the winner[s] of a full house tie. Check the higher set
            # and then the higher pair. If both are tied, split the pot.

            high_card = get_highest_ranked_hand(top_hands, hand_type)
            pair_rank_int = get_highest_ranked_hand(top_hands, "One Pair")
            winners = get_winners(top_hands, hand_type, high_card)
            set_rank_str = self.card_ranks[high_card - 2]
            pair_rank_str = self.card_ranks[pair_rank_int - 2]
            if len(winners) > 1:
                msg = one_pair_ties(top_hands, "One Pair")
                print(f"{msg} {set_rank_str}s Full of {pair_rank_str}s")
                input("")
            else:
                msg = f"Player {winners[0]} wins!"
            return f"{msg}\n{set_rank_str}s Full of {pair_rank_str}s"



        func_call = {
            "Royal Flush": no_kicker_ties,
            "Straight Flush": no_kicker_ties,
            "Quads": no_kicker_ties,
            "Full House": full_house_ties,
            "Flush": no_kicker_ties,
            "Straight": no_kicker_ties,
            "Set": print,
            "Two Pair": print,
            "One Pair": print,
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
        # Return the highest ranked players/top hands.
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

        print("--main--")
        print(h.hole)
        print(h.comm_cards)
        print("**********\n")
        # hands = h.get_hands(h.dealt)

    w = WinCalculator(d.players)

    line_break()
    line_break()


i = 2
players = [Player(i + 1) for i in range(i)]

for i in range(200000):
    d = Dealer(players)
    main(d)
