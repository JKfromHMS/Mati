### Mati (Mathematics and tactic intelligence) ###
### V0.0.8 Beta V1.0.8 ###
### Author: Janosch Klawatsch, 08.07.2026 ###
### widgets file V0.0.0 ###

### Structure-Plan ###
# - config.py - Constants #
# - level.py - Generate Levels, Check Wins ... #
# - persistence.py - Save and load of .mati files #
# - widgets.py - Draw-Functions #
# - game.py - The main game handling #
# - screens.py - Building the screens #
# - main.py - Entry point and main loop #

### -Imports- ###
### External ###
import pygame # Something like the engine on which the game runs.

### Own ###
import config # To have the constants

### -Functions- ###
### Initialize ###
def init(screen, title_font, font, small_font): # Get the defined fonts
    global _screen, _title_font, _font, _small_font # Make the fonts be seen in the whole file
    _screen = screen         # Define got screen as screen to deal with
    _title_font = title_font # Define got title font as real title font
    _font = font             # Define got font als real font
    _small_font = small_font # Define got small font as real small font
    
### Give screen ###
def get_screen(): # Give the screen information to others files
    return _screen # Screens infos are send as a return

### Allover text handling ###
def _blit(text, font, color, x, y, center=True): # Get the information about the text and where it should be
    obj = font.render(text, True, color) # Work with the font element to make it understandable and connect it with the text and the color
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

### For a button ###
def draw_button(rect, text, is_hovered, enabled=True): # Get the information about the button
    if not enabled: # If explicit said the button is disabled
        color = config.BUTTON_DISABLED # Set button color to the right one
    else: 
        color = config.BUTTON_HOVER if is_hovered else config.BUTTON_COLOR # If the Button is hovered or normal right color
    pygame.draw.rect(_screen, color, rect, border_radius=8) # Send the command to draw the rect
    _blit(text, _small_font, config.WHITE, rect.centerx, rect.centery) # Let the text draw centered on the button
    
### For the total grid border ###
def draw_outer_border(offset_x, offset_y, n, cell_size): # Get the information about the size and position of the grid it should border
    total_size = (n + 1) * cell_size # Size of one cell streched to the size of the whole grid
    border_rect = pygame.Rect(offset_x, offset_y, total_size, total_size) # The rect information about the border
    pygame.draw.rect(_screen, config.BLACK, border_rect, 2)
    
### For the indicators if a sum is reached ###
def draw_fulfilled_indicators(grid, user_sel, row_sums, col_sums, n, offset_x, offset_y, cell_size): # Get the information about the grid and what the user did
    radius = cell_size // 2 - 4 # The circles should fit in the cells
    for r in range(n): # Check the rows
        s = sum(grid[r][c] for c in range(n) if user_sel[r][c]) # Sum up every clicked cell in a row
        if s == row_sums[r]: # If the sum is the expected
            cx = offset_x + cell_size // 2 # The x center of the sum cells
            cy = offset_y + (r + 1) * cell_size + cell_size // 2 # The y center of the sum cells
            pygame.draw.circle(_screen, config.GREEN, (cx, cy,), radius, 2) # Send draw commands for the circle
    for c in range(n): # Check the columns
        s = sum(grid[r][c] for r in range(n) if user_sel[r][c]) # Sum up every clicked cell in a column 
        if s == col_sums[c]: # If the sum is the expected
            cx = offset_x + (c + 1) * cell_size + cell_size // 2 # The x center of the sum cells
            cy = offset_y + cell_size // 2 # The y center of the sum cells
            pygame.draw.circle(_screen, config.GREEN, (cx, cy), radius, 2) # Send draw command for the circle
            
### For the cross highlighting ###
def draw_hover_cross(offset_x, offset_y, n, cell_size, hover_r, hover_c): # Get information about the grid and the main hovered cell
    if hover_r is None or hover_c is None: # Nothing to do
        return # do nothing
    row_rect = pygame.Rect(offset_x + cell_size, offset_y + (hover_r + 1) * cell_size, n * cell_size, cell_size) # Get the complete plan of the row
    col_rect = pygame.Rect(offset_x + (hover_c + 1) * cell_size, offset_y + cell_size, cell_size, n * cell_size) # Get the complete plan of the column
    pygame.draw.rect(_screen, config.HOVER_LINE_COLOR, row_rect) # Mark the whole row
    pygame.draw.rect(_screen, config.HOVER_LINE_COLOR, col_rect) # And the whole column