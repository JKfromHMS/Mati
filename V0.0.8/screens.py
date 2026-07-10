### Mati (Mathematics and tactic intelligence) ###
### V0.0.8 Beta V1.0.8 ###
### Author: Janosch Klawatsch, 10.07.2026 ###
### screens file V0.0.0 ###

### Structure-Plan ###
# - config.py - Constants #
# - level.py - Generate Levels, Check Wins ... #
# - persistence.py - Save and load of .mati files #
# - widgets.py - Draw-Functions #
# - game.py - The main game handling #
# - screens.py - Building the screens #
# - main.py - Entry point and main loop #

### -Imports- ###
### External ###
import pygame # Something like the engine on which the game runs.

### Own ###
import config
import widgets as w

### Other Constants ###
BTN_BACK = pygame.Rect(20, 20, 100, 40) # Button to jump back
ACTION_LABELS = {"Left": "Select", "Right": "Mark", "Hint": "Hint"} # Define the action names
_ENTRY_WIDTH =  300 # The WIDTH of an entry in the history view

### Functions ###
def play_grid_offset(n): # Defines the offset values 
    offset_x = config.WIDTH // 2 - ((n + 1) * config.CELL_SIZE) // 2  # Something like the grid x
    offset_y = config.HEIGHT // 2 - ((n + 1) * config.CELL_SIZE) // 2 # Something like the grid y
    return offset_x, offset_y # Give the values back

