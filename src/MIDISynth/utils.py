import numpy as np
import music21 as m21


# Parameters
REFERENCE_HERTZ = 440
REFERENCE_MIDI = 69


def midi_to_hertz(midi: float) -> float:
    return REFERENCE_HERTZ * 2**((midi - REFERENCE_MIDI) / 12)


def hertz_to_midi(hertz: float) -> float:
    return 12 * np.log2(hertz / REFERENCE_HERTZ) + REFERENCE_MIDI


def frequency_to_notes(f_vector, integer=False, numbers=False):
    n_vector = list()
    if numbers:
        if integer:
            for i in range(len(f_vector)):
                n_vector.append(hertz_to_midi(f_vector[i]))
        else:
            for i in range(len(f_vector)):
                n_vector.append(int(hertz_to_midi(f_vector[i])))
    else:
        for i in range(len(f_vector)):
            n_vector.append(m21.pitch.Pitch(midi=hertz_to_midi(f_vector[i])).unicodeNameWithOctave)
    return n_vector


def ticks2seconds(ticks, ticks_per_beat, bpm):
    seconds = ((ticks / ticks_per_beat) / (bpm / 60))
    return seconds


def velocity_to_amplitude(velocity: int, velocity_range: int = 128) -> float:
    return velocity / velocity_range
