### Mati (Mathematics and tactic intelligence) ###
### V0.3.1 Beta V1.0.15 ###
### Author: Janosch Klawatsch, 27.07.2026 ###
### game file V0.3.4 ###

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
import config as con # To have the constants
from level import check_win, find_hint, generate_level, generate_level_letter # That levels can be created and checked
from persistence import delete_match, list_history_meta, load_match, save_match # For the save and history parts
from persistence import load_settings_and_stats, save_settings_and_stats, record_stat # For settings and statistics and paused games

### -Classes- ###
### Game ###
class Game: # Create a class
    ### Classic "GAME" Functions ###
    def __init__(self, sounds): # Every class need a init with the start parameters
        self.sounds = sounds # Load the sounds
        self.state = "MENU" # A state system for the screens and reaction handling
        self.n = 5          # Classic game hint, it all started with 5x5 so instead of a 0 because you user ever select something the 5
        
        # Data about the game
        self.grid = []          # The numbers of the grid
        self.row_sums = []      # The sums of the rows
        self.col_sums = []      # The sums of the columns
        self.solution = []      # One solution of the game to enable hints
        self.user_sel = []      # Saves what the player select
        self.user_dimmed = []   # Saves what the player mark
        self.row_fulfilled = [] # Saves if a row is correct
        self.col_fulfilled = [] # Saves if a column is correct
        
        self.won = False          # Saves if the player has won
        self.paused = False       # Saves if the game is running
        self.start_time = 0       # Calculate in game time helper
        self.pause_started_at = 0 # Trackes the time the game got paused
        self.total_paused_ms = 0  # Tracked the total time in pause
        self.play_time = 0        # Trackes the total time in game
        
        # Data in the settings
        self.settings, self.stats, self.paused_games, self.hannah_solved = load_settings_and_stats() # Load the settings, statistics and paused games
        self.timer_enabled = self.settings["timer_enabled"] # Trackes if timer is shown
        self.timer_ms = self.settings["timer_ms"] # Trackes if ms are shown
        self.save_history = self.settings["save_history"] # Trackes if history should exists
        self.alt_control = self.settings["alt_control"] # Trackes if keyboard navigation is enabled
        self.sounds.enabled = self.settings["sound_enabled"] # Trackes if sounds enabled
        if "alt_control" not in self.settings:
            self.alt_control = True
        self.request_fullscreen_toggle = False # Should change the fullscreen state
        self.is_fullscreen = False # Save if the game in fullscreen
                
        # Hints & Undo
        self.hints_left = con.HINTS_PER_GAME # Sets the number of hints of a round
        self.last_hint_cell = None           # Saves which cells was hints
        self.hint_flash_timer = 0            # Trackes hint time
        self.current_game_actions = []       # Trackes every game action
        self.current_ultra = False           # Trackes if current match is ultra
        
        # Keyboard navigation
        self.cursor_r = 0     # Row of the keyboard cursor
        self.cursor_c = 0     # Col of the keyboard cursor
        self.focus_index = 0  # Index of the focused button in menu screens
        self.focus_key = None # Key of the current keyboard focused element
        self.focus_lock_until = 0 # Prevents immediate focus jumps after a screen change
        self.last_key_time = pg.time.get_ticks() # Saves last time, pressed key of the keyboard
        self.pending_new_n = None      # Size waiting for a decision
        self.pending_new_ultra = False # Mode waiting for a decision
        
        # History
        self.history_entries = []           # Remembers all played games
        self.history_scroll_y = 0           # Trackes how far is scrolled threw this files
        self.history_filter_size = None     # Saves if a size filter is active
        self.history_filter_top10 = None    # Saves if just the top 10 should be shown
        self.history_filter_ultra = None    # Saves if ultra filter should be on
        self.selected_history_data = None   # Saves which data are selected
        self.selected_history_name = None   # Save the name of the selected data package
        self.detail_selected_index = None   # Also the index number off the data
        self.detail_scroll_y = 0            # Trackes how far is scrolled threw the moves of a game
        self.file_to_delete = None          # Saves the file the player want to delete
        
        # Trackpad Click Save
        self.last_wheel_time = - 10 ** 9      # Time of last scroll
        
    def new_game(self, n, ultra=False, force_new=False): # Creates a new game
        key = self._pause_key(n, ultra) # The slot this mode/size would use
        if not force_new and key in self.paused_games: # If a paused match already existis in this size mode combo
            self.pending_new_n = n # Remember what size
            self.pending_new_ultra = ultra # Remember the mode
            self.state = "RESUME_CHOICE" # Let the player decide between old or new game
            return # task is done
        self._start_fresh(n, ultra) # No paused match or forced to start a new

    def _pause_key(self, n, ultra): # Build the storage key for a paused game
        return f"{n}_{'ultra' if ultra else 'normal'}" # One key per size and mode
        
    def _start_fresh(self, n, ultra=False): # Actually generating the new level
        self.n = n # The size of the grid
        self.current_ultra = ultra # Remember which mode this round is
        self.grid, self.row_sums, self.col_sums, self.solution = generate_level(n) # Fill the information with them of a new game
        self.user_sel = [[False] * n for _ in range(n)] # Self size like grid, but empty to save selected
        self.user_dimmed = [[False] * n for _ in range(n)] # Self size like grid, but empty to save the markes
        self.row_fulfilled = [False] * n # No row is correct
        self.col_fulfilled = [False] * n # No column is correct
        self.won = False # The player had not won yet
        self.paused = False # The game isn't paused
        self.total_paused_ms = 0 # Never paused now
        self.start_time = pg.time.get_ticks() # Start time is now
        self.play_time = 0 # But not played yet
        self.hints_left = con.HINTS_PER_GAME # reset the number of hints available
        self.last_hint_cell = None # No hint was given yet
        self.current_game_actions = [] # No actions yet
        self.cursor_c = 0 # Reset keyboard cursor
        self.cursor_r = 0 # Reset keyboard cursor
        self.state = "PLAY" # Now we need the Play-Screen
        
    def restart_same(self): # Let the game start again under same conditions
        ultra = self.current_ultra # Keep the same mode
        self.paused_games.pop(self._pause_key(self.n, ultra), None) # Clear the paused save of this slot
        self._start_fresh(self.n, ultra) # Just say the normal methode, do it again
        save_settings_and_stats(self.settings, self.stats, self.paused_games) # Persist the cleared slot
        
    def resume_paused(self, n, ultra): # Continue a previously game
        saved = self.paused_games.get(self._pause_key(n, ultra)) # Load the saved state
        if not saved: # If it got lost somehow
            self._start_fresh(n, ultra) # Just start a new one instead
            return # task is done
        self.n = n # The size of the grid
        self.current_ultra = ultra # Remember the mode
        self.grid = saved["grid"] # Restore the numbers
        self.row_sums = saved["row_sums"] # Restore the row targets
        self.col_sums = saved["col_sums"] # Restore the col targets
        self.solution = saved["solution"] # Restore the solution for hints
        self.user_sel = saved["user_sel"] # Restore what was selected
        self.user_dimmed = saved["user_dimmed"] # Restore what was marked
        self.row_fulfilled = [False] * n # Recalculated on the next draw
        self.col_fulfilled = [False] * n # Recalculated on the next draw
        self.won = False # A paused round can never already be won
        self.paused = False # Continue playing right away
        self.total_paused_ms = 0 # Timer maths start fresh from here
        self.play_time = saved.get("play_time", 0) # Restore the duration till now
        self.start_time = pg.time.get_ticks() - self.play_time # To have a correct timer
        self.hints_left = saved.get("hints_left", con.HINTS_PER_GAME) # Restore the number of hints
        self.last_hint_cell = None # No fresh hint flash
        self.current_game_actions = saved.get("actions", []) # Restore the recorded actions
        self.cursor_c = 0 # Reset the keyboard position
        self.cursor_r = 0 # Reset the keyboard position
        self.state = "PLAY" # To go to the play screen
        
    def discard_and_start(self, n, ultra): # Throe away a paused game
        self.paused_games.pop(self._pause_key(n, ultra), None) # Remove the old slot
        self._start_fresh(n, ultra) # Start the new match
        save_settings_and_stats(self.settings, self.stats, self.paused_games) # Persist the cleared slot
    
    def stash_current_game(self, o_time=None): # Save an unfinished match, so it can be continued
        if self.state != "PLAY" or self.won: # Only unfinished matches
            return # do nothing
        key = self._pause_key(self.n, self.current_ultra) # The size/mode slot
        play_time = o_time if o_time is not None else self.play_time # Use the given time
        self.paused_games[key] = {
            "grid": self.grid,
            "row_sums": self.row_sums,
            "col_sums": self.col_sums,
            "solution": self.solution,
            "user_sel": self.user_sel,
            "user_dimmed": self.user_dimmed,
            "play_time": play_time,
            "hints_left": self.hints_left,
            "actions": self.current_game_actions
        } # Everything needed to can continue
        save_settings_and_stats(self.settings, self.stats, self.paused_games) # Persist the game
    
    def persist_settings(self): # Save the current settings
        self.settings = {
            "save_history": self.save_history,
            "timer_enabled": self.timer_enabled,
            "timer_ms": self.timer_ms,
            "sound_enabled": self.sounds.enabled,
            "alt_control": self.alt_control
        } # Collect the current values
        save_settings_and_stats(self.settings, self.stats, self.paused_games) # Persist the settings
        
    def move_cursor(self, key): # Move the keyboard cursor
        if self.won:
            return
        if self.state == "HANNAH" and getattr(self, "hannah_open_index", None) is not None:
            size = con.HANNAH_SIZE
        else:
            size = self.n
        if key == pg.K_UP: self.cursor_r = max(0, self.cursor_r - 1) # Move up the grid
        elif key == pg.K_DOWN: self.cursor_r = min(size - 1, self.cursor_r + 1) # Move down the grid
        elif key == pg.K_LEFT: self.cursor_c = max(0, self.cursor_c - 1) # Move left the grid
        elif key == pg.K_RIGHT: self.cursor_c = min(size - 1, self.cursor_c + 1) # Move right the grid
    
    ### Functions of Time ###
    def tick_timer(self): # Counts the time
        if self.state == "PLAY" and not self.won and not self.paused: # If the player is playing
            self.play_time = pg.time.get_ticks() - self.start_time - self.total_paused_ms # Time we have without the time we started and the time we haven't played
            
    def toggle_pause(self): # Collect the pause
        if self.won: # If the player already won
            return   # Do nothing
        self.paused = not self.paused # If paused follows not and else it follows
        if self.paused: # If we are in pause
            self.pause_started_at = pg.time.get_ticks() # Pause started now
        else:
            self.total_paused_ms += pg.time.get_ticks() - self.pause_started_at # Total time is the time it already is and also the time it was paused until.
            
    ### Interact with cells ###
    def click_cell(self, r, c, right_click=False, o_time=None, ultra=False): # Get the position and the click
        if self.won or self.paused: # Only if the game is not active
            return # Do nothing
        prev_sel = self.user_sel[r][c]       # Last move is this move
        prev_dimmed = self.user_dimmed[r][c] # Last mark is this mark
        
        if right_click: # If it was a right click
            self.user_dimmed[r][c] = not self.user_dimmed[r][c] # Toggle the state of the mark save
            self.user_sel[r][c] = False # A marked cell can not be selected
            action_type = "Right" # Name of the action
            self.sounds.play(self.sounds.dim) # Play dim sound
        else: # If it was a left click
            self.user_dimmed[r][c] = False # A selected cell can n ot be marked
            self.user_sel[r][c] = not self.user_sel[r][c] # Toggle between if it is selected or not
            action_type = "Left" # Name of the action
            self.sounds.play(self.sounds.click) # Play click sound
            
        if o_time is None:
            self.current_game_actions.append({
                "time": self.play_time,
                "type": action_type,
                "r": r, "c": c,
                "prev_sel": prev_sel,
                "prev_dimmed": prev_dimmed,
                "new_sel": self.user_sel[r][c],
                "new_dimmed": self.user_dimmed[r][c],
                "hints_used_so_far": con.HINTS_PER_GAME - self.hints_left
            }) # Add the action to the action saver
        else:
            self.current_game_actions.append({
                "time": o_time,
                "type": action_type,
                "r": r, "c": c,
                "prev_sel": prev_sel,
                "prev_dimmed": prev_dimmed,
                "new_sel": self.user_sel[r][c],
                "new_dimmed": self.user_dimmed[r][c],
                "hints_used_so_far": con.HINTS_PER_GAME - self.hints_left
            }) # Add the action to the action saver
        
        self._refresh_win_state(o_time, ultra) # Check if won
        
    def undo(self): # Delete the last move
        if not self.current_game_actions or self.won or self.paused: # If the game hasn't start or do not run
            return # Do nothing
        last = self.current_game_actions.pop() # Get the last saved action
        r, c = last["r"], last["c"] # Get the row and the column
        self.user_sel[r][c] = last["prev_sel"] # Get if the last action selected this cell
        self.user_dimmed[r][c] = last["prev_dimmed"] # Get if the last action marked this cell
        self.row_fulfilled = [False] * self.n # Because a correct row could now be wrong
        self.col_fulfilled = [False] * self.n # And we can calculate if the state should be something else
        self.sounds.play(self.sounds.undo) # Play undo sound
        
    def use_hint(self, o_time=None, ultra=False): # To handle the usage of a hint
        if self.hints_left <= 0 or self.won or self.paused: # Should be a running game and hints left
            return # Do nothing
        result = find_hint(self.solution, self.user_sel, self.user_dimmed, self.n) # Asked for a action
        if result is None: # If no action possible
            return # Do nothing
        r, c, should_select = result # Define parameters to show the valid action
        prev_sel = self.user_sel[r][c] # Last action is this action
        prev_dimmed = self.user_dimmed[r][c] # Last mark is this mark
        
        if should_select: # If the player should select this
            self.user_sel[r][c] = True # select it
            self.user_dimmed[r][c] = False # not mark it
        else:
            self.user_sel[r][c] = False # do not select
            self.user_dimmed[r][c] = True # do mark it
            
        self.hints_left -= 1 # One hint is used
        self.last_hint_cell = (r, c) # Save the row and the column
        self.hint_flash_timer = pg.time.get_ticks() # Get the time
        if o_time is None:
            self.current_game_actions.append({
                "time": self.play_time,
                "type": "Hint",
                "r": r, "c": c,
                "prev_sel": prev_sel,
                "prev_dimmed": prev_dimmed,
                "new_sel": self.user_sel[r][c],
                "new_dimmed": self.user_dimmed[r][c],
                "hints_used_so_far": con.HINTS_PER_GAME - self.hints_left
            }) # Add the action to the action saver
        else:
            self.current_game_actions.append({
                "time": o_time,
                "type": "Hint",
                "r": r, "c": c,
                "prev_sel": prev_sel,
                "prev_dimmed": prev_dimmed,
                "new_sel": self.user_sel[r][c],
                "new_dimmed": self.user_dimmed[r][c],
                "hints_used_so_far": con.HINTS_PER_GAME - self.hints_left
            }) # Add the action to the action saver
        self.sounds.play(self.sounds.hint) # Play hint sound
        self._refresh_win_state(o_time, ultra) # Check if won
        
    def _refresh_win_state(self, o_time=None, ultra=False): # Handle the win check
        self.row_fulfilled = [False] * self.n # Clear the correct marks
        self.col_fulfilled = [False] * self.n # So they do not glitch over each other
        self.won = check_win(self.grid, self.user_sel, self.row_sums, self.col_sums, self.n) # Check if won
        if self.won: # If the player actually won
            self.sounds.play(self.sounds.win) # Play win jingle
            hints_used = con.HINTS_PER_GAME - self.hints_left # The number of used hints
            final_time = o_time if o_time is not None else self.play_time # The time to record
            record_stat(self.stats, self.n, ultra, final_time) # Add the game to the statistics
            self.paused_games.pop(self._pause_key(self.n, ultra), None) # Clear the paused game
            save_settings_and_stats(self.settings, self.stats, self.paused_games) # Persist thet new situation
            if self.save_history: # If the user wants that his data get saved
                if o_time is not None:
                    save_match(self.grid, self.row_sums, self.col_sums, self.user_sel, self.user_dimmed, o_time, self.current_game_actions, hints_used, ultra=ultra) # Give the data to let them be saved
                else:
                    save_match(self.grid, self.row_sums, self.col_sums, self.user_sel, self.user_dimmed, self.play_time, self.current_game_actions, hints_used, ultra=ultra) # Give all the data to let them be saved
                
    ### History ###
    def open_history(self): # Open the history view
        self.history_entries = list_history_meta() # Need the files to show
        self.history_scroll_y = 0 # Start at the top
        self.state = "HISTORY" # Set the state to the history one
        
    def toggle_size_filter(self, n): # Handle if a size should be shown
        self.history_filter_size = n if self.history_filter_size != n else None # If the filter is selected unselect, else select
        self.history_scroll_y = 0 # Back to the top
        
    def toggle_top10_filter(self): # Handle the time filter
        self.history_filter_top10 = not self.history_filter_top10 # Toggle the filter
        self.history_scroll_y = 0 # Back to the top
        
    def toggle_ultra_filter(self): # Handle the ultra filter
        self.history_filter_ultra = not self.history_filter_ultra # Toggle if active or not
        self.history_scroll_y = 0 # Back to the top
        
    def filtered_history(self): # Does the filtering
        entries = self.history_entries # Load entries
        if self.history_filter_size is not None: # If a size specification is active
            entries = [e for e in entries if e["size"] == self.history_filter_size] # Sort for the right size
        if self.history_filter_ultra and not any(e.get("ultra") for e in entries): # If the ultra filter is active but no ultra entries exist
            self.history_filter_ultra = False # Turn it off automatically
        if self.history_filter_ultra: # If the ultra filter is active
            entries = [e for e in entries if e["ultra"] == True] # If the game is ultra
        if self.history_filter_top10: # If the top 10 is active
            entries = sorted(entries, key=lambda e: e["play_time"])[:10] # Sorted when clicked for the time and cut everything under top 10
        return entries # Gives created right entries
    
    def delete_history(self, filename): # Delete a given file from the storage
        delete_match(filename) # Outsources the task
        self.history_entries = list_history_meta() # Update the enable history
    
    ### History Detail    
    def open_history_detail(self, filename): # Open the more informtive view of an file
        self.selected_history_data = load_match(filename) # Load the game data
        self.selected_history_name = filename # Get the name
        self.detail_selected_index = None # No move selected
        self.detail_scroll_y = 0 # Start at the top
        self.state = "HISTORY_DETAIL" # Set the state to the right one
        
    def select_detail_action(self, index): # Let select an action
        self.detail_selected_index = None if self.detail_selected_index == index else index # Self index, doppleclick, end view, else the clicked view
        
    def reset_detail_view(self): # Go back to end view
        self.detail_selected_index = None # Nothing is selected
        
    def init_hannah(self): # Prepares or reopen hannah screen
        if not getattr(self, "hannah_levels", None): # Only build levels once
            self.hannah_levels = [] # Empty level slott
            n = con.HANNAH_SIZE # The size every gird uses
            for letter_char in con.HANNAH_MESSAGE: # For every letter in the message
                if letter_char is None: # For the empty spaces
                    self.hannah_levels.append(None) # No puzzle here
                    continue # Next slot
                grid, row_sums, col_sums, solution = generate_level_letter(n, letter_char) # Build the letter based puzzle
                self.hannah_levels.append({
                    "letter": letter_char, "grid": grid, "row_sums": row_sums, "col_sums": col_sums, "solution": solution, "user_sel": [[False] * n for _ in range(n)], "user_dimmed": [[False] * n for _ in range(n)], "actions": []
                }) # Saves everything needed
            for i, solved in enumerate(self.hannah_solved): # Restore already solved letters
                if solved and i < len(self.hannah_levels) and self.hannah_levels[i] is not None: # If this slot is a solved letter
                    lvl = self.hannah_levels[i] # Get the level data
                    lvl["user_sel"] = [row[:] for row in lvl["solution"]] # Fill it in as already solved
        self.hannah_scroll_x = 0 # Start scrolled all the way to the left
        self.cursor_r = 0
        self.cursor_c = 0
        self.hannah_open_index = None # Show the overview
        self.state = "HANNAH" # Set the state to the easter egg screen
    
    def hannah_open(self, index): # Open one tile as a playable mini puzzle
        if index is None or index >= len(self.hannah_levels) or self.hannah_levels[index] is None: # If this is not a valid slot
            return # do nothing
        self.hannah_open_index = index # Remember the open tile
        self.cursor_r = 0
        self.cursor_c = 0
        
    def hannah_close(self): # Leave a mini puzzle
        self.hannah_open_index = None # Back to the overview
        
    def hannah_click_cell(self, r, c, right_click=False): # Handle a click inside the letter puzzle
        if self.hannah_open_index is None: # Nothing opend
            return # nothing to do
        lvl = self.hannah_levels[self.hannah_open_index] # the currently open puzzle game
        prev_sel = lvl["user_sel"][r][c]
        prev_dimmed = lvl["user_dimmed"][r][c]
        if lvl["user_sel"][r][c] and lvl["user_dimmed"][r][c]: # Both possibilities selected
            lvl["user_dimmed"][r][c] = False # Clear the normally wrong state
        if right_click: # Right-click makrs a cell
            lvl["user_dimmed"][r][c] = not lvl["user_dimmed"][r][c] # Toggle the mark
            if lvl["user_dimmed"][r][c]: # If marked
                lvl["user_sel"][r][c] = False # It can not be selected as well
            self.sounds.play(self.sounds.dim) # Play the right click sound
        else: # Have to be a left click
            lvl["user_sel"][r][c] = not lvl["user_sel"][r][c] # Toggle the selection
            if lvl["user_sel"][r][c]: # If a cell is selected
                lvl["user_dimmed"][r][c] = False # can not be marked
            self.sounds.play(self.sounds.click) # Play the left click sound
        lvl["actions"].append({"r": r, "c": c, "prev_sel": prev_sel, "prev_dimmed": prev_dimmed})
        n = con.HANNAH_SIZE # Load the grid size
        if check_win(lvl["grid"], lvl["user_sel"], lvl["row_sums"], lvl["col_sums"], n): # If the letter is found
            self.sounds.play(self.sounds.win) # Play the win sound
            while len(self.hannah_solved) <= self.hannah_open_index: # Make sure it can be rememberd
                self.hannah_solved.append(False) # fill with unsolved level entries
            self.hannah_solved[self.hannah_open_index] = True # Set level entry to solved
            save_settings_and_stats(self.settings, self.stats, self.paused_games, self.hannah_solved) # Persist the progress
            self.hannah_open_index = None # Return to the overview automatically
            
    def hannah_undo(self): 
        if self.hannah_open_index is None:
            return
        lvl = self.hannah_levels[self.hannah_open_index]
        if not lvl["actions"]:
            return
        last = lvl["actions"].pop()
        lvl["user_sel"][last["r"]][last["c"]] = last["prev_sel"]
        lvl["user_dimmed"][last["r"]][last["c"]] = last["prev_dimmed"]
        self.sounds.play(self.sounds.undo)