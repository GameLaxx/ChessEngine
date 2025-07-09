import json
import copy

# debug
def print_bit(bb):
    ret = ""
    for i in range(64):
        ret += str((1 << i) & bb)
    print(ret)

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
    def __init__(self, board_fen = ""):
        self.size = 8
        self.debug = False
        with open("MagicBitboards/mb_bishop.json", "r", encoding="utf-8") as f:
            self.mb_bishop = json.load(f)
            self.mb_bishop = {int(k): v for k, v in self.mb_bishop.items()}
        with open("MagicBitboards/mb_rook.json", "r", encoding="utf-8") as f:
            self.mb_rook = json.load(f)
            self.mb_rook = {int(k): v for k, v in self.mb_rook.items()}
        # ----- flags
        self.flags = {
            "wCastle" : 0, # "three" bits : 000, left is rook, middle is king and right is rook
            "bCastle" : 0,
            "wP2m" : None,
            "bP2m" : None,
            "moveCount" : 0,
            "50moveRule" : 0
        }
        self.winner = -1
        self.player_turn = self.WHITE
        # ----- board
        self.bitboards = [
            [0 for _ in range(6)],
            [0 for _ in range(6)]
        ] # all pieces on square 
        if board_fen != "":
            self.load(board_fen)
        else:
            self.init_board() # place pieces on the right squares
        # ----- occupancy
        self.occupancy = {self.WHITE : 0, self.BLACK : 0, self.BOTH : 0}
        self.update_occupancy() # after placing pieces, update occupancy
        self._stack = [] # stack of all previous positions and can be used for future positions
        # ----- first legal moves
        self.current_moves = self.get_moves(self.player_turn)

    #-------------------------------------------------------------------------------------------------------------
    # Utilities
    #-------------------------------------------------------------------------------------------------------------

    def print_bitboard(self, bitboard):
        for rank in range(8):
            line = ""
            for file in range(8):
                sq = rank * 8 + file
                line += "1 " if (bitboard >> sq) & 1 else ". "
            print(line)
        print()

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
    
    def index_to_square(self, index):
        return divmod(index, 8)
    def square_to_index(self, square_str : str):
        row = 8 - int(square_str[1])
        col = ord(square_str[0]) - 97
        return (col + row * 8)
    def square_to_bit(self, square_str : str):
        return 1 << self.square_to_index(square_str)

    def set_piece(self, color, piece, index : int):
        self.bitboards[color][piece] |= 1 << index
    def pop_piece(self, color, piece, index : int):
        if piece == -1:
            for i in range(6):
                self.bitboards[color][i] &= ~(1 << index)
            return
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
        return list(map(self.index_to_square, self.bitboard_to_indices(bitboard)))
    
    def letter_to_column(self, letter : str):
        if len(letter) != 1:
            return -1
        if letter > "h" or letter < "a":
            return -1
        return ord(letter) - 97 # 97 == ord("a")
    
    def count_piece_bitboard(self, bitboard):
        count = 0
        while bitboard:
            bitboard &= bitboard - 1  # remove lowest bit
            count += 1
        return count
    def count_piece_wholeboard(self, color, piece):
        piece_bitboard = self.bitboards[color][piece]
        return self.count_piece_bitboard(piece_bitboard)

    #-------------------------------------------------------------------------------------------------------------
    # Init
    #-------------------------------------------------------------------------------------------------------------

    def init_board(self):
        self.winner = -1
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

    def load(self, board_fen : str):
        fen_flags = board_fen.split(" ")
        fen_split : list[str] = fen_flags[0].split("/")
        index = 63
        for i in range(len(fen_split) - 1, -1, -1): # my bad all is reverse for now
            row = fen_split[i]
            for j in range(len(row) - 1, -1, -1):
                if row[j].isnumeric():
                    index -= int(row[j])
                    continue
                if row[j].isupper():
                    self.set_piece(self.WHITE, self.str_to_piece(row[j]), index)
                else:
                    self.set_piece(self.BLACK, self.str_to_piece(row[j].upper()), index)
                index -= 1

        if fen_flags[1] == "w":
            self.player_turn = self.WHITE
        else:
            self.player_turn = self.BLACK

        if fen_flags[2] == "-": # no castle
            self.flags["wCastle"] = 7
            self.flags["bCastle"] = 7
        else:
            if not "K" in fen_flags[2]:
                self.flags["wCastle"] |= 1
            if not "Q" in fen_flags[2]:
                self.flags["wCastle"] |= 1 << 2
            if not "K" in fen_flags[2] and not "Q" in fen_flags[2]:
                self.flags["wCastle"] |= 1 << 1 
            if not "k" in fen_flags[2]:
                self.flags["bCastle"] |= 1
            if not "q" in fen_flags[2]:
                self.flags["bCastle"] |= 1 << 2
            if not "k" in fen_flags[2] and not "q" in fen_flags[2]:
                self.flags["bCastle"] |= 1 << 1 

    #-------------------------------------------------------------------------------------------------------------
    # Update functions
    #-------------------------------------------------------------------------------------------------------------

    def update_occupancy(self):
        self.occupancy[self.WHITE] = sum(self.bitboards[self.WHITE])
        self.occupancy[self.BLACK] = sum(self.bitboards[self.BLACK])
        self.occupancy[self.BOTH] = self.occupancy[self.WHITE] | self.occupancy[self.BLACK]

    def update_flags(self, move : str):
        if move[-2:] == "h8" or move[-2:] == "h1":
            self.flags["bCastle" if self.player_turn == self.WHITE else "wCastle"] |= 1 << 2
        if move[-2:] == "a8" or move[-2:] == "a1":
            self.flags["bCastle" if self.player_turn == self.WHITE else "wCastle"] |= 1
        if move[0] == "P":
            if abs(int(move[6]) - int(move[2])) == 2:
                self.flags["wP2m" if self.player_turn == self.WHITE else "bP2m"] = ord(move[1]) - 97
            else:
                self.flags["wP2m" if self.player_turn == self.WHITE else "bP2m"] = None
            return
        if move[0] == "K":
            self.flags["wCastle" if self.player_turn == self.WHITE else "bCastle"] |= 1 << 1
            return
        if move[0] == "R":
            if move[1] == "a" and ((self.player_turn == self.WHITE and move[2] == "1") or ((self.player_turn == self.BLACK and move[2] == "8"))):
                self.flags["wCastle" if self.player_turn == self.WHITE else "bCastle"] |= 1
                return
            if move[1] == "h" and ((self.player_turn == self.WHITE and move[2] == "1") or ((self.player_turn == self.BLACK and move[2] == "8"))):
                self.flags["wCastle" if self.player_turn == self.WHITE else "bCastle"] |= 1 << 2
                return
        self.flags["wP2m" if self.player_turn == self.WHITE else "bP2m"] = None

    #-------------------------------------------------------------------------------------------------------------
    # Stack behaviour
    #-------------------------------------------------------------------------------------------------------------

    def _push(self):
        flags = (self.flags["wCastle"], self.flags["bCastle"], self.flags["wP2m"], self.flags["bP2m"], self.flags["moveCount"],self.flags["50moveRule"])
        self._stack.append((copy.deepcopy(self.bitboards), flags, self.player_turn))

    def _pop(self):
        self.bitboards, flags, self.player_turn = self._stack.pop()
        self.flags["wCastle"], self.flags["bCastle"], self.flags["wP2m"], self.flags["bP2m"], self.flags["moveCount"], self.flags["50moveRule"] = flags
        self.update_occupancy()

    #-------------------------------------------------------------------------------------------------------------
    # Legal Moves
    #-------------------------------------------------------------------------------------------------------------

    def board_attacked(self, player_attacked):
        """
        ### Params:
            - sim_bitboard: the bitboards to use
            - sim_occupancy: the occupancy that goes with the bitboards
            - sim_color: the color that is attacked
        
        ### Returns:
            - the bitboard of the attacks
        """
        opponent_bitboards = self.bitboards[(player_attacked + 1) % 2]
        ret_bitboards = 0
        for piece in range(6):
            indices = self.bitboard_to_indices(opponent_bitboards[piece])
            tmp_bb = 0
            for index in indices:
                tmp_bb |= self.get_moves_piece_bitboard(piece, index, player_moving=(player_attacked + 1) % 2, attack_only=True)
            ret_bitboards |= tmp_bb
            # currently the index of the piece is not taken into account => if problem might be try this solution
        return ret_bitboards
    
    def is_king_checked(self, player_attacked, king_index = -1):
        king_position = king_index if king_index != -1 else 1 << (self.bitboards[player_attacked][self.KING].bit_length() - 1) # only one king
        bitboards_attacked = self.board_attacked(player_attacked)
        return king_position & bitboards_attacked != 0
    
    def is_legal(self, move : str, player_moving):
        self._move(move)
        is_legal = not self.is_king_checked(player_moving)
        self._pop()
        return is_legal

    #-------------------------------------------------------------------------------------------------------------
    # Moves
    #-------------------------------------------------------------------------------------------------------------
    
    def detect_special_move(self, player_moving, piece, from_square, to_square):
        if piece == self.PAWN:
            if player_moving == self.WHITE and to_square[0] == 0: # promotion
                return "+"
            if player_moving == self.BLACK and to_square[0] == 8: # promotion
                return "+"
            if from_square[1] == to_square[1]:
                return ""
            if to_square not in self.bitboard_to_squares(self.occupancy[(player_moving + 1) % 2]): # en passant
                return "*"
        if piece == self.KING:
            if from_square[1] - to_square[1] == 2:
                return "O" # queen castle
            if from_square[1] - to_square[1] == -2:
                return "o" # queen castle
        return ""

    def get_moves_piece_bitboard(self, piece : int, index : int, player_moving, attack_only = False):
        moves = 0
        if piece == self.PAWN:
            piece_square = self.index_to_square(index)
            pos = 1 << index
            one_step = 0 
            two_steps = 0
            captures_left = 0
            captures_right = 0
            en_passant = 0
            if player_moving == self.WHITE:
                if index < 8 == 0:
                    return 0
                if not attack_only:
                    # simple
                    one_step = (pos >> 8) & ~self.occupancy[self.BOTH]
                    # double
                    two_steps = ((one_step & 0x0000FF0000000000) >> 8) & ~self.occupancy[self.BOTH]
                # captures
                captures_left = (pos >> 7) & ~0x0101010101010101
                captures_right = (pos >> 9) & ~0x8080808080808080
                if not attack_only:
                    captures_left &= self.occupancy[self.BLACK]
                    captures_right &= self.occupancy[self.BLACK]
                if self.flags["bP2m"] != None and piece_square[1] - self.flags["bP2m"] == 1 and piece_square[0] == 3:
                    en_passant = pos >> 9
                if self.flags["bP2m"] != None and piece_square[1] - self.flags["bP2m"] == -1 and piece_square[0] == 3:
                    en_passant = pos >> 7
            else:
                if index >= 56:
                    return 0
                if not attack_only:
                    # simple
                    one_step = (pos << 8) & ~self.occupancy[self.BOTH]
                    # double
                    two_steps = ((one_step & 0x0000000000FF0000) << 8) & ~self.occupancy[self.BOTH]
                # captures
                captures_left = (pos << 9) & ~0x0101010101010101
                captures_right = (pos << 7) & ~0x8080808080808080
                if not attack_only:
                    captures_left &= self.occupancy[self.WHITE]
                    captures_right &= self.occupancy[self.WHITE]
                if self.flags["wP2m"] != None and piece_square[1] - self.flags["wP2m"] == 1 and piece_square[0] == 4:
                    en_passant = pos << 7
                if self.flags["wP2m"] != None and piece_square[1] - self.flags["wP2m"] == -1 and piece_square[0] == 4:
                    en_passant = pos << 9
            moves |= one_step | two_steps | captures_left | captures_right | en_passant
            return moves
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
            return moves & ~self.occupancy[player_moving]
        if piece == self.ROOK:
            masked = self.occupancy[self.BOTH] & self.mb_rook[index]["mask"]
            attack_index = (masked * self.mb_rook[index]["magic"]) >> self.mb_rook[index]["shift"]
            relevant_bits = 64 - self.mb_rook[index]["shift"]
            attack_index &= (1 << relevant_bits) - 1
            moves = self.mb_rook[index]["table"][attack_index]
            return moves & ~self.occupancy[player_moving]
        if piece == self.BISHOP:
            masked = self.occupancy[self.BOTH] & self.mb_bishop[index]["mask"]
            attack_index = (masked * self.mb_bishop[index]["magic"]) >> self.mb_bishop[index]["shift"]
            relevant_bits = 64 - self.mb_bishop[index]["shift"]
            attack_index &= (1 << relevant_bits) - 1
            moves = self.mb_bishop[index]["table"][attack_index]
            return moves & ~self.occupancy[player_moving]
        if piece == self.KNIGHT:
            rank, file = divmod(index, 8)
            for delta in self.KNIGHT_DELTAS:
                target = index + delta
                if 0 <= target < 64: # on the board
                    tr, tf = divmod(target, 8)
                    if abs(tr - rank) <= 2 and abs(tf - file) <= 2: # on a square around the knight
                        moves |= 1 << target
            return moves & ~self.occupancy[player_moving]
        # only king is left
        rank, file = divmod(index, 8)
        for delta in self.KING_DELTAS:
            target = index + delta
            if 0 <= target < 64: # on the board
                tr, tf = divmod(target, 8)
                if abs(tr - rank) <= 1 and abs(tf - file) <= 1: # on a square around the king
                    moves |= 1 << target
        castle_rights = self.flags["wCastle" if player_moving == self.WHITE else "bCastle"]
        if attack_only or castle_rights & 1 << 1 == 1 or self.is_king_checked(player_moving):
            return moves & ~self.occupancy[player_moving] 
        if castle_rights & 1 == 0: # queen castle
            queen_castle_mask = (1 << 57) | (1 << 58) | (1 << 59) if player_moving == self.WHITE else (1 << 1) | (1 << 2) | (1 << 3)
            queen_castle_right = self.occupancy[self.BOTH] & queen_castle_mask
            if queen_castle_right == 0 and not self.is_king_checked(player_moving, queen_castle_mask):
                moves |= 1 << (index - 2)
        if castle_rights & 1 << 2 == 0: # king castle
            king_castle_mask = (1 << 61) | (1 << 62) if player_moving == self.WHITE else (1 << 5) | (1 << 6)
            king_castle_right = self.occupancy[self.BOTH] & king_castle_mask
            if king_castle_right == 0 and not self.is_king_checked(player_moving, king_castle_mask):
                moves |= 1 << (index + 2)
        return moves & ~self.occupancy[player_moving] 
    def get_moves_piece(self, piece : int, index : int, player_moving):
        ret = []
        moves_bitboard = self.get_moves_piece_bitboard(piece, index, player_moving)
        from_square = divmod(index, 8)
        to_squares = self.bitboard_to_squares(moves_bitboard)
        for square in to_squares:
            piece_str = self.piece_to_str(piece)
            is_special_move = self.detect_special_move(player_moving, piece, from_square, square)
            if is_special_move == "": # no special move
                ret.append(f"{piece_str}{chr(from_square[1] + 97)}{8 - from_square[0]}-{piece_str}{chr(square[1] + 97)}{8 - square[0]}")
                continue 
            if is_special_move == "+": # pawn promotion
                for i in range(self.KNIGHT, self.KING):
                    ret.append(f"{piece_str}{chr(from_square[1] + 97)}{8 - from_square[0]}-{piece_str}{chr(square[1] + 97)}{8 - square[0]}-{i}")
                continue 
            if is_special_move in ["*", "o", "O"]:
                ret.append(f"{piece_str}{chr(from_square[1] + 97)}{8 - from_square[0]}-{piece_str}{chr(square[1] + 97)}{8 - square[0]}-{is_special_move}")
                continue
        return ret
    def get_moves(self, player_moving):
        ret = []
        for piece in range(6):
            indices = self.bitboard_to_indices(self.bitboards[player_moving][piece])
            for index in indices:
                ret += list(filter(lambda x : self.is_legal(x, player_moving) , self.get_moves_piece(piece, index, player_moving)))
        return ret

    def _move(self, move : str, save = True): # convention is "piece from-piece to"
        if save:
            self._push()
        next_player = (self.player_turn + 1) % 2
        move_split = move.split("-")
        piece_from = move_split[0]
        piece_to = move_split[1]
        if len(move_split) == 2:
            piece_type = self.str_to_piece(move[0])
            index_from = self.square_to_index(piece_from[1:])
            index_to = self.square_to_index(piece_to[1:])
            self.set_piece(self.player_turn, piece_type, index_to)
            self.pop_piece(self.player_turn, piece_type, index_from)
            self.pop_piece(next_player, -1, index_to) # -1 because we don't know the piece type and it is not relevant
        else:
            special_move : str = move_split[2]
            if special_move == "*": # en passant
                piece_type = self.str_to_piece(move[0])
                index_from = self.square_to_index(piece_from[1:])
                index_to = self.square_to_index(piece_to[1:])
                remove_from = index_to - (- 8 if self.player_turn == self.WHITE else 8)
                self.set_piece(self.player_turn, piece_type, index_to)
                self.pop_piece(self.player_turn, piece_type, index_from)
                self.pop_piece(next_player, -1, remove_from) # -1 because we don't know the piece type and it is not relevant
            elif special_move == "o": # king castle
                piece_type = self.str_to_piece(move[0])
                index_from = self.square_to_index(piece_from[1:])
                index_to = self.square_to_index(piece_to[1:])
                self.set_piece(self.player_turn, piece_type, index_to)
                self.pop_piece(self.player_turn, piece_type, index_from)
                self.set_piece(self.player_turn, self.ROOK, index_to - 1)
                self.pop_piece(self.player_turn, self.ROOK, index_from + 3)
            elif special_move == "O": # queen castle
                piece_type = self.str_to_piece(move[0])
                index_from = self.square_to_index(piece_from[1:])
                index_to = self.square_to_index(piece_to[1:])
                self.set_piece(self.player_turn, piece_type, index_to)
                self.pop_piece(self.player_turn, piece_type, index_from)
                self.set_piece(self.player_turn, self.ROOK, index_to + 1)
                self.pop_piece(self.player_turn, self.ROOK, index_from - 4)
            elif special_move.isnumeric() and self.KNIGHT <= int(special_move) <= self.QUEEN: # pawn promotion
                piece_type = self.str_to_piece(move[0])
                new_piece_type = int(special_move)
                index_from = self.square_to_index(piece_from[1:])
                index_to = self.square_to_index(piece_to[1:])
                self.set_piece(self.player_turn, new_piece_type, index_to)
                self.pop_piece(self.player_turn, piece_type, index_from)
                self.pop_piece(next_player, -1, index_to) # -1 because we don't know the piece type and it is not relevant
            else:
                raise ValueError("❗Illegal special move !")
        self.update_occupancy()
        self.update_flags(move)
        return self.bitboards # redundant because already changed
    
    def play(self, move : str):
        if move not in self.current_moves:
            raise ValueError("❗Illegal move !")
        self._move(move, False)
        self.player_turn = (self.player_turn + 1) % 2
        self.current_moves = self.get_moves(self.player_turn)
        self.flags["moveCount"] += 1
        if move[0] == "P":
            self.flags["50moveRule"] = 0
        else:
            self.flags["50moveRule"] += 1
        if self.flags["50moveRule"] >= 100 and self.player_turn == self.WHITE:
            self.winner = self.BOTH
            return
        if len(self.current_moves) == 0 :
            self.winner = (self.player_turn + 1) % 2 if self.is_king_checked() else self.BOTH
            return
        
    #-------------------------------------------------------------------------------------------------------------
    # Moves
    #-------------------------------------------------------------------------------------------------------------

    def to_matrix(self, sim_bitboards = None):
        bitboards = sim_bitboards if sim_bitboards else self.bitboards
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
            indices_w = self.bitboard_to_squares(bitboards[self.WHITE][piece]) 
            for index in indices_w:
                ret[index[0]][index[1]] = "w" + self.piece_to_str(piece)
            indices_b = self.bitboard_to_squares(bitboards[self.BLACK][piece]) 
            for index in indices_b:
                ret[index[0]][index[1]] = "b" + self.piece_to_str(piece)
        return ret

    def __repr__(self, sim_bitboards = None):
        rows = list(map(lambda row : ".".join(row), self.to_matrix(sim_bitboards)))
        board = "\n".join(rows)
        return board