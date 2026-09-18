"""Low-level drawing helpers for text, buttons, sliders, and scrollbars."""

import functools
from datetime import datetime as dt
import pygame as pg

import config as con

Color = tuple[int, int, int]

_screen: pg.Surface | None = None
_real_screen: pg.Surface | None = None
_title_font: pg.font.Font | None = None
_font: pg.font.Font | None = None
_small_font: pg.font.Font | None = None
_tiny_font: pg.font.Font | None = None
_scale_mode: str = "auto"
_render_quality: int = 1
_bg_surface: pg.Surface | None = None
_bg_size: tuple[int, int] | None = None

_SS_FACTOR: int = 4


def init(screen, title_font, font, small_font, tiny_font) -> None:
    """Store the virtual screen and the four font sizes that all drawing uses."""
    global _screen, _title_font, _font, _small_font, _tiny_font
    _screen = screen
    _title_font = title_font
    _font = font
    _small_font = small_font
    _tiny_font = tiny_font


def get_screen() -> pg.Surface | None:
    """Return the virtual screen surface."""
    return _screen


def get_fonts() -> tuple[pg.font.Font | None, pg.font.Font | None, pg.font.Font | None, pg.font.Font | None]:
    """Return the ``(title, normal, small, tiny)`` fonts in one tuple."""
    return _title_font, _font, _small_font, _tiny_font


def set_real_screen(real_screen: pg.Surface) -> None:
    """Store the real (window) screen for scaling in ``present``."""
    global _real_screen
    _real_screen = real_screen


def set_scale_mode(mode: str | int) -> None:
    """Select the display scale mode (``auto`` or an integer factor like ``2``)."""
    global _scale_mode
    if str(mode) in con.SCALE_MODES:
        _scale_mode = str(mode)


def get_scale_mode() -> str:
    """Return the currently selected scale mode (``auto`` by default)."""
    return _scale_mode


def set_render_quality(quality: int) -> None:
    """Select the text supersampling factor (1, 2 or 4) and refresh the cache."""
    global _render_quality
    try:
        quality = max(1, min(4, int(quality)))
    except (TypeError, ValueError):
        quality = 1
    if quality != _render_quality:
        _render_quality = quality
        _render_text_cached.cache_clear()


def get_render_quality() -> int:
    """Return the currently selected text supersampling factor."""
    return _render_quality


def layout_for(real_w: int, real_h: int, mode: str | None = None):
    """Compute the 4:3 game layout for a window of ``real_w`` x ``real_h``."""
    if mode is None:
        mode = _scale_mode
    fit = max(min(real_w / con.WIDTH, real_h / con.HEIGHT), 0.01)

    if mode == "auto":
        scale = fit
        filter_name = "smooth"
    else:
        preset = int(mode)
        if fit >= preset - 0.001:
            scale = preset
            filter_name = "nearest"
        else:
            scale = fit
            filter_name = "smooth"

    scaled_w = max(1, int(con.WIDTH * scale))
    scaled_h = max(1, int(con.HEIGHT * scale))
    offset_x = (real_w - scaled_w) // 2
    offset_y = (real_h - scaled_h) // 2
    return scale, scaled_w, scaled_h, offset_x, offset_y, filter_name


