"""Procedural grid generation plus win and hint logic."""

### -Imports- ###
import random

_Grid = list[list[int]]
_Cover = list[bool]
_Level = tuple[_Grid, list[int], list[int], _Grid]


### -Functions- ###
def generate_level(n: int) -> _Level:
    """Generate a random solvable puzzle level of size ``n x n``."""
    while True:
        grid = [[random.randint(1, 9) for _ in range(n)] for _ in range(n)]
        selected = [[False] * n for _ in range(n)]
        row_sums = [0] * n
        col_sums = [0] * n

        for r in range(n):
            num_to_select = random.randint(1, n)
            indices = random.sample(range(n), num_to_select)
            for c in indices:
                selected[r][c] = True
                row_sums[r] += grid[r][c]

        for c in range(n):
            for r in range(n):
                if selected[r][c]:
                    col_sums[c] += grid[r][c]

        if 0 not in col_sums:
            return grid, row_sums, col_sums, selected


def generate_level_letter(n: int, letter_char: str) -> _Level | tuple[None, None, None, None]:
    """Generate a level whose marked cells spell the given letter.

    Returns a 4-tuple ``(grid, row_sums, col_sums, selected)``, or four
    ``None`` values when the letter is not defined for this grid size.
    """
    cover_1d = letter(n, letter_char)
    if not cover_1d:
        return None, None, None, None

    grid = [[random.randint(1, 9) for _ in range(n)] for _ in range(n)]
    selected = [[False] * n for _ in range(n)]
    row_sums = [0] * n
    col_sums = [0] * n

    for r in range(n):
        for c in range(n):
            is_selected = cover_1d[r * n + c]
            selected[r][c] = is_selected
            if is_selected:
                row_sums[r] += grid[r][c]
                col_sums[c] += grid[r][c]

    return grid, row_sums, col_sums, selected


def letter(n: int, letter_char: str) -> _Cover:
    """Return the 1D boolean mask representing the given letter character."""
    cover: _Cover = []
    T = True
    F = False

    match letter_char:
        case "A":
            if n == 5:
                cover = [
                    F, T, T, T, F,
                    T, F, F, F, T,
                    T, T, T, T, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    F, F, T, T, T, F, F,
                    F, T, F, F, F, T, F,
                    T, F, F, F, F, F, T,
                    T, T, T, T, T, T, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                ]

        case "B":
            if n == 5:
                cover = [
                    T, T, T, T, F,
                    T, F, F, F, T,
                    T, T, T, T, F,
                    T, F, F, F, T,
                    T, T, T, T, F,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, T, T, T, T, T, F,
                ]

        case "C":
            if n == 5:
                cover = [
                    F, T, T, T, T,
                    T, F, F, F, F,
                    T, F, F, F, F,
                    T, F, F, F, F,
                    F, T, T, T, T,
                ]
            elif n == 7:
                cover = [
                    F, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, T,
                    F, T, T, T, T, T, F,
                ]

        case "D":
            if n == 5:
                cover = [
                    T, T, T, T, F,
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, T, T, T, F,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, F, F,
                    T, F, F, F, F, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, T, F,
                    T, T, T, T, T, F, F,
                ]

        case "E":
            if n == 5:
                cover = [
                    T, T, T, T, T,
                    T, F, F, F, F,
                    T, T, T, T, F,
                    T, F, F, F, F,
                    T, T, T, T, T,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, T,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, T, T, T, T, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, T, T, T, T, T, T,
                ]

        case "F":
            if n == 5:
                cover = [
                    T, T, T, T, T,
                    T, F, F, F, F,
                    T, T, T, T, F,
                    T, F, F, F, F,
                    T, F, F, F, F,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, T,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, T, T, T, T, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                ]

        case "F2":
            if n == 5:
                cover = [
                    T, T, T, T, T,
                    F, F, T, F, F,
                    F, T, T, T, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, T,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, T, T, T, T, T, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                ]

        case "G":
            if n == 5:
                cover = [
                    F, T, T, T, F,
                    T, F, F, F, F,
                    T, F, T, T, T,
                    T, F, F, F, T,
                    F, T, T, T, F,
                ]
            elif n == 7:
                cover = [
                    F, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, F,
                    T, F, F, T, T, T, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    F, T, T, T, T, T, F,
                ]

        case "H":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, T, T, T, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    T, T, F, F, F, T, T,
                    T, T, F, F, F, T, T,
                    T, T, F, F, F, T, T,
                    T, T, T, T, T, T, T,
                    T, T, F, F, F, T, T,
                    T, T, F, F, F, T, T,
                    T, T, F, F, F, T, T,
                ]

        case "I":
            if n == 5:
                cover = [
                    T, T, T, T, T,
                    F, F, T, F, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                    T, T, T, T, T,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, T,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    T, T, T, T, T, T, T,
                ]

        case "I2":
            if n == 5:
                cover = [
                    F, F, T, F, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                ]
            elif n == 7:
                cover = [
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                ]

        case "J":
            if n == 5:
                cover = [
                    F, F, T, T, T,
                    F, F, F, T, F,
                    F, F, F, T, F,
                    T, F, F, T, F,
                    F, T, T, F, F,
                ]
            elif n == 7:
                cover = [
                    F, F, F, T, T, T, T,
                    F, F, F, F, F, T, F,
                    F, F, F, F, F, T, F,
                    F, F, F, F, F, T, F,
                    T, F, F, F, F, T, F,
                    T, F, F, F, F, T, F,
                    F, T, T, T, T, F, F,
                ]

        case "K":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    T, F, F, T, F,
                    T, T, T, F, F,
                    T, F, F, T, F,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, T, F,
                    T, F, F, F, T, F, F,
                    T, T, T, T, F, F, F,
                    T, F, F, F, T, F, F,
                    T, F, F, F, F, T, F,
                    T, F, F, F, F, F, T,
                ]

        case "L":
            if n == 5:
                cover = [
                    T, F, F, F, F,
                    T, F, F, F, F,
                    T, F, F, F, F,
                    T, F, F, F, F,
                    T, T, T, T, T,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, T, T, T, T, T, T,
                ]

        case "M":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    T, T, F, T, T,
                    T, F, T, F, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    T, T, F, F, F, T, T,
                    T, F, T, F, T, F, T,
                    T, F, F, T, F, F, T,
                    T, F, T, F, T, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                ]

        case "N":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    T, T, F, F, T,
                    T, F, T, F, T,
                    T, F, F, T, T,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    T, T, F, F, F, F, T,
                    T, F, T, F, F, F, T,
                    T, F, F, T, F, F, T,
                    T, F, F, F, T, F, T,
                    T, F, F, F, F, T, T,
                    T, F, F, F, F, F, T,
                ]

        case "O":
            if n == 5:
                cover = [
                    F, T, T, T, F,
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                    F, T, T, T, F,
                ]
            elif n == 7:
                cover = [
                    F, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    F, T, T, T, T, T, F,
                ]

        case "P":
            if n == 5:
                cover = [
                    T, T, T, T, F,
                    T, F, F, F, T,
                    T, T, T, T, F,
                    T, F, F, F, F,
                    T, F, F, F, F,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, T, T, T, T, T, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                    T, F, F, F, F, F, F,
                ]

        case "Q":
            if n == 5:
                cover = [
                    F, T, T, T, F,
                    T, F, F, F, T,
                    T, F, T, F, T,
                    T, F, F, T, F,
                    F, T, T, F, T,
                ]
            elif n == 7:
                cover = [
                    F, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, T, F, T,
                    T, F, F, F, F, T, F,
                    F, T, T, T, T, F, T,
                ]

        case "R":
            if n == 5:
                cover = [
                    T, T, T, T, F,
                    T, F, F, F, T,
                    T, T, T, T, F,
                    T, F, F, T, F,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, F, F,
                    T, F, F, F, F, T, F,
                    T, F, F, F, F, T, F,
                    T, T, T, T, T, F, F,
                    T, F, F, F, T, F, F,
                    T, F, F, F, F, T, F,
                    T, F, F, F, F, F, T,
                ]

        case "S":
            if n == 5:
                cover = [
                    F, T, T, T, T,
                    T, F, F, F, F,
                    F, T, T, T, F,
                    F, F, F, F, T,
                    T, T, T, T, F,
                ]
            elif n == 7:
                cover = [
                    F, T, T, T, T, T, F,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, F,
                    F, T, T, T, T, T, F,
                    F, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    F, T, T, T, T, T, F,
                ]

        case "T":
            if n == 5:
                cover = [
                    T, T, T, T, T,
                    F, F, T, F, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, T,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                ]

        case "U":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                    F, T, T, T, F,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    F, T, T, T, T, T, F,
                ]

        case "V":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, F, F, F, T,
                    F, T, F, T, F,
                    F, F, T, F, F,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    F, T, F, F, F, T, F,
                    F, T, F, F, F, T, F,
                    F, F, T, F, T, F, F,
                    F, F, T, F, T, F, F,
                    F, F, F, T, F, F, F,
                ]

        case "W":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    T, F, F, F, T,
                    T, F, T, F, T,
                    T, T, F, T, T,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, F, F, F, T,
                    T, F, F, T, F, F, T,
                    T, F, T, F, T, F, T,
                    T, T, F, F, F, T, T,
                    T, F, F, F, F, F, T,
                ]

        case "X":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    F, T, F, T, F,
                    F, F, T, F, F,
                    F, T, F, T, F,
                    T, F, F, F, T,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    F, T, F, F, F, T, F,
                    F, F, T, F, T, F, F,
                    F, F, F, T, F, F, F,
                    F, F, T, F, T, F, F,
                    F, T, F, F, F, T, F,
                    T, F, F, F, F, F, T,
                ]

        case "Y":
            if n == 5:
                cover = [
                    T, F, F, F, T,
                    F, T, F, T, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                    F, F, T, F, F,
                ]
            elif n == 7:
                cover = [
                    T, F, F, F, F, F, T,
                    F, T, F, F, F, T, F,
                    F, F, T, F, T, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                    F, F, F, T, F, F, F,
                ]

        case "Z":
            if n == 5:
                cover = [
                    T, T, T, T, T,
                    F, F, F, T, F,
                    F, F, T, F, F,
                    F, T, F, F, F,
                    T, T, T, T, T,
                ]
            elif n == 7:
                cover = [
                    T, T, T, T, T, T, T,
                    F, F, F, F, F, T, F,
                    F, F, F, F, T, F, F,
                    F, F, F, T, F, F, F,
                    F, F, T, F, F, F, F,
                    F, T, F, F, F, F, F,
                    T, T, T, T, T, T, T,
                ]

    return cover


def check_win(grid: _Grid, user_sel: _Grid, row_sums: list[int], col_sums: list[int], n: int) -> bool:
    """Return ``True`` if every row and column matches its target sum."""
    for r in range(n):
        if sum(grid[r][c] for c in range(n) if user_sel[r][c]) != row_sums[r]:
            return False
            
    for c in range(n):
        if sum(grid[r][c] for r in range(n) if user_sel[r][c]) != col_sums[c]:
            return False
            
    return True


def find_hint(
    solution: _Grid, user_sel: _Grid, user_dimmed: _Grid, n: int
) -> tuple[int, int, bool] | None:
    """Return one correct cell correction or selection for the player.

    Returns:
        A ``(row, column, should_select)`` tuple, or ``None`` when the
        board already matches the solution.
    """
    problems = []
    for r in range(n):
        for c in range(n):
            if solution[r][c] and not user_sel[r][c]:
                problems.append((r, c, True))
            elif not solution[r][c] and user_sel[r][c]:
                problems.append((r, c, False))

    if not problems:
        return None
        
    return random.choice(problems)
