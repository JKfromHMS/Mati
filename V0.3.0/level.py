### Mati (Mathematics and tactic intelligence) ###
### V0.3.0 Beta V1.0.14 ###
### Author: Janosch Klawatsch, 19.07.2026 ###
### level file V0.3.0 ###

### Structure-Plan ###
# - config.py - Constants #
# - level.py - Generate Levels, Check Wins ... #
# - persistence.py - Save and load of .mati files #
# - widgets.py - Draw-Functions #
# - game.py - The main game handling #
# - screens.py - Building the screens #
# - main.py - Entry point and main loop #
# - audio.py - Sound generation #
# - replay.py - Rebuild games # 
# - terminal.py - The Terminal #

### -Imports- ###
### External ###
import random as ra # To enable random generation processes

### -Functions- ###
def generate_level(n): # Generates a whole level
    while True:
        grid = [[ra.randint(1, 9) for _ in range(n)] for _ in range(n)] # Generate the grid
        selected = [[False] * n for _ in range(n)] # makes sure nothing is selected what could make the level unsolveable
        row_sums = [0] * n # Not calculated yet
        col_sums = [0] * n # Not calculated yet
        
        for r in range(n): # For every row
            num_to_select = ra.randint(1, n) # Defines how much nums this row will have
            indices = ra.sample(range(n), num_to_select) # Return the given number of cells random
            for c in indices: # For every choosen cell
                selected[r][c] = True # The game set it as intern marked
                row_sums[r] += grid[r][c] # Adds the amount of the new, to the exsistent
                
        for c in range(n): # For every column
            for r in range(n): # For every row in the column
                if selected[r][c]: # If the system selected it
                    col_sums[c] += grid[r][c] # Add the new the the rest
                    
        if 0 not in col_sums: # Needs to be a good level
            return grid, row_sums, col_sums, selected # Gives the level back
        
def generate_level_letter(n, letter_char): # Generates a whole level with given marked fields
    cover_1d = letter(n, letter_char) # Load the letter
    
    if not cover_1d: # If the letter is not defined
        return # Nothing to do
    
    grid = [[ra.randint(1, 9) for _ in range(n)] for _ in range(n)] # Generate the grid
    selected = [[False] * n for _ in range(n)] # makes sure nothing is selected what could make the level unsolveable
    row_sums = [0] * n # Not calculated yet
    col_sums = [0] * n # Not calculated yet
        
    # Live converting from 1d zu 2d while getting it done
    for r in range(n): # For every row
        for c in range(n): # For every column
            is_selected = cover_1d[r * n + c] # Convert for this row/column
            selected[r][c] = is_selected # Copy status to handle it
            if is_selected: # If it is true
                row_sums[r] += grid[r][c] # Count row sum
                col_sums[c] += grid[r][c] # Count col sum
                
    return grid, row_sums, col_sums, selected # Gives the level
                    
