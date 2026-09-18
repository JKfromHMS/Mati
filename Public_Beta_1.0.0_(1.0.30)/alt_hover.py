"""Keyboard navigation and focus management for the game's screens.

This module contains keyboard/mouse focus traversal logic for the game's UI,
including dynamic return paths and scroll-aware focus handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import buttons as bt
import config as con
import helpers
from helpers import hannah_scroll_bounds, history_scroll_bounds

if TYPE_CHECKING:
    from game import Game


FocusOrder = list[tuple[str, pg.Rect]]


_NeighborMap = dict[str, dict[str, str | None]]


def _lookup_neighbor(
    neighbors: _NeighborMap,
    key: str,
    direction: str,
) -> str | None:
    """Return the target for a UI key and navigation direction."""
    return neighbors.get(key, {}).get(direction)


_MENU_NEIGHBORS: _NeighborMap = {
    "start_4": {"down": "start_5", "up": None, "left": None, "right": None},
    "start_5": {"down": "start_6", "up": "start_4", "left": None, "right": None},
    "start_6": {"down": "start_7", "up": "start_5", "left": None, "right": None},
    "start_7": {"down": "settings", "up": "start_6", "left": None, "right": None},
    "settings": {"down": "history", "up": "start_7", "left": None, "right": None},
    "history": {"down": "quit", "up": "settings", "left": None, "right": None},
    "quit": {"down": None, "up": "history", "left": None, "right": None},
}

_ACHIEVEMENTS_NEIGHBORS: _NeighborMap = {
    "back": {"down": None, "up": None, "left": None, "right": None},
}

_ABOUT_NEIGHBORS: _NeighborMap = {
    "back": {"down": None, "up": None, "left": None, "right": None},
}

_BINARY_DIALOG_NEIGHBORS: _NeighborMap = {
    "yes": {"left": None, "right": "no", "up": None, "down": None},
    "no": {"left": "yes", "right": None, "up": None, "down": None},
}

_RESUME_NEIGHBORS: _NeighborMap = {
    "resume": {"right": "new", "left": None, "up": None, "down": None},
    "new": {"left": "resume", "right": "cancel", "up": None, "down": None},
    "cancel": {"left": "new", "right": None, "up": None, "down": None},
}

_TUTORIAL_NEIGHBORS: _NeighborMap = {
    "back": {"down": "close", "up": None, "left": None, "right": "close"},
    "close": {"up": "back", "down": None, "left": None, "right": None},
}

_STATS_NEIGHBORS: _NeighborMap = {
    "back": {"down": "size", "up": None, "left": None, "right": "size"},
    "size": {"down": None, "up": "back", "left": "back", "right": "mode"},
    "mode": {"down": None, "up": "back", "left": "size", "right": "games"},
    "games": {"down": None, "up": "back", "left": "mode", "right": "best"},
    "best": {"down": None, "up": "back", "left": "games", "right": "average"},
    "average": {"down": None, "up": "back", "left": "best", "right": None},
}

_HISTORY_NEIGHBORS_WITHOUT_ULTRA: _NeighborMap = {
    "back": {"down": "size_all", "up": None, "left": None, "right": "size_all"},
    "size_all": {
        "down": "top10",
        "up": "back",
        "left": "back",
        "right": "size_4",
    },
    "size_4": {
        "down": "top10",
        "up": "back",
        "left": "size_all",
        "right": "size_5",
    },
    "size_5": {
        "down": "top10",
        "up": "back",
        "left": "size_4",
        "right": "size_6",
    },
    "size_6": {
        "down": "top10",
        "up": "back",
        "left": "size_5",
        "right": "size_7",
    },
    "size_7": {
        "down": "top10",
        "up": "back",
        "left": "size_6",
        "right": None,
    },
    "top10": {
        "down": "entry_0",
        "up": "size_5",
        "left": None,
        "right": None,
    },
}

_HISTORY_NEIGHBORS_WITH_ULTRA: _NeighborMap = {
    "back": {"down": "size_all", "up": None, "left": None, "right": "size_all"},
    "size_all": {
        "down": "top10",
        "up": "back",
        "left": "back",
        "right": "size_4",
    },
    "size_4": {
        "down": "top10",
        "up": "back",
        "left": "size_all",
        "right": "size_5",
    },
    "size_5": {
        "down": None,
        "up": "back",
        "left": "size_4",
        "right": "size_6",
    },
    "size_6": {
        "down": "ultra",
        "up": "back",
        "left": "size_5",
        "right": "size_7",
    },
    "size_7": {
        "down": "ultra",
        "up": "back",
        "left": "size_6",
        "right": None,
    },
    "top10": {
        "down": "entry_0",
        "up": "size_4",
        "left": None,
        "right": "ultra",
    },
    "ultra": {
        "down": "entry_0",
        "up": "size_6",
        "left": "top10",
        "right": None,
    },
}


def _hardcoded_neighbor(
    game: Game,
    key: str,
    direction: str,
) -> str | None:
    """Determine the default neighboring UI element.

    Dynamic settings and history targets are resolved from the current game
    state. Static navigation maps are kept outside this function so they are
    easy to inspect and do not need to be rebuilt on every call.
    """
    match game.state:
        case "MENU":
            return _lookup_neighbor(_MENU_NEIGHBORS, key, direction)

        case "SETTINGS":
            terminal_found = bool(
                getattr(game, "achievements", {}).get("terminal_found")
            )

            if terminal_found:
                neighbors: _NeighborMap = {
                    "back": {
                        "down": "toggle_history",
                        "up": None,
                        "left": None,
                        "right": "toggle_history",
                    },
                    "toggle_history": {
                        "down": "toggle_sound",
                        "up": "back",
                        "left": "back",
                        "right": "toggle_ultra_timer",
                    },
                    "toggle_sound": {
                        "down": "toggle_alt_control",
                        "up": "toggle_history",
                        "left": "back",
                        "right": (
                            "toggle_ultra_timer_ms"
                            if game.ultra_timer_enabled
                            else "toggle_ultra_timer_clock"
                        ),
                    },
                    "toggle_alt_control": {
                        "down": "toggle_timer",
                        "up": "toggle_sound",
                        "left": "back",
                        "right": (
                            "toggle_ultra_timer_clock"
                            if game.ultra_timer_enabled
                            else None
                        ),
                    },
                    "toggle_timer": {
                        "down": (
                            "toggle_ms" if game.timer_enabled else "stats"
                        ),
                        "up": "toggle_alt_control",
                        "left": "back",
                        "right": "toggle_fullscreen",
                    },
                    "toggle_ms": {
                        "down": "stats",
                        "up": "toggle_timer",
                        "left": "back",
                        "right": "toggle_live_clock",
                    },
                    "toggle_ultra_timer": {
                        "down": (
                            "toggle_ultra_timer_ms"
                            if game.ultra_timer_enabled
                            else "toggle_ultra_timer_clock"
                        ),
                        "up": "back",
                        "left": "toggle_history",
                        "right": None,
                    },
                    "toggle_ultra_timer_ms": {
                        "down": "toggle_ultra_timer_clock",
                        "up": "toggle_ultra_timer",
                        "left": "toggle_sound",
                        "right": None,
                    },
                    "toggle_ultra_timer_clock": {
                        "down": "toggle_fullscreen",
                        "up": (
                            "toggle_ultra_timer_ms"
                            if game.ultra_timer_enabled
                            else "toggle_ultra_timer"
                        ),
                        "left": (
                            "toggle_alt_control"
                            if game.ultra_timer_enabled
                            else "toggle_sound"
                        ),
                        "right": None,
                    },
                    "toggle_fullscreen": {
                        "down": "toggle_live_clock",
                        "up": "toggle_ultra_timer_clock",
                        "left": "toggle_timer",
                        "right": None,
                    },
                    "toggle_live_clock": {
                        "down": "about",
                        "up": "toggle_fullscreen",
                        "left": (
                            "toggle_ms" if game.timer_enabled else None
                        ),
                        "right": None,
                    },
                    "stats": {
                        "down": None,
                        "up": (
                            "toggle_ms"
                            if game.timer_enabled
                            else "toggle_timer"
                        ),
                        "left": None,
                        "right": "achievements",
                    },
                    "achievements": {
                        "down": None,
                        "up": (
                            "toggle_ms"
                            if game.timer_enabled
                            else "toggle_timer"
                        ),
                        "left": "stats",
                        "right": "about",
                    },
                    "about": {
                        "down": None,
                        "up": "toggle_live_clock",
                        "left": "achievements",
                        "right": None,
                    },
                }
            else:
                neighbors = {
                    "back": {
                        "down": "toggle_history",
                        "up": None,
                        "left": None,
                        "right": "toggle_history",
                    },
                    "toggle_history": {
                        "down": "toggle_sound",
                        "up": "back",
                        "left": "back",
                        "right": None,
                    },
                    "toggle_sound": {
                        "down": "toggle_alt_control",
                        "up": "toggle_history",
                        "left": "back",
                        "right": None,
                    },
                    "toggle_alt_control": {
                        "down": "toggle_timer",
                        "up": "toggle_sound",
                        "left": "back",
                        "right": None,
                    },
                    "toggle_timer": {
                        "down": (
                            "toggle_ms" if game.timer_enabled else "stats"
                        ),
                        "up": "toggle_alt_control",
                        "left": "back",
                        "right": "toggle_fullscreen",
                    },
                    "toggle_ms": {
                        "down": "stats",
                        "up": "toggle_timer",
                        "left": "back",
                        "right": "toggle_live_clock",
                    },
                    "toggle_fullscreen": {
                        "down": "toggle_live_clock",
                        "up": "toggle_alt_control",
                        "left": "toggle_timer",
                        "right": None,
                    },
                    "toggle_live_clock": {
                        "down": "about",
                        "up": "toggle_fullscreen",
                        "left": (
                            "toggle_ms" if game.timer_enabled else None
                        ),
                        "right": None,
                    },
                    "stats": {
                        "down": None,
                        "up": (
                            "toggle_ms"
                            if game.timer_enabled
                            else "toggle_timer"
                        ),
                        "left": None,
                        "right": "achievements",
                    },
                    "achievements": {
                        "down": None,
                        "up": (
                            "toggle_ms"
                            if game.timer_enabled
                            else "toggle_timer"
                        ),
                        "left": "stats",
                        "right": "about",
                    },
                    "about": {
                        "down": None,
                        "up": "toggle_live_clock",
                        "left": "achievements",
                        "right": None,
                    },
                }

            return _lookup_neighbor(neighbors, key, direction)

        case "ACHIEVEMENTS":
            return _lookup_neighbor(_ACHIEVEMENTS_NEIGHBORS, key, direction)

        case "ADVANCED_SETTINGS":
            front_current = game.settings.get(
                "input_order_front",
                "action_column_row",
            )
            back_current = game.settings.get(
                "input_order_back",
                "column_row_action",
            )
            front_unselected = next(
                (
                    option
                    for option in con.INPUT_ORDER_FRONT_OPTIONS
                    if option != front_current
                ),
                con.INPUT_ORDER_FRONT_OPTIONS[0],
            )
            back_unselected = next(
                (
                    option
                    for option in con.INPUT_ORDER_BACK_OPTIONS
                    if option != back_current
                ),
                con.INPUT_ORDER_BACK_OPTIONS[0],
            )

            io_keys = {
                option: f"input_order_{index}"
                for index, option in enumerate(con.INPUT_ORDER_OPTIONS)
            }
            keybind_keys = [
                f"keybind_{action}" for action in con.DEFAULT_KEYBINDINGS
            ]

            neighbors: _NeighborMap = {
                "back": {
                    "up": None,
                    "down": "game_volume",
                    "left": None,
                    "right": "game_volume",
                },
                "game_volume": {
                    "up": "back",
                    "down": "terminal_volume",
                    "left": None,
                    "right": io_keys[back_unselected],
                },
                "terminal_volume": {
                    "up": "game_volume",
                    "down": "toggle_terminal_sound",
                    "left": None,
                    "right": io_keys[front_unselected],
                },
                "toggle_terminal_sound": {
                    "up": "terminal_volume",
                    "down": "scale_mode",
                    "left": None,
                    "right": None,
                },
                "scale_mode": {
                    "up": "toggle_terminal_sound",
                    "down": "render_quality",
                    "left": None,
                    "right": None,
                },
                "render_quality": {
                    "up": "scale_mode",
                    "down": "language_dropdown",
                    "left": None,
                    "right": None,
                },
                "language_dropdown": {
                    "up": "render_quality",
                    "down": (
                        "language_option_0"
                        if getattr(game, "language_dropdown_open", False)
                        else None
                    ),
                    "left": None,
                    "right": keybind_keys[0] if keybind_keys else None,
                },
                io_keys["column_row_action"]: {
                    "up": "back",
                    "down": io_keys["row_column_action"],
                    "left": "game_volume",
                    "right": None,
                },
                io_keys["row_column_action"]: {
                    "up": io_keys["column_row_action"],
                    "down": io_keys["action_column_row"],
                    "left": "game_volume",
                    "right": None,
                },
                io_keys["action_column_row"]: {
                    "up": io_keys["row_column_action"],
                    "down": io_keys["action_row_column"],
                    "left": "terminal_volume",
                    "right": None,
                },
                io_keys["action_row_column"]: {
                    "up": io_keys["action_column_row"],
                    "down": keybind_keys[0] if keybind_keys else None,
                    "left": "terminal_volume",
                    "right": None,
                },
            }

            for index, keybind_key in enumerate(keybind_keys):
                neighbors[keybind_key] = {
                    "up": (
                        keybind_keys[index - 1]
                        if index > 0
                        else io_keys["action_row_column"]
                    ),
                    "down": (
                        keybind_keys[index + 1]
                        if index + 1 < len(keybind_keys)
                        else None
                    ),
                    "left": "language_dropdown",
                    "right": None,
                }

            if getattr(game, "language_dropdown_open", False):
                option_keys = [
                    f"language_option_{index}"
                    for index in range(len(helpers.available_languages()))
                ]
                for index, option_key in enumerate(option_keys):
                    neighbors[option_key] = {
                        "up": (
                            option_keys[index - 1]
                            if index > 0
                            else "language_dropdown"
                        ),
                        "down": (
                            option_keys[index + 1]
                            if index + 1 < len(option_keys)
                            else None
                        ),
                        "left": None,
                        "right": None,
                    }

            return _lookup_neighbor(neighbors, key, direction)

        case "ABOUT":
            return _lookup_neighbor(_ABOUT_NEIGHBORS, key, direction)

        case "DELETE_HISTORY" | "EXPORT_EXISTS":
            return _lookup_neighbor(_BINARY_DIALOG_NEIGHBORS, key, direction)

        case "RESUME_CHOICE":
            return _lookup_neighbor(_RESUME_NEIGHBORS, key, direction)

        case "HISTORY":
            has_ultra = any(
                entry.get("ultra") for entry in game.history_entries
            )
            neighbors = (
                _HISTORY_NEIGHBORS_WITH_ULTRA
                if has_ultra
                else _HISTORY_NEIGHBORS_WITHOUT_ULTRA
            )
            return _lookup_neighbor(neighbors, key, direction)

        case "HISTORY_DETAIL":
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

            detail_neighbors: _NeighborMap = {
                "back": {
                    "down": "export_mp4",
                    "up": None,
                    "left": None,
                    "right": "export_mp4",
                },
                "export_mp4": {
                    "down": "export_quality",
                    "up": "back",
                    "left": "back",
                    "right": None,
                },
                "detail_reset": {
                    "down": "action_start",
                    "up": "export_quality",
                    "left": "back",
                    "right": None,
                },
                "export_quality": {
                    "down": "detail_reset",
                    "up": "export_mp4",
                    "left": "back",
                    "right": "export_fps",
                },
                "export_fps": {
                    "down": "detail_reset",
                    "up": "export_mp4",
                    "left": "export_quality",
                    "right": None,
                },
            }
            return _lookup_neighbor(detail_neighbors, key, direction)

        case "STATS":
            return _lookup_neighbor(_STATS_NEIGHBORS, key, direction)

        case "TUTORIAL":
            return _lookup_neighbor(_TUTORIAL_NEIGHBORS, key, direction)

        case "PLAY":
            if getattr(game, "paused", False):
                neighbors = {
                    "menu": {
                        "right": "break",
                        "left": None,
                        "up": None,
                        "down": None,
                    },
                    "break": {
                        "left": "menu",
                        "right": "new",
                        "up": None,
                        "down": None,
                    },
                    "new": {
                        "left": "break",
                        "right": None,
                        "up": None,
                        "down": None,
                    },
                }
                return _lookup_neighbor(neighbors, key, direction)

            if getattr(game, "won", False):
                neighbors = {
                    "back": {
                        "right": "restart",
                        "left": None,
                        "up": None,
                        "down": None,
                    },
                    "restart": {
                        "left": "back",
                        "right": None,
                        "up": None,
                        "down": None,
                    },
                }
                return _lookup_neighbor(neighbors, key, direction)

    return None


def _remembered_neighbor(
    game: Game,
    direction: str,
    *,
    default: str | None,
    attribute: str,
    return_direction: str | None = None,
    use_opposite_direction: bool = False,
) -> str | None:
    """Resolve a temporary navigation return path.

    A remembered return path is consumed only when the user navigates back in
    the expected direction. The stored path is cleared after it is used.
    """
    remembered = getattr(game, attribute, None)
    if remembered is None:
        return default

    origin_key, arrival_direction = remembered

    expected_direction = (
        con.OPPOSITE_DIRECTION.get(arrival_direction)
        if use_opposite_direction
        else return_direction
    )
    if direction != expected_direction:
        return default

    setattr(game, attribute, None)
    return origin_key


def _settings_back_neighbor(game: Game, direction: str) -> str | None:
    """Return the settings back-button target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "back", direction),
        attribute="settings_back_return",
        use_opposite_direction=True,
    )


