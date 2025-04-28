from simfile.simfile import Notes, BPM, Simfile
from simfile.interpolation import Interpolator


import numpy as np



class Note:
    def __init__(self):
        self.presses = []
        self.releases = []

    def add_note(self, t, note):
        if note == '0':
            pass
        elif note == '1':
            self.presses.append(t)
            self.releases.append(t)
        elif note == '2':
            self.presses.append(t)
        elif note == '3':
            self.releases.append(t)

    def time_until_next_press(self, t):
        index = np.searchsorted(self.presses, t)
        try:
            return self.presses[index] - t
        except IndexError:
            return 999

    def time_since_last_press(self, t):
        index = np.searchsorted(self.presses, t, 'right') - 1
        if index == -1:
            return 999
        try:
            return t - self.presses[index]
        except IndexError:
            return 999

    def to_xy(self, x, interp: Interpolator):
        y = []
        for t in x:
            y.append(max(
                np.nan_to_num(interp(-self.time_until_next_press(t))),
                np.nan_to_num(interp(self.time_since_last_press(t))),
            ))
        return y


def notes_to_intensity(notes: Notes, interp: Interpolator):
    measures = notes.notes.split(',')
    measures = [measure.strip().split('\n') for measure in measures]

    a_note = Note()
    b_note = Note()
    c_note = Note()
    d_note = Note()

    for (measure_no, measure) in enumerate(measures):
        for beat_no, beat in enumerate(measure):
            t = measure_no + beat_no / len(measure)
            a, b, c, d = beat
            a_note.add_note(t, a)
            b_note.add_note(t, b)
            c_note.add_note(t, c)
            d_note.add_note(t, d)

    end_t = len(measures) + 1
    x = np.arange(0, end_t, 1.0/64)
    a = a_note.to_xy(x, interp)
    b = b_note.to_xy(x, interp)
    c = c_note.to_xy(x, interp)
    d = d_note.to_xy(x, interp)

    return x, (a, b, c, d)


def electrode_intensity_to_position_3p(a, b, c):
    a_vec = np.array([1, 0])
    b_vec = np.array([-0.5, np.sqrt(3) / 2])
    c_vec = np.array([-0.5, -np.sqrt(3) / 2])

    alpha = []
    beta = []
    for i in range(len(a)):
        p = a_vec * a[i] + b_vec * b[i] + c_vec * c[i]
        norm = np.linalg.norm(p)
        if norm > 1:
            p = p / norm

        alpha.append(p[0])
        beta.append(p[1])

    return alpha, beta