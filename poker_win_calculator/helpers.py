import atexit
import cursor
import shutil
from getkey import getkey

CARD_RANK = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_SUITS = ["C", "D", "S", "H"]


def all_card_combos():
    """Return a list of all possible card combinations."""
    return [f"{r}{s}" for r in CARD_RANK for s in CARD_SUITS]


def all_in(items: list, container: iter) -> bool:
    """Checks if all items from list 'items' are in list 'container'."""
    for item in items:
        if item not in container:
            return False
    return True


def clear():
    """Clear the terminal screen with ANSI escape codes."""
    print('\033[1;1H')
    print('\033[2J')


def debug_print(to_print):
    """Print a debug message to the terminal."""
    print(to_print)


def key_input():
    """Return the getkey().upper() value of the key pressed."""
    usr_in = getkey().upper()
    return usr_in


def line_break():
    """Print a line break."""
    print("\n", end="")


def none_in(items: list, container: iter) -> bool:
    """Checks that no items in the list 'items' are in the list 'container."""
    for item in items:
        if item in container:
            return False
    return True


def print_centre(s):
    """Print a string centred on the terminal screen."""
    width = shutil.get_terminal_size().columns
    print(s.center(width))


def print_lm(s):
    """Print with a left margin of n"""
    n = 4
    print(" " * n + s)


def start_cli():
    """Enable an alternative screen buffer to clear the terminal screen.
    Then, hide the cursor."""

    print('\033[?1049h')
    cursor.hide()
    atexit.register(cursor.show)


def quit_cli():
    """Re-enable the cursor, disable the alternative screen buffer,
    and quit the program."""
    cursor.show()
    print('\033[?1049l')
    exit()

