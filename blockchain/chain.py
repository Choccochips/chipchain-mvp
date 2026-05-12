"""
File is for the actual 'chain' portion of this blockchain 
"""

# import json for testing
import json

# import Block from block.py to create chain
from blockchain.block import Block

class Blockchain:
    def __init__(self):
        self.chain = []
        # start off chain w/ genesis block
        self.chain.append(self.create_genesis_block())
   
    # a gensis block is the first block of a blockchain and requires some special handling
    def create_genesis_block(self):
        return Block(0, "05/12/2026", "Creation of Genesis block", "0" )
    
    def get_curr_block(self):
        return self.chain[len(self.chain) - 1]

    def add_block(self, new_block):
        new_block.prev_hash = self.get_curr_block().hash
        new_block.hash = new_block.calc_hash()
        self.chain.append(new_block)

# test run for curr blockchain code
chip_chain = Blockchain()

# create some blocks
block_1 = Block( 1, "05/12/2026", {"value": 4})
block_2 = Block( 2, "05/12/2026", {"value": 14})
block_3 = Block( 3, "05/12/2026", {"value": 24})

# add blocks to chain
chip_chain.add_block(block_1)
chip_chain.add_block(block_2)
chip_chain.add_block(block_3)


# output test
for block in chip_chain.chain:
    print(f"Block {block.index} | Hash: {block.hash} \nPrev: {block.prev_hash}")
