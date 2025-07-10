from chess_game import ChessGame
from chess_bot import ChessBot, ChessParams

board = ChessGame()
bot1_params = ChessParams(king_safety=0.2, pawn_center=0.5, square_attacked=0.2)
bot2_params = ChessParams()
bot1 = ChessBot(bot1_params)
bot2 = ChessBot(bot2_params)

while board.winner == -1:
    to_play = None
    if board.player_turn == board.WHITE:
        to_play = bot1.make_decision(board)
    else:
        to_play = bot2.make_decision(board)
    board.play(to_play)
if board.winner == 0:
    print("White won !")
elif board.winner == 1:
    print("Black won !")
elif board.winner == 2:
    print("Draw !")