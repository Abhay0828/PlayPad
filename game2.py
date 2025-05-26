import pygame
import random
import sys
import time
from pygame import mixer
import math

# Initialize pygame
pygame.init()
mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4-in-1 Game Station")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
LIGHT_BLUE = (173, 216, 230)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# Fonts
title_font = pygame.font.Font(None, 72)
menu_font = pygame.font.Font(None, 48)
game_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
button_font = pygame.font.Font(None, 32)

# Game states
MENU = 0
SCRAMBLED_SAGA = 1
BLOCK_BUSTER = 2
SNAKE_GAME = 3
MEMORY_GAME = 4
current_state = MENU

# Load sounds
try:
    click_sound = mixer.Sound('click.wav')
    correct_sound = mixer.Sound('correct.wav')
    wrong_sound = mixer.Sound('wrong.wav')
    bounce_sound = mixer.Sound('bounce.wav')
    game_over_sound = mixer.Sound('game_over.wav')
    background_music = mixer.Sound('background.wav')
    background_music.set_volume(0.5)
    background_music.play(-1)  # Loop background music
except:
    print("Sound files not found. Continuing without sound.")

# Button class for better UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)  # Border
        
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Particle effect for visual feedback
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 6.28)
        self.life = random.randint(20, 40)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Game 1: Scrambled Saga (Word Scramble)
