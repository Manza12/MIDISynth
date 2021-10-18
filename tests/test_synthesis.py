# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 14:49:07 2021

@author: Gonzalo Romero-García
"""

from MIDISynth import midi2piece
from MIDISynth import Synthesizer, synthesize

import numpy as np
import scipy.io.wavfile as wav
from pathlib import Path

# MIDI parameters
file_name = 'tempest'
file_path = Path('..') / Path('data') / Path('midi') / Path(file_name + '.mid')
piece = midi2piece(file_name, file_path, 1.)

# Synthesizer parameters
attack_time: float = 0.01  # in seconds
number_harmonics: int = 16
amplitude_harmonics: str = 'inverse_square'
decay_harmonics: str = 'linear'
reference_freq: float = 440.
value_for_reference_freq: float = 0.5
coefficient: float = 0.001
linear_dictionary = {'reference_freq': reference_freq,
                     'value_for_reference_freq': value_for_reference_freq,
                     'coefficient': coefficient}

# Frequency parameters
f_min = 27.5  # La 0
bins_per_octave = 12
n_bins = int(bins_per_octave * (7 + 1 / 3))  # number of bins of a piano
frequency_vector = f_min * 2 ** (np.arange(n_bins) / bins_per_octave)

synthesizer = Synthesizer(attack_time, number_harmonics, amplitude_harmonics, 
                          decay_harmonics, **linear_dictionary)

decays = synthesizer.decay_function(frequency_vector)

# Synthesis
fs = 48000
signal: np.ndarray = synthesize(synthesizer, piece, fs=fs, verbose=False)

# Write
master_volume = 0.5
mastered_signal = master_volume * signal / signal.max()
audio_path = Path('..') / Path('data') / Path('audio')
wav.write(audio_path / Path(file_name + '.wav'), fs, mastered_signal)
