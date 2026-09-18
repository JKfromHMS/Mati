"""Render the final board of a match into an MP4 video via ffmpeg.

This module handles the reconstruction of a match state timeline and
the rendering of each state into an MP4 video with synchronized audio.
"""

from __future__ import annotations

import functools
import os
from array import array
from collections.abc import Callable
from fractions import Fraction
from typing import TYPE_CHECKING, Any

import av
import numpy as np
import pygame as pg

import config as con
import replay as re
from level import check_win

if TYPE_CHECKING:
    pass


# One chapter tick equals exactly one millisecond. Because an action's
# ``time`` is stored in milliseconds, a chapter's ``start``/``end`` values
# become the exact action timestamps with zero rounding.
_CHAPTER_TIME_BASE = Fraction(1, 1000)


@functools.lru_cache(maxsize=4096)
def _render_text_cached(
    font: pg.font.Font,
    text: str,
    color: tuple[int, int, int],
) -> pg.Surface:
    """Renders text once and reuses the result for later calls with the same
    font, text, and color.
    
    Grid digits and sum labels are rendered repeatedly across cells, states,
    and frames. Caching avoids repeating the comparatively expensive font
    rasterization process for identical text.
    
    Args:
        font (pg.font.Font): Pygame Font object used to render the text.
        text (str): String containing the text to render.
        color (tuple[int, int, int]): RGB tuple defining the text color.

    Returns:
        pg.Surface: The rendered text surface, either newly created or
            retrieved from cache.
    """
    return font.render(text, True, color)


def _blit_centered(
    surf: pg.Surface,
    font: pg.font.Font,
    text: str,
    color: tuple[int, int, int],
    x: int, 
    y: int,
) -> None:
    """Renders text and blits it centered at a specified (x, y) coordinate.

    Args:
        surf (pg.Surface): Target Pygame Surface onto which the text is drawn.
        font (pg.font.Font): Pygame Font object used to render the text.
        text (str): String containing the text to render.
        color (tuple[int, int, int]): RGB tuple defining the text color.
        x (int): Horizontal pixel coordinate of the text center.
        y (int): Vertical pixel coordinate for the text center.
    """
    obj = _render_text_cached(font, text, color)
    rect = obj.get_rect(center=(x, y))
    surf.blit(obj, rect)
    
    
def _make_fonts(scale: int) -> tuple[pg.font.Font, pg.font.Font, pg.font.Font]:
    """Creates fonts with the appropriate sizes for the given scale factor.

    Args:
        scale (int): Factor used to scale the font sizes. 
            (Is expected to be 1 or greater)

    Returns:
        tuple[pg.font.Font, pg.font.Font, pg.font.Font]: The three required 
            fonts in the following order: normal font, tiny font, and label font.
    """
    font_size = 28 * scale
    tiny_size = 16 * scale
    label_size = 15 * scale
    
    font = pg.font.SysFont("arial", font_size, bold=True)
    tiny_font = pg.font.SysFont("arial", tiny_size)
    label_font = pg.font.SysFont("arial", label_size, bold=True)
    
    return font, tiny_font, label_font

 
def _frame_size(
    n: int,
    cell_size: int,
    margin: int,
    header_height: int,
) -> tuple[int, int]:
    """Calculates the total pixel dimensions of an exported video frame.
    
    The frame contains an (N + 1) x (N + 1) grid, including the sum headers,
    outer margins, and an additional top header area for the playback time.
    
    Args:
        n (int): Dimension of the main grid (N x N).
        cell_size (int): Pixel size of each scaled grid cell.
        margin (int): Scaled outer margin in pixels.
        header_height (int): Scaled height of the top header area.

    Returns:
        tuple[int, int]: Total frame width and height in pixels.
    """
    side = (n + 1) * cell_size + margin * 2 
    height = side + header_height
    
    return side, height