class ScrambledSaga:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.current_word = ""
        self.scrambled_word = ""
        self.user_input = ""
        self.words_by_level = {
            1: ["apple", "dog", "cat", "tree", "book", "water", "pencil", "happy", "music", "light"],
            2: ["elephant", "giraffe", "kangaroo", "computer", "keyboard", "monitor", "python", "program", "developer", "algorithm"],
            3: ["extravaganza", "magnificent", "quadrilateral", "xylophone", "quintessential", "jazz", "puzzle", "rhythm", "sphinx", "zombie"]
        }
        self.time_limit = 30  # seconds
        self.start_time = 0
        self.hint_used = False
        self.particles = []
        
    def new_word(self):
        word_list = self.words_by_level.get(self.level, self.words_by_level[3])
        self.current_word = random.choice(word_list)
        self.scrambled_word = self.scramble_word(self.current_word)
        self.user_input = ""
        self.hint_used = False
        self.start_time = time.time()
        
    def scramble_word(self, word):
        letters = list(word)
        while True:
            random.shuffle(letters)
            scrambled = ''.join(letters)
            if scrambled != word:
                return scrambled.upper()
                
    def check_answer(self):
        if self.user_input.lower() == self.current_word.lower():
            # Create particles for correct answer
            for _ in range(20):
                self.particles.append(Particle(WIDTH//2, 300, GREEN))
            self.score += len(self.current_word) * self.level
            if not self.hint_used:
                self.score += 5  # bonus for no hint
            return True
        else:
            self.lives -= 1
            # Create particles for wrong answer
            for _ in range(20):
                self.particles.append(Particle(WIDTH//2, 300, RED))
            return False
            
    def get_hint(self):
        self.hint_used = True
        hint = ""
        for i, letter in enumerate(self.current_word):
            if i < len(self.current_word) // 2:
                hint += letter.upper()
            else:
                hint += "_"
        return hint
        
    def time_remaining(self):
        elapsed = time.time() - self.start_time
        return max(0, self.time_limit - elapsed)
        
    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
                
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Game 2: Block Buster Bonanza
class BlockBusterBonanza:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.paddle_width = 120
        self.paddle_height = 20
        self.paddle_x = WIDTH // 2 - self.paddle_width // 2
        self.paddle_y = HEIGHT - 50
        self.paddle_speed = 10
        
        self.ball_radius = 12
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_dx = 5 * random.choice([-1, 1])
        self.ball_dy = -5
        self.ball_speed = 5
        
        self.level = 1
        self.score = 0
        self.lives = 3
        self.blocks = []
        self.create_blocks()
        self.game_over = False
        self.level_complete = False
        self.power_ups = []
        self.paddle_powered = False
        self.power_timer = 0
        self.particles = []
        
    def create_blocks(self):
        self.blocks = []
        rows = self.level + 2
        cols = 10
        block_width = WIDTH // cols - 6
        block_height = 25
        
        colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, PINK, LIGHT_BLUE]
        
        for row in range(rows):
            for col in range(cols):
                if row < len(colors):
                    color = colors[row]
                else:
                    color = random.choice(colors)
                    
                block = {
                    "x": 3 + col * (block_width + 6),
                    "y": 80 + row * (block_height + 6),
                    "width": block_width,
                    "height": block_height,
                    "color": color,
                    "hits": 1 if self.level < 3 else (2 if self.level < 5 else 3),
                    "points": (row + 1) * 5
                }
                self.blocks.append(block)
                
    def update(self):
        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball collision with walls
        if self.ball_x <= self.ball_radius or self.ball_x >= WIDTH - self.ball_radius:
            self.ball_dx *= -1
            try:
                bounce_sound.play()
            except:
                pass
            
        if self.ball_y <= self.ball_radius:
            self.ball_dy *= -1
            try:
                bounce_sound.play()
            except:
                pass
            
        # Ball collision with paddle
        if (self.ball_y + self.ball_radius >= self.paddle_y and 
            self.ball_y - self.ball_radius <= self.paddle_y + self.paddle_height and
            self.ball_x >= self.paddle_x and self.ball_x <= self.paddle_x + self.paddle_width):
            
            # Calculate bounce angle based on where ball hits paddle
            relative_x = (self.ball_x - self.paddle_x) / self.paddle_width
            angle = relative_x * 2 - 1  # -1 to 1
            
            self.ball_dx = angle * 7
            self.ball_dy *= -1
            try:
                bounce_sound.play()
            except:
                pass
            
        # Ball out of bounds
        if self.ball_y > HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                try:
                    game_over_sound.play()
                except:
                    pass
            else:
                self.ball_x = WIDTH // 2
                self.ball_y = HEIGHT // 2
                self.ball_dx = 5 * random.choice([-1, 1])
                self.ball_dy = -5
                
        # Block collisions
        for block in self.blocks[:]:
            if (self.ball_x + self.ball_radius > block["x"] and 
                self.ball_x - self.ball_radius < block["x"] + block["width"] and
                self.ball_y + self.ball_radius > block["y"] and 
                self.ball_y - self.ball_radius < block["y"] + block["height"]):
                
                block["hits"] -= 1
                if block["hits"] <= 0:
                    self.blocks.remove(block)
                    self.score += block["points"]
                    
                    # Create particles when block is destroyed
                    for _ in range(15):
                        self.particles.append(Particle(
                            block["x"] + block["width"]//2,
                            block["y"] + block["height"]//2,
                            block["color"]
                        ))
                    
                    # Chance to spawn power-up
                    if random.random() < 0.2:
                        self.power_ups.append({
                            "x": block["x"] + block["width"] // 2,
                            "y": block["y"],
                            "type": random.choice(["expand", "slow", "extra_life", "laser"]),
                            "color": GREEN if random.random() < 0.5 else YELLOW
                        })
                
                # Determine bounce direction
                if (self.ball_x < block["x"] or self.ball_x > block["x"] + block["width"]):
                    self.ball_dx *= -1
                else:
                    self.ball_dy *= -1
                
                try:
                    bounce_sound.play()
                except:
                    pass
                
                break
                
        # Check level complete
        if len(self.blocks) == 0:
            self.level_complete = True
            # Celebration particles
            for _ in range(100):
                self.particles.append(Particle(
                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT//2),
                    random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE])
                ))
            
        # Update power-ups
        for power in self.power_ups[:]:
            power["y"] += 3
            
            # Power-up caught by paddle
            if (power["y"] >= self.paddle_y and 
                power["x"] >= self.paddle_x and 
                power["x"] <= self.paddle_x + self.paddle_width):
                
                if power["type"] == "expand":
                    self.paddle_width = 180
                    self.paddle_powered = True
                    self.power_timer = pygame.time.get_ticks()
                elif power["type"] == "slow":
                    self.ball_speed = max(3, self.ball_speed - 2)
                    self.paddle_powered = True
                    self.power_timer = pygame.time.get_ticks()
                elif power["type"] == "extra_life":
                    self.lives = min(5, self.lives + 1)
                elif power["type"] == "laser":
                    # Temporary laser power (not implemented fully)
                    pass
                    
                self.power_ups.remove(power)
                try:
                    correct_sound.play()
                except:
                    pass
                
            # Power-up missed
            elif power["y"] > HEIGHT:
                self.power_ups.remove(power)
                
        # Check power-up timeout (8 seconds)
        if self.paddle_powered and pygame.time.get_ticks() - self.power_timer > 8000:
            self.paddle_width = 120
            self.ball_speed = 5
            self.paddle_powered = False
            
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
                
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)
            
    def next_level(self):
        self.level += 1
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_dx = 5 * random.choice([-1, 1])
        self.ball_dy = -5
        self.create_blocks()
        self.level_complete = False
        self.power_ups = []
        self.paddle_powered = False