def letter(n, letter_char): # Defines letters
    cover = [] # Empty list
    T = True # Less to write
    F = False # Less to write
    if letter_char == "H": # If the letter is H
        if n == 5: # 5x5 grid
            cover = [T,F,F,F,T,
                     T,F,F,F,T,
                     T,T,T,T,T,
                     T,F,F,F,T,
                     T,F,F,F,T
                ]
        elif n == 7: # 7x7 grid
            cover = [T,T,F,F,F,T,T,
                     T,T,F,F,F,T,T,
                     T,T,F,F,F,T,T,
                     T,T,T,T,T,T,T,
                     T,T,F,F,F,T,T,
                     T,T,F,F,F,T,T,
                     T,T,F,F,F,T,T
                ]
    elif letter_char == "A": # If the letter is A
        if n == 5: # 5x5 grid
            cover = [F,T,T,T,F,
                     T,F,F,F,T,
                     T,T,T,T,T,
                     T,F,F,F,T,
                     T,F,F,F,T
                ]
        elif n == 7: # 7x7 grid
            cover = [F,F,T,T,T,F,F,
                     F,T,F,F,F,T,F,
                     T,F,F,F,F,F,T,
                     T,T,T,T,T,T,T,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T
                ]
    elif letter_char == "N": # If the letter is N
        if n == 5: # 5x5 grid
            cover = [T,F,F,F,T,
                     T,T,F,F,T,
                     T,F,T,F,T,
                     T,F,F,T,T,
                     T,F,F,F,T
                ]
        elif n == 7: # 7x7 grid
            cover = [T,F,F,F,F,F,F,T,
                     T,T,F,F,F,F,F,T,
                     T,F,T,F,F,F,F,T,
                     T,F,F,T,F,F,F,T,
                     T,F,F,F,T,F,F,T,
                     T,F,F,F,F,T,F,T,
                     T,F,F,F,F,F,T,T,
                     T,F,F,F,F,F,F,T
                ]
    elif letter_char == "M": # If the letter is M
        if n == 5: # 5x5 grid
            cover = [T,F,F,F,T,
                     T,T,F,T,T,
                     T,F,T,F,T,
                     T,F,F,F,T,
                     T,F,F,F,T
                ]
        elif n == 7: # 7x7 grid
            cover = [T,F,F,F,F,F,T,
                     T,T,F,F,F,T,T,
                     T,F,T,F,T,F,T,
                     T,F,F,T,F,F,T,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T
                ] 
    elif letter_char == "Y": # If the letter is Y
        if n == 5: # 5x5 grid
            cover = [T,F,F,F,T,
                     F,T,F,T,F,
                     F,F,T,F,F,
                     F,F,T,F,F,
                     F,F,T,F,F
                ]
        elif n == 7: # 7x7 grid
            cover = [T,F,F,F,F,F,T,
                     F,T,F,F,F,T,F,
                     F,F,T,F,T,F,F,
                     F,F,F,T,F,F,F,
                     F,F,F,T,F,F,F,
                     F,F,F,T,F,F,F,
                     F,F,F,T,F,F,F
                ]
    elif letter_char == "L": # If the letter is L
        if n == 5: # 5x5 grid
            cover = [T,F,F,F,F,
                     T,F,F,F,F,
                     T,F,F,F,F,
                     T,F,F,F,F,
                     T,T,T,T,T
                ]
        elif n == 7: # 7x7 grid
            cover = [T,F,F,F,F,F,F,
                     T,F,F,F,F,F,F,
                     T,F,F,F,F,F,F,
                     T,F,F,F,F,F,F,
                     T,F,F,F,F,F,F,
                     T,F,F,F,F,F,F,
                     T,T,T,T,T,T,T
                ]
    elif letter_char == "O": # If the letter is O
        if n == 5: # 5x5 grid
            cover = [F,T,T,T,F,
                     T,F,F,F,T,
                     T,F,F,F,T,
                     T,F,F,F,T,
                     F,T,T,T,F
                ]
        elif n == 7: # 7x7 grid
            cover = [F,T,T,T,T,T,F,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T,
                     F,T,T,T,T,T,F
                ]
    elif letter_char == "V": # If the letter is V
        if n == 5: # 5x5 grid
            cover = [T,F,F,F,T,
                     T,F,F,F,T,
                     T,F,F,F,T,
                     F,T,F,T,F,
                     F,F,T,F,F
                ]
        elif n == 7: # 7x7 grid
            cover = [T,F,F,F,F,F,T,
                     T,F,F,F,F,F,T,
                     F,T,F,F,F,T,F,
                     F,T,F,F,F,T,F,
                     F,F,T,F,T,F,F,
                     F,F,T,F,T,F,F,
                     F,F,F,T,F,F,F
                ]
    elif letter_char == "E": # If the letter is E
        if n == 5: # 5x5 grid
            cover = [T,T,T,T,T,
                     T,F,F,F,F,
                     T,T,T,T,F,
                     T,F,F,F,F,
                     T,T,T,T,T
                ]
        elif n == 7: # 7x7 grid
            cover = [T,T,T,T,T,T,T,
                     T,F,F,F,F,F,F,
                     T,F,F,F,F,F,F,
                     T,T,T,T,T,F,F,
                     T,F,F,F,F,F,F,
                     T,F,F,F,F,F,F,
                     T,T,T,T,T,T,T
                ]
            
    return cover # Gives the list back
        
def check_win(grid, user_sel, row_sums, col_sums, n): # Gets the situation and finds out if the player has one
    for r in range(n): # For every row
        if sum(grid[r][c] for c in range(n) if user_sel[r][c]) != row_sums[r]: # If a row is not correct
            return False # Say not won
    for c in range(n): # For every column
        if sum(grid[r][c] for r in range(n) if user_sel[r][c]) != col_sums[c]: # If a column is not correct
            return False # Say not won
    return True # If the functions comes so far, nothing inccorect was found

def find_hint(solution, user_sel, user_dimmed, n): # Identify a correct not selected sel
    problems = [] # To save the possible hints
    for r in range(n): # For every row
        for c in range(n): # For every column
            if solution[r][c] and not user_sel[r][c]: # Possible and new
                problems.append((r, c, True)) # Add hint to the list
            elif not solution[r][c] and user_sel[r][c]: # Wrong cell the user already has selected
                problems.append((r, c, False)) # Add hint to the list
                
    if not problems: # If everything is fine and nothing is missing
        return None # Say all good
    return ra.choice(problems) # Gives a random hint back