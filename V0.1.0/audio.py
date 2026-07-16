### Mati (Mathematics and tactic intelligence) ###
### V0.1.0 Beta V1.0.10 ###
### Author: Janosch Klawatsch, 13.07.2026 ###
### audio file V0.0.1 ###

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

### -Imports- ###
### External ###
import array as ar  # To handle arrays
import math as ma   # To have mathematic operations like pi
import pygame as pg # Something like the engine on which the game runs.

### Own ###
from config import SAMPLE_RATE as SR

### -Functions- ###
def _make_tone(freq, duration_ms, volume=0.3): # Create a tone
    n_samples = int(SR * duration_ms / 1000) # Number of samples per second
    amplitude = int(32767 * volume) # Define the amplitude
    buf = ar.array("h") # Generate an array
    for i in range(n_samples): # For each sample
        t = i / SR # Calculate duration point of this sample
        fade = 1.0 - (i / n_samples) # Fade values
        sample = ma.sin(2 * ma.pi * freq * t) # Generate sample as sinus value
        value = int(sample * amplitude * fade) # Make it complete
        buf.append(value) # Left
        buf.append(value) # Right
    return pg.mixer.Sound(buffer=buf) # Really generate the tone

def _make_jingle(notes, note_ms=90, volume=0.3): # Gernate more tones to a jingle
    buf = ar.array("h") # Generate an array
    n_samples = int(SR * note_ms / 1000) # Number of samples per second
    amplitude = int(32767 * volume) # Define the amplitude
    for freq in notes: # For number of notes
        for i in range(n_samples): # For each sample
            t = i / SR # duration point
            fade = 1.0 - (i / n_samples) * 0.3 # Fade values
            sample = ma.sin(2 * ma.pi * freq * t) # Generate sinus sample
            value = int(sample * amplitude * fade) # Blueprint for the tone
            buf.append(value) # Left
            buf.append(value) # Right
    return pg.mixer.Sound(buffer=buf) # Generate the jingle

class Sounds: # Handle sound play
    def __init__(self): # Inititalize the class
        self.enabled = True # Be activated
        self.available = False # Need to check if audio can be played
        try: # If all possible do
            pg.mixer.init(frequency=SR, size=-16, channels=2) # Initialize the mixer
            self.click = _make_tone(440, 60, 0.25) # Click Sound
            self.dim = _make_tone(300, 55, 0.2)    # Right click sound
            self.hint = _make_tone(700, 120, 0.28) # Hint used sound
            self.undo = _make_tone(250, 80, 0.2)   # Undone sound
            
            self.win = _make_jingle([523, 659, 784, 1046]) # Jingle for win
            self.available = True # Give sounds is possible
        except Exception: # If not possible
            self.available = False # Can not give sounds
            
    def play(self, sound): # Gets a sound to play
        if self.available and self.enabled and sound is not None: # If it should, can and have something to play
            sound.play() # Let the sound play