### Mati (Mathematics and tactic intelligence) ###
### V0.6.1 (Beta V1.0.22) ###
### Author: Janosch Klawatsch, 2026-08-25 ###
### audio file V0.6.0 ###

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
from array import array   # For generating audio data
from math import sin, pi  # To get and have mathematic operations like pi and the sinus
import pygame as pg       # 'Game engine' and rendering framework

### Own ###
from config import SAMPLE_RATE as SR # Provides the programms 'Sample rate'


### -Functions- ###

def _make_tone(
    freq: float,
    duration_ms: float,
    volume: float = 0.3
) -> pg.mixer.Sound:
    """Create a stereo sine-wave tone with a short fade-out.
        
    Args:
        freq (float): Frequency of the tone in Hertz.
        duration_ms (float): Duration of the tone in milliseconds.
        volume (float): Volume of the tone, ranging from 0.0 to 1.0.
        
    Returns:
        pg.mixer.Sound: Pygame Sound object containing the generated tone.
    """
    n_samples = int(SR * duration_ms / 1000)
    amplitude = int(32767 * volume)
    buffer = array("h")
    
    for i in range(n_samples):
        t = i / SR
        fade = 1.0 - (i / n_samples) * 0.1
        sample = sin(2 * pi * freq * t)
        value = int(sample * amplitude * fade)
        
        # Add the same sample to both channels for stereo output.
        buffer.extend((value, value))
        
    return pg.mixer.Sound(buffer=buffer)


def _make_jingle(
    notes: list[float],
    note_ms: float = 90,
    volume: float = 0.3
) -> pg.mixer.Sound:
    """Creates a stereo jingle consisting of multiple sine-wave notes.
    
    Each freqency in the notes list is played sequentially for the specified
    duration. A short fade-out is applied to each note to reduce unwanted
    sounds at the transitions between notes.

    Args:
        notes (list[float]): List of frequencies in Hertz for the individual
            notes. 
        note_ms (float, optional): Duration of each note in milliseconds. 
            Defaults to 90.
        volume (float, optional): Volume of the jingle, ranging from 0.0 to 1.0.
            Defaults to 0.3.

    Returns:
        pg.mixer.Sound: Pygame Sound object containing the generated jingle.
    """
    n_samples = int(SR * note_ms / 1000)
    amplitude = int(32767 * volume)
    buffer = array("h")
    
    for freq in notes:
        for i in range(n_samples):
            t = i / SR
            fade = 1.0 - (i / n_samples) * 0.3
            sample = sin(2 * pi * freq * t)
            value = int(sample * amplitude * fade)
            
            # Add the same sample to both channels for stereo output.
            buffer.extend((value, value))
            
    return pg.mixer.Sound(buffer=buffer)


class Sounds:
    def __init__(self) -> None:
        """Initializes the sound system and creates all available sound effects.
        
        The Pygame mixer is initializes with the global sample rate and stereo
        output. If the mixer or sound creation fails, the sound system is
        marked as unavailable.
        
        Attributes:
            enabled (bool): Indicates whether sound playback is enabled.
            available (bool): Indicates whether the sound system was
                initialized successfully.
            volume (float): master volume for all sound effects, ranging from
                0.0 to 1.0.
            
            click (pg.mixer.Sound): Short sound for left clicks in a match.
            dim (pg.mixer.Sound): Short sound for right clicks in a match.
            hint (pg.mixer.Sound): Short sound for each hint used.
            undo (pg.mixer.Sound): Short sound for any action being undone.
            tip (pg.mixer.Sound): Short sound for every key pressed in terminal.
            sub (pg.mixer.Sound): Short sound for a command sending 'Return' in
                terminal.
            win (pg.mixer.Sound): Jingle for the moment the player has won.
        """
        self.enabled = True
        self.available = False
        self.volume = 1.0
        
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
            
        except Exception:
            self.available = False
            
    
    def play(self, sound: pg.mixer.Sound | None) -> None:
        """Plays a sound effect if the sound system is available and enabled.
        
        The volume is clamped to the valid range from 0.0 to 1.0 before
        playback.

        Args:
            sound (pg.mixer.Sound | None): Sound object to play, or None if no
                sound should be played.
        """
        if self.available and self.enabled and sound is not None:
            sound.set_volume(max(0.0, min(1.0, self.volume)))
            sound.play()