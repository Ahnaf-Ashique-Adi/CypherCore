import pygame
import sys
import os
import time
import random
from matrix_effect import MatrixEffect
from audio_engine import AudioEngine
from level_manager import LevelManager

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BRIGHT_GREEN = (0, 255, 128)
BLUE = (0, 128, 255)
RED = (255, 0, 0)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CypherCore")
clock = pygame.time.Clock()

# Game states
INTRO = 0
MAIN_MENU = 1
PLAYING = 2
GAME_OVER = 3

class Game:
    def __init__(self):
        self.state = INTRO
        self.font = pygame.font.SysFont('consolas', 20)
        self.title_font = pygame.font.SysFont('consolas', 40)
        
        # Initialize components
        self.matrix_effect = MatrixEffect(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.matrix_effect.set_color_scheme("cyan_purple")  # Set the new color scheme
        self.audio_engine = AudioEngine()
        self.level_manager = LevelManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Setup intro screen
        self.setup_intro()
        
        # Menu options
        self.menu_options = ["Start Game", "Quit"]
        self.selected_option = 0
        
        # Transition effects
        self.transition_active = False
        self.transition_start_time = 0
        self.transition_duration = 1000  # 1 second
        self.transition_from_state = None
        self.transition_to_state = None
        self.transition_alpha = 0
        
        # Performance tracking
        self.frame_times = []
        self.show_fps = False
        
    def setup_intro(self):
        self.intro_text = [
            "   ______      ______  _                 ______                 ",
            "  / ____/_  __/ __ \\ |__   ___  _ __   / ____/___   _ __ ___   ",
            " / /   / / / / /_/ / '_ \\ / _ \\| '_ \\ / /    / _ \\ | '__/ _ \\  ",
            "/ /___/ /_/ / ____/| | | | (_) | | | / /____| (_) || | |  __/  ",
            "\\____/\\__, /_/    |_| |_|\\___/|_| |_\\______|\\___/ |_|  \\___|  ",
            "     /____/                                                     "
        ]
        self.intro_progress = 0
        self.intro_char_index = 0
        self.intro_line_index = 0
        self.intro_complete = False
        self.intro_start_time = time.time()
        self.intro_display_text = ["" for _ in range(len(self.intro_text))]
        
    def run(self):
        # Main game loop
        running = True
        while running:
            # Start frame timing
            frame_start_time = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    # Toggle FPS display
                    self.show_fps = not self.show_fps
                self.handle_event(event)
            
            # Update game state
            self.update()
            
            # Render the game
            self.render()
            
            # Cap the frame rate
            clock.tick(FPS)
            
            # Track frame time for performance monitoring
            frame_time = time.time() - frame_start_time
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 60:  # Keep only last 60 frames
                self.frame_times.pop(0)
        
        pygame.quit()
        sys.exit()
    
    def handle_event(self, event):
        # Don't process events during transitions
        if self.transition_active:
            return
            
        if self.state == INTRO:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.start_transition(INTRO, MAIN_MENU)
                self.audio_engine.play_sound('click')
        
        elif self.state == MAIN_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    self.audio_engine.play_sound('click')
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    self.audio_engine.play_sound('click')
                elif event.key == pygame.K_RETURN:
                    self.select_menu_option()
        
        elif self.state == PLAYING:
            self.level_manager.handle_event(event)
    
    def select_menu_option(self):
        if self.menu_options[self.selected_option] == "Start Game":
            self.start_transition(MAIN_MENU, PLAYING)
            self.audio_engine.play_sound('success')
        elif self.menu_options[self.selected_option] == "Quit":
            pygame.quit()
            sys.exit()
    
    def start_transition(self, from_state, to_state):
        """Start a transition between game states"""
        self.transition_active = True
        self.transition_start_time = pygame.time.get_ticks()
        self.transition_from_state = from_state
        self.transition_to_state = to_state
    
    def update_transition(self):
        """Update the transition effect"""
        if not self.transition_active:
            return
            
        elapsed = pygame.time.get_ticks() - self.transition_start_time
        progress = elapsed / self.transition_duration
        
        if progress < 0.5:
            # First half: fade out
            self.transition_alpha = int(progress * 2 * 255)
        else:
            # Second half: fade in and change state
            if self.state == self.transition_from_state:
                self.state = self.transition_to_state
                
                # Reset intro if going back to it
                if self.state == INTRO:
                    self.setup_intro()
                
            self.transition_alpha = int((1 - (progress - 0.5) * 2) * 255)
        
        # End transition
        if progress >= 1.0:
            self.transition_active = False
    
    def update(self):
        # Update transition effect
        self.update_transition()
        
        # Update matrix effect background with occasional glitches
        self.matrix_effect.update()
        
        # Randomly trigger glitch effects for more visual interest
        if random.random() < 0.01 and self.state != INTRO:  # 1% chance per frame
            self.matrix_effect.render_glitch(screen, 0.2)
        
        if not self.transition_active:
            if self.state == INTRO:
                self.update_intro()
            elif self.state == PLAYING:
                self.level_manager.update()
    
    def update_intro(self):
        # Auto-progress intro after 10 seconds
        if time.time() - self.intro_start_time > 10:
            self.start_transition(INTRO, MAIN_MENU)
            return
            
        # Typewriter effect for ASCII art
        if not self.intro_complete:
            if self.intro_line_index < len(self.intro_text):
                if self.intro_char_index < len(self.intro_text[self.intro_line_index]):
                    self.intro_display_text[self.intro_line_index] = self.intro_text[self.intro_line_index][:self.intro_char_index+1]
                    self.intro_char_index += 1
                else:
                    self.intro_line_index += 1
                    self.intro_char_index = 0
            else:
                # All lines are complete
                self.intro_progress = 100
    
    def render(self):
        screen.fill(BLACK)
        
        # Draw matrix effect as background for all states except intro
        if self.state != INTRO:
            # Use glitch effect during transitions
            if self.transition_active:
                self.matrix_effect.render_glitch(screen, 0.2)
            else:
                self.matrix_effect.render(screen, 64)  # Lower alpha for background
        
        if self.state == INTRO:
            self.render_intro()
        elif self.state == MAIN_MENU:
            self.render_main_menu()
        elif self.state == PLAYING:
            self.level_manager.render(screen)
        
        # Draw transition overlay
        if self.transition_active:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.transition_alpha))
            screen.blit(overlay, (0, 0))
        
        # Draw FPS counter if enabled
        if self.show_fps and self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / max(avg_frame_time, 0.001)  # Avoid division by zero
            fps_text = self.font.render(f"FPS: {int(fps)}", True, GREEN)
            screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 10, 10))
        
        pygame.display.flip()
    
    def render_intro(self):
        # Draw ASCII art with typewriter effect
        y_offset = SCREEN_HEIGHT // 2 - (len(self.intro_text) * 20) // 2
        
        for i, line in enumerate(self.intro_display_text):
            # Add glitch effect
            glitch_line = line
            if random.random() < 0.05 and line:  # 5% chance of glitch
                glitch_pos = random.randint(0, len(line)-1)
                glitch_char = chr(random.randint(33, 126))
                glitch_line = line[:glitch_pos] + glitch_char + line[glitch_pos+1:]
            
            text_surface = self.font.render(glitch_line, True, GREEN)
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, y_offset + i * 20))
        
        # Press Enter to continue
        if self.intro_progress >= 80:
            press_enter = self.font.render("Press ENTER to continue...", True, 
                                          GREEN if pygame.time.get_ticks() % 1000 < 500 else BLACK)
            screen.blit(press_enter, (SCREEN_WIDTH // 2 - press_enter.get_width() // 2, 
                                     y_offset + len(self.intro_text) * 20 + 40))
    
    def render_main_menu(self):
        # Draw title
        title = self.title_font.render("CypherCore", True, BRIGHT_GREEN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Draw subtitle
        subtitle = self.font.render("A Cyberpunk Puzzle Adventure", True, GREEN)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
        
        # Draw menu options
        y_offset = 250
        for i, option in enumerate(self.menu_options):
            if i == self.selected_option:
                # Selected option
                color = BRIGHT_GREEN
                option_text = f"> {option} <"
            else:
                # Unselected option
                color = GREEN
                option_text = option
            
            text = self.font.render(option_text, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset + i * 40))
        
        # Draw footer
        footer = self.font.render("Use arrow keys to navigate, ENTER to select", True, GREEN)
        screen.blit(footer, (SCREEN_WIDTH // 2 - footer.get_width() // 2, SCREEN_HEIGHT - 50))

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
