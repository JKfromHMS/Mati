### Mati (Mathematics and tactic intelligence) ###
### V0.1.0 Beta V1.0.10 ###
### Author: Janosch Klawatsch, 16.07.2026 ###
### main file V0.1.3 ###

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
import sys    # System Commands like sys.exit() to close the tab.
import pygame as pg # Something like the engine on which the game runs.

### Own ###
import config as con     # To have the constants
import screens as s      # To draw the screens
import widgets as w      # To use the widgets
from game import Game    # To start a game
from audio import Sounds # To play sounds

### -Functions- ###
### Screen-Size ###
def toggle_fullscreen(fullscreen, windowed_size): # Switches between fulllscreen and not
    if fullscreen: # If the fullscreen is active
        real_screen = pg.display.set_mode(windowed_size, pg.RESIZABLE) # To now want screen version
        return False, real_screen # Give the want screen size back
    info = pg.display.Info() # Get the size information about the screen
    real_screen = pg.display.set_mode((info.current_w, info.current_h), pg.FULLSCREEN) # Say we want Fullscreen
    return True, real_screen # Gives the information about the fullscreen back

def compute_scale(real_w, real_h): # To calculate the scale
    scale = min(real_w / con.WIDTH, real_h / con.HEIGHT) # Scale factor
    scale = max(scale, 0.01) # Defines the minimum scale and make sure it is 
    scaled_w, scaled_h = int(con.WIDTH * scale), int(con.HEIGHT * scale) # Gets the scaled screen size
    offset_x = (real_w - scaled_w) // 2 # New offset value for x cord
    offset_y = (real_h - scaled_h) // 2 # New offset value for y cord
    return scale, scaled_w, scaled_h, offset_x, offset_y # Give the new values back

### Main ###
def main(): # The main function
    pg.init() # Pygame need to be initialized
    real_screen = pg.display.set_mode((con.WIDTH, con.HEIGHT), pg.RESIZABLE) # Define the size of the window
    pg.display.set_caption("Mati") # The shown name of the window
    virtual_screen = pg.Surface((con.WIDTH, con.HEIGHT)) # Define the virtual screen
    
    # Because fonts need pygame, they are defined in this file and not in config. But maybe they could be in widgets.
    title_font = pg.font.SysFont("arial", 48, bold=True) # For the biggest texts
    font = pg.font.SysFont("arial", 28, bold=True) # For the normal texts and buttons
    small_font = pg.font.SysFont("arial", 22) # For small  texts and most buttons
    tiny_font = pg.font.SysFont("arial",16) # A very small font
    w.init(virtual_screen, title_font, font, small_font, tiny_font)
    
    sounds = Sounds() # Load all sounds
    game = Game(sounds) # start the game with those sounds
    clock = pg.time.Clock() # Start the Clock
    
    fullscreen = False # Start in a normal window
    windowed_size = (con.WIDTH, con.HEIGHT) # The size it has
    
    while True: # Until the programm gots quit
        virtual_screen.fill(con.BG_COLOR) # Draw the background
        
        real_w, real_h = real_screen.get_size() # Split the screen into x and y
        scale, scaled_w, scaled_h, offset_x, offset_y = compute_scale(real_w, real_h) # Get the main values for the virtual screen
        
        raw_mx, raw_my = pg.mouse.get_pos() # Get the mouse cords
        vx = (raw_mx - offset_x) / scale # Get the virtual mouse x 
        vy = (raw_my - offset_y) / scale # Get the virtual mouse y
        mouse_inside = 0 <= vx <= con.WIDTH and 0 <= vy <= con.HEIGHT # Checks if mouse in the window
        mx = max(0, min(con.WIDTH, vx)) # x position to work with
        my = max(0, min(con.HEIGHT, vy)) # y position to work with
        
        for event in pg.event.get(): # Everything happend got saved
            if event.type == pg.QUIT: # If the user want to quit
                pg.quit() # End the game engine
                sys.exit() # Close the game
                
            elif event.type == pg.VIDEORESIZE: # If the user resizes the window
                if not fullscreen: # If the user is in the normal window mode
                    new_w = max(event.w, con.MIN_REAL_WIDTH) # Resize the tab, but not under the min widht
                    new_h = max(event.h, con.MIN_REAL_HEIGHT) # Resize the tab, but not under the min height
                    real_screen = pg.display.set_mode((new_w, new_h), pg.RESIZABLE) # Create the screen
                    windowed_size = (new_w, new_h) # Save the window size
            
            elif event.type == pg.KEYDOWN: # If the player pressed a key
                if event.key == pg.K_F11: # If f11 pressed
                    fullscreen, real_screen = toggle_fullscreen(fullscreen, windowed_size) # Change fullscreen and window
                    game.is_fullscreen = fullscreen # Set state to fullscreen state (True/False)
                elif event.key == pg.K_ESCAPE and fullscreen: # If the player pressed esc while fullscreen
                    fullscreen, real_screen = toggle_fullscreen(fullscreen, windowed_size) # Chanfe fullscreen and window
                    game.is_fullscreen = fullscreen # Set state to fullscreen state (True/False), but it is everytime False in this situation
                elif event.key == pg.K_p and game.state == "PLAY": # If the player pressed p in the game
                    game.toggle_pause() # Make the game paused or continued
                elif event.key == pg.K_z and (event.mod & pg.KMOD_CTRL) and game.state == "PLAY": # If the player pressed CTRL and z and is playing
                    game.undo() # Make the last move undone
                    
            elif event.type == pg.MOUSEBUTTONDOWN and mouse_inside: # If the player clicked the mousebutton
                handle_click(game, event, mx, my) # Check what for a click
            
            elif event.type == pg.MOUSEWHEEL and game.state in ("HISTORY", "HISTORY_DETAIL"): # If the player tries to scroll in history or detail view
                handle_scroll(game, event) # Handle the scroll
                
        if game.request_fullscreen_toggle: # If the user want to change the size
            fullscreen, real_screen = toggle_fullscreen(fullscreen, windowed_size) # Change fullscreen and window
            game.is_fullscreen = fullscreen # Set the fullscreen state
            game.request_fullscreen_toggle = False # We wont stuck in an endless repetition
                
        game.tick_timer() # Update the timer
        draw(game, mx, my) # Redraw the whole game
        
        real_screen.fill(con.BG_COLOR) # The Background-Color, maybe should be something else
        scaled_surface = pg.transform.smoothscale(virtual_screen, (scaled_w, scaled_h)) # Defines the virtual surface
        real_screen.blit(scaled_surface, (offset_x, offset_y)) # Place the virtual screen in the real
        pg.display.flip() # Make it visible
        clock.tick(60) # Set the framerate to 60 frames per second (fps)
    
