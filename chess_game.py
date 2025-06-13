import json

# debug
def print_bitboard(bb):
    for rank in range(8):
        line = ""
        for file in range(8):
            sq = rank * 8 + file
            line += "1 " if (bb >> sq) & 1 else ". "
        print(line)
    print()

class ChessGame():
    WHITE = 0
    BLACK = 1
    BOTH = 2
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5
    KNIGHT_DELTAS = [17, 15, 10, 6, -17, -15, -10, -6]
    KING_DELTAS = [1, -1, 8, -8, 9, -9, 7, -7]
    # bitboards : a1 == 0 and h8 == 63
    def __init__(self):
        self.size = 8
        with open("MagicBitboards/mb_bishop.json", "r", encoding="utf-8") as f:
            self.mb_bishop = json.load(f)
            self.mb_bishop = {int(k): v for k, v in self.mb_bishop.items()}
        with open("MagicBitboards/mb_rook.json", "r", encoding="utf-8") as f:
            self.mb_rook = json.load(f)
            self.mb_rook = {int(k): v for k, v in self.mb_rook.items()}
        self.bitboards = [
            [0 for _ in range(6)],
            [0 for _ in range(6)]
        ] # all pieces on square 
        self.init_board() # place pieces on the right squares
        self.occupancy = {self.WHITE : 0, self.BLACK : 0, self.BOTH : 0}
        self.update_occupancy() # after placing pieces, update occupancy
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
        self.player_turn = self.WHITE
        self.current_moves = self.get_moves()

    #-------------------------------------------------------------------------------------------------------------
    # Utilities
    #-------------------------------------------------------------------------------------------------------------

    def piece_to_str(self, piece):
        if piece == self.PAWN:
            return "P"
        if piece == self.KNIGHT:
            return "N"
        if piece == self.BISHOP:
            return "B"
        if piece == self.ROOK:
            return "R"
        if piece == self.QUEEN:
            return "Q"
        return "K"
    def str_to_piece(self, piece):
        if piece == "P":
            return self.PAWN
        if piece == "N":
            return self.KNIGHT
        if piece == "B":
            return self.BISHOP
        if piece == "R":
            return self.ROOK
        if piece == "Q":
            return self.QUEEN
        return self.KING
    
    def square_to_index(self, square_str : str):
        row = 8 - int(square_str[1])
        col = ord(square_str[0]) - 97
        return (col + row * 8)
    def square_to_bit(self, square_str : str):
        return 1 << self.square_to_index(square_str)

    def set_piece(self, color, piece, index : int):
        self.bitboards[color][piece] |= 1 << index
    def pop_piece(self, color, piece, index : int):
        self.bitboards[color][piece] &= ~(1 << index)

    def bitboard_to_indices(self, bitboard : int):
        """
        ### Params:
            - bitboard: the bitboard to convert
        
        ### Returns:
            - list[(row, col)]
        """
        indices = []
        while bitboard:
            lowest_bit = bitboard & -bitboard
            indices.append(lowest_bit.bit_length() - 1)
            bitboard &= bitboard - 1 # remove lowest bit
        return indices
    def bitboard_to_squares(self, bitboard : int):
        return list(map(lambda x : divmod(x, 8), self.bitboard_to_indices(bitboard)))
    
    def letter_to_column(self, letter : str):
        if len(letter) != 1:
            return -1
        if letter > "h" or letter < "a":
            return -1
        return ord(letter) - 97 # 97 == ord("a")

    #-------------------------------------------------------------------------------------------------------------
    # Init
    #-------------------------------------------------------------------------------------------------------------

    def init_board(self):
        # pawns
        for i in range(8):
            self.set_piece(self.WHITE, self.PAWN, 48 + i)
            self.set_piece(self.BLACK, self.PAWN, 8 + i)
        # rooks
        self.set_piece(self.BLACK, self.ROOK, 0)
        self.set_piece(self.BLACK, self.ROOK, 7)
        self.set_piece(self.WHITE, self.ROOK, 56)
        self.set_piece(self.WHITE, self.ROOK, 63)
        # knights
        self.set_piece(self.BLACK, self.KNIGHT, 1)
        self.set_piece(self.BLACK, self.KNIGHT, 6)
        self.set_piece(self.WHITE, self.KNIGHT, 57)
        self.set_piece(self.WHITE, self.KNIGHT, 62)
        # bishops
        self.set_piece(self.BLACK, self.BISHOP, 2)
        self.set_piece(self.BLACK, self.BISHOP, 5)
        self.set_piece(self.WHITE, self.BISHOP, 58)
        self.set_piece(self.WHITE, self.BISHOP, 61)
        # queens
        self.set_piece(self.BLACK, self.QUEEN, 3)
        self.set_piece(self.WHITE, self.QUEEN, 59)
        # kings
        self.set_piece(self.BLACK, self.KING, 4)
        self.set_piece(self.WHITE, self.KING, 60)

    #-------------------------------------------------------------------------------------------------------------
    # Update functions
    #-------------------------------------------------------------------------------------------------------------

    def update_occupancy(self):
        self.occupancy[self.WHITE] = sum(self.bitboards[self.WHITE])
        self.occupancy[self.BLACK] = sum(self.bitboards[self.BLACK])
        self.occupancy[self.BOTH] = self.occupancy[self.WHITE] | self.occupancy[self.BLACK]

    def update_flags(self, move : str):
        if move[0] == "P":
            if abs(int(move[6]) - int(move[2])) == 2:
                self.flags["wP2m" if self.player_turn == self.WHITE else "bP2m"] = ord(move[1]) - 97
            else:
                self.flags["wP2m" if self.player_turn == self.WHITE else "bP2m"] = None
            return
        if move[0] == "K":
            self.flags["wKm" if self.player_turn == self.WHITE else "bKm"] = True
            return
        if move[0] == "R":
            if move[1] == "a" and ((self.player_turn == self.WHITE and move[2] == "1") or ((self.player_turn == self.BLACK and move[2] == "8"))):
                self.flags["wRam" if self.player_turn == self.WHITE else "bRam"] = True
                return
            if move[1] == "h" and ((self.player_turn == self.WHITE and move[2] == "1") or ((self.player_turn == self.BLACK and move[2] == "8"))):
                self.flags["wRhm" if self.player_turn == self.WHITE else "bRhm"] = True
                return
        self.flags["wP2m" if self.player_turn == self.WHITE else "bP2m"] = None

    #-------------------------------------------------------------------------------------------------------------
    # Moves
    #-------------------------------------------------------------------------------------------------------------
    
    def get_moves_piece_bitboard(self, piece : int, index : int):
        moves = 0
        if piece == self.PAWN:
            return 0
        if piece == self.QUEEN:
            # bishop
            masked_bishop = self.occupancy[self.BOTH] & self.mb_bishop[index]["mask"]
            attack_index_bishop = (masked_bishop * self.mb_bishop[index]["magic"]) >> self.mb_bishop[index]["shift"]
            relevant_bits_bishop = 64 - self.mb_bishop[index]["shift"]
            attack_index_bishop &= (1 << relevant_bits_bishop) - 1
            # rook
            masked_rook = self.occupancy[self.BOTH] & self.mb_rook[index]["mask"]
            attack_index_rook = (masked_rook * self.mb_rook[index]["magic"]) >> self.mb_rook[index]["shift"]
            relevant_bits_rook = 64 - self.mb_rook[index]["shift"]
            attack_index_rook &= (1 << relevant_bits_rook) - 1
            moves = self.mb_bishop[index]["table"][attack_index_bishop] | self.mb_rook[index]["table"][attack_index_rook]
            return moves & ~self.occupancy[self.player_turn]
        if piece == self.ROOK:
            masked = self.occupancy[self.BOTH] & self.mb_rook[index]["mask"]
            attack_index = (masked * self.mb_rook[index]["magic"]) >> self.mb_rook[index]["shift"]
            relevant_bits = 64 - self.mb_rook[index]["shift"]
            attack_index &= (1 << relevant_bits) - 1
            moves = self.mb_rook[index]["table"][attack_index]
            return moves & ~self.occupancy[self.player_turn]
        if piece == self.BISHOP:
            masked = self.occupancy[self.BOTH] & self.mb_bishop[index]["mask"]
            attack_index = (masked * self.mb_bishop[index]["magic"]) >> self.mb_bishop[index]["shift"]
            relevant_bits = 64 - self.mb_bishop[index]["shift"]
            attack_index &= (1 << relevant_bits) - 1
            moves = self.mb_bishop[index]["table"][attack_index]
            return moves & ~self.occupancy[self.player_turn]
        if piece == self.KNIGHT:
            rank, file = divmod(index, 8)
            for delta in self.KNIGHT_DELTAS:
                target = index + delta
                if 0 <= target < 64: # on the board
                    tr, tf = divmod(target, 8)
                    if abs(tr - rank) <= 2 and abs(tf - file) <= 2: # on a square around the knight
                        moves |= 1 << target
            return moves & ~self.occupancy[self.player_turn]
        # only king is left
        rank, file = divmod(index, 8)
        for delta in self.KING_DELTAS:
            target = index + delta
            if 0 <= target < 64: # on the board
                tr, tf = divmod(target, 8)
                if abs(tr - rank) <= 1 and abs(tf - file) <= 1: # on a square around the king
                    moves |= 1 << target
        return moves & ~self.occupancy[self.player_turn]
    
    def get_moves_piece(self, piece : int, index : int):
        ret = []
        moves_bitboard = self.get_moves_piece_bitboard(piece, index)
        from_square = divmod(index, 8)
        to_squares = self.bitboard_to_squares(moves_bitboard)
        for square in to_squares:
            piece_str = self.piece_to_str(piece)
            ret.append(f"{piece_str}{chr(from_square[1] + 97)}{8 - from_square[0]}-{piece_str}{chr(square[1] + 97)}{8 - square[0]}")
        return ret

    def get_moves(self): # 36s for 1M call
        ret = []
        player_bitboards = self.bitboards[self.player_turn]
        for piece in range(6):
            indices = self.bitboard_to_indices(player_bitboards[piece])
            for index in indices:
                ret += self.get_moves_piece(piece, index)
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
        raise ValueError("Not build yet")
    
    #-------------------------------------------------------------------------------------------------------------
    # Moves
    #-------------------------------------------------------------------------------------------------------------

    def to_matrix(self):
        ret = [
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
        ]
        for piece in range(6):
            indices_w = self.bitboard_to_squares(self.bitboards[self.WHITE][piece]) 
            for index in indices_w:
                ret[index[0]][index[1]] = "w" + self.piece_to_str(piece)
            indices_b = self.bitboard_to_squares(self.bitboards[self.BLACK][piece]) 
            for index in indices_b:
                ret[index[0]][index[1]] = "b" + self.piece_to_str(piece)
        return ret

    def __repr__(self):
        rows = list(map(lambda row : ".".join(row), self.to_matrix()))
        board = "\n".join(rows)
        return board