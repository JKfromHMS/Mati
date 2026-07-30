### Mati (Mathematics and tactic intelligence) ###
### V0.3.2 Beta V1.0.16 ###
### Author: Janosch Klawatsch, 29/30.07.2026 ###
### main file V0.3.6 ###

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
### External ###
import sys    # System Commands like sys.exit() to close the tab.
import pygame as pg # Something like the engine on which the game runs.

### Own ###
import config as con     # To have the constants
import screens as s      # To draw the screens
import widgets as w      # To use the widgets
from game import Game    # To start a game
from audio import Sounds # To play sounds
import terminal as t     # To use the terminal

### -Functions- ###
### Screen-Size ###
def toggle_fullscreen(fullscreen, windowed_size): # Switches between fulllscreen and not
    if fullscreen: # If the fullscreen is active
        real_screen = pg.display.set_mode(windowed_size, pg.RESIZABLE) # To now want screen version
        return False, real_screen # Give the want screen size back
    info = pg.display.Info() # Get the size information about the screen
    real_screen = pg.display.set_mode((info.current_w, info.current_h), pg.NOFRAME) # Say we want Fullscreen
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
    pending_click = None # To check if the click was not wanted
    active_terminal = None # Check if in the terminal
    prev_state = game.state # To notice when the screen changes
    
    while True: # Until the programm gots quit
        if game.state != prev_state: # If the screen changed
            game.focus_index = 0 # Start focus on the new screen
            game.focus_key = None
            game.focus_lock_until = pg.time.get_ticks() + 200
            prev_state = game.state # Remember new screen
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
                game.stash_current_game() # Save the game even if it is not finished
                if active_terminal is not None and active_terminal.ultra_game is not None: # If the player is playing ultra
                    active_terminal.ultra_game.stash_current_game(o_time=pg.time.get_ticks() - active_terminal.timer) # Save also the ultra mode
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
                elif (event.key == pg.K_n) and (event.mod & (pg.KMOD_CTRL | pg.KMOD_META)) and game.state == "PLAY": # Start a new round with Ctrl/Cmd+N
                    game.restart_same() # Same as the New button
                elif (event.key == pg.K_m) and (event.mod & (pg.KMOD_CTRL | pg.KMOD_META)) and game.state in ("MENU", "SETTINGS", "ABOUT", "HISTORY", "HISTORY_DETAIL", "DELETE_HISTORY", "RESUME_CHOICE", "HANNAH", "PLAY", "TERMINAL"):
                    if game.state == "PLAY":
                        game.stash_current_game() # Save the unfinished match before leaving
                    elif game.state == "TERMINAL" and active_terminal: # If in terminal
                        active_terminal.close() # Say the terminal it should close
                    game.state = "MENU" # Return to the menu from other screens
                elif event.key == pg.K_z and (event.mod & pg.KMOD_CTRL) and game.state == "PLAY": # If the player pressed CTRL and z and is playing
                    game.undo() # Make the last move undone
                elif game.alt_control and game.state == "PLAY" and game.paused: # Pause menu keyboard support
                    if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                        game.last_key_time = pg.time.get_ticks()
                        direction = {pg.K_UP: "up", pg.K_DOWN: "down", pg.K_LEFT: "left", pg.K_RIGHT: "right"}[event.key]
                        s.move_focus(game, direction)
                    elif event.key in (pg.K_SPACE, pg.K_RETURN):
                        game.last_key_time = pg.time.get_ticks()
                        key = s._effective_focus_key(game, mx, my)
                        lookup = dict(s.focus_order(game))
                        if key is not None and key in lookup:
                            rect = lookup[key]
                            handle_click(game, pg.time.get_ticks(), rect.centerx, rect.centery, 1)
                        elif game.focus_key == "break":
                            game.toggle_pause()
                elif game.alt_control and game.state == "PLAY" and game.won: # Win screen keyboard support
                    if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                        game.last_key_time = pg.time.get_ticks()
                        direction = {pg.K_UP: "up", pg.K_DOWN: "down", pg.K_LEFT: "left", pg.K_RIGHT: "right"}[event.key]
                        s.move_focus(game, direction)
                    elif event.key in (pg.K_SPACE, pg.K_RETURN):
                        game.last_key_time = pg.time.get_ticks()
                        key = s._effective_focus_key(game, mx, my)
                        lookup = dict(s.focus_order(game))
                        if key is not None and key in lookup:
                            rect = lookup[key]
                            handle_click(game, pg.time.get_ticks(), rect.centerx, rect.centery, 1)
                elif game.alt_control and game.state == "PLAY" and not game.paused and not game.won: # If the player is playing normal
                    if event.key in(pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT): game.move_cursor(event.key) # Handle the move
                    elif event.key in (pg.K_l, pg.K_SPACE, pg.K_RETURN): game.click_cell(game.cursor_r, game.cursor_c) # Make a left click
                    elif event.key == pg.K_r: game.click_cell(game.cursor_r, game.cursor_c, right_click=True) # Make a right click
                    elif event.key == pg.K_u: game.undo() # Undo the last action
                    elif event.key == pg.K_h: game.use_hint() # Use an hint
                elif game.alt_control and game.state == "HANNAH" and game.hannah_open_index is not None:
                    if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                        game.move_cursor(event.key)
                    elif event.key in (pg.K_l, pg.K_SPACE, pg.K_RETURN):
                        game.hannah_click_cell(game.cursor_r, game.cursor_c)
                    elif event.key == pg.K_r:
                        game.hannah_click_cell(game.cursor_r, game.cursor_c, right_click=True)
                    elif event.key == pg.K_u:
                        game.hannah_undo()
                elif game.alt_control and game.state == "PLAY" and event.key == pg.K_n: # If the player is in the game mode
                    game.restart_same() # Restart the game
                elif game.alt_control and event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT) and game.state in ("MENU", "SETTINGS", "ABOUT", "HISTORY", "HISTORY_DETAIL", "DELETE_HISTORY", "RESUME_CHOICE", "HANNAH"): # Keyboard menu navigation
                    game.last_key_time = pg.time.get_ticks() # Get the time of this click
                    direction = {pg.K_UP: "up", pg.K_DOWN: "down", pg.K_LEFT: "left", pg.K_RIGHT: "right"}[event.key] # Which way to move
                    s.move_focus(game, direction) # Move the focus
                    #order = s.focus_order(game) # Get the navigable elements of this screen
                    #if order: # If there is anything to navigate
                    #    delta = -1 if event.key in (pg.K_UP, pg.K_LEFT) else 1 # Direction to move
                    #    game.focus_index = (game.focus_index + delta) % len(order) # Move the focus, wrapping around
                    #    s.ensure_focus_visible(game, order) # Keep the focused row scrolled into view
                elif game.alt_control and event.key in (pg.K_SPACE, pg.K_RETURN) and game.state in ("MENU", "SETTINGS", "ABOUT", "HISTORY", "HISTORY_DETAIL", "DELETE_HISTORY", "RESUME_CHOICE", "HANNAH"): # Keyboard click replacement
                    game.last_key_time = pg.time.get_ticks() # Get the time
                    key = s._effective_focus_key(game, mx, my) # Get the real focused key
                    lookup = dict(s.focus_order(game)) # Key -> rect
                    if key is not None and key in lookup: # If the is something
                        rect = lookup[key] # get what
                        handle_click(game, pg.time.get_ticks(), rect.centerx, rect.centery, 1) # Simulate a left click on it                    
                    #order = s.focus_order(game) # Get the navigable elements of this screen
                    #if order: # If there is a focused element
                    #    idx = game.focus_index % len(order) # Keep the index inside bounds
                    #    _, rect = order[idx] # The focused rect
                elif (not game.alt_control) and game.state == "HANNAH" and game.hannah_open_index is None and event.key in (pg.K_LEFT, pg.K_RIGHT): # Scrolling without keyboard navigation
                    step = 90 # Distance per key press
                    game.hannah_scroll_x = step if event.key == pg.K_LEFT else -step # Find out if in pos or neg direction
                    total_width = s.hannah_content_width() # Full content width
                    min_scroll = -max(0, total_width - (con.WIDTH - 80)) # Do not scroll behind the end
                    game.hannah_scroll_x = max(min_scroll, min(0, game.hannah_scroll_x)) # Make sure its not in front of
                elif game.state == "TERMINAL": # If in the terminal
                    active_terminal.handle_key(event) # Let the terminal handle the key
                    if active_terminal.should_close: # If the player want to close or switch
                        target_state = active_terminal.next_state or "MENU" # If the terminal get leaved with a excact state or MENU, get it
                        if target_state == "HISTORY": # If the player want to go to history
                            game.open_history() # Simply open history
                        elif target_state == "HANNAH":
                            game.init_hannah()
                        elif target_state == "PLAY" and active_terminal.next_game is not None: # If the player want to play a game
                            n, ultra = active_terminal.next_game # Load the game elements
                            game.new_game(n, ultra=ultra, force_new=True) # Force to start a new game
                        else: # If the player want to go somewhere else
                            game.state = target_state # Simply copy the state to let it work
                        active_terminal = None # Terminal is off
                elif event.key == pg.K_t and (event.mod & pg.KMOD_CTRL) and game.state == "MENU": # If the player pressed CTRL and t and is in menu
                    game.state = "TERMINAL" # Say the game, that it is in terminal
                    active_terminal = t.Terminal(sounds) # Start the terminal
                    
            elif event.type == pg.MOUSEBUTTONDOWN and mouse_inside: # If the player clicked the mousebutton
                pending_click = {
                    "time": pg.time.get_ticks(),
                    "mx": mx,
                    "my": my,
                    "button": event.button,
                    "valid": True,
                } # The necessary information
            
            elif event.type == pg.MOUSEWHEEL:
                if game.state in ("HISTORY", "HISTORY_DETAIL"): # If the player tries to scroll in history or detail view
                    handle_scroll(game, event) # Handle the scroll
                elif game.state == "TERMINAL" and active_terminal: # Scroll threw terminal
                    active_terminal.scroll(int(event.y * 3)) # A few lines up and down
                if pending_click is not None and pg.time.get_ticks() - pending_click["time"] < con.WHEEL_CLICK_GUARD_MS_min: # Compare
                    pending_click["valid"] = False # Make the click does not count
                
        repeat_states = ("HISTORY", "HISTORY_DETAIL", "HANNAH") # states with scrollbar
        in_hannah_strip = game.state == "HANNAH" and getattr(game, "hannah_open_index", None) is None # not in open puzzle
        if game.alt_control and (game.state in ("HISTORY", "HISTORY_DETAIL") or in_hannah_strip): # If repeat should be active
            keys_down = pg.key.get_pressed() # Key the is held
            direction = None # Nothing held by default
            if keys_down[pg.K_DOWN]: direction = "down"
            elif keys_down[pg.K_UP]: direction = "up"
            elif keys_down[pg.K_LEFT]: direction = "left"
            elif keys_down[pg.K_RIGHT]: direction = "right"
            now_ticks = pg.time.get_ticks() # Get the time
            if direction is None: # No pressed arrow-key
                game._repeat_direction = None # no direction of the key
            elif direction != game._repeat_direction: # A new direction
                game._repeat_direction = direction # remeber the action
                game._repeat_next_time = now_ticks + con.KEY_REPEAT_DELAY_MS
            elif now_ticks >= game._repeat_next_time: # Time for an repeat
                game.last_key_time = now_ticks
                s.move_focus(game, direction)
                game._repeat_next_time = now_ticks + con.KEY_REPEAT_INTERVAL_MS
        else:
            game._repeat_direction = None # reset the tracker
        
        if game.request_fullscreen_toggle: # If the user want to change the size
            fullscreen, real_screen = toggle_fullscreen(fullscreen, windowed_size) # Change fullscreen and window
            game.is_fullscreen = fullscreen # Set the fullscreen state
            game.request_fullscreen_toggle = False # We wont stuck in an endless repetition
                
        if pending_click is not None: # If click had happend
            click_time = pending_click["time"] # Get time
            if pending_click.get("valid", True) and pg.time.get_ticks() - click_time >= con.WHEEL_CLICK_GUARD_MS_min: # If the click is real
                handle_click(game, click_time, pending_click["mx"], pending_click["my"], pending_click["button"]) # Say it was a click
                pending_click = None # No click to check
            elif not pending_click.get("valid", True): # Not valid click
                pending_click = None # Nothing to do
                
        if game.state != "TERMINAL" and active_terminal:
            active_terminal = None

        game.tick_timer() # Update the timer
        if active_terminal is not None: # If the player is in the terminal
            active_terminal.draw() # Let the terminal be drawn
        else:
            draw(game, mx, my) # Redraw the whole game
        
        real_screen.fill(con.BLACK) # The Background-Color, maybe should be something else
        scaled_surface = pg.transform.smoothscale(virtual_screen, (scaled_w, scaled_h)) # Defines the virtual surface
        real_screen.blit(scaled_surface, (offset_x, offset_y)) # Place the virtual screen in the real
        pg.display.flip() # Make it visible
        clock.tick(60) # Set the framerate to 60 frames per second (fps)
    
