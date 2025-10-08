import random
from collections import deque
import os
from wcwidth import wcswidth
from readchar import readkey as readkey
from readchar.key import UP as UP, DOWN as DOWN, LEFT as LEFT, RIGHT as RIGHT

from validation import ask_yes_no

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.next = None
        self.prev = None

class Snake:
    def __init__(self):
        self.head = None
        self.tail = None
        self.positions = set()
        self.length = 0

    def add_head(self, x, y):
        new_node = Node(x, y)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        self.head = new_node
        if not self.tail:
            self.tail = new_node
        self.positions.add((x, y))
        self.length += 1

    def remove_tail(self):
        if not self.tail:
            return None
        if self.head == self.tail:
            removed = (self.tail.x, self.tail.y)
            try:
                self.positions.remove(removed)
            except KeyError:
                pass
            self.head = self.tail = None
            self.length = 0
            return removed

        old_tail = self.tail
        removed = (old_tail.x, old_tail.y)
        try:
            self.positions.remove(removed)
        except KeyError:
            pass
        self.tail = old_tail.prev
        if self.tail:
            self.tail.next = None
        old_tail.prev = None
        self.length -= 1
        return removed

    def remove_head(self):
        if not self.head:
            return None
        old_head = self.head
        removed = (old_head.x, old_head.y)
        self.head = old_head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        try:
            self.positions.remove(removed)
        except KeyError:
            pass
        self.length -= 1
        return removed

    def append_tail(self, pos):
        x, y = pos
        new_node = Node(x, y)
        new_node.prev = self.tail
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.positions.add((x, y))
        self.length += 1

    def to_list(self):
        cur = self.head
        res = []
        while cur:
            res.append((cur.x, cur.y))
            cur = cur.next
        return res

    def head_coordinates(self):
        return (self.head.x, self.head.y)

    def contains(self, pos):
        return pos in self.positions

def _heapify(arr, n, i):  
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and arr[l][1] > arr[largest][1]:
        largest = l
    if r < n and arr[r][1] > arr[largest][1]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _heapify(arr, n, largest)

def heapSort(arr):  
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _heapify(arr, i, 0)
    arr.reverse()
    return arr 

BOARD_WIDTH = 10
BOARD_HEIGHT = 7

def generate_food(snake, bombs, food_count=3):
    food_queue = deque()
    food_set = set()
    snake_positions = snake.positions if hasattr(snake, 'positions') else set(snake.to_list())

    while len(food_queue) < food_count:
        fx = random.randint(0, BOARD_WIDTH - 1)
        fy = random.randint(0, BOARD_HEIGHT - 1)
        pos = (fx, fy)
        if pos in snake_positions or pos in food_set or pos in bombs:
            continue
        food_queue.append(pos)
        food_set.add(pos)

    return food_queue, food_set

def generate_bombs(snake, food_set, bomb_count=5):
    bombs = set()
    snake_positions = snake.positions if hasattr(snake, 'positions') else set(snake.to_list())

    while len(bombs) < bomb_count:
        bx = random.randint(0, BOARD_WIDTH - 1)
        by = random.randint(0, BOARD_HEIGHT - 1)
        pos = (bx, by)
        if pos in snake_positions or pos in food_set or pos in bombs:
            continue
        bombs.add(pos)
    return bombs

def count_adjacent_bombs(x, y, bombs):
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if (x + dx, y + dy) in bombs:
                count += 1
    return count

def _print_board(board, snake, food_queue, food_set, bombs, trial=False):
    display = [row.copy() for row in board]
    snake_list = snake.to_list()
    snake_set = snake.positions if hasattr(snake, 'positions') else set(snake_list)

    for fx, fy in food_queue:
        display[fy][fx] = '🍎'
    
    if trial:
        for bx, by in bombs:
            display[by][bx] = '💣'

    head_coords = snake.head_coordinates()
    for x, y in snake_list:
        display[y][x] = '🐍' if (x, y) == head_coords else '🟩'

    head_x, head_y = head_coords
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = head_x + dx, head_y + dy
        if 0 <= nx < BOARD_WIDTH and 0 <= ny < BOARD_HEIGHT:
            pos = (nx, ny)
            if pos not in food_set and pos not in snake_set:
                display[ny][nx] = str(count_adjacent_bombs(nx, ny, bombs))

    cell_w = 6  
    horiz_top = "╔" + "╦".join(["═" * cell_w for _ in range(BOARD_WIDTH)]) + "╗"
    horiz_mid = "╠" + "╬".join(["═" * cell_w for _ in range(BOARD_WIDTH)]) + "╣"
    horiz_bot = "╚" + "╩".join(["═" * cell_w for _ in range(BOARD_WIDTH)]) + "╝"

    print(horiz_top)
    for y, row in enumerate(display):
        line = "║"
        for cell in row:
            s = str(cell) if cell != ' ' else ' '
            width = wcswidth(s)
            pad_left = (cell_w - width) // 2
            pad_right = cell_w - width - pad_left
            line += " " * pad_left + s + " " * pad_right + "║"
        print(line)
        if y != len(display) - 1:
            print(horiz_mid)
    print(horiz_bot)