def _build_background(real_w: int, real_h: int) -> pg.Surface:
    """Build a cached game-appropriate background filling the unused window area."""
    top = (24, 26, 44)
    bottom = (58, 66, 100)
    grad = pg.Surface((1, 256))
    for i in range(256):
        t = i / 255
        col = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        pg.draw.line(grad, col, (0, i), (0, i))
    surf = pg.transform.smoothscale(grad, (real_w, real_h))

    dot = (206, 212, 228)
    spacing = 18
    for y in range(spacing // 2, real_h, spacing):
        for x in range(spacing // 2, real_w, spacing):
            surf.set_at((x, y), dot)
    return surf


def _background(real_w: int, real_h: int) -> pg.Surface:
    """Return the cached background for the given window size, rebuilding on change."""
    global _bg_surface, _bg_size
    if _bg_surface is None or _bg_size != (real_w, real_h):
        _bg_surface = _build_background(real_w, real_h)
        _bg_size = (real_w, real_h)
    return _bg_surface


def present(real_screen: pg.Surface | None = None) -> None:
    """Scale the virtual 4:3 screen onto the real window over the cached background and flip."""
    target = real_screen if real_screen else _real_screen
    if target is None or _screen is None:
        return
    real_w, real_h = target.get_size()
    scale, scaled_w, scaled_h, offset_x, offset_y, filter_name = layout_for(real_w, real_h)
    
    if filter_name == "nearest":
        scaled_surface = pg.transform.scale(_screen, (scaled_w, scaled_h))
    else:
        scaled_surface = pg.transform.smoothscale(_screen, (scaled_w, scaled_h))
        
    target.blit(_background(real_w, real_h), (0, 0))
    target.blit(scaled_surface, (offset_x, offset_y))
    pg.display.flip()


@functools.lru_cache(maxsize=256)
def _render_text_cached(font: pg.font.Font, text: str, color: tuple[int, int, int]) -> pg.Surface:
    """Render ``text`` with ``font`` and ``color``, caching the result surface."""
    rendered = font.render(text, True, color)
    if _render_quality > 1:
        try:
            big = font.copy()
            try:
                base = font.get_point_size()
            except AttributeError:
                base = font.get_height()
            big.set_point_size(max(1, base * _render_quality))
            big_rendered = big.render(text, True, color)
            if big_rendered.get_width() > rendered.get_width():
                rendered = pg.transform.smoothscale(big_rendered, rendered.get_size())
        except Exception:
            pass
    return rendered


def _blit(text: str, font: pg.font.Font | None, color, x: int, y: int, center: bool = True) -> None:
    """Draw ``text`` with ``font`` in ``color`` centred or top-left at (x, y)."""
    if _screen is None or font is None:
        return
    color_tuple = tuple(color) if isinstance(color, (list, pg.Color)) else color
    obj = _render_text_cached(font, text, color_tuple)
    rect = obj.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    _screen.blit(obj, rect)


def draw_title(text: str, color, x: int, y: int, center: bool = True) -> None:
    """Draw ``text`` using the title font."""
    _blit(text, _title_font, color, x, y, center)


def draw_text(text: str, color, x: int, y: int, center: bool = True) -> None:
    """Draw ``text`` using the normal font."""
    _blit(text, _font, color, x, y, center)


def draw_small(text: str, color, x: int, y: int, center: bool = True) -> None:
    """Draw ``text`` using the small font."""
    _blit(text, _small_font, color, x, y, center)


def draw_tiny(text: str, color, x: int, y: int, center: bool = True) -> None:
    """Draw ``text`` using the tiny font."""
    _blit(text, _tiny_font, color, x, y, center)


@functools.lru_cache(maxsize=128)
def _aa_circle_surface(radius: int, color: tuple[int, int, int], width: int) -> pg.Surface:
    """Build a small, cached, anti-aliased circle image via supersampling."""
    radius = max(1, int(radius))
    size = radius * 2 * _SS_FACTOR
    big = pg.Surface((size, size), pg.SRCALPHA)
    big_radius = radius * _SS_FACTOR
    big_width = 0 if width <= 0 else max(1, width * _SS_FACTOR)
    pg.draw.circle(big, color, (big_radius, big_radius), big_radius, big_width)
    return pg.transform.smoothscale(big, (radius * 2, radius * 2))


def _draw_aa_circle(surface: pg.Surface, color, center: tuple[float, float], radius: float, width: int = 0) -> None:
    img = _aa_circle_surface(int(round(radius)), tuple(color), width)
    rect = img.get_rect(center=(int(round(center[0])), int(round(center[1]))))
    surface.blit(img, rect)


@functools.lru_cache(maxsize=64)
def _aa_chevron_surface(width: int, height: int, direction: str, color: tuple[int, int, int], thickness: int) -> pg.Surface:
    big = pg.Surface((width * _SS_FACTOR, height * _SS_FACTOR), pg.SRCALPHA)
    origin_rect = pg.Rect(0, 0, width, height)
    big_points = [(x * _SS_FACTOR, y * _SS_FACTOR) for x, y in _chevron_points(origin_rect, direction)]
    pg.draw.lines(big, color, False, big_points, max(1, thickness * _SS_FACTOR))
    return pg.transform.smoothscale(big, (width, height))


def _chevron_points(rect: pg.Rect, direction: str) -> list[tuple[int, int]]:
    """Return the three points forming a left/right chevron inside ``rect``."""
    box = min(rect.width, rect.height)
    half_w = int(box * 0.32)
    half_h = int(box * 0.92)
    cx, cy = rect.center
    if direction == "right":
        return [(cx - half_w, cy - half_h), (cx + half_w, cy), (cx - half_w, cy + half_h)]
    return [(cx + half_w, cy - half_h), (cx - half_w, cy), (cx + half_w, cy + half_h)]


def draw_button(
    rect: pg.Rect,
    text: str,
    is_hovered: bool,
    enabled: bool = True,
    focused: bool = False,
    color: tuple[int, int, int] | None = None,
    color_hover: tuple[int, int, int] | None = None,
    color_unenabled: tuple[int, int, int] | None = None,
    text_color: tuple[int, int, int] | None = None,
) -> None:
    """Draw a standard button with optional hover, disabled and focus states."""
    if not enabled:
        btn_color = color_unenabled or con.BUTTON_DISABLED
    else:
        btn_color = (color_hover or con.BUTTON_HOVER) if is_hovered else (color or con.BUTTON_COLOR)
        
    pg.draw.rect(_screen, btn_color, rect, border_radius=8)
    if focused:
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius=8)
    _blit(text, _small_font, text_color or con.WHITE, rect.centerx, rect.centery)


def draw_nav_arrow(rect: pg.Rect, direction: str, is_hovered: bool, enabled: bool = True, focused: bool = False) -> None:
    """Draw a left/right navigation chevron arrow."""
    color = con.BUTTON_DISABLED if not enabled else (con.BUTTON_GREY_HOVER if is_hovered else con.BUTTON_GREY_COLOR)
    pg.draw.rect(_screen, color, rect, border_radius=8)
    pg.draw.rect(_screen, con.BUTTON_GREY_BORDER, rect, 2, border_radius=8)
    if focused:
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius=8)
        
    thickness = max(3, min(rect.width, rect.height) // 8)
    chevron_img = _aa_chevron_surface(rect.width, rect.height, direction, tuple(con.TURQUIS), thickness)
    _screen.blit(chevron_img, rect.topleft)


def draw_toggle_button(rect: pg.Rect, text: str, is_hovered: bool, active: bool, focused: bool = False) -> None:
    """Draw a toggle button whose colour reflects its ``active`` state."""
    color = (con.TOGGLE_ON_HOVER if is_hovered else con.TOGGLE_ON_COLOR) if active else (con.TOGGLE_OFF_HOVER if is_hovered else con.TOGGLE_OFF_COLOR)
    pg.draw.rect(_screen, color, rect, border_radius=8)
    if focused:
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius=8)
    _blit(text, _small_font, con.WHITE, rect.centerx, rect.centery, True)


