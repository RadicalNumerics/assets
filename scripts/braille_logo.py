#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from typing import Iterable, Dict, Set, List

# =========================
# Constants & mappings
# =========================
BRAILLE_BASE = 0x2800
BRAILLE_BLANK = chr(BRAILLE_BASE)

# Dot -> bit (little endian per Unicode Braille)
DOT_TO_BIT = {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7}

# Column layouts (top -> bottom)
LEFT_COL  = [1, 2, 3, 7]
RIGHT_COL = [4, 5, 6, 8]

# Pair across columns (same row)
ROW_PAIR = {1:4, 2:5, 3:6, 7:8, 4:1, 5:2, 6:3, 8:7}

# Dot <-> (row, col) within a single 4x2 cell (rows 0..3, cols 0..1)
DOT_TO_COORD = {
    1:(0,0), 2:(1,0), 3:(2,0), 7:(3,0),
    4:(0,1), 5:(1,1), 6:(2,1), 8:(3,1)
}
COORD_TO_DOT = {v:k for k,v in DOT_TO_COORD.items()}


# =========================
# Conversions
# =========================
def dots_to_braille(dots: Iterable[int]) -> str:
    v = 0
    for d in dots:
        if d not in DOT_TO_BIT:
            raise ValueError(f"Dot numbers must be 1..8. Got {d}.")
        v |= (1 << DOT_TO_BIT[d])
    return chr(BRAILLE_BASE + v)

def braille_to_dots(ch: str) -> Set[int]:
    code = ord(ch)
    if not (0x2800 <= code <= 0x28FF):
        raise ValueError(f"Character {repr(ch)} (U+{code:04X}) is not a Braille pattern.")
    bits = code - BRAILLE_BASE
    dots = []
    for dot, bit in DOT_TO_BIT.items():
        if bits & (1 << bit):
            dots.append(dot)
    return set(dots)

def is_braille_char(ch: str) -> bool:
    return 0x2800 <= ord(ch) <= 0x28FF


# =========================
# Cells container helpers
# =========================
def parse_initial_cells(char1: Iterable[int], char2: Iterable[int]) -> Dict[int, Set[int]]:
    # Always include both indices 0 and 1, even if a cell is blank
    return {0: set(char1), 1: set(char2)}

def cells_from_braille_string(b: str) -> Dict[int, Set[int]]:
    # Include every index in the string (blank char -> empty set)
    return {i: braille_to_dots(ch) for i, ch in enumerate(b)}

def cells_to_string(cells: Dict[int, Set[int]]) -> str:
    if not cells:
        return ""
    return "".join(dots_to_braille(sorted(cells.get(i, set()))) for i in sorted(cells.keys()))

def cells_to_string_fixed(cells: Dict[int, Set[int]], width: int = 2, clip_side: str = "left") -> str:
    """
    Force a fixed-width output. If more cells are produced than `width`,
    clip either from the left (keep rightmost) or right (keep leftmost).
    """
    s = cells_to_string(cells)
    if len(s) == width:
        return s
    if len(s) < width:
        return s + BRAILLE_BLANK * (width - len(s))
    # len(s) > width
    if clip_side == "left":
        return s[-width:]
    if clip_side == "right":
        return s[:width]
    raise ValueError("clip_side must be 'left' or 'right'.")


# =========================
# Moves (L/R/U/D)
# =========================
def shift_right(cells: Dict[int, Set[int]]) -> Dict[int, Set[int]]:
    new_cells: Dict[int, Set[int]] = {}
    for i in sorted(cells.keys()):
        ds = cells.get(i, set())
        new_cells.setdefault(i, set())
        new_cells.setdefault(i + 1, set())
        for d in ds:
            if d in (1, 2, 3, 7):      # left col -> right col (same cell)
                new_cells[i].add(ROW_PAIR[d])
            else:                      # right col -> overflow to next cell (as left col)
                new_cells[i + 1].add(ROW_PAIR[d])
    # prune empties
    return {k: v for k, v in new_cells.items() if v}

def shift_left(cells: Dict[int, Set[int]]) -> Dict[int, Set[int]]:
    if not cells:
        return {}
    new_cells: Dict[int, Set[int]] = {}
    min_idx, max_idx = min(cells.keys()), max(cells.keys())
    new_cells.setdefault(min_idx - 1, set())
    for i in range(min_idx, max_idx + 1):
        ds = cells.get(i, set())
        new_cells.setdefault(i, set())
        for d in ds:
            if d in (4, 5, 6, 8):      # right col -> left col (same cell)
                new_cells[i].add(ROW_PAIR[d])
            else:                      # left col -> overflow to previous cell (as right col)
                new_cells[i - 1].add(ROW_PAIR[d])
    return {k: v for k, v in new_cells.items() if v}

