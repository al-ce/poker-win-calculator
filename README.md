# pokerstats
Calculate winner of a Holdem round from user input of cards, or generate random Holdem rounds and show the winner.

https://user-images.githubusercontent.com/23170004/201289475-c2a95ce7-359a-48f2-a990-c2751f2e0d8d.mov

# Usage

*(q)* to quit, *(m)* to return to the main menu.

## Test specific hands (t)
Caculate the winner among a specific set of cards for both the players and the board (community cards) by pressing (t) from the main menu.

First, select the number of players (minimum 1, maximum 9. Nine is typically the maximum number allowed for Holdem).


Second, input the cards for each player and then for the board. Only valid cards are allowed in the format `RankSuit` e.g. `9S` (Nine of Spades), `10C`, `KH`, etc.
Confirm your card selection with `Return` or `Spacebar`.
Exit this testing module's input phase by pressing `<Esc>`.


The program will determine a winner, or winners if the pot is to be split.

<img width="696" alt="Results display" src="https://user-images.githubusercontent.com/23170004/201291135-4618d142-5be6-4a44-b1f5-1d393f8acf20.png">

## Show random hands (r)
Select the number of players as above and automatically deal to all the players and the board as if from a shuffled deck.

# Description of design

Calculating what hands a Player has in a given round proved challenging because
of the complexity of the rules of tie-breaking in Texas Hold'em. So this meant
pre-emptively storing all possible tie breakers in a HandCalculator object
before passing it to the WinCalculator. Additionally, for the sake of reducing
complexity, you don't want to store *every* hand the Player makes in a round
because lower ranked hands might be irrelevant to the win calculation (e.g. a
pair that is not part of the highest hand is irrelevant to the calculation of a
tie breaaker between two full houses, a straight, or a flush). Again, the OOP
structure hepled bounce around between methods since the tie breaking
calculations needed to be so specific. See, for example, the `resolve_ties`
method in the `WinCalculator` class, which is a dict of functions that calls
the relevant tie breaking function.

The CLI interface uses the `getkey` module to take input directly, and the
`cursor` module to hide the cursor. This gives the user speed and comfort when
moving around the program by taking input and acting on it on each keypress
rather than waiting for the user to press `return`. I also clear the screen on
every input to rewrite the contents for a cleaner overall look. This makes the
command line interface experience more aesthetically pleasing and takes
advantage of the terminal's speed compared to a webapp.

The CLI interface also tries to handle user 'error' as much as possible. For
example, keys irrelevant to the current screen are ignored or responded to with
a non-intrusive, uninterruptive error message. If the user inputs a letter when
the only valid options are numbers (or `q` to quit), an error message is
displayed without altering the layout of the screen.

Using classes also allows for easier implementations of future features. It
would be nice to also display and update the Player's win chances as each hand
in a round is dealt(one street at a time rather than all at once). To allow for
that development,each Card object has a unique `id` and `location` attribute
that could be used to keep track of what cards have been dealt or folded, but
currently they do nothing.

# Roadmap
* Huge rewrite to clean up the code.

* Export *n* rounds of randomized data to a .csv file.

* Make this the backend of a webapp.
