import pygame

pygame.init()

# =============================================================================
# Board Configuration
# =============================================================================
ROWS = 6
COLUMNS = 7
CELL_SIZE = 100
WIDTH = COLUMNS * CELL_SIZE
HEIGHT = (ROWS + 1) * CELL_SIZE

# =============================================================================
# Colors
# =============================================================================
# Background gradient colors (deep blue theme)
BACKGROUND_TOP = (10, 25, 50)
BACKGROUND_BOTTOM = (25, 50, 90)

# Header area color (darker)
HEADER_COLOR = (8, 20, 40)

# Board colors
BOARD_PRIMARY = (0, 70, 180)
BOARD_HIGHLIGHT = (60, 130, 220)
BOARD_SHADOW = (0, 40, 120)

# Empty cell color (matches board for cleaner look)
EMPTY_CELL_COLOR = (15, 35, 70)

# Token colors: [Empty, Player 1 (Red), Player 2 (Yellow)]
TOKEN_COLORS = [
    EMPTY_CELL_COLOR,  # Empty - dark blue
    (220, 50, 50),     # Player 1 - Red
    (255, 200, 50)     # Player 2 - Yellow
]

# Token shading for 3D effect
TOKEN_SHADOW = {
    1: (150, 30, 30),     # Red shadow
    2: (180, 140, 30)     # Yellow shadow
}
TOKEN_HIGHLIGHT = {
    1: (255, 120, 120),   # Red highlight
    2: (255, 240, 150)    # Yellow highlight
}

# Menu colors
MENU_TITLE_COLOR = (255, 220, 100)
MENU_TEXT_COLOR = (230, 230, 245)
MENU_SUBTITLE_COLOR = (140, 160, 200)
MENU_ACCENT_COLOR = (80, 180, 255)
MENU_BOX_BG = (20, 40, 70)

# =============================================================================
# Fonts
# =============================================================================
FONT_TITLE = pygame.font.Font(None, 85)
FONT_LARGE = pygame.font.Font(None, 65)
FONT_MEDIUM = pygame.font.Font(None, 45)
FONT_SMALL = pygame.font.Font(None, 32)
FONT_TINY = pygame.font.Font(None, 26)

# =============================================================================
# Menu Text
# =============================================================================
MENU_TITLE = "CONNECT 4"
MENU_SUBTITLE = "Select Difficulty"
MENU_OPTIONS = [
    ("1", "Easy AI", "Random + basic strategy"),
    ("2", "Hard AI", "Minimax algorithm")
]
MENU_FOOTER = "Press ESC to quit"

END_GAME_MESSAGES = {
    True: "VICTORY!",
    False: "DEFEAT!",
    None: "DRAW!"
}
END_MENU_INSTRUCTIONS = ["Press 1 to play again", "Press ESC to quit"]

# =============================================================================
# Game Title (with glow effect)
# =============================================================================
GAME_TITLE_TEXT = "CONNECT 4"
TITLE_FONT = pygame.font.Font(None, 72)

def create_title_surface():
    """Create a title with glow and shadow effects."""
    # Colors
    glow_color = (255, 180, 50)
    main_color = (255, 230, 100)
    highlight_color = (255, 255, 200)
    shadow_color = (20, 10, 0)

    # Create surface large enough for glow
    padding = 15
    text_surface = TITLE_FONT.render(GAME_TITLE_TEXT, True, main_color)
    width = text_surface.get_width() + padding * 2
    height = text_surface.get_height() + padding * 2

    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Draw shadow (offset)
    shadow = TITLE_FONT.render(GAME_TITLE_TEXT, True, shadow_color)
    surface.blit(shadow, (padding + 3, padding + 3))

    # Draw glow layers (multiple offset renders)
    for offset in [(0, -2), (0, 2), (-2, 0), (2, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        glow = TITLE_FONT.render(GAME_TITLE_TEXT, True, glow_color)
        surface.blit(glow, (padding + offset[0], padding + offset[1]))

    # Draw main text
    main = TITLE_FONT.render(GAME_TITLE_TEXT, True, main_color)
    surface.blit(main, (padding, padding))

    # Draw highlight (slight offset up-left)
    highlight = TITLE_FONT.render(GAME_TITLE_TEXT, True, highlight_color)
    highlight.set_alpha(100)
    surface.blit(highlight, (padding - 1, padding - 1))

    return surface

TITLE_SURFACE = create_title_surface()
TITLE_RECT = TITLE_SURFACE.get_rect()
TITLE_RECT.center = (WIDTH // 2, CELL_SIZE // 2)


def create_gradient_surface(width, height, top_color, bottom_color):
    """Create a vertical gradient surface."""
    surface = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    return surface


# Pre-create background gradient
BACKGROUND_SURFACE = create_gradient_surface(WIDTH, HEIGHT, BACKGROUND_TOP, BACKGROUND_BOTTOM)


# =============================================================================
# Sound System
# =============================================================================
import os

# Initialize mixer
pygame.mixer.init()

# Sound file paths (in assets/sounds/)
SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")

# Supported audio formats
AUDIO_FORMATS = [".wav", ".mp3", ".ogg"]


class SoundManager:
    """Manages game sound effects."""

    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.max_durations = {}
        self._load_sounds()

    def _find_sound_file(self, base_name):
        """Find a sound file with any supported format."""
        for ext in AUDIO_FORMATS:
            path = os.path.join(SOUNDS_DIR, base_name + ext)
            if os.path.exists(path):
                return path
        return None

    def _load_sounds(self):
        """Load all sound files if they exist."""
        # Sound name -> (base filename, max duration in ms, fallback sound)
        sound_config = {
            "drop": ("drop", 1000, None),
            "win": ("win", 2000, None),
            "lose": ("lose", 2000, None),
            "draw": ("draw", 2000, "lose"),
            "select": ("select", 500, None),
        }

        for name, (base_name, max_duration, fallback) in sound_config.items():
            path = self._find_sound_file(base_name)
            if path:
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.max_durations[name] = max_duration
                except Exception:
                    pass

        # Apply fallbacks for missing sounds
        for name, (_, max_duration, fallback) in sound_config.items():
            if name not in self.sounds and fallback and fallback in self.sounds:
                self.sounds[name] = self.sounds[fallback]
                self.max_durations[name] = max_duration

    def play(self, sound_name):
        """Play a sound by name with duration limit."""
        if self.enabled and sound_name in self.sounds:
            max_ms = self.max_durations.get(sound_name, 0)
            self.sounds[sound_name].play(maxtime=max_ms)

    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)."""
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def toggle(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled
        return self.enabled


# Global sound manager instance
SOUND_MANAGER = SoundManager()
