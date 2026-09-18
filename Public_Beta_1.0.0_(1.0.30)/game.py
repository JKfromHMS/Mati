"""Game state, match logic, and event handling.

This module contains the core game logic and state management.
Rendering is handled by the screens and widgets modules.
"""

import os
import threading
import tkinter as tk
from datetime import datetime as dt
from tkinter import filedialog

import pygame as pg

import alt_hover as ah
import config as con
import export as ex
import helpers
import lang
import screens as s
import tutorial
from level import (
    check_win,
    find_hint,
    generate_level,
    generate_level_letter,
)
from persistence import (
    delete_match,
    get_export_entry,
    list_history_meta,
    load_match,
    load_settings_and_stats,
    record_export,
    record_stat,
    save_match,
    save_settings_and_stats,
)
from widgets import get_fonts, get_screen, present


class Game:
    def __init__(self, sounds):
        self.sounds = sounds

        self._init_game_state()
        self._init_settings()
        self._init_input_state()
        self._init_scroll_state()
        self._init_hint_state()
        self._init_navigation_state()
        self._init_history_state()
        self._init_export()
        self._init_tutorial()

        self.apply_settings()

    def _init_game_state(self):
        """Initialize the core game state."""
        self.state = "MENU"
        self.n = 5

        self.grid = []
        self.row_sums = []
        self.col_sums = []
        self.solution = []
        self.user_sel = []
        self.user_dimmed = []
        self.row_fulfilled = []
        self.col_fulfilled = []

        self.won = False
        self.paused = False
        self.start_time = 0
        self.pause_started_at = 0
        self.total_paused_ms = 0
        self.play_time = 0

    def _init_settings(self):
        """Initialize settings, statistics, and settings UI state."""
        (
            self.settings,
            self.stats,
            self.paused_games,
            self.hannah_solved,
            self.achievements,
        ) = load_settings_and_stats()

        self.achievements_page = 0
        self.rebind_listening = None
        self.language_dropdown_open = False
        self.slider_drag = None

        self.request_fullscreen_toggle = False
        self.is_fullscreen = False

        self.stats_sort_key = None  # Interactive sorting of stats table (None = default order)
        self.stats_sort_asc = True  # Direction of active stats sorting

    def _init_input_state(self):
        """Initialize keyboard and mouse interaction state."""
        self.mouse_hover_key = None
        self.mouse_hover_start = 0

        self._repeat_direction = None
        self._repeat_next_time = 0

        self.scrollbar_drag = None

    def _init_scroll_state(self):
        """Initialize scroll tracking and scrollbar fade state."""
        self.history_scroll_last = -(10**9)
        self.detail_scroll_last = -(10**9)
        self.hannah_scroll_last = -(10**9)

    def _init_hint_state(self):
        """Initialize hints, undo, and current-game actions."""
        self.hints_left = con.HINTS_PER_GAME
        self.last_hint_cell = None
        self.hint_flash_timer = 0
        self.current_game_actions = []
        self.current_ultra = False

    def _init_navigation_state(self):
        """Initialize keyboard navigation and focus state."""
        self.cursor_r = 0
        self.cursor_c = 0
        self.focus_index = 0
        self.focus_key = None
        self.focus_lock_until = 0
        self.return_focus = {}

        self.last_key_time = pg.time.get_ticks()
        self.pending_new_n = None
        self.pending_new_ultra = False

    def _init_history_state(self):
        """Initialize game history and export state."""
        self.history_entries = []
        self.history_scroll_y = 0

        self.history_filter_size = None
        self.history_filter_top10 = None
        self.history_filter_ultra = None

        self.selected_history_data = None
        self.selected_history_name = None

        self.export_status = None
        self.export_status_until = 0
        self.export_finished_at = None  # Trigger timestamp for notification popup
        self.export_quality_idx = 0
        self.export_fps_idx = 0
        self.last_export_folder = None

        self.detail_selected_index = None
        self.detail_scroll_y = 0
        self.file_to_delete = None

        self.last_wheel_time = -(10**9)

    def _init_export(self):
        """Initialize video export state."""
        self.exporting = False
        self.export_backgrounded = False
        self.export_progress = 0.0
        self.export_thread = None
        self.export_popup_allowed = True  # Latched at export-finish time

    def _init_tutorial(self):
        """Set up onboarding tutorial, auto-starting only for new players."""
        total_games, _ = self.general_totals()
        is_new_player = total_games == 0 and not self.achievements.get("terminal_found")
        completed = self.settings.get("tutorial_completed", False) or not is_new_player
        self.tutorial = tutorial.Tutorial(completed=completed)

    def mark_tutorial_complete(self):
        """Persist that onboarding tutorial has been shown."""
        if not self.settings.get("tutorial_completed", False):
            self.settings["tutorial_completed"] = True
            save_settings_and_stats(self.settings, self.stats, self.paused_games)

    def new_game(self, n, ultra=False, force_new=False):
        key = self._pause_key(n, ultra)
        if not force_new and key in self.paused_games:
            self.pending_new_n = n
            self.pending_new_ultra = ultra
            self.state = "RESUME_CHOICE"
            return
        self._start_fresh(n, ultra)

    @staticmethod
    def _pause_key(n, ultra):
        return f"{n}_{'ultra' if ultra else 'normal'}"

    def _start_fresh(self, n, ultra=False):
        self.n = n
        self.current_ultra = ultra
        self.grid, self.row_sums, self.col_sums, self.solution = generate_level(n)
        self.user_sel = [[False] * n for _ in range(n)]
        self.user_dimmed = [[False] * n for _ in range(n)]
        self.row_fulfilled = [False] * n
        self.col_fulfilled = [False] * n
        self.won = False
        self.paused = False
        self.total_paused_ms = 0
        self.start_time = pg.time.get_ticks()
        self.play_time = 0
        self.hints_left = con.HINTS_PER_GAME
        self.last_hint_cell = None
        self.current_game_actions = []
        self.cursor_c = 0
        self.cursor_r = 0
        self.state = "PLAY"

    def restart_same(self):
        ultra = self.current_ultra
        self.paused_games.pop(self._pause_key(self.n, ultra), None)
        self._start_fresh(self.n, ultra)
        save_settings_and_stats(self.settings, self.stats, self.paused_games)

    def resume_paused(self, n, ultra):
        saved = self.paused_games.get(self._pause_key(n, ultra))
        if not saved:
            self._start_fresh(n, ultra)
            return
        self.n = n
        self.current_ultra = ultra
        self.grid = saved["grid"]
        self.row_sums = saved["row_sums"]
        self.col_sums = saved["col_sums"]
        self.solution = saved["solution"]
        self.user_sel = saved["user_sel"]
        self.user_dimmed = saved["user_dimmed"]
        self.row_fulfilled = [False] * n
        self.col_fulfilled = [False] * n
        self.won = False
        self.paused = False
        self.total_paused_ms = 0
        self.play_time = saved.get("play_time", 0)
        self.start_time = pg.time.get_ticks() - self.play_time
        self.hints_left = saved.get("hints_left", con.HINTS_PER_GAME)
        self.last_hint_cell = None
        self.current_game_actions = saved.get("actions", [])
        self.cursor_c = 0
        self.cursor_r = 0
        self.state = "PLAY"

    def discard_and_start(self, n, ultra):
        """Discard a paused game and start a new match."""
        self.paused_games.pop(self._pause_key(n, ultra), None)
        self._start_fresh(n, ultra)
        save_settings_and_stats(self.settings, self.stats, self.paused_games)

    def stash_current_game(self, o_time=None):
        """Save an unfinished match so it can be resumed later."""
        if self.state not in ("PLAY", "TERMINAL") or self.won:
            return
        key = self._pause_key(self.n, self.current_ultra)
        if not self.current_game_actions:
            self.paused_games.pop(key, None)
            save_settings_and_stats(self.settings, self.stats, self.paused_games)
            return

        has_selection = any(any(row) for row in self.user_sel)
        has_dimmed = any(any(row) for row in self.user_dimmed)
        if not (has_selection or has_dimmed):
            self.paused_games.pop(key, None)
            save_settings_and_stats(self.settings, self.stats, self.paused_games)
            return

        play_time = o_time if o_time is not None else self.play_time
        old_save = self.paused_games.get(key, {})
        self.paused_games[key] = {
            "started_at": old_save.get("started_at", dt.now().strftime("%Y-%m-%d %H:%M:%S")),
            "saved_at": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
            "grid": self.grid,
            "row_sums": self.row_sums,
            "col_sums": self.col_sums,
            "solution": self.solution,
            "user_sel": self.user_sel,
            "user_dimmed": self.user_dimmed,
            "play_time": play_time,
            "hints_left": self.hints_left,
            "actions": self.current_game_actions,
        }
        save_settings_and_stats(self.settings, self.stats, self.paused_games)

    def persist_settings(self):
        """Save current game settings."""
        self.settings.update({
            "save_history": self.save_history,
            "timer_enabled": self.timer_enabled,
            "timer_ms": self.timer_ms,
            "sound_enabled": self.sounds.enabled,
            "alt_control": self.alt_control,
            "live_clock_enabled": self.live_clock_enabled,
            "ultra_timer_enabled": self.ultra_timer_enabled,
            "ultra_timer_ms": self.ultra_timer_ms,
            "ultra_timer_show_clock": self.ultra_timer_show_clock,
            "game_volume": self.sounds.volume,
            "keybindings": self.keybindings,
        })
        save_settings_and_stats(self.settings, self.stats, self.paused_games)

    def adjust_slider_value(self, key, step):
        setting_key = "game_volume" if key == "game_volume" else "terminal_volume"
        value = self.settings.get(setting_key, 1.0)
        value = max(0.0, min(1.0, value + step))
        self.settings[setting_key] = value
        if key == "game_volume":
            self.sounds.volume = value

    def apply_settings(self):
        self.timer_enabled = self.settings.get("timer_enabled", False)
        self.timer_ms = self.settings.get("timer_ms", False) if self.timer_enabled else False
        self.save_history = self.settings.get("save_history", True)
        self.alt_control = self.settings.get("alt_control", True)
        self.sounds.enabled = self.settings.get("sound_enabled", True)
        self.sounds.volume = self.settings.get("game_volume", 1.0)
        self.live_clock_enabled = self.settings.get("live_clock_enabled", False)
        self.ultra_timer_enabled = self.settings.get("ultra_timer_enabled", False)
        self.ultra_timer_ms = (
            self.settings.get("ultra_timer_ms", False) if self.ultra_timer_enabled else False
        )
        self.ultra_timer_show_clock = self.settings.get("ultra_timer_show_clock", False)
        self.keybindings = {**con.DEFAULT_KEYBINDINGS, **self.settings.get("keybindings", {})}
        self.scale_mode = self.settings.get("scale_mode", "auto")
        self.render_quality = self.settings.get("render_quality", 1)
        lang.load_language(self.settings.get("language", con.BUILTIN_LANGUAGE))

    def set_keybinding(self, action, key_name, ctrl):
        self.keybindings[action] = {"key": key_name, "ctrl": ctrl}
        self.settings["keybindings"] = self.keybindings
        save_settings_and_stats(self.settings, self.stats, self.paused_games)

    def matches_binding(self, action, event):
        binding = self.keybindings.get(action, con.DEFAULT_KEYBINDINGS.get(action))
        if not binding:
            return False
        if pg.key.name(event.key) != binding["key"]:
            return False
        has_ctrl = bool(event.mod & (pg.KMOD_CTRL | pg.KMOD_META))
        return has_ctrl == bool(binding.get("ctrl", False))

    def mark_achievement(self, key):
        if not self.achievements.get(key):
            self.achievements[key] = True
            save_settings_and_stats(
                self.settings, self.stats, self.paused_games, achievements=self.achievements
            )

    def refresh_achievements(self):
        _, _, _, _, self.achievements = load_settings_and_stats()

    def general_totals(self):
        """Return total games played and total duration in milliseconds."""
        total_games = 0
        total_times_ms = 0
        for n in con.DIFFICULTIES:
            entry = self.stats.get(str(n), {})
            for ultra in (False, True):
                mode_stats = entry.get("ultra" if ultra else "normal", {})
                total_games += mode_stats.get("games", 0)
                total_times_ms += mode_stats.get("total", 0)

        return total_games, total_times_ms

    def check_achievements(self):
        changed = False
        ach = self.achievements

        letter_needed = [i for i, ch in enumerate(con.HANNAH_MESSAGE) if ch]
        hannah_done = all(
            i < len(self.hannah_solved) and self.hannah_solved[i] for i in letter_needed
        )
        if hannah_done and not ach.get("hannah_completed"):
            ach["hannah_completed"] = True
            changed = True

        for n in con.DIFFICULTIES:
            entry = self.stats.get(str(n), {})
            for ultra in (False, True):
                mode_stats = entry.get("ultra" if ultra else "normal", {})
                games = mode_stats.get("games", 0)
                best = mode_stats.get("best")

                suffix = "_ultra" if ultra else ""
                for m in con.ACHIEVEMENT_MILESTONES:
                    key = f"{m}_{n}x{n}{suffix}"
                    if games >= m and not ach.get(key):
                        ach[key] = True
                        changed = True

                if best:
                    for key, seconds in con.TIME_ACHIEVEMENTS.get((n, ultra), []):
                        if best <= seconds * 1000 and not ach.get(key):
                            ach[key] = True
                            changed = True

        total_games, total_times_ms = self.general_totals()

        for m in con.GENERAL_GAME_MILESTONES:
            key = f"games_{m}"
            if total_games >= m and not ach.get(key):
                ach[key] = True
                changed = True

        for key, seconds in con.GENERAL_TIME_MILESTONES:
            if total_times_ms >= seconds * 1000 and not ach.get(key):
                ach[key] = True
                changed = True

        if changed:
            save_settings_and_stats(
                self.settings, self.stats, self.paused_games, achievements=self.achievements
            )
        return changed

    def move_cursor(self, key):
        """Move keyboard navigation cursor across grid cells."""
        if self.won:
            return
        if self.state == "HANNAH" and getattr(self, "hannah_open_index", None):
            size = con.HANNAH_SIZE
        else:
            size = self.n

        match key:
            case pg.K_UP:
                self.cursor_r = max(0, self.cursor_r - 1)
            case pg.K_DOWN:
                self.cursor_r = min(size - 1, self.cursor_r + 1)
            case pg.K_LEFT:
                self.cursor_c = max(0, self.cursor_c - 1)
            case pg.K_RIGHT:
                self.cursor_c = min(size - 1, self.cursor_c + 1)

    # --- Time Management ---
    def tick_timer(self):
        """Update active play duration."""
        if self.state == "PLAY" and not self.won and not self.paused:
            self.play_time = pg.time.get_ticks() - self.start_time - self.total_paused_ms

    def toggle_pause(self):
        """Toggle game pause state."""
        if self.won:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_started_at = pg.time.get_ticks()
            if self.alt_control:
                self.focus_key = "break"
        else:
            self.total_paused_ms += pg.time.get_ticks() - self.pause_started_at

    # --- Cell Interaction ---
    def click_cell(self, r, c, right_click=False, o_time=None, ultra=False):
        """Process click interaction on a specific grid cell."""
        if self.won or self.paused:
            return
        prev_sel = self.user_sel[r][c]
        prev_dimmed = self.user_dimmed[r][c]

        if right_click:
            if self.user_dimmed[r][c]:
                action_type = "Undone"
                self.user_dimmed[r][c] = False
            else:
                action_type = "Right"
                self.user_sel[r][c] = False
                self.user_dimmed[r][c] = True
                self.sounds.play(self.sounds.dim)
        else:
            if self.user_sel[r][c]:
                action_type = "Undone"
                self.user_sel[r][c] = False
            else:
                self.user_dimmed[r][c] = False
                self.user_sel[r][c] = True
                action_type = "Left"
                self.sounds.play(self.sounds.click)

        self.current_game_actions.append({
            "time": o_time if o_time else self.play_time,
            "type": action_type,
            "r": r,
            "c": c,
            "prev_sel": prev_sel,
            "prev_dimmed": prev_dimmed,
            "new_sel": self.user_sel[r][c],
            "new_dimmed": self.user_dimmed[r][c],
            "hints_used_so_far": con.HINTS_PER_GAME - self.hints_left,
        })

        self._refresh_win_state(o_time, ultra)

    def start_tutorial(self, intro=True):
        """Open tutorial overview."""
        if intro:
            return
        self.tutorial_entry_state = self.state
        if self.state == "PLAY":
            self.stash_current_game()
            self.tutorial_entry_state = "MENU"
        self.state = "TUTORIAL"

    def tutorial_next(self):
        """Finish compact tutorial overview."""
        self.close_tutorial()

    def close_tutorial(self, destination=None):
        """Close compact tutorial overview and restore previous state."""
        if self.state == "PLAY":
            self.stash_current_game()
        self.state = (
            destination if destination is not None else getattr(self, "tutorial_entry_state", "MENU")
        )

    def undo(self):
        """Undo last move made by player."""
        if not self.current_game_actions or self.won or self.paused:
            return
        last = self.current_game_actions.pop()
        r, c = last["r"], last["c"]
        self.user_sel[r][c] = last["prev_sel"]
        self.user_dimmed[r][c] = last["prev_dimmed"]
        self.row_fulfilled = [False] * self.n
        self.col_fulfilled = [False] * self.n
        self.sounds.play(self.sounds.undo)

    def use_hint(self, o_time=None, ultra=False):
        """Provide a strategic hint for active game."""
        if self.hints_left <= 0 or self.won or self.paused:
            return
        result = find_hint(self.solution, self.user_sel, self.user_dimmed, self.n)
        if result is None:
            return
        r, c, should_select = result
        prev_sel = self.user_sel[r][c]
        prev_dimmed = self.user_dimmed[r][c]

        if should_select:
            self.user_sel[r][c] = True
            self.user_dimmed[r][c] = False
        else:
            self.user_sel[r][c] = False
            self.user_dimmed[r][c] = True

        self.hints_left -= 1
        self.last_hint_cell = (r, c)
        self.hint_flash_timer = pg.time.get_ticks()

        self.current_game_actions.append({
            "time": o_time if o_time else self.play_time,
            "type": "Hint",
            "r": r,
            "c": c,
            "prev_sel": prev_sel,
            "prev_dimmed": prev_dimmed,
            "new_sel": self.user_sel[r][c],
            "new_dimmed": self.user_dimmed[r][c],
            "hints_used_so_far": con.HINTS_PER_GAME - self.hints_left,
        })

        self.sounds.play(self.sounds.hint)
        self._refresh_win_state(o_time, ultra)

    def _refresh_win_state(self, o_time=None, ultra=False):
        """Evaluate and handle game win state."""
        self.row_fulfilled = [False] * self.n
        self.col_fulfilled = [False] * self.n
        self.won = check_win(self.grid, self.user_sel, self.row_sums, self.col_sums, self.n)
        if self.won:
            self.sounds.play(self.sounds.win)
            if self.alt_control:
                self.focus_key = "restart"
            hints_used = con.HINTS_PER_GAME - self.hints_left
            final_time = o_time if o_time is not None else self.play_time
            record_stat(self.stats, self.n, ultra, final_time)
            self.paused_games.pop(self._pause_key(self.n, ultra), None)
            save_settings_and_stats(self.settings, self.stats, self.paused_games)
            self.check_achievements()
            if self.save_history:
                save_match(
                    self.grid,
                    self.row_sums,
                    self.col_sums,
                    self.user_sel,
                    self.user_dimmed,
                    final_time,
                    self.current_game_actions,
                    hints_used,
                    ultra=ultra,
                )

    # --- History Management ---
    def open_history(self):
        """Open game history view."""
        self.history_entries = list_history_meta()
        for key in (
            "detail_back_return",
            "detail_export_return",
            "history_back_return",
            "history_top10_return",
            "history_top10_down_return",
            "history_ultra_return",
        ):
            setattr(self, key, None)

        self.state = "HISTORY"

        try:
            fk = getattr(self, "focus_key", None)
            if isinstance(fk, str) and (fk.startswith("entry_") or fk.startswith("delete_")):
                order = s.focus_order(self)
                ah.ensure_focus_visible(self, order)
        except Exception:
            self.history_scroll_y = 0

    def toggle_size_filter(self, n):
        """Toggle size filter in history view."""
        self.history_filter_size = n if self.history_filter_size != n else None
        self.history_scroll_y = 0

    def toggle_top10_filter(self):
        """Toggle top 10 speed run filter."""
        self.history_filter_top10 = not self.history_filter_top10
        self.history_scroll_y = 0

    def toggle_ultra_filter(self):
        """Toggle ultra mode filter."""
        self.history_filter_ultra = not self.history_filter_ultra
        self.history_scroll_y = 0

    def filtered_history(self):
        """Filter history entries based on current filter settings."""
        entries = self.history_entries
        if self.history_filter_size is not None:
            entries = [e for e in entries if e["size"] == self.history_filter_size]
        if self.history_filter_ultra and not any(e.get("ultra") for e in entries):
            self.history_filter_ultra = False
        if self.history_filter_ultra:
            entries = [e for e in entries if e.get("ultra")]
        if self.history_filter_top10:
            entries = sorted(entries, key=lambda e: e["play_time"])[:10]
        return entries

    def delete_history(self, filename):
        """Delete specific record from match history."""
        delete_match(filename)
        self.history_entries = list_history_meta()

    # --- History Detail ---
    def open_history_detail(self, filename):
        """Open detailed view for a match record."""
        self.selected_history_data = load_match(filename)
        self.selected_history_name = filename
        self.detail_selected_index = None
        self.detail_scroll_y = 0
        self.state = "HISTORY_DETAIL"

    def select_detail_action(self, index):
        """Select action step in history detail playback."""
        self.detail_selected_index = None if self.detail_selected_index == index else index

    def reset_detail_view(self):
        """Reset detail playback view to completion state."""
        self.detail_selected_index = None

    def sort_stats_by(self, key):
        """Sort stats table interactively by specified column key."""
        defaults = {"size": True, "mode": True, "games": False, "best": True, "average": True}
        if self.stats_sort_key == key:
            self.stats_sort_asc = not self.stats_sort_asc
        else:
            self.stats_sort_key = key
            self.stats_sort_asc = defaults.get(key, True)

    def export_selected_to_mp4(self):
        """Export currently selected match history to MP4 video."""
        if not self.selected_history_data or self.exporting:
            return

        entry = get_export_entry(self.selected_history_name)
        if entry:
            self.pending_export_entry = entry
            self.state = "EXPORT_EXISTS"
            return

        self._start_export()

    def confirm_export_selected_to_mp4(self):
        self.pending_export_entry = None
        self.state = "HISTORY_DETAIL"
        self._start_export()

    def cancel_export_exists(self):
        self.pending_export_entry = None
        self.state = "HISTORY_DETAIL"

    def _start_export(self):
        base = (
            (self.selected_history_name or dt.now().strftime("%Y-%m-%d_%H-%M-%S"))
            .replace("_", " ")
            .split(".")[0]
        )
        out_path = self._ask_export_path(base)

        if not out_path:
            return

        quality_name, quality_scale = con.EXPORT_QUALITIES[self.export_quality_idx]
        fps = con.EXPORT_FPS_CHOICES[self.export_fps_idx]

        self.exporting = True
        self.export_backgrounded = False
        self.export_progress = 0.0
        self.export_match_name = self.selected_history_name
        self.export_quality_name = quality_name
        self.export_thread = threading.Thread(
            target=self._run_export_thread,
            args=(self.selected_history_data, out_path, quality_scale, fps),
            daemon=True,
        )
        self.export_thread.start()

    def _run_export_thread(self, data, out_path, quality_scale, fps):
        ok, result = ex.export_history_to_mp4(
            self.sounds,
            data,
            out_path,
            quality_scale=quality_scale,
            fps=fps,
            progress_callback=self._set_export_progress,
        )
        finished_at = pg.time.get_ticks()
        if ok:
            try:
                n = len(data.get("grid", []))
                cell = int(con.CELL_SIZE * quality_scale)
                margin = int(con.EXPORT_MARGIN * quality_scale)
                header = int(con.EXPORT_HEADER_HEIGHT * quality_scale)
                side = (n + 1) * cell + margin * 2
                height = side + header
                record_export(
                    self.export_match_name,
                    {
                        "exported": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "format": "MP4",
                        "resolution": f"{side - side % 2}x{height - height % 2}",
                        "quality": getattr(
                            self,
                            "export_quality_name",
                            con.EXPORT_QUALITIES[self.export_quality_idx][0],
                        ),
                        "fps": fps,
                    },
                )
            except Exception:
                pass
        self.export_status = f"Saved: {out_path}" if ok else result
        self.export_finished_at = finished_at
        self.export_status_until = finished_at + (3000 if self.export_backgrounded else 6000)
        self.export_progress = 1.0

    def _set_export_progress(self, fraction):
        self.export_progress = fraction

    def check_export_progress(self):
        """Finalize finished background export."""
        if self.exporting and self.export_thread is not None and not self.export_thread.is_alive():
            self.exporting = False
            self.export_thread = None
            self.export_backgrounded = False

    def _ask_export_path(self, default_path):
        """Open file dialog picker for saving video export."""
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            initial = getattr(self, "last_export_folder", None) or os.getcwd()
            path = filedialog.asksaveasfilename(
                title="Choose where to save the mp4",
                initialdir=initial,
                initialfile=default_path + ".mp4",
                defaultextension=".mp4",
                filetypes=[("MP4 video container", "*.mp4")],
            )
            root.destroy()
            if path:
                self.last_export_folder = os.path.dirname(path)
            return path or None
        except Exception:
            fallback = os.path.join(os.getcwd(), con.EXPORT_DIR)
            os.makedirs(fallback, exist_ok=True)
            return os.path.join(fallback, default_path + ".mp4")

    def cycle_export_quality(self):
        """Switch to next export video quality setting."""
        self.export_quality_idx = (self.export_quality_idx + 1) % len(con.EXPORT_QUALITIES)

    def cycle_export_fps(self):
        """Switch to next export video FPS setting."""
        self.export_fps_idx = (self.export_fps_idx + 1) % len(con.EXPORT_FPS_CHOICES)

    # --- Easter Egg / Hannah Feature ---
    def init_hannah(self):
        """Prepare or re-open Hannah easter egg screen."""
        self.mark_achievement("hannah_found")
        if not getattr(self, "hannah_levels", None):
            self.hannah_levels = []
            n = con.HANNAH_SIZE
            for letter_char in con.HANNAH_MESSAGE:
                if letter_char is None:
                    self.hannah_levels.append(None)
                    continue
                grid, row_sums, col_sums, solution = generate_level_letter(n, letter_char)
                self.hannah_levels.append({
                    "letter": letter_char,
                    "grid": grid,
                    "row_sums": row_sums,
                    "col_sums": col_sums,
                    "solution": solution,
                    "user_sel": [[False] * n for _ in range(n)],
                    "user_dimmed": [[False] * n for _ in range(n)],
                    "actions": [],
                })
            for i, solved in enumerate(self.hannah_solved):
                if solved and i < len(self.hannah_levels) and self.hannah_levels[i] is not None:
                    lvl = self.hannah_levels[i]
                    lvl["user_sel"] = [row[:] for row in lvl["solution"]]
        self.hannah_scroll_x = 0
        self.cursor_r = 0
        self.cursor_c = 0
        self.hannah_open_index = None
        self.state = "HANNAH"

    def hannah_open(self, index):
        """Open specific letter puzzle in Hannah easter egg mode."""
        if index is None or index >= len(self.hannah_levels) or self.hannah_levels[index] is None:
            return
        self.hannah_open_index = index
        self.cursor_r = 0
        self.cursor_c = 0

    def hannah_close(self):
        """Return to Hannah overview mode."""
        self.hannah_open_index = None

    def hannah_click_cell(self, r, c, right_click=False):
        """Handle cell interaction inside Hannah letter puzzle."""
        if self.hannah_open_index is None:
            return
        lvl = self.hannah_levels[self.hannah_open_index]
        prev_sel = lvl["user_sel"][r][c]
        prev_dimmed = lvl["user_dimmed"][r][c]
        if lvl["user_sel"][r][c] and lvl["user_dimmed"][r][c]:
            lvl["user_dimmed"][r][c] = False

        if right_click:
            lvl["user_dimmed"][r][c] = not lvl["user_dimmed"][r][c]
            if lvl["user_dimmed"][r][c]:
                lvl["user_sel"][r][c] = False
            self.sounds.play(self.sounds.dim)
        else:
            lvl["user_sel"][r][c] = not lvl["user_sel"][r][c]
            if lvl["user_sel"][r][c]:
                lvl["user_dimmed"][r][c] = False
            self.sounds.play(self.sounds.click)

        lvl["actions"].append({"r": r, "c": c, "prev_sel": prev_sel, "prev_dimmed": prev_dimmed})
        n = con.HANNAH_SIZE
        if check_win(lvl["grid"], lvl["user_sel"], lvl["row_sums"], lvl["col_sums"], n):
            self.sounds.play(self.sounds.win)
            while len(self.hannah_solved) <= self.hannah_open_index:
                self.hannah_solved.append(False)
            self.hannah_solved[self.hannah_open_index] = True
            save_settings_and_stats(
                self.settings, self.stats, self.paused_games, self.hannah_solved
            )
            self.check_achievements()
            solved_index = self.hannah_open_index
            self.hannah_open_index = None
            self._hannah_scroll_to_next(solved_index)

    def _hannah_scroll_to_next(self, from_index):
        """Scroll automatically to next unsolved Hannah tile."""
        next_index = None
        for i in range(from_index + 1, len(con.HANNAH_MESSAGE)):
            already_solved = i < len(self.hannah_solved) and self.hannah_solved[i]
            if con.HANNAH_MESSAGE[i] and not already_solved:
                next_index = i
                break
        if next_index is None:
            return

        rect = helpers.hannah_tile_rect(next_index, self.hannah_scroll_x)
        min_scroll = helpers.hannah_scroll_bounds()

        target_scroll = self.hannah_scroll_x
        if rect.left < 40:
            target_scroll = self.hannah_scroll_x + (40 - rect.left)
        elif rect.right > con.WIDTH - 40:
            target_scroll = self.hannah_scroll_x - (rect.right - (con.WIDTH - 40))

        self.hannah_scroll_x = max(min_scroll, min(0, target_scroll))

    def hannah_undo(self):
        """Undo action inside active Hannah letter puzzle."""
        if self.hannah_open_index is None:
            return
        lvl = self.hannah_levels[self.hannah_open_index]
        if not lvl["actions"]:
            return
        last = lvl["actions"].pop()
        lvl["user_sel"][last["r"]][last["c"]] = last["prev_sel"]
        lvl["user_dimmed"][last["r"]][last["c"]] = last["prev_dimmed"]
        self.sounds.play(self.sounds.undo)