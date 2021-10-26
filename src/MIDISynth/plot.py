from datetime import time as tm
import math
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as tick

from .music import Piece, Note
from .utils import midi_to_hertz, frequency_to_notes


def format_freq(x, pos, f, freq_type='int', freq_names=None, plot_units=False):
    if pos:
        pass
    n = int(round(x))
    if 0 <= n < f.size:
        if plot_units:
            if freq_type == 'int':
                return str(f[n].astype(int)) + " Hz"
            elif freq_type == 'str':
                return freq_names[n]
            else:
                return ""
        else:
            if freq_type == 'int':
                return str(f[n].astype(int))
            elif freq_type == 'str':
                return freq_names[n]
            else:
                return ""
    else:
        return ""


def format_time(x, pos, t, plot_units=False):
    if pos:
        pass
    n = int(round(x))
    if 0 <= n < t.size:
        if plot_units:
            return str(round(t[n], 3)) + " s"
        else:
            decomposition = math.modf(round(t[n], 6))
            s = round(decomposition[1])
            hours = s // (60 * 60)
            minutes = (s - hours * 60 * 60) // 60
            seconds = s - (hours*60*60) - (minutes*60)
            return tm(second=seconds, minute=minutes, hour=hours,
                      microsecond=round(decomposition[0] * 1e6)).isoformat(
                timespec='milliseconds')[3:-1]  # [3:]
    else:
        return ""


def plot_time_frequency(a, t, f, v_min=0, v_max=1, c_map='Greys',
                        fig_title=None, show=True, numpy=True,
                        full_screen=False, fig_size=(640, 480),
                        freq_type='int',
                        freq_label='Frequency (Hz)', time_label='Time (s)',
                        plot_units=False, freq_names=None, dpi=120,
                        backend='Qt5Agg'):
    fig = plt.figure(figsize=(fig_size[0]/dpi, fig_size[1]/dpi), dpi=dpi)

    if fig_title:
        fig.suptitle(fig_title)

    ax = fig.add_subplot(111)

    if numpy:
        a_plot = a
    else:
        a_plot = a.cpu().numpy()

    ax.imshow(a_plot, cmap=c_map, aspect='auto', vmin=v_min, vmax=v_max,
              origin='lower')

    # Freq axis
    ax.yaxis.set_major_formatter(
        tick.FuncFormatter(lambda x, pos:
                           format_freq(x, pos, f, freq_type, freq_names,
                                       plot_units=plot_units)))

    # Time axis
    ax.xaxis.set_major_formatter(
        tick.FuncFormatter(lambda x, pos: format_time(x, pos, t,
                                                      plot_units=plot_units)))

    # Labels
    ax.set_xlabel(time_label)
    ax.set_ylabel(freq_label)

    if full_screen:
        manager = plt.get_current_fig_manager()
        if backend == 'WXAgg':
            manager.frame.Maximize(True)
        elif backend == 'TkAgg':
            manager.resize(*manager.window.maxsize())
        elif backend == 'Qt5Agg':
            manager.window.showMaximized()
        else:
            raise Exception("Backend not supported.")

    if show:
        plt.show(block=False)

    return fig


def plot_piano_roll(piece: Piece, frequency_vector, time_vector,
                    semitone_width=1, bins_per_octave=12, full_screen=False):

    # Initialize piano roll matrix
    p_roll = np.zeros((len(frequency_vector), len(time_vector)))

    for note in piece.notes:
        if isinstance(note, Note):
            freq = midi_to_hertz(note.note_number)
            time_start = note.start_seconds
            time_end = note.end_seconds

            tmp = freq * 2**(- semitone_width / 2 / bins_per_octave)
            f_0 = tmp <= frequency_vector
            f_1 = frequency_vector < freq * 2**(semitone_width / 2 /
                                                bins_per_octave)
            f = np.logical_and(f_0, f_1)

            t_0 = time_start <= time_vector
            t_1 = time_vector < time_end
            t = np.logical_and(t_0, t_1)

            tf = np.expand_dims(f, 1) * np.expand_dims(t, 0)
            # section = p_roll[f, :][:, t]
            p_roll[tf] = max(note.velocity, np.max(p_roll[tf]))

    notes_vector = frequency_to_notes(frequency_vector)

    fig = plot_time_frequency(p_roll, time_vector, frequency_vector,
                              fig_title='Piano roll of ' + piece.name,
                              v_min=0, v_max=128, c_map='Greys',
                              freq_type='str', freq_label='Notes',
                              freq_names=notes_vector,
                              full_screen=full_screen)

    return fig