def handle_click(game, event, mx, my): # Let the programm work with a click
    if pg.time.get_ticks() - game.last_wheel_time < con.WHEEL_CLICK_GUARD_MS: # Check if a click is really wanted
        return # Do nothing
    state = game.state # Gets the state
    
    if state == "MENU": # If the player is in the menu
        buttons = s.menu_buttons() # Load the buttons
        for n in con.DIFFICULTIES: # For every grid size
            if buttons[f"start_{n}"].collidepoint(mx, my): # If a grid size button clicked
                game.new_game(n) # Start a new game with the given grid size
                return # End of this task
        if buttons["settings"].collidepoint(mx, my): # If the player clicked on settings
            game.state = "SETTINGS" # Set state to settings
        elif buttons["history"].collidepoint(mx, my): # If the player clicked on history
            game.open_history() # Open the history
        elif buttons["quit"].collidepoint(mx, my): # If player want to quit
            pg.quit() # End the game
            sys.exit() # Close the game
    
    elif state == "SETTINGS": # If the player is in the settings
        buttons = s.settings_buttons() # Load buttons
        if buttons["back"].collidepoint(mx, my): # If the player clicked back
            game.state = "MENU" # Return to menu
        elif buttons["toggle_history"].collidepoint(mx, my): # If the player clicked history save
            game.save_history = not game.save_history # Toggle if save or not
        elif buttons["toggle_timer"].collidepoint(mx, my): # If the player clicked the timer toggle
            game.timer_enabled = not game.timer_enabled # Toggle on and off
        elif buttons["toggle_ms"].collidepoint(mx, my): # If the player clicked on ms
            game.timer_ms = not game.timer_ms # toggle between on and off
        elif buttons["toggle_sound"].collidepoint(mx, my): # If the player clicked on the sound
            game.sounds.enabled = not game.sounds.enabled # Toggle this state
        elif buttons["toggle_fullscreen"].collidepoint(mx, my): # If the player clicked on fullscreen
            game.request_fullscreen_toggle = True # activate Fullscreen or deactivate
        elif buttons["about"].collidepoint(mx, my): # If the player clicked on about
            game.state = "ABOUT" # go to about
            
    elif state == "ABOUT": # If the player is in the about
        if s.BTN_BACK.collidepoint(mx, my): # If the player clicked back
            game.state = "SETTINGS" # Return to settings
            
    elif state == "HISTORY": # If the player is in the history menu
        if s.BTN_BACK.collidepoint(mx, my): # If the player clicked on back
            game.state = "MENU" # return to the menu
            return # Task is over
        
        filter_buttons = s.history_filter_buttons() # Load the filter buttons
        if filter_buttons["size_all"].collidepoint(mx, my): # Clicked on all sizes
            game.toggle_size_filter(None) # This filter is the main, or no
            return # Task is over
        for n in con.DIFFICULTIES: # For each difficultie
            if filter_buttons[f"size_{n}"].collidepoint(mx, my): # If a size is clicked
                game.toggle_size_filter(n) # Make the filter work
                return # Task is over
        if filter_buttons["top10"].collidepoint(mx, my): # For the top 10 filter
            game.toggle_top10_filter() # Make the filter work
            return # Task is over
        
        if my <= s.LIST_TOP - 10: # If the cursor is to high
            return # Do nothing
        entries = game.filtered_history()
        for i, entry in enumerate(entries): # For each file in history files
            delete_rect = s.history_delete_rect(i, game.history_scroll_y) # Get positions for delete buttons
            entry_rect = s.history_entry_rect(i, game.history_scroll_y) # Get the positions of the buttons
            if delete_rect.collidepoint(mx, my): # If the player want to delete something
                game.delete_history(entry["filename"]) # Delete the selected file
                return # Task is over
            if entry_rect.collidepoint(mx, my): # If the player clicked on a file
                game.open_history_detail(entry["filename"]) # Open the file
                return # Task is done
    
    elif state == "HISTORY_DETAIL": # If in a history file
        if s.BTN_BACK.collidepoint(mx, my): # If clicked on back
            game.open_history() # Reset the scrol etc
            return # Task is over
        if s.detail_reset_button().collidepoint(mx, my): # End view wanted
            game.reset_detail_view() # Let the game reset to the end view
            return # Task is over
        if game.selected_history_data: # Clicked on a action
            actions = game.selected_history_data.get("actions", []) # Load the action
            for i in range(len(actions)): # Froe each action
                rect = s.detail_action_rect(i, game.detail_scroll_y) # Scroll area
                if rect.bottom < 100 or rect.top > 560: # checking positioning
                    continue # everything is fine
                if rect.collidepoint(mx, my): # If the player clicked it
                    game.select_detail_action(i) # Show action
                    return # Task is done
            
    elif state == "PLAY": # If the player is playing
        buttons = s.play_buttons() #  load buttons
        if buttons["back"].collidepoint(mx, my): # If the player clicked back
            game.state = "MENU" # Return to the menu
            return # Task is over
        if buttons["hint"].collidepoint(mx, my): # If the player want a hint
            game.use_hint() # Let the game use a hint
            return # Task is over
        if buttons["undo"].collidepoint(mx, my): # If the play want to make his last action undone
            game.undo() # Remove the last action
            return # Task is over
        if buttons["restart"].collidepoint(mx, my): # If the player want to restart the game
            game.restart_same() # Restart the game
            return # task is done
        if buttons["pause"].collidepoint(mx, my): # If the player want to have a break
            game.toggle_pause() # Change the value of the toggle
            return # task is done
        
        if game.paused or game.won: # If the player is not playing anymore
            return # Do nothing
        
        offset_x, offset_y = s.play_grid_offset(game.n) # Load the offsets
        if offset_x + con.CELL_SIZE <= mx < offset_x + (game.n + 1) * con.CELL_SIZE and \
           offset_y + con.CELL_SIZE <= my < offset_y + (game.n + 1) * con.CELL_SIZE: # If a cell got a click
            c = int((mx - offset_x - con.CELL_SIZE) // con.CELL_SIZE) # The column is
            r = int((my - offset_y - con.CELL_SIZE) // con.CELL_SIZE) # The row is
            game.click_cell(r, c, right_click=(event.button == 3)) # Send a left or a right click further
            
def handle_scroll(game, event): # Make scrolling possible
    game.last_wheel_time = pg.time.get_ticks() # Save the time
    last_time = getattr(handle_scroll, "_last_time", game.last_wheel_time) # Finds the last time
    time_diff = max(1, game.last_wheel_time - last_time) # Time between this and last scroll
    handle_scroll._last_time = game.last_wheel_time # Defines old time as this time
    
    raw_speed = event.y / time_diff # The speed in which was scrolled
    scroll_speed = 1 + (abs(raw_speed) * 1000) # The speed the screen need to move
    delta = event.y * scroll_speed # Let the screen scroll
    
    if game.state == "HISTORY": # If scroll in history
        game.history_scroll_y += delta # Scroll
        count = len(game.filtered_history()) # Show right history
        max_scroll = 0 # Not over the top
        min_scroll = -max(0, (count * s.ENTRY_SPACING) - (con.HEIGHT - s.LIST_TOP)) # Not under the bottom
        game.history_scroll_y = max(min_scroll, min(game.history_scroll_y, max_scroll)) # Makes sure the player do not leave the defined area
    
    elif game.state == "HISTORY_DETAIL": # If scroll in history detail
        game.detail_scroll_y += delta # Scroll
        count = len(game.selected_history_data.get("actions", [])) if game.selected_history_data else 0 # Show right history
        max_scroll = 0 # Not over the top
        min_scroll = -max(0, (count * 34) - 460) # Not under the bottom
        game.detail_scroll_y = max(min_scroll, min(game.detail_scroll_y, max_scroll)) # Makes sure the player do not leave the defined area

    
def draw(game, mx, my): # Let the programm draw the views
    if game.state == "MENU": # If in menu
        s.draw_menu(mx, my) # Create Menu
    elif game.state == "SETTINGS": # If in settings
        s.draw_settings(game, mx, my) # Create the settings
    elif game.state == "ABOUT": # If in about
        s.draw_about(mx, my) # Create the about
    elif game.state == "HISTORY": # If in history
        s.draw_history(game, mx, my) # Create the history
    elif game.state == "HISTORY_DETAIL": # If in history detail
        s.draw_history_detail(game, mx ,my) # Create the history detail
    elif game.state == "PLAY": # In in a game
        s.draw_play(game, mx, my) # Creates the game view
        
main() # Starts the programm