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

    # Check unimplemented features
    has_pedal = check_pedal(midi)
    if has_pedal:
        # TODO: Integrate pedal
        raise Exception("Pedal not integrated yet")
    if len(midi.tracks) != 1:
        # TODO: Allow several tracks
        raise Exception("Several tracks not integrated")

    track = midi.tracks[0]

    # Tempo
    tempo = 500000 * 2
    bpm = mid.tempo2bpm(tempo)

    # Notes loop
    time_ticks = 0
    for m, msg in enumerate(track):
        time_ticks += msg.time
        # Is note?
        if msg.type in ['note_on', 'note_off']:
            # The two styles of note off
            is_note_off = (msg.velocity == 0) or (msg.type == 'note_off')

            if not is_note_off:
                m_end = m + 1
                delta_ticks = 0
                while True:
                    new_msg = track[m_end]

                    delta_ticks += new_msg.time

                    if new_msg.type in ['note_on', 'note_off']:
                        is_note_off = (new_msg.velocity == 0) or (new_msg.type == 'note_off')

                        if new_msg.note == msg.note and is_note_off:
                            start_seconds = ticks2seconds(time_ticks, midi.ticks_per_beat, bpm)
                            end_seconds = ticks2seconds(time_ticks + delta_ticks, midi.ticks_per_beat, bpm)
                            note = Note(msg.note, msg.velocity, start_seconds, end_seconds)
                            piece.notes.append(note)
                            break
                    m_end += 1
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            bpm = mid.tempo2bpm(tempo)

    return piece
