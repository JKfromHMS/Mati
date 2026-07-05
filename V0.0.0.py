### Mati (Mathematics and tactic intelligence trainer) ###
### V0.0.0 Beta V1.0.0 ###
### Author: Janosch Klawatsch, 04.07.2026 ###

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
CELL_SIZE = 60

### --- Pygame Initialization --- ###
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mati")
FONT = pygame.font.SysFont("arial", 28, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)

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
                
    return grid, row_sums, col_sums # Return the grid and the sums

def check_win(grid, user_sel, row_sums, col_sums, n):
    # Check the rows
    for r in range(n):
        current_row_sum = 0 # The sum of the current row
        for c in range(n):
            if user_sel[r][c]: # If the user selected this cell
                current_row_sum += grid[r][c] # Calculate the sum of the row
                
        # Check the sums
        if current_row_sum != row_sums[r]: # If the sum is not equal
            return False # Game not over
                
    # Check the columns
    for c in range(n):
        current_col_sum = 0 # The sum of the current column
        for r in range(n):
            if user_sel[r][c]: # If the user selected this cell
                current_col_sum += grid[r][c] # Calculate the sum of the column
                
        # Check the sums
        if current_col_sum != col_sums[c]: # If the sum is not equal
            return False # Game not over
        
    return True # If the programm still runs, the player must have completed the game


### --- Main Loop --- ###
def main():
    n = 5
    grid, row_sums, col_sums = generate_level(n)
    user_sel = [[False] * n for _ in range(n)]
    won = False
    
    offset_x = WIDTH // 2 - ((n + 1) * CELL_SIZE) // 2
    offset_y = HEIGHT // 2 - ((n + 1) * CELL_SIZE) // 2
    
    clock = pygame.time.Clock()

    while True:
        SCREEN.fill(BG_COLOR)
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not won:
                if offset_x + CELL_SIZE <= mx < offset_x + (n + 1) * CELL_SIZE and \
                   offset_y + CELL_SIZE <= my < offset_y + (n + 1) * CELL_SIZE:
                    
                    c = (mx - offset_x - CELL_SIZE) // CELL_SIZE
                    r = (my - offset_y - CELL_SIZE) // CELL_SIZE
                    
                    user_sel[r][c] = not user_sel[r][c] 
                    
                    won = check_win(grid, user_sel, row_sums, col_sums, n)

        
        for c in range(n):
            cx = offset_x + (c + 1) * CELL_SIZE + CELL_SIZE // 2
            cy = offset_y + CELL_SIZE // 2
            textobj = FONT.render(str(col_sums[c]), True, TARGET_COLOR)
            SCREEN.blit(textobj, textobj.get_rect(center=(cx, cy)))
            
        for r in range(n):
            cx = offset_x + CELL_SIZE // 2
            cy = offset_y + (r + 1) * CELL_SIZE + CELL_SIZE // 2
            textobj = FONT.render(str(row_sums[r]), True, TARGET_COLOR)
            SCREEN.blit(textobj, textobj.get_rect(center=(cx, cy)))
            
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
                
                textobj = FONT.render(str(grid[r][c]), True, TEXT_COLOR)
                SCREEN.blit(textobj, textobj.get_rect(center=rect.center))
                
        if won:
            textobj = TITLE_FONT.render("You won!", True, (50, 180, 50))
            SCREEN.blit(textobj, textobj.get_rect(center=(WIDTH//2, HEIGHT - 50)))

        pygame.display.flip()
        clock.tick(60)

main()