# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 15:45:10 2021

@author: trite
"""

from MIDISynth import midi2piece

import numpy as np
from pathlib import Path

file_name = 'tempest'
file_path = Path('..') / Path('data') / Path('midi') \
              / Path(file_name + 'mid')
piece = midi2piece(file_name, file_path, 1.)
piece.__str__()

# Frequency parameters
f_min = 27.5  # La 0
bins_per_octave = 12
n_bins = int(bins_per_octave * (7 + 1 / 3))  # number of bins of a piano

# Times parameters
time_resolution = 0.001  # ms resolution

# Plot
frequency_vector = f_min * 2 ** (np.arange(n_bins) / bins_per_octave)
time_vector = np.arange(0, piece.duration(), time_resolution)
piece.piano_roll(frequency_vector, time_vector, 
                 bins_per_octave=bins_per_octave, semitone_width=1)
