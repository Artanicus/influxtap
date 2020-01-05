import json, os

from . import xdg

class Cache():
    def __init__(self):
        # init XDG path to store in
        self.dump_file = xdg.initXDG('influxtap') + 'cache.json'

# dump provided datapoints cache data to a file
    def dump(self, datapoints):
        if len(datapoints) > 0:
            with open(self.dump_file, 'w') as fh:
                json.dump(datapoints, fh)
                return True
        else:
            return False

    def read(self):
        if self.exists():
            with open(self.dump_file, 'r') as fh:
                return json.load(fh)
        else:
            return None

    def clear(self):
        if self.exists():
            os.unlink(self.dump_file)
            return True
        else:
            return False

    def flush(self):
        out = read()
        clear()
        return out

    def exists(self):
        return os.path.isfile(self.dump_file)
