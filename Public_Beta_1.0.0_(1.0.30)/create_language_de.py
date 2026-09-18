"""Generate the deutsch.smati translation file."""
# This translation was part tested and created in coperation between Human and AI.

import base64
import json
import sys
import zlib
from pathlib import Path

# Obfuscation key - must stay in sync with config.XOR_KEY (see persistence.py).
XOR_KEY: bytes = b"Mati_Obfuscation_Key_2026"

translations = {
    "settings_title": "Einstellungen",
    "advanced_settings_title": "Erweiterte Einstellungen",
    "back": "Zurück",
    "volume": "Lautstärke",
    "ter_sound_on": "Terminal Sounds: An",
    "ter_sound_off": "Terminal Sounds: Aus",
    "save_played": "Spiele sichern: ",
    "on": "An",
    "off": "Aus",
    "sound": "Spiel-Ton: ",
    "alt_control": "Tastatur Modus: ",
    "show_timer": "Spielzeit anzeigen: ",
    "milliseconds": "mit Millisekunden: ",
    "fullscreen": "Vollbild: ",
    "live_clock": "Uhrzeit: ",
    "ultra_timer": "Ultra Spielzeit:",
    "ultra_ms": "Ultra Millisekunden: ",
    "ultra_clock": "Terminal Uhr: ",
    "game_volume": "Spiel Lautstärke",
    "terminal_volume": "Terminal Lautstärke",
    "language": "Sprache",
    "u_ter_in_ord": "Ultra Terminal Eingabereihenfolge",
    "keybindings": "Verknüpfungen",
    "key_press": "Drücke eine Taste",
    "about_1": "Über Mati",
    "about_2": "Mati ist ein Algorithmus. Ein wirklich cooler.",
    "about_3": "Er generiert das innere Spielfeld und wählt zufällig Felder aus.",
    "about_4": "Die ausgewählten Felder werden addiert und die Summen werden notiert.",
    "about_5": "Erstellt von:",
    "size": "Größe",
    "mode": "Modus",
    "games": "Siegzahl",
    "best": "Schnellste Runde",
    "average": "Durchschnittliche Zeit",
    "achievements": "Erfolge",
    "unlocked": " freigeschaltet",
    "unlocked_overall": " insgesamt freigeschaltet",
    "nothing_achieved": "Noch nichts abgeschlossen.",
    "page": "Seite",
    "delete_match": "Partie löschen?",
    "under_1": "Bist du dir sicher, dass du wirklich diese Partie",
    "under_2": "dauerhaft aus deiner Historie löschen möchtest?",
    "delete": "Löschen",
    "cancel": "Abbrechen",
    "menu": "Menü",
    "no_history_entries": "Keine Spiele gespeichert, zumindest bis jetzt.",
    "all": "Alle",
    "no_matches": "Keine deiner Partien entspricht deinen aktiven Filtern.",
    "mati": "Mati",
    "intro_text": "Mathematisches und taktisches Denken",
    "settings": "Einstellungen",
    "history": "Historie",
    "quit": "Beenden",
    "gameplay": "Spielmechanik",
    "timer": "Spielzeit",
    "ultra_mode": "Ultra Modus",
    "display": "Anzeige",
    "stats": "Statistiken",
    "about": "Über",
    "fullscreen_info": "Drücke F11 zum Wechseln oder ESC zum Beenden des Vollbild-Modus.",
    "ultra": "ULTRA",
    "ultra_1": "Ultra",
    "normal": "Normal",
    "hints": "Hilfe verw.: ",
    "action_start": "Aktion: Start",
    "action": "Aktion: ",
    "row": " (Reihe: ",
    "column": " / Spalte: ",
    "end": "Ende des Spiels",
    "export": "Als MP4 exportieren",
    "show_end": "Endstand zeigen",
    "start": "Start",
    "action_found": "Keine Aktionen gefunden",
    "continue": "Weiter",
    "new": "Neu",
    "undo": "Rückgängig",
    "hint": "Hinweis ",
    "time": "Spielzeit: ",
    "won": "Du hast gewonnen",
    "paused": "Pausiert",
    "pressing": "Drücke ",
    "contin": " oder <<Weiter>> zum weiterspielen",
    "unfinished": "Pausierte Spiele gefunden",
    "ask_return": "Möchtest du weiterspielen oder ein neues Spiel starten?",
    "new_game": "Neues Spiel",
    "resume": "Weiter spielen",
    "break": "Pause",
    "histo": "Historie",
    "Easy": "Einfach",
    "Advanced": "Fortgeschritten",
    "Hard": "Kompliziert",
    "Expert": "Experte",
    "Select": "Ausgewählt",
    "Mark": "Markiert",
    "Hint": "Hinweis",
    "Undone": "Zurückgenommen",
    "hannah_com": "Hannah - Nachricht vervollständigt",
    "hannah_fou": "Hannah - Nachricht gefunden",
    "Column, Row, Action": "Spalte, Reihe, Aktion",
    "Row, Column, Action": "Reihe, Spalte, Aktion",
    "Action, Column, Row": "Aktion, Spalte, Reihe",
    "Action, Row, Column": "Aktion, Reihe, Spalte",
    "Back to Menu": "Zurück ins Menü",
    "New Round": "Neue Runde",
    "Toggle Fullscreen": "Vollbildmodus",
    "Use Hint": "Hinweis",
    "Undo": "Rückgängig",
    "Pause": "Pause",
    "Right-Click Cell": "Feld markieren",
    "Standard": "Standard",
    "High": "Hoch",
    "Ultra": "Ultra",
    "Highest": "Höchstes",
    "milestones_reached": "Vervollständigt!",
    "left": "übrig", # sence of missing
    "hover_to_browse": "Zum Durchsuchen hovern",
    "scroll_to_browse": "Zum Durchsuchen scrollen",
    "games_played": "Spiele gespielt",
    "total_playtime": "Spielzeit",
    "ultra_l": "Ultra",
    "display_scale": "Anzeigegröße",
    "render_quality": "Qualität",
    "export_again": "Erneut exportieren",
    "exporting": "Export als MP4 ...",
    "export_bg_hint": "Klicke irgendwo, um im Hintergrund weiterzuspielen",
    "exporting_short": "Export läuft ",
    "export_done": "Export abgeschlossen",
    "export_exists": "Dieses Video wurde bereits exportiert.",
    "exported_at": "Exportiert",
    "export_format": "Format",
    "export_quality": "Qualität",
    "export_resolution": "Auflösung",
    "tutorial_title": "Kurzhilfe",
    "tutorial_overview_sub": "Kurzer Überblick über die wichtigsten Spielfunktionen",
    "tutorial_overview_line_165": "Hier ist die Kurzfassung der Anleitung:",
    "tutorial_overview_line_221": "Menü: Pfeile bewegen den Fokus, Leertaste / Enter bestätigen.",
    "tutorial_overview_line_249": "Regeln: Wähle die Felder, deren Summe jede Zeile und",
    "tutorial_overview_line_277": "  Spalte ergibt; markiere den Rest - gewinne, wenn alles stimmt.",
    "tutorial_overview_line_305": "Historie: Gespeicherte Partien, standardmäßig die neuesten zuerst.",
    "tutorial_overview_line_333": "Details: Klicke auf einen Eintrag, um die Partie durchzugehen.",
    "tutorial_overview_line_361": "Terminal: Drücke Strg+T im Menü und gib 'help' ein.",
    "tutorial_overview_line_389": "Einstellungen: Grundlagen umschalten, Strg+Rechts öffnet die erweiterten.",
    "tutorial_overview_line_417": "Erfolge: Versteckte Meilensteine werden über alle Partien verfolgt.",
    "tutorial_overview_line_445": "Hinweis / Terminal: Hinweis-Schaltfläche im Spiel und Strg+T",
    "tutorial_overview_line_473": "  für das Schnellzugriffs-Terminal (für Befehle 'help' eingeben).",
    "tutorial_overview_line_501": "Uhr: Klicke oben rechts auf die Uhr,",
    "tutorial_overview_line_529": "  um diese Übersicht erneut zu öffnen.",
    "tut_terminal_1": "Du hast das versteckte Terminal gefunden!",
    "tut_terminal_2": "Gib 'help' ein, um alle verfügbaren Befehle zu sehen.",
    "tut_menu_title": "Willkommen bei Mati!",
    "tut_menu_body": "Wähle unten eine Spielfeldgröße für dein erstes Rätsel. 'Einfach' (4x4) ist ein guter Einstieg.",
    "tut_play_title": "So wird gespielt",
    "tut_play_body": "Klicke links auf ein Feld, rechts, um es zu markieren. Jede Zeile und Spalte muss ihre Zielsumme erreichen.",
    "tut_play2_title": "Weiter so!",
    "tut_play2_body": "Du kommst nicht weiter? Klicke auf Hinweis für einen kostenlosen Zug oder Rückgängig, um einen zurückzunehmen.",
    "tut_win_title": "Du hast es gelöst!",
    "tut_win_body": "Gut gemacht. Mati hat auch ein Geheimnis - kehre ins Menü zurück und suche danach.",
    "tut_terminal_hint_title": "Suchst du das Geheimnis?",
    "tut_terminal_hint_body": "Drücke im Menü Strg+T.",
    "tut_done_title": "Anleitung abgeschlossen!",
    "tut_done_body": "Du bist startklar - entdecke Mati jetzt selbst. Viel Spaß!",
    "Column, Row, Action": "Spalte, Zeile, Aktion",
    "Row, Column, Action": "Zeile, Spalte, Aktion",
    "Action, Column, Row": "Aktion, Spalte, Zeile",
    "Action, Row, Column": "Aktion, Zeile, Spalte",
    "Back to Menu": "Zurück zum Menü",
    "New Round": "Neue Runde",
    "Toggle Fullscreen": "Vollbild wechseln",
    "Use Hint": "Hinweis",
}


def _encode(data: dict[str, str]) -> str:
    """Serialize ``data`` into the obfuscated text blob Mati stores in ``.smati``."""
    raw = json.dumps(data).encode("utf-8")
    compressed = zlib.compress(raw)
    scrambled = bytes(b ^ XOR_KEY[i % len(XOR_KEY)] for i, b in enumerate(compressed))
    return base64.b64encode(scrambled).decode("ascii")


def _base_dir() -> Path:
    """Return the folder that ``rsc`` is expected next to.

    A frozen build (for example a PyInstaller ``.exe``) unpacks its own code into
    a temporary folder, so there the folder of the running executable is used.
    """
    if getattr(sys, "frozen", False) or "__compiled__" in globals():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def main() -> None:
    """Write the language pack into the ``rsc/languages`` folder next to the code."""
    output_path: Path = _base_dir() / "rsc" / "languages" / "deutsch.smati"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_encode(translations), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()