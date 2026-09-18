"""Generate the francais.smati translation file."""
# This translation was part tested and created in coperation between Human and AI.

import base64
import json
import sys
import zlib
from pathlib import Path

# Obfuscation key - must stay in sync with config.XOR_KEY (see persistence.py).
XOR_KEY: bytes = b"Mati_Obfuscation_Key_2026"

translations = {
    "settings_title": "Paramètres",
    "advanced_settings_title": "Paramètres avancés",
    "back": "Retour",
    "volume": "Volume",
    "ter_sound_on": "Sons du terminal: Oui",
    "ter_sound_off": "Sons du terminal: Non",
    "save_played": "Sauvegarde parties: ",
    "on": "Oui",
    "off": "Non",
    "sound": "Son de jeu: ",
    "alt_control": "Mode clavier: ",
    "show_timer": "Temps de jeu: ",
    "milliseconds": "avec millisecondes : ",
    "fullscreen": "Plein écran: ",
    "live_clock": "Heure: ",
    "ultra_timer": "Temps du jeu Ultra: ",
    "ultra_ms": "Millisecondes Ultra: ",
    "ultra_clock": "Horloge du terminal: ",
    "game_volume": "Volume de jeu",
    "terminal_volume": "Volume de terminal",
    "language": "Langue",
    "u_ter_in_ord": "Ordre de saisie du terminal Ultra",
    "keybindings": "Raccourcis",
    "key_press": "Appuyez sur une touche",
    "about_1": "À propos de Mati",
    "about_2": "Mati est un algorithme. Et vraiment un algorithme cool.",
    "about_3": "Il génère le plateau interne et sélectionne des cases au hasard.",
    "about_4": "Les cases sélectionnées sont additionnées et les sommes sont notées.",
    "about_5": "Créé par :",
    "size": "Taille",
    "mode": "Mode",
    "games": "Victoires",
    "best": "Meilleur temps",
    "average": "Temps moyen",
    "achievements": "Succès",
    "unlocked": " déverrouillé",
    "unlocked_overall": "déverrouillés au total",
    "nothing_achieved": "Rien de terminé pour l'instant.",
    "page": "Page",
    "delete_match": "Supprimer la partie ?",
    "under_1": "Êtes-vous sûr de vouloir vraiment",
    "under_2": "supprimer définitivement cette partie de votre historique ?",
    "delete": "Supprimer",
    "cancel": "Annuler",
    "menu": "Menu",
    "no_history_entries": "Aucune partie enregistrée, du moins pour l'instant.",
    "all": "Toutes",
    "no_matches": "Aucune de vos parties ne correspond aux filtres actifs.",
    "mati": "Mati",
    "intro_text": "Réflexion mathématique et tactique",
    "settings": "Paramètres",
    "history": "Historique",
    "quit": "Quitter",
    "gameplay": "Mécanique de jeu",
    "timer": "Temps de jeu",
    "ultra_mode": "Mode Ultra",
    "display": "Affichage",
    "stats": "Statistiques",
    "about": "À propos",
    "fullscreen_info": "Appuyez sur F11 pour changer de mode ou sur Échap pour quitter le plein écran.",
    "ultra": "ULTRA",
    "ultra_1": "Ultra",
    "normal": "Normal",
    "time": "Temps de jeu: ",
    "hints": "Nb. l'aide: ",
    "action_start": "Action: Début",
    "action": "Action: ",
    "row": " (Ligne: ",
    "column": " / Colonne: ",
    "end": "Fin de la partie",
    "export": "Exporter en MP4",
    "show_end": "Afficher le résultat",
    "start": "Démarrer",
    "action_found": "Aucune action trouvée",
    "continue": "Continuer",
    "new": "Nouveau",
    "undo": "Annuler",
    "hint": "Indice ",
    "won": "Vous avez gagné",
    "paused": "En pause",
    "pressing": "Appuyez sur ",
    "contin": " ou sur <<Continuer>> pour reprendre",
    "unfinished": "Parties en pause trouvées",
    "ask_return": "Voulez-vous reprendre ou commencer une nouvelle partie?",
    "new_game": "Nouvelle partie",
    "resume": "Reprendre",
    "break": "Pause",
    "histo": "Historique",
    "Easy": "Facile",
    "Advanced": "Avancé",
    "Hard": "Difficile",
    "Expert": "Expert",
    "Select": "Sélectionné",
    "Mark": "Marqué",
    "Hint": "Indice",
    "Undone": "Annulé",
    "hannah_com": "Hannah - Message complété",
    "hannah_fou": "Hannah - Message trouvé",
    "Column, Row, Action": "Colonne, Ligne, Action",
    "Row, Column, Action": "Ligne, Colonne, Action",
    "Action, Row, Column": "Action, Ligne, Colonne",
    "Action, Column, Row": "Action, Colonne, Ligne",
    "Back to Menu": "Retour au menu",
    "New Round": "Nouvelle manche",
    "Toggle Fullscreen": "Plein écran",
    "Use Hint": "Indice",
    "Undo": "Annuler",
    "Pause": "Pause",
    "Right-Click Cell": "Marquer la case",
    "Standard": "Standard",
    "Ultra": "Ultra",
    "High": "Élevé",
    "Highest": "Maximum",
    "milestones_reached": "Jalons atteints",
    "left": "Restant",
    "hover_to_browse": "Survolez pour parcourir",
    "scroll_to_browse": "Faites défiler pour parcourir",
    "games_played": "Parties jouées",
    "total_playtime": "Temps de jeu total",
    "ultra_l": "Ultra",
    "display_scale": "Échelle d'affichage",
    "render_quality": "Qualité de rendu",
    "export_again": "Exporter à nouveau",
    "exporting": "Exportation en MP4 ...",
    "export_bg_hint": "Cliquez n'importe où pour continuer en arrière-plan",
    "exporting_short": "Exportation ",
    "export_done": "Exportation terminée",
    "export_exists": "Cette vidéo a déjà été exportée.",
    "exported_at": "Exportée",
    "export_format": "Format",
    "export_quality": "Qualité",
    "export_resolution": "Résolution",
    "tutorial_title": "Aide rapide",
    "tutorial_overview_sub": "Bref aperçu des fonctions principales du jeu",
    "tutorial_overview_line_165": "Voici la version courte du tutoriel :",
    "tutorial_overview_line_221": "Menu : les flèches déplacent le focus, Espace / Entrée valident.",
    "tutorial_overview_line_249": "Règles : sélectionnez les cases dont la somme atteint chaque ligne et",
    "tutorial_overview_line_277": "  colonne ; marquez les autres et gagnez quand tout est correct.",
    "tutorial_overview_line_305": "Historique : parties enregistrées, les plus récentes en premier.",
    "tutorial_overview_line_333": "Détails : cliquez sur une entrée pour parcourir la partie.",
    "tutorial_overview_line_361": "Terminal : appuyez sur Ctrl+T dans le menu, puis tapez 'help'.",
    "tutorial_overview_line_389": "Paramètres : activez les options de base, Ctrl+Droite ouvre les options avancées.",
    "tutorial_overview_line_417": "Succès : les étapes secrètes sont suivies dans toutes les parties.",
    "tutorial_overview_line_445": "Indice / Terminal : le bouton Indice en jeu et Ctrl+T",
    "tutorial_overview_line_473": "  pour le terminal rapide (tapez 'help' pour les commandes).",
    "tutorial_overview_line_501": "Horloge : cliquez sur l'horloge en haut à droite",
    "tutorial_overview_line_529": "  pour rouvrir cet aperçu.",
    "tut_terminal_1": "Vous avez trouvé le terminal caché !",
    "tut_terminal_2": "Tapez 'help' pour voir toutes les commandes disponibles.",
    "tut_menu_title": "Bienvenue dans Mati !",
    "tut_menu_body": "Choisissez une taille de grille pour votre premier puzzle. « Facile » (4x4) est un bon début.",
    "tut_play_title": "Comment jouer",
    "tut_play_body": "Cliquez à gauche sur une case pour la sélectionner, à droite pour la marquer. Chaque ligne et colonne doit atteindre sa cible.",
    "tut_play2_title": "Continuez !",
    "tut_play2_body": "Bloqué ? Cliquez sur Indice pour un coup gratuit ou sur Annuler pour en retirer un.",
    "tut_win_title": "Vous avez réussi !",
    "tut_win_body": "Bien joué. Mati a aussi un secret : retournez au menu et cherchez-le.",
    "tut_terminal_hint_title": "Vous cherchez le secret ?",
    "tut_terminal_hint_body": "Essayez d'appuyer sur Ctrl+T dans le menu.",
    "tut_done_title": "Tutoriel terminé !",
    "tut_done_body": "Tout est prêt : explorez maintenant Mati par vous-même. Amusez-vous bien !",
    "Column, Row, Action": "Colonne, Ligne, Action",
    "Row, Column, Action": "Ligne, Colonne, Action",
    "Action, Column, Row": "Action, Colonne, Ligne",
    "Action, Row, Column": "Action, Ligne, Colonne",
    "Back to Menu": "Retour au menu",
    "New Round": "Nouvelle partie",
    "Toggle Fullscreen": "Basculer en plein écran",
    "Use Hint": "Utiliser un indice",
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
    output_path: Path = _base_dir() / "rsc" / "languages" / "francais.smati"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_encode(translations), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()