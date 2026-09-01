### Mati (Mathematics and tactic intelligence) ###
### V0.6.3 (Beta V1.0.24) ###
### Author: Janosch Klawatsch, 2026-09-01 ###
### helpers file V0.6.2 ###

### Structure-Plan ###
# - alt_hover.py - Keyboard movement hovering #
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
import glob # To find every language file
import os   # For paths
import pygame as pg

### Own ###
import config as con


### -Functions- ###
def history_content_height(count):
    if count == 0:
        return 0
    
    return (count - 1) * con.ENTRY_SPACING + con.ENTRY_HEIGHT


def history_scroll_bounds(count):
    content = history_content_height(count)
    if content == 0:
        return 0
    
    visible = con.HISTORY_VISIBLE_BOTTOM - con.LIST_TOP
    
    return min(0, visible - content)


def hannah_content_width():
    total = 40
    last_i = max(i for i, ch in enumerate(con.HANNAH_MESSAGE) if ch)
    for i, letter_char in enumerate(con.HANNAH_MESSAGE):
        if letter_char is None:
            total += con.HANNAH_SPACE_GAP
        else:
            total += con.HANNAH_TITE_SIZE
            if i != last_i:
                total += con.HANNAH_TITE_GAP
                
    return total
                

def hannah_scroll_bounds():
    return min(0, con.HANNAH_VISIBLE_LENGTH - hannah_content_width())


def settings_sections(game):
    # Check if the terminal already was found
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    
    timer_rows = ["toggle_timer"]
    if game.timer_enabled:
        timer_rows.append("toggle_ms")
        
    display_rows = ["toggle_fullscreen", "toggle_live_clock"]
    gameplay_rows = ["toggle_history", "toggle_sound", "toggle_alt_control"]
    
    sections = []
    
    # X coordinates
    left_x = con.WIDTH // 2 - 235
    right_x = con.WIDTH // 2 + 15
    mid_x = con.WIDTH // 2 - 110
    y = 150
    
    if terminal_found:
        ultra_rows = ["toggle_ultra_timer"]
        if game.ultra_timer_enabled:
            ultra_rows.extend(["toggle_ultra_timer_ms", "toggle_ultra_timer_clock"])
        else:
            ultra_rows.extend(["toggle_ultra_timer_clock", ""])
        
        sections.extend([
            ("gameplay", gameplay_rows, left_x, y),
            ("timer", timer_rows, left_x, y + 138),
            ("ultra_mode", ultra_rows, right_x, y),
            ("display", display_rows, right_x, y + 138)
        ])

    else:
        sections.extend([
            ("gameplay", gameplay_rows, mid_x, y),
            ("timer", timer_rows, left_x, y + 138),
            ("display", display_rows, right_x, y + 138)
        ])
        
    return sections
    
    
