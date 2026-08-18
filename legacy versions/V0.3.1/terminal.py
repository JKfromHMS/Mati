### Mati (Mathematics and tactic intelligence) ###
### V0.3.1 Beta V1.0.15 ###
### Author: Janosch Klawatsch, 22.07.2026 ###
### terminal file V0.3.4 ###

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

### Own ###
import config as con     # For the constants
import widgets as w      # To have widgets
from game import Game    # For the game parameters
import persistence as ps # To read the statistics

### -Functions- ###
class Terminal: # The hole terminal
    def __init__(self, sounds): # Every class needs an init
        self.sounds = sounds # Load sounds
        self.lines = [] # Terminal is empty
        self.input_buffer = "" # The player had not a word tipped
        self.ultra_game = None # Start in the normal terminal
        self.should_close = False # That it stays open
        self.next_state = None # State to switch to after leaving terminal
        self.next_game = None # Game to start after leaving terminal
        self._pending_resume_n = None # Set size paused ultra game
        self._font = pg.font.SysFont("couriernew", 19) # The font for the terminal
        self._print("Mati Terminal") # Welcome Message
        self._print("") # An empty line
        
    def _print(self, text=""): # Prints a given text into the terminal
        self.lines.append(text) # Add the line to the save
        if len(self.lines) > con.MAX_LINES: # If there are to much lines
            self.lines = self.lines[-con.MAX_LINES:] # Delete the last line
            
    def handle_key(self, event): # Handle the pressed keys
        if event.key == pg.K_RETURN: # If the entry is finished
            self._submit() # Make what said
        elif event.key == pg.K_BACKSPACE: # If mistipped
            self.input_buffer = self.input_buffer[:-1] # Delete last letter
        elif event.unicode and event.unicode.isprintable() and len(self.input_buffer) < con.INPUT_MAX_LEN: # Check if an other key is pressed and the press is valid
            self.input_buffer += event.unicode # Show the pressed key
            
    def _submit(self): # Do a command
        command = self.input_buffer.strip() # Load the command
        if not command: # If wrong alert
            return # do nothing
        self._print(f"> {command}") # Print command to the screen
        self._handle_command(command) # Let the command be done
        self.input_buffer = "" # Clear the current line after execution
        
    def _handle_command(self, command): # Handles the commands
        cmd = command.lower() # Make big and small leter version does not count
        if cmd == "close": # If in the normal view and want to close
            if self.ultra_game is not None: # If the player is playing
                self.ultra_game.stash_current_game(o_time=pg.time.get_ticks() - self.timer)
            self.next_state = "MENU"
            self.should_close = True # Say it should be closed
            self._clear() # Give command to clear
            self._print("Terminal is getting closed") # Say the user what happend, if it takes long
            return # task is done

        
        if self.ultra_game is not None: # If in the game mode
            self._handle_game_command(cmd) # Say handle the ingame command
            return # task is done
        
        if cmd == "jay loves":
            self.next_state = "HANNAH"
            self.should_close = True
            self._clear()
            return # task is done
        
        if cmd == "history": # Leave terminal to history
            self.next_state = "HISTORY" # Set next state
            self.should_close = True # Say the game it should close the terminal
            self._clear() # Clear the screen
            self._print("Leaving terminal to history.") # If the programm got slow, to explain what is happening.
            return # task is done
            
        if cmd == "settings": # Leave terminal to settings
            self.next_state = "SETTINGS" # Set next state
            self.should_close = True # Say the game it should close the terminal
            self._clear() # Clear the screen
            self._print("Leaving terminal to settings.") # If the programm got slow, to explain what is happening.
            return # task is done
        
        if cmd == "about": # Leave terminal to about
            self.next_state = "ABOUT" # Set next state
            self.should_close = True # Say the game it should close the terminal
            self._clear() # Clear the screen
            self._print("Leaving terminal to about.") # If the programm got slow, to explain what is happening
            return # task is done

        if cmd.startswith("p "): # To use les system ressources
            if cmd in ("play 4x4", "p 4x4"): # normal 4x4
                self.next_game = (4, False) # let match start
            elif cmd in ("play 5x5", "p 5x5"): # normal 5x5
                self.next_game = (5, False) # let match start
            elif cmd in ("play 6x6", "p 6x6"): # normal 6x6
                self.next_game = (6, False) # let match start
            elif cmd in ("play 7x7", "p 7x7"): # normal 7x7
                self.next_game = (7, False) # let match start
            else:
                self.next_game = None # Unvalid size or command
            if self.next_game is not None: # If valid
                self.next_state = "PLAY" # Set next state
                self.should_close = True # Say the game it should close the terminal
                self._clear() # Clear the screen
                self._print(f"Leaving terminal to play {self.next_game[0]}x{self.next_game[0]}.") # If the programm got slow, to explain what is happening
                return # task is done
        
        if self._pending_resume_n is not None: # While desicion is made
            n = self._pending_resume_n # The written size
            if cmd in ("continue", "c"): # If the player want to continue
                self.ultra_game = Game(self.sounds) # Load the sounds
                self.ultra_game.resume_paused(n, True) # Restore the paused match
                self.timer = pg.time.get_ticks() - self.ultra_game.play_time # Keep the timer
                self._pending_resume_n = None # Decision made
                self._clear() # Give command to clear
                self._print("Round continued.") # Say it the user
                self._print_board() # Show the board
            elif cmd in ("new", "n"): # If the player want a new match
                self.ultra_game = Game(self.sounds) # Load the new game
                self.ultra_game.discard_and_start(n, True) # Throw the paused round away
                self.timer = pg.time.get_ticks() # Get the time
                self._pending_resume_n = None # Desicion made
                self._print(f"Starting round in {n}x{n}") # Print what is happening
                self._print_board() # Print the board
                return # task is done
            else: # Anything else
                self._print("Please type 'continue' or 'new'.")
                return # task is done
        
        if cmd == "help": # If the player want help
            self._clear() # Clear the screen
            self._help_menu(state=1) # Draw the help menu
            return # task is done
        
        if cmd == "quit": # User want to quit the game
            pg.quit()  # End the game
            sys.exit() # End the programm
            return # In case of a failure do nothing more
        
        if cmd == "clear": # User want an empty screen
            self._clear() # Say the screen should be cleared
            return # task is done
        
        if cmd == "time": # If the user want to now the time
            self._print(f"    The current time is: {dt.now().strftime("%H:%M:%S")}") # Give the time
            return # task is over
        
        if cmd == "stats": # If the player want to see his stats
            self._clear() # Clear the screen
            self._print_stats() # Show the stats
            return # task is done
        
        if cmd.startswith("p"): # To use less system capacity
            if cmd == "play ultra 4x4" or cmd == "pu 4x4": # If the player want to play 4x4
                self._start_ultra(4) # Start an ultra game in 4x4
                return # task is done
            elif cmd == "play ultra 5x5" or cmd == "pu 5x5": # If the player want to play 5x5
                self._start_ultra(5) # Start an ultra game in 5x5
                return # task is done
            elif cmd == "play ultra 6x6" or cmd == "pu 6x6": # If the player want to play 6x6
                self._start_ultra(6) # Start an ultra game in 6x6
                return # task is done
            elif cmd == "play ultra 7x7" or cmd == "pu 7x7": # If the player want to play 4x4
                self._start_ultra(7) # Start an ultra game in 7x7
                return # task is done
            
        self._print(f"Unknown Command: {command}") # If the code goes until here, the command was not valid
        
    def _start_ultra(self, n): # Starts a new ultra match
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
        self._print_board() # Print the board
        self.timer = pg.time.get_ticks() # Get the time
        
    def _handle_game_command(self, cmd): # Handle commands in game mode
        game = self.ultra_game # Load the game
        
        if cmd == "help": # If the player want help
            self._print_board() # Clear the screen
            self._help_menu(state=2) # Draw the help menu
            return # task is done
        
        if cmd == "return": # If the user want to go back
            game.stash_current_game(o_time=pg.time.get_ticks() - self.timer) # Save the unfinished game
            self.ultra_game = None # No game is running anymore
            self._clear() # Give command to clear
            return # task is over
        
        if cmd == "hint": # If the user want a hint
            if game.won: # If the user has won
                self._print("You have already won.") # Say it to the user
            else:
                before = game.hints_left # Load the number of hints left
                game.use_hint(o_time=pg.time.get_ticks() - self.timer, ultra=True) # Find an hint
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
        
        if cmd == "play time" or cmd == "pt": # If the user want to now the time in the round
            self._print_board() # Redraw the board (Makes sure that not multible commands block the view)
            if not game.won: self.tim = pg.time.get_ticks() - self.timer # Get the difference between start and now
            ms = self.tim % 1000 # Get the miliseconds
            seconds = self.tim // 1000 % 60 # Get the seconds
            minutes = self.tim // 60000 % 60 # Get the minutes
            if minutes < 1: # If the game duration is under a minute
                self.ingame_time = f"{seconds:2}:{ms:03}s" # The full time
            elif minutes > 1 and game.won:
                self.ingame_time = f"{minutes:02}:{seconds:02}:{ms:03}min" # The full time
            else:
                self.ingame_time = f"{minutes:02}:{seconds:02}min" # The full time
            self._print(f"> {cmd}") # Make it look more equal 
            self._print(f"    Time in Game: {self.ingame_time}") # The message
            return # task is done
        
        if cmd == "time": # If the user want to now the time
            self._print_board() # Draw the board
            self._print(f"> {cmd}") # Make it look more equal
            self._print(f"    The current time is: {dt.now().strftime("%H:%M:%S")}") # Give the time
            return # task is over
        
        parsed = self._parse_action(cmd, game.n) # Find out if the command was a command for clicks
        if parsed is None: # If is not
            self._print_board() # Print the board
            self._print(f"> {cmd}") # Make it look more equal
            self._print(f"Unknown command: {cmd}") # Say it to the user
            return # task is done
        
        if game.won: # If the player has won
            self._print("You have already won.") # Say it to the user
            return # task is done
        
        r, c, right_click = parsed # Load what was done
        game.click_cell(r, c, right_click=right_click, o_time=pg.time.get_ticks() - self.timer, ultra=True) # Let the game work the click
        self._print_board() # Print the new board
        if game.won: # If this action made the win
            self.tim = pg.time.get_ticks() - self.timer # The end time
            
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
        s = ms % 1000 # Get correct miliseconds remaining
        seconds = (ms // 1000) % 60 # Get whole seconds
        minutes = seconds // 60 # get minutes
        return f"{minutes}:{seconds:02}:{s:03}min" # Give the formated time
    
    def _print_stats(self): # Print the stats
        _, stats, _ = ps.load_settings_and_stats() # Reload stats
        self._print("Statistics") # Heading
        self._print("") # An empty line
        for mode_label, mode_key in (("Normal", "normal"), ("Ultra", "ultra")): # For each mode
            self._print(f"{mode_label:<6}") # Give the label
            for n in con.DIFFICULTIES: # For every grid size
                m = stats.get(str(n), {}).get(mode_key, {}) # Get the stats and from them the mode
                games = m.get("games", 0) # Number of played games
                best = m.get("best", None) # Best time
                total = m.get("total", 0) # Total played time
                avg = int(total / games) if games else None # Average time per game
                game_word = "game " if games == 1 else "games" # Get if it has to be games or game (with space to get to the same len)
                self._print(f"  {n}x{n}: {games} {game_word} | Best: {self._fmt_time(best)} | Avg: {self._fmt_time(avg)}") # One line each size with same len
        
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

    
    def _help_menu(self, state): # Draw the help menu
        if state == 1: # If in the terminal
            self._print("close - Leave the terminal.") # Close command
            self._print("quit  - Leave the whole game.") # Quit command
            self._print("time  - Get the time of your location.") # time command
            self._print("clear - Refresh the screen.") # clear command
            self._print("stats - Show your stats.") # Stats command
            self._print("history - Open the history view.") # history command
            self._print("settings - Open the settings view.") # settings command
            self._print("about - Open the about screen.") # about command
            self._print("play 4x4 / p 4x4 - Start a normal 4x4 game.") # normal 4x4 game
            self._print("play 5x5 / p 5x5 - Start a normal 5x5 game.") # normal 5x5 game
            self._print("play 6x6 / p 6x6 - Start a normal 6x6 game.") # normal 6x6 game
            self._print("play 7x7 / p 7x7 - Start a normal 7x7 game.") # normal 7x7 game
            self._print("play ultra 4x4 / pu 4x4 - Start an ultra game in 4x4.") # ultra 4x4 game
            self._print("play ultra 5x5 / pu 5x5 - Start an ultra game in 5x5.") # ultra 5x5 game
            self._print("play ultra 6x6 / pu 6x6 - Start an ultra game in 6x6.") # ultra 6x6 game
            self._print("play ultra 7x7 / pu 7x7 - Start an ultra game in 7x7.") # ultra 7x7 game
        elif state == 2: # If in the ultra game modus
            self._print("close  - Leave the terminal.") # Close command
            self._print("return - Return to the terminal.") # Return command
            self._print("time   - Get the time of your location.") # time command
            self._print("play time / pt - Get the time of the match.") # pt command
            self._print("new    - Start a new ultra match with same size.") # New command
            self._print("hint   - Get a hint for the game.") # Hint commmand
            self._print("crw - column row right(r)/left(l) [l selects; r marks].") # Declare the clicks

    def _print_board(self): # How to draw the board
        self._cleared() # Give command to clear
        game = self.ultra_game # Load the game
        n = game.n # Get n
        row_fulfilled = [
            sum(game.grid[r][c] for c in range(n) if game.user_sel[r][c]) == game.row_sums[r]
            for r in range(n)
        ] # Get the fulfilled rows
        col_fulfilled = [
            sum(game.grid[r][c] for r in range(n) if game.user_sel[r][c]) == game.col_sums[c]
            for c in range(n)
        ] # Get the fulfilled columns
        
        self._print("") # An empty line
        for r in range(n): # For every row
            cells = [] # Empty cell list
            for c in range(n): # For every column
                val = str(game.grid[r][c]) # Get the cell numbers
                if game.user_sel[r][c]: # If the user has the cell selected
                    val = "*" + val # Add a star in front of it
                elif game.user_dimmed[r][c] or (row_fulfilled[r] and not game.user_sel[r][c]) or (col_fulfilled[c] and not game.user_sel[r][c]): # If the user has dimmed
                    val = "~" + val # Add a minus in front of it
                else: 
                    val = " " + val # Add an empty for the same distance
                cells.append(val) # Add the cell to the others
            mark = "s" if row_fulfilled[r] else " " # Defines the mark for the sums
            self._print(f"{game.row_sums[r]:02}{mark} | " + "  | ".join(cells)) # Defines a row
                
        col_marks = [f"{game.col_sums[c]:02}{'s' if col_fulfilled[c] else ' '}" for c in range(n)] # Defines the col sums mark
        self._print("      " + " | ".join(col_marks)) # Show them
        self._print("") # An empty line
        if game.won:
            self._print("Celebration! You have won.") # Make clear, that the user has won
            self._print("") # An empty line
        
    def _clear(self): # To clear the screen
        self.lines = [] # Clear lines
        self.input_buffer = "" # Clear buffer
        self._print("Mati Terminal") # Set heading
        self._print("") # Add an empty row
        
    def _cleared(self): # Without heading
        self.lines = [] # Clear lines
        self.input_buffer = "" # Clear buffer

    def draw(self): # Draw something on the screen
        screen = w.get_screen() # Load the screen
        screen.fill(con.LIGHT_BLACK) # Set the bg color
        
        visible = max(1, (con.HEIGHT - 60) // con.LINE_HEIGHT) # Gets the visible lines
        visible_lines = self.lines[-visible:] # Cut of not visibles
        
        y = 20 # defines teh line y
        for line in visible_lines: # For every visible line
            surf = self._font.render(line, True, con.TEXT_COLOR_2) # Get te full line
            screen.blit(surf, (20, y)) # Get the line on the screen
            y += con.LINE_HEIGHT # Get the y from the next line
            
        cursor = "_" if (pg.time.get_ticks() // 500) % 2 == 0 else " " # The lighteffect of the cursor
        prompt_surf = self._font.render("> " + self.input_buffer + cursor, True, con.WHITE) # Get the things to show
        screen.blit(prompt_surf, (20, con.HEIGHT - 34)) # Get the thing away