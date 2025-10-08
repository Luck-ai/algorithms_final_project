import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
import random
from gamelogic import Snake, generate_food, generate_bombs, count_adjacent_bombs, heapSort

pygame.init()
pygame.mixer.init()


BOARD_WIDTH = 10
BOARD_HEIGHT = 8
CELL_SIZE = 70
SIDEBAR_WIDTH = 380
HEADER_HEIGHT = 140
PADDING = 20

GAME_AREA_WIDTH = BOARD_WIDTH * CELL_SIZE
GAME_AREA_HEIGHT = BOARD_HEIGHT * CELL_SIZE
WINDOW_WIDTH = GAME_AREA_WIDTH + SIDEBAR_WIDTH + PADDING * 3
WINDOW_HEIGHT = GAME_AREA_HEIGHT + HEADER_HEIGHT + PADDING * 2

COLORS = {
    'bg': (76, 111, 68),
    'board_bg_light': (170, 215, 81),
    'board_bg_dark': (162, 209, 73),
    'grid': (147, 195, 65),
    'sidebar': (60, 88, 54),
    'header': (60, 88, 54),
    'snake_head': (34, 139, 34),
    'snake_body': (50, 205, 50),
    'snake_eye': (255, 255, 255),
    'snake_pupil': (30, 30, 40),
    'food': (230, 70, 70),
    'food_highlight': (255, 120, 120),
    'food_stem': (60, 150, 60),
    'bomb': (50, 50, 60),
    'bomb_highlight': (255, 100, 50),
    'text': (255, 255, 255),
    'text_dim': (200, 220, 180),
    'accent': (255, 215, 70),
    'success': (130, 220, 90),
    'danger': (230, 70, 70),
    'warning': (255, 215, 70),
    'shadow': (40, 60, 35),
    'button': (90, 130, 80),
    'button_hover': (110, 150, 100),
}

DIRECTIONS = {
        pygame.K_w: (0, -1),
        pygame.K_UP: (0, -1),
        pygame.K_s: (0, 1),
        pygame.K_DOWN: (0, 1),
        pygame.K_a: (-1, 0),
        pygame.K_LEFT: (-1, 0),
        pygame.K_d: (1, 0),
        pygame.K_RIGHT: (1, 0),
    }

