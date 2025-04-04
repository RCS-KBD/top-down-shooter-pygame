import pygame
import traceback
import sys
from game.settings import Settings
from game.scenes.gameplay import GameplayScene

class Game:
    """Main game class."""

    def __init__(self):
        """Initialize game."""
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption(self.settings.title)
        self.clock = pygame.time.Clock()
        self.running = True
        
        try:
            # Initialize gameplay scene
            self.current_scene = GameplayScene(self.screen, self.settings)
        except Exception as e:
            print("Error initializing gameplay scene:")
            traceback.print_exc()
            pygame.quit()
            sys.exit(1)

    def handle_events(self):
        """Handle game events."""
        try:
            for event in pygame.event.get():
                if not self.current_scene.handle_event(event):
                    self.running = False
        except Exception as e:
            print("Error handling events:")
            traceback.print_exc()
            self.running = False

    def update(self):
        """Update game state."""
        try:
            self.current_scene.update()
        except Exception as e:
            print("Error updating game state:")
            traceback.print_exc()
            self.running = False

    def draw(self):
        """Draw the game screen."""
        try:
            self.current_scene.draw()
        except Exception as e:
            print("Error drawing game screen:")
            traceback.print_exc()
            self.running = False

    def run(self):
        """Main game loop."""
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(self.settings.fps)
        except Exception as e:
            print("Error in main game loop:")
            traceback.print_exc()
        finally:
            pygame.quit()