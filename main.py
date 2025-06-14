from chess_game import ChessGame, print_bitboard, print_bit
from chess_render import ChessRender
from chess_bot import ChessBot

board = ChessGame()
bot = ChessBot(board)

bitboards = [
            [0 for _ in range(6)],
            [0 for _ in range(6)]
        ]
board.set_piece(0, 4, 36, bitboards)
occupancy = {0 : 0, 1 : 0, 2 : 0}
board.update_occupancy(bitboards, occupancy)
bot.evaluate(bitboards, occupancy)

# bot.make_decision(bitboards)