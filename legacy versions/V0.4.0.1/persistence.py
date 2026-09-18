### Mati (Mathematics and tactic intelligence) ###
### V0.4.0.1 Beta V1.0.18 ###
### Author: Janosch Klawatsch, 11.08.2026 ###
### persistence file V0.4.1 ###

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
import base64                       # To make the obfuscated bytes safe to store as text
import glob                         # For file searching
import json                         # For the file format
import os                           # For OS communication
import zlib                         # To compress and to help obfuscate the saved files
from datetime import datetime as dt # For the date and time

### Own ###
from config import HISTORY_DIR as HD     # Information where the files should be
from config import SETTINGS_FILE as SF   # Information where the settings file is
from config import DIFFICULTIES as DIFFS # The grid sizes

### -Functions- ###
def _ensure_history_dir(): # Create the folder if needed
    os.makedirs(HD, exist_ok=True) # ||
    
def _resolve_path(filename): # For the old file save location
    new_path = os.path.join(HD, filename) # New path
    if os.path.exists(new_path): # checks if the new filepath can be found
        return new_path # Give the new path
    return filename # Give the normal path, if the new is not available

_XOR_KEY = b"Mati_Obfuscation_Key_2026" # A fixed key, just to make it uneditable not to make it save

def _xor(raw): # XOR every byte to make it uneditable
    key = _XOR_KEY # Short name, introduction because it should be in config later
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(raw)) # One xor per byte

def _encode(data): # Turns a python dict into an obfuscated, storable text
    raw = json.dumps(data).encode("utf-8") # Normal JSON, as bytes
    compressed = zlib.compress(raw) # Smaller and not readable for humans anymore
    scrambled = _xor(compressed) # Not defineable anymore
    return base64.b64encode(scrambled).decode("ascii") # Saved data

def _decode(blob): # text to python dict
    scrambled = base64.b64decode(blob.encode("ascii")) # Back to raw
    compressed = _xor(scrambled) # Xor undoes itself
    raw = zlib.decompress(compressed) # Back to original json bytes
    return json.loads(raw.decode("utf-8")) # Bac kto python dict

def _read_data_file(path): # Reads a .mati/.smati file
    with open(path, "r") as f: # Open the file
        content = f.read() # Get its whole content
    try: # The normal, obfuscated file
        return _decode(content) # Try to decode it
    except Exception: # Normally in reason of an old file decode
        return json.loads(content) # Decode it on the old way
    
def _write_data_file(path, data): # Save a obfuscated file
    with open(path, "w") as f: # Open/create the file
        f.write(_encode(data)) # Write the obfuscated blob

def save_match(grid, row_sums, col_sums, user_sel ,user_dimmed, play_time, actions, hints_used, ultra=False): # Get information about the file
    _ensure_history_dir() # create the folder for the files
    filename = dt.now().strftime("%Y-%m-%d_%H-%M-%S.%f") + ".mati"
    data = {
        "grid": grid,
        "row_sums": row_sums,
        "col_sums": col_sums,
        "user_sel": user_sel,
        "user_dimmed": user_dimmed,
        "play_time": play_time,
        "actions": actions,
        "hints_used": hints_used,
        "ultra": ultra
    } # The data that need to be saved
    _write_data_file(os.path.join(HD, filename), data) # save the data
    return filename # Gives the name of the new file

def list_history(): # list all the files
    _ensure_history_dir() # If no folder exsists
    new_files = sorted(glob.glob(os.path.join(HD, "*.mati")), reverse=True) # List the new files
    legacy_files = sorted(glob.glob("*.mati"), reverse=True) # List the old files
    names = [os.path.basename(f) for f in new_files] + [os.path.basename(f) for f in legacy_files] # Connects the list to one
    return names # Give all the names

def _label_for(filename): # Rewrite the filename
    stem = filename.replace(".mati", "") # cut the .mati off
    for fmt in ("%Y-%m-%d_%H-%M-%S-%f", "%Y-%m-%d_%H-%M-%S.%f", "%Y-%m-%d_%H-%M-%S"): # Every file from the new and the old system
        try: # Only continues if possible
            d = dt.strptime(stem, fmt) # Read the time
            return d.strftime("%d.%m.%Y %H:%M:%S") # the format we want to have
        except ValueError: # Not valid name
            continue # Do nothing, but let the rest of the code do their work
    return stem.replace("_", " ") # To make the look of the unchanged names a little better

def list_history_meta(): # list all the files with extra information
    entries = [] # Defines a list
    for name in list_history(): # Gets the normale list from the old method
        try: # does if possible
            data = load_match(name) # Load the game
        except (OSError, json.JSONDecodeError): # OS denies it or JSON cant encode the file
            continue # Do like nothing happens
        entries.append({
            "filename": name,
            "label": _label_for(name),
            "size": len(data.get("grid", [])),
            "play_time": data.get("play_time", 0),
            "hints_used": data.get("hints_used", 0),
            "ultra": data.get("ultra")
        }) # Save the important imformations temporary
    return entries # Give the saved entries

def load_match(filename): # Load the data from a file
    return _read_data_file(_resolve_path(filename)) # Give the things in the file
    
