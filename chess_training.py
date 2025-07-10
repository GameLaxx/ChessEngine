import random
import multiprocessing
from chess_game import ChessGame
from chess_bot import ChessBot, ChessParams

g_population : list[ChessParams] = []

def play_match(pair : tuple[tuple[int, int], int]) -> tuple[tuple[int, float]]:
    """
    ### Play a match between two sets of parameters.

    Args:
        pair (tuple[tuple[int, int], int]): The two parameters index and the index of the match

    Returns:
        (tuple[tuple[int, float]]) : each set of parameters and its gain (1 for win, 0 for loss, 0.5 for draw)
    """
    global g_population # global population so that the changes made by one worker will remain outside of its memory
    index_parameters_a, index_parameters_b = pair[0]
    bot_a = ChessBot(g_population[index_parameters_a]) # bot a is considered to be the one with white color
    bot_b = ChessBot(g_population[index_parameters_b])
    board = ChessGame()
    try: # this try except is here to counter the issue "1 << (index - 2)"
        while board.winner == -1:
            to_play = bot_a.make_decision(board) if board.player_turn == board.WHITE else bot_b.make_decision(board)
            board.play(to_play)
    except Exception as e:
        print("Match", pair[1], e)
        board.winner = 2
    print("Match", pair[1], "White win" if board.winner == 0 else "Black win" if board.winner == 1 else "Draw")

    if board.winner == 0:
        return (index_parameters_a, 1.0), (index_parameters_b, 0.0)
    elif board.winner == 1:
        return (index_parameters_a, 0.0), (index_parameters_b, 1.0)
    else:
        return (index_parameters_a, 0.5), (index_parameters_b, 0.5)

def evaluate_pop(number_matches : int = 10000, processes : int = 1) -> None:
    """
    ### Evaluate a population by playing matches between two elements of the population.

    Args:
        number_matches (int): The number of matches to be played
        processes (int): The number of sub processes that will be launch

    Returns:
        (None) : the score for each element is stored inside its attributes `score`
    """
    global g_population
    # create the elements that will be used with multiprocessing
    pairs = [(random.sample(range(len(g_population)), 2), i) for i in range(number_matches)] 
    with multiprocessing.Pool(processes=processes) as pool:
        results = pool.map(play_match, pairs)
    # reset every scores
    for p in g_population:
        p.score = 0
    # apply results
    for result in results:
        for player_index, score in result:
            g_population[player_index].score += score

def build_pop(population_size : int) -> list[ChessParams]:
    """
    ### Build the population

    Args:
        population_size (int): The number of element that the population will be made of

    Returns:
        (list[ChessParams]) : The population
    """
    return [ChessParams().random() for _ in range(population_size)]

if __name__ == "__main__":
    generation_number = 2
    population_size = 100
    matches_number = 500
    for gen in range(generation_number):
        print("*-* Generation :", gen)
        g_population += build_pop(population_size - len(g_population)) # build the population to always start with the same length
        evaluate_pop(matches_number)
        g_population.sort(key=lambda x: -x.score)
        print("Top score:", g_population[0].score)
        print("Lowest score:", g_population[-1].score)
        print("Top params:", g_population[0].dict)
        pop = g_population[:len(g_population) // 3] # trim the population to keep only the best