def draw_toggle_history_button(rect: pg.Rect, text: str, is_hovered: bool, active: bool, focused: bool = False) -> None:
    """Draw a history filter toggle button reflecting its ``active`` state."""
    color = con.GREEN if active else (con.BUTTON_HOVER if is_hovered else con.BUTTON_COLOR)
    pg.draw.rect(_screen, color, rect, border_radius=8)
    if focused:
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius=8)
    _blit(text, _small_font, con.WHITE, rect.centerx, rect.centery, True)


def draw_panel_row(rect: pg.Rect, is_hovered: bool, highlighted: bool = False, focused: bool = False) -> None:
    """Draw a background for one multi-selectable panel row."""
    color = con.GOLD if highlighted else (con.BUTTON_HOVER if is_hovered else con.BUTTON_COLOR)
    pg.draw.rect(_screen, color, rect, border_radius=6)
    if focused:
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius=6)


def draw_achievements_tile(rect: pg.Rect) -> None:
    """Draw the coloured tile used on the graphical achievements page."""
    pg.draw.rect(_screen, con.SKYBLUE, rect, border_radius=16)


def draw_outer_border(offset_x: int, offset_y: int, n: int, cell_size: int, ultra: bool = False) -> None:
    """Draw the border around the whole game grid."""
    total_size = (n + 1) * cell_size + 4
    color = con.SHINE if ultra else con.BLACK
    pg.draw.rect(_screen, color, (offset_x - 2, offset_y - 2, total_size, total_size), 2)


