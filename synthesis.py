import numpy as np
from typing import Union
import scipy.signal.windows as win
import scipy.io.wavfile as wav
import tqdm

from midi import midi2piece
from music import Piece
from utils import midi_to_hertz, velocity_to_amplitude


class Synthesizer:
    def __init__(self, attack_time: float, number_harmonics: int, amplitude_harmonics: Union[str, np.ndarray],
                 decay_harmonics: Union[str, np.ndarray], **kwargs):
        # Attack time to reach max amplitude
        self.attack_time: float = attack_time

        # Number of harmonics
        self.number_harmonics: int = number_harmonics

        # Amplitude of harmonics
        if type(amplitude_harmonics) is np.ndarray:
            assert len(amplitude_harmonics.shape) == 1, 'Parameter _amplitude_harmonics should be a 1D array.'
            assert amplitude_harmonics.shape[0] == number_harmonics, 'Parameter _amplitude_harmonics should have ' \
                                                                     'length equal to _number_harmonics.'
            self.amplitude_harmonics: np.ndarray = amplitude_harmonics
        elif type(amplitude_harmonics) is str:
            self.amplitude_harmonics: np.ndarray = get_amplitudes(amplitude_harmonics, number_harmonics)
        else:
            raise ValueError('Parameter type of _amplitude_harmonics should be str or Numpy array.')

        # Decay of harmonics (in Hertz)
        if type(decay_harmonics) is np.ndarray:
            assert len(decay_harmonics.shape) == 1, 'Parameter _decay_harmonics should be a 1D array.'
            assert decay_harmonics.shape[0] == number_harmonics, 'Parameter _decay_harmonics should have length equal' \
                                                                 ' to _number_harmonics.'
            self.decay_function = get_decay_function('array', number_harmonics, array=decay_harmonics)
        elif type(decay_harmonics) is str:
            self.decay_function = get_decay_function(decay_harmonics, number_harmonics, **kwargs)
        else:
            raise ValueError('Parameter type of _decay_harmonics should be str or Numpy array.')


def synthesize(synthesizer: Synthesizer, piece: Piece, fs: int = 48000, verbose: bool = False) -> np.ndarray:
    n_signal = int(fs * piece.duration()) + 1
    signal = np.zeros(n_signal, dtype=np.float32)

    if verbose:
        for note in tqdm.tqdm(piece.notes):
            n_start: int = int(note.start_seconds * fs)
            n_length: int = int(note.duration * fs)
            t = np.arange(n_length) / fs

            f_0: float = midi_to_hertz(note.note_number)
            f: np.ndarray = f_0 * np.arange(1, synthesizer.number_harmonics + 1, 1)

            decay_harmonics: np.ndarray = synthesizer.decay_function(f)

            starting_amplitude = velocity_to_amplitude(note.velocity)

            oscillators: np.ndarray = np.sin(2 * np.pi * np.expand_dims(f, 1) * np.expand_dims(t, 0))
            decays: np.ndarray = np.exp(- 2 * np.pi * np.expand_dims(decay_harmonics, 1)
                                        * np.expand_dims(t, 0))
            amplitudes: np.ndarray = np.expand_dims(synthesizer.amplitude_harmonics, 1)
            modulated_oscillators: np.ndarray = decays * oscillators
            scaled_oscillators = starting_amplitude * amplitudes * modulated_oscillators
            signal_sum: np.ndarray = np.sum(scaled_oscillators, 0)
            signal_note: np.ndarray = win.tukey(n_length, 2 * synthesizer.attack_time * fs / n_length) * signal_sum

            signal[n_start: n_start + n_length] += signal_note
    else:
        for note in piece.notes:
            n_start: int = int(note.start_seconds * fs)
            n_length: int = int(note.duration * fs)
            t = np.arange(n_length) / fs

            f_0: float = midi_to_hertz(note.note_number)
            f: np.ndarray = f_0 * np.arange(1, synthesizer.number_harmonics + 1, 1)

            decay_harmonics: np.ndarray = synthesizer.decay_function(f)

            starting_amplitude = velocity_to_amplitude(note.velocity)

            oscillators: np.ndarray = np.sin(2 * np.pi * np.expand_dims(f, 1) * np.expand_dims(t, 0))
            decays: np.ndarray = np.exp(- 2 * np.pi * np.expand_dims(decay_harmonics, 1)
                                        * np.expand_dims(t, 0))
            amplitudes: np.ndarray = np.expand_dims(synthesizer.amplitude_harmonics, 1)
            modulated_oscillators: np.ndarray = decays * oscillators
            scaled_oscillators = starting_amplitude * amplitudes * modulated_oscillators
            signal_sum: np.ndarray = np.sum(scaled_oscillators, 0)
            signal_note: np.ndarray = win.tukey(n_length, 2 * synthesizer.attack_time * fs / n_length) * signal_sum

            signal[n_start: n_start + n_length] += signal_note

    return signal


