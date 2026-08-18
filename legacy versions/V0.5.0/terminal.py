### Mati (Mathematics and tactic intelligence) ###
### V0.5.0 Beta V1.0.19 ###
### Author: Janosch Klawatsch, 16.08.2026 ###
### terminal file V0.5.2 ###

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
import sys          # For system commands
import pygame as pg # Something like the engine on which the game runs.
from datetime import datetime as dt # To get the time
from collections import deque # To make the terminal shown object more efficent
import re # To get efficient matching situations

### Own ###
import config as con     # For the constants
import widgets as w      # To have widgets
from game import Game    # For the game parameters
import persistence as ps # To read the statistics

### -Functions- ###
class Terminal: # The hole terminal
    def __init__(self, sounds): # Every class needs an init
        self.sounds = sounds # Load sounds
        self.lines = deque(maxlen=con.MAX_LINES) # Generate a line handler
        self.line_surfs = deque(maxlen=con.MAX_LINES) # Finished rendered version of line
        self.input_buffer = "" # The player had not a word tipped
        self.cursor_pos = 0 # where in the buffer the user is
        self.scroll_offset = 0 # How far scrolled threw terminal
        self.ultra_game = None # Start in the normal terminal
        self.terminal_mode = None # Start in the normal terminal
        self.should_close = False # That it stays open
        self.next_state = None # State to switch to after leaving terminal
        self.next_game = None # Game to start after leaving terminal
        self._pending_resume_n = None # Set size paused ultra game
        self._normal_history = [] # Saved commands in the normal terminal mode
        self._ultra_history = [] # Saved commands in the ultra game mode
        self._history_index = None # Current position in the active command history
        self._font = pg.font.SysFont("couriernew", 19) # The font for the terminal
        self.settings, self.stats, _, _, self.achievements = ps.load_settings_and_stats() # Load the settings
        self.heading = "Mati Terminal"
        self.o_time = 0
        self.active_filters = []
        self.active_sort = []
        
    def _play_terminal_sound(self, sound): # Plays a sound for the terminal itself, independent from the normal game's sound setting
        if self.settings.get("terminal_sound_enabled", True) and self.sounds and self.sounds.available and sound: # Only if wanted and possible
            sound.play() # Play it, bypassing the shared Sounds.enabled flag on purpose

    
    
    def _print(self, text="", size="normal"): # Prints a given text into the terminal
        self.lines.append(text) # Add the new lines
        if size == "normal": self._font = pg.font.SysFont("couriernew", 19)
        elif size == "small": self._font = pg.font.SysFont("couriernew", 17)
        surf = self._font.render(text, True, con.TEXT_COLOR_2) # Creates the surf new
        self.line_surfs.append(surf) # Get it on the screen
        self.scroll_offset = 0 # follow new output
         
    def _visible_count(self): # Lines fit on the screen
        return max(1, (con.HEIGHT - 90) // con.LINE_HEIGHT)
    
    def scroll(self, delta): # scroll threw the lines
        if self.ultra_game: # in game mode
            return # do not work in game
        max_offset = max(0, len(self.line_surfs) - self._visible_count()) # how far we can scroll
        self.scroll_offset = max(0, min(self.scroll_offset + delta, max_offset)) # scroll     
      
          
    def _active_history(self): # Get the history for the current terminal mode
        return self._ultra_history if self.ultra_game else self._normal_history


    def _store_command(self, command): # Save a command in the right history
        if not command:
            return
        history = self._active_history()
        if not history or history[-1] != command:
            history.append(command)
        self._history_index = None


    def handle_key(self, event): # Handle the pressed keys
        if event.key in (pg.K_UP, pg.K_DOWN) and (event.mod & (pg.KMOD_CTRL | pg.KMOD_META)) and not self.ultra_game: # to scroll the screen
            self.scroll(3 if event.key == pg.K_UP else -3) # move up or down
            return # task is done
        
        match event.key: # Since py 3.10 match case is possible for more speed
            case pg.K_RETURN: # If the entry is finished
                self._submit() # Work with the entry
                
            case pg.K_BACKSPACE: # Delete last character
                if self.cursor_pos > 0: # not empty or at start
                    self.input_buffer = self.input_buffer[:self.cursor_pos - 1] + self.input_buffer[self.cursor_pos:] # cut the right element out
                    self.cursor_pos -= 1 # move cursor with delete
                    self._history_index = None # in no list anymore
                    
            case pg.K_DELETE: # delete the character right of the cursor
                if self.cursor_pos < len(self.input_buffer): # not at the end
                    self.input_buffer = self.input_buffer[:self.cursor_pos] + self.input_buffer[self.cursor_pos + 1:] # cut it of
                    self._history_index = None # in no list anymore
                    
            case pg.K_LEFT: # Move the cursor to the left
                self.cursor_pos = max(0, self.cursor_pos - 1) # not before the start
                
            case pg.K_RIGHT: # Move the cursor to the right
                self.cursor_pos = min(len(self.input_buffer), self.cursor_pos + 1) # not behind the end
                
            case pg.K_HOME: # Jump to the start
                self.cursor_pos = 0 # very start
                
            case pg.K_END: # Jump to the end
                self.cursor_pos = len(self.input_buffer) # very end
                    
            case pg.K_UP: # Move backward the command history
                if history := self._active_history(): # get game/terminal
                    if self._history_index is None:
                        self._history_index = len(history) - 1
                    else:
                        self._history_index = max(0, self._history_index - 1)
                    self.input_buffer = history[self._history_index] # Show the got element
                    self.cursor_pos = len(self.input_buffer) # cursor goes to the end
                    
            case pg.K_DOWN: # Move forward in command history
                history = self._active_history()
                if history and self._history_index is not None and self._history_index + 1 < len(history):
                    self._history_index += 1
                    self.input_buffer = history[self._history_index]
                else:
                    self.input_buffer = ""
                    self._history_index = None
                self.cursor_pos = len(self.input_buffer) # cursor goes to the end
                    
            case _: # Any other key
                if event.unicode and event.unicode.isprintable() and len(self.input_buffer) < con.INPUT_MAX_LEN:
                    self._play_terminal_sound(self.sounds.tip if self.sounds else None) # A small keystroke sound
                    self.input_buffer = self.input_buffer[:self.cursor_pos] + event.unicode + self.input_buffer[self.cursor_pos:] # Insert at the cursor
                    self.cursor_pos += 1 # Move the cursor with the new character
                    self._history_index = None
            
            
    def close(self): # Allow to close the terminal from out of the terminal
        self._handle_command("close") # close the game
       
            
    def _submit(self): # Do a command
        command = self.input_buffer.strip() # Load the command
        if not command: # If wrong alert
            return # do nothing
        self._play_terminal_sound(self.sounds.sub if self.sounds else None) # A distinct sound for submitting a command
        self._store_command(command)
        self._print(f"> {command}") # Print command to the screen
        self._handle_command(command) # Let the command be done
        self.input_buffer = "" # Clear the current line after execution
        self.cursor_pos = 0 # put cursor back to start
       
        
    def _handle_command(self, command): # Handles the commands
        cmd = command.lower() # Make big and small leter version does not count
        c_cmd = cmd.replace(" ", "") if " " in cmd else cmd # Remove spaces to make it easier to handle
        
        match self.terminal_mode:
            case "about":
                self._handle_about_command(c_cmd, command)
                return
            
            case "settings":
                self._handle_settings_command(c_cmd, command)
                return
            
            case "history":
                self._handle_history_command(cmd, c_cmd, command)
                return
        
        match c_cmd: # py 3.10 method for efficient if else leave out
            case "close": # User wnat to close the terminal
                if self.ultra_game: # If the player is playing
                    self.o_time = pg.time.get_ticks() - self.timer
                    self.ultra_game.stash_current_game(o_time=self.o_time)
                    self.next_state = "MENU"
                self.should_close = True # Say it should be closed
                self._clear() # Give command to clear
                self._print("Terminal is getting closed") # Say the user what happend, if it takes long
                return # task is done
            
            case "time": # User want the time
                if self.ultra_game:
                    self._print_board() # Redraw the board
                    self._print(f"> {command}") # Make it look more equal
                self._print(f"    The current time is: {dt.now().strftime("%H:%M:%S")}") # Give the time
                return # task is over        
            
        if self.ultra_game: # If in the game mode
            self._handle_game_command(c_cmd, command) # Say handle the ingame command
            return # task is done
        
        if cmd == "jay loves": # Easteregg command
            self.next_state = "HANNAH" # easteregg state
            self.should_close = True # outside the terminal
            self._clear() # leave empty terminal
            return # task is done
                
            
        match c_cmd: # py 3.10 method for efficient if else leave out
            case "help": # User want help
                self._clear() # Clear the screen
                self._help_menu(state=1) # Draw the help menu
                return # task is done
            
            case "helpoverall": # The general terminal commands
                self._clear()
                self._help_overall()
                return
            
            case "helpgame": # The help how to start a game
                self._clear()
                self._help_game()
                return
            
            case "helpingame": # The commands ingame
                self._clear()
                self._help_menu(state=2)
                return
            
            case "helpsettings": # The setting commands
                self._clear()
                self._help_settings()
                return
            
            case "quit": # User want to quit the game
                pg.quit()  # End the game
                sys.exit() # End the programm
                return # In case of a failure do nothing more
            
            case "clear": # User want an empty screen
                self._clear() # Say the screen should be cleared
                return # task is done
            
            case "stats": # If the player want to see his stats
                self._clear() # Clear the screen
                self._print_stats() # Show the stats
                return # task is done
            
            case "achievements":
                self._clear()
                self._print_achievements()
                return
            
            case "abouttext": # About in the terminal
                self.terminal_mode = "about"
                self._cleared()
                self._print_about()
                return
            
            case "settingstext": # Settings in terminal
                self.terminal_mode = "settings"
                self._cleared()
                self._print_settings()
                return
            
            case "historytext": # history in terminal
                self.terminal_mode = "history"
                self._cleared()
                self._print_history()
                return 
            
        
        if self._pending_resume_n: # If the player has to decide if he want to continue or start a new game
            is_continue = cmd in ("continue", "c") # Continue
            is_new = cmd in ("new", "n") # New

            if not (is_continue or is_new): # Non of these
                self._print("Please type 'continue' or 'new'.") # Ask again
                return # nothing more

            n = self._pending_resume_n # get size
            self.ultra_game = Game(self.sounds) # get sounds
            self._pending_resume_n = None # decision made

            if is_continue: # wants to resume
                self.ultra_game.resume_paused(n, True) # make it
                self.timer = pg.time.get_ticks() - self.ultra_game.play_time # get time
                self._clear() # clear the screen
                self._print("Round continued.") # say it
            else:  # is_new
                self.ultra_game.discard_and_start(n, True) # make it
                self.timer = pg.time.get_ticks() # get time refreshed
                self._print(f"Starting round in {n}x{n}") # say it

            self._print_board() # show it
            return # end
        
        if state := con.NAVIGATE_COMMANDS.get(c_cmd): # If the player want to navigate to another state
            self.next_state = state # Set the next state
            self.should_close = True # Say the game it should close the terminal
            self._clear() # Clear the screen
            self._print(f"Leaving terminal to {state.lower()}.") # If the programm got slow, to explain what is happening
            return # task is done
        
        if size := con.PLAY_COMMANDS.get(c_cmd): # If the player want to start a normal match
            self.next_game = (size, False) # Set the next game
            self.next_state = "PLAY" # Set next state
            self.should_close = True # Say the game it should close the terminal
            self._clear() # Clear the screen
            self._print(f"Leaving terminal to play {size}x{size}.") # If the programm got slow, to explain what is happening             
            return # task is done
            
        if size := con.ULTRA_COMMANDS.get(c_cmd): # If the player want to start an ultra match
            self._start_ultra(size) # Start the ultra match
            return # task is done
            
        self._print(f"Unknown Command: {command}") # If the code goes until here, the command was not valid
        
        
    def _start_ultra(self, n): # Starts a new ultra match
        ### extrem efficientcy lose, because it create a new class object for checking in some cases ###
        ### just to make sure i will find it ###
        ### even when i read threw this code later ###
        
        probe = Game(self.sounds) # Just to check the paused slot
        
        if probe._pause_key(n, True) in probe.paused_games: # If a paused match exsist
            self._clear() # Give command to clear
            self._pending_resume_n = n # Remember the size
            self._print(F"Found a paused ultra round in {n}x{n}.") # Inform the player
            self._print("Type 'continue' (c) to resume it or 'new' (n) to start over.") # Ask what to do
            return # Wait for the desicion
        
        self._clear() # Give the command to clear
        self.ultra_game = probe # Load the game class
        self.ultra_game.new_game(n, ultra=True, force_new=True) # Generate new game
        self._print(f"Starting round in {n}x{n}") # Print what is happening
        self.timer = pg.time.get_ticks() # Get the time
        self._print_board() # Print the board
        
        
    def _handle_game_command(self, cmd, command): # Handle commands in game mode
        game = self.ultra_game # Load the game
        
        if command == "42": # Second little easter egg
            self._print_board() # Clear the screen
            self._print("42 - The answer for everything except this game.")
            game.mark_achievement("42_found") # Remember the easter egg was found.
            return
        
        if cmd == "help": # If the player want help
            self._print_board() # Clear the screen
            self._help_menu(state=2) # Draw the help menu
            return # task is done
        
        if cmd == "return": # If the user want to go back
            self.o_time = pg.time.get_ticks() - self.timer
            game.stash_current_game(o_time=self.o_time) # Save the unfinished game
            self.ultra_game = None # No game is running anymore
            self._clear() # Give command to clear
            return # task is over
        
        if cmd == "hint": # If the user want a hint
            if game.won: # If the user has won
                self._print("You have already won.") # Say it to the user
            else:
                self.o_time = pg.time.get_ticks() - self.timer
                before = game.hints_left # Load the number of hints left
                game.use_hint(o_time=self.o_time, ultra=True) # Find an hint
                game.stash_current_game(o_time=self.o_time)
                self._print_board() # Show the board
                self._print("No hints available." if game.hints_left == before else "Hint used.") # Print if the hint is available or not
                if game.won: # If this action made the win
                    self._print("Celebration! You have won.") # Say it the user
                    self.tim = pg.time.get_ticks() - self.timer # The end time
            return # Task is over
        
        if cmd == "new": # If the player want a new game
            game.restart_same() # Restart the game
            self._clear() # Give command to clear
            self._print("Started new round") # Say it the user
            self._print_board() # Show the board to the player
            self.timer = pg.time.get_ticks() # Get the time
            return # Task is done
        
        if cmd in {"playtime", "pt", "playtimelong", "ptl"}:
            if not game.won:
                self.tim = pg.time.get_ticks() - self.timer

            ms = self.tim % 1000
            seconds = (self.tim // 1000) % 60
            minutes = self.tim // 60000

            is_long = cmd in {"playtimelong", "ptl"}

            if self.tim < 60000: # Less than a minute: seconds and ms
                self.ingame_time = f"{seconds:02}:{ms:03}s"
            elif is_long or game.won: # More than a minute and won or long
                self.ingame_time = f"{minutes:02}:{seconds:02}:{ms:03}min"
            else: # More than a minute: normal view
                self.ingame_time = f"{minutes:02}:{seconds:02}min"

            self._print_board()
            self._print(f"> {command}")
            self._print(f"    Time in Game: {self.ingame_time}")
            return
        
        parsed = self._parse_action(cmd, game.n) # Find out if the command was a command for clicks
        if parsed is None: # If is not
            self._print_board() # Print the board
            self._print(f"> {command}") # Make it look more equal
            self._print(f"Unknown command: {command}") # Say it to the user
            return # task is done
        
        if game.won: # If the player has won
            self._print("You have already won.") # Say it to the user
            return # task is done
        
        r, c, right_click = parsed # Load what was done
        self.o_time = pg.time.get_ticks() - self.timer
        game.click_cell(r, c, right_click=right_click, o_time=self.o_time, ultra=True) # Let the game work the click
        game.stash_current_game(o_time=self.o_time)
        self._print_board() # Print the new board
        if game.won: # If this action made the win
            self.tim = pg.time.get_ticks() - self.timer # The end time
            
            
    def _handle_about_command(self, c_cmd, command):
        if c_cmd == "return":
            self.terminal_mode = None
            self._clear()
        else:
            self.terminal_mode = None
            self._handle_command("abouttext")
            
            
    def _handle_settings_command(self, c_cmd, command):
        # Split the command into words to identify the action
        words = command.lower().split()
        if not words:
            return
        
        action = words[0]
        
        if c_cmd in ("return", "close"):
            self.terminal_mode = None
            self._clear()
            if c_cmd == "close":
                self._handle_command("close")
            return
        
        elif c_cmd == "openreal":
            self.next_state = "SETTINGS"
            self.should_close = True
            self._clear
            self._print("Leaving terminal to settings.")
            return
        
        if action == "change":
            _, stats, paused_games, _, _ = ps.load_settings_and_stats()
            
            if "to" in words: # Change 'setting' to 'status'
                to = words.index("to")
                setting = ""
                for i in range (1, to):
                    setting += f"{words[i]}"
                     
                status = words[to + 1]
                
                if status not in ("yes", "no"):
                    return
                
                stat = True if status == "yes" else False
                
                match setting:
                    case "saveplayed":
                        self.settings["save_history"] = stat
                        
                    case "showtimer":
                        self.settings["timer_enabled"] = stat
                        if stat == False: self.settings["timer_ms"] = stat
                        
                    case "milliseconds":
                        self.settings["timer_ms"] = True if (stat and self.settings["timer_enabled"] == True) else False
                        
                    case "sound":
                        self.settings["sound_enabled"] = stat
                        
                    case "terminalsound":
                        self.settings["terminal_sound_enabled"] = stat
                        
                    case "keyboard-navigation":
                        self.settings["alt_control"] = stat
                        
                    case "liveclock":
                        self.settings["live_clock_enabled"] = stat
                        
                    case "ultratimer":
                        self.settings["ultra_timer_enabled"] = stat
                        if stat == False: self.settings["ultra_timer_ms"] = stat
                        
                    case "ultramilliseconds":
                        self.settings["ultra_timer_ms"] = True if (stat and self.settings["ultra_timer_enabled"] == True) else False
                        
                    case "liveclockterminal":
                        self.settings["ultra_timer_show_clock"] = stat
                        
                    case _:
                        self._print("Please type: Change 'setting' to 'Yes/No'")
                        self._print("Or: Change 'setting', to toggle it.")
                        
            else: # Change 'setting'
                setting = ""
                for i in range (1, len(words)):
                    setting += f"{words[i]}"
                    
                match setting:
                    case "saveplayed":
                        self.settings["save_history"] = not self.settings["save_history"]
                                            
                    case "showtimer":
                        self.settings["timer_enabled"] = not self.settings["timer_enabled"]
                        if self.settings["timer_enabled"] == False: self.settings["timer_ms"] = False
                                            
                    case "milliseconds":
                        self.settings["timer_ms"] = True if (self.settings["timer_ms"] == False and self.settings["timer_enabled"] == True) else False
                                            
                    case "sound":
                        self.settings["sound_enabled"] = not self.settings["sound_enabled"]
                        
                    case "terminalsound":
                        self.settings["terminal_sound_enabled"] = not self.settings["terminal_sound_enabled"]
                                            
                    case "keyboard-navigation":
                        self.settings["alt_control"] = not self.settings["alt_control"]
                                                                   
                    case "liveclock":
                        self.settings["live_clock_enabled"] = not self.settings["live_clock_enabled"]
                                            
                    case "ultratimer":
                        self.settings["ultra_timer_enabled"] = not self.settings["ultra_timer_enabled"]
                        if self.settings["ultra_timer_enabled"] == False: self.settings["ultra_timer_ms"] = False
                               
                    case "ultramilliseconds":
                        self.settings["ultra_timer_ms"] = True if (self.settings["ultra_timer_ms"] == False and self.settings["ultra_timer_enabled"] == True) else False
                        
                    case "liveclockterminal":
                        self.settings["ultra_timer_show_clock"] = not self.settings["ultra_timer_show_clock"]
                                         
                    case _:
                        self._print("Please type: Change 'setting' to 'Yes/No'")
                        self._print("Or: Change 'setting', to toggle it.")     
                        
            ps.save_settings_and_stats(self.settings, stats, paused_games)
            self.terminal_mode = None
            self._handle_command("settingstext")
        
        else:
            self.terminal_mode = None
            self._handle_command("settingstext")
        
        return
    
    
    def _handle_history_command(self, cmd, c_cmd, command):
        if c_cmd in ("return", "close"):
            self.terminal_mode = None
            self._clear()
            if c_cmd == "close":
                self._handle_command("close")
            return
                
        elif c_cmd == "openreal":
            self.next_state = "HISTORY"
            self.should_close = True
            self._clear
            self._print("Leaving terminal to history.")
            return
        
        if cmd.startswith("filter "):
            cmdo = cmd.split()[1]
            if cmdo == "under_time" or  cmdo == "over_time": cmdo += cmd.split()[2]
            self.active_filters.append(cmdo)
        elif c_cmd == "sorted":
            self.active_sort = ["newest"]
        elif c_cmd == "unfiltered":
            self.active_filters = []
        elif c_cmd == "reset":
            self.active_filters = []
            self.active_sort = ["newest"]
        elif cmd.startswith("sort by "):
            raw_args = cmd.removeprefix("sort by ").strip().replace(" ", "_").split("_")
            
            # Normalize tokens
            tokens = []
            i = 0
            while i < len(raw_args):
                if i + 1 < len(raw_args) and f"{raw_args[i]}_{raw_args[i + 1]}" in ("hints_up", "hints_down"):
                    tokens.append(f"{raw_args[i]}_{raw_args[i + 1]}")
                    i += 2
                else:
                    tokens.append(raw_args[i])
                    i += 1
                    
            # Prevent conflict opposites
            opposites = [
                {"newest", "oldest"},
                {"fastest", "slowest"},
                {"hints_up", "hints_down"},
                {"smallest", "biggest"},
                {"ultra", "normal"}
            ]
            
            valid_tokens = []
            time_tokens = []
            TIME_KEYS = {"fastest", "slowest", "newest", "oldest"}
            
            for token in tokens:
                has_conflict = any(token in group and any(t in group for t in valid_tokens + time_tokens) for group in opposites)
                if not has_conflict:
                    if token in TIME_KEYS:
                        time_tokens.append(token)
                    else:
                        valid_tokens.append(token)
            
            self.active_sort = valid_tokens + (time_tokens[:1] if time_tokens else [])
            
        
        self._print_history(active_filters=self.active_filters[:], active_sort=self.active_sort[:])
            
        
        
        return
         
            
    @staticmethod # The next function does not need self
    def _parse_action(cmd, n): # Find out if it was an action
        if len(cmd) != 3 or not cmd[0].isdigit() or not cmd[1].isdigit() or cmd[2] not in ("l", "r"): # Check if valid
            return None # Say not valid
        c = int(cmd[0]) - 1 # Get the column
        r = int(cmd[1]) - 1 # Get the row
        if not (0 <= r < n) or not (0 <= c < n): # Check if given position exsists
            return None # Say it
        return r, c, (cmd[2] == "r") # If the pos is valid give it back
    
    
    @staticmethod # The nect function does not need self
    def _fmt_time(ms): # Forms ms to mins secs and remaining ms
        if ms is None: # Nothing to format
            return "-          " # Say so
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        s = ms % 1000 # Get correct miliseconds remaining
        return f"{minutes}:{seconds:02}:{s:03}min" # Give the formated time
    
    @staticmethod
    def _format_time(second):
        seconds = float(second)
        minutes = int(seconds // 60)
        rem_seconds = seconds % 60
        
        # Remove the trailing zero
        if rem_seconds.is_integer():
            rem_seconds = int(rem_seconds)
            
        if minutes > 0 and rem_seconds:
            return f"{minutes}min and {rem_seconds}s"
        elif minutes > 0:
            return f"{minutes}min"
        else:
            return f"{rem_seconds}s"
        
    @classmethod
    def _format_achievement(cls, key: str, completed: bool) -> str:
        mode = "ultra" if "_ultra" in key else "normal"
        
        # Find out if it is time achievement
        time_match = re.match(r"^(\d+x\d+)(?:_ultra)?_(\d+(?:\.\d+)?)s$", key) # This part is AI made, this line and the next three
        if time_match:
            puzzle = time_match.group(1)
            second = time_match.group(2)
            formatted_time = cls._format_time(second)
            
            if completed:
                return f"You have won a {puzzle} {mode} match in less than {formatted_time}"
            else:
                return f"Try to win a {puzzle} {mode} match in less than {formatted_time}"
            
        # Find out if it is count based achievement
        count_match = re.match(r"^(\d+)_(\d+x\d+)(?:_ultra)?$", key) # This part is AI made, this line and the next three
        if count_match:
            count = count_match.group(1)
            puzzle = count_match.group(2)
            
            if completed:
                return f"You have won more than {count} {mode} {puzzle} matches"
            else:
                return f"Try to win {count} {mode} {puzzle} matches"
            
        return key
    
    
    def _print_stats(self): # Print the stats
        self._print("Statistics")
        self._print("") # An empty line
        
        max_games = max(
            (
                self.stats.get(str(n), {}).get(mode, {}).get("games", 0) 
                for n in con.DIFFICULTIES 
                for mode in ("normal", "ultra") 
            ), 
            default=0
        )
        g_width = len(str(max_games))
        
        for mode_label, mode_key in (("Normal", "normal"), ("Ultra", "ultra")): # For each mode
            self._print(f"{mode_label:<6}") # Give the label
            for n in con.DIFFICULTIES: # For every grid size
                m = self.stats.get(str(n), {}).get(mode_key, {}) # Get the stats and from them the mode
                games = m.get("games", 0) # Number of played games
                best = m.get("best", None) # Best time
                total = m.get("total", 0) # Total played time
                
                avg = total // games if games else None # Average time per game
                game_word = "game " if games == 1 else "games" # Get if it has to be games or game (with space to get to the same len)
                
                self._print(f"  {n}x{n}: {games:>{g_width}} {game_word} | Best: {self._fmt_time(best)} | Avg: {self._fmt_time(avg)}") # One line each size with same len
        
        #for n in con.DIFFICULTIES: # For every grid size
        #    entry = stats.get(str(n), {}) # Get its stats if available
        #    for mode_label, mode_key in (("Normal", "normal"), ("Ultra", "ultra")): # For each mode
        #        m = entry.get(mode_key, {"games": 0, "best": None, "total": 0}) # Get the mode stats
        #        games = m.get("games", 0) # Number a played games
        #        best = m.get("best") # Best time
        #        total = m.get("total", 0) # Total played time
        #        avg = int(total / games) if games else None # Average time per game
        #        if mode_label in ("Normal", "normal"): self._print(f"{n}x{n} {mode_label}: {games} game(s) | Best: {self._fmt_time(best)} | Avg: {self._fmt_time(avg)}") # One line each size mode combo
        #        else: self._print(f"{n}x{n} {mode_label}:  {games} game(s) | Best: {self._fmt_time(best)} | Avg: {self._fmt_time(avg)}") # One line each size mode combo
        # Saved because of the idea, that you can make a setting, how the user like to see it
        self._print("") # An empty line
        
        
    def _print_achievements(self):
        hannah_completed = "You have completed the Hannah Easter-Egg"
        
        readable_results = {key: self._format_achievement(key, status) for key, status in self.achievements.items()}
        
        self._print("Achievements")
        self._print("")
        
        for key, text in readable_results.items():
            if text == "hannah_completed":
                if self.achievements["hannah_completed"]: text = hannah_completed
                else: text = None
            if text != None: self._print(f"{text}")
            
        self.scroll_offset = max(0, len(self.line_surfs) - self._visible_count())


    def _print_about(self):
        self.heading = "About Mati"
        self._print("")
        self._print("                Mathematic and Tactic Intelligence")
        self._print("Mati is short for                                       but it is now more.", size = "small")
        self._print("")
        self._print("The reason for the name and for the whole game, is an simple algorithem.", size = "small")
        self._print("This algorithem return a full grid, even today.", size = "small")
        self._print("But now it is quite more than just the game with his algorithem.", size = "small")
        self._print("You can visit a termianl, find easter eggs, see you past games, ", size = "small")
        self._print("export them as mp4 video files and more.", size = "small")
        self._print("")
        self._print("So I hope you enjoy the game and the many features it have. ;-)", size = "small")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("Created by: Janosch Klawatsch")
        self._print("")


    def _print_settings(self): # Print the current settings
        self.heading = "Settings"
        self._print("")
        self._print(f"Save Played: {'Yes' if self.settings['save_history'] else 'No'}")
        self._print(f"Show Timer:  {'Yes' if self.settings['timer_enabled'] else 'No'}")
        if self.settings["timer_enabled"]:
            self._print(f"  Milliseconds: {'Yes' if self.settings['timer_ms'] else 'No'}")
        self._print(f"Sound: {'Yes' if self.settings['sound_enabled'] else 'No'}")
        self._print(f"Terminal Sound: {'Yes' if self.settings.get('terminal_sound_enabled', True) else 'No'}")
        self._print(f"Keyboard Navigation: {'Yes' if self.settings['alt_control'] else 'No'}")
        self._print(f"Live Clock: {'Yes' if self.settings['live_clock_enabled'] else 'No'}")
        self._print(f"Ultra Timer: {'Yes' if self.settings['ultra_timer_enabled'] else 'No'}")
        if self.settings["ultra_timer_enabled"]:
            self._print(f"  Ultra Milliseconds: {'Yes' if self.settings['ultra_timer_ms'] else 'No'}")
        self._print(f"Live Clock Terminal: {'Yes' if self.settings['ultra_timer_show_clock'] else 'No'}")
        self._print("")
        
        
    def _print_history(self, active_filters = [], active_sort = ["newest"]): # Print the last played matches
        self._cleared()
        entries = ps.list_history_meta()
        entries_use = entries
        
        self.heading = "History"
        self._print("     Timestamp       |  Size Modus  |  Played Time  |  Help by ")
        self._print("---------------------|--------------|---------------|----------")
        
        if "4x4" in active_filters:
            entries_use = [entry for entry in entries_use if entry["size"] == 4]
            active_filters.remove("4x4") 
        elif "5x5" in active_filters:
            entries_use = [entry for entry in entries_use if entry["size"] == 5]
            active_filters.remove("5x5")
        elif "6x6" in active_filters:
            entries_use = [entry for entry in entries_use if entry["size"] == 6]
            active_filters.remove("6x6")
        elif "7x7" in active_filters:
            entries_use = [entry for entry in entries_use if entry["size"] == 7]
            active_filters.remove("7x7")
            
        if "ultra" in active_filters:
            entries_use = [entry for entry in entries_use if entry["ultra"]]
            active_filters.remove("ultra")
        elif "normal" in active_filters:
            entries_use = [entry for entry in entries_use if entry["ultra"] is False]
            active_filters.remove("normal")
            
        if "no_hints" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] == 0]
            active_filters.remove("no_hints")
        elif "one_hint" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] == 1]
            active_filters.remove("one_hint")
        elif "two_hints" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] == 2]
            active_filters.remove("two_hints")
        elif "three_hints" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] == 3]
            active_filters.remove("three_hints")
        elif "under_hints_two" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] <= 1]
            active_filters.remove("under_hints_two")
        elif "under_hints_three" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] <= 2]
            active_filters.remove("under_hints_three")
        elif "hints_used" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] >= 1]
            active_filters.remove("hints_used")
        elif "over_hints_one" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] >= 2]
            active_filters.remove("over_hints_one")
            
        for enties in active_filters:
            if "under_time" in enties:
                enti = enties.split("me")[1]
                entries_use = [entry for entry in entries_use if entry["play_time"] <= int(enti)]
            elif "over_time" in enties:
                enti = enties.replace("over_time", "")
                entries_use = [entry for entry in entries_use if entry["play_time"] >= int(enti)]
        
        if active_sort:
            def sort_key(entry):
                keys = []
                for s in active_sort:
                    match s:
                        case "smallest":
                            keys.append(entry.get("size", 0))
                            
                        case "biggest":
                            keys.append(-entry.get("size", 0))
                            
                        case "ultra":
                            keys.append(not bool(entry.get("ultra")))
                            
                        case "normal":
                            keys.append(bool(entry.get("ultra")))
                            
                        case "hints_up":
                            keys.append(entry.get("hints_used", 0))
                        
                        case "hints_down":
                            keys.append(-entry.get("hints_used", 0))
                            
                        case "fastest":
                            keys.append(entry.get("play_time", 0))
                        
                        case "slowest":
                            keys.append(-entry.get("play_time", 0))
                            
                        case "newest":
                            keys.append(entry.get("filename", ""))
                        
                        case "oldest":
                            keys.append(entry.get("filename", ""))
                return tuple(keys)
            
            is_reverse = "newest" in active_sort
            entries_use.sort(key=sort_key, reverse=is_reverse)
            
        
        
        if not entries:
            self._print("No matches saved yet.")
            return 
        elif not entries_use:
            self._print("No matches fitting your filters.")
            return
        
        i = 0
        for entry in entries_use:
            mode = "Ultra " if entry.get("ultra") else "Normal"
            self._print(f"{entry['label']}  |  {entry['size']}x{entry['size']} {mode}  |  {self._fmt_time(entry['play_time'])}  |  {entry['hints_used']} {'hint ' if entry['hints_used'] == 1 else 'hints'}") # Game info
            i += 1
        self._print("")
        
        # self.scroll_offset = max(0, len(self.line_surfs) - self._visible_count())
        self.number_of_entries = i
        
        self._print("")
        self._print(f"This list has {self.number_of_entries} entries.")
        self._print("And are reached threw these filters:")
        for filter in self.active_filters:
            self._print(filter)
            
        self.scroll_offset = max(0, len(self.line_surfs) - self._visible_count())
            
    
    def _help_menu(self, state): # Draw the help menu
        if state == 1: # If in the terminal
            self._print("What do you need help with?")
            self._print("")
            self._print("  help overall  - general terminal commands")
            self._print("  help game     - commands to start or open a game")
            self._print("  help ingame   - commands available while playing an ultra match")
            self._print("  help settings - commands you can use in the settings")
            self._print("")
        elif state == 2: # If in the ultra game modus
            self._print("close  - Leave the terminal.") # Close command
            self._print("return - Return to the terminal.") # Return command
            self._print("time   - Get the time of your location.") # time command
            self._print("play time / pt - Get the time of the match.") # pt command
            self._print("play time long / ptl - Get the time with ms.")
            self._print("new    - Start a new ultra match with same size.") # New command
            self._print("hint   - Get a hint for the game.") # Hint commmand
            self._print("crw - column row right(r)/left(l) [l selects; r marks].") # Declare the clicks


    def _help_overall(self):
        self._print("close         - Leave the terminal.")
        self._print("quit          - Leave the whole game.")
        self._print("time          - Get the time of your location.")
        self._print("clear         - Refresh the screen.")
        self._print("stats         - Show your stats.")
        self._print("achievements  - Show your achievements.")
        self._print("history       - Open the graphical history view.")
        self._print("history text  - Show your recent matches right here.")
        self._print("settings      - Open the graphical settings view.")
        self._print("settings text - Show your current settings right here.")
        self._print("about         - Open the graphical about screen.")
        self._print("about text    - Show the about info right here.")
        
        
    def _help_game(self):
        self._print("play 4x4 / p 4x4 - Start a normal 4x4 game.")
        self._print("play 5x5 / p 5x5 - Start a normal 5x5 game.")
        self._print("play 6x6 / p 6x6 - Start a normal 6x6 game.")
        self._print("play 7x7 / p 7x7 - Start a normal 7x7 game.")
        self._print("play ultra 4x4 / pu 4x4 - Start an ultra game in 4x4.")
        self._print("play ultra 5x5 / pu 5x5 - Start an ultra game in 5x5.")
        self._print("play ultra 6x6 / pu 6x6 - Start an ultra game in 6x6.")
        self._print("play ultra 7x7 / pu 7x7 - Start an ultra game in 7x7.")
        
    
    def _help_settings(self):
        self._print("change 'setting name' to 'Yes/No'")
        self._print("   It change the setting to the given value.")
        self._print("change 'setting name'")
        self._print("   Changes the value to the other.")
        self._print("return    - Leave the settings.")
        self._print("close     - Leave the whole game.")
        self._print("open real - Open the graphical version of the settings.")
        

    def _print_board(self): # How to draw the board
        self._cleared() # Give command to clear
        game = self.ultra_game # Load the game
        n = game.n # Get n
        
        self.heading = f"Ultra Game in {n}x{n}"
        
        grid = game.grid
        user_sel = game.user_sel
        user_dimmed = game.user_dimmed
        row_sums = game.row_sums
        col_sums = game.col_sums
        
        row_fulfilled = [
            sum(val for val, sel in zip(grid[r], user_sel[r]) if sel) == row_sums[r]
            for r in range(n)
        ] # Get the fulfilled rows, with the premade rows
        col_fulfilled = [
            sum(grid[r][c] for r in range(n) if user_sel[r][c]) == col_sums[c]
            for c in range(n)
        ] # Get the fulfilled columns
            
        self._print("") # An empty line
        self._print("")
        
        col_marks = [f"{col_sums[c]:02}{'s' if col_fulfilled[c] else ' '}" for c in range(n)] # Defines the col sums mark
        self._print("      " + " | ".join(col_marks)) # Show them
        self._print("     " + "─ " * (n * 3 - 1)) # An empty line
        
        for r in range(n): # For every row
            rf = row_fulfilled[r]
            row_g = grid[r]
            row_s = user_sel[r]
            row_d = user_dimmed[r]
            
            cells = [] # Empty cell list
            for c in range(n): # For every column
                if row_s[c]:
                    prefix = "*"
                elif row_d[c] or rf or col_fulfilled[c]:
                    prefix = "~"
                else:
                    prefix = " "
                cells.append(f"{prefix}{row_g[c]}") # Add the cell to the others
                
            mark = "s" if rf else " " # Defines the mark for the sums
            self._print(f"{row_sums[r]:02}{mark} | " + "  | ".join(cells)) # Defines a row
            
        self._print("")
            
        
        if game.won:
            self._print("Celebration! You have won.") # Make clear, that the user has won
            self._print("") # An empty line
        
        
    def _clear(self): # To clear the screen
        self.lines.clear() # Clear the screen come in
        self.line_surfs.clear() # Clear the screen
        self.input_buffer = "" # Clear buffer
        self.cursor_pos = 0 # jump to start
        self.heading = "Mati Terminal" # Set heading
        
        
    def _cleared(self): # Without heading
        self.lines.clear() # Clear the screen come in
        self.line_surfs.clear() # Clear the screen
        self.input_buffer = "" # Clear buffer
        self.cursor_pos = 0 # Jump to start


    def draw(self): # Draw something on the screen
        screen = w.get_screen() # Load the screen
        screen.fill(con.LIGHT_BLACK) # Set the bg color
        
        visible = self._visible_count() # Gets the number of visible lines
        surfs = list(self.line_surfs) # get the lines
        end = len(surfs) - self.scroll_offset # last seen
        start = max(0, end - visible) # first seen
        visible_surfs = surfs[start:end] # Cut of not visibles
        
        y = 50 # defines the line y
        for surf in visible_surfs: # For every visible line
            screen.blit(surf, (20, y))
            y += con.LINE_HEIGHT # Get the y from the next line
        
        before = self.input_buffer[:self.cursor_pos] # text left of cursor
        after = self.input_buffer[self.cursor_pos:] # text right of cursor
        prefix_surf = self._font.render("> " + before, True, con.WHITE)    
        screen.blit(prefix_surf, (20, con.HEIGHT - 34)) # Get the thing on the screen
        cursor_x = 20 + prefix_surf.get_width() # where the cursor is
        underscore_w = self._font.size("_")[0] # widht of cursor glyph
        
        if (pg.time.get_ticks() // 500) % 2 == 0: # the blink effect
            cursor_surf = self._font.render("_", True, con.WHITE) # the cursor
            screen.blit(cursor_surf, (cursor_x, con.HEIGHT - 34)) # draw it
        after_surf = self._font.render(after, True, con.WHITE)
        screen.blit(after_surf, (cursor_x + underscore_w, con.HEIGHT - 34)) # draw it
        
        surfer = self._font.render(self.heading, True, con.TEXT_COLOR_2)
        screen.blit(surfer, (20, 20))
        screen.blit(surfer, (20, 20))
        
        if self.settings["ultra_timer_enabled"]: self._draw_ultra_timer_overlay(screen)
        if self.settings["ultra_timer_show_clock"]: self._draw_ultra_clock(screen)
        
        
    def _draw_ultra_clock(self, screen):
        line = f"{dt.now().strftime('%H:%M:%S')}"
        surf = self._font.render(line, True, con.TEXT_COLOR_2)
        screen.blit(surf, (con.WIDTH - surf.get_width() - 20, 20))
        screen.blit(surf, (con.WIDTH - surf.get_width() - 20, 20))
                
        
    def _draw_ultra_timer_overlay(self, screen): 
        game = self.ultra_game
        if game is None:
            return
        
        elapsed = self.o_time if game.won else (pg.time.get_ticks() - self.timer)
        ms = elapsed % 1000
        seconds = (elapsed // 1000) % 60
        minutes = elapsed // 60000
        if minutes:
            time_str = f"{minutes}:{seconds:02}:{ms:03}min" if game.ultra_timer_ms else f"{minutes}:{seconds:02}min"
        else:
            time_str = f"{seconds}:{ms:03}s" if game.ultra_timer_ms else f"{seconds}s"

        line = f"Game Time: {time_str}"
        
        surf = self._font.render(line, True, con.TEXT_COLOR_2)
        screen.blit(surf, (20, 50))
        screen.blit(surf, (20, 50))
        