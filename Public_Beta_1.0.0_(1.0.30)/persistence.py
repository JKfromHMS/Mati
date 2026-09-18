"""Read and write the obfuscated ``.mati`` and ``.smati`` data files."""

import base64
import json
import zlib
from datetime import datetime as dt
from pathlib import Path
from typing import Any, TypeAlias

### Own ###
from config import (
    DEFAULT_ACHIEVEMENTS,
    DEFAULT_SETTINGS,
    DIFFICULTIES as DIFFS,
    EXPORT_HISTORY_FILE as EHF,
    HISTORY_DIR as HD,
    SETTINGS_FILE as SF,
    XOR_KEY,
)

# --- Type Aliases ---
Stats: TypeAlias = dict[str, Any]


def _ensure_history_dir() -> None:
    """Create the history directory if it does not exist yet."""
    HD.mkdir(parents=True, exist_ok=True)


def _resolve_path(filename: str | Path) -> Path:
    """Return the real path of a match file, resolving the legacy location."""
    new_path = HD / filename
    if new_path.exists():
        return new_path
    return Path(filename)


def _xor(raw: bytes) -> bytes:
    """XOR every byte of ``raw`` with a repeating key to obscure the data."""
    key = XOR_KEY
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))


def _encode(data: dict[str, Any]) -> str:
    """Serialize ``data`` into an obfuscated, storable text blob."""
    raw = json.dumps(data).encode("utf-8")
    compressed = zlib.compress(raw)
    scrambled = _xor(compressed)
    return base64.b64encode(scrambled).decode("ascii")


def _decode(blob: str) -> dict[str, Any]:
    """Turn an obfuscated text blob back into a Python dict."""
    scrambled = base64.b64decode(blob.encode("ascii"))
    compressed = _xor(scrambled)
    raw = zlib.decompress(compressed)
    return json.loads(raw.decode("utf-8"))


def _read_data_file(path: Path) -> dict[str, Any]:
    """Read a ``.mati``/``.smati`` file, falling back to plain JSON on failure."""
    content = path.read_text(encoding="utf-8")
    try:
        return _decode(content)
    except Exception:
        return json.loads(content)


def _write_data_file(path: Path, data: dict[str, Any]) -> None:
    """Write ``data`` to ``path`` as an obfuscated blob."""
    path.write_text(_encode(data), encoding="utf-8")


def save_match(
    grid: list[list[int]],
    row_sums: list[int],
    col_sums: list[int],
    user_sel: list[list[bool]],
    user_dimmed: list[list[bool]],
    play_time: int,
    actions: list[dict[str, Any]],
    hints_used: int,
    ultra: bool = False,
) -> str:
    """Save a finished or paused match and return its filename."""
    _ensure_history_dir()
    filename = f"{dt.now().strftime('%Y-%m-%d_%H-%M-%S.%f')}.mati"
    data = {
        "grid": grid,
        "row_sums": row_sums,
        "col_sums": col_sums,
        "user_sel": user_sel,
        "user_dimmed": user_dimmed,
        "play_time": play_time,
        "actions": actions,
        "hints_used": hints_used,
        "ultra": ultra,
    }
    _write_data_file(HD / filename, data)
    return filename


def list_history() -> list[str]:
    """List all saved match filenames, newest first."""
    _ensure_history_dir()
    new_files = sorted(HD.glob("*.mati"), reverse=True)
    legacy_files = sorted(Path(".").glob("*.mati"), reverse=True)
    
    # .name extracts just the filename (e.g., 'match.mati') from the Path object
    return [f.name for f in new_files] + [f.name for f in legacy_files]


def _label_for(filename: str) -> str:
    """Turn a match filename into a human readable timestamp label."""
    stem = filename.replace(".mati", "")
    for fmt in ("%Y-%m-%d_%H-%M-%S-%f", "%Y-%m-%d_%H-%M-%S.%f", "%Y-%m-%d_%H-%M-%S"):
        try:
            d = dt.strptime(stem, fmt)
            return d.strftime("%d.%m.%Y %H:%M:%S")
        except ValueError:
            continue
    return stem.replace("_", " ")


def list_history_meta() -> list[dict[str, Any]]:
    """List all saved matches together with their metadata."""
    entries: list[dict[str, Any]] = []
    for name in list_history():
        try:
            data = load_match(name)
        except (OSError, json.JSONDecodeError):
            continue
        entries.append({
            "filename": name,
            "label": _label_for(name),
            "size": len(data.get("grid", [])),
            "play_time": data.get("play_time", 0),
            "hints_used": data.get("hints_used", 0),
            "ultra": data.get("ultra"),
        })
    return entries


def load_match(filename: str) -> dict[str, Any]:
    """Load and return the data of a saved match."""
    return _read_data_file(_resolve_path(filename))


def delete_match(filename: str) -> None:
    """Delete a match file from storage if it exists."""
    path = _resolve_path(filename)
    if path.exists():
        path.unlink()


