## Concurrency Issues in Game Overview 
### 1: Non-repeatable Read in Game Overview

When a user views a game overview while another user is updating the same game's basic information.

#### Sequence Diagram
```
Transaction A (get_game_overview)   |   Transaction B (update_game)
-----------------------------------|---------------------------
Begin                              |
Read game (id=5, title="Halo")     |
                                   |   Begin
                                   |   Update game 5 title to "Halo Infinite"
                                   |   Commit
Read reviews for game_id=5         |
Read comments for each review      |
Read optional reviews              |
Calculate statistics               |
Return GameOverview with           |
  title="Halo" but reviews for     |
  "Halo Infinite"                  |
Commit                             |
```

The user receives inconsistent data where the game title doesn't match the reviews being displayed. This creates confusion since the reviews might reference features specific to "Halo Infinite" while the title shows "Halo".

### 2: Phantom Reads in Rating Calculation

When a user views a game overview with calculated aggregate rating while new reviews are being added.

#### Sequence Diagram
```
Transaction A (get_game_overview)   |   Transaction B (add_review)
-----------------------------------|---------------------------
Begin                              |
Read game data                     |
Read all reviews (3 reviews)       |
                                   |   Begin
                                   |   Insert new review with score=1
                                   |   Commit
Read optional reviews              |
Read total playtime                |
Calculate avg rating (avg of 4)    |
Return GameOverview with           |
  aggregate_rating = 4          |
  (while actual avg now = 3.5)     |
Commit                             |
```

The aggregate rating displayed to the user is no longer accurate because a new review was added during the transaction. This can mislead users about the game's current reception.


### Recommended Isolation Level

To prevent these problems the solution is to use a Repeatable Read isolation level.
This Prevents Non-repeatable Reads because it Ensures that if the transaction reads the same row twice, it gets the same value each time, maintaining consistency in the game information throughout the transaction. This also Prevents Phantom Reads because if the transaction runs a query twice, it sees the same set of rows each time, providing consistent aggregate calculations and review counts.
This isolation level ensures that users get a consistent view of a game's data throughout the entire API call, even if other transactions are modifying game