### Menu ###
def menu_buttons(): # Creates the buttons for the main menu
    buttons = {} # A place to save the buttons
    y = 190 # Defines the y start
    for n in config.DIFFICULTIES: # Every difficultie gets its own button
        buttons[f"start_{n}"] = pygame.Rect(config.WIDTH // 2 - 110, y, 220, 44) # Buttons are defined
        y += 54 # change the position that they do not get over each other
    buttons["settings"] = pygame.Rect(config.WIDTH // 2 - 110, y, 220, 44)       # Setting button
    buttons["history"] = pygame.Rect(config.WIDTH // 2 - 110, y + 54, 220, 44)   # History button
    buttons["quit"] = pygame.Rect(config.WIDTH // 2 - 110, y + 54 + 54, 220, 44) # quit button
    return buttons # Give all buttons back

def draw_menu(mx, my): # Draw the defined menu
    w.draw_title("Mati", config.TEXT_COLOR, config.WIDTH // 2, 90) # Let the title been drawn
    w.draw_small("Mathematic and Tactic Intelligence", config.TEXT_COLOR, config.WIDTH // 2, 135) # Let the name definition been drawn
    buttons = menu_buttons() # Load the needed buttons
    for n in config.DIFFICULTIES: # For every difficult a own button
        rect = buttons[f"start_{n}"] # Get it to a drawable button
        w.draw_button(rect, config.DIFFICULTY_NAMES[n], rect.collidepoint(mx, my)) # let the buttons be drawn
    w.draw_button(buttons["settings"], "Settings", buttons["settings"].collidepoint(mx, my)) # let the setting button draw
    w.draw_button(buttons["history"], "History", buttons["history"].collidepoint(mx, my)) # Let the history button draw
    w.draw_button(buttons["quit"], "Quit", buttons["quit"].collidepoint(mx, my)) # let the quit button draw
    
### Settings ###
def settings_buttons(): # Create the buttons for the settings
    return{
        "back": BTN_BACK,
        "toggle_history": pygame.Rect(config.WIDTH // 2 - 110, 150, 220, 42),
        "toggle_timer": pygame.Rect(config.WIDTH // 2 - 110, 200, 220, 42),
        "toggle_ms": pygame.Rect(config.WIDTH // 2 - 110, 250, 220, 42),
        "about": pygame.Rect(config.WIDTH // 2 - 110, 400, 220, 42)
    } # The buttons
    
def draw_settings(game, mx ,my): # Draw the defined settings
    w.draw_title("Settings", config.TEXT_COLOR, config.WIDTH // 2, 90) # Draw Setting declaration
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
    w.draw_title("About Mati", config.TEXT_COLOR, config.WIDTH // 2, 90) # Draw the title
    w.draw_button(BTN_BACK, "Back", BTN_BACK.collidepoint(mx, my)) # Let back button draw
    w.draw_text("Created by:", config.TEXT_COLOR, config.WIDTH // 2, 240) # Draw the created by text
    w.draw_text("Janosch Klawatsch", config.TEXT_COLOR, config.WIDTH // 2, 280) # Draw Janosch Klawatsch
    
### History ###
def history_entry_rect(i, scroll_y): # Defines the place for the history
    y = 100 + i * 60 + scroll_y # That they do not cover each other
    return pygame.Rect(config.WIDTH // 2 - _ENTRY_WIDTH // 2, y, _ENTRY_WIDTH - 45, 42) # The build information for the entry

def history_delete_rect(i, scroll_y): # Defines the place for a entry that got deleted
    y = 100 + i * 60 + scroll_y # That they do not cover each other
    return pygame.Rect(config.WIDTH // 2 + _ENTRY_WIDTH // 2, y, 40, 42) # The build information for the entry

def draw_history(game, mx, my): # Draw the history
    w.draw_title("History", config.TEXT_COLOR, config.WIDTH // 2, 50) # Draw the title
    w.draw_button(BTN_BACK, "Menu", BTN_BACK.collidepoint(mx, my)) # Draw the back button
    
    if not game.history_files: # If no saved games found
        w.draw_text("No saved files found!", config.DIMMED_TEXT_COLOR, config.WIDTH // 2, 200) # Say it
        return # End here
    
    screen = w.get_screen() # Get screen information
    clip_area = pygame.Rect(0, 80, config.WIDTH, config.HEIGHT - 80) # Define the area for the history files
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
    w.draw_title("Actions", config.TEXT_COLOR, config.WIDTH // 2, 40) # Draw the title
    
    hn = len(data["grid"]) # Get the number off actions
    offset_x = config.WIDTH // 2 - ((hn + 1) * config.CELL_SIZE) // 2 # Offset for x direction
    offset_y = 100 # Offset for y direction
    screen = w.get_screen() # Get the screen informations
    
    for r in range(hn): # For every row
        for c in range(hn): # For every column
            rect = pygame.Rect(offset_x + (c + 1) * config.CELL_SIZE, offset_y + (r + 1) * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE) # draw the grid again
            is_dimmed = data["user_dimmed"][r][c] # Get the dimmed data
            is_sel = data["user_sel"][r][c] # Get the selected data
            if is_sel:
                pygame.draw.rect(screen, config.SELECTED_COLOR, rect) # Draw the cell in right color
            pygame.draw.rect(screen, config.GRID_COLOR, rect, 2) # The grid lines
            color = config.DIMMED_TEXT_COLOR if is_dimmed else config.TEXT_COLOR # Defines the color
            w.draw_text(str(data["grid"][r][c]), color, rect.centerx, rect.centery) # Write the numbers in the grid
            
    w.draw_outer_border(offset_x, offset_y, hn, config.CELL_SIZE) # Draw the border around the grid
    
    start_y = offset_x + (hn + 1) * config.CELL_SIZE + 20 # Define y cord for the time
    play_time = data["play_time"] # Get the played time
    w.draw_text(f"Time: {play_time // 1000}:{(play_time % 1000):3}s", config.TARGET_COLOR, config.WIDTH // 2, start_y) # Draw the time
    
    hints_used = data.get("hints_used", 0) # Get the number of used hints
    w.draw_small(f"Used hints: {hints_used}", config.TEXT_COLOR, config.WIDTH // 2, start_y + 25) # Draw the number off used hints
    
    actions_to_show = data["actions"][-6:] # Get the first 6 actions
    for i, act in enumerate(actions_to_show): # Get the actions one by one
        second = act["time"] // 1000
        ms = act["time"] % 1000
        label = ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?")) # Get the Left and hint actions
        t_str = f'[{second:02}:{ms:03}s] Row {act["r"]+1}, Column {act["c"]+1} - {label}' # Defines the output for every action
        w.draw_small(t_str, config.TEXT_COLOR, config.WIDTH // 2, start_y + 55 + i * 24) # let the actions been drawn
        
### Play ###
def play_buttons(): # The button in the game 
    return {
        "back": BTN_BACK,
        "hint": pygame.Rect(config.WIDTH - 150, 20, 130, 34),
        "undo": pygame.Rect(config.WIDTH - 150, 60, 130, 34),
        "restart": pygame.Rect(config.WIDTH - 150, 100, 130, 34),
        "pause": pygame.Rect(config.WIDTH - 150, 140, 130, 34)
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
       offset_x + config.CELL_SIZE <= mx < offset_x + (n + 1) * config.CELL_SIZE and \
       offset_y + config.CELL_SIZE <= my < offset_y + (n + 1) * config.CELL_SIZE: # If the cursor is over a cell and the game is running
        hover_c = (mx - offset_x - config.CELL_SIZE) // config.CELL_SIZE # Get the column to hover
        hover_r = (my - offset_y - config.CELL_SIZE) // config.CELL_SIZE # Get the row to hover
    w.draw_hover_cross(offset_x, offset_y, n, config.CELL_SIZE, hover_r, hover_c) # Let the cross be hovered
    
    for c in range(n): # For every column
        cx = offset_x + (c + 1) * config.CELL_SIZE + config.CELL_SIZE // 2 # x cord of the column
        cy = offset_y + config.CELL_SIZE // 2 # y cord of the column center
        w.draw_text(str(game.col_sums[c]), config.TARGET_COLOR, cx, cy) # Draw the correct number 
    for r in range(n): # For every row
        cx = offset_x + config.CELL_SIZE // 2 # x cord oof the row center
        cy = offset_y + (r + 1) * config.CELL_SIZE + config.CELL_SIZE // 2 # y cord of the row center
        w.draw_text(str(game.row_sums[r]), config.TARGET_COLOR, cx, cy) # Draw the correct number
        
        flashing_cell = None # No flashing cell set
        if game.last_hint_cell is not None and pygame.time.get_ticks() - game.hint_flash_timer < 900: # Short time after a hint was used
            flashing_cell = game.last_hint_cell # Highlight the last hinted cell
            
        screen = w.get_screen() # Get inforamtion about the screen
        for r in range(n): # For every row
            for c in range(n): # For every column
                rect = pygame.Rect(offset_x + (c + 1) * config.CELL_SIZE, offset_y + (r + 1) * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE) # Define the cords
                is_dimmed = game.user_dimmed[r][c] or ((game.row_fulfilled[r] or game.col_fulfilled[c]) and not game.user_sel[r][c]) # Dimm if either should dimmed or already clear it cant be selected
                
                if game.user_sel[r][c]: # If the user selected a cell
                    pygame.draw.rect(screen, config.SELECTED_COLOR, rect) # Change color to make it visible
                elif rect.collidepoint(mx, my) and not is_dimmed and not game.won and not game.paused: # If a cell is normal in a runnign game it can be hovered
                    pygame.draw.rect(screen, config.HOVER_COLOR, rect) # Hover the cell
                    
                pygame.draw.rect(screen, config.GRID_COLOR, rect, 2) # Draw the lines between the cells
                color = config.DIMMED_TEXT_COLOR if is_dimmed else config.TEXT_COLOR # Finds the right color
                w.draw_text(str(game.grid[r][c]), color, rect.centerx, rect.centery) # Draw the new colors and dimmed thtings
                
                if flashing_cell == (r, c): # If a cell should be flashed
                    pygame.draw.rect(screen, config.GOLD, rect, 4) # Give her a golden border
                    
        w.draw_outer_border(offset_x, offset_y, n, config.CELL_SIZE) # Draw the border
        w.draw_fulfilled_indicators(game.grid, game.user_sel, game.row_sums, game.col_sums, n, offset_x, offset_y, config.CELL_SIZE) # Let the correct sums be circled
        
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
            w.draw_text(time_string, config.TEXT_COLOR, config.WIDTH // 2, config.HEIGHT - 20) # Draw the time
            
        if game.won: # If the player won
            w.draw_title("You have Won", config.GREEN, config.WIDTH // 2, config.HEIGHT - 55) # Make a label to give the player feedback
            
        if game.paused: # If the game is paused
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT)) # Generate a complete overlay
            overlay.set_alpha(210) # Set alpha attitude
            overlay.fill(config.BG_COLOR) # Fill it with background color
            screen.blit(overlay, (0, 0)) # Place it over the whole screen
            w.draw_title("Paused", config.TEXT_COLOR, config.WIDTH // 2, config.HEIGHT // 2) # Shows that in pause menu
            w.draw_button(buttons["pause"], "Continue" if game.paused else "Break", buttons["pause"].collidepoint(mx, my), enabled=not game.won) # The return to game button
            w.draw_small("Press P or the Continue Button to retrun", config.TEXT_COLOR, config.WIDTH // 2, config.HEIGHT // 2 + 45) # Gives a hint of how to return