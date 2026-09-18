"""A small speech-bubble tutorial guiding a first-time player through their
first match and towards the hidden terminal easter egg.
"""

from typing import Any
import pygame as pg

import config as con
import lang
import widgets as w

PLAY_PHASE_MS: int = 7000
_BANNER_RECT: pg.Rect = pg.Rect(130, 14, 540, 88)


class Tutorial:
    """Drives the onboarding sequence: first match -> hidden terminal -> advanced settings.

    The sequence is a small state machine (``self.step``) that is advanced by
    ``update()`` (called once per frame, purely by observing ``game.state``
    and ``game.won``) and rendered on top of everything else by ``draw()``.
    It never blocks input; it is a non-modal hint layer only.
    """

    def __init__(self, completed: bool = False) -> None:
        self.active: bool = not completed
        self.step: str = "menu"  # menu -> play -> win -> menu_terminal -> terminal -> done
        self.step_started_at: int = pg.time.get_ticks()
        self._printed_terminal_id: int | None = None

    def _set_step(self, step: str) -> None:
        """Switch to ``step`` and remember when, for the timed sub-phases."""
        if step != self.step:
            self.step = step
            self.step_started_at = pg.time.get_ticks()

    def update(self, game: Any, active_terminal: Any) -> None:
        """Advance the tutorial from the current game/terminal state. Call once per frame."""
        if not self.active:
            return

        match self.step:
            case "menu":
                if game.state == "PLAY":
                    self._set_step("play")

            case "play":
                if game.won:
                    self._set_step("win")
                elif game.state == "MENU":
                    self._set_step("menu")

            case "win":
                if game.state == "MENU":
                    self._set_step("menu_terminal")

            case "menu_terminal":
                if game.state == "TERMINAL":
                    self._set_step("terminal")

            case "terminal":
                if active_terminal is not None and id(active_terminal) != self._printed_terminal_id:
                    active_terminal.print_lines([
                        "",
                        lang.t("tut_terminal_1", "You found the hidden terminal!"),
                        lang.t("tut_terminal_2", "Type 'help' to see all available commands."),
                        "And try advanced settings"
                    ])
                    self._printed_terminal_id = id(active_terminal)
                if game.state == "ADVANCED_SETTINGS":
                    self._set_step("done")

            case "done":
                if pg.time.get_ticks() - self.step_started_at > 5000:
                    self.active = False
                    game.mark_tutorial_complete()

    def draw(self, game: Any, active_terminal: Any) -> None:
        """Draw the current step's speech bubble on top of everything else, if any."""
        if not self.active:
            return
        title, lines = self._bubble_text()
        if title is None:
            return
        _draw_banner(title, lines)

    def _bubble_text(self) -> tuple[str | None, list[str]]:
        """Return the ``(title, [body lines])`` for the currently active step."""
        match self.step:
            case "menu":
                return (
                    lang.t("tut_menu_title", "Welcome to Mati!"),
                    [lang.t("tut_menu_body", 'Pick a grid size below to start your first puzzle. "Easy" (4x4) is a great place to begin.')],
                )

            case "play":
                elapsed = pg.time.get_ticks() - self.step_started_at
                if elapsed < PLAY_PHASE_MS:
                    return (
                        lang.t("tut_play_title", "How to play"),
                        [lang.t("tut_play_body", "Left-click a cell to select it, right-click to mark it out. Get every row and column to add up to its target number.")],
                    )
                return (
                    lang.t("tut_play2_title", "Keep going!"),
                    [lang.t("tut_play2_body", "Stuck? Click Hint for a free move, or Undo to take one back.")],
                )

            case "win":
                return (
                    lang.t("tut_win_title", "You solved it!"),
                    [lang.t("tut_win_body", "Nicely done. Mati has a secret, too - head back to the menu and see if you can find it.")],
                )

            case "menu_terminal":
                return (
                    lang.t("tut_terminal_hint_title", "Looking for the secret?"),
                    [lang.t("tut_terminal_hint_body", "Try pressing Ctrl+T while you're here in the menu.")],
                )

            case "done":
                return (
                    lang.t("tut_done_title", "Tutorial complete!"),
                    [lang.t("tut_done_body", "You're all set - explore the rest of Mati on your own. Have fun!")],
                )

        return None, []


def _wrap(text: str, font: pg.font.Font, max_width: int) -> list[str]:
    """Word-wrap ``text`` into lines no wider than ``max_width`` px in ``font``."""
    words = text.split(" ")
    lines: list[str] = []
    current: str = ""

    for word in words:
        trial = f"{current} {word}".strip()
        if current and font.size(trial)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = trial

    if current:
        lines.append(current)
    return lines


def _draw_banner(title: str, body_lines: list[str]) -> None:
    """Draw the shared rounded speech-bubble banner used by every tutorial step."""
    screen = w.get_screen()
    if screen is None:
        return

    _title_font, font, small_font, _tiny_font = w.get_fonts()
    if font is None or small_font is None:
        return

    pad_x, pad_y, tab_gap = 20, 14, 16
    inner_w = _BANNER_RECT.width - pad_x * 2 - tab_gap

    wrapped: list[str] = []
    for line in body_lines:
        wrapped.extend(_wrap(line, small_font, inner_w))

    title_h = font.get_height() + 6
    line_h = small_font.get_height() + 4
    content_h = pad_y * 2 + title_h + len(wrapped) * line_h
    box_h = max(_BANNER_RECT.height, content_h)
    rect = pg.Rect(_BANNER_RECT.x, _BANNER_RECT.y, _BANNER_RECT.width, box_h)

    # Soft drop shadow
    shadow = rect.move(3, 4)
    shadow_surf = pg.Surface((shadow.width, shadow.height), pg.SRCALPHA)
    pg.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=14)
    screen.blit(shadow_surf, shadow.topleft)

    pg.draw.rect(screen, con.BG_COLOR, rect, border_radius=14)
    pg.draw.rect(screen, con.BUTTON_COLOR, rect, width=2, border_radius=14)

    # Accent tab
    tab_rect = pg.Rect(rect.x + 10, rect.y + 12, 5, rect.height - 24)
    pg.draw.rect(screen, con.BUTTON_COLOR, tab_rect, border_radius=3)

    text_x = rect.x + pad_x + tab_gap
    y = rect.y + pad_y
    w.draw_text(title, con.BUTTON_COLOR, text_x, y, center=False)
    y += title_h
    for line in wrapped:
        w.draw_small(line, con.TEXT_COLOR, text_x, y, center=False)
        y += line_h