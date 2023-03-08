import numpy as np
import json


class Funscript:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_file(filename):
        x = []
        y = []
        with open(filename) as f:
            js = json.load(f)
            for action in js['actions']:
                at = float(action['at']) / 1000
                pos = float(action['pos']) * 0.01
                x.append(at)
                y.append(pos)
        return Funscript(x, y)

    def save_to_path(self, path):
        actions = [{"at": int(at * 1000), "pos": int(pos * 100)} for at, pos in zip(self.x, self.y)]
        js = {"actions": actions}
        with open(path, 'w') as f:
            json.dump(js, f)

