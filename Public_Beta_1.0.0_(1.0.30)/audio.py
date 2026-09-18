"""Procedurally generated sound effects and background music for the game."""

from __future__ import annotations

import logging
from typing import Final

import numpy as np
import pygame as pg

from config import SAMPLE_RATE as SR

logger = logging.getLogger(__name__)

# Constants
AUDIO_DEPTH_MAX: Final[float] = 32767.0


def _make_tone(
    freq: float,
    duration_ms: float,
    volume: float = 0.3,
) -> pg.mixer.Sound:
    """Create a stereo sine-wave tone with a short fade-out using NumPy vectorization."""
    n_samples = int(SR * duration_ms / 1000.0)
    if n_samples <= 0:
        return pg.mixer.Sound(buffer=b"")

    amplitude = AUDIO_DEPTH_MAX * max(0.0, min(1.0, volume))
    t = np.arange(n_samples, dtype=np.float64) / SR
    fade = 1.0 - (t / n_samples) * 0.1
    wave = np.sin(2.0 * np.pi * freq * t)

    data = (wave * amplitude * fade).astype(np.int16)
    stereo = np.repeat(data[:, np.newaxis], 2, axis=1).reshape(-1)
    return pg.mixer.Sound(buffer=stereo.tobytes())


def _make_jingle(
    notes: list[float],
    note_ms: float = 90.0,
    volume: float = 0.3,
) -> pg.mixer.Sound:
    """Create a stereo jingle consisting of multiple sequential sine-wave notes."""
    n_samples = int(SR * note_ms / 1000.0)
    if not notes or n_samples <= 0:
        return pg.mixer.Sound(buffer=b"")

    amplitude = AUDIO_DEPTH_MAX * max(0.0, min(1.0, volume))
    t = np.arange(n_samples, dtype=np.float64) / SR
    fade = 1.0 - (t / n_samples) * 0.3

    note_buffers = []
    for freq in notes:
        wave = np.sin(2.0 * np.pi * freq * t)
        data = (wave * amplitude * fade).astype(np.int16)
        note_buffers.append(data)

    full_data = np.concatenate(note_buffers)
    stereo = np.repeat(full_data[:, np.newaxis], 2, axis=1).reshape(-1)
    return pg.mixer.Sound(buffer=stereo.tobytes())


def _midi_to_freq(midi: float, a4: float = 440.0) -> float:
    """Convert a MIDI note number into its frequency in Hertz."""
    return a4 * (2.0 ** ((midi - 69.0) / 12.0))


def _build_music(
    notes: list[tuple[float, float, float, float]],
    bpm: float,
    beats: float,
    title: str,
    volume: float = 0.16,
) -> pg.mixer.Sound:
    """Synthesize a seamless, stereo, looping music phrase as a sound object."""
    beats_per_sec = bpm / 60.0
    total_s = beats / beats_per_sec
    n = int(round(SR * total_s))

    t = np.arange(n, dtype=np.float64) / SR
    acc = np.zeros(n, dtype=np.float64)

    for start_beat, dur_beats, midi, amp in notes:
        start_s = start_beat / beats_per_sec
        dur_s = dur_beats / beats_per_sec
        start_i = max(0, min(int(round(start_s * SR)), n - 1))
        end_i = max(start_i + 1, min(int(round((start_s + dur_s) * SR)), n))
        seg_len = end_i - start_i
        seg_t = t[start_i:end_i] - t[start_i]

        env = np.ones(seg_len, dtype=np.float64)
        atk = max(1, min(seg_len - 1, int(seg_len * 0.06)))
        rls = max(1, min(seg_len - atk, int(seg_len * 0.22)))
        env[:atk] = np.linspace(0.0, 1.0, atk)
        env[-rls:] = np.linspace(1.0, 0.0, rls)

        freq = _midi_to_freq(midi)
        wav = np.sin(2.0 * np.pi * freq * seg_t) + 0.2 * np.sin(
            4.0 * np.pi * freq * seg_t
        )
        acc[start_i:end_i] += wav * env * amp

    peak = float(np.max(np.abs(acc))) if n else 0.0
    base = max(0.0, min(1.0, volume)) * AUDIO_DEPTH_MAX
    acc = (acc / peak * base * 0.95) if peak > 0.0 else (acc * base * 0.95)

    data = np.clip(acc, -AUDIO_DEPTH_MAX, AUDIO_DEPTH_MAX).astype(np.int16)
    stereo = np.repeat(data[:, np.newaxis], 2, axis=1).reshape(-1)
    return pg.mixer.Sound(buffer=stereo.tobytes())


