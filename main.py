from chess_game import ChessGame, print_bitboard, print_bit
from chess_render import ChessRender
from chess_bot import ChessBot

board = ChessGame()
bot = ChessBot(board)
white_move = bot.make_decision(bot.chess_engine.bitboards)
print(white_move)
bot.chess_engine.move(white_move)
black_move = bot.make_decision(bot.chess_engine.bitboards)
print(black_move)