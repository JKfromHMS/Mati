"""Generate the espanol.smati translation file."""
# This translation was part tested and created in coperation between Human and AI.

import base64
import json
import sys
import zlib
from pathlib import Path

# Obfuscation key - must stay in sync with config.XOR_KEY (see persistence.py).
XOR_KEY: bytes = b"Mati_Obfuscation_Key_2026"

translations = {
    "settings_title": "Ajustes",
    "advanced_settings_title": "Ajustes avanzados",
    "back": "Atrás",
    "volume": "Volumen",
    "ter_sound_on": "Sonidos terminal: Sí",
    "ter_sound_off": "Sonidos terminal: No",
    "save_played": "Guardar partidas: ",
    "on": "Sí",
    "off": "No",
    "sound": "Sonido del juego: ",
    "alt_control": "Modo teclado: ",
    "show_timer": "Mostrar tiempo: ",
    "milliseconds": "con milisegundos: ",
    "fullscreen": "Pantalla completa: ",
    "live_clock": "Hora: ",
    "ultra_timer": "Tiempo Ultra: ",
    "ultra_ms": "Milisegundos Ultra: ",
    "ultra_clock": "Hora terminal: ",
    "game_volume": "Volumen del juego",
    "terminal_volume": "Volumen terminal",
    "language": "Idioma",
    "u_ter_in_ord": "Orden de entrada del terminal Ultra",
    "keybindings": "Atajos",
    "key_press": "Pulsa una tecla",
    "about_1": "Sobre Mati",
    "about_2": "Mati es un algoritmo. Y uno realmente genial.",
    "about_3": "Genera el tablero interno y elige casillas al azar.",
    "about_4": "Las casillas elegidas se suman y se anotan los resultados.",
    "about_5": "Creado por:",
    "size": "Tamaño",
    "mode": "Modo",
    "games": "Victorias",
    "best": "Mejor tiempo",
    "average": "Tiempo medio",
    "achievements": "Logros",
    "unlocked": " desbloqueado",
    "unlocked_overall": " desbloqueados en total",
    "nothing_achieved": "Aún no has completado nada.",
    "page": "Página",
    "delete_match": "¿Borrar partida?",
    "under_1": "¿Seguro que quieres borrar esta partida",
    "under_2": "permanentemente de tu historial?",
    "delete": "Borrar",
    "cancel": "Cancelar",
    "menu": "Menú",
    "no_history_entries": "No hay partidas guardadas, al menos por ahora.",
    "all": "Todas",
    "no_matches": "Ninguna partida coincide con tus filtros activos.",
    "mati": "Mati",
    "intro_text": "Pensamiento matemático y táctico",
    "settings": "Ajustes",
    "history": "Historial",
    "quit": "Salir",
    "gameplay": "Mecánica de juego",
    "timer": "Tiempo de juego",
    "ultra_mode": "Modo Ultra",
    "display": "Pantalla",
    "stats": "Estadísticas",
    "about": "Sobre",
    "fullscreen_info": "Pulsa F11 para cambiar o ESC para salir del modo de pantalla completa.",
    "ultra": "ULTRA",
    "ultra_1": "Ultra",
    "normal": "Normal",
    "time": "Tiempo: ",
    "hints": "Asistencia: ",
    "action_start": "Acción: Inicio",
    "action": "Acción: ",
    "row": " (Fila: ",
    "column": " / Columna: ",
    "end": "Fin de la partida",
    "export": "Exportar como MP4",
    "show_end": "Mostrar resultado",
    "start": "Inicio",
    "action_found": "No se encontraron acciones",
    "continue": "Continuar",
    "new": "Nuevo",
    "undo": "Deshacer",
    "hint": "Pista ",
    "won": "Has ganado",
    "paused": "En pausa",
    "pressing": "Pulsa ",
    "contin": " o <<Continuar>> para seguir jugando",
    "unfinished": "Partidas pausadas encontradas",
    "ask_return": "¿Quieres continuar o iniciar una partida nueva?",
    "new_game": "Nueva partida",
    "resume": "Continuar",
    "break": "Pausa",
    "histo": "Historial",
    "Easy": "Fácil",
    "Advanced": "Avanzado",
    "Hard": "Difícil",
    "Expert": "Experto",
    "Select": "Seleccionado",
    "Mark": "Marcado",
    "Hint": "Pista",
    "Undone": "Deshecho",
    "hannah_com": "Hannah - Mensaje completado",
    "hannah_fou": "Hannah - Mensaje encontrado",
    "Column, Row, Action": "Columna, Fila, Acción",
    "Row, Column, Action": "Fila, Columna, Acción",
    "Action, Row, Column": "Acción, Fila, Columna",
    "Action, Column, Row": "Acción, Columna, Fila",
    "Back to Menu": "Volver al menú",
    "New Round": "Nueva ronda",
    "Toggle Fullscreen": "Pantalla completa",
    "Use Hint": "Pista",
    "Undo": "Deshacer",
    "Pause": "Pausa",
    "Right-Click Cell": "Marcar casilla",
    "Standard": "Estándar",
    "High": "Alto",
    "Ultra": "Ultra",
    "Highest": "Máximo",
    "milestones_reached": "Hitos logrados",
    "left": "Restante",
    "hover_to_browse": "Pasa el cursor para explorar",
    "scroll_to_browse": "Desplázate para explorar",
    "games_played": "Partidas jugadas",
    "total_playtime": "Tiempo total de juego",
    "ultra_l": "Ultra",
    "display_scale": "Escala de pantalla",
    "render_quality": "Calidad",
    "export_again": "Exportar de nuevo",
    "exporting": "Exportando a MP4 ...",
    "export_bg_hint": "Haz clic en cualquier lugar para continuar en segundo plano",
    "exporting_short": "Exportando ",
    "export_done": "Exportación terminada",
    "export_exists": "Este vídeo ya se ha exportado.",
    "exported_at": "Exportado",
    "export_format": "Formato",
    "export_quality": "Calidad",
    "export_resolution": "Resolución",
    "tutorial_title": "Ayuda rápida",
    "tutorial_overview_sub": "Resumen breve de las funciones principales del juego",
    "tutorial_overview_line_165": "Esta es la versión corta del tutorial:",
    "tutorial_overview_line_221": "Menú: las flechas mueven el foco, Espacio / Intro confirman.",
    "tutorial_overview_line_249": "Reglas: selecciona las casillas cuya suma complete cada fila y",
    "tutorial_overview_line_277": "  columna; marca el resto y gana cuando todo esté correcto.",
    "tutorial_overview_line_305": "Historial: partidas guardadas, las más recientes primero.",
    "tutorial_overview_line_333": "Detalles: haz clic en una entrada para recorrer la partida.",
    "tutorial_overview_line_361": "Terminal: pulsa Ctrl+T en el menú y escribe 'help'.",
    "tutorial_overview_line_389": "Ajustes: cambia las opciones básicas; Ctrl+Derecha abre las avanzadas.",
    "tutorial_overview_line_417": "Logros: los hitos ocultos se siguen en todas las partidas.",
    "tutorial_overview_line_445": "Pista / Terminal: el botón Pista durante la partida y Ctrl+T",
    "tutorial_overview_line_473": "  para el terminal rápido (escribe 'help' para ver los comandos).",
    "tutorial_overview_line_501": "Reloj: haz clic en el reloj de arriba a la derecha",
    "tutorial_overview_line_529": "  para abrir este resumen otra vez.",
    "tut_terminal_1": "¡Has encontrado el terminal oculto!",
    "tut_terminal_2": "Escribe 'help' para ver todos los comandos disponibles.",
    "tut_menu_title": "¡Bienvenido a Mati!",
    "tut_menu_body": "Elige abajo el tamaño de la cuadrícula para tu primer rompecabezas. 'Fácil' (4x4) es un buen comienzo.",
    "tut_play_title": "Cómo jugar",
    "tut_play_body": "Haz clic izquierdo en una casilla para seleccionarla y derecho para marcarla. Cada fila y columna debe alcanzar su objetivo.",
    "tut_play2_title": "¡Sigue así!",
    "tut_play2_body": "¿Atascado? Pulsa Pista para obtener un movimiento gratis o Deshacer para retirar uno.",
    "tut_win_title": "¡Lo has resuelto!",
    "tut_win_body": "Bien hecho. Mati también tiene un secreto: vuelve al menú y búscalo.",
    "tut_terminal_hint_title": "¿Buscas el secreto?",
    "tut_terminal_hint_body": "Prueba a pulsar Ctrl+T en el menú.",
    "tut_done_title": "¡Tutorial completado!",
    "tut_done_body": "Ya estás listo: explora Mati por tu cuenta. ¡Diviértete!",
    "Column, Row, Action": "Columna, Fila, Acción",
    "Row, Column, Action": "Fila, Columna, Acción",
    "Action, Column, Row": "Acción, Columna, Fila",
    "Action, Row, Column": "Acción, Fila, Columna",
    "Back to Menu": "Volver al menú",
    "New Round": "Nueva partida",
    #"Toggle Fullscreen": "Alternar pantalla completa",
    "Use Hint": "Usar pista",
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
    output_path: Path = _base_dir() / "rsc" / "languages" / "espanol.smati"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_encode(translations), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()