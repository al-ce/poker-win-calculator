# pokerstats
Calculate winner of a Holdem round from user input of cards, or generate random Holdem rounds and show the winner.

https://user-images.githubusercontent.com/23170004/201289475-c2a95ce7-359a-48f2-a990-c2751f2e0d8d.mov

My first Python/programming project. Very messy! One day I'll rewrite it.

# Usage

*(q)* to quit, *(m)* to return to the main menu.

## Test specific hands (t)
Caculate the winner among a specific set of cards for both the players and the board (community cards) by pressing (t) from the main menu. 

First, select the number of players (minimum 1, maximum 9. Nine is typically the maximum number allowed for Holdem).


Second, input the cards for each player and then for the board. Only valid cards are allowed in the format `RankSuit` e.g. `9S` (Nine of Spades), `10C`, `KH`, etc.
Confirm your card selection with `Return` or `Spacebar`.
Exit this testing module's input phase by pressing `<Esc>`.


The program will determine a winner, or winners if the pot is to be split.

<img width="696" alt="Screen Shot 2022-11-11 at 01 43 54" src="https://user-images.githubusercontent.com/23170004/201291135-4618d142-5be6-4a44-b1f5-1d393f8acf20.png">

## Show random hands (r)
Select the number of players as above and automatically deal to all the players and the board as if from a shuffled deck.

# Roadmap
* Huge rewrite to clean up the code.

* Export *n* rounds of randomized data to a .csv file.

* Make this the backend of a webapp.
