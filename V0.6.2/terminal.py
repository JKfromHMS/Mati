### Mati (Mathematics and tactic intelligence) ###
### V0.6.2 (Beta V1.0.23) ###
### Author: Janosch Klawatsch, 2026-08-30 ###
### terminal file V0.6.3 ###

### Structure-Plan ###
# - audio.py - Sound generation #
# - config.py - Constants #
# - export.py - Video creation and saving #
# - game.py - Main game handling #
# - lang.py - Translation logic #
# - level.py - Level generation and win checking #
# - main.py - Entry point and main loop #
# - persistence.py - Saving and loading .mati files #
# - replay.py - Rebuilding games #
# - screens.py - Screen construction #
# - terminal.py - Terminal handling #
# - widgets.py - Drawing functions #

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
        self.tro = False  # Fast-input mode: auto-submit short commands
        self.active_sort = []
        self.help_mode = None
        self.achievements_mode = None
        self._repeat_key = None
        self._repeat_next_time = 0 
        
        
    def _play_terminal_sound(self, sound): # Plays a sound for the terminal itself, independent from the normal game's sound setting
        if self.settings.get("terminal_sound_enabled", True) and self.sounds and self.sounds.available and sound: # Only if wanted and possible
            volume = self.settings.get("terminal_volume", 1.0)
            sound.set_volume(max(0.0, min(1.0, volume)))
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


    def _repeatable_action(self, key, mod=None):
        if key in (pg.K_UP, pg.K_DOWN) and mod and not self.ultra_game: # to scroll the screen
            self.scroll(3 if key == pg.K_UP else -3) # move up or down
            return
        
        match key:
            case pg.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.input_buffer = self.input_buffer[:self.cursor_pos - 1] + self.input_buffer[self.cursor_pos:]
                    self.cursor_pos -= 1
                    self._history_index = None
                    
            case pg.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
                
            case pg.K_RIGHT:
                self.cursor_pos = min(len(self.input_buffer), self.cursor_pos + 1)
                
            case pg.K_UP:
                if history := self._active_history():
                    if self._history_index is None:
                        self._history_index = len(history) - 1
                    else:
                        self._history_index = max(0, self._history_index - 1)
                    self.input_buffer = history[self._history_index]
                    self.cursor_pos = len(self.input_buffer)
                    
            case pg.K_DOWN:        
                history = self._active_history()
                if history and self._history_index is not None and self._history_index + 1 < len(history):
                    self._history_index += 1
                    self.input_buffer = history[self._history_index]
                else:
                    self.input_buffer = ""
                    self._history_index = None
                self.cursor_pos = len(self.input_buffer) # cursor goes to the end


    def handle_key(self, event): # Handle the pressed keys
        if event.key in (pg.K_UP, pg.K_DOWN) and (event.mod & (pg.KMOD_CTRL | pg.KMOD_META)) and not self.ultra_game: # to scroll the screen
            self.scroll(3 if event.key == pg.K_UP else -3) # move up or down
            return # task is done
        
        match event.key: # Since py 3.10 match case is possible for more speed
            case pg.K_RETURN: # If the entry is finished
                self._submit() # Work with the entry
                
            case pg.K_BACKSPACE | pg.K_LEFT | pg.K_RIGHT | pg.K_UP | pg.K_DOWN: # Delete last character
                self._repeatable_action(event.key)
                    
            case pg.K_DELETE: # delete the character right of the cursor
                if self.cursor_pos < len(self.input_buffer): # not at the end
                    self.input_buffer = self.input_buffer[:self.cursor_pos] + self.input_buffer[self.cursor_pos + 1:] # cut it of
                    self._history_index = None # in no list anymore
                        
            case pg.K_HOME: # Jump to the start
                self.cursor_pos = 0 # very start
                
            case pg.K_END: # Jump to the end
                self.cursor_pos = len(self.input_buffer) # very end
                    
            case _: # Any other key
                if event.unicode and event.unicode.isprintable() and len(self.input_buffer) < con.INPUT_MAX_LEN:
                    self._play_terminal_sound(self.sounds.tip if self.sounds else None) # A small keystroke sound
                    self.input_buffer = self.input_buffer[:self.cursor_pos] + event.unicode + self.input_buffer[self.cursor_pos:] # Insert at the cursor
                    self.cursor_pos += 1 # Move the cursor with the new character
                    self._history_index = None
                    # Auto-submit short commands when tro mode active and an ultra game is running
                    if getattr(self, "tro", False) and self.ultra_game:
                        buf = self.input_buffer.strip().lower()
                        # auto-submit single-letter pause/break commands
                        if buf in ("p", "b"):
                            self._submit()
                        # auto-submit 3-char coordinate commands like '12l' or '34r'
                        elif len(buf) == 3 and self._parse_action(buf, self.ultra_game.n):
                            self._submit()
            
            
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
            
            case "achievements":
                self._handle_achievements_command(c_cmd, command)
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
                self.help_mode = "help"
                self._help_menu() # Draw the help menu
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
                self._help_ingame()
                return
            
            case "helpsettings": # The setting commands
                self._clear()
                self._help_settings()
                return
            
            case "helphistory": # The history commands
                self._clear()
                self.help_mode = "history"
                self._help_history()
                return
            
            case "helphistoryfilter": # The history filters
                self._clear()
                self._help_history_filter()
                return
            
            case "helphistorysort": # The history filters
                self._clear()
                self._help_history_sort()
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
            
            case "achievementstext":
                self.terminal_mode = "achievements"
                self._cleared()
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
            
        if self.help_mode == "help":
            match c_cmd: # py 3.10 method for efficient if else leave out
                case "overall": # The general terminal commands
                    self._clear()
                    self._help_overall()
                    return
                        
                case "game": # The help how to start a game
                    self._clear()
                    self._help_game()
                    return
                        
                case "ingame": # The commands ingame
                    self._clear()
                    self._help_ingame()
                    return
                        
                case "settings": # The setting commands
                    self._clear()
                    self._help_settings()
                    return
                        
                case "history": # The history commands
                    self._clear()
                    self.help_mode = "history"
                    self._help_history()
                    return
                        
                case "historyfilter": # The history filters
                    self._clear()
                    self._help_history_filter()
                    return
                        
                case "historysort": # The history filters
                    self._clear()
                    self._help_history_sort()
                    return
                
        elif self.help_mode == "history":
            match c_cmd:
                case "filter":
                    self._clear()
                    self._help_history_filter()
                    return
                
                case "sort":
                    self._clear()
                    self._help_history_sort()
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
        
        match cmd:
            case "help": # If the player want help
                self._print_board() # Clear the screen
                self._help_ingame() # Draw the help menu
                return # task is done
        
            case "return": # If the user want to go back
                self.o_time = pg.time.get_ticks() - self.timer
                game.stash_current_game(o_time=self.o_time) # Save the unfinished game
                self.ultra_game = None # No game is running anymore
                self._clear() # Give command to clear
                return # task is over
        
            case "hint": # If the user want a hint
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
        
            case "new": # If the player want a new game
                game.restart_same() # Restart the game
                self._clear() # Give command to clear
                self._print("Started new round") # Say it the user
                self._print_board() # Show the board to the player
                self.timer = pg.time.get_ticks() # Get the time
                return # Task is done
            
            case "tro": # Three reached on (auto submit if p or 3 chars tipped in)
                # Toggle tro (fast-input) mode: auto-submit short/coordinate inputs
                self.tro = not getattr(self, "tro", False)
                self._print(f"tro is now {'ON' if self.tro else 'OFF'}")
                return
            
        if cmd in {"continue", "c"}:
            if getattr(game, "paused", False):
                game.toggle_pause()
                # resumed: re-anchor terminal timer to game's play_time
                self.timer = pg.time.get_ticks() - self.o_time
                self._print_board()
                self._print("Round continued.")
            else:
                self._print("Round is not paused.")
            return
                
        if cmd in {"pause", "break", "b", "p"}:
            # Do not allow pausing if the player already won
            if getattr(game, "won", False):
                self._print("Round already won — cannot pause.")
                return
            # Toggle game pause state
            game.toggle_pause()
            if game.paused:
                # capture elapsed time at pause for display
                self.o_time = pg.time.get_ticks() - self.timer
                self._cleared()
                self._print("")
                self._print("=== PAUSED ===")
                self._print("Type 'continue' or 'c' to resume the round.")
            else:
                # resumed: re-anchor terminal timer to game's play_time
                self.timer = pg.time.get_ticks() - self.o_time
                self._print_board()
                self._print("Round continued.")
            return
        
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
            
    
    def _handle_achievements_command(self, c_cmd, command):
        if c_cmd == "return" and self.heading == "Achievements":
            self.terminal_mode = None
            self._clear()
        elif c_cmd == "return" and self.heading != "Mati Terminal":
            self.terminal_mode = None
            self._handle_command("achievementstext")
        elif c_cmd == "terminal":
            self.terminal_mode = None
            self._clear()
        elif c_cmd == "achiev" and self.achievements_mode not in (-1, 0, 9):
            self.terminal_mode = None
            self._clear()
            
            mode_mapping = {1: 4, 3: 5, 5: 6, 7: 7, 2: 4, 4: 5, 6: 6, 8: 7}
            current_mode = int(self.achievements_mode)

            if current_mode in mode_mapping:
                number = mode_mapping[current_mode]
    
                prefix = "play" if current_mode % 2 == 1 else "playultra"
    
                self._handle_command(f"{prefix}{number}x{number}")
                
            return
        
        elif c_cmd == "next" and self.achievements_mode not in (-1, 9):
            self._print_achievement_page(self.achievements_mode + 1)
            
        elif c_cmd == "back" and self.achievements_mode not in (-1, 0):
            self._print_achievement_page(self.achievements_mode - 1)
            
        
        elif self.heading == "Achievements":
            self._print_achievements(c_cmd)
            
        elif self.heading not in ("Mati Terminal", "Achievements"):
            self._print_achievements_help(command)
        
        
        
        
        
        
        
        
            
            
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
    
    
    def _normalize_filter_phrase(self, words):
        phrases = [
            ("under", "two", "hints"),
            ("under", "three", "hints"),
            ("over", "one", "hint"),
            ("hints", "used"),
            ("no", "hints"),
            ("one", "hint"),
            ("two", "hints"),
            ("three", "hints"),
            ("under", "time"),
            ("over", "time"),
        ] # Every word that can be single sorted right to avoid cutting up
        phrases.sort(key=len, reverse=True)
        
        # Convert to understandable for the programm
        for phrase in phrases:
            n = len(phrase)
            if tuple(words[:n]) == phrase:
                return "_".join(phrase), words[n:]
            
        return (words[0], words[1:]) if words else ("", [])
    
    
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
            words = cmd.removeprefix("filter ").split()
            cmdo, rest = self._normalize_filter_phrase(words) or (words[0] if words else "", [])
            if cmdo in ("under_time", "over_time") and rest: cmdo += rest[0]
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
                if i + 1 < len(raw_args) and f"{raw_args[i]}_{raw_args[i + 1]}" in ("hints_up", "hints_down", "size_up", "size_down", "played_time", "-hints_up", "-hints_down", "-size_up", "-size_down", "-played_time"):
                    if f"{raw_args[i]}_{raw_args[i + 1]}" == "played_time": tokens.append("fastest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "size_up": tokens.append("smallest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "size_down": tokens.append("biggest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "hints_used": tokens.append("hints_up")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "help_by": tokens.append("hints_up")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-help_by": tokens.append("hints_down")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-hints_used": tokens.append("hints_down")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-size_up": tokens.append("biggest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-size_down": tokens.append("smallest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-played_time": tokens.append("slowest")
                    else: tokens.append(f"{raw_args[i]}_{raw_args[i + 1]}")
                    i += 2
                else:
                    if raw_args[i] == "timestamp": tokens.append("newest")
                    elif raw_args[i] == "-timestamp": tokens.append("oldest")
                    elif raw_args[i] == "size": tokens.append("smallest")
                    elif raw_args[i] == "-size": tokens.append("biggest")
                    elif raw_args[i] == "-smallest": tokens.append("biggest")
                    elif raw_args[i] == "-biggest": tokens.append("smallest")
                    elif raw_args[i] == "-newest": tokens.append("oldest")
                    elif raw_args[i] == "-oldest": tokens.append("newest")
                    elif raw_args[i] == "-ultra": tokens.append("normal")
                    elif raw_args[i] == "-normal": tokens.append("ultra")
                    elif raw_args[i] == "mode": tokens.append("ultra")
                    elif raw_args[i] == "-mode": tokens.append("normal")
                    elif raw_args[i] == "modus": tokens.append("normal")
                    elif raw_args[i] == "-modus": tokens.append("ultra")
                    elif raw_args[i] == "-fastest": tokens.append("slowest")
                    elif raw_args[i] == "-slowest": tokens.append("fastest")
                    else: tokens.append(raw_args[i])
                    i += 1
                    
            # Prevent conflict opposites
            opposites = [
                {"newest", "oldest"},
                {"fastest", "slowest"},
                {"hints_up", "hints_down"},
                {"smallest", "biggest"},
                {"ultra", "normal"},
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
         
            
    def _parse_action(self, cmd, n): # Find out if it was an action
        if len(cmd) != 3: # Check if valid
            return None # Say not valid
        # It know need to accept two inputs and not just one
        orders = [
            self.settings.get("input_order_front", "action_column_row"),
            self.settings.get("input_order_back", "column_row_action"),
        ]
        for order in orders:
            pos = {"column": None, "row": None, "action": None}
            for i, part in enumerate(order.split("_")[:3]):
                pos[part] = i
                
            col_char, row_char, action_char = cmd[pos["column"]], cmd[pos["row"]], cmd[pos["action"]]
            if not col_char.isdigit() or not row_char.isdigit() or action_char not in ("l", "r"):
                continue
            c = int(col_char) - 1
            r = int(row_char) - 1
            if not (0 <= r < n) or not (0 <= c < n):
                continue
            return r, c, (action_char == "r")
        return None
    
    
    @staticmethod # The nect function does not need self
    def _fmt_time(ms, minute_width=1): # Forms ms to mins secs and remaining ms
        if ms is None: # Nothing to format
            return "-" + " " * (minute_width + 9) # Say so
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        s = ms % 1000 # Get correct miliseconds remaining
        return f"{minutes:>{minute_width}}:{seconds:02}:{s:03}min" # Give the formated time
    
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
        
        
    def _print_achievements_help(self, command):
        if self.achievements_mode < 0:
            self._print_achievements()
            text = "Mati Terminal"
        else:
            self._print_achievement_page(self.achievements_mode)
            text = "Achievements"
                
        self._print(f"Invalid command <{command}>")
        self._print("These are the valid commands:")
        self._print(f"   return - Go back to {text}")
        self._print("   terminal - Leave towards Mati Terminal")
        
        if self.achievements_mode not in (-1, 9):
            self._print("   next - Go to the next page.")
            
        if self.achievements_mode not in (-1, 0):
            self._print("   back - Go to the last page.")
        
        if self.achievements_mode not in (-1, 0, 9):
            self._print("   achiev - Start the game type you see the achievements of.")
    
        
    def _resolve_achievement_page(self, selector):
        text = (selector or "").strip().lower().replace("_", " ").replace("-", " ")
        if not text:
            return None

        normalized = " ".join(text.split())
        if normalized in {"overall", "general", "all"}:
            return 0

        page_count = len(con.ACHIEVEMENT_PAGES)
        if normalized.isdigit():
            index = int(normalized) - 1
            if 0 <= index < page_count:
                return index

        for n in con.DIFFICULTIES:
            size_token = str(n)
            if normalized == size_token:
                for i, page in enumerate(con.ACHIEVEMENT_PAGES):
                    title = page["title"].lower()
                    if f"{n}x{n}" in title:
                        return i

        for i, page in enumerate(con.ACHIEVEMENT_PAGES):
            title = page["title"].lower()
            aliases = {
                title,
                title.replace(" ", ""),
                title.replace(" ultra", ""),
                title.replace(" ", "_"),
                str(i + 1),
            }
            if title.startswith("general"):
                aliases.add("overall")
            if normalized in aliases:
                return i

        return None

    def _print_achievement_page(self, page_index):
        page = con.ACHIEVEMENT_PAGES[page_index]
        self._cleared()
        self.heading = f"Achievements - {page['title']}"
        self.achievements_mode = page_index
        for key in page["keys"]:
            unlocked = bool(self.achievements.get(key))
            label = con.ACHIEVEMENT_LABELS.get(key, key)
            status = "Unlocked" if unlocked else " Locked "
            self._print(f"  [{status}] {label}")
        self._print("")
        self.scroll_offset = max(0, len(self.line_surfs) - self._visible_count())

    def _print_achievements(self, selector=None):
        self._cleared()
        self.heading = "Achievements"
        self.achievements_mode = -1
        if selector is None:
            self._print("Choose a page by number or name:")
            for i, page in enumerate(con.ACHIEVEMENT_PAGES, start=1):
                self._print(f"    {i}. {page['title']}")
            self._print("")
            self._print("Examples: overall, 4x4 ultra, 5x5, 7")
            self.scroll_offset = max(0, len(self.line_surfs) - self._visible_count())
            return

        page_index = self._resolve_achievement_page(selector)
        if page_index is None:
            self._print(f"Unknown achievement page: {selector}")
            self._print("")
            self._print("Available pages:")
            for i, page in enumerate(con.ACHIEVEMENT_PAGES, start=1):
                self._print(f"  {i}. {page['title']}")
            self.scroll_offset = max(0, len(self.line_surfs) - self._visible_count())
            return

        self._print_achievement_page(page_index)


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
        elif "under_two_hints" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] <= 1]
            active_filters.remove("under_two_hints")
        elif "under_three_hints" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] <= 2]
            active_filters.remove("under_three_hints")
        elif "hints_used" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] >= 1]
            active_filters.remove("hints_used")
        elif "over_one_hint" in active_filters:
            entries_use = [entry for entry in entries_use if entry["hints_used"] >= 2]
            active_filters.remove("over_one_hint")
            
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
            
        minute_width = 3 if any((entry.get("play_time") or 0) >= 600_000 for entry in entries_use) else 1
        extra = minute_width - 1
        played_header = " " * (2 + extra // 2) + "Played Time" + " " * (2 + extra - extra // 2)
        played_sep = "-" * (15 + extra)
        self._print(f"     Timestamp       |  Size Modus  |{played_header}|  Help by ")
        self._print(f"---------------------|--------------|{played_sep}|----------")
        
        if not entries:
            self._print("No matches saved yet.")
            return 
        elif not entries_use:
            self._print("No matches fitting your filters.")
            return
        
        i = 0
        for entry in entries_use:
            mode = "Ultra " if entry.get("ultra") else "Normal"
            self._print(f"{entry['label']}  |  {entry['size']}x{entry['size']} {mode}  |  {self._fmt_time(entry['play_time'], minute_width)}  |  {entry['hints_used']} {'hint ' if entry['hints_used'] == 1 else 'hints'}") # Game info
            i += 1
        self._print("")
        
        self.number_of_entries = i
        
        self._print("")
        for filter in self.active_filters:
            if filter in active_filters: self.active_filters.remove(filter)
        self._print(f"This list has {self.number_of_entries} entries.")
        if self.active_filters and len(self.active_filters) != 1: self._print("And is reached threw these filters:")
        elif len(self.active_filters) == 1: self._print("And is reached threw this filters:")
        for i, filter in enumerate(self.active_filters):
            self._print(f"    {i + 1}    {filter}")
            
        self.scroll_offset = max(0, len(self.line_surfs) - self._visible_count())
            
    
    def _help_menu(self): # Draw the help menu
        self._print("What do you need help with?")
        self._print("")
        self._print("  help overall  - general terminal commands")
        self._print("  help game     - commands to start or open a game")
        self._print("  help ingame   - commands available while playing an ultra match")
        self._print("  help settings - commands you can use in the settings mode")
        self._print("  help history  - commands you can use in the history mode")
        self._print("")
        self._print("  help history filter - All possible filters")
        self._print("  help history sort - All possible sort options")
        

    def _help_overall(self):
        self._print("Terminal commands:")
        self._print("")
        self._print("   close              - Leave the terminal.")
        self._print("   quit               - Leave the whole game.")
        self._print("   time               - Get the time of your location.")
        self._print("   clear              - Refresh the screen.")
        self._print("   stats              - Show your stats.")
        self._print("   achievements       - Open the graphical achievements view.")
        self._print("   achievements text  - Show your achievements.")
        self._print("   history            - Open the graphical history view.")
        self._print("   history text       - Show your recent matches right here.")
        self._print("   settings           - Open the graphical settings view.")
        self._print("   settings text      - Show your current settings right here.")
        self._print("   advanced settings  - Open the graphical advanced settings view.")
        self._print("   about              - Open the graphical about screen.")
        self._print("   about text         - Show the about info right here.")
        
        
    def _help_game(self):
        self._print("Commands to start a match:")
        self._print("")
        self._print("   play 4x4 / p 4x4 - Start a normal 4x4 game.")
        self._print("   play 5x5 / p 5x5 - Start a normal 5x5 game.")
        self._print("   play 6x6 / p 6x6 - Start a normal 6x6 game.")
        self._print("   play 7x7 / p 7x7 - Start a normal 7x7 game.")
        self._print("")
        self._print("   play ultra 4x4 / pu 4x4 - Start an ultra game in 4x4.")
        self._print("   play ultra 5x5 / pu 5x5 - Start an ultra game in 5x5.")
        self._print("   play ultra 6x6 / pu 6x6 - Start an ultra game in 6x6.")
        self._print("   play ultra 7x7 / pu 7x7 - Start an ultra game in 7x7.")
        
        
    def _help_ingame(self):
        front = self.settings.get("input_order_front", "action_column_row")
        back = self.settings.get("input_order_back", "column_row_action")
        active_orders = [front, back]
        order_labels = {
            "column_row_action": "cra",
            "row_column_action": "rca",
            "action_column_row": "acr",
            "action_row_column": "arc",
        }
        
        self._print("Available Ultra game commands: ")
        self._print("    hint  - Get a hint for the game") # Hint commmand
        self._print("    p / b - Open the pause section (pause, break)")
        self._print("    c     - Return to the match   (continue)")
        self._print("    new   - Start a new Ultra match with same size") # New command
        self._print("")
        self._print("")
        self._print("Accepted input orders:")
        
        for order in active_orders:
            short = order_labels.get(order, order)
            label = order.replace("_", " ")
            self._print(f"    {short} - {label} [l selects; r marks]")
        
        self._print("")
        self._print("")
        self._print("Other available commands:")
        self._print("    close  - Leave the terminal") # Close command
        self._print("    return - Return to the terminal") # Return command
        self._print("    time   - Get the time of your location") # time command
        self._print("    pt     - Get the time of the match (play time)") # pt command
        self._print("    ptl    - Get the time with ms (play time long)")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("The input order can be changed in the advanced settings.")
    
    
    def _help_settings(self):
        self._print("Commands to change settings:")
        self._print("")
        self._print("    change 'setting name' to 'Yes/No'")
        self._print("    change 'setting name'")
        self._print("")
        self._print("")
        self._print("")
        self._print("Other Commands:")
        self._print("")
        self._print("    return    - Leave the settings")
        self._print("    close     - Leave the whole terminal")
        self._print("    open real - Open the graphical version of the settings")
        
    
    def _help_history(self):
        self._print("Commands to find a match:")
        self._print("    filter 'name'     - Removes all entries not matching")
        self._print("    sort by 'arg 1-4' - Sort for the given things in given order")
        self._print("")
        self._print("    sorted     - Reset sort to default (newest)")
        self._print("    unfiltered - Remove all filters")
        self._print("    reset      - Remove all filters and reset sort to default (newest)")
        self._print("")
        self._print("")
        self._print("")
        self._print("Other Commands:")
        self._print("    return    - Leave the history")
        self._print("    close     - Leave the whole terminal")
        self._print("    open real - Open the graphical version of history")
        
    
    def _help_history_filter(self):
        self._print("filter 'name' - Removes all entries not matching")
        self._print("")
        self._print("Filter options:")
        self._print("    grid size    - 4x4, 5x5, 6x6, 7x7")
        self._print("    game mode    - ultra, normal")
        self._print("    number hints - no hints, one hint, two hints, three hints")
        self._print("    range hints  - under two hints (0, 1), under three hints (0, 1, 2)")
        self._print("    range hints  - hints used (1, 2, 3), over one hint (2, 3)")
        self._print("    play time    - under_time/over_time 'time in ms' (longer/shorter)")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("(...) defines output, not additional input", size="small")
        
        
        
    def _help_history_sort(self):
        self._print("sort by 'arg 1-4' - Sort for the given things in given order")
        self._print("")
        self._print("Sorting options:")
        self._print("    timestamp - oldest, newest (timestamp)")
        self._print("    play time - fastest (played time), slowest")
        self._print("    grid size - smallest (size up, size), biggest (size down)")
        self._print("    game mode - ultra (mode), normal (modus)")
        self._print("    num hints - hints up (hints used, help by), hints down")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("")
        self._print("Explaination:")
        self._print("  Chain up to 4 sort parameters (e.g., 'sort by fastest smallest').")
        self._print("  Prefix with '-' to reverse the sort order (e.g., '-fastest').")
        self._print("  Sorts sequentially: 1st parameter, then 2nd to break ties, etc.")
        self._print("  Final ties are broken by the time parameter (or most recent game).")
        self._print("  Note: You can only use one time parameter.")
        

    def _print_board(self): # How to draw the board
        self._cleared() # Give command to clear
        game = self.ultra_game # Load the game
        # If the game is paused, show a clear paused message instead of the board
        if game and getattr(game, "paused", False):
            self.heading = f"Ultra Game in {getattr(game, 'n', '?')}x{getattr(game, 'n', '?')}"
            self._print("")
            self._print("=== PAUSED ===")
            self._print("Type 'continue' or 'c' to resume the round.")
            return
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
        
        if game.won:
            elapsed = self.o_time
        elif getattr(game, "paused", False):
            elapsed = getattr(self, "o_time", 0)
        else:
            elapsed = pg.time.get_ticks() - self.timer
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
        