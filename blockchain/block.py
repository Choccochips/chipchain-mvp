"""
File is for the 'blocks' that will make up the blockchain
"""

# needed for sha256 implementation
import hashlib

# needed to 'stringigy' object to then use encoding on for sha256
import json

from blockchain.transaction import Transaction

# block class for container to hold data
class Block:
    # methods
    def __init__(self, timestamp, transactions, prev_hash = ''):
        self.timestamp = timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash

        # value added to spice up hash so we can "mine" on rehash until we get 'n' number of prefix zeroes
        self.nonce = 0
        self.hash = self.calc_hash()

    def calc_hash(self):
        # transform transactions to pass as arg
        t_data = [t.to_dict() for t in self.transactions]
        # need to convert to entire to string as python is giving operand issues
        return_string = str(self.prev_hash) + str(self.timestamp) + str(json.dumps(t_data)) + str(self.nonce)
        return hashlib.sha256(return_string.encode()).hexdigest()

    # to avoid people spamming blocks, we add proof of work, using a set number of prefix zeros needed
    # to be achieved by hash before block is considered 'mined'. The more zeroes, the greater the amount
    # of tries needed to 'mine' the block
    def mine_block(self, difficulty):
        # with python, there is a thing called string multiplication, which nth-plicates strings
        # since we want the prefix to be n-zeroes long, we just multiply (n-plicate) the zero to match so we know
        # what to look for when mining. Was a bug as loop was running forever since 0 != any string greater than a single 0
        target = '0' * difficulty
        while self.hash[0:difficulty] != target:
            self.nonce += 1
            self.hash = self.calc_hash()