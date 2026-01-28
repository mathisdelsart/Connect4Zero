import pygame
import os
from src.functions import get_valid_moves, check_win
from src.players.hard_ai import HardAI
from src.players.easy_ai import EasyAI
from src.configs import (
    ROWS, COLUMNS, CELL_SIZE, WIDTH, HEIGHT,
    BACKGROUND_SURFACE, HEADER_COLOR,
    BOARD_PRIMARY, BOARD_HIGHLIGHT, BOARD_SHADOW,
    TOKEN_COLORS, TOKEN_SHADOW, TOKEN_HIGHLIGHT,
    MENU_TITLE_COLOR, MENU_TEXT_COLOR, MENU_SUBTITLE_COLOR,
    MENU_ACCENT_COLOR, MENU_BOX_BG,
    FONT_TITLE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_TINY,
    MENU_TITLE, MENU_SUBTITLE, MENU_OPTIONS, MENU_FOOTER,
    END_GAME_MESSAGES, END_MENU_INSTRUCTIONS,
    TITLE_SURFACE, TITLE_RECT,
    SOUND_MANAGER
)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect 4")

# Set window icon
ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "connect4.png")
if os.path.exists(ICON_PATH):
    icon = pygame.image.load(ICON_PATH)
    # Scale to 32x32 for better compatibility
    icon = pygame.transform.scale(icon, (32, 32))
    pygame.display.set_icon(icon)


