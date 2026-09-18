### Mati (Mathematics and tactic intelligence) ###
### V0.6.3 (Beta V1.0.24) ###
### Author: Janosch Klawatsch, 2026-09-01 ###
### screens file V0.6.5 ###

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
import pygame as pg # Something like the engine on which the game runs.

### Own ###
import alt_hover as ah
import buttons as bt
import config as con
import helpers
from helpers import hannah_content_width
import lang
import replay as re
import widgets as w

### -Functions- ###
### Menu ###    
def draw_menu(game, mx, my): # Draw the defined menu
    w.draw_title(lang.t("mati", "Mati"), con.TEXT_COLOR, con.WIDTH // 2, 90) # Let the title been drawn
    w.draw_small(lang.t("intro_text", "Mathematic and Tactic Intelligence"), con.TEXT_COLOR, con.WIDTH // 2, 135) # Let the name definition been drawn
    buttons = bt.menu_buttons.get(game) # Load the needed buttons
    fk = ah.effective_focus_key(game, mx, my)
    for button in buttons.values():
        button.draw(mx, my, focus_key=fk)
    
### Settings ###    
def draw_settings(game, mx ,my): # Draw the defined settings
    w.draw_title(lang.t("settings_title", "Settings"), con.TEXT_COLOR, con.WIDTH // 2, 90) # Draw Setting declaration
    buttons = bt.settings_buttons.get(game) # Load the buttons and headers
    fk = ah.effective_focus_key(game, mx, my) # Get the current keyboard focus
    
    buttons["back"].draw(mx, my, focus_key=fk)
    
    # Headers now include the updated x coords
    sections = helpers.settings_sections(game)
    headers = [(title, x, y) for title, _keys, x, y in sections]
    for title, x, y in headers: # Every section gets a small label above
        x_h = x if len(headers) == 4 else x + 110
        y_h = y if len(headers) == 4 else y + 10
        w.draw_tiny(lang.t("title", f"{title.upper()}"), con.DIMMED_TEXT_COLOR, x_h, y_h, center=True if len(headers) == 3 else False)
    
    buttons["toggle_history"].label = lang.t("save_played", "Save Played: ") + (lang.t("on", "On") if game.save_history else lang.t("off", "Off"))
    buttons["toggle_history"].active = game.save_history
    buttons["toggle_history"].draw(mx, my, focus_key=fk)
    
    buttons["toggle_sound"].label = lang.t("sound", "Sound: ") + (lang.t("on", "On") if game.sounds.enabled else lang.t("off", "Off"))
    buttons["toggle_sound"].active = game.sounds.enabled
    buttons["toggle_sound"].draw(mx, my, focus_key=fk)
    
    buttons["toggle_alt_control"].label = lang.t("alt_control", "Keyboard-Navigation: ") + (lang.t("on", "On") if game.alt_control else lang.t("off", "Off"))
    buttons["toggle_alt_control"].active = game.alt_control
    buttons["toggle_alt_control"].draw(mx, my, focus_key=fk)
    
    buttons["toggle_timer"].label = lang.t("show_timer", "Show Timer: ") + (lang.t("on", "On") if game.timer_enabled else lang.t("off", "Off"))
    buttons["toggle_timer"].active = game.timer_enabled
    buttons["toggle_timer"].draw(mx, my, focus_key=fk)
    
    if game.timer_enabled:
        buttons["toggle_ms"].label = lang.t("milliseconds", "Milliseconds: ") + (lang.t("on", "On") if game.timer_ms else lang.t("off", "Off"))
        buttons["toggle_ms"].active = game.timer_ms
        buttons["toggle_ms"].draw(mx, my, focus_key=fk)
    
    buttons["toggle_fullscreen"].label = lang.t("fullscreen", "Fullscreen: ") + (lang.t("on", "On") if game.is_fullscreen else lang.t("off", "Off"))
    buttons["toggle_fullscreen"].active = game.is_fullscreen
    buttons["toggle_fullscreen"].draw(mx, my, focus_key=fk)
    
    buttons["toggle_live_clock"].label = lang.t("live_clock", "Live Clock: ") + (lang.t("on", "On") if game.live_clock_enabled else lang.t("off", "Off"))
    buttons["toggle_live_clock"].active = game.live_clock_enabled
    buttons["toggle_live_clock"].draw(mx, my, focus_key=fk)
    
    if "toggle_ultra_timer" in buttons:
        buttons["toggle_ultra_timer"].label = lang.t("ultra_timer", "Ultra Timer: ") + (lang.t("on", "On") if game.ultra_timer_enabled else lang.t("off", "Off"))
        buttons["toggle_ultra_timer"].active = game.ultra_timer_enabled
        buttons["toggle_ultra_timer"].draw(mx, my, focus_key=fk)
    
    if game.ultra_timer_enabled and "toggle_ultra_timer_ms" in buttons:
        buttons["toggle_ultra_timer_ms"].label = lang.t("ultra_ms", "Ultra Timer ms: ") + (lang.t("on", "On") if game.ultra_timer_ms else lang.t("off", "Off"))
        buttons["toggle_ultra_timer_ms"].active = game.ultra_timer_ms
        buttons["toggle_ultra_timer_ms"].draw(mx, my, focus_key=fk)
    
    if "toggle_ultra_timer_clock" in buttons:
        buttons["toggle_ultra_timer_clock"].label = lang.t("ultra_clock", "Terminal Clock: ") + (lang.t("on", "On") if game.ultra_timer_show_clock else lang.t("off", "Off"))
        buttons["toggle_ultra_timer_clock"].active = game.ultra_timer_show_clock
        buttons["toggle_ultra_timer_clock"].draw(mx, my, focus_key=fk)

    buttons["stats"].label = lang.t("stats", "Stats")
    buttons["stats"].draw(mx, my, focus_key=fk)
    buttons["achievements"].label = lang.t("achievements", "Achievements")
    buttons["achievements"].draw(mx, my, focus_key=fk)
    buttons["about"].label = lang.t("about", "About")
    buttons["about"].draw(mx, my, focus_key=fk)
    w.draw_tiny(lang.t("fullscreen_info", "Press F11 to switch or ESC to end fullscreen"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, buttons["about"].rect.bottom + 14)
    
    
### Advanced Settings ###
def draw_advanced_settings(game, mx, my):
    fk = ah.effective_focus_key(game, mx, my)
    buttons = bt.advanced_settings_buttons.get(game)
    
    w.draw_title(lang.t("advanced_settings_title", "Advanced Settings"), con.TEXT_COLOR, con.WIDTH // 2, 55)
    buttons["back"].draw(mx, my, focus_key=fk)
    
    # --- Volume ---
    w.draw_small(lang.t("volume", "Volume"), con.TEXT_COLOR, 60, 105, center=False)
    dot_mode = getattr(game, "slider_dot_mode", False)
    game_focus_mode = ("dot" if dot_mode else "region") if fk == "game_volume" else None
    terminal_focus_mode = ("dot" if dot_mode else "region") if fk == "terminal_volume" else None
    w.draw_slider(bt.ADV_GAME_VOLUME_RECT, game.settings.get("game_volume", 1.0), bt.ADV_GAME_VOLUME_RECT.collidepoint(mx, my), label=lang.t("game_volume", "Game volume"), focus_mode=game_focus_mode)
    w.draw_slider(bt.ADV_TERMINAL_VOLUME_RECT, game.settings.get("terminal_volume", 1.0), bt.ADV_TERMINAL_VOLUME_RECT.collidepoint(mx, my), label=lang.t("terminal_volume", "Terminal Volume"), focus_mode=terminal_focus_mode)
        
    terminal_sound_on = game.settings.get("terminal_sound_enabled", True)
    buttons["toggle_terminal_sound"].label = lang.t("ter_sound_on", "Terminal Sounds: On") if terminal_sound_on else lang.t("ter_sound_off", "Terminal Sounds: Off")
    buttons["toggle_terminal_sound"].active = terminal_sound_on
    buttons["toggle_terminal_sound"].draw(mx, my, focus_key=fk)
        
    # --- Language ---
    w.draw_small(lang.t("language", "Language"), con.TEXT_COLOR, 60, 305, center = False)
    current_display = next((label for label, internal in helpers.available_languages() if internal == lang.current_language()), "English")
    buttons["language_dropdown"].label = current_display
    buttons["language_dropdown"].draw(mx, my, focus_key=fk)
    if getattr(game, "language_dropdown_open", False):
        for i, (label, internal) in enumerate(helpers.available_languages()):
            key = f"language_option_{i}"
            buttons[key].active = internal == lang.current_language()
            buttons[key].draw(mx, my, focus_key=fk)
                        
    # --- Ultra terminal input order ---
    w.draw_small(lang.t("u_ter_in_ord", "Ultra Terminal Input Order"), con.TEXT_COLOR, 420, 105, center=False)
    current_front = game.settings.get("input_order_front", "action_column_row")
    current_back = game.settings.get("input_order_back", "column_row_action")
    for i, option in enumerate(con.INPUT_ORDER_OPTIONS):
        key = f"input_order_{i}"
        buttons[key].label = lang.t(con.INPUT_ORDER_LABELS[option], con.INPUT_ORDER_LABELS[option])
        buttons[key].active = option == current_front or option == current_back
        buttons[key].draw(mx, my, focus_key=fk)
            
    w.draw_small(lang.t("keybindings", "Keybindings"), con.TEXT_COLOR, 420, 305, center=False)
    for i, action in enumerate(con.DEFAULT_KEYBINDINGS):
        key = f"keybind_{action}"
        rect = buttons[key].rect
        binding = game.keybindings.get(action, con.DEFAULT_KEYBINDINGS[action])
        label_text = lang.t(con.KEYBINDINGS_LABELS.get(action, action), con.KEYBINDINGS_LABELS.get(action, action))
        w.draw_small(f"{label_text}:", con.TEXT_COLOR, rect.centerx - 230, rect.centery - 14, center=False)
        listening = getattr(game, "rebind_listening", None) == action
        buttons[key].label = lang.t("key_press", "Press a key...") if listening else helpers.keybinding_label(binding) # Was con.keybinding_label - that function actually lives in helpers.py
        buttons[key].draw(mx, my, focus_key=fk)
                
### About ###
def draw_about(game, mx, my):
    w.draw_title(lang.t("about_1", "About Mati"), con.TEXT_COLOR, con.WIDTH // 2, 90) # Draw the title
    fk = ah.effective_focus_key(game, mx, my) # Get the keyboard focus
    bt.about_buttons.get(game)["back"].draw(mx, my, focus_key=fk)
    w.draw_small(lang.t("about_2", "Mati is an algorithm. A really cool one."), con.TEXT_COLOR, con.WIDTH // 2, 200)
    w.draw_small(lang.t("about_3", "It generates the inner grid and picks some random cells."), con.TEXT_COLOR, con.WIDTH // 2, 230)
    w.draw_small(lang.t("about_4", "The chosen cells are then added together, and the sums are written down."), con.TEXT_COLOR, con.WIDTH // 2, 260)
    w.draw_text(lang.t("about_5", "Created by:"), con.TEXT_COLOR, con.WIDTH // 2, 400) # Draw the created by text
    w.draw_text("Janosch Klawatsch", con.TEXT_COLOR, con.WIDTH // 2, 440) # Draw Janosch Klawatsch
    
    
### Stats ###
def draw_stats(game, mx, my): # Draws the graphical version of the stats
    w.draw_title("Stats", con.TEXT_COLOR, con.WIDTH // 2, 70) # Draw the title
    fk = ah.effective_focus_key(game, mx, my) # Get the keyboard focus
    bt.stats_buttons.get(game)["back"].draw(mx, my, focus_key=fk) # Draw back button with focus option
    
    # Check if the terminal was found
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    
    stats = game.stats # the loaded statistics
    y = 130 # start of first row
    col_x = [100, 170, 300, 425, 600] # Column position
    headers = [lang.t("size", "Size"), lang.t("mode", "Mode"), lang.t("games", "Games"), lang.t("best", "Best"), lang.t("average", "Average")] # Column headers
    for x, text in zip(col_x, headers): # Draw the header row
        w.draw_small(text, con.DIMMED_TEXT_COLOR, x, y, center=False)
    y += 34
    
    # Handle the stats that should be shown
    modes = (("Normal", "normal"), ("Ultra", "ultra")) if terminal_found else (("Normal", "normal"),)
    
    for n in con.DIFFICULTIES: # Every grid size
        for mode_label, mode_key in modes:
            m = stats.get(str(n), {}).get(mode_key, {})
            games = m.get("games", 0)
            best = m.get("best")
            total = m.get("total", 0)
            avg = total // games if games else None
            row = [f"{n}x{n}", mode_label, str(games), helpers.fmt_stat_time(best), helpers.fmt_stat_time(avg)] # The text of each row
            for x, text in zip(col_x, row): # Draw every column
                w.draw_small(text, con.TARGET_COLOR, x, y, center=False)
            y += 30
            
### Achievements ###
def _draw_milestone_tile(rect, title, keys, values, achievements, current_value, index, fmt_value, mx, my, nav_buttons=None):
    screen = w.get_screen()
    hovering = rect.collidepoint(mx, my)
    mouse_visible = bool(pg.mouse.get_visible())
    
    # w.draw_panel_row(rect, False)
    w.draw_achievements_tile(rect)
    w.draw_tiny(title, con.WHITE, rect.centerx, rect.y + 18)
    
    index = max(0, min(index, len(keys) - 1))
    key = keys[index]
    target = values[index]
    unlocked = bool(achievements.get(key))
    color = con.GREEN_NEON if unlocked else con.DIMMED_TEXT_COLOR
    label = con.ACHIEVEMENT_LABELS.get(key, key)
    w.draw_small(label, color, rect.centerx, rect.y + 62)
    w.draw_tiny(f"{index + 1} / {len(keys)}", con.WHITE, rect.centerx, rect.y + 86)
    
    if nav_buttons and hovering and mouse_visible:
        prev_button, next_button = nav_buttons
        if index > 0:
            prev_button.draw(mx, my)
        if index < len(keys) - 1:
            next_button.draw(mx, my)
            
    remaining = max(0, target - current_value)
    frac = helpers.milestone_fraction(current_value, target)
    bar_rect = pg.Rect(rect.x + 16, rect.y + 226, rect.width - 32, 18)
    
    if remaining <= 0:
        w.draw_small(lang.t("milestones_reached", "Reached!"), con.GOLDEN, rect.centerx, rect.y + 170)
    else:
        w.draw_tiny(f"{fmt_value(remaining)} " + lang.t("left", "left"), con.WHITE, rect.centerx, rect.y + 170)
    w.draw_small(f"{fmt_value(current_value)} / {fmt_value(target)}", con.WHITE, rect.centerx, rect.y + 202)
    pg.draw.rect(screen, con.GRID_COLOR, bar_rect, border_radius=9)
    fill_rect = pg.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * frac), bar_rect.height)
    if fill_rect.width > 0:
        pg.draw.rect(screen, con.GREEN, fill_rect, border_radius=9)
    pg.draw.rect(screen, con.BLACK, bar_rect, 1, border_radius=6)
            
    hint = lang.t("hover_to_browse", "Hover to browse") if nav_buttons else lang.t("scroll_to_browse", "Scroll to browse")
    w.draw_tiny(hint, con.DIMMED_TEXT_COLOR, rect.centerx, rect.bottom - 16)
    
    return index
    

def draw_achievements(game, mx, my):
    fk = ah.effective_focus_key(game, mx, my)
    achievements = getattr(game, "achievements", {})
    pages = helpers.ACHIEVEMENT_PAGES
    total_pages = len(pages)
    page_idx = max(0, min(getattr(game, "achievements_page", 0), total_pages - 1))
    game.achievements_page = page_idx
    page = pages[page_idx]
    is_easter_page = page_idx == total_pages - 1
    is_general_page = page_idx == 0
    
    nav_buttons = bt.achievements_nav_buttons.get(game)
    games_nav_buttons = bt.achievements_games_nav_buttons.get(game)
    
    w.draw_title(lang.t("achievements", "Achievements"), con.TEXT_COLOR, con.WIDTH // 2, 60)
    nav_buttons["back"].draw(mx, my, focus_key=fk)
    
    w.draw_text(page["title"], con.TEXT_COLOR, con.WIDTH // 2, 100)
    
    page_unlocked = sum(1 for key in page["keys"] if achievements.get(key))
    w.draw_small(f"{page_unlocked}/{len(page['keys'])}" + lang.t("unlocked", " unlocked"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 128)
    
    if page_idx == 0:
        all_keys = [key for p in pages for key in p["keys"]]
        total_unlocked = sum(1 for key in all_keys if achievements.get(key))
        w.draw_tiny(f"{total_unlocked}/{len(all_keys)}" + lang.t("unlocked_overall", " unlocked overall"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 150)
        
    if is_general_page:
        total_games, total_times_ms = game.general_totals()
        
        games_keys = [f"games_{m}" for m in con.GENERAL_GAME_MILESTONES]
        games_index = getattr(game, "ach_games_index", None)
        if games_index is None:
            games_index = helpers.milestone_default_index(games_keys, achievements)
        games_nav = games_nav_buttons["games_prev"], games_nav_buttons["games_next"]
        game.ach_games_index = _draw_milestone_tile(
            helpers.ACH_GAMES_TILE_RECT, lang.t("games_played", "Games Played"),
            games_keys, con.GENERAL_GAME_MILESTONES, achievements, total_games,
            games_index, str, mx, my, nav_buttons=games_nav,
        )
        
        time_keys = [key for key, _ in con.GENERAL_TIME_MILESTONES]
        time_values_ms = [seconds * 1000 for _, seconds in con.GENERAL_TIME_MILESTONES]
        time_index = getattr(game, "ach_time_index", None)
        if time_index is None:
            time_index = helpers.milestone_default_index(time_keys, achievements)
        game.ach_time_index = _draw_milestone_tile(
            helpers.ACH_TIME_TILE_RECT, lang.t("total_playtime", "Total Play Time"),
            time_keys, time_values_ms, achievements, total_times_ms,
            time_index, helpers.fmt_total_time, mx, my, nav_buttons=None,
        )
    else:    
        y = 178
        row_h = 28
        visible_keys = page["keys"] if not is_easter_page else [key for key in page["keys"] if achievements.get(key)]
    
        if is_easter_page and not visible_keys:
            w.draw_small(lang.t("nothing_achieved", "Nothing achieved yet..."), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, y + 20, center = True)
        else:
            for key in visible_keys:
                unlocked = bool(achievements.get(key))
                color = con.GREEN if unlocked else con.DIMMED_TEXT_COLOR
                label = con.ACHIEVEMENT_LABELS.get(key, key)
                w.draw_small(f"{label}", color, con.WIDTH // 2, y, center=True)
                y += row_h
            
    # --- Page navigation arrows, auto-hidden until the mouse moves or hovers them ---
    prev_button = nav_buttons["prev_page"]
    next_button = nav_buttons["next_page"]
    now = pg.time.get_ticks()
    moved = (mx, my) != getattr(game, "achievements_last_mouse", (mx, my))
    game.achievements_last_mouse = (mx, my)
    hovering_nav = prev_button.is_hovered(mx, my) or next_button.is_hovered(mx, my)
    
    if moved or hovering_nav:
        game.achievements_nav_shown_until = now + con.SCROLLBAR_VISIBLE_MS
    
    mouse_visible = bool(pg.mouse.get_visible())
    nav_visible = (mouse_visible and (now < getattr(game, "achievements_nav_shown_until", 0) or fk in ("prev_page", "next_page"))) or (not mouse_visible and fk in ("prev_page", "next_page"))
    
    if nav_visible and page_idx > 0:
        prev_button.draw(mx, my, focus_key=fk)
                
    if nav_visible and page_idx < total_pages - 1:
        next_button.draw(mx, my, focus_key=fk)
        
    w.draw_tiny(lang.t("page", "Page") + f" {page_idx + 1} / {total_pages}", con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 575)
    
        
### History ###
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
    
    w.draw_text(lang.t("delete_match", "Delete Match?"), con.TEXT_COLOR, con.WIDTH // 2, box_y + 40, center = True) # Text 1
    w.draw_small(lang.t("under_1", "Do you really want to permanently delete"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 85, center=True) # Text 2
    w.draw_small(lang.t("under_2", "this game from your history?"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 110, center=True) # Text 3
    
    fk = ah.effective_focus_key(game, mx, my) # Get the current keyboard
    buttons = bt.delete_confirm_buttons.get(game) # Cached (fixed centered box, only language can change the labels)
    buttons["yes"].draw(mx, my, focus_key=fk) # Draw yes button
    buttons["no"].draw(mx, my, focus_key=fk) # Draw the no button

def draw_history(game, mx, my): # Draw the history
    w.draw_title(lang.t("histo", "History"), con.TEXT_COLOR, con.WIDTH // 2, 50) # Draw the title
    fk = ah.effective_focus_key(game, mx, my) # Get the keyboard focus
    bt.history_back_button.get(game)["back"].draw(mx, my, focus_key=fk) # Draw the back button
    
    if not game.history_entries: # If no saved games found
        w.draw_text(lang.t("no_history_entries", "No game saved until now, but you can change that."), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 200) # Say it
        return # End here
    
    filter_buttons = bt.history_filter_buttons.get(game) # Cached, rebuilt only if ultra entries appear/disappear or the language changes
    size_options = [("size_all", None)] + [(f"size_{n}", n) for n in con.DIFFICULTIES] # Load the size options
    for key, val in size_options: # For each option
        button = filter_buttons[key] # extract one option
        button.active = (game.history_filter_size == val) # Checks if a filter is active
        button.draw(mx, my, focus_key=fk) # Let the buttons draw
    filter_buttons["top10"].active = game.history_filter_top10
    filter_buttons["top10"].draw(mx, my, focus_key=fk) # Draw top 10 button
    if "ultra" in filter_buttons:
        filter_buttons["ultra"].active = game.history_filter_ultra
        filter_buttons["ultra"].draw(mx, my, focus_key=fk) # Draw the ultra button
    
    entries = game.filtered_history() # Define entrie
    if not entries: # If no entry
        w.draw_text(lang.t("no_matches", "No game matchs your filters!"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 230) # Define the empty game message
        return # Do nothing
    
    track = helpers.history_scrollbar_track()
    
    screen = w.get_screen() # Get screen information
    clip_area = pg.Rect(0, track.y - 4, con.WIDTH, track.height + 8) # Define the area for the history files
    screen.set_clip(clip_area) # Connects the screen with the area
    for i, entry in enumerate(entries): # Goes threw the files
        entry_rect = helpers.history_entry_rect(i, game.history_scroll_y)   # Gets the place
        delete_rect = helpers.history_delete_rect(i, game.history_scroll_y) # Gets the cords for the delete
        if entry_rect.bottom < track.y - 4 or entry_rect.top > track.y - 4 + track.height: # Check position
            continue # Everything is fine
        is_hovered = entry_rect.collidepoint(mx, my) # Check the hover
        w.draw_panel_row(entry_rect, is_hovered, focused=(fk == f"entry_{i}")) # Define the row for the select buttons
        w.draw_small(entry["label"], con.WHITE, entry_rect.x + 14, entry_rect.y + 11, center=False) # Declare the button text
        if entry["ultra"] == True: w.draw_small(lang.t("ultra", "ULTRA"), con.SHINE, entry_rect.x + 250, entry_rect.centery) # Show those who are ultramode
        w.draw_small(f'{entry["size"]}x{entry["size"]}', con.WHITE, entry_rect.x + 360, entry_rect.centery) # Declare the button text
        w.draw_small(helpers.format_duration(entry["play_time"]), con.WHITE, entry_rect.x + 480, entry_rect.centery) # Declare the button text
        w.draw_button(delete_rect, "x", delete_rect.collidepoint(mx, my), focused=(fk == f"delete_{i}")) # let the delete buttons be drawm
    screen.set_clip(None) 
    
    w.draw_scrollbar(track, helpers.history_content_height(len(entries)), track.height, -game.history_scroll_y, mx, my, game.history_scroll_last) # draw the scrollbar


### History-Detail ###
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
    
    fk = ah.effective_focus_key(game, mx, my) # Get the keyboard focus
    detail_buttons = bt.history_detail_buttons.get(game) # Cached (fixed layout, only language changes the labels)
    detail_buttons["back"].draw(mx, my, focus_key=fk) # The Back button
    
    n = (len(data["grid"])) # Load n
    offset_x, offset_y = 120 - (n - 4) * 30, 135 - (n - 4) * 20
    hints_x = offset_x + 220 + (n - 4) * 60
    action_y_offset = 8 if n == 7 else 11
    actions = data.get("actions", []) # Load the actions
    
    user_sel, user_dimmed, hints_used, play_time, last_action = re.reconstruct_state(data, game.detail_selected_index) # Find the screen after a action
    
    is_start_view = (game.detail_selected_index == -1) # The synthetic Start entry is selected
    
    highlight_cell = None # No highlighted cell yet
    highlight_color = None # The color will be defined later
    if last_action and not is_start_view: # A real, selected action (never for Start or the end view)
        highlight_cell = (last_action["r"], last_action["c"]) # Get the row/col from the last cell
        if last_action.get("Undone"): # This action was undone
            highlight_color = con.UNDONE_COLOR
        else:
            highlight_color = con.ACTION_HIGHLIGHT_COLOR.get(last_action.get("type"), con.GOLD) # Find out which color it should have
        
    if not data.get("ultra"): # If a old file
        data["ultra"] = False # Say it was no ultra
        
    _draw_full_grid(data["grid"], data["row_sums"], data["col_sums"], user_sel, user_dimmed, n, offset_x, offset_y, highlight_cell, highlight_color, data["ultra"])
    
    footer_y = offset_y + (n + 1) * con.CELL_SIZE + 14 # Bottom
    minutes = play_time // 60000 # Get the minutes
    seconds = play_time // 1000 # Get the seconds
    ms = play_time % 1000 # Get the miliseconds
                
    if minutes < 1:
        time_text = lang.t("time", "Time: ") + f"{seconds:02}:{ms:03}s"
    else:
        time_text = lang.t("time", "Time: ") + f"{minutes}:{(seconds%60):02}:{ms:03}min"
        
    w.draw_tiny(time_text, con.TEXT_COLOR, offset_x, footer_y - 10, center = False)
    
    hints_text = lang.t("hints", "Hints used: ") + f"{hints_used}"
    w.draw_tiny(hints_text, con.TEXT_COLOR, hints_x, footer_y - 10, center = False)
    
    if is_start_view:
        w.draw_tiny(lang.t("action_start", "Action: Start"), con.TEXT_COLOR, offset_x, footer_y + action_y_offset, center = False)
    elif last_action:
        label = lang.t(con.ACTION_LABELS.get(last_action.get("type", "Left"), last_action.get("type", "?")), con.ACTION_LABELS.get(last_action.get("type", "Left"), last_action.get("type", "?")))
        action_text = (lang.t("action", "Action: ") + str(label) + lang.t("row", " (Row: ") + str(last_action['r'] + 1) + lang.t("column", " / Column: ") + str(last_action['c'] + 1) + ")")
        w.draw_tiny(action_text, con.TEXT_COLOR, offset_x, footer_y + action_y_offset, center = False)
    else:
        w.draw_tiny(lang.t("end", "End of game"), con.DIMMED_TEXT_COLOR, offset_x, footer_y + action_y_offset, center = False)
        
    detail_buttons["export_mp4"].draw(mx, my, focus_key=fk) # Button to export as mp4
    
    quality_name, _ = con.EXPORT_QUALITIES[game.export_quality_idx]
    detail_buttons["export_quality"].label = lang.t(quality_name, quality_name)
    detail_buttons["export_quality"].draw(mx, my, focus_key=fk)
    
    fps_value = con.EXPORT_FPS_CHOICES[game.export_fps_idx]
    detail_buttons["export_fps"].label = f"{fps_value} FPS"
    detail_buttons["export_fps"].draw(mx, my, focus_key=fk)
    
    detail_buttons["detail_reset"].draw(mx, my, focus_key=fk) # Button for end view
    
    if game.export_status and pg.time.get_ticks() < game.export_status_until: # If there is a export sucess
        w.draw_tiny(game.export_status, con.DIMMED_TEXT_COLOR, 400, 580, center=True) # Show it under the action list
    
    screen = w.get_screen() # Get the screen informations
    display_actions = helpers.detail_display_actions(data) # get the actions to show
    detail_count = len(display_actions) # len
    track = helpers.DETAIL_SCROLLBAR_TRACK
    w.draw_scrollbar(track, detail_count * 34, 438, -game.detail_scroll_y, mx, my, game.detail_scroll_last) # Draw it BEHIND the entries first
    
        
    clip_area = pg.Rect(530, 120, 250, 440) # Define the area for the actions
    screen.set_clip(clip_area) # Connect it to the screen
    for i, act in enumerate(display_actions):
        rect = helpers.detail_action_rect(i, game.detail_scroll_y) # Get the buttons
        if rect.bottom < 120 or rect.top > 560: # If in the right spot
            continue # Everything is fine
        is_hovered = rect.collidepoint(mx, my) # check hover state
        real_index = i - 1 # get the real index
        is_selected = (game.detail_selected_index == real_index) # check selected state
        key = helpers.detail_key_for(i) # focus key
        w.draw_panel_row(rect, is_hovered, highlighted=is_selected, focused=(fk == key)) # Draw the action buttons
        text_color = con.TEXT_COLOR if is_selected else con.WHITE
        second = (act["time"] // 1000) % 60   # Get the secs
        ms_ = act["time"] % 1000       # Get the milisecs
        minutes = act["time"] // 60000 # Get the minutes
        check = data["play_time"] # Get the time from the full game
        if act.get("synthetic"): # the start
            if check < 60000: line = "00:000s: " + lang.t("start", "Start")
            if check >= 60000: line = "0:00:000min: " + lang.t("start", "Start")
        else:
            label = lang.t(con.ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?")), con.ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?"))) # Define the right label
            if check < 60000: line = f'{second:02}:{ms_:03}s: R{act["r"] + 1}/C{act["c"] + 1} - {label}' # Defines the complete line
            if check >= 60000: line = f'{minutes}:{second:02}:{ms_:03}min: R{act["r"] + 1}/C{act["c"] + 1} - {label}'
        w.draw_tiny(line, text_color, rect.x + 8, rect.y + 7, center=False) # Draw the line on the button
    screen.set_clip(None) # End clip mode
    if not actions: # If there is no real move at all, hint that only Start is there
        w.draw_small(lang.t("action_found", "No action found"), con.DIMMED_TEXT_COLOR, 665, 145) # Say it, below the Start row
           
### Play ###
def draw_play(game, mx, my): # draw the play view
    buttons = bt.play_buttons.get(game) # Cached (fixed layout, only language changes the labels)
    fk = ah.effective_focus_key(game, mx, my)
    buttons["back"].draw(mx, my, focus_key=fk) # Let the back button be drawn
    
    n = game.n # Load the grid size
    offset_x, offset_y = helpers.play_grid_offset(n) # Load the offsets
    
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
        
        buttons["hint"].label = lang.t("hint", "Hint ") + f"({game.hints_left})"
        buttons["hint"].enabled = game.hints_left > 0 and not game.won and not game.paused
        buttons["hint"].draw(mx, my) # If available sends hint find alogrithem threw the grid
        buttons["undo"].enabled = bool(game.current_game_actions) and not game.won and not game.paused
        buttons["undo"].draw(mx, my) # If available gives command to make the last move undone
        buttons["restart"].draw(mx, my, focus_key=fk) # Show the restart button
        buttons["pause"].enabled = not game.won
        buttons["pause"].draw(mx, my) # If available pause the game
        
        if game.timer_enabled: # If timer should be shown
            seconds = (game.play_time // 1000) % 60 # miliseconds to seconds
            minutes = (game.play_time // 60000) # miliseconds in minutes
            if game.timer_ms: # If the miliseconds should also been shown
                ms = game.play_time % 1000 # maximum of 999 ms
                time_string = lang.t("time", "Time: ") + f"{minutes:02}:{seconds:02}:{ms:03}" # Defines how the time should be shown
            else:
                time_string = lang.t("time", "Time: ") + f"{minutes:02}:{seconds:02}" # Defines how to show time
            w.draw_text(time_string, con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT - 20) # Draw the time
            
        if game.won: # If the player won
            w.draw_title(lang.t("won", "You have Won"), con.GREEN, con.WIDTH // 2, con.HEIGHT - 55) # Make a label to give the player feedback
            
        if game.paused: # If the game is paused
            overlay = pg.Surface((con.WIDTH, con.HEIGHT)) # Generate a complete overlay
            overlay.fill(con.PAUSE) # Fill it with background color
            screen.blit(overlay, (0, 0)) # Place it over the whole screen
            w.draw_title(lang.t("paused", "Paused"), con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2 - 45) # Shows that in pause menu
            buttons["menu"].draw(mx, my, focus_key=fk) # Let the back button be drawn
            buttons["break"].draw(mx, my, focus_key=fk) # The return to game button
            buttons["new"].draw(mx, my, focus_key=fk) # Show the restart button
            w.draw_small(lang.t("pressing", "Press ") + str(game.keybindings["pause"]["key"]).capitalize() + (" + CTRL / META " if game.keybindings["pause"]["ctrl"] != False else "") + lang.t("contin", " or the <<Continue>> Button to retrun"), con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2) # Gives a hint of how to return
            

def draw_resume_choice(game, mx, my): # Draw the resume/new decision
    n = game.pending_new_n # The size
    ultra = game.pending_new_ultra # The mode
    mode_label = lang.t("ultra_l", "Ultra") if ultra else lang.t("normal", "Normal") # Readable mode names
    fk = ah.effective_focus_key(game, mx, my) # Get the current keyboard
    
    w.draw_title(lang.t("unfinished", "Unfinished game found"), con.TEXT_COLOR, con.WIDTH // 2, 120) # Title
    w.draw_text(f"{n}x{n} - {mode_label}", con.TEXT_COLOR, con.WIDTH // 2, 175) # Declare which round
    w.draw_small(lang.t("ask_return", "Would you like to resume or to start a new match?"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 220) # Question
    
    buttons = bt.resume_choice_buttons.get(game) # Cached (fixed layout, only language changes the labels)
    buttons["resume"].draw(mx, my, focus_key=fk) # Continue button
    buttons["new"].draw(mx, my, focus_key=fk) # New game button
    buttons["cancel"].draw(mx, my, focus_key=fk) # Cancel back to menu

### Easter eggs views ###
def draw_hannah(game, mx, my): # Creates first easter egg view
    fk = ah.effective_focus_key(game, mx, my)
    if game.hannah_open_index is None:
        w.draw_title("Jay Loves", con.TEXT_COLOR, con.WIDTH // 2, 70)
        bt.hannah_buttons.get(game)["back"].draw(mx, my, focus_key=fk)
        screen = w.get_screen()
        clip_area = pg.Rect(0, con.HANNAH_STRIP_Y - 90, con.WIDTH, 180)
        screen.set_clip(clip_area)
        for i, lvl in enumerate(game.hannah_levels):
            if lvl is None:
                continue
            rect = helpers.hannah_tile_rect(i, game.hannah_scroll_x)
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
        
        track = pg.Rect(40, con.HEIGHT - con.SCROLLBAR_WIDTH - 6, con.HANNAH_VISIBLE_LENGTH - 40, con.SCROLLBAR_WIDTH)
        w.draw_scrollbar(track, hannah_content_width(), con.HANNAH_VISIBLE_LENGTH, -game.hannah_scroll_x, mx, my, game.hannah_scroll_last, vertical=False) # draw the scrollbar
    else:
        lvl = game.hannah_levels[game.hannah_open_index]
        n = con.HANNAH_SIZE
        offset_x, offset_y = helpers.play_grid_offset(n)
        buttons = bt.hannah_play_buttons.get(game)
        buttons["back"].draw(mx, my, focus_key=fk)
        
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
        buttons["undo"].enabled = bool(lvl["actions"])
        buttons["undo"].draw(mx, my)
        