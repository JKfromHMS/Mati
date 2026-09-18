### Mati (Mathematics and tactic intelligence) ###
### V0.6.3 (Beta V1.0.24) ###
### Author: Janosch Klawatsch, 2026-09-01 ###
### buttons file V0.6.1 ###

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
import pygame as pg

### Own ###
import config as con
import helpers
import lang
import widgets as w


### -The Button class- ###
class Button:
    """A single clickable/hoverable/focusable UI element.
    
    Attributes:
        key (str): Identifier used for keyboard focus and click routing.
        rect (pg.Rect): The button's position and size.
        label (str): Text drawn on the button. Unused by kinds that draw
            no text of their own (e.g. 'tile').
        kind (str): Which widgets.py drawing style to use. One of:
            'button' (default, widgets.draw_button),
            'toggle' (widgets.draw_toggle_button),
            'panel' (widgets.draw_panel_row),
            'nav_arrow_left'/'nav_arrow_right' (widgets.draw_nav_arrow),
            'tile' (widgets.draw_achievements_tile, colored box),
        enabled (bool): Whether the button can be hovered/clicked/drawn as
            active. Disabled buttons still draw (greyed out), just never
            report a hover or a click.
        active (bool): Toggle/highlight state for 'toggle', 'toggle_history'
            and 'panel' kinds (on/off, or "this is the highlighted row").
        color / color_hover / color_disabled: Optional color overrides,
            passed through to widgets.draw_button for the 'button' kind.
    """
    
    __slots__ = ("key", "rect", "label", "kind", "enabled", "active", "color", "color_hover", "color_disabled")
    
    def __init__(self, key, rect, label="", kind="button", enabled=True, active=False, color=None, color_hover=None, color_disabled=None):
        self.key = key
        self.rect = rect
        self.label = label
        self.kind = kind
        self.enabled = enabled
        self.active = active
        self.color = color
        self.color_hover = color_hover
        self.color_disabled = color_disabled
        
    def is_hovered(self, mx, my):
        return self.enabled and self.rect.collidepoint(mx, my)
    
    def is_clicked(self, mx, my):
        return self.rect.collidepoint(mx, my)
    
    def draw(self, mx, my, focus_key=None):
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
                
            case _: # 'button', the default
                w.draw_button(
                    self.rect, self.label, hovered, enabled=self.enabled, focused=focused,
                    color=self.color, color_hover=self.color_hover, color_unenabled=self.color_disabled,
                )
                
                
### -Caching a screen's buttons- ###
class ButtonSet:
    """Caches the Button objects for one screen, rebuilding them only when
    something that actually affects their layout changes.
    
    Args:
        build (Callable[[Game], Dict[str, Button]]): Builds the buttons
            for this screen from scratch.
        signature (Callable[[Game], Hashable], optional): Computes a cheap,
            hashable value from whatever part of the game/settings state
            this screen's layout depends on (e.g. the current language, or
            whether a particular section is expanded). Defaults to a 
            function that always return the current language, since 
            labels are localized on every screen - override it to add
            screen-specific triggers on top of that, not instead of it.
    """
    
    def __init__(self, build, signature=None):
        self._build = build
        self._signature_fn = signature or (lambda game: lang.current_language())
        self._signature = object() # a sentinel no real signature will ever equal, forcing the first build
        self._buttons = {}
        
    def get(self, game): # The current buttons, rebuilt first if the layout-relevant state has changed
        sig = self._signature_fn(game)
        if sig != self._signature:
            self._buttons = self._build(game)
            self._signature = sig
        return self._buttons
    
    def invalidate(self): # Force the next get() to rebuild regardless of the signature
        self._signature = object()
        
        
### -Helpers for working with a dict of Buttons- ###
def hit_text(buttons, mx, my): # The key of the first button under (mx, my), or None
    for key, button in buttons.items():
        if button.is_clicked(mx, my):
            return key
    return None


