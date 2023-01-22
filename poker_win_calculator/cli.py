from getkey import keys
from string import digits

from poker_win_calculator.game_objects import Card, Dealer, Player
from poker_win_calculator.hand_calculator import HandCalculator
from poker_win_calculator.helpers import (
    all_card_combos,
    clear,
    key_input,
    line_break,
    print_centre,
    print_lm,
    quit_cli,
    start_cli,
)
from poker_win_calculator.win_calculator import WinCalculator


class CLI:
    header = "Texas Holdem Hand Wins Calculator"

    readme = """
    * Navigate with (q) (r) (t) (m).
    * Repeat (r) with 1-9 without leaving the (r)andom page.
    * (esc) breaks the (t)est input loop and takes you back to this screen.
    """
    menu_options = "(q)uit (r)andom (t)est (m)enu"
    top_bar_msg = ""
    hand_printout = ""
    tot_player_msg = "Please enter a digit 1-9 (for number of players), (q)uit, or back to (m)enu"
    dealt_display = ""

    def print_header(self):
        """Print a standard header on each page of the CLI."""
        clear()
        line_break()
        print_centre(self.header)
        line_break()
        print_centre(self.menu_options)
        line_break()
        print_lm(self.top_bar_msg)

    def deal_hand_header(self):
        """Print a standard header on the deal hand page of the CLI."""
        self.print_header()
        hand_printout = self.hand_printout.split("\n")
        for line in hand_printout:
            print_lm(line)

    def clear_top_bar(self):
        """Clear the top bar message."""
        self.top_bar_msg = ""

    def set_top_bar(self, s: str):
        """Set the top bar message."""
        self.top_bar_msg = s

    def clear_hand_printout(self):
        """Clear the hand printout."""
        self.hand_printout = ""

    def menu(self):
        """Run the main menu of the CLI."""

        start_cli()

        while True:
            self.print_header()
            for line in self.readme.split('\n'):
                print_lm(line)
            usr_in = key_input()
            if usr_in == "Q":
                quit_cli()
            elif usr_in == "R":
                self.deal_hand("random")
            elif usr_in == "T":
                self.deal_hand("test")
            elif usr_in == "M":
                return self.menu()
        return

    def deal_test_hands(self, dealer: Dealer):
        """Pass information directly to the Dealer instead of drawing randomly
        from a Deck."""

        all_dealt_cards = []
        for player in dealer.players:
            player_card_select = CardSelector(
                2, f"Player {player.id}", all_dealt_cards)
            player_card_select.screen_draw(self)
            # Update all dealt cards so duplicates can't be input.
            all_dealt_cards += player_card_select.get_dealt_cards()
            player_card_list = player_card_select.convert_strings_to_Cards()
            player.hole = player_card_list

        comm_card_select = CardSelector(5, "Board", all_dealt_cards)
        comm_card_select.screen_draw(self)
        comm_card_list = comm_card_select.convert_strings_to_Cards()
        dealer.community_cards = comm_card_list

    def deal_hand(self, deal_type: str):
        """Deal a random or custom hand based on deal_type param."""
        self.set_top_bar(self.tot_player_msg)
        self.deal_hand_header()
        tot_players = key_input()
        while True:
            if tot_players == "Q":
                quit_cli()
            elif tot_players == "T":
                self.clear_top_bar()
                self.clear_hand_printout()
                return self.deal_hand("test")
            elif tot_players == "R":
                self.clear_top_bar()
                self.clear_hand_printout()
                return self.deal_hand("random")
            elif tot_players == "M":
                self.clear_top_bar()
                self.clear_hand_printout()
                return self.menu()
            elif tot_players == "" or tot_players not in digits:
                self.set_top_bar(self.tot_player_msg)
                return self.deal_hand(deal_type)
            # Handle 0 as input
            elif tot_players in digits and int(tot_players) < 1:
                return self.deal_hand(deal_type)

            self.set_top_bar(f"Number of players: {tot_players}")
            # Create as many Player objects as needed
            tot_players = int(tot_players)
            players = [Player(i + 1) for i in range(tot_players)]
            dealer = Dealer(players)

            if deal_type == "random":
                # Deal all cards to players and to the board
                dealer.deal_full_round()
                # Store the round info (board cards + player cards)
            elif deal_type == "test":
                self.clear_hand_printout()
                self.deal_hand_header()
                self.deal_test_hands(dealer)

            round_info = dealer.get_round_info()
            # Print blank space so results always print in the same place
            round_info += "\n" * (9 - tot_players)

            for player in dealer.players:
                h = HandCalculator(dealer.community_cards, player)
                h.report_hands_to_player()
            w = WinCalculator(dealer.players)
            results = w.get_results()

            self.clear_hand_printout()
            self.hand_printout += f"{round_info}\n{results}"
            self.deal_hand_header()
            tot_players = key_input()
        return


class CardSelector:
    def __init__(self, max_cards: int, card_location: str, dealt_cards: list):
        # How many cards to take as input before returning them
        self.max_cards = max_cards
        self.card_location = card_location

        self.dealt_cards = dealt_cards
        self.temp_cards = []

        self.input_display = ""

    def convert_strings_to_Cards(self):
        """Convert the names in temp_cards to Card objects."""
        usr_list = []
        rank = ["2", "3", "4", "5", "6", "7",
                "8", "9", "10", "J", "Q", "K", "A"]
        for card in self.temp_cards:
            # Get card rank, allowing for special case of a 10
            r = "10" if card[0] == "1" else card[0]
            s = card[2] if card[1] == "0" else card[1]
            card_rank = rank.index(r)
            card = Card(s, (r, card_rank + 2))
            usr_list.append(card)
        return usr_list

    def print_cards_display(self, cards_display_string: str):
        """Print the cards_display string."""
        print_lm(cards_display_string)

    def cards_display(self):
        """Return a string to display the cards in temp_cards."""
        display = f"{self.card_location}: "
        for card in self.temp_cards:
            display += f" {card}"
        return display

    def clear_input_display(self):
        """Clear the input display."""
        self.input_display = ""

    def get_dealt_cards(self):
        """Return the list of dealt cards."""""
        return self.dealt_cards

    def screen_draw(self, cli: CLI):
        """Draw the CLI screen for the user to input cards."""
        valid_cards = all_card_combos()

        cli.set_top_bar("")

        while True:
            clear()
            cli.deal_hand_header()
            print_lm(cli.dealt_display)
            line_break()
            self.print_cards_display(self.cards_display())
            line_break()
            print_lm(self.input_display)

            c = key_input()
            cli.clear_top_bar()
            if c == keys.BACKSPACE:
                self.input_display = self.input_display[:-1]
            elif c == keys.SPACE or c == keys.ENTER:
                if self.input_display in self.dealt_cards:
                    cli.set_top_bar("Duplicate Card!")
                elif self.input_display in valid_cards:
                    self.temp_cards.append(self.input_display)
                    self.dealt_cards.append(self.input_display)
                    if len(self.temp_cards) == self.max_cards:
                        cli.dealt_display += self.cards_display() + " | "
                        return self.temp_cards
                else:
                    cli.top_bar_msg = "Invalid Card!"
                self.clear_input_display()
            elif c == keys.ESCAPE:
                break
            else:
                # Add a character to the input
                self.input_display += c

        return cli.menu()


def main():

    run = CLI()
    run.menu()


if __name__ == "__main__":
    main()
