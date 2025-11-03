"""
HEART BALLOON POP - Main game implementation.
"""

import pygame
import random
import time
import math
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


# Virtual resolution (increased for better readability)
VIRTUAL_WIDTH = 480
VIRTUAL_HEIGHT = 270

# Physical resolution
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Scale factor (6x for pixel-perfect scaling)
SCALE = 6

# Colors (Bright and cheerful pastel palette!)
COLOR_SKY = (135, 206, 250)        # Light sky blue - cheerful!
COLOR_GROUND = (152, 251, 152)     # Pale green - bright grass
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 99, 71)          # Tomato red - bright but not harsh
COLOR_YELLOW = (255, 215, 0)       # Gold - warm and bright
COLOR_PINK = (255, 182, 193)       # Light pink
COLOR_ORANGE = (255, 165, 0)       # Orange - vibrant
COLOR_PURPLE = (186, 85, 211)      # Medium orchid
COLOR_GREEN = (50, 205, 50)        # Lime green - vibrant
COLOR_CYAN = (0, 191, 255)         # Deep sky blue - bright
COLOR_MAGENTA = (238, 130, 238)    # Violet

# High contrast text colors (readable on any background)
COLOR_TEXT_MAIN = (255, 255, 255)     # White - maximum readability
COLOR_TEXT_SECONDARY = (255, 255, 255)  # White - consistent
COLOR_TEXT_HIGHLIGHT = (255, 215, 0) # Gold - vibrant and visible

# Game settings
GAME_DURATION = 30  # seconds
BALLOON_SPAWN_INTERVAL = 0.8  # seconds (even faster!)
BALLOON_SPEED_MIN = 20
BALLOON_SPEED_MAX = 40
BALLOON_SIZE = 12
BULLET_SPEED = 120
BULLET_SIZE = 4
SHOOT_COOLDOWN = 0.3  # seconds

# Scoring
SCORE_PER_BALLOON = 10

# Balloon types and their probabilities
BALLOON_TYPES = {
    "normal": 0.35,      # 35% - Normal balloon (+10 points)
    "bonus": 0.20,       # 20% - Bonus balloon (+20 points, golden)
    "penalty": 0.20,     # 20% - Penalty balloon (-30 points, dark purple) - INCREASED!
    "fast": 0.10,        # 10% - Fast balloon (+15 points, moves faster)
    "zigzag": 0.10,      # 10% - Zigzag balloon (+15 points, moves horizontally)
    "ultra_rare": 0.05,  # 5% - ULTRA RARE super fast balloon (+100 points!!!)
}


