### Mati (Mathematics and tactic intelligence) ###
### V0.6.1 (Beta V1.0.22) ###
### Author: Janosch Klawatsch, 2026-08-27 ###
### export file V0.6.1 ###

### Structure-Plan ###
# - audio.py - Sound generation #
# - config.py - Constants #
# - export.py - Video creation and saving #
# - game.py - Main game handling #
# - lang.py - Translation logic #
# - level.py - Level generation and win checking #
# - main.py - Entry point and main loop #
# - persistence.py - Saving and loading .mati files #
# - replay.py - Rebuilding games #
# - screens.py - Screen construction #
# - terminal.py - Terminal handling #
# - widgets.py - Drawing functions #


### -Imports- ###

### External ###
from array import array # For generating audio data
import av               # For direct access to FFmpeg libraries
import functools        # To cache repeated font renders
import numpy as np      # Required by PyAV
import os               # For path handling and temporary folders
import pygame as pg     # 'Game engine' and rendering framework

from typing import Any, Dict, List, Tuple, Optional # For type annotations

### Own ###
import config as con          # Provides the program constants
from level import check_win   # Checks whether the match has been won
import replay as re           # Rebuilds the states of a match
from widgets import get_fonts # Provides the exact same fonts as the game


### -Functions- ###

@functools.lru_cache(maxsize=4096)
def _render_text_cached(
    font: pg.font.Font,
    text: str,
    color: Tuple[int, int, int],
) -> pg.Surface:
    """Renders text once and reuses the result for later calls with the same
    font, text, and color.
    
    Grid digits and sum labels are rendered repeatedly across cells, states,
    and frames. Caching avoids repeating the comparatively expensive font
    rasterization process for identical text.
    
    Args:
        font (pg.font.Font): Pygame Font object used to render the text.
        text (str): String containing the text to render.
        color (Tuple[int, int, int]): RGB tuple defining the text color.

    Returns:
        pg.Surface: The rendered text surface, either newly created or
        retrieved from cache.
    """
    return font.render(text, True, color)


def _blit_centered(
    surf: pg.Surface,
    font: pg.font.Font,
    text: str,
    color: Tuple[int, int, int],
    x: int, 
    y: int,
) -> None:
    """Renders text and blits it centered at a specified (x, y) coordinate.

    Args:
        surf (pg.Surface): Target Pygame Surface onto which the text is drawn.
        font (pg.font.Font): Pygame Font object used to render the text.
        text (str): String containing the text to render.
        color (Tuple[int, int, int]): RGB tuple defining the text color.
        x (int): Horizontal pixel coordinate of the text center.
        y (int): Vertical pixel coordinate for the text center.
    """
    # Retrieve the rendered text from the cache or render it if necessary.
    obj = _render_text_cached(font, text, color)
    
    # Create a rectangle centered at the target (x, y) position
    rect = obj.get_rect(center=(x, y))
    
    # Draw the text surface onto the destination surface.
    surf.blit(obj, rect)
    
    
def _make_fonts(scale: int) -> Tuple[pg.font.Font, pg.font.Font, pg.font.Font]:
    """Creates fonts with the appropriate sizes for the given scale factor.

    Args:
        scale (int): Factor used to scale the font sizes. 
            (Is expected to be 1 or greater)

    Returns:
        Tuple: The three required fonts in the following order:
            normal font, tiny font, and label font.
    """
    # Calculate the font sizes based on the scale factor.
    font_size = 28 * scale
    tiny_size = 16 * scale
    label_size = 15 * scale
    
    # Create the fonts with their respective sizes and styles.
    font = pg.font.SysFont("arial", font_size, bold=True)
    tiny_font = pg.font.SysFont("arial", tiny_size)
    label_font = pg.font.SysFont("arial", label_size, bold=True)
    
    return font, tiny_font, label_font

 
def _frame_size(
    n: int,
    cell_size: int,
    margin: int,
    header_height: int,
) -> Tuple[int, int]:
    """Calculates the total pixel dimensions of an exported video frame.
    
    The frame contains an (N + 1) x (N + 1) grid, including the sum headers,
    outer margins, and an additional top header area for the playback time.
    
    Args:
        n (int): Dimension of the main grid (N x N).
        cell_size (int): Pixel size of each scaled grid cell.
        margin (int): Scaled outer margin in pixels.
        header_height (int): Scaled height of the top header area.

    Returns:
        Tuple[int, int]: A tuple containing the total frame width and height
        in pixels, respectively.
    """
    # Calculate the total width of the grid and its outer margins.
    side = (n + 1) * cell_size + margin * 2 
    
    # Add the top header area to the total frame height.
    height = side + header_height
    
    return side, height


def _compute_fulfilled(
    grid: List[List[int]],
    sel: List[List[bool]],
    row_sums: List[int],
    col_sums: List[int],
    n: int,
) -> Tuple[List[bool], List[bool]]:
    """Calculates row/column target fulfillment for a given selection state.

    Args:
        grid (List[List[int]]): The puzzle's numeric grid.
        sel (List[List[bool]]): 2D boolean grid of currently selected cells.
        row_sums (List[int]): Target sums for each row.
        col_sums (List[int]): Target sums for each column.
        n (int): Dimension of the grid (N x N).

    Returns:
        Tuple[List[bool], List[bool]]: Fulfillment flags for each row and 
        each column, respectively.
    """
    row_fulfilled = [
        sum(grid[r][c] for c in range(n) if sel[r][c]) == row_sums[r]
        for r in range(n)
    ]
    
    col_fulfilled = [
        sum(grid[r][c] for r in range(n) if sel[r][c]) == col_sums[c]
        for c in range(n)
    ]
    
    return row_fulfilled, col_fulfilled


