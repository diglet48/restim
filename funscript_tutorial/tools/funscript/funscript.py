import numpy as np
import json
import time
import logging
import hashlib
import pathlib


logger = logging.getLogger('restim.funscript')


# TOOD: consider cleaning up old files
funscript_cache = {

}


def sha1_hash(path):
    sha1 = hashlib.sha1()
    with path.open('rb') as f:
        while True:
            data = f.read(2 ** 16)
            sha1.update(data)
            if not data:
                break
    return sha1.hexdigest()


class Funscript:
    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)

    @staticmethod
    def from_file(filename_or_path):
        start = time.time()
        x = []
        y = []

        if isinstance(filename_or_path, str):
            path = pathlib.Path(filename_or_path)
        else:
            path = filename_or_path

        hash = sha1_hash(path)
        if hash in funscript_cache:
            logger.info(f'imported {path} from cache')
            return funscript_cache[hash]

        with path.open(encoding='utf-8') as f:
            js = json.load(f)
            for action in js['actions']:
                at = float(action['at']) / 1000
                pos = float(action['pos']) * 0.01
                x.append(at)
                y.append(pos)

        end = time.time()
        logger.info(f'imported {path} in {end-start} seconds')
        funscript = Funscript(x, y)
        funscript_cache[hash] = funscript
        return funscript

    def save_to_path(self, path):
        actions = [{"at": int(at * 1000), "pos": int(pos * 100)} for at, pos in zip(self.x, self.y)]
        js = {"actions": actions}
        with open(path, 'w') as f:
            json.dump(js, f)

