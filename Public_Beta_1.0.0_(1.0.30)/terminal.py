"""In-game terminal offering commands to control and query Mati.
"""

import sys         
import pygame as pg 
from datetime import datetime as dt
from collections import deque 

import config as con    
import helpers
import widgets as w    
from game import Game   
import persistence as ps

class Terminal:
    def __init__(self, sounds): 
        self.sounds = sounds 
        self.lines = deque(maxlen=con.MAX_LINES) 
        self.line_surfs = deque(maxlen=con.MAX_LINES)
        self.input_buffer = ""
        self.cursor_pos = 0 
        self.scroll_offset = 0 
        self.ultra_game = None 
        self.terminal_mode = None 
        self.should_close = False 
        self.next_state = None 
        self.next_game = None 
        self._pending_resume_n = None 
        self._normal_history = [] 
        self._ultra_history = [] 
        self._history_index = None 
        self._font = pg.font.SysFont("couriernew", 19) 
        self.settings, self.stats, _, _, self.achievements = ps.load_settings_and_stats() 
        self.heading = "Mati Terminal"
        self.o_time = 0
        self.active_filters = []
        self.tro = False  
        self.active_sort = []
        self.help_mode = None
        self.achievements_mode = None
        self._repeat_key = None
        self._repeat_next_time = 0 
        
    def _play_terminal_sound(self, sound): 
        if self.settings.get("terminal_sound_enabled", True) and self.sounds and self.sounds.available and sound:
            volume = self.settings.get("terminal_volume", 1.0)
            sound.set_volume(max(0.0, min(1.0, volume)))
            sound.play() 
    
    def _print(self, text="", size="normal"):
        self.lines.append(text) 
        if size == "normal": self._font = pg.font.SysFont("couriernew", 19)
        elif size == "small": self._font = pg.font.SysFont("couriernew", 17)
        surf = self._font.render(text, True, con.TEXT_COLOR_2)
        self.line_surfs.append(surf) 
        self.scroll_offset = 0 
         
    def print_lines(self, lines): 
        for line in lines:
            self._print(line)

    def _visible_count(self):
        return max(1, (con.HEIGHT - 90) // con.LINE_HEIGHT)
    
    def scroll(self, delta): 
        if self.ultra_game:
            return 
        max_offset = max(0, len(self.line_surfs) - self._visible_count())
        self.scroll_offset = max(0, min(self.scroll_offset + delta, max_offset))    
      
    def _active_history(self): 
        return self._ultra_history if self.ultra_game else self._normal_history
    
    def _store_command(self, command): 
        if not command:
            return
        history = self._active_history()
        if not history or history[-1] != command:
            history.append(command)
        self._history_index = None

    def _repeatable_action(self, key, mod=None):
        if key in (pg.K_UP, pg.K_DOWN) and mod and not self.ultra_game: 
            self.scroll(3 if key == pg.K_UP else -3)
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
                self.cursor_pos = len(self.input_buffer)

    def handle_key(self, event): 
        if event.key in (pg.K_UP, pg.K_DOWN) and (event.mod & (pg.KMOD_CTRL | pg.KMOD_META)) and not self.ultra_game: 
            self.scroll(3 if event.key == pg.K_UP else -3) 
            return 
        
        match event.key:
            case pg.K_RETURN:
                self._submit() 
            case pg.K_BACKSPACE | pg.K_LEFT | pg.K_RIGHT | pg.K_UP | pg.K_DOWN: 
                self._repeatable_action(event.key)
            case pg.K_DELETE:
                if self.cursor_pos < len(self.input_buffer):
                    self.input_buffer = self.input_buffer[:self.cursor_pos] + self.input_buffer[self.cursor_pos + 1:]
                    self._history_index = None          
            case pg.K_HOME: 
                self.cursor_pos = 0 
            case pg.K_END: 
                self.cursor_pos = len(self.input_buffer)        
            case _: 
                if event.unicode and event.unicode.isprintable() and len(self.input_buffer) < con.INPUT_MAX_LEN:
                    self._play_terminal_sound(self.sounds.tip if self.sounds else None) 
                    self.input_buffer = self.input_buffer[:self.cursor_pos] + event.unicode + self.input_buffer[self.cursor_pos:]
                    self.cursor_pos += 1 
                    self._history_index = None
                    if getattr(self, "tro", False) and self.ultra_game:
                        buf = self.input_buffer.strip().lower()
                        if buf in ("p", "b"):
                            self._submit()
                        elif len(buf) == 3 and self._parse_action(buf, self.ultra_game.n):
                            self._submit()
            
    def close(self): # Allow to close the terminal from out of the terminal
        self._handle_command("close") 
             
    def _submit(self): 
        command = self.input_buffer.strip() 
        if not command: 
            return 
        self._play_terminal_sound(self.sounds.sub if self.sounds else None) 
        self._store_command(command)
        self._print(f"> {command}") 
        self._handle_command(command) 
        self.input_buffer = "" 
        self.cursor_pos = 0 
       
        
    def _handle_command(self, command):
        cmd = command.lower() 
        c_cmd = cmd.replace(" ", "") if " " in cmd else cmd
        
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
        
        match c_cmd:
            case "close": 
                if self.ultra_game: 
                    self.o_time = pg.time.get_ticks() - self.timer
                    self.ultra_game.stash_current_game(o_time=self.o_time)
                    self.next_state = "MENU"
                self.should_close = True 
                self._clear() 
                self._print("Terminal is getting closed") 
                return 
            
            case "time": 
                if self.ultra_game:
                    self._print_board() 
                    self._print(f"> {command}") 
                self._print(f"    The current time is: {dt.now().strftime("%H:%M:%S")}")
                return         
            
        if self.ultra_game: 
            self._handle_game_command(c_cmd, command) 
            return 
        
        if cmd == "jay loves":
            self.next_state = "HANNAH"
            self.should_close = True 
            self._clear() 
            return      
            
        if cmd == "export history" or cmd.startswith("export history ") or c_cmd.startswith("exporthistory"): 
            self._clear()
            arg = ""
            if cmd.startswith("export history "):
                arg = cmd.removeprefix("export history ").strip()
            elif c_cmd.startswith("exporthistory"):
                arg = c_cmd.removeprefix("exporthistory").strip()
            self._print_export_history(arg or None)
            return 
        
        if self.help_mode == "help":
            self.help_mode == None
            match c_cmd: 
                case "overall": 
                    self._clear()
                    self._help_overall()
                    return       
                case "game": 
                    self._clear()
                    self._help_game()
                    return        
                case "ingame": 
                    self._clear()
                    self._help_ingame()
                    return       
                case "settings": 
                    self._clear()
                    self._help_settings()
                    return       
                case "history": 
                    self._clear()
                    self.help_mode = "history"
                    self._help_history()
                    return       
                case "historyfilter":
                    self._clear()
                    self._help_history_filter()
                    return       
                case "historysort": 
                    self._clear()
                    self._help_history_sort()
                    return
                
        elif self.help_mode == "history":
            self.help_mode == None
            match c_cmd:
                case "filter":
                    self._clear()
                    self._help_history_filter()
                    return
                case "sort":
                    self._clear()
                    self._help_history_sort()
                    return

        match c_cmd:
            case "help": 
                self._clear()
                self.help_mode = "help"
                self._help_menu() 
                return 
            
            case "helpoverall": 
                self._clear()
                self._help_overall()
                return
            
            case "helpgame": 
                self._clear()
                self._help_game()
                return
            
            case "helpingame": 
                self._clear()
                self._help_ingame()
                return
            
            case "helpsettings": 
                self._clear()
                self._help_settings()
                return
            
            case "helphistory": 
                self._clear()
                self.help_mode = "history"
                self._help_history()
                return
            
            case "helphistoryfilter": 
                self._clear()
                self._help_history_filter()
                return
            
            case "helphistorysort": 
                self._clear()
                self._help_history_sort()
                return
            
            case "quit":
                pg.quit()  
                sys.exit()  
                return 
            
            case "clear": 
                self._clear() 
                return 
            
            case "stats": 
                self._clear()
                self._print_stats() 
                return 
            
            case "achievements":
                self.terminal_mode = "achievements"
                self._cleared()
                self._print_achievements()
                return
            
            case "about": 
                self.terminal_mode = "about"
                self._cleared()
                self._print_about()
                return
            
            case "settings": 
                self.terminal_mode = "settings"
                self._cleared()
                self._print_settings()
                return
            
            case "history":
                self.terminal_mode = "history"
                self._cleared()
                self._print_history()
                return

            case "activeplay": 
                self._cleared()
                self._print_active_play()
                return

            case "historyanalysis": 
                self._cleared()
                self._print_history_analysis()
                return
        
        if self._pending_resume_n: 
            is_continue = cmd in ("continue", "c") 
            is_new = cmd in ("new", "n") 

            if not (is_continue or is_new): 
                self._print("Please type 'continue' or 'new'.")
                return 

            n = self._pending_resume_n 
            self.ultra_game = Game(self.sounds) 
            self._pending_resume_n = None 

            if is_continue:
                self.ultra_game.resume_paused(n, True)
                self.timer = pg.time.get_ticks() - self.ultra_game.play_time 
                self._clear()
                self._print("Round continued.") 
            else:
                self.ultra_game.discard_and_start(n, True) 
                self.timer = pg.time.get_ticks() 
                self._print(f"Starting round in {n}x{n}") 

            self._print_board() 
            return 
        
        if state := con.NAVIGATE_COMMANDS.get(c_cmd): 
            self.next_state = state 
            self.should_close = True 
            self._clear()
            self._print(f"Leaving terminal to {state.lower()}.") 
            return 
        
        if size := con.PLAY_COMMANDS.get(c_cmd): 
            self.next_game = (size, False)
            self.next_state = "PLAY" 
            self.should_close = True 
            self._clear()
            self._print(f"Leaving terminal to play {size}x{size}.")           
            return 
            
        if size := con.ULTRA_COMMANDS.get(c_cmd): 
            self._start_ultra(size) 
            return 
            
        self._print(f"Unknown Command: {command}") # If the code goes until here, the command was not valid
          
    def _start_ultra(self, n):
        
        probe = Game(self.sounds)
        
        if probe._pause_key(n, True) in probe.paused_games: 
            self._clear() 
            self._pending_resume_n = n 
            self._print(F"Found a paused ultra round in {n}x{n}.") 
            self._print("Type 'continue' (c) to resume it or 'new' (n) to start over.") 
            return 
        
        self._clear() 
        self.ultra_game = probe 
        self.ultra_game.new_game(n, ultra=True, force_new=True) 
        self._print(f"Starting round in {n}x{n}") 
        self.timer = pg.time.get_ticks() 
        self._print_board()
        
    def _handle_game_command(self, cmd, command): 
        game = self.ultra_game 
        
        if command == "42": # Second little easter egg
            self._print_board()
            self._print("42 - The answer for everything except this game.")
            game.mark_achievement("42_found")
            return
        
        match cmd:
            case "help": 
                self._print_board()
                self._help_ingame() 
                return 
        
            case "return":
                self.o_time = pg.time.get_ticks() - self.timer
                game.stash_current_game(o_time=self.o_time) 
                self.ultra_game = None
                self._clear() 
                return 
        
            case "hint":
                if game.won:
                    self._print("You have already won.") 
                else:
                    self.o_time = pg.time.get_ticks() - self.timer
                    before = game.hints_left 
                    game.use_hint(o_time=self.o_time, ultra=True) 
                    game.stash_current_game(o_time=self.o_time)
                    self._print_board() 
                    self._print("No hints available." if game.hints_left == before else "Hint used.")
                    if game.won:
                        self._print("Celebration! You have won.")
                        self.tim = pg.time.get_ticks() - self.timer
                return 
        
            case "new":
                game.restart_same() 
                self._clear() 
                self._print("Started new round")
                self._print_board()
                self.timer = pg.time.get_ticks() 
                return 
            
            case "tro": # Three reached on (auto submit if p or 3 chars tipped in)
                self.tro = not getattr(self, "tro", False)
                self._print(f"tro is now {'ON' if self.tro else 'OFF'}")
                return
            
        if cmd in {"continue", "c"}:
            if getattr(game, "paused", False):
                game.toggle_pause()
                self.timer = pg.time.get_ticks() - self.o_time
                self._print_board()
                self._print("Round continued.")
            else:
                self._print("Round is not paused.")
            return
                
        if cmd in {"pause", "break", "b", "p"}:
            if getattr(game, "won", False):
                self._print("Round already won — cannot pause.")
                return
            game.toggle_pause()
            if game.paused:
                self.o_time = pg.time.get_ticks() - self.timer
                self._cleared()
                self._print("")
                self._print("=== PAUSED ===")
                self._print("Type 'continue' or 'c' to resume the round.")
            else:
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
        
        parsed = self._parse_action(cmd, game.n) 
        if parsed is None: 
            self._print_board()
            self._print(f"> {command}") 
            self._print(f"Unknown command: {command}") 
            return 
        
        if game.won: 
            self._print("You have already won.") 
            return 
        
        r, c, right_click = parsed 
        self.o_time = pg.time.get_ticks() - self.timer
        game.click_cell(r, c, right_click=right_click, o_time=self.o_time, ultra=True)
        game.stash_current_game(o_time=self.o_time)
        self._print_board() 
        if game.won: 
            self.tim = pg.time.get_ticks() - self.timer 
            
            
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

        elif c_cmd in ("analysis", "historyanalysis"):
            self._print_history_analysis()
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
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "play_time": tokens.append("fastest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "size_up": tokens.append("smallest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "size_down": tokens.append("biggest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "hints_used": tokens.append("hints_up")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "help_by": tokens.append("hints_up")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-help_by": tokens.append("hints_down")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-hints_used": tokens.append("hints_down")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-size_up": tokens.append("biggest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-size_down": tokens.append("smallest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-played_time": tokens.append("slowest")
                    elif f"{raw_args[i]}_{raw_args[i + 1]}" == "-play_time": tokens.append("slowest")
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
        if len(cmd) != 3:
            return None 
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
    
    @staticmethod
    def _fmt_time(ms, minute_width=1):
        if ms is None:
            return "-" + " " * (minute_width + 9)
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        s = ms % 1000 
        return f"{minutes:>{minute_width}}:{seconds:02}:{s:03}min"
    
    @staticmethod
    def _format_time(second):
        seconds = float(second)
        minutes = int(seconds // 60)
        rem_seconds = seconds % 60
        
        if rem_seconds.is_integer():
            rem_seconds = int(rem_seconds)
            
        if minutes > 0 and rem_seconds:
            return f"{minutes}min and {rem_seconds}s"
        elif minutes > 0:
            return f"{minutes}min"
        else:
            return f"{rem_seconds}s"
    
    @staticmethod
    def _fmt_duration(seconds): # Human readable duration like 45 s, 12 min or 2 h 14 min
        try:
            seconds = max(0, int(seconds))
        except (TypeError, ValueError):
            return "-"
        if seconds < 60:
            return f"{seconds} s"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} min"
        elif minutes % 60 == 0:
            return f"{minutes // 60}h"
        return f"{minutes // 60}h {minutes % 60}min"

    def _print_active_play(self): # Terminal overview of all matches with an active save state
        self._clear()
        _, _, paused, _, _ = ps.load_settings_and_stats()
        entries = []
        if self.ultra_game is not None: 
            entries.append((f"{self.ultra_game.n}x{self.ultra_game.n} (ultra)", None, {
                "saved_at": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                "play_time": pg.time.get_ticks() - getattr(self, "timer", pg.time.get_ticks()),
            }))
        for key in sorted(paused): 
            saved = paused[key]
            size, _, mode = key.partition("_")
            entries.append((f"{size}x{size} ({mode})", key, saved))
        if not entries:
            self._print("No matches with an active save state.")
            self._print("")
            self._print("0 active saves")
            return
        for name, save_id, saved in entries:
            self._print(f"Game: {name}")
            if save_id is None:
                self._print("    State: in session right now (ultra, in this terminal)")
            else:
                self._print(f"    Save: {save_id}")
            self._print(f"    Active time: {self._fmt_time(saved.get('play_time', 0))}")
            saved_at = saved.get("saved_at")
            if saved_at:
                try:
                    elapsed = (dt.now() - dt.strptime(saved_at, "%Y-%m-%d %H:%M:%S")).total_seconds()
                    self._print(f"    Last saved: {saved_at} ({self._fmt_duration(elapsed)} ago)")
                except ValueError:
                    self._print(f"    Last saved: {saved_at}")
            else:
                self._print("    Last saved: -")
            self._print("")
        self._print("-" * 36)
        self._print(f"{len(entries)} active saves")

    def _print_export_history(self, project_filter=None): 
        self._clear()
        history = ps._read_export_history()
        items = list(history.items())
        if project_filter: 
            needle = project_filter.lower()
            items = [
                (k, v) 
                for k, v in items 
                if needle in k.lower() or needle in str(
                    v.get("exported", "")
                ).lower()
            ]
        items.sort(key=lambda kv: str(kv[1].get("exported", "")), reverse=True) 
        if not items:
            if project_filter:
                self._print(f"No exports recorded for '{project_filter}'.")
            else:
                self._print("No exports have been recorded yet.")
            self._print("")
            self._print("0 exports recorded")
            return
        for name, entry in items:
            video = name.replace("_", " ").split(".")[0]
            self._print(f"Video: {video}")
            self._print(f"    Exported: {entry.get('exported', '-')}")
            self._print("    Settings:")
            self._print(f"        Quality: {entry.get('quality', '-')}")
            self._print(f"        Resolution: {entry.get('resolution', '-')}")
            self._print(f"        FPS: {entry.get('fps', '-')}")
            self._print("")
        self._print("-" * 36)
        self._print(f"{len(items)} exports recorded")

    @staticmethod
    def _median(values): # Median of a list of numbers
        vals = sorted(values)
        n = len(vals)
        if n == 0:
            return 0
        mid = n // 2
        if n % 2:
            return vals[mid]
        return (vals[mid - 1] + vals[mid]) / 2.0

    @staticmethod
    def _percentile(values, p): # Linear-interpolated percentile (p in 0..100)
        vals = sorted(values)
        if not vals:
            return 0
        k = (len(vals) - 1) * p / 100.0
        lo = int(k)
        hi = min(lo + 1, len(vals) - 1)
        frac = k - lo
        return vals[lo] * (1.0 - frac) + vals[hi] * frac

    @staticmethod
    def _mean(values):
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def _cv(values): # Coefficient of variation of a list
        if len(values) < 2:
            return 0.0
        m = sum(values) / len(values)
        if m <= 0:
            return 0.0
        var = sum((v - m) ** 2 for v in values) / len(values)
        return (var ** 0.5) / m

    @staticmethod
    def _fmt_short(ms): # Compact duration like 4.1 s, 2 m 05 s or 1 h 12 m
        try:
            ms = max(0, int(ms))
        except (TypeError, ValueError):
            return "-"
        seconds = ms / 1000.0
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = int(seconds // 60)
        rem = int(seconds % 60)
        if minutes < 60:
            return f"{minutes:2}min {rem:02d}s"
        return f"{(minutes // 60):2}h {minutes % 60}min"

    def _print_history_analysis(self):
        # Deep statistical analysis of the whole match history
        self._cleared()

        games = list(reversed(ps.list_history_meta()))  # Oldest -> newest
        total = len(games)

        def blank_lines():
            self._print("")
            self._print("")

        def cfg_of(g):
            return f"{g['size']}x{g['size']}" + (
                " Ultra" if g.get("ultra") else ""
            )

        def size_of(g):
            return f"{g['size']}x{g['size']}"

        def size_num(name):
            try:
                return int(name.split("x", 1)[0])
            except (ValueError, AttributeError):
                return 0

        def cfg_sort_key(name):
            return (
                size_num(name),
                1 if name.endswith(" Ultra") else 0,
                name
            )

        def trend_label(change):
            if change <= -20:
                return "Major improvement"
            if change <= -10:
                return "Improving"
            if change <= -5:
                return "Slight improvement"
            if change < 5:
                return "Stable"
            if change < 10:
                return "Slight decline"
            if change < 20:
                return "Declining"
            return "Major decline"

        def consistency_level(cv):
            if cv < 0.35:
                return "Low"
            if cv < 0.70:
                return "Moderate"
            return "High"

        def change_percent(current, previous):
            if previous <= 0:
                return None
            return (current - previous) / previous * 100.0

        # ------------------------------------------------------------------
        # Empty history
        # ------------------------------------------------------------------

        self._print("OVERVIEW")
        self._print("-" * 36)

        if total == 0:
            self._print("No games have been recorded yet.")
            blank_lines()
            self._print("Play some matches and come back for an analysis.")
            return

        # ------------------------------------------------------------------
        # Basic data preparation
        # ------------------------------------------------------------------

        durations = [g["play_time"] for g in games]
        total_ms = sum(durations)

        hints_games = sum(
            1 for g in games if g.get("hints_used", 0) > 0
        )

        cfg_games = {}
        size_games = {}

        for g in games:
            cfg = cfg_of(g)
            size = size_of(g)

            cfg_games.setdefault(cfg, []).append(g["play_time"])
            size_games.setdefault(size, []).append(g["play_time"])

        cfg_names = sorted(cfg_games, key=cfg_sort_key)
        size_names = sorted(size_games, key=size_num)

        # Cache statistics for every configuration.
        stats = {}

        for name in cfg_names:
            times = cfg_games[name]
            count = len(times)

            entry = {
                "times": times,
                "count": count,
                "total": sum(times),
                "median": self._median(times),
                "mean": self._mean(times),
                "min": min(times),
                "max": max(times),
            }

            if count >= 8:
                entry["p10"] = self._percentile(times, 10)
                entry["p25"] = self._percentile(times, 25)
                entry["p50"] = self._percentile(times, 50)
                entry["p75"] = self._percentile(times, 75)
                entry["p90"] = self._percentile(times, 90)

                q1 = entry["p25"]
                q3 = entry["p75"]
                iqr = q3 - q1

                entry["lower_fence"] = q1 - 1.5 * iqr
                entry["upper_fence"] = q3 + 1.5 * iqr

                entry["short_outliers"] = [
                    d for d in times if d < entry["lower_fence"]
                ]
                entry["long_outliers"] = [
                    d for d in times if d > entry["upper_fence"]
                ]

            if count >= 5:
                entry["cv"] = self._cv(times)
                entry["consistency"] = consistency_level(entry["cv"])

            stats[name] = entry

        # ------------------------------------------------------------------
        # OVERVIEW
        # ------------------------------------------------------------------

        self._print(f"Recorded games: {total}")
        self._print(f"Total play time: {self._fmt_short(total_ms)}")
        self._print(
            f"Games with hints used: {hints_games} of {total} "
            f"({hints_games * 100.0 / total:.1f}%)"
        )

        blank_lines()

        # ------------------------------------------------------------------
        # SIZE DISTRIBUTION
        # ------------------------------------------------------------------

        self._print("SIZE DISTRIBUTION")
        self._print("-" * 36)

        for name in size_names:
            times = size_games[name]
            count = len(times)
            size_total = sum(times)

            game_pct = count * 100.0 / total
            time_pct = size_total * 100.0 / total_ms if total_ms else 0.0

            self._print(
                f"    {name:<7} {count:>4}/{total:<4}"
                f"[{game_pct:5.1f}%] "
                f"({self._fmt_short(size_total)} [{time_pct:5.1f}%])"
            )

        blank_lines()

        # ------------------------------------------------------------------
        # SIZE / MODE DISTRIBUTION
        # ------------------------------------------------------------------

        self._print("SIZE / MODE DISTRIBUTION")
        self._print("-" * 36)

        for name in cfg_names:
            entry = stats[name]
            count = entry["count"]
            cfg_total = entry["total"]

            game_pct = count * 100.0 / total
            time_pct = cfg_total * 100.0 / total_ms if total_ms else 0.0

            self._print(
                f"    {name:<14} {count:>4}/{total:<4}"
                f"[{game_pct:5.1f}%] "
                f"({self._fmt_short(cfg_total)} [{time_pct:5.1f}%])"
            )

        blank_lines()

        # ------------------------------------------------------------------
        # TIME ANALYSIS
        # ------------------------------------------------------------------

        self._print("TIME ANALYSIS")
        self._print("-" * 36)

        self._print("Overall")
        self._print(f"    Fastest: {self._fmt_short(min(durations))}")

        if total >= 8:
            self._print(
                f"    10th percentile: "
                f"{self._fmt_short(self._percentile(durations, 10))}"
            )
            self._print(
                f"    25th percentile: "
                f"{self._fmt_short(self._percentile(durations, 25))}"
            )
            self._print(
                f"    50th percentile: "
                f"{self._fmt_short(self._percentile(durations, 50))}"
            )
            self._print(
                f"    75th percentile: "
                f"{self._fmt_short(self._percentile(durations, 75))}"
            )
            self._print(
                f"    90th percentile: "
                f"{self._fmt_short(self._percentile(durations, 90))}"
            )

        self._print(f"    Slowest: {self._fmt_short(max(durations))}")

        if total < 8:
            self._print("    Percentiles require at least 8 games.")

        for name in cfg_names:
            entry = stats[name]
            count = entry["count"]

            self._print("")
            self._print(name)

            if count < 3:
                self._print(
                    f"    Only {count} game(s); "
                    "too little data for meaningful statistics."
                )
                self._print(
                    "    Basic range shown above is the reliable part."
                )
                continue

            self._print(
                f"    Fastest: {self._fmt_short(entry['min'])}"
            )

            if count >= 8:
                self._print(
                    f"    10th percentile: "
                    f"{self._fmt_short(entry['p10'])}"
                )
                self._print(
                    f"    25th percentile: "
                    f"{self._fmt_short(entry['p25'])}"
                )
                self._print(
                    f"    50th percentile: "
                    f"{self._fmt_short(entry['p50'])}"
                )
                self._print(
                    f"    75th percentile: "
                    f"{self._fmt_short(entry['p75'])}"
                )
                self._print(
                    f"    90th percentile: "
                    f"{self._fmt_short(entry['p90'])}"
                )

            else:
                print_med = self._fmt_short(entry["median"])
                print_avg = self._fmt_short(entry["mean"])
                self._print(
                    f"    Median: {print_med} "
                    f"(avg. {print_avg})"
                )

            self._print(
                f"    Slowest: {self._fmt_short(entry['max'])}"
            )

        blank_lines()

        # ------------------------------------------------------------------
        # OUTLIERS
        # ------------------------------------------------------------------

        self._print("OUTLIERS")
        self._print("-" * 36)

        any_outlier_analysis = False

        for name in cfg_names:
            entry = stats[name]

            if entry["count"] < 8:
                continue

            any_outlier_analysis = True

            short_outliers = entry["short_outliers"]
            long_outliers = entry["long_outliers"]

            self._print(name)
            self._print(
                f"    Short outliers: {len(short_outliers)} / "
                f"{entry['count']}"
            )
            self._print(
                f"    Long outliers: {len(long_outliers)} / "
                f"{entry['count']}"
            )
            self._print(
                f"    Shortest: {self._fmt_short(entry['min'])}"
            )
            self._print(
                f"    Longest: {self._fmt_short(entry['max'])}"
            )
            self._print(
                f"    Typical: {self._fmt_short(entry['median'])} "
                f"(avg. {self._fmt_short(entry['mean'])})"
            )

            self._print("")

        if not any_outlier_analysis:
            self._print(
                "Not enough data for configuration-level "
                "outlier detection."
            )
            self._print(
                "Each configuration needs at least 8 games."
            )

        blank_lines()

        # ------------------------------------------------------------------
        # RECENT PERFORMANCE
        # ------------------------------------------------------------------

        self._print("RECENT PERFORMANCE")
        self._print("-" * 36)

        any_recent = False

        for name in cfg_names:
            entry = stats[name]
            count = entry["count"]

            if count < 8:
                continue

            any_recent = True

            if count >= 15:
                w = 10
            else:
                w = 5

            recent = entry["times"][-w:]
            previous = entry["times"][-2 * w:-w]

            if len(previous) < w:
                continue

            r_med = self._median(recent)
            r_avg = self._mean(recent)
            p_med = self._median(previous)
            p_avg = self._mean(previous)

            change = change_percent(r_med, p_med)
            label = trend_label(change) if change is not None else "Unknown"

            self._print(name)
            self._print(
                f"    Recent: {self._fmt_short(r_med)} "
                f"(avg. {self._fmt_short(r_avg)})"
            )
            self._print(
                f"    Previous: {self._fmt_short(p_med)} "
                f"(avg. {self._fmt_short(p_avg)})"
            )

            if change is not None:
                self._print(f"    Change: {change:+.1f}%")

            self._print(
                f"    Best recent: {self._fmt_short(min(recent))}"
            )
            self._print(
                f"    Worst recent: {self._fmt_short(max(recent))}"
            )
            self._print(f"    Trend: {label}")
            self._print("")

        if not any_recent:
            self._print(
                "Not enough data for configuration-level "
                "recent performance."
            )
            self._print(
                "Each configuration needs at least 8 games."
            )

        blank_lines()

        # ------------------------------------------------------------------
        # TREND ANALYSIS
        # ------------------------------------------------------------------

        self._print("TREND ANALYSIS")
        self._print("-" * 36)

        any_trend = False

        for name in cfg_names:
            entry = stats[name]

            available = False

            for w in (5, 10, 20, 50):
                if entry["count"] >= 2 * w:
                    available = True
                    break

            if not available:
                continue

            any_trend = True
            self._print(name)

            for w in (5, 10, 20, 50):
                if entry["count"] < 2 * w:
                    continue

                recent = entry["times"][-w:]
                previous = entry["times"][-2 * w:-w]

                r_med = self._median(recent)
                r_avg = self._mean(recent)
                p_med = self._median(previous)
                p_avg = self._mean(previous)

                change = change_percent(r_med, p_med)

                self._print(
                    f"    Last {w}: {self._fmt_short(r_med)} "
                    f"avg {self._fmt_short(r_avg)}"
                )
                self._print(
                    f"         prev: {self._fmt_short(p_med)} "
                    f"avg {self._fmt_short(p_avg)} "
                    f"({change:+.1f}%)"
                )

            self._print("")

        if not any_trend:
            self._print(
                "Not enough games for configuration-level "
                "trend windows."
            )

        blank_lines()

        # ------------------------------------------------------------------
        # HISTORICAL BASELINE VS RECENT
        # ------------------------------------------------------------------

        self._print("HISTORICAL BASELINE VS RECENT")
        self._print("-" * 36)

        any_baseline = False

        for name in cfg_names:
            entry = stats[name]
            count = entry["count"]

            if count < 12:
                continue

            if count >= 13:
                w = 10
            else:
                w = 5

            historical = entry["times"][:-w]
            recent = entry["times"][-w:]

            if len(historical) < 3:
                continue

            any_baseline = True

            h_med = self._median(historical)
            h_avg = self._mean(historical)
            r_med = self._median(recent)
            r_avg = self._mean(recent)

            diff = change_percent(r_med, h_med)
            assessment = trend_label(diff) if diff is not None else "Unknown"

            self._print(name)
            self._print(
                f"    Historical: {self._fmt_short(h_med)} "
                f"(avg. {self._fmt_short(h_avg)})"
            )
            self._print(
                f"    Recent:     {self._fmt_short(r_med)} "
                f"(avg. {self._fmt_short(r_avg)})"
            )

            if diff is not None:
                self._print(f"    Difference: {diff:+.1f}%")
                self._print(f"    Assessment: {assessment}")

            self._print("")

        if not any_baseline:
            self._print(
                "Not enough data for a historical baseline comparison."
            )
            self._print(
                "At least 12 games per configuration are recommended."
            )

        blank_lines()

        # ------------------------------------------------------------------
        # CONSISTENCY
        # ------------------------------------------------------------------

        self._print("CONSISTENCY")
        self._print("-" * 36)

        any_consistency = False

        for name in cfg_names:
            entry = stats[name]

            if entry["count"] < 5:
                continue

            any_consistency = True

            self._print(name)
            self._print(
                f"    Typical: {self._fmt_short(entry['median'])} "
                f"(avg. {self._fmt_short(entry['mean'])})"
            )

            if entry["count"] >= 8:
                self._print(
                    f"    Typical range: "
                    f"{self._fmt_short(entry['p25'])} - "
                    f"{self._fmt_short(entry['p75'])}"
                )

            self._print(
                f"    Variation: {entry['consistency']} "
                f"(CV {entry['cv']:.2f})"
            )
            self._print("")

        if not any_consistency:
            self._print(
                "Not enough data for configuration-level "
                "consistency analysis."
            )
            self._print(
                "Each configuration needs at least 5 games."
            )

        blank_lines()

        # ------------------------------------------------------------------
        # MODE ANALYSIS
        # ------------------------------------------------------------------

        self._print("MODE ANALYSIS")
        self._print("-" * 36)

        for name in cfg_names:
            entry = stats[name]
            count = entry["count"]

            game_pct = count * 100.0 / total
            time_pct = (
                entry["total"] * 100.0 / total_ms
                if total_ms else 0.0
            )

            self._print(name)
            self._print(
                f"    Games: {count} "
                f"({game_pct:.1f}% of games)"
            )
            self._print(
                f"    Total time: {self._fmt_short(entry['total'])} "
                f"({time_pct:.1f}% of play time)"
            )

            if count >= 3:
                self._print(
                    f"    Median: {self._fmt_short(entry['median'])} "
                    f"(avg. {self._fmt_short(entry['mean'])})"
                )

            self._print(
                f"    Fastest: {self._fmt_short(entry['min'])}"
            )
            self._print(
                f"    Slowest: {self._fmt_short(entry['max'])}"
            )

            if count < 3:
                self._print(
                    "    Too little data for meaningful "
                    "typical-time statistics."
                )

            self._print("")

        blank_lines()

        # ------------------------------------------------------------------
        # FORECAST
        # ------------------------------------------------------------------

        self._print("FORECAST")
        self._print("-" * 36)

        for name in cfg_names:
            entry = stats[name]
            count = entry["count"]

            self._print(name)

            if count < 10:
                self._print(
                    f"    Forecast unavailable with only {count} games."
                )
                self._print(
                    "    At least 10 games are recommended for a useful"
                )
                self._print(
                    "    estimate."
                )
                self._print("")
                continue

            recent = entry["times"][-10:]
            r_med = self._median(recent)
            r_avg = self._mean(recent)
            r_q1 = self._percentile(recent, 25)
            r_q3 = self._percentile(recent, 75)

            trend = "Stable"

            if count >= 20:
                previous = entry["times"][-20:-10]
                p_med = self._median(previous)
                change = change_percent(r_med, p_med)

                if change is not None:
                    trend = trend_label(change)

            self._print(
                f"    Expected: ~{self._fmt_short(r_med)} "
                f"(avg. {self._fmt_short(r_avg)})"
            )
            self._print(
                f"    Typical range: {self._fmt_short(r_q1)} - "
                f"{self._fmt_short(r_q3)}"
            )
            self._print(f"    Trend: {trend}")

            self._print("")

        blank_lines()

        # ------------------------------------------------------------------
        # KEY FINDINGS
        # ------------------------------------------------------------------

        self._print("KEY FINDINGS")
        self._print("-" * 36)

        findings = []

        def add_finding(priority, text, key):
            findings.append({
                "priority": priority,
                "text": text,
                "key": key,
            })

        # --------------------------------------------------------------
        # Configuration trends
        # --------------------------------------------------------------

        for name in cfg_names:
            entry = stats[name]

            if entry["count"] >= 15:
                recent = entry["times"][-10:]
                previous = entry["times"][-20:-10]

                r_med = self._median(recent)
                p_med = self._median(previous)
                change = change_percent(r_med, p_med)

                if change is not None:
                    if abs(change) >= 20:
                        label = trend_label(change)
                        add_finding(
                            100,
                            f"{name}: {label} ({change:+.0f}%).",
                            f"trend_major_{name}"
                        )
                    elif abs(change) >= 10:
                        label = trend_label(change)
                        add_finding(
                            75,
                            f"{name}: {label} ({change:+.0f}%).",
                            f"trend_{name}"
                        )

        # --------------------------------------------------------------
        # Normal vs Ultra ratio
        # --------------------------------------------------------------

        normal_by_size = {}

        for name in cfg_names:
            if name.endswith(" Ultra"):
                continue

            normal_by_size[size_num(name)] = name

        for size, normal_name in normal_by_size.items():
            ultra_name = f"{size}x{size} Ultra"

            if ultra_name not in stats:
                continue

            normal = stats[normal_name]
            ultra = stats[ultra_name]

            if normal["count"] < 3 or ultra["count"] < 3:
                continue

            if normal["median"] <= 0:
                continue

            ratio = ultra["median"] / normal["median"]

            if ratio < 1.5 or ratio > 2.5:
                add_finding(
                    90,
                    f"{ultra_name} is {ratio:.1f}x as long as "
                    f"{normal_name} (expected ~2x).",
                    f"ultra_ratio_major_{size}"
                )
            elif ratio < 1.8 or ratio > 2.2:
                add_finding(
                    65,
                    f"{ultra_name} is {ratio:.1f}x as long as "
                    f"{normal_name} (expected ~2x).",
                    f"ultra_ratio_{size}"
                )

        # --------------------------------------------------------------
        # Long and short outliers
        # --------------------------------------------------------------

        for name in cfg_names:
            entry = stats[name]

            if entry["count"] < 8:
                continue

            short_count = len(entry["short_outliers"])
            long_count = len(entry["long_outliers"])

            if short_count:
                fastest = min(entry["short_outliers"])

                add_finding(
                    88 if short_count >= 2 else 72,
                    f"{name}: {short_count} unusually fast "
                    f"game(s), fastest {self._fmt_short(fastest)}.",
                    f"short_outlier_{name}"
                )

            if long_count:
                longest = max(entry["long_outliers"])

                multiplier = (
                    longest / entry["median"]
                    if entry["median"] > 0 else 0
                )

                add_finding(
                    90 if multiplier >= 3 else 76,
                    f"{name}: {long_count} unusually slow "
                    f"game(s), longest {self._fmt_short(longest)}.",
                    f"long_outlier_{name}"
                )

        # --------------------------------------------------------------
        # Consistency
        # --------------------------------------------------------------

        for name in cfg_names:
            entry = stats[name]

            if entry["count"] < 5:
                continue

            cv = entry["cv"]

            if cv >= 0.70:
                add_finding(
                    72,
                    f"{name}: high variation in completion time "
                    f"(CV {cv:.2f}).",
                    f"high_variation_{name}"
                )

        # --------------------------------------------------------------
        # Game share vs time share
        # --------------------------------------------------------------

        for name in cfg_names:
            entry = stats[name]

            game_share = entry["count"] / total
            time_share = (
                entry["total"] / total_ms
                if total_ms else 0.0
            )

            share_difference = abs(time_share - game_share) * 100.0

            if share_difference >= 15:
                if time_share > game_share:
                    wording = "uses more play time than its game share"
                else:
                    wording = "uses less play time than its game share"

                add_finding(
                    58,
                    f"{name}: {wording} "
                    f"({time_share * 100:.1f}% vs "
                    f"{game_share * 100:.1f}%).",
                    f"share_difference_{name}"
                )

        # --------------------------------------------------------------
        # Most played / largest time consumer
        # --------------------------------------------------------------

        if len(cfg_names) >= 2 and total >= 5:
            most_played = max(
                cfg_names,
                key=lambda name: stats[name]["count"]
            )

            most_time = max(
                cfg_names,
                key=lambda name: stats[name]["total"]
            )

            add_finding(
                40,
                f"{most_played} is your most played configuration "
                f"({stats[most_played]['count']} games).",
                "most_played"
            )

            if most_time != most_played:
                add_finding(
                    45,
                    f"{most_time} accounts for the most total play time "
                    f"({self._fmt_short(stats[most_time]['total'])}).",
                    "most_time"
                )

        # --------------------------------------------------------------
        # Sort, deduplicate, and limit to the most important findings.
        # --------------------------------------------------------------

        findings.sort(
            key=lambda item: (-item["priority"], item["key"])
        )

        selected = []
        used_keys = set()

        for finding in findings:
            if finding["key"] in used_keys:
                continue

            selected.append(finding)
            used_keys.add(finding["key"])

            if len(selected) >= 6:
                break

        if selected:
            for finding in selected:
                text = finding["text"]

                # Hard 70-character output limit.
                # Break findings at word boundaries instead of truncating.
                while len(text) > 68:
                    split_at = text.rfind(" ", 0, 68)

                    if split_at <= 0:
                        split_at = 68

                    self._print(f"    - {text[:split_at]}")
                    text = text[split_at:].lstrip()

                self._print(f"    - {text}")
        else:
            self._print(
                "No significant findings stand out in your history."
            )

        blank_lines()

        self._print(f"Analyzed {total} recorded game(s).")

    def _print_stats(self): # 
        self._print("Statistics")
        self._print("") 
        
        max_games = max(
            (
                self.stats.get(str(n), {}).get(mode, {}).get("games", 0) 
                for n in con.DIFFICULTIES 
                for mode in ("normal", "ultra") 
            ), 
            default=0
        )
        g_width = len(str(max_games))
        
        for mode_label, mode_key in (("Normal", "normal"), ("Ultra", "ultra")):
            self._print(f"{mode_label:<6}") 
            for n in con.DIFFICULTIES:
                m = self.stats.get(str(n), {}).get(mode_key, {}) 
                games = m.get("games", 0) 
                best = m.get("best", None)
                total = m.get("total", 0) 
                
                avg = total // games if games else None 
                game_word = "game " if games == 1 else "games" 
                
                self._print(
                    f"  {n}x{n}: {games:>{g_width}} {game_word} | "
                    f"Best: {self._fmt_time(best)} | Avg: {self._fmt_time(avg)}"
                ) 
        
        self._print("")
        
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

        page_count = len(helpers.ACHIEVEMENT_PAGES)
        if normalized.isdigit():
            index = int(normalized) - 1
            if 0 <= index < page_count:
                return index

        for n in con.DIFFICULTIES:
            size_token = str(n)
            if normalized == size_token:
                for i, page in enumerate(helpers.ACHIEVEMENT_PAGES):
                    title = page["title"].lower()
                    if f"{n}x{n}" in title:
                        return i

        for i, page in enumerate(helpers.ACHIEVEMENT_PAGES):
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
        page = helpers.ACHIEVEMENT_PAGES[page_index]
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
            for i, page in enumerate(helpers.ACHIEVEMENT_PAGES, start=1):
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
            for i, page in enumerate(helpers.ACHIEVEMENT_PAGES, start=1):
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

    def _print_settings(self):
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
        
    def _print_history(self, active_filters = [], active_sort = ["newest"]):
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
            self._print(
                f"{entry['label']}  |  "
                f"{entry['size']}x{entry['size']} {mode}  |  "
                f"{self._fmt_time(entry['play_time'], minute_width)}  |  "
                f"{entry['hints_used']} "
                f"{'hint' if entry['hints_used'] == 1 else 'hints'}"
            )
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
    
    def _help_menu(self): 
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
        self._print("   close                - Leave the terminal.")
        self._print("   quit                 - Leave the whole game.")
        self._print("   time                 - Get the time of your location.")
        self._print("   clear                - Refresh the screen.")
        self._print("   stats                - Show your stats.")
        self._print("   graphic achievements - Open the graphical achievements view.")
        self._print("   achievements         - Show your achievements.")
        self._print("   graphic history      - Open the graphical history view.")
        self._print("   history              - Show your recent matches right here.")
        self._print("   active play          - Show matches with an active save state.")
        self._print("   export history       - Show the recorded video export history.")
        self._print("   graphic settings     - Open the graphical settings view.")
        self._print("   settings             - Show your current settings right here.")
        self._print("   advanced settings    - Open the graphical advanced settings view.")
        self._print("   graphic about        - Open the graphical about screen.")
        self._print("   about                - Show the about info right here.") 
        
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
        self._print("    hint  - Get a hint for the game") 
        self._print("    p / b - Open the pause section (pause, break)")
        self._print("    c     - Return to the match   (continue)")
        self._print("    new   - Start a new Ultra match with same size") 
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
        self._print("    close  - Leave the terminal") 
        self._print("    return - Return to the terminal") 
        self._print("    time   - Get the time of your location") 
        self._print("    pt     - Get the time of the match (play time)") 
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
        self._print("    analysis  - Deep statistical analysis of your whole history")  
    
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
        self._cleared() 
        game = self.ultra_game 
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
        ] 
        col_fulfilled = [
            sum(grid[r][c] for r in range(n) if user_sel[r][c]) == col_sums[c]
            for c in range(n)
        ] 
            
        self._print("") 
        self._print("")
        
        col_marks = [f"{col_sums[c]:02}{'s' if col_fulfilled[c] else ' '}" for c in range(n)]
        self._print("      " + " | ".join(col_marks)) 
        self._print("     " + "─ " * (n * 3 - 1))
        
        for r in range(n): 
            rf = row_fulfilled[r]
            row_g = grid[r]
            row_s = user_sel[r]
            row_d = user_dimmed[r]
            
            cells = [] 
            for c in range(n): 
                if row_s[c]:
                    prefix = "*"
                elif row_d[c] or rf or col_fulfilled[c]:
                    prefix = "~"
                else:
                    prefix = " "
                cells.append(f"{prefix}{row_g[c]}") 
                
            mark = "s" if rf else " " 
            self._print(f"{row_sums[r]:02}{mark} | " + "  | ".join(cells)) 
            
        self._print("")
            
        
        if game.won:
            self._print("Celebration! You have won.") 
            self._print("")  
        
    def _clear(self): 
        self.lines.clear() 
        self.line_surfs.clear() 
        self.input_buffer = "" 
        self.cursor_pos = 0 
        self.heading = "Mati Terminal"   
        
    def _cleared(self):
        self.lines.clear() 
        self.line_surfs.clear() 
        self.input_buffer = "" 
        self.cursor_pos = 0 
        
    def _sync_ultra_flags(self): # Keep the ultra display flags in sync with the terminal settings
        game = self.ultra_game 
        if game is None: 
            return
        game.ultra_timer_ms = bool(self.settings.get("ultra_timer_ms", False)) 
        game.ultra_timer_show_clock = bool(self.settings.get("ultra_timer_show_clock", False)) 

    def ultra_elapsed_ms(self, now=None): 
        if self.ultra_game is None: 
            return None 
        game = self.ultra_game 
        if game.won: 
            return max(0, int(getattr(self, "o_time", 0)))
        if getattr(game, "paused", False): 
            return max(0, int(getattr(self, "o_time", 0)))
        base = getattr(self, "timer", None) 
        if base is None: 
            return max(0, int(getattr(self, "o_time", 0)))
        if now is None: 
            now = pg.time.get_ticks()
        return max(0, int(now - base))

    def ultra_timer_key(self, now=None): # Comparable key of the displayed ultra-timer text
        if not self.settings.get("ultra_timer_enabled", False): 
            return None
        if self.ultra_game is None: 
            return None
        self._sync_ultra_flags() 
        elapsed = self.ultra_elapsed_ms(now)
        if elapsed is None: 
            return None
        game = self.ultra_game
        if game.won or getattr(game, "paused", False):
            if getattr(game, "ultra_timer_ms", False):
                return ("frozen_ms", elapsed // 10)
            return ("frozen_s", elapsed // 1000)
        if getattr(game, "ultra_timer_ms", False): # Running with ms: refresh every 10 ms
            return ("run_ms", elapsed // 10)
        return ("run_s", elapsed // 1000) # Running seconds: refresh on the second change

    def ultra_clock_text(self):
        return dt.now().strftime("%H:%M:%S")

    def draw(self): 
        screen = w.get_screen()
        screen.fill(con.LIGHT_BLACK) 
        
        visible = self._visible_count() 
        surfs = list(self.line_surfs) 
        end = len(surfs) - self.scroll_offset 
        start = max(0, end - visible)
        visible_surfs = surfs[start:end]
        
        y = 50 
        for surf in visible_surfs: 
            screen.blit(surf, (20, y))
            y += con.LINE_HEIGHT
        
        before = self.input_buffer[:self.cursor_pos]
        after = self.input_buffer[self.cursor_pos:]
        prefix_surf = self._font.render("> " + before, True, con.WHITE)    
        screen.blit(prefix_surf, (20, con.HEIGHT - 34))
        cursor_x = 20 + prefix_surf.get_width()
        underscore_w = self._font.size("_")[0]
        
        if (pg.time.get_ticks() // 500) % 2 == 0:
            cursor_surf = self._font.render("_", True, con.WHITE)
            screen.blit(cursor_surf, (cursor_x, con.HEIGHT - 34))
        after_surf = self._font.render(after, True, con.WHITE)
        screen.blit(after_surf, (cursor_x + underscore_w, con.HEIGHT - 34))
        
        surfer = self._font.render(self.heading, True, con.TEXT_COLOR_2)
        screen.blit(surfer, (20, 20))
        screen.blit(surfer, (20, 20))
        
        if self.settings["ultra_timer_enabled"]: self._draw_ultra_timer_overlay(screen)
        if self.settings["ultra_timer_show_clock"]: self._draw_ultra_clock(screen)
        
        
    def _draw_ultra_clock(self, screen):
        line = self.ultra_clock_text()
        surf = self._font.render(line, True, con.TEXT_COLOR_2)
        screen.blit(surf, (con.WIDTH - surf.get_width() - 20, 20))
        screen.blit(surf, (con.WIDTH - surf.get_width() - 20, 20))
                
        
    def _draw_ultra_timer_overlay(self, screen): 
        game = self.ultra_game
        if game is None:
            return
        self._sync_ultra_flags() # Scheduler and renderer share the ms flag
        
        if game.won:
            elapsed = max(0, int(getattr(self, "o_time", 0)))
        elif getattr(game, "paused", False):
            elapsed = max(0, int(getattr(self, "o_time", 0)))
        else:
            elapsed = self.ultra_elapsed_ms()
            if elapsed is None:
                return
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
        