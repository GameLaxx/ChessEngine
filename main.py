from chess_game import ChessGame
from chess_render import ChessRender
from chess_bot import ChessBot, ChessParams

board = ChessGame("8/2P5/8/8/5k2/1K6/4p3/8 w -")
bot_params = ChessParams()
bot = ChessBot(bot_params)
render = ChessRender(board, opponent1=bot, opponent2=bot, chess_evaluation=bot, bot_speed=0.5)
render.update()