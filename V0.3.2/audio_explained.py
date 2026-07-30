### Mati (Mathematics and tactic intelligence) ###
### V0.3.2 Beta V1.0.16 ###
### Author: Janosch Klawatsch, 21.07.2026 ###
### audio explained file V0.3.0 ###

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
# - terminal.py - The Terminal #

### -Imports- ###
### External ###
# Because Python as a coding language does not contain every function everyone could need,
# some people created extensions (Imports) which are just code you can use without having to
# develop it by your own
from array import array   # To handle arrays, an efficent way to handle an amount of data
from math import sin, pi  # To have mathematic operations like pi
import pygame as pg       # Something like Unity but made for Python

### Own ###
# Additionally to extension from others you can create an extension by your own
# This extension also need to be imported
# the from at the start just means: "I don't want everything from you, just what I tell you"
# This way of getting a method is more efficent, but you need to know every you may need
# Because you so do not get suggestions in your editor
from config import SAMPLE_RATE # To get the self defined constant of the SAMPLE_RATE
# The sample rate is a number that is something like the audio quality
# In this situation it has a value of 41000 which is the normal quality of a CD or DVD-Audio

### -Functions- ###
# A function is every code block starting with def
# You can think of a function like a mini programm that can be called
# Functions make it possible to wright code ones and use it various times
def _make_tone(freq: float, duration_ms: float, volume: float = 0.3): # This function should create a single tone
    # To make this, the function get parameters, if you set a timer, the timer is the function and the time is the parameter
    # freq is short for frequency and the type is a float (: means now i give you a hint what I am)
    # float is basically an number that could have digits after the dot
    # duration_ms means duration in miliseconds
    # the value 0.3 behind the float in the volume parameter is just an automatic given value if you don't say it
    # Like that your timer starts now if you do not tell him to start in 10 minutes
    
    # The names n_samples, short for number of samples, amplitude and buffer are variables
    # Variables are little storages that handle what you give them until you need it again
    # Their are like your calendar, they save what you want them to save
    # the number of samples gives the number of parts the audio should have
    # int just says it should be an integer, that means a number without digit after the dot
    # and is the result of the time in seconds (duration_ms / 1000) multiplied with the quality we want
    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    # The amplitude is the value how loud a tone can be
    # its the result from the maximum noice value possible in our system (32767) and the part of it we want (volume)
    amplitude = int(32767 * volume)
    # The buffer is just an array in 16 bit ("h" = 16 bit), that can save all the note parts we need
    buffer = array("h") # Generate an array
    
    # for ... is a predefined way how to get threw a lot of data efficiency, that means something like a function but handled different
    # In this case it counts i up to the number of the sample we give it and do a block of code with every i
    for i in range(n_samples): # For each sample
        # t means time and saves the excact microsecond this part (i-value) need to be played on this quality (SAMPLE_RATE)
        t = i / SAMPLE_RATE
        # The fade makes the noice value of the note variate so no wrong sounds can appear at the time the note starts or ends
        fade = 1.0 - (i / n_samples) * 0.1 # Fade values
        # The sample is one audio part withoud the information containing how loud it is
        # You can get it with the sinus, because the way sound is created is threw vibrations of air
        # If we take the information which note we want and on which time we are the sinus return the information how far this vibration is in this moment
        sample = sin(2 * pi * freq * t) # Generate sample as sinus value
        # Combined with the informations containing how loud it is, we get the value, that means one single part with every information that is needed to create a note
        value = int(sample * amplitude * fade) # Make it complete
        # We add this part to our save list, so it do not get lost
        buffer.extend((value, value)) # To get stereo audio, we give the value dopple, one for left and one for right speaker
    # All parts to getter can be interpreted as a note. 
    # To do this task we take help from pygame, because it can easly create the note of the information
    return pg.mixer.Sound(buffer=buffer) # Really generate the tone
    # And if you not already noticed, this is the way everything you hear is created,
    # of course this is more technically then the nature, but it uses the same way
    # so, if you have enough time and strong enough nervs you can generate you own voice with just this commands
    # But I guess to not do this, because it is way to much work


# This function basically works like the one before
# notes just contains more than one frequenc and note_ms is the equivilant to duration_ms
# The only significant different is, that this function generates threw the for freq in notes:
# for every given frequenz a note and add all this notes together
# So this functions generates various notes at ones
def _make_jingle(notes: list[float], note_ms: float = 90, volume: float = 0.3): # Gernate more tones to a jingle
    n_samples = int(SAMPLE_RATE * note_ms / 1000) # Number of samples per second
    amplitude = int(32767 * volume) # Define the amplitude
    buffer = array("h") # Generate an array
    for freq in notes: # For number of notes
        for i in range(n_samples): # For each sample
            t = i / SAMPLE_RATE # duration point
            fade = 1.0 - (i / n_samples) * 0.3 # Fade values
            sample = sin(2 * pi * freq * t) # Generate sinus sample
            value = int(sample * amplitude * fade) # Blueprint for the tone
            buffer.extend((value, value)) # To get stereo audio
    return pg.mixer.Sound(buffer=buffer) # Generate the jingle


# A class is a container
# So everything in there can have acess to everything in there, but what is out can't have acess withoutwe let him come in
# In classes self. is nearly in front of everything to make clear what is part of the class and what not
# If a thing is not in the class no other functions of the class can use it
class Sounds: # Handle sound play
    # Every class needs an init.
    # the init is a function that defines what should happen if someone whants acess the first time to the class or one of the functions in this class
    def __init__(self): # Inititalize the class
        # It defines key values that need to be fixed to make the class work without problems
        # Like that the one who called it want the sound to work (enabled)
        self.enabled = True # Be activated
        # And think that it is not sure, if the speakers are working
        self.available = False # Need to check if audio can be played
        # try code blocks are runned threw, but break the run if they realise that something is not doing like planned
        try: # If all possible do
            # what we try to do is, to active the pygame function that allows us to generate a note 
            # and with that really generate the notes and save them, so that we can use them everytime we want
            pg.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2) # Initialize the mixer
            self.click = _make_tone(440, 60, 0.25) # Click Sound
            self.dim = _make_tone(300, 55, 0.2)    # Right click sound
            self.hint = _make_tone(700, 120, 0.28) # Hint used sound
            self.undo = _make_tone(250, 80, 0.2)   # Undone sound
            
            self.win = _make_jingle([523, 659, 784, 1046]) # Jingle for win
            self.available = True # Give sounds is possible
            # If everything got without any problems we say that we are ready and everything worked
        # except blocks are the action thats is just made if something failed
        except Exception: # If not possible
            # what we do is just saying that the sounds do not work
            self.available = False # Can not give sounds
            
            
    # the play functions task is to find the sounds and let the sound be heard
    def play(self, sound): # Gets a sound to play
        # but before it checks if the player want the sound to be played, if it can be played and if it exsists
        if self.available and self.enabled and sound is not None: # If it should, can and have something to play
            # if all this is correct, the ffunction let the sound play
            sound.play() # Let the sound play