def handle_click(game, click_time, mx, my, button): # Let the programm work with a click
    if pg.time.get_ticks() - game.last_wheel_time < con.WHEEL_CLICK_GUARD_MS and game.last_wheel_time >= click_time: # Second check
        return # Do nothing
    state = game.state # Gets the state
    
    match state: # py 3.10 method to make if else more efficient
        case "MENU": # If the player is in the menu
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
    
        case "SETTINGS": # If the player is in the settings
            buttons = s.settings_buttons(game) # Load buttons
            if game.timer_enabled:
                if buttons["toggle_ms"].collidepoint(mx, my): # If the player clicked on ms
                    game.timer_ms = not game.timer_ms # toggle between on and off
            if buttons["back"].collidepoint(mx, my): # If the player clicked back
                game.state = "MENU" # Return to menu
            elif buttons["toggle_history"].collidepoint(mx, my): # If the player clicked history save
                game.save_history = not game.save_history # Toggle if save or not
            elif buttons["toggle_timer"].collidepoint(mx, my): # If the player clicked the timer toggle
                game.timer_enabled = not game.timer_enabled # Toggle on and off
                if game.timer_enabled == False: game.timer_ms = False # Turn miliseconds off, if timer is turned of
            elif buttons["toggle_sound"].collidepoint(mx, my): # If the player clicked on the sound
                game.sounds.enabled = not game.sounds.enabled # Toggle this state
            elif buttons["toggle_fullscreen"].collidepoint(mx, my): # If the player clicked on fullscreen
                game.request_fullscreen_toggle = True # activate Fullscreen or deactivate
            elif buttons["toggle_alt_control"].collidepoint(mx, my): # If the Player want to toggle keyboard navigation
                game.alt_control = not game.alt_control # Toggle if keyboard navigation is on/off
                if game.alt_control: # If it just got turned on
                    game.focus_key = "toggle_alt_control" # The first focus is the button itself
                    game.focus_lock_until = pg.time.get_ticks() + 200 # Avoid an immediate mouse-hover jump
            elif buttons["toggle_live_clock"].collidepoint(mx, my): # If the player clicked on the live clock
                game.live_clock_enabled = not game.live_clock_enabled # Toggle on and off
                if not game.live_clock_enabled: game.live_clock_ms = False # Turn ms off too, if the clock is turned off
            elif "toggle_live_clock_ms" in buttons and buttons["toggle_live_clock_ms"].collidepoint(mx, my): # If the player clicked on live clock ms
                game.live_clock_ms = not game.live_clock_ms # Toggle on and off
            elif buttons["toggle_ultra_timer"].collidepoint(mx, my): # If the player clicked on the ultra timer
                game.ultra_timer_enabled = not game.ultra_timer_enabled # Toggle on and off
                if not game.ultra_timer_enabled: # Turn its extras off too, if it is turned off
                    game.ultra_timer_ms = False
                    game.ultra_timer_show_clock = False
            elif "toggle_ultra_timer_ms" in buttons and buttons["toggle_ultra_timer_ms"].collidepoint(mx, my): # If the player clicked on ultra timer ms
                game.ultra_timer_ms = not game.ultra_timer_ms # Toggle on and off
            elif "toggle_ultra_timer_clock" in buttons and buttons["toggle_ultra_timer_clock"].collidepoint(mx, my): # If the player clicked on ultra timer clock
                game.ultra_timer_show_clock = not game.ultra_timer_show_clock # Toggle on and off
            
            game.persist_settings() # Save the new settings
            if buttons["about"].collidepoint(mx, my): # If the player clicked on about
                game.state = "ABOUT" # go to about
            
        case "ABOUT": # If the player is in the about
            if con.BTN_BACK.collidepoint(mx, my): # If the player clicked back
                game.state = "SETTINGS" # Return to settings
            
        case "HISTORY": # If the player is in the history menu
            if con.BTN_BACK.collidepoint(mx, my): # If the player clicked on back
                game.state = "MENU" # return to the menu
                return # Task is over
        
            filter_buttons = s.history_filter_buttons(game) # Load the filter buttons
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
            if "ultra" in filter_buttons and filter_buttons["ultra"].collidepoint(mx, my): # For the ultra filter
                game.toggle_ultra_filter() # make the toggle
                return # task is done
        
            if my <= con.LIST_TOP - 10: # If the cursor is to high
                return # Do nothing
            entries = game.filtered_history()
            for i, entry in enumerate(entries): # For each file in history files
                delete_rect = s.history_delete_rect(i, game.history_scroll_y) # Get positions for delete buttons
                entry_rect = s.history_entry_rect(i, game.history_scroll_y) # Get the positions of the buttons
                if delete_rect.collidepoint(mx, my): # If the player want to delete something
                    game.file_to_delete = entry["filename"] # Get the file to delete
                    state = "DELETE_HISTORY" # Set the right state
                    # game.delete_history(entry["filename"]) # Delete the selected file (simple version)
                    return # Task is over
                if entry_rect.collidepoint(mx, my): # If the player clicked on a file
                    game.open_history_detail(entry["filename"]) # Open the file
                    return # Task is done
            
        case "DELETE_HISTORY": # The delete screen
            buttons = s.draw_delete_confirm(game, mx, my) # Get the buttons
        
            if buttons["yes"].collidepoint(mx, my): # If yes clicked
                game.delete_history(game.file_to_delete) # Let the file be deleted
                game.file_to_delete = None # clear the file save
                game.state = "HISTORY" # Return to History
                return # task is done
            elif buttons["no"].collidepoint(mx, my): # If clicked no
                game.file_to_delete = None # clear the file save
                state = "HISTORY" # Return to History
                return # task is done
    
        case "HISTORY_DETAIL": # If in a history file
            if con.BTN_BACK.collidepoint(mx, my): # If clicked on back
                game.open_history() # Reset the scrol etc
                return # Task is over
            if s.detail_reset_button().collidepoint(mx, my): # End view wanted
                game.reset_detail_view() # Let the game reset to the end view
                return # Task is over
            if game.selected_history_data: # Clicked on a action
                display_actions = s.detail_display_actions(game.selected_history_data) # Load the action
                for i in range(len(display_actions)): # Froe each action
                    rect = s.detail_action_rect(i, game.detail_scroll_y) # Scroll area
                    if rect.bottom < 100 or rect.top > 560: # checking positioning
                        continue # everything is fine
                    if rect.collidepoint(mx, my): # If the player clicked it
                        game.select_detail_action(s.detail_real_index_for(i)) # Show action
                        return # Task is done
                
        case "RESUME_CHOICE": # If the player is asked if he want to continue
            buttons = s.resume_choice_buttons() # Load the buttons
            if buttons["resume"].collidepoint(mx, my): # If the player want to resume
                game.resume_paused(game.pending_new_n, game.pending_new_ultra) # countine the paused match
                return # task is done
            elif buttons["new"].collidepoint(mx, my): # If the player ant create a new
                game.discard_and_start(game.pending_new_n, game.pending_new_ultra) # throw the paused away
                return # task is done
            elif buttons["cancel"].collidepoint(mx, my): # If the player want to cancle
                game.state = "MENU" # Set state back to menu
                return # task is done
                
        case "HANNAH": # If the player is in the first easter egg
            if game.hannah_open_index is None: # The scrollable overview
                buttons = s.hannah_buttons() # Load the buttons
                if buttons["back"].collidepoint(mx, my): # If the player clicked back
                    game.state = "MENU" # Go back to the menu
                    return # task is done
                for i, lvl in enumerate(game.hannah_levels): # Check every tile
                    if lvl is None: # The spaces
                        continue # next slot
                    rect = s.hannah_tile_rect(i, game.hannah_scroll_x) # its position
                    if rect.collidepoint(mx, my): # If the player clicked on the lvl
                        solved = i < len(game.hannah_solved) and game.hannah_solved[i] # Already solved
                        if not solved: # If still solvable
                            game.hannah_open(i) # open it
                        return # task is done
            else: # A single mati puzzle is open
                buttons = s.hannah_play_buttons()
                if con.BTN_BACK.collidepoint(mx, my): # If the player clicked back
                    game.hannah_close() # Close the level
                    return # task is done
                if buttons["undo"].collidepoint(mx, my): # Clicked on undo
                    game.hannah_undo() # Call the right function
                    return # task is done
                n = con.HANNAH_SIZE # Size of the grid 5x5
                offset_x, offset_y = s.play_grid_offset(n)
                for r in range(n): # Every row
                    for c in range(n): # Every column
                        rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE) # One cell
                        if rect.collidepoint(mx, my): # If the player clicked
                            game.hannah_click_cell(r, c, right_click=(button == 3)) # Give cords and type of click
                            return # task is done
            
        case "PLAY": # If the player is playing
            buttons = s.play_buttons() #  load buttons
            if not game.paused:
                if buttons["back"].collidepoint(mx, my): # If the player clicked back
                    game.stash_current_game() # Save the unfinished match
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
            else:
                if buttons["new"].collidepoint(mx, my): # If the player want a new game in pause
                    game.restart_same() # Restart the game
                    return # task is done
                if buttons["menu"].collidepoint(mx, my): # If the player want to go to the menu
                    game.stash_current_game() # Save the game
                    game.state = "MENU" # Say go to menu
                    return # task is done
                if buttons["break"].collidepoint(mx, my): # If the player want continue
                    game.toggle_pause() # Change back to play
                    return # task is done
        
            if game.paused or game.won: # If the player is not playing anymore
                return # Do nothing
        
            offset_x, offset_y = s.play_grid_offset(game.n) # Load the offsets
            if offset_x + con.CELL_SIZE <= mx < offset_x + (game.n + 1) * con.CELL_SIZE and offset_y + con.CELL_SIZE <= my < offset_y + (game.n + 1) * con.CELL_SIZE: # If a cell got a click
                c = int((mx - offset_x - con.CELL_SIZE) // con.CELL_SIZE) # The column is
                r = int((my - offset_y - con.CELL_SIZE) // con.CELL_SIZE) # The row is
                game.click_cell(r, c, right_click=(button == 3)) # Send a left or a right click further
            
def handle_scroll(game, event): # Make scrolling possible
    game.last_wheel_time = pg.time.get_ticks() # Save the time
    last_time = getattr(handle_scroll, "_last_time", game.last_wheel_time) # Finds the last time
    time_diff = max(1, game.last_wheel_time - last_time) # Time between this and last scroll
    handle_scroll._last_time = game.last_wheel_time # Defines old time as this time
    
    raw_speed = event.y / time_diff # The speed in which was scrolled
    scroll_speed = 1 + (abs(raw_speed) * 1000) # The speed the screen need to move
    delta = event.y * scroll_speed # Let the screen scroll
    
    match game.state: # py 3.10 method to make if else more efficient
        case "HISTORY": # If scroll in history
            game.history_scroll_y += delta # Scroll
            count = len(game.filtered_history()) # Show right history
            max_scroll = 0 # Not over the top
            min_scroll = -max(0, (count * con.ENTRY_SPACING) - (con.HEIGHT - con.LIST_TOP)) # Not under the bottom
            game.history_scroll_y = max(min_scroll, min(game.history_scroll_y, max_scroll)) # Makes sure the player do not leave the defined area
            game.history_scroll_last = pg.time.get_ticks() # Remember last scroll time
    
        case "HISTORY_DETAIL": # If scroll in history detail
            game.detail_scroll_y += delta # Scroll
            count = len(s.detail_display_actions(game.selected_history_data)) if game.selected_history_data else 0 # Show right history
            max_scroll = 0 # Not over the top
            min_scroll = -max(0, (count * 34) - 460) # Not under the bottom
            game.detail_scroll_y = max(min_scroll, min(game.detail_scroll_y, max_scroll)) # Makes sure the player do not leave the defined area
            game.detail_scroll_last = pg.time.get_ticks() # Get the last scroll time

        case "HANNAH": # In scrollable view
            if game.hannah_open_index: return # Check for scrollbar view
            
            game.hannah_scroll_x += delta # scroll
            total_width = s.hannah_content_width() # Load the width
            min_scroll = -max(0, total_width - (con.WIDTH - 80)) # Do not scrolll to further
            game.hannah_scroll_x = max(min_scroll, min(0, game.hannah_scroll_x)) # Not to much back
            game.hannah_scroll_last = pg.time.get_ticks() # Last time scrolled
    
def draw(game, mx, my): # Let the programm draw the views
    match game.state: # py 3.10 method to make if else more efficient
        case "MENU": # If in menu
            s.draw_menu(game, mx, my) # Create Menu
            
        case "SETTINGS": # If in settings
            s.draw_settings(game, mx, my) # Create the settings
            
        case "ABOUT": # If in about
            s.draw_about(game, mx, my) # Create the about
            
        case "RESUME_CHOICE": # If deciding about continuing the match or starting a new
            s.draw_resume_choice(game, mx, my) # Creates the decision view
            
        case "HISTORY": # If in history
            s.draw_history(game, mx, my) # Create the history
        
        case "HISTORY_DETAIL": # If in history detail
            s.draw_history_detail(game, mx ,my) # Create the history detail
            
        case "PLAY": # In a game
            s.draw_play(game, mx, my) # Creates the game view
            
        case "DELETE_HISTORY": # If in delete history screen
            s.draw_delete_confirm(game, mx, my) # Creates the delete screen
        
        case "HANNAH": # If the player is in the first easter egg
            s.draw_hannah(game, mx, my) # Create the easter egg view
        
    if game.state not in ("ABOUT", "HANNAH"): 
        w.draw_live_clock(game) # show the live clock if wanted
        
main() # Starts the programm