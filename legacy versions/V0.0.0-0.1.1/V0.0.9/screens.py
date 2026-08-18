### Mati (Mathematics and tactic intelligence) ###
### V0.0.9 Beta V1.0.9 ###
### Author: Janosch Klawatsch, 10.07.2026 ###
### screens file V0.0.1 ###

### Structure-Plan ###
# - config.py - Constants #
# - level.py - Generate Levels, Check Wins ... #
# - persistence.py - Save and load of .mati files #
# - widgets.py - Draw-Functions #
# - game.py - The main game handling #
# - screens.py - Building the screens #
# - main.py - Entry point and main loop #
# - audio.py - Sound generation #

### -Imports- ###
### External ###
import pygame as pg # Something like the engine on which the game runs.

### Own ###
import config as con
import widgets as w

### Other Constants ###
BTN_BACK = pg.Rect(20, 20, 100, 40) # Button to jump back
ACTION_LABELS = {"Left": "Select", "Right": "Mark", "Hint": "Hint"} # Define the action names
_ENTRY_WIDTH =  300 # The WIDTH of an entry in the history view

### Functions ###
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
    buttons["quit"] = pg.Rect(con.WIDTH // 2 - 110, y + 54 + 54, 220, 44) # quit button
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
        "about": pg.Rect(con.WIDTH // 2 - 110, 400, 220, 42)
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
    
    w.draw_button(buttons["about"], "About", buttons["about"].collidepoint(mx, my)) # let the about button draw
    
### About ###
def draw_about(mx, my):
    w.draw_title("About Mati", con.TEXT_COLOR, con.WIDTH // 2, 90) # Draw the title
    w.draw_button(BTN_BACK, "Back", BTN_BACK.collidepoint(mx, my)) # Let back button draw
    w.draw_text("Created by:", con.TEXT_COLOR, con.WIDTH // 2, 240) # Draw the created by text
    w.draw_text("Janosch Klawatsch", con.TEXT_COLOR, con.WIDTH // 2, 280) # Draw Janosch Klawatsch
    
### History ###
def history_entry_rect(i, scroll_y): # Defines the place for the history
    y = 100 + i * 60 + scroll_y # That they do not cover each other
    return pg.Rect(con.WIDTH // 2 - _ENTRY_WIDTH // 2, y, _ENTRY_WIDTH - 45, 42) # The build information for the entry

def history_delete_rect(i, scroll_y): # Defines the place for a entry that got deleted
    y = 100 + i * 60 + scroll_y # That they do not cover each other
    return pg.Rect(con.WIDTH // 2 + _ENTRY_WIDTH // 2, y, 40, 42) # The build information for the entry

def draw_history(game, mx, my): # Draw the history
    w.draw_title("History", con.TEXT_COLOR, con.WIDTH // 2, 50) # Draw the title
    w.draw_button(BTN_BACK, "Menu", BTN_BACK.collidepoint(mx, my)) # Draw the back button
    
    if not game.history_files: # If no saved games found
        w.draw_text("No saved files found!", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 200) # Say it
        return # End here
    
    screen = w.get_screen() # Get screen information
    clip_area = pg.Rect(0, 80, con.WIDTH, con.HEIGHT - 80) # Define the area for the history files
    screen.set_clip(clip_area) # Connects the screen with the area
    for i, f in enumerate(game.history_files): # Goes threw the files
        entry_rect = history_entry_rect(i, game.history_scroll_y)   # Gets the place
        delete_rect = history_delete_rect(i, game.history_scroll_y) # Gets the cords for the delete
        display_name = f.replace(".mati", "").replace("_", " ") # Get the name in a better redable version
        w.draw_button(entry_rect, display_name, entry_rect.collidepoint(mx, my)) # let the buttons be drawn
        w.draw_button(delete_rect, "X", delete_rect.collidepoint(mx, my)) # let the delete buttons be drawm
    screen.set_clip(None) # End the are only write to get control of the fullwindow again
    
def draw_history_detail(game, mx, my): # the draw the detailed history view
    data = game.selected_history_data # Get the data from the game
    if not data: # Empty file
        game.state = "HISTORY" # Fallback
        return # End it
    
    w.draw_button(BTN_BACK, "Back", BTN_BACK.collidepoint(mx, my)) # The Back button
    w.draw_title("Actions", con.TEXT_COLOR, con.WIDTH // 2, 40) # Draw the title
    
    hn = len(data["grid"]) # Get the number off actions
    offset_x = con.WIDTH // 2 - ((hn + 1) * con.CELL_SIZE) // 2 # Offset for x direction
    offset_y = 100 # Offset for y direction
    screen = w.get_screen() # Get the screen informations
    
    for r in range(hn): # For every row
        for c in range(hn): # For every column
            rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE) # draw the grid again
            is_dimmed = data["user_dimmed"][r][c] # Get the dimmed data
            is_sel = data["user_sel"][r][c] # Get the selected data
            if is_sel:
                pg.draw.rect(screen, con.SELECTED_COLOR, rect) # Draw the cell in right color
            pg.draw.rect(screen, con.GRID_COLOR, rect, 2) # The grid lines
            color = con.DIMMED_TEXT_COLOR if is_dimmed else con.TEXT_COLOR # Defines the color
            w.draw_text(str(data["grid"][r][c]), color, rect.centerx, rect.centery) # Write the numbers in the grid
            
    w.draw_outer_border(offset_x, offset_y, hn, con.CELL_SIZE) # Draw the border around the grid
    
    start_y = offset_x + (hn + 1) * con.CELL_SIZE + 20 # Define y cord for the time
    play_time = data["play_time"] # Get the played time
    w.draw_text(f"Time: {play_time // 1000}:{(play_time % 1000):3}s", con.TARGET_COLOR, con.WIDTH // 2, start_y) # Draw the time
    
    hints_used = data.get("hints_used", 0) # Get the number of used hints
    w.draw_small(f"Used hints: {hints_used}", con.TEXT_COLOR, con.WIDTH // 2, start_y + 25) # Draw the number off used hints
    
    actions_to_show = data["actions"][-6:] # Get the first 6 actions
    for i, act in enumerate(actions_to_show): # Get the actions one by one
        second = act["time"] // 1000
        ms = act["time"] % 1000
        label = ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?")) # Get the Left and hint actions
        t_str = f'[{second:02}:{ms:03}s] Row {act["r"]+1}, Column {act["c"]+1} - {label}' # Defines the output for every action
        w.draw_small(t_str, con.TEXT_COLOR, con.WIDTH // 2, start_y + 55 + i * 24) # let the actions been drawn
        
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