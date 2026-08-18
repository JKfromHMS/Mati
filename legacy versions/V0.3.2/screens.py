### Mati (Mathematics and tactic intelligence) ###
### V0.3.2 Beta V1.0.16 ###
### Author: Janosch Klawatsch, 29/30.07.2026 ###
### screens file V0.3.5 ###

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
import pygame as pg # Something like the engine on which the game runs.

### Own ###
import config as con
import replay as re
import widgets as w

### -Functions- ###
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

def detail_real_index_for(i): # list position to real action index
    return -1 if i == 0 else i - 1

### Keyboard navigation
def focus_order(game): # Gives the orderd, navigable elements in the current screen
    order = [] # Start empty
    state = game.state # Get the current screen
    if state == "MENU": # Main menu
        order = list(menu_buttons().items()) # Every menu button
    elif state == "SETTINGS": # Setting screen
        order = list(settings_buttons(game).items()) # Every setting button
    elif state == "ABOUT": # About screen
        order = [("back", con.BTN_BACK)] # Just the back button
    elif state == "HISTORY": # History screen
        order.append(("back", con.BTN_BACK)) # Back button first
        if game.history_entries: # Must have entries 
            order += list(history_filter_buttons(game).items()) # Add the filter buttons
            for i, _ in enumerate(game.filtered_history()): # Every visible entry
                order.append((f"entry_{i}", history_entry_rect(i, game.history_scroll_y))) # The entries itself
                order.append((f"delete_{i}", history_delete_rect(i, game.history_scroll_y))) # The delete for every entry
    elif state == "HISTORY_DETAIL": # Detail view of a match
        order.append(("back", con.BTN_BACK)) # Back button
        order.append(("detail_reset", detail_reset_button())) # Reset button
        if game.selected_history_data: # If a match is loaded
            display_actions = detail_display_actions(game.selected_history_data) # The actions
            for i in range(len(display_actions)): # For every action
                order.append((detail_key_for(i), detail_action_rect(i, game.detail_scroll_y))) # Navigate threw the actions
    elif state == "DELETE_HISTORY": # Delete confirmation
        box_w, box_h = 440, 220 # The size
        box_x = (con.WIDTH - box_w) // 2 # Same x
        box_y = (con.HEIGHT - box_h) // 2 # Same y
        order.append(("yes", pg.Rect(box_x + 60, box_y + 150, 130, 42))) # delete button
        order.append(("no", pg.Rect(box_x + 250, box_y + 150, 130, 42))) # cancel button
    elif state == "RESUME_CHOICE": # Paused game detected
        buttons = resume_choice_buttons() # Load the buttons
        order = [("resume", buttons["resume"]), ("new", buttons["new"]), ("cancel", buttons["cancel"])] # Defined order
    elif state == "HANNAH" and getattr(game, "hannah_open_index", None) is None: # If in hannah menu overview
        order.append(("back", con.BTN_BACK)) # Back button
        for i, lvl in enumerate(getattr(game, "hannah_levels", [])): # For every level
            if lvl is None: # Empty signes ignore
                continue # skip
            order.append((f"tile_{i}", hannah_tile_rect(i, game.hannah_scroll_x))) # Add the grids
    elif state == "PLAY" and getattr(game, "paused", False): # Pause menu buttons
        buttons = play_buttons()
        order = [("menu", buttons["menu"]), ("break", buttons["break"]), ("new", buttons["new"])]
    elif state == "PLAY" and getattr(game, "won", False): # Win screen buttons
        buttons = play_buttons()
        order = [("back", buttons["back"]), ("restart", buttons["restart"])]
    return order # Give them back
    
def _nearest_in_direction(order, current_key, direction): # Finds the closest element to navigate to
    lookup = dict(order) # get order / load order
    current_rect = lookup.get(current_key) # Get the key or the focused rect
    if current_rect is None: # If empty spot
        return None # nothing to do
    cx, cy = current_rect.center # Get center cords
    best = None # Save the nearst element
    best_score = None # The distance to it
    for key, rect in order: # Go threw every key and rect of order
        if key == current_key: # If it find itself
            continue # Just make nothing
        x, y = rect.center # Get the center of the button
        dx, dy = x - cx, y - cy # Get the distances
        if direction == "down" and dy <= 2: continue # If the same high nothing to do
        if direction == "up" and dy >= -2: continue # If the same high nothing to do
        if direction == "right" and dx <= 2: continue # If the same high nothing to do
        if direction == "left" and dx >= 2: continue # If the same high nothing to do
        if direction in ("down", "up"): # If check up down
            score = (abs(dy), abs(dx)) # Set score
        else: 
            score = (abs(dx), abs(dy)) # Set score
        if best_score is None or score < best_score: # If nearer button found
            best_score = score # Set new best score
            best = key # Set new best element
    return best # Give best element back

def _move_focus_history(game, order, direction):
    lookup = dict(order) # key -> rect
    key = game.focus_key # where we are
    entries = game.filtered_history()
    header_keys = [k for k, _ in order if not (k.startswith("entry_") or k.startswith("delete_"))] # not a row just in one
    
    if key.startswith("entry_") or key.startswith("delete_"): # inside the list
        idx = int(key.split("_", 1)[1]) # number of row
        column = "delete" if key.startswith("delete_") else "entry" # the right column
        if direction in ("left", "right"): # Toggle between entry and delete
            other = "delete" if column == "entry" else "entry" # the right other mode
            other_key = f"{other}_{idx}" # the key
            if other_key in lookup: # other key exists
                game.focus_key = other_key # switch to it
                ensure_focus_visible(game, order) # keep it visible
            return # task is done
        if direction == "down": # move down a row
            if idx + 1 < len(entries): # exisisting row below
                game.focus_key = f"{column}_{idx + 1}"
                ensure_focus_visible(game, order) # keep it visible
            return # task is done
        if direction == "up": # move a row up
            if idx - 1 >= 0: # row above
                game.focus_key = f"{column}_{idx - 1}" # move there
                ensure_focus_visible(game, order) # keep it visible
            else: # to the header buttons
                nxt = _nearest_in_direction([(k, lookup[k]) for k in header_keys] + [(key, lookup[key])], key, "up") # nearest header button
                if nxt: # if found
                    game.focus_key = nxt # jump there
                    ensure_focus_visible(game, order) # keep it visible
            return # task is done
    else: # Means in the header buttons
        if direction == "down" and entries: # enter the list from top
            game.focus_key = "entry_0" # first row
            ensure_focus_visible(game, order) # keep it visible
            return # task is done
        nxt = _nearest_in_direction([(k, lookup[k]) for k in header_keys], key, direction) # move to the nearest
        if nxt: # if found
            game.focus_key = nxt # jump there
            ensure_focus_visible(game, order) # keep it visible
                         