def _settings_alt_neighbor(game: Game, direction: str) -> str | None:
    """Return the settings alt-control target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "toggle_alt_control", direction),
        attribute="setting_alt_return",
        return_direction="down",
    )


def _settings_achievements_up_neighbor(game: Game) -> str:
    """Return the target above the achievements button."""
    default_left = "toggle_ms" if game.timer_enabled else "toggle_timer"
    portal = getattr(game, "settings_ach_portal", "left")
    return "toggle_live_clock" if portal == "right" else default_left


def _settings_left_terminus_neighbor(
    game: Game,
    direction: str,
) -> str | None:
    """Return the dynamic target from the left settings terminus."""
    terminus_key = "toggle_ms" if game.timer_enabled else "toggle_timer"
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, terminus_key, direction),
        attribute="settings_left_terminus_return",
        use_opposite_direction=True,
    )


def _settings_right_terminus_neighbor(
    game: Game,
    direction: str,
) -> str | None:
    """Return the dynamic target from the right settings terminus."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "toggle_live_clock", direction),
        attribute="settings_right_terminus_return",
        use_opposite_direction=True,
    )


def _adv_language_neighbor(game: Game, direction: str) -> str | None:
    """Return the advanced-settings language target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "language_dropdown", direction),
        attribute="adv_language_return",
        use_opposite_direction=True,
    )


def _detail_back_neighbor(game: Game, direction: str) -> str | None:
    """Return the history-detail back target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "back", direction),
        attribute="detail_back_return",
        return_direction="right",
    )


