# Mati

**Mati** is a Sudoku-like puzzle game in which you can either practice your math skills or refresh your terminal gaming experience.

Current version: **V0.7.1.2 (Beta V1.0.30)**.

![Mati](MATI.jpg)

![Mati Gameplay](gameplay.gif)

---

## Try Mati

[Download-Page](https://github.com/JKfromHMS/Mati/releases)

To run the application on **Windows**, simply download and double-click MATI.exe.

### Operating System Support:
Please note that ready-to-run executables are currently **only available for Windows**. The game uses Windows-specific methods, so running it on other OS can cause visual glitches and issues.

If you are not able to test it on Windows but really want to, you need to build it manually. In this case please do not rate it bad for rendering and graphic issues.

### Language Settings:
To change the language ingame, run the corresponding language file first, launch the main file again, open advanced settings select it (click on current language will open a dropdown).

---

## Features

- **4 Grid sizes** from **4x4** up to **7x7**.
- **Keyboard Mode** to control the full game **without mouse or trackpad**.
- **History** to see your recent matchs.
- **MP4 video export** of completed matches with selectable quality and frame rate.
- **Sin-Wave Sound Effects** to give the game an audio touch without copyright issues.

Wanna see more features? -> They are in the features.md.

---

## Run is locally

### Prerequisites

- **Python 3.10+** — the code uses `match` statements and modern type annotations.
- **Pygame**, **NumPy**, and **PyAV (`av`)**.
- **tkinter** (included automatically if not on Linux)

### Run

From the folder containing `main.py`:

```bash
pip install pygame numpy av
python main.py
```

Language scripts like `create_language_de.py`, are not required to launch the game, but they cana be used to create a translation to select ingame.

---

## How It Works

### Level generation 

This is the **main algorithem** and works like this:

- creates a list of numbers
- selects a few at random
- sums all chosen numbers across each row and column.

### Sound

Because at my last years project had problems due copyright issues I decided to not want to get into trubble again, so Mati uses **Sin-Waves** to create every sound effect and even the background music.

---

## Credits

- **Pygame** — windowing, input, rendering, and mixer support.
- **NumPy** — numerical helpers used in audio and export paths.
- **PyAV (`av`)** — MP4 export encoding.
- **Python standard library**, including `tkinter` used for native file dialogs during save/export flows.
- **Author:** Janosch Klawatsch (Jay/JKfromHMS).

#### Translations & AI Disclosure

German, Spanish, and French language packs (English fallback) were generated using AI and online dictionaries, so minor translation or naming inconsistencies may occur.

AI was used strictly as an assistant: GitHub Copilot for code completion, and Google Gemini for debugging, translations, and brainstorming.

---

## License

Mati is distributed under the **PolyForm Noncommercial License 1.0.0**.

Required notice: **Copyright JKfromHMS (https://github.com/JKfromHMS/Mati)**.

See `LICENSE` in the repository root for the full terms.
