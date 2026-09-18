"""Central constants and default configuration for the game."""

import sys
from pathlib import Path
from typing import TypeAlias

# --- Base folder ---
# The folder the program code sits in. A frozen build (PyInstaller, Nuitka) unpacks
# its code into a temporary folder, so there the folder of the executable is used.
if getattr(sys, "frozen", False) or "__compiled__" in globals():
    BASE_DIR: Path = Path(sys.executable).resolve().parent
else:
    BASE_DIR: Path = Path(__file__).resolve().parent

# --- Type Aliases ---
Color: TypeAlias = tuple[int, int, int]

# --- Sizes ---
WIDTH: int = 800       # The width of the window
HEIGHT: int = 600      # The height of the window
CELL_SIZE: int = 60    # The size of each cell in the grid

MIN_REAL_WIDTH: int = 480  # To restrict the resize to a good-looking size
MIN_REAL_HEIGHT: int = 360 # To restrict the resize to a good-looking size

# --- Scaling modes ---
SCALE_MODES: list[str] = ["auto", "1", "2", "4"]
SCALE_MODE_LABELS: list[str] = ["Auto", "1x", "2x", "4x"]
SCALE_MODE_DEFAULTS: dict[str, int | None] = {"auto": None, "1": 1, "2": 2, "4": 4}

RENDER_QUALITIES: list[int] = [1, 2, 4]
RENDER_QUALITY_LABELS: list[str] = ["Normal", "High", "Ultra"]

HISTORY_VISIBLE_BOTTOM: int = HEIGHT - 10
HANNAH_VISIBLE_LENGTH: int = WIDTH - 40

# --- Colors ---
BG_COLOR: Color = (245, 245, 250)           # The Background Color (A non-perfect white)
TEXT_COLOR: Color = (40, 40, 40)            # The Text Color in most situations (A dark gray)
TARGET_COLOR: Color = (200, 60, 60)         # The Color for the sums (A normal red)
GRID_COLOR: Color = (200, 200, 200)         # The Grid Color for the game (A light gray)
SELECTED_COLOR: Color = (150, 220, 150)     # The Color for selected cells in the game (A mint green)
HOVER_COLOR: Color = (220, 220, 220)        # The Color for hovered cells (A light gray)
HOVER_LINE_COLOR: Color = (234, 234, 244)   # The Color for the row and column of the hovered cell (A lighter gray)
BUTTON_COLOR: Color = (100, 150, 220)       # The Color for the buttons (A sky blue)
BUTTON_HOVER: Color = (80, 130, 200)        # The Color for hovered buttons (A darker sky blue)
BUTTON_DISABLED: Color = (195, 195, 200)    # The Color for unclickable buttons (A version of gray)
DIMMED_TEXT_COLOR: Color = (180, 180, 180)  # The Color for background text (Another gray)
HISTORY_RIGHT_COLOR: Color = (90, 130, 200) # The Color for the dimmed actions in the history view (A cloudy blue)
TOGGLE_ON_COLOR: Color = (70, 180, 95)      # Active toggle state: green
TOGGLE_ON_HOVER: Color = (45, 145, 70)      # Hovered active toggle: darker green
TOGGLE_OFF_COLOR: Color = (120, 95, 140)    # Inactive toggle state: muted blue-red blend
TOGGLE_OFF_HOVER: Color = (95, 70, 110)     # Hovered inactive toggle: darker blue-red blend
GREEN: Color = (50, 180, 50)                # The example for Green text
GOLD: Color = (215, 175, 60)                # The example for Gold text
WHITE: Color = (255, 255, 255)              # The example for White text
BLACK: Color = (0, 0, 0)                    # The example for Black text
PAUSE: Color = (237, 255, 3)                # The Color for the Pause menu (A neon yellow)
TEXT_COLOR_2: Color = (80, 220, 120)        # The Color for Terminal text (A forest green)
LIGHT_BLACK: Color = (10, 10, 10)           # The Color for the Terminal (A light black)
SHINE: Color = (255, 228, 60)               # Border in ultra mode history (A shining Gold)
FOCUS_COLOR: Color = (255, 140, 0)          # The Color to highlight the focused button (Yellow-Orange)
SCROLLBAR_COLOR: Color = (120, 120, 135)    # The Color of the scrollbars (Another gray)
UNDONE_COLOR: Color = (190, 40, 40)         # The Color to show that an action was undone (Red)
BUTTON_GREY_HOVER: Color = (186, 230, 220)
BUTTON_GREY_COLOR: Color = (212, 255, 245)
BUTTON_GREY_BORDER: Color = (121, 212, 191)
TURQUIS: Color = (41, 255, 251)
GREEN_NEON: Color = (0, 255, 0)
GOLDEN: Color = (234, 211, 0)
SKYBLUE: Color = (24, 131, 255)

