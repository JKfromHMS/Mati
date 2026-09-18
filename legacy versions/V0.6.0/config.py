### Mati (Mathematics and tactic intelligence) ###
### V0.6.0 (Beta V1.0.21) ###
### Author: Janosch Klawatsch, 2026-08-27 ###
### config file V0.6.3 ###

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
import pygame as pg # Something like the engine


### -Constants- ###
### Sizes ###
WIDTH = 800    # The wide of the window
HEIGHT = 600   # The heigh of the window
CELL_SIZE = 60 # The size of each cell in the grid

MIN_REAL_WIDTH = 480  # To restrict the resize to a good looking size
MIN_REAL_HEIGHT = 360 # To restrict the resize to a good lokking size

### Colors ###
BG_COLOR = (245, 245, 250)           # The Background Color (A nonperfect white)
TEXT_COLOR = (40, 40, 40)            # The Text Color in most situations (A dark gray)
TARGET_COLOR = (200, 60, 60)         # The Color for the sums (A normal red)
GRID_COLOR = (200, 200, 200)         # The Grid Color for the game (A light gray)
SELECTED_COLOR = (150, 220, 150)     # The Color for selected cells in the game (A mint green)
HOVER_COLOR = (220, 220, 220)        # The Color for hoverd cells (A light gray)
HOVER_LINE_COLOR = (234, 234, 244)   # The Color for the row and column of the hoverd cell (A lighter gray)
BUTTON_COLOR = (100, 150, 220)       # The Color for the buttons (A sky blue)
BUTTON_HOVER = (80, 130, 200)        # The Color for hoverd buttons (A darker sky blue)
BUTTON_DISABLED = (195, 195, 200)    # The Color for unclickabel buttons (A version of gray)
DIMMED_TEXT_COLOR = (180, 180, 180)  # The Color for background text (Another gray)
HISTORY_RIGHT_COLOR = (90, 130, 200) # The Color for the dimmed actions in the history view (A cloudy blue)
GREEN = (50, 180, 50)                # The example for Green text 
GOLD = (215, 175, 60)                # The example for Gold text
WHITE = (255, 255, 255)              # The example for White text
BLACK = (0, 0, 0)                    # The example for Black text
PAUSE = (237, 255, 3)                # The Color for the Pause menu (A neon yellow)
TEXT_COLOR_2 = (80 ,220 ,120)        # The Color for Terminal text (A forest green)
LIGHT_BLACK = (10, 10, 10)           # The Color for the Terminal (A light Black)
SHINE = (255, 228, 60)               # Border in ultra mode history (A shining Gold)
FOCUS_COLOR = (255, 140, 0)          # The Color the highlight the focused button (An other Yellow-Orange)
SCROLLBAR_COLOR = (120, 120, 135)    # The Color of the scrollbars (Another gray)
UNDONE_COLOR = (190, 40, 40)         # The Color to show that an action was undone (Red)

### Difficulties ###
DIFFICULTIES = [4, 5, 6, 7]  # The grid sizes
DIFFICULTY_NAMES = {
    4: "Easy",
    5: "Advanced",
    6: "Hard",
    7: "Expert",
} # Names for the grid sizes
HINTS_PER_GAME = 3 # The number of hints the player have each game
HISTORY_DIR = "history" # The name of the folder that includes the save games
SETTINGS_FILE = "settings.smati" # The file that saves settings and statistics
EXPORT_DIR = "exports" # The folder mp4 exports get saved to

### Buttons ###
BTN_BACK = pg.Rect(20, 20, 100, 40) # Button to jump back
BTN_ADVANCED = pg.Rect(WIDTH - 120, HEIGHT - 60, 100, 40)

### For actions ###
ACTION_LABELS = {"Left": "Select", "Right": "Mark", "Hint": "Hint", "Undone": "Undone"} # Define the action names
ACTION_HIGHLIGHT_COLOR = {"Left": GREEN, "Right": HISTORY_RIGHT_COLOR, "Hint": GOLD, "Undone": UNDONE_COLOR} # Defines the colors to show in

### History Detail Entry ###
ENTRY_X = 60 # x-cord of the entries in detail
ENTRY_WIDTH = 680 # The width of each entry
ENTRY_HEIGHT = 44 # The height of each entry
ENTRY_SPACING = 54 # The place between two 
LIST_TOP = 190 # Start y-cord