def _detail_export_neighbor(game: Game, direction: str) -> str | None:
    """Return the history-detail export target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "export_mp4", direction),
        attribute="detail_export_return",
        return_direction="down",
    )


def _hannah_back_neighbor(game: Game) -> str:
    """Consume and return Hannah's stored back-navigation target."""
    origin_key, _ = game.hannah_back_return
    game.hannah_back_return = None
    return origin_key


def _stats_back_neighbor(game: Game, direction: str) -> str | None:
    """Return the stats back target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "back", direction),
        attribute="stats_back_return",
        return_direction="down",
    )


def _history_back_neighbor(game: Game, direction: str) -> str | None:
    """Return the history back target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "back", direction),
        attribute="history_back_return",
        use_opposite_direction=True,
    )


def _history_top10_neighbor(game: Game, direction: str) -> str | None:
    """Return the history Top 10 target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "top10", direction),
        attribute="history_top10_return",
        use_opposite_direction=True,
    )


def _history_top10_down_neighbor(game: Game, direction: str) -> str | None:
    """Return the history Top 10 downward return target."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "top10", direction),
        attribute="history_top10_down_return",
        use_opposite_direction=True,
    )


def _history_ultra_neighbor(game: Game, direction: str) -> str | None:
    """Return the history Ultra target, honoring return memory."""
    return _remembered_neighbor(
        game,
        direction,
        default=_hardcoded_neighbor(game, "ultra", direction),
        attribute="history_ultra_return",
        use_opposite_direction=True,
    )


