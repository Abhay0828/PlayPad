import pygame
import random
import sys
import time
import json
import math
from typing import List, Dict, Tuple
from pygame import gfxdraw

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions - now dynamic
info = pygame.display.Info()
WIDTH, HEIGHT = min(1200, info.current_w), min(800, info.current_h)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("4-in-1 Game Station")

# Load sound effects
try:
    sounds = {
        'click': pygame.mixer.Sound('click.wav'),
        'success': pygame.mixer.Sound('success.wav'),
        'fail': pygame.mixer.Sound('fail.wav'),
        'select': pygame.mixer.Sound('select.wav')
    }
except:
    # Create silent dummy sounds if files not found
    class DummySound:
        def play(self): pass
    sounds = {name: DummySound() for name in ['click', 'success', 'fail', 'select']}

# Constants
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 50, 50)
    GREEN = (50, 255, 50)
    BLUE = (50, 50, 255)
    YELLOW = (255, 255, 50)
    PURPLE = (180, 50, 255)
    CYAN = (50, 255, 255)
    ORANGE = (255, 150, 50)
    DARK_GRAY = (30, 30, 40)
    LIGHT_GRAY = (220, 220, 230)
    NEON_BLUE = (0, 200, 255)
    NEON_PINK = (255, 50, 200)
    NEON_GREEN = (50, 255, 100)
    DARK_BLUE = (10, 20, 40)
    GLASS = (100, 100, 120, 150)
    GLASS_DARK = (50, 60, 80, 200)

# Fonts
class Fonts:
    try:
        title = pygame.font.Font('orbitron.ttf', 60)
        large = pygame.font.Font('orbitron.ttf', 48)
        menu = pygame.font.Font('orbitron.ttf', 36)
        game = pygame.font.Font('orbitron.ttf', 28)
        small = pygame.font.Font('orbitron.ttf', 20)
    except:
        title = pygame.font.SysFont('arial', 60, bold=True)
        large = pygame.font.SysFont('arial', 48, bold=True)
        menu = pygame.font.SysFont('arial', 36, bold=True)
        game = pygame.font.SysFont('arial', 28)
        small = pygame.font.SysFont('arial', 20)

# Game states
class GameStates:
    MENU = 0
    SCRAMBLED_SAGA = 1
    BLOCK_BUSTER = 2
    SNAKE_GAME = 3
    MEMORY_GAME = 4
    EXIT_CONFIRM = 5
    SETTINGS = 6
    CREDITS = 7

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

def render_text_with_outline(text, font, color, outline_color, outline_size=2):
    text_surface = font.render(text, True, color).convert_alpha()
    w = text_surface.get_width() + 2 * outline_size
    h = text_surface.get_height() + 2 * outline_size
    
    outline_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    outline_surface.fill((0, 0, 0, 0))
    
    # Draw outline
    for x in range(-outline_size, outline_size+1):
        for y in range(-outline_size, outline_size+1):
            if x != 0 or y != 0:
                outline_text = font.render(text, True, outline_color)
                outline_surface.blit(outline_text, (outline_size + x, outline_size + y))
    
    # Draw main text
    outline_surface.blit(text_surface, (outline_size, outline_size))
    
    return outline_surface

def draw_rounded_rect(surface, rect, color, radius=10, border=0, border_color=None):
    """Draw a rectangle with rounded corners"""
    rect = pygame.Rect(rect)
    if border:
        inner_rect = rect.inflate(-border*2, -border*2)
        draw_rounded_rect(surface, inner_rect, color, radius)
        if border_color:
            draw_rounded_rect(surface, rect, border_color, radius)
        return
    
    # Draw filled rounded rectangle
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    # Draw anti-aliased corners
    corners = [
        (rect.left + radius, rect.top + radius),  # Top-left
        (rect.right - radius - 1, rect.top + radius),  # Top-right
        (rect.left + radius, rect.bottom - radius - 1),  # Bottom-left
        (rect.right - radius - 1, rect.bottom - radius - 1)  # Bottom-right
    ]
    
    for cx, cy in corners:
        gfxdraw.aacircle(surface, int(cx), int(cy), radius, color)
        gfxdraw.filled_circle(surface, int(cx), int(cy), radius, color)