# Game 3: Snake Eating Fruit
class SnakeGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.snake_size = 25
        self.grid_size = 25  # Add this line before place_fruit() is called
        self.snake_x = WIDTH // 2
        self.snake_y = HEIGHT // 2
        self.snake_dx = self.snake_size
        self.snake_dy = 0
        self.snake_body = []
        self.snake_length = 3
        self.fruit_x = 0
        self.fruit_y = 0
        self.fruit_size = 25
        self.score = 0
        self.level = 1
        self.game_over = False
        self.place_fruit()  # Now grid_size is defined before this is called
        self.speed = 8
        self.last_move = pygame.time.get_ticks()
        self.special_fruit = None
        self.special_timer = 0
        self.snake_color = GREEN
        self.fruit_color = RED
        self.growth_particles = []
        
    def place_fruit(self):
        max_x = (WIDTH - self.fruit_size) // self.grid_size
        max_y = (HEIGHT - self.fruit_size) // self.grid_size
        self.fruit_x = random.randint(0, max_x) * self.grid_size
        self.fruit_y = random.randint(0, max_y) * self.grid_size
        
        # Check if fruit is placed on snake
        for block in self.snake_body:
            if block[0] == self.fruit_x and block[1] == self.fruit_y:
                self.place_fruit()
                return
                
        # Chance for special fruit (20% chance)
        if random.random() < 0.2 and self.level > 1:
            self.special_fruit = {
                "x": random.randint(0, max_x) * self.grid_size,
                "y": random.randint(0, max_y) * self.grid_size,
                "type": random.choice(["speed", "slow", "bonus", "invincible"]),
                "color": YELLOW if random.random() < 0.5 else PURPLE,
                "timer": 0,
                "blink": False
            }
            self.special_timer = pygame.time.get_ticks()
            
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move < self.speed * 50 - self.level * 10:
            return
            
        self.last_move = current_time
        
        # Move snake
        self.snake_x += self.snake_dx
        self.snake_y += self.snake_dy
        
        # Check wall collision (wrap around for modern snake feel)
        if self.snake_x < 0:
            self.snake_x = WIDTH - self.grid_size
        elif self.snake_x >= WIDTH:
            self.snake_x = 0
        if self.snake_y < 0:
            self.snake_y = HEIGHT - self.grid_size
        elif self.snake_y >= HEIGHT:
            self.snake_y = 0
                
        # Check self collision
        for block in self.snake_body[:-1]:
            if block[0] == self.snake_x and block[1] == self.snake_y:
                self.game_over = True
                try:
                    game_over_sound.play()
                except:
                    pass
                return
                
        # Update snake body
        self.snake_body.append([self.snake_x, self.snake_y])
        if len(self.snake_body) > self.snake_length:
            del self.snake_body[0]
            
        # Check fruit collision
        if (abs(self.snake_x - self.fruit_x) < self.grid_size and 
            abs(self.snake_y - self.fruit_y) < self.grid_size):
            
            self.snake_length += 1
            self.score += 10 * self.level
            
            # Add growth particles
            for _ in range(15):
                self.growth_particles.append(Particle(
                    self.snake_x + self.grid_size//2,
                    self.snake_y + self.grid_size//2,
                    GREEN
                ))
            
            try:
                correct_sound.play()
            except:
                pass
            
            # Level up every 3 fruits
            if self.snake_length % 3 == 0:
                self.level += 1
                # Change snake color based on level
                colors = [GREEN, BLUE, PURPLE, CYAN, ORANGE, PINK]
                self.snake_color = colors[(self.level-1) % len(colors)]
                
            self.place_fruit()
            
        # Check special fruit collision
        if self.special_fruit:
            # Blink effect when about to disappear
            if current_time - self.special_timer > 4000:
                self.special_fruit["blink"] = (current_time % 200) < 100
                
            if (abs(self.snake_x - self.special_fruit["x"]) < self.grid_size and 
                abs(self.snake_y - self.special_fruit["y"]) < self.grid_size):
                
                if self.special_fruit["type"] == "speed":
                    self.speed = max(3, self.speed - 2)
                elif self.special_fruit["type"] == "slow":
                    self.speed = min(15, self.speed + 3)
                elif self.special_fruit["type"] == "bonus":
                    self.score += 50 * self.level
                elif self.special_fruit["type"] == "invincible":
                    # Temporary invincibility (not implemented fully)
                    pass
                    
                # Create special effect particles
                for _ in range(30):
                    self.growth_particles.append(Particle(
                        self.special_fruit["x"] + self.grid_size//2,
                        self.special_fruit["y"] + self.grid_size//2,
                        self.special_fruit["color"]
                    ))
                    
                self.special_fruit = None
                try:
                    correct_sound.play()
                except:
                    pass
                
            # Special fruit timeout (5 seconds)
            elif current_time - self.special_timer > 5000:
                self.special_fruit = None
                
        # Update particles
        for particle in self.growth_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.growth_particles.remove(particle)