def _compute_dimmed(
    dimmed: List[List[bool]],
    sel: List[List[bool]],
    row_fulfilled: List[bool],
    col_fulfilled: List[bool],
    n: int,
) -> List[List[bool]]:
    """Derives the effective per-cell dimmed state for a selection state.
    
    A cell counts as dimmed if it was explicitly dimmed by the player, or if
    its row/column target is fulfilled while the cell itself is unselected.

    Args:
        dimmed (List[List[bool]]): 2D boolean grid of explicitly dimmed cells.
        sel (List[List[bool]]): 2D boolean grid of currently selected cells.
        row_fulfilled (List[bool]): Fulfillment flag for each row.
        col_fulfilled (List[bool]): Fulfillment flag for each column.
        n (int): Dimension of the grid (N x N).

    Returns:
        List[List[bool]]: 2D boolean grid of the effective dimmed state.
    """
    return [
        [
            dimmed[r][c] or ((row_fulfilled[r] or col_fulfilled[c]) and not sel[r][c])
            for c in range(n)
        ]
        for r in range(n)
    ]
    
    
def _derive_render_state(
    data: Dict,
    n: int,
    sel: List[List[bool]],
    dimmed: List[List[bool]],
) -> Dict:
    """Bundles the values needed to render of diff one reconstructed state.

    Args:
        data (Dict): Dictionary containing the puzzle data.
        n (int): Dimension of the main grid (N x N).
        sel (List[List[bool]]): 2D boolean grid of currenty selected cells.
        dimmed (List[List[bool]]): 2D boolen grid of explicitly dimmed cells.

    Returns:
        Dict: Selection grid, effective dimmed grid, and row/column
        fulfillment flags for this state.
    """
    row_fulfilled, col_fulfilled = _compute_fulfilled(
        data["grid"],
        sel,
        data["row_sums"],
        data["col_sums"],
        n,
    )
    
    is_dimmed = _compute_dimmed(
        dimmed,
        sel,
        row_fulfilled,
        col_fulfilled,
        n,
    )
    
    return {
        "sel": sel,
        "is_dimmed": is_dimmed,
        "row_fulfilled": row_fulfilled,
        "col_fulfilled": col_fulfilled,
    }
    
    
def _board_style(ultra: bool) -> Dict:
    """Resolves the color palette for the board, depending on Ultra mode.
    
    The palette is constant for the whole export (Ultra mode never changes
    mid-replay), so it is resolved once and reused for every render call.

    Args:
        ultra (bool): Whether the game is runnung in Ultra mode.

    Returns:
        Dict: Named colors used across the static base, cells, and headers.
    """
    return {
        "bg_color": (28, 24, 12) if ultra else con.BG_COLOR,
        "sum_color": con.SHINE if ultra else con.TARGET_COLOR,
        "text_color_normal": con.WHITE if ultra else con.TEXT_COLOR,
        "dim_color": (110, 100, 70) if ultra else con.DIMMED_TEXT_COLOR,
        "cell_fill_color": (52, 46, 26) if ultra else con.BG_COLOR,
        "cell_border_color": con.SHINE if ultra else con.GRID_COLOR,
        "outer_border_color": con.SHINE if ultra else con.BLACK,
    }
    
    
def _render_static_base(
    n: int,
    cell_size: int,
    margin: int,
    header_height: int,
    ultra: bool,
    label_font: pg.font.Font,
    style: Dict,
    scale: int = 1,
) -> pg.Surface:
    """Renders the part of the board that never changes across a replay.
    
    Covers the background fill, the outer grid border, and the Ultra label.
    These depend only on the grid size and Ultra mode, never on the replay
    state, so this is rendered exactly once per export and then reused as
    the base of the persistent board surface for every state.

    Args:
        n (int): Dimension of the main grid (N x N).
        cell_size (int): Scaled size of each grid cell in pixels.
        margin (int): Scaled outer margin in pixels.
        header_height (int): Scaled height of the top header area.
        ultra (bool): Whether the game is running in Ultra mode.
        label_font (pg.font.Font): Font used for the Ultra label.
        style (Dict): Color palette from ``_board_style``.
        scale (int): Scale factor used for rendering. Defaults to 1.

    Returns:
        pg.Surface: The static board base, without cells or headers.
    """
    w_px, h_px = _frame_size(
        n,
        cell_size,
        margin,
        header_height,
    )
    
    surf = pg.Surface((w_px, h_px))
    surf.fill(style["bg_color"])
    
    offset_x = margin
    offset_y = margin + header_height
    border_width = 4 * scale if ultra else 2 * scale
    
    pg.draw.rect(
        surf,
        style["outer_border_color"],
        (
            offset_x - 2 * scale,
            offset_y - 2 * scale,
            (n + 1) * cell_size + 4 * scale,
            (n + 1) * cell_size + 4 * scale,
        ),
        border_width,
    )
    
    if ultra:
        header_scale = cell_size / con.CELL_SIZE
        
        _blit_centered(
            surf,
            label_font,
            "ULTRA",
            con.SHINE,
            w_px - margin,
            int(margin / 2 + 8 * header_scale),
        )
        
    return surf


