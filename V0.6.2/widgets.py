### Mati (Mathematics and tactic intelligence) ###
### V0.6.2 (Beta V1.0.23) ###
### Author: Janosch Klawatsch, 2026-08-30 ###
### widgets file V0.6.2 ###

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
import functools # Efficency reasons
from datetime import datetime as dt # for the live clock

### Own ###
import config as con # To have the constants

### -Functions- ###
### Initialize ###
def init(screen, title_font, font, small_font, tiny_font): # Get the defined fonts
    global _screen, _title_font, _font, _small_font, _tiny_font # Make the fonts be seen in the whole file
    _screen = screen         # Define got screen as screen to deal with
    _title_font = title_font # Define got title font as real title font
    _font = font             # Define got font als real font
    _small_font = small_font # Define got small font as real small font
    _tiny_font = tiny_font   # Define got tiny font as real tiny font
    
    
### Give screen ###
def get_screen(): # Give the screen information to others files
    return _screen # Screens infos are send as a return

def get_fonts(): # Give the fonts to others files, so they draw with the exact same look
    return _title_font, _font, _small_font, _tiny_font # title, normal, small, tiny

_real_screen = None

def set_real_screen(real_screen):
    global _real_screen
    _real_screen = real_screen
    
def compute_scale(real_w, real_h):
    scale = min(real_w / con.WIDTH, real_h / con.HEIGHT)
    scale = max(scale, 0.01)
    scaled_w, scaled_h = int(con.WIDTH * scale), int(con.HEIGHT * scale)
    offset_x = (real_w - scaled_w) // 2
    offset_y = (real_h - scaled_h) // 2
    return scale, scaled_w, scaled_h, offset_x, offset_y

def present(real_screen=None):
    target = real_screen if real_screen else _real_screen
    if target is None or _screen is None:
        return
    real_w, real_h = target.get_size()
    scale, scaled_w, scaled_h, offset_x, offset_y = compute_scale(real_w, real_h)
    scaled_surface = pg.transform.smoothscale(_screen, (scaled_w, scaled_h))
    target.blit(scaled_surface, (offset_x, offset_y))
    pg.display.flip()
    

@functools.lru_cache(maxsize=256)
def _render_text_cached(font, text, color): # Save object that stayed
    return font.render(text, True, color) # Let them stay exsisting

### All over text handling ###
def _blit(text, font, color, x, y, center=True): # Get the information about the text and where it should be
    color_tuple = tuple(color) if isinstance(color, (list, pg.Color)) else color
    obj = _render_text_cached(font, text, color_tuple) # Work with the font element to make it understandable and connect it with the text and the color
    
    rect = obj.get_rect() # Work the text information further to a drawable object
    if center: # If a object should be in the center or if it wasn't said if it should
        rect.center = (x, y)  # Set the given cords as the center
    else: 
        rect.topleft = (x, y) # Set the given cords as the left top
    _screen.blit(obj, rect)   # Showable on the screen
    
    
### For a title text ###
def draw_title(text, color, x, y, center=True): # Get the information about the title
    _blit(text, _title_font, color, x, y, center) # Give the information with all needed details to the blit thing
    
    
### For a normal text ###
def draw_text(text, color, x, y, center=True): # Get the information about the text
    _blit(text, _font, color, x, y, center) # Give the information with all needed details to the blit thing
    
    
### For a small text ###
def draw_small(text, color, x, y, center=True): # Get the information about the text
    _blit(text, _small_font, color, x, y, center) # Give the information with all needed details to the blit thing


### For a tiny text ###
def draw_tiny(text, color, x, y, center=True): # Get the information for a tiny text
    _blit(text, _tiny_font, color, x, y, center) # Give the information with the right font


### For a button ###
def draw_button(rect, text, is_hovered, enabled=True, focused=False, color=None, color_hover=None, color_unenabled=None): # Get the information about the button
    if not enabled: # If explicit said the button is disabled
        colore = color_unenabled or con.BUTTON_DISABLED # Set button color to the right one
    else: 
        colore = (color_hover or con.BUTTON_HOVER) if is_hovered else (color or con.BUTTON_COLOR) # If the Button is hovered or normal right color
    pg.draw.rect(_screen, colore, rect, border_radius=8) # Send the command to draw the rect
    if focused: # If the button has the keyboard focus
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius = 8) # Draw a bright border
    _blit(text, _small_font, con.WHITE, rect.centerx, rect.centery) # Let the text draw centered on the button
    