# --- Difficulties & Paths ---
DIFFICULTIES: list[int] = [4, 5, 6, 7]
DIFFICULTY_NAMES: dict[int, str] = {
    4: "Easy",
    5: "Advanced",
    6: "Hard",
    7: "Expert",
}
HINTS_PER_GAME: int = 3

HISTORY_DIR: Path = Path("history")
SETTINGS_FILE: Path = Path("settings.smati")
EXPORT_DIR: Path = Path("exports")
EXPORT_HISTORY_FILE: Path = HISTORY_DIR / "export_history.smati"

ACH_TILE_BTN_SIZE: int = 34

# --- Actions ---
ACTION_LABELS: dict[str, str] = {
    "Left": "Select", 
    "Right": "Mark", 
    "Hint": "Hint", 
    "Undone": "Undone"
}
ACTION_HIGHLIGHT_COLOR: dict[str, Color] = {
    "Left": GREEN, 
    "Right": HISTORY_RIGHT_COLOR, 
    "Hint": GOLD, 
    "Undone": UNDONE_COLOR
}

# --- History Detail Entry ---
ENTRY_X: int = 60
ENTRY_WIDTH: int = 680
ENTRY_HEIGHT: int = 44
ENTRY_SPACING: int = 52
LIST_TOP: int = 190
DETAIL_ABOVE: int = 120
DETAIL_BELOW: int = 560

# --- Terminal ---
MAX_LINES: int = 500
INPUT_MAX_LEN: int = 100
LINE_HEIGHT: int = 22

SIZE_COMMANDS: tuple[str, ...] = ("4x4", "5x5", "6x6", "7x7")

ULTRA_COMMANDS: dict[str, int] = {
    "playultra4x4": 4, "pu4x4": 4,
    "playultra5x5": 5, "pu5x5": 5,
    "playultra6x6": 6, "pu6x6": 6,
    "playultra7x7": 7, "pu7x7": 7,
}

PLAY_COMMANDS: dict[str, int] = {
    "play4x4": 4, "p4x4": 4,
    "play5x5": 5, "p5x5": 5,
    "play6x6": 6, "p6x6": 6,
    "play7x7": 7, "p7x7": 7,
}

NAVIGATE_COMMANDS: dict[str, str] = {
    "graphichistory": "HISTORY",
    "graphicsettings": "SETTINGS",
    "graphicabout": "ABOUT",
    "graphicachievements": "ACHIEVEMENTS",
    "advancedsettings": "ADVANCED_SETTINGS"
}

