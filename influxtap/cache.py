import json, os

from . import xdg

class Cache():
    def __init__(self):
        # init XDG path to store in
        self.dump_file = xdg.initXDG('influxtap') + 'cache.json'
        self.cache = []
        self.read() # prepop any offline cache

# dump provided datapoints cache data to a file
    def dump(self, datapoints=None):
        if datapoints is None:
            datapoints = self.cache
        if len(datapoints) > 0:
            with open(self.dump_file, 'w') as fh:
                json.dump(datapoints, fh)
                return True
        else:
            return False

    def read(self):
        if self.exists():
            with open(self.dump_file, 'r') as fh:
                self.cache = json.load(fh)
        else:
            return None

    def clear(self):
        self.cache = []
        if self.exists():
            os.unlink(self.dump_file)
            return True
        else:
            return False

    def exists(self):
        return os.path.isfile(self.dump_file)