def _move_focus_hannah(game, order, direction): # navigation
    lookup = dict(order) # key -> rect
    key = game.focus_key # where we are
    tile_keys = [k for k, _ in order if k.startswith("tile_")] # Get ordered tiles
    
    if direction not in ("left", "right"): # just right left movement
        return # task is over
    if key.startswith("tile_"): # current on a tile
        idx = tile_keys.index(key) if key in tile_keys else 0 # the position
        if direction == "right": # move on tile further
            if idx + 1 < len(tile_keys): # if there is a next tile
                game.focus_key = tile_keys[idx + 1] # move there
                ensure_focus_visible(game, order) # keep it visible
        else: # must be left
            if idx - 1 >= 0: # if there is a prev tile
                game.focus_key = tile_keys[idx - 1] # move there
                ensure_focus_visible(game, order) # keep it visible
            elif "back" in lookup: # Got to back button
                game.focus_key = "back" # jump there
                ensure_focus_visible(game, order) # keep it visible
    else: # on back button
        if direction == "right" and tile_keys: # enter the strip
            game.focus_key = tile_keys[0] # jump there
            ensure_focus_visible(game, order) # keep it visible
                          
def move_focus(game, direction): # Hoe to move the focus
    order = focus_order(game) # Load the order
    if not order: # If the load failed
        return # nothing to do
    keys = [k for k, _ in order] # Get every key
    if game.focus_key not in keys: 
        game.focus_key = keys[0]
        return
    if game.state == "HISTORY": # to fix a bug
        _move_focus_history(game, order, direction) # handle it there
        return # task is done
    if game.state == "HANNAH" and getattr(game, "hannah_open_index", None) is None: # to fix a bug
        _move_focus_hannah(game, order, direction) # handle it there
        return # task is done
    nxt = _nearest_in_direction(order, game.focus_key, direction)
    if nxt is not None:
        game.focus_key = nxt
        ensure_focus_visible(game, order)
        
def _effective_focus_key(game, mx, my):
    if not game.alt_control:
        return None
    order = focus_order(game)
    if not order:
        return None
    keys = [k for k, _ in order]
    if game.focus_key not in keys:
        game.focus_key = keys[0]
    now = pg.time.get_ticks()
    
    hovered_key = None # mouse hover element
    for key, rect in order:
        if rect.collidepoint(mx, my):
            hovered_key = key
            break
    if hovered_key != getattr(game, "mouse_hover_key", None): # mouse moved
        game.mouse_hover_key = hovered_key # remember the new one
        game.mouse_hover_start = now # get the time
        
    if getattr(game, "focus_lock_until", 0) > now:
        return game.focus_key
    idle_ms = now - getattr(game, "last_key_time", 0)
    hover_ms = now - getattr(game, "mouse_hover_start", 0) # how long no input
    if idle_ms >= con.FOCUS_IDLE_MS and hovered_key and hover_ms >= con.FOCUS_IDLE_MS:
        return hovered_key # if mouse rest for long enough on a button without any other moves
    
    return game.focus_key


def ensure_focus_visible(game, order): # Makes sure in lists the focused is visible
    lookup = dict(order)
    rect = lookup.get(game.focus_key)
    if rect is None:
        return
    key = game.focus_key
    if game.state == "HISTORY" and (key.startswith("entry_") or key.startswith("delete_")): # In the history list
        margin = con.ENTRY_SPACING // 2
        if rect.top < con.LIST_TOP - 10: # Above the visible area
            game.history_scroll_y += (con.LIST_TOP - 10 - rect.top) + margin # Scroll down to show it
            game.history_scroll_y = min(game.history_scroll_y, 0) # never scroll over the top
            game.history_scroll_last = pg.time.get_ticks() # remeber the scrollbar time
        elif rect.bottom > con.HEIGHT: # Below the visible area
            game.history_scroll_y -= (rect.bottom - con.HEIGHT) + margin # Scroll up
            game.history_scroll_last = pg.time.get_ticks() # remember the time
    elif game.state == "HISTORY_DETAIL" and key.startswith("action_"): # In the action list
        if rect.top < 100: # Above the visible area
            game.detail_scroll_y += (100 - rect.top) # Scroll down
            game.detail_scroll_last = pg.time.get_ticks() # remember the time
        elif rect.bottom > 560: # Below the visible area
            game.detail_scroll_y -= (rect.bottom - 560) # Scroll up
            game.detail_scroll_last = pg.time.get_ticks() # remember the time
    elif game.state == "HANNAH" and key.startswith("tile_"):
        if rect.left < 20:
            game.hannah_scroll_x += (20 - rect.left)
            game.hannah_scroll_last = pg.time.get_ticks() # remember the time
        elif rect.right > con.WIDTH - 20:
            game.hannah_scroll_x -= (rect.right - (con.WIDTH - 20))
            game.hannah_scroll_last = pg.time.get_ticks() # remember the time

