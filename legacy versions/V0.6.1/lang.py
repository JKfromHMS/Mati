### Mati (Mathematics and tactic intelligence) ###
### V0.6.1 (Beta V1.0.22) ###
### Author: Janosch Klawatsch, 2026-08-28 ###
### lang file V0.6.1 ###

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
import os   # For paths

### Own ###
import config as con     # For the language configurations
import persistence as ps # Reuse the same file read as normal

### -State- ###
_translations = {}
_current = con.BUILTIN_LANGUAGE

### -Functions- ###
def load_language(name):
    global _translations, _current
    _current = (name or con.BUILTIN_LANGUAGE).lower()
    _translations = {}
    
    if _current == con.BUILTIN_LANGUAGE:
        return
    path = os.path.join(con.LANGUAGES_DIR, f"{_current}.smati")
    if not os.path.exists(path):
        _current = con.BUILTIN_LANGUAGE
        return
    
    try:
        data = ps._read_data_file(path)
        if isinstance(data, dict):
            _translations = data
    except Exception:
        _translations = {}
        
def t(key, default):
    return _translations.get(key, default)

def current_language():
    return _current