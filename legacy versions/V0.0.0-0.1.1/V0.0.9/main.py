### Mati (Mathematics and tactic intelligence) ###
### V0.0.9 Beta V1.0.9 ###
### Author: Janosch Klawatsch, 12.07.2026 ###
### main file V0.0.3 ###

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
import sys    # System Commands like sys.exit() to close the tab.
import pygame as pg # Something like the engine on which the game runs.

### Own ###
import config as con     # To have the constants
import screens as s      # To draw the screens
import widgets as w      # To use the widgets
from game import Game    # To start a game
from audio import Sounds # To play sounds

### -Functions- ###
### Main ###
def main(): # The main function
    pg.init() # Pygame need to be initialized
    screen = pg.display.set_mode((con.WIDTH, con.HEIGHT)) # Define the size of the window
    pg.display.set_caption("Mati") # The shown name of the window
    
    # Because fonts need pygame, they are defined in this file and not in config. But maybe they could be in widgets.
    title_font = pg.font.SysFont("arial", 48, bold=True) # For the biggest texts
    font = pg.font.SysFont("arial", 28, bold=True) # For the normal texts and buttons
    small_font = pg.font.SysFont("arial", 22) # For small  texts and most buttons
    w.init(screen, title_font, font, small_font)
    
    sounds = Sounds() # Load all sounds
    game = Game(sounds) # start the game with those sounds
    clock = pg.time.Clock() # Start the Clock
    
    while True: # Until the programm gots quit
        screen.fill(con.BG_COLOR) # Draw the background
        mx, my = pg.mouse.get_pos() # Get the mouse position
        
        for event in pg.event.get(): # Everything happend got saved
            if event.type == pg.QUIT: # If the user want to quit
                pg.quit() # End the game engine
                sys.exit() # Close the game
            
            elif event.type == pg.KEYDOWN: # If the player pressed a key
                if event.key == pg.K_p and game.state == "PLAY": # If the player pressed p in the game
                    game.toggle_pause() # Make the game paused or continued
                elif event.key == pg.K_z and (event.mod & pg.KMOD_CTRL) and game.state == "PLAY": # If the player pressed CTRL and z and is playing
                    game.undo() # Make the last move undone
                    
            elif event.type == pg.MOUSEBUTTONDOWN: # If the player clicked the mousebutton
                handle_click(game, event, mx, my) # Check what for a click
            
            elif event.type == pg.MOUSEWHEEL and game.state == "HISTORY": # If the player tries to scroll in history view
                handle_history_scroll(game, event) # Handle the scroll
                
        game.tick_timer() # Update the timer
        draw(game, mx, my) # Redraw the whole game
        
        pg.display.flip() # Make it visible
        clock.tick(60) # Set the framerate to 60 frames per second (fps)
    
def handle_click(game, event, mx, my): # Let the programm work with a click
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
        elif buttons["about"].collidepoint(mx, my): # If the player clicked on about
            game.state = "ABOUT" # go to about
            
    elif state == "ABOUT": # If the player is in the about
        if s.BTN_BACK.collidepoint(mx, my): # If the player clicked back
            game.state = "SETTINGS" # Return to settings
            
    elif state == "HISTORY": # If the player is in the history menu
        if s.BTN_BACK.collidepoint(mx, my): # If the player clicked on back
            game.state = "MENU" # return to the menu
            return # Task is over
        if my <= 80: # If the cursor is to high
            return # Do nothing
        for i, f in enumerate(game.history_files): # For each file in history files
            delete_rect = s.history_delete_rect(i, game.history_scroll_y) # Get positions for delete buttons
            entry_rect = s.history_entry_rect(i, game.history_scroll_y) # Get the positions of the buttons
            if delete_rect.collidepoint(mx, my): # If the player want to delete something
                game.delete_history(f) # Delete the selected file
                return # Task is over
            if entry_rect.collidepoint(mx, my): # If the player clicked on a file
                game.open_history_detail(f) # Open the file
                return # Task is done
    
    elif state == "HISTORY_DETAIL": # If in a history file
        if s.BTN_BACK.collidepoint(mx, my): # If clicked on back
            game.state = "HISTORY" # return to history
            
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
            c = (mx - offset_x - con.CELL_SIZE) // con.CELL_SIZE # The column is
            r = (my - offset_y - con.CELL_SIZE) // con.CELL_SIZE # The row is
            game.click_cell(r, c, right_click=(event.button == 3)) # Send a left or a right click further
            
def handle_history_scroll(game, event): # Make scrolling possible
    current_time = pg.time.get_ticks() # Gets the time
    last_time = getattr(handle_history_scroll, "_last_time", current_time) # Finds the last time
    time_diff = max(1, current_time - last_time) # Time between this and last scroll
    handle_history_scroll._last_time = current_time # Defines old time as this time
    
    raw_speed = event.y / time_diff # The speed in which was scrolled
    scroll_speed = 1 + (abs(raw_speed) * 1000) # The speed the screen need to move
    game.history_scroll_y += event.y * scroll_speed # Let the screen scroll
    
    max_scroll = 0 # Not over the top
    min_scroll = -max(0, (len(game.history_files) * 60) - (con.HEIGHT - 150)) # Not under the bottom
    game.history_scroll_y = max(min_scroll, min(game.history_scroll_y, max_scroll)) # Makes sure the player do not leave the defined area
    
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