class Balloon:
    """Balloon sprite with various types."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int], speed: float, balloon_type: str = "normal"):
        self.x = x
        self.y = y
        self.initial_x = x  # For zigzag movement
        self.color = color
        self.speed = speed
        self.radius = BALLOON_SIZE
        self.alive = True
        self.balloon_type = balloon_type
        self.age = 0  # For zigzag animation

        # Type-specific properties
        if balloon_type == "bonus":
            self.color = (255, 215, 0)  # Gold
            self.score_value = 20
            self.radius = BALLOON_SIZE + 2  # Slightly larger
        elif balloon_type == "penalty":
            self.color = (138, 43, 226)  # Blue violet
            self.score_value = -30  # INCREASED penalty!
        elif balloon_type == "fast":
            self.speed *= 1.8  # 80% faster
            self.score_value = 15
        elif balloon_type == "zigzag":
            self.score_value = 15
        elif balloon_type == "ultra_rare":
            self.color = (255, 0, 255)  # Magenta/Purple - ULTRA RARE!
            self.speed *= 3.0  # 3x faster!!!
            self.score_value = 100
            self.radius = BALLOON_SIZE + 3  # Even larger
        else:  # normal
            self.score_value = 10

    def update(self, dt: float):
        """Update balloon position."""
        self.age += dt

        # Vertical movement (upward)
        self.y -= self.speed * dt

        # Horizontal movement for zigzag type
        if self.balloon_type == "zigzag":
            # Sine wave horizontal movement
            self.x = self.initial_x + math.sin(self.age * 3) * 30

        # Remove if off screen
        if self.y < -self.radius * 2:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        """Draw balloon on surface."""
        # Balloon body (circle)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

        # Balloon highlight (smaller circle)
        highlight_offset = self.radius // 3
        pygame.draw.circle(
            surface,
            COLOR_WHITE,
            (int(self.x - highlight_offset), int(self.y - highlight_offset)),
            self.radius // 4
        )

        # Type-specific visual indicators
        if self.balloon_type == "bonus":
            # Star symbol for bonus (larger yellow center)
            pygame.draw.circle(surface, (255, 215, 0), (int(self.x), int(self.y)), 5)
        elif self.balloon_type == "penalty":
            # Skull symbol for penalty (simple dots for eyes)
            pygame.draw.circle(surface, COLOR_BLACK, (int(self.x - 3), int(self.y - 2)), 2)
            pygame.draw.circle(surface, COLOR_BLACK, (int(self.x + 3), int(self.y - 2)), 2)
            # Frown
            pygame.draw.arc(surface, COLOR_BLACK,
                          (int(self.x - 4), int(self.y), 8, 6), 0, 3.14, 2)
            # Draw "-30" text
            mini_font = pygame.font.Font(None, 16)
            text = mini_font.render("-30", True, COLOR_WHITE)
            surface.blit(text, (int(self.x - 8), int(self.y + 2)))
        elif self.balloon_type == "fast":
            # Lightning bolt symbol for fast balloon
            points = [
                (int(self.x + 2), int(self.y - 5)),
                (int(self.x), int(self.y)),
                (int(self.x + 2), int(self.y + 1)),
                (int(self.x), int(self.y + 5)),
                (int(self.x - 1), int(self.y)),
                (int(self.x + 1), int(self.y - 1))
            ]
            pygame.draw.polygon(surface, COLOR_YELLOW, points)
        elif self.balloon_type == "zigzag":
            # Wavy line symbol for zigzag balloon
            for i in range(3):
                x_offset = -4 + i * 4
                y_offset = 2 if i % 2 == 0 else -2
                pygame.draw.circle(surface, COLOR_CYAN,
                                 (int(self.x + x_offset), int(self.y + y_offset)), 2)
        elif self.balloon_type == "ultra_rare":
            # ULTRA RARE: Big star and "100" text!
            # Draw multiple stars
            pygame.draw.circle(surface, COLOR_YELLOW, (int(self.x), int(self.y)), 7)
            pygame.draw.circle(surface, COLOR_WHITE, (int(self.x), int(self.y)), 5)
            # Draw "100!" text
            mini_font = pygame.font.Font(None, 18)
            text = mini_font.render("100", True, COLOR_BLACK)
            surface.blit(text, (int(self.x - 10), int(self.y - 4)))

        # Balloon string (line)
        pygame.draw.line(
            surface,
            COLOR_BLACK,
            (int(self.x), int(self.y + self.radius)),
            (int(self.x), int(self.y + self.radius + 10)),
            1
        )

    def collides_with(self, x: float, y: float, radius: float) -> bool:
        """Check collision with a point."""
        distance = ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5
        return distance < (self.radius + radius)


class ShootEffect:
    """Shooting effect that appears at shoot position."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 3
        self.max_radius = 20
        self.alive = True
        self.lifetime = 0.3  # seconds
        self.age = 0

    def update(self, dt: float):
        """Update effect animation."""
        self.age += dt
        if self.age >= self.lifetime:
            self.alive = False
        else:
            # Expand radius over time
            progress = self.age / self.lifetime
            self.radius = 3 + (self.max_radius - 3) * progress

    def draw(self, surface: pygame.Surface):
        """Draw shoot effect on surface."""
        # Calculate alpha based on age (fade out)
        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress))

        # Draw expanding circle with fading effect
        for i in range(3):
            r = int(self.radius - i * 2)
            if r > 0:
                color_alpha = max(0, alpha - i * 50)
                color = (COLOR_YELLOW[0], COLOR_YELLOW[1], COLOR_YELLOW[2], color_alpha)
                # Draw semi-transparent circles
                pygame.draw.circle(surface, COLOR_YELLOW, (int(self.x), int(self.y)), r, 2)


