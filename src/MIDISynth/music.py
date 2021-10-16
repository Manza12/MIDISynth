import music21 as m21
import numpy as np

from .utils import frequency_to_notes, midi_to_hertz
from .plot import plot_time_frequency


class Pitch:
    def __init__(self, note_number: int):
        self.note_number = note_number
        self.pitch = m21.pitch.Pitch(midi=note_number)

    def __str__(self) -> str:
        return self.pitch.unicodeNameWithOctave


class Note(Pitch):
    def __init__(self, note_number, velocity, start_seconds, end_seconds):
        super().__init__(note_number)
        self.velocity = velocity
        self.start_seconds = start_seconds
        self.end_seconds = end_seconds
        self.duration = end_seconds - start_seconds

    def __str__(self, name_str=True, time_str=True, velocity_str=False):
        result = ""

        if name_str:
            result += self.pitch.unicodeNameWithOctave
        if time_str:
            result += ", start: " + str(round(self.start_seconds, 3)) \
                      + ", end: " + str(round(self.end_seconds, 3)) \
                      + ", duration: " + str(round(self.duration, 3))
        if velocity_str:
            result += ", velocity: " + str(self.velocity)
        return result


class Piece:
    def __init__(self, name: str = None, final_rest: float = 0.):
        self.name: str = name
        self.final_rest: float = final_rest
        self.notes: list[Note] = list()

    def __str__(self) -> str:
        result = ""
        result += "Piece: "

        if self.name:
            result += self.name + "\n"
        else:
            result += "[no name]\n"

        result += "Notes:\n"
        for i in range(len(self.notes)):
            result += self.notes[i].__str__() + "\n"

        return result

    def duration(self):
        dur = 0.
        for note in self.notes:
            if note.end_seconds > dur:
                dur = note.end_seconds
        return dur + self.final_rest

    def piano_roll(self, frequency_vector, time_vector, semitone_width=1, bins_per_octave=12):
        # Initialize piano roll matrix
        p_roll = np.zeros((len(frequency_vector), len(time_vector)))

        for note in self.notes:
            if isinstance(note, Note):
                freq = midi_to_hertz(note.note_number)
                time_start = note.start_seconds
                time_end = note.end_seconds

                f_0 = freq * 2**(- semitone_width / 2 / bins_per_octave) <= frequency_vector
                f_1 = frequency_vector < freq * 2**(semitone_width / 2 / bins_per_octave)
                f = np.logical_and(f_0, f_1)

                t_0 = time_start <= time_vector
                t_1 = time_vector < time_end
                t = np.logical_and(t_0, t_1)

                tf = np.expand_dims(f, 1) * np.expand_dims(t, 0)
                # section = p_roll[f, :][:, t]
                p_roll[tf] = max(note.velocity, np.max(p_roll[tf]))

        notes_vector = frequency_to_notes(frequency_vector)

        fig = plot_time_frequency(p_roll, time_vector, frequency_vector, fig_title='Piano roll of ' + self.name,
                                  v_min=0, v_max=128, c_map='Greys', freq_type=str, freq_label='Notes',
                                  freq_names=notes_vector)
        return fig