class Button:
    def __init__(self, x, y, width, height, text, 
                 color=Colors.NEON_BLUE, hover_color=Colors.NEON_PINK, 
                 text_color=Colors.WHITE, radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.hover = False
        self.click_anim = 0
        self.original_y = y
        
    def draw(self, surface):
        color = self.hover_color if self.hover else self.color
        y_offset = -5 if self.hover else 0
        
        # Button shadow
        shadow_rect = pygame.Rect(
            self.rect.x + 3, 
            self.rect.y + 3 + y_offset,
            self.rect.width, 
            self.rect.height
        )
        draw_rounded_rect(surface, shadow_rect, (*Colors.BLACK[:3], 100), self.radius)
        
        # Button main
        btn_rect = pygame.Rect(
            self.rect.x, 
            self.rect.y + y_offset - self.click_anim,
            self.rect.width, 
            self.rect.height
        )
        draw_rounded_rect(surface, btn_rect, color, self.radius, 2, Colors.WHITE)
        
        # Button text
        text_surf = render_text_with_outline(self.text, Fonts.menu, self.text_color, Colors.BLACK)
        surface.blit(text_surf, (
            btn_rect.centerx - text_surf.get_width() // 2,
            btn_rect.centery - text_surf.get_height() // 2
        ))
        
        # Click animation
        if self.click_anim > 0:
            self.click_anim = max(0, self.click_anim - 1)
    
    def update(self, mouse_pos, mouse_click):
        self.hover = self.rect.collidepoint(mouse_pos)
        
        if self.hover and mouse_click:
            self.click_anim = 5
            sounds['click'].play()
            return True
        return False

class Particle:
    def __init__(self, x, y, color, shape='circle', size=None, velocity=None):
        self.x = x
        self.y = y
        self.vx = velocity[0] if velocity else random.uniform(-3, 3)
        self.vy = velocity[1] if velocity else random.uniform(-3, 3)
        self.color = color
        self.lifetime = random.randint(20, 50)
        self.size = size if size else random.randint(3, 8)
        self.shape = shape
        self.alpha = 255
        self.gravity = random.choice([0, 0.1, 0.2])
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
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
            elif self.shape == 'star':
                points = []
                for i in range(5):
                    angle = math.pi * 2 * i / 5 - math.pi / 2
                    outer_x = self.size * math.cos(angle)
                    outer_y = self.size * math.sin(angle)
                    inner_x = (self.size // 2) * math.cos(angle + math.pi / 5)
                    inner_y = (self.size // 2) * math.sin(angle + math.pi / 5)
                    points.extend([(self.size + outer_x, self.size + outer_y), 
                                 (self.size + inner_x, self.size + inner_y)])
                pygame.draw.polygon(temp_surface, color, points)
            
            # Add glow effect
            glow = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color[:3], self.alpha // 2), 
                             (self.size, self.size), self.size + 2)
            temp_surface.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.twinkle = random.random() * 5
        self.base_alpha = random.randint(150, 255)
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
        self.twinkle += 0.05
        
    def draw(self, surface):
        alpha = int(self.base_alpha * (0.8 + 0.2 * math.sin(self.twinkle)))
        color = (*Colors.WHITE[:3], alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

# High score manager (unchanged from original)

# Game classes (ScrambledSaga, BlockBusterBonanza, SnakeGame, MemoryGame)
# These would be updated with better UI elements but the core gameplay remains the same
# For brevity, I'll show the improved ScrambledSaga class as an example:

class ScrambledSaga:
    def __init__(self):
        self.reset()
        
    def reset(self):
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
        self.new_word()
        
    def draw(self, screen):
        # Draw animated background
        self.draw_background(screen)
        
        # Draw particles
        self.draw_particles(screen)
        
        # Draw UI elements with new styling
        self.draw_ui(screen)
        
        # Draw game elements
        self.draw_game_elements(screen)
        
        # Draw pause overlay if paused
        if self.paused:
            self.draw_pause_overlay(screen)
    
    def draw_ui(self, screen):
        # Draw glass panel for stats
        panel_rect = pygame.Rect(20, 20, 200, 120)
        draw_rounded_rect(screen, panel_rect, Colors.GLASS, 15)
        draw_rounded_rect(screen, panel_rect, Colors.WHITE, 15, 2)
        
        # Draw stats
        level_text = render_text_with_outline(f"Level: {self.level}", Fonts.game, Colors.WHITE, Colors.BLACK)
        score_text = render_text_with_outline(f"Score: {self.score}", Fonts.game, Colors.WHITE, Colors.BLACK)
        lives_text = render_text_with_outline(f"Lives: {'❤' * self.lives}", Fonts.game, 
                                            Colors.RED if self.lives <= 1 else Colors.WHITE, Colors.BLACK)
        
        screen.blit(level_text, (40, 30))
        screen.blit(score_text, (40, 60))
        screen.blit(lives_text, (40, 90))
        
        # Draw time remaining with animated bar
        time_panel = pygame.Rect(WIDTH - 220, 20, 200, 30)
        draw_rounded_rect(screen, time_panel, Colors.GLASS_DARK, 15)
        
        time_left = self.time_remaining()
        time_ratio = time_left / (self.time_limit / self.difficulty)
        time_fill = pygame.Rect(WIDTH - 220, 20, 200 * time_ratio, 30)
        time_color = Colors.NEON_GREEN if time_ratio > 0.5 else Colors.YELLOW if time_ratio > 0.2 else Colors.RED
        draw_rounded_rect(screen, time_fill, (*time_color[:3], 200), 15)
        draw_rounded_rect(screen, time_panel, Colors.WHITE, 15, 2)
        
        time_text = render_text_with_outline(f"Time: {int(time_left)}s", Fonts.game, Colors.WHITE, Colors.BLACK)
        screen.blit(time_text, (WIDTH - 210, 25))
        
        # Draw score animation if active
        if self.score_animation > 0:
            anim_text = render_text_with_outline(f"+{self.score_animation}", Fonts.game, Colors.YELLOW, Colors.BLACK)
            anim_y = 90 - (10 - self.score_animation) * 2  # Rising animation
            screen.blit(anim_text, (150, anim_y))
    
    def draw_game_elements(self, screen):
        # Draw title with gradient
        title = render_text_with_outline("Scrambled Saga", Fonts.large, Colors.NEON_BLUE, Colors.BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw scrambled word with fancy effect
        scrambled_rect = pygame.Rect(WIDTH // 2 - 200, 150, 400, 80)
        draw_rounded_rect(screen, scrambled_rect, Colors.GLASS, 20)
        draw_rounded_rect(screen, scrambled_rect, Colors.NEON_BLUE, 20, 2)
        
        scrambled_text = render_text_with_outline(self.scrambled_word.upper(), Fonts.title, Colors.WHITE, Colors.BLACK)
        screen.blit(scrambled_text, (WIDTH // 2 - scrambled_text.get_width() // 2, 170))
        
        # Draw input box
        input_rect = pygame.Rect(WIDTH // 2 - 200, 250, 400, 60)
        draw_rounded_rect(screen, input_rect, Colors.GLASS, 15)
        draw_rounded_rect(screen, input_rect, Colors.NEON_PINK, 15, 2)
        
        input_text = render_text_with_outline(f"Your answer: {self.user_input}", Fonts.game, Colors.WHITE, Colors.BLACK)
        screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 265))
        
        # Draw hint button
        hint_rect = pygame.Rect(WIDTH // 2 - 100, 350, 200, 40)
        draw_rounded_rect(screen, hint_rect, Colors.GLASS, 10)
        draw_rounded_rect(screen, hint_rect, Colors.YELLOW, 10, 2)
        
        hint_text = render_text_with_outline("Press H for Hint", Fonts.small, Colors.WHITE, Colors.BLACK)
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 360))
    
    def draw_pause_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*Colors.BLACK[:3], 150))
        screen.blit(overlay, (0, 0))
        
        pause_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
        draw_rounded_rect(screen, pause_rect, Colors.GLASS_DARK, 20)
        draw_rounded_rect(screen, pause_rect, Colors.NEON_BLUE, 20, 3)
        
        pause_text = render_text_with_outline("PAUSED", Fonts.title, Colors.NEON_PINK, Colors.BLACK)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
        
        continue_text = render_text_with_outline("Press P to continue", Fonts.game, Colors.WHITE, Colors.BLACK)
        screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 20))

# Main game loop with improved UI
def main():
    clock = pygame.time.Clock()
    high_score_manager = HighScoreManager()
    
    # Initialize games
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
    stars = [Star() for _ in range(100)]
    enable_animations = True
    enable_sound = True
    
    # Create logo
    logo = create_logo()
    logo_pos = (WIDTH // 2 - logo.get_width() // 2, 50)
    
    # Create menu buttons with new Button class
    menu_buttons = [
        Button(WIDTH // 2 - 150, 200, 300, 50, "Scrambled Saga"),
        Button(WIDTH // 2 - 150, 270, 300, 50, "Block Buster"),
        Button(WIDTH // 2 - 150, 340, 300, 50, "Snake Game"),
        Button(WIDTH // 2 - 150, 410, 300, 50, "Memory Game"),
        Button(WIDTH // 2 - 150, 480, 300, 50, "Settings"),
        Button(WIDTH // 2 - 150, 550, 300, 50, "Credits")
    ]
    
    # Game loop
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_state = GameStates.EXIT_CONFIRM
            
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                logo_pos = (WIDTH // 2 - logo.get_width() // 2, 50)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
        
        # Update stars
        if enable_animations:
            for star in stars:
                star.update()
        
        # Clear screen with space-like background
        screen.fill(Colors.DARK_BLUE)
        
        # Draw stars
        if enable_animations:
            for star in stars:
                star.draw(screen)
        
        # Handle current state
        if current_state == GameStates.MENU:
            # Draw logo with pulsing effect
            scale = 1.0 + 0.02 * math.sin(animation_timer * 0.05) if enable_animations else 1.0
            scaled_logo = pygame.transform.scale(
                logo, 
                (int(logo.get_width() * scale), int(logo.get_height() * scale))
            )
            screen.blit(scaled_logo, (
                WIDTH // 2 - scaled_logo.get_width() // 2,
                logo_pos[1] + (logo.get_height() - scaled_logo.get_height()) // 2
            ))
            
            # Draw menu buttons
            for i, button in enumerate(menu_buttons):
                if button.update(mouse_pos, mouse_click):
                    if i == 0:
                        transition_state = GameStates.SCRAMBLED_SAGA
                        scrambled_game.reset()
                    elif i == 1:
                        transition_state = GameStates.BLOCK_BUSTER
                        block_game.reset()
                    elif i == 2:
                        transition_state = GameStates.SNAKE_GAME
                        snake_game.reset()
                    elif i == 3:
                        transition_state = GameStates.MEMORY_GAME
                        memory_game.reset()
                    elif i == 4:
                        current_state = GameStates.SETTINGS
                    elif i == 5:
                        current_state = GameStates.CREDITS
                
                button.draw(screen)
            
            # Draw high scores
            score_panel = pygame.Rect(20, HEIGHT - 180, 250, 160)
            draw_rounded_rect(screen, score_panel, Colors.GLASS, 15)
            draw_rounded_rect(screen, score_panel, Colors.NEON_BLUE, 15, 2)
            
            score_title = render_text_with_outline("High Scores", Fonts.game, Colors.WHITE, Colors.BLACK)
            screen.blit(score_title, (30, HEIGHT - 170))
            
            for i, (game, score) in enumerate(high_score_manager.scores.items()):
                game_name = game.replace('_', ' ').title()
                score_text = render_text_with_outline(f"{game_name}: {score}", Fonts.small, Colors.WHITE, Colors.BLACK)
                screen.blit(score_text, (30, HEIGHT - 140 + i * 25))
        
        elif current_state == GameStates.SCRAMBLED_SAGA:
            scrambled_game.draw(screen)
            
            # Back button
            back_btn = Button(20, HEIGHT - 70, 120, 50, "Menu")
            if back_btn.update(mouse_pos, mouse_click):
                transition_state = GameStates.MENU
                high_score_manager.update_score('scrambled_saga', scrambled_game.score)
            back_btn.draw(screen)
        
        # Other game states would follow similar patterns...
        
        # Handle transitions
        if transition_state:
            transition_alpha = min(255, transition_alpha + 15)
            if transition_alpha == 255:
                current_state = transition_state
                transition_state = None
                transition_alpha = 0
        elif transition_alpha > 0:
            transition_alpha = max(0, transition_alpha - 15)
        
        # Draw transition overlay if needed
        if transition_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((*Colors.BLACK[:3], transition_alpha))
            screen.blit(overlay, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)
        animation_timer += 1
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