def _settings_path() -> Path:
    """Return the path where the settings file currently lives."""
    return HD / SF.name if isinstance(SF, Path) else HD / SF


def _legacy_settings_path() -> Path:
    """Return the legacy, repo-root settings path."""
    return Path(SF)


def _default_stats() -> dict[str, Any]:
    """Build an empty statistics structure for every grid size."""
    return {
        str(n): {
            "normal": {"games": 0, "best": None, "total": 0},
            "ultra": {"games": 0, "best": None, "total": 0},
        }
        for n in DIFFS
    }


def load_settings_and_stats() -> tuple[dict[str, Any], Stats, dict[str, Any], list[Any], dict[str, Any]]:
    """Load settings, stats, paused games, Hannah progress and achievements."""
    _ensure_history_dir()
    path = _settings_path()
    
    if not path.exists() and _legacy_settings_path().exists():
        path = _legacy_settings_path()
        
    if not path.exists():
        return dict(DEFAULT_SETTINGS), _default_stats(), {}, [], dict(DEFAULT_ACHIEVEMENTS)
        
    try:
        data = _read_data_file(path)
    except (OSError, json.JSONDecodeError, zlib.error, ValueError):
        return dict(DEFAULT_SETTINGS), _default_stats(), {}, [], dict(DEFAULT_ACHIEVEMENTS)
        
    settings = {**DEFAULT_SETTINGS, **data.get("settings", {})}
    stats = data.get("stats", {})
    for n in DIFFS:
        stats.setdefault(str(n), {
            "normal": {"games": 0, "best": None, "total": 0},
            "ultra": {"games": 0, "best": None, "total": 0},
        })
    paused = data.get("paused", {})
    hannah = data.get("hannah", [])
    achievements = {**DEFAULT_ACHIEVEMENTS, **data.get("achievements", {})}
    return settings, stats, paused, hannah, achievements


def save_settings_and_stats(
    settings: dict[str, Any],
    stats: dict[str, Any],
    paused: dict[str, Any],
    hannah: list[Any] | None = None,
    achievements: dict[str, Any] | None = None,
) -> None:
    """Persist settings, stats, paused games, Hannah progress and achievements.

    The Hannah progress and achievements are only written when provided;
    otherwise the existing values are carried over from the current file so
    that a save from code that does not track them does not erase them.
    """
    _ensure_history_dir()
    path = _settings_path()
    legacy_path = _legacy_settings_path()
    
    existing_path = path if path.exists() else (legacy_path if legacy_path.exists() else None)
    
    if hannah is None or achievements is None:
        old_hannah: list[Any] = []
        old_achievements = dict(DEFAULT_ACHIEVEMENTS)
        if existing_path:
            try:
                old = _read_data_file(existing_path)
                old_hannah = old.get("hannah", [])
                old_achievements = {**DEFAULT_ACHIEVEMENTS, **old.get("achievements", {})}
            except (OSError, json.JSONDecodeError, zlib.error, ValueError):
                pass
                
        if hannah is None:
            hannah = old_hannah
        if achievements is None:
            achievements = old_achievements

    data = {
        "settings": settings,
        "stats": stats,
        "paused": paused,
        "hannah": hannah,
        "achievements": achievements,
    }
    _write_data_file(path, data)


def record_stat(stats: dict[str, Any], n: int, ultra: bool, play_time_ms: int) -> dict[str, Any]:
    """Register a finished match in the statistics and return the updated stats."""
    mode = "ultra" if ultra else "normal"
    size_entry = stats.setdefault(str(n), {
        "normal": {"games": 0, "best": None, "total": 0},
        "ultra": {"games": 0, "best": None, "total": 0},
    })
    entry = size_entry[mode]
    entry["games"] += 1
    entry["total"] += play_time_ms
    if entry["best"] is None or play_time_ms < entry["best"]:
        entry["best"] = play_time_ms
    return stats


# --- Export history (dedicated, unencrypted .smati file) ---

def _read_export_history() -> dict[str, Any]:
    """Load the export history from its dedicated, unencrypted ``.smati`` file."""
    if not EHF.exists():
        return {}
    try:
        data = _read_data_file(EHF)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, zlib.error, ValueError):
        return {}


def _write_export_history(history: dict[str, Any]) -> None:
    """Persist the export history as plain (unencrypted) JSON."""
    _ensure_history_dir()
    EHF.write_text(json.dumps(history, indent=2), encoding="utf-8")


def get_export_entry(match_name: str | None) -> dict[str, Any] | None:
    """Return the stored export info of a match file, or ``None``."""
    if not match_name:
        return None
    return _read_export_history().get(match_name)


def record_export(match_name: str, entry: dict[str, Any]) -> None:
    """Store/refresh the export info of a successfully finished export."""
    history = _read_export_history()
    history[match_name] = entry
    _write_export_history(history)