# Game 4: Memory Matching
class MemoryGame:
    def __init__(self):
        # Define card colors first
        self.card_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, PINK, LIGHT_BLUE]
        self.reset()
        
    def reset(self):
        self.level = 1
        self.cards = []
        self.selected = []
        self.matched = []
        self.moves = 0
        self.score = 0
        self.game_over = False
        self.card_back = BLUE
        self.card_front = WHITE
        self.particles = []
        self.create_cards()
        self.start_time = time.time()
        self.time_limit = 90  # seconds
        
    def create_cards(self):
        pairs = self.level + 2  # More pairs for higher levels
        symbols = list(range(1, 65))  # 64 different symbols
        random.shuffle(symbols)
        card_symbols = symbols[:pairs] * 2
        random.shuffle(card_symbols)
        
        self.cards = []
        card_width = 100
        card_height = 130
        margin = 15
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
                "color": random.choice(self.card_colors)
            })
    def flip_card(self, index):
        if (len(self.selected) < 2 and 
            index not in self.selected and 
            not self.cards[index]["matched"]):
            
            self.cards[index]["face_up"] = True
            self.selected.append(index)
            
            if len(self.selected) == 2:
                self.moves += 1
                idx1, idx2 = self.selected
                
                if self.cards[idx1]["symbol"] == self.cards[idx2]["symbol"]:
                    self.cards[idx1]["matched"] = True
                    self.cards[idx2]["matched"] = True
                    self.matched.extend(self.selected)
                    self.score += 10 * self.level
                    
                    # Create particles for match
                    for i in [idx1, idx2]:
                        for _ in range(15):
                            self.particles.append(Particle(
                                self.cards[i]["x"] + self.cards[i]["width"]//2,
                                self.cards[i]["y"] + self.cards[i]["height"]//2,
                                self.cards[i]["color"]
                            ))
                    
                    try:
                        correct_sound.play()
                    except:
                        pass
                    
                    # Check if all cards matched
                    if len(self.matched) == len(self.cards):
                        self.level += 1
                        if self.level > 8:  # Max level
                            self.game_over = True
                        else:
                            self.create_cards()
                            self.selected = []
                            self.matched = []
                else:
                    try:
                        wrong_sound.play()
                    except:
                        pass
                    
    def hide_selected(self):
        for idx in self.selected:
            self.cards[idx]["face_up"] = False
        self.selected = []
        
    def time_remaining(self):
        elapsed = time.time() - self.start_time
        return max(0, self.time_limit - elapsed)
        
    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
                
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Create game instances
scrambled_game = ScrambledSaga()
block_game = BlockBusterBonanza()
snake_game = SnakeGame()
memory_game = MemoryGame()

