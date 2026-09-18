"""Draw every screen onto the virtual surface."""

import math
from typing import Any
import pygame as pg

import alt_hover as ah
import buttons as bt
import config as con
import helpers
from helpers import hannah_content_width
import lang
import replay as re
import widgets as w


def draw_menu(game: Any, mx: int, my: int) -> None:
    """Draw the main menu screen."""
    w.draw_title(lang.t("mati", "Mati"), con.TEXT_COLOR, con.WIDTH // 2, 90)
    w.draw_small(lang.t("intro_text", "Mathematic and Tactic Intelligence"), con.TEXT_COLOR, con.WIDTH // 2, 135)
    buttons = bt.menu_buttons.get(game)
    fk = ah.effective_focus_key(game, mx, my)
    for button in buttons.values():
        button.draw(mx, my, focus_key=fk)


def draw_settings(game: Any, mx: int, my: int) -> None:
    """Draw the standard settings menu."""
    w.draw_title(lang.t("settings_title", "Settings"), con.TEXT_COLOR, con.WIDTH // 2, 90)
    buttons = bt.settings_buttons.get(game)
    fk = ah.effective_focus_key(game, mx, my)

    buttons["back"].draw(mx, my, focus_key=fk)

    sections = helpers.settings_sections(game)
    headers = [(title, x, y) for title, _keys, x, y in sections]
    for title, x, y in headers:
        x_h = x if len(headers) == 4 else x + 110
        y_h = y if len(headers) == 4 else y + 10
        w.draw_tiny(lang.t(title, title.upper()), con.DIMMED_TEXT_COLOR, x_h, y_h, center=len(headers) == 3)

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


def draw_advanced_settings(game: Any, mx: int, my: int) -> None:
    """Draw the advanced audio, scale, quality, language, and keybindings screen."""
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

    # --- Display scale ---
    cur_scale = getattr(game, "scale_mode", "auto")
    scale_label = con.SCALE_MODE_LABELS[con.SCALE_MODES.index(cur_scale)] if cur_scale in con.SCALE_MODES else con.SCALE_MODE_LABELS[0]
    buttons["scale_mode"].label = lang.t("display_scale", "Display Scale") + ": " + scale_label
    buttons["scale_mode"].active = True
    buttons["scale_mode"].draw(mx, my, focus_key=fk)

    # --- Render quality ---
    cur_quality = getattr(game, "render_quality", 1)
    if cur_quality in con.RENDER_QUALITIES:
        quality_label = con.RENDER_QUALITY_LABELS[con.RENDER_QUALITIES.index(cur_quality)]
    else:
        quality_label = con.RENDER_QUALITY_LABELS[0]
    buttons["render_quality"].label = lang.t("render_quality", "Render Quality") + ": " + quality_label
    buttons["render_quality"].active = True
    buttons["render_quality"].draw(mx, my, focus_key=fk)

    # --- Language ---
    w.draw_small(lang.t("language", "Language"), con.TEXT_COLOR, 60, 385, center=False)
    current_display = next((label for label, internal in helpers.available_languages() if internal == lang.current_language()), "English")
    buttons["language_dropdown"].label = current_display
    buttons["language_dropdown"].draw(mx, my, focus_key=fk)
    if getattr(game, "language_dropdown_open", False):
        for i, (_label, internal) in enumerate(helpers.available_languages()):
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
    for _i, action in enumerate(con.DEFAULT_KEYBINDINGS):
        key = f"keybind_{action}"
        rect = buttons[key].rect
        binding = game.keybindings.get(action, con.DEFAULT_KEYBINDINGS[action])
        label_text = lang.t(con.KEYBINDINGS_LABELS.get(action, action), con.KEYBINDINGS_LABELS.get(action, action))
        w.draw_small(f"{label_text}:", con.TEXT_COLOR, rect.centerx - 230, rect.centery - 14, center=False)
        listening = getattr(game, "rebind_listening", None) == action
        buttons[key].label = lang.t("key_press", "Press a key...") if listening else helpers.keybinding_label(binding)
        buttons[key].draw(mx, my, focus_key=fk)


def draw_about(game: Any, mx: int, my: int) -> None:
    """Draw the about screen."""
    w.draw_title(lang.t("about_1", "About Mati"), con.TEXT_COLOR, con.WIDTH // 2, 90)
    fk = ah.effective_focus_key(game, mx, my)
    bt.about_buttons.get(game)["back"].draw(mx, my, focus_key=fk)
    w.draw_small(lang.t("about_2", "Mati is an algorithm. A really cool one."), con.TEXT_COLOR, con.WIDTH // 2, 200)
    w.draw_small(lang.t("about_3", "It generates the inner grid and picks some random cells."), con.TEXT_COLOR, con.WIDTH // 2, 230)
    w.draw_small(lang.t("about_4", "The chosen cells are then added together, and the sums are written down."), con.TEXT_COLOR, con.WIDTH // 2, 260)
    w.draw_text(lang.t("about_5", "Created by:"), con.TEXT_COLOR, con.WIDTH // 2, 400)
    w.draw_text("Janosch Klawatsch", con.TEXT_COLOR, con.WIDTH // 2, 440)


def draw_stats(game: Any, mx: int, my: int) -> None:
    """Draw the statistics screen."""
    w.draw_title("Stats", con.TEXT_COLOR, con.WIDTH // 2, 70)
    fk = ah.effective_focus_key(game, mx, my)
    bt.stats_buttons.get(game)["back"].draw(mx, my, focus_key=fk)

    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    stats = game.stats
    col_x = [100, 170, 300, 425, 600]

    modes = (("Normal", "normal"), ("Ultra", "ultra")) if terminal_found else (("Normal", "normal"),)
    rows: list[dict[str, Any]] = []

    for n in con.DIFFICULTIES:
        for mode_label, mode_key in modes:
            m = stats.get(str(n), {}).get(mode_key, {})
            games = m.get("games", 0)
            best = m.get("best")
            total = m.get("total", 0)
            avg = total // games if games else None

            rows.append({
                "size": n,
                "mode_label": mode_label,
                "games": games,
                "best": best,
                "avg": avg,
                "display": [
                    f"{n}x{n}",
                    mode_label,
                    str(games),
                    helpers.fmt_stat_time(best),
                    helpers.fmt_stat_time(avg),
                ],
            })

    sk = getattr(game, "stats_sort_key", None)
    if sk is not None:
        asc = getattr(game, "stats_sort_asc", True)
        if sk == "size":
            key_fn = lambda r: r["size"]
        elif sk == "mode":
            key_fn = lambda r: r["mode_label"].lower()
        elif sk == "games":
            key_fn = lambda r: r["games"]
        elif sk == "best":
            key_fn = lambda r: (r["best"] if r["best"] is not None else 10**18)
        else:
            key_fn = lambda r: (r["avg"] if r["avg"] is not None else 10**18)

        rows.sort(key=key_fn, reverse=not asc)

    header_buttons = bt.stats_header_buttons.get(game)
    for _key, btn in header_buttons.items():
        btn.text_color = con.BLACK
        btn.draw(mx, my, focus_key=fk)
        btn.text_color = con.WHITE

    y = 164
    for row in rows:
        for x, text in zip(col_x, row["display"]):
            w.draw_small(text, con.TARGET_COLOR, x, y, center=False)
        y += 30


def _draw_progress_circle(screen: pg.Surface, rect: pg.Rect, frac: float, bar_rect: pg.Rect) -> None:
    """Draw a circular progress indicator whose fill level rises from bottom to top."""
    frac = max(0.0, min(1.0, frac))
    cx = rect.centerx
    cy = bar_rect.centery

    radius = min(30, max(18, bar_rect.height // 2 + 5))

    background_color = (
        max(0, con.GRID_COLOR[0] - 15),
        max(0, con.GRID_COLOR[1] - 15),
        max(0, con.GRID_COLOR[2] - 15),
    )
    fill_color = con.GOLD
    outline_color = con.GRID_COLOR

    pg.draw.circle(screen, background_color, (cx, cy), radius)

    if frac > 0:
        fill_height = int(radius * 2 * frac)
        fill_top = cy + radius - fill_height
        fill_bottom = cy + radius

        for y in range(fill_top, fill_bottom + 1):
            dy = y - cy
            inside = radius * radius - dy * dy
            if inside < 0:
                continue
            half_width = int(math.sqrt(inside))
            pg.draw.line(screen, fill_color, (cx - half_width, y), (cx + half_width, y))

    pg.draw.circle(screen, outline_color, (cx, cy), radius, 2)

    if frac > 0:
        highlight_color = (
            min(255, fill_color[0] + 25),
            min(255, fill_color[1] + 20),
            min(255, fill_color[2] + 10),
        )
        surface_y = cy + radius - int(radius * 2 * frac)
        if cy - radius < surface_y < cy + radius:
            dy = surface_y - cy
            inside = radius * radius - dy * dy
            if inside > 0:
                half_width = int(math.sqrt(inside))
                pg.draw.line(screen, highlight_color, (cx - half_width, surface_y), (cx + half_width, surface_y), 2)


def _draw_milestone_tile(
    rect: pg.Rect,
    title: str,
    keys: list[str],
    values: list[int],
    achievements: dict[str, Any],
    current_value: int,
    index: int,
    fmt_value: Any,
    mx: int,
    my: int,
    nav_buttons: tuple[Any, Any] | None = None,
    is_time_tile: bool = False,
) -> int:
    screen = w.get_screen()
    hovering = rect.collidepoint(mx, my)
    mouse_visible = bool(pg.mouse.get_visible())

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

    if is_time_tile and screen is not None:
        _draw_progress_circle(screen, rect, frac, bar_rect)
    elif screen is not None:
        pg.draw.rect(screen, con.GRID_COLOR, bar_rect, border_radius=9)
        fill_rect = pg.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * frac), bar_rect.height)
        if fill_rect.width > 0:
            pg.draw.rect(screen, con.GREEN, fill_rect, border_radius=9)
        pg.draw.rect(screen, con.BLACK, bar_rect, 1, border_radius=6)

    hint = lang.t("hover_to_browse", "Hover to browse") if nav_buttons else lang.t("scroll_to_browse", "Scroll to browse")
    w.draw_tiny(hint, con.DIMMED_TEXT_COLOR, rect.centerx, rect.bottom - 16)

    return index


def draw_achievements(game: Any, mx: int, my: int) -> None:
    """Draw the achievements screen and milestones."""
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
            bt.ACH_GAMES_TILE_RECT, lang.t("games_played", "Games Played"),
            games_keys, con.GENERAL_GAME_MILESTONES, achievements, total_games,
            games_index, str, mx, my, nav_buttons=games_nav,
        )

        time_keys = [key for key, _ in con.GENERAL_TIME_MILESTONES]
        time_values_ms = [seconds * 1000 for _, seconds in con.GENERAL_TIME_MILESTONES]
        time_index = getattr(game, "ach_time_index", None)
        if time_index is None:
            time_index = helpers.milestone_default_index(time_keys, achievements)
        game.ach_time_index = _draw_milestone_tile(
            bt.ACH_TIME_TILE_RECT, lang.t("total_playtime", "Total Play Time"),
            time_keys, time_values_ms, achievements, total_times_ms,
            time_index, helpers.fmt_total_time, mx, my, nav_buttons=None,
            is_time_tile=True,
        )
    else:
        y = 178
        row_h = 28
        visible_keys = page["keys"] if not is_easter_page else [key for key in page["keys"] if achievements.get(key)]

        if is_easter_page and not visible_keys:
            w.draw_small(lang.t("nothing_achieved", "Nothing achieved yet..."), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, y + 20, center=True)
        else:
            for key in visible_keys:
                unlocked = bool(achievements.get(key))
                color = con.GREEN if unlocked else con.DIMMED_TEXT_COLOR
                label = con.ACHIEVEMENT_LABELS.get(key, key)
                w.draw_small(f"{label}", color, con.WIDTH // 2, y, center=True)
                y += row_h

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


def draw_export_overlay(game: Any, mx: int, my: int) -> None:
    """Draw the modal overlay during MP4 export."""
    screen = w.get_screen()
    if screen is None:
        return
    overlay = pg.Surface((con.WIDTH, con.HEIGHT), pg.SRCALPHA)
    pg.draw.rect(overlay, (0, 0, 0, 190), overlay.get_rect())
    screen.blit(overlay, (0, 0))

    percent = int(round(min(1.0, getattr(game, "export_progress", 0.0)) * 100))
    w.draw_text(lang.t("exporting", "Exporting to MP4 ...") + f" {percent}%", con.WHITE, con.WIDTH // 2, con.HEIGHT // 2 - 20)
    w.draw_small(lang.t("export_bg_hint", "Click anywhere to continue in the background"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2 + 24)


def draw_export_background_badge(game: Any, mx: int, my: int) -> None:
    """Draw background export status badge on top-center of history detail."""
    percent = int(round(min(1.0, getattr(game, "export_progress", 0.0)) * 100))
    text = lang.t("exporting_short", "Exporting ") + f"{percent}%"
    screen = w.get_screen()
    if screen is None:
        return
    pad_x, pad_y = 12, 6
    _title_font, _font, small_font, _tiny_font = w.get_fonts()
    if small_font is None:
        return
    text_surf = small_font.render(text, True, con.WHITE)
    badge_w, badge_h = text_surf.get_width() + pad_x * 2, text_surf.get_height() + pad_y * 2
    badge_rect = pg.Rect((con.WIDTH - badge_w) // 2, 12, badge_w, badge_h)
    chip = pg.Surface((badge_w, badge_h), pg.SRCALPHA)
    pg.draw.rect(chip, (0, 0, 0, 170), chip.get_rect(), border_radius=8)
    screen.blit(chip, badge_rect.topleft)
    w.draw_small(text, con.WHITE, badge_rect.centerx, badge_rect.centery)


POPUP_ENTER_MS: int = 300
POPUP_HOLD_MS: int = 2000
POPUP_EXIT_MS: int = 250

_popup: dict[str, Any] = {
    "phase": "inactive",
    "start": 0,
    "finished_at": None,
    "from_x": 0,
    "returning": False,
}


def _popup_set_phase(phase: str, now: int) -> None:
    _popup["phase"] = phase
    _popup["start"] = now


def popup_animation_running() -> bool:
    return _popup["phase"] in ("entering", "holding", "exiting")


def _ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3


def _ease_in_cubic(t: float) -> float:
    return t ** 3


def draw_export_notification(game: Any, mx: int | None = None, my: int | None = None) -> None:
    """Draw sliding export completed toast notification."""
    now = pg.time.get_ticks()
    status = getattr(game, "export_status", None)
    status_valid = bool(status) and now < getattr(game, "export_status_until", 0)

    if game.state == "HISTORY_DETAIL":
        if status_valid:
            w.draw_tiny(status, con.DIMMED_TEXT_COLOR, 400, 580, center=True)
        return

    if not getattr(game, "export_popup_allowed", True):
        return

    if game.state in ("TERMINAL", "HANNAH"):
        return

    screen = w.get_screen()
    if screen is None:
        return
    _title_font, _font, small_font, _tiny_font = w.get_fonts()
    if small_font is None:
        return
    text = lang.t("export_done", "Export done")
    text_surf = small_font.render(text, True, con.WHITE)

    pad_x, pad_y = 12, 7
    banner_w = min(con.WIDTH - 40, text_surf.get_width() + pad_x * 2)
    banner_h = text_surf.get_height() + pad_y * 2

    target_x, target_y = con.WIDTH - 55, 26
    start_x = con.WIDTH + banner_w // 2 + 4

    finished_at = getattr(game, "export_finished_at", None)
    if status_valid and finished_at != _popup["finished_at"]:
        if _popup["phase"] == "exiting":
            p = min(1.0, (now - _popup["start"]) / POPUP_EXIT_MS)
            _popup["from_x"] = target_x + (start_x - target_x) * _ease_in_cubic(p)
            _popup_set_phase("entering", now)
            _popup["returning"] = True
            game.sounds.play(getattr(game.sounds, "export_pop", None))
        elif _popup["phase"] == "holding":
            _popup_set_phase("holding", now)
        else:
            _popup_set_phase("entering", now)
            _popup["returning"] = False
            game.sounds.play(getattr(game.sounds, "export_pop", None))
        _popup["finished_at"] = finished_at
    elif not status_valid and _popup["phase"] in ("entering", "holding"):
        _popup_set_phase("exiting", now)
        game.sounds.play(getattr(game.sounds, "export_bye", None))
    elif not status_valid and _popup["phase"] == "inactive":
        return

    phase = _popup["phase"]
    if phase == "entering":
        p = min(1.0, (now - _popup["start"]) / POPUP_ENTER_MS)
        from_x = _popup["from_x"] if _popup["returning"] else start_x
        x = from_x + (target_x - from_x) * _ease_out_cubic(p)
        alpha = int(255 * p)
        if p >= 1.0:
            _popup["returning"] = False
            _popup_set_phase("holding", now)
    elif phase == "holding":
        x = target_x
        alpha = 255
        if now - _popup["start"] >= POPUP_HOLD_MS:
            _popup_set_phase("exiting", now)
            game.sounds.play(getattr(game.sounds, "export_bye", None))
    else:
        p = min(1.0, (now - _popup["start"]) / POPUP_EXIT_MS)
        x = target_x + (start_x - target_x) * _ease_in_cubic(p)
        alpha = int(255 * (1.0 - p))
        if p >= 1.0:
            _popup_set_phase("inactive", now)
            return

    if phase == "inactive" or alpha <= 0:
        return

    banner_rect = pg.Rect(0, 0, banner_w, banner_h)
    banner_rect.center = (int(round(x)), target_y)

    chip = pg.Surface((banner_w, banner_h), pg.SRCALPHA)
    pg.draw.rect(chip, (25, 25, 29, 235), chip.get_rect(), border_radius=10)
    pg.draw.rect(chip, (90, 90, 96, 170), chip.get_rect(), width=1, border_radius=10)

    accent_rect = pg.Rect(0, 0, 3, max(4, banner_h - 10))
    accent_rect.midleft = (5, banner_h // 2)
    pg.draw.rect(chip, (60, 180, 90, 255), accent_rect, border_radius=2)

    if alpha < 255:
        chip.set_alpha(alpha)
        text_surf.set_alpha(alpha)

    screen.blit(chip, banner_rect.topleft)
    text_rect = text_surf.get_rect(center=banner_rect.center)
    screen.blit(text_surf, text_rect)


def draw_delete_confirm(game: Any, mx: int, my: int) -> None:
    """Draw delete match confirmation modal."""
    overlay = pg.Surface((con.WIDTH, con.HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((215, 215, 215))
    screen = w.get_screen()
    if screen is None:
        return
    screen.blit(overlay, (0, 0))

    box_w, box_h = 440, 220
    box_x = (con.WIDTH - box_w) // 2
    box_y = (con.HEIGHT - box_h) // 2

    pg.draw.rect(screen, con.BG_COLOR, (box_x, box_y, box_w, box_h), border_radius=12)
    pg.draw.rect(screen, con.TEXT_COLOR, (box_x, box_y, box_w, box_h), width=2, border_radius=12)

    w.draw_text(lang.t("delete_match", "Delete Match?"), con.TEXT_COLOR, con.WIDTH // 2, box_y + 40, center=True)
    w.draw_small(lang.t("under_1", "Do you really want to permanently delete"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 85, center=True)
    w.draw_small(lang.t("under_2", "this game from your history?"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 110, center=True)

    fk = ah.effective_focus_key(game, mx, my)
    buttons = bt.delete_confirm_buttons.get(game)
    buttons["yes"].draw(mx, my, focus_key=fk)
    buttons["no"].draw(mx, my, focus_key=fk)


def draw_export_exists_confirm(game: Any, mx: int, my: int) -> None:
    """Draw modal dialog when re-exporting an already exported video."""
    overlay = pg.Surface((con.WIDTH, con.HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((215, 215, 215))
    screen = w.get_screen()
    if screen is None:
        return
    screen.blit(overlay, (0, 0))

    box_w, box_h = 470, 250
    box_x = (con.WIDTH - box_w) // 2
    box_y = (con.HEIGHT - box_h) // 2

    pg.draw.rect(screen, con.BG_COLOR, (box_x, box_y, box_w, box_h), border_radius=12)
    pg.draw.rect(screen, con.TEXT_COLOR, (box_x, box_y, box_w, box_h), width=2, border_radius=12)

    entry = getattr(game, "pending_export_entry", None) or {}
    w.draw_text(lang.t("export_exists", "This video was already exported."), con.TEXT_COLOR, con.WIDTH // 2, box_y + 38, center=True)
    w.draw_small(f'{lang.t("exported_at", "Exported")}: {entry.get("exported", "-")}', con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 82, center=True)
    w.draw_small(lang.t("settings", "Settings"), con.TEXT_COLOR, con.WIDTH // 2, box_y + 114, center=True)
    w.draw_small(f'{lang.t("export_format", "Format")}: {entry.get("format", "MP4")}   {lang.t("export_quality", "Quality")}: {entry.get("quality", "-")}', con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 140, center=True)
    w.draw_small(f'{lang.t("export_resolution", "Resolution")}: {entry.get("resolution", "-")}   FPS: {entry.get("fps", "-")}', con.DIMMED_TEXT_COLOR, con.WIDTH // 2, box_y + 163, center=True)

    fk = ah.effective_focus_key(game, mx, my)
    buttons = bt.export_exists_buttons.get(game)
    buttons["yes"].draw(mx, my, focus_key=fk)
    buttons["no"].draw(mx, my, focus_key=fk)


def draw_history(game: Any, mx: int, my: int) -> None:
    """Draw match history list with filters and scrollbar."""
    w.draw_title(lang.t("histo", "History"), con.TEXT_COLOR, con.WIDTH // 2, 50)
    fk = ah.effective_focus_key(game, mx, my)
    bt.history_back_button.get(game)["back"].draw(mx, my, focus_key=fk)

    if not game.history_entries:
        w.draw_text(lang.t("no_history_entries", "No game saved until now, but you can change that."), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 200)
        return

    filter_buttons = bt.history_filter_buttons.get(game)
    size_options = [("size_all", None)] + [(f"size_{n}", n) for n in con.DIFFICULTIES]
    for key, val in size_options:
        button = filter_buttons[key]
        button.active = (game.history_filter_size == val)
        button.draw(mx, my, focus_key=fk)

    filter_buttons["top10"].active = game.history_filter_top10
    filter_buttons["top10"].draw(mx, my, focus_key=fk)

    if "ultra" in filter_buttons:
        filter_buttons["ultra"].active = game.history_filter_ultra
        filter_buttons["ultra"].draw(mx, my, focus_key=fk)

    entries = game.filtered_history()
    if not entries:
        w.draw_text(lang.t("no_matches", "No game matchs your filters!"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 230)
        return

    track = helpers.history_scrollbar_track()
    screen = w.get_screen()
    if screen is None:
        return

    clip_area = pg.Rect(0, track.y - 4, con.WIDTH, track.height + 8)
    screen.set_clip(clip_area)
    for i, entry in enumerate(entries):
        entry_rect = helpers.history_entry_rect(i, game.history_scroll_y)
        delete_rect = helpers.history_delete_rect(i, game.history_scroll_y)
        if entry_rect.bottom < track.y - 4 or entry_rect.top > track.y - 4 + track.height:
            continue
        is_hovered = entry_rect.collidepoint(mx, my)
        w.draw_panel_row(entry_rect, is_hovered, focused=(fk == f"entry_{i}"))
        w.draw_small(entry["label"], con.WHITE, entry_rect.x + 14, entry_rect.y + 11, center=False)
        if entry.get("ultra"):
            w.draw_small(lang.t("ultra", "ULTRA"), con.SHINE, entry_rect.x + 250, entry_rect.centery)
        w.draw_small(f'{entry["size"]}x{entry["size"]}', con.WHITE, entry_rect.x + 360, entry_rect.centery)
        w.draw_small(helpers.format_duration(entry["play_time"]), con.WHITE, entry_rect.x + 480, entry_rect.centery)
        w.draw_button(delete_rect, "x", delete_rect.collidepoint(mx, my), focused=(fk == f"delete_{i}"))
    screen.set_clip(None)

    w.draw_scrollbar(track, helpers.history_content_height(len(entries)), track.height, -game.history_scroll_y, mx, my, game.history_scroll_last)


def _draw_full_grid(
    grid: list[list[int]],
    row_sums: list[int],
    col_sums: list[int],
    user_sel: list[list[bool]],
    user_dimmed: list[list[bool]],
    n: int,
    offset_x: int,
    offset_y: int,
    highlight_cell: tuple[int, int] | None = None,
    highlight_color: tuple[int, int, int] | None = None,
    ultra: bool = False,
) -> None:
    screen = w.get_screen()
    if screen is None:
        return

    for c in range(n):
        cx = offset_x + (c + 1) * con.CELL_SIZE + con.CELL_SIZE // 2
        cy = offset_y + con.CELL_SIZE // 2
        w.draw_text(str(col_sums[c]), con.TARGET_COLOR, cx, cy)

    for r in range(n):
        cx = offset_x + con.CELL_SIZE // 2
        cy = offset_y + (r + 1) * con.CELL_SIZE + con.CELL_SIZE // 2
        w.draw_text(str(row_sums[r]), con.TARGET_COLOR, cx, cy)

    row_fulfilled = [sum(grid[r][c] for c in range(n) if user_sel[r][c]) == row_sums[r] for r in range(n)]
    col_fulfilled = [sum(grid[r][c] for r in range(n) if user_sel[r][c]) == col_sums[c] for c in range(n)]

    for r in range(n):
        for c in range(n):
            rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE)
            is_dimmed = user_dimmed[r][c] or ((row_fulfilled[r] or col_fulfilled[c]) and not user_sel[r][c])
            if user_sel[r][c]:
                pg.draw.rect(screen, con.SELECTED_COLOR, rect)
            pg.draw.rect(screen, con.GRID_COLOR, rect, 2)
            color = con.DIMMED_TEXT_COLOR if is_dimmed else con.TEXT_COLOR
            w.draw_text(str(grid[r][c]), color, rect.centerx, rect.centery)
            if highlight_cell == (r, c):
                pg.draw.rect(screen, highlight_color or con.GOLD, rect, 4)

    w.draw_outer_border(offset_x, offset_y, n, con.CELL_SIZE, ultra=ultra)
    w.draw_fulfilled_indicators(grid, user_sel, row_sums, col_sums, n, offset_x, offset_y, con.CELL_SIZE)


def draw_history_detail(game: Any, mx: int, my: int) -> None:
    """Draw detail view of a historical match replay."""
    data = game.selected_history_data
    if not data:
        game.state = "HISTORY"
        return

    fk = ah.effective_focus_key(game, mx, my)
    detail_buttons = bt.history_detail_buttons.get(game)
    detail_buttons["back"].draw(mx, my, focus_key=fk)

    n = len(data["grid"])
    offset_x, offset_y = 120 - (n - 4) * 30, 135 - (n - 4) * 20
    hints_x = offset_x + 220 + (n - 4) * 60
    action_y_offset = 8 if n == 7 else 11
    actions = data.get("actions", [])

    user_sel, user_dimmed, hints_used, play_time, last_action = re.reconstruct_state(data, game.detail_selected_index)
    is_start_view = (game.detail_selected_index == -1)

    highlight_cell = None
    highlight_color = None
    if last_action and not is_start_view:
        highlight_cell = (last_action["r"], last_action["c"])
        if last_action.get("Undone"):
            highlight_color = con.UNDONE_COLOR
        else:
            highlight_color = con.ACTION_HIGHLIGHT_COLOR.get(last_action.get("type"), con.GOLD)

    if not data.get("ultra"):
        data["ultra"] = False

    _draw_full_grid(data["grid"], data["row_sums"], data["col_sums"], user_sel, user_dimmed, n, offset_x, offset_y, highlight_cell, highlight_color, data["ultra"])

    footer_y = offset_y + (n + 1) * con.CELL_SIZE + 14
    minutes = play_time // 60000
    seconds = play_time // 1000
    ms = play_time % 1000

    if minutes < 1:
        time_text = lang.t("time", "Time: ") + f"{seconds:02}:{ms:03}s"
    else:
        time_text = lang.t("time", "Time: ") + f"{minutes}:{(seconds % 60):02}:{ms:03}min"

    w.draw_tiny(time_text, con.TEXT_COLOR, offset_x, footer_y - 10, center=False)

    hints_text = lang.t("hints", "Hints used: ") + f"{hints_used}"
    w.draw_tiny(hints_text, con.TEXT_COLOR, hints_x, footer_y - 10, center=False)

    if is_start_view:
        w.draw_tiny(lang.t("action_start", "Action: Start"), con.TEXT_COLOR, offset_x, footer_y + action_y_offset, center=False)
    elif last_action:
        label = lang.t(con.ACTION_LABELS.get(last_action.get("type", "Left"), last_action.get("type", "?")), con.ACTION_LABELS.get(last_action.get("type", "Left"), last_action.get("type", "?")))
        action_text = (lang.t("action", "Action: ") + str(label) + lang.t("row", " (Row: ") + str(last_action['r'] + 1) + lang.t("column", " / Column: ") + str(last_action['c'] + 1) + ")")
        w.draw_tiny(action_text, con.TEXT_COLOR, offset_x, footer_y + action_y_offset, center=False)
    else:
        w.draw_tiny(lang.t("end", "End of game"), con.DIMMED_TEXT_COLOR, offset_x, footer_y + action_y_offset, center=False)

    detail_buttons["export_mp4"].draw(mx, my, focus_key=fk)

    quality_name, _ = con.EXPORT_QUALITIES[game.export_quality_idx]
    detail_buttons["export_quality"].label = lang.t(quality_name, quality_name)
    detail_buttons["export_quality"].draw(mx, my, focus_key=fk)

    fps_value = con.EXPORT_FPS_CHOICES[game.export_fps_idx]
    detail_buttons["export_fps"].label = f"{fps_value} FPS"
    detail_buttons["export_fps"].draw(mx, my, focus_key=fk)

    detail_buttons["detail_reset"].draw(mx, my, focus_key=fk)

    screen = w.get_screen()
    if screen is None:
        return

    display_actions = helpers.detail_display_actions(data)
    detail_count = len(display_actions)
    track = helpers.DETAIL_SCROLLBAR_TRACK
    w.draw_scrollbar(track, detail_count * 34, 438, -game.detail_scroll_y, mx, my, game.detail_scroll_last)

    clip_area = pg.Rect(530, 120, 250, 440)
    screen.set_clip(clip_area)
    for i, act in enumerate(display_actions):
        rect = helpers.detail_action_rect(i, game.detail_scroll_y)
        if rect.bottom < 120 or rect.top > 560:
            continue
        is_hovered = rect.collidepoint(mx, my)
        real_index = i - 1
        is_selected = (game.detail_selected_index == real_index)
        key = helpers.detail_key_for(i)
        w.draw_panel_row(rect, is_hovered, highlighted=is_selected, focused=(fk == key))
        text_color = con.TEXT_COLOR if is_selected else con.WHITE
        second = (act["time"] // 1000) % 60
        ms_ = act["time"] % 1000
        minutes = act["time"] // 60000
        check = data["play_time"]
        if act.get("synthetic"):
            line = "00:000s: " + lang.t("start", "Start") if check < 60000 else "0:00:000min: " + lang.t("start", "Start")
        else:
            label = lang.t(con.ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?")), con.ACTION_LABELS.get(act.get("type", "Left"), act.get("type", "?")))
            if check < 60000:
                line = f'{second:02}:{ms_:03}s: R{act["r"] + 1}/C{act["c"] + 1} - {label}'
            else:
                line = f'{minutes}:{second:02}:{ms_:03}min: R{act["r"] + 1}/C{act["c"] + 1} - {label}'
        w.draw_tiny(line, text_color, rect.x + 8, rect.y + 7, center=False)
    screen.set_clip(None)

    if not actions:
        w.draw_small(lang.t("action_found", "No action found"), con.DIMMED_TEXT_COLOR, 665, 145)


def draw_play(game: Any, mx: int, my: int) -> None:
    """Draw the active match grid screen."""
    buttons = bt.play_buttons.get(game)
    fk = ah.effective_focus_key(game, mx, my)
    buttons["back"].draw(mx, my, focus_key=fk)

    n = game.n
    offset_x, offset_y = helpers.play_grid_offset(n)

    for r in range(n):
        if sum(game.grid[r][c] for c in range(n) if game.user_sel[r][c]) == game.row_sums[r]:
            game.row_fulfilled[r] = True
    for c in range(n):
        if sum(game.grid[r][c] for r in range(n) if game.user_sel[r][c]) == game.col_sums[c]:
            game.col_fulfilled[c] = True

    hover_r = hover_c = None
    if not game.won and not game.paused and \
       offset_x + con.CELL_SIZE <= mx < offset_x + (n + 1) * con.CELL_SIZE and \
       offset_y + con.CELL_SIZE <= my < offset_y + (n + 1) * con.CELL_SIZE:
        hover_c = (mx - offset_x - con.CELL_SIZE) // con.CELL_SIZE
        hover_r = (my - offset_y - con.CELL_SIZE) // con.CELL_SIZE
    w.draw_hover_cross(offset_x, offset_y, n, con.CELL_SIZE, hover_r, hover_c)

    for c in range(n):
        cx = offset_x + (c + 1) * con.CELL_SIZE + con.CELL_SIZE // 2
        cy = offset_y + con.CELL_SIZE // 2
        w.draw_text(str(game.col_sums[c]), con.TARGET_COLOR, cx, cy)

    for r in range(n):
        cx = offset_x + con.CELL_SIZE // 2
        cy = offset_y + (r + 1) * con.CELL_SIZE + con.CELL_SIZE // 2
        w.draw_text(str(game.row_sums[r]), con.TARGET_COLOR, cx, cy)

    flashing_cell = None
    if game.last_hint_cell is not None and pg.time.get_ticks() - game.hint_flash_timer < 900:
        flashing_cell = game.last_hint_cell

    screen = w.get_screen()
    if screen is not None:
        for r in range(n):
            for c in range(n):
                rect = pg.Rect(offset_x + (c + 1) * con.CELL_SIZE, offset_y + (r + 1) * con.CELL_SIZE, con.CELL_SIZE, con.CELL_SIZE)
                is_dimmed = game.user_dimmed[r][c] or ((game.row_fulfilled[r] or game.col_fulfilled[c]) and not game.user_sel[r][c])

                if game.user_sel[r][c]:
                    pg.draw.rect(screen, con.SELECTED_COLOR, rect)
                elif rect.collidepoint(mx, my) and not is_dimmed and not game.won and not game.paused:
                    pg.draw.rect(screen, con.HOVER_COLOR, rect)

                pg.draw.rect(screen, con.GRID_COLOR, rect, 2)
                color = con.DIMMED_TEXT_COLOR if is_dimmed else con.TEXT_COLOR
                w.draw_text(str(game.grid[r][c]), color, rect.centerx, rect.centery)

                if flashing_cell == (r, c):
                    pg.draw.rect(screen, con.GOLD, rect, 4)

                if game.alt_control and not game.won and not game.paused and (r, c) == (game.cursor_r, game.cursor_c):
                    pg.draw.rect(screen, con.FOCUS_COLOR, rect, 3)

        w.draw_outer_border(offset_x, offset_y, n, con.CELL_SIZE)
        w.draw_fulfilled_indicators(game.grid, game.user_sel, game.row_sums, game.col_sums, n, offset_x, offset_y, con.CELL_SIZE)

    buttons["hint"].label = lang.t("hint", "Hint ") + f"({game.hints_left})"
    buttons["hint"].enabled = game.hints_left > 0 and not game.won and not game.paused
    buttons["hint"].draw(mx, my)
    buttons["undo"].enabled = bool(game.current_game_actions) and not game.won and not game.paused
    buttons["undo"].draw(mx, my)
    buttons["restart"].draw(mx, my, focus_key=fk)
    buttons["pause"].enabled = not game.won
    buttons["pause"].draw(mx, my)

    if game.timer_enabled:
        seconds = (game.play_time // 1000) % 60
        minutes = (game.play_time // 60000)
        if game.timer_ms:
            ms = game.play_time % 1000
            time_string = lang.t("time", "Time: ") + f"{minutes:02}:{seconds:02}:{ms:03}"
        else:
            time_string = lang.t("time", "Time: ") + f"{minutes:02}:{seconds:02}"
        w.draw_text(time_string, con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT - 20)

    if game.won:
        w.draw_title(lang.t("won", "You have Won"), con.GREEN, con.WIDTH // 2, con.HEIGHT - 55)

    if game.paused and screen is not None:
        overlay = pg.Surface((con.WIDTH, con.HEIGHT))
        overlay.fill(con.PAUSE)
        screen.blit(overlay, (0, 0))
        w.draw_title(lang.t("paused", "Paused"), con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2 - 45)
        buttons["menu"].draw(mx, my, focus_key=fk)
        buttons["break"].draw(mx, my, focus_key=fk)
        buttons["new"].draw(mx, my, focus_key=fk)
        w.draw_small(lang.t("pressing", "Press ") + str(game.keybindings["pause"]["key"]).capitalize() + (" + CTRL / META " if game.keybindings["pause"]["ctrl"] != False else "") + lang.t("contin", " or the <<Continue>> Button to retrun"), con.TEXT_COLOR, con.WIDTH // 2, con.HEIGHT // 2)


def draw_tutorial(game: Any, mx: int, my: int) -> None:
    """Draw the compact tutorial overview (Kurzhilfe) overlay."""
    fk = ah.effective_focus_key(game, mx, my)
    buttons = bt.tutorial_buttons.get(game)

    w.draw_title(lang.t("tutorial_title", "Tutorial"), con.TEXT_COLOR, con.WIDTH // 2, 55)
    w.draw_small(
        lang.t("tutorial_overview_sub", "Quick overview of the basic game functionality"),
        con.DIMMED_TEXT_COLOR,
        con.WIDTH // 2,
        100,
    )
    lines = helpers.TUTORIAL_OVERVIEW
    y = 165
    for line in lines:
        if line:
            w.draw_small(
                lang.t(f"tutorial_overview_line_{y}", line),
                con.TEXT_COLOR,
                60,
                y,
                center=False,
            )
        y += 28

    buttons["back"].draw(mx, my, focus_key=fk)


def draw_resume_choice(game: Any, mx: int, my: int) -> None:
    """Draw resume vs. new game selection screen."""
    n = game.pending_new_n
    ultra = game.pending_new_ultra
    mode_label = lang.t("ultra_l", "Ultra") if ultra else lang.t("normal", "Normal")
    fk = ah.effective_focus_key(game, mx, my)

    w.draw_title(lang.t("unfinished", "Unfinished game found"), con.TEXT_COLOR, con.WIDTH // 2, 120)
    w.draw_text(f"{n}x{n} - {mode_label}", con.TEXT_COLOR, con.WIDTH // 2, 175)
    w.draw_small(lang.t("ask_return", "Would you like to resume or to start a new match?"), con.DIMMED_TEXT_COLOR, con.WIDTH // 2, 220)

    buttons = bt.resume_choice_buttons.get(game)
    buttons["resume"].draw(mx, my, focus_key=fk)
    buttons["new"].draw(mx, my, focus_key=fk)
    buttons["cancel"].draw(mx, my, focus_key=fk)


def draw_hannah(game: Any, mx: int, my: int) -> None:
    """Draw easter egg level select / play view."""
    fk = ah.effective_focus_key(game, mx, my)
    if game.hannah_open_index is None:
        w.draw_title("Jay Loves", con.TEXT_COLOR, con.WIDTH // 2, 70)
        bt.hannah_buttons.get(game)["back"].draw(mx, my, focus_key=fk)
        screen = w.get_screen()
        if screen is None:
            return
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
        w.draw_scrollbar(track, hannah_content_width(), con.HANNAH_VISIBLE_LENGTH, -game.hannah_scroll_x, mx, my, game.hannah_scroll_last, vertical=False)
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
        if screen is not None:
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