def get_amplitudes(amplitude_string: str, number_harmonics: int) -> np.ndarray:
    if amplitude_string == 'inverse_square':
        amplitude_harmonics: np.ndarray = 1 / np.arange(1, number_harmonics + 1, 1)**2
        return amplitude_harmonics
    else:
        raise ValueError("Parameter amplitude_string should be one of: 'inverse_square'.")


def get_decay_function(decay_string: str, number_harmonics: int, **kwargs):
    if decay_string == 'array':
        try:
            array: np.ndarray = kwargs['array']
        except KeyError:
            raise ValueError('When decay_string is array you should specify the parameter array.')
        decay_function = lambda f: decay_array(f, array)
        return decay_function

    elif decay_string == 'constant':
        try:
            value: float = kwargs['value']
        except KeyError:
            raise ValueError('When decay_string is constant you should specify the parameter value.')
        decay_function: lambda f: decay_constant(f, value)
        return decay_function

    elif decay_string == 'linear':
        try:
            reference_freq: float = kwargs['reference_freq']
        except KeyError:
            raise ValueError('When decay_string is linear you should specify the parameter _reference_freq.')

        try:
            value_for_reference_freq: float = kwargs['value_for_reference_freq']
        except KeyError:
            raise ValueError('When decay_string is linear you should specify the parameter _value_for_reference_freq.')

        try:
            coefficient: float = kwargs['coefficient']
        except KeyError:
            raise ValueError('When decay_string is linear you should specify the parameter _coefficient.')

        decay_function = lambda f: decay_linear(f, reference_freq, value_for_reference_freq, coefficient)
        return decay_function

    elif decay_string == 'logarithmic':
        try:
            reference_freq: float = kwargs['reference_freq']
        except KeyError:
            raise ValueError('When decay_string is linear you should specify the parameter _reference_freq.')

        try:
            value_for_reference_freq: float = kwargs['value_for_reference_freq']
        except KeyError:
            raise ValueError('When decay_string is linear you should specify the parameter _value_for_reference_freq.')

        try:
            coefficient: float = kwargs['coefficient']
        except KeyError:
            raise ValueError('When decay_string is linear you should specify the parameter _coefficient.')

        decay_function = lambda f: decay_logarithmic(f, reference_freq, value_for_reference_freq, coefficient)
        return decay_function

    else:
        raise ValueError("Parameter amplitude_string should be one of: 'inverse_square'.")


def decay_array(f: np.ndarray, array: np.ndarray) -> np.ndarray:
    return array


def decay_constant(f: np.ndarray, value: float) -> np.ndarray:
    return np.ones(len(f)) * value


def decay_linear(f: np.ndarray, reference_freq: float, value_for_reference_freq: float, coefficient: float) \
        -> np.ndarray:
    return coefficient * (f - reference_freq) + value_for_reference_freq


def decay_logarithmic(f: np.ndarray, reference_freq: float, value_for_reference_freq: float, coefficient: float) \
        -> np.ndarray:
    return value_for_reference_freq * 2**(coefficient * (f - reference_freq))


if __name__ == '__main__':
    # MIDI parameters
    _file_name = 'tempest'
    _file_folder = 'midi'
    _piece = midi2piece(_file_name, _file_folder, 1.)

    # Synthesizer parameters
    _attack_time: float = 0.01  # in seconds
    _number_harmonics: int = 16
    _amplitude_harmonics: str = 'inverse_square'
    _decay_harmonics: str = 'logarithmic'
    _reference_freq: float = 440.
    _value_for_reference_freq: float = 0.5
    _coefficient: float = 0.001

    # Frequency parameters
    _f_min = 27.5  # La 0
    _bins_per_octave = 12
    _n_bins = int(_bins_per_octave * (7 + 1 / 3))  # number of bins of a piano
    _frequency_vector = _f_min * 2 ** (np.arange(_n_bins) / _bins_per_octave)

    _synthesizer = Synthesizer(_attack_time, _number_harmonics, _amplitude_harmonics, _decay_harmonics,
                               reference_freq=_reference_freq, value_for_reference_freq=_value_for_reference_freq,
                               coefficient=_coefficient)

    _decays = _synthesizer.decay_function(_frequency_vector)

    # Synthesis
    fs = 48000
    _signal: np.ndarray = synthesize(_synthesizer, _piece, fs=fs, verbose=True)

    # Write
    master_volume = 0.5
    wav.write('audio\\' + _file_name + '.wav', fs, master_volume * _signal / _signal.max())
