### Mati (Mathematics and tactic intelligence) ###
### V0.0.5 Beta V1.0.5 ###
### Author: Janosch Klawatsch, 05.07.2026 ###

### --- Imports --- ###
import pygame # pygame is something like a game engine
import random # for random number generation
import sys    # for system funtions like exit

### --- Main Configuration & Colors --- ###
WIDTH, HEIGHT = 800, 600
BG_COLOR = (245, 245, 250)
TEXT_COLOR = (40, 40, 40)
TARGET_COLOR = (200, 60, 60)
GRID_COLOR = (200, 200, 200)
SELECTED_COLOR = (150, 220, 150)
HOVER_COLOR = (220, 220, 220)
BUTTON_COLOR = (100, 150, 220) # Add a button color
BUTTON_HOVER = (80, 130, 200) # Add a button hover color
GREEN = (50, 180, 50) # Add a green color
DIMMED_TEXT_COLOR = (180, 180, 180)  # Adde a color for dimmed numbers
CELL_SIZE = 60

### --- Pygame Initialization --- ###
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mati")
FONT = pygame.font.SysFont("arial", 28, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 24) # Add a small font shortcut

### --- Logic --- ###
### Level Generation ###
def generate_level(n):
    grid = [[random.randint(1, 9) for _ in range(n)] for _ in range(n)] # Generate all numbers in the grid
    # The number are now basically in a 2D array,
    # To get the row and column sums, we need to select some
    selected = [[False] * n for _ in range(n)] # Another 2D array
    # This array is simply a list of the state, either False, like created, or True
    # Know we need the sums
    row_sums = [0] * n # Every row has a sum of 0 in the moment
    col_sums = [0] * n # Every column has a sum of 0 in the moment as well
    
    # Now we need to actually select some numbers
    for r in range(n):
        num_to_select = random.randint(1, n) # The number of the relevant cells
        indices = random.sample(range(n), num_to_select) # Randomly get the defined number of cells
        for c in indices:
            selected[r][c] = True # Every choosen cell is marked
            row_sums[r] += grid[r][c] # Calculating the sum of the row
            
    # Now we need the colums as well
    for c in range(n):
        for r in range(n):
            if selected[r][c]: # Every marked cell
                col_sums[c] += grid[r][c] # Adding to the column sum
                
    if 0 in col_sums: # If a column is empty
        generate_level(n) # Regenerate the level
                
    return grid, row_sums, col_sums # Return the grid and the sums

### Win Check ###
def check_win(grid, user_sel, row_sums, col_sums, n): # Add a complete new function system
    # Check the rows
    for r in range(n):
        if sum(grid[r][c] for c in range(n) if user_sel[r][c]) != row_sums[r]:
            return False # If the sum in one row is not correct, game not over
    
    # Check the columns
    for c in range(n):
        if sum(grid[r][c] for r in range(n) if user_sel[r][c]) != col_sums[c]:
            return False # Also if not every column is correct, game not over
    
    return True # If the programm still runs, the player must have completed the game

### Drawing Functions ###
def draw_text(text, font, color, surface, x, y, center=True): # A function to draw text to the screen
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_button(rect, text, is_hovered): # A function to draw buttons to the screen
    color = BUTTON_HOVER if is_hovered else BUTTON_COLOR # If hovered, one color, if not the other
    pygame.draw.rect(SCREEN, color, rect, border_radius=8)
    draw_text(text, SMALL_FONT, (255,255,255), SCREEN, rect.centerx, rect.centery)
    
def draw_outer_border(surface, offset_x, offset_y, n, cell_size): # -New- A funtion to draw the border
    total_size = (n + 1) * cell_size
    border_rect = pygame.Rect(offset_x, offset_y, total_size, total_size)
    pygame.draw.rect(surface, (0, 0, 0), border_rect, 2)
    
def draw_fulfilled_indicators(surface, grid, user_sel, row_sums, col_sums, n, offset_x, offset_y, cell_size): # -New- A function to draw circles around the correct numbers
    radius = cell_size // 2 - 4 
    # For the rows
    for r in range(n):
        sum_u_row = 0
        for c in range(n):
            if user_sel[r][c] == True:
                sum_u_row += grid[r][c]
                
        # If the clicked sum and the expected are equal, circle
        if sum_u_row == row_sums[r]:
            cx = offset_x + cell_size // 2
            cy = offset_y + (r+1) * cell_size + cell_size // 2
            pygame.draw.circle(surface, GREEN, (cx, cy), radius, 2)
            
    # For the columns
    for c in range(n):
        sum_u_col = 0
        for r in range(n):
            if user_sel[r][c] == True:
                sum_u_col += grid[r][c]
        
        # If the clicked sum and the expected are equal, circle
        if sum_u_col == col_sums[c]:
            cx = offset_x + (c+1) * cell_size + cell_size // 2
            cy = offset_y + cell_size // 2
            pygame.draw.circle(surface, GREEN, (cx, cy), radius, 2)
    
