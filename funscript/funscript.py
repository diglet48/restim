import numpy as np
import json
import time
import logging
import hashlib


logger = logging.getLogger('restim.funscript')


# TOOD: consider cleaning up old files
funscript_cache = {

}


def sha1_hash(filename):
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
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
    def from_file(filename):
        start = time.time()
        x = []
        y = []

        hash = sha1_hash(filename)
        if hash in funscript_cache:
            logger.info(f'imported {filename} from cache')
            return funscript_cache[hash]

        with open(filename, encoding='utf-8') as f:
            js = json.load(f)
            for action in js['actions']:
                at = float(action['at']) / 1000
                pos = float(action['pos']) * 0.01
                x.append(at)
                y.append(pos)

        end = time.time()
        logger.info(f'imported {filename} in {end-start} seconds')
        funscript = Funscript(x, y)
        funscript_cache[hash] = funscript
        return funscript

    def save_to_path(self, path):
        actions = [{"at": int(at * 1000), "pos": int(pos * 100)} for at, pos in zip(self.x, self.y)]
        js = {"actions": actions}
        with open(path, 'w') as f:
            json.dump(js, f)