def _history_size5_down_neighbor(game: Game) -> str:
    """Return the history target below the size-5 filter."""
    last = getattr(game, "history_bottom_last", None)
    return last if last in {"top10", "ultra"} else "entry_0"


def _move_focus_history(
    game: Game,
    order: FocusOrder,
    direction: str,
) -> bool | None:
    """Handle directional UI focus movement within the history view.

    Args:
        game (object): The main game object containing focus key and history state.
        order (List[Tuple[str, object]]): List of tuples pairing UI element keys with
            their bounding rectangles.
        direction (str): The navigation direction (e.g., "up", "down", "left", "right")

    Returns:
        bool | None: True if focus movement was successfully handled, None otherwise.
    """
    lookup = dict(order)
    key = game.focus_key
    entries = game.filtered_history()
    header_keys = [
        key
        for key, _ in order
        if not (key.startswith("entry_") or key.startswith("delete_"))
    ]
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

        match direction:
            case "left" | "right":
                other = "delete" if column == "entry" else "entry"
                other_key = f"{other}_{idx}"

                if other_key in lookup:
                    game.focus_key = other_key
                    game.history_list_column = other
                    ensure_focus_visible(game, order)

                return True

            case "down":
                if idx + 1 < len(entries):
                    game.focus_key = f"{column}_{idx + 1}"
                    ensure_focus_visible(game, order)
                else:
                    game.focus_key = f"{column}_0"
                    ensure_focus_visible(game, order)

                return True

            case "up":
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


