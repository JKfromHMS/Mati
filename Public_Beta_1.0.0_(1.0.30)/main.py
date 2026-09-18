"""Entry point and the main event loop that ties all modules together."""

import sys    
import pygame as pg
from datetime import datetime as dt

import alt_hover as ah
import buttons as bt
import config as con
import screens as s
import widgets as w
from game import Game
import helpers
from audio import Sounds
import terminal as t
import lang

### -Functions- ###
def toggle_fullscreen(fullscreen, windowed_size) -> tuple[bool, pg.Surface]:
    """Toggles between fullscreen and normal window."""
    if fullscreen:
        real_screen = pg.display.set_mode(windowed_size, pg.RESIZABLE)
        return False, real_screen
    
    info = pg.display.Info()
    real_screen = pg.display.set_mode((info.current_w, info.current_h), pg.FULLSCREEN)
    return True, real_screen


### Adaptive rendering ###
def _ms_until_next_wall_second():
    """Return ms until the wall-clock second flips (``dt.now()`` based)."""
    return max(1, 1000 - (dt.now().microsecond // 1000))


def _ms_until_next_10ms_tick(now):
    """Return ms until the next 10 ms boundary of an uptime value."""
    return max(1, con.CLOCK_MS_UPDATE_MS - (now % con.CLOCK_MS_UPDATE_MS))


def _live_clock_text():
    """Return the currently displayed live-clock text (``HH:MM:SS``)."""
    return dt.now().strftime("%H:%M:%S")


def _normal_timer_key(game):
    """Return the displayed normal-timer text, or ``None`` when hidden/paused."""
    if game.state != "PLAY" or not getattr(game, "timer_enabled", False):
        return None
    
    if game.won or game.paused:
        return ("frozen", game.play_time // 1000 if not getattr(game, "timer_ms", False) else game.play_time // 10)
    
    if getattr(game, "timer_ms", False):
        return ("run_ms", game.play_time // 10)
    
    return ("run_s", game.play_time // 1000)


def _ultra_clock_text():
    """Return the currently displayed ultra/terminal-clock text."""
    return dt.now().strftime("%H:%M:%S")


def _note_redraw_done(r, game, active_terminal):
    """Remember the currently displayed time texts after a redraw."""
    r["last_clock_s"] = _live_clock_text() if getattr(game, "live_clock_enabled", False) else None
    r["last_timer_key"] = _normal_timer_key(game)
    
    if active_terminal is not None:
        r["last_ultra_clock_s"] = (
            _ultra_clock_text()
            if active_terminal.settings.get("ultra_timer_show_clock", False)
            else None
        )
        r["last_ultra_timer_key"] = active_terminal.ultra_timer_key()
    else:
        r["last_ultra_clock_s"] = None
        r["last_ultra_timer_key"] = None


def _new_redraw_state():
    """Return fresh per-session state for the adaptive redraw gate."""
    return {
        "size_key": None, "last_mx": None, "last_my": None, "last_export_pct": -1, "next_timed_at": None,
        "last_clock_s": None, "last_timer_key": None, "last_ultra_clock_s": None, "last_ultra_timer_key": None
    }


def _scheduled_redraw_at(game, active_terminal, now):
    """Return the earliest future time (in ms) the screen should be redrawn, or ``None``."""
    times = []
    
    if active_terminal:
        times.append(((now // con.TERMINAL_BLINK_MS) + 1) * con.TERMINAL_BLINK_MS)
        
    if getattr(game, "live_clock_enabled", False):
        if getattr(game, "live_clock_ms", False):
            times.append(now + _ms_until_next_10ms_tick(now))
        else:
            times.append(now + _ms_until_next_wall_second())
            
    if game.state == "PLAY" and getattr(game, "timer_enabled", False) and not game.won and not game.paused:
        if getattr(game, "timer_ms", False):
            times.append(now + _ms_until_next_10ms_tick(game.play_time))
        else:
            times.append(now + max(1, 1000 - (game.play_time % 1000)))
            
    if active_terminal is not None:
        if active_terminal.settings.get("ultra_timer_show_clock", False):
            times.append(now + _ms_until_next_wall_second())
            
        ultra_key = active_terminal.ultra_timer_key(now)
        if ultra_key is not None:
            if ultra_key[0] == "run_ms":
                elapsed_ms = active_terminal.ultra_elapsed_ms(now) or 0
                times.append(now + _ms_until_next_10ms_tick(elapsed_ms))
            elif ultra_key[0] == "run_s":
                elapsed_ms = active_terminal.ultra_elapsed_ms(now) or 0
                times.append(now + max(1, 1000 - (elapsed_ms % 1000)))
                
    if game.state == "PLAY" and getattr(game, "last_hint_cell", None) is not None:
        expiry = getattr(game, "hint_flash_timer", 0) + con.HINT_FLASH_MS
        if now < expiry:
            times.append(expiry)
            
    for attr in ("history_scroll_last", "detail_scroll_last", "hannah_scroll_last"):
        last = getattr(game, attr, -10 ** 9)
        if now - last < con.SCROLLBAR_VISIBLE_MS:
            times.append(last + con.SCROLLBAR_VISIBLE_MS)
            
    if game.state == "ACHIEVEMENTS":
        nav_until = getattr(game, "achievements_nav_shown_until", 0)
        if now < nav_until:
            times.append(nav_until)
            
    idle_hide = getattr(game, "last_move_time", 0) + con.MOUSE_IDLE_HIDE_MS
    if now < idle_hide or game.state == "TERMINAL":
        times.append(idle_hide)
        
    if getattr(game, "alt_control", False) and game.state != "TERMINAL":
        hop = getattr(game, "mouse_hover_start", 0) + con.FOCUS_IDLE_MS
        if now < hop:
            times.append(hop)
            
    if (getattr(game, "export_status", None)
            and getattr(game, "export_popup_allowed", True)
            and now < getattr(game, "export_status_until", 0)
            and game.state not in ("HISTORY_DETAIL", "TERMINAL", "HANNAH")
            and s.popup_animation_running()):
        times.append(now + con.POPUP_REDRAW_INTERVAL_MS)
        
    if not times:
        return None
    return min(times)


def _needs_redraw(r, game, active_terminal, mx, my, real_w, real_h, now, had_event, state_changed, forced):
    """Decide whether this frame must be drawn and blitted to the window."""
    if forced or had_event or state_changed:
        return True
    
    mouse_moved = (mx, my) != (r["last_mx"], r["last_my"])
    r["last_mx"], r["last_my"] = mx, my
    
    if (real_w, real_h) != r["size_key"]:
        r["size_key"] = (real_w, real_h)
        return True
        
    if mouse_moved:
        return True
        
    if getattr(game, "exporting", False):
        pct = int(round(min(1.0, getattr(game, "export_progress", 0.0)) * 100))
        if pct != r["last_export_pct"]:
            return True
            
    if getattr(game, "scrollbar_drag", None) or getattr(game, "slider_drag", None):
        return True
        
    if getattr(game, "_repeat_direction", None) is not None:
        return True
        
    held = False
    if active_terminal is not None:
        try:
            pressed = pg.key.get_pressed()
            held = any(pressed[i] for i in range(len(pressed)))
        except TypeError:
            held = bool(pg.key.get_focused())
        if held:
            return True
            
    if getattr(game, "live_clock_enabled", False):
        if _live_clock_text() != r.get("last_clock_s"):
            return True
            
    if _normal_timer_key(game) != r.get("last_timer_key"):
        return True
        
    if active_terminal is not None:
        if active_terminal.settings.get("ultra_timer_show_clock", False):
            if _ultra_clock_text() != r.get("last_ultra_clock_s"):
                return True
        elif r.get("last_ultra_clock_s") is not None:
            return True
            
        if active_terminal.ultra_timer_key(now) != r.get("last_ultra_timer_key"):
            return True
            
    nxt = r["next_timed_at"]
    if nxt is not None and now >= nxt:
        return True
        
    return False


### Main ###
def main():
    pg.init()
    real_screen = pg.display.set_mode((con.WIDTH, con.HEIGHT), pg.RESIZABLE)
    pg.display.set_caption("Mati")
    virtual_screen = pg.Surface((con.WIDTH, con.HEIGHT))
    
    title_font = pg.font.SysFont("arial", 48, bold=True)
    font = pg.font.SysFont("arial", 28, bold=True)
    small_font = pg.font.SysFont("arial", 22)
    tiny_font = pg.font.SysFont("arial", 16)
    w.init(virtual_screen, title_font, font, small_font, tiny_font)
    w.set_real_screen(real_screen)
    
    sounds = Sounds()
    game = Game(sounds)
    clock = pg.time.Clock()
    w.set_scale_mode(getattr(game, "scale_mode", "auto"))
    w.set_render_quality(getattr(game, "render_quality", 1))
    
    game.last_mouse_pos = pg.mouse.get_pos()
    game.last_move_time = pg.time.get_ticks()
    
    fullscreen = False
    windowed_size = (con.WIDTH, con.HEIGHT)
    pending_click = None
    active_terminal = None
    prev_state = game.state
    redraw = _new_redraw_state()

    while True:
        had_event = False
        forced_redraw = False
        state_changed = game.state != prev_state
        
        if state_changed:
            game.focus_index = 0
            game.focus_key = game.return_focus.pop(game.state, None)
            game.focus_lock_until = pg.time.get_ticks() + 200
            prev_state = game.state
            
        virtual_screen.fill(con.BG_COLOR)
        current_time = pg.time.get_ticks()
        
        music = getattr(sounds, "music", None)
        if music is not None:
            music.update(game.state, game.paused, sounds.enabled, sounds.volume)
        
        real_w, real_h = real_screen.get_size()
        _sc, scaled_w, scaled_h, offset_x, offset_y, _flt = w.layout_for(real_w, real_h)
        
        raw_mx, raw_my = pg.mouse.get_pos()
        vx = (raw_mx - offset_x) / _sc
        vy = (raw_my - offset_y) / _sc
        mouse_inside = 0 <= vx <= con.WIDTH and 0 <= vy <= con.HEIGHT
        mx = max(0, min(con.WIDTH, vx))
        my = max(0, min(con.HEIGHT, vy))
        
        for event in pg.event.get():
            had_event = True
            
            if event.type == pg.QUIT:
                game.stash_current_game()
                if active_terminal and active_terminal.ultra_game:
                    active_terminal.ultra_game.stash_current_game(o_time=pg.time.get_ticks() - active_terminal.timer)
                pg.quit()
                sys.exit()
                
            elif game.exporting and not game.export_backgrounded and event.type == pg.MOUSEBUTTONDOWN:
                game.export_backgrounded = True
                continue
                
            elif event.type == pg.VIDEORESIZE:
                if not fullscreen:
                    new_w = max(event.w, con.MIN_REAL_WIDTH)
                    new_h = max(event.h, con.MIN_REAL_HEIGHT)
                    real_screen = pg.display.set_mode((new_w, new_h), pg.RESIZABLE)
                    windowed_size = (new_w, new_h)
                    w.set_real_screen(real_screen)
            
            elif event.type == pg.KEYDOWN:
                pg.mouse.set_visible(True)
                
                if getattr(game, "rebind_listening", None):
                    MODIFIER_KEYS = {
                        pg.K_LCTRL, pg.K_RCTRL, pg.K_LMETA, pg.K_RMETA,
                        pg.K_LALT, pg.K_RALT, pg.K_LSHIFT, pg.K_RSHIFT,
                    }
                    if event.key in MODIFIER_KEYS:
                        continue
                    
                    action = game.rebind_listening
                    game.rebind_listening = None
                    
                    if event.key != pg.K_ESCAPE:
                        has_ctrl = bool(event.mod & (pg.KMOD_CTRL | pg.KMOD_META))
                        key_name = pg.key.name(event.key)
                        game.set_keybinding(action, key_name, has_ctrl)
                    continue

                if event.key not in (pg.K_SPACE, pg.K_RETURN, pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN):
                    game.last_key_time = pg.time.get_ticks()

                if game.matches_binding("fullscreen", event):
                    fullscreen, real_screen = toggle_fullscreen(fullscreen, windowed_size)
                    game.is_fullscreen = fullscreen
                    w.set_real_screen(real_screen)
                elif event.key == pg.K_ESCAPE and fullscreen:
                    fullscreen, real_screen = toggle_fullscreen(fullscreen, windowed_size)
                    game.is_fullscreen = fullscreen
                    w.set_real_screen(real_screen)
                elif game.matches_binding("pause", event) and game.state == "PLAY":
                    game.toggle_pause()
                elif game.matches_binding("new_round", event) and game.state == "PLAY":
                    game.restart_same()
                elif game.matches_binding("menu", event) and game.state in ("MENU", "SETTINGS", "ABOUT", "HISTORY", "HISTORY_DETAIL", "DELETE_HISTORY", "EXPORT_EXISTS", "RESUME_CHOICE", "HANNAH", "PLAY", "TERMINAL", "STATS", "ACHIEVEMENTS", "ADVANCED_SETTINGS", "TUTORIAL"):
                    if game.state == "PLAY":
                        game.stash_current_game()
                    elif game.state == "TERMINAL" and active_terminal:
                        active_terminal.close()
                    elif game.state == "TUTORIAL":
                        game.close_tutorial(destination="MENU")
                    game.state = "MENU"
                elif game.matches_binding("undo", event) and game.state == "PLAY":
                    game.undo()
                elif game.alt_control and game.state == "PLAY" and game.paused:
                    if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                        direction = {pg.K_UP: "up", pg.K_DOWN: "down", pg.K_LEFT: "left", pg.K_RIGHT: "right"}[event.key]
                        ah.move_focus(game, direction)
                    elif event.key in (pg.K_SPACE, pg.K_RETURN):
                        key = ah.effective_focus_key(game, mx, my)
                        lookup = dict(ah.focus_order(game))
                        if key is not None and key in lookup:
                            rect = lookup[key]
                            handle_click(game, pg.time.get_ticks(), rect.centerx, rect.centery, 1)
                        elif game.focus_key == "break":
                            game.toggle_pause()
                elif game.alt_control and game.state == "PLAY" and game.won:
                    if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                        game.last_key_time = pg.time.get_ticks()
                        direction = {pg.K_UP: "up", pg.K_DOWN: "down", pg.K_LEFT: "left", pg.K_RIGHT: "right"}[event.key]
                        ah.move_focus(game, direction)
                    elif event.key in (pg.K_SPACE, pg.K_RETURN):
                        game.last_key_time = pg.time.get_ticks()
                        key = ah.effective_focus_key(game, mx, my)
                        lookup = dict(ah.focus_order(game))
                        if key is not None and key in lookup:
                            rect = lookup[key]
                            handle_click(game, pg.time.get_ticks(), rect.centerx, rect.centery, 1)
                elif game.alt_control and game.state == "PLAY" and not game.paused and not game.won:
                    if event.key in(pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT): 
                        game.move_cursor(event.key)
                    elif event.key in (pg.K_l, pg.K_SPACE, pg.K_RETURN): 
                        game.click_cell(game.cursor_r, game.cursor_c)
                    elif game.matches_binding("right_click", event): 
                        game.click_cell(game.cursor_r, game.cursor_c, right_click=True)
                    elif event.key == pg.K_u: 
                        game.undo()
                    elif game.matches_binding("hint", event): 
                        game.use_hint()
                elif game.alt_control and game.state == "HANNAH" and game.hannah_open_index is not None:
                    if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                        game.move_cursor(event.key)
                    elif event.key in (pg.K_l, pg.K_SPACE, pg.K_RETURN):
                        game.hannah_click_cell(game.cursor_r, game.cursor_c)
                    elif game.matches_binding("right_click", event):
                        game.hannah_click_cell(game.cursor_r, game.cursor_c, right_click=True)
                    elif game.matches_binding("hint", event):
                        game.hannah_undo()
                elif game.alt_control and game.state == "PLAY" and event.key == pg.K_n:
                    game.restart_same()
                elif event.key == pg.K_RIGHT and (event.mod & (pg.KMOD_CTRL | pg.KMOD_META)) and game.state == "SETTINGS":
                    game.return_focus["SETTINGS"] = game.focus_key
                    game.language_dropdown_open = False
                    game.state = "ADVANCED_SETTINGS"
                elif event.key == pg.K_LEFT and (event.mod & (pg.KMOD_CTRL | pg.KMOD_META)) and game.state == "ADVANCED_SETTINGS":
                    game.return_focus["ADVANCED_SETTINGS"] = game.focus_key
                    game.language_dropdown_open = False
                    game.state = "SETTINGS"
                elif game.alt_control and game.state == "ADVANCED_SETTINGS" and getattr(game, "slider_dot_mode", False) and game.focus_key in ("game_volume", "terminal_volume") and event.key in (pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN):
                    game.last_key_time = pg.time.get_ticks()
                    if event.key in (pg.K_UP, pg.K_DOWN):
                        game.slider_dot_mode = False
                        game.persist_settings()
                    else:
                        step = 0.01 if event.key == pg.K_RIGHT else -0.01
                        game.adjust_slider_value(game.focus_key, step)
                elif game.alt_control and game.state == "ADVANCED_SETTINGS" and event.key in (pg.K_SPACE, pg.K_RETURN) and ah.effective_focus_key(game, mx, my) in ("game_volume", "terminal_volume"):
                    game.last_key_time = pg.time.get_ticks()
                    game.focus_key = ah.effective_focus_key(game, mx, my)
                    game.slider_dot_mode = True
                elif game.alt_control and event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT) and game.state in ("MENU", "SETTINGS", "ABOUT", "HISTORY", "HISTORY_DETAIL", "DELETE_HISTORY", "EXPORT_EXISTS", "RESUME_CHOICE", "HANNAH", "STATS", "ADVANCED_SETTINGS", "TUTORIAL"):
                    was_following_mouse = ah.effective_focus_key(game, mx, my) != game.focus_key
                    game.last_key_time = pg.time.get_ticks()
                    if not was_following_mouse:
                        direction = {pg.K_UP: "up", pg.K_DOWN: "down", pg.K_LEFT: "left", pg.K_RIGHT: "right"}[event.key]
                        ah.move_focus(game, direction)
                elif game.alt_control and event.key in (pg.K_SPACE, pg.K_RETURN) and game.state in ("MENU", "SETTINGS", "ABOUT", "HISTORY", "HISTORY_DETAIL", "DELETE_HISTORY", "EXPORT_EXISTS", "RESUME_CHOICE", "HANNAH", "STATS", "ACHIEVEMENTS", "ADVANCED_SETTINGS", "TUTORIAL"):
                    key = ah.effective_focus_key(game, mx, my)
                    lookup = dict(ah.focus_order(game))
                    if key is not None and key in lookup:
                        rect = lookup[key]
                        handle_click(game, pg.time.get_ticks(), rect.centerx, rect.centery, 1)
                elif (not game.alt_control) and game.state == "HANNAH" and game.hannah_open_index is None and event.key in (pg.K_LEFT, pg.K_RIGHT):
                    step = 90
                    game.hannah_scroll_x = step if event.key == pg.K_LEFT else -step
                    min_scroll = helpers.hannah_scroll_bounds()
                    game.hannah_scroll_x = max(min_scroll, min(0, game.hannah_scroll_x))
                elif game.state == "ACHIEVEMENTS" and event.key in {pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN, pg.K_b, pg.K_n}:
                    total_pages = len(helpers.ACHIEVEMENT_PAGES)
                    if event.key == pg.K_LEFT and game.achievements_page > 0:
                        game.achievements_page -= 1
                    elif event.key == pg.K_RIGHT and game.achievements_page < total_pages - 1:
                        game.achievements_page += 1
                    elif game.achievements_page == 0 and event.key in (pg.K_UP, pg.K_DOWN):
                        time_count = len(con.GENERAL_TIME_MILESTONES)
                        index = getattr(game, "ach_time_index", 0)
                        step = 1 if event.key == pg.K_DOWN else -1
                        game.ach_time_index = max(0, min(time_count - 1, index + step))
                    elif game.achievements_page == 0 and event.key in (pg.K_b, pg.K_n):
                        games_count = len(con.GENERAL_GAME_MILESTONES)
                        index = getattr(game, "ach_games_index", 0)
                        step = 1 if event.key == pg.K_n else -1
                        game.ach_games_index = max(0, min(games_count - 1, index + step))
                elif game.state == "TERMINAL":
                    active_terminal.handle_key(event)
                    if active_terminal.should_close:
                        target_state = active_terminal.next_state or "MENU"
                        if hasattr(active_terminal, "settings"):
                            game.settings = active_terminal.settings
                            game.apply_settings()
                        if target_state == "HISTORY":
                            game.open_history()
                        elif target_state == "HANNAH":
                            game.init_hannah()
                        elif target_state == "PLAY" and active_terminal.next_game:
                            n, ultra = active_terminal.next_game
                            game.new_game(n, ultra=ultra, force_new=True)
                        else:
                            game.state = target_state
                            
                        active_terminal = None
                        game.refresh_achievements()
                elif event.key == pg.K_t and (event.mod & pg.KMOD_CTRL) and game.state == "MENU":
                    game.state = "TERMINAL"
                    active_terminal = t.Terminal(sounds)
                    game.mark_achievement("terminal_found")
                    
                game.mouse_hover_start = current_time
                    
            elif event.type == pg.MOUSEBUTTONDOWN and mouse_inside:
                pg.mouse.set_visible(True)
                started_drag = False
                if event.button == 1:
                    if game.state == "ADVANCED_SETTINGS":
                        slider_tracks = {"game_volume": bt.ADV_GAME_VOLUME_RECT, "terminal_volume": bt.ADV_TERMINAL_VOLUME_RECT}
                        for which in ("game_volume", "terminal_volume"):
                            track = slider_tracks[which]
                            if track and track.collidepoint(mx, my):
                                game.slider_drag = which
                                value = w.value_for_slider_x(track, mx)
                                if which == "game_volume":
                                    game.settings["game_volume"] = value
                                    game.sounds.volume = value
                                else:
                                    game.settings["terminal_volume"] = value
                                started_drag = True
                                break
                    if not started_drag:
                        target = _scrollbar_target(game)
                        if target:
                            which, track, content, visible, vertical = target
                            if content > visible:
                                offset = _scrollbar_current_offset(game, which)
                                handle_rect = w.scrollbar_handle_rect(track, content, visible, offset, vertical)
                                if handle_rect.collidepoint(mx, my):
                                    grab = (my - handle_rect.y) if vertical else (mx - handle_rect.x)
                                    game.scrollbar_drag = {"which": which, "track": track, "content": content, "visible": visible, "vertical": vertical, "grab": grab}
                                    started_drag = True
                                elif track.collidepoint(mx, my):
                                    grab = handle_rect.height // 2 if vertical else handle_rect.width // 2
                                    game.scrollbar_drag = {"which": which, "track": track, "content": content, "visible": visible, "vertical": vertical, "grab": grab}
                                    new_offset = w.scrollbar_offset_for_handle_pos(track, content, visible, (mx, my), grab, vertical)
                                    _scrollbar_apply_offset(game, which, new_offset)
                                    started_drag = True
                                    
                if not started_drag:
                    pending_click = {
                        "time": pg.time.get_ticks(), "mx": mx, "my": my, "button": event.button, "valid": True
                    }
                game.mouse_hover_start = current_time
            
            elif event.type == pg.MOUSEWHEEL:
                pg.mouse.set_visible(True)
                game.mouse_hover_start = current_time
                if game.state in ("HISTORY", "HISTORY_DETAIL"):
                    handle_scroll(game, event)
                elif game.state == "TERMINAL" and active_terminal:
                    active_terminal.scroll(int(event.y * 3))
                elif game.state == "ACHIEVEMENTS" and game.achievements_page == 0:
                    time_tile = bt.ACH_TIME_TILE_RECT
                    if time_tile.collidepoint(mx, my):
                        time_count = len(con.GENERAL_TIME_MILESTONES)
                        index = getattr(game, "ach_time_index", 0)
                        game.ach_time_index = max(0, min(time_count - 1, index - int(event.y)))
                if pending_click and pg.time.get_ticks() - pending_click["time"] < con.WHEEL_CLICK_GUARD_MS_MIN:
                    pending_click["valid"] = False
        
        if game.scrollbar_drag:
            if pg.mouse.get_pressed()[0]:
                d = game.scrollbar_drag
                new_offset = w.scrollbar_offset_for_handle_pos(d["track"], d["content"], d["visible"], (mx, my), d["grab"], d["vertical"])
                _scrollbar_apply_offset(game, d["which"], new_offset)
            else:
                game.scrollbar_drag = None
                
        if getattr(game, "slider_drag", None):
            if pg.mouse.get_pressed()[0]:
                slider_tracks = {"game_volume": bt.ADV_GAME_VOLUME_RECT, "terminal_volume": bt.ADV_TERMINAL_VOLUME_RECT}
                track = slider_tracks.get(game.slider_drag)
                if track:
                    value = w.value_for_slider_x(track, mx)
                    if game.slider_drag == "game_volume":
                        game.settings["game_volume"] = value
                        game.sounds.volume = value
                    else:
                        game.settings["terminal_volume"] = value
            else:
                game.persist_settings()
                game.slider_drag = None
                
        if (mx, my) != getattr(game, "last_mouse_pos", (mx, my)) and game.state != "TERMINAL":
            game.last_mouse_pos = (mx, my)
            pg.mouse.set_visible(True)
            game.last_move_time = current_time
            game.mouse_hover_start = current_time
        else:
            if current_time - game.last_move_time > 5000:
                pg.mouse.set_visible(False)

        in_hannah_strip = game.state == "HANNAH" and getattr(game, "hannah_open_index", None) is None
        in_slider_dot_mode = game.state == "ADVANCED_SETTINGS" and getattr(game, "slider_dot_mode", False) and game.focus_key in ("game_volume", "terminal_volume")
        
        if game.alt_control and (game.state in ("HISTORY", "HISTORY_DETAIL") or in_hannah_strip or in_slider_dot_mode):
            keys_down = pg.key.get_pressed()
            direction = None
            if keys_down[pg.K_DOWN]: direction = "down"
            elif keys_down[pg.K_UP]: direction = "up"
            elif keys_down[pg.K_LEFT]: direction = "left"
            elif keys_down[pg.K_RIGHT]: direction = "right"
            
            now_ticks = pg.time.get_ticks()
            if direction is None:
                game._repeat_direction = None
            elif direction != game._repeat_direction:
                game._repeat_direction = direction
                game._repeat_next_time = now_ticks + con.KEY_REPEAT_DELAY_MS
            elif now_ticks >= game._repeat_next_time:
                game.last_key_time = now_ticks
                if in_slider_dot_mode and direction in ("left", "right"):
                    game.adjust_slider_value(game.focus_key, 0.01 if direction == "right" else -0.01)
                else:
                    ah.move_focus(game, direction)
                game._repeat_next_time = now_ticks + con.KEY_REPEAT_INTERVAL_MS
        else:
            game._repeat_direction = None
            
        if game.state == "TERMINAL" and active_terminal:
            keys_down = pg.key.get_pressed()
            mods = pg.key.get_mods()
            ctrl_held = bool(mods & (pg.KMOD_CTRL | pg.KMOD_META))
            repeat_key = None
            if keys_down[pg.K_BACKSPACE]: repeat_key = pg.K_BACKSPACE
            elif keys_down[pg.K_LEFT]: repeat_key = pg.K_LEFT
            elif keys_down[pg.K_RIGHT]: repeat_key = pg.K_RIGHT
            elif keys_down[pg.K_UP]: repeat_key = pg.K_UP
            elif keys_down[pg.K_DOWN]: repeat_key = pg.K_DOWN
            
            now_ticks = pg.time.get_ticks()
            if repeat_key is None:
                active_terminal._repeat_key = None
            elif repeat_key != active_terminal._repeat_key:
                active_terminal._repeat_key = repeat_key
                active_terminal._repeat_next_time = now_ticks + con.KEY_REPEAT_DELAY_MS
            elif now_ticks >= active_terminal._repeat_next_time:
                active_terminal._repeatable_action(repeat_key, ctrl_held)
                active_terminal._repeat_next_time = now_ticks + con.KEY_REPEAT_INTERVAL_MS
        elif active_terminal:
            active_terminal._repeat_key = None
        
        if game.request_fullscreen_toggle:
            fullscreen, real_screen = toggle_fullscreen(fullscreen, windowed_size)
            game.is_fullscreen = fullscreen
            game.request_fullscreen_toggle = False
            w.set_real_screen(real_screen)
            forced_redraw = True
            
        if pending_click:
            click_time = pending_click["time"]
            if pending_click.get("valid", True) and pg.time.get_ticks() - click_time >= con.WHEEL_CLICK_GUARD_MS_MIN:
                handle_click(game, click_time, pending_click["mx"], pending_click["my"], pending_click["button"])
                forced_redraw = True
                pending_click = None
            elif not pending_click.get("valid", True):
                pending_click = None
                
        if game.state != "TERMINAL" and active_terminal:
            active_terminal = None
            game.refresh_achievements()

        export_was_active = game.exporting and game.export_thread is not None
        was_backgrounded = game.export_backgrounded
        game.check_export_progress()
        if export_was_active and not game.exporting:
            forced_redraw = True
            game.export_popup_allowed = was_backgrounded and game.state != "HISTORY_DETAIL"

        game.tick_timer()
        game.tutorial.update(game, active_terminal)
        
        if _needs_redraw(redraw, game, active_terminal, mx, my, real_w, real_h,
                         current_time, had_event, state_changed, forced_redraw):
            if active_terminal:
                active_terminal.draw()
            else:
                draw(game, mx, my)
            game.tutorial.draw(game, active_terminal)
            w.present(real_screen)
            redraw["last_export_pct"] = int(round(min(1.0, getattr(game, "export_progress", 0.0)) * 100))
            _note_redraw_done(redraw, game, active_terminal)
            redraw["next_timed_at"] = _scheduled_redraw_at(game, active_terminal, current_time)
            
        clock.tick(60)
    
    
def handle_click(game, click_time, mx, my, button):
    if pg.time.get_ticks() - game.last_wheel_time < con.WHEEL_CLICK_GUARD_MS and game.last_wheel_time >= click_time:
        return
        
    if button == 1 and getattr(game, "live_clock_enabled", False) and game.state not in ("TUTORIAL", "ABOUT", "HANNAH", "HISTORY_DETAIL", "ACHIEVEMENTS", "TERMINAL"):
        if helpers.CLOCK_CLICK_RECT.collidepoint((mx, my)):
            game.start_tutorial(intro=False)
            return
            
    match game.state:
        case "MENU":
            buttons = bt.menu_buttons.get(game)
            for n in con.DIFFICULTIES:
                if buttons[f"start_{n}"].is_clicked(mx, my):
                    game.return_focus["MENU"] = f"start_{n}"
                    game.new_game(n)
                    return
            if buttons["settings"].is_clicked(mx, my):
                game.return_focus["MENU"] = "settings"
                game.state = "SETTINGS"
            elif buttons["history"].is_clicked(mx, my):
                game.return_focus["MENU"] = "history"
                game.open_history()
            elif buttons["quit"].is_clicked(mx, my):
                pg.quit()
                sys.exit()
    
        case "SETTINGS":
            buttons = bt.settings_buttons.get(game)
            
            if game.timer_enabled and buttons["toggle_ms"].is_clicked(mx, my):
                game.timer_ms = not game.timer_ms
                
            if buttons["back"].is_clicked(mx, my):
                game.state = "MENU"
            elif buttons["toggle_history"].is_clicked(mx, my):
                game.save_history = not game.save_history
            elif buttons["toggle_timer"].is_clicked(mx, my):
                game.timer_enabled = not game.timer_enabled
                if not game.timer_enabled: game.timer_ms = False
            elif buttons["toggle_sound"].is_clicked(mx, my):
                game.sounds.enabled = not game.sounds.enabled
            elif buttons["toggle_fullscreen"].is_clicked(mx, my):
                game.request_fullscreen_toggle = True
            elif buttons["toggle_alt_control"].is_clicked(mx, my):
                game.alt_control = not game.alt_control
                if game.alt_control:
                    game.focus_key = "toggle_alt_control"
                    game.focus_lock_until = pg.time.get_ticks() + 200
            elif buttons["toggle_live_clock"].is_clicked(mx, my):
                game.live_clock_enabled = not game.live_clock_enabled
                if not game.live_clock_enabled: game.live_clock_ms = False
            elif "toggle_ultra_timer" in buttons and buttons["toggle_ultra_timer"].is_clicked(mx, my):
                game.ultra_timer_enabled = not game.ultra_timer_enabled
                if not game.ultra_timer_enabled:
                    game.ultra_timer_ms = False
            elif "toggle_ultra_timer_ms" in buttons and buttons["toggle_ultra_timer_ms"].is_clicked(mx, my):
                game.ultra_timer_ms = not game.ultra_timer_ms
            elif "toggle_ultra_timer_clock" in buttons and buttons["toggle_ultra_timer_clock"].is_clicked(mx, my):
                game.ultra_timer_show_clock = not game.ultra_timer_show_clock
                
            game.persist_settings()
            
            if buttons["stats"].is_clicked(mx, my):
                game.return_focus["SETTINGS"] = "stats"
                game.state = "STATS"
            elif buttons["achievements"].is_clicked(mx, my):
                game.return_focus["SETTINGS"] = "achievements"
                game.check_achievements()
                game.achievements_page = 0
                game.state = "ACHIEVEMENTS"
            elif buttons["about"].is_clicked(mx, my):
                game.return_focus["SETTINGS"] = "about"
                game.state = "ABOUT"
            
        case "ABOUT":
            if bt.about_buttons.get(game)["back"].is_clicked(mx, my):
                game.state = "SETTINGS"
                
        case "STATS":
            if bt.stats_buttons.get(game)["back"].is_clicked(mx, my):
                game.state = "SETTINGS"
            else:
                for key, header_button in bt.stats_header_buttons.get(game).items():
                    if header_button.is_clicked(mx, my):
                        game.sort_stats_by(key)
                        break
                
        case "ACHIEVEMENTS":
            nav_buttons = bt.achievements_nav_buttons.get(game)
            if nav_buttons["back"].is_clicked(mx, my):
                game.state = "SETTINGS"
            else:
                total_pages = len(helpers.ACHIEVEMENT_PAGES)
                if game.achievements_page > 0 and nav_buttons["prev_page"].is_clicked(mx, my):
                    game.achievements_page -= 1
                elif game.achievements_page < total_pages - 1 and nav_buttons["next_page"].is_clicked(mx, my):
                    game.achievements_page += 1
                
                if game.achievements_page == 0:
                    games_tile = bt.ACH_GAMES_TILE_RECT
                    if games_tile.collidepoint(mx, my):
                        games_nav_buttons = bt.achievements_games_nav_buttons.get(game)
                        games_count = len(con.GENERAL_GAME_MILESTONES)
                        index = getattr(game, "ach_games_index", 0)
                        if index > 0 and games_nav_buttons["games_prev"].is_clicked(mx, my):
                            game.ach_games_index = index - 1
                        elif index < games_count - 1 and games_nav_buttons["games_next"].is_clicked(mx, my):
                            game.ach_games_index = index + 1                    

        case "ADVANCED_SETTINGS":
            buttons = bt.advanced_settings_buttons.get(game)
            
            if buttons["back"].is_clicked(mx, my):
                game.language_dropdown_open = False
                game.state = "SETTINGS"
                return
            
            if buttons["toggle_terminal_sound"].is_clicked(mx, my):
                game.settings["terminal_sound_enabled"] = not game.settings["terminal_sound_enabled"]
                game.persist_settings()
                return

            if buttons["scale_mode"].is_clicked(mx, my):
                modes = con.SCALE_MODES
                idx = (modes.index(game.scale_mode) + 1) % len(modes) if getattr(game, "scale_mode", "auto") in modes else 0
                game.scale_mode = modes[idx]
                game.settings["scale_mode"] = game.scale_mode
                game.persist_settings()
                w.set_scale_mode(game.scale_mode)
                return

            if buttons["render_quality"].is_clicked(mx, my):
                qualities = con.RENDER_QUALITIES
                cur = getattr(game, "render_quality", 1)
                idx = (qualities.index(cur) + 1) % len(qualities) if cur in qualities else 0
                game.render_quality = qualities[idx]
                game.settings["render_quality"] = game.render_quality
                game.persist_settings()
                w.set_render_quality(game.render_quality)
                return
            
            if buttons["language_dropdown"].is_clicked(mx, my):
                game.language_dropdown_open = not getattr(game, "language_dropdown_open", False)
                return
            
            if getattr(game, "language_dropdown_open", False):
                for i, (label, internal) in enumerate(helpers.available_languages()):
                    button = buttons.get(f"language_option_{i}")
                    if button and button.is_clicked(mx, my):
                        game.settings["language"] = internal
                        lang.load_language(internal)
                        game.language_dropdown_open = False
                        game.persist_settings()
                        return
                    
            for i, option in enumerate(con.INPUT_ORDER_OPTIONS):
                if buttons[f"input_order_{i}"].is_clicked(mx, my):
                    target_key = "input_order_front" if option in con.INPUT_ORDER_FRONT_OPTIONS else "input_order_back"
                    game.settings[target_key] = option
                    game.persist_settings()
                    return
                
            for action in con.DEFAULT_KEYBINDINGS:
                if buttons[f"keybind_{action}"].is_clicked(mx, my):
                    game.rebind_listening = action
                    return
            
        case "HISTORY":
            if bt.history_back_button.get(game)["back"].is_clicked(mx, my):
                game.state = "MENU"
                return
        
            filter_buttons = bt.history_filter_buttons.get(game)
            if filter_buttons["size_all"].is_clicked(mx, my):
                game.toggle_size_filter(None)
                return
            for n in con.DIFFICULTIES:
                if filter_buttons[f"size_{n}"].is_clicked(mx, my):
                    game.toggle_size_filter(n)
                    return
            if filter_buttons["top10"].is_clicked(mx, my):
                game.toggle_top10_filter()
                return
            if "ultra" in filter_buttons and filter_buttons["ultra"].is_clicked(mx, my):
                game.toggle_ultra_filter()
                return
        
            if my <= con.LIST_TOP - 10:
                return
                
            entries = game.filtered_history()
            for i, entry in enumerate(entries):
                delete_rect = helpers.history_delete_rect(i, game.history_scroll_y)
                entry_rect = helpers.history_entry_rect(i, game.history_scroll_y)
                
                if delete_rect.collidepoint(mx, my):
                    game.return_focus["HISTORY"] = f"delete_{i}"
                    game.file_to_delete = entry["filename"]
                    game.state = "DELETE_HISTORY"
                    return
                elif entry_rect.collidepoint(mx, my):
                    game.return_focus["HISTORY"] = f"entry_{i}"
                    game.open_history_detail(entry["filename"])
                    return
            
        case "DELETE_HISTORY":
            buttons = bt.delete_confirm_buttons.get(game)
            if buttons["yes"].is_clicked(mx, my):
                game.delete_history(game.file_to_delete)
                game.file_to_delete = None
                game.state = "HISTORY"
            elif buttons["no"].is_clicked(mx, my):
                game.file_to_delete = None
                game.state = "HISTORY"
    
        case "EXPORT_EXISTS":
            buttons = bt.export_exists_buttons.get(game)
            if buttons["yes"].is_clicked(mx, my):
                game.confirm_export_selected_to_mp4()
            elif buttons["no"].is_clicked(mx, my):
                game.cancel_export_exists()
    
        case "HISTORY_DETAIL":
            detail_buttons = bt.history_detail_buttons.get(game)
            if detail_buttons["back"].is_clicked(mx, my):
                game.open_history()
            elif detail_buttons["export_mp4"].is_clicked(mx, my):
                game.export_selected_to_mp4()
            elif detail_buttons["export_quality"].is_clicked(mx, my):
                game.cycle_export_quality()
            elif detail_buttons["export_fps"].is_clicked(mx, my):
                game.cycle_export_fps()
            elif detail_buttons["detail_reset"].is_clicked(mx, my):
                game.reset_detail_view()
            elif game.selected_history_data:
                display_actions = helpers.detail_display_actions(game.selected_history_data)
                for i in range(len(display_actions)):
                    rect = helpers.detail_action_rect(i, game.detail_scroll_y)
                    if rect.bottom < con.DETAIL_ABOVE or rect.top > con.DETAIL_BELOW:
                        continue
                    if rect.collidepoint(mx, my):
                        game.select_detail_action(i - 1)
                        return
                
        case "RESUME_CHOICE":
            buttons = bt.resume_choice_buttons.get(game)
            if buttons["resume"].is_clicked(mx, my):
                game.resume_paused(game.pending_new_n, game.pending_new_ultra)
            elif buttons["new"].is_clicked(mx, my):
                game.discard_and_start(game.pending_new_n, game.pending_new_ultra)
            elif buttons["cancel"].is_clicked(mx, my):
                game.state = "MENU"
                
        case "HANNAH":
            if game.hannah_open_index is None:
                buttons = bt.hannah_buttons.get(game)
                if buttons["back"].is_clicked(mx, my):
                    game.state = "MENU"
                    return
                for i, lvl in enumerate(game.hannah_levels):
                    if lvl is None:
                        continue
                    rect = helpers.hannah_tile_rect(i, game.hannah_scroll_x)
                    if rect.collidepoint(mx, my):
                        solved = i < len(game.hannah_solved) and game.hannah_solved[i]
                        if not solved:
                            game.hannah_open(i)
                        return
            else:
                buttons = bt.hannah_play_buttons.get(game)
                if buttons["back"].is_clicked(mx, my):
                    game.hannah_close()
                    return
                if buttons["undo"].is_clicked(mx, my):
                    game.hannah_undo()
                    return
                    
                n = con.HANNAH_SIZE
                offset_x, offset_y = helpers.play_grid_offset(n)
                for r in range(n):
                    for c in range(n):
                        rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE)
                        if rect.collidepoint(mx, my):
                            game.hannah_click_cell(r, c, right_click=(button == 3))
                            return
            
        case "TUTORIAL":
            buttons = bt.tutorial_buttons.get(game)
            if buttons["back"].is_clicked(mx, my):
                game.close_tutorial()
            elif buttons["close"].is_clicked(mx, my):
                game.tutorial_next()
                
        case "PLAY":
            buttons = bt.play_buttons.get(game)
            button_actions_game = {
                "back": lambda: (game.stash_current_game(), setattr(game, "state", "MENU")),
                "hint": game.use_hint,
                "undo": game.undo,
                "restart": game.restart_same,
                "pause": game.toggle_pause,
            }
            button_actions_pause = {
                "new": game.restart_same,
                "menu": lambda: (game.stash_current_game(), setattr(game, "state", "MENU")),
                "break": game.toggle_pause,
            }
            
            button_actions = button_actions_pause if game.paused else button_actions_game
            
            for name, action in button_actions.items():
                if buttons[name].is_clicked(mx, my):
                    action()
                    return
        
            if game.paused or game.won:
                return
        
            offset_x, offset_y = helpers.play_grid_offset(game.n)
            if offset_x + con.CELL_SIZE <= mx < offset_x + (game.n + 1) * con.CELL_SIZE and offset_y + con.CELL_SIZE <= my < offset_y + (game.n + 1) * con.CELL_SIZE:
                c = int((mx - offset_x - con.CELL_SIZE) // con.CELL_SIZE)
                r = int((my - offset_y - con.CELL_SIZE) // con.CELL_SIZE)
                game.click_cell(r, c, right_click=(button == 3))


def _scrollbar_target(game):
    match game.state:
        case "HISTORY":
            entries = game.filtered_history()
            track = helpers.history_scrollbar_track()
            visible = con.HISTORY_VISIBLE_BOTTOM - con.LIST_TOP
            content = helpers.history_content_height(len(entries))
            return ("history", track, content, visible, True)
        
        case "HISTORY_DETAIL":
            if game.selected_history_data:
                display_actions = helpers.detail_display_actions(game.selected_history_data)
                track = helpers.DETAIL_SCROLLBAR_TRACK
                return ("detail", track, len(display_actions) * 34, 440, True)
        
        case "HANNAH":
            if getattr(game, "hannah_open_index", None) is None:
                track = helpers.hannah_scrollbar_track()
                return ("hannah", track, helpers.hannah_content_width(), con.HANNAH_VISIBLE_LENGTH, False)
                
    return None


def _scrollbar_current_offset(game, which):
    match which:
        case "history": return -game.history_scroll_y
        case "detail": return -game.detail_scroll_y
        case "hannah": return -game.hannah_scroll_x
    return 0


def _scrollbar_apply_offset(game, which, offset):
    now = pg.time.get_ticks()
    match which:
        case "history":
            game.history_scroll_y = -offset
            game.history_scroll_last = now
        case "detail":
            game.detail_scroll_y = -offset
            game.detail_scroll_last = now
        case "hannah":
            game.hannah_scroll_x = -offset
            game.hannah_scroll_last = now
    
        
def handle_scroll(game, event):
    game.last_wheel_time = pg.time.get_ticks()
    last_time = getattr(handle_scroll, "_last_time", game.last_wheel_time)
    time_diff = max(1, game.last_wheel_time - last_time)
    handle_scroll._last_time = game.last_wheel_time
    
    raw_speed = event.y / time_diff
    scroll_speed = 1 + (abs(raw_speed) * 1000)
    delta = event.y * scroll_speed
    
    match game.state:
        case "HISTORY":
            game.history_scroll_y += delta
            count = len(game.filtered_history())
            max_scroll = 0
            min_scroll = helpers.history_scroll_bounds(count)
            game.history_scroll_y = max(min_scroll, min(game.history_scroll_y, max_scroll))
            game.history_scroll_last = pg.time.get_ticks()
    
        case "HISTORY_DETAIL":
            game.detail_scroll_y += delta
            count = len(helpers.detail_display_actions(game.selected_history_data)) if game.selected_history_data else 0
            max_scroll = 0
            min_scroll = -max(0, (count * 34) - 440)
            game.detail_scroll_y = max(min_scroll, min(game.detail_scroll_y, max_scroll))
            game.detail_scroll_last = pg.time.get_ticks()

        case "HANNAH":
            if game.hannah_open_index: return
             
            game.hannah_scroll_x += delta
            min_scroll = helpers.hannah_scroll_bounds()
            game.hannah_scroll_x = max(min_scroll, min(0, game.hannah_scroll_x))
            game.hannah_scroll_last = pg.time.get_ticks()
    
    
def draw(game, mx, my):
    match game.state:
        case "MENU": s.draw_menu(game, mx, my)
        case "SETTINGS": s.draw_settings(game, mx, my)
        case "ADVANCED_SETTINGS": s.draw_advanced_settings(game, mx, my)
        case "ABOUT": s.draw_about(game, mx, my)
        case "STATS": s.draw_stats(game, mx, my)
        case "ACHIEVEMENTS": s.draw_achievements(game, mx, my)
        case "RESUME_CHOICE": s.draw_resume_choice(game, mx, my)
        case "HISTORY": s.draw_history(game, mx, my)
        case "HISTORY_DETAIL": s.draw_history_detail(game, mx ,my)
        case "PLAY": s.draw_play(game, mx, my)
        case "DELETE_HISTORY": s.draw_delete_confirm(game, mx, my)
        case "EXPORT_EXISTS": s.draw_export_exists_confirm(game, mx, my)
        case "HANNAH": s.draw_hannah(game, mx, my)
        case "TUTORIAL": s.draw_tutorial(game, mx, my)
            
    if game.state not in ("ABOUT", "HANNAH", "HISTORY_DETAIL", "ACHIEVEMENTS", "TERMINAL", "TUTORIAL"): 
        w.draw_live_clock(game)
        
    if game.exporting and not game.export_backgrounded:
        s.draw_export_overlay(game, mx, my)
    elif game.exporting and game.export_backgrounded and game.state == "HISTORY_DETAIL":
        s.draw_export_background_badge(game, mx, my)
        
    if game.export_status:
        s.draw_export_notification(game)


if __name__ == "__main__":
    main()