# Create menu buttons
game_buttons = [
    Button(WIDTH//2 - 200, 200, 400, 60, "1. Scrambled Saga", BLUE, LIGHT_BLUE),
    Button(WIDTH//2 - 200, 280, 400, 60, "2. Block Buster", RED, PINK),
    Button(WIDTH//2 - 200, 360, 400, 60, "3. Snake Game", GREEN, LIGHT_BLUE),
    Button(WIDTH//2 - 200, 440, 400, 60, "4. Memory Game", PURPLE, PINK),
    Button(WIDTH//2 - 200, 520, 400, 60, "Exit", DARK_GRAY, RED)
]

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill(BLACK)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEMOTION:
            for button in game_buttons:
                button.check_hover(mouse_pos)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == MENU:
                for i, button in enumerate(game_buttons):
                    if button.is_clicked(mouse_pos, event):
                        try:
                            click_sound.play()
                        except:
                            pass
                        if i == 0:
                            current_state = SCRAMBLED_SAGA
                            scrambled_game.new_word()
                        elif i == 1:
                            current_state = BLOCK_BUSTER
                        elif i == 2:
                            current_state = SNAKE_GAME
                            snake_game.reset()
                        elif i == 3:
                            current_state = MEMORY_GAME
                            memory_game.reset()
                        elif i == 4:
                            running = False
                            
            elif current_state == MEMORY_GAME:
                if len(memory_game.selected) == 2:
                    memory_game.hide_selected()
                    
                for i, card in enumerate(memory_game.cards):
                    if (not card["matched"] and not card["face_up"] and 
                        event.pos[0] >= card["x"] and event.pos[0] <= card["x"] + card["width"] and
                        event.pos[1] >= card["y"] and event.pos[1] <= card["y"] + card["height"]):
                        
                        memory_game.flip_card(i)
                        try:
                            click_sound.play()
                        except:
                            pass
                        break
                        
        if event.type == pygame.KEYDOWN:
            if current_state == SCRAMBLED_SAGA:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    try:
                        click_sound.play()
                    except:
                        pass
                elif event.key == pygame.K_RETURN:
                    if scrambled_game.check_answer():
                        try:
                            correct_sound.play()
                        except:
                            pass
                        if scrambled_game.lives > 0:
                            scrambled_game.new_word()
                        else:
                            current_state = MENU
                    else:
                        try:
                            wrong_sound.play()
                        except:
                            pass
                        if scrambled_game.lives <= 0:
                            current_state = MENU
                elif event.key == pygame.K_BACKSPACE:
                    scrambled_game.user_input = scrambled_game.user_input[:-1]
                elif event.key == pygame.K_h:
                    hint = scrambled_game.get_hint()
                    scrambled_game.user_input = hint.replace("_", "")
                else:
                    if len(scrambled_game.user_input) < len(scrambled_game.current_word):
                        scrambled_game.user_input += event.unicode
                        
            elif current_state == BLOCK_BUSTER:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    try:
                        click_sound.play()
                    except:
                        pass
                elif event.key == pygame.K_SPACE and (block_game.game_over or block_game.level_complete):
                    if block_game.game_over:
                        block_game.reset()
                    else:
                        block_game.next_level()
                        
            elif current_state == SNAKE_GAME:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    try:
                        click_sound.play()
                    except:
                        pass
                elif event.key == pygame.K_UP and snake_game.snake_dy == 0:
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
                    snake_game.reset()
                    
            elif current_state == MEMORY_GAME:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    try:
                        click_sound.play()
                    except:
                        pass
                elif event.key == pygame.K_SPACE and memory_game.game_over:
                    memory_game.reset()
                    
    # Game state handling
    if current_state == MENU:
        # Draw menu background
        pygame.draw.rect(screen, DARK_GRAY, (WIDTH//2 - 250, 50, 500, 600), border_radius=20)
        
        # Draw title
        title = title_font.render("Game Station", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = small_font.render("4-in-1 Gaming Experience", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 160))
        
        # Draw buttons
        for button in game_buttons:
            button.draw(screen)
            
    elif current_state == SCRAMBLED_SAGA:
        # Update game
        scrambled_game.update_particles()
        if scrambled_game.time_remaining() <= 0:
            scrambled_game.lives -= 1
            if scrambled_game.lives <= 0:
                current_state = MENU
            else:
                scrambled_game.new_word()
                
        # Draw game background
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, HEIGHT))
        
        # Draw particles
        scrambled_game.draw_particles(screen)
        
        # Draw title
        title = title_font.render("Scrambled Saga", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Draw info panel
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 80))
        pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, 80), 2)
        
        level_text = game_font.render(f"Level: {scrambled_game.level}", True, WHITE)
        screen.blit(level_text, (20, 20))
        
        score_text = game_font.render(f"Score: {scrambled_game.score}", True, WHITE)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))
        
        lives_text = game_font.render(f"Lives: {'❤' * scrambled_game.lives}", True, RED)
        screen.blit(lives_text, (WIDTH//2 - lives_text.get_width()//2, 20))
        
        # Draw game area
        pygame.draw.rect(screen, BLACK, (50, 100, WIDTH-100, HEIGHT-200), border_radius=10)
        pygame.draw.rect(screen, BLUE, (50, 100, WIDTH-100, HEIGHT-200), 3, border_radius=10)
        
        time_text = game_font.render(f"Time: {int(scrambled_game.time_remaining())}s", True, 
                                   YELLOW if scrambled_game.time_remaining() < 10 else WHITE)
        screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 120))
        
        scrambled_text = title_font.render(scrambled_game.scrambled_word, True, CYAN)
        screen.blit(scrambled_text, (WIDTH//2 - scrambled_text.get_width()//2, 200))
        
        input_text = game_font.render(f"Your answer: {scrambled_game.user_input}", True, WHITE)
        screen.blit(input_text, (WIDTH//2 - input_text.get_width()//2, 300))
        
        hint_text = small_font.render("Press 'h' for hint (reduces bonus)", True, YELLOW)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 350))
        
        # Draw back button
        back_button = Button(20, HEIGHT-70, 150, 50, "Back", RED, PINK)
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})):
            current_state = MENU
            try:
                click_sound.play()
            except:
                pass
                
    elif current_state == BLOCK_BUSTER:
        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and block_game.paddle_x > 0:
            block_game.paddle_x -= block_game.paddle_speed
        if keys[pygame.K_RIGHT] and block_game.paddle_x < WIDTH - block_game.paddle_width:
            block_game.paddle_x += block_game.paddle_speed
            
        if not (block_game.game_over or block_game.level_complete):
            block_game.update()
            
        # Draw game background
        screen.fill(BLACK)
        
        # Draw particles
        block_game.draw_particles(screen)
        
        # Draw title
        title = title_font.render("Block Buster", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))
        
        # Draw info panel
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
        pygame.draw.rect(screen, RED, (0, 0, WIDTH, 50), 2)
        
        level_text = game_font.render(f"Level: {block_game.level}", True, WHITE)
        screen.blit(level_text, (20, 10))
        
        score_text = game_font.render(f"Score: {block_game.score}", True, WHITE)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 10))
        
        lives_text = game_font.render(f"Lives: {block_game.lives}", True, WHITE)
        screen.blit(lives_text, (WIDTH//2 - lives_text.get_width()//2, 10))
        
        # Draw game elements
        pygame.draw.rect(screen, WHITE, 
                        (block_game.paddle_x, block_game.paddle_y, 
                         block_game.paddle_width, block_game.paddle_height), border_radius=5)
                         
        pygame.draw.circle(screen, WHITE, (int(block_game.ball_x), int(block_game.ball_y)), block_game.ball_radius)
        
        for block in block_game.blocks:
            pygame.draw.rect(screen, block["color"], 
                           (block["x"], block["y"], block["width"], block["height"]), border_radius=3)
                           
        for power in block_game.power_ups:
            color = GREEN if power["type"] == "expand" else BLUE if power["type"] == "slow" else RED
            pygame.draw.circle(screen, power["color"], (power["x"], power["y"]), 10)
            
        # Draw game over/level complete screens
        if block_game.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
            
            score_text = title_font.render(f"Score: {block_game.score}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            
            restart_text = game_font.render("Press SPACE to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
            
        elif block_game.level_complete:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            complete_text = title_font.render(f"LEVEL {block_game.level} COMPLETE!", True, GREEN)
            screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 100))
            
            score_text = title_font.render(f"Score: {block_game.score}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            
            next_text = game_font.render("Press SPACE for next level", True, WHITE)
            screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 100))
            
        # Draw back button
        back_button = Button(20, HEIGHT-70, 150, 50, "Back", RED, PINK)
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})):
            current_state = MENU
            try:
                click_sound.play()
            except:
                pass
                
    elif current_state == SNAKE_GAME:
        # Update game
        if not snake_game.game_over:
            snake_game.update()
            
        # Draw game background with grid
        screen.fill(BLACK)
        for x in range(0, WIDTH, snake_game.grid_size):
            pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, snake_game.grid_size):
            pygame.draw.line(screen, DARK_GRAY, (0, y), (WIDTH, y), 1)
        
        # Draw snake
        for i, block in enumerate(snake_game.snake_body):
            # Gradient color from head to tail
            if i == len(snake_game.snake_body) - 1:  # Head
                color = snake_game.snake_color
            else:
                # Calculate color intensity based on position
                intensity = 0.5 + 0.5 * (i / len(snake_game.snake_body))
                r = min(255, snake_game.snake_color[0] * intensity)
                g = min(255, snake_game.snake_color[1] * intensity)
                b = min(255, snake_game.snake_color[2] * intensity)
                color = (int(r), int(g), int(b))
                
            pygame.draw.rect(screen, color, 
                           (block[0], block[1], snake_game.snake_size, snake_game.snake_size), border_radius=5)
                           
        # Draw fruit
        pygame.draw.rect(screen, snake_game.fruit_color, 
                       (snake_game.fruit_x, snake_game.fruit_y, 
                        snake_game.fruit_size, snake_game.fruit_size), border_radius=10)
                        
        # Draw special fruit
        if snake_game.special_fruit and not snake_game.special_fruit["blink"]:
            pygame.draw.rect(screen, snake_game.special_fruit["color"], 
                           (snake_game.special_fruit["x"], snake_game.special_fruit["y"], 
                            snake_game.fruit_size, snake_game.fruit_size), border_radius=10)
                            
        # Draw particles
        for particle in snake_game.growth_particles:
            particle.draw(screen)
            
        # Draw UI
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
        pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, 50), 2)
        
        title = title_font.render("Snake Game", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 5))
        
        score_text = game_font.render(f"Score: {snake_game.score}", True, WHITE)
        screen.blit(score_text, (20, 10))
        
        level_text = game_font.render(f"Level: {snake_game.level}", True, WHITE)
        screen.blit(level_text, (WIDTH - level_text.get_width() - 20, 10))
        
        length_text = game_font.render(f"Length: {snake_game.snake_length}", True, WHITE)
        screen.blit(length_text, (WIDTH//2 - length_text.get_width()//2, 10))
        
        if snake_game.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
            
            score_text = title_font.render(f"Score: {snake_game.score}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            
            restart_text = game_font.render("Press SPACE to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
            
        # Draw back button
        back_button = Button(20, HEIGHT-70, 150, 50, "Back", RED, PINK)
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})):
            current_state = MENU
            try:
                click_sound.play()
            except:
                pass
                
    elif current_state == MEMORY_GAME:
        # Update game
        memory_game.update_particles()
        if memory_game.time_remaining() <= 0 and not memory_game.game_over:
            memory_game.game_over = True
            
        # Draw game background
        screen.fill(BLACK)
        
        # Draw particles
        memory_game.draw_particles(screen)
        
        # Draw title
        title = title_font.render("Memory Game", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))
        
        # Draw info panel
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 60))
        pygame.draw.rect(screen, PURPLE, (0, 0, WIDTH, 60), 2)
        
        level_text = game_font.render(f"Level: {memory_game.level}", True, WHITE)
        screen.blit(level_text, (20, 15))
        
        score_text = game_font.render(f"Score: {memory_game.score}", True, WHITE)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 15))
        
        moves_text = game_font.render(f"Moves: {memory_game.moves}", True, WHITE)
        screen.blit(moves_text, (WIDTH//2 - moves_text.get_width()//2, 15))
        
        time_text = game_font.render(f"Time: {int(memory_game.time_remaining())}s", True, 
                                   YELLOW if memory_game.time_remaining() < 10 else WHITE)
        screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 45))
        
        # Draw cards
        for card in memory_game.cards:
            if card["matched"]:
                color = GREEN
            elif card["face_up"]:
                color = card["color"]
            else:
                color = memory_game.card_back
                
            pygame.draw.rect(screen, color, (card["x"], card["y"], card["width"], card["height"]), border_radius=5)
            pygame.draw.rect(screen, BLACK, (card["x"], card["y"], card["width"], card["height"]), 2, border_radius=5)
            
            if card["face_up"] or card["matched"]:
                symbol_text = game_font.render(str(card["symbol"]), True, BLACK)
                screen.blit(symbol_text, 
                          (card["x"] + card["width"]//2 - symbol_text.get_width()//2,
                           card["y"] + card["height"]//2 - symbol_text.get_height()//2))
                           
        if memory_game.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
            
            if memory_game.level > 8:
                congrats_text = game_font.render("You completed all levels!", True, GREEN)
                screen.blit(congrats_text, (WIDTH//2 - congrats_text.get_width()//2, HEIGHT//2))
                
            score_text = title_font.render(f"Final Score: {memory_game.score}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 50))
            
            restart_text = game_font.render("Press SPACE to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 120))
            
        # Draw back button
        back_button = Button(20, HEIGHT-70, 150, 50, "Back", RED, PINK)
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})):
            current_state = MENU
            try:
                click_sound.play()
            except:
                pass
                
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
sys.exit()
