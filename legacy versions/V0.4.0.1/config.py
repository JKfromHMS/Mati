### Mati (Mathematics and tactic intelligence) ###
### V0.4.0.1 Beta V1.0.18 ###
### Author: Janosch Klawatsch, 10.08.2026 ###
### config file V0.4.2 ###

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
import pygame as pg # Something like the engine

### -Constants- ###
### Sizes ###
WIDTH = 800    # The wide of the window
HEIGHT = 600   # The heigh of the window
CELL_SIZE = 60 # The size of each cell in the grid

MIN_REAL_WIDTH = 480  # To restrict the resize to a good looking size
MIN_REAL_HEIGHT = 360 # To restrict the resize to a goof lokking size

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
    7: "Expert"
} # Names for the grid sizes
HINTS_PER_GAME = 3 # The number of hints the player have each game
HISTORY_DIR = "history" # The name of the folder that includes the save games
SETTINGS_FILE = "settings.smati" # The file that saves settings and statistics
EXPORT_DIR = "exports" # The folder mp4 exports get saved to

### Buttons ###
BTN_BACK = pg.Rect(20, 20, 100, 40) # Button to jump back

### For actions ###
ACTION_LABELS = {"Left": "Select", "Right": "Mark", "Hint": "Hint", "Undone": "Undone"} # Define the action names
ACTION_HIGHLIGHT_COLOR = {"Left": GREEN, "Right": HISTORY_RIGHT_COLOR, "Hint": GOLD, "Undone": UNDONE_COLOR} # Defines the colors to show in

### History Detail Entry ###
ENTRY_X = 60 # x-cord of the entries in detail
ENTRY_WIDTH = 680 # The width of each entry
ENTRY_HEIGHT = 44 # The height of each entry
ENTRY_SPACING = 54 # The place between two 
LIST_TOP = 190 # Start y-cord

### Termianl ###
MAX_LINES = 50     # The number of calculated lines for performance
INPUT_MAX_LEN = 60 # The numbers of chars each input can have
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
} # Commands to navigate to the given screen

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
