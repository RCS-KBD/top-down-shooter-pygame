import pygame
import random
from ..settings import Settings
from ..components.player import Player
from ..components.enemy import Enemy
from ..components.tilemap import Tilemap
from ..components.camera import Camera

class GameplayScene:
    """Main gameplay scene."""
    
    def __init__(self, screen: pygame.Surface, settings: Settings):
        """Initialize the gameplay scene."""
        self.screen = screen
        self.settings = settings
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # Create tilemap
        self.tilemap = Tilemap(settings)
        
        # Create camera
        self.camera = Camera(settings)
        
        # Create player at center of screen
        player_x = settings.screen_width // 2
        player_y = settings.screen_height // 2
        self.player = Player(settings, player_x, player_y)
        self.all_sprites.add(self.player)
        
        # Game state
        self.score = 0
        self.max_enemies = 5
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 74)
        
        # Spawn initial enemies
        self.spawn_enemies(self.max_enemies)
        
    def spawn_enemies(self, count: int):
        """Spawn a number of enemies at random positions."""
        for _ in range(count):
            while True:
                # Try to find a valid spawn position
                x = random.randint(100, self.settings.world_size[0] * self.settings.tile_size - 100)
                y = random.randint(100, self.settings.world_size[1] * self.settings.tile_size - 100)
                
                # Create temporary rect to check position
                temp_rect = pygame.Rect(x - 32, y - 32, 64, 64)
                
                # Check if position is valid (not in walls, far from player, and not colliding with other enemies)
                valid_position = (not self.tilemap.check_collision(temp_rect) and
                                abs(x - self.player.rect.centerx) > 300 and
                                abs(y - self.player.rect.centery) > 300)
                
                if valid_position:
                    # Check collision with existing enemies
                    enemy_collision = False
                    for enemy in self.enemies:
                        if temp_rect.colliderect(enemy.rect):
                            enemy_collision = True
                            break
                    
                    if not enemy_collision:
                        enemy = Enemy(self.settings, x, y)
                        self.enemies.add(enemy)
                        self.all_sprites.add(enemy)
                        break
        
    def handle_event(self, event):
        """Handle game events."""
        if event.type == pygame.QUIT:
            return False
            
        if event.type == pygame.KEYDOWN:
            # Toggle pause
            if event.key == pygame.K_ESCAPE:
                self.settings.paused = not self.settings.paused
            # Debug controls
            elif event.key == pygame.K_F1:
                self.settings.debug_menu_visible = not self.settings.debug_menu_visible
            elif event.key == pygame.K_F2:
                self.settings.invincible = not self.settings.invincible
            elif event.key == pygame.K_F3:
                self.settings.game_won = True
                
        if not self.settings.paused and not self.settings.game_won:
            # Handle player events
            bullet = self.player.handle_event(event)
            if bullet:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)
            
        return True
        
    def update(self):
        """Update game state."""
        if self.settings.paused or self.settings.game_won:
            return
            
        # Update player
        self.player.update(self.tilemap, self.camera)
        
        # Update camera to follow player
        self.camera.update(self.player.rect.centerx, self.player.rect.centery)
        
        # Update enemies and handle their bullets
        for enemy in self.enemies:
            bullet = enemy.update((self.player.rect.centerx, self.player.rect.centery), 
                                self.tilemap, self.enemies)
            if bullet:
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)
        
        # Update bullets
        for bullet in self.player_bullets:
            bullet.update()
            # Check collision with walls
            if bullet.check_collision(self.tilemap):
                bullet.kill()
            else:
                # Check collision with enemies
                for enemy in pygame.sprite.spritecollide(bullet, self.enemies, False):
                    if enemy.take_damage(25):
                        self.score += 100
                    bullet.kill()
                    break
                
        for bullet in self.enemy_bullets:
            bullet.update()
            # Check collision with walls
            if bullet.check_collision(self.tilemap):
                bullet.kill()
            else:
                # Check collision with player
                if pygame.sprite.collide_rect(bullet, self.player):
                    if not self.settings.invincible and self.player.take_damage(10):
                        self.settings.game_over = True
                    bullet.kill()
        
        # Check win condition
        if len(self.enemies) == 0:
            self.settings.game_won = True
        
    def draw(self):
        """Draw the scene."""
        # Clear screen
        self.screen.fill(self.settings.bg_color)
        
        # Draw tilemap
        tilemap_rect = self.tilemap.surface.get_rect()
        screen_rect = self.screen.get_rect()
        tilemap_pos = self.camera.apply(self.tilemap.surface, (tilemap_rect.x, tilemap_rect.y))
        self.screen.blit(self.tilemap.surface, tilemap_pos)
        
        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            screen_pos = self.camera.apply_rect(sprite.rect)
            self.screen.blit(sprite.image, screen_pos)
            # Draw health bars for enemies
            if isinstance(sprite, Enemy):
                sprite.draw_health_bar(self.screen, 
                                     (screen_pos.x - sprite.rect.x, 
                                      screen_pos.y - sprite.rect.y))
        
        # Draw UI
        if not self.settings.game_over and not self.settings.game_won:
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            
            # Draw health
            health_text = self.font.render(f"Health: {self.player.health}", True, (255, 255, 255))
            self.screen.blit(health_text, (10, 50))
            
            # Draw debug menu if enabled
            if self.settings.debug_menu_visible:
                debug_y = 90
                debug_color = (0, 255, 0)
                
                # Debug status
                debug_text = self.font.render("Debug Menu (F1)", True, debug_color)
                self.screen.blit(debug_text, (10, debug_y))
                
                # Invincibility status
                invincible_text = self.font.render(
                    f"Invincible (F2): {'ON' if self.settings.invincible else 'OFF'}", 
                    True, debug_color)
                self.screen.blit(invincible_text, (10, debug_y + 30))
                
                # Win trigger
                win_text = self.font.render("Press F3 to Win", True, debug_color)
                self.screen.blit(win_text, (10, debug_y + 60))