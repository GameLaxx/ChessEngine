import random
import multiprocessing
from chess_game import ChessGame
from chess_bot import ChessBot, ChessParams

number_gen = 2
len_pop = 100
g_population : list[ChessParams] = []

def play_match(pair):
    global g_population
    param_a, param_b = pair[0]
    try:
        bot_a = ChessBot(g_population[param_a])
        bot_b = ChessBot(g_population[param_b])
    except:
        raise ValueError(param_a, param_b)
    board = ChessGame()
    while board.winner == -1:
        to_play = bot_a.make_decision(board) if board.player_turn == board.WHITE else bot_b.make_decision(board)
        board.play(to_play)

    print("Match", pair[1], "White win" if board.winner == 0 else "Black win" if board.winner == 1 else "Draw")

    if board.winner == 0:
        return (param_a, 1.0), (param_b, 0.0)
    elif board.winner == 1:
        return (param_a, 0.0), (param_b, 1.0)
    else:
        return (param_a, 0.5), (param_b, 0.5)

def evaluate_pop(num_matches=10000):
    global g_population
    pairs = [(random.sample(range(len(g_population)), 2), i) for i in range(num_matches)]

    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(play_match, pairs)

    # Réinitialiser les scores
    for p in g_population:
        p.score = 0

    # Appliquer les résultats
    for result in results:
        for player_index, score in result:
            g_population[player_index].score += score

def build_pop(size):
    return [ChessParams().random() for _ in range(size)]

if __name__ == "__main__":
    for gen in range(number_gen):
        print("Gen", gen)
        g_population += build_pop(len_pop - len(g_population))
        evaluate_pop(500)
        g_population.sort(key=lambda x: -x.score)
        print("Top score:", g_population[0].score)
        print("Lowest score:", g_population[-1].score)
        print("Top params:", g_population[0].dict)
        pop = g_population[:len(g_population) // 3]