### Mati (Mathematics and tactic intelligence) ###
### V0.6.1 (Beta V1.0.22) ###
### Author: Janosch Klawatsch, 2026-08-29 ###
### alt hover file V0.6.1 ###

### Structure-Plan ###
# - alt_hover.py - Keyboard movement hovering #
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
import pygame as pg

### Own ###
import config as con
import helpers
from helpers import history_scroll_bounds, hannah_scroll_bounds


### -Functions- ###
def _hardcoded_neighbor(game, key, direction):
    match game.state:
        case "MENU":
            neighbors = {
                "start_4": {"down": "start_5", "up": None, "left": None, "right": None},
                "start_5": {"down": "start_6", "up": "start_4", "left": None, "right": None},
                "start_6": {"down": "start_7", "up": "start_5", "left": None, "right": None},
                "start_7": {"down": "settings", "up": "start_6", "left": None, "right": None},
                "settings": {"down": "history", "up": "start_7", "left": None, "right": None},
                "history": {"down": "quit", "up": "settings", "left": None, "right": None},
                "quit": {"down": None, "up": "history", "left": None, "right": None},
            }
            return neighbors.get(key, {}).get(direction)

        case "SETTINGS":
            terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
            if terminal_found:
                neighbors = {
                    "back": {"down": "toggle_history", "up": None, "left": None, "right": "toggle_history"},
                    "toggle_history": {"down": "toggle_sound", "up": "back", "left": "back", "right": "toggle_ultra_timer"},
                    "toggle_sound": {"down": "toggle_alt_control", "up": "toggle_history", "left": "back", "right": f'{"toggle_ultra_timer_ms" if game.ultra_timer_enabled else "toggle_ultra_timer_clock"}'},
                    "toggle_alt_control": {"down": "toggle_timer", "up": "toggle_sound", "left": "back", "right": f'{"toggle_ultra_timer_clock" if game.ultra_timer_enabled else None}'},
                    "toggle_timer": {"down": f'{"toggle_ms" if game.timer_enabled else "stats"}', "up": "toggle_alt_control", "left": "back", "right": "toggle_fullscreen"},
                    "toggle_ms": {"down": "stats", "up": "toggle_timer", "left": "back", "right": "toggle_live_clock"},
                    "toggle_ultra_timer": {"down": f'{"toggle_ultra_timer_ms" if game.ultra_timer_enabled else "toggle_ultra_timer_clock"}', "up": "back", "left": "toggle_history", "right": None},
                    "toggle_ultra_timer_ms": {"down": "toggle_ultra_timer_clock", "up": "toggle_ultra_timer", "left": "toggle_sound", "right": None},
                    "toggle_ultra_timer_clock": {"down": "toggle_fullscreen", "up": f'{"toggle_ultra_timer_ms" if game.ultra_timer_enabled else "toggle_ultra_timer"}', "left": f'{"toggle_alt_control" if game.ultra_timer_enabled else "toggle_sound"}', "right": None},
                    "toggle_fullscreen": {"down": "toggle_live_clock", "up": "toggle_ultra_timer_clock", "left": "toggle_timer", "right": None},
                    "toggle_live_clock": {"down": "about", "up": "toggle_fullscreen", "left": f'{"toggle_ms" if game.timer_enabled else None}', "right": None},
                    "stats": {"down": None, "up": f'{"toggle_ms" if game.timer_enabled else "toggle_timer"}', "left": None, "right": "achievements"},
                    "achievements": {"down": None, "up": f'{"toggle_ms" if game.timer_enabled else "toggle_timer"}', "left": "stats", "right": "about"},
                    "about": {"down": None, "up": "toggle_live_clock", "left": "achievements", "right": None},
                }
            else:
                neighbors = {
                    "back": {"down": "toggle_history", "up": None, "left": None, "right": "toggle_history"},
                    "toggle_history": {"down": "toggle_sound", "up": "back", "left": "back", "right": None},
                    "toggle_sound": {"down": "toggle_alt_control", "up": "toggle_history", "left": "back", "right": None},
                    "toggle_alt_control": {"down": "toggle_timer", "up": "toggle_sound", "left": "back", "right": None},
                    "toggle_timer": {"down": f'{"toggle_ms" if game.timer_enabled else "stats"}', "up": "toggle_alt_control", "left": "back", "right": "toggle_fullscreen"},
                    "toggle_ms": {"down": "stats", "up": "toggle_timer", "left": "back", "right": "toggle_live_clock"},
                    "toggle_fullscreen": {"down": "toggle_live_clock", "up": "toggle_alt_control", "left": "toggle_timer", "right": None},
                    "toggle_live_clock": {"down": "about", "up": "toggle_fullscreen", "left": f'{"toggle_ms" if game.timer_enabled else None}', "right": None},
                    "stats": {"down": None, "up": f'{"toggle_ms" if game.timer_enabled else "toggle_timer"}', "left": None, "right": "achievements"},
                    "achievements": {"down": None, "up": f'{"toggle_ms" if game.timer_enabled else "toggle_timer"}', "left": "stats", "right": "about"},
                    "about": {"down": None, "up": "toggle_live_clock", "left": "achievements", "right": None},
                }
            return neighbors.get(key, {}).get(direction)
        
        case "ACHIEVEMENTS":
            neighbors = {
                "back": {"down": None, "up": None, "left": None, "right": None},
            }
            return neighbors.get(key, {}).get(direction)
        
        case "ADVANCED_SETTINGS":
            front_current = game.settings.get("input_order_front", "action_column_row")
            back_current = game.settings.get("input_order_back", "column_row_action")
            front_unselected = next((opt for opt in con.INPUT_ORDER_FRONT_OPTIONS if opt != front_current), con.INPUT_ORDER_FRONT_OPTIONS[0])
            back_unselected = next((opt for opt in con.INPUT_ORDER_BACK_OPTIONS if opt != back_current), con.INPUT_ORDER_BACK_OPTIONS[0])
            io_keys = {opt: f"input_order_{i}" for i, opt in enumerate(con.INPUT_ORDER_OPTIONS)}
            
            keybind_keys = [f"keybind_{action}" for action in con.DEFAULT_KEYBINDINGS]
            
            neighbors = {
                "back": {"up": None, "down": "game_volume", "left": None, "right": "game_volume"},
                "game_volume": {"up": "back", "down": "terminal_volume", "left": None, "right": io_keys[back_unselected]},
                "terminal_volume": {"up": "game_volume", "down": "toggle_terminal_sound", "left": None, "right": io_keys[front_unselected]},
                "toggle_terminal_sound": {"up": "terminal_volume", "down": "language_dropdown", "left": None, "right": None},
                "language_dropdown": {
                    "up": "toggle_terminal_sound",
                    "down": "language_option_0" if getattr(game, "language_dropdown_open", False) else None,
                    "left": None,
                    "right": keybind_keys[0] if keybind_keys else None,
                },
                io_keys["column_row_action"]: {"up": "back", "down": io_keys["row_column_action"], "left": "game_volume", "right": None},
                io_keys["row_column_action"]: {"up": io_keys["column_row_action"], "down": io_keys["action_column_row"], "left": "game_volume", "right": None},
                io_keys["action_column_row"]: {"up": io_keys["row_column_action"], "down": io_keys["action_row_column"], "left": "terminal_volume", "right": None},
                io_keys["action_row_column"]: {"up": io_keys["action_column_row"], "down": keybind_keys[0] if keybind_keys else None, "left": "terminal_volume", "right": None},
            }
            
            for i, kb_key in enumerate(keybind_keys):
                neighbors[kb_key] = {
                    "up": keybind_keys[i - 1] if i > 0 else io_keys["action_row_column"],
                    "down": keybind_keys[i + 1] if i + 1 < len(keybind_keys) else None,
                    "left": "language_dropdown",
                    "right": None,
                }
                
            if getattr(game, "language_dropdown_open", False):
                option_keys = [f"language_option_{i}" for i in range(len(helpers.available_languages()))]
                for i, opt_key in enumerate(option_keys):
                    neighbors[opt_key] = {
                        "up": option_keys[i - 1] if i > 0 else "language_dropdown",
                        "down": option_keys[i + 1] if i + 1 < len(option_keys) else None,
                        "left": None,
                        "right": None,
                    }
                    
            return neighbors.get(key, {}).get(direction)

        case "ABOUT":
            return {"back": {"down": None, "up": None, "left": None, "right": None}}.get(key, {}).get(direction)

        case "DELETE_HISTORY":
            return {"yes": {"left": None, "right": "no", "up": None, "down": None}, "no": {"left": "yes", "right": None, "up": None, "down": None}}.get(key, {}).get(direction)

        case "RESUME_CHOICE":
            return {"resume": {"right": "new", "left": None, "up": None, "down": None}, "new": {"left": "resume", "right": "cancel", "up": None, "down": None}, "cancel": {"left": "new", "right": None, "up": None, "down": None}}.get(key, {}).get(direction)

        case "HISTORY":
            has_ultra = any(entry.get("ultra") for entry in game.history_entries)
            if has_ultra:
                neighbors = {
                    "back": {"down": "size_all", "up": None, "left": None, "right": "size_all"},
                    "size_all": {"down": "top10", "up": "back", "left": "back", "right": "size_4"},
                    "size_4": {"down": "top10", "up": "back", "left": "size_all", "right": "size_5"},
                    "size_5": {"down": None, "up": "back", "left": "size_4", "right": "size_6"},
                    "size_6": {"down": "ultra", "up": "back", "left": "size_5", "right": "size_7"},
                    "size_7": {"down": "ultra", "up": "back", "left": "size_6", "right": None},
                    "top10": {"down": "entry_0", "up": "size_4", "left": None, "right": "ultra"},
                    "ultra": {"down": "entry_0", "up": "size_6", "left": "top10", "right": None},
                }
            else:
                neighbors = {
                    "back": {"down": "size_all", "up": None, "left": None, "right": "size_all"},
                    "size_all": {"down": "top10", "up": "back", "left": "back", "right": "size_4"},
                    "size_4": {"down": "top10", "up": "back", "left": "size_all", "right": "size_5"},
                    "size_5": {"down": "top10", "up": "back", "left": "size_4", "right": "size_6"},
                    "size_6": {"down": "top10", "up": "back", "left": "size_5", "right": "size_7"},
                    "size_7": {"down": "top10", "up": "back", "left": "size_6", "right": None},
                    "top10": {"down": "entry_0", "up": "size_5", "left": None, "right": None},
                }
            return neighbors.get(key, {}).get(direction)

        case "HISTORY_DETAIL":
            match key:
                case "back":
                    return {"down": "export_mp4", "up": None, "left": None, "right": "export_mp4"}.get(direction)
                
                case "export_mp4":
                    return {"down": "export_quality", "up": "back", "left": "back", "right": None}.get(direction)
                
                case "detail_reset":
                    return {"down": "action_start", "up": "export_quality", "left": "back", "right": None}.get(direction)
                
                case "export_quality":
                    return {"down": "detail_reset", "up": "export_mp4", "left": "back", "right": "export_fps"}.get(direction)
                
                case "export_fps":
                    return {"down": "detail_reset", "up": "export_mp4", "left": "export_quality", "right": None}.get(direction)
            
            if key.startswith("action_"):
                if direction == "up":
                    if key == "action_start":
                        return "detail_reset"
                    index = int(key.split("_", 1)[1])
                    return f"action_{index - 1}" if index > 1 else "action_start"
                if direction == "down":
                    if key == "action_start":
                        return "action_1"
                    index = int(key.split("_", 1)[1])
                    return f"action_{index + 1}"
                if direction == "left":
                    return "back"
                return None
            return None

        case "PLAY":
            if getattr(game, "paused", False):
                return {"menu": {"right": "break", "left": None, "up": None, "down": None}, "break": {"left": "menu", "right": "new", "up": None, "down": None}, "new": {"left": "break", "right": None, "up": None, "down": None}}.get(key, {}).get(direction)
            elif getattr(game, "won", False):
                return {"back": {"right": "restart", "left": None, "up": None, "down": None}, "restart": {"left": "back", "right": None, "up": None, "down": None}}.get(key, {}).get(direction)
            
    return None