def shift_up(cells: Dict[int, Set[int]]) -> Dict[int, Set[int]]:
    new_cells: Dict[int, Set[int]] = {}
    for i, ds in cells.items():
        new: Set[int] = set()
        for d in ds:
            if d in LEFT_COL:
                pos = LEFT_COL.index(d)
                if pos > 0:
                    new.add(LEFT_COL[pos - 1])  # clip at top
            else:
                pos = RIGHT_COL.index(d)
                if pos > 0:
                    new.add(RIGHT_COL[pos - 1]) # clip at top
        if new:
            new_cells[i] = new
    return new_cells

def shift_down(cells: Dict[int, Set[int]]) -> Dict[int, Set[int]]:
    new_cells: Dict[int, Set[int]] = {}
    for i, ds in cells.items():
        new: Set[int] = set()
        for d in ds:
            if d in LEFT_COL:
                pos = LEFT_COL.index(d)
                if pos < len(LEFT_COL) - 1:
                    new.add(LEFT_COL[pos + 1])
            else:
                pos = RIGHT_COL.index(d)
                if pos < len(RIGHT_COL) - 1:
                    new.add(RIGHT_COL[pos + 1])
        if new:
            new_cells[i] = new
    return new_cells

def apply_moves(cells: Dict[int, Set[int]], moves: str) -> Dict[int, Set[int]]:
    for m in moves.upper():
        if m == 'R':
            cells = shift_right(cells)
        elif m == 'L':
            cells = shift_left(cells)
        elif m == 'U':
            cells = shift_up(cells)
        elif m == 'D':
            cells = shift_down(cells)
        else:
            raise ValueError(f"Unknown move '{m}'. Use only L, R, U, D.")
    return cells


# =========================
# Rotations (0/90/180/270)
# =========================
def _cells_to_4x4(cell_a: Set[int], cell_b: Set[int]) -> List[List[int]]:
    """
    Convert two side-by-side cells to a 4x4 bitmap (list of rows with 0/1).
    Left cell occupies columns 0-1; right cell columns 2-3.
    """
    grid = [[0]*4 for _ in range(4)]
    for d in cell_a:
        r, c = DOT_TO_COORD[d]
        grid[r][c] = 1
    for d in cell_b:
        r, c = DOT_TO_COORD[d]
        grid[r][c + 2] = 1
    return grid

def _grid4x4_rotate(grid: List[List[int]], angle: int) -> List[List[int]]:
    """Rotate a 4x4 0/1 grid by 0/90/180/270 degrees clockwise."""
    angle = angle % 360
    if angle == 0:
        return [row[:] for row in grid]
    if angle == 90:
        # (r, c) -> (c, 3 - r)
        return [[grid[3 - r][c] for r in range(4)] for c in range(4)]
    if angle == 180:
        return [[grid[3 - r][3 - c] for c in range(4)] for r in range(4)]
    if angle == 270:
        # (r, c) -> (3 - c, r)
        return [[grid[c][3 - r] for r in range(4)] for c in range(4)]
    raise ValueError("Angle must be one of {0,90,180,270}.")

def _grid4x4_to_pair(grid: List[List[int]]) -> (Set[int], Set[int]):
    """Convert a 4x4 grid back to two 4x2 cells (left, right)."""
    left: Set[int] = set()
    right: Set[int] = set()
    for r in range(4):
        for c in range(4):
            if grid[r][c]:
                if c < 2:
                    left.add(COORD_TO_DOT[(r, c)])
                else:
                    right.add(COORD_TO_DOT[(r, c - 2)])
    return left, right