class GameGUI:
    def __init__(self, food_count=3, bomb_count=7, trial=False):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍💣 SnakeSweeper")
        try:
            icon = pygame.Surface((32, 32))
            icon.fill(COLORS['snake_head'])
            pygame.display.set_icon(icon)
        except:
            pass
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 22)
        self.food_count = food_count
        self.bomb_count = bomb_count
        self.trial = trial
        self.undo_stack = []
        self.MAX_UNDOS = 3
        self.remaining_undos = self.MAX_UNDOS
        self.pulse_offset = 0
        self.grid_offset = 0
        self.game_over = False
        self.game_over_message = ""
        self.victory = False
        self.leaderboard_file = os.path.join(os.path.dirname(__file__), "leaderboard.txt")
        self.leaderboard = self.load_leaderboard()
        print(f"Loaded {len(self.leaderboard)} scores from {self.leaderboard_file}")
        self.player_name = None
        self.show_name_input = False
        self.name_input_text = ""
        self.show_leaderboard_screen = False
        self.reset_game()
        self.last_move_time = 0
        self.move_cooldown = 100
    def reset_game(self):
        self.snake = Snake()
        self.snake.add_head(BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
        self.score = 0
        temp_empty_bombs = set()
        self.food_set = generate_food(self.snake, temp_empty_bombs, self.food_count)
        self.bombs = generate_bombs(self.snake, self.food_set, self.bomb_count)
        self.game_over = False
        self.game_over_message = ""
        self.victory = False
        self.undo_stack = []
        self.remaining_undos = self.MAX_UNDOS
        self.show_name_input = False
        self.name_input_text = ""
    def draw_rounded_rect(self, surface, color, rect, radius=10):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    def draw_gradient_rect(self, surface, color1, color2, rect):
        for i in range(rect.height):
            ratio = i / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x, rect.y + i), 
                           (rect.x + rect.width, rect.y + i))
    def load_leaderboard(self):
        leaderboard = []
        try:
            with open(self.leaderboard_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    name_part, score_part = line.split(':', 1)
                    try:
                        leaderboard.append([name_part.strip(), int(score_part.strip())])
                    except ValueError:
                        continue
        except FileNotFoundError:
            leaderboard = []
        return leaderboard
    def save_score(self, name, score):
        print(f"Saving score: {name} - {score} to {self.leaderboard_file}")
        with open(self.leaderboard_file, 'a') as file:
            file.write(f"{name}:{score}\n")
        self.leaderboard.append([name, score])
        self.leaderboard = heapSort(self.leaderboard)
        print(f"Leaderboard now has {len(self.leaderboard)} entries")
    def get_top_leaderboard(self, count=5):
        sorted_board = heapSort(self.leaderboard.copy())
        return sorted_board[:count]
    def draw_header(self):
        header_rect = pygame.Rect(PADDING, PADDING, WINDOW_WIDTH - PADDING * 2, HEADER_HEIGHT)
        shadow_rect = header_rect.copy()
        shadow_rect.y += 4
        self.draw_rounded_rect(self.screen, COLORS['shadow'], shadow_rect, 20)
        self.draw_rounded_rect(self.screen, COLORS['header'], header_rect, 20)
        title_shadow = self.font_large.render("SNAKESWEEPER", True, COLORS['shadow'])
        title = self.font_large.render("SNAKESWEEPER", True, COLORS['accent'])
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, PADDING + 35))
        shadow_rect = title_rect.copy()
        shadow_rect.y += 3
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        score_bg = pygame.Rect(PADDING + 15, PADDING + 75, 160, 35)
        self.draw_rounded_rect(self.screen, COLORS['button'], score_bg, 10)
        score_text = self.font_small.render(f"SCORE: {self.score}", True, COLORS['text'])
        score_rect = score_text.get_rect(center=score_bg.center)
        self.screen.blit(score_text, score_rect)
        undo_bg = pygame.Rect(WINDOW_WIDTH // 2 - 80, PADDING + 75, 160, 35)
        undo_color_bg = COLORS['button'] if self.remaining_undos > 0 else COLORS['shadow']
        self.draw_rounded_rect(self.screen, undo_color_bg, undo_bg, 10)
        undo_text = self.font_small.render(f"UNDO: {self.remaining_undos}/{self.MAX_UNDOS}", True, COLORS['text'])
        undo_rect = undo_text.get_rect(center=undo_bg.center)
        self.screen.blit(undo_text, undo_rect)
        if self.trial:
            trial_bg = pygame.Rect(WINDOW_WIDTH - PADDING - 175, PADDING + 75, 160, 35)
            self.draw_rounded_rect(self.screen, COLORS['danger'], trial_bg, 10)
            trial_text = self.font_small.render("PRACTICE", True, COLORS['text'])
            trial_rect = trial_text.get_rect(center=trial_bg.center)
            self.screen.blit(trial_text, trial_rect)
    def draw_board(self):
        board_x = PADDING
        board_y = HEADER_HEIGHT + PADDING * 2
        shadow_rect = pygame.Rect(board_x, board_y + 4, GAME_AREA_WIDTH, GAME_AREA_HEIGHT)
        self.draw_rounded_rect(self.screen, COLORS['shadow'], shadow_rect, 20)
        board_rect = pygame.Rect(board_x, board_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT)
        board_surface = pygame.Surface((GAME_AREA_WIDTH, GAME_AREA_HEIGHT), pygame.SRCALPHA)
        temp_rect = pygame.Rect(0, 0, GAME_AREA_WIDTH, GAME_AREA_HEIGHT)
        pygame.draw.rect(board_surface, COLORS['board_bg_light'], temp_rect, border_radius=20)
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if (x + y) % 2 == 1:
                    cell_rect = pygame.Rect(
                        x * CELL_SIZE,
                        y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(board_surface, COLORS['board_bg_dark'], cell_rect)
        self.screen.blit(board_surface, (board_x, board_y))
        if self.trial:
            for bx, by in self.bombs:
                self.draw_bomb(bx, by, board_x, board_y)
        for fx, fy in self.food_set:
            self.draw_food(fx, fy, board_x, board_y)
        snake_list = self.snake.to_list()
        head_coords = self.snake.head_coordinates()
        for idx, (sx, sy) in enumerate(snake_list):
            is_head = (sx, sy) == head_coords
            self.draw_snake_segment(sx, sy, board_x, board_y, is_head)
        head_x, head_y = head_coords
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = head_x + dx, head_y + dy
            if 0 <= nx < BOARD_WIDTH and 0 <= ny < BOARD_HEIGHT:
                pos = (nx, ny)
                if pos not in self.food_set and pos not in self.snake.positions:
                    count = count_adjacent_bombs(nx, ny, self.bombs)
                    self.draw_bomb_count(nx, ny, count, board_x, board_y)
    def draw_snake_segment(self, x, y, offset_x, offset_y, is_head=False):
        cell_x = offset_x + x * CELL_SIZE
        cell_y = offset_y + y * CELL_SIZE
        center_x = cell_x + CELL_SIZE // 2
        center_y = cell_y + CELL_SIZE // 2
        if is_head:
            radius = 26
            pygame.draw.circle(self.screen, COLORS['shadow'], (center_x + 2, center_y + 2), radius)
            pygame.draw.circle(self.screen, COLORS['snake_head'], (center_x, center_y), radius)
            eye_offset_x = 10
            eye_offset_y = -6
            eye_radius = 7
            pupil_radius = 4
            left_eye_pos = (center_x - eye_offset_x, center_y + eye_offset_y)
            pygame.draw.circle(self.screen, COLORS['snake_eye'], left_eye_pos, eye_radius)
            pygame.draw.circle(self.screen, COLORS['snake_pupil'], left_eye_pos, pupil_radius)
            right_eye_pos = (center_x + eye_offset_x, center_y + eye_offset_y)
            pygame.draw.circle(self.screen, COLORS['snake_eye'], right_eye_pos, eye_radius)
            pygame.draw.circle(self.screen, COLORS['snake_pupil'], right_eye_pos, pupil_radius)
        else:
            radius = 24
            pygame.draw.circle(self.screen, COLORS['shadow'], (center_x + 2, center_y + 2), radius)
            pygame.draw.circle(self.screen, COLORS['snake_body'], (center_x, center_y), radius)
            highlight_pos = (center_x - 6, center_y - 6)
            pygame.draw.circle(self.screen, (100, 255, 100), highlight_pos, 6)
    def draw_food(self, x, y, offset_x, offset_y):
        cell_x = offset_x + x * CELL_SIZE
        cell_y = offset_y + y * CELL_SIZE
        center_x = cell_x + CELL_SIZE // 2
        center_y = cell_y + CELL_SIZE // 2
        radius = 20
        pygame.draw.circle(self.screen, COLORS['shadow'], (center_x + 2, center_y + 2), radius)
        pygame.draw.circle(self.screen, COLORS['food'], (center_x, center_y), radius)
        highlight_pos = (center_x - 7, center_y - 7)
        pygame.draw.circle(self.screen, COLORS['food_highlight'], highlight_pos, 7)
        stem_rect = pygame.Rect(center_x - 2, center_y - radius - 6, 4, 8)
        pygame.draw.rect(self.screen, COLORS['food_stem'], stem_rect, border_radius=2)
        leaf_points = [
            (center_x + 3, center_y - radius - 4),
            (center_x + 10, center_y - radius - 6),
            (center_x + 8, center_y - radius - 1),
        ]
        pygame.draw.polygon(self.screen, COLORS['food_stem'], leaf_points)
    def draw_bomb(self, x, y, offset_x, offset_y):
        cell_x = offset_x + x * CELL_SIZE
        cell_y = offset_y + y * CELL_SIZE
        center_x = cell_x + CELL_SIZE // 2
        center_y = cell_y + CELL_SIZE // 2
        radius = 18
        pygame.draw.circle(self.screen, COLORS['shadow'], (center_x + 2, center_y + 2), radius)
        pygame.draw.circle(self.screen, COLORS['bomb'], (center_x, center_y), radius)
        fuse_start = (center_x, center_y - radius)
        fuse_end = (center_x - 4, center_y - radius - 10)
        pygame.draw.line(self.screen, (80, 80, 90), fuse_start, fuse_end, 3)
        spark_colors = [(255, 200, 50), (255, 150, 50), (255, 100, 50)]
        spark_time = pygame.time.get_ticks() % 300
        if spark_time < 100:
            pygame.draw.circle(self.screen, spark_colors[0], fuse_end, 4)
        elif spark_time < 200:
            pygame.draw.circle(self.screen, spark_colors[1], fuse_end, 3)
        else:
            pygame.draw.circle(self.screen, spark_colors[2], fuse_end, 2)
        highlight_pos = (center_x - 6, center_y - 6)
        pygame.draw.circle(self.screen, (80, 80, 90), highlight_pos, 5)
    def draw_bomb_count(self, x, y, count, offset_x, offset_y):
        cell_x = offset_x + x * CELL_SIZE
        cell_y = offset_y + y * CELL_SIZE
        center_x = cell_x + CELL_SIZE // 2
        center_y = cell_y + CELL_SIZE // 2
        if count == 0:
            color = COLORS['success']
            bg_color = (100, 180, 70)
        elif count >= 4:
            color = COLORS['danger']
            bg_color = (180, 50, 50)
        elif count >= 2:
            color = COLORS['warning']
            bg_color = (200, 160, 50)
        else:
            color = (180, 200, 160)
            bg_color = (100, 130, 90)
        bg_size = 32
        bg_rect = pygame.Rect(
            center_x - bg_size // 2 + 1,
            center_y - bg_size // 2 + 1,
            bg_size, bg_size
        )
        shadow_rect = bg_rect.copy()
        shadow_rect.y += 2
        self.draw_rounded_rect(self.screen, COLORS['shadow'], shadow_rect, 8)
        self.draw_rounded_rect(self.screen, bg_color, bg_rect, 8)
        text = self.font_medium.render(str(count), True, COLORS['text'])
        text_rect = text.get_rect(center=(center_x, center_y))
        self.screen.blit(text, text_rect)
    def draw_sidebar(self):
        sidebar_x = GAME_AREA_WIDTH + PADDING * 2
        sidebar_y = HEADER_HEIGHT + PADDING * 2
        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, SIDEBAR_WIDTH, GAME_AREA_HEIGHT)
        shadow_rect = sidebar_rect.copy()
        shadow_rect.y += 4
        self.draw_rounded_rect(self.screen, COLORS['shadow'], shadow_rect, 20)
        self.draw_rounded_rect(self.screen, COLORS['sidebar'], sidebar_rect, 20)
        y_offset = sidebar_y + 20
        title = self.font_medium.render("Controls", True, COLORS['accent'])
        self.screen.blit(title, (sidebar_x + 20, y_offset))
        y_offset += 50
        instructions = [
            ("WASD / Arrows", "Move"),
            ("Z", "Undo move"),
            ("R", "Restart game"),
            ("L", "Leaderboard"),
            ("Q / ESC", "Quit"),
        ]
        for key, action in instructions:
            key_text = self.font_tiny.render(key, True, COLORS['warning'])
            action_text = self.font_tiny.render(action, True, COLORS['text_dim'])
            self.screen.blit(key_text, (sidebar_x + 20, y_offset))
            self.screen.blit(action_text, (sidebar_x + 140, y_offset))
            y_offset += 30
        y_offset += 20
        info_title = self.font_medium.render("Game Info", True, COLORS['accent'])
        self.screen.blit(info_title, (sidebar_x + 20, y_offset))
        y_offset += 40
        info_lines = [
            f"Snake Length: {self.snake.length}",
            f"Food Left: {len(self.food_set)}",
            f"Total Bombs: {len(self.bombs)}",
        ]
        for line in info_lines:
            text = self.font_tiny.render(line, True, COLORS['text'])
            self.screen.blit(text, (sidebar_x + 20, y_offset))
            y_offset += 30
        y_offset += 20
        leaderboard_title = self.font_medium.render("Top 3 Scores", True, COLORS['accent'])
        self.screen.blit(leaderboard_title, (sidebar_x + 20, y_offset))
        y_offset += 40
        top_scores = self.get_top_leaderboard(3)
        if top_scores:
            for i, (name, score) in enumerate(top_scores, start=1):
                display_name = name[:10] + "..." if len(name) > 10 else name
                score_line = f"{i}. {display_name}: {score}"
                score_color = COLORS['accent'] if i == 1 else COLORS['text']
                text = self.font_tiny.render(score_line, True, score_color)
                self.screen.blit(text, (sidebar_x + 20, y_offset))
                y_offset += 30
        else:
            no_scores = self.font_tiny.render("No scores yet!", True, COLORS['text_dim'])
            self.screen.blit(no_scores, (sidebar_x + 20, y_offset))
            y_offset += 30
        y_offset += 10
        hint = self.font_tiny.render("Press L for full list", True, COLORS['text_dim'])
        self.screen.blit(hint, (sidebar_x + 20, y_offset))
    def draw_leaderboard_screen(self):
        self.screen.fill(COLORS['bg'])
        box_width = 600
        box_height = 600
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = (WINDOW_HEIGHT - box_height) // 2
        shadow_rect = pygame.Rect(box_x, box_y + 4, box_width, box_height)
        self.draw_rounded_rect(self.screen, COLORS['shadow'], shadow_rect, 20)
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        self.draw_rounded_rect(self.screen, COLORS['header'], box_rect, 20)
        pygame.draw.rect(self.screen, COLORS['accent'], box_rect, 4, border_radius=20)
        title = self.font_large.render("🏆 LEADERBOARD 🏆", True, COLORS['accent'])
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, box_y + 50))
        self.screen.blit(title, title_rect)
        divider_y = box_y + 90
        pygame.draw.line(self.screen, COLORS['accent'], 
                        (box_x + 40, divider_y), 
                        (box_x + box_width - 40, divider_y), 3)
        y_offset = box_y + 110
        rank_header = self.font_small.render("RANK", True, COLORS['accent'])
        name_header = self.font_small.render("NAME", True, COLORS['accent'])
        score_header = self.font_small.render("SCORE", True, COLORS['accent'])
        self.screen.blit(rank_header, (box_x + 60, y_offset))
        self.screen.blit(name_header, (box_x + 200, y_offset))
        self.screen.blit(score_header, (box_x + 450, y_offset))
        y_offset += 45
        top_scores = self.get_top_leaderboard(10)
        if top_scores:
            for i, (name, score) in enumerate(top_scores, start=1):
                if i % 2 == 0:
                    row_rect = pygame.Rect(box_x + 30, y_offset - 8, box_width - 60, 40)
                    self.draw_rounded_rect(self.screen, COLORS['button'], row_rect, 8)
                if i == 1:
                    rank_text = "🥇"
                    text_color = COLORS['accent']
                elif i == 2:
                    rank_text = "🥈"
                    text_color = COLORS['text']
                elif i == 3:
                    rank_text = "🥉"
                    text_color = COLORS['text']
                else:
                    rank_text = f"{i}."
                    text_color = COLORS['text_dim']
                display_name = name[:20] if len(name) <= 20 else name[:17] + "..."
                rank_surface = self.font_small.render(rank_text, True, text_color)
                name_surface = self.font_small.render(display_name, True, text_color)
                score_surface = self.font_small.render(str(score), True, text_color)
                self.screen.blit(rank_surface, (box_x + 60, y_offset))
                self.screen.blit(name_surface, (box_x + 200, y_offset))
                self.screen.blit(score_surface, (box_x + 450, y_offset))
                y_offset += 42
        else:
            no_scores = self.font_medium.render("No scores yet!", True, COLORS['text_dim'])
            no_scores_rect = no_scores.get_rect(center=(WINDOW_WIDTH // 2, box_y + 300))
            self.screen.blit(no_scores, no_scores_rect)
            play_msg = self.font_small.render("Play a game to get on the board!", True, COLORS['text_dim'])
            play_rect = play_msg.get_rect(center=(WINDOW_WIDTH // 2, box_y + 340))
            self.screen.blit(play_msg, play_rect)
        instruction = self.font_small.render("Press L to return to game  |  Press Q to quit", True, COLORS['text_dim'])
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, box_x + box_height - 30))
        self.screen.blit(instruction, instruction_rect)
    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(COLORS['bg'])
        self.screen.blit(overlay, (0, 0))
        if self.show_name_input:
            box_width = 500
            box_height = 250
            box_x = (WINDOW_WIDTH - box_width) // 2
            box_y = (WINDOW_HEIGHT - box_height) // 2
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            self.draw_rounded_rect(self.screen, COLORS['header'], box_rect, 20)
            pygame.draw.rect(self.screen, COLORS['accent'], box_rect, 4, border_radius=20)
            title = self.font_large.render("Game Over!", True, COLORS['accent'])
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, box_y + 50))
            self.screen.blit(title, title_rect)
            score_text = self.font_medium.render(f"Score: {self.score}", True, COLORS['success'])
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, box_y + 100))
            self.screen.blit(score_text, score_rect)
            prompt = self.font_small.render("Enter your name:", True, COLORS['text'])
            prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH // 2, box_y + 140))
            self.screen.blit(prompt, prompt_rect)
            input_box = pygame.Rect(box_x + 100, box_y + 165, 300, 40)
            self.draw_rounded_rect(self.screen, COLORS['button'], input_box, 10)
            pygame.draw.rect(self.screen, COLORS['accent'], input_box, 2, border_radius=10)
            text_surface = self.font_small.render(self.name_input_text + "_", True, COLORS['text'])
            text_rect = text_surface.get_rect(left=input_box.left + 10, centery=input_box.centery)
            self.screen.blit(text_surface, text_rect)
            instruction = self.font_tiny.render("Press ENTER to save, ESC to skip", True, COLORS['text_dim'])
            instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, box_y + 220))
            self.screen.blit(instruction, instruction_rect)
        else:
            box_width = 500
            box_height = 300
            box_x = (WINDOW_WIDTH - box_width) // 2
            box_y = (WINDOW_HEIGHT - box_height) // 2
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            self.draw_rounded_rect(self.screen, COLORS['header'], box_rect, 20)
            pygame.draw.rect(self.screen, COLORS['accent'], box_rect, 4, border_radius=20)
            title_color = COLORS['success'] if self.victory else COLORS['danger']
            title_text = "Victory! 🎉" if self.victory else "Game Over! 💀"
            title = self.font_large.render(title_text, True, title_color)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, box_y + 60))
            self.screen.blit(title, title_rect)
            message = self.font_medium.render(self.game_over_message, True, COLORS['text'])
            message_rect = message.get_rect(center=(WINDOW_WIDTH // 2, box_y + 120))
            self.screen.blit(message, message_rect)
            score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLORS['accent'])
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, box_y + 170))
            self.screen.blit(score_text, score_rect)
            restart = self.font_small.render("Press R to Restart or Q to Quit", True, COLORS['text_dim'])
            restart_rect = restart.get_rect(center=(WINDOW_WIDTH // 2, box_y + 240))
            self.screen.blit(restart, restart_rect)
    def handle_move(self, direction):
        if self.game_over:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_cooldown:
            return
        self.last_move_time = current_time
        dx, dy = direction
        head_x, head_y = self.snake.head.x, self.snake.head.y
        new_x, new_y = head_x + dx, head_y + dy
        if new_x < 0 or new_x >= BOARD_WIDTH or new_y < 0 or new_y >= BOARD_HEIGHT:
            self.game_over = True
            self.game_over_message = "Hit the wall!"
            if not self.trial:
                self.show_name_input = True
            return
        if (new_x, new_y) in self.snake.positions:
            self.game_over = True
            self.game_over_message = "Ate yourself!"
            if not self.trial:
                self.show_name_input = True
            return
        if (new_x, new_y) in self.bombs:
            self.game_over = True
            self.game_over_message = "Hit a bomb!"
            if not self.trial:
                self.show_name_input = True
            return
        self.snake.add_head(new_x, new_y)
        removed_tail = None
        ate = False
        eaten_pos = None
        respawned_food = None
        if (new_x, new_y) in self.food_set:
            ate = True
            eaten_pos = (new_x, new_y)
            if not self.trial:
                self.score += 10
            self.food_set.discard(eaten_pos)
            attempts = 0
            while attempts < 100:
                fx = random.randint(0, BOARD_WIDTH - 1)
                fy = random.randint(0, BOARD_HEIGHT - 1)
                pos = (fx, fy)
                if pos not in self.snake.positions and pos not in self.food_set and pos not in self.bombs:
                    self.food_set.add(pos)
                    respawned_food = pos
                    break
                attempts += 1
        else:
            removed_tail = self.snake.remove_tail()
        move_info = {
            'head': (new_x, new_y),
            'removed_tail': removed_tail,
            'ate': ate,
            'eaten_pos': eaten_pos,
            'respawned_food': respawned_food,
        }
        self.undo_stack.append(('move', move_info))
    def handle_undo(self):
        if self.remaining_undos <= 0:
            print("No more undos available!")
            return
        if not self.undo_stack:
            print("Nothing to undo!")
            return
        kind, info = self.undo_stack.pop()
        if kind != 'move':
            return
        self.snake.remove_head()
        if info.get('ate'):
            if not self.trial:
                self.score -= 10
            respawned = info.get('respawned_food')
            if respawned and respawned in self.food_set:
                self.food_set.discard(respawned)
            eaten_pos = info.get('eaten_pos')
            if eaten_pos:
                self.food_set.add(eaten_pos)
        else:
            removed_tail = info.get('removed_tail')
            if removed_tail:
                self.snake.append_tail(removed_tail)
        self.remaining_undos -= 1
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.show_name_input:
                        if event.key == pygame.K_RETURN:
                            if self.name_input_text.strip():
                                self.save_score(self.name_input_text.strip(), self.score)
                            self.show_name_input = False
                        elif event.key == pygame.K_ESCAPE:
                            self.show_name_input = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_input_text = self.name_input_text[:-1]
                        elif len(self.name_input_text) < 20 and event.unicode.isprintable():
                            self.name_input_text += event.unicode
                    else:
                        if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_l:
                            self.show_leaderboard_screen = not self.show_leaderboard_screen
                        elif event.key == pygame.K_r and not self.show_leaderboard_screen:
                            self.reset_game()
                        elif event.key == pygame.K_z and not self.show_leaderboard_screen:
                            self.handle_undo()
                        elif event.key in DIRECTIONS and not self.game_over and not self.show_leaderboard_screen:
                            self.handle_move(DIRECTIONS[event.key])
            if self.show_leaderboard_screen:
                self.draw_leaderboard_screen()
            else:
                self.screen.fill(COLORS['bg'])
                self.draw_header()
                self.draw_board()
                self.draw_sidebar()
                if self.game_over:
                    self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        return self.score