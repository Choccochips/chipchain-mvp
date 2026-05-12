# needed for sha256 implementation
import hashlib

# needed to 'stringigy' object to then use encoding on for sha256
import json


# block class for container to hold data
class Block:
    # methods
    def __init__(self, index, timestamp, data, prevHash = ''):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prevHash = prevHash
        self.hash = self.calc_Hash()

    def calc_Hash(self):
        return hashlib.sha256(self.index + self.prevHash + self.timestamp +  str(json.dumps(self.data)))
