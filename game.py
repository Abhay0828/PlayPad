import pygame
import random
import sys
import time
import json
import math
from typing import List, Dict, Tuple

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4-in-1 Game Station")

# Constants
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (128, 0, 128)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)
    DARK_GRAY = (30, 30, 30)
    LIGHT_GRAY = (200, 200, 200)
    NEON_BLUE = (0, 200, 255)
    NEON_PINK = (255, 0, 200)

# Fonts
class Fonts:
    try:
        title = pygame.font.SysFont('orbitron', 60, bold=True)
        menu = pygame.font.SysFont('orbitron', 36)
        game = pygame.font.SysFont('orbitron', 28)
        small = pygame.font.SysFont('orbitron', 20)
    except:
        title = pygame.font.SysFont('comicsans', 60, bold=True)
        menu = pygame.font.SysFont('comicsans', 36)
        game = pygame.font.SysFont('comicsans', 28)
        small = pygame.font.SysFont('comicsans', 20)

# Game states
class GameStates:
    MENU = 0
    SCRAMBLED_SAGA = 1
    BLOCK_BUSTER = 2
    SNAKE_GAME = 3
    MEMORY_GAME = 4
    EXIT_CONFIRM = 5
    SETTINGS = 6

# Utility functions
def create_gradient_surface(size, color1, color2, vertical=True):
    surface = pygame.Surface(size, pygame.SRCALPHA)

    
    for i in range(size[1 if vertical else 0]):
        ratio = i / (size[1 if vertical else 0] - 1)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        if vertical:
            pygame.draw.line(surface, (r, g, b), (0, i), (size[0], i))
        else:
            pygame.draw.line(surface, (r, g, b), (i, 0), (i, size[1]))
    return surface

def render_text_with_gradient(text, font, color1, color2):
    surface = font.render(text, True, color1)
    grad = create_gradient_surface((surface.get_width(), surface.get_height()), color1, color2, False)
    surface.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surface

def render_text_with_shadow(text, font, color, shadow_color, shadow_offset=(2, 2)):
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)
    surface = pygame.Surface((main.get_width() + shadow_offset[0], main.get_height() + shadow_offset[1]), pygame.SRCALPHA)
    surface.blit(shadow, shadow_offset)
    surface.blit(main, (0, 0))
    return surface

class Particle:
    def __init__(self, x, y, color, shape='circle'):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.color = color
        self.lifetime = random.randint(20, 50)
        self.size = random.randint(3, 8)
        self.shape = shape
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.alpha = max(0, int(255 * (self.lifetime / 50)))

    def draw(self, surface):
        if self.lifetime > 0:
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color = (*self.color[:3], self.alpha)
            if self.shape == 'circle':
                pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
            elif self.shape == 'square':
                pygame.draw.rect(temp_surface, color, (0, 0, self.size * 2, self.size * 2))
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, Colors.WHITE, (int(self.x), int(self.y)), self.size)

# High score manager
class HighScoreManager:
    def __init__(self):
        self.filename = "high_scores.json"
        self.scores = {
            'scrambled_saga': 0,
            'block_buster': 0,
            'snake_game': 0,
            'memory_game': 0
        }
        self.load_scores()

    def load_scores(self):
        try:
            with open(self.filename, 'r') as f:
                self.scores = json.load(f)
        except FileNotFoundError:
            self.save_scores()

    def save_scores(self):
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f)

    def update_score(self, game: str, score: int):
        if score > self.scores[game]:
            self.scores[game] = score
            self.save_scores()