def _menu_loop() -> pg.mixer.Sound:
    """Build the main-menu loop in C major."""
    bpm = 64.0
    bars = [
        {"bass": 48, "pad": [60, 64, 67, 71], "melody": [(1.0, 67), (2.6, 69)]},
        {"bass": 45, "pad": [57, 60, 64, 67], "melody": [(1.2, 64), (3.0, 60)]},
        {"bass": 41, "pad": [53, 57, 60, 64], "melody": [(1.4, 65), (2.8, 64)]},
        {"bass": 43, "pad": [55, 59, 62, 64], "melody": [(1.0, 67), (2.5, 62)]},
    ]
    notes: list[tuple[float, float, float, float]] = []
    for bar, bd in enumerate(bars):
        start = bar * 4.0
        notes.append((start, 4.0, float(bd["bass"]), 0.85))
        for midi in bd["pad"]:
            notes.append((start, 3.8, float(midi), 0.5))
        for beat, midi in bd["melody"]:
            notes.append((start + beat, 0.8, float(midi), 0.26))

    return _build_music(notes, bpm, 16.0, "menu")


def _play_loop() -> pg.mixer.Sound:
    """Build the gameplay loop in C major."""
    bpm = 76.0
    bars = [
        {"bass": 48, "pad": [60, 64, 67], "arp": [72, 64, 67, 60, 67, 64]},
        {"bass": 43, "pad": [55, 59, 62], "arp": [67, 59, 62, 55, 62, 59]},
        {"bass": 45, "pad": [57, 60, 64], "arp": [69, 60, 64, 57, 64, 60]},
        {"bass": 41, "pad": [53, 57, 60], "arp": [65, 57, 60, 53, 60, 57]},
    ]
    notes: list[tuple[float, float, float, float]] = []
    for bar, bd in enumerate(bars):
        start = bar * 4.0
        notes.append((start, 4.0, float(bd["bass"]), 0.8))
        for midi in bd["pad"]:
            notes.append((start, 3.9, float(midi), 0.36))
        for i, midi in enumerate(bd["arp"]):
            notes.append((start + i * 0.5, 0.4, float(midi), 0.22))

    return _build_music(notes, bpm, 16.0, "play")


def _terminal_loop() -> pg.mixer.Sound:
    """Build the terminal loop in A minor pentatonic."""
    bpm = 96.0
    notes: list[tuple[float, float, float, float]] = [
        (0.0, 8.0, 45.0, 0.55),
        (0.0, 8.0, 33.0, 0.35),
    ]
    penta = [57, 60, 62, 64, 67, 69, 72]
    slots = [0.5, 1.5, 2.5, 3.0, 4.5, 5.5, 6.5, 7.0]
    for i, slot in enumerate(slots):
        notes.append((slot, 0.3, float(penta[i % len(penta)]), 0.34))

    return _build_music(notes, bpm, 8.0, "terminal")