def rotate_cells(cells: Dict[int, Set[int]], angle: int) -> Dict[int, Set[int]]:
    """
    Rotate cells:
      - 0°: no-op
      - 180°: per-cell rotation (valid for any length)
      - 90°/270°: rotate **pairwise** as 4×4 squares: (0,1), (2,3), ...
                   If the last cell has no pair, it is treated as paired with a blank.
    """
    angle = angle % 360
    if angle == 0:
        return dict(cells)

    # 180°: per-cell
    if angle == 180:
        out: Dict[int, Set[int]] = {}
        for i, ds in cells.items():
            # (r,c) -> (3-r,1-c)
            out[i] = {COORD_TO_DOT[(3 - DOT_TO_COORD[d][0], 1 - DOT_TO_COORD[d][1])] for d in ds}
        return out

    # 90°/270°: rotate pairwise across consecutive indices
    out: Dict[int, Set[int]] = {}
    if not cells:
        return out
    min_idx, max_idx = min(cells.keys()), max(cells.keys())
    i = min_idx
    while i <= max_idx:
        a = cells.get(i, set())
        b = cells.get(i + 1, set())  # may be empty if odd count
        grid = _cells_to_4x4(a, b)
        grid_r = _grid4x4_rotate(grid, angle)
        new_a, new_b = _grid4x4_to_pair(grid_r)
        if new_a:
            out[i] = new_a
        if new_b:
            out[i + 1] = new_b
        i += 2
    return out


# =========================
# High-level helpers
# =========================
def translate_braille_string(
    b: str,
    moves: str = "",
    rotate: int = 0,
    width: int = 2,
    clip_side: str = "left",
) -> str:
    for ch in b:
        if not is_braille_char(ch):
            raise ValueError(f"Non-braille character in input: {repr(ch)}")
    cells = cells_from_braille_string(b)
    # Apply rotation first, then moves
    cells = rotate_cells(cells, rotate)
    cells = apply_moves(cells, moves)
    return cells_to_string_fixed(cells, width=width, clip_side=clip_side)

def translate_frames(
    frames: List[str],
    moves: str = "",
    rotate: int = 0,
    width: int = 2,
    clip_side: str = "left",
) -> List[str]:
    out = []
    for f in frames:
        if not f:
            out.append(BRAILLE_BLANK * width)
            continue
        out.append(translate_braille_string(f, moves=moves, rotate=rotate, width=width, clip_side=clip_side))
    return out


# =========================
# CLI
# =========================
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Move (L/R/U/D) and rotate (0/90/180/270) Braille cells on strings or frames."
    )
    p.add_argument("--moves", type=str, default="",
                   help="Sequence like 'RRUDL'. Empty = no movement.")
    p.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270],
                   help="Rotate by 0/90/180/270 degrees clockwise (default: 0).")
    p.add_argument("--width", type=int, default=2,
                   help="Output width (number of cells). Default: 2.")
    p.add_argument("--clip-side", choices=["left", "right"], default="left",
                   help="When movement creates extra cells, which side to clip (default: left = keep rightmost).")
    p.add_argument("--show-codepoints", action="store_true",
                   help="Also print hex Unicode codepoints of the result(s).")

    # Input modes (mutually exclusive)
    g = p.add_mutually_exclusive_group(required=True)

    # Mode 1: two dot lists
    g.add_argument("--char1", nargs="+", type=int, help="Dots (1..8) for first cell.")
    p.add_argument("--char2", nargs="+", type=int, help="Dots (1..8) for second cell.")

    # Mode 2: a single braille string (any length)
    g.add_argument("--input-braille", type=str,
                   help="A braille string to translate (e.g., '⠏⠆').")

    # Mode 3: multiple frames (one or more braille strings)
    g.add_argument("--frames", nargs="+", type=str,
                   help="One or more braille frames (each often 2 chars).")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Mode 1: two dot lists
    if args.char1 is not None or args.char2 is not None:
        if args.char1 is None or args.char2 is None:
            parser.error("When using --char1/--char2, both must be provided.")
        cells = parse_initial_cells(args.char1, args.char2)
        cells = rotate_cells(cells, args.rotate)
        cells = apply_moves(cells, args.moves)
        out = cells_to_string_fixed(cells, width=args.width, clip_side=args.clip_side)
        print(out if out else "(all dots moved off-canvas)")
        if args.show_codepoints and out:
            print([f"U+{ord(c):04X}" for c in out])
        return

    # Mode 2: single braille string
    if args.input_braille is not None:
        out = translate_braille_string(args.input_braille, moves=args.moves,
                                       rotate=args.rotate, width=args.width,
                                       clip_side=args.clip_side)
        print(out if out else "(all dots moved off-canvas)")
        if args.show_codepoints and out:
            print([f"U+{ord(c):04X}" for c in out])
        return

    # Mode 3: frames list
    if args.frames is not None:
        outs = translate_frames(args.frames, moves=args.moves,
                                rotate=args.rotate, width=args.width,
                                clip_side=args.clip_side)
        for o in outs:
            print(o if o else "(all dots moved off-canvas)")
            if args.show_codepoints and o:
                print([f"U+{ord(c):04X}" for c in o])
        return


if __name__ == "__main__":
    main()
