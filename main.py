from chess_game import ChessGame
from chess_render import ChessRender
from chess_bot import ChessBot, ChessParams

board = ChessGame()
bot1_params = ChessParams()
bot2_params = ChessParams().random()
bot1 = ChessBot(bot1_params)
bot2 = ChessBot(bot2_params)
render = ChessRender(board, opponent2=bot2)
render.update()