# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 15:48:15 2021

@author: trite
"""

from MIDISynth import Piece, Note

import numpy as np

piece = Piece("Example")
note_1 = Note(69, 80, 0., 1.)
note_2 = Note(71, 100, 0.5, 1.4)
note_3 = Note(72, 120, 1., 2.)
piece.notes.append(note_1)
piece.notes.append(note_2)
piece.notes.append(note_3)

print(piece)
print("Length of " + piece.name + ":", len(piece.notes))
print("Duration of " + piece.name + ":", piece.duration())

# Frequency parameters
f_min = 27.5  # La 0
bins_per_octave = 12
n_bins = int(bins_per_octave * (7 + 1/3))  # number of bins of a piano

# Times parameters
time_resolution = 0.001  # ms resolution

# Plot
frequency_vector = f_min * 2**(np.arange(n_bins) / bins_per_octave)
time_vector = np.arange(0, piece.duration(), time_resolution)
piece.piano_roll(frequency_vector, time_vector, 
                 bins_per_octave=bins_per_octave, semitone_width=1)