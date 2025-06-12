class ChessGame():
    def __init__(self):
        self.size = 8
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["wP"] * 8,
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.flags = {
            "wKm" : False,
            "bKm" : False,
            "wRam" : False,
            "wRhm" : False,
            "bRam" : False,
            "bRhm" : False,
            "wP2m" : None,
            "bP2m" : None
        }
        self.player_turn = 0 # 0 is white, 1 is black
        self.current_moves = self.get_moves()

    def update_flags(self, move : str):
        if move[0] == "P":
            if abs(int(move[6]) - int(move[2])) == 2:
                self.flags["wP2m" if self.player_turn == 0 else "bP2m"] = ord(move[1]) - 97
            else:
                self.flags["wP2m" if self.player_turn == 0 else "bP2m"] = None
            return
        if move[0] == "K":
            self.flags["wKm" if self.player_turn == 0 else "bKm"] = True
            return
        if move[0] == "R":
            if move[1] == "a" and ((self.player_turn == 0 and move[2] == "1") or ((self.player_turn == 1 and move[2] == "8"))):
                self.flags["wRam" if self.player_turn == 0 else "bRam"] = True
                return
            if move[1] == "h" and ((self.player_turn == 0 and move[2] == "1") or ((self.player_turn == 1 and move[2] == "8"))):
                self.flags["wRhm" if self.player_turn == 0 else "bRhm"] = True
                return
        self.flags["wP2m" if self.player_turn == 0 else "bP2m"] = None

    def letter_to_column(self, letter : str):
        if len(letter) != 1:
            return -1
        if letter > "h" or letter < "a":
            return -1
        return ord(letter) - 97 # 97 == ord("a")
    
    def get_moves_piece(self, piece_str: str):
        if len(piece_str) != 3:
            return None
        name = piece_str[0]
        col = self.letter_to_column(piece_str[1])
        row = 8 - int(piece_str[2])
        if not (0 <= row < 8 and 0 <= col < 8):
            return None
        piece = self.board[row][col]
        if piece == "--":
            return None
        current_color = 'w' if self.player_turn == 0 else 'b'
        if piece[0] != current_color:
            return None
        if piece[1] != name:
            return None

        directions = []
        moves = []

        def in_bounds(r, c):
            return 0 <= r < 8 and 0 <= c < 8
        def add_moves(r, c, dr, dc):
            # add the first directionnal boost before searching for empty spaces
            r += dr
            c += dc
            while in_bounds(r, c):
                target = self.board[r][c]
                # empty square
                if target == "--":
                    moves.append(f"{piece_str}-{name}{chr(c + 97)}{8 - r}")
                # opponent piece
                elif target[0] != current_color:
                    moves.append(f"{piece_str}-{name}{chr(c + 97)}{8 - r}")
                    break
                # own piece
                else:
                    break
                r += dr
                c += dc

        if name == "P":
            direction = -1 if current_color == "w" else 1
            start_row = 6 if current_color == "w" else 1
            # front moves
            if in_bounds(row + direction, col) and self.board[row + direction][col] == "--":
                moves.append(f"{piece_str}-{name}{chr(col + 97)}{8 - (row + direction)}")
                if row == start_row and self.board[row + 2 * direction][col] == "--":
                    moves.append(f"{piece_str}-{name}{chr(col + 97)}{8 - (row + 2 * direction)}")
            # diagonal captures
            for dc in [-1, 1]:
                if in_bounds(row + direction, col + dc):
                    target = self.board[row + direction][col + dc]
                    if target != "--" and target[0] != current_color:
                        moves.append(f"{piece_str}-{name}{chr(col + dc + 97)}{8 - (row + direction)}")
                    if (col + dc) == self.flags["wP2m" if self.player_turn == 1 else "bP2m"]: # en passant
                        if (self.player_turn == 0 and row == 3) or (self.player_turn == 1 and row == 4):
                            moves.append(f"{piece_str}-{name}{chr(col + dc + 97)}{8 - (row + direction)}-*")
            return moves
        if name == "Q":
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                add_moves(row, col, dr, dc)
            return moves
        if name == "R":
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                add_moves(row, col, dr, dc)
            return moves
        if name == "B":
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                add_moves(row, col, dr, dc)
            return moves
        if name == "N":
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                r2, c2 = row + dr, col + dc
                if in_bounds(r2, c2):
                    target = self.board[r2][c2]
                    if target == "--" or target[0] != current_color:
                        moves.append(f"{piece_str}-{name}{chr(c2 + 97)}{8 - r2}")
            return moves
        # nominal case is king because almost never used
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r2, c2 = row + dr, col + dc
                if in_bounds(r2, c2):
                    target = self.board[r2][c2]
                    if target == "--" or target[0] != current_color:
                        moves.append(f"{piece_str}-{name}{chr(c2 + 97)}{8 - r2}")
        return moves
    
    def get_moves(self): # 36s for 1M call
        ret = []
        color = "w" if self.player_turn == 0 else "b"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col] 
                if piece == "--":
                    continue
                if piece[0] != color:
                    continue
                moves = self.get_moves_piece(f"{piece[1]}{chr(97 + col)}{8 - row}")
                if moves == None:
                    continue
                ret += moves
        return ret

    def move(self, move : str): # convention is "piece from-piece to"
        move_split = move.split("-")
        piece_from = move_split[0]
        piece_to = move_split[1]
        from_row = 8 - int(piece_from[2])
        from_col = self.letter_to_column(piece_from[1])
        to_row = 8 - int(piece_to[2])
        to_col = self.letter_to_column(piece_to[1])
        # outside of the board
        if from_col == -1 or to_col == -1:
            return 0
        if not (0 <= from_row < 8) or not (0 <= to_row < 8):
            return 0
        piece = self.board[from_row][from_col]
        # no piece selected
        if piece == "--":
            return 0
        current_color = 'w' if self.player_turn == 0 else 'b'
        # piece of wrong color selected
        if piece[0] != current_color:
            return 0
        # set piece
        self.update_flags(move)
        if move[0] == "P" and len(move_split) == 3:
            if move_split[2] == "*": # for now only en passant but later promotion
                self.board[from_row][to_col] = "--"
        self.board[from_row][from_col] = "--"
        self.board[to_row][to_col] = piece
        self.player_turn = (self.player_turn + 1) % 2
        self.current_moves = self.get_moves()

    def __repr__(self):
        rows = list(map(lambda row : ".".join(row), self.board))
        board = "\n".join(rows)
        return board