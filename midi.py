from music import Note, Piece
from pathlib import Path
import mido as mid

from utils import ticks2seconds


def print_messages(midi):
    for i, track in enumerate(midi.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in track:
            print(msg)


def check_pedal(midi):
    for msg in midi.tracks[0]:
        if msg.type == 'control_change':
            if msg.control == 64:
                Warning('There is pedal')
                return False
            else:
                Exception("Control change not handled")
    return False


def midi2piece(file_name: str, file_folder: str, final_rest: float = 0.):
    piece = Piece(file_name, final_rest)
    file_path = Path(file_folder) / Path(file_name + '.mid')
    midi = mid.MidiFile(file_path)

    has_pedal = check_pedal(midi)
    tempo = 500000 * 2
    bpm = mid.tempo2bpm(tempo)

    if not has_pedal:
        time_ticks = 0
        for m, msg in enumerate(midi.tracks[0]):
            time_ticks += msg.time
            if msg.type == 'note_on':
                if msg.velocity != 0:
                    m_end = m + 1
                    delta_ticks = 0
                    while True:
                        delta_ticks += midi.tracks[0][m_end].time
                        if midi.tracks[0][m_end].note == msg.note and midi.tracks[0][m_end].velocity == 0:
                            start_seconds = ticks2seconds(time_ticks, midi.ticks_per_beat, bpm)
                            end_seconds = ticks2seconds(time_ticks + delta_ticks, midi.ticks_per_beat, bpm)
                            note = Note(msg.note, msg.velocity, start_seconds, end_seconds)
                            piece.notes.append(note)
                            break
                        m_end += 1
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                bpm = mid.tempo2bpm(tempo)
    else:
        # TODO: Integrate pedal
        raise Exception("Pedal not integrated yet")

    return piece


if __name__ == '__main__':
    import numpy as np

    _file_name = 'tempest'
    _file_folder = 'midi'
    _piece = midi2piece(_file_name, _file_folder, 1.)
    _piece.__str__()

    # Frequency parameters
    _f_min = 27.5  # La 0
    _bins_per_octave = 12
    _n_bins = int(_bins_per_octave * (7 + 1 / 3))  # number of bins of a piano

    # Times parameters
    time_resolution = 0.001  # ms resolution

    # Plot
    _frequency_vector = _f_min * 2 ** (np.arange(_n_bins) / _bins_per_octave)
    _time_vector = np.arange(0, _piece.duration(), time_resolution)
    _piece.piano_roll(_frequency_vector, _time_vector, bins_per_octave=_bins_per_octave, semitone_width=1)