def as_rects(buttons): # A plain {key: pg.Rect} view - for compatibility with non converted older code snippets
    return {key: button.rect for key, button in buttons.items()}


### -Menu- ###
def _build_menu_buttons(game):
    buttons = {}
    y = 175
    
    for n in con.DIFFICULTIES:
        buttons[f"start_{n}"] = Button(f"start_{n}", pg.Rect(con.WIDTH // 2 - 110, y, 220, 44), lang.t(con.DIFFICULTY_NAMES[n], con.DIFFICULTY_NAMES[n]))
        y += 54
        
    buttons["settings"] = Button("settings", pg.Rect(con.WIDTH // 2 - 110, y + 15, 220, 44), lang.t("settings", "Settings"))
    buttons["history"] = Button("history", pg.Rect(con.WIDTH // 2 - 110, y + 69, 220, 44), lang.t("history", "History"))
    buttons["quit"] = Button("quit", pg.Rect(con.WIDTH // 2 - 110, y + 123, 220, 44), lang.t("quit", "Quit"))
    
    return buttons


### -Settings- ###
def _build_settings_buttons(game):
    rects, _headers = helpers.settings_layout(game)
    buttons = {}
    
    for key, rect in rects.items():
        kind = "toggle" if key.startswith("toggle") else "button"
        label = lang.t("menu", "Menu") if key == "back" else ""
        buttons[key] = Button(key, rect, label, kind=kind)
    
    return buttons

def _settings_signature(game):
    terminal_found = bool(getattr(game, "achievements", {}).get("terminal_found"))
    return (lang.current_language(), terminal_found, game.timer_enabled, game.ultra_timer_enabled)


### -Advanced settings- ###
ADV_GAME_VOLUME_RECT = pg.Rect(60, 160, 260, 10)
ADV_TERMINAL_VOLUME_RECT = pg.Rect(60, 215, 260, 10)

def _build_advanced_settings_buttons(game):
    buttons = {"back": Button("back", helpers.BTN_BACK, lang.t("back", "Back"))}
    
    buttons["toggle_terminal_sound"] = Button("toggle_terminal_sound", pg.Rect(60, 245, 220, 34), kind="toggle")
    buttons["language_dropdown"] = Button("language_dropdown", pg.Rect(60, 335, 220, 34))
    
    if getattr(game, "language_dropdown_open", False):
        for i, (label, _internal) in enumerate(helpers.available_languages()):
            key = f"language_option_{i}"
            buttons[key] = Button(key, pg.Rect(60, 340 + 34 * (i + 1), 220, 30), label, kind="toggle")
            
    for i in range(len(con.INPUT_ORDER_OPTIONS)):
        key = f"input_order_{i}"
        buttons[key] = Button(key, pg.Rect(420, 135 + i * 40, 300, 32), kind="toggle")
        
    for i, action in enumerate(con.DEFAULT_KEYBINDINGS):
        key = f"keybind_{action}"
        buttons[key] = Button(key, pg.Rect(600, 335 + i * 30, 160, 26))
        
    return buttons

def _advanced_settings_signature(game):
    open_ = getattr(game, "language_dropdown_open", False)
    return (lang.current_language(), open_, len(helpers.available_languages()) if open_ else 0)


### -Play- ###
def _build_play_buttons(game):
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
    
    
### -Resume choice- ###
def _build_resume_choice_buttons(game):
    return {
        "resume": Button("resume", pg.Rect(con.WIDTH // 2 - 240, 300, 210, 50), lang.t("resume", "Resume")),
        "new": Button("new", pg.Rect(con.WIDTH // 2 + 30, 300, 210, 50), lang.t("new_game", "New Game")),
        "cancel": Button("cancel", helpers.BTN_BACK, lang.t("back", "Back")),
    }
    
    
### -Hannah (easter egg)- ###
def _build_hannah_buttons(game):
    return {"back": Button("back", helpers.BTN_BACK, lang.t("menu", "Menu"))}

def _build_hannah_play_buttons(game):
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back")),
        "undo": Button("undo", pg.Rect(con.WIDTH - 150, 20, 130, 34), lang.t("undo", "Undo")),
    }
    
    
### -History filter- ###
def _history_has_ultra_entries(game):
    return any(entry.get("ultra") for entry in game.history_entries) or bool(getattr(game, "achievements", {}).get("terminal_found"))

def _build_history_filter_buttons(game):
    buttons = {}
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
        buttons["top10"] = Button("top10", pg.Rect(con.WIDTH // 2 - 110, 140, 220, 36), "Top 10", kind="toogle_history")
        
    return buttons


### -Delete-match confirmation- ###
def _build_delete_confirm_buttons(game):
    box_w, box_h = 440, 220
    box_x = (con.WIDTH - box_w) // 2
    box_y = (con.HEIGHT - box_h) // 2
    
    return {
        "yes": Button("yes", pg.Rect(box_x + 60, box_y + 150, 130, 42), lang.t("delete", "Delete")),
        "no": Button("no", pg.Rect(box_x + 250, box_y + 150, 130, 42), lang.t("cancel", "Cancel")),
    }
    
    
### -Achievements- ###
def _build_achievements_nav_buttons(game):
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back")),
        "prev_page": Button("prev_page", helpers.ACH_PREV_RECT, kind="nav_arrow_left"),
        "next_page": Button("neext_page", helpers.ACH_NEXT_RECT, kind="nav_arrow_right"),
    }
    
def _build_achievements_games_nav_buttons(game):
    return {
        "games_prev": Button("games_prev", helpers.ACH_GAMES_PREV_RECT, "<", color=con.SKYBLUE),
        "games_next": Button("games_next", helpers.ACH_GAMES_NEXT_RECT, ">", color=con.SKYBLUE),
    }
    
    
### -History detail- ###
def _build_history_detail_buttons(game):
    return {
        "back": Button("back", helpers.BTN_BACK, lang.t("back", "Back")),
        "export_mp4": Button("export_mp4", helpers.DETAIL_EXPORT_BUTTON, lang.t("export", "Export as MP4")),
        "export_quality": Button("export_quality", helpers.DETAIL_QUALITY_BUTTON),
        "export_fps": Button("export_fps", helpers.DETAIL_FPS_BUTTON),
        "detail_reset": Button("detail_reset", helpers.DETAIL_RESET_BUTTON, lang.t("show_end", "Show End")),
    }
    
    
### -Single "back" needed- ###
def _back_only_buttons(label_key, label_default):
    return ButtonSet(lambda game: {"back": Button("back", helpers.BTN_BACK, lang.t(label_key, label_default))})


### Build call section ###
menu_buttons = ButtonSet(_build_menu_buttons)

settings_buttons = ButtonSet(_build_settings_buttons, _settings_signature)

advanced_settings_buttons = ButtonSet(_build_advanced_settings_buttons, _advanced_settings_signature)

play_buttons = ButtonSet(_build_play_buttons)

resume_choice_buttons = ButtonSet(_build_resume_choice_buttons)

hannah_buttons = ButtonSet(_build_hannah_buttons)
hannah_play_buttons = ButtonSet(_build_hannah_play_buttons)

history_filter_buttons = ButtonSet(
    _build_history_filter_buttons,
    signature=lambda game: (lang.current_language(), _history_has_ultra_entries(game)),
)

delete_confirm_buttons = ButtonSet(_build_delete_confirm_buttons)

achievements_nav_buttons = ButtonSet(_build_achievements_nav_buttons)
achievements_games_nav_buttons = ButtonSet(_build_achievements_games_nav_buttons)

history_detail_buttons = ButtonSet(_build_history_detail_buttons)

about_buttons = _back_only_buttons("back", "Back")
stats_buttons = _back_only_buttons("back", "Back")
history_detail_button = _back_only_buttons("back", "Back")
history_back_button = _back_only_buttons("back", "Back")
