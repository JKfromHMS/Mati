"""Button classes and the per-screen button blueprints."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import Any

import pygame as pg

import config as con
import helpers
import lang
import widgets as w

# --- Constants for UI Layouts ---
ADV_GAME_VOLUME_RECT = pg.Rect(60, 160, 260, 10)
ADV_TERMINAL_VOLUME_RECT = pg.Rect(60, 215, 260, 10)

ACH_PREV_RECT = pg.Rect(20, 250, 37, 100)
ACH_NEXT_RECT = pg.Rect(743, 250, 37, 100)
ACH_GAMES_TILE_RECT = pg.Rect(75, 185, 310, 330)
ACH_TIME_TILE_RECT = pg.Rect(415, 185, 310, 330)
ACH_GAMES_PREV_RECT = pg.Rect(
    ACH_GAMES_TILE_RECT.x + 8,
    ACH_GAMES_TILE_RECT.y + 43,
    con.ACH_TILE_BTN_SIZE,
    con.ACH_TILE_BTN_SIZE,
)
ACH_GAMES_NEXT_RECT = pg.Rect(
    ACH_GAMES_TILE_RECT.right - 8 - con.ACH_TILE_BTN_SIZE,
    ACH_GAMES_TILE_RECT.y + 43,
    con.ACH_TILE_BTN_SIZE,
    con.ACH_TILE_BTN_SIZE,
)


@dataclass(slots=True)
class Button:
    """A single clickable/hoverable/focusable UI element."""
    
    key: str
    rect: pg.Rect
    label: str = ""
    kind: str = "button"
    enabled: bool = True
    active: bool = False
    color: tuple[int, int, int] | None = None
    color_hover: tuple[int, int, int] | None = None
    color_disabled: tuple[int, int, int] | None = None
    text_color: tuple[int, int, int] = con.WHITE

    def is_hovered(self, mx: int, my: int) -> bool:
        """Return whether the enabled button is underneath the given point."""
        return self.enabled and self.rect.collidepoint(mx, my)

    def is_clicked(self, mx: int, my: int) -> bool:
        """Return whether the button is underneath the given point."""
        return self.rect.collidepoint(mx, my)

    def draw(self, mx: int, my: int, focus_key: str | None = None) -> None:
        """Draw the button, selecting the style based on its `kind`."""
        hovered = self.rect.collidepoint(mx, my)
        focused = focus_key is not None and focus_key == self.key

        match self.kind:
            case "toggle":
                w.draw_toggle_button(self.rect, self.label, hovered, self.active, focused=focused)
            case "toggle_history":
                w.draw_toggle_history_button(self.rect, self.label, hovered, self.active, focused=focused)
            case "panel":
                w.draw_panel_row(self.rect, hovered, highlighted=self.active, focused=focused)
            case "nav_arrow_left":
                w.draw_nav_arrow(self.rect, "left", hovered, enabled=self.enabled, focused=focused)
            case "nav_arrow_right":
                w.draw_nav_arrow(self.rect, "right", hovered, enabled=self.enabled, focused=focused)
            case "tile":
                w.draw_achievements_tile(self.rect)
            case _:  # Fallback to standard 'button'
                w.draw_button(
                    self.rect,
                    self.label,
                    hovered,
                    enabled=self.enabled,
                    focused=focused,
                    color=self.color,
                    color_hover=self.color_hover,
                    color_unenabled=self.color_disabled,
                    text_color=self.text_color,
                )


class ButtonSet:
    """Caches the Button objects for one screen, rebuilding them only when necessary."""

    def __init__(
        self,
        build: Callable[[Any], dict[str, Button]],
        signature: Callable[[Any], Hashable] | None = None,
    ) -> None:
        self._build = build
        self._signature_fn = signature or (lambda _game: lang.current_language())
        self._signature: Any = object()  # sentinel forcing the first build
        self._buttons: dict[str, Button] = {}

    def get(self, game: Any) -> dict[str, Button]:
        """Return the current buttons, rebuilt first if the layout state changed."""
        sig = self._signature_fn(game)
        if sig != self._signature:
            self._buttons = self._build(game)
            self._signature = sig
        return self._buttons

    def invalidate(self) -> None:
        """Force the next `get()` call to rebuild regardless of the signature."""
        self._signature = object()


# --- Helpers for working with a dict of Buttons ---

def hit_text(buttons: dict[str, Button], mx: int, my: int) -> str | None:
    """Return the key of the first button underneath `(mx, my)`, or `None`."""
    for key, button in buttons.items():
        if button.is_clicked(mx, my):
            return key
    return None

def as_rects(buttons: dict[str, Button]) -> dict[str, pg.Rect]:
    """Return a plain `{key: rect}` view for legacy non-Button call sites."""
    return {key: button.rect for key, button in buttons.items()}


# --- Build Functions ---

def _build_menu_buttons(game: Any) -> dict[str, Button]:
    buttons: dict[str, Button] = {}
    y = 175

    for n in con.DIFFICULTIES:
        key = f"start_{n}"
        buttons[key] = Button(
            key, 
            pg.Rect(con.WIDTH // 2 - 110, y, 220, 44), 
            lang.t(con.DIFFICULTY_NAMES[n], con.DIFFICULTY_NAMES[n])
        )
        y += 54

    buttons["settings"] = Button("settings", pg.Rect(con.WIDTH // 2 - 110, y + 15, 220, 44), lang.t("settings", "Settings"))
    buttons["history"] = Button("history", pg.Rect(con.WIDTH // 2 - 110, y + 69, 220, 44), lang.t("history", "History"))
    buttons["quit"] = Button("quit", pg.Rect(con.WIDTH // 2 - 110, y + 123, 220, 44), lang.t("quit", "Quit"))

    return buttons


def _build_settings_buttons(game: Any) -> dict[str, Button]:
    rects, _headers = helpers.settings_layout(game)
    buttons: dict[str, Button] = {}

    for key, rect in rects.items():
        kind = "toggle" if key.startswith("toggle") else "button"
        label = lang.t("menu", "Menu") if key == "back" else ""
        buttons[key] = Button(key, rect, label, kind=kind)

    return buttons

def _settings_signature(game: Any) -> tuple[Hashable, ...]:
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    return (
        lang.current_language(), 
        terminal_found, 
        getattr(game, "timer_enabled", None), 
        getattr(game, "ultra_timer_enabled", None)
    )


def _build_advanced_settings_buttons(game: Any) -> dict[str, Button]:
    buttons: dict[str, Button] = {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back"))
    }

    buttons["toggle_terminal_sound"] = Button("toggle_terminal_sound", pg.Rect(60, 245, 220, 34), kind="toggle")
    buttons["scale_mode"] = Button("scale_mode", pg.Rect(60, 283, 220, 34), kind="toggle")
    buttons["render_quality"] = Button("render_quality", pg.Rect(60, 321, 220, 34), kind="toggle")
    buttons["language_dropdown"] = Button("language_dropdown", pg.Rect(60, 415, 220, 34))

    if getattr(game, "language_dropdown_open", False):
        for i, (label, _internal) in enumerate(helpers.available_languages()):
            key = f"language_option_{i}"
            buttons[key] = Button(key, pg.Rect(60, 420 + 34 * (i + 1), 220, 30), label, kind="toggle")

    for i in range(len(con.INPUT_ORDER_OPTIONS)):
        key = f"input_order_{i}"
        buttons[key] = Button(key, pg.Rect(420, 135 + i * 40, 300, 32), kind="toggle")

    for i, action in enumerate(con.DEFAULT_KEYBINDINGS):
        key = f"keybind_{action}"
        buttons[key] = Button(key, pg.Rect(600, 335 + i * 30, 160, 26))

    return buttons

def _advanced_settings_signature(game: Any) -> tuple[Hashable, ...]:
    dropdown_open = getattr(game, "language_dropdown_open", False)
    return (
        lang.current_language(), 
        dropdown_open, 
        len(helpers.available_languages()) if dropdown_open else 0
    )


def _build_play_buttons(game: Any) -> dict[str, Button]:
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("menu", "Menu")),
        "hint": Button("hint", pg.Rect(con.WIDTH - 147, 50, 130, 34), lang.t("hint", "Hint ")),
        "undo": Button("undo", pg.Rect(con.WIDTH - 147, 90, 130, 34), lang.t("undo", "Undo")),
        "restart": Button("restart", pg.Rect(con.WIDTH - 147, 130, 130, 34), lang.t("new", "New")),
        "pause": Button("pause", pg.Rect(con.WIDTH - 147, 170, 130, 34), lang.t("break", "Break")),
        "menu": Button("menu", pg.Rect(con.WIDTH - 650, con.HEIGHT // 2 + 75, 130, 50), lang.t("menu", "Menu")),
        "break": Button("break", pg.Rect(con.WIDTH - 450, con.HEIGHT // 2 + 75, 130, 50), lang.t("continue", "Continue")),
        "new": Button("new", pg.Rect(con.WIDTH - 250, con.HEIGHT // 2 + 75, 130, 50), lang.t("new", "New")),
    }


def _build_resume_choice_buttons(game: Any) -> dict[str, Button]:
    return {
        "resume": Button("resume", pg.Rect(con.WIDTH // 2 - 240, 300, 210, 50), lang.t("resume", "Resume")),
        "new": Button("new", pg.Rect(con.WIDTH // 2 + 30, 300, 210, 50), lang.t("new_game", "New Game")),
        "cancel": Button("cancel", helpers.BTN_BACK, lang.t("back", "Back")),
    }


def _build_hannah_buttons(game: Any) -> dict[str, Button]:
    return {"back": Button("back", helpers.BTN_BACK, lang.t("menu", "Menu"))}


def _build_hannah_play_buttons(game: Any) -> dict[str, Button]:
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back")),
        "undo": Button("undo", pg.Rect(con.WIDTH - 150, 20, 130, 34), lang.t("undo", "Undo")),
    }


def _history_has_ultra_entries(game: Any) -> bool:
    has_ultra = any(entry.get("ultra") for entry in getattr(game, "history_entries", []))
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    return has_ultra or terminal_found


def _build_history_filter_buttons(game: Any) -> dict[str, Button]:
    buttons: dict[str, Button] = {}
    labels_values = [("All", None)] + [(f"{n}x{n}", n) for n in con.DIFFICULTIES]
    
    btn_w, gap = 90, 25
    total_w = len(labels_values) * btn_w + (len(labels_values) - 1) * gap
    start_x = con.WIDTH // 2 - total_w // 2

    for i, (_label, val) in enumerate(labels_values):
        key = "size_all" if val is None else f"size_{val}"
        label = lang.t("all", "All") if val is None else f"{val}x{val}"
        buttons[key] = Button(key, pg.Rect(start_x + i * (btn_w + gap), 95, btn_w, 36), label, kind="toggle_history")

    if _history_has_ultra_entries(game):
        buttons["top10"] = Button("top10", pg.Rect(con.WIDTH // 2 - 230, 140, 220, 36), "Top 10", kind="toggle_history")
        buttons["ultra"] = Button("ultra", pg.Rect(con.WIDTH // 2 + 10, 140, 220, 36), "Ultra", kind="toggle_history")
    else:
        buttons["top10"] = Button("top10", pg.Rect(con.WIDTH // 2 - 110, 140, 220, 36), "Top 10", kind="toggle_history")

    return buttons


def _build_delete_confirm_buttons(game: Any) -> dict[str, Button]:
    box_w, box_h = 440, 220
    box_x = (con.WIDTH - box_w) // 2
    box_y = (con.HEIGHT - box_h) // 2

    return {
        "yes": Button("yes", pg.Rect(box_x + 60, box_y + 150, 130, 42), lang.t("delete", "Delete")),
        "no": Button("no", pg.Rect(box_x + 250, box_y + 150, 130, 42), lang.t("cancel", "Cancel")),
    }


def _build_achievements_nav_buttons(game: Any) -> dict[str, Button]:
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back")),
        "prev_page": Button("prev_page", ACH_PREV_RECT, kind="nav_arrow_left"),
        "next_page": Button("next_page", ACH_NEXT_RECT, kind="nav_arrow_right"),
    }


def _build_achievements_games_nav_buttons(game: Any) -> dict[str, Button]:
    return {
        "games_prev": Button("games_prev", ACH_GAMES_PREV_RECT, "<", color=con.SKYBLUE),
        "games_next": Button("games_next", ACH_GAMES_NEXT_RECT, ">", color=con.SKYBLUE),
    }


def _build_history_detail_buttons(game: Any) -> dict[str, Button]:
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back")),
        "export_mp4": Button("export_mp4", helpers.DETAIL_EXPORT_BUTTON, lang.t("export", "Export as MP4")),
        "export_quality": Button("export_quality", helpers.DETAIL_QUALITY_BUTTON),
        "export_fps": Button("export_fps", helpers.DETAIL_FPS_BUTTON),
        "detail_reset": Button("detail_reset", helpers.DETAIL_RESET_BUTTON, lang.t("show_end", "Show End")),
    }


def _build_tutorial_buttons(game: Any) -> dict[str, Button]:
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back")),
    }


def _build_export_exists_buttons(game: Any) -> dict[str, Button]:
    box_w, box_h = 470, 250
    box_x = (con.WIDTH - box_w) // 2
    box_y = (con.HEIGHT - box_h) // 2

    return {
        "yes": Button("yes", pg.Rect(box_x + 55, box_y + 190, 160, 42), lang.t("export_again", "Export again")),
        "no": Button("no", pg.Rect(box_x + 255, box_y + 190, 160, 42), lang.t("cancel", "Cancel")),
    }


def _build_stats_header_buttons(game: Any) -> dict[str, Button]:
    y = 116  # The header row of the graphical stats table
    return {
        "size": Button("size", pg.Rect(80, y, 75, 26), lang.t("size", "Size"), color=con.BG_COLOR, color_hover=con.WHITE),
        "mode": Button("mode", pg.Rect(155, y, 75, 26), lang.t("mode", "Mode"), color=con.BG_COLOR, color_hover=con.WHITE),
        "games": Button("games", pg.Rect(292, y, 75, 26), lang.t("games", "Games"), color=con.BG_COLOR, color_hover=con.WHITE),
        "best": Button("best", pg.Rect(405, y, 75, 26), lang.t("best", "Best"), color=con.BG_COLOR, color_hover=con.WHITE),
        "average": Button("average", pg.Rect(600, y, 75, 26), lang.t("average", "Average"), color=con.BG_COLOR, color_hover=con.WHITE),
    }


def _back_only_buttons(label_key: str, label_default: str) -> ButtonSet:
    """Return a ButtonSet containing only a 'back' button."""
    return ButtonSet(
        lambda _game: {"back": Button("back", helpers.BTN_BACK, lang.t(label_key, label_default))}
    )


# --- Build Call Section (Instantiating ButtonSets) ---

menu_buttons = ButtonSet(_build_menu_buttons)
settings_buttons = ButtonSet(_build_settings_buttons, _settings_signature)
advanced_settings_buttons = ButtonSet(_build_advanced_settings_buttons, _advanced_settings_signature)
play_buttons = ButtonSet(_build_play_buttons)
resume_choice_buttons = ButtonSet(_build_resume_choice_buttons)
hannah_buttons = ButtonSet(_build_hannah_buttons)
hannah_play_buttons = ButtonSet(_build_hannah_play_buttons)
tutorial_buttons = ButtonSet(_build_tutorial_buttons, signature=lambda _game: (lang.current_language(),))
history_filter_buttons = ButtonSet(
    _build_history_filter_buttons,
    signature=lambda game: (lang.current_language(), _history_has_ultra_entries(game)),
)
export_exists_buttons = ButtonSet(_build_export_exists_buttons)
stats_header_buttons = ButtonSet(_build_stats_header_buttons, signature=lambda _game: lang.current_language())
delete_confirm_buttons = ButtonSet(_build_delete_confirm_buttons)
achievements_nav_buttons = ButtonSet(_build_achievements_nav_buttons)
achievements_games_nav_buttons = ButtonSet(_build_achievements_games_nav_buttons)
history_detail_buttons = ButtonSet(_build_history_detail_buttons)

about_buttons = _back_only_buttons("back", "Back")
stats_buttons = _back_only_buttons("back", "Back")
history_detail_button = _back_only_buttons("back", "Back")
history_back_button = _back_only_buttons("back", "Back")