def _move_focus_hannah(
    game: Game,
    order: FocusOrder,
    direction: str,
) -> None:
    """Handle directional UI focus movement within the hannah screen.

    Args:
        game (object): The main game object cantaining focus key and hannah state.
        order (List[Tuple[str, object]]): List of tuples pairing UI element keys with
            their bounding rectangles.
        direction (str): The navigation direction (e.g., "up", "down", "left", "right")

    Returns:
        None
    """
    lookup = dict(order)
    key = game.focus_key
    tile_keys = [k for k, _ in order if k.startswith("tile_")]

    if key.startswith("tile_"):
        idx = tile_keys.index(key) if key in tile_keys else 0
        if direction == "right":
            if idx + 1 < len(tile_keys):
                game.focus_key = tile_keys[idx + 1]
                ensure_focus_visible(game, order)
        elif direction == "up":
            game.hannah_back_return = (key, "up")
            game.focus_key = "back"
            ensure_focus_visible(game, order)
        elif direction == "down":
            return
        else:
            if idx - 1 >= 0:
                game.focus_key = tile_keys[idx - 1]
                ensure_focus_visible(game, order)
            elif "back" in lookup:
                game.focus_key = "back"
                ensure_focus_visible(game, order)
    else:
        if (direction == "right" and tile_keys) or (
            direction == "down"
            and tile_keys
            and not getattr(game, "hannah_back_return", None)
        ):
            game.focus_key = tile_keys[0]
            ensure_focus_visible(game, order)
        elif direction == "down" and tile_keys and getattr(game, "hannah_back_return", None):
            nxt = _hannah_back_neighbor(game)
            game.focus_key = nxt
            ensure_focus_visible(game, order)


