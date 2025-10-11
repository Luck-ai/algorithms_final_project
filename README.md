# Final Project for Intro to Algorithms: SnakeSweeper

This is a game that combines elements of Snake and Minesweeper. The player controls a snake that moves around a grid, collecting food to grow longer while avoiding bombs. The game includes features such as a leaderboard, undo functionality, and both text-based and graphical interfaces. For further explantions of key algrithms and data structures used, see [explanation.md](explanation.md).

## Project file descriptions

- `gamelogic.py` — Contains the main logic of the game. Includes `Node`/`Snake`, `generate_food`, `generate_bombs`, `count_adjacent_bombs`, `heapSort`, and board constants.
- `terminal.py` — CLI game loop, board rendering and printing, undo handling, leaderboard I/O.
- `graphicals.py` — Pygame-based GUI, event loop, graphical rendering, undo handling, save score UI.
- `validation.py` — input helpers and validators used by the CLI/UI.
- `main.py` — Entry point to start the game in either CLI or GUI mode.

## Running the Game

To run the game, first install the required dependencies:

```bash 
pip install -r requirements.txt
```

Then, execute the main script:

```bash 
python main.py
```