def _render_cell(
    surf: pg.Surface,
    grid: List[List[int]],
    r: int,
    c: int,
    selected: bool,
    is_dimmed: bool,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: Dict,
    scale: int,
) -> None:
    """(Re-)draws a single grid cell, overwriting whatever was there before.
    
    Used both for the one-time initial board render and for patching in a
    single changed cell onto the persistent board surface, so it always
    repaints the full resting background first to erase any previous
    selection fill.

    Args:
        surf (pg.Surface): Persistent board surface to draw onto.
        grid (List[List[int]]): The puzzle's numeric grid.
        r (int): Row index of the cell.
        c (int): Column index of the cell.
        selected (bool): Whether the cell is currently selected.
        is_dimmed (bool): Whether the cell's value should render dimmed.
        font (pg.font.Font): Font used for the cell value.
        cell_size (int): Scaled size of each grid cell in pixels.
        offset_x (int): Horizontal pixel offset of the grid origin.
        offset_y (int): Vertical pixel offset of the grid origin.
        style (Dict): Color palette from ``_board_style``.
        scale (int): Scale factor used for the border width.
    """
    rect = pg.Rect(
        offset_x + (c + 1) * cell_size,
        offset_y + (r + 1) * cell_size,
        cell_size,
        cell_size,
    )
    
    # Repaint the resting background first to erase a previous selection fill.
    pg.draw.rect(surf, style["cell_fill_color"], rect)
    
    if selected:
        pg.draw.rect(surf, con.SELECTED_COLOR, rect)
    
    pg.draw.rect(surf, style["cell_border_color"], rect, 2 * scale)
    
    color = style["dim_color"] if is_dimmed else style["text_color_normal"]
    
    _blit_centered(
        surf,
        font, 
        str(grid[r][c]),
        color,
        rect.centerx,
        rect.centery,
    )
    
    
