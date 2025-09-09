from chess_game import ChessGame
from chess_render import ChessRender
from chess_bot import ChessBot, ChessParams

board = ChessGame()
bot_params = ChessParams()
bot = ChessBot(bot_params)
render = ChessRender(board, opponent2=bot, chess_evaluation=bot)
render.update()