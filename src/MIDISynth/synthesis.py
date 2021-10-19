import numpy as np
from typing import Union
import scipy.signal.windows as win
import tqdm

from .music import Piece
from .utils import midi_to_hertz, velocity_to_amplitude


class Synthesizer:
    def __init__(self, attack_time: float, number_harmonics: int, 
                 amplitude_harmonics: Union[str, np.ndarray],
                 decay_harmonics: Union[str, np.ndarray], **kwargs):
        # Attack time to reach max amplitude
        self.attack_time: float = attack_time

        # Number of harmonics
        self.number_harmonics: int = number_harmonics

        # Amplitude of harmonics
        if type(amplitude_harmonics) is np.ndarray:
            assert len(amplitude_harmonics.shape) == 1, 'Parameter ' \
                'amplitude_harmonics should be a 1D array.'
            assert amplitude_harmonics.shape[0] == number_harmonics, '' \
                'Parameter amplitude_harmonics should have length equal to ' \
                'number_harmonics.'
            self.amplitude_harmonics: np.ndarray = amplitude_harmonics
        elif type(amplitude_harmonics) is str:
            self.amplitude_harmonics: np.ndarray = get_amplitudes(
                amplitude_harmonics, number_harmonics)
        else:
            raise ValueError('Parameter type of amplitude_harmonics should '
                             'be str or Numpy array.')

        # Decay of harmonics (in Hertz)
        if type(decay_harmonics) is np.ndarray:
            assert len(decay_harmonics.shape) == 1, 'Parameter ' \
                'decay_harmonics should be a 1D array.'
            assert decay_harmonics.shape[0] == number_harmonics, \
                'Parameter decay_harmonics should have length equal to ' \
                'number_harmonics.'
            self.decay_function = get_decay_function('array', 
                                                     array=decay_harmonics)
        elif type(decay_harmonics) is str:
            self.decay_function = get_decay_function(decay_harmonics, **kwargs)
        else:
            raise ValueError('Parameter type of _decay_harmonics should be '
                             'str or Numpy array.')


def synthesize(synthesizer: Synthesizer, piece: Piece, fs: int = 48000, 
               verbose: bool = False) -> np.ndarray:
    n_signal = int(fs * piece.duration()) + 1
    signal = np.zeros(n_signal, dtype=np.float32)

    if verbose:
        for note in tqdm.tqdm(piece.notes):
            n_start: int = int(note.start_seconds * fs)
            n_length: int = int(note.duration * fs)
            t = np.arange(n_length) / fs

            f_0: float = midi_to_hertz(note.note_number)
            f = f_0 * np.arange(1, synthesizer.number_harmonics + 1, 1)

            decay_harmonics: np.ndarray = synthesizer.decay_function(f)

            starting_amplitude = velocity_to_amplitude(note.velocity)

            oscillators = np.sin(2 * np.pi * np.expand_dims(f, 1)
                                 * np.expand_dims(t, 0))
            decays: np.ndarray = np.exp(- 2 * np.pi 
                                        * np.expand_dims(decay_harmonics, 1)
                                        * np.expand_dims(t, 0))
            amplitudes: np.ndarray = np.expand_dims(
                synthesizer.amplitude_harmonics, 1)
            modulated_oscillators: np.ndarray = decays * oscillators
            scaled_oscillators = \
                starting_amplitude * amplitudes * modulated_oscillators
            signal_sum: np.ndarray = np.sum(scaled_oscillators, 0)
            signal_note = \
                win.tukey(n_length,
                          2 * synthesizer.attack_time * fs / n_length) \
                * signal_sum

            signal[n_start: n_start + n_length] += signal_note
    else:
        for note in piece.notes:
            n_start: int = int(note.start_seconds * fs)
            n_length: int = int(note.duration * fs)
            t = np.arange(n_length) / fs

            f_0: float = midi_to_hertz(note.note_number)
            f = f_0 * np.arange(1, synthesizer.number_harmonics + 1, 1)

            decay_harmonics: np.ndarray = synthesizer.decay_function(f)

            starting_amplitude = velocity_to_amplitude(note.velocity)

            oscillators = np.sin(2 * np.pi * np.expand_dims(f, 1)
                                 * np.expand_dims(t, 0))
            decays: np.ndarray = np.exp(- 2 * np.pi
                                        * np.expand_dims(decay_harmonics, 1)
                                        * np.expand_dims(t, 0))
            amplitudes = np.expand_dims(synthesizer.amplitude_harmonics, 1)
            modulated_oscillators: np.ndarray = decays * oscillators
            scaled_oscillators = \
                starting_amplitude * amplitudes * modulated_oscillators
            signal_sum: np.ndarray = np.sum(scaled_oscillators, 0)
            signal_note = \
                win.tukey(n_length,
                          2 * synthesizer.attack_time * fs / n_length) \
                * signal_sum

            signal[n_start: n_start + n_length] += signal_note

    return signal


