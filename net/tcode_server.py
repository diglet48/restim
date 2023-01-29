import asyncio
import time
import websockets
import numpy as np
import re

from net.tcode import TCodeCommand, InvalidTCodeException


class TCodeFunscriptAxis:
    def __init__(self, axis_specification, init=0.5):
        self.axis_specification = axis_specification
        self.funscript = np.zeros(shape=(0, 2))
        self.add_cmd(0, init)

    def add_cmd(self, at_time, value):
        # todo: this is really slow
        self.funscript = np.vstack((self.funscript, [at_time, value]))


class TCodeFunscriptEmulator:
    def __init__(self):
        self.axis = {
            'L0': TCodeFunscriptAxis('L0'),
            'L1': TCodeFunscriptAxis('L1'),
            'L2': TCodeFunscriptAxis('L2', 1.0),

            'C0': TCodeFunscriptAxis('C0', 1.0),
            'C1': TCodeFunscriptAxis('C1', 1.0),
            'C2': TCodeFunscriptAxis('C2', 1.0),
            'C3': TCodeFunscriptAxis('C3', 1.0),
            'C4': TCodeFunscriptAxis('C4', 1.0),
            'C5': TCodeFunscriptAxis('C5', 1.0),
            'C6': TCodeFunscriptAxis('C6', 1.0),
        }

    def parse_message(self, line):
        for cmd in re.split('\\s|\n|\r', line):
            try:
                tcode = TCodeCommand.parse_command(cmd)
                self.add_cmd(tcode)
            except InvalidTCodeException:
                pass

    def add_cmd(self, cmd):
        try:
            axis = self.axis[cmd.axis_identifier]
            axis.add_cmd(time.time(), cmd.value)
        except KeyError:
            pass

    def interpolate(self, axis_identifier, at_time):
        try:
            axis = self.axis[axis_identifier]
            return np.interp(at_time, axis.funscript[:, 0], axis.funscript[:, 1])
        except KeyError:
            return np.zeros_like(at_time)

    def last_value(self, axis_identifier):
        try:
            axis = self.axis[axis_identifier]
            return axis.funscript[-1, 1]
        except KeyError:
            return None


class TCodeWebsocketServer:
    def __init__(self, url, port):
        self.url = url
        self.port = port

        self.funscript_emulator = TCodeFunscriptEmulator()

    async def start(self):
        print('starting server {} at port {}'.format(self.url, self.port))
        async with websockets.serve(self.new_message, self.url, self.port):
            await asyncio.Future()  # run forever

    async def new_message(self, websocket):
        async for message in websocket:
            self.funscript_emulator.parse_message(message)


if __name__ == '__main__':
    ws_server = TCodeWebsocketServer("localhost", 12346)
    asyncio.run(ws_server.start())