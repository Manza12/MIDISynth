import music21 as m21


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