def _settings_back_neighbor(game, direction): # To follow the keyboard hover to send the player better back.
    default_next = _hardcoded_neighbor(game, "back", direction)
    remembered = getattr(game, "settings_back_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.settings_back_return = None
            
            return origin_key
        
    return default_next


def _settings_alt_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "toggle_alt_control", direction)
    remembered = getattr(game, "setting_alt_return", None)
    
    if remembered:
        origin_key, _ = remembered
        
        if direction == "down":
            game.setting_alt_return = None
            
            return origin_key
        
    return default_next


def _settings_achievements_up_neighbor(game):
    default_left = "toggle_ms" if game.timer_enabled else "toggle_timer"
    portal = getattr(game, "settings_ach_portal", "left")
    
    return "toggle_live_clock" if portal == "right" else default_left


def _settings_left_terminus_neighbor(game, direction):
    terminus_key = "toggle_ms" if game.timer_enabled else "toggle_timer"
    default_next = _hardcoded_neighbor(game, terminus_key, direction)
    remembered = getattr(game, "settings_left_terminus_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.settings_left_terminus_return = None
            
            return origin_key
        
    return default_next


def _settings_right_terminus_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "toggle_live_clock", direction)
    remembered = getattr(game, "settings_right_terminus_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.settings_right_terminus_return = None
            
            return origin_key
        
    return default_next


def _adv_language_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "language_dropdown", direction)
    remembered = getattr(game, "adv_language_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.adv_language_return = None
            
            return origin_key
        
    return default_next


def _detail_back_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "back", direction)
    remembered = getattr(game, "detail_back_return", None)
        
    if remembered:
        origin_key, _ = remembered
            
        if direction == "right":
            game.detail_back_return = None
                
            return origin_key
            
    return default_next