def focus_order(game: Game) -> FocusOrder:
    """Retrieve the ordered list of focusable UI elements and their bounding rectangles
    for the current game state.

    Args:
        game (object): The main game object containing state details and UI configurations.

    Returns:
        List[Tuple[str, object]]: A list of tuples pairing UI element keys with their
            bounding rectangles.
    """
    order = []

    match game.state:
        case "MENU":
            order = list(bt.as_rects(bt.menu_buttons.get(game)).items())

        case "SETTINGS":
            order = list(bt.as_rects(bt.settings_buttons.get(game)).items())

        case "ADVANCED_SETTINGS":
            # Start with the button rects, then insert slider rects so
            # keyboard focus can reach the volume controls.
            order = list(bt.as_rects(bt.advanced_settings_buttons.get(game)).items())
            # Insert sliders after the back button if present
            back_index = next((i for i, (k, _) in enumerate(order) if k == "back"), 0)
            # Avoid duplicate keys if they somehow exist
            keys = {k for k, _ in order}
            insert_at = back_index + 1
            if "game_volume" not in keys:
                order.insert(insert_at, ("game_volume", bt.ADV_GAME_VOLUME_RECT))
                insert_at += 1
            if "terminal_volume" not in keys:
                order.insert(insert_at, ("terminal_volume", bt.ADV_TERMINAL_VOLUME_RECT))

        case "ABOUT":
            order = [("back", helpers.BTN_BACK)]

        case "STATS":
            order = [("back", helpers.BTN_BACK)]
            # The sortable column headers are keyboard/mouse focus targets too,
            # so arrow navigation and the focus ring can reach them.
            order += list(bt.as_rects(bt.stats_header_buttons.get(game)).items())

        case "ACHIEVEMENTS":
            order = [("back", helpers.BTN_BACK)]

        case "HISTORY":
            order = [("back", helpers.BTN_BACK)]
            if game.history_entries:
                order += list(bt.as_rects(bt.history_filter_buttons.get(game)).items())
                for i, _ in enumerate(game.filtered_history()):
                    order.extend([
                        (f"entry_{i}", helpers.history_entry_rect(i, game.history_scroll_y)),
                        (f"delete_{i}", helpers.history_delete_rect(i, game.history_scroll_y))
                    ])

        case "HISTORY_DETAIL":
            order = list(bt.as_rects(bt.history_detail_buttons.get(game)).items())

            if game.selected_history_data:
                display_actions = helpers.detail_display_actions(game.selected_history_data)
                for i in range(len(display_actions)):
                    order.append(
                        (
                            helpers.detail_key_for(i),
                            helpers.detail_action_rect(i, game.detail_scroll_y),
                        )
                    )

        case "DELETE_HISTORY":
            order = list(bt.as_rects(bt.delete_confirm_buttons.get(game)).items())

        case "EXPORT_EXISTS":
            order = list(bt.as_rects(bt.export_exists_buttons.get(game)).items())

        case "RESUME_CHOICE":
            order = list(bt.as_rects(bt.resume_choice_buttons.get(game)).items())

        case "HANNAH":
            if getattr(game, "hannah_open_index", None) is None:
                order = [("back", helpers.BTN_BACK)]
                for i, lvl in enumerate(getattr(game, "hannah_levels", [])):
                    if lvl is None:
                        continue
                    order.append((f"tile_{i}", helpers.hannah_tile_rect(i, game.hannah_scroll_x)))

        case "TUTORIAL":
            order = list(bt.as_rects(bt.tutorial_buttons.get(game)).items())

        case "PLAY":
            buttons = bt.play_buttons.get(game)

            if getattr(game, "paused", False):
                order = [
                    ("menu", buttons["menu"].rect),
                    ("break", buttons["break"].rect),
                    ("new", buttons["new"].rect)
                ]

            elif getattr(game, "won", False):
                order = [
                    ("back", buttons["back"].rect),
                    ("restart", buttons["restart"].rect)
                ]

    return order


