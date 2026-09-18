### Mati (Mathematics and tactic intelligence) ###
### V0.4.0.1 Beta V1.0.18 ###
### Author: Janosch Klawatsch, 11.08.2026 ###
### export file V0.4.5 ###

### Structure-Plan ###
# - config.py - Constants #
# - level.py - Generate Levels, Check Wins ... #
# - persistence.py - Save and load of .mati files #
# - widgets.py - Draw-Functions #
# - game.py - The main game handling #
# - screens.py - Building the screens #
# - main.py - Entry point and main loop #
# - audio.py - Sound generation #
# - replay.py - Rebuild games # 
# - terminal.py - The Terminal #
# - export.py - Turns a saved match into a video #

### -Imports- ###
### External ###
import os # For paths and temp folders
from array import array # To generate the audio in an array
import numpy as np # PyAV needs numpy
import av # Direct usage of the ffmpeg libaries
import pygame as pg # Something like the engine on which the game runs
from typing import Any, Dict, List, Tuple, Optional # For the documentation

### Own ###
import config as con # To have the constants
import replay as re # To rebuild the states of the match
from level import check_win # To find when the match was won
from widgets import get_fonts # To draw with the exact same fonts as the real game

### -Functions- ###
def _blit_centered(
    surf: pg.Surface,
    font: pg.font.Font,
    text: str,
    color: Tuple[int, int, int],
    x: int, 
    y: int,
) -> None:
    """Renders text and blits it centerd at a specified (x, y) coordinate.

    Args:
        surf (pg.Surface): Target Pygame Surface onto which the text will be drawn.
        font (pg.font.Font): Pygame Font object used to render the text surface.
        text (str): String message to render.
        color (Tuple[int, int, int]): RGB tuple defining text color.
        x (int): Horizontal pixel coordinate for the center of the text.
        y (int): Vertical pixel coordinate for the center of the text.
    """
    # Render the text string into a graphic surface with anti-aliasing enabled
    obj = font.render(text, True, color)
    
    # Calculate bounding rectangle centered at the target (x, y) location.
    rect = obj.get_rect(center=(x, y))
    
    # Blit the text surface onto the destination surface.
    surf.blit(obj, rect)
    
    
def _make_fonts(scale: int) -> Tuple:
    """Creates fonts in the rights sizes for the given scale factor.

    Args:
        scale (int): The factor which declares how much the font get scaled.

    Returns:
        Tuple:
        The three needed fonts in order of font (normal), tiny_font (tiny) 
        and label_font (smallest).
    """
    # Define the size depending on the scale
    font_size = max(12, int(28 * scale))
    tiny_size = max(10, int(16 * scale))
    label_size = max(10, int(15 * scale))
    
    # Define with this size the correct font.
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
    """Calculates total pixel dimensions for exported video frames.
    
    Accounts for an (N + 1) grid layout (including sum headers) plus canvas
    margins and the top header reagion reserved for playback time display.

    Args:
        n (int): Grid dimension size (N x N).
        cell_size (int): The scaled size of the cells.
        margin (int): The scaled margin to every direction.
        header_height (int): The scaled extra space to the top.

    Returns:
        Tuple[int, int]:
        A tuple of (width_px, height_px) representing total frame dimensions.
    """
    # Total horizontal span including grid, target sum headers, and outer margins
    side = (n + 1) * cell_size + margin * 2 
    
    # Total vertical height including the grid, margins, and top status header
    height = side + header_height
    
    return side, height


