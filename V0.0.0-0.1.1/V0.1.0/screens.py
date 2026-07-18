### Mati (Mathematics and tactic intelligence) ###
### V0.1.0 Beta V1.0.10 ###
### Author: Janosch Klawatsch, 16.07.2026 ###
### screens file V0.1.3 ###

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
### External ###
import pygame as pg # Something like the engine on which the game runs.

### Own ###
import config as con
import replay as re
import widgets as w

### Other Constants ###
BTN_BACK = pg.Rect(20, 20, 100, 40) # Button to jump back
ACTION_LABELS = {"Left": "Select", "Right": "Mark", "Hint": "Hint"} # Define the action names
ACTION_HIGHLIGHT_COLOR = {"Left": con.GREEN, "Right": con.HISTORY_RIGHT_COLOR, "Hint": con.GOLD} # Defines the colors to show in
ENTRY_X = 60 # x-cord of the entries in detail
ENTRY_WIDTH = 680 # The width of each entry
ENTRY_HEIGHT = 44 # The height of each entry
ENTRY_SPACING = 54 # The place between two 
LIST_TOP = 190 # Start y-cord

### -Functions- ###
def play_grid_offset(n): # Defines the offset values 
    offset_x = con.WIDTH // 2 - ((n + 1) * con.CELL_SIZE) // 2  # Something like the grid x
    offset_y = con.HEIGHT // 2 - ((n + 1) * con.CELL_SIZE) // 2 # Something like the grid y
    return offset_x, offset_y # Give the values back

