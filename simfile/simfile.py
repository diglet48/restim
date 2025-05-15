import pathlib

from msdparser import parse_msd

from dataclasses import dataclass

# simfile documentation: https://outfox.wiki/en/dev/mode-support/sm-support

@dataclass
class BPM:
    bpms: list[(float, float)]

    @staticmethod
    def parse_bpm(string):
        bpms = list()
        for bpm in string.split(','):
            onset, _, value = bpm.strip().partition('=')
            bpms.append((float(onset), float(value)))
        return BPM(bpms=bpms)


@dataclass
class Notes:
    steps_type: str
    description: str
    difficulty: str
    chart_meter: str
    radar_values: str
    notes: str

    @staticmethod
    def parse_notes(components):
        _, steps_type, description, difficulty, chart_meter, radar_values, notes = components
        return Notes(steps_type.strip(), description.strip(), difficulty.strip(), chart_meter.strip(), radar_values.strip(), notes)


class Simfile:
    def __init__(self):
        self.bpms = BPM([(0, 100)])
        self.offset = 0
        self.notes = list()

    @staticmethod
    def from_file(filename_or_path):
        simfile = Simfile()

        if isinstance(filename_or_path, str):
            path = pathlib.Path(filename_or_path)
        else:
            path = filename_or_path

        with path.open(encoding='utf-8') as f:
            for param in parse_msd(file=f):
                if param.key == 'BPMS':
                    simfile.bpms = BPM.parse_bpm(param.value)

                if param.key == 'OFFSET':
                    simfile.offset = float(param.value)

                if param.key == 'NOTES':
                    notes = Notes.parse_notes(param.components)
                    simfile.notes.append(notes)

        return simfile