"""
File is for the 'blocks' that will make up the blockchain
"""

# needed for sha256 implementation
import hashlib

# needed to 'stringigy' object to then use encoding on for sha256
import json


# block class for container to hold data
class Block:
    # methods
    def __init__(self, index, timestamp, data, prev_hash = ''):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        # need to convert to entire to string as python is giving operand issues
        return_string = str(self.index) + self.prev_hash + self.timestamp + str(json.dumps(self.data))
        return hashlib.sha256(return_string.encode()).hexdigest()
