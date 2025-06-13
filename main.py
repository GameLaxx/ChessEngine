from chess_game import ChessGame
from chess_render import ChessRender
from chess_bot import ChessBot

board = ChessGame()
bot = ChessBot(board)

bitboards = [
            [0 for _ in range(6)],
            [0 for _ in range(6)]
        ]
board.set_piece(0, 4, 36, bitboards)

bot.make_decision(bitboards)