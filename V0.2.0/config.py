### Mati (Mathematics and tactic intelligence) ###
### V0.2.0 Beta V1.0.13 ###
### Author: Janosch Klawatsch, 18.07.2026 ###
### config file V0.2.1 ###

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

### Buttons ###
BTN_BACK = pg.Rect(20, 20, 100, 40) # Button to jump back

### For actions ###
ACTION_LABELS = {"Left": "Select", "Right": "Mark", "Hint": "Hint"} # Define the action names
ACTION_HIGHLIGHT_COLOR = {"Left": GREEN, "Right": HISTORY_RIGHT_COLOR, "Hint": GOLD} # Defines the colors to show in

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

### Others ###
SAMPLE_RATE = 44100 # Sample Rate for the generated audios
WHEEL_CLICK_GUARD_MS = 500 # To avoid trackpad errors while scrolling
WHEEL_CLICK_GUARD_MS_min = 20 # To do it with scrolls after