# --- Achievements ---
ACHIEVEMENT_MILESTONES: list[int] = [1, 25, 50, 75, 100, 150, 200]
GENERAL_GAME_MILESTONES: list[int] = [1, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
GENERAL_TIME_MILESTONES: list[tuple[str, int]] = [
    ("playtime_30m", 30 * 60),
    ("playtime_1h", 60 * 60),
    ("playtime_5h", 5 * 60 * 60),
    ("playtime_10h", 10 * 60 * 60),
    ("playtime_24h", 24 * 60 * 60),
]

TIME_ACHIEVEMENTS: dict[tuple[int, bool], list[tuple[str, float]]] = {
    (4, False): [("4x4_7.5s", 7.5), ("4x4_10s", 10), ("4x4_15s", 15)],
    (4, True): [("4x4_ultra_20s", 20), ("4x4_ultra_25s", 25), ("4x4_ultra_30s", 30)],
    (5, False): [("5x5_30s", 30), ("5x5_35s", 35), ("5x5_45s", 45)],
    (5, True): [("5x5_ultra_60s", 60), ("5x5_ultra_70s", 70), ("5x5_ultra_90s", 90)],
    (6, False): [("6x6_60s", 60), ("6x6_70s", 70), ("6x6_80s", 80)],
    (6, True): [("6x6_ultra_180s", 180), ("6x6_ultra_200s", 200), ("6x6_ultra_240s", 240)],
    (7, False): [("7x7_75s", 75), ("7x7_90s", 90), ("7x7_120s", 120)],
    (7, True): [("7x7_ultra_270s", 270), ("7x7_ultra_300s", 300), ("7x7_ultra_330s", 330)],
}

EASTER_EGG_ACHIEVEMENTS: list[str] = ["hannah_found", "hannah_completed", "42_found", "terminal_found"]

ACHIEVEMENT_LABELS: dict[str, str] = {
    "hannah_completed": "Hannah - Message Complete",
    "hannah_found": "Hannah - Secret Found",
    "42_found": "The Answer: 42",
    "terminal_found": "Terminal Discovered",
    "1_4x4": "First Steps in 4x4 (1x 4x4)",
    "25_4x4": "4x4 Regular (25x 4x4)",
    "50_4x4": "4x4 Enthusiast (50x 4x4)",
    "75_4x4": "4x4 Addict (75x 4x4)",
    "100_4x4": "The 100 Club (100x 4x4)",
    "150_4x4": "4x4 Veteran (150x 4x4)",
    "200_4x4": "4x4 Master (200x 4x4)",
    "4x4_7.5s": "That's Impossible! (4x4 in under 7.5s)",
    "4x4_10s": "You Are Speed (4x4 in under 10s)",
    "4x4_15s": "That Was Fast (4x4 in under 15s)",
    "1_4x4_ultra": "A New Dimension (1x 4x4 Ultra)",
    "25_4x4_ultra": "Ultra 4x4 Challenger (25x 4x4 Ultra)",
    "50_4x4_ultra": "Hardcore 4x4 Solver (50x 4x4 Ultra)",
    "75_4x4_ultra": "Iron Will (75x 4x4 Ultra)",
    "100_4x4_ultra": "Ultra 4x4 Centurion (100x 4x4 Ultra)",
    "150_4x4_ultra": "4x4 Gladiator (150x 4x4 Ultra)",
    "200_4x4_ultra": "Ultra 4x4 Sovereign (200x 4x4 Ultra)",
    "4x4_ultra_20s": "Beyond Human (4x4 Ultra in under 20s)",
    "4x4_ultra_25s": "Ultra Instinct (4x4 Ultra in under 25s)",
    "4x4_ultra_30s": "Adrenaline Rush (4x4 Ultra in under 30s)",
    "1_5x5": "Expanding the Grid (1x 5x5)",
    "25_5x5": "5x5 Challenger (25x 5x5)",
    "50_5x5": "5x5 Tactician (50x 5x5)",
    "75_5x5": "Grid Iron Worker (75x 5x5)",
    "100_5x5": "5x5 Centurion (100x 5x5)",
    "150_5x5": "5x5 Expert (150x 5x5)",
    "200_5x5": "5x5 Grandmaster (200x 5x5)",
    "5x5_30s": "Are You a Robot? (5x5 in under 30s)",
    "5x5_35s": "Blink and You Miss It (5x5 in under 35s)",
    "5x5_45s": "Mach 5 (5x5 in under 45s)",
    "1_5x5_ultra": "Overcharged 5x5 (1x 5x5 Ultra)",
    "25_5x5_ultra": "Ultra 5x5 Vanguard (25x 5x5 Ultra)",
    "50_5x5_ultra": "Ultra 5x5 Specialist (50x 5x5 Ultra)",
    "75_5x5_ultra": "Unstoppable Force (75x 5x5 Ultra)",
    "100_5x5_ultra": "Ultra 5x5 Centurion (100x 5x5 Ultra)",
    "150_5x5_ultra": "Ultra 5x5 Elite (150x 5x5 Ultra)",
    "200_5x5_ultra": "Ultra 5x5 Warlord (200x 5x5 Ultra)",
    "5x5_ultra_60s": "The Singularity (5x5 Ultra in under 60s)",
    "5x5_ultra_70s": "Processor Meltdown (5x5 Ultra in under 70s)",
    "5x5_ultra_90s": "Neural Overdrive (5x5 Ultra in under 90s)",
    "1_6x6": "Into the Labyrinth (1x 6x6)",
    "25_6x6": "6x6 Navigator (25x 6x6)",
    "50_6x6": "6x6 Architect (50x 6x6)",
    "75_6x6": "Maze Runner (75x 6x6)",
    "100_6x6": "6x6 Conqueror (100x 6x6)",
    "150_6x6": "6x6 Virtuoso (150x 6x6)",
    "200_6x6": "6x6 Legend (200x 6x6)",
    "6x6_60s": "Breaking the Light Barrier (6x6 in under 60s)",
    "6x6_70s": "Fingers of Fury (6x6 in under 70s)",
    "6x6_80s": "Sixth Sense (6x6 in under 80s)",
    "1_6x6_ultra": "Hypercube Initiate (1x 6x6 Ultra)",
    "25_6x6_ultra": "Ultra 6x6 Pioneer (25x 6x6 Ultra)",
    "50_6x6_ultra": "Ultra 6x6 Operative (50x 6x6 Ultra)",
    "75_6x6_ultra": "Relentless Focus (75x 6x6 Ultra)",
    "100_6x6_ultra": "Ultra 6x6 Overlord (100x 6x6 Ultra)",
    "150_6x6_ultra": "Ultra 6x6 Prodigy (150x 6x6 Ultra)",
    "200_6x6_ultra": "Ultra 6x6 Deity (200x 6x6 Ultra)",
    "6x6_ultra_180s": "Breaking Physics (6x6 Ultra in under 180s)",
    "6x6_ultra_200s": "Tachyon Sprinter (6x6 Ultra in under 200s)",
    "6x6_ultra_240s": "Warp Drive Engaged (6x6 Ultra in under 240s)",
    "1_7x7": "The Grand Stage (1x 7x7)",
    "25_7x7": "7x7 Explorer (25x 7x7)",
    "50_7x7": "7x7 Visionary (50x 7x7)",
    "75_7x7": "Master of Space (75x 7x7)",
    "100_7x7": "7x7 Colossus (100x 7x7)",
    "150_7x7": "7x7 Oracle (150x 7x7)",
    "200_7x7": "7x7 God (200x 7x7)",
    "7x7_75s": "Quantum Computing (7x7 in under 75s)",
    "7x7_90s": "Warp Speed (7x7 in under 90s)",
    "7x7_120s": "Lucky Number 7 (7x7 in under 120s)",
    "1_7x7_ultra": "Entering the Cosmos (1x 7x7 Ultra)",
    "25_7x7_ultra": "Ultra 7x7 Astronaut (25x 7x7 Ultra)",
    "50_7x7_ultra": "Ultra 7x7 Commander (50x 7x7 Ultra)",
    "75_7x7_ultra": "Defying Gravity (75x 7x7 Ultra)",
    "100_7x7_ultra": "Ultra 7x7 Titan (100x 7x7 Ultra)",
    "150_7x7_ultra": "Ultra 7x7 Immortal (150x 7x7 Ultra)",
    "200_7x7_ultra": "Omnipotent (200x 7x7 Ultra)",
    "7x7_ultra_270s": "Ascension (7x7 Ultra in under 270s)",
    "7x7_ultra_300s": "Bending Reality (7x7 Ultra in under 300s)",
    "7x7_ultra_330s": "Cosmic Anomaly (7x7 Ultra in under 330s)",
    "games_1": "First Game",
    "games_10": "Still New?",
    "games_25": "On a Roll!",
    "games_50": "Warming Up",
    "games_100": "Century",
    "games_250": "Can't Stop Now",
    "games_500": "Half a Grand",
    "games_1000": "The 1K Club",
    "games_2500": "Marathon Runner",
    "games_5000": "One With The Grid",
    "games_10000": "Absolute Legend",
    "playtime_30m": "Coffee Break",
    "playtime_1h": "Time Flies",
    "playtime_5h": "Hooked",
    "playtime_10h": "Double Digits",
    "playtime_24h": "A Full Rotation",
}

DEFAULT_ACHIEVEMENTS: dict[str, bool] = {key: False for key in ACHIEVEMENT_LABELS}

# --- Settings and Progress ---
DEFAULT_SETTINGS: dict[str, bool | float | str | int] = {
    "save_history": True,
    "timer_enabled": False,
    "timer_ms": False,
    "sound_enabled": True,
    "terminal_sound_enabled": True,
    "alt_control": True,
    "live_clock_enabled": False,
    "ultra_timer_enabled": False,
    "ultra_timer_ms": False,
    "ultra_timer_show_clock": False,
    "game_volume": 1.0,
    "terminal_volume": 1.0,
    "language": "english",
    "input_order_front": "action_column_row",
    "input_order_back": "column_row_action",
    "scale_mode": "auto",
    "render_quality": 1,
    "tutorial_completed": False,
}

# --- Advanced Settings ---
LANGUAGES_DIR: Path = Path("rsc/languages")
LANGUAGES_DIRS: tuple[Path, ...] = (
    BASE_DIR / LANGUAGES_DIR,
    LANGUAGES_DIR,
)
BUILTIN_LANGUAGE: str = "english"

INPUT_ORDER_OPTIONS: list[str] = [
    "column_row_action", 
    "row_column_action", 
    "action_column_row", 
    "action_row_column"
]
INPUT_ORDER_FRONT_OPTIONS: list[str] = [INPUT_ORDER_OPTIONS[2], INPUT_ORDER_OPTIONS[3]]
INPUT_ORDER_BACK_OPTIONS: list[str] = [INPUT_ORDER_OPTIONS[0], INPUT_ORDER_OPTIONS[1]]

INPUT_ORDER_LABELS: dict[str, str] = {
    "column_row_action": "Column, Row, Action",
    "row_column_action": "Row, Column, Action",
    "action_column_row": "Action, Column, Row",
    "action_row_column": "Action, Row, Column",
}

DEFAULT_KEYBINDINGS: dict[str, dict[str, str | bool]] = {
    "menu": {"key": "m", "ctrl": True},
    "new_round": {"key": "n", "ctrl": True},
    "fullscreen": {"key": "f11", "ctrl": False},
    "undo": {"key": "z", "ctrl": True},
    "pause": {"key": "p", "ctrl": False},
    "hint": {"key": "h", "ctrl": False},
    "right_click": {"key": "r", "ctrl": False},
}

KEYBINDINGS_LABELS: dict[str, str] = {
    "menu": "Back to Menu",
    "new_round": "New Round",
    "fullscreen": "Toggle Fullscreen",
    "undo": "Undo",
    "pause": "Pause",
    "hint": "Use Hint",
    "right_click": "Right-Click Cell",
}

BOTTOM_Y: int = 525
OPPOSITE_DIRECTION: dict[str, str] = {"up": "down", "down": "up", "left": "right", "right": "left"}

# --- Easter Eggs ---
HANNAH_SIZE: int = 5
HANNAH_MESSAGE: list[str | None] = [
    "H", "A", "N", "N", "A", "H", None, 
    "B", "Y", None, 
    "H", "E", "A", "R", "T", None, 
    "F", "O", "R", None, 
    "E", "V", "E", "R"
]
HANNAH_TITE_SIZE: int = 110
HANNAH_TITE_GAP: int = 18
HANNAH_SPACE_GAP: int = 46
HANNAH_STRIP_Y: int = 260

# --- Others ---
SAMPLE_RATE: int = 44100
WHEEL_CLICK_GUARD_MS: int = 500
WHEEL_CLICK_GUARD_MS_MIN: int = 20
FOCUS_IDLE_MS: int = 3000
XOR_KEY: bytes = b"Mati_Obfuscation_Key_2026"

# --- Scrollbars ---
SCROLLBAR_WIDTH: int = 8
SCROLLBAR_MIN_LENGTH: int = 30
SCROLLBAR_MAX_ALPHA: int = 190
SCROLLBAR_MOVE_ALPHA: int = 130
SCROLLBAR_VISIBLE_MS: int = 700

# --- Adaptive redraw ---
CLOCK_MS_UPDATE_MS: int = 10
TERMINAL_BLINK_MS: int = 500
MOUSE_IDLE_HIDE_MS: int = 5000
HINT_FLASH_MS: int = 900

# --- Hold to repeat ---
KEY_REPEAT_DELAY_MS: int = 400
KEY_REPEAT_INTERVAL_MS: int = 90

# --- MP4 export ---
EXPORT_FPS: int = 30
EXPORT_TAIL_MS: int = 1500
EXPORT_MARGIN: int = 30
EXPORT_HEADER_HEIGHT: int = 40
EXPORT_QUALITIES: list[tuple[str, int]] = [("Standard", 1), ("High", 2), ("Ultra", 4)]
EXPORT_FPS_CHOICES: list[int] = [30, 60]
POPUP_REDRAW_INTERVAL_MS: int = 33