### Menu ###
def menu_buttons(): # Creates the buttons for the main menu
    buttons = {} # A place to save the buttons
    y = 190 # Defines the y start
    for n in con.DIFFICULTIES: # Every difficultie gets its own button
        buttons[f"start_{n}"] = pg.Rect(con.WIDTH // 2 - 110, y, 220, 44) # Buttons are defined
        y += 54 # change the position that they do not get over each other
    buttons["settings"] = pg.Rect(con.WIDTH // 2 - 110, y, 220, 44)       # Setting button
    buttons["history"] = pg.Rect(con.WIDTH // 2 - 110, y + 54, 220, 44)   # History button
    buttons["quit"] = pg.Rect(con.WIDTH // 2 - 110, y + 108, 220, 44) # quit button
    return buttons # Give all buttons back

def draw_menu(mx, my): # Draw the defined menu
    w.draw_title("Mati", con.TEXT_COLOR, con.WIDTH // 2, 90) # Let the title been drawn
    w.draw_small("Mathematic and Tactic Intelligence", con.TEXT_COLOR, con.WIDTH // 2, 135) # Let the name definition been drawn
    buttons = menu_buttons() # Load the needed buttons
    for n in con.DIFFICULTIES: # For every difficult a own button
        rect = buttons[f"start_{n}"] # Get it to a drawable button
        w.draw_button(rect, con.DIFFICULTY_NAMES[n], rect.collidepoint(mx, my)) # let the buttons be drawn
    w.draw_button(buttons["settings"], "Settings", buttons["settings"].collidepoint(mx, my)) # let the setting button draw
    w.draw_button(buttons["history"], "History", buttons["history"].collidepoint(mx, my)) # Let the history button draw
    w.draw_button(buttons["quit"], "Quit", buttons["quit"].collidepoint(mx, my)) # let the quit button draw
    
### Settings ###
def settings_buttons(): # Create the buttons for the settings
    return{
        "back": BTN_BACK,
        "toggle_history": pg.Rect(con.WIDTH // 2 - 110, 150, 220, 42),
        "toggle_timer": pg.Rect(con.WIDTH // 2 - 110, 200, 220, 42),
        "toggle_ms": pg.Rect(con.WIDTH // 2 - 110, 250, 220, 42),
        "toggle_sound": pg.Rect(con.WIDTH // 2 - 110, 300, 220, 42),
        "toggle_fullscreen": pg.Rect(con.WIDTH //  2 - 110, 350, 220, 42),
        "about": pg.Rect(con.WIDTH // 2 - 110, 420, 220, 42)
    } # The buttons
    
def draw_settings(game, mx ,my): # Draw the defined settings
    w.draw_title("Settings", con.TEXT_COLOR, con.WIDTH // 2, 90) # Draw Setting declaration
    buttons = settings_buttons() # Load the buttons
    w.draw_button(buttons["back"], "Menu", buttons["back"].collidepoint(mx, my)) # Let back button draw
    
    hist_text = "Save Played: Yes" if game.save_history else "Save Played: No" # Define save text
    w.draw_button(buttons["toggle_history"], hist_text, buttons["toggle_history"].collidepoint(mx, my)) # let save toggle draw
    
    time_text = "Show Timer: Yes" if game.timer_enabled else "Show Timer: No" # Define show time text
    w.draw_button(buttons["toggle_timer"], time_text, buttons["toggle_timer"].collidepoint(mx, my)) # let show timer toggle draw
    
    ms_text = "Miliseconds: Yes" if game.timer_ms else "Miliseconds: No" # Define show miliseconds text
    w.draw_button(buttons["toggle_ms"], ms_text, buttons["toggle_ms"].collidepoint(mx, my)) # Let the show miliseconds toggle draw
    
    sound_text = "Sound: Yes" if game.sounds.enabled else "Sound: No" # Defines the text should shonw
    w.draw_button(buttons["toggle_sound"], sound_text, buttons["toggle_sound"].collidepoint(mx, my)) # Let the sound toggle draw
    
    fs_text = "Fullscreen: Yes" if game.is_fullscreen else "Fullscreen: No" # Defines the fullscreen button text
    w.draw_button(buttons["toggle_fullscreen"], fs_text, buttons["toggle_fullscreen"].collidepoint(mx, my)) # Let the fullscreen togggle draw
    w.draw_tiny("Press F11 to switch or ESC to end fullscreen", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 397)
    
    w.draw_button(buttons["about"], "About", buttons["about"].collidepoint(mx, my)) # let the about button draw
    
### About ###
def draw_about(mx, my):
    w.draw_title("About Mati", con.TEXT_COLOR, con.WIDTH // 2, 90) # Draw the title
    w.draw_button(BTN_BACK, "Back", BTN_BACK.collidepoint(mx, my)) # Let back button draw
    w.draw_text("Created by:", con.TEXT_COLOR, con.WIDTH // 2, 240) # Draw the created by text
    w.draw_text("Janosch Klawatsch", con.TEXT_COLOR, con.WIDTH // 2, 280) # Draw Janosch Klawatsch
    
### History ###
def history_filter_buttons(): # Defines the filter buttons
    buttons = {} # Empty button list
    labels_values = [("All", None)] + [(f"{n}x{n}", n) for n in con.DIFFICULTIES] # How the buttons should be named
    btn_w, gap = 90, 8 # Defines the width off the buttons and the unused space between them
    total_w = len(labels_values) * btn_w + (len(labels_values) - 1) * gap # The width the button can get
    start_x = con.WIDTH // 2 - total_w // 2 # Defines were the buttons should start
    for i, (label, val) in enumerate(labels_values): # Goes threw every label
        key = "size_all" if val is None else f"size_{val}" # Get the button name
        buttons[key] = pg.Rect(start_x + i * (btn_w + gap), 95, btn_w, 36) # Inteprate the daata as buttons
    buttons["top10"] = pg.Rect(con.WIDTH // 2 - 110, 140, 220, 36) # Defines the top 10 button
    return buttons # Give the buttons back 

def history_entry_rect(i, scroll_y): # Defines the place for the history
    y = LIST_TOP + i * ENTRY_SPACING + scroll_y # That they do not cover each other
    return pg.Rect(ENTRY_X, y, ENTRY_WIDTH - 50, ENTRY_HEIGHT) # The build information for the entry

def history_delete_rect(i, scroll_y): # Defines the place for a entry that got deleted
    y = LIST_TOP + i * ENTRY_SPACING + scroll_y # That they do not cover each other
    return pg.Rect(ENTRY_X + ENTRY_WIDTH - 44, y, 40, ENTRY_HEIGHT) # The build information for the entry

def _format_duration(play_time_ms): # Changes the time from ms to mins and secs
    total_seconds = play_time_ms // 1000 # ms in s
    minutes = total_seconds // 60 # Seconds to minutes
    seconds = total_seconds % 60  # Cut of seconds that are shown as minutes
    return f"{minutes}:{seconds:02}" # Give the transfered time back

def draw_history(game, mx, my): # Draw the history
    w.draw_title("History", con.TEXT_COLOR, con.WIDTH // 2, 50) # Draw the title
    w.draw_button(BTN_BACK, "Menu", BTN_BACK.collidepoint(mx, my)) # Draw the back button
    
    if not game.history_entries: # If no saved games found
        w.draw_text("No game saved until now, but you can change that.", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 200) # Say it
        return # End here
    
    filter_buttons = history_filter_buttons() # Load the buttons
    size_options = [("size_all", None)] + [(f"size_{n}", n) for n in con.DIFFICULTIES] # Load the size options
    for key, val in size_options: # For each option
        rect = filter_buttons[key] # extract one option
        label = "All" if val is None else f"{val}x{val}" # Defines the label
        active = (game.history_filter_size == val) # Checks if a filter is active
        w.draw_toggle_button(rect, label, rect.collidepoint(mx, my), active) # Let the buttons draw
    top10_rect = filter_buttons["top10"] # Defines top ten button
    w.draw_toggle_button(top10_rect, "Top 10", top10_rect.collidepoint(mx, my), game.history_filter_top10) # Draw top 10 button
    
    entries = game.filtered_history() # Define entrie
    if not entries: # If no entry
        w.draw_text("No game matchs your filters!", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 230) # Define the empty game message
        return # Do nothing more
    
    screen = w.get_screen() # Get screen information
    clip_area = pg.Rect(0, LIST_TOP - 10, con.WIDTH, con.HEIGHT - LIST_TOP) # Define the area for the history files
    screen.set_clip(clip_area) # Connects the screen with the area
    for i, entry in enumerate(entries): # Goes threw the files
        entry_rect = history_entry_rect(i, game.history_scroll_y)   # Gets the place
        delete_rect = history_delete_rect(i, game.history_scroll_y) # Gets the cords for the delete
        if entry_rect.bottom < LIST_TOP - 10 or entry_rect.top > con.HEIGHT: # Check position
            continue # Everything is fine
        is_hovered = entry_rect.collidepoint(mx, my) # Check the hover
        w.draw_panel_row(entry_rect, is_hovered) # Define the row for the select buttons
        w.draw_small(entry["label"], con.WHITE, entry_rect.x + 14, entry_rect.y + 11, center=False) # Declare the button text
        w.draw_small(f'{entry["size"]}x{entry["size"]}', con.WHITE, entry_rect.x + 360, entry_rect.centery) # Declare the button text
        w.draw_small(_format_duration(entry["play_time"]) + "s", con.WHITE, entry_rect.x + 480, entry_rect.centery) # Declare the button text
        w.draw_button(delete_rect, "x", delete_rect.collidepoint(mx, my)) # let the delete buttons be drawm
    screen.set_clip(None) # End the are only write to get control of the fullwindow again
    
### History-Detail ###
def detail_reset_button(): # End view switch
    return pg.Rect(540, 60, 250, 30) # Give the button position and size

def detail_action_rect(i, scroll_y): # Action view switch
    y = 100 + i * 34 + scroll_y # Defines the height
    return pg.Rect(540, y, 250, 30) # Give the button pos ans size

def _draw_full_grid(grid, row_sums, col_sums, user_sel, user_dimmed, n, offset_x, offset_y, highlight_cell=None, highlight_color=None): # Information of the grid
    screen = w.get_screen() # Load the screen information
    for c in range(n): # For every column
        cx = offset_x + (c + 1) * con.CELL_SIZE + con.CELL_SIZE // 2 # x cord of the text
        cy = offset_y + con.CELL_SIZE // 2 # y cord of the text
        w.draw_text(str(col_sums[c]), con.TARGET_COLOR, cx, cy) # Let the text draw
    for r in range(n): # For every row
        cx = offset_x + con.CELL_SIZE // 2 # x cord of the text
        cy = offset_y + (r + 1) * con.CELL_SIZE + con.CELL_SIZE // 2  # y cord of the text
        w.draw_text(str(row_sums[r]), con.TARGET_COLOR, cx, cy) # Let the text draw
    
    for r in range(n): # For every row
        for c in range(n): # For every column
            rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE) # Pos and size of every cell
            is_dimmed = user_dimmed[r][c] # Load dim situation
            if user_sel[r][c]: # If a cell is selected
                pg.draw.rect(screen, con.SELECTED_COLOR, rect) # Draw the selected cells
            pg.draw.rect(screen, con.GRID_COLOR, rect, 2) # Draw the lines between the cells
            color = con.DIMMED_TEXT_COLOR if is_dimmed else con.TEXT_COLOR # Defines the color should used
            w.draw_text(str(grid[r][c]), color, rect.centerx, rect.centery) # Let the numbers be drawn
            if highlight_cell == (r, c): # Checks if this cell is highlighted
                pg.draw.rect(screen, highlight_color or con.GOLD, rect, 4) # Draw the highlight
                
    w.draw_outer_border(offset_x, offset_y, n, con.CELL_SIZE) # Draw the border
    w.draw_fulfilled_indicators(grid, user_sel, row_sums, col_sums, n, offset_x, offset_y, con.CELL_SIZE) # Check and mark right sums

def draw_history_detail(game, mx, my): # the draw the detailed history view
    data = game.selected_history_data # Get the data from the game
    if not data: # Empty file
        game.state = "HISTORY" # Fallback
        return # End it
    
    w.draw_button(BTN_BACK, "Back", BTN_BACK.collidepoint(mx, my)) # The Back button
    
    n = (len(data["grid"])) # Load n
    offset_x, offset_y = 30, 60 # Defines the offset cords
    actions = data.get("actions", []) # Load the actions
    
    user_sel, user_dimmed, hints_used, play_time, last_action = re.reconstruct_state(data, game.detail_selected_index) # Find the screen after a action
    
    highlight_cell = None # No highlighted cell yet
    highlight_color = None # The color will be defined later
    if last_action is not None: # If there are actions
        highlight_cell = (last_action["r"], last_action["c"]) # Get the row/col from the last cell
        highlight_color = ACTION_HIGHLIGHT_COLOR.get(last_action.get("type"), con.GOLD) # Find out which color it should have
        
    _draw_full_grid(data["grid"], data["row_sums"], data["col_sums"], user_sel, user_dimmed, n, offset_x, offset_y, highlight_cell, highlight_color)
    
    footer_y = offset_y + (n + 1) * con.CELL_SIZE + 14 # Bottom
    seconds = play_time // 1000 # Get the seconds
    ms = play_time % 1000 # Get the miliseconds
    w.draw_tiny(f"Time: {seconds}:{ms:03}s", con.TEXT_COLOR, offset_x, footer_y, center=False) # Time under the grid
    w.draw_tiny(f"Hints used: {hints_used}", con.TEXT_COLOR, offset_x, footer_y + 20, center=False) # Hints used under the time
    if last_action is not None: # If a last action is defined
        label = ACTION_LABELS.get(last_action.get("type", "Left"), last_action.get("type", "?")) # Get the right action name
        w.draw_tiny(f"Selected: Row {last_action['r'] + 1}, Column {last_action['c'] + 1} - {label}", con.TEXT_COLOR, offset_x, footer_y + 40, center=False) # Describe action underneath
    else: 
        w.draw_tiny("End of game", con.DIMMED_TEXT_COLOR, offset_x, footer_y + 40, center=False) # Or that it is the last
        
    reset_rect = detail_reset_button() # Load the buttons
    w.draw_button(reset_rect, "Show End", reset_rect.collidepoint(mx, my)) # Button for end view
    
    screen = w.get_screen() # Get the screen informations
    if not actions: # If no actions defined
        w.draw_small("No action found", con.DIMMED_TEXT_COLOR, 665, 120) # Say it
    else:
        clip_area = pg.Rect(540, 100, 250, 460) # Define the area for the actions
        screen.set_clip(clip_area) # Connect it to the screen
        for i, act in enumerate(actions):
            rect = detail_action_rect(i, game.detail_scroll_y) # Get the buttons
            if rect.bottom < 100 or rect.top > 560: # If in the right spot
                continue # Everything is fine
            is_hovered = rect.collidepoint(mx, my) # check hover state
            is_selected = (game.detail_selected_index == i) # check selected state
            w.draw_panel_row(rect, is_hovered, highlighted=is_selected) # Draw the action buttons
            second = act["time"] // 1000 # Get the secs
            ms_ = act["time"] % 1000     # Get the milisecs
            label = ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?")) # Define the right label
            text_color = con.TEXT_COLOR if is_selected else con.WHITE # Defines the right color
            line = f'{second:02}:{ms_:03}s R{act["r"] + 1}/C{act["c"] + 1} {label}' # Defines the complete line
            w.draw_tiny(line, text_color, rect.x + 8, rect.y + 7, center=False) # Draw the line on the button
        screen.set_clip(None) # End clip mode
        
            
### Play ###
def play_buttons(): # The button in the game 
    return {
        "back": BTN_BACK,
        "hint": pg.Rect(con.WIDTH - 150, 20, 130, 34),
        "undo": pg.Rect(con.WIDTH - 150, 60, 130, 34),
        "restart": pg.Rect(con.WIDTH - 150, 100, 130, 34),
        "pause": pg.Rect(con.WIDTH - 150, 140, 130, 34)
    } # Give them back
    
def draw_play(game, mx, my): # draw the play view
    buttons = play_buttons() # Load the buttons
    w.draw_button(buttons["back"], "Menu", buttons["back"].collidepoint(mx, my)) # Let the back button be drawn
    
    n = game.n # Load the grid size
    offset_x, offset_y = play_grid_offset(n) # Load the offsets
    
    for r in range(n): # for every row
        if sum(game.grid[r][c] for c in range(n) if game.user_sel[r][c]) == game.row_sums[r]: # If row correct
            game.row_fulfilled[r] = True # Say its correct
    for c in range(n): # for every row
        if sum(game.grid[r][c] for r in range(n) if game.user_sel[r][c]) == game.col_sums[c]: # If column correct
            game.col_fulfilled[c] = True # Say its correct
            
    hover_r = hover_c = None # Nothing is hovered
    if not game.won and not game.paused and \
       offset_x + con.CELL_SIZE <= mx < offset_x + (n + 1) * con.CELL_SIZE and \
       offset_y + con.CELL_SIZE <= my < offset_y + (n + 1) * con.CELL_SIZE: # If the cursor is over a cell and the game is running
        hover_c = (mx - offset_x - con.CELL_SIZE) // con.CELL_SIZE # Get the column to hover
        hover_r = (my - offset_y - con.CELL_SIZE) // con.CELL_SIZE # Get the row to hover
    w.draw_hover_cross(offset_x, offset_y, n, con.CELL_SIZE, hover_r, hover_c) # Let the cross be hovered
    
    for c in range(n): # For every column
        cx = offset_x + (c + 1) * con.CELL_SIZE + con.CELL_SIZE // 2 # x cord of the column
        cy = offset_y + con.CELL_SIZE // 2 # y cord of the column center
        w.draw_text(str(game.col_sums[c]), con.TARGET_COLOR, cx, cy) # Draw the correct number 
    for r in range(n): # For every row
        cx = offset_x + con.CELL_SIZE // 2 # x cord oof the row center
        cy = offset_y + (r + 1) * con.CELL_SIZE + con.CELL_SIZE // 2 # y cord of the row center
        w.draw_text(str(game.row_sums[r]), con.TARGET_COLOR, cx, cy) # Draw the correct number
        
        flashing_cell = None # No flashing cell set
        if game.last_hint_cell is not None and pg.time.get_ticks() - game.hint_flash_timer < 900: # Short time after a hint was used
            flashing_cell = game.last_hint_cell # Highlight the last hinted cell
            
        screen = w.get_screen() # Get inforamtion about the screen
        for r in range(n): # For every row
            for c in range(n): # For every column
                rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE) # Define the cords
                is_dimmed = game.user_dimmed[r][c] or ((game.row_fulfilled[r] or game.col_fulfilled[c]) and not game.user_sel[r][c]) # Dimm if either should dimmed or already clear it cant be selected
                
                if game.user_sel[r][c]: # If the user selected a cell
                    pg.draw.rect(screen, con.SELECTED_COLOR, rect) # Change color to make it visible
                elif rect.collidepoint(mx, my) and not is_dimmed and not game.won and not game.paused: # If a cell is normal in a runnign game it can be hovered
                    pg.draw.rect(screen, con.HOVER_COLOR, rect) # Hover the cell
                    
                pg.draw.rect(screen, con.GRID_COLOR, rect, 2) # Draw the lines between the cells
                color = con.DIMMED_TEXT_COLOR if is_dimmed else con.TEXT_COLOR # Finds the right color
                w.draw_text(str(game.grid[r][c]), color, rect.centerx, rect.centery) # Draw the new colors and dimmed thtings
                
                if flashing_cell == (r, c): # If a cell should be flashed
                    pg.draw.rect(screen, con.GOLD, rect, 4) # Give her a golden border
                    
        w.draw_outer_border(offset_x, offset_y, n, con.CELL_SIZE) # Draw the border
        w.draw_fulfilled_indicators(game.grid, game.user_sel, game.row_sums, game.col_sums, n, offset_x, offset_y, con.CELL_SIZE) # Let the correct sums be circled
        
        w.draw_button(buttons["hint"], f"Hint ({game.hints_left})", buttons["hint"].collidepoint(mx, my), enabled=game.hints_left > 0 and not game.won and not game.paused) # If available sends hint find alogrithem threw the grid
        w.draw_button(buttons["undo"], "Undo", buttons["undo"].collidepoint(mx, my), enabled=bool(game.current_game_actions) and not game.won and not game.paused) # If available gives command to make the last move undone
        w.draw_button(buttons["restart"], "New", buttons["restart"].collidepoint(mx, my)) # Show the restart button
        w.draw_button(buttons["pause"], "Continue" if game.paused else "Break", buttons["pause"].collidepoint(mx, my), enabled=not game.won) # If available pause the game
        
        if game.timer_enabled: # If timer should be shown
            seconds = (game.play_time // 1000) % 60 # miliseconds to seconds
            minutes = (game.play_time // 60000) # miliseconds in minutes
            if game.timer_ms: # If the miliseconds should also been shown
                ms = game.play_time % 1000 # maximum of 999 ms
                time_string = f"Time: {minutes:02}:{seconds:02}:{ms:03}" # Defines how the time should be shown
            else:
                time_string = f"Time: {minutes:02}:{seconds:02}" # Defines how to show time
            w.draw_text(time_string, con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT - 20) # Draw the time
            
        if game.won: # If the player won
            w.draw_title("You have Won", con.GREEN, con.WIDTH // 2, con.HEIGHT - 55) # Make a label to give the player feedback
            
        if game.paused: # If the game is paused
            overlay = pg.Surface((con.WIDTH, con.HEIGHT)) # Generate a complete overlay
            overlay.set_alpha(210) # Set alpha attitude
            overlay.fill(con.BG_COLOR) # Fill it with background color
            screen.blit(overlay, (0, 0)) # Place it over the whole screen
            w.draw_title("Paused", con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2) # Shows that in pause menu
            w.draw_button(buttons["pause"], "Continue" if game.paused else "Break", buttons["pause"].collidepoint(mx, my), enabled=not game.won) # The return to game button
            w.draw_small("Press P or the Continue Button to retrun", con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2 + 45) # Gives a hint of how to return