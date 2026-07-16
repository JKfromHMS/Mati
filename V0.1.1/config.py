### Mati (Mathematics and tactic intelligence) ###
### V0.1.1 Beta V1.0.11 ###
### Author: Janosch Klawatsch, 16.07.2026 ###
### config file V0.1.3 ###

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

### Difficulties ###
DIFFICULTIES = [4, 5, 6, 7]  # The grid sizes
DIFFICULTY_NAMES = {
    4: "4x4 -   Easy",
    5: "5x5 -  Normal",
    6: "6x6 - Advanced",
    7: "7x7 -  Expert"
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

### Others ###
SAMPLE_RATE = 44100 # Sample Rate for the generated audios
WHEEL_CLICK_GUARD_MS = 500 # To avoid trackpad errors while scrolling