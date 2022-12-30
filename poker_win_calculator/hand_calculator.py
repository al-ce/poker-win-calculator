from poker_win_calculator.game_objects import Player
from poker_win_calculator.helpers import all_in, none_in


class HandCalculator:
    """Takes a Player object and a deck of dealt cards and calculates the
    Player's valid hands and ranks them."""

    def __init__(self, community_cards: list, player: Player):
        # The order of these attributes should be fixed, as calculating the
        # value of one usually depends on calculating the previous ones.
        self.player = player
        self.hole = player.hole
        self.comm_cards = community_cards
        self.dealt = sorted(self.hole + self.comm_cards, reverse=True)

    def report_hands_to_player(self):
        self.player.hands = self.get_hands(self.dealt)

    def get_hands(self, cards: list) -> dict:
        # Return a simplified dict based on player's hands
        hands = self.matches_check(cards)
        hands = self.sort_matches(hands)

        quads = self.quads_check(hands)
        if quads:
            return quads

        full_house = self.full_house_check(hands)
        if full_house:
            return full_house

        st_or_flush = self.which_straight_or_flush(cards, hands)
        if st_or_flush:
            return st_or_flush

        set_of_three = self.set_check(hands)
        if set_of_three:
            return set_of_three

        two_pair = self.two_pair_check(hands)
        if two_pair:
            return two_pair

        one_pair = self.one_pair_check(hands)
        if one_pair:
            return one_pair
        # If the function makes it here, the best hand is a high card, and all
        # kickers may be needed to break a tie.
        return hands

    def which_straight_or_flush(self, cards: list, hands: dict) -> dict:
        straight = self.straight_check(cards)
        flush: list = self.flush_check(cards)

        if flush and straight == flush[-1] and straight - 4 == flush[0]:
            if straight == 14:
                return {"Royal Flush": straight}
            return {"Straight Flush": straight}
        elif straight:
            return {"Straight": straight}
        elif flush:
            order = ["Flush", "Second", "Third", "Fourth", "Fifth"]
            flush_dict = {}

            for i in range(5):
                flush_dict[order[i]] = flush[-(i + 1)]

            return flush_dict

        return None

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

    def quads_check(self, hands: dict) -> dict:
        if "Quads" in hands:
            return {"Quads": hands.get("Quads")}
        return None

    def two_pair_check(self, hands: dict) -> dict:
        two_pairs = ["One Pair", "Low Pair"]
        if "Set" not in hands and all_in(two_pairs, hands):
            two_pair_dict = {
                "Two Pair": hands.get("One Pair"),
                "Low Pair": hands.get("Low Pair"),
                # High Card is the kicker in this situation
                "High Card": hands.get("High Card"),
            }
            return two_pair_dict
        return None

    def one_pair_check(self, hands: dict) -> dict:
        pair_override = ["Two Pair", "Set", "Full House", "Quads"]
        if "One Pair" in hands and none_in(pair_override, hands):
            kickers = ["High Card", "Second Kicker", "Third Kicker"]
            one_pair_dict = {"One Pair": hands.get("One Pair")}
            for kicker in kickers:
                if kicker in hands:
                    one_pair_dict[kicker] = hands.get(kicker)
            return one_pair_dict
        return None

    def set_check(self, hands: dict) -> dict:
        set_override = ["Quads", "Flush", "Straight"]
        if "Set" in hands and none_in(set_override, hands):
            # Don't need a third kicker for Set tiebreakers
            set_dict = {
                "Set": hands.get("Set"),
                "High Card": hands.get("High Card"),
                "Second Kicker": hands.get("Second Kicker"),
            }
            return set_dict
        return None

    def full_house_check(self, hands: dict) -> dict:
        full_house = ["Set", "One Pair"]
        if all_in(full_house, hands):
            full_house_dict = {
                "Full House": hands.get("Set"),
                "One Pair": hands.get("One Pair"),
            }
            return full_house_dict
        return None

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

        hands = self.add_kickers_to_hands(hands)

        return hands

    def add_kickers_to_hands(self, hands: dict) -> dict:
        # We only check against the matched ranks (ranks that are in pairs,
        # sets, or quads) because kickers are irrelevant in straights/flushes.
        matched_ranks = hands.values()
        dealt_ranks = []
        for card in self.dealt:
            if card.rank not in matched_ranks:
                dealt_ranks.append(card.rank)

        dealt_ranks.sort(reverse=True)
        # The number of unique dealt ranks
        length = len(dealt_ranks)
        hands["High Card"] = dealt_ranks[0] if dealt_ranks else 0
        kickers = ["Second", "Third", "Fourth", "Fifth"]
        i = 1
        for kicker in kickers:
            hands[f"{kicker} Kicker"] = dealt_ranks[i] if length > i else 0
            i += 1

        return {k: v for k, v in hands.items() if v > 0}