def settings_layout(game): # computes button rects and headers
    buttons = {"back": BTN_BACK}
    headers = []
    
    sections = settings_sections(game)
    
    for title, keys, start_x, start_y in sections:
        headers.append((title, start_x, start_y))
        y = start_y + 24
        for key in keys:
            if key:
                buttons[key] = pg.Rect(start_x, y, 220, 32)
            y += 34
        
    # Layout for bottom buttons
    bottom_y = 525
    buttons["stats"] = pg.Rect(con.WIDTH // 2 - 250, bottom_y, 160, 34) # Stats button
    buttons["achievements"] = pg.Rect(con.WIDTH // 2 - 80, bottom_y, 160, 34) # Achievement button
    buttons["about"] = pg.Rect(con.WIDTH // 2 + 90, bottom_y, 160, 34) # About button
    # buttons["advanced"] = con.BTN_ADVANCED
    
    return buttons, headers # Give both back


#def settings_buttons(game): # Create the buttons for settings
#    buttons, _ = settings_layout(game)
#    
#    return buttons


def available_languages():
    result = [("English", con.BUILTIN_LANGUAGE)]
    if os.path.isdir(con.LANGUAGES_DIR):
        for path in sorted(glob.glob(os.path.join(con.LANGUAGES_DIR, "*.smati"))):
            stem = os.path.splitext(os.path.basename(path))[0]
            if stem.lower() != con.BUILTIN_LANGUAGE:
                result.append((stem.capitalize(), stem.lower()))
    
    return result


#def advanced_settings_layout(game):
#    buttons = {"back": BTN_BACK}
    #
    # Left column:
    #buttons["game_volume"] = pg.Rect(60, 160, 260, 10)
    #buttons["terminal_volume"] = pg.Rect(60, 215, 260, 10)
    #buttons["toggle_terminal_sound"] = pg.Rect(60, 245, 220, 34)
   # buttons["language_dropdown"] = pg.Rect(60, 335, 220, 34)
    
   # if getattr(game, "language_dropdown_open", False):
  #      for i, (label, _internal) in enumerate(available_languages()):
        #    buttons[f"language_option_{i}"] = pg.Rect(60, 340 + 34 * (i + 1), 220, 30)
  #          
 #   # Right column
   # for i in range(len(con.INPUT_ORDER_OPTIONS)):
 #       buttons[f"input_order_{i}"] = pg.Rect(420, 135 + i * 40, 300, 32)
        
    #for i, action in enumerate(con.DEFAULT_KEYBINDINGS):
    #    buttons[f"keybind_{action}"] = pg.Rect(600, 335 + i * 30, 160, 26)
        
    #return buttons


### Buttons ###
BTN_BACK = pg.Rect(20, 20, 100, 40) # Button to jump back
BTN_ADVANCED = pg.Rect(con.WIDTH - 120, con.HEIGHT - 60, 100, 40)

ACH_PREV_RECT = pg.Rect(20, 250, 37, 100)
ACH_NEXT_RECT = pg.Rect(743, 250, 37, 100)

ACH_GAMES_TILE_RECT = pg.Rect(75, 185, 310, 330)
ACH_TIME_TILE_RECT = pg.Rect(415, 185, 310, 330)

ACH_GAMES_PREV_RECT = pg.Rect(
    ACH_GAMES_TILE_RECT.x + 8, ACH_GAMES_TILE_RECT.y + 43, con.ACH_TILE_BTN_SIZE, con.ACH_TILE_BTN_SIZE,
)
ACH_GAMES_NEXT_RECT = pg.Rect(
    ACH_GAMES_TILE_RECT.right - 8 - con.ACH_TILE_BTN_SIZE, ACH_GAMES_TILE_RECT.y + 43, con.ACH_TILE_BTN_SIZE, con.ACH_TILE_BTN_SIZE,
)


def fmt_total_time(ms):
    hours, minutes, _, _ = format_duration_short(ms) # Get the right values
    return f"{hours}h {minutes:02}min" if hours else f"{minutes}min"

def fmt_stat_time(ms): # The time for stats
    if ms is None: return "-"
    _, minutes, seconds, msec = format_duration_short(ms) # Get the right values
    return f"{minutes}:{seconds:02}:{msec:03}min" if minutes else f"{seconds}:{msec:03}s"

def format_duration(play_time_ms): # Changes the time from ms to mins and secs
    _, minutes, seconds, ms = format_duration_short(play_time_ms) # Get the right values
    return f"{minutes}:{seconds:02}:{ms:03}min" # Give the transfered time back

def format_duration_short(play_time_ms): # Changes the time from ms to mins and secs
    total_ms = max(0, play_time_ms)
    ms = total_ms % 1000 # get the right number of ms
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60 # ms in s
    minutes = (total_seconds // 60) % 60 # get the minutes
    hours = total_seconds // 3600 # get the hours
    return hours, minutes, seconds, ms # Give the transfered time back


def milestone_default_index(keys, achievements):
    for i, key in enumerate(keys):
        if not achievements.get(key):
            return i
    return len(keys) - 1


def milestone_fraction(current, target):
    if target <= 0: 
        return 1.0
    return max(0.0, min(1.0, current / target))


#def history_filter_buttons(game): # Defines the filter buttons
#    buttons = {} # Empty button list
#    labels_values = [("All", None)] + [(f"{n}x{n}", n) for n in con.DIFFICULTIES] # How the buttons should be named
#    btn_w, gap = 90, 25 # Defines the width off the buttons and the unused space between them
#    total_w = len(labels_values) * btn_w + (len(labels_values) - 1) * gap # The width the button can get
#    start_x = con.WIDTH // 2 - total_w // 2 # Defines were the buttons should start
#    for i, (label, val) in enumerate(labels_values): # Goes threw every label
#        key = "size_all" if val is None else f"size_{val}" # Get the button name
#        buttons[key] = pg.Rect(start_x + i * (btn_w + gap), 95, btn_w, 36) # Inteprate the daata as buttons
#
#    has_ultra_entries = any(entry.get("ultra") for entry in game.history_entries) or bool(getattr(game, "achievements", {}).get("terminal_found"))
#    if has_ultra_entries:
#        buttons["top10"] = pg.Rect(con.WIDTH // 2 - 230, 140, 220, 36) # Defines the top 10 button
#        buttons["ultra"] = pg.Rect(con.WIDTH // 2 + 10, 140, 220, 36) # Defines the ultra button
#    else:
#        buttons["top10"] = pg.Rect(con.WIDTH // 2 - 110, 140, 220, 36) # Centered top 10 button when no ultra entries exist
#    return buttons # Give the buttons back 

def history_entry_rect(i, scroll_y): # Defines the place for the history
    y = con.LIST_TOP + i * con.ENTRY_SPACING + scroll_y # That they do not cover each other
    return pg.Rect(con.ENTRY_X, y, con.ENTRY_WIDTH - 50, con.ENTRY_HEIGHT) # The build information for the entry

def history_delete_rect(i, scroll_y): # Defines the place for a entry that got deleted
    y = con.LIST_TOP + i * con.ENTRY_SPACING + scroll_y # That they do not cover each other
    return pg.Rect(con.ENTRY_X + con.ENTRY_WIDTH - 44, y, 40, con.ENTRY_HEIGHT) # The build information for the entry



def history_scrollbar_track():
    return pg.Rect(con.ENTRY_X + con.ENTRY_WIDTH + 6, con.LIST_TOP, con.SCROLLBAR_WIDTH, con.HISTORY_VISIBLE_BOTTOM - con.LIST_TOP)


DETAIL_EXPORT_BUTTON = pg.Rect(530, 20, 250, 30)
DETAIL_QUALITY_BUTTON = pg.Rect(530, 54, 120, 24)
DETAIL_FPS_BUTTON = pg.Rect(660, 54, 120, 24)
DETAIL_RESET_BUTTON = pg.Rect(530, 86, 250, 26)
DETAIL_SCROLLBAR_TRACK = pg.Rect(785, 120, con.SCROLLBAR_WIDTH, 438)


def detail_action_rect(i, scroll_y): # Action view switch
    y = 120 + i * 34 + scroll_y # Defines the height
    return pg.Rect(530, y, 250, 30) # Give the button pos ans size


def play_grid_offset(n): # Defines the offset values 
    offset_x = con.WIDTH // 2 - ((n + 1) * con.CELL_SIZE) // 2  # Something like the grid x to start
    if n == 7: n = 8 # Correct a 7x7 misdrawing
    offset_y = con.HEIGHT // 2 - ((n + 1) * con.CELL_SIZE) // 2 # Something like the grid y to start
    return offset_x, offset_y # Give the values back

### History-Detail helpers (Start entry) ###
def detail_display_actions(data): # makes start to real action
    actions = data.get("actions", []) # the real actions
    start_entry = {"time": 0, "type": "Start", "r": None, "c": None, "synthetic": True}
    return [start_entry] + actions # give start and actions back

def detail_key_for(i): # position into key
    return "action_start" if i == 0 else f"action_{i}" # Give back the right focus

#def play_buttons(): # The button in the game 
#    return {
#        "back": BTN_BACK,
#        "hint": pg.Rect(con.WIDTH - 147, 50, 130, 34),
#        "undo": pg.Rect(con.WIDTH - 147, 90, 130, 34),
#        "restart": pg.Rect(con.WIDTH - 147, 130, 130, 34),
#        "pause": pg.Rect(con.WIDTH - 147, 170, 130, 34),
#        "menu": pg.Rect(con.WIDTH - 650, con.HEIGHT // 2 + 75, 130, 50),
#        "break": pg.Rect(con.WIDTH - 450, con.HEIGHT // 2 + 75, 130, 50),
#        "new": pg.Rect(con.WIDTH - 250, con.HEIGHT // 2 + 75, 130, 50)
#    } # Give them back
#    
#    
#def resume_choice_buttons(): # Creates the buttons for the decide of continue
#    return {
#        "resume": pg.Rect(con.WIDTH // 2 - 240, 300, 210, 50),
#        "new": pg.Rect(con.WIDTH // 2 + 30, 300, 210, 50),
#        "cancel": BTN_BACK
#    } # Give the buttons back
    

def hannah_scrollbar_track():
    return pg.Rect(40, con.HEIGHT - con.SCROLLBAR_WIDTH - 6, con.WIDTH - 80, con.SCROLLBAR_WIDTH)

def hannah_tile_rect(index, scroll_x):
    x = 40
    for i, letter_char in enumerate(con.HANNAH_MESSAGE):
        if i == index:
            break
        if letter_char is None:
            x += con.HANNAH_SPACE_GAP
        else:
            x += con.HANNAH_TITE_SIZE + con.HANNAH_TITE_GAP
    x += scroll_x
    y = con.HANNAH_STRIP_Y - con.HANNAH_TITE_SIZE // 2
    return pg.Rect(x, y, con.HANNAH_TITE_SIZE, con.HANNAH_TITE_SIZE)

#def hannah_buttons(): # Defines the buttons for the easter egg
#    return {"back": BTN_BACK}
#
#def hannah_play_buttons():
#    return {
#        "back": BTN_BACK,
#        "undo": pg.Rect(con.WIDTH - 150, 20, 130, 34)
#    }

def _achievement_page(title, keys):
    return {"title": title, "keys": keys}

ACHIEVEMENT_PAGES = (
    [_achievement_page("General", [f"games_{m}" for m in con.GENERAL_GAME_MILESTONES] + [key for key, _ in con.GENERAL_TIME_MILESTONES])]
    + [
        _achievement_page(
            f"{n}x{n}{' Ultra' if ultra else ''}",
            [f"{m}_{n}x{n}{'_ultra' if ultra else ''}" for m in con.ACHIEVEMENT_MILESTONES] + [key for key, _ in con.TIME_ACHIEVEMENTS.get((n, ultra), [])]
        )
        for n in con.DIFFICULTIES for ultra in (False, True)
    ]
    + [_achievement_page("Easter Eggs",
    con.EASTER_EGG_ACHIEVEMENTS)]
)

def keybinding_label(binding):
    key_part = binding.get("key", "?").upper()
    return f"Ctrl+{key_part}" if binding.get("ctrl") else key_part