DETAIL_ABOVE = 120 # The top value of the action list
DETAIL_BELOW = 560 # The bottom value of the action list

### Terminal ###
MAX_LINES = 200     # The number of calculated lines for performance
INPUT_MAX_LEN = 100 # The numbers of chars each input can have
LINE_HEIGHT = 22   # The size of the lines

SIZE_COMMANDS = ("4x4", "5x5", "6x6", "7x7") # The Sizes to handle

ULTRA_COMMANDS = {
    "playultra4x4": 4, "pu4x4": 4,
    "playultra5x5": 5, "pu5x5": 5,
    "playultra6x6": 6, "pu6x6": 6,
    "playultra7x7": 7, "pu7x7": 7,
} # Ultra commands to start a game with the given size

PLAY_COMMANDS = {
    "play4x4": 4, "p4x4": 4,
    "play5x5": 5, "p5x5": 5,
    "play6x6": 6, "p6x6": 6,
    "play7x7": 7, "p7x7": 7,
} # Normal commands to start a game with the given size

NAVIGATE_COMMANDS = {
    "history": "HISTORY",
    "settings": "SETTINGS",
    "about": "ABOUT",
    "achievements": "ACHIEVEMENTS",
    "advancedsettings": "ADVANCED_SETTINGS"
} # Commands to navigate to the given screen

### Achievements ###
ACHIEVEMENT_MILESTONES = [1, 25, 50, 75, 100, 150, 200] # The number of wins for each milestone

GENERAL_GAME_MILESTONES = [1, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000] # All combined game numbers
GENERAL_TIME_MILESTONES = [
    ("playtime_30m", 30 * 60),
    ("playtime_1h", 60 * 60),
    ("playtime_5h", 5 * 60 * 60),
    ("playtime_10h", 10 * 60 * 60),
    ("playtime_24h", 24 * 60 * 60),
] # (key, seconds) Total play time

TIME_ACHIEVEMENTS = {
    (4, False): [("4x4_7.5s", 7.5), ("4x4_10s", 10), ("4x4_15s", 15)],
    (4, True): [("4x4_ultra_20s", 20), ("4x4_ultra_25s", 25), ("4x4_ultra_30s", 30)],
    (5, False): [("5x5_30s", 30), ("5x5_35s", 35), ("5x5_45s", 45)],
    (5, True): [("5x5_ultra_60s", 60), ("5x5_ultra_70s", 70), ("5x5_ultra_90s", 90)],
    (6, False): [("6x6_60s", 60), ("6x6_70s", 70), ("6x6_80s", 80)],
    (6, True): [("6x6_ultra_180s", 180), ("6x6_ultra_200s", 200), ("6x6_ultra_240s", 240)],
    (7, False): [("7x7_75s", 75), ("7x7_90s", 90), ("7x7_120s", 120)],
    (7, True): [("7x7_ultra_270s", 270), ("7x7_ultra_300s", 300), ("7x7_ultra_330s", 330)],    
} # Per (size, ultra): list of (key, max seconds needed)

EASTER_EGG_ACHIEVEMENTS = ["hannah_found", "hannah_completed", "42_found", "terminal_found"] # Easter egg achievements

ACHIEVEMENT_LABELS = {
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
    "1_5x5_ultra": "Overchrged 5x5 (1x 5x5 Ultra)",
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
}

# Add labels for every situation it is not predefined
_MILESTONE_TIER_NAMES = {
    1: "First Steps",
    25: "Getting Started",
    50: "Dedicated",
    75: "Committed",
    100: "Century",
    150: "Veteran",
    200: "Master",
}

for _n in DIFFICULTIES: # Block created by AI
    for _ultra in (False, True):
        _suffix = "_ultra" if _ultra else ""
        _mode_label = "Ultra" if _ultra else ""
        for _m in ACHIEVEMENT_MILESTONES:
            ACHIEVEMENT_LABELS.setdefault(f"{_m}_{_n}x{_n}{_suffix}", f"{_MILESTONE_TIER_NAMES[_m]} {_n}x{_n}{_mode_label} ({_m}x)")
        for _key, _seconds in TIME_ACHIEVEMENTS.get((_n, _ultra), []):
            _sec_label = f"{_seconds:g}s"
            ACHIEVEMENT_LABELS.setdefault(_key, f"{_n}x{_n}{_mode_label} Speedrun: Under {_sec_label}")
            