def draw_fulfilled_indicators(grid, user_sel, row_sums, col_sums, n: int, offset_x: int, offset_y: int, cell_size: int) -> None:
    """Draw a small circle next to every row/column whose sum is reached."""
    radius = cell_size // 2 - 4
    half_cell = cell_size // 2

    for r in range(n):
        if sum(grid[r][c] for c in range(n) if user_sel[r][c]) == row_sums[r]:
            cx = offset_x + half_cell
            cy = offset_y + (r + 1) * cell_size + half_cell
            _draw_aa_circle(_screen, con.GREEN, (cx, cy), radius, 2)

    for c in range(n):
        if sum(grid[r][c] for r in range(n) if user_sel[r][c]) == col_sums[c]:
            cx = offset_x + (c + 1) * cell_size + half_cell
            cy = offset_y + half_cell
            _draw_aa_circle(_screen, con.GREEN, (cx, cy), radius, 2)


def draw_hover_cross(offset_x: int, offset_y: int, n: int, cell_size: int, hover_r: int | None, hover_c: int | None) -> None:
    """Highlight the whole row and column of the hovered cell."""
    if hover_r is None or hover_c is None:
        return

    grid_size = n * cell_size
    pg.draw.rect(_screen, con.HOVER_LINE_COLOR, (offset_x + cell_size, offset_y + (hover_r + 1) * cell_size, grid_size, cell_size))
    pg.draw.rect(_screen, con.HOVER_LINE_COLOR, (offset_x + (hover_c + 1) * cell_size, offset_y + cell_size, cell_size, grid_size))


def scrollbar_handle_rect(track_rect: pg.Rect, content_length: int, visible_length: int, scroll_offset: int, vertical: bool = True) -> pg.Rect:
    """Return the rect of the scrollbar handle for the given scroll position."""
    track_len = track_rect.height if vertical else track_rect.width
    handle_len = max(con.SCROLLBAR_MIN_LENGTH, int(track_len * (visible_length / max(1, content_length))))
    max_scroll = max(1, content_length - visible_length)
    progress = min(1.0, max(0.0, scroll_offset / max_scroll))
    handle_pos = int((track_len - handle_len) * progress)

    if vertical:
        return pg.Rect(track_rect.x, track_rect.y + handle_pos, track_rect.width, handle_len)
    return pg.Rect(track_rect.x + handle_pos, track_rect.y, handle_len, track_rect.height)


def scrollbar_offset_for_handle_pos(
    track_rect: pg.Rect, content_length: int, visible_length: int, mouse_pos: tuple[int, int], grab_offset: int, vertical: bool = True
) -> float:
    """Convert a dragged handle position back to a scroll offset."""
    track_len = track_rect.height if vertical else track_rect.width
    handle_len = max(con.SCROLLBAR_MIN_LENGTH, int(track_len * (visible_length / max(1, content_length))))
    mouse_along_track = (mouse_pos[1] - track_rect.y) if vertical else (mouse_pos[0] - track_rect.x)
    
    handle_pos = max(0, min(mouse_along_track - grab_offset, track_len - handle_len))
    max_scroll = max(1, content_length - visible_length)
    progress = handle_pos / max(1, track_len - handle_len)
    return progress * max_scroll


