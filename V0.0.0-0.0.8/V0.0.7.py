### Mati (Mathematics and tactic intelligence) ###
### V0.0.6 Beta V1.0.7 ###
### Author: Janosch Klawatsch, 05.07.2026 ###

### --- Imports --- ###
import pygame # pygame is something like a game engine
import random # for random number generation
import sys    # for system funtions like exit
import json   # -New- To enable json file handling
import os     # -New- To enable OS features
import glob   # -New- 
from datetime import datetime # -New- To get the excate time

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
        return generate_level(n) # Regenerate the level
                
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
            
            
### --- .mati stuff ###
def save_match_to_mati(grid, row_sums, col_sums, user_sel, user_dimmed, play_time, actions): # -New- Enable to save as a .mati
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mati"
    
    data = {
        "grid": grid,
        "row_sums": row_sums,
        "col_sums": col_sums,
        "user_sel": user_sel,
        "user_dimmed": user_dimmed,
        "play_time": play_time,
        "actions": actions
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f)
        
        
### --- Main Loop --- ###
def main():
    state = "MENU" # Add a state system to handle different screens
    n = 5
    grid, row_sums, col_sums, user_sel, user_dimmed = [], [], [], [], [] # Create the variables
    won = False
    timer_enabled = False # save if the timer is on or off
    timer_ms = False # same for special role of miliseconds
    save_history = True # -New- should the games be saved
    
    current_game_actions = [] # -New- Save all game actions
    history_files = [] # -New- List of all found games
    selected_history_data = None # -New- Data of this round
    history_scroll_y = 0 # -New- The scroll state for the history menu
    last_scroll_time = 0 # -New- Last scroll
    scroll_speed_factor = 0 # -New- How fast is scrolled
    
    # Add buttons for the screens
    # Main screen
    btn_start_4 = pygame.Rect(WIDTH//2 - 100, 200, 200, 50) # Different Buttons for different Sizes
    btn_start_5 = pygame.Rect(WIDTH//2 - 100, 260, 200, 50) # Different Buttons for different Sizes
    btn_start_6 = pygame.Rect(WIDTH//2 - 100, 320, 200, 50) # Different Buttons for different Sizes
    btn_settings = pygame.Rect(WIDTH//2 - 100, 380, 200, 50)# Add a button for the settings
    btn_history = pygame.Rect(WIDTH//2 - 100, 440, 200, 50) # -New- To open the history
    btn_quit = pygame.Rect(WIDTH//2 - 100, 500, 200, 50)
    
    # Others
    btn_back = pygame.Rect(20, 20, 100, 40) # A button for a back action
    btn_about = pygame.Rect(WIDTH//2 - 100, 350, 200, 50) # Add a button for the about menu
    btn_toggle_timer = pygame.Rect(WIDTH//2 - 100, 230, 200, 50) # Add a button for the timer
    btn_toggle_ms = pygame.Rect(WIDTH//2 - 100, 290, 200, 50) # Toggle for ms
    btn_toggle_history = pygame.Rect(WIDTH//2 - 100, 170, 200, 50) # -New- History On/Off toggle
    
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
                    elif btn_settings.collidepoint(mx, my): state = "SETTINGS"# Open Settings
                    elif btn_history.collidepoint(mx, my): history_files = sorted(glob.glob("*.mati"), reverse=True); history_scroll_y = 0; state="HISTORY" # -New- What do wenn clicked history
                    elif btn_quit.collidepoint(mx, my): pygame.quit(); sys.exit() 
                        
                    if state == "PLAY":
                        grid, row_sums, col_sums = generate_level(n)
                        user_sel = [[False] * n for _ in range(n)] # Fill with False
                        user_dimmed = [[False] * n for _ in range(n)] # Fill with False
                        won = False
                        row_fulfilled = [False] * n
                        col_fulfilled = [False] * n
                        start_time = pygame.time.get_ticks() # -New- Start time, for the timer
                        play_time = 0
                        current_game_actions = [] # -New- Start an empty action list
                        
                elif state == "SETTINGS": # Handling while in SETTINGS
                    if btn_back.collidepoint(mx, my): state = "MENU"
                    elif btn_about.collidepoint(mx, my): state = "ABOUT"
                    elif btn_toggle_timer.collidepoint(mx, my): timer_enabled = not timer_enabled
                    elif btn_toggle_ms.collidepoint(mx, my): timer_ms = not timer_ms
                    elif btn_toggle_history.collidepoint(mx, my): save_history = not save_history # -New- Toggle Logic for saving
                    
                elif state == "ABOUT": # Handling being in the About
                    if btn_back.collidepoint(mx, my): state = "SETTINGS"
                    
                elif state == "HISTORY": # -New- What to do in past game view
                    if btn_back.collidepoint(mx, my): state="MENU"
                    else:
                        for i, f in enumerate(history_files):
                            btn_y = 100 + i * 60 + history_scroll_y
                            if my > 80:
                                rect = pygame.Rect(WIDTH//2 - 150, btn_y, 300, 40)
                                if rect.collidepoint(mx, my):
                                    with open(f, 'r') as file:
                                        selected_history_data = json.load(file)
                                    state = "HISTORY_DETAIL"
                                    
                elif state == "HISTORY_DETAIL": # -New- To handle the look in one file
                    if btn_back.collidepoint(mx, my): state="HISTORY"
                        
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
                            current_game_actions.append({
                                "time": play_time,
                                "type": "Left",
                                "r": r, "c": c
                            }) # -New- Save every action
                            won = check_win(grid, user_sel, row_sums, col_sums, n)
                            row_fulfilled = [False] * n
                            col_fulfilled = [False] * n
                            
                            if won and save_history: # -New- If game over and save is on
                                save_match_to_mati(grid, row_sums, col_sums, user_sel, user_dimmed, play_time, current_game_actions)
                            
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
                            current_game_actions.append({
                                "time": play_time,
                                "type": "Right",
                                "r": r, "c": c
                            }) # -New- Save every action
                            won = check_win(grid, user_sel, row_sums, col_sums, n)
                            row_fulfilled = [False] * n
                            col_fulfilled = [False] * n
                            
                            if won and save_history: # -New- If game over and save is on
                                save_match_to_mati(grid, row_sums, col_sums, user_sel, user_dimmed, play_time, current_game_actions)
            
            elif event.type == pygame.MOUSEWHEEL: # -New- For a scrollbar we catch the mousewheel movement
                if state == "HISTORY":
                    current_time = pygame.time.get_ticks()
                    time_diff = current_time - last_scroll_time
                    last_scroll_time = current_time
                    
                    if time_diff == 0: time_diff = 1
                    
                    raw_speed = event.y / time_diff
                    scroll_speed = 1 + (abs(raw_speed) * 1000)
                    
                    history_scroll_y += event.y * scroll_speed
                    max_scroll = 0
                    min_scroll = -max(0, (len(history_files) * 60) - (HEIGHT - 150))
                    history_scroll_y = max(min_scroll, min(history_scroll_y, max_scroll))
                                    
        if state == "PLAY" and not won: # To track the time
            play_time = pygame.time.get_ticks() - start_time


        ### Draw the Screens
        if state == "MENU":
            draw_text("Mati", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 100)
            draw_text("Mathematic and Tactic Intelligence", SMALL_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 150)
            draw_button(btn_start_4, "Play 4x4", btn_start_4.collidepoint(mx, my)) 
            draw_button(btn_start_5, "Play 5x5", btn_start_5.collidepoint(mx, my)) 
            draw_button(btn_start_6, "Play 6x6", btn_start_6.collidepoint(mx, my))
            draw_button(btn_settings, "Settings", btn_settings.collidepoint(mx, my)) # Add the button
            draw_button(btn_history, "History", btn_history.collidepoint(mx, my))
            draw_button(btn_quit, "QUIT", btn_quit.collidepoint(mx, my))
            
        elif state == "SETTINGS": # -New- Draw the settings
            draw_text("Settings", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 100)
            draw_button(btn_back, "MENU", btn_back.collidepoint(mx, my))
            hist_text = "Save: ON" if save_history else "Save: OFF"
            draw_button(btn_toggle_history, hist_text, btn_toggle_history.collidepoint(mx, my)) # -New- Show the button
            timer_text = "Timer: ON" if timer_enabled else "Timer: OFF"
            draw_button(btn_toggle_timer, timer_text, btn_toggle_timer.collidepoint(mx, my))
            if timer_enabled:
                ms_text = "MS: ON" if timer_ms else "MS: OFF"
                btn_about = pygame.Rect(WIDTH//2 - 100, 350, 200, 50)
                draw_button(btn_about, "About", btn_about.collidepoint(mx, my))
                draw_button(btn_toggle_ms, ms_text, btn_toggle_ms.collidepoint(mx, my))
            else:
                btn_about = pygame.Rect(WIDTH//2 - 100, 290, 200, 50)
                draw_button(btn_about, "About", btn_about.collidepoint(mx, my))
                
                
        elif state == "HISTORY": # -New- History view
            if not history_files:
                draw_text("Last Games", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 50)
                draw_button(btn_back, "MENU", btn_back.collidepoint(mx, my))
                draw_text("No saved games found!", FONT, DIMMED_TEXT_COLOR, SCREEN, WIDTH//2, 200)
            
            else:
                scroll_area = pygame.Rect(0, 80, WIDTH, HEIGHT - 80)
                SCREEN.set_clip(scroll_area)
                for i, f in enumerate(history_files):
                    btn_y = 100 + i * 60 + history_scroll_y
                    rect = pygame.Rect(WIDTH//2 - 150, btn_y, 300, 40)
                    dis_name = f.replace(".mati", "").replace("_", " ")
                    draw_button(rect, dis_name, rect.collidepoint(mx, my))
                
                SCREEN.set_clip(None)
                draw_text("Last Games", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 50)
                draw_button(btn_back, "MENU", btn_back.collidepoint(mx, my))
                
                    
        elif state == "HISTORY_DETAIL" and selected_history_data: # -New- Detail history look
            draw_button(btn_back, "BACK", btn_back.collidepoint(mx, my))
            draw_text("End & Actions", TITLE_FONT, TEXT_COLOR, SCREEN, WIDTH//2, 40)
            
            h_data = selected_history_data
            hn = len(h_data["grid"])
            
            h_offset_x = WIDTH // 2 - ((hn+1) * CELL_SIZE) // 2
            h_offset_y = 100
            
            for r in range(hn):
                for c in range(hn):
                    rect = pygame.Rect(h_offset_x + (c + 1) * CELL_SIZE, h_offset_y + (r + 1)* CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    
                    is_dimmed = h_data["user_dimmed"][r][c]
                    is_sel = h_data["user_sel"][r][c]
                    
                    if is_sel:
                        pygame.draw.rect(SCREEN, SELECTED_COLOR, rect)
                        
                    pygame.draw.rect(SCREEN, GRID_COLOR, rect, 2)
                    colo = DIMMED_TEXT_COLOR if is_dimmed else TEXT_COLOR
                    draw_text(str(h_data["grid"][r][c]), FONT, colo, SCREEN, rect.centerx, rect.centery)
            
            draw_outer_border(SCREEN, h_offset_x, h_offset_y, hn, CELL_SIZE)
            
            start_text_y = h_offset_y + (hn + 1) * CELL_SIZE + 20
            draw_text(f'Time: {h_data["play_time"] // 1000}:{(h_data["play_time"] % 1000):3}s', FONT, TARGET_COLOR, SCREEN, WIDTH//2, start_text_y)
            
            actions_to_show = h_data["actions"][-5:]
            for i, act in enumerate(actions_to_show):
                second = act["time"] // 1000
                ms = act["time"] % 1000
                t_str = f'[{second:02}:{ms:02}s] {act["c"]+1}'
                draw_text(t_str, SMALL_FONT, TEXT_COLOR, SCREEN, WIDTH//2, start_text_y + 40 + (i * 25))
            
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

            if timer_enabled: # -New- So you can see the timer
                seconds = (play_time // 1000) % 60
                minutes = (play_time // 1000) // 60
                if timer_ms:
                    miliseconds = play_time % 1000
                    time_string = f'Time: {minutes:02}:{seconds:02}:{miliseconds:03}'
                else:
                    time_string = f'Time: {minutes:02}:{seconds:02}'
                draw_text(time_string, FONT, TEXT_COLOR, SCREEN, WIDTH - 100, 40)
            
            if won:
                draw_text("You won!", TITLE_FONT, (50, 180, 50), SCREEN, WIDTH//2, HEIGHT-50) 
                

        pygame.display.flip()
        clock.tick(60)

main()