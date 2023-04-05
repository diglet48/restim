import numpy as np


L0 = "L0"
L1 = "L1"
L2 = "L2"


class InvalidTCodeException(Exception):
    pass


class TCodeCommand:
    def __init__(self, axis_identifier: str, value: float, interval: int=0):
        self.axis_identifier = axis_identifier
        self.value = value
        self.interval = interval
        if interval < 0:
            raise InvalidTCodeException()

    @staticmethod
    def parse_command(buf):
        if isinstance(buf, bytes):
            try:
                buf = buf.decode('ascii')
            except UnicodeDecodeError:
                raise InvalidTCodeException()

        buf = buf.strip()
        if len(buf) < 3:
            raise InvalidTCodeException()

        axis_identifier = buf[0:2]
        value = buf[2:]
        value, _, interval = value.partition('I')
        value = value[:value.find('I')]
        try:
            value = float(value) / (10**len(value) - 1)
        except ValueError:
            raise InvalidTCodeException()

        try:
            interval = int(interval) if interval else 0
        except ValueError:
            raise InvalidTCodeException()

        return TCodeCommand(axis_identifier, value, interval)

    def format_cmd(self):
        if self.interval:
            return "{}{:04d}I{:d}".format(self.axis_identifier, int(np.clip(self.value, 0.0, 1.0) * 9999), int(self.interval))
        return "{}{:04d}".format(self.axis_identifier, int(np.clip(self.value, 0.0, 1.0) * 9999))

    def __str__(self):
        return self.format_cmd()