def _detail_export_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "export_mp4", direction)
    remembered = getattr(game, "detail_export_return", None)
    
    if remembered:
        origin_key, _ = remembered
        
        if direction == "down":
            game.detail_export_return = None
            
            return origin_key
        
    return default_next


def _hannah_back_neighbor(game):
    origin_key, _ = game.hannah_back_return
    game.hannah_back_return = None
    
    return origin_key


def _history_back_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "back", direction)
    remembered = getattr(game, "history_back_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.history_back_return = None
            
            return origin_key
        
    return default_next


def _history_top10_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "top10", direction)
    remembered = getattr(game, "history_top10_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.history_top10_return = None
            
            return origin_key
    
    return default_next


def _history_top10_down_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "top10", direction)
    remembered = getattr(game, "history_top10_down_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.history_top10_down_return = None
            
            return origin_key
    
    return default_next


def _history_ultra_neighbor(game, direction):
    default_next = _hardcoded_neighbor(game, "ultra", direction)
    remembered = getattr(game, "history_ultra_return", None)
    
    if remembered:
        origin_key, arrival_direction = remembered
        
        if direction == con.OPPOSITE_DIRECTION.get(arrival_direction):
            game.history_ultra_return = None
            
            return origin_key
    
    return default_next


def _history_size5_down_neighbor(game):
    last = getattr(game, "history_bottom_last", None)
    if last in ("top10", "ultra"):
        return last
    return "entry_0"


# Real navigation blocks
def _move_focus_history(game, order, direction):
    lookup = dict(order) # key -> rect
    key = game.focus_key # where we are
    entries = game.filtered_history()
    header_keys = [k for k, _ in order if not (k.startswith("entry_") or k.startswith("delete_"))] # not a row just in one
    has_ultra = "ultra" in lookup

    if key == "top10" and direction == "down":
        if has_ultra:
            target = "entry_0"
        else:
            target = _history_top10_down_neighbor(game, direction)
        if target in lookup:
            game.focus_key = target
            ensure_focus_visible(game, order)
            return True

    if key.startswith("delete_") and direction == "up":
        if has_ultra:
            if "ultra" in lookup:
                game.focus_key = "ultra"
                ensure_focus_visible(game, order)
                return True
        else:
            game.focus_key = "top10"
            ensure_focus_visible(game, order)
            game.history_top10_down_return = (key, direction)
            return True

    if key.startswith("entry_") or key.startswith("delete_"):
        idx = int(key.split("_", 1)[1])
        column = "delete" if key.startswith("delete_") else "entry"
        game.history_list_column = column
        if direction in ("left", "right"):
            other = "delete" if column == "entry" else "entry"
            other_key = f"{other}_{idx}"
            if other_key in lookup:
                game.focus_key = other_key
                game.history_list_column = other
                ensure_focus_visible(game, order)
            return True
        if direction == "down":
            if idx + 1 < len(entries):
                game.focus_key = f"{column}_{idx + 1}"
                ensure_focus_visible(game, order)
            else:
                game.focus_key =  f"{column}_0"
                ensure_focus_visible(game, order)
            return True
        if direction == "up":
            if idx - 1 >= 0:
                game.focus_key = f"{column}_{idx - 1}"
                ensure_focus_visible(game, order)
            else:
                source = getattr(game, "history_bottom_last", None)
                if source and source in header_keys:
                    game.focus_key = source
                elif header_keys:
                    game.focus_key = header_keys[-1]
                ensure_focus_visible(game, order)
            return True
        return True
    
    if key in ("top10", "ultra"):
        if direction == "down" and entries:
            column = getattr(game, "history_list_column", "entry")
            game.focus_key = f"{column}_0"
            ensure_focus_visible(game, order)
            return True
        
    return None


def _move_focus_hannah(game, order, direction): # navigation
    lookup = dict(order) # key -> rect
    key = game.focus_key # where we are
    tile_keys = [k for k, _ in order if k.startswith("tile_")] # Get ordered tiles
    
    if key.startswith("tile_"): # current on a tile
        idx = tile_keys.index(key) if key in tile_keys else 0 # the position
        if direction == "right": # move on tile further
            if idx + 1 < len(tile_keys): # if there is a next tile
                game.focus_key = tile_keys[idx + 1] # move there
                ensure_focus_visible(game, order) # keep it visible
        elif direction == "up":
            game.hannah_back_return = (key, "up")
            game.focus_key = "back"
            ensure_focus_visible(game, order)
        elif direction == "down": 
            return # do nothing
        else: # must be left
            if idx - 1 >= 0: # if there is a prev tile
                game.focus_key = tile_keys[idx - 1] # move there
                ensure_focus_visible(game, order) # keep it visible
            elif "back" in lookup: # Got to back button
                game.focus_key = "back" # jump there
                ensure_focus_visible(game, order) # keep it visible
    else: # on back button
        if (direction == "right" and tile_keys) or (direction == "down" and tile_keys and not getattr(game, "hannah_back_return", None)): # enter the strip
            game.focus_key = tile_keys[0] # jump there
            ensure_focus_visible(game, order) # keep it visible
        elif direction == "down" and tile_keys and getattr(game, "hannah_back_return", None):
            nxt = _hannah_back_neighbor(game)
            game.focus_key = nxt
            ensure_focus_visible(game, order)
             
            
def focus_order(game): # Gives the orderd, navigable elements in the current screen
    order = [] # Start empty
    
    match game.state:
        case "MENU": # Main menu
            order = list(helpers.menu_buttons().items()) # Every menu button
            
        case "SETTINGS": # Setting screen
            order = list(helpers.settings_buttons(game).items()) # Every setting button
            
        case "ADVANCED_SETTINGS":
            order = list(helpers.advanced_settings_layout(game).items())
    
        case "ABOUT": # About screen
            order = [("back", helpers.BTN_BACK)] # Just the back button
    
        case "STATS": # Stats screen
            order = [("back", helpers.BTN_BACK)] # Just the back button
            
        case "ACHIEVEMENTS":
            order = [("back", helpers.BTN_BACK)] # Just the back button
            page_idx = max(0, min(getattr(game, "achievements_page", 0), len(con.ACHIEVEMENT_PAGES) - 1))
            prev_rect = helpers.ACH_PREV_RECT
            next_rect = helpers.ACH_NEXT_RECT
            if page_idx > 0:
                order.append(("prev_page", prev_rect))
            if page_idx < len(con.ACHIEVEMENT_PAGES) - 1:
                order.append(("next_page", next_rect))
    
        case "HISTORY": # History screen
            order = [("back", helpers.BTN_BACK)] # Back button first
            if game.history_entries: # Must have entries 
                order += list(helpers.history_filter_buttons(game).items()) # Add the filter buttons
                for i, _ in enumerate(game.filtered_history()): # Every visible entry
                    order.extend([
                        (f"entry_{i}", helpers.history_entry_rect(i, game.history_scroll_y)),
                        (f"delete_{i}", helpers.history_delete_rect(i, game.history_scroll_y))
                    ])
                    
        case "HISTORY_DETAIL": # Detail view of a match
            order = [
                ("back", helpers.BTN_BACK),
                ("export_mp4", helpers.DETAIL_EXPORT_BUTTON),
                ("export_quality", helpers.DETAIL_QUALITY_BUTTON),
                ("export_fps", helpers.DETAIL_FPS_BUTTON),
                ("detail_reset", helpers.DETAIL_RESET_BUTTON),
            ]
            
            if game.selected_history_data: # If a match is loaded
                display_actions = helpers.detail_display_actions(game.selected_history_data) # The actions
                for i in range(len(display_actions)): # For every action
                    order.append((helpers.detail_key_for(i), helpers.detail_action_rect(i, game.detail_scroll_y))) # Navigate threw the actions
                    
        case "DELETE_HISTORY": # Delete confirmation
            box_w, box_h = 440, 220 # The size
            box_x = (con.WIDTH - box_w) // 2 # Same x
            box_y = (con.HEIGHT - box_h) // 2 # Same y
            
            order = [
                ("yes", pg.Rect(box_x + 60, box_y + 150, 130, 42)),
                ("no", pg.Rect(box_x + 250, box_y + 150, 130, 42))
            ]
            
        case "RESUME_CHOICE": # Paused game detected
            buttons = helpers.resume_choice_buttons() # Load the buttons
            order = [
                ("resume", buttons["resume"]),
                ("new", buttons["new"]),
                ("cancel", buttons["cancel"])
            ]
    
        case "HANNAH":
            if getattr(game, "hannah_open_index", None) is None: # If in hannah menu overview
                order = [("back", helpers.BTN_BACK)] # Back button
                for i, lvl in enumerate(getattr(game, "hannah_levels", [])): # For every level
                    if lvl is None: # Empty signes ignore
                        continue # skip
                    order.append((f"tile_{i}", helpers.hannah_tile_rect(i, game.hannah_scroll_x))) # Add the grids
    
        case "PLAY":
            if getattr(game, "paused", False): # Pause menu buttons
                buttons = helpers.play_buttons()
                order = [
                    ("menu", buttons["menu"]),
                    ("break", buttons["break"]),
                    ("new", buttons["new"])
                ]
    
            elif getattr(game, "won", False): # Win screen buttons
                buttons = helpers.play_buttons()
                order = [
                    ("back", buttons["back"]),
                    ("restart", buttons["restart"])
                ]
    
    return order # Give them back
                                            
                                             
def move_focus(game, direction): # How to move the focus
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    order = focus_order(game) # Load the order
    if not order: # If the load failed
        return # nothing to do
    keys = [k for k, _ in order] # Get every key
    key = game.focus_key
    state = game.state
    if key not in keys:
        game.focus_key = keys[0]
        return
    
    nxt = _hardcoded_neighbor(game, key, direction)
    
    if state == "HISTORY":
        if key == "back":
            nxt = _history_back_neighbor(game, direction)
        else:
            if nxt == "back" and key != "back":
                game.history_back_return = (key, direction)
                
        if key == "size_5" and direction == "down" and nxt is None:
            nxt = _history_size5_down_neighbor(game)
                
        if key == "top10":
            nxt = _history_top10_neighbor(game, direction)
        else:
            if nxt == "top10" and key != "top10":
                game.history_top10_return = (key, direction)
                
        if key == "ultra":
            nxt = _history_ultra_neighbor(game, direction)
        else:
            if nxt == "ultra" and key != "ultra":
                game.history_ultra_return = (key, direction)
                
        if nxt in ("top10", "ultra"):
            game.history_bottom_last = nxt
            
        handled = _move_focus_history(game, order, direction)
        if handled:
            return
        
        if nxt and nxt in keys:
            game.focus_key = nxt
            ensure_focus_visible(game, order)
        return
    
    if state == "HANNAH" and getattr(game, "hannah_open_index", None) is None:    
        _move_focus_hannah(game, order, direction)
        return
    
    if state == "SETTINGS":
        if key == "back":
            nxt = _settings_back_neighbor(game, direction)
        else:
            if nxt == "back" and key != "back":
                game.settings_back_return = (key, direction)
        
        if not terminal_found:       
            if key == "toggle_alt_control":
                nxt = _settings_alt_neighbor(game, direction)
            else:
                if nxt == "toggle_alt_control" and key != "toggle_alt_control" and direction == "up":
                    game.setting_alt_return = (key, direction)
                    
        if key == "achievements" and direction == "up":
            nxt = _settings_achievements_up_neighbor(game)
        
        left_terminus = "toggle_ms" if game.timer_enabled else "toggle_timer"
        if key == left_terminus:
            nxt = _settings_left_terminus_neighbor(game, direction)
        else:
            if nxt == left_terminus and key != left_terminus and key != "toggle_timer" and key != "toggle_alt_control":
                game.settings_left_terminus_return = (key, direction)
                
        if key == "toggle_live_clock":
            nxt = _settings_right_terminus_neighbor(game, direction)
        else:
            if nxt == "toggle_live_clock" and key != "toggle_live_clock" and key != "toggle_fullscreen":
                game.settings_right_terminus_return = (key, direction)
            
        if nxt == "achievements":
            if key in ("stats", "toggle_ms", "toggle_timer"):
                game.settings_ach_portal = "left"
            elif key in ("about", "toggle_live_clock"):
                game.settings_ach_portal = "right"
                
    if state == "ADVANCED_SETTINGS":
        if key == "language_dropdown":
            nxt = _adv_language_neighbor(game, direction)
        else:
            if nxt == "language_dropdown" and key != "language_dropdown":
                game.adv_language_return = (key, direction)
    
    if state == "HISTORY_DETAIL":
        if key == "back":
            nxt = _detail_back_neighbor(game, direction)
        else:
            if nxt == "back" and key != "back":
                game.detail_back_return = (key, direction)
                
        if key == "export_mp4":
            nxt = _detail_export_neighbor(game, direction)
        else:
            if nxt == "export_mp4" and key != "back":
                game.detail_export_return = (key, direction)
    
    if nxt is None:
        return
    if nxt in keys:
        game.focus_key = nxt
        ensure_focus_visible(game, order)
            
            
def effective_focus_key(game, mx, my):
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
        
    moved = (mx, my) != getattr(game, "last_mouse_pos", (mx, my))
    game.last_mouse_pos = (mx, my)
    if hovered_key != getattr(game, "mouse_hover_key", None) or moved: # mouse moved
        pg.mouse.set_visible(True)
        game.mouse_hover_key = hovered_key # remember the new one
        game.mouse_hover_start = now # get the time
        
    if getattr(game, "focus_lock_until", 0) > now:
        return game.focus_key
    idle_ms = now - getattr(game, "last_key_time", 0)
    hover_ms = now - getattr(game, "mouse_hover_start", 0) # how long no input
    if idle_ms >= con.FOCUS_IDLE_MS and hovered_key and hover_ms >= con.FOCUS_IDLE_MS:
        pg.mouse.set_visible(False)
        return hovered_key # if mouse rest for long enough on a button without any other moves
    
    return game.focus_key
            
            
def ensure_focus_visible(game, order): # Makes sure in lists the focused is visible
    lookup = dict(order)
    rect = lookup.get(game.focus_key)
    if rect is None:
        return
    key = game.focus_key
    state = game.state
    if state == "HISTORY" and (key.startswith("entry_") or key.startswith("delete_")): # In the history list
        margin = con.ENTRY_SPACING // 2
        track = helpers.history_scrollbar_track()
        visible_top = track.y - 4
        visible_bottom = visible_top + track.height
        if rect.top < visible_top: # Above the visible area
            game.history_scroll_y += (visible_top - rect.top) + margin # Scroll down to show it
            game.history_scroll_y = min(game.history_scroll_y, 0) # never scroll over the top
            game.history_scroll_last = pg.time.get_ticks() # remeber the scrollbar time
        elif rect.bottom > visible_bottom: # Below the visible area
            game.history_scroll_y -= (rect.bottom - visible_bottom) + margin # Scroll up
            game.history_scroll_y = max(history_scroll_bounds(len(game.filtered_history())), game.history_scroll_y)
            game.history_scroll_last = pg.time.get_ticks() # remember the time
    elif state == "HISTORY_DETAIL" and key.startswith("action_"): # In the action list
        clip_top = 120
        clip_bottom = 560
        if rect.top < clip_top: # Above the visible area
            game.detail_scroll_y += (clip_top - rect.top) # Scroll down
            game.detail_scroll_last = pg.time.get_ticks() # remember the time
        elif rect.bottom > clip_bottom: # Below the visible area
            game.detail_scroll_y -= (rect.bottom - clip_bottom) # Scroll up
            count = len(helpers.detail_display_actions(game.selected_history_data)) if game.selected_history_data else 0
            min_scroll = -max(0, (count * 34) - 440)
            game.detail_scroll_y = max(min_scroll, min(game.detail_scroll_y, 0))
            game.detail_scroll_last = pg.time.get_ticks() # remember the time
    elif state == "HANNAH" and key.startswith("tile_"):
        if rect.left < 40:
            game.hannah_scroll_x += (40 - rect.left)
            game.hannah_scroll_x = max(hannah_scroll_bounds(), min(0, game.hannah_scroll_x))
            game.hannah_scroll_last = pg.time.get_ticks()
        elif rect.right > con.WIDTH - 40:
            game.hannah_scroll_x -= (rect.right - (con.WIDTH - 40))
            game.hannah_scroll_x = max(hannah_scroll_bounds(), min(0, game.hannah_scroll_x))
            game.hannah_scroll_last = pg.time.get_ticks()


