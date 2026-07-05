### Mati (Mathematics and tactic intelligence) ###
### V0.0.1 Beta V1.0.1 ###
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
BUTTON_COLOR = (100, 150, 220) # -New- Added a button color
BUTTON_HOVER = (80, 130, 200) # -New- Added a button hover color
CELL_SIZE = 60

### --- Pygame Initialization --- ###
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mati")
FONT = pygame.font.SysFont("arial", 28, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 24) # -New- Added a small font shortcut

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
                
    if 0 in col_sums: # -New- If a column is empty
        generate_level(n) # -New- Regenerate the level
                
    return grid, row_sums, col_sums # Return the grid and the sums

### Win Check ###
def check_win(grid, user_sel, row_sums, col_sums, n): # -New- Added a complete new function system
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
def draw_text(text, font, color, surface, x, y, center=True): # -New- A function to draw text to the screen
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_button(rect, text, is_hovered): # -New- A function to draw buttons to the screen
    color = BUTTON_HOVER if is_hovered else BUTTON_COLOR # If hovered, one color, if not the other
    pygame.draw.rect(SCREEN, color, rect, border_radius=8)
    draw_text(text, SMALL_FONT, (255,255,255), SCREEN, rect.centerx, rect.centery)
    
### --- Main Loop --- ###
def main():
    state = "MENU" # Add a state system to handle different screens
    n = 5
    grid, row_sums, col_sums, user_sel = [], [], [], [] # Create the variables
    won = False
    
    # Add buttons for the screens
    btn_start_4 = pygame.Rect(WIDTH//2 - 100, 200, 200, 50) # -New- Different Buttons for different Sizes
    btn_start_5 = pygame.Rect(WIDTH//2 - 100, 270, 200, 50) # -New- Different Buttons for different Sizes
    btn_start_6 = pygame.Rect(WIDTH//2 - 100, 340, 200, 50) # -New- Different Buttons for different Sizes
    btn_quit = pygame.Rect(WIDTH//2 - 100, 410, 200, 50)
    btn_back = pygame.Rect(20, 20, 100, 40) # -New- A button for a back action

    clock = pygame.time.Clock()

    while True:
        SCREEN.fill(BG_COLOR)
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "MENU":
                    if btn_start_4.collidepoint(mx, my): n=4; state="PLAY"  # -New- Different size handling
                    elif btn_start_5.collidepoint(mx, my): n=5; state="PLAY"# -New- Different size handling
                    elif btn_start_6.collidepoint(mx, my): n=6; state="PLAY"# -New- Different size handling
                    elif btn_quit.collidepoint(mx, my): pygame.quit(); sys.exit() 
                        
                    if state == "PLAY":
                        grid, row_sums, col_sums = generate_level(n)
                        user_sel = [[False] * n for _ in range(n)]
                        won = False
                        
                elif state == "PLAY":
                    if btn_back.collidepoint(mx, my): state="MENU" # -New- Backbutton handling
                    elif not won: # Clicks on the cells only while not won
                        offset_x = WIDTH // 2 - ((n+1) * CELL_SIZE) // 2
                        offset_y = HEIGHT // 2 - ((n+1) * CELL_SIZE) // 2
                    
                        if offset_x + CELL_SIZE <= mx < offset_x + (n+1) * CELL_SIZE and \
                           offset_y + CELL_SIZE <= my < offset_y + (n+1) * CELL_SIZE:
                            c = (mx - offset_x - CELL_SIZE) // CELL_SIZE
                            r = (my - offset_y - CELL_SIZE) // CELL_SIZE
                            user_sel[r][c] = not user_sel[r][c]
                            won = check_win(grid, user_sel, row_sums, col_sums, n)


        ### Draw the Screens
        if state == "MENU":
            draw_text("Mati", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 100)
            draw_text("Mathematic and Tactic Intelligence", SMALL_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 150)
            draw_button(btn_start_4, "Play 4x4", btn_start_4.collidepoint(mx, my)) # -New- Activate all Buttons
            draw_button(btn_start_5, "Play 5x5", btn_start_5.collidepoint(mx, my)) # -New- Activate all Buttons
            draw_button(btn_start_6, "Play 6x6", btn_start_6.collidepoint(mx, my)) # -New- Activate all Buttons
            draw_button(btn_quit, "QUIT", btn_quit.collidepoint(mx, my))
            
        elif state == "PLAY":
            draw_button(btn_back, "MENU", btn_back.collidepoint(mx, my)) # -New- Activate all Buttons
            offset_x = WIDTH // 2 - ((n+1) * CELL_SIZE) // 2
            offset_y = HEIGHT // 2 - ((n+1) * CELL_SIZE) // 2
        
            for c in range(n):
                cx = offset_x + (c + 1) * CELL_SIZE + CELL_SIZE // 2
                cy = offset_y + CELL_SIZE // 2
                draw_text(str(col_sums[c]), FONT, TARGET_COLOR, SCREEN, cx, cy) # -New- Change to new system
    
            
            for r in range(n):
                cx = offset_x + CELL_SIZE // 2
                cy = offset_y + (r + 1) * CELL_SIZE + CELL_SIZE // 2
                draw_text(str(row_sums[r]), FONT, TARGET_COLOR, SCREEN, cx, cy) # -New- Change to new system

            
            for r in range(n):
                for c in range(n):
                    rect = pygame.Rect(offset_x + (c + 1) * CELL_SIZE, 
                                       offset_y + (r + 1) * CELL_SIZE, 
                                       CELL_SIZE, CELL_SIZE)
                
                    if user_sel[r][c]:
                        pygame.draw.rect(SCREEN, SELECTED_COLOR, rect)
                    elif rect.collidepoint(mx, my) and not won:
                        pygame.draw.rect(SCREEN, HOVER_COLOR, rect)
                    
                    pygame.draw.rect(SCREEN, GRID_COLOR, rect, 2) 
                    draw_text(str(grid[r][c]), FONT, TEXT_COLOR, SCREEN, rect.centerx, rect.centery) # -New- Change to new system

                
            if won:
                draw_text("You won!", TITLE_FONT, (50, 180, 50), SCREEN, WIDTH//2, HEIGHT-50) # -New- Change to new system
                

        pygame.display.flip()
        clock.tick(60)

main()