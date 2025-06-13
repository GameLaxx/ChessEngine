from chess_game import ChessGame, print_bitboard, print_bit
from chess_render import ChessRender
from chess_bot import ChessBot

board = ChessGame()
render = ChessRender(board)
render.update()
# bot = ChessBot(board)

# bitboards = [
#             [0 for _ in range(6)],
#             [0 for _ in range(6)]
#         ]
# board.set_piece(0, 4, 36, bitboards)

# bot.make_decision(bitboards)