### For the wide open chevron of the graphical achievements screen
def _chevron_points(rect, direction):
    box = min(rect.width, rect.height) # scale relativ to the smaller side to stay it in limits
    half_w = int(box * 0.32) # how far the tip reaches out
    half_h = int(box * 0.92) # how far the corners spread apart
    cx, cy = rect.center
    if direction == "right":
        tip = (cx + half_w, cy)
        return [(cx - half_w, cy - half_h), tip, (cx - half_w, cy + half_h)]
    tip = (cx - half_w, cy)
    return [(cx + half_w, cy - half_h), tip, (cx + half_w, cy + half_h)]


def draw_nav_arrow(rect, direction, is_hovered, enabled=True, focused=False):
    if not enabled:
        color = con.BUTTON_DISABLED
    else:
        color = con.BUTTON_GREY_HOVER if is_hovered else con.BUTTON_GREY_COLOR
    pg.draw.rect(_screen, color, rect, border_radius=8)
    pg.draw.rect(_screen, con.BUTTON_GREY_BORDER, rect, 2, border_radius=8)
    if focused:
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius=8)
    thickness = max(3, min(rect.width, rect.height) // 8)
    pg.draw.lines(_screen, con.TURQUIS, False, _chevron_points(rect, direction), thickness)


def draw_toggle_button(rect, text, is_hovered, active, focused=False): # Color changed button
    if active: # If it should be in the other color
        color = con.TOGGLE_ON_HOVER if is_hovered else con.TOGGLE_ON_COLOR # Set the active color and hover variant
    else:
        color = con.TOGGLE_OFF_HOVER if is_hovered else con.TOGGLE_OFF_COLOR # Use explicit off state and hover variant
    pg.draw.rect(_screen, color, rect, border_radius=8) # Draw the button
    if focused: # If the button has the keyboard focus
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius = 8) # Draw a bright border
    _blit(text, _small_font, con.WHITE, rect.centerx, rect.centery, True) # Draw the text in the button
    
    
def draw_toggle_history_button(rect, text, is_hovered, active, focused=False): # Color changed button
    if active: # If it should be in the other color
        color = con.GREEN # Set the active color and hover variant
    else:
        color = con.BUTTON_HOVER if is_hovered else con.BUTTON_COLOR # Use explicit off state and hover variant
    pg.draw.rect(_screen, color, rect, border_radius=8) # Draw the button
    if focused: # If the button has the keyboard focus
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius = 8) # Draw a bright border
    _blit(text, _small_font, con.WHITE, rect.centerx, rect.centery, True) # Draw the text in the button
    
    
### For a panel row ###
def draw_panel_row(rect, is_hovered, highlighted=False, focused=False): # Background for multiple multi buttons
    if highlighted: # If it is highlighted
        color = con.GOLD # Set the color
    else:
        color = con.BUTTON_HOVER if is_hovered else con.BUTTON_COLOR # Defines the color
    pg.draw.rect(_screen, color, rect, border_radius=6) # Draw the Background thing
    if focused: # If the button has the keyboard focus
        pg.draw.rect(_screen, con.FOCUS_COLOR, rect, 3, border_radius = 6) # Draw a bright border
    
    
def draw_achievements_tile(rect):
    pg.draw.rect(_screen, con.SKYBLUE, rect, border_radius=16)
    
    
### For the total grid border ###
def draw_outer_border(offset_x, offset_y, n, cell_size, ultra=False): # Get the information about the size and position of the grid it should border
    total_size = (n + 1) * cell_size # Size of one cell streched to the size of the whole grid
    color = con.SHINE if ultra else con.BLACK # Defines the color
    pg.draw.rect(_screen, color, (offset_x, offset_y, total_size, total_size), 2) # The border
    
    