class Game:
    """Main game logic."""

    def __init__(self):
        pygame.init()

        # Create display surface
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("HEART BALLOON POP")

        # Create virtual surface for pixel-perfect rendering
        self.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

        # Load background image
        self.background_image = None
        self._load_background()

        # Clock
        self.clock = pygame.time.Clock()

        # Font (system fonts for better appearance)
        # Try to use a nice monospace font, fallback to default
        try:
            self.font_small = pygame.font.SysFont("couriernew,monospace,dejavusansmono", 22, bold=True)
            self.font = pygame.font.SysFont("couriernew,monospace,dejavusansmono", 28, bold=True)
            self.font_big = pygame.font.SysFont("couriernew,monospace,dejavusansmono", 48, bold=True)
        except:
            # Fallback to default font
            self.font_small = pygame.font.Font(None, 22)
            self.font = pygame.font.Font(None, 28)
            self.font_big = pygame.font.Font(None, 48)

        # Game state
        self.state = "READY"  # READY, RUN, RESULT
        self.score = 0
        self.balloons_popped = 0
        self.game_start_time = 0
        self.last_shoot_time = 0
        self.last_balloon_spawn = 0

        # Game objects
        self.balloons: List[Balloon] = []
        self.shoot_effects: List[ShootEffect] = []

        # Balloon colors (pop & vibrant)
        self.balloon_colors = [COLOR_RED, COLOR_YELLOW, COLOR_PINK, COLOR_ORANGE, COLOR_PURPLE, COLOR_GREEN, COLOR_CYAN, COLOR_MAGENTA]

        # Running flag
        self.running = True

        # Camera preview
        self.camera_frame = None
        self.show_camera_preview = True

        # Aiming system
        self.is_aiming = False
        self.aiming_position = None

    def spawn_balloon(self):
        """Spawn a new balloon at random position with random type."""
        x = random.randint(BALLOON_SIZE, VIRTUAL_WIDTH - BALLOON_SIZE)
        y = VIRTUAL_HEIGHT + BALLOON_SIZE
        color = random.choice(self.balloon_colors)
        speed = random.uniform(BALLOON_SPEED_MIN, BALLOON_SPEED_MAX)

        # Choose balloon type based on probability
        rand_val = random.random()
        cumulative_prob = 0
        balloon_type = "normal"

        for btype, prob in BALLOON_TYPES.items():
            cumulative_prob += prob
            if rand_val <= cumulative_prob:
                balloon_type = btype
                break

        balloon = Balloon(x, y, color, speed, balloon_type)
        self.balloons.append(balloon)

    def shoot(self, x: float, y: float):
        """Shoot at given position - instant hit detection."""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_shoot_time < SHOOT_COOLDOWN:
            return

        # Convert normalized coordinates (0-1000) to virtual coordinates
        virtual_x = (x / 1000.0) * VIRTUAL_WIDTH
        virtual_y = (y / 1000.0) * VIRTUAL_HEIGHT

        # Create shoot effect at position
        effect = ShootEffect(virtual_x, virtual_y)
        self.shoot_effects.append(effect)

        # Instant hit detection at shoot position
        hit_radius = 15  # Hit detection radius
        for balloon in self.balloons:
            if balloon.alive and balloon.collides_with(virtual_x, virtual_y, hit_radius):
                balloon.alive = False
                # Add score based on balloon type
                self.score += balloon.score_value
                # Only count positive scores toward balloon count
                if balloon.score_value > 0:
                    self.balloons_popped += 1
                # Only hit one balloon per shot
                break

        self.last_shoot_time = current_time


    def calculate_time_tickets(self) -> int:
        """
        Calculate time tickets based on balloons popped (in seconds).

        Logic:
        - Maximum: +90 seconds (1:30) for excellent performance (30+ balloons)
        - Middle point: 0 seconds for average performance (15 balloons)
        - Below middle: Negative time penalty for poor performance

        Returns:
            Time tickets in seconds (can be negative)
        """
        # Linear scale based on balloons popped
        # Middle point (0 seconds): 15 balloons
        # Maximum (+90 seconds): 30 balloons or more
        # Below middle: -6 seconds per balloon below 15

        if self.balloons_popped >= 30:
            # Maximum reward: 90 seconds (1:30)
            return 90
        elif self.balloons_popped >= 15:
            # Linear interpolation between 0 and 90 seconds
            # For each balloon above 15, add 6 seconds (90/15 = 6)
            return (self.balloons_popped - 15) * 6
        else:
            # Penalty: -6 seconds per balloon below 15
            return (self.balloons_popped - 15) * 6

    def update(self, dt: float):
        """Update game state."""
        if self.state == "READY":
            # Wait for user input to start
            pass

        elif self.state == "RUN":
            current_time = time.time()
            elapsed_time = current_time - self.game_start_time

            # Check if game time is up
            if elapsed_time >= GAME_DURATION:
                self.state = "RESULT"
                return

            # Spawn balloons
            if current_time - self.last_balloon_spawn >= BALLOON_SPAWN_INTERVAL:
                self.spawn_balloon()
                self.last_balloon_spawn = current_time

            # Update balloons
            for balloon in self.balloons:
                balloon.update(dt)

            # Update shoot effects
            for effect in self.shoot_effects:
                effect.update(dt)

            # Remove dead objects
            self.balloons = [b for b in self.balloons if b.alive]
            self.shoot_effects = [e for e in self.shoot_effects if e.alive]

    def set_camera_frame(self, frame):
        """Set current camera frame for preview."""
        self.camera_frame = frame

    def set_aiming(self, is_aiming: bool, position: Optional[Tuple[int, int]]):
        """Set aiming state and position."""
        self.is_aiming = is_aiming
        self.aiming_position = position

    def _load_background(self):
        """Load background image from assets folder."""
        try:
            # Try to load background.jpg first, then background.png
            background_path = None
            if (Path(__file__).parent.parent / "assets" / "background.jpg").exists():
                background_path = str(Path(__file__).parent.parent / "assets" / "background.jpg")
            elif (Path(__file__).parent.parent / "assets" / "background.png").exists():
                background_path = str(Path(__file__).parent.parent / "assets" / "background.png")

            if background_path:
                # Load and scale background to virtual resolution
                original_bg = pygame.image.load(background_path)
                self.background_image = pygame.transform.scale(original_bg, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
                print(f"Background image loaded: {background_path}")
            else:
                print("No background image found, using default background")
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.background_image = None

    def draw(self):
        """Draw game on virtual surface."""
        # Draw background image or default background
        if self.background_image:
            # Use background image
            self.virtual_surface.blit(self.background_image, (0, 0))
        else:
            # Use default background
            self.virtual_surface.fill(COLOR_SKY)

            # Draw background decorations (pixel art style)
            self._draw_background_decorations()

            # Draw ground
            ground_y = VIRTUAL_HEIGHT - 20
            pygame.draw.rect(
                self.virtual_surface,
                COLOR_GROUND,
                (0, ground_y, VIRTUAL_WIDTH, 20)
            )

        if self.state == "READY":
            self._draw_ready_screen()

        elif self.state == "RUN":
            self._draw_game_screen()

        elif self.state == "RESULT":
            self._draw_result_screen()

        # Scale virtual surface to screen
        scaled_surface = pygame.transform.scale(
            self.virtual_surface,
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.screen.blit(scaled_surface, (0, 0))

        # Draw camera preview on top (in screen space, not virtual)
        if self.show_camera_preview and self.camera_frame is not None:
            self._draw_camera_preview()

        pygame.display.flip()

    def _draw_aiming_reticle(self):
        """Draw aiming reticle at aiming position."""
        if not self.aiming_position:
            return

        # Convert normalized coordinates (0-1000) to virtual coordinates
        x, y = self.aiming_position
        virtual_x = (x / 1000.0) * VIRTUAL_WIDTH
        virtual_y = (y / 1000.0) * VIRTUAL_HEIGHT

        # Draw crosshair
        reticle_size = 12
        line_thickness = 2

        # Outer circle (pulsing effect)
        pulse_time = time.time() * 3  # Pulse speed
        pulse_offset = int(3 * (0.5 + 0.5 * np.sin(pulse_time)))
        outer_radius = 18 + pulse_offset

        # Draw outer circle (yellow)
        pygame.draw.circle(self.virtual_surface, COLOR_YELLOW, (int(virtual_x), int(virtual_y)), outer_radius, 3)

        # Draw inner crosshair (white)
        # Horizontal line
        pygame.draw.line(
            self.virtual_surface,
            COLOR_WHITE,
            (int(virtual_x - reticle_size), int(virtual_y)),
            (int(virtual_x + reticle_size), int(virtual_y)),
            line_thickness
        )
        # Vertical line
        pygame.draw.line(
            self.virtual_surface,
            COLOR_WHITE,
            (int(virtual_x), int(virtual_y - reticle_size)),
            (int(virtual_x), int(virtual_y + reticle_size)),
            line_thickness
        )

        # Draw center dot (filled circle, larger and more visible)
        pygame.draw.circle(self.virtual_surface, COLOR_RED, (int(virtual_x), int(virtual_y)), 4)
        # Add white outline to make it pop
        pygame.draw.circle(self.virtual_surface, COLOR_WHITE, (int(virtual_x), int(virtual_y)), 4, 1)

    def _draw_background_decorations(self):
        """Draw simple background decorations matching reference image."""
        ground_y = VIRTUAL_HEIGHT - 20

        # Draw simple clouds scattered in the sky
        cloud_color = (255, 255, 255)
        cloud_positions = [
            (50, 25), (120, 30), (200, 20), (280, 35),
            (350, 25), (420, 30)
        ]
        for cx, cy in cloud_positions:
            self._draw_simple_cloud(cx, cy, cloud_color)

        # Draw trees on both sides - simple forest look
        # Left side trees
        tree_positions_left = [30, 60, 90]
        for tree_x in tree_positions_left:
            self._draw_simple_tree(tree_x, ground_y)

        # Right side trees
        tree_positions_right = [390, 420, 450]
        for tree_x in tree_positions_right:
            self._draw_simple_tree(tree_x, ground_y)

        # Simple grass on ground
        grass_color = (34, 139, 34)
        for i in range(15):
            x = 30 + i * 30
            self._draw_simple_grass(x, ground_y, grass_color)

    def _draw_simple_cloud(self, x: int, y: int, color: Tuple[int, int, int]):
        """Draw a simple cloud."""
        # Simple cloud made of circles
        pygame.draw.circle(self.virtual_surface, color, (x, y), 6)
        pygame.draw.circle(self.virtual_surface, color, (x + 8, y), 7)
        pygame.draw.circle(self.virtual_surface, color, (x + 16, y), 6)
        pygame.draw.circle(self.virtual_surface, color, (x + 8, y - 3), 5)

    def _draw_simple_tree(self, x: int, ground_y: int):
        """Draw a simple tree."""
        # Tree trunk
        trunk_color = (101, 67, 33)
        pygame.draw.rect(
            self.virtual_surface,
            trunk_color,
            (x - 3, ground_y - 15, 6, 15)
        )

        # Tree foliage (simple circle)
        foliage_color = (34, 139, 34)
        pygame.draw.circle(self.virtual_surface, foliage_color, (x, ground_y - 20), 10)

    def _draw_simple_grass(self, x: int, y: int, color: Tuple[int, int, int]):
        """Draw simple grass blades."""
        # 2 simple grass blades
        for i in range(2):
            offset_x = i * 4 - 2
            pygame.draw.line(
                self.virtual_surface,
                color,
                (x + offset_x, y),
                (x + offset_x, y - 4),
                1
            )

    def _draw_text_with_shadow(self, font, text: str, color: Tuple[int, int, int],
                               center_pos: Tuple[int, int], shadow_offset: int = 3):
        """Draw text with shadow effect for better readability."""
        # Draw thicker shadow for better contrast (multiple layers)
        for offset in [(shadow_offset, shadow_offset), (shadow_offset+1, shadow_offset+1)]:
            shadow_surface = font.render(text, True, COLOR_BLACK)
            shadow_rect = shadow_surface.get_rect(center=(center_pos[0] + offset[0], center_pos[1] + offset[1]))
            self.virtual_surface.blit(shadow_surface, shadow_rect)

        # Draw main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center_pos)
        self.virtual_surface.blit(text_surface, text_rect)

    def _draw_text_with_border(self, font, text: str, color: Tuple[int, int, int],
                               center_pos: Tuple[int, int], border_color: Tuple[int, int, int] = COLOR_WHITE):
        """Draw text with outline border for pixel art style."""
        # Draw border (8 directions)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                border_surface = font.render(text, True, border_color)
                border_rect = border_surface.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
                self.virtual_surface.blit(border_surface, border_rect)

        # Draw main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center_pos)
        self.virtual_surface.blit(text_surface, text_rect)

    def _draw_camera_preview(self):
        """Draw camera preview in top-right corner."""
        if self.camera_frame is None:
            return

        # Define preview size (in screen pixels) - large size for better visibility
        preview_width = 512  # Increased from 384
        preview_height = 288  # 16:9 aspect ratio (increased from 216)

        # Resize camera frame
        frame_resized = cv2.resize(self.camera_frame, (preview_width, preview_height))

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        # Convert to pygame surface
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))

        # Position in top-right corner with margin
        margin = 10
        x = SCREEN_WIDTH - preview_width - margin
        y = margin

        # Draw border
        border_rect = pygame.Rect(x - 2, y - 2, preview_width + 4, preview_height + 4)
        pygame.draw.rect(self.screen, COLOR_WHITE, border_rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, border_rect, 2)

        # Draw camera frame
        self.screen.blit(frame_surface, (x, y))

    def _draw_ready_screen(self):
        """Draw READY state screen."""
        # Title with border effect (pixel art style)
        self._draw_text_with_border(
            self.font_big,
            "BALLOON SHOOTER",
            COLOR_TEXT_MAIN,
            (VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 30)
        )

        # Instructions with shadow
        self._draw_text_with_shadow(
            self.font_small,
            "Point gun to aim & shoot!",
            COLOR_TEXT_SECONDARY,
            (VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 10)
        )

        # Start text with shadow (pulsing effect)
        pulse_time = time.time() * 2
        pulse_alpha = 0.5 + 0.5 * np.sin(pulse_time)
        pulse_color = (
            int(COLOR_TEXT_HIGHLIGHT[0] * pulse_alpha + COLOR_YELLOW[0] * (1 - pulse_alpha)),
            int(COLOR_TEXT_HIGHLIGHT[1] * pulse_alpha + COLOR_YELLOW[1] * (1 - pulse_alpha)),
            int(COLOR_TEXT_HIGHLIGHT[2] * pulse_alpha + COLOR_YELLOW[2] * (1 - pulse_alpha))
        )
        self._draw_text_with_shadow(
            self.font_small,
            "Press SPACE to start",
            pulse_color,
            (VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 30)
        )

    def _draw_game_screen(self):
        """Draw RUN state screen."""
        # Draw balloons
        for balloon in self.balloons:
            balloon.draw(self.virtual_surface)

        # Draw shoot effects
        for effect in self.shoot_effects:
            effect.draw(self.virtual_surface)

        # Draw aiming reticle if aiming
        if self.is_aiming and self.aiming_position:
            self._draw_aiming_reticle()

        # Draw UI - simple text with shadows (no boxes)
        current_time = time.time()
        elapsed_time = current_time - self.game_start_time
        remaining_time = max(0, GAME_DURATION - elapsed_time)

        # Score (top left) with thick shadow for readability
        score_text = f"SCORE: {self.score}"
        # Double shadow for better contrast
        shadow = self.font.render(score_text, True, COLOR_BLACK)
        self.virtual_surface.blit(shadow, (12, 12))
        self.virtual_surface.blit(shadow, (13, 13))
        text = self.font.render(score_text, True, COLOR_TEXT_MAIN)
        self.virtual_surface.blit(text, (10, 10))

        # Balloons popped (below score) with thick shadow
        popped_text = f"POPPED: {self.balloons_popped}"
        shadow = self.font.render(popped_text, True, COLOR_BLACK)
        self.virtual_surface.blit(shadow, (12, 32))
        self.virtual_surface.blit(shadow, (13, 33))
        text = self.font.render(popped_text, True, COLOR_TEXT_SECONDARY)
        self.virtual_surface.blit(text, (10, 30))

        # Time (below popped) with thick shadow
        time_text = f"TIME: {int(remaining_time)}s"
        shadow = self.font.render(time_text, True, COLOR_BLACK)
        self.virtual_surface.blit(shadow, (12, 52))
        self.virtual_surface.blit(shadow, (13, 53))
        text = self.font.render(time_text, True, COLOR_TEXT_HIGHLIGHT)
        self.virtual_surface.blit(text, (10, 50))

    def _draw_result_screen(self):
        """Draw RESULT state screen."""
        # Draw decorative stars scattered around (like in reference image)
        star_positions = [
            (80, 40), (150, 35), (330, 45), (400, 38),
            (70, 120), (410, 125), (240, 30), (200, 140)
        ]
        for star_x, star_y in star_positions:
            self._draw_star(star_x, star_y, 6, COLOR_YELLOW)

        # Big title "YOU WIN!" with border (pixel art style)
        self._draw_text_with_border(
            self.font_big,
            "YOU WIN!",
            COLOR_YELLOW,
            (VIRTUAL_WIDTH // 2, 60),
            border_color=COLOR_TEXT_MAIN
        )

        # Score with shadow - simple and clean
        self._draw_text_with_shadow(
            self.font,
            f"SCORE: {self.score}",
            COLOR_TEXT_MAIN,
            (VIRTUAL_WIDTH // 2, 100)
        )

        # Balloons popped with shadow
        self._draw_text_with_shadow(
            self.font,
            f"POPPED: {self.balloons_popped}",
            COLOR_TEXT_SECONDARY,
            (VIRTUAL_WIDTH // 2, 120)
        )

        # Time tickets (in seconds, can be negative)
        tickets_seconds = self.calculate_time_tickets()

        # Format time display - always show minutes and seconds
        if tickets_seconds < 0:
            # Negative time - show in RED
            abs_seconds = abs(tickets_seconds)
            minutes = abs_seconds // 60
            seconds = abs_seconds % 60

            if minutes > 0:
                ticket_text_str = f"TICKETS: -{minutes}:{seconds:02d}"
            else:
                ticket_text_str = f"TICKETS: -{seconds}s"

            self._draw_text_with_border(
                self.font_big,
                ticket_text_str,
                COLOR_RED,
                (VIRTUAL_WIDTH // 2, 155),
                border_color=COLOR_BLACK
            )
        else:
            # Positive time - show in bright pink with border!
            minutes = tickets_seconds // 60
            seconds = tickets_seconds % 60

            if minutes > 0:
                ticket_text_str = f"TICKETS: +{minutes}:{seconds:02d}"
            else:
                ticket_text_str = f"TICKETS: +{seconds}s"

            self._draw_text_with_border(
                self.font_big,
                ticket_text_str,
                COLOR_TEXT_HIGHLIGHT,
                (VIRTUAL_WIDTH // 2, 155),
                border_color=COLOR_BLACK
            )

        # Restart instruction with shadow
        self._draw_text_with_shadow(
            self.font_small,
            "R:Restart  S:Save  Q:Quit",
            COLOR_TEXT_SECONDARY,
            (VIRTUAL_WIDTH // 2, 185)
        )

    def _draw_star(self, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Draw a simple pixel art star."""
        # 5-pointed star using simple lines
        points = []
        for i in range(5):
            angle = (i * 4 * 3.14159 / 5) - (3.14159 / 2)
            px = x + size * np.cos(angle)
            py = y + size * np.sin(angle)
            points.append((px, py))

        # Draw star as polygon
        pygame.draw.polygon(self.virtual_surface, color, points)
        # Draw outline
        pygame.draw.polygon(self.virtual_surface, COLOR_WHITE, points, 1)

    def start_game(self):
        """Start the game."""
        self.state = "RUN"
        self.score = 0
        self.balloons_popped = 0
        self.game_start_time = time.time()
        self.last_balloon_spawn = time.time()
        self.balloons.clear()
        self.shoot_effects.clear()

    def save_result_screenshot(self) -> str:
        """Save result screenshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/result_{timestamp}.png"

        pygame.image.save(self.screen, filename)
        return filename

    def handle_event(self, event) -> Optional[str]:
        """
        Handle pygame event.

        Returns:
            Command string if any action should be taken (e.g., 'shoot', 'start')
        """
        if event.type == pygame.QUIT:
            self.running = False
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.running = False
                return None

            if self.state == "READY":
                if event.key == pygame.K_SPACE:
                    return "start"

            elif self.state == "RUN":
                if event.key == pygame.K_m:
                    # Manual shoot (for testing without gesture)
                    return "manual_shoot"

            elif self.state == "RESULT":
                if event.key == pygame.K_r:
                    self.state = "READY"
                    return None
                elif event.key == pygame.K_s:
                    return "save_screenshot"

        return None

    def run_frame(self, dt: float):
        """Run one frame of the game."""
        self.update(dt)
        self.draw()

    def quit(self):
        """Cleanup and quit."""
        pygame.quit()
