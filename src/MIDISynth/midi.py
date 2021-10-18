from pathlib import Path
import mido as mid

from .music import Note, Piece
from .utils import ticks2seconds


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


def midi2piece(name: str, file_path: Path, final_rest: float = 0.):
    piece = Piece(name, final_rest)
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