def delete_match(filename): # Deletes a file from the storage
    path = _resolve_path(filename) # Get the full path
    if os.path.exists(path): # Is it the right file
        os.remove(path) # Delete the file
        
### -Settings, Statistics and paused games (.smati)- ###
DEFAULT_SETTINGS = {
    "save_history": True,
    "timer_enabled": False,
    "timer_ms": False,
    "sound_enabled": True,
    "alt_control": True,
    "live_clock_enabled": False,
    "ultra_timer_enabled": False,
    "ultra_timer_ms": False,
    "ultra_timer_show_clock": False,
} # The defaults, for the case no file exists.

DEFAULT_PROGRESS = {
    "visited_terminal": False,
    "found_42": False,
}

DEFAULT_ACHIEVMENTS = {
    "hannah_completed": False,
    "1_4x4": False,
    "25_4x4": False,
    "50_4x4": False,
    "75_4x4": False,
    "100_4x4": False,
    "150_4x4": False,
    "200_4x4": False,
    "1_4x4_ultra": False,
    "25_4x4_ultra": False,
    "50_4x4_ultra": False,
    "75_4x4_ultra": False,
    "100_4x4_ultra": False,
    "150_4x4_ultra": False,
    "200_4x4_ultra": False,
}

def _settings_path(): # Where the settings file actually lives
    return os.path.join(HD, SF) # Its full path

def _legacy_settings_path(): # Legacy save location
    return SF 

def _default_stats(): # Build an empty statistics structure
    return {
        str(n): {
            "normal": {"games":0, "best": None, "total": 0}, 
            "ultra": {"games": 0, "best": None, "total": 0}
        } for n in DIFFS
    } # One entry for every grid size
    
def load_settings_and_stats(): # Load settings, stats and paused games
    _ensure_history_dir() # Make sure the destination folder is there
    path = _settings_path() # The correct location
    if not os.path.exists(path) and os.path.exists(_legacy_settings_path()): # An older version of this file
        path = _legacy_settings_path() # Get the old file
    if not os.path.exists(path): # If the file does not exsist
        return dict(DEFAULT_SETTINGS), _default_stats(), {}, [], dict(DEFAULT_PROGRESS) # Give the defaults back
    try: # try to read it
        data = _read_data_file(path) # Load the content
    except (OSError, json.JSONDecodeError, zlib.error, ValueError): # If the file is broken or the system denies it
        return dict(DEFAULT_SETTINGS), _default_stats(), {}, [], dict(DEFAULT_PROGRESS) # Give back the default
    settings = {**DEFAULT_SETTINGS, **data.get("settings", {})} # Merge saved values
    stats = data.get("stats", {}) # Load the stats
    for n in DIFFS: # Make sure it works with files with missing sizes
        stats.setdefault(str(n), {"normal": {"games": 0, "best": None, "total": 0}, "ultra": {"games": 0, "best": None, "total":0}}) # Default for no set sizes 
    paused = data.get("paused", {}) # Load the paused games
    hannah = data.get("hannah", []) # Load the hannah easter egg progress
    progress = {**DEFAULT_PROGRESS, **data.get("progress", {})} # Load the progresses
    achievments = {**DEFAULT_ACHIEVMENTS, **data.get("achievments", {})}
    return settings, stats, paused, hannah, progress#, achievments # Give everything back

def save_settings_and_stats(settings, stats, paused, hannah=None, progress=None, achievments=None): # Save the settings, stats and paused games in a file
    _ensure_history_dir() # make sure he folder exists
    path = _settings_path() # The correct, current location
    existing_path = path if os.path.exists(path) else (_legacy_settings_path() if os.path.exists(_legacy_settings_path()) else None) # Every possible folder of the file
    if hannah is None or progress is None: # If the player has not found the easter egg
        old_hannah, old_progress = [], dict(DEFAULT_PROGRESS) # Fallback, empty value
        if existing_path: # If there is the setting file
            try: # Try to load existing Hannah progress
                old = _read_data_file(existing_path) # load the content
                old_hannah = old.get("hannah", []) # Load the old hannah content
                old_progress = {**DEFAULT_PROGRESS, **old.get("progress", {})} # Load the progress
            except (OSError, json.JSONDecodeError, zlib.error, ValueError): # If it is broken
                pass
        if hannah is None: hannah = old_hannah # The saved what was there
        if progress is None: progress = old_progress # The saved what was there
    data = {"settings": settings, "stats": stats, "paused": paused, "hannah": hannah, "progress": progress} # Bundle everthing 
    _write_data_file(path, data)
        
def record_stat(stats, n, ultra, play_time_ms): # Adds a finished match to the stats
    mode = "ultra" if ultra else "normal" # Which sub category
    size_entry = stats.setdefault(str(n), {"normal": {"games": 0, "best": None, "total": 0}, "ultra": {"games": 0, "best": None, "total": 0}}) # the default values
    entry = size_entry[mode] # Get the right mode entry
    entry["games"] += 1 # One more game played
    entry["total"] += play_time_ms # Add the time for the average
    if entry["best"] is None or play_time_ms < entry["best"]: # If the first or best game
        entry["best"] = play_time_ms # Save the game as best
    return stats # Give the updated stats back