def _game_loop(food_count=3, bomb_count=5, trial=False):
    snake = Snake()
    snake.add_head(BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
    score = 0

    temp_empty_bombs = set()
    food_queue, food_set = generate_food(snake, temp_empty_bombs, food_count)
    bombs = generate_bombs(snake, food_set, bomb_count)

    board = [[' '] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

    def add_food(pos):
        food_queue.append(pos)
        food_set.add(pos)

    def remove_food(pos):
        food_queue.remove(pos)
        food_set.remove(pos)

    print("Initial Board:")
    _print_board(board, snake, food_queue, food_set, bombs, trial)

    undo_stack = []
    MAX_UNDOS = 3
    remaining_undos = MAX_UNDOS

    def _do_move(dx, dy):
        nonlocal score
        head_x, head_y = snake.head.x, snake.head.y
        new_x, new_y = head_x + dx, head_y + dy

        if new_x < 0 or new_x >= BOARD_WIDTH or new_y < 0 or new_y >= BOARD_HEIGHT or (new_x, new_y) in snake.positions:
            print(f"💀 Game Over! You crashed into a wall or yourself. {('Final Score: ' + str(score)) if not trial else 'Have fun playing the real game!'}")
            return False

        if (new_x, new_y) in bombs:
            print(f"💥 BOOM! You hit a bomb. Game Over! {('Final Score: ' + str(score)) if not trial else 'Have fun playing the real game!'}")
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
            remove_food(eaten_pos)

            added = False
            while not added:
                fx = random.randint(0, BOARD_WIDTH - 1)
                fy = random.randint(0, BOARD_HEIGHT - 1)
                pos = (fx, fy)
                if pos in snake.positions or pos in food_set or pos in bombs:
                    added = False
                    continue
                add_food(pos)
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

    try:
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
                if not undo_stack:
                    print("Nothing to undo yet.")
                kind, info = undo_stack.pop()
                if kind != 'move':
                    print("Undo error occurred.")
                removed_head = snake.remove_head()
                if info.get('ate'):
                    score -= 10
                    eaten_pos = info.get('eaten_pos')
                    respawned = info.get('respawned_food')
                    if respawned is not None:
                        try:
                            if respawned in food_set:
                                food_queue.remove(respawned)
                                food_set.remove(respawned)
                        except ValueError:
                            pass
                    if eaten_pos is not None:
                        add_food(eaten_pos)
                else:
                    removed_tail = info.get('removed_tail')
                    if removed_tail is not None:
                        snake.append_tail(removed_tail)
                remaining_undos -= 1
                print(f"Undos remaining: {remaining_undos}")

            mapping = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0) , 'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0)}
            if k in mapping:
                dx, dy = mapping[k]
                cont = _do_move(dx, dy)
                if not cont:
                    return score if not trial else -1

            os.system('cls' if os.name == 'nt' else 'clear')
            _print_board(board, snake, food_queue, food_set, bombs, trial)

    finally:
        pass

def _default_leaderboard_path():
    root = os.path.dirname(os.path.dirname(__file__)) if os.path.dirname(__file__) else os.getcwd()
    return os.path.join(root, 'leaderboard.txt')

def _load_leaderboard(file_path=None):
    if file_path is None:
        file_path = _default_leaderboard_path()
    leaderboard = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
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
        file_path = _default_leaderboard_path()
    with open(file_path, 'a') as f:
        f.write(f"{name}:{score}\n")

def run_game(food_count=3, bomb_count=5, trial=False):
          while True:
            name = input("Enter your name for the leaderboard (or leave blank for 'Anonymous'): ").strip()
            if not name:
                name = 'Anonymous'

            score = _game_loop(food_count, bomb_count, trial=trial)
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
                print("\nFinal Leaderboard:\n")
                if not leaderboard_sorted:
                    print(" (no scores yet)")
                else:
                    for i, (n, s) in enumerate(leaderboard_sorted, start=1):
                        print(f" {i:>2}. {n:<20} {s} pts")
                print("\nThanks for playing SnakeSweeper!\n")
                break