def _compute_fulfilled(
    grid: list[list[int]],
    sel: list[list[bool]],
    row_sums: list[int],
    col_sums: list[int],
    n: int,
) -> tuple[list[bool], list[bool]]:
    """Calculates row/column target fulfillment for a given selection state.

    Args:
        grid (list[list[int]]): The puzzle's numeric grid.
        sel (list[list[bool]]): 2D boolean grid of currently selected cells.
        row_sums (list[int]): Target sums for each row.
        col_sums (list[int]): Target sums for each column.
        n (int): Dimension of the grid (N x N).

    Returns:
        tuple[list[bool], list[bool]]: Fulfillment flags for each row and 
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
    dimmed: list[list[bool]],
    sel: list[list[bool]],
    row_fulfilled: list[bool],
    col_fulfilled: list[bool],
    n: int,
) -> list[list[bool]]:
    """Derives the effective per-cell dimmed state for a selection state.

    Args:
        dimmed (list[list[bool]]): 2D boolean grid of explicitly dimmed cells.
        sel (list[list[bool]]): 2D boolean grid of currently selected cells.
        row_fulfilled (list[bool]): Fulfillment flag for each row.
        col_fulfilled (list[bool]): Fulfillment flag for each column.
        n (int): Dimension of the grid (N x N).

    Returns:
        list[list[bool]]: 2D boolean grid of the effective dimmed state.
    """
    return [
        [
            dimmed[r][c] or ((row_fulfilled[r] or col_fulfilled[c]) and not sel[r][c])
            for c in range(n)
        ]
        for r in range(n)
    ]
    
    
def _derive_render_state(
    data: dict[str, Any],
    n: int,
    sel: list[list[bool]],
    dimmed: list[list[bool]],
) -> dict[str, Any]:
    """Bundles the values needed to render one reconstructed state.

    Args:
        data (dict[str, Any]): Dictionary containing the puzzle data.
        n (int): Dimension of the main grid (N x N).
        sel (list[list[bool]]): 2D boolean grid of currenty selected cells.
        dimmed (list[list[bool]]): 2D boolen grid of explicitly dimmed cells.

    Returns:
        dict[str, Any]: Selection grid, effective dimmed grid, and row/col
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
    
    
def _board_style(ultra: bool) -> dict[str, tuple[int, int, int]]:
    """Resolves the color palette for the board, depending on Ultra mode.

    Args:
        ultra (bool): Whether the game is running in Ultra mode.

    Returns:
        dict[str, tuple[int, int, int]]: Named colors used across the static 
            base, cells, and headers.
    """
    if ultra:
        return {
            "bg_color": (28, 24, 12),
            "sum_color": con.SHINE,
            "text_color_normal": con.WHITE,
            "dim_color": (110, 100, 70),
            "cell_fill_color": (52, 46, 26),
            "cell_border_color": con.SHINE,
            "outer_border_color": con.SHINE,
        }
    
    return {
        "bg_color": con.BG_COLOR,
        "sum_color": con.TARGET_COLOR,
        "text_color_normal": con.TEXT_COLOR,
        "dim_color": con.DIMMED_TEXT_COLOR,
        "cell_fill_color": con.BG_COLOR,
        "cell_border_color": con.GRID_COLOR,
        "outer_border_color": con.BLACK,
    }
    
    
