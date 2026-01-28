from src.functions import get_valid_moves


class HumanPlayer:
    """Human player that gets moves via console input."""

    def get_move(self, board, player):
        """
        Prompt the user to enter a column number.
        Validates that the column is not full.
        """
        valid_moves = get_valid_moves(board)
        valid_columns = [move[1] for move in valid_moves]

        while True:
            try:
                column = int(input("Enter column number (0-6): "))
                if column in valid_columns:
                    return column
                print("This column is full! Choose another.")
            except ValueError:
                print("Please enter a valid number.")
