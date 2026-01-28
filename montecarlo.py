"""
Monte Carlo simulation to compare AI performance.

Runs multiple tournaments between Easy AI and Hard AI
to measure win rates and draw rates.
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from multiprocessing import Pool, cpu_count

from src.functions import get_valid_moves, check_win, BOARD_ROWS, BOARD_COLS
from src.players.easy_ai import EasyAI
from src.players.hard_ai import HardAI


def simulate_game(args):
    """
    Simulate a single game between two AIs.

    Returns:
        1 if player 1 wins, 2 if player 2 wins, 0 if draw
    """
    player1, player2 = args
    board = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]
    current_player = 1
    move_count = 0

    while move_count < 42:
        # Get move from current player's AI
        if current_player == 1:
            column = player1.get_move(board, current_player)
        else:
            column = player2.get_move(board, current_player)

        # Find the row to place the token
        valid_moves = get_valid_moves(board)
        for move in valid_moves:
            if column == move[1]:
                row = move[0]
                board[row][column] = current_player
                break

        # Check for win
        if check_win(board, column, current_player):
            return current_player

        move_count += 1
        current_player = 3 - current_player

    # Draw
    return 0


if __name__ == '__main__':
    start_time = time.time()

    NUM_TRIALS = 10
    GAME_COUNTS = [10, 100, 1000, 10000]

    player1_wins = np.zeros((NUM_TRIALS, len(GAME_COUNTS)))
    draws = np.zeros((NUM_TRIALS, len(GAME_COUNTS)))

    search_depth = 4

    print("Starting Monte Carlo simulation...")
    print(f"Player 1: HardAI (depth={search_depth})")
    print(f"Player 2: EasyAI")
    print()

    for i, num_games in enumerate(GAME_COUNTS):
        print(f"Running {num_games} games x {NUM_TRIALS} trials...")

        for trial in range(NUM_TRIALS):
            # Create fresh AI instances for each trial
            hard_ai = HardAI(depth=search_depth)
            easy_ai = EasyAI()

            # Run games sequentially (multiprocessing has issues with pygame)
            trial_results = []
            for _ in range(num_games):
                result = simulate_game((hard_ai, easy_ai))
                trial_results.append(result)

            player1_wins[trial][i] = 100 * (trial_results.count(1) / num_games)
            draws[trial][i] = 100 * (trial_results.count(0) / num_games)

        print(f"  Completed: P1 wins={np.mean(player1_wins[:, i]):.1f}%, Draws={np.mean(draws[:, i]):.1f}%")

    print()
    print(f"Player 1 wins: {player1_wins}")
    print(f"Draws: {draws}")

    wins_mean = np.mean(player1_wins, axis=0)
    draws_mean = np.mean(draws, axis=0)

    print()
    print(f"Mean win rate: {wins_mean}")
    print(f"Mean draw rate: {draws_mean}")

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.2f}s")

    # Plot results
    plt.figure(figsize=(10, 6))
    for i, num_games in enumerate(GAME_COUNTS):
        plt.scatter(np.full(NUM_TRIALS, num_games), player1_wins[:, i], c='blue', s=10, alpha=0.5)
        plt.scatter(np.full(NUM_TRIALS, num_games), draws[:, i], c='red', s=10, alpha=0.5)
        plt.scatter(num_games, wins_mean[i], c='blue', marker='x', s=100)
        plt.scatter(num_games, draws_mean[i], c='red', marker='x', s=100)

    plt.legend(['Player 1 wins', 'Draws', 'Mean win rate', 'Mean draw rate'], loc='best')
    plt.xlabel('Number of games')
    plt.ylabel('Probability (%)')
    plt.title('HardAI vs EasyAI Performance')
    plt.xscale('log')
    plt.ylim((-10, 110))
    plt.grid(True, alpha=0.3)
    plt.savefig('ai_comparison_results.pdf')
    print("Graph saved to ai_comparison_results.pdf")
    plt.show()
