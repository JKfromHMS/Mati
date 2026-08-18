### Mati (Mathematics and tactic intelligence) ###
### V0.1.0 Beta V1.0.10 ###
### Author: Janosch Klawatsch, 16.07.2026 ###
### game file V0.1.2 ###

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
import config as con # To have the constants
from level import check_win, find_hint, generate_level # That levels can be created and checked
from persistence import delete_match, list_history_meta, load_match, save_match # For the save and history parts

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
        self.timer_enabled = False             # Trackes if the timer is shown
        self.timer_ms = False                  # Trackes if the timer has a ms digit
        self.save_history = True               # Tracked if the history is saved
        self.request_fullscreen_toggle = False # Should change fullscreen state
        self.is_fullscreen = False             # Saves if the game is in fullscreen
        
        # Hints & Undo
        self.hints_left = con.HINTS_PER_GAME # Sets the number of hints of a round
        self.last_hint_cell = None           # Saves which cells was hints
        self.hint_flash_timer = 0            # Trackes hint time
        self.current_game_actions = []       # Trackes every game action
        
        # History
        self.history_entries = []           # Remembers all played games
        self.history_scroll_y = 0           # Trackes how far is scrolled threw this files
        self.history_filter_size = None     # Saves if a size filter is active
        self.history_filter_top10 = None    # Saves if just the top 10 should be shown
        self.selected_history_data = None   # Saves which data are selected
        self.selected_history_name = None   # Save the name of the selected data package
        self.detail_selected_index = None   # Also the index number off the data
        self.detail_scroll_y = 0            # Trackes how far is scrolled threw the moves of a game
        
        # Trackpad Click Save
        self.last_wheel_time = - 10 ** 9      # Time of last scroll
        
    def new_game(self, n): # Creates a new game depending on the size given
        self.n = n # The size of the grid
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
        self.state = "PLAY" # Now we need the Play-Screen
        
    def restart_same(self): # Let the game start again under same conditions
        self.new_game(self.n) # Just say the normal methode, do it again
        
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
    def click_cell(self, r, c, right_click=False): # Get the position and the click
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
        
        self._refresh_win_state() # Check if won
        
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
        
    def use_hint(self): # To handle the usage of a hint
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
        self.sounds.play(self.sounds.hint) # Play hint sound
        self._refresh_win_state() # Check if won
        
    def _refresh_win_state(self): # Handle the win check
        self.row_fulfilled = [False] * self.n # Clear the correct marks
        self.col_fulfilled = [False] * self.n # So they do not glitch over each other
        self.won = check_win(self.grid, self.user_sel, self.row_sums, self.col_sums, self.n) # Check if won
        if self.won: # If the player actually won
            self.sounds.play(self.sounds.win) # Play win jingle
            if self.save_history: # If the user wants that his data get saved
                hints_used = con.HINTS_PER_GAME - self.hints_left # Number of used hints
                save_match(self.grid, self.row_sums, self.col_sums, self.user_sel, self.user_dimmed, self.play_time, self.current_game_actions, hints_used) # GIve all the data to let them be saved
                
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
        
    def filtered_history(self): # Does the filtering
        entries = self.history_entries # Load entries
        if self.history_filter_size is not None: # If a size specification is active
            entries = [e for e in entries if e["size"] == self.history_filter_size] # Sort for the right size
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