def _render_frame(
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
) -> pg.Surface:
    """Renders a single video frame off-screen for the replay video.
    
    Draws the complete game state at a given timestamp-including row/column sum targets,
    grid values, cell selections, dimming states, action highlights, completion rings,
    and the elapsed time overlay.

    Args:
        data (Dict): Dictionary containing puzzle data.
        n (int): Grid dimension size (N x N).
        sel (List[List[bool]]): 2D boolean grid where True indicates a selected cell.
        dimmed (List[List[bool]]): 2D boolean grid where True indicates a manually dimmed cell.
        highlight_cell (Optional[Tuple[int, int]]): Tuple of (row, col) specifying the active action cell, or None.
        highlight_color (Optional[Tuple[int, int, int]]): RGB tuple for the action highlight border, or None for default gold.
        time_ms (int): Current playback time in milliseconds.
        font (pg.font.Font): Primary Pygame Font object for grid numbers and sum labels.
        tiny_font (pg.font.Font): Small Pygame Font object for header text/time display.
        label_font (pg.font.Font): Smallest font for the ultra show.
        cell_size (int): The scaled cell size.
        margin (int): The scaled margin to every side.
        header_height (int): The scaled extra space to the top.
        ultra (bool): If it is an ultra game or not.
        scale (int): The scale factor.

    Returns:
        pg.Surface:
        A Pygame Surface object containing the fully rendered frame.
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
            
            # Cell is dimmed if explicitly set, or if row/column sum is fulfilled without selection
            is_dimmed = dimmed[r][c] or (
                (row_fulfilled[r] or col_fulfilled[c]) and not sel[r][c]
            )
            
            # The game is ultra mode show it
            if ultra:
                pg.draw.rect(surf, cell_bg, rect)
            
            # Fill cell background if selected
            if sel[r][c]:
                pg.draw.rect(surf, con.SELECTED_COLOR, rect)
            
            # Inner cell border
            pg.draw.rect(surf, border_color, rect, 2 * scale)
            
            # Draw cell value text
            color = dim_color if is_dimmed else text_color_normal
            _blit_centered(
                surf, font, str(grid[r][c]), color, rect.centerx, rect.centery
            )
            
            # Draw action highlight border on the active cell
            if highlight_cell == (r, c):
                pg.draw.rect(surf, highlight_color or con.GOLD, rect, 4 * scale)
    
    # Redefine the border und draw it
    border_color = con.SHINE if ultra else con.BLACK
    border_width = 4 * scale if ultra else 2 * scale
    pg.draw.rect(
        surf,
        border_color,
        (
            offset_x,
            offset_y, 
            (n + 1) * cell_size,
            (n + 1) * cell_size
        ),
        border_width
    )
    
    # --- Render Target Completion Rings ---
    radius = cell_size // 2 - 4
    half_cell = cell_size // 2
    
    # Row target completion indicators
    for r in range(n):
        if row_fulfilled[r]:
            cx = offset_x + half_cell
            cy = offset_y + (r + 1) * cell_size + half_cell
            pg.draw.circle(surf, con.GREEN, (cx, cy), radius, max(2, cell_size // 30))
            
    # Column target completion indicators
    for c in range(n): # Check the columns
        if col_fulfilled[c]: # If that column's sum is currently correct
            cx = offset_x + (c + 1) * cell_size + half_cell # The x center of the col-sum cell
            cy = offset_y + half_cell # The y center of the col-sum cell
            pg.draw.circle(surf, con.GREEN, (cx, cy), radius, max(2, cell_size // 30)) # The same green ring as in the live game
    
    # --- Render Elapsed Time Display ---
    seconds = (time_ms // 1000) % 60
    minutes = time_ms // 60000
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
        text_color_normal,
        w_px // 2,
        margin / 2 + 8 * header_scale
    )
    
    # And ultra label
    if ultra:
        _blit_centered(surf, label_font, "ULTRA", con.SHINE, w_px - margin, int(margin / 2 + 8 * header_scale))
    
    return surf


def _display_actions(data: Dict) -> List[Dict]:
    """Generates the full timeline of game actions, prepended with a synthetic start frame.
    
    Inserts an initial frame at timestamp t=0 to establish the initial empty or starting
    board state prior to processing logged player moves.

    Args:
        data (Dict): Replay payload dictionary containing the recorded 'actions' list.

    Returns:
        List[Dict]:
        A list of action dictionaries, starting with a synthetic initial state followed
        by all original match actions.
    """
    # Extract recorded match actions or default to an empty list
    actions = data.get("actions", [])
    
    # Synthetic baseline entry representing the initial state prior to player actions
    start_entry = {
        "time": 0,
        "type": "Start",
        "r": None,
        "c": None,
        "synthetic": True
    }
    
    return [start_entry] + actions


def _build_states(data: Dict) -> Tuple[int, List[Tuple]]:
    """Precalculates board display states and highlight metadata after each game action.
    
    Reconstructs board conditions (selected cells, dimmed cells, action highlights)
    at every logged action timestamp to build a frame-by-frame state timeline.

    Args:
        data (Dict): Dictionary containing grid configuration and play history.

    Returns:
        Tuple[int, List[Tuple]]:
            - n (int): Grid size dimension (N x N).
            - states (List[Tuple]): List of state tuples containing
                (timestamp_ms, sel, dimmed, hl_cell, hl_color).
    """
    n = len(data["grid"])
    display_actions = _display_actions(data)
    states = []
    
    # Reconstruct state at each action point in the replay sequence
    for i in range(len(display_actions)):
        real_index = i - 1
        sel, dimmed, hints_used, play_time_i, last_action = re.reconstruct_state(
            data,
            real_index
        )
        
        # Apply cell highlight metadata if processing a valid player action
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
            # Initial state before any actions occur
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
    """Identifies the timestamp in milliseconds when a winning board state was first reached.
    
    Iterates through chronologically ordered game states and evalutes the board configuration
    against puzzle completion rules.

    Args:
        data (Dict): Dictionary containing puzzle data including 'grid', 'row_sums', and 'col_sums'.
        states (List[Tuple]): List of state tuples where the first item is the timestamp (ms) and the
            second item is the 'sel' (selected cells) state structure.
        n (int): The grid dimension size (e.g., N x N grid).

    Returns:
        Optional[int]:
        The timestamp in milliseconds (int) when the winning condition was satisfied,
        or None if no winning state occurred during the timeline.
    """
    
    # Checks if the last move really is a win move
    start_time, sel, *_ = states[-1]
    if check_win(data["grid"], sel, data["row_sums"], data["col_sums"], n):
        return start_time
        
    return None


def _tone_for(sounds: Any, action_type: str) -> Optional[Any]:
    """Retrieves the corresponding sound effect object for a given game action type.

    Args:
        sounds (Any): Audio manager or container holding game sound assets.
        action_type (str): Key representing the player action (e.g., 'Left', 'Right', 'Hint').

    Returns:
        Optional[Any]:
        The matching sound object if recognized, or None if the action type 
        has no associated sound.
    """
    # Map input action types of their corresponding sound attributes on the sounds object
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
    """Mixes action sound effects and victory audio into a single PCM audio track.

    Args:
        data (Dict): Replay event payload containing historical action timestamps.
        sounds (Any): Audio manager instance containing sound effect objects and state.
        total_ms (float): Total duration of the audio stream in miliseconds.
        win_time_ms (Optional[float], optional): Timestamp in miliseconds when the victory sound should trigger. 
            Defaults to None.
        sample_rate (int, optional): Audio sampling frequency in Hz.
            Defaults to con.SAMPLE_RATE.

    Returns:
        array:
        An 'array' of signed 16-bit integers ('h') containing the mixed
        interleaved stereo audio PCM data.
    """
    # Allocate a zero-initialized buffer for 16-bit signed stereo samples (2 channels * 2 bytes)
    total_samples = int(total_ms / 1000 * sample_rate) + sample_rate
    buf = array("h", bytes(total_samples * 2 * 2))
    
    # Return silence if the sound system is uninitialized or disabled
    if not sounds.available:
        return buf
    
    def _mix_in(tone: Any, time_ms: float) -> None:
        """Additive-mixes a single sound effect into the main PCM buffer with clipping prevention.

        Args:
            tone (Any): Sound object exposing a get_raw() method returnung sample bytes.
            time_ms (float): Start offset in milliseconds where the sound should be placed.
        """
        tone_samples = array("h", tone.get_raw()) # The original sound
        # Convert milliseconds to sample index (multiplied by 2 for interleaved stereo L/R)
        start_idx = int(time_ms / 1000 * sample_rate) * 2
        
        for i, v in enumerate(tone_samples):
            idx = start_idx + i
            if idx >= len(buf):
                break
            
            # Additive mix and clamp to signed 16-bit integer boundaries (-32768 to 32767)
            mixed = buf[idx] + v
            buf[idx] = max(-32768, min(32767, mixed))
    
    # Iterate through game actions and mix matching sound effects
    for act in _display_actions(data):
        tone = _tone_for(sounds, act.get("type"))
        if tone is None:
            continue
        _mix_in(tone, act["time"])
     
    # Mix in victory sound effect if a win event occurred    
    if win_time_ms:
        _mix_in(sounds.win, win_time_ms)
        
    return buf


def _samples_to_planar(samples: bytes) -> np.ndarray:
    """Converts raw interleaved stereo audio byte buffer into C-contiguous planar audio format.

    PyAV expects planar audio formats (such as 's16p') to separate audio channels
    into distinct, contiguous memory blocks (shape: [channels, sample_count])
    rather than interleaved samples (shape: [sample_count, channels]).
    
    Args:
        samples (bytes): Raw bytes buffer containing 16-bit signed integer interleaved
            stereo PCM audio data (L-R-L-R...).

    Returns:
        np.ndarray:
        A C-contiguous 2D NumPy array with shape (2, num_samples) where row 0
        contains left channel samples and row 1 contains right channel samples.
    """
    # Parse the raw byte buffer into a 1D array of 16-bit signed integers
    arr = np.frombuffer(samples, dtype=np.int16)
    
    # Reshape interleaved samples to (num_samples, 2) and transpose to (2, num_samples)
    stereo = arr.reshape(-1, 2).T
    
    # Enforce C-contiguous memory layout across channel rows for PyAV encoding
    return np.ascontiguousarray(stereo)


def _surface_to_ndarray(surf: pg.Surface) -> np.ndarray:
    """Converts a Pygame Surface object into a contiguous NumPy ndarray.
    
    Pygame stores pixel arrays in a (width, height, 3) coordinate space, whereas
    PyAV video frames expect image data arranged in standard row_major order
    (height, width, channels / RGB).

    Args:
        surf (pg.Surface): The Pygame Surface instance to be converted.

    Returns:
        np.ndarray:
        A C-contiguous uint8 NumPy array formatted as (height, width, RGB)
        ready for PyAV VideoFrame encoding.
    """
    # Extract raw 3D RGB array from Pygame surface: shape is (width, height, 3)
    arr = pg.surfarray.array3d(surf)
    
    # Transpose dimensions from (width, height, channels) to (height, width, channels)
    # and enforce memory contiguity required by C-based encoding libraries.
    return np.ascontiguousarray(arr.transpose(1, 0, 2))


def export_history_to_mp4(
    sounds: Any,
    data: Dict,
    output_path: str,
    quality_scale: int = 1,
    fps: int | None = None,
) -> Tuple[bool, str]:
    """Exports game replay history to an MP4 video file with synchronized audio.

    Args:
        sounds (any): Dictionary mapping sound event names to audio data/buffers.
        data (dict): Game replay payload containing moves, metadata, and play time
        output_path (str): File system destination path for the resulting MP4 video.
        quality_scale(int): The scale factor. Normally 1.
        fps(int | None): The frame rate normaly None for default.

    Returns:
        tuple[bool, str]: 
        A tuple where the first element indicates success (True/False) and the
        second element contains either the output path or an error message.
    """
    try:
        # Get the fps rate to use
        fps = fps or con.EXPORT_FPS
        
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
        vstream.options = {"crf": "20"}
        
        astream = container.add_stream("aac", rate=con.SAMPLE_RATE)
        astream.layout = "stereo"
        
        # --- Video Encoding Loop ---
        state_idx = 0
        finish_ms = data.get("play_time", 0)
        
        for f in range(total_frames):
            t_ms = int(f / fps * 1000)
            
            # Advance state index to match the current frame timestamp
            while (
                state_idx + 1 < len(states)
                and states[state_idx + 1][0] <= t_ms
            ):
                    state_idx += 1
            
            _, sel, dimmed, hl_cell, hl_color = states[state_idx]
            display_ms = min(t_ms, finish_ms)
            
            # Render frame surface and convert to PyAv VideoFrame
            surf = _render_frame(
                data, 
                n, 
                sel, 
                dimmed, 
                hl_cell, 
                hl_color, 
                display_ms, 
                font, 
                tiny_font,
                label_font,
                cell_size,
                margin,
                header_height,
                ultra,
                quality_scale
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
