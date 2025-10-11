
## Project algorithms and data structures
This project implements a Snake-like game. The main Python modules containing the logic are `gamelogic.py`, `terminal.py`, `graphicals.py`, and `validation.py`. The sections below summarize the core algorithms and data structures used, where they appear in the code, and how operations (searching, sorting, adding, deleting) are implemented.

 

## How searching, sorting, adding and deleting are done

This section explains the operations used across the codebase and where they are implemented.

### Searching 

- Snake collision checks: When the snake moves, presence of the new head position in the snake body is checked using `Snake.positions` — average-case O(1). 
- Food/bomb occupancy checks: The new head position is checked against `food_set` and `bombs` to see if food or a bomb is present. This is average O(1).

### Sorting

- Leaderboard sorting: `gamelogic.heapSort` sorts the list of `[name, score]` pairs by score in descending order. Complexity: O(n log n) time. The result is reversed to present highest-first.

### Adding (insertion / growth)

- Snake growth on eat: `Snake.add_head(x, y)` creates a new `Node` and links it as the new head. It also inserts the new coordinate into `Snake.positions` (set). Complexity: O(1).

- Append tail (undo restore): `Snake.append_tail(pos)` creates a new tail node and updates pointers and the `positions` set. Complexity: O(1).

- Food and bombs: Adding a food/bomb position inserts into `food_set` and `bombs` — average O(1).

### Deleting (removal)

- Snake move (normal): When the snake moves without eating, the tail is removed with `Snake.remove_tail()`, which updates the linked list and removes the old tail coordinate from `Snake.positions`. Complexity: O(1).

- Removing head (undo): `Snake.remove_head()` is used for undo and removes the head node and its position from `positions`. Complexity: O(1).

- Food/bomb removal: Removing a specific food or bomb coordinate uses `set.discard()`. This is average O(1).


