import pygame
from chess_game import ChessGame
import sys

class ChessRender():
    def __init__(self, board : ChessGame, size = 640):
        pygame.init()
        self.board = board
        self.size = size
        self.square_size = self.size // self.board.size
        self.white_color = (240, 217, 181)
        self.brown_color = (181, 136, 99)
        self.green_color = (100, 180, 100)
        self.pieces = {}
        self.selected_piece = None
        PIECE_NAMES = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
        for name in PIECE_NAMES:
            self.pieces[name] = pygame.transform.scale(
                pygame.image.load(f"pieces/{name}.png"), (self.square_size, self.square_size)
            )
        self.win = pygame.display.set_mode((self.size, self.size))
        pygame.display.set_caption("Jeu d'échecs")

    def draw_board(self, win):
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.selected_piece and (row == 8 - int(self.selected_piece[2])) and col == ord(self.selected_piece[1]) - 97:
                    color = self.green_color
                else:
                    color = self.white_color if (row + col) % 2 == 0 else self.brown_color
                pygame.draw.rect(win, color, (col * self.square_size, row * self.square_size, self.square_size, self.square_size))
                piece = self.board.board[row][col]
                if piece == "--":
                    continue
                win.blit(self.pieces[piece], (col * self.square_size, row * self.square_size))
        pygame.display.update()


    def get_square_clicked(self, pos):
        x, y = pos
        row = y // self.square_size
        col = x // self.square_size
        return row, col


    def update(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.draw_board(self.win)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    rc, cc = self.get_square_clicked(pygame.mouse.get_pos())
                    piece = self.board.board[rc][cc]
                    
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
                        print("Selecting", self.selected_piece, self.board.get_moves_piece(self.selected_piece))
                        continue
                    if (piece[0] == "w" and self.board.player_turn == 0) or (piece[0] == "b" and self.board.player_turn == 1):
                        self.selected_piece = f"{piece[1]}{chr(cc + 97)}{8 - rc}"
                        print("Selecting", self.selected_piece, self.board.get_moves_piece(self.selected_piece))
                        continue
                    move = f"{self.selected_piece}-{self.selected_piece[0]}{chr(cc + 97)}{8 - rc}"
                    if not move in self.board.current_moves:
                        self.selected_piece = None
                        continue
                    if self.board.move(move) == -1:
                        break
                    self.selected_piece = None



                    
