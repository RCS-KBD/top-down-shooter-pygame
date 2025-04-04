class Settings:
    """Game settings class for top-down shooter."""

    def __init__(self):
        """Initialize settings."""
        # Screen settings
        self.screen_width = 1024
        self.screen_height = 768
        self.title = "Top-Down Shooter"
        self.bg_color = (20, 20, 20)
        self.fps = 60

        # Player settings
        self.player_speed = 5.0
        self.player_rotation_speed = 8.0  # Degrees per frame, scaled by FPS
        self.player_size = (64, 64)
        
        # Weapon settings
        self.bullet_speed = 10.0
        self.bullet_size = (8, 8)
        self.bullet_color = (255, 255, 0)
        self.bullet_lifetime = 1000  # milliseconds
        
        # Game world settings
        self.tile_size = 64
        self.world_size = (32, 24)  # in tiles
        
        # Camera settings
        self.camera_lerp = 0.1  # camera smoothing factor