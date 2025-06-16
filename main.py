from chess_game import ChessGame, print_bit
from chess_render import ChessRender
from chess_bot import ChessBot

board = ChessGame()
bot = ChessBot(board)

# bot.debug = True
# print(bot.make_decision(board))

render = ChessRender(board, opponent1=bot, opponent2=bot)
render.update()