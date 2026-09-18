"""Layout math and small reusable helpers for the screens.

This module contains calculation utilities for UI placement, scrolling boundaries,
and formatting values like timestamps or history entries.
"""

### -Imports- ###
from typing import Any

import pygame as pg

import config as con

_Section = tuple[str, list[str], int, int]


def history_content_height(count: int) -> int:
    """Return the total vertical space (in px) taken by ``count`` history rows."""
    if count == 0:
        return 0
    return (count - 1) * con.ENTRY_SPACING + con.ENTRY_HEIGHT


def history_scroll_bounds(count: int) -> int:
    """Return the maximum (negative) scroll offset for a ``count``-row history."""
    content = history_content_height(count)
    if content == 0:
        return 0
    visible = con.HISTORY_VISIBLE_BOTTOM - con.LIST_TOP
    return min(0, visible - content)


def hannah_content_width() -> int:
    """Return the total width of the Hannah easter egg tile strip."""
    total = 40
    last_i = max(i for i, ch in enumerate(con.HANNAH_MESSAGE) if ch)
    for i, letter_char in enumerate(con.HANNAH_MESSAGE):
        if letter_char is None:
            total += con.HANNAH_SPACE_GAP
        else:
            total += con.HANNAH_TITE_SIZE  # Note: Retained "TITE" to match config.py
            if i != last_i:
                total += con.HANNAH_TITE_GAP
    return total


def hannah_scroll_bounds() -> int:
    """Return the maximum (negative) horizontal scroll for the tile strip."""
    return min(0, con.HANNAH_VISIBLE_LENGTH - hannah_content_width())


def settings_sections(game: Any) -> list[_Section]:
    """Build the ``(title, keys, x, y)`` layout sections for the settings screen."""
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))

    timer_rows = ["toggle_timer"]
    if game.timer_enabled:
        timer_rows.append("toggle_ms")

    display_rows = ["toggle_fullscreen", "toggle_live_clock"]
    gameplay_rows = ["toggle_history", "toggle_sound", "toggle_alt_control"]

    sections: list[_Section] = []

    left_x = con.WIDTH // 2 - 235
    right_x = con.WIDTH // 2 + 15
    mid_x = con.WIDTH // 2 - 110
    y = 150

    if terminal_found:
        ultra_rows = ["toggle_ultra_timer"]
        if game.ultra_timer_enabled:
            ultra_rows.extend(["toggle_ultra_timer_ms", "toggle_ultra_timer_clock"])
        else:
            ultra_rows.extend(["toggle_ultra_timer_clock", ""])
            
        sections.extend([
            ("gameplay", gameplay_rows, left_x, y),
            ("timer", timer_rows, left_x, y + 138),
            ("ultra_mode", ultra_rows, right_x, y),
            ("display", display_rows, right_x, y + 138),
        ])
    else:
        sections.extend([
            ("gameplay", gameplay_rows, mid_x, y),
            ("timer", timer_rows, left_x, y + 138),
            ("display", display_rows, right_x, y + 138),
        ])

    return sections