# Game 1: Scrambled Saga
class ScrambledSaga:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.current_word = ""
        self.scrambled_word = ""
        self.user_input = ""
        self.words_by_level = {
            1: ["banana", "dog", "cat", "tree", "book", "water", "eraser"],
            2: ["lizard", "giraffe", "kangaroo", "computer", "keyboard", "monitor", "clap"],
            3: ["extravaganza", "magnificent", "quadrilateral", "piano", "quintessential"]
        }
        self.time_limit = 30
        self.start_time = 0
        self.hint_used = False
        self.paused = False
        self.difficulty = 1
        self.particles = []
        self.score_animation = 0
        self.background_offset = 0

    def new_word(self):
        word_list = self.words_by_level.get(self.level, self.words_by_level[3])
        self.current_word = random.choice(word_list)
        self.scrambled_word = self.scramble_word(self.current_word)
        self.user_input = ""
        self.hint_used = False
        self.start_time = time.time()

    def scramble_word(self, word: str) -> str:
        letters = list(word)
        while True:
            random.shuffle(letters)
            scrambled = ''.join(letters)
            if scrambled != word:
                return scrambled

    def check_answer(self) -> bool:
        if self.user_input.lower() == self.current_word.lower():
            score_multipliers = {1: 1, 2: 2, 3: 3}
            points = len(self.current_word) * score_multipliers.get(self.difficulty, 1)
            if not self.hint_used:
                points += 5
            self.score += points
            self.score_animation = points
            for _ in range(15):
                self.particles.append(Particle(WIDTH // 2, HEIGHT // 2, Colors.YELLOW, random.choice(['circle', 'square'])))
            return True
        self.lives -= 1
        return False

    def get_hint(self) -> str:
        self.hint_used = True
        hint = ""
        for i, letter in enumerate(self.current_word):
            if i < len(self.current_word) // 2:
                hint += letter
            else:
                hint += "_"
        return hint

    def time_remaining(self) -> float:
        if not self.paused:
            elapsed = time.time() - self.start_time
            return max(0, self.time_limit - elapsed * self.difficulty)
        return self.time_limit

    def set_difficulty(self, difficulty: int):
        self.difficulty = max(1, min(3, difficulty))
        self.time_limit = {1: 30, 2: 20, 3: 15}[self.difficulty]
        self.lives = {1: 5, 2: 3, 3: 2}[self.difficulty]

    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for p in self.particles:
            p.update()
        self.background_offset = (self.background_offset + 0.5) % HEIGHT
        if self.score_animation > 0:
            self.score_animation -= 1

    def draw_background(self, surface):
        cloud_surface = create_gradient_surface((WIDTH, HEIGHT), (*Colors.PURPLE[:3], 50), Colors.BLACK)
        for y in range(-HEIGHT, HEIGHT, 100):
            pygame.draw.ellipse(surface, Colors.WHITE, (100, (y + self.background_offset) % HEIGHT, 200, 50), 2)
        surface.blit(cloud_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

# Game 2: Block Buster Bonanza
class BlockBusterBonanza:
    def __init__(self):
        self.reset()

    def reset(self):
        self.paddle_width = 100
        self.paddle_height = 15
        self.paddle_x = WIDTH // 2 - self.paddle_width // 2
        self.paddle_y = HEIGHT - 30
        self.paddle_speed = 8
        self.paddle_shake = 0

        self.ball_radius = 10
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_dx = 5 * random.choice([-1, 1])
        self.ball_dy = -5
        self.ball_speed = 5

        self.level = 1
        self.score = 0
        self.lives = 3
        self.blocks = []
        self.game_over = False
        self.level_complete = False
        self.power_ups = []
        self.paddle_powered = False
        self.power_timer = 0
        self.paused = False
        self.difficulty = 1
        self.particles = []
        self.score_animation = 0
        self.background_offset = 0
        self.create_blocks()

    def create_blocks(self):
        self.blocks = []
        rows = self.level + 2
        cols = 8
        block_width = WIDTH // cols - 5
        block_height = 20

        colors = [Colors.RED, Colors.GREEN, Colors.BLUE, Colors.YELLOW, Colors.PURPLE, Colors.CYAN, Colors.ORANGE]

        for row in range(rows):
            for col in range(cols):
                color = colors[row % len(colors)]
                hits = 1
                if self.difficulty == 3:
                    level_hits = max(1, min((self.level or 1) // 2, 3))
                    hits = level_hits
                block = {
                    "x": 5 + col * (block_width + 5),
                    "y": 50 + row * (block_height + 5),
                    "width": block_width,
                    "height": block_height,
                    "color": color,
                    "hits": hits
                }
                self.blocks.append(block)

    def update(self):
        if self.paused:
            return

        # Mouse control for paddle
        mouse_x, _ = pygame.mouse.get_pos()
        if mouse_x > 0 and mouse_x < WIDTH - self.paddle_width:
            self.paddle_x = mouse_x

        self.ball_x += self.ball_dx * self.difficulty
        self.ball_y += self.ball_dy * self.difficulty

        if self.ball_x <= self.ball_radius or self.ball_x >= WIDTH - self.ball_radius:
            self.ball_dx *= -1

        if self.ball_y <= self.ball_radius:
            self.ball_dy *= -1

        if (self.ball_y + self.ball_radius >= self.paddle_y and
                self.ball_y - self.ball_radius <= self.paddle_y + self.paddle_height and
                self.ball_x >= self.paddle_x and self.ball_x <= self.paddle_x + self.paddle_width):
            relative_x = (self.ball_x - self.paddle_x) / self.paddle_width
            angle = relative_x * 2 - 1
            self.ball_dx = angle * 7 * self.difficulty
            self.ball_dy *= -1
            self.paddle_shake = 10
            for _ in range(5):
                self.particles.append(Particle(self.ball_x, self.paddle_y, Colors.NEON_BLUE, 'circle'))

        if self.ball_y > HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_x = WIDTH // 2
                self.ball_y = HEIGHT // 2
                self.ball_dx = 5 * random.choice([-1, 1]) * self.difficulty
                self.ball_dy = -5 * self.difficulty

        for block in self.blocks[:]:
            if (self.ball_x + self.ball_radius > block["x"] and
                    self.ball_x - self.ball_radius < block["x"] + block["width"] and
                    self.ball_y + self.ball_radius > block["y"] and
                    self.ball_y - self.ball_radius < block["y"] + block["height"]):
                block["hits"] -= 1
                if block["hits"] <= 0:
                    self.blocks.remove(block)
                    points = 10 * self.level * self.difficulty
                    self.score += points
                    self.score_animation = points
                    for _ in range(10):
                        self.particles.append(Particle(block["x"] + block["width"] // 2,
                                                     block["y"] + block["height"] // 2,
                                                     block["color"], random.choice(['circle', 'square'])))
                    if random.random() < 0.2:
                        self.power_ups.append({
                            "x": block["x"] + block["width"] // 2,
                            "y": block["y"],
                            "type": random.choice(["expand", "slow", "extra_life"])
                        })
                if self.ball_x < block["x"] or self.ball_x > block["x"] + block["width"]:
                    self.ball_dx *= -1
                else:
                    self.ball_dy *= -1
                break

        if len(self.blocks) == 0:
            self.level_complete = True

        for power in self.power_ups[:]:
            power["y"] += 3
            if (power["y"] >= self.paddle_y and
                    power["x"] >= self.paddle_x and
                    power["x"] <= self.paddle_x + self.paddle_width):
                if power["type"] == "expand":
                    self.paddle_width = 150
                    self.paddle_powered = True
                    self.power_timer = pygame.time.get_ticks()
                elif power["type"] == "slow":
                    self.ball_speed = max(3, self.ball_speed - 2)
                    self.paddle_powered = True
                    self.power_timer = pygame.time.get_ticks()
                elif power["type"] == "extra_life":
                    self.lives += 1
                self.power_ups.remove(power)
            elif power["y"] > HEIGHT:
                self.power_ups.remove(power)

        if self.paddle_powered and pygame.time.get_ticks() - self.power_timer > 5000:
            self.paddle_width = 100
            self.ball_speed = 5
            self.paddle_powered = False

        self.particles = [p for p in self.particles if p.lifetime > 0]
        for p in self.particles:
            p.update()
        self.background_offset = (self.background_offset + 1) % WIDTH
        if self.score_animation > 0:
            self.score_animation -= 1
        if self.paddle_shake > 0:
            self.paddle_shake -= 1

    def draw_background(self, surface):
        grid_surface = create_gradient_surface((WIDTH, HEIGHT), (*Colors.BLUE[:3], 50), Colors.BLACK)
        for x in range(-WIDTH, WIDTH, 50):
            pygame.draw.line(surface, Colors.NEON_BLUE, ((x + self.background_offset) % WIDTH, 0),
                            ((x + self.background_offset) % WIDTH, HEIGHT), 1)
        surface.blit(grid_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

    def next_level(self):
        self.level += 1
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_dx = 5 * random.choice([-1, 1]) * self.difficulty
        self.ball_dy = -5 * self.difficulty
        self.create_blocks()
        self.level_complete = False
        self.power_ups = []
        self.paddle_powered = False

    def set_difficulty(self, difficulty: int):
        self.difficulty = max(1, min(3, difficulty))
        self.ball_speed = {1: 5, 2: 6, 3: 7}[self.difficulty]
        self.lives = {1: 5, 2: 3, 3: 2}[self.difficulty]

# Game 3: Snake Game
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake_size = 20
        self.snake_x = WIDTH // 2
        self.snake_y = HEIGHT // 2
        self.snake_dx = self.snake_size
        self.snake_dy = 0
        self.snake_body = []
        self.snake_length = 1
        self.fruit_x = 0
        self.fruit_y = 0
        self.fruit_size = 20
        self.score = 0
        self.level = 1
        self.game_over = False
        self.place_fruit()
        self.speed = 10
        self.last_move = pygame.time.get_ticks()
        self.special_fruit = None
        self.special_timer = 0
        self.paused = False
        self.difficulty = 1
        self.particles = []
        self.score_animation = 0
        self.background_offset = 0

    def place_fruit(self):
        max_x = (WIDTH - self.fruit_size) // self.fruit_size
        max_y = (HEIGHT - self.fruit_size) // self.fruit_size
        self.fruit_x = random.randint(0, max_x) * self.fruit_size
        self.fruit_y = random.randint(0, max_y) * self.fruit_size

        for block in self.snake_body:
            if block[0] == self.fruit_x and block[1] == self.fruit_y:
                self.place_fruit()
                return

        if random.random() < 0.1 and self.level > 1:
            self.special_fruit = {
                "x": random.randint(0, max_x) * self.fruit_size,
                "y": random.randint(0, max_y) * self.fruit_size,
                "type": random.choice(["speed", "slow", "bonus"]),
                "color": Colors.YELLOW if random.random() < 0.5 else Colors.PURPLE
            }
            self.special_timer = pygame.time.get_ticks()

    def update(self):
        if self.paused or self.game_over:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_move < (self.speed * 50 - self.level * 10) / self.difficulty:
            return

        self.last_move = current_time

        self.snake_x += self.snake_dx
        self.snake_y += self.snake_dy

        if (self.snake_x < 0 or self.snake_x >= WIDTH or
                self.snake_y < 0 or self.snake_y >= HEIGHT):
            self.game_over = True
            return

        for block in self.snake_body[:-1]:
            if block[0] == self.snake_x and block[1] == self.snake_y:
                self.game_over = True
                return

        self.snake_body.append([self.snake_x, self.snake_y])
        if len(self.snake_body) > self.snake_length:
            del self.snake_body[0]

        if (abs(self.snake_x - self.fruit_x) < self.snake_size and
                abs(self.snake_y - self.fruit_y) < self.snake_size):
            self.snake_length += 1
            points = 10 * self.level * self.difficulty
            self.score += points
            self.score_animation = points
            if self.snake_length % 5 == 0:
                self.level += 1
            for _ in range(8):
                self.particles.append(Particle(self.fruit_x + self.fruit_size // 2,
                                             self.fruit_y + self.fruit_size // 2,
                                             Colors.RED, 'circle'))
            self.place_fruit()

        if self.special_fruit:
            if (abs(self.snake_x - self.special_fruit["x"]) < self.snake_size and
                    abs(self.snake_y - self.special_fruit["y"]) < self.snake_size):
                if self.special_fruit["type"] == "speed":
                    self.speed = max(5, self.speed - 2)
                elif self.special_fruit["type"] == "slow":
                    self.speed = min(20, self.speed + 5)
                elif self.special_fruit["type"] == "bonus":
                    points = 50 * self.level * self.difficulty
                    self.score += points
                    self.score_animation = points
                for _ in range(8):
                    self.particles.append(Particle(self.special_fruit["x"] + self.fruit_size // 2,
                                                 self.special_fruit["y"] + self.fruit_size // 2,
                                                 self.special_fruit["color"], 'square'))
                self.special_fruit = None
            elif current_time - self.special_timer > 5000:
                self.special_fruit = None

        self.particles = [p for p in self.particles if p.lifetime > 0]
        for p in self.particles:
            p.update()
        self.background_offset = (self.background_offset + 0.5) % HEIGHT
        if self.score_animation > 0:
            self.score_animation -= 1

    def draw_background(self, surface):
        grass_surface = create_gradient_surface((WIDTH, HEIGHT), (*Colors.GREEN[:3], 50), Colors.BLACK)
        for y in range(-HEIGHT, HEIGHT, 50):
            pygame.draw.line(surface, Colors.YELLOW, (0, (y + self.background_offset) % HEIGHT),
                            (WIDTH, (y + self.background_offset) % HEIGHT), 1)
        surface.blit(grass_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

    def set_difficulty(self, difficulty: int):
        self.difficulty = max(1, min(3, difficulty))
        self.speed = {1: 10, 2: 8, 3: 6}[self.difficulty]

# Game 4: Memory Game
class MemoryGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.level = 1
        self.cards = []
        self.selected = []
        self.matched = []
        self.moves = 0
        self.score = 0
        self.game_over = False
        self.create_cards()
        self.start_time = time.time()
        self.time_limit = 60
        self.paused = False
        self.difficulty = 1
        self.particles = []
        self.score_animation = 0
        self.background_offset = 0

    def create_cards(self):
        pairs = self.level + 2
        symbols = list(range(1, 13))
        random.shuffle(symbols)
        card_symbols = symbols[:pairs] * 2
        random.shuffle(card_symbols)

        self.cards = []
        card_width = 80
        card_height = 100
        margin = 10
        cols = min(6, pairs + 2)
        rows = (len(card_symbols) + cols - 1) // cols

        start_x = (WIDTH - (cols * (card_width + margin))) // 2
        start_y = (HEIGHT - (rows * (card_height + margin))) // 2

        for i, symbol in enumerate(card_symbols):
            row = i // cols
            col = i % cols
            self.cards.append({
                "x": start_x + col * (card_width + margin),
                "y": start_y + row * (card_height + margin),
                "width": card_width,
                "height": card_height,
                "symbol": symbol,
                "face_up": False,
                "matched": False,
                "flip_progress": 0
            })

    def flip_card(self, index: int):
        if (len(self.selected) < 2 and
                index not in self.selected and
                not self.cards[index]["matched"]):
            self.cards[index]["face_up"] = True
            self.cards[index]["flip_progress"] = 1
            self.selected.append(index)

            if len(self.selected) == 2:
                self.moves += 1
                idx1, idx2 = self.selected
                if self.cards[idx1]["symbol"] == self.cards[idx2]["symbol"]:
                    self.cards[idx1]["matched"] = True
                    self.cards[idx2]["matched"] = True
                    self.matched.extend(self.selected)
                    points = 10 * self.level * self.difficulty
                    self.score += points
                    self.score_animation = points
                    for _ in range(10):
                        self.particles.append(Particle(self.cards[idx1]["x"] + self.cards[idx1]["width"] // 2,
                                                     self.cards[idx1]["y"] + self.cards[idx1]["height"] // 2,
                                                     Colors.GREEN, 'circle'))
                    if len(self.matched) == len(self.cards):
                        self.level += 1
                        if self.level > 5:
                            self.game_over = True
                        else:
                            self.create_cards()
                            self.selected = []
                            self.matched = []

    def hide_selected(self):
        for idx in self.selected:
            self.cards[idx]["face_up"] = False
            self.cards[idx]["flip_progress"] = 0
        self.selected = []

    def time_remaining(self) -> float:
        if not self.paused:
            elapsed = time.time() - self.start_time
            return max(0, self.time_limit / self.difficulty - elapsed)
        return self.time_limit

    def set_difficulty(self, difficulty: int):
        self.difficulty = max(1, min(3, difficulty))
        self.time_limit = {1: 60, 2: 45, 3: 30}[self.difficulty]

    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for p in self.particles:
            p.update()
        self.background_offset = (self.background_offset + 0.5) % WIDTH
        if self.score_animation > 0:
            self.score_animation -= 1
        for card in self.cards:
            if card["flip_progress"] > 0:
                card["flip_progress"] = min(1, card["flip_progress"] + 0.1)

    def draw_background(self, surface):
        wave_surface = create_gradient_surface((WIDTH, HEIGHT), (*Colors.CYAN[:3], 50), Colors.BLACK)
        for x in range(-WIDTH, WIDTH, 50):
            pygame.draw.line(surface, Colors.NEON_PINK, ((x + self.background_offset) % WIDTH, 0),
                            ((x + self.background_offset) % WIDTH, HEIGHT), 1)
        surface.blit(wave_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

# Main game
def main():
    clock = pygame.time.Clock()
    high_score_manager = HighScoreManager()
    
    scrambled_game = ScrambledSaga()
    block_game = BlockBusterBonanza()
    snake_game = SnakeGame()
    memory_game = MemoryGame()
    
    current_state = GameStates.MENU
    difficulty_selection = 1
    running = True
    animation_timer = 0
    transition_alpha = 0
    transition_state = None
    stars = [Star() for _ in range(50)]
    enable_animations = True

    # Menu buttons
    buttons = [
        {"text": "Scrambled Saga", "rect": pygame.Rect(WIDTH // 2 - 150, 200, 300, 50), "state": GameStates.SCRAMBLED_SAGA, "tooltip": "Unscramble words to score points!"},
        {"text": "Block Buster Bonanza", "rect": pygame.Rect(WIDTH // 2 - 150, 270, 300, 50), "state": GameStates.BLOCK_BUSTER, "tooltip": "Break blocks with a bouncing ball!"},
        {"text": "Snake Eating Fruit", "rect": pygame.Rect(WIDTH // 2 - 150, 340, 300, 50), "state": GameStates.SNAKE_GAME, "tooltip": "Grow your snake by eating fruit!"},
        {"text": "Memory Matching", "rect": pygame.Rect(WIDTH // 2 - 150, 410, 300, 50), "state": GameStates.MEMORY_GAME, "tooltip": "Match cards to test your memory!"},
        {"text": "Settings", "rect": pygame.Rect(WIDTH // 2 - 150, 480, 300, 50), "state": GameStates.SETTINGS, "tooltip": "Adjust game settings"}
    ]

    # Settings buttons
    settings_buttons = [
        {"text": "Difficulty: Easy", "rect": pygame.Rect(WIDTH // 2 - 150, 200, 300, 50), "action": "difficulty"},
        {"text": "Animations: On", "rect": pygame.Rect(WIDTH // 2 - 150, 270, 300, 50), "action": "animations"},
        {"text": "Back", "rect": pygame.Rect(WIDTH // 2 - 150, 340, 300, 50), "state": GameStates.MENU}
    ]

    # HUD surfaces
    hud_surface = pygame.Surface((150, 80), pygame.SRCALPHA)
    pygame.draw.rect(hud_surface, (*Colors.DARK_GRAY[:3], 200), (0, 0, 150, 80), border_radius=10)
    pygame.draw.rect(hud_surface, Colors.NEON_BLUE, (0, 0, 150, 80), 2, border_radius=10)

    while running:
        screen.fill(Colors.BLACK)
        mouse_pos = pygame.mouse.get_pos()
        animation_timer += 1
        hover_button = None

        # Update stars
        if enable_animations:
            for star in stars:
                star.update()
                star.draw(screen)

        # Handle transitions
        if transition_state:
            transition_alpha += 20
            if transition_alpha >= 255:
                current_state = transition_state
                transition_state = None
                transition_alpha = 255
        elif transition_alpha > 0:
            transition_alpha -= 20

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_state = GameStates.EXIT_CONFIRM

            if event.type == pygame.KEYDOWN:
                if current_state == GameStates.MENU:
                    if event.key == pygame.K_1:
                        transition_state = GameStates.SCRAMBLED_SAGA
                        scrambled_game = ScrambledSaga()
                        scrambled_game.set_difficulty(difficulty_selection)
                        scrambled_game.new_word()
                    elif event.key == pygame.K_2:
                        transition_state = GameStates.BLOCK_BUSTER
                        block_game = BlockBusterBonanza()
                        block_game.set_difficulty(difficulty_selection)
                    elif event.key == pygame.K_3:
                        transition_state = GameStates.SNAKE_GAME
                        snake_game = SnakeGame()
                        snake_game.set_difficulty(difficulty_selection)
                    elif event.key == pygame.K_4:
                        transition_state = GameStates.MEMORY_GAME
                        memory_game = MemoryGame()
                        memory_game.set_difficulty(difficulty_selection)
                    elif event.key == pygame.K_s:
                        current_state = GameStates.SETTINGS
                    elif event.key == pygame.K_ESCAPE:
                        current_state = GameStates.EXIT_CONFIRM

                elif current_state == GameStates.SCRAMBLED_SAGA:
                    if event.key == pygame.K_ESCAPE:
                        transition_state = GameStates.MENU
                        high_score_manager.update_score('scrambled_saga', scrambled_game.score)
                    elif event.key == pygame.K_p:
                        scrambled_game.paused = not scrambled_game.paused
                    elif not scrambled_game.paused:
                        if event.key == pygame.K_RETURN:
                            if scrambled_game.check_answer():
                                if scrambled_game.lives > 0:
                                    scrambled_game.new_word()
                                else:
                                    transition_state = GameStates.MENU
                                    high_score_manager.update_score('scrambled_saga', scrambled_game.score)
                            else:
                                if scrambled_game.lives <= 0:
                                    transition_state = GameStates.MENU
                                    high_score_manager.update_score('scrambled_saga', scrambled_game.score)
                        elif event.key == pygame.K_BACKSPACE:
                            scrambled_game.user_input = scrambled_game.user_input[:-1]
                        elif event.key == pygame.K_h:
                            hint = scrambled_game.get_hint()
                            scrambled_game.user_input = hint.replace("_", "")
                        elif len(scrambled_game.user_input) < len(scrambled_game.current_word):
                            char = event.unicode
                            if char.isalnum():
                                scrambled_game.user_input += char

                elif current_state == GameStates.BLOCK_BUSTER:
                    if event.key == pygame.K_ESCAPE:
                        transition_state = GameStates.MENU
                        high_score_manager.update_score('block_buster', block_game.score)
                    elif event.key == pygame.K_p:
                        block_game.paused = not block_game.paused
                    elif event.key == pygame.K_SPACE and (block_game.game_over or block_game.level_complete):
                        if block_game.game_over:
                            high_score_manager.update_score('block_buster', block_game.score)
                            block_game.reset()
                        else:
                            block_game.next_level()

                elif current_state == GameStates.SNAKE_GAME:
                    if event.key == pygame.K_ESCAPE:
                        transition_state = GameStates.MENU
                        high_score_manager.update_score('snake_game', snake_game.score)
                    elif event.key == pygame.K_p:
                        snake_game.paused = not snake_game.paused
                    elif not snake_game.paused:
                        if event.key == pygame.K_UP and snake_game.snake_dy == 0:
                            snake_game.snake_dx = 0
                            snake_game.snake_dy = -snake_game.snake_size
                        elif event.key == pygame.K_DOWN and snake_game.snake_dy == 0:
                            snake_game.snake_dx = 0
                            snake_game.snake_dy = snake_game.snake_size
                        elif event.key == pygame.K_LEFT and snake_game.snake_dx == 0:
                            snake_game.snake_dx = -snake_game.snake_size
                            snake_game.snake_dy = 0
                        elif event.key == pygame.K_RIGHT and snake_game.snake_dx == 0:
                            snake_game.snake_dx = snake_game.snake_size
                            snake_game.snake_dy = 0
                        elif event.key == pygame.K_SPACE and snake_game.game_over:
                            high_score_manager.update_score('snake_game', snake_game.score)
                            snake_game.reset()

                elif current_state == GameStates.MEMORY_GAME:
                    if event.key == pygame.K_ESCAPE:
                        transition_state = GameStates.MENU
                        high_score_manager.update_score('memory_game', memory_game.score)
                    elif event.key == pygame.K_p:
                        memory_game.paused = not memory_game.paused
                    elif event.key == pygame.K_SPACE and memory_game.game_over:
                        high_score_manager.update_score('memory_game', memory_game.score)
                        memory_game.reset()

                elif current_state == GameStates.SETTINGS:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                        current_state = GameStates.MENU
                    elif event.key == pygame.K_d:
                        difficulty_selection = (difficulty_selection % 3) + 1
                        settings_buttons[0]["text"] = f"Difficulty: {'Easy' if difficulty_selection == 1 else 'Medium' if difficulty_selection == 2 else 'Hard'}"
                    elif event.key == pygame.K_a:
                        enable_animations = not enable_animations
                        settings_buttons[1]["text"] = f"Animations: {'On' if enable_animations else 'Off'}"

                elif current_state == GameStates.EXIT_CONFIRM:
                    if event.key == pygame.K_y:
                        running = False
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        current_state = GameStates.MENU

            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_state == GameStates.MENU:
                    for button in buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            if button.get("state"):
                                transition_state = button["state"]
                                if button["state"] == GameStates.SCRAMBLED_SAGA:
                                    scrambled_game = ScrambledSaga()
                                    scrambled_game.set_difficulty(difficulty_selection)
                                    scrambled_game.new_word()
                                elif button["state"] == GameStates.BLOCK_BUSTER:
                                    block_game = BlockBusterBonanza()
                                    block_game.set_difficulty(difficulty_selection)
                                elif button["state"] == GameStates.SNAKE_GAME:
                                    snake_game = SnakeGame()
                                    snake_game.set_difficulty(difficulty_selection)
                                elif button["state"] == GameStates.MEMORY_GAME:
                                    memory_game = MemoryGame()
                                    memory_game.set_difficulty(difficulty_selection)
                elif current_state == GameStates.SETTINGS:
                    for button in settings_buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            if button.get("state"):
                                current_state = button["state"]
                            elif button["action"] == "difficulty":
                                difficulty_selection = (difficulty_selection % 3) + 1
                                settings_buttons[0]["text"] = f"Difficulty: {'Easy' if difficulty_selection == 1 else 'Medium' if difficulty_selection == 2 else 'Hard'}"
                            elif button["action"] == "animations":
                                enable_animations = not enable_animations
                                settings_buttons[1]["text"] = f"Animations: {'On' if enable_animations else 'Off'}"
                elif current_state == GameStates.MEMORY_GAME and not memory_game.paused:
                    if len(memory_game.selected) == 2:
                        memory_game.hide_selected()
                    for i, card in enumerate(memory_game.cards):
                        if (not card["matched"] and not card["face_up"] and
                                event.pos[0] >= card["x"] and event.pos[0] <= card["x"] + card["width"] and
                                event.pos[1] >= card["y"] and event.pos[1] <= card["y"] + card["height"]):
                            memory_game.flip_card(i)
                            break

        # Render game states
        if current_state == GameStates.MENU:
            title = render_text_with_gradient("4-in-1 Game Station", Fonts.title, Colors.NEON_BLUE, Colors.NEON_PINK)
            scale = 1.0 + 0.05 * math.sin(animation_timer * 0.05) if enable_animations else 1.0
            scaled_title = pygame.transform.scale(title, (int(title.get_width() * scale), int(title.get_height() * scale)))
            screen.blit(scaled_title, (WIDTH // 2 - scaled_title.get_width() // 2, 50))

            for button in buttons:
                scale = 1.1 if button["rect"].collidepoint(mouse_pos) else 1.0
                color = Colors.NEON_BLUE if button["rect"].collidepoint(mouse_pos) else Colors.LIGHT_GRAY
                button_surface = pygame.Surface((button["rect"].width, button["rect"].height), pygame.SRCALPHA)
                pygame.draw.rect(button_surface, color, (0, 0, button["rect"].width, button["rect"].height), border_radius=10)
                pygame.draw.rect(button_surface, Colors.WHITE, (0, 0, button["rect"].width, button["rect"].height), 2, border_radius=10)
                scaled_button = pygame.transform.scale(button_surface, (int(button["rect"].width * scale), int(button["rect"].height * scale)))
                screen.blit(scaled_button, (button["rect"].x + (button["rect"].width - scaled_button.get_width()) // 2,
                                           button["rect"].y + (button["rect"].height - scaled_button.get_height()) // 2))
                text = render_text_with_shadow(button["text"], Fonts.menu, Colors.BLACK, Colors.WHITE)
                screen.blit(text, (button["rect"].x + button["rect"].width // 2 - text.get_width() // 2,
                                 button["rect"].y + button["rect"].height // 2 - text.get_height() // 2))
                if button["rect"].collidepoint(mouse_pos):
                    hover_button = button

            # High scores
            score_box = pygame.Rect(20, HEIGHT - 150, 220, 130)
            score_surface = pygame.Surface((220, 130), pygame.SRCALPHA)
            pygame.draw.rect(score_surface, (*Colors.DARK_GRAY[:3], 200), (0, 0, 220, 130), border_radius=10)
            pygame.draw.rect(score_surface, Colors.NEON_PINK, (0, 0, 220, 130), 2, border_radius=10)
            screen.blit(score_surface, (20, HEIGHT - 150))
            for i, (game, score) in enumerate(high_score_manager.scores.items()):
                text = render_text_with_shadow(f"{game.replace('_', ' ').title()}: {score}", Fonts.small, Colors.CYAN, Colors.BLACK)
                screen.blit(text, (30, HEIGHT - 140 + i * 25))

            # Tooltip
            if hover_button and enable_animations:
                tooltip = render_text_with_shadow(hover_button["tooltip"], Fonts.small, Colors.WHITE, Colors.BLACK)
                tooltip_rect = pygame.Rect(mouse_pos[0] + 10, mouse_pos[1], tooltip.get_width() + 10, tooltip.get_height() + 10)
                pygame.draw.rect(screen, (*Colors.DARK_GRAY[:3], 200), tooltip_rect, border_radius=5)
                pygame.draw.rect(screen, Colors.NEON_BLUE, tooltip_rect, 1, border_radius=5)
                screen.blit(tooltip, (tooltip_rect.x + 5, tooltip_rect.y + 5))

        elif current_state == GameStates.SCRAMBLED_SAGA:
            if scrambled_game.time_remaining() <= 0 and not scrambled_game.paused:
                scrambled_game.lives -= 1
                if scrambled_game.lives <= 0:
                    transition_state = GameStates.MENU
                    high_score_manager.update_score('scrambled_saga', scrambled_game.score)
                else:
                    scrambled_game.new_word()

            if enable_animations:
                scrambled_game.draw_background(screen)
            scrambled_game.update()
            scrambled_game.draw_particles(screen)

            title = render_text_with_gradient("Scrambled Saga", Fonts.title, Colors.NEON_BLUE, Colors.NEON_PINK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

            screen.blit(hud_surface, (20, 20))
            level_text = render_text_with_shadow(f"Level: {scrambled_game.level}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(level_text, (30, 30))
            score_text = render_text_with_shadow(f"Score: {scrambled_game.score}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(score_text, (30, 60))
            if scrambled_game.score_animation > 0:
                anim_text = render_text_with_shadow(f"+{scrambled_game.score_animation}", Fonts.small, Colors.YELLOW, Colors.BLACK)
                screen.blit(anim_text, (150, 60))

            lives_box = pygame.Rect(WIDTH // 2 - 50, 20, 100, 40)
            pygame.draw.rect(screen, (*Colors.DARK_GRAY[:3], 200), lives_box, border_radius=10)
            pygame.draw.rect(screen, Colors.RED if scrambled_game.lives <= 1 else Colors.NEON_BLUE, lives_box, 2, border_radius=10)
            lives_text = render_text_with_shadow(f"{'❤' * scrambled_game.lives}", Fonts.game, Colors.RED, Colors.BLACK)
            screen.blit(lives_text, (WIDTH // 2 - lives_text.get_width() // 2, 30))

            time_box = pygame.Rect(WIDTH // 2 - 50, 120, 100, 40)
            pygame.draw.rect(screen, (*Colors.DARK_GRAY[:3], 200), time_box, border_radius=10)
            pygame.draw.rect(screen, Colors.YELLOW if scrambled_game.time_remaining() < 10 else Colors.NEON_BLUE, time_box, 2, border_radius=10)
            time_text = render_text_with_shadow(f"{int(scrambled_game.time_remaining())}s", Fonts.game, Colors.YELLOW if scrambled_game.time_remaining() < 10 else Colors.WHITE, Colors.BLACK)
            screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 130))

            scrambled_text = render_text_with_gradient(scrambled_game.scrambled_word, Fonts.title, Colors.CYAN, Colors.NEON_BLUE)
            screen.blit(scrambled_text, (WIDTH // 2 - scrambled_text.get_width() // 2, 200))

            input_text = render_text_with_shadow(f"Your answer: {scrambled_game.user_input}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 300))

            hint_text = render_text_with_shadow("Press 'H' for hint (reduces bonus)", Fonts.small, Colors.YELLOW, Colors.BLACK)
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 350))

            pause_text = render_text_with_shadow("Press 'P' to pause", Fonts.small, Colors.YELLOW, Colors.BLACK)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 380))

            if scrambled_game.paused:
                pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pause_surface.fill((*Colors.BLACK[:3], 150))
                screen.blit(pause_surface, (0, 0))
                paused_text = render_text_with_gradient("PAUSED", Fonts.title, Colors.RED, Colors.NEON_PINK)
                screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2))

            esc_text = render_text_with_shadow("ESC to return to menu", Fonts.small, Colors.RED, Colors.BLACK)
            screen.blit(esc_text, (WIDTH // 2 - esc_text.get_width() // 2, HEIGHT - 50))

        elif current_state == GameStates.BLOCK_BUSTER:
            if not block_game.paused:
                block_game.update()

            if enable_animations:
                block_game.draw_background(screen)
            block_game.draw_particles(screen)

            paddle_offset = math.sin(animation_timer * 0.5) * 5 if block_game.paddle_shake > 0 and enable_animations else 0
            paddle_surface = create_gradient_surface((block_game.paddle_width, block_game.paddle_height), Colors.NEON_BLUE, Colors.CYAN)
            screen.blit(paddle_surface, (block_game.paddle_x, block_game.paddle_y + paddle_offset), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.rect(screen, Colors.WHITE, (block_game.paddle_x, block_game.paddle_y + paddle_offset,
                                                   block_game.paddle_width, block_game.paddle_height), 2, border_radius=5)

            ball_surface = create_gradient_surface((block_game.ball_radius * 2, block_game.ball_radius * 2), Colors.WHITE, Colors.NEON_BLUE)
            screen.blit(ball_surface, (int(block_game.ball_x - block_game.ball_radius), int(block_game.ball_y - block_game.ball_radius)))

            for block in block_game.blocks:
                block_surface = create_gradient_surface((block["width"], block["height"]), block["color"], Colors.BLACK)
                screen.blit(block_surface, (block["x"], block["y"]))
                pygame.draw.rect(screen, Colors.WHITE, (block["x"], block["y"], block["width"], block["height"]), 1, border_radius=3)
                if block["hits"] > 1:
                    hits_text = render_text_with_shadow(str(block["hits"]), Fonts.small, Colors.WHITE, Colors.BLACK)
                    screen.blit(hits_text, (block["x"] + block["width"] // 2 - hits_text.get_width() // 2,
                                          block["y"] + block["height"] // 2 - hits_text.get_height() // 2))

            for power in block_game.power_ups:
                color = Colors.GREEN if power["type"] == "expand" else Colors.BLUE if power["type"] == "slow" else Colors.RED
                pygame.draw.circle(screen, color, (power["x"], power["y"]), 8)
                pygame.draw.circle(screen, Colors.WHITE, (power["x"], power["y"]), 8, 1)

            title = render_text_with_gradient("Block Buster Bonanza", Fonts.title, Colors.NEON_BLUE, Colors.NEON_PINK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

            screen.blit(hud_surface, (20, 20))
            level_text = render_text_with_shadow(f"Level: {block_game.level}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(level_text, (30, 30))
            score_text = render_text_with_shadow(f"Score: {block_game.score}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(score_text, (30, 60))
            if block_game.score_animation > 0:
                anim_text = render_text_with_shadow(f"+{block_game.score_animation}", Fonts.small, Colors.YELLOW, Colors.BLACK)
                screen.blit(anim_text, (150, 60))

            lives_box = pygame.Rect(WIDTH // 2 - 50, 20, 100, 40)
            pygame.draw.rect(screen, (*Colors.DARK_GRAY[:3], 200), lives_box, border_radius=10)
            pygame.draw.rect(screen, Colors.RED if block_game.lives <= 1 else Colors.NEON_BLUE, lives_box, 2, border_radius=10)
            lives_text = render_text_with_shadow(f"{block_game.lives}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(lives_text, (WIDTH // 2 - lives_text.get_width() // 2, 30))

            if block_game.game_over:
                game_over_text = render_text_with_gradient("GAME OVER", Fonts.title, Colors.RED, Colors.NEON_PINK)
                scale = 1.0 + 0.1 * math.sin(animation_timer * 0.05) if enable_animations else 1.0
                scaled_text = pygame.transform.scale(game_over_text, (int(game_over_text.get_width() * scale), int(game_over_text.get_height() * scale)))
                screen.blit(scaled_text, (WIDTH // 2 - scaled_text.get_width() // 2, HEIGHT // 2 - 50))
                restart_text = render_text_with_shadow("Press SPACE to restart", Fonts.game, Colors.WHITE, Colors.BLACK)
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

            elif block_game.level_complete:
                complete_text = render_text_with_gradient(f"LEVEL {block_game.level} COMPLETE!", Fonts.title, Colors.GREEN, Colors.NEON_BLUE)
                scale = 1.0 + 0.1 * math.sin(animation_timer * 0.05) if enable_animations else 1.0
                scaled_text = pygame.transform.scale(complete_text, (int(complete_text.get_width() * scale), int(complete_text.get_height() * scale)))
                screen.blit(scaled_text, (WIDTH // 2 - scaled_text.get_width() // 2, HEIGHT // 2 - 50))
                next_text = render_text_with_shadow("Press SPACE for next level", Fonts.game, Colors.WHITE, Colors.BLACK)
                screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2 + 50))

            pause_text = render_text_with_shadow("Press 'P' to pause | Mouse to move paddle", Fonts.small, Colors.YELLOW, Colors.BLACK)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT - 80))

            if block_game.paused:
                pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pause_surface.fill((*Colors.BLACK[:3], 150))
                screen.blit(pause_surface, (0, 0))
                paused_text = render_text_with_gradient("PAUSED", Fonts.title, Colors.RED, Colors.NEON_PINK)
                screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2))

            esc_text = render_text_with_shadow("ESC to return to menu", Fonts.small, Colors.RED, Colors.BLACK)
            screen.blit(esc_text, (WIDTH // 2 - esc_text.get_width() // 2, HEIGHT - 50))

        elif current_state == GameStates.SNAKE_GAME:
            if not (snake_game.game_over or snake_game.paused):
                snake_game.update()

            if enable_animations:
                snake_game.draw_background(screen)
            snake_game.draw_particles(screen)

            for block in snake_game.snake_body:
                block_surface = create_gradient_surface((snake_game.snake_size, snake_game.snake_size), Colors.GREEN, Colors.NEON_BLUE)
                screen.blit(block_surface, (block[0], block[1]))
                pygame.draw.rect(screen, Colors.WHITE, (block[0], block[1], snake_game.snake_size, snake_game.snake_size), 1, border_radius=5)

            fruit_surface = create_gradient_surface((snake_game.fruit_size, snake_game.fruit_size), Colors.RED, Colors.YELLOW)
            screen.blit(fruit_surface, (snake_game.fruit_x, snake_game.fruit_y))
            pygame.draw.rect(screen, Colors.WHITE, (snake_game.fruit_x, snake_game.fruit_y, snake_game.fruit_size, snake_game.fruit_size), 1, border_radius=5)

            if snake_game.special_fruit:
                special_surface = create_gradient_surface((snake_game.fruit_size, snake_game.fruit_size), snake_game.special_fruit["color"], Colors.BLACK)
                screen.blit(special_surface, (snake_game.special_fruit["x"], snake_game.special_fruit["y"]))
                pygame.draw.rect(screen, Colors.WHITE, (snake_game.special_fruit["x"], snake_game.special_fruit["y"], snake_game.fruit_size, snake_game.fruit_size), 1, border_radius=5)

            title = render_text_with_gradient("Snake Eating Fruit", Fonts.title, Colors.NEON_BLUE, Colors.NEON_PINK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

            screen.blit(hud_surface, (20, 20))
            score_text = render_text_with_shadow(f"Score: {snake_game.score}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(score_text, (30, 30))
            level_text = render_text_with_shadow(f"Level: {snake_game.level}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(level_text, (30, 60))
            if snake_game.score_animation > 0:
                anim_text = render_text_with_shadow(f"+{snake_game.score_animation}", Fonts.small, Colors.YELLOW, Colors.BLACK)
                screen.blit(anim_text, (150, 60))

            length_box = pygame.Rect(WIDTH // 2 - 50, 20, 100, 40)
            pygame.draw.rect(screen, (*Colors.DARK_GRAY[:3], 200), length_box, border_radius=10)
            pygame.draw.rect(screen, Colors.NEON_BLUE, length_box, 2, border_radius=10)
            length_text = render_text_with_shadow(f"{snake_game.snake_length}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(length_text, (WIDTH // 2 - length_text.get_width() // 2, 30))

            if snake_game.game_over:
                game_over_text = render_text_with_gradient("GAME OVER", Fonts.title, Colors.RED, Colors.NEON_PINK)
                scale = 1.0 + 0.1 * math.sin(animation_timer * 0.05) if enable_animations else 1.0
                scaled_text = pygame.transform.scale(game_over_text, (int(game_over_text.get_width() * scale), int(game_over_text.get_height() * scale)))
                screen.blit(scaled_text, (WIDTH // 2 - scaled_text.get_width() // 2, HEIGHT // 2 - 50))
                restart_text = render_text_with_shadow("Press SPACE to restart", Fonts.game, Colors.WHITE, Colors.BLACK)
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

            pause_text = render_text_with_shadow("Press 'P' to pause", Fonts.small, Colors.YELLOW, Colors.BLACK)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT - 80))

            if snake_game.paused:
                pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pause_surface.fill((*Colors.BLACK[:3], 150))
                screen.blit(pause_surface, (0, 0))
                paused_text = render_text_with_gradient("PAUSED", Fonts.title, Colors.RED, Colors.NEON_PINK)
                screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2))

            esc_text = render_text_with_shadow("ESC to return to menu", Fonts.small, Colors.RED, Colors.BLACK)
            screen.blit(esc_text, (WIDTH // 2 - esc_text.get_width() // 2, HEIGHT - 50))

        elif current_state == GameStates.MEMORY_GAME:
            if memory_game.time_remaining() <= 0 and not memory_game.paused:
                memory_game.game_over = True

            if enable_animations:
                memory_game.draw_background(screen)
            memory_game.update()
            memory_game.draw_particles(screen)

            title = render_text_with_gradient("Memory Matching", Fonts.title, Colors.NEON_BLUE, Colors.NEON_PINK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

            screen.blit(hud_surface, (20, 20))
            level_text = render_text_with_shadow(f"Level: {memory_game.level}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(level_text, (30, 30))
            score_text = render_text_with_shadow(f"Score: {memory_game.score}", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(score_text, (30, 60))
            if memory_game.score_animation > 0:
                anim_text = render_text_with_shadow(f"+{memory_game.score_animation}", Fonts.small, Colors.YELLOW, Colors.BLACK)
                screen.blit(anim_text, (150, 60))

            time_box = pygame.Rect(WIDTH // 2 - 50, 20, 100, 40)
            pygame.draw.rect(screen, (*Colors.DARK_GRAY[:3], 200), time_box, border_radius=10)
            pygame.draw.rect(screen, Colors.YELLOW if memory_game.time_remaining() < 10 else Colors.NEON_BLUE, time_box, 2, border_radius=10)
            time_text = render_text_with_shadow(f"{int(memory_game.time_remaining())}s", Fonts.game, Colors.YELLOW if memory_game.time_remaining() < 10 else Colors.WHITE, Colors.BLACK)
            screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 30))

            for card in memory_game.cards:
                scale = 1 - (1 - card["flip_progress"]) * 0.5 if enable_animations else 1
                card_surface = pygame.Surface((card["width"], card["height"]), pygame.SRCALPHA)
                color = Colors.GREEN if card["matched"] else Colors.BLUE if card["face_up"] else Colors.WHITE
                pygame.draw.rect(card_surface, color, (0, 0, card["width"], card["height"]), border_radius=5)
                if card["face_up"] or card["matched"]:
                    symbol_text = render_text_with_shadow(str(card["symbol"]), Fonts.game, Colors.BLACK, Colors.WHITE)
                    card_surface.blit(symbol_text, (card["width"] // 2 - symbol_text.get_width() // 2,
                                                  card["height"] // 2 - symbol_text.get_height() // 2))
                scaled_card = pygame.transform.scale(card_surface, (int(card["width"] * scale), int(card["height"] * scale)))
                screen.blit(scaled_card, (card["x"] + (card["width"] - scaled_card.get_width()) // 2,
                                         card["y"] + (card["height"] - scaled_card.get_height()) // 2))

            if memory_game.game_over:
                game_over_text = render_text_with_gradient("GAME OVER", Fonts.title, Colors.RED, Colors.NEON_PINK)
                scale = 1.0 + 0.1 * math.sin(animation_timer * 0.05) if enable_animations else 1.0
                scaled_text = pygame.transform.scale(game_over_text, (int(game_over_text.get_width() * scale), int(game_over_text.get_height() * scale)))
                screen.blit(scaled_text, (WIDTH // 2 - scaled_text.get_width() // 2, HEIGHT // 2 - 50))
                if memory_game.level > 5:
                    congrats_text = render_text_with_shadow("You completed all levels!", Fonts.game, Colors.GREEN, Colors.BLACK)
                    screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 2 + 20))
                restart_text = render_text_with_shadow("Press SPACE to restart", Fonts.game, Colors.WHITE, Colors.BLACK)
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))

            pause_text = render_text_with_shadow("Press 'P' to pause", Fonts.small, Colors.YELLOW, Colors.BLACK)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT - 80))

            if memory_game.paused:
                pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pause_surface.fill((*Colors.BLACK[:3], 150))
                screen.blit(pause_surface, (0, 0))
                paused_text = render_text_with_gradient("PAUSED", Fonts.title, Colors.RED, Colors.NEON_PINK)
                screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2))

            esc_text = render_text_with_shadow("ESC to return to menu", Fonts.small, Colors.RED, Colors.BLACK)
            screen.blit(esc_text, (WIDTH // 2 - esc_text.get_width() // 2, HEIGHT - 50))

        elif current_state == GameStates.SETTINGS:
            title = render_text_with_gradient("Settings", Fonts.title, Colors.NEON_BLUE, Colors.NEON_PINK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

            for button in settings_buttons:
                scale = 1.1 if button["rect"].collidepoint(mouse_pos) else 1.0
                color = Colors.NEON_BLUE if button["rect"].collidepoint(mouse_pos) else Colors.LIGHT_GRAY
                button_surface = pygame.Surface((button["rect"].width, button["rect"].height), pygame.SRCALPHA)
                pygame.draw.rect(button_surface, color, (0, 0, button["rect"].width, button["rect"].height), border_radius=10)
                pygame.draw.rect(button_surface, Colors.WHITE, (0, 0, button["rect"].width, button["rect"].height), 2, border_radius=10)
                scaled_button = pygame.transform.scale(button_surface, (int(button["rect"].width * scale), int(button["rect"].height * scale)))
                screen.blit(scaled_button, (button["rect"].x + (button["rect"].width - scaled_button.get_width()) // 2,
                                           button["rect"].y + (button["rect"].height - scaled_button.get_height()) // 2))
                text = render_text_with_shadow(button["text"], Fonts.menu, Colors.BLACK, Colors.WHITE)
                screen.blit(text, (button["rect"].x + button["rect"].width // 2 - text.get_width() // 2,
                                 button["rect"].y + button["rect"].height // 2 - text.get_height() // 2))
                if button["rect"].collidepoint(mouse_pos):
                    hover_button = button

        elif current_state == GameStates.EXIT_CONFIRM:
            confirm_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            confirm_surface.fill((*Colors.BLACK[:3], 150))
            screen.blit(confirm_surface, (0, 0))
            confirm_text = render_text_with_gradient("Exit Game? (Y/N)", Fonts.title, Colors.RED, Colors.NEON_PINK)
            screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2))

        # Draw transition overlay
        if transition_alpha > 0:
            transition_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            transition_surface.fill((*Colors.BLACK[:3], transition_alpha))
            screen.blit(transition_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
