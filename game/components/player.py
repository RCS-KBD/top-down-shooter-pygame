import pygame
import math
from ..settings import Settings
from .bullet import Bullet

class Player(pygame.sprite.Sprite):
    """Player class for the top-down shooter."""
    
    def __init__(self, settings: Settings, x: int, y: int):
        """Initialize the player."""
        super().__init__()
        self.settings = settings
        
        # Load and scale player image
        self.original_image = pygame.image.load("game/assets/images/Topdown Shooter/PNG/Man Blue/manBlue_gun.png")
        self.original_image = pygame.transform.scale(self.original_image, settings.player_size)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        
        # Position and movement
        self.x = float(x)
        self.y = float(y)
        self.rect.centerx = x
        self.rect.centery = y
        self.angle = 0
        self.target_angle = 0
        self.rotation_speed = settings.player_rotation_speed * 60  # Scale with FPS
        
        # Movement flags
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        
        # Combat attributes
        self.health = 100
        self.shoot_delay = 250  # milliseconds
        self.last_shot = 0
        
    def update(self, tilemap, camera=None):
        """Update the player's position and rotation."""
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert screen mouse position to world position
        if camera:
            world_mouse_x = mouse_x + camera.offset_x
            world_mouse_y = mouse_y + camera.offset_y
        else:
            world_mouse_x = mouse_x
            world_mouse_y = mouse_y
            
        # Calculate relative position and angle
        rel_x = world_mouse_x - self.x
        rel_y = world_mouse_y - self.y
        self.target_angle = math.degrees(math.atan2(-rel_y, rel_x))
        
        # Calculate shortest rotation path
        angle_diff = (self.target_angle - self.angle + 180) % 360 - 180
        rotation_amount = self.rotation_speed / self.settings.fps
        
        # Rotate towards target angle
        if abs(angle_diff) > 0.5:  # Only rotate if difference is significant
            if angle_diff > 0:
                self.angle += min(rotation_amount, angle_diff)
            else:
                self.angle -= min(rotation_amount, -angle_diff)
        else:
            self.angle = self.target_angle
            
        # Update player image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Store old position for collision checking
        old_x, old_y = self.x, self.y
        
        # Update position based on movement flags
        if self.moving_up:
            self.y -= self.settings.player_speed
        if self.moving_down:
            self.y += self.settings.player_speed
        if self.moving_left:
            self.x -= self.settings.player_speed
        if self.moving_right:
            self.x += self.settings.player_speed
            
        # Update rect position and check collisions
        self.rect.centerx = int(self.x)
        if tilemap.check_collision(self.rect):
            self.x = old_x
            self.rect.centerx = int(self.x)
            
        self.rect.centery = int(self.y)
        if tilemap.check_collision(self.rect):
            self.y = old_y
            self.rect.centery = int(self.y)
        
    def handle_event(self, event) -> Bullet:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.moving_up = True
            elif event.key == pygame.K_s:
                self.moving_down = True
            elif event.key == pygame.K_a:
                self.moving_left = True
            elif event.key == pygame.K_d:
                self.moving_right = True
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.moving_up = False
            elif event.key == pygame.K_s:
                self.moving_down = False
            elif event.key == pygame.K_a:
                self.moving_left = False
            elif event.key == pygame.K_d:
                self.moving_right = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                current_time = pygame.time.get_ticks()
                if current_time - self.last_shot > self.shoot_delay:
                    self.last_shot = current_time
                    return Bullet(self.settings, self.rect.centerx, self.rect.centery, self.angle)
        
        return None
        
    def take_damage(self, damage: int):
        """Take damage and check if dead."""
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False