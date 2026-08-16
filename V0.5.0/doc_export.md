# Documentation for export.py
Handles rendering a completed and saved Mati match into an .mp4 video file with synchronized Pygame surface frames and PyAV audio generation.


# Overview 
Component:           Information:
Module Target        Match export & video generation
Dependencies         os, array, numpy, av, pygame
Internal Imports     config, replay, level, widgets


## Public Functions

export_history_to_mp4()
The primary entry point of the module.
Takes match data, state audio, the output path, and renders out a fully encoded H.264 video (.mp4) with synchronized AAC audio track

def export_history_to_mp4(sounds: Any, data: dict, output_path: str):
    return tuple[bool, str]

Parameters
Parameter   Type    Default     Desciption
sounds      Sound   (Required)  Audio manager holding
                                .click , .dim , .hint ,
                                .win sound objects.
data        dict    (Required)  Match dictionary containing 
                                board, configuration, actions 
                                and timing.
output_path str     (Required)  Filepath destination for the
                                generated .mp4 file.

Returns
tuple[bool, str]:
    (True, output_path) on successful export.
    (False, error_message) if the export fails during frame construction or encoding.

How to use:
from audio import Sounds
from export import export_history_to_mp4
from persistence import load_match

time = f"{%y-%m-%d_%H-%M-%S}"
sounds = Sounds()
match_data = load_match(f"{time}.mati") # Time need to be real

success, result = export_history_to_mp4(
    sounds=sounds,
    data=match_data,
    output_path=f"{time}.mp4"
)

if success:
    print(f"Export saved to {result}")
else:
    print(f"Error: {result}")


## Internal Utility Functions
[!NOTE]
Functions prefixed with an underscore(_) are private helpers used internally by export_history_to_mp4.

_render_frame()
Renders a single video frame onto a pygame.Surface representing the game grid at a given millisecond timestamp.

def _render_frame(
    data: dict,
    n: int,
    sel: list[list[bool]],
    dimmed: list[list[bool]],
    highlight_cell: tuple[int, int] | None,
    highlight_color: tuple[int, int, int] | None,
    time_ms: int,
    font: pygame.font.Font,
    tiny_font: pygame.font.Font
) -> pygame.Surface

Returns:
pygame.Surface: Rendered frame containing the grid, correct sums, highlighted actions, indicator rings and active match timer.


_build_audio()
Constructs and mixes the complete raw stereo PCM audio array for the duration of the video based on player action timestamps.

def _build_audio(
    data: dict,
    sounds: Any,
    total_ms: int,
    win_time_ms: int | None,
    sample_rate: int = config.SAMPLE_RATE
) -> array

Returns:
array("h"): Signed 16-bit interleaved stereo audio buffer.


_build_states()
Pre-calculates all historical board selection states, dimmed states, and active action highlights across every action logged in the match data.

def _build_states(data: dict)
-> tuple[int, list[tuple]]

Returns:
tuple[int, list[tuple]]: A tuple containing:
    1. n: Grid dimensions (n x n).
    2. states: List of tuples containing (timestamp, sel_matrix, dimmed_matrix, highlight_cell, highlight_color).


# Additional Helpers
Function                Signature               Description
_blit_centered()        (surf, font, text       Draws centered text on 
                        , color, x, y)          a target pygame.Surface.
_frame_size()           (n: int)                Calculates output pixel 
                        -> tuple[int, int]      width and height for a
                                                grid size of n.
_display_actions()      (data: dict)            Returns action history
                        -> list[dict]           prepended with a synthetic
                                                "Start" action at t = 0.
_find_win_time()        (data, states, n)       Iterates states to find
                        -> int | None           the exact timestamp where
                                                the victory is reached.
_tone_for()             (sounds, action_type:   Maps action string types
                        str) -> Sound | None    ("Left", etc.) to corres-
                                                ponding audio clips.
_samples_to_planar()    (samples: array)        Converts 16-bit PCM sampels
                        -> numpy.ndarray        into a planar C-contiguous
                                                NumPy array for PyAV.
_surface_to_ndarray()   (surf: pg.Surface)      Converts a Pygame surface
                        -> numpy.ndarray        to an RGB PyAV frame.


