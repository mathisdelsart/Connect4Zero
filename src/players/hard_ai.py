import numpy as np
from src.functions import (
    get_valid_moves, get_opponent, is_board_empty,
    minimax, evaluate_terminal_state, evaluate_position
)


class GameTreeNode:
    """
    Represents a node in the minimax game tree.

    Each node contains:
    - The board state after a move
    - The player who made the move
    - The move coordinates [row, col]
    - The evaluation value
    - Child nodes representing possible future moves
    """

    def __init__(self, value, board, player, move, depth):
        self.value = value
        self.board = board
        self.player = player
        self.move = move
        self.depth = depth
        self.children = []

    def build_tree(self, player, parent_nodes, boards, maximizing_player):
        """
        Recursively build the game tree from this node.

        Args:
            player: Current player to move
            parent_nodes: List of parent nodes at current level
            boards: List of board states corresponding to parent nodes
            maximizing_player: The player we're optimizing for
        """
        if self.depth == 0:
            return

        child_nodes = []
        child_boards = []
        terminal_nodes = []

        for i, (parent, board) in enumerate(zip(parent_nodes, boards)):
            valid_moves = get_valid_moves(board)

            for move in valid_moves:
                row, col = move[0], move[1]
                new_board = np.copy(board)
                new_board[row][col] = player

                child = GameTreeNode(0, new_board, player, move, self.depth)

                # Check for terminal state (win)
                is_terminal, score = evaluate_terminal_state(
                    child.board, child.player, maximizing_player, col
                )

                if is_terminal:
                    # Multiply by depth to prefer faster wins
                    child.value = score * (self.depth + 1)
                    child.children = []
                    terminal_nodes.append(child)
                else:
                    child_nodes.append(child)
                    child_boards.append(new_board)

                parent.children.append(child)

        self.depth -= 1
        self.build_tree(
            get_opponent(player),
            child_nodes,
            child_boards,
            maximizing_player
        )


class HardAI:
    """
    Hard difficulty AI using the Minimax algorithm.

    Uses a game tree with configurable search depth to find
    the optimal move. Includes position evaluation heuristics
    for non-terminal states.
    """

    def __init__(self, depth=4):
        """
        Initialize the AI with a search depth.

        Args:
            depth: How many moves ahead to search (default: 4)
        """
        self.search_depth = depth

    def find_best_move(self, root_node, depth, maximizing_player):
        """
        Find the best move using the minimax algorithm.

        Args:
            root_node: Root of the game tree
            depth: Search depth
            maximizing_player: Player to optimize for

        Returns:
            Best column to play
        """
        best_score = minimax(root_node, depth, maximizing_player)
        best_children = []

        # Find all moves with the best score
        for child in root_node.children:
            if child.value == best_score:
                best_children.append(child)

        if len(best_children) == 1:
            return best_children[0].move[1]

        # Multiple moves with same score - use position evaluation as tiebreaker
        move_scores = {}
        for child in best_children:
            score = evaluate_position(
                child.player,
                get_opponent(child.player),
                child.board,
                child.move,
                maximizing_player,
                opponent_weight=5,
                player_weight=10
            )
            move_scores[score] = child.move[1]

        best_score = max(move_scores.keys())
        return move_scores[best_score]

    def get_move(self, board, player):
        """
        Determine the best column to play.

        Args:
            board: Current game board state
            player: Current player number

        Returns:
            Best column to play
        """
        board_copy = np.array(board)

        # Opening move: always play center (optimal strategy)
        if is_board_empty(board_copy):
            return len(board[0]) // 2

        # Build game tree and find best move
        root_node = GameTreeNode(
            value=0,
            board=board_copy,
            player=get_opponent(player),
            move=None,
            depth=self.search_depth
        )

        root_node.build_tree(
            player=player,
            parent_nodes=[root_node],
            boards=[board_copy],
            maximizing_player=player
        )

        return self.find_best_move(root_node, self.search_depth, player)
