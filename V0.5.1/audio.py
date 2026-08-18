### Mati (Mathematics and tactic intelligence) ###
### V0.5.1 Beta V1.0.20 ###
### Author: Janosch Klawatsch, 18.08.2026 ###
### audio file V0.5.1 ###

### Structure-Plan ###
# - audio.py - Sound generation #
# - config.py - Constants #
# - export.py - video creating and saving #
# - game.py - The main game handling #
# - level.py - Generate Levels, Check Wins ... #
# - main.py - Entry point and main loop #
# - persistence.py - Save and load of .mati files #
# - replay.py - Rebuild games #
# - screens.py - Building the screens #
# - terminal.py - The Terminal #
# - widgets.py - Draw-Functions #

### -Imports- ###
### External ###
from array import array   # To get the posibility to have and handle arrays
from math import sin, pi  # To get and have mathematic operations like pi and the sinus
import pygame as pg       # Something like the engine on which the game runs

### Own ###
from config import SAMPLE_RATE as SR

### -Functions- ###
def _make_tone(freq: float, duration_ms: float, volume: float = 0.3):
    n_samples = int(SR * duration_ms / 1000) # Number of samples per second
    amplitude = int(32767 * volume)
    buffer = array("h")
    for i in range(n_samples):
        t = i / SR # Calculate the start point of every sample
        fade = 1.0 - (i / n_samples) * 0.1 # To generate a fade in and fade out to avoid unwanted sounds at the start or end
        sample = sin(2 * pi * freq * t)
        value = int(sample * amplitude * fade)
        buffer.extend((value, value)) # To get stereo audio
    return pg.mixer.Sound(buffer=buffer)


def _make_jingle(notes: list[float], note_ms: float = 90, volume: float = 0.3):
    n_samples = int(SR * note_ms / 1000) # Number of samples per second
    amplitude = int(32767 * volume)
    buffer = array("h")
    for freq in notes:
        for i in range(n_samples):
            t = i / SR # Calculate the start point of every sample
            fade = 1.0 - (i / n_samples) * 0.3 # To generate a fade in and fade out to avoid unwanted sounds at the start or end
            sample = sin(2 * pi * freq * t)
            value = int(sample * amplitude * fade)
            buffer.extend((value, value)) # To get stereo audio
    return pg.mixer.Sound(buffer=buffer)


class Sounds:
    def __init__(self):
        self.enabled = True
        self.available = False
        
        try:
            pg.mixer.init(frequency=SR, size=-16, channels=2)
            self.click = _make_tone(440, 60, 0.25)
            self.dim = _make_tone(300, 55, 0.2)
            self.hint = _make_tone(700, 120, 0.28)
            self.undo = _make_tone(250, 80, 0.2)
            
            self.tip = _make_tone(400, 50, 0.1)
            self.sub = _make_tone(370, 130, 0.14)
            
            self.win = _make_jingle([523, 659, 784, 1046])
            self.available = True
            
        except Exception: # If any failure happend
            self.available = False
            
    
    def play(self, sound):
        if self.available and self.enabled and sound is not None:
            sound.play()