### For the indicators if a sum is reached ###
def draw_fulfilled_indicators(grid, user_sel, row_sums, col_sums, n, offset_x, offset_y, cell_size): # Get the information about the grid and what the user did
    # It is unusual to calculate something in a draw function, but is the only place needed
    radius = cell_size // 2 - 4 # The circles should fit in the cells
    half_cell = cell_size // 2 # The half cell
    
    for r in range(n): # Check the rows
        s = sum(grid[r][c] for c in range(n) if user_sel[r][c]) # Sum up every clicked cell in a row
        if s == row_sums[r]: # If the sum is the expected
            cx = offset_x + half_cell # The x center of the sum cells
            cy = offset_y + (r + 1) * cell_size + half_cell # The y center of the sum cells
            pg.draw.circle(_screen, con.GREEN, (cx, cy,), radius, 2) # Send draw commands for the circle
    
    for c in range(n): # Check the columns
        s = sum(grid[r][c] for r in range(n) if user_sel[r][c]) # Sum up every clicked cell in a column 
        if s == col_sums[c]: # If the sum is the expected
            cx = offset_x + (c + 1) * cell_size + half_cell # The x center of the sum cells
            cy = offset_y + half_cell # The y center of the sum cells
            pg.draw.circle(_screen, con.GREEN, (cx, cy), radius, 2) # Send draw command for the circle
     

### For the cross highlighting ###
def draw_hover_cross(offset_x, offset_y, n, cell_size, hover_r, hover_c): # Get information about the grid and the main hovered cell
    if hover_r is None or hover_c is None: # Nothing to do
        return # do nothing
    
    grid_size = n * cell_size
    pg.draw.rect(_screen, con.HOVER_LINE_COLOR, (offset_x + cell_size, offset_y + (hover_r + 1) * cell_size, grid_size, cell_size)) # Mark the whole row
    pg.draw.rect(_screen, con.HOVER_LINE_COLOR, (offset_x + (hover_c + 1) * cell_size, offset_y + cell_size, cell_size, grid_size)) # And the whole column
    
    
### for the scrollbars ###
def scrollbar_handle_rect(track_rect, content_length, visible_length, scroll_offset, vertical = True):
    track_len = track_rect.height if vertical else track_rect.width
    handle_len = max(con.SCROLLBAR_MIN_LENGTH, int(track_len * (visible_length / max(1, content_length))))
    max_scroll = max(1, content_length - visible_length)
    progress = min(1, max(0, scroll_offset / max_scroll))
    handle_pos = int((track_len - handle_len) * progress)
    if vertical:
        return pg.Rect(track_rect.x, track_rect.y + handle_pos, track_rect.width, handle_len)
    return pg.Rect(track_rect.x + handle_pos, track_rect.y, handle_len, track_rect.height)


def scrollbar_offset_for_handle_pos(track_rect, content_length, visible_Length, mouse_pos, grab_offset, vertical = True):
    track_len = track_rect.height if vertical else track_rect.width
    handle_len = max(con.SCROLLBAR_MIN_LENGTH, int(track_len * (visible_Length / max(1, content_length))))
    mouse_along_track = (mouse_pos[1] - track_rect.y) if vertical else (mouse_pos[0] - track_rect.x)
    handle_pos = mouse_along_track - grab_offset
    handle_pos = max(0, min(handle_pos, track_len - handle_len))
    max_scroll = max(1, content_length - visible_Length)
    progress = handle_pos / max(1, track_len - handle_len)
    return progress * max_scroll