for _m in GENERAL_GAME_MILESTONES:
    ACHIEVEMENT_LABELS[f"games_{_m}"] = f"{_m} Games Played"
for _key, _seconds in GENERAL_TIME_MILESTONES:
    _hours = _seconds / 3600
    _time_label = f"{_hours:g}h" if _hours >= 1 else f"{int(_seconds // 60)}min"
    ACHIEVEMENT_LABELS[_key] = f"{_time_label} Played In Total"
del _n, _ultra, _suffix, _mode_label, _m, _key, _seconds, _sec_label, _hours, _time_label 

DEFAULT_ACHIEVEMENTS = {
    "hannah_completed": False,
    "hannah_found": False,
    "42_found": False,
    "terminal_found": False,
    "1_4x4": False,
    "25_4x4": False,
    "50_4x4": False,
    "75_4x4": False,
    "100_4x4": False,
    "150_4x4": False,
    "200_4x4": False,
    "4x4_7.5s": False,
    "4x4_10s": False,
    "4x4_15s": False,
    "1_4x4_ultra": False,
    "25_4x4_ultra": False,
    "50_4x4_ultra": False,
    "75_4x4_ultra": False,
    "100_4x4_ultra": False,
    "150_4x4_ultra": False,
    "200_4x4_ultra": False,
    "4x4_ultra_20s": False,
    "4x4_ultra_25s": False,
    "4x4_ultra_30s": False,
    "1_5x5": False,
    "25_5x5": False,
    "50_5x5": False,
    "75_5x5": False,
    "100_5x5": False,
    "150_5x5": False,
    "200_5x5": False,
    "5x5_30s": False,
    "5x5_35s": False,
    "5x5_45s": False,
    "1_5x5_ultra": False,
    "25_5x5_ultra": False,
    "50_5x5_ultra": False,
    "75_5x5_ultra": False,
    "100_5x5_ultra": False,
    "150_5x5_ultra": False,
    "200_5x5_ultra": False,
    "5x5_ultra_60s": False,
    "5x5_ultra_70s": False,
    "5x5_ultra_90s": False,
    "1_6x6": False,
    "25_6x6": False,
    "50_6x6": False,
    "75_6x6": False,
    "100_6x6": False,
    "150_6x6": False,
    "200_6x6": False,
    "6x6_60s": False,
    "6x6_70s": False,
    "6x6_80s": False,
    "1_6x6_ultra": False,
    "25_6x6_ultra": False,
    "50_6x6_ultra": False,
    "75_6x6_ultra": False,
    "100_6x6_ultra": False,
    "150_6x6_ultra": False,
    "200_6x6_ultra": False,
    "6x6_ultra_180s": False,
    "6x6_ultra_200s": False,
    "6x6_ultra_240s": False,
    "1_7x7": False,
    "25_7x7": False,
    "50_7x7": False,
    "75_7x7": False,
    "100_7x7": False,
    "150_7x7": False,
    "200_7x7": False,
    "7x7_75s": False,
    "7x7_90s": False,
    "7x7_120s": False,
    "1_7x7_ultra": False,
    "25_7x7_ultra": False,
    "50_7x7_ultra": False,
    "75_7x7_ultra": False,
    "100_7x7_ultra": False,
    "150_7x7_ultra": False,
    "200_7x7_ultra": False,
    "7x7_ultra_270s": False,
    "7x7_ultra_300s": False,
    "7x7_ultra_330s": False,
}

for _m in GENERAL_GAME_MILESTONES: # This Block is from AI
    DEFAULT_ACHIEVEMENTS[f"games_{_m}"] = False
for _key, _seconds in GENERAL_TIME_MILESTONES:
    DEFAULT_ACHIEVEMENTS[_key] = False
del _m, _key, _seconds 

def _achievement_page(title, keys):
    return {"title": title, "keys": keys}

ACHIEVEMENT_PAGES = (
    [_achievement_page("General", [f"games_{m}" for m in GENERAL_GAME_MILESTONES] + [key for key, _ in GENERAL_TIME_MILESTONES])]
    + [
        _achievement_page(
            f"{n}x{n}{' Ultra' if ultra else ''}",
            [f"{m}_{n}x{n}{'_ultra' if ultra else ''}" for m in ACHIEVEMENT_MILESTONES] + [key for key, _ in TIME_ACHIEVEMENTS.get((n, ultra), [])]
        )
        for n in DIFFICULTIES for ultra in (False, True)
    ]
    + [_achievement_page("Easter Eggs",
    EASTER_EGG_ACHIEVEMENTS)]
)
    

