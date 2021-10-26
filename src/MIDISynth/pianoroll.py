import numpy as np

from MIDISynth.music import Piece, Note
from MIDISynth.utils import midi_to_hertz


def create_piano_roll(piece: Piece, frequency_vector, time_vector,
                      semitone_width=1, bins_per_octave=12):
    # Initialize piano roll matrix
    piano_roll = np.zeros((len(frequency_vector), len(time_vector)))

    for note in piece.notes:
        if isinstance(note, Note):
            freq = midi_to_hertz(note.note_number)
            time_start = note.start_seconds
            time_end = note.end_seconds

            tmp = freq * 2 ** (- semitone_width / 2 / bins_per_octave)
            f_0 = tmp <= frequency_vector
            f_1 = frequency_vector < freq * 2 ** (semitone_width / 2 /
                                                  bins_per_octave)
            f = np.logical_and(f_0, f_1)

            t_0 = time_start <= time_vector
            t_1 = time_vector < time_end
            t = np.logical_and(t_0, t_1)

            tf = np.expand_dims(f, 1) * np.expand_dims(t, 0)

            piano_roll[tf] = max(note.velocity, np.max(piano_roll[tf]))

    return piano_roll