class Sounds:
    """Sound manager responsible for audio initialisation and sound playback."""

    def __init__(self) -> None:
        self.enabled: bool = True
        self.available: bool = False
        self.volume: float = 1.0
        self.music: Music | None = None

        self.click: pg.mixer.Sound | None = None
        self.dim: pg.mixer.Sound | None = None
        self.hint: pg.mixer.Sound | None = None
        self.undo: pg.mixer.Sound | None = None
        self.tip: pg.mixer.Sound | None = None
        self.sub: pg.mixer.Sound | None = None
        self.win: pg.mixer.Sound | None = None
        self.export_pop: pg.mixer.Sound | None = None
        self.export_bye: pg.mixer.Sound | None = None

        try:
            pg.mixer.init(frequency=SR, size=-16, channels=2)

            self.click = _make_tone(440.0, 60.0, 0.25)
            self.dim = _make_tone(300.0, 55.0, 0.2)
            self.hint = _make_tone(700.0, 120.0, 0.28)
            self.undo = _make_tone(250.0, 80.0, 0.2)
            self.tip = _make_tone(400.0, 50.0, 0.1)
            self.sub = _make_tone(370.0, 130.0, 0.14)

            self.win = _make_jingle([523.0, 659.0, 784.0, 1046.0])
            self.export_pop = _make_jingle([523.0, 784.0], note_ms=85.0, volume=0.18)
            self.export_bye = _make_jingle([659.0, 392.0], note_ms=95.0, volume=0.15)

            self.music = Music()
            self.available = True
        except (pg.error, RuntimeError) as exc:
            logger.warning("Audio mixer initialisation failed: %s", exc)
            self.available = False

    def play(self, sound: pg.mixer.Sound | None) -> None:
        """Play a sound effect if audio is active and initialized."""
        if self.available and self.enabled and sound is not None:
            sound.set_volume(max(0.0, min(1.0, self.volume)))
            sound.play()


class Music:
    """Manages background music loops and dynamic crossfading."""

    FADE_MS: Final[int] = 400
    PAUSE_DUCK: Final[float] = 0.6

    def __init__(self) -> None:
        self.available: bool = False
        self.tracks: dict[str, pg.mixer.Sound] = {}
        self._channels: list[pg.mixer.Channel] = []
        self._active_channel: pg.mixer.Channel | None = None
        self._current: str | None = None
        self._volume: float = 1.0

        try:
            pg.mixer.set_reserved(2)
            self._channels = [pg.mixer.Channel(i) for i in range(2)]
            self.tracks = {
                "menu": _menu_loop(),
                "play": _play_loop(),
                "terminal": _terminal_loop(),
            }
            self.available = True
        except (pg.error, RuntimeError) as exc:
            logger.warning("Music channel initialisation failed: %s", exc)
            self.available = False

    @staticmethod
    def _state_track(state: str) -> str:
        """Return the track name corresponding to the game state."""
        if state in ("PLAY", "HANNAH"):
            return "play"
        if state == "TERMINAL":
            return "terminal"
        return "menu"

    def stop(self, fade: int | None = None) -> None:
        """Fade out and silence all background music channels."""
        if not self.available:
            return
        fade_duration = self.FADE_MS if fade is None else fade

        if self._active_channel is not None and self._active_channel.get_busy():
            self._active_channel.fadeout(fade_duration)
        self._active_channel = None
        self._current = None

    def _crossfade(self, target: str) -> None:
        """Crossfade smoothly to the specified track."""
        if self._current is not None and self._active_channel is not None:
            self._active_channel.fadeout(self.FADE_MS)

        next_ch = (
            self._channels[0]
            if self._active_channel is not self._channels[0]
            else self._channels[1]
        )
        sound = self.tracks[target]
        sound.set_volume(self._volume)
        next_ch.play(sound, loops=-1, fade_ms=self.FADE_MS)

        self._active_channel = next_ch
        self._current = target

    def update(
        self, state: str, paused: bool, enabled: bool, volume: float
    ) -> None:
        """Update music state, volume level, and handle track transitions."""
        if not self.available:
            return
        if not enabled:
            self.stop()
            return

        vol = max(0.0, min(1.0, volume))
        if paused:
            vol *= self.PAUSE_DUCK
        self._volume = vol

        target = self._state_track(state)
        if target != self._current:
            self._crossfade(target)

        if self._active_channel is not None:
            current_vol = self._active_channel.get_volume()
            if abs(current_vol - vol) > 0.001:
                self._active_channel.set_volume(vol)
                