from chess_game import ChessGame, print_bit
from chess_render import ChessRender
from chess_bot import ChessBot

board = ChessGame()
# bot = ChessBot(board)
render = ChessRender(board)
render.update()