### Menu ###
def menu_buttons(): # Creates the buttons for the main menu
    buttons = {} # A place to save the buttons
    y = 175 # Defines the y start
    for n in con.DIFFICULTIES: # Every difficultie gets its own button
        buttons[f"start_{n}"] = pg.Rect(con.WIDTH // 2 - 110, y, 220, 44) # Buttons are defined
        y += 54 # change the position that they do not get over each other
    buttons["settings"] = pg.Rect(con.WIDTH // 2 - 110, y + 15, 220, 44)       # Setting button
    buttons["history"] = pg.Rect(con.WIDTH // 2 - 110, y + 69, 220, 44)   # History button
    buttons["quit"] = pg.Rect(con.WIDTH // 2 - 110, y + 123, 220, 44) # quit button
    return buttons # Give all buttons back

def draw_menu(game, mx, my): # Draw the defined menu
    w.draw_title("Mati", con.TEXT_COLOR, con.WIDTH // 2, 90) # Let the title been drawn
    w.draw_small("Mathematic and Tactic Intelligence", con.TEXT_COLOR, con.WIDTH // 2, 135) # Let the name definition been drawn
    buttons = menu_buttons() # Load the needed buttons
    fk = _effective_focus_key(game, mx, my) # Get the current keyboard cursor position
    for n in con.DIFFICULTIES: # For every difficult a own button
        key = f"start_{n}" # Key of this button
        rect = buttons[key] # Get it to a drawable button
        w.draw_button(rect, con.DIFFICULTY_NAMES[n], rect.collidepoint(mx, my), focused=(key == fk)) # let the buttons be drawn
    w.draw_button(buttons["settings"], "Settings", buttons["settings"].collidepoint(mx, my), focused=(fk == "settings")) # let the setting button draw
    w.draw_button(buttons["history"], "History", buttons["history"].collidepoint(mx, my), focused=(fk == "history")) # Let the history button draw
    w.draw_button(buttons["quit"], "Quit", buttons["quit"].collidepoint(mx, my), focused=(fk == "quit")) # let the quit button draw
    
### Settings ###
def settings_buttons(game): # Create the buttons for the settings
    rows = ["toggle_history", "toggle_timer"] # Rows that are always shown
    if game.timer_enabled: # ms only makes sense if timer is on
        rows.append("toggle_ms") # Add that row
    rows += ["toggle_sound", "toggle_fullscreen", "toggle_alt_control", "toggle_live_clock"] # The others rows
    if game.live_clock_enabled: # ms only when time on
        rows.append("toggle_live_clock_ms") # Add the ms button
    rows.append("toggle_ultra_timer") # the ultra ingame timer
    if game.ultra_timer_enabled:
        rows.append("toggle_ultra_timer_ms") # ms for ultra timer
    rows.append("toggle_ultra_timer_clock") # add the clock toggle
    buttons = {"back": con.BTN_BACK} # Start with back button
    y = 100 # y cord of first row
    for key in rows: # Stack every row under the last
        buttons[key] = pg.Rect(con.WIDTH // 2 -110, y, 220, 34) # Place the button
        y += 36 # Move to make them not be over each other
    buttons["about"] = pg.Rect(con.WIDTH // 2 - 110, y + 18, 220, 34) # About is a little lower
    return buttons # Give the buttons back
    
def draw_settings(game, mx ,my): # Draw the defined settings
    w.draw_title("Settings", con.TEXT_COLOR, con.WIDTH // 2, 90) # Draw Setting declaration
    buttons = settings_buttons(game) # Load the buttons
    fk = _effective_focus_key(game, mx, my) # Get the current keyboard focus
    w.draw_button(buttons["back"], "Menu", buttons["back"].collidepoint(mx, my), focused=(fk == "back")) # Let back button draw
    
    hist_text = "Save Played: Yes" if game.save_history else "Save Played: No" # Define save text
    w.draw_button(buttons["toggle_history"], hist_text, buttons["toggle_history"].collidepoint(mx, my), focused=(fk == "toggle_history")) # let save toggle draw
    
    time_text = "Show Timer: Yes" if game.timer_enabled else "Show Timer: No" # Define show time text
    w.draw_button(buttons["toggle_timer"], time_text, buttons["toggle_timer"].collidepoint(mx, my), focused=(fk == "toggle_timer")) # let show timer toggle draw
    
    if game.timer_enabled:
        ms_text = "Miliseconds: Yes" if game.timer_ms else "Miliseconds: No" # Define show miliseconds text
        w.draw_button(buttons["toggle_ms"], ms_text, buttons["toggle_ms"].collidepoint(mx, my), focused=(fk == "toggle_ms")) # Let the show miliseconds toggle draw
    
    sound_text = "Sound: Yes" if game.sounds.enabled else "Sound: No" # Defines the text should shonw
    w.draw_button(buttons["toggle_sound"], sound_text, buttons["toggle_sound"].collidepoint(mx, my), focused=(fk == "toggle_sound")) # Let the sound toggle draw
    
    fs_text = "Fullscreen: Yes" if game.is_fullscreen else "Fullscreen: No" # Defines the fullscreen button text
    w.draw_button(buttons["toggle_fullscreen"], fs_text, buttons["toggle_fullscreen"].collidepoint(mx, my), focused=(fk == "toggle_fullscreen")) # Let the fullscreen togggle draw
    
    alt_text = "Keyboard-Navigation: Yes" if game.alt_control else "Keyboard-Navigation: No" # Defines Keyboard navigation text
    w.draw_button(buttons["toggle_alt_control"], alt_text, buttons["toggle_alt_control"].collidepoint(mx, my), focused=(fk == "toggle_alt_control")) # Let the keyboard input activate be drawn
    
    clock_text = "Live Clock: Yes" if game.live_clock_enabled else "Live Clock: No" # Defines the live clock button text
    w.draw_button(buttons["toggle_live_clock"], clock_text, buttons["toggle_live_clock"].collidepoint(mx, my), focused=(fk == "toggle_live_clock")) # draw the toggle
    
    if game.live_clock_enabled: # If clock is active
        clock_ms_text = "Live Clock ms: Yes" if game.live_clock_ms else "Live Clock ms: No" # Define the text
        w.draw_button(buttons["toggle_live_clock_ms"], clock_ms_text, buttons["toggle_live_clock_ms"].collidepoint(mx, my), focused=(fk == "toggle_live_clock_ms")) # draw the toggle
        
    ultra_time_text = "Ultra Timer: Yes" if game.ultra_timer_enabled else "Ultra Timer: No" # Defines the ultra timer text
    w.draw_button(buttons["toggle_ultra_timer"], ultra_time_text, buttons["toggle_ultra_timer"].collidepoint(mx, my), focused=(fk == "toggle_ultra_timer")) # draw the button
    
    if game.ultra_timer_enabled: # if ultra timer is active
        ultra_ms_text = "Ultra Timer ms: Yes" if game.ultra_timer_ms else "Ultra Timer ms: No" # Define the text
        w.draw_button(buttons["toggle_ultra_timer_ms"], ultra_ms_text, buttons["toggle_ultra_timer_ms"].collidepoint(mx, my), focused=(fk == "toggle_ultra_timer_ms")) # draw the button
        
    ultra_clock_text = "Ultra Timer Clock: Yes" if game.ultra_timer_show_clock else "Ultra Timer Clock: No" # Defines the text
    w.draw_button(buttons["toggle_ultra_timer_clock"], ultra_clock_text, buttons["toggle_ultra_timer_clock"].collidepoint(mx, my), focused=(fk == "toggle_ultra_timer_clock")) # draw the toggle
    
    w.draw_button(buttons["about"], "About", buttons["about"].collidepoint(mx, my), focused=(fk == "about")) # let the about button draw
    w.draw_tiny("Press F11 to switch or ESC to end fullscreen", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, buttons["about"].bottom + 14)
    
### About ###
def draw_about(game, mx, my):
    w.draw_title("About Mati", con.TEXT_COLOR, con.WIDTH // 2, 90) # Draw the title
    fk = _effective_focus_key(game, mx, my) # Get the keyboard focus
    w.draw_button(con.BTN_BACK, "Back", con.BTN_BACK.collidepoint(mx, my), focused=(fk == "back")) # Let back button draw
    w.draw_text("Created by:", con.TEXT_COLOR, con.WIDTH // 2, 240) # Draw the created by text
    w.draw_text("Janosch Klawatsch", con.TEXT_COLOR, con.WIDTH // 2, 280) # Draw Janosch Klawatsch
    
### History ###
def history_filter_buttons(game): # Defines the filter buttons
    buttons = {} # Empty button list
    labels_values = [("All", None)] + [(f"{n}x{n}", n) for n in con.DIFFICULTIES] # How the buttons should be named
    btn_w, gap = 90, 8 # Defines the width off the buttons and the unused space between them
    total_w = len(labels_values) * btn_w + (len(labels_values) - 1) * gap # The width the button can get
    start_x = con.WIDTH // 2 - total_w // 2 # Defines were the buttons should start
    for i, (label, val) in enumerate(labels_values): # Goes threw every label
        key = "size_all" if val is None else f"size_{val}" # Get the button name
        buttons[key] = pg.Rect(start_x + i * (btn_w + gap), 95, btn_w, 36) # Inteprate the daata as buttons

    has_ultra_entries = any(entry.get("ultra") for entry in game.history_entries)
    if has_ultra_entries:
        buttons["top10"] = pg.Rect(con.WIDTH // 2 - 230, 140, 220, 36) # Defines the top 10 button
        buttons["ultra"] = pg.Rect(con.WIDTH // 2 + 10, 140, 220, 36) # Defines the ultra button
    else:
        buttons["top10"] = pg.Rect(con.WIDTH // 2 - 110, 140, 220, 36) # Centered top 10 button when no ultra entries exist
    return buttons # Give the buttons back 

def history_entry_rect(i, scroll_y): # Defines the place for the history
    y = con.LIST_TOP + i * con.ENTRY_SPACING + scroll_y # That they do not cover each other
    return pg.Rect(con.ENTRY_X, y, con.ENTRY_WIDTH - 50, con.ENTRY_HEIGHT) # The build information for the entry

def history_delete_rect(i, scroll_y): # Defines the place for a entry that got deleted
    y = con.LIST_TOP + i * con.ENTRY_SPACING + scroll_y # That they do not cover each other
    return pg.Rect(con.ENTRY_X + con.ENTRY_WIDTH - 44, y, 40, con.ENTRY_HEIGHT) # The build information for the entry

def _format_duration(play_time_ms): # Changes the time from ms to mins and secs
    ms = play_time_ms % 1000 # get the right number of ms
    total_seconds = play_time_ms // 1000 # ms in s
    minutes = total_seconds // 60 # Seconds to minutes
    seconds = total_seconds % 60  # Cut of seconds that are shown as minutes
    return f"{minutes}:{seconds:02}:{ms:03}min" # Give the transfered time back

def draw_delete_confirm(game, mx, my): # Drawn the menu to delete a file
    overlay = pg.Surface((con.WIDTH, con.HEIGHT)) # Creates a surface
    overlay.set_alpha(180) # Set the level of transperancy
    overlay.fill((215, 215, 215)) # Fill it with a little different bg color
    screen = w.get_screen() # Load the screen
    screen.blit(overlay, (0, 0)) # Lay the surface over the screen
    
    box_w, box_h = 440, 220 # Size off the box
    box_x = (con.WIDTH - box_w) // 2 # x center
    box_y = (con.HEIGHT - box_h) // 2 # y center
    
    pg.draw.rect(screen, con.BG_COLOR, (box_x, box_y, box_w, box_h), border_radius=12) # Draw the outer box border
    pg.draw.rect(screen, con.TEXT_COLOR, (box_x, box_y, box_w, box_h), width=2, border_radius=12) # Draws the inner box
    
    w.draw_text("Delete Match?", con.TEXT_COLOR, con.WIDTH // 2, box_y + 40, center = True) # Text 1
    w.draw_small("Do you really want to permanently delete", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 85, center=True) # Text 2
    w.draw_small("this game from your history?", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 110, center=True) # Text 3
    
    btn_yes = pg.Rect(box_x + 60, box_y + 150, 130, 42) # Define the yes button
    btn_no = pg.Rect(box_x + 250, box_y + 150, 130, 42) # Define the no button
    
    fk = _effective_focus_key(game, mx, my) # Get the current keyboard
    w.draw_button(btn_yes, "Delete", btn_yes.collidepoint(mx, my), focused=(fk == "yes")) # Draw yes button
    w.draw_button(btn_no, "Cancel", btn_no.collidepoint(mx, my), focused=(fk == "no")) # Draw the no button
    
    return {"yes": btn_yes, "no": btn_no} # Give the click back

def draw_history(game, mx, my): # Draw the history
    w.draw_title("History", con.TEXT_COLOR, con.WIDTH // 2, 50) # Draw the title
    fk = _effective_focus_key(game, mx, my) # Get the keyboard focus
    w.draw_button(con.BTN_BACK, "Menu", con.BTN_BACK.collidepoint(mx, my), focused=(fk == "back")) # Draw the back button
    
    if not game.history_entries: # If no saved games found
        w.draw_text("No game saved until now, but you can change that.", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 200) # Say it
        return # End here
    
    filter_buttons = history_filter_buttons(game) # Load the buttons
    size_options = [("size_all", None)] + [(f"size_{n}", n) for n in con.DIFFICULTIES] # Load the size options
    for key, val in size_options: # For each option
        rect = filter_buttons[key] # extract one option
        label = "All" if val is None else f"{val}x{val}" # Defines the label
        active = (game.history_filter_size == val) # Checks if a filter is active
        w.draw_toggle_button(rect, label, rect.collidepoint(mx, my), active, focused=(fk == key)) # Let the buttons draw
    top10_rect = filter_buttons["top10"] # Defines top ten button
    w.draw_toggle_button(top10_rect, "Top 10", top10_rect.collidepoint(mx, my), game.history_filter_top10, focused=(fk == "top10")) # Draw top 10 button
    if "ultra" in filter_buttons:
        ultra_rect = filter_buttons["ultra"] # Defines ultra button
        w.draw_toggle_button(ultra_rect, "Ultra", ultra_rect.collidepoint(mx, my), game.history_filter_ultra, focused=(fk == "ultra")) # Draw the ultra button
    
    entries = game.filtered_history() # Define entrie
    if not entries: # If no entry
        w.draw_text("No game matchs your filters!", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 230) # Define the empty game message
        return # Do nothing more
    
    screen = w.get_screen() # Get screen information
    clip_area = pg.Rect(0, con.LIST_TOP - 10, con.WIDTH, con.HEIGHT - con.LIST_TOP) # Define the area for the history files
    screen.set_clip(clip_area) # Connects the screen with the area
    for i, entry in enumerate(entries): # Goes threw the files
        entry_rect = history_entry_rect(i, game.history_scroll_y)   # Gets the place
        delete_rect = history_delete_rect(i, game.history_scroll_y) # Gets the cords for the delete
        if entry_rect.bottom < con.LIST_TOP - 10 or entry_rect.top > con.HEIGHT: # Check position
            continue # Everything is fine
        is_hovered = entry_rect.collidepoint(mx, my) # Check the hover
        w.draw_panel_row(entry_rect, is_hovered, focused=(fk == f"entry_{i}")) # Define the row for the select buttons
        w.draw_small(entry["label"], con.WHITE, entry_rect.x + 14, entry_rect.y + 11, center=False) # Declare the button text
        if entry["ultra"] == True: w.draw_small("ULTRA", con.SHINE, entry_rect.x + 250, entry_rect.centery) # Show those who are ultramode
        w.draw_small(f'{entry["size"]}x{entry["size"]}', con.WHITE, entry_rect.x + 360, entry_rect.centery) # Declare the button text
        w.draw_small(_format_duration(entry["play_time"]), con.WHITE, entry_rect.x + 480, entry_rect.centery) # Declare the button text
        w.draw_button(delete_rect, "x", delete_rect.collidepoint(mx, my), focused=(fk == f"delete_{i}")) # let the delete buttons be drawm
    screen.set_clip(None) # End the are only write to get control of the fullwindow again
    
    track = pg.Rect(con.ENTRY_X + con.ENTRY_WIDTH + 6, con.LIST_TOP - 10, con.SCROLLBAR_WIDTH, con.HEIGHT - (con.LIST_TOP - 10)) # scrollbar position
    visible_length = con.HEIGHT - (con.LIST_TOP - 10)
    w.draw_scrollbar(track, len(entries) * con.ENTRY_SPACING, visible_length, -game.history_scroll_y, mx, my, game.history_scroll_last) # draw the scrollbar

### History-Detail ###
def detail_reset_button(): # End view switch
    return pg.Rect(540, 60, 250, 30) # Give the button position and size

def detail_action_rect(i, scroll_y): # Action view switch
    y = 100 + i * 34 + scroll_y # Defines the height
    return pg.Rect(540, y, 250, 30) # Give the button pos ans size

def _draw_full_grid(grid, row_sums, col_sums, user_sel, user_dimmed, n, offset_x, offset_y, highlight_cell=None, highlight_color=None, ultra=False): # Information of the grid
    screen = w.get_screen() # Load the screen information
    for c in range(n): # For every column
        cx = offset_x + (c + 1) * con.CELL_SIZE + con.CELL_SIZE // 2 # x cord of the text
        cy = offset_y + con.CELL_SIZE // 2 # y cord of the text
        w.draw_text(str(col_sums[c]), con.TARGET_COLOR, cx, cy) # Let the text draw
    for r in range(n): # For every row
        cx = offset_x + con.CELL_SIZE // 2 # x cord of the text
        cy = offset_y + (r + 1) * con.CELL_SIZE + con.CELL_SIZE // 2  # y cord of the text
        w.draw_text(str(row_sums[r]), con.TARGET_COLOR, cx, cy) # Let the text draw
    
    row_fulfilled = [sum(grid[r][c] for c in range(n) if user_sel[r][c]) == row_sums[r] for r in range(n)] # Get the correct rows
    col_fulfilled = [sum(grid[r][c] for r in range(n) if user_sel[r][c]) == col_sums[c] for c in range(n)] # Get the correct columns
    
    for r in range(n): # For every row
        for c in range(n): # For every column
            rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE) # Pos and size of every cell
            is_dimmed = user_dimmed[r][c] or ((row_fulfilled[r] or col_fulfilled[c]) and not user_sel[r][c]) # Load dim situation
            if user_sel[r][c]: # If a cell is selected
                pg.draw.rect(screen, con.SELECTED_COLOR, rect) # Draw the selected cells
            pg.draw.rect(screen, con.GRID_COLOR, rect, 2) # Draw the lines between the cells
            color = con.DIMMED_TEXT_COLOR if is_dimmed else con.TEXT_COLOR # Defines the color should used
            w.draw_text(str(grid[r][c]), color, rect.centerx, rect.centery) # Let the numbers be drawn
            if highlight_cell == (r, c): # Checks if this cell is highlighted
                pg.draw.rect(screen, highlight_color or con.GOLD, rect, 4) # Draw the highlight
                
    w.draw_outer_border(offset_x, offset_y, n, con.CELL_SIZE, ultra=ultra) # Draw the border
    w.draw_fulfilled_indicators(grid, user_sel, row_sums, col_sums, n, offset_x, offset_y, con.CELL_SIZE) # Check and mark right sums

def draw_history_detail(game, mx, my): # the draw the detailed history view
    data = game.selected_history_data # Get the data from the game
    if not data: # Empty file
        game.state = "HISTORY" # Fallback
        return # End it
    
    fk = _effective_focus_key(game, mx, my) # Get the keyboard focus
    w.draw_button(con.BTN_BACK, "Back", con.BTN_BACK.collidepoint(mx, my), focused=(fk == "back")) # The Back button
    
    n = (len(data["grid"])) # Load n
    offset_x, offset_y = 30, 75 # Defines the offset cords
    actions = data.get("actions", []) # Load the actions
    
    user_sel, user_dimmed, hints_used, play_time, last_action = re.reconstruct_state(data, game.detail_selected_index) # Find the screen after a action
    
    highlight_cell = None # No highlighted cell yet
    highlight_color = None # The color will be defined later
    if last_action is not None and last_action.get("r"): # If there are actions
        highlight_cell = (last_action["r"], last_action["c"]) # Get the row/col from the last cell
        highlight_color = con.ACTION_HIGHLIGHT_COLOR.get(last_action.get("type"), con.GOLD) # Find out which color it should have
        
    if not data.get("ultra"): # If a old file
        data["ultra"] = False # Say it was no ultra
        
    _draw_full_grid(data["grid"], data["row_sums"], data["col_sums"], user_sel, user_dimmed, n, offset_x, offset_y, highlight_cell, highlight_color, data["ultra"])
    
    footer_y = offset_y + (n + 1) * con.CELL_SIZE + 14 # Bottom
    minutes = play_time // 60000 # Get the minutes
    seconds = play_time // 1000 # Get the seconds
    ms = play_time % 1000 # Get the miliseconds
    n = len(data["grid"])
    if n != 7:
        if minutes < 1: w.draw_tiny(f"Time: {seconds:02}:{ms:03}s", con.TEXT_COLOR, offset_x, footer_y, center=False) # Time under the grid
        if minutes >= 1: w.draw_tiny(f"Time: {minutes}:{(seconds%60):02}:{ms:03}min", con.TEXT_COLOR, offset_x, footer_y, center=False)
        w.draw_tiny(f"Hints used: {hints_used}", con.TEXT_COLOR, offset_x, footer_y + 20, center=False) # Hints used under the time
        if last_action and last_action.get("r"): # If a real last action is defined
            label = con.ACTION_LABELS.get(last_action.get("type", "Left"), last_action.get("type", "?")) # Get the right action name
            w.draw_tiny(f"Action: Row: {last_action['r'] + 1}, Column: {last_action['c'] + 1} - {label}", con.TEXT_COLOR, offset_x, footer_y + 40, center=False) # Describe action underneath
        elif last_action:
            w.draw_tiny("Action: Start", con.TEXT_COLOR, offset_x, footer_y + 40, center=False) # describe start
        else: 
            w.draw_tiny("End of game", con.DIMMED_TEXT_COLOR, offset_x, footer_y + 40, center=False) # Or that it is the last
    else:
        footer_y = offset_y + (n + 1) * con.CELL_SIZE + 14 # Bottom
        if minutes < 1: w.draw_tiny(f"Time: {seconds:02}:{ms:03}s", con.TEXT_COLOR, offset_x, footer_y - 10, center=False) # Time under the grid
        if minutes >= 1: w.draw_tiny(f"Time: {minutes}:{(seconds%60):02}:{ms:03}min", con.TEXT_COLOR, offset_x, footer_y - 10, center=False)
        w.draw_tiny(f"Hints used: {hints_used}", con.TEXT_COLOR, offset_x + 400, footer_y - 10, center=False) # Hints used under the time
        if last_action and last_action.get("r"): # If a last real action is defined
            label = con.ACTION_LABELS.get(last_action.get("type", "Left"), last_action.get("type", "?")) # Get the right action name
            w.draw_tiny(f"Action: Row: {last_action['r'] + 1}, Column: {last_action['c'] + 1} - {label}", con.TEXT_COLOR, offset_x, footer_y + 8, center=False) # Describe action underneath
        elif last_action:
            w.draw_tiny("Action: Start", con.TEXT_COLOR, offset_x, footer_y + 8, center=False)
        else: 
            w.draw_tiny("End of game", con.DIMMED_TEXT_COLOR, offset_x, footer_y + 8, center=False) # Or that it is the last
        
    reset_rect = detail_reset_button() # Load the buttons
    w.draw_button(reset_rect, "Show End", reset_rect.collidepoint(mx, my), focused=(fk == "detail_reset")) # Button for end view
    
    screen = w.get_screen() # Get the screen informations
    display_actions = detail_display_actions(data) # get the actions to show
    detail_count = len(display_actions) # len
    track = pg.Rect(540 + 250 - con.SCROLLBAR_WIDTH - 2, 100, con.SCROLLBAR_WIDTH, 460)
    w.draw_scrollbar(track, detail_count * 34, 460, -game.detail_scroll_y, mx, my, game.detail_scroll_last) # Draw it BEHIND the entries first
    
        
    clip_area = pg.Rect(540, 100, 250, 460) # Define the area for the actions
    screen.set_clip(clip_area) # Connect it to the screen
    for i, act in enumerate(display_actions):
        rect = detail_action_rect(i, game.detail_scroll_y) # Get the buttons
        if rect.bottom < 100 or rect.top > 560: # If in the right spot
            continue # Everything is fine
        is_hovered = rect.collidepoint(mx, my) # check hover state
        real_index = detail_real_index_for(i) # get the real index
        is_selected = (game.detail_selected_index == real_index) # check selected state
        key = detail_key_for(i) # focus key
        w.draw_panel_row(rect, is_hovered, highlighted=is_selected, focused=(fk == f"action_{i}")) # Draw the action buttons
        text_color = con.TEXT_COLOR if is_selected else con.WHITE
        if act.get("synthetic"): # the start
            line = "00:000s   - Start" # start entry name
        else:
            second = (act["time"] // 1000) % 60   # Get the secs
            ms_ = act["time"] % 1000       # Get the milisecs
            minutes = act["time"] // 60000 # Get the minutes
            check = data["play_time"] # Get the time from the full game
            label = con.ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?")) # Define the right label
            if check < 60000: line = f'{second:02}:{ms_:03}s   - R{act["r"] + 1}/C{act["c"] + 1} - {label}' # Defines the complete line
            if check >= 60000: line = f'{minutes}:{second:02}:{ms_:03}min  - R{act["r"] + 1}/C{act["c"] + 1} - {label}'
        w.draw_tiny(line, text_color, rect.x + 8, rect.y + 7, center=False) # Draw the line on the button
    screen.set_clip(None) # End clip mode
    if not actions: # If there is no real move at all, hint that only Start is there
        w.draw_small("No action found", con.DIMMED_TEXT_COLOR, 665, 145) # Say it, below the Start row
           
### Play ###
def play_buttons(): # The button in the game 
    return {
        "back": con.BTN_BACK,
        "hint": pg.Rect(con.WIDTH - 147, 50, 130, 34),
        "undo": pg.Rect(con.WIDTH - 147, 90, 130, 34),
        "restart": pg.Rect(con.WIDTH - 147, 130, 130, 34),
        "pause": pg.Rect(con.WIDTH - 147, 170, 130, 34),
        "menu": pg.Rect(con.WIDTH - 650, con.HEIGHT // 2 + 75, 130, 50),
        "break": pg.Rect(con.WIDTH - 450, con.HEIGHT // 2 + 75, 130, 50),
        "new": pg.Rect(con.WIDTH - 250, con.HEIGHT // 2 + 75, 130, 50)
    } # Give them back
    
def draw_play(game, mx, my): # draw the play view
    buttons = play_buttons() # Load the buttons
    fk = _effective_focus_key(game, mx, my)
    w.draw_button(buttons["back"], "Menu", buttons["back"].collidepoint(mx, my), focused=(fk == "back")) # Let the back button be drawn
    
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
                    
                if game.alt_control and not game.won and not game.paused and (r, c) == (game.cursor_r, game.cursor_c): # Check if this is the keyboard cell
                    pg.draw.rect(screen, con.FOCUS_COLOR, rect, 3) # Highlight it
                    
        w.draw_outer_border(offset_x, offset_y, n, con.CELL_SIZE) # Draw the border
        w.draw_fulfilled_indicators(game.grid, game.user_sel, game.row_sums, game.col_sums, n, offset_x, offset_y, con.CELL_SIZE) # Let the correct sums be circled
        
        w.draw_button(buttons["hint"], f"Hint ({game.hints_left})", buttons["hint"].collidepoint(mx, my), enabled=game.hints_left > 0 and not game.won and not game.paused) # If available sends hint find alogrithem threw the grid
        w.draw_button(buttons["undo"], "Undo", buttons["undo"].collidepoint(mx, my), enabled=bool(game.current_game_actions) and not game.won and not game.paused) # If available gives command to make the last move undone
        w.draw_button(buttons["restart"], "New", buttons["restart"].collidepoint(mx, my), focused=(fk == "restart")) # Show the restart button
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
            overlay.set_alpha(255) # Set alpha attitude
            overlay.fill(con.PAUSE) # Fill it with background color
            screen.blit(overlay, (0, 0)) # Place it over the whole screen
            w.draw_title("Paused", con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2 - 45) # Shows that in pause menu
            w.draw_button(buttons["menu"], "Menu", buttons["menu"].collidepoint(mx, my), focused=(fk == "menu")) # Let the back button be drawn
            w.draw_button(buttons["break"], "Continue", buttons["break"].collidepoint(mx, my), focused=(fk == "break")) # The return to game button
            w.draw_button(buttons["new"], "New", buttons["new"].collidepoint(mx, my), focused=(fk == "new")) # Show the restart button
            w.draw_small("Press P or the Continue Button to retrun", con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2) # Gives a hint of how to return
            
def resume_choice_buttons(): # Creates the buttons for the decide of continue
    return {
        "resume": pg.Rect(con.WIDTH // 2 - 240, 300, 210, 50),
        "new": pg.Rect(con.WIDTH // 2 + 30, 300, 210, 50),
        "cancel": con.BTN_BACK
    } # Give the buttons back

def draw_resume_choice(game, mx, my): # Draw the resume/new decision
    n = game.pending_new_n # The size
    ultra = game.pending_new_ultra # The mode
    mode_label = "Ultra" if ultra else "Normal" # Readable mode names
    fk = _effective_focus_key(game, mx, my) # Get the current keyboard
    
    w.draw_title("Unfinished game found", con.TEXT_COLOR, con.WIDTH // 2, 120) # Title
    w.draw_text(f"{n}x{n} - {mode_label}", con.TEXT_COLOR, con.WIDTH // 2, 175) # Declare which round
    w.draw_small("Would you like to resume or to start a new match", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 220) # Question
    
    buttons = resume_choice_buttons() # Load the buttons
    w.draw_button(buttons["resume"], "Resume", buttons["resume"].collidepoint(mx, my), focused=(fk == "resume")) # Continue button
    w.draw_button(buttons["new"], "New Game", buttons["new"].collidepoint(mx, my), focused=(fk == "new")) # New game button
    w.draw_button(buttons["cancel"], "Back", buttons["cancel"].collidepoint(mx, my), focused=(fk == "cancel")) # Cancel back to menu

### Easter eggs views ###
def hannah_content_width():
    total = 40
    for letter_char in con.HANNAH_MESSAGE:
        if letter_char is None:
            total += con.HANNAH_SPACE_GAP
        else:
            total += con.HANNAH_TITE_SIZE + con.HANNAH_TITE_GAP
    return total

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

def hannah_buttons(): # Defines the buttons for the easter egg
    return {"back": con.BTN_BACK}

def hannah_play_buttons():
    return {
        "back": con.BTN_BACK,
        "undo": pg.Rect(con.WIDTH - 150, 20, 130, 34)
    }

def draw_hannah(game, mx, my): # Creates first easter egg view
    fk = _effective_focus_key(game, mx, my)
    if game.hannah_open_index is None:
        w.draw_title("Jay Loves", con.TEXT_COLOR, con.WIDTH // 2, 70)
        w.draw_button(con.BTN_BACK, "Menu", con.BTN_BACK.collidepoint(mx, my), focused=(fk == "back"))
        screen = w.get_screen()
        clip_area = pg.Rect(0, con.HANNAH_STRIP_Y - 90, con.WIDTH, 180)
        screen.set_clip(clip_area)
        for i, lvl in enumerate(game.hannah_levels):
            if lvl is None:
                continue
            rect = hannah_tile_rect(i, game.hannah_scroll_x)
            if rect.right < 0 or rect.left > con.WIDTH:
                continue
            solved = i < len(game.hannah_solved) and game.hannah_solved[i]
            is_hovered = rect.collidepoint(mx, my)
            is_focused = (fk == f"tile_{i}")
            if solved:
                pg.draw.rect(screen, con.HOVER_LINE_COLOR, rect, border_radius=6)
                pg.draw.rect(screen, con.GRID_COLOR, rect, 2, border_radius=6)
                cell = rect.width // con.HANNAH_SIZE
                for r in range(con.HANNAH_SIZE):
                    for c in range(con.HANNAH_SIZE):
                        if lvl["user_sel"][r][c]:
                            mini_rect = pg.Rect(rect.x + c * cell, rect.y + r * cell, cell, cell)
                            pg.draw.rect(screen, con.GREEN, mini_rect)
            else:
                color = con.HOVER_LINE_COLOR if is_hovered else con.WHITE
                pg.draw.rect(screen, color, rect, border_radius=6)
                pg.draw.rect(screen, con.GRID_COLOR, rect, 2, border_radius=6)
            if is_focused:
                focus_rect = rect.inflate(8, 8)
                pg.draw.rect(screen, con.FOCUS_COLOR, focus_rect, 3, border_radius=8)
        screen.set_clip(None)
        
        track = pg.Rect(40, con.HEIGHT - con.SCROLLBAR_WIDTH - 6, con.WIDTH - 80, con.SCROLLBAR_WIDTH)
        w.draw_scrollbar(track, hannah_content_width(), con.WIDTH - 80, -game.hannah_scroll_x, mx, my, game.hannah_scroll_last, vertical=False) # draw the scrollbar
    else:
        lvl = game.hannah_levels[game.hannah_open_index]
        n = con.HANNAH_SIZE
        offset_x, offset_y = play_grid_offset(n)
        buttons = hannah_play_buttons()
        w.draw_button(buttons["back"], "Back", buttons["back"].collidepoint(mx, my))
        
        row_fulfilled = [sum(lvl["grid"][r][c] for c in range(n) if lvl["user_sel"][r][c]) == lvl["row_sums"][r] for r in range(n)]
        col_fulfilled = [sum(lvl["grid"][r][c] for r in range(n) if lvl["user_sel"][r][c]) == lvl["col_sums"][c] for c in range(n)]
        
        hover_r = hover_c = None
        if offset_x + con.CELL_SIZE <= mx < offset_x + (n + 1) * con.CELL_SIZE and offset_y + con.CELL_SIZE <= my < offset_y + (n + 1) * con.CELL_SIZE:
            hover_c = (mx - offset_x - con.CELL_SIZE) // con.CELL_SIZE
            hover_r = (my - offset_y - con.CELL_SIZE) // con.CELL_SIZE
        w.draw_hover_cross(offset_x, offset_y, n, con.CELL_SIZE, hover_r, hover_c)
        
        for c in range(n):
            cx = offset_x + (c + 1) * con.CELL_SIZE + con.CELL_SIZE // 2
            cy = offset_y + con.CELL_SIZE // 2
            w.draw_text(str(lvl["col_sums"][c]), con.TARGET_COLOR, cx, cy)
        for r in range(n):
            cx = offset_x + con.CELL_SIZE // 2
            cy = offset_y + (r + 1) * con.CELL_SIZE + con.CELL_SIZE // 2
            w.draw_text(str(lvl["row_sums"][r]), con.TARGET_COLOR, cx, cy)
            
        screen = w.get_screen()
        for r in range(n):
            for c in range(n):
                rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE)
                is_dimmed = lvl["user_dimmed"][r][c] or ((row_fulfilled[r] or col_fulfilled[c]) and not lvl["user_sel"][r][c])
                if lvl["user_sel"][r][c]:
                    pg.draw.rect(screen, con.SELECTED_COLOR, rect)
                elif rect.collidepoint(mx, my) and not is_dimmed:
                    pg.draw.rect(screen, con.HOVER_COLOR, rect)
                if game.alt_control and (r, c) == (game.cursor_r, game.cursor_c):
                    pg.draw.rect(screen, con.FOCUS_COLOR, rect, 3)
                pg.draw.rect(screen, con.GRID_COLOR, rect, 2)
                color = con.DIMMED_TEXT_COLOR if is_dimmed else con.TEXT_COLOR
                w.draw_text(str(lvl["grid"][r][c]), color, rect.centerx, rect.centery)
        
        w.draw_outer_border(offset_x, offset_y, n, con.CELL_SIZE)    
        w.draw_fulfilled_indicators(lvl["grid"], lvl["user_sel"], lvl["row_sums"], lvl["col_sums"], n, offset_x, offset_y, con.CELL_SIZE)
        w.draw_button(buttons["undo"], "Undo", buttons["undo"].collidepoint(mx, my), enabled=bool(lvl["actions"]))
            