import random
import json

#-------------------------------------------------------------------------------------------------------------
# Masks
#-------------------------------------------------------------------------------------------------------------

def bishop_mask(square):
    attacks = 0
    rank, file = divmod(square, 8)
    for dr, df in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        r, f = rank + dr, file + df
        while 0 < r < 7 and 0 < f < 7:
            attacks |= 1 << (r * 8 + f)
            r += dr
            f += df
    return attacks

def rook_mask(square):
    attacks = 0
    rank, file = divmod(square, 8)
    for dr, df in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, f = rank + dr, file + df
        while 0 <= r < 8 and 0 <= f < 8:
            if r == rank and f == file:
                break
            attacks |= 1 << (r * 8 + f)
            r += dr
            f += df
    return attacks

#-------------------------------------------------------------------------------------------------------------
# Attacks
#-------------------------------------------------------------------------------------------------------------

def bishop_attacks_on_the_fly(square, blockers):
    attacks = 0
    rank, file = divmod(square, 8)
    for dr, df in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        r, f = rank + dr, file + df
        while 0 <= r < 8 and 0 <= f < 8:
            sq = r * 8 + f
            attacks |= 1 << (sq)
            if blockers & 1 << (sq):
                break
            r += dr
            f += df
    return attacks

def rook_attacks_on_the_fly(square, blockers):
    attacks = 0
    rank, file = divmod(square, 8)
    for dr, df in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, f = rank + dr, file + df
        while 0 <= r < 8 and 0 <= f < 8:
            sq = r * 8 + f
            attacks |= 1 << (sq)
            if blockers & 1 << (sq):
                break
            r += dr
            f += df
    return attacks

#-------------------------------------------------------------------------------------------------------------
# Occupancy
#-------------------------------------------------------------------------------------------------------------

def generate_occupancy_variations(mask):
    bits = [i for i in range(64) if (mask >> i) & 1]
    variations = []
    for i in range(1 << len(bits)):
        occ = 0
        for j, bit_index in enumerate(bits):
            if (i >> j) & 1:
                occ |= 1 << (bit_index)
        variations.append(occ)
    return variations

#-------------------------------------------------------------------------------------------------------------
# Magic number
#-------------------------------------------------------------------------------------------------------------

def find_magic_number(square, mask, attack_map, relevant_bits):
    for _ in range(1000000):
        magic = random.getrandbits(64) & random.getrandbits(64) & random.getrandbits(64)
        used = {}
        success = True
        for occ, attack in attack_map.items():
            index = ((occ & mask) * magic) >> (64 - relevant_bits)
            index &= (1 << relevant_bits) - 1
            if index in used:
                if used[index] != attack:
                    success = False
                    break
            else:
                used[index] = attack
        if success:
            return magic
    return None

#-------------------------------------------------------------------------------------------------------------
# Magic Table
#-------------------------------------------------------------------------------------------------------------

def build_magic_table(square, mask_func, attacks_func):
    mask = mask_func(square)
    occs = generate_occupancy_variations(mask)
    attack_map = {occ: attacks_func(square, occ) for occ in occs}
    relevant_bits = bin(mask).count("1")
    magic = find_magic_number(square, mask, attack_map, relevant_bits)
    
    if magic is None:
        raise Exception("Aucun magic number valide trouvé")
    
    attack_table = [0] * (1 << relevant_bits)
    for occ, attacks in attack_map.items():
        index = ((occ & mask) * magic) >> (64 - relevant_bits)
        index &= (1 << relevant_bits) - 1
        attack_table[index] = attacks

    return {
        "mask": mask,
        "magic": magic,
        "shift": 64 - relevant_bits,
        "table": attack_table
    }

#-------------------------------------------------------------------------------------------------------------
# JSON generation
#-------------------------------------------------------------------------------------------------------------

def generate_all_attacks(mb):
    ret = {}
    for i in range(64):
        ret[i] = build_magic_table(i, mb[0], mb[2])
    with open(f"MagicBitboards/{mb[1]}", "w+", encoding="utf-8") as f:
        json.dump(ret, f, ensure_ascii=False, indent=4)

#-------------------------------------------------------------------------------------------------------------
# Variables
#-------------------------------------------------------------------------------------------------------------

rook_mb = [rook_mask, "mb_rook.json", rook_attacks_on_the_fly]
bishop_mb = [bishop_mask, "mb_bishop.json", bishop_attacks_on_the_fly]
generate_all_attacks(rook_mb)