# Settings and Progress
DEFAULT_SETTINGS = {
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
    "input_order": "column_row_action",
} # The defaults, for the case no file exists.

### Advanced Settings ###
LANGUAGES_DIR = "rsc/languages"
BUILTIN_LANGUAGE = "english" # Fallback language

INPUT_ORDER_OPTIONS = ["column_row_action", "row_column_action", "action_column_row", "action_row_column"]
INPUT_ORDER_LABELS = {
    "column_row_action": "Column, Row, Action",
    "row_column_action": "Row, Column, Action",
    "action_column_row": "Action, Column, Row",
    "action_row_column": "Action, Row, Column",
} # Human readable

DEFAULT_KEYBINDINGS = {
    "menu": {"key": "m", "ctrl": True},
    "new_round": {"key": "n", "ctrl": True},
    "fullscreen": {"key": "f11", "ctrl": False},
    "undo": {"key": "z", "ctrl": True},
    "pause": {"key": "p", "ctrl": False},
    "hint": {"key": "h", "ctrl": False},
    "right_click": {"key": "r", "ctrl": False},
}

KEYBINDINGS_LABELS = {
    "menu": "Back to Menu",
    "new_round": "New Round",
    "fullscreen": "Toggle Fullscreen",
    "undo": "Undo",
    "pause": "Pause",
    "hint": "Use Hint",
    "right_click": "Right-Click Cell",
}

def keybinding_label(binding):
    key_part = binding.get("key", "?").upper()
    return f"Ctrl+{key_part}" if binding.get("ctrl") else key_part


# Jump back system
OPPOSITE_DIRECTION = {"up": "down", "down": "up", "left": "right", "right": "left"}

### Easter Eggs ###
HANNAH_SIZE = 5 # The grid size of the Hannah Easter Egg
HANNAH_MESSAGE = ["H", "A", "N", "N", "A", "H", None, "B", "Y", None, "H", "E", "A", "R", "T", None, "F", "O", "R", None, "E", "V", "E", "R"] # The Easter Egg message
HANNAH_TITE_SIZE = 110 # The width and height of one tile in the scroll strip
HANNAH_TITE_GAP = 18   # The space between two tiles
HANNAH_SPACE_GAP = 46  # The extra space for word breaks
HANNAH_STRIP_Y = 260   # The vertical center of the scroll strip

### Others ###
SAMPLE_RATE = 44100 # Sample Rate for the generated audios
WHEEL_CLICK_GUARD_MS = 500 # To avoid trackpad errors while scrolling
WHEEL_CLICK_GUARD_MS_min = 20 # To do it with scrolls after
FOCUS_IDLE_MS = 3000 # Time until the keyboard navigation position jumps to the mouse hover
XOR_KEY = b"Mati_Obfuscation_Key_2026" # A fixed key, just to make it uneditable not to make it save

### Scrollbars ###
SCROLLBAR_WIDTH = 8        # Width of the scrollbar
SCROLLBAR_MIN_LENGTH = 30  # Smallest size of the scrollbar
SCROLLBAR_MAX_ALPHA = 190  # See threw mouse hoverd
SCROLLBAR_MOVE_ALPHA = 130 # Screen moving without hover
SCROLLBAR_VISIBLE_MS = 700 # How long the scrollbar stays visible without hovering or moving

### Hold to repeat ###
KEY_REPEAT_DELAY_MS = 400   # Time until a held key starts repeating
KEY_REPEAT_INTERVAL_MS = 90 # Time between repeats while key pressed

### MP4 export ###
EXPORT_FPS = 30           # Frames per second of an exported video
EXPORT_TAIL_MS = 1500     # Time the final board stays on the screen
EXPORT_MARGIN = 30        # Empty space around the grid
EXPORT_HEADER_HEIGHT = 40 # Space above the grid for time
EXPORT_QUALITIES = [("Standard", 1), ("High", 2), ("Ultra", 4)] # Name + render scale multiplier
EXPORT_FPS_CHOICES = [30, 60] # Selecable fps