def settings_layout(game: Any) -> tuple[dict[str, pg.Rect], list[tuple[str, int, int]]]:
    """Compute the button rects and section headers for the settings screen."""
    buttons = {"back": BTN_BACK}
    headers: list[tuple[str, int, int]] = []
    sections = settings_sections(game)

    for title, keys, start_x, start_y in sections:
        headers.append((title, start_x, start_y))
        y = start_y + 24
        for key in keys:
            if key:
                buttons[key] = pg.Rect(start_x, y, 220, 32)
            y += 34

    bottom_y = 525
    buttons["stats"] = pg.Rect(con.WIDTH // 2 - 250, bottom_y, 160, 34)
    buttons["achievements"] = pg.Rect(con.WIDTH // 2 - 80, bottom_y, 160, 34)
    buttons["about"] = pg.Rect(con.WIDTH // 2 + 90, bottom_y, 160, 34)

    return buttons, headers


def available_languages() -> list[tuple[str, str]]:
    """Return a list of selectable languages as ``(label, internal_name)``."""
    result: list[tuple[str, str]] = [("English", con.BUILTIN_LANGUAGE)]
    seen: set[str] = {con.BUILTIN_LANGUAGE}
    for folder in con.LANGUAGES_DIRS:
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.smati")):
            stem = path.stem.lower()
            if stem not in seen:
                seen.add(stem)
                result.append((stem.capitalize(), stem))
    return result


### Buttons & Interactive Areas ###
BTN_BACK = pg.Rect(20, 20, 100, 40)

# Invisible click area over the live clock (top-right, centre (WIDTH-55, 26)).
CLOCK_CLICK_RECT = pg.Rect(con.WIDTH - 145, 6, 145, 42)

# Button for the "Close" action on the compact tutorial overview.
TUTORIAL_NEXT_RECT = pg.Rect(con.WIDTH - 160, con.HEIGHT - 60, 140, 40)

# The compact overview opened by clicking the clock: every topic in one page.
TUTORIAL_OVERVIEW: list[str] = [
    "Here is the short version of the tutorial:",
    "",
    "Menu: arrows move the focus, Space / Enter activate.",
    "Rules: select the cells that add up to every row and",
    "  column sum, mark the rest - win when all are done.",
    "History: saved matches, newest first by default.",
    "Detail: click an entry to step through the match.",
    "Terminal: press Ctrl+T in the menu, type 'help'.",
    "Settings: toggle the basics, Ctrl+Right opens advanced.",
    "Achievements: hidden milestones tracked across all games.",
    "Hint / Terminal: the Hint button in-game, and Ctrl+T for",
    "  the quick-access terminal (type 'help' for commands).",
    "Clock: click the live clock in the top-right corner to",
    "  open this overview again.",
]


def fmt_total_time(ms: int) -> str:
    """Format a millisecond duration as a compact ``Xh Ymin`` label."""
    hours, minutes, _, _ = format_duration_short(ms)
    return f"{hours}h {minutes:02}min" if hours else f"{minutes}min"


def fmt_stat_time(ms: int | None) -> str:
    """Format a millisecond duration for the statistics view."""
    if ms is None:
        return "-"
    _, minutes, seconds, msec = format_duration_short(ms)
    return f"{minutes}:{seconds:02}:{msec:03}min" if minutes else f"{seconds}:{msec:03}s"


def format_duration(play_time_ms: int) -> str:
    """Format ``play_time_ms`` as a ``minutes:seconds:ms`` label."""
    _, minutes, seconds, ms = format_duration_short(play_time_ms)
    return f"{minutes}:{seconds:02}:{ms:03}min"


def format_duration_short(play_time_ms: int) -> tuple[int, int, int, int]:
    """Split a millisecond duration into ``(hours, minutes, seconds, ms)``."""
    total_ms = max(0, play_time_ms)
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return hours, minutes, seconds, ms


def milestone_default_index(keys: list[str], achievements: dict[str, Any]) -> int:
    """Return the first not-yet-unlocked milestone index (last one as fallback)."""
    for i, key in enumerate(keys):
        if not achievements.get(key):
            return i
    return len(keys) - 1


def milestone_fraction(current: int, target: int) -> float:
    """Return ``current / target`` clamped to the interval ``[0.0, 1.0]``."""
    if target <= 0:
        return 1.0
    return max(0.0, min(1.0, current / target))


def history_entry_rect(i: int, scroll_y: int) -> pg.Rect:
    """Return the rect of the i-th history entry at the given scroll offset."""
    y = con.LIST_TOP + i * con.ENTRY_SPACING + scroll_y
    return pg.Rect(con.ENTRY_X, y, con.ENTRY_WIDTH - 50, con.ENTRY_HEIGHT)


def history_delete_rect(i: int, scroll_y: int) -> pg.Rect:
    """Return the rect of the delete button for the i-th history entry."""
    y = con.LIST_TOP + i * con.ENTRY_SPACING + scroll_y
    return pg.Rect(con.ENTRY_X + con.ENTRY_WIDTH - 44, y, 40, con.ENTRY_HEIGHT)


def history_scrollbar_track() -> pg.Rect:
    """Return the track rect of the history list scrollbar."""
    return pg.Rect(
        con.ENTRY_X + con.ENTRY_WIDTH + 6, 
        con.LIST_TOP, 
        con.SCROLLBAR_WIDTH, 
        con.HISTORY_VISIBLE_BOTTOM - con.LIST_TOP
    )


DETAIL_EXPORT_BUTTON = pg.Rect(530, 20, 250, 30)
DETAIL_QUALITY_BUTTON = pg.Rect(530, 54, 120, 24)
DETAIL_FPS_BUTTON = pg.Rect(660, 54, 120, 24)
DETAIL_RESET_BUTTON = pg.Rect(530, 86, 250, 26)
DETAIL_SCROLLBAR_TRACK = pg.Rect(785, 120, con.SCROLLBAR_WIDTH, 438)


def detail_action_rect(i: int, scroll_y: int) -> pg.Rect:
    """Return the rect of the i-th action row in the history-detail view."""
    y = 120 + i * 34 + scroll_y
    return pg.Rect(530, y, 250, 30)


def play_grid_offset(n: int) -> tuple[int, int]:
    """Return the top-left ``(x, y)`` offset for drawing an ``n`` x ``n`` grid."""
    offset_x = con.WIDTH // 2 - ((n + 1) * con.CELL_SIZE) // 2
    grid_n = 8 if n == 7 else n  # Correct a 7x7 misdrawing
    offset_y = con.HEIGHT // 2 - ((grid_n + 1) * con.CELL_SIZE) // 2
    return offset_x, offset_y


def detail_display_actions(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all actions of ``data`` with a synthetic ``Start`` entry prepended."""
    actions = data.get("actions", [])
    start_entry = {"time": 0, "type": "Start", "r": None, "c": None, "synthetic": True}
    return [start_entry] + actions


def detail_key_for(i: int) -> str:
    """Map an action index to its keyboard-focus key name."""
    return "action_start" if i == 0 else f"action_{i}"


def hannah_scrollbar_track() -> pg.Rect:
    """Return the track rect of the Hannah easter egg scrollbar."""
    return pg.Rect(
        40, 
        con.HEIGHT - con.SCROLLBAR_WIDTH - 6, 
        con.WIDTH - 80, 
        con.SCROLLBAR_WIDTH
    )


def hannah_tile_rect(index: int, scroll_x: int) -> pg.Rect:
    """Return the rect of the Hannah tile at ``index`` given the scroll offset."""
    x = 40
    for i, letter_char in enumerate(con.HANNAH_MESSAGE):
        if i == index:
            break
        if letter_char is None:
            x += con.HANNAH_SPACE_GAP
        else:
            x += con.HANNAH_TITE_SIZE + con.HANNAH_TITE_GAP
    x += scroll_x
    y = con.HANNAH_STRIP_Y - con.HANNAH_TITE_SIZE // 2
    return pg.Rect(x, y, con.HANNAH_TITE_SIZE, con.HANNAH_TITE_SIZE)


def _achievement_page(title: str, keys: list[str]) -> dict[str, Any]:
    """Bundle one achievement page's title and listed achievement keys."""
    return {"title": title, "keys": keys}


ACHIEVEMENT_PAGES: list[dict[str, Any]] = (
    [
        _achievement_page(
            "General", 
            [f"games_{m}" for m in con.GENERAL_GAME_MILESTONES] + 
            [key for key, _ in con.GENERAL_TIME_MILESTONES]
        )
    ]
    + [
        _achievement_page(
            f"{n}x{n}{' Ultra' if ultra else ''}",
            [f"{m}_{n}x{n}{'_ultra' if ultra else ''}" for m in con.ACHIEVEMENT_MILESTONES] + 
            [key for key, _ in con.TIME_ACHIEVEMENTS.get((n, ultra), [])],
        )
        for n in con.DIFFICULTIES
        for ultra in (False, True)
    ]
    + [_achievement_page("Easter Eggs", con.EASTER_EGG_ACHIEVEMENTS)]
)


def keybinding_label(binding: dict[str, Any]) -> str:
    """Render a keybinding dict as a human readable label (e.g., ``Ctrl+M``)."""
    key_part = binding.get("key", "?").upper()
    return f"Ctrl+{key_part}" if binding.get("ctrl") else key_part