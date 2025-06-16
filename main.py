from chess_game import ChessGame, print_bitboard, print_bit
from chess_render import ChessRender
from chess_bot import ChessBot

board = ChessGame()
bot = ChessBot(board)
render = ChessRender(board, bot, bot)

render.update()