def _render_static_base(
    n: int,
    cell_size: int,
    margin: int,
    header_height: int,
    ultra: bool,
    label_font: pg.font.Font,
    style: dict[str, tuple[int, int, int]],
    scale: int = 1,
) -> pg.Surface:
    """Renders the part of the board that never changes across a replay.

    Args:
        n (int): Dimension of the main grid (N x N).
        cell_size (int): Scaled size of each grid cell in pixels.
        margin (int): Scaled outer margin in pixels.
        header_height (int): Scaled height of the top header area.
        ultra (bool): Whether the game is running in Ultra mode.
        label_font (pg.font.Font): Font used for the Ultra label.
        style (dict[str, tuple[int, int, int]]): Color palette.
        scale (int): Scale factor used for rendering. Defaults to 1.

    Returns:
        pg.Surface: The static board base, without cells or headers.
    """
    w_px, h_px = _frame_size(n, cell_size, margin, header_height)
    
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
    grid: list[list[int]],
    r: int,
    c: int,
    selected: bool,
    is_dimmed: bool,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: dict[str, tuple[int, int, int]],
    scale: int,
) -> None:
    """(Re-)draws a single grid cell, overwriting whatever was there before."""
    rect = pg.Rect(
        offset_x + (c + 1) * cell_size,
        offset_y + (r + 1) * cell_size,
        cell_size,
        cell_size,
    )
    
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
    row_sums: list[int],
    r: int,
    fulfilled: bool,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: dict[str, tuple[int, int, int]],
    scale: int,
) -> None:
    """(Re-)draws a row's target-sum label and completion ring."""
    rect = pg.Rect(
        offset_x,
        offset_y + (r + 1) * cell_size,
        cell_size,
        cell_size,
    )
    
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
        pg.draw.circle(surf, con.GREEN, rect.center, radius, max(2, cell_size // 30))
        
        
def _render_col_header(
    surf: pg.Surface,
    col_sums: list[int],
    c: int,
    fulfilled: bool,
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: dict[str, tuple[int, int, int]],
    scale: int,
) -> None:
    """(Re-)draws a column's target-sum label and completion ring."""
    rect = pg.Rect(
        offset_x + (c + 1) * cell_size,
        offset_y,
        cell_size,
        cell_size,
    )
    
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
        pg.draw.circle(surf, con.GREEN, rect.center, radius, max(2, cell_size // 30))
        
        
def _render_full_board(
    surf: pg.Surface,
    data: dict[str, Any],
    n: int,
    render_state: dict[str, Any],
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: dict[str, tuple[int, int, int]],
    scale: int,
) -> None:
    """Draws every cell and header once, onto the static base surface."""
    grid = data["grid"]
    row_sums = data["row_sums"]
    col_sums = data["col_sums"]
    
    for r in range(n):
        _render_row_header(
            surf, row_sums, r, render_state["row_fulfilled"][r], font,
            cell_size, offset_x, offset_y, style, scale
        )
        
    for c in range(n):
        _render_col_header(
            surf, col_sums, c, render_state["col_fulfilled"][c], font,
            cell_size, offset_x, offset_y, style, scale
        )
        
    for r in range(n):
        for c in range(n):
            _render_cell(
                surf, grid, r, c,
                render_state["sel"][r][c],
                render_state["is_dimmed"][r][c],
                font, cell_size, offset_x, offset_y, style, scale,
            )
            
            
def _apply_board_delta(
    surf: pg.Surface,
    data: dict[str, Any],
    n: int,
    prev: dict[str, Any],
    new: dict[str, Any],
    font: pg.font.Font,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    style: dict[str, tuple[int, int, int]],
    scale: int,
) -> None:
    """Patches the persistent board surface for one advance in replay time."""
    grid = data["grid"]
    row_sums = data["row_sums"]
    col_sums = data["col_sums"]
    
    for r in range(n):
        if prev["row_fulfilled"][r] != new["row_fulfilled"][r]:
            _render_row_header(
                surf, row_sums, r, new["row_fulfilled"][r], font, 
                cell_size, offset_x, offset_y, style, scale
            )
    
    for c in range(n):
        if prev["col_fulfilled"][c] != new["col_fulfilled"][c]:
            _render_col_header(
                surf, col_sums, c, new["col_fulfilled"][c], font,
                cell_size, offset_x, offset_y, style, scale
            )
            
    for r in range(n):
        prev_sel_row, prev_dim_row = prev["sel"][r], prev["is_dimmed"][r]
        new_sel_row, new_dim_row = new["sel"][r], new["is_dimmed"][r]
        
        for c in range(n):
            if prev_sel_row[c] != new_sel_row[c] or prev_dim_row[c] != new_dim_row[c]:
                _render_cell(
                    surf, grid, r, c,
                    new_sel_row[c], new_dim_row[c], font,
                    cell_size, offset_x, offset_y, style, scale,
                )
                
                
def _draw_action_highlight(
    surf: pg.Surface,
    highlight_cell: tuple[int, int] | None,
    highlight_color: tuple[int, int, int] | None,
    action_time_ms: int,
    display_ms: int,
    cell_size: int,
    offset_x: int,
    offset_y: int,
    scale: int,
) -> None:
    """Draws the fading action-highlight border for the current frame."""
    if highlight_cell is None or (display_ms - action_time_ms) >= 1500:
        return
    
    r, c = highlight_cell
    rect = pg.Rect(
        offset_x + (c + 1) * cell_size,
        offset_y + (r + 1) * cell_size,
        cell_size,
        cell_size,
    )
    pg.draw.rect(surf, highlight_color or con.GOLD, rect, 4 * scale)


def _draw_time_overlay(
    surf: pg.Surface,
    time_ms: int,
    tiny_font: pg.font.Font,
    text_color: tuple[int, int, int],
    w_px: int,
    margin: int,
    cell_size: int,
) -> None:
    """Draws the elapsed-time overlay onto an already rendered board surface."""
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
    
    
def _display_actions(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Generates the complete timeline of game actions with a synthetic
    starting frame at timestamp t=0.
    """
    actions = data.get("actions", [])
    start_entry = {
        "time": 0,
        "type": "Start",
        "r": None,
        "c": None,
        "synthetic": True,
    }
    return [start_entry] + actions


def _action_chapter_label(act: dict[str, Any]) -> str:
    """Builds the navigation title for one recorded action's chapter."""
    if act.get("synthetic") or act.get("type") == "Start":
        return "Start"

    label = con.ACTION_LABELS.get(act.get("type"), act.get("type") or "Action")

    if act.get("r") is not None and act.get("c") is not None:
        return f"{label} R{act['r'] + 1}/C{act['c'] + 1}"

    return label


def _build_chapters(data: dict[str, Any], total_ms: int) -> list[dict[str, Any]]:
    """Builds one navigation chapter (marker) per game action."""
    max_ms = max(0, total_ms)
    chapters: list[dict[str, Any]] = []
    last_time_ms = 0

    for i, act in enumerate(_display_actions(data)):
        raw_time = act.get("time")

        if raw_time is None:
            time_ms = last_time_ms
        else:
            time_ms = int(raw_time)
            last_time_ms = time_ms

        start_ms = max(0, min(time_ms, max_ms))
        title = _action_chapter_label(act)

        chapters.append({
            "id": i,
            "start": start_ms,
            "end": 0,  
            "time_base": _CHAPTER_TIME_BASE,
            "metadata": {"title": title},
        })

    for idx in range(len(chapters)):
        if idx + 1 < len(chapters):
            chapters[idx]["end"] = chapters[idx + 1]["start"]
        else:
            chapters[idx]["end"] = max_ms

        if chapters[idx]["end"] <= chapters[idx]["start"]:
            chapters[idx]["end"] = chapters[idx]["start"] + 1

    return chapters


def _build_states(data: dict[str, Any]) -> tuple[int, list[tuple]]:
    """Precalculates the board display state after each recorded game action."""
    n = len(data["grid"])
    display_actions = _display_actions(data)
    states = []
    
    for i in range(len(display_actions)):
        real_index = i - 1
        sel, dimmed, hints_used, play_time_i, last_action = re.reconstruct_state(
            data,
            real_index
        )
        
        if i > 0 and last_action:
            hl_cell = (last_action["r"], last_action["c"])
            if last_action.get("Undone"):
                hl_color = con.UNDONE_COLOR
            else:
                hl_color = con.ACTION_HIGHLIGHT_COLOR.get(
                    last_action.get("type"), con.GOLD
                )
        else:
            hl_cell, hl_color = None, None
        
        states.append(
            (display_actions[i]["time"], sel, dimmed, hl_cell, hl_color)
        )
        
    return n, states


def _find_win_time(
    data: dict[str, Any],
    states: list[tuple],
    n: int,
) -> int | None:
    """Identifies the timestamp at which the winning board state was reached."""
    start_time, sel, *_ = states[-1]
    
    if check_win(data["grid"], sel, data["row_sums"], data["col_sums"], n):
        return start_time
        
    return None


def _tone_for(sounds: Any, action_type: str) -> Any | None:
    """Returns the sound effect associated with a game action type.

    Args:
        sounds (Any): Object containing the available game sound effects.
        action_type (str): Identifier of the player action.

    Returns:
        Any | None: The corresponding sound object or None.
    """
    match action_type:
        case "Left":
            return sounds.click
        case "Right":
            return sounds.dim
        case "Hint":
            return sounds.hint
        case _:
            return None


def _build_audio(
    data: dict[str, Any],
    sounds: Any,
    total_ms: float,
    win_time_ms: float | None = None,
    sample_rate: int = con.SAMPLE_RATE,
) -> array:
    """Mixes action sound effects and victory audio into a single PCM track."""
    total_samples = int(total_ms / 1000 * sample_rate) + sample_rate
    buf = array("h", bytes(total_samples * 2 * 2))
    
    if not getattr(sounds, "available", False):
        return buf
    
    def _mix_in(tone: Any, time_ms: float) -> None:
        """Mixes a sound effect into the main PCM buffer."""
        tone_samples = array("h", tone.get_raw())
        start_idx = int(time_ms / 1000 * sample_rate) * 2
        
        for i, v in enumerate(tone_samples):
            idx = start_idx + i
            if idx >= len(buf):
                break
            
            mixed = buf[idx] + v
            buf[idx] = max(-32768, min(32767, mixed))
    
    for act in _display_actions(data):
        tone = _tone_for(sounds, act.get("type"))
        if tone is None:
            continue
        _mix_in(tone, act["time"])
     
    if win_time_ms is not None: 
        _mix_in(sounds.win, win_time_ms)
        
    return buf


def _samples_to_planar(samples: bytes) -> np.ndarray:
    """Converts interleaved stereo PCM audio into C-contiguous planar audio."""
    arr = np.frombuffer(samples, dtype=np.int16)
    stereo = arr.reshape(-1, 2).T
    return np.ascontiguousarray(stereo)


def _surface_to_ndarray(surf: pg.Surface) -> np.ndarray:
    """Converts a Pygame Surface into a contiguous NumPy array."""
    arr = pg.surfarray.array3d(surf)
    return np.ascontiguousarray(arr.transpose(1, 0, 2))


def export_history_to_mp4(
    sounds: Any,
    data: dict[str, Any],
    output_path: str,
    quality_scale: int = 1,
    fps: int | None = None, 
    progress_callback: Callable[[float], None] | None = None, 
) -> tuple[bool, str]:
    """Exports a game replay history to an MP4 video with synchronized audio.
    
    The replay is reconstructed into the game states. A persistent board surface
    is fully rendered once, for the very first state, and then patched in
    place for every later state.
    
    Audio is generated separately from the recorded actions and victory
    state, converted to the planar format required by PyAV, and encoded
    as stereo AAC audio.

    Args:
        sounds (Any): Audio manager containing the available game sounds.
        data (dict[str, Any]): Replay data containing actions and metadata.
        output_path (str): Destination path for the resulting MP4 file.
        quality_scale (int): Rendering scale factor. Defaults to 1.
        fps (int | None): Output frame rate. Defaults to None (config FPS).
        progress_callback (Callable | None): Callback for progress percentage.

    Returns:
        tuple[bool, str]: A tuple containing a success flag and either the
            output path on success or an error message on failure.
    """
    try:
        fps = con.EXPORT_FPS if fps is None else fps
        
        font, tiny_font, label_font = _make_fonts(quality_scale)
        cell_size = int(con.CELL_SIZE * quality_scale)
        margin = int(con.EXPORT_MARGIN * quality_scale)
        header_height = int(con.EXPORT_HEADER_HEIGHT * quality_scale)
        ultra = bool(data.get("ultra"))
        n, states = _build_states(data)
        
        total_ms = data.get("play_time", 0) + con.EXPORT_TAIL_MS
        total_frames = max(1, int(total_ms / 1000 * fps) + 1)
        
        w_px, h_px = _frame_size(n, cell_size, margin, header_height)
        w_px -= w_px % 2
        h_px -= h_px % 2
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        container = av.open(output_path, mode="w")
        
        vstream = container.add_stream("libx264", rate=fps)
        vstream.width = w_px
        vstream.height = h_px
        vstream.pix_fmt = "yuv420p"
        vstream.options = {"crf": "20", "preset": "ultrafast"}
        
        astream = container.add_stream("aac", rate=con.SAMPLE_RATE)
        astream.layout = "stereo"

        try:
            container.set_chapters(_build_chapters(data, total_ms))
        except Exception:
            pass

        style = _board_style(ultra)
        
        render_states = [
            _derive_render_state(data, n, s[1], s[2])
            for s in states
        ]
        
        offset_x = margin
        offset_y = margin + header_height

        board_surf = _render_static_base(
            n, cell_size, margin, header_height,
            ultra, label_font, style, quality_scale
        )
        
        _render_full_board(
            board_surf, data, n, render_states[0],
            font, cell_size, offset_x, offset_y,
            style, quality_scale
        )
        
        state_idx = 0
        finish_ms = data.get("play_time", 0)
        time_text_color = con.WHITE if ultra else con.TEXT_COLOR
        cached_state_idx = 0
        act_t, hl_cell, hl_color = states[0][0], states[0][3], states[0][4]
        last_reported_pct = -1
        
        for f in range(total_frames):
            t_ms = int(f / fps * 1000)
            
            if progress_callback is not None:
                pct = 100 if f == total_frames - 1 else int(f / total_frames * 100)
                if pct != last_reported_pct:
                    last_reported_pct = pct
                    try:
                        progress_callback(f / total_frames)
                    except Exception:
                        pass
            
            while (
                state_idx + 1 < len(states)
                and states[state_idx + 1][0] <= t_ms
            ):
                state_idx += 1
                    
            display_ms = min(t_ms, finish_ms)
            
            if state_idx != cached_state_idx:
                _apply_board_delta(
                    board_surf, data, n,
                    render_states[cached_state_idx], render_states[state_idx],
                    font, cell_size, offset_x, offset_y, style, quality_scale
                )
                
                cached_state_idx = state_idx
                act_t, hl_cell, hl_color = states[state_idx][0], states[state_idx][3], states[state_idx][4]
              
            surf = board_surf.copy()
            
            _draw_action_highlight(
                surf, hl_cell, hl_color, act_t, display_ms,
                cell_size, offset_x, offset_y, quality_scale
            )
            
            _draw_time_overlay(
                surf, display_ms, tiny_font, time_text_color, 
                w_px, margin, cell_size
            )
            
            arr = _surface_to_ndarray(surf)[:h_px, :w_px, :]
            
            frame = av.VideoFrame.from_ndarray(arr, format="rgb24")
            frame.pts = f
            
            for packet in vstream.encode(frame):
                container.mux(packet)
        
        for packet in vstream.encode(None):
            container.mux(packet)
        
        win_time_ms = _find_win_time(data, states, n)
        samples = _build_audio(
            data, sounds, total_ms, win_time_ms=win_time_ms
        )
        
        planar = _samples_to_planar(samples)
        needed_samples = int(total_ms / 1000 * con.SAMPLE_RATE)
        planar = planar[:, :needed_samples]
        
        frame_size = astream.codec_context.frame_size or 1024
        total_samples = planar.shape[1]
        pts = 0
        
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
        
        for packet in astream.encode(None):
            container.mux(packet)
            
        container.close()
        return True, output_path
    
    except Exception as e:
        return False, f"Export failed: {e}"