def move_focus(
    game: Game,
    direction: str,
) -> None:
    """Navigate focus to the appropriate UI element based on current state
    and directional input.

    Args:
        game (object): The main game object containing current state, UI focus
            key, and screen configurations.
        direction (str): The navigation direction (e.g., "up", "down", "left", "right")

    Returns:
        None
    """
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    order = focus_order(game)
    if not order:
        return
    keys = [k for k, _ in order]
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
                if (
                    nxt == "toggle_alt_control"
                    and key != "toggle_alt_control"
                    and direction == "up"
                ):
                    game.setting_alt_return = (key, direction)

        if key == "achievements" and direction == "up":
            nxt = _settings_achievements_up_neighbor(game)

        left_terminus = "toggle_ms" if game.timer_enabled else "toggle_timer"
        if key == left_terminus:
            nxt = _settings_left_terminus_neighbor(game, direction)
        else:
            if (
                nxt == left_terminus
                and key != left_terminus
                and key != "toggle_timer"
                and key != "toggle_alt_control"
            ):
                game.settings_left_terminus_return = (key, direction)

        if key == "toggle_live_clock":
            nxt = _settings_right_terminus_neighbor(game, direction)
        else:
            if (
                nxt == "toggle_live_clock"
                and key != "toggle_live_clock"
                and key != "toggle_fullscreen"
            ):
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

    if state == "STATS":
        if key == "back":
            nxt = _stats_back_neighbor(game, direction)
        else:
            if nxt == "back" and key != "back":
                game.stats_back_return = (key, direction)

    if nxt is None:
        return
    if nxt in keys:
        game.focus_key = nxt
        ensure_focus_visible(game, order)


