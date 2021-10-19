from datetime import time as tm
import math

import matplotlib.pyplot as plt
import matplotlib.ticker as tick


def format_freq(x, pos, f, freq_type=int, freq_names=None, plot_units=False):
    if pos:
        pass
    n = int(round(x))
    if 0 <= n < f.size:
        if plot_units:
            if freq_type == int:
                return str(f[n].astype(int)) + " Hz"
            elif freq_type == str:
                return freq_names[n]
            else:
                return ""
        else:
            if freq_type == int:
                return str(f[n].astype(int))
            elif freq_type == str:
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
                      microsecond=round(decomposition[0] * 1e6)).isoformat(timespec='milliseconds')[6:-1]  # [3:]
    else:
        return ""


def plot_time_frequency(a, t, f, v_min=0, v_max=1, c_map='Greys', fig_title=None, show=True, numpy=True,
                        full_screen=False, fig_size=(640, 480), freq_type=int, freq_label='Frequency (Hz)',
                        time_label='Time (s)', plot_units=False, freq_names=None, dpi=120, backend='Qt5Agg'):
    fig = plt.figure(figsize=(fig_size[0]/dpi, fig_size[1]/dpi), dpi=dpi)

    if fig_title:
        fig.suptitle(fig_title)

    ax = fig.add_subplot(111)

    if numpy:
        a_plot = a
    else:
        a_plot = a.cpu().numpy()

    ax.imshow(a_plot, cmap=c_map, aspect='auto', vmin=v_min, vmax=v_max, origin='lower')

    # Freq axis
    ax.yaxis.set_major_formatter(
        tick.FuncFormatter(lambda x, pos: format_freq(x, pos, f, freq_type, freq_names, plot_units=plot_units)))

    # Time axis
    ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, pos: format_time(x, pos, t, plot_units=plot_units)))

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
