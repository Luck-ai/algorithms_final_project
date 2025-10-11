from gamelogic import Snake, generate_food, generate_bombs,print_board, heapSort, BOARD_WIDTH, BOARD_HEIGHT
from validation import ask_yes_no, ask_int

import os
import random
from readchar import readkey
from readchar.key import UP, DOWN, LEFT, RIGHT

def _game_loop(food_count=3, bomb_count=5, trial=False):
    snake = Snake()
    snake.add_head(BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
    score = 0

    temp_empty_bombs = set()
    food_set = generate_food(snake, temp_empty_bombs, food_count)
    bombs = generate_bombs(snake, food_set, bomb_count)

    board = [[' '] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

    print("Initial Board:")
    print_board(board, snake, food_set, bombs, trial)

    undo_stack = []
    MAX_UNDOS = 3
    remaining_undos = MAX_UNDOS

    def _do_move(dx, dy):
        nonlocal score
        head_x, head_y = snake.head.x, snake.head.y
        new_x, new_y = head_x + dx, head_y + dy

        if (
            new_x < 0
            or new_x >= BOARD_WIDTH
            or new_y < 0
            or new_y >= BOARD_HEIGHT
            or (new_x, new_y) in snake.positions
        ):
            print(
                f"💀 Game Over! You crashed into a wall or yourself. {('Final Score: ' + str(score)) if not trial else 'Have fun playing the real game!'}"
            )
            return False

        if (new_x, new_y) in bombs:
            print(
                f"💥 BOOM! You hit a bomb. Game Over! {('Final Score: ' + str(score)) if not trial else 'Have fun playing the real game!'}"
            )
            return False

        snake.add_head(new_x, new_y)
        removed_tail = None
        ate = False
        eaten_pos = None
        respawned_food = None

        if (new_x, new_y) in food_set:
            ate = True
            eaten_pos = (new_x, new_y)
            if not trial:
                score += 10
            food_set.discard(eaten_pos)

            added = False
            while not added:
                fx = random.randint(0, BOARD_WIDTH - 1)
                fy = random.randint(0, BOARD_HEIGHT - 1)
                pos = (fx, fy)
                if pos in snake.positions or pos in food_set or pos in bombs:
                    continue
                food_set.add(pos)
                respawned_food = pos
                added = True
        else:
            removed_tail = snake.remove_tail()

        move_info = {
            'head': (new_x, new_y),
            'removed_tail': removed_tail,
            'ate': ate,
            'eaten_pos': eaten_pos,
            'respawned_food': respawned_food,
        }
        undo_stack.append(('move', move_info))
        return True

    while True:
        print(f"Score: {score} | Undos left: {remaining_undos}")
        try:
            k = readkey()
        except KeyboardInterrupt:
            print(f"{('You chose to quit. Final Score: ' + str(score)) if not trial else 'Have fun playing the real game!' }")
            return score

        if (isinstance(k, str) and k.lower() == 'q'):
            print(f"{('You chose to quit. Final Score: ' + str(score)) if not trial else 'Have fun playing the real game!' }")
            return score

        if (isinstance(k, str) and k.lower() == 'z'):
            if remaining_undos <= 0:
                print("Oops! No more undos left.")
                continue
            if not undo_stack:
                print("Nothing to undo yet.")
                continue
            kind, info = undo_stack.pop()
            if kind != 'move':
                print("Undo error occurred.")
            removed_head = snake.remove_head()
            if info.get('ate'):
                score -= 10
                eaten_pos = info.get('eaten_pos')
                respawned = info.get('respawned_food')
                if respawned is not None:
                    food_set.discard(respawned)
                if eaten_pos is not None:
                    food_set.add(eaten_pos)
            else:
                removed_tail = info.get('removed_tail')
                if removed_tail is not None:
                    snake.append_tail(removed_tail)
            remaining_undos -= 1
            print(f"Undos remaining: {remaining_undos}")

        mapping = {
            UP: (0, -1),
            DOWN: (0, 1),
            LEFT: (-1, 0),
            RIGHT: (1, 0),
            'w': (0, -1),
            's': (0, 1),
            'a': (-1, 0),
            'd': (1, 0),
        }
        if k in mapping:
            dx, dy = mapping[k]
            cont = _do_move(dx, dy)
            if not cont:
                return score if not trial else -1

        os.system('cls' if os.name == 'nt' else 'clear')
        print_board(board, snake, food_set, bombs, trial)


file = os.path.join(os.path.dirname(__file__), "leaderboard.txt")

def _load_leaderboard(file_path=None):
    if file_path is None:
        file_path = file
    leaderboard = []
    try:
        with open(file_path, 'r') as fh:
            for line in fh:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                name_part, score_part = line.split(':', 1)
                try:
                    leaderboard.append([name_part.strip(), int(score_part.strip())])
                except ValueError:
                    continue
    except FileNotFoundError:
        return []
    return leaderboard

def _save_score(name, score, file_path=None):
    if file_path is None:
        file_path = file
    with open(file_path, 'a') as fh:
        fh.write(f"{name}:{score}\n")

def run_game(food_count=3, bomb_count=5, trial=False):
    leaderboard_sorted = []
    while True:
        if not trial:
            name = input("Enter your name for the leaderboard (or leave blank for 'Anonymous'): ").strip()
            if not name:
                name = 'Anonymous'

        score = _game_loop(food_count, bomb_count, trial=trial)
        if trial and score == -1:
            play_real = ask_yes_no("Practice round ended — start the full game now?", default=True)
            if play_real:
                print("\nEnter settings for the full game (press Enter to keep current values):\n")
                food_count = ask_int("How many food items?", default=food_count, min_value=1, max_value=100)
                bomb_count = ask_int("How many bombs?", default=bomb_count, min_value=0, max_value=200)
                trial = False
                continue
            else:
                print("\nThanks for trying the practice round!\n")
                break

        if score != -1:
            _save_score(name, score)
            leaderboard_sorted = heapSort(_load_leaderboard())[:5]

        print("\nCurrent Leaderboard:\n")
        if not leaderboard_sorted:
            print(" (no scores yet)")
        else:
            for i, (n, s) in enumerate(leaderboard_sorted, start=1):
                print(f" {i:>2}. {n:<20} {s} pts")

        play_again = ask_yes_no("Play another round?", default=False)
        if not play_again:
            print("\n🏆 Final Leaderboard:\n")
            if not leaderboard_sorted:
                print(" (no scores yet)")
            else:
                for i, (n, s) in enumerate(leaderboard_sorted, start=1):
                    print(f" {i:>2}. {n:<20} {s} pts")
            print("\nThanks for playing SnakeSweeper!\n")
            break