def _render_row_header(
    surf: pg.Surface,
    row_sums: List[int],
    r: int,
    fulfilled: bool,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: Dict,
    scale: int,
) -> None:
    """(Re-)draws a row's target-sum label and completion ring.

    Args:
        surf (pg.Surface): Persistent board surface to draw onto.
        row_sums (List[int]): Target sums for each row.
        r (int): Row index of the header cell.
        fulfilled (bool): Whether the row's target is currently fulfilled.
        font (pg.font.Font): Font used for the sum label.
        cell_size (int): Scaled size of each grid cell in pixels.
        offset_x (int): Horizontal pixel offset of the grid origin.
        offset_y (int): Vertical pixel offset of the grid origin.
        style (Dict): Color palette from ``_board_style``.
        scale (int): Scale factor used for the ring radius.
    """
    rect = pg.Rect(
        offset_x,
        offset_y + (r + 1) * cell_size,
        cell_size,
        cell_size,
    )
    
    # Repaint the background first to erase a previous completion ring.
    pg.draw.rect(surf, style["bg_color"], rect)
    
    _blit_centered(
        surf, 
        font,
        str(row_sums[r]),
        style["sum_color"],
        rect.centerx,
        rect.centery,
    )
    
    if fulfilled:
        radius = cell_size // 2 - 4 * scale
        
        pg.draw.circle(
            surf, 
            con.GREEN,
            rect.center,
            radius,
            max(2, cell_size // 30),
        )
        
        
def _render_col_header(
    surf: pg.Surface,
    col_sums: List[int],
    c: int,
    fulfilled: bool,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: Dict,
    scale: int,
) -> None:
    """(Re-)draws a column's target-sum label and completion ring.

    Args:
        surf (pg.Surface): Persistent board surface to draw onto.
        col_sums (List[int]): Target sums for each column.
        c (int): Column index of the header cell.
        fulfilled (bool): Whether the column's target is currently fulfilled.
        font (pg.font.Font): Font used for the sum label.
        cell_size (int): Scaled size of each grid cell in pixels.
        offset_x (int): Horizontal pixel offset of the grid origin.
        offset_y (int): Vertical pixel offset of the grid origin.
        style (Dict): Color palette from ``_board_style``.
        scale (int): Scale factor used for the ring radius.
    """
    rect = pg.Rect(
        offset_x + (c + 1)  * cell_size,
        offset_y,
        cell_size,
        cell_size,
    )
    
    # Repaint the background first to erase a previous completion ring.
    pg.draw.rect(surf, style["bg_color"], rect)
    
    _blit_centered(
        surf,
        font,
        str(col_sums[c]), 
        style["sum_color"],
        rect.centerx, 
        rect.centery,
    )
    
    if fulfilled:
        radius = cell_size // 2 - 4 * scale
        
        pg.draw.circle(
            surf,
            con.GREEN,
            rect.center,
            radius,
            max(2, cell_size // 30),
        )
        
        
def _render_full_board(
    surf: pg.Surface,
    data: Dict,
    n: int,
    render_state: Dict,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: Dict,
    scale: int,
) -> None:
    """Draws every cell and header once, onto the static base surface.
    
    This is the only full O(n^2) board draw in an export: it happens once,
    for the very first replay state. Every later state is patched in via 
    ``_apply_board_delta`` instead of being redrawn from scratch.

    Args:
        surf (pg.Surface): Static base surface to draw onto (mutated in place).
        data (Dict): Dictionary containing teh puzzle data.
        n (int): Dimension of the main grid (N x N).
        render_state (Dict): Render state from ``_derive_render_state`` for
            the first replay state.
        font (pg.font.Font): Font used fro grid values and sum labels.
        cell_size (int): Scaled size of each grid cell in pixels.
        offset_x (int): Horizontal pixel offset of the grid origin.
        offset_y (int): Vertical pixel offset of the grid origin.
        style (Dict): Color palette from ``_board_style``.
        scale (int): Scale factor used for border widths.
    """
    grid, row_sums, col_sums = data["grid"], data["row_sums"], data["col_sums"]
    
    for r in range(n):
        _render_row_header(
            surf,
            row_sums,
            r,
            render_state["row_fulfilled"][r],
            font,
            cell_size,
            offset_x,
            offset_y,
            style,
            scale,
        )
        
    for c in range(n):
        _render_col_header(
            surf,
            col_sums,
            c,
            render_state["col_fulfilled"][c],
            font,
            cell_size,
            offset_x,
            offset_y,
            style,
            scale,
        )
        
    for r in range(n):
        for c in range(n):
            _render_cell(
                surf,
                grid,
                r,
                c,
                render_state["sel"][r][c],
                render_state["is_dimmed"][r][c],
                font,
                cell_size,
                offset_x,
                offset_y, style,
                scale,
            )
            
            
def _apply_board_delta(
    surf: pg.Surface,
    data: Dict,
    n: int,
    prev: Dict,
    new: Dict,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: Dict,
    scale: int,
) -> None:
    """Patches the persistent board surface for one advance in replay time.
    
    Compares the previous and new render state and repaints only the cells
    and headers whose appearance actually changed - directly touched cells,
    plus any cell whose dimmed state flipped as a ripple effect of a 
    row/column target becoming (un)fulfilled. Untouched cells, borders, and 
    sum labels are left exactly as they were, so the cost of this call scales
    with how much of the board actually changes, not with the grid size.

    Args:
        surf (pg.Surface): Persistent board surface to patch in place.
        data (Dict): Dictionary containing the puzzle data.
        n (int): Dimension of the main grid (N x N).
        prev (Dict): Render state the surface currenty reflects.
        new (Dict): Render state to advance the surface to.
        font (pg.font.Font): Font used for grid values and sum labels.
        cell_size (int): Scaled size of each grid cell in pixels.
        offset_x (int): Horizontal pixel offset of the grid origin.
        offset_y (int): Vertical pixel offset of the grid origin.
        style (Dict): Color palette from ``_board_style``.
        scale (int): Scale factor used for border widths.
    """
    grid, row_sums, col_sums = data["grid"], data["row_sums"], data["col_sums"]
    
    for r in range(n):
        if prev["row_fulfilled"][r] != new["row_fulfilled"][r]:
            _render_row_header(
                surf,
                row_sums,
                r,
                new["row_fulfilled"][r],
                font,
                cell_size,
                offset_x,
                offset_y,
                style,
                scale,
            )
    
    for c in range(n):
        if prev["col_fulfilled"][c] != new["col_fulfilled"][c]:
            _render_col_header(
                surf,
                col_sums,
                c,
                new["col_fulfilled"][c],
                font,
                cell_size,
                offset_x,
                offset_y,
                style,
                scale,
            )
            
    for r in range(n):
        prev_sel_row, prev_dim_row = prev["sel"][r], prev["is_dimmed"][r]
        new_sel_row, new_dim_row = new["sel"][r], new["is_dimmed"][r]
        
        for c in range(n):
            if prev_sel_row[c] != new_sel_row[c] or prev_dim_row[c] != new_dim_row[c]:
                _render_cell(
                    surf,
                    grid,
                    r,
                    c,
                    new_sel_row[c],
                    new_dim_row[c],
                    font, 
                    cell_size, 
                    offset_x,
                    offset_y,
                    style,
                    scale,
                )
                
                
def _draw_action_highlight(
    surf: pg.Surface,
    highlight_cell: Optional[Tuple[int, int]],
    highlight_color: Optional[Tuple[int, int, int]],
    action_time_ms: int,
    display_ms: int,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    scale: int,
) -> None:
    """Draws the fading action-highlight border for the current frame.
    
    The highlight fades out 1500ms after its action, which depends on the
    elapsed playback time rather than on the replay state. It is therefore
    drawn per frame on a copy of the persistent board, exactly like the time
    overlay, instead of being baked into the cached/patched board.

    Args:
        surf (pg.Surface): Per-frame board copy to draw onto.
        highlight_cell (Optional[Tuple[int, int]]): Row/column of the 
            highlighted cell, or None.
        highlight_color (Optional[Tuple[int, int, int]]): RGB color of the 
            highlighted border, or None to use the default gold color.
        action_time_ms (int): Timestamp of the highlighted action.
        display_ms (int): Current playback time in milliseconds.
        cell_size (int): Scaled size of each grid cell in pixels.
        offset_x (int): Horizontal pixel offset of the grid origin.
        offset_y (int): Vertical pixel offset of the grid origin.
        scale (int): Scale factor used for the border width.
    """
    if highlight_cell is None or (display_ms - action_time_ms) >= 1500:
        return
    
    r, c = highlight_cell
    
    rect = pg.Rect(
        offset_x + (c + 1) * cell_size,
        offset_y + (r + 1) * cell_size,
        cell_size,
        cell_size,
    )
    
    pg.draw.rect(
        surf, 
        highlight_color or con.GOLD, 
        rect,
        4 * scale,
    )


def _render_board(
    data: Dict,
    n: int,
    sel: List[List[bool]],
    dimmed: List[List[bool]],
    highlight_cell: Optional[Tuple[int, int]],
    highlight_color: Optional[Tuple[int, int, int]],
    time_ms: int,
    font: pg.font.Font,
    tiny_font: pg.font.Font,
    label_font: pg.font.Font,
    cell_size: int,
    margin: int,
    header_height: int,
    ultra: bool,
    scale: int = 1,
    action_time_ms: int = 0,
) -> pg.Surface:
    """Renders the static board state for a replay video frame.
    
    Draws the board for a given game state, including row and column target
    sums, grid values, cell selections, dimming states, action highlights,
    completion indicators, and the Ultra label.
    
    The elapsed-time overlay is intentionally excluded because it changes
    between frames. The rendered board can therefore be reused for multiple
    output frames until the game state changes.

    Args:
        data (Dict): Dictionary containing the puzzle data.
        n (int): Dimension of the main grid (N x N)
        sel (List[List[bool]]): 2D boolen grid where True indicates a 
            selected cell.
        dimmed (List[List[bool]]): 2D boolean grid where True indicates a 
            manually dimmed cell.
        highlight_cell (Optional[Tuple[int, int]]): Row and column of the
            currently highlighted cell, or None.
        highlight_color (Optional[Tuple[int, int, int]]): RGB color of the
            action highlight border, or None to use the default gold color.
        time_ms (int): Current elapsed game time in milliseconds.
        font (pg.font.Font): Primary font used for grid values and sum labels.
        # tiny_font (pg.font.Font): Small font used for the header time.
        label_font (pg.font.Font): Smallest font used for the Ultra label.
        cell_size (int): Scaled size of each grid cell in pixels.
        margin (int): Scaled outer margin in pixels.
        header_height (int): Scaled height of the top header area.
        ultra (bool): Whether the game is running in Ultra mode.
        scale (int): Scale factor used for rendering. Defaults to 1.
        action_time_ms (int): Timestamp of the highlighted action
            in milliseconds. Defaults to 0.

    Returns:
        pg.Surface: A Pygame Surface containing the rendered board state,
        excluding the elapsed-time overlay.
    """
    w_px, h_px = _frame_size(n, cell_size, margin, header_height)
    surf = pg.Surface((w_px, h_px))
    bg_color = (28, 24, 12) if ultra else con.BG_COLOR
    surf.fill(bg_color)
    
    # Grid positioning offsets
    offset_x = margin
    offset_y = margin + header_height
    
    grid = data["grid"]
    row_sums = data["row_sums"]
    col_sums = data["col_sums"]
    
    # Calculate fulfillment status for each row and column based on current selections
    row_fulfilled = [
        sum(grid[r][c] for c in range(n) if sel[r][c]) == row_sums[r]
        for r in range(n)
    ]
    col_fulfilled = [
        sum(grid[r][c] for r in range(n) if sel[r][c]) == col_sums[c]
        for c in range(n)
    ]
    
    # Define the colors depending on if the game is ultra mode played or not.
    sum_color = con.SHINE if ultra else con.TARGET_COLOR
    text_color_normal = con.WHITE if ultra else con.TEXT_COLOR
    dim_color = (110, 100, 70) if ultra else con.DIMMED_TEXT_COLOR
    cell_bg = (52, 46, 26) if ultra else con.WHITE
    border_color = con.SHINE if ultra else con.GRID_COLOR
    
    # --- Render Target Sums ---
    # Draw column target sums along top header row
    for c in range(n):
        cx = offset_x + (c + 1) * cell_size + cell_size // 2
        cy = offset_y + cell_size // 2
        _blit_centered(surf, font, str(col_sums[c]), sum_color, cx, cy)
    
    # Draw row target sums along left margin column
    for r in range(n):
        cx = offset_x + cell_size // 2
        cy = offset_y + (r + 1) * cell_size + cell_size // 2
        _blit_centered(surf, font, str(row_sums[r]), sum_color, cx, cy)
        
    # --- Render Main Grid Cells ---
    for r in range(n):
        for c in range(n):
            rect = pg.Rect(
                offset_x + (c + 1) * cell_size,
                offset_y + (r + 1) * cell_size,
                cell_size,
                cell_size,
            )
            
            # Cell is dimmed if explicitly set, or if row/column sums is fulfilled without selection
            is_dimmed = dimmed[r][c] or (
                (row_fulfilled[r] or col_fulfilled[c]) and not sel[r][c]
            )
            
            # The game is ultra mode, show it
            if ultra:
                pg.draw.rect(surf, cell_bg, rect)
            
            # Fill cell background if selected
            if sel[r][c]:
                pg.draw.rect(surf, con.SELECTED_COLOR, rect)
            
            # Inner cell border
            pg.draw.rect(surf, border_color, rect, 2 * scale)
            
            # Draw cell value text
            color = dim_color if is_dimmed else text_color_normal
            _blit_centered(surf, font, str(grid[r][c]), color, rect.centerx, rect.centery)
            
            # Draw action highlight border on the active cell
            if highlight_cell == (r, c) and (time_ms - action_time_ms) < 1500:
                pg.draw.rect(surf, highlight_color or con.GOLD, rect, int(4 * scale))
                
    # Redefine the border and draw it
    border_color = con.SHINE if ultra else con.BLACK
    border_width = 4 * scale if ultra else 2 * scale
    pg.draw.rect(
        surf,
        border_color,
        (
            offset_x,
            offset_y,
            (n + 1) * cell_size,
            (n + 1) * cell_size,
        ),
        border_width,
    )
    
    # --- Render Target Completion Rings ---
    half_cell = cell_size // 2
    radius = half_cell - 4
    
    # Row target completion indicators
    for r in range(n):
        if row_fulfilled[r]:
            cx = offset_x + half_cell
            cy = offset_y + (r + 1) * cell_size + half_cell
            pg.draw.circle(surf, con.GREEN, (cx, cy), radius, max(2, cell_size // 30))
            
    # Column target completion indicators
    for c in range(n):
        if col_fulfilled[c]:
            cx = offset_x + (c + 1) * cell_size + half_cell
            cy = offset_y + half_cell
            pg.draw.circle(surf, con.GREEN, (cx, cy), radius, max(2, cell_size // 30))
            
    # And ultra label (static per state, does not depend on the elapsed time)
    if ultra:
        header_scale = cell_size / con.CELL_SIZE
        _blit_centered(surf, label_font, "ULTRA", con.SHINE, w_px - margin, int(margin / 2 + 8 * header_scale))
        
    return surf


def _draw_time_overlay(
    surf: pg.Surface,
    time_ms: int,
    tiny_font: pg.font.Font,
    text_color: Tuple[int, int, int],
    w_px: int,
    margin: int,
    cell_size: int,
) -> None:
    """Draws the elapsed-time overlay onto an already rendered board surface.
    
    This is kept separate from _render_board because the board only changes
    when the game state changes, while the elapsed time changes between
    output frames. Seperating the two allows the caller to cache and reuse
    the rendered board and update only time display for each frame.

    Args:
        surf (pg.Surface): Board surface onto which the time overlay is drawn.
        time_ms (int): Current playback time in milliseconds.
        tiny_font (pg.font.Font): Pygame Font object used for the time display.
        text_color (Tuple[int, int, int]): RGB color of the time text..
        w_px (int): Total frame width in pixels.
        margin (int): Scaled outer margin in pixels.
        cell_size (int): Scaled cell size used to calculate the header scale.
    """
    seconds = (time_ms // 1000) % 60
    minutes = (time_ms // 60000)
    ms = time_ms % 1000
    
    time_str = (
        f"{minutes}:{seconds:02}:{ms:03}min"
        if minutes
        else f"{seconds:02}:{ms:03}s"
    )
    header_scale = cell_size / con.CELL_SIZE
     
    _blit_centered(
        surf,
        tiny_font,
        f"Time: {time_str}",
        text_color,
        w_px // 2,
        int(margin / 2 + 8 * header_scale),
    )
    
    
def _display_actions(data: Dict) -> List[Dict]:
    """Generates the complete timeline of game actions with a synthetic
    starting frame at timestamp t=0.
    
    The synthetic starting entry represents the initial board state before
    any player actions have occurred. It is prepended to the recorded actions
    so that the replay always has an explicit starting point.

    Args:
        data (Dict): Replay data containing the recorded ``actions`` list.

    Returns:
        List[Dict]: A list of action dictionaries beginning with the synthetic
        starting entry, followed by all recorded player actions.
    """
    # Retrieve the recorded actions or use an empty list if none are present.
    actions = data.get("actions", [])
    
    # Create a synthetic entry representing the initial state before
    # any player actions have occurred.
    start_entry = {
        "time": 0,
        "type": "Start",
        "r": None,
        "c": None,
        "synthetic": True,
    }
    
    return [start_entry] + actions


def _build_states(data: Dict) -> Tuple[int, List[Tuple]]:
    """Precalculates the board display state after each recorded game action.
    
    Reconstructs the selected cells, dimmed cells, and action highlight
    information for every point in the replay timeline. The resulting states
    can be used by the video exporter to render each game state once and
    reuse it for all frames until the next action.
    
    Args:
        data (Dict): Dictionary containing the grid configuration and play 
            history.

    Returns:
        Tuple[int, List[Tuple]]:
            - n (int): Grid dimension (N x N).
            - states (List[Tuple]): List of state tuples containing
                (timestamp_ms, selected_cells, dimmed_cells, highlight_cell,
                highlight_color).
    """
    n = len(data["grid"])
    display_actions = _display_actions(data)
    states = []
    
    # Reconstruct the board state at each point in the replay timeline.
    for i in range(len(display_actions)):
        real_index = i - 1
        
        sel, dimmed, hints_used, play_time_i, last_action = re.reconstruct_state(
            data,
            real_index
        )
        
        # Apply highlight information for a valid player action.
        if i > 0 and last_action:
            hl_cell = (last_action["r"], last_action["c"])
            
            if last_action.get("Undone"):
                hl_color = con.UNDONE_COLOR
            else:
                hl_color = con.ACTION_HIGHLIGHT_COLOR.get(
                    last_action.get("type"),
                    con.GOLD
                )
        else:
            # Initial state before any player actions occurs.
            hl_cell, hl_color = None, None
        
        states.append(
            (display_actions[i]["time"], sel, dimmed, hl_cell, hl_color)
        )
        
    return n, states


def _find_win_time(
    data: Dict,
    states: List[Tuple],
    n: int,
) -> Optional[int]:
    """Identifies the timestamp at which the winning board state was reached.
    
    The recorded play time could normally be used directly to determine the 
    win time. However, the reconstructed board state is checked explicitly
    with ``check_win()`` to validate the replay data. This provides an
    additional integrity check and helps ensure that corrupted or inconsistent
    files do not report an invalid win time.
    
    Args:
        data (Dict): Dictionary containing puzzle data including ``grid``,
            ``row_sums``, and ``col_sums``.
        states (List[Tuple]): List of reconstructed state tuples. The first
            item is the timestamp in milliseconds and the second item is the
            selected-cell state.
        n (int): Dimension of the grid (N x N).

    Returns:
        Optional[int]: The timestamp in milliseconds at which the final
        reconstructed board state satisfies the winning condition, or None
        if the final state is not a winning state.
    """
    # Validate that the final reconstructed state actually satisfies
    # the puzzle's winning condition.
    start_time, sel, *_ = states[-1]
    
    if check_win(
        data["grid"],
        sel,
        data["row_sums"],
        data["col_sums"],
        n
    ):
        return start_time
        
    return None


def _tone_for(
    sounds: Any,
    action_type: str
) -> Optional[Any]:
    """Returns the sound effect associated with a game action type.

    Args:
        sounds (Any): Object containing the available game sound effects.
        action_type (str): Indentifier of the player action, such as
            ``"Left"``, ``"Right"``, or ``"Hint"``.

    Returns:
        Optional[Any]: The corresponding sound object if the action type 
        has an associated sound, otherwise None.
    """
    # Map each action type to its corresponding sound effect.
    tone_map = {
        "Left": sounds.click,
        "Right": sounds.dim,
        "Hint": sounds.hint,
    }
    
    return tone_map.get(action_type)


def _build_audio(
    data: Dict,
    sounds: Any,
    total_ms: float,
    win_time_ms: Optional[float] = None,
    sample_rate: int = con.SAMPLE_RATE,
) -> array:
    """Mixes action sound effects and victory audio into a single PCM track.
    
    Creates a stereo 16-bit PCM buffer for the complete export duration and 
    mixes each recorded action sound into the buffer at its corresponding
    timestamp. If a victory time is provided, the victory sound is mixed in
    at that timestamp as well.

    Args:
        data (Dict): Replay data containing the recorded action timestamps.
        sounds (Any): Audio manager containing the available sound effects.
        total_ms (float): Total duration of the audio track in miliseconds.
        win_time_ms (Optional[float], optional): Timestamp in miliseconds at
            which the victory sound should be played. Defaults to None. 
        sample_rate (int, optional): Audio sampling frequency in Hz.
            Defaults to con.SAMPLE_RATE.

    Returns:
        array: An array of signed 16-bit integers (``"h"``) containing the
        mixed interleaved stereo PCM audio data.
    """
    # Allocate a zero-initialized buffer for 16-bit signed stereo samples.
    total_samples = int(total_ms / 1000 * sample_rate) + sample_rate
    buf = array("h", bytes(total_samples * 2 * 2))
    
    # Return silence if the sound system is unavailable.
    if not sounds.available:
        return buf
    
    def _mix_in(tone: Any, time_ms: float) -> None:
        """Mixes a sound effect into the main PCM buffer.
        
        The sound is added sample by sample at the specified timestamp.
        Resulting values are clamped to the signed 16-bit PCM range to
        prevent integer overflow

        Args:
            tone (Any): Sound object providing a ``get_raw()`` method that
                returns PCM sample bytes.
            time_ms (float): Start position of the sound on milliseconds.
        """
        tone_samples = array("h", tone.get_raw())
        
        # Convert the timestamp to the starting stereo sample index.
        start_idx = int(time_ms / 1000 * sample_rate) * 2
        
        for i, v in enumerate(tone_samples):
            idx = start_idx + i
            
            if idx >= len(buf):
                break
            
            # Add the sample and clamp it to the signed 16-bit range.
            mixed = buf[idx] + v
            buf[idx] = max(-32768, min(32767, mixed))
    
    # Mix the sound associated with each recorded action.
    for act in _display_actions(data):
        tone = _tone_for(sounds, act.get("type"))
        
        if tone is None:
            continue
        
        _mix_in(tone, act["time"])
     
    # Mix the victory sound if a valid victory timestamp was provided.
    if win_time_ms is not None: # Maybe just win_time_ms to avoid a win after None time.
        _mix_in(sounds.win, win_time_ms)
        
    return buf


def _samples_to_planar(samples: bytes) -> np.ndarray:
    """Converts interleaved stereo PCM audio into C-contiguous planar audio.

    The input contains signed 16-bit stereo samples in interleaved
    left-right order. The samples are converted into a two-dimensional
    NumPy array where each row contains one complete audio channel.
    
    Args:
        samples (bytes): Raw signed 16-bit stereo PCm data in interleaved
            L-R-L-R order.

    Returns:
        np.ndarray: A C-contiguous 2D NumPy array with shape 
        ``(2, num_samples)``. Row 0 contains the left channel and
        row 1 contains the right channel.
    """
    # Interpret the raw byte buffer a signed 16-bit PCM samples.
    arr = np.frombuffer(samples, dtype=np.int16)
    
    # Separate the interleaved left and right channels.
    stereo = arr.reshape(-1, 2).T
    
    # Ensure that each channel occupies continuous memory for PyAV.
    return np.ascontiguousarray(stereo)


def _surface_to_ndarray(surf: pg.Surface) -> np.ndarray:
    """Converts a Pygame Surface into a contiguous NumPy array.
    
    Pygame's surfarray uses a (width, height, channels) layout, while PyAV
    expects image data in row-major (height, width, channels) order.    

    Args:
        surf (pg.Surface): Pygame Surface containing the RGB image data.

    Returns:
        np.ndarray: A C-contiguous uint8 NumPy array with shape 
        (height, width, 3), containing RGB pixel data ready for PyAV.
    """
    # Extract the RGB pixel data from the Pygame Surface.
    arr = pg.surfarray.array3d(surf)
    
    # Convert from (width, height, channels) to
    # (height, width, channels) and ensure contiguous memory.
    return np.ascontiguousarray(arr.transpose(1, 0, 2))


def export_history_to_mp4(
    sounds: Any,
    data: Dict,
    output_path: str,
    quality_scale: int = 1,
    fps: Optional[int] = None, # = None remove and put before quality_scale, need in every caller funtion to implement.
) -> Tuple[bool, str]:
    """Exports a game replay history to an MP4 video with synchronized audio.
    
    The replay is reconstructed into the game states. A persistent board surface
    is fully rendered once, for the very first state, and then patched in
    place for every later state - only the cells and headers whose 
    appearence actually changed are repainted, instead of redrawing the 
    whole board on every action. For each output frame, a cheap copy of that 
    persistent surface gets the fading action highlight and the elapsed-time
    overlay drawn on top before the resulting image is passed tp PyAV 
    for H.264 encoding.
    
    Audio is generated separately from the recorded actions and victory
    state, converted to the planar format required by PyAV, and encoded
    as stereo AAC audio.

    Args:
        sounds (any): Audio manager containing the available game sounds.
        data (dict): Replay data containing actions, game state information,
            metadata, and total play time.
        output_path (str): Destination path for the resulting MP4 file.
        quality_scale(int): Rendering scale factor. Defaults to 1.
        fps(int | None): Output frame rate. Uses the configured
            export frame rate when None.

    Returns:
        tuple[bool, str]: A tuple containing a success flag and either the
        output path on success or an error message on failure.
    """
    try:
        # Get the fps rate to use
        fps = con.EXPORT_FPS if fps is None else fps
        
        # Load rendering assets and build state timeline.
        font, tiny_font, label_font = _make_fonts(quality_scale)
        cell_size = int(con.CELL_SIZE * quality_scale)
        margin = int(con.EXPORT_MARGIN * quality_scale)
        header_height = int(con.EXPORT_HEADER_HEIGHT * quality_scale)
        ultra = bool(data.get("ultra"))
        n, states = _build_states(data)
        
        # Calculate video timing properties
        total_ms = data.get("play_time", 0) + con.EXPORT_TAIL_MS
        total_frames = max(1, int(total_ms / 1000 * fps) + 1)
        
        # Calculate and enforce even frame dimensions required by H.264
        w_px, h_px = _frame_size(n, cell_size, margin, header_height)
        w_px -= w_px % 2
        h_px -= h_px % 2
        
        # Ensure target directory exists before initializing container
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Initialize PyAV container and stream configurations
        container = av.open(output_path, mode="w")
        
        vstream = container.add_stream("libx264", rate=fps)
        vstream.width = w_px
        vstream.height = h_px
        vstream.pix_fmt = "yuv420p"
        vstream.options = {"crf": "20", "preset": "ultrafast"}
        
        astream = container.add_stream("aac", rate=con.SAMPLE_RATE)
        astream.layout = "stereo"
        
        # --- Video Encoding Loop ---
        # Precompute the color palette and the selection/dimmed/fulfillment
        # data needed to render or diff every reconstructed state up front,
        # rather than recomputing it inline on every state change.
        style = _board_style(ultra)
        
        render_states = [
            _derive_render_state(
                data,
                n,
                s[1],
                s[2],
            )
            for s in states
        ]
        
        offset_x = margin
        offset_y = margin + header_height
        
        # The persistent board surface starts as the static base (background,
        # outer border, Ultra label - these never change across the whole
        # replay) and is then patched is place as playback advances. The one 
        # and only full O(n^2) cell/header draw happens here, for state 0;
        # every later state only repaints the cells and header that actually 
        # changed since the previous state via _apply_board_delta.
        board_surf = _render_static_base(
            n,
            cell_size,
            margin,
            header_height,
            ultra,
            label_font,
            style,
            quality_scale,
        )
        
        _render_full_board(
            board_surf, 
            data, 
            n,
            render_states[0],
            font,
            cell_size,
            offset_x,
            offset_y,
            style,
            quality_scale,
        )
        
        state_idx = 0
        finish_ms = data.get("play_time", 0)
        time_text_color = con.WHITE if ultra else con.TEXT_COLOR
        cached_state_idx = 0
        act_t, hl_cell, hl_color = states[0][0], states[0][3], states[0][4]
        
        for f in range(total_frames):
            t_ms = int(f / fps * 1000)
            
            # Advance state index to match the current frame timestamp
            while (
                state_idx + 1 < len(states)
                and states[state_idx + 1][0] <= t_ms
            ):
                    state_idx += 1
                    
            display_ms = min(t_ms, finish_ms)
            
            # The grid, selections, dimming, highlights and rings only change when the game state changes,
            # so only rebuild that (expensive) part when we actually reach a new state, not for every frame
            if state_idx != cached_state_idx:
                _apply_board_delta(
                    board_surf,
                    data,
                    n,
                    render_states[cached_state_idx],
                    render_states[state_idx],
                    font,
                    cell_size,
                    offset_x,
                    offset_y,
                    style,
                    quality_scale,
                )
                
                cached_state_idx = state_idx
                act_t, hl_cell, hl_color = states[state_idx][0], states[state_idx][3], states[state_idx][4]
              
            # Cheap copy of the cached board, then draw only the part that truly changes every frame
            surf = board_surf.copy()
            
            _draw_action_highlight(
                surf,
                hl_cell,
                hl_color,
                act_t,
                display_ms,
                cell_size,
                offset_x,
                offset_y,
                quality_scale,
            )
            
            _draw_time_overlay(
                surf, 
                display_ms, 
                tiny_font, 
                time_text_color, 
                w_px, margin, 
                cell_size
            )
            
            arr = _surface_to_ndarray(surf)[:h_px, :w_px, :]
            
            frame = av.VideoFrame.from_ndarray(arr, format="rgb24")
            frame.pts = f
            
            for packet in vstream.encode(frame):
                container.mux(packet)
        
        # Flush remaining video encoder packets
        for packet in vstream.encode(None):
            container.mux(packet)
        
        # --- Audio Encoding Loop ---  
        win_time_ms = _find_win_time(data, states, n)
        samples = _build_audio(
            data,
            sounds,
            total_ms,
            win_time_ms=win_time_ms
        )
        
        planar = _samples_to_planar(samples)
        needed_samples = int(total_ms / 1000 * con.SAMPLE_RATE)
        planar = planar[:, :needed_samples]
        
        frame_size = astream.codec_context.frame_size or 1024
        total_samples = planar.shape[1]
        pts = 0
        
        # Chunk planar audio samples into frames expected by AAC encoder
        for start in range(0, total_samples, frame_size):
            chunk = planar[:, start:start + frame_size]
            if chunk.shape[1] == 0:
                break
            
            aframe = av.AudioFrame.from_ndarray(
                chunk,
                format="s16p",
                layout="stereo",
            )
            aframe.sample_rate = con.SAMPLE_RATE
            aframe.pts = pts
            pts += chunk.shape[1]
            
            for packet in astream.encode(aframe):
                container.mux(packet)
        
        # Flush remaining audio encoder packets
        for packet in astream.encode(None):
            container.mux(packet)
            
        container.close()
        return True, output_path
    
    except Exception as e:
        return False, f"Export failed: {e}"
