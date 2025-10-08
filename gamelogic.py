import os
import random
from wcwidth import wcswidth

BOARD_WIDTH = 10
BOARD_HEIGHT = 7

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
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left][1] > arr[largest][1]:
        largest = left
    if right < n and arr[right][1] > arr[largest][1]:
        largest = right
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

def generate_food(snake, bombs, food_count=3):
    """Return a set of food positions. Use only a set for membership and iteration.

    Returns:
        set of (x, y) tuples
    """
    food_set = set()
    snake_positions = snake.positions if hasattr(snake, 'positions') else set(snake.to_list())

    while len(food_set) < food_count:
        fx = random.randint(0, BOARD_WIDTH - 1)
        fy = random.randint(0, BOARD_HEIGHT - 1)
        pos = (fx, fy)
        if pos in snake_positions or pos in food_set or pos in bombs:
            continue
        food_set.add(pos)

    return food_set

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

def print_board(board, snake, food_set, bombs, trial=False):
    display = [row.copy() for row in board]
    snake_list = snake.to_list()
    snake_set = snake.positions if hasattr(snake, 'positions') else set(snake_list)

    for fx, fy in food_set:
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

