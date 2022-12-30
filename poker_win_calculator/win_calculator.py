from poker_win_calculator.helpers import line_break


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

        self.top_hands, self.top_ranked_hand = self.get_top_hands(self.hands)

        self.win_results = self.resolve_ties(
            self.top_hands, self.top_ranked_hand)

    def print_results(self):
        print(self.win_results)
        line_break()
        line_break()

    def get_results(self):
        return self.win_results

    def print_all_player_hands(self):
        for pid, pdata in self.top_hands:
            print(f"Player {pid}:")
            for hand, rank in pdata.items():
                print(f"  {hand}: {self.get_card_name(rank)}", end="")
            line_break()

    # TODO: Implement in future versions
    def designate_player_win_status(self, player_id):
        """Designates whether a player won in a hand, including split pots."""
        self.players[player_id - 1].is_winner = True

    def get_card_name(self, card_rank: int) -> str:
        """Converts a card's rank by int to its corresponding str.
        Relevant for face cards."""
        return self.card_ranks[card_rank - 2]

    def get_top_hands(self, hands: list) -> tuple:
        def set_player_highest_hand(player_id: int, hand_rank: str):
            self.players[player_id - 1].highest_hand = hand_rank

        temp_rank_data = {rank: [] for rank in self.rank_types}

        # for player id, all player's hands in self.hands
        for p_id, p_data in self.hands:
            # for the key 'rank' (value of []) in temp_rank_data
            for rank in temp_rank_data:
                # if the player has that rank in their hand
                if rank in p_data:
                    # append that player(s) & their data to the list, ignoring
                    # all other rank keys.
                    temp_rank_data[rank].append((p_id, p_data))
                    set_player_highest_hand(p_id, rank)
                    break

        # Remove empty keys
        sorted_players = {k: v for k, v in temp_rank_data.items() if v}
        # Only return highest ranked players/top hands by finding the first
        # non-empty key in the dict (which, since it's sorted, will be the
        # highest). Returns a list of tuples:
        # (player_id, {'hand_type': highest_ranked_card_in_that_hand})
        # and the top ranked hand (str)
        for rank in self.rank_types:
            if rank in sorted_players:
                top_hands = sorted_players.get(rank)
                return top_hands, rank

    def tag_msg(self, hand_type: str, card_name: str, msg: str) -> str:
        # Tags to put at the end of the message based on certain hand types
        if hand_type == "Royal Flush":
            return "\nRoyal Flush"
        elif hand_type == "High Card":
            return f"\n{card_name}-high"
        _high = ["Straight Flush", "Straight", "Flush"]
        suffix = " high" if hand_type in _high else "s"
        tag = f"\n{hand_type}, {card_name}{suffix}"
        return f"{msg}{tag}"

    def split_pot_msg(self, winners: list) -> str:
        msg = "Split Pot -"
        for player in winners:
            player_id = player[0]
            msg += f" Player {player_id},"
        return msg[:-1]

    def announce_winner(self, winners_list: list) -> str:
        player_id = winners_list[0][0]
        return f"Player {player_id} wins!"

    def full_house_ties(self, top_hands: list, hand_type, card_name) -> str:
        """Resolve ties for a full house."""
        # Full houses tied by the set are resolved by the pair in the FH.
        # If that is also a tie, the pot is split.

        winners, pair_rank = self.tiebreaker_info(top_hands, "One Pair")
        if len(top_hands) > 1:
            if len(winners) > 1:
                msg = self.split_pot_msg(winners)
            else:
                msg = self.announce_winner(winners)
        else:
            msg = self.announce_winner(top_hands)
        msg += f"\n{hand_type}, {card_name}s full of {pair_rank}s"
        return msg

    def staight_flush_or_quad_ties(
            self, top_hands: list, hand_type, card_name) -> str:
        """Resolve ties for straights, flushes, or quads."""
        if len(top_hands) > 1:
            msg = self.split_pot_msg(top_hands)
        else:
            msg = self.announce_winner(top_hands)
        msg = self.tag_msg(hand_type, card_name, msg)
        return msg

    def set_ties(self, top_hands: list, hand_type, card_name) -> str:
        """Resolve ties for sets."""

        tag = ""
        if len(top_hands) > 1:
            kickers = ["High Card", "Second Kicker"]
            # If returning a list of players with the highest first/second
            # kicker only returns one player, announce that kicker
            for kicker in kickers:
                winners, kicker_rank = self.tiebreaker_info(top_hands, kicker)
                if len(winners) == 1:
                    tag = f", {kicker_rank} kicker"
                    msg = self.announce_winner(winners)
                    break
            # If it's ties all the way down, split the pot
            else:
                msg = self.split_pot_msg(top_hands)
        else:
            msg = self.announce_winner(top_hands)
        msg += f"\n{hand_type} of {card_name}s{tag}"
        return msg

    def two_pair_ties(self, top_hands: list, hand_type, card_name) -> str:
        """Resolve ties for two pairs."""

        low_pair = top_hands[0][1]["Low Pair"]
        low_pair = self.get_card_name(low_pair)
        tag = ""
        if len(top_hands) > 1:
            kickers = ["Low Pair", "High Card"]
            # If returning a list of players with the highest first/second
            # kicker only returns one player, announce that kicker
            for kicker in kickers:
                winners, kicker_rank = self.tiebreaker_info(top_hands, kicker)
                if len(winners) == 1:
                    tag = f", {kicker_rank} kicker" if kicker_rank != "Low Pair" else ""
                    msg = self.announce_winner(winners)
                    break
            # If it's ties all the way down, split the pot
            else:
                msg = self.split_pot_msg(top_hands)
        else:
            msg = self.announce_winner(top_hands)
        msg += f"\n{hand_type} {card_name}s and {low_pair}s{tag}"
        return msg

    def one_pair_ties(self, top_hands: list, hand_type, card_name) -> str:
        """Resolve ties for one pairs."""

        tag = ""
        if len(top_hands) > 1:
            kickers = ["High Card", "Second Kicker", "Third Kicker"]
            # If returning a list of players with the highest first/second
            # kicker only returns one player, announce that kicker
            for kicker in kickers:
                winners, kicker_rank = self.tiebreaker_info(top_hands, kicker)
                if len(winners) == 1:
                    tag = f", {kicker_rank} kicker"
                    msg = self.announce_winner(winners)
                    break
            # If it's ties all the way down, split the pot
            else:
                msg = self.split_pot_msg(top_hands)
        else:
            msg = self.announce_winner(top_hands)
        msg += f"\nPair of {card_name}s{tag}"
        return msg

    def high_card_ties(self, top_hands: list, hand_type, card_name) -> str:
        """Resolve ties for high cards."""

        tag = ""
        if len(top_hands) > 1:
            kickers = ["Second Kicker", "Third Kicker",
                       "Fourth Kicker", "Fifth Kicker"]
            # If returning a list of players with the highest first/second
            # kicker only returns one player, announce that kicker
            for kicker in kickers:
                winners, kicker_rank = self.tiebreaker_info(top_hands, kicker)
                if len(winners) == 1:
                    tag = f", {kicker_rank} kicker"
                    msg = self.announce_winner(winners)
                    break
            # If it's ties all the way down, split the pot
            else:
                msg = self.split_pot_msg(top_hands)
        else:
            msg = self.announce_winner(top_hands)
        msg += f"\n{card_name}-high{tag}"
        return msg

    def flush_ties(self, top_hands: list, hand_type, card_name) -> str:
        """Resolve ties for flushes."""

        tag = ""
        if len(top_hands) > 1:

            kickers = ["Second", "Third",
                       "Fourth", "Fifth"]
            # If returning a list of players with the highest first/second
            # kicker only returns one player, announce that kicker
            for kicker in kickers:

                winners, kicker_rank = self.tiebreaker_info(top_hands, kicker)
                if len(winners) == 1:
                    tag = f", {kicker_rank} kicker"
                    msg = self.announce_winner(winners)
                    break
            # If it's ties all the way down, split the pot
            else:
                msg = self.split_pot_msg(top_hands)
        else:
            msg = self.announce_winner(top_hands)
        msg += f"\n{card_name}-high Flush{tag}"

        return msg

    def get_highest_value(self, top_hands: list, hand_type: str) -> int:
        # Return the highest rank of a given hand type (h_type).
        # top_hands = [(int, {hand_type: rank})]
        _list = sorted(top_hands, key=lambda d: d[1][hand_type], reverse=True)
        high_card = _list[0][1].get(hand_type)
        return high_card

    def potential_winners(
        self, top_hands: list, hand_type: str, high_card: int
    ) -> list:
        # Return a list of potential winners, i.e. all players that
        # have the highest ranking card of a given hand type (h_type)
        winners = []
        for pid, data in top_hands:
            if data.get(hand_type) == high_card:
                winners.append((pid, data))
        return winners

    def tiebreaker_info(self, top_hnds: list, hand_type: str) -> tuple:

        high_card = self.get_highest_value(top_hnds, hand_type)
        winners = self.potential_winners(top_hnds, hand_type, high_card)
        card_name = self.get_card_name(high_card)
        return winners, card_name

    def resolve_ties(self, top_hands: list, hand_type: str) -> list:
        """Return the winner(s) of the round and break ties if needed by
        calling the relevant tie breaking function."""

        func_call = {
            "Royal Flush": self.staight_flush_or_quad_ties,
            "Straight Flush": self.staight_flush_or_quad_ties,
            "Quads": self.staight_flush_or_quad_ties,
            "Full House": self.full_house_ties,
            "Flush": self.flush_ties,
            "Straight": self.staight_flush_or_quad_ties,
            "Set": self.set_ties,
            "Two Pair": self.two_pair_ties,
            "One Pair": self.one_pair_ties,
            "High Card": self.high_card_ties,
        }

        # Gather the first round of relevant info. Some of the tiebreaking info
        # functions might need to be called again depending on the kind of tie
        # that needs to be broken, e.g. a full house that needs to be broken by
        # the pair, a set or high card broken by one or more kickers, etc.
        winners, card_name = self.tiebreaker_info(top_hands, hand_type)
        msg = func_call[hand_type](winners, hand_type, card_name)
        return msg
