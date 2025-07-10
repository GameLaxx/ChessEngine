import pygame
from chess_game import ChessGame
from chess_bot import ChessBot
import sys

def getElementSatisfy(list : list[str], elem : str):
    for i, x in enumerate(list):
        if x.startswith(elem):
            return i
    return -1

class ChessRender():
    def __init__(self, board : ChessGame, opponent1 : ChessBot = None, opponent2 : ChessBot = None, bottom = 0, size = 640):
        pygame.init()
        self.board = board
        self.size = size # size of the canvas
        self.square_size = self.size // self.board.size
        self.white_color = (240, 217, 181)
        self.brown_color = (181, 136, 99)
        self.green_color = (100, 180, 100)
        self.pieces = {}
        self.selected_piece = None
        self.changed = True
        self.players = [opponent1, opponent2] # store bot or human player
        PIECE_NAMES = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
        for name in PIECE_NAMES:
            self.pieces[name] = pygame.transform.scale(
                pygame.image.load(f"pieces/{name}.png"), (self.square_size, self.square_size)
            )
        self.win = pygame.display.set_mode((self.size, self.size))
        self.bottom_player = bottom # 0 is for white, 1 is for black
        pygame.display.set_caption("Chess board")

    def draw_board(self, win : pygame.surface.Surface):
        """
        ### Draw the board from the current position

        Args:
            win (pygame.surface.Surface): The surface / canvas to draw on.
        """
        current_board = self.board.to_matrix()
        # draw squares
        for _row in range(self.board.size):
            row = 7 - _row if self.bottom_player else _row
            for col in range(self.board.size):
                color = self.white_color if (row + col) % 2 == 0 else self.brown_color
                pygame.draw.rect(win, color, (col * self.square_size, row * self.square_size, self.square_size, self.square_size))
        if self.selected_piece:
            row_s = 8 - int(self.selected_piece[2]) if self.bottom_player == 0 else int(self.selected_piece[2]) - 1
            col_s = ord(self.selected_piece[1]) - 97
            color = self.green_color
            pygame.draw.rect(win, color, (col_s * self.square_size, row_s * self.square_size, self.square_size, self.square_size))
        # draw pieces
        for _row in range(self.board.size):
            row = 7 - _row if self.bottom_player else _row
            for col in range(self.board.size):
                piece = current_board[_row][col]
                if piece == "--":
                    continue
                win.blit(self.pieces[piece], (col * self.square_size, row * self.square_size))
        if self.selected_piece:
            for move in self.board.get_moves_piece(self.board.str_to_piece(self.selected_piece[0]), self.board.square_str_to_index(self.selected_piece[1:3]), self.board.player_turn):
                if not self.board.is_legal(move, self.board.player_turn):
                    continue
                move = move.split("-")[1]
                row_s = 8 - int(move[2]) if self.bottom_player == 0 else int(move[2]) - 1
                col_s = ord(move[1]) - 97
                pygame.draw.circle(win, color, (col_s * self.square_size + self.square_size // 2, row_s * self.square_size + self.square_size // 2), self.square_size // 8)
        pygame.display.update()
        self.changed = False

    def get_square_clicked(self, pos : tuple[float, float]) -> tuple[int, int]:
        """
        ### Transform a position on the canvas into a row and column index.

        Args:
            pos (tuple[float, float]): x and y coordinates of the click.

        Returns:
            (tuple[int, int]) : The square clicked.
        """
        x, y = pos
        row = 7 - y // self.square_size if self.bottom_player else y // self.square_size
        col = x // self.square_size
        return row, col


    def update(self):
        """
        ### Update the canvas depending on events.

        Click on pieces to show their legal moves.
        Click on the highlighted squares to move the piece.
        Stops when the game ends or an error occurs.
        """
        clock = pygame.time.Clock()
        while self.board.winner == -1:
            clock.tick(60)
            if self.changed: # this avoid unneeded graphic update
                self.draw_board(self.win)
            if self.players[self.board.player_turn] != None: # bot moves instantly
                to_play = self.players[self.board.player_turn].make_decision(self.board)
                self.board.play(to_play)
                self.changed = True
                pygame.time.wait(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.players[self.board.player_turn] == None:
                    current_board = self.board.to_matrix()
                    self.changed = True
                    rc, cc = self.get_square_clicked(pygame.mouse.get_pos())
                    piece = current_board[rc][cc]
                    if self.selected_piece == None:
                        # wrong color
                        if piece[0] == "w" and self.board.player_turn == 1:
                            continue
                        if piece[0] == "b" and self.board.player_turn == 0:
                            continue
                        # no piece clicked
                        if piece == "--":
                            continue
                        self.selected_piece = f"{piece[1]}{chr(cc + 97)}{8 - rc}"
                        continue
                    # change piece
                    if (piece[0] == "w" and self.board.player_turn == 0) or (piece[0] == "b" and self.board.player_turn == 1):
                        self.selected_piece = f"{piece[1]}{chr(cc + 97)}{8 - rc}"
                        continue
                    # try to play the move
                    move_played = f"{self.selected_piece}-{self.selected_piece[0]}{chr(cc + 97)}{8 - rc}"
                    move_wanted = getElementSatisfy(self.board.current_moves, move_played)
                    if move_wanted == -1:
                        self.selected_piece = None
                        continue
                    self.board.play(self.board.current_moves[move_wanted])
                    self.selected_piece = None
        if self.changed:
            self.draw_board(self.win)
        if self.board.winner == 0:
            print("White won !")
        elif self.board.winner == 1:
            print("Black won !")
        elif self.board.winner == 2:
            print("Draw !")
        else:
            print("Problem occured..")
        while True: # keep the canvas open but do nothing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


                    