### --- Main Loop --- ###
def main():
    state = "MENU" # Add a state system to handle different screens
    n = 5
    grid, row_sums, col_sums, user_sel, user_dimmed = [], [], [], [], [] # Create the variables
    won = False
    
    # Add buttons for the screens
    btn_start_4 = pygame.Rect(WIDTH//2 - 100, 200, 200, 50) # Different Buttons for different Sizes
    btn_start_5 = pygame.Rect(WIDTH//2 - 100, 260, 200, 50) # Different Buttons for different Sizes
    btn_start_6 = pygame.Rect(WIDTH//2 - 100, 320, 200, 50) # Different Buttons for different Sizes
    btn_settings = pygame.Rect(WIDTH//2 - 100, 380, 200, 50)# -New- Added a button for the settings
    btn_quit = pygame.Rect(WIDTH//2 - 100, 440, 200, 50)
    
    btn_back = pygame.Rect(20, 20, 100, 40) # A button for a back action
    btn_about = pygame.Rect(WIDTH//2 - 100, 250, 200, 50) # -New- Added a button for the about menu

    clock = pygame.time.Clock()

    while True:
        SCREEN.fill(BG_COLOR)
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "MENU":
                    if btn_start_4.collidepoint(mx, my): n=4; state="PLAY"    # Different size handling
                    elif btn_start_5.collidepoint(mx, my): n=5; state="PLAY"  # Different size handling
                    elif btn_start_6.collidepoint(mx, my): n=6; state="PLAY"  # Different size handling
                    elif btn_settings.collidepoint(mx, my): state = "SETTINGS"# -New- Open Settings
                    elif btn_quit.collidepoint(mx, my): pygame.quit(); sys.exit() 
                        
                    if state == "PLAY":
                        grid, row_sums, col_sums = generate_level(n)
                        user_sel = [[False] * n for _ in range(n)] # Fill with False
                        user_dimmed = [[False] * n for _ in range(n)] # Fill with False
                        won = False
                        row_fulfilled = [False] * n
                        col_fulfilled = [False] * n
                        
                elif state == "SETTINGS": # -New- Handling while in SETTINGS
                    if btn_back.collidepoint(mx, my): state = "MENU"
                    elif btn_about.collidepoint(mx, my): state = "ABOUT"
                    
                elif state == "ABOUT": # -New- Handling being in the About
                    if btn_back.collidepoint(mx, my): state = "SETTINGS"
                        
                elif state == "PLAY":
                    if btn_back.collidepoint(mx, my): state="MENU" # Backbutton handling
                    elif not won: # Check clicks on the cells only while not won
                        offset_x = WIDTH // 2 - ((n+1) * CELL_SIZE) // 2
                        offset_y = HEIGHT // 2 - ((n+1) * CELL_SIZE) // 2
                    
                        if offset_x + CELL_SIZE <= mx < offset_x + (n+1) * CELL_SIZE and \
                           offset_y + CELL_SIZE <= my < offset_y + (n+1) * CELL_SIZE:
                            c = (mx - offset_x - CELL_SIZE) // CELL_SIZE
                            r = (my - offset_y - CELL_SIZE) // CELL_SIZE
                            user_dimmed[r][c] = False # If a cell get left clicked end rightclick look
                            user_sel[r][c] = not user_sel[r][c]
                            won = check_win(grid, user_sel, row_sums, col_sums, n)
                            row_fulfilled = [False] * n
                            col_fulfilled = [False] * n
                            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # Handling what happen with rightclicks
                if state == "PLAY":
                    if not won:
                        offset_x = WIDTH // 2 - ((n+1) * CELL_SIZE) // 2
                        offset_y = HEIGHT // 2 - ((n+1) * CELL_SIZE) // 2
                        
                        if offset_x + CELL_SIZE <= mx < offset_x + (n+1) * CELL_SIZE and \
                           offset_y + CELL_SIZE <= my < offset_y + (n+1) * CELL_SIZE:
                            c = (mx - offset_x - CELL_SIZE) // CELL_SIZE
                            r = (my - offset_y - CELL_SIZE) // CELL_SIZE
                            user_dimmed[r][c] = not user_dimmed[r][c] # Toggle for True/False
                            user_sel[r][c] = False # If dimmed it is not clicked
                            won = check_win(grid, user_sel, row_sums, col_sums, n)
                            row_fulfilled = [False] * n
                            col_fulfilled = [False] * n


        ### Draw the Screens
        if state == "MENU":
            draw_text("Mati", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 100)
            draw_text("Mathematic and Tactic Intelligence", SMALL_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 150)
            draw_button(btn_start_4, "Play 4x4", btn_start_4.collidepoint(mx, my)) 
            draw_button(btn_start_5, "Play 5x5", btn_start_5.collidepoint(mx, my)) 
            draw_button(btn_start_6, "Play 6x6", btn_start_6.collidepoint(mx, my))
            draw_button(btn_settings, "Settings", btn_settings.collidepoint(mx, my)) # -New- Added the button
            draw_button(btn_quit, "QUIT", btn_quit.collidepoint(mx, my))
            
        elif state == "SETTINGS": # -New- Draw the settings
            draw_text("Settings", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 100)
            draw_button(btn_back, "MENU", btn_back.collidepoint(mx, my))
            draw_button(btn_about, "About", btn_about.collidepoint(mx, my))
            
        elif state == "ABOUT": # -New- Draw the about
            draw_text("About Mati", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 100)
            draw_button(btn_back, "BACK", btn_back.collidepoint(mx, my))
            
            draw_text("Created by:", FONT, TEXT_COLOR, SCREEN, WIDTH//2, 250)
            draw_text("Janosch Klawatsch", FONT, TEXT_COLOR, SCREEN, WIDTH//2, 300)

            
        elif state == "PLAY":
            draw_button(btn_back, "MENU", btn_back.collidepoint(mx, my)) 
            offset_x = WIDTH // 2 - ((n+1) * CELL_SIZE) // 2
            offset_y = HEIGHT // 2 - ((n+1) * CELL_SIZE) // 2
            
            for r in range (n): # Automatic dimm row
                if sum(grid[r][c] for c in range(n) if user_sel[r][c]) == row_sums[r]: row_fulfilled[r] = True
                
            for c in range(n): # Automatic dimm col
                if sum(grid[r][c] for r in range(n) if user_sel[r][c]) == col_sums[c]: col_fulfilled[c] = True
        
            for c in range(n):
                cx = offset_x + (c + 1) * CELL_SIZE + CELL_SIZE // 2
                cy = offset_y + CELL_SIZE // 2
                draw_text(str(col_sums[c]), FONT, TARGET_COLOR, SCREEN, cx, cy) 
    
            for r in range(n):
                cx = offset_x + CELL_SIZE // 2
                cy = offset_y + (r + 1) * CELL_SIZE + CELL_SIZE // 2
                draw_text(str(row_sums[r]), FONT, TARGET_COLOR, SCREEN, cx, cy) 

                        
            for r in range(n):
                for c in range(n):
                    rect = pygame.Rect(offset_x + (c + 1) * CELL_SIZE, 
                                       offset_y + (r + 1) * CELL_SIZE, 
                                       CELL_SIZE, CELL_SIZE)
                    
                    is_dimmed = user_dimmed[r][c] or ((row_fulfilled[r] or col_fulfilled[c]) and not user_sel[r][c])
                
                    if user_sel[r][c]:
                        pygame.draw.rect(SCREEN, SELECTED_COLOR, rect)
                    elif rect.collidepoint(mx, my) and not is_dimmed and not won: # -New- Check for dimm as well
                        pygame.draw.rect(SCREEN, HOVER_COLOR, rect)
                    
                    pygame.draw.rect(SCREEN, GRID_COLOR, rect, 2) 
                    
                    current_text_color = DIMMED_TEXT_COLOR if is_dimmed else TEXT_COLOR # Check if number is dimmed or not to draw
                    
                    draw_text(str(grid[r][c]), FONT, current_text_color, SCREEN, rect.centerx, rect.centery) 
                    draw_outer_border(SCREEN, offset_x, offset_y, n, CELL_SIZE) # Give the grid a border
                    draw_fulfilled_indicators(SCREEN, grid, user_sel, row_sums, col_sums, n, offset_x, offset_y, CELL_SIZE) # Give the sums a mark if they are reached

                
            if won:
                draw_text("You won!", TITLE_FONT, (50, 180, 50), SCREEN, WIDTH//2, HEIGHT-50) 
                

        pygame.display.flip()
        clock.tick(60)

main()