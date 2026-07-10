### Mati (Mathematics and tactic intelligence) ###
### V0.0.8 Beta V1.0.8 ###
### Author: Janosch Klawatsch, 09.07.2026 ###
### persistence file V0.0.0 ###

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
import glob # For file searching
import json # For the file format
import os   # For OS communication
from datetime import datetime

### Own ###
from config import HISTORY_DIR as HD # Information where the files should be

### -Functions- ###
def _ensure_history_dir(): # Create the folder if needed
    os.makedirs(HD, exist_ok=True) # ||
    
def _resolve_path(filename): # For the old file save location
    new_path = os.path.join(HD, filename) # New path
    if os.path.exists(new_path): # checks if the new filepath can be found
        return new_path # Give the new path
    return filename # Give the normal path, if the new is not available

def save_match(grid, row_sums, col_sums, user_sel ,user_dimmed, play_time, actions, hints_used): # Get information about the file
    _ensure_history_dir() # create the folder for the files
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mati"
    data = {
        "grid": grid,
        "row_sums": row_sums,
        "col_sums": col_sums,
        "user_sel": user_sel,
        "user_dimmed": user_dimmed,
        "play_time": play_time,
        "actions": actions,
        "hints_used": hints_used
    } # The data that need to be saved
    with open(os.path.join(HD, filename), "w") as f: # Creates the new file
        json.dump(data, f) # Writes the new file
    return filename # Gives the name of the new file

def list_history(): # list all the files
    _ensure_history_dir() # If no folder exsists
    new_files = sorted(glob.glob(os.path.join(HD, "*.mati")), reverse=True) # List the new files
    legacy_files = sorted(glob.glob("*.mati"), reverse=True) # List the old files
    names = [os.path.basename(f) for f in new_files] + [os.path.basename(f) for f in legacy_files] # Connects the list to one
    return names # Give all the names

def load_match(filename): # Load the data from a file
    with open(_resolve_path(filename), "r") as f: # Open a file
        return json.load(f) # Gives the things in the file 
    
def delete_match(filename): # Deletes a file from the storage
    path = _resolve_path(filename) # Get the full path
    if os.path.exists(path): # Is it the right file
        os.remove(path) # Delete the file