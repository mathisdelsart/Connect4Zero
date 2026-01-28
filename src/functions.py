import numpy as np

# =============================================================================
# Board Constants
# =============================================================================
BOARD_ROWS = 6
BOARD_COLS = 7
WINNING_LENGTH = 4

# =============================================================================
# Board Operations
# =============================================================================

def drop_token(board, column, player):
    """
    Drop a token in the specified column for the given player.
    Returns a new board with the token placed at the lowest available row.
    """
    new_board = np.copy(board)
    for row in range(BOARD_ROWS - 1, -1, -1):
        if new_board[row][column] == 0:
            new_board[row][column] = player
            return new_board
    return new_board


def get_valid_moves(board):
    """
    Get all valid moves as a list of [row, column] pairs.
    A move is valid if the column is not full.
    """
    valid_moves = []
    for col in range(BOARD_COLS):
        if board[0][col] == 0:
            for row in range(BOARD_ROWS - 1, -1, -1):
                if board[row][col] == 0:
                    valid_moves.append([row, col])
                    break
    return valid_moves


def get_available_columns(board):
    """Get list of columns that are not full."""
    return [col for col in range(BOARD_COLS) if board[0][col] == 0]


def is_board_empty(board):
    """Check if the board is empty (first move of the game)."""
    return np.sum(board) == 0


def get_opponent(player):
    """Return the opponent's player number (1 -> 2, 2 -> 1)."""
    return 3 - player


# =============================================================================
# Win Detection
# =============================================================================

def check_win(board, column, player):
    """
    Check if the last move in the given column results in a win.
    Checks horizontal, vertical, and both diagonal directions.
    """
    # Find the row where the token was placed
    row = -1
    for r in range(BOARD_ROWS):
        if board[r][column] == player:
            row = r
            break

    if row == -1:
        return False

    # Direction vectors: (row_delta, col_delta)
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal (down-right)
        (1, -1)   # Diagonal (down-left)
    ]

    for row_delta, col_delta in directions:
        count = 1

        # Count in positive direction
        r, c = row + row_delta, column + col_delta
        while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and board[r][c] == player:
            count += 1
            r += row_delta
            c += col_delta

        # Count in negative direction
        r, c = row - row_delta, column - col_delta
        while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and board[r][c] == player:
            count += 1
            r -= row_delta
            c -= col_delta

        if count >= WINNING_LENGTH:
            return True

    return False


# =============================================================================
# Minimax Algorithm
# =============================================================================

def minimax(node, depth, maximizing_player):
    """
    Minimax algorithm to find the best move.

    Args:
        node: Current game tree node
        depth: Remaining search depth
        maximizing_player: The player trying to maximize the score

    Returns:
        The best score achievable from this position
    """
    # Base case: reached maximum depth
    if depth == 0:
        if node.value == 0:
            node.value += evaluate_position(
                node.player,
                get_opponent(node.player),
                node.board,
                node.move,
                maximizing_player,
                opponent_weight=5,
                player_weight=10
            )
        return node.value

    # No children means terminal node (win/loss/draw)
    if not node.children:
        return node.value

    if node.player != maximizing_player:
        # Maximizing player's turn
        max_score = -np.inf
        for child in node.children:
            score = minimax(child, depth - 1, maximizing_player)
            max_score = max(max_score, score)
        node.value = max_score
        return max_score
    else:
        # Minimizing player's turn
        min_score = np.inf
        for child in node.children:
            score = minimax(child, depth - 1, maximizing_player)
            min_score = min(min_score, score)
        node.value = min_score
        return min_score


# =============================================================================
# Position Evaluation
# =============================================================================

WIN_SCORE = 1_000_000


def evaluate_terminal_state(board, player, maximizing_player, column):
    """
    Check if the position is a winning state.

    Returns:
        Tuple of (is_terminal, score)
        - is_terminal: True if someone has won
        - score: Positive for maximizing player win, negative for opponent win
    """
    if check_win(board, column, player):
        if player == maximizing_player:
            return (True, WIN_SCORE)
        else:
            return (True, -WIN_SCORE)
    return (False, 0)


def count_consecutive_tokens(board, row, col, row_delta, col_delta, target_player):
    """Count consecutive tokens in a direction for threat evaluation."""
    count = 0
    for i in range(3):
        r, c = row + row_delta * i, col + col_delta * i
        if 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS:
            if board[r][c] == target_player:
                count += 1
            else:
                break
        else:
            break
    return count


def evaluate_threats(board, move, target_player, weight):
    """
    Evaluate threats around a move position.
    Higher scores for positions that create or block threats.
    """
    row, col = move[0], move[1]
    total_score = 0

    # Check all 4 directions (both ways)
    directions = [
        (0, 1), (0, -1),   # Horizontal
        (1, 0), (-1, 0),   # Vertical
        (1, 1), (-1, -1),  # Diagonal \
        (1, -1), (-1, 1)   # Diagonal /
    ]

    for row_delta, col_delta in directions:
        count = count_consecutive_tokens(board, row, col, row_delta, col_delta, target_player)
        total_score += count * weight

    return total_score


# Position value table - center positions are more valuable
POSITION_VALUES = [
    [3,  4,  5,  7,  5,  4,  3],
    [4,  6,  8,  10, 8,  6,  4],
    [5,  8,  11, 13, 11, 8,  5],
    [5,  8,  11, 13, 11, 8,  5],
    [4,  6,  8,  10, 8,  6,  4],
    [3,  4,  5,  7,  5,  4,  3]
]
POSITION_WEIGHT = 80


def evaluate_board_position(move):
    """
    Evaluate the strategic value of a board position.
    Center positions are worth more.
    """
    row, col = move[0], move[1]
    return POSITION_VALUES[row][col] * POSITION_WEIGHT


def evaluate_position(player, opponent, board, move, maximizing_player, opponent_weight, player_weight):
    """
    Comprehensive position evaluation combining:
    - Threat evaluation for both players
    - Positional value of the move
    """
    score = (
        evaluate_threats(board, move, opponent, opponent_weight) +
        evaluate_threats(board, move, player, player_weight) +
        evaluate_board_position(move)
    )

    if player != maximizing_player:
        return -score
    return score
