import random
import numpy as np
from src.functions import drop_token, check_win, get_opponent, get_available_columns


class EasyAI:
    """
    Easy difficulty AI opponent.

    Strategy:
    - Plays winning moves immediately
    - Blocks opponent's winning moves
    - Otherwise plays randomly
    """

    def get_move(self, board, player):
        """
        Determine the best column to play.

        Args:
            board: Current game board state
            player: Current player number (1 or 2)

        Returns:
            Column number to play
        """
        board_copy = np.copy(board)
        available_columns = get_available_columns(board_copy)
        opponent = get_opponent(player)

        for col in available_columns:
            # Check if this move wins the game
            attack_board = drop_token(board_copy, col, player)
            if check_win(attack_board, col, player):
                return col

            # Check if opponent would win here (must block)
            defense_board = drop_token(board_copy, col, opponent)
            if check_win(defense_board, col, opponent):
                return col

        # No immediate win or block needed - play randomly
        return random.choice(available_columns)