def draw_scrollbar(track_rect, content_length, visibel_length, scroll_offset, mx, my, last_scroll_time, vertical = True): # draws a draw_scrollbar
    if content_length <= visibel_length: # nothing to scroll
        return # do nothing
    now = pg.time.get_ticks() # the time now
    handle_rect = scrollbar_handle_rect(track_rect, content_length, visibel_length, scroll_offset, vertical)
    border_rect = track_rect.inflate(4, 4)
    #track_len = track_rect.height if vertical else track_rect.width # len and direction
    #handle_len = max(con.SCROLLBAR_MIN_LENGTH, int(track_len * (visibel_length / content_length))) # handle the lenght
    #max_scroll = max(1, content_length - visibel_length) 
    #progress = min(1, max(0, scroll_offset / max_scroll)) # how far scrolled
    #handle_pos = int((track_len - handle_len) * progress) # where the handle should be
    #if vertical: # vertical bars
    #    handle_rect = pg.Rect(track_rect.x, track_rect.y + handle_pos, track_rect.width, handle_len) # the handle itself
    #else: # horizontal bars, at the bottom
    #    handle_rect = pg.Rect(track_rect.x + handle_pos, track_rect.y, handle_len, track_rect.height) # the handle itself
        
    is_hovered = handle_rect.collidepoint(mx, my) or track_rect.collidepoint(mx, my) # is the mouse on the bar
    is_moving = (now - last_scroll_time) < con.SCROLLBAR_VISIBLE_MS # was it moved lately
    if not is_hovered and not is_moving: # invisible bar
        return # nothing to do
    
    alpha = con.SCROLLBAR_MAX_ALPHA if is_hovered else con.SCROLLBAR_MOVE_ALPHA # how transperent it is
    border_surface = pg.Surface((border_rect.width, border_rect.height), pg.SRCALPHA)
    pg.draw.rect(border_surface, (*con.SCROLLBAR_COLOR, max(25, alpha // 3)), border_surface.get_rect(), border_radius=max(6, con.SCROLLBAR_WIDTH + 2))
    pg.draw.rect(border_surface, (*con.SCROLLBAR_COLOR, alpha), border_surface.get_rect(), 1, border_radius=max(6, con.SCROLLBAR_WIDTH + 2))
    _screen.blit(border_surface, border_rect.topleft)

    surf = pg.Surface((handle_rect.width, handle_rect.height), pg.SRCALPHA) # the transparent surface
    pg.draw.rect(surf, (*con.SCROLLBAR_COLOR, alpha), surf.get_rect(), border_radius=con.SCROLLBAR_WIDTH // 2) # draw it
    _screen.blit(surf, handle_rect.topleft) # place it on the screen
   
   
### for sliders ###
def slider_handle_rect(track_rect, value):
    value = max(0.0, min(1.0, value))
    cx = track_rect.x + int(track_rect.width * value)
    radius = track_rect.height
    return pg.Rect(cx - radius // 2, track_rect.centery - radius // 2, radius, radius)


def value_for_slider_x(track_rect, mouse_x):
    if track_rect.width <= 0:
        return 0.0
    progress = (mouse_x - track_rect.x) / track_rect.width
    return max(0.0, min(1.0, progress))


def draw_slider(track_rect, value, is_hovered, label=None, focus_mode=None):
    pg.draw.rect(_screen, con.GRID_COLOR, track_rect, border_radius=track_rect.height // 2)
    filled = pg.Rect(track_rect.x, track_rect.y, int(track_rect.width * max(0.0, min(1.0, value))), track_rect.height)
    pg.draw.rect(_screen, con.BUTTON_HOVER if is_hovered else con.BUTTON_COLOR, filled, border_radius=track_rect.height // 2)
    
    if focus_mode == "region":
        outline_rect = track_rect.inflate(6, 6)
        pg.draw.rect(_screen, con.FOCUS_COLOR, outline_rect, 3, border_radius=outline_rect.height // 2)
    
    handle = slider_handle_rect(track_rect, value)
    pg.draw.circle(_screen, con.WHITE, handle.center, handle.width // 2)
    pg.draw.circle(_screen, con.BLACK, handle.center, handle.width // 2, 1)
    if focus_mode == "dot":
        pg.draw.circle(_screen, con.FOCUS_COLOR, handle.center, handle.width // 2 + 3, 3)
    
    if label:
        draw_small(f"{label}: {int(round(value * 100))}%", con.TEXT_COLOR, track_rect.centerx, track_rect.y - 14, center=True)
        
    
### for the realtime clock ###
def draw_live_clock(game): # draw the clock
    if not getattr(game, "live_clock_enabled", False): # only if wanted
        return # he do not want it
    now = dt.now() # get the time
    if getattr(game, "live_clock_ms", False): # With ms
        text = now.strftime("%H:%M:%S") + f".{now.microsecond // 1000 :03}" # with ms
    else:
        text = now.strftime("%H:%M:%S") # without ms
    draw_small(text, con.TEXT_COLOR, con.WIDTH - 55, 26, center=True) # draw it