def effective_focus_key(
    game: Game,
    mx: int,
    my: int,
) -> str | None:
    """Determine the active UI focus key considering keyboard activity, mouse
    hover, and input idle timeouts.

    Args:
        game (object): The main game object containing focus state, control settings,
            and mouse timing attributes.
        mx (int): The current horizontal mouse coordinate.
        my (int): The current vertical mouse coordinate.

    Returns:
        str | None: The key of the currently effective focused UI element, or None
            if alternative controls are disabled or no focus order exists.
    """
    if not game.alt_control:
        return None
    order = focus_order(game)
    if not order:
        return None

    keys = [k for k, _ in order]
    if game.focus_key not in keys:
        game.focus_key = keys[0]
    now = pg.time.get_ticks()

    hovered_key = None
    for key, rect in order:
        if rect.collidepoint(mx, my):
            hovered_key = key
            break

    moved = (mx, my) != getattr(game, "last_mouse_pos", (mx, my))
    game.last_mouse_pos = (mx, my)
    if hovered_key != getattr(game, "mouse_hover_key", None) or moved:
        pg.mouse.set_visible(True)
        game.mouse_hover_key = hovered_key
        game.mouse_hover_start = now

    if getattr(game, "focus_lock_until", 0) > now:
        return game.focus_key
    idle_ms = now - getattr(game, "last_key_time", 0)
    hover_ms = now - getattr(game, "mouse_hover_start", 0)
    if idle_ms >= con.FOCUS_IDLE_MS and hovered_key and hover_ms >= con.FOCUS_IDLE_MS:
        pg.mouse.set_visible(False)
        return hovered_key

    return game.focus_key


def ensure_focus_visible(
    game: Game,
    order: list[tuple[str, pg.Rect]],
) -> None:
    """Adjust scrolling to keep the focused UI elements visible.

    Args:
        game: The main game instance.
        order: UI elements paired with their bounding rectangles.
    """
    lookup = dict(order)
    rect = lookup.get(game.focus_key)

    if rect is None:
        return

    match game.state, game.focus_key:
        case "HISTORY", focus_key if focus_key.startswith(
            ("entry_", "delete_")
        ):
            margin = con.ENTRY_SPACING // 2
            visible_top = con.LIST_TOP
            visible_bottom = con.HISTORY_VISIBLE_BOTTOM

            if rect.top < visible_top:
                game.history_scroll_y += (
                    visible_top - rect.top
                ) + margin
                game.history_scroll_y = min(
                    game.history_scroll_y,
                    0,
                )
                game.history_scroll_last = pg.time.get_ticks()

            elif rect.bottom > visible_bottom:
                game.history_scroll_y -= (
                    rect.bottom - visible_bottom
                ) + margin
                game.history_scroll_y = max(
                    history_scroll_bounds(
                        len(game.filtered_history())
                    ),
                    game.history_scroll_y,
                )
                game.history_scroll_last = pg.time.get_ticks()

        case "HISTORY_DETAIL", focus_key if focus_key.startswith("action_"):
            clip_top = 120
            clip_bottom = 560

            if rect.top < clip_top:
                game.detail_scroll_y += (clip_top - rect.top)
                game.detail_scroll_last = pg.time.get_ticks()

            elif rect.bottom > clip_bottom:
                game.detail_scroll_y -= (rect.bottom - clip_bottom)

                count = (
                    len(
                        helpers.detail_display_actions(
                            game.selected_history_data
                            )
                        )
                    if game.selected_history_data
                    else 0
                )

                min_scroll = -max(0, (count * 34) - 440)
                game.detail_scroll_y = max(
                    min_scroll,
                    min(game.detail_scroll_y, 0),
                )
                game.detail_scroll_last = pg.time.get_ticks()

        case "HANNAH", focus_key if focus_key.startswith("tile_"):
            if rect.left < 40:
                game.hannah_scroll_x += (40 - rect.left)
                game.hannah_scroll_x = max(
                    hannah_scroll_bounds(),
                    min(0, game.hannah_scroll_x),
                )
                game.hannah_scroll_last = pg.time.get_ticks()

            elif rect.right > con.WIDTH - 40:
                game.hannah_scroll_x -= (
                    rect.right - (con.WIDTH - 40)
                )
                game.hannah_scroll_x = max(
                    hannah_scroll_bounds(),
                    min(0, game.hannah_scroll_x),
                )
                game.hannah_scroll_last = pg.time.get_ticks()


