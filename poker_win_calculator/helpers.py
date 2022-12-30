import shutil
from getkey import getkey
from os import system

CARD_RANK = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_SUITS = ["C", "D", "S", "H"]


def all_card_combos():
    return [f"{r}{s}" for r in CARD_RANK for s in CARD_SUITS]


def all_in(items: list, container: iter) -> bool:
    """Checks if all items from list 'items' are in list 'container'."""
    for item in items:
        if item not in container:
            return False
    return True


def clear():
    """Clear the terminal screen."""
    return system("clear")


def debug_print(to_print):
    print(to_print)


def key_input():
    usr_in = getkey().upper()
    return usr_in


def line_break():
    print("\n", end="")


def none_in(items: list, container: iter) -> bool:
    """Checks that no items in the list 'items' are in the list 'container."""
    for item in items:
        if item in container:
            return False
    return True


def print_centre(s):
    print(s.center(shutil.get_terminal_size().columns))


def print_lm(s):
    """Print with a left margin of n"""
    n = 4
    print(" " * n + s)


def quit_cli():
    clear()
    exit()