def draw_scrollbar(
    track_rect: pg.Rect, content_length: int, visible_length: int, scroll_offset: int, mx: int, my: int, last_scroll_time: int, vertical: bool = True
) -> None:
    """Draw a scrollbar, hiding it once the mouse stops hovering or moving."""
    if content_length <= visible_length:
        return

    now = pg.time.get_ticks()
    handle_rect = scrollbar_handle_rect(track_rect, content_length, visible_length, scroll_offset, vertical)
    border_rect = track_rect.inflate(4, 4)

    is_hovered = handle_rect.collidepoint(mx, my) or track_rect.collidepoint(mx, my)
    is_moving = (now - last_scroll_time) < con.SCROLLBAR_VISIBLE_MS
    if not is_hovered and not is_moving:
        return

    alpha = con.SCROLLBAR_MAX_ALPHA if is_hovered else con.SCROLLBAR_MOVE_ALPHA
    border_surface = pg.Surface((border_rect.width, border_rect.height), pg.SRCALPHA)
    pg.draw.rect(border_surface, (*con.SCROLLBAR_COLOR, max(25, alpha // 3)), border_surface.get_rect(), border_radius=max(6, con.SCROLLBAR_WIDTH + 2))
    pg.draw.rect(border_surface, (*con.SCROLLBAR_COLOR, alpha), border_surface.get_rect(), 1, border_radius=max(6, con.SCROLLBAR_WIDTH + 2))
    _screen.blit(border_surface, border_rect.topleft)

    surf = pg.Surface((handle_rect.width, handle_rect.height), pg.SRCALPHA)
    pg.draw.rect(surf, (*con.SCROLLBAR_COLOR, alpha), surf.get_rect(), border_radius=con.SCROLLBAR_WIDTH // 2)
    _screen.blit(surf, handle_rect.topleft)


def slider_handle_rect(track_rect: pg.Rect, value: float) -> pg.Rect:
    """Return the circular handle rect for a slider at ``value`` in [0, 1]."""
    value = max(0.0, min(1.0, value))
    cx = track_rect.x + int(track_rect.width * value)
    radius = track_rect.height
    return pg.Rect(cx - radius // 2, track_rect.centery - radius // 2, radius, radius)


def value_for_slider_x(track_rect: pg.Rect, mouse_x: int) -> float:
    """Convert a mouse x position to a slider value in ``[0.0, 1.0]``."""
    if track_rect.width <= 0:
        return 0.0
    progress = (mouse_x - track_rect.x) / track_rect.width
    return max(0.0, min(1.0, progress))


def draw_slider(track_rect: pg.Rect, value: float, is_hovered: bool, label: str | None = None, focus_mode: str | None = None) -> None:
    """Draw a volume-style slider with an optional label and focus ring."""
    pg.draw.rect(_screen, con.GRID_COLOR, track_rect, border_radius=track_rect.height // 2)
    filled = pg.Rect(track_rect.x, track_rect.y, int(track_rect.width * max(0.0, min(1.0, value))), track_rect.height)
    pg.draw.rect(_screen, con.BUTTON_HOVER if is_hovered else con.BUTTON_COLOR, filled, border_radius=track_rect.height // 2)

    if focus_mode == "region":
        outline_rect = track_rect.inflate(6, 6)
        pg.draw.rect(_screen, con.FOCUS_COLOR, outline_rect, 3, border_radius=outline_rect.height // 2)

    handle = slider_handle_rect(track_rect, value)
    _draw_aa_circle(_screen, con.WHITE, handle.center, handle.width // 2)
    _draw_aa_circle(_screen, con.BLACK, handle.center, handle.width // 2, 1)
    if focus_mode == "dot":
        _draw_aa_circle(_screen, con.FOCUS_COLOR, handle.center, handle.width // 2 + 3, 3)

    if label:
        draw_small(f"{label}: {int(round(value * 100))}%", con.TEXT_COLOR, track_rect.centerx, track_rect.y - 14, center=True)


def draw_live_clock(game) -> None:
    """Draw the current time in the top-right corner if enabled."""
    if not getattr(game, "live_clock_enabled", False):
        return
    now = dt.now()
    if getattr(game, "live_clock_ms", False):
        text = now.strftime("%H:%M:%S") + f".{now.microsecond // 1000:03}"
    else:
        text = now.strftime("%H:%M:%S")
    draw_small(text, con.TEXT_COLOR, con.WIDTH - 55, 26, center=True)