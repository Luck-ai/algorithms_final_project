## Project file descriptions

- `gamelogic.py` — Contains the main logic of the game. Includes `Node`/`Snake`, `generate_food`, `generate_bombs`, `count_adjacent_bombs`, `heapSort`, and board constants.
- `terminal.py` — CLI game loop, board rendering and printing, undo handling, leaderboard I/O.
- `graphicals.py` — Pygame-based GUI, event loop, graphical rendering, undo handling, save score UI.
- `validation.py` — input helpers and validators used by the CLI/UI.

## Project algorithms and data structures
This project implements a Snake-like game. The main Python modules containing the logic are `gamelogic.py`, `terminal.py`, `graphicals.py`, and `validation.py`. The sections below summarize the core algorithms and data structures used, where they appear in the code, and how operations (searching, sorting, adding, deleting) are implemented.

### Key data structures

- Snake as a doubly-linked list (nodes): The body of the snake is implemented as a doubly-linked list using `Node` and `Snake` classes. Each segment is a `Node` with `next` and `prev` pointers. This makes adding a head and removing a tail O(1) operations which are required in every move.

- Positions set for membership checks: `Snake.positions` is a `set` of (x, y) tuples. This provides average O(1) membership checks used for collision detection and placement validation.

- Foods and Bombs set: Food and Bomb positions are stored in a `set` of food positions (`food_set`) for fast membership tests. Using only a set provides average O(1) membership and removal.

- Board representation (CLI): A `2D Array` is used to render the CLI board for printing. Filling and printing the board is O(width * height).

- Undo stack: A `stack` is used to store the moves allowing for fast undo operations; push/pop are O(1). It is implemented as a Python list.

- Leaderboard: Scores are loaded into an array of pairs name and score and sorted when needed using heap sort. This is O(n log n) time complexity. The leaderboard is stored in a text file.

### Key algorithms

- Heap sort: Heap Sort is used to sort the leaderboard by score. This is an in-place heap sort: time O(n log n).

- Neighbor counting: `gamelogic.count_adjacent_bombs` checks the 3x3 neighborhood around a cell to count bombs.

- Random generation of food and bombs: `gamelogic.generate_food` and `gamelogic.generate_bombs` use random sampling with rejection to place items on the board.

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