class Game:
    """Main game class handling game loop, rendering, and state management."""

    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.board = [[0] * COLUMNS for _ in range(ROWS)]
        self.current_player = 1
        self.ai_opponent = None
        self.is_game_over = False
        self.show_menu = True
        self.show_end_screen = False
        self.game_result = None  # True=win, False=lose, None=draw
        self.move_count = 0

    def draw_background(self):
        """Draw the gradient background."""
        screen.blit(BACKGROUND_SURFACE, (0, 0))

    def draw_header(self):
        """Draw the header area with title."""
        pygame.draw.rect(screen, HEADER_COLOR, (0, 0, WIDTH, CELL_SIZE))
        screen.blit(TITLE_SURFACE, TITLE_RECT)

    def draw_menu_box(self, x, y, width, height, alpha=230):
        """Draw a semi-transparent box for menu elements."""
        box_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (*MENU_BOX_BG, alpha), (0, 0, width, height), border_radius=12)
        pygame.draw.rect(box_surface, MENU_ACCENT_COLOR, (0, 0, width, height), 2, border_radius=12)
        screen.blit(box_surface, (x, y))

    def draw_board(self):
        """Render the game board with tokens."""
        for row in range(ROWS):
            for col in range(COLUMNS):
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = (row + 1) * CELL_SIZE + CELL_SIZE // 2

                # Draw board cell
                pygame.draw.rect(
                    screen, BOARD_PRIMARY,
                    (col * CELL_SIZE, (row + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )

                # Draw cell hole with 3D effect
                pygame.draw.circle(screen, BOARD_HIGHLIGHT, (x - 1.2, y - 1.2), CELL_SIZE // 2 - 2)
                pygame.draw.circle(screen, BOARD_SHADOW, (x + 1.2, y + 1.2), CELL_SIZE // 2 - 2)
                pygame.draw.circle(screen, BOARD_PRIMARY, (x, y), CELL_SIZE // 2 - 2.5)

                # Draw token
                token_value = self.board[row][col]
                pygame.draw.circle(screen, TOKEN_COLORS[token_value], (x, y), CELL_SIZE // 2 - 5)

                # Add 3D shading to tokens (only for player tokens, not empty)
                if token_value in TOKEN_SHADOW:
                    pygame.draw.circle(screen, TOKEN_SHADOW[token_value], (x - 2, y - 2), CELL_SIZE // 2 - 10)
                    pygame.draw.circle(screen, TOKEN_HIGHLIGHT[token_value], (x + 2, y + 2), CELL_SIZE // 2 - 10)
                    pygame.draw.circle(screen, TOKEN_COLORS[token_value], (x, y), CELL_SIZE // 2 - 10.5)

    def draw_main_menu(self):
        """Render the main menu screen."""
        self.draw_background()

        # Draw menu container box
        box_width, box_height = 420, 380
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2 - 10
        self.draw_menu_box(box_x, box_y, box_width, box_height)

        # Draw title
        title_surface = FONT_TITLE.render(MENU_TITLE, True, MENU_TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, box_y + 55))
        screen.blit(title_surface, title_rect)

        # Draw subtitle
        subtitle_surface = FONT_SMALL.render(MENU_SUBTITLE, True, MENU_SUBTITLE_COLOR)
        subtitle_rect = subtitle_surface.get_rect(center=(WIDTH // 2, box_y + 105))
        screen.blit(subtitle_surface, subtitle_rect)

        # Draw options
        option_y = box_y + 155
        for key, name, description in MENU_OPTIONS:
            # Option header
            option_text = f"[{key}]  {name}"
            option_surface = FONT_MEDIUM.render(option_text, True, MENU_TEXT_COLOR)
            option_rect = option_surface.get_rect(center=(WIDTH // 2, option_y))
            screen.blit(option_surface, option_rect)

            # Option description (smaller font)
            desc_surface = FONT_TINY.render(description, True, MENU_SUBTITLE_COLOR)
            desc_rect = desc_surface.get_rect(center=(WIDTH // 2, option_y + 28))
            screen.blit(desc_surface, desc_rect)

            option_y += 70

        # Draw footer
        footer_surface = FONT_TINY.render(MENU_FOOTER, True, MENU_SUBTITLE_COLOR)
        footer_rect = footer_surface.get_rect(center=(WIDTH // 2, box_y + box_height - 30))
        screen.blit(footer_surface, footer_rect)

    def draw_end_screen(self):
        """Render the end game screen with board visible behind."""
        # First draw the game state (board + header)
        self.draw_background()
        self.draw_board()
        self.draw_header()

        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Draw result box
        box_width, box_height = 380, 250
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2
        self.draw_menu_box(box_x, box_y, box_width, box_height)

        # Draw result message
        result_text = END_GAME_MESSAGES.get(self.game_result, "Game Over")
        if self.game_result is True:
            result_color = (100, 255, 100)  # Green for victory
        elif self.game_result is False:
            result_color = (255, 100, 100)  # Red for defeat
        else:
            result_color = MENU_TEXT_COLOR  # White for draw

        result_surface = FONT_LARGE.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(WIDTH // 2, box_y + 70))
        screen.blit(result_surface, result_rect)

        # Draw instructions
        instruction_y = box_y + 140
        for instruction in END_MENU_INSTRUCTIONS:
            inst_surface = FONT_SMALL.render(instruction, True, MENU_TEXT_COLOR)
            inst_rect = inst_surface.get_rect(center=(WIDTH // 2, instruction_y))
            screen.blit(inst_surface, inst_rect)
            instruction_y += 40

    def handle_player_move(self, column):
        """Process a player's move."""
        valid_moves = get_valid_moves(self.board)
        for move in valid_moves:
            if column == move[1]:
                row = move[0]
                self.board[row][column] = self.current_player
                SOUND_MANAGER.play("drop")

                self.move_count += 1

                if check_win(self.board, column, self.current_player):
                    self.game_result = True
                    # Show the winning move first
                    self.draw_background()
                    self.draw_board()
                    self.draw_header()
                    pygame.display.update()
                    # Play sound and wait for it to play
                    SOUND_MANAGER.play("win")
                    pygame.time.delay(1200)
                    self.show_end_screen = True
                    return True

                self.current_player = 3 - self.current_player
                return True
        return False

    def handle_ai_move(self):
        """Process the AI's move."""
        column = self.ai_opponent.get_move(self.board, self.current_player)
        valid_moves = get_valid_moves(self.board)

        for move in valid_moves:
            if column == move[1]:
                row = move[0]
                self.board[row][column] = self.current_player
                SOUND_MANAGER.play("drop")

                self.move_count += 1

                if check_win(self.board, column, self.current_player):
                    self.game_result = False
                    # Show the losing move first
                    self.draw_background()
                    self.draw_board()
                    self.draw_header()
                    pygame.display.update()
                    # Play sound and wait for it to play
                    SOUND_MANAGER.play("lose")
                    pygame.time.delay(1200)
                    self.show_end_screen = True
                    return

                self.current_player = 3 - self.current_player
                return

    def run(self):
        """Main game loop."""
        while not self.is_game_over:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_game_over = True
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_game_over = True
                        pygame.quit()
                        return

                    if self.show_menu or self.show_end_screen:
                        if event.key == pygame.K_1:
                            SOUND_MANAGER.play("select")
                            if self.show_menu:
                                self.show_menu = False
                                self.ai_opponent = EasyAI()
                            elif self.show_end_screen:
                                self.reset_game()
                        elif event.key == pygame.K_2:
                            SOUND_MANAGER.play("select")
                            if self.show_menu:
                                self.show_menu = False
                                self.ai_opponent = HardAI(depth=4)
                            elif self.show_end_screen:
                                self.reset_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.show_menu and not self.show_end_screen and self.current_player == 1:
                        column = event.pos[0] // CELL_SIZE
                        if self.handle_player_move(column):
                            # Redraw after player move
                            self.draw_background()
                            self.draw_board()
                            self.draw_header()
                            pygame.display.update()
                            pygame.time.delay(400)

            # Render based on game state
            if self.show_menu:
                self.draw_main_menu()
            elif self.show_end_screen:
                self.draw_end_screen()
            else:
                # AI's turn
                if self.current_player == 2:
                    self.handle_ai_move()

                self.draw_background()
                self.draw_board()
                self.draw_header()

                # Check for draw
                if self.move_count == 42:
                    self.game_result = None
                    SOUND_MANAGER.play("draw")
                    pygame.time.delay(1200)
                    self.show_end_screen = True

            pygame.display.update()