def get_amplitudes(amplitude_string: str, number_harmonics: int) -> np.ndarray:
    if amplitude_string == 'inverse_square':
        amplitude_harmonics: np.ndarray = 1 / np.arange(1, 
                                                        number_harmonics + 1, 
                                                        1)**2
        return amplitude_harmonics
    elif amplitude_string == 'constant':
        amplitude_harmonics: np.ndarray = np.ones(number_harmonics)
        return amplitude_harmonics
    raise ValueError("Parameter amplitude_string should be one of: "
                     "'inverse_square'.")


def get_decay_function(decay_string: str, **kwargs):
    if decay_string == 'array':
        try:
            array: np.ndarray = kwargs['array']
            return lambda f: decay_array(f, array)
        except KeyError as key:
            raise ValueError('When decay_string is array you should specify '
                             'the parameter array.') from key

    elif decay_string == 'constant':
        try:
            value: float = kwargs['value']
            return lambda f: decay_constant(f, value)
        except KeyError as key:
            raise ValueError('When decay_string is constant you should '
                             'specify the parameter value.') from key

    elif decay_string == 'linear':
        try:
            reference_freq: float = kwargs['reference_freq']
        except KeyError as key:
            raise ValueError('When decay_string is linear you should '
                             'specify the parameter _reference_freq.') from key

        try:
            value_for_reference_freq: float = kwargs['value_for_reference_freq']
        except KeyError as key:
            raise ValueError('When decay_string is linear you should '
                             'specify the parameter '
                             'value_for_reference_freq.') from key

        try:
            coefficient: float = kwargs['coefficient']
        except KeyError as key:
            raise ValueError('When decay_string is linear you should '
                             'specify the parameter _coefficient.') from key

        decay_function = lambda f: decay_linear(f, reference_freq, 
                                                value_for_reference_freq, 
                                                coefficient)
        return decay_function

    elif decay_string == 'logarithmic':
        try:
            reference_freq: float = kwargs['reference_freq']
        except KeyError as key:
            raise ValueError('When decay_string is linear you should '
                             'specify the parameter reference_freq.') from key

        try:
            value_for_reference_freq: float = \
                kwargs['value_for_reference_freq']
        except KeyError as key:
            raise ValueError('When decay_string is linear you should '
                             'specify the parameter '
                             'value_for_reference_freq.') from key

        try:
            coefficient: float = kwargs['coefficient']
        except KeyError as key:
            raise ValueError('When decay_string is linear you should '
                             'specify the parameter coefficient.') from key

        decay_function = lambda f: decay_logarithmic(f, reference_freq, 
                                                     value_for_reference_freq, 
                                                     coefficient)
        return decay_function

    raise ValueError("Parameter amplitude_string should be one of: "
                     "'inverse_square'.")


def decay_array(f: np.ndarray, array: np.ndarray) -> np.ndarray:
    assert type(f) == np.ndarray
    return array


def decay_constant(f: np.ndarray, value: float) -> np.ndarray:
    return np.ones(len(f)) * value


def decay_linear(f: np.ndarray, reference_freq: float,
                 value_for_reference_freq: float, coefficient: float) \
        -> np.ndarray:
    return coefficient * (f - reference_freq) + value_for_reference_freq


def decay_logarithmic(f: np.ndarray, reference_freq: float,
                      value_for_reference_freq: float, coefficient: float) \
        -> np.ndarray:
    return value_for_reference_freq * 2**(coefficient * (f - reference_freq))
