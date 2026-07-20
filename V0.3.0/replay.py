### Mati (Mathematics and tactic intelligence) ###
### V0.3.0 Beta V1.0.14 ###
### Author: Janosch Klawatsch, 16.07.2026 ###
### replay file V0.1.1 ###

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

### -Functions- ###
def _derive_new_state(action): # Checks for new file states
    if "new_sel" in action and "new_dimmed" in action: # If it is a new file
        return action["new_sel"], action["new_dimmed"] # Give the given values
    
    action_type = action.get("type") # Get action type
    prev_sel = action.get("prev_sel", False) # If just prev_sel
    prev_dimmed = action.get("prev_dimmed", False) # If just prev_dimmed
    if action_type == "Left": # If action was to select
        return (not prev_sel), False # Return if prev_sel is missing
    if action_type == "Right": # If action was to dim
        return False, (not prev_dimmed) # Return if prev_dimmed is missing
    return prev_sel, prev_dimmed # If the code does this, the action was not left or right

def reconstruct_state(data, up_to_index): # Reconstruct the state for each move
    if up_to_index is None: # If is to index is not set, normally means last move in the game
        return (data["user_sel"], data["user_dimmed"], data.get("hints_used", 0), data.get("play_time", 0), None) # Gives the needed data
    
    n = len(data["grid"]) # Load n from the data
    user_sel = [[False] * n for _ in range(n)] # Nothing selected
    user_dimmed = [[False] * n for _ in range(n)] # Nothing dimmed
    actions = data.get("actions", []) # Load all actions
    hints_used = 0 # No hint used now
    play_time = 0 # No time in the game yet
    last_action = None # No action done until
    
    up_to_index = max(0, min(up_to_index, len(actions) - 1)) # Makes sure the up_to_index is valid
    for i in range(up_to_index + 1): # Count the index and add the end situation
        act = actions[i] # Extract one action
        r, c = act["r"], act["c"] # Load the row and the column of the action
        new_sel, new_dimmed = _derive_new_state(act) # Load the states depending on the file case, new or old
        user_sel[r][c] = new_sel # copy the states to draw
        user_dimmed[r][c] = new_dimmed # copy the state to draw
        if act.get("type") == "Hint": # If action is a hint
            hints_used += 1 # One more hint was used
        play_time = act.get("time", play_time) # Get the play_time
        last_action = act # This action is over means this action is old
        
    if last_action is not None and "hints_used_so_far" in last_action: # If it is a new action available
        hints_used = last_action["hints_used_so_far"] # Redefine as the given number
        
    return user_sel, user_dimmed, hints_used, play_time, last_action # Give the asked values back
