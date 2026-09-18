"""Translation loading and lookup for the .smati language files.

This module manages loading language data and providing a translation
interface for the application.
"""

### -Imports- ###
from pathlib import Path

import config as con
import persistence as ps

_translations: dict[str, str] = {}
_current: str = con.BUILTIN_LANGUAGE


def find_language_file(name: str) -> Path | None:
    """Return the ``.smati`` file of a language by searching every language folder.

    Args:
        name: Language code to look up (e.g., "deutsch").

    Returns:
        The path of the first matching file, or ``None`` if no folder contains one.
    """
    filename = f"{name}.smati"
    for folder in con.LANGUAGES_DIRS:
        candidate = folder / filename
        if candidate.is_file():
            return candidate
    return None


def load_language(name: str | None) -> None:
    """Load the translation table for a language, falling back to the built-in default.

    Args:
        name: Language code to load (e.g., "deutsch"). If None or the file is missing,
            it falls back to the built-in language.
    """
    global _translations, _current
    _current = (name or con.BUILTIN_LANGUAGE).lower()
    _translations = {}

    if _current == con.BUILTIN_LANGUAGE:
        return
        
    path = find_language_file(_current)
    if path is None:
        _current = con.BUILTIN_LANGUAGE
        return

    try:
        data = ps._read_data_file(path)
        if isinstance(data, dict):
            _translations = {str(k): str(v) for k, v in data.items()}
    except Exception:
        # Fallback to an empty translation dictionary on read/parse errors
        _translations = {}


def t(key: str, default: str) -> str:
    """Return the translated label for the given key, or the default if missing."""
    return _translations.get(key, default)


def current_language() -> str:
    """Return the currently active language code (e.g., "english")."""
    return _current