"""
File is for the actual 'chain' portion of this blockchain 
"""

# import json for testing
import json

# import Block from block.py to create chain
from blockchain.block import Block

# since we dont have CONST keyword in python, will be using Final to flag for changes in place of that
from typing import Final

class Blockchain:
    def __init__(self):
        self.chain = []

        # start off chain w/ genesis block
        self.chain.append(self.create_genesis_block())

        # set difficulty of mining, which will affect speed at which blocks can be created (AKA proof of work)
        self.difficulty = 5

    # a gensis block is the first block of a blockchain and requires some special handling
    def create_genesis_block(self):
        return Block(0, "05/12/2026", "Creation of Genesis block", "0" )
    
    def get_curr_block(self):
        return self.chain[len(self.chain) - 1]

    def add_block(self, new_block):
        new_block.prev_hash = self.get_curr_block().hash

        # need to mine block to add, slowing process down a bit
        new_block.mine_block(self.difficulty)

        self.chain.append(new_block)

    def is_chain_valid(self):
        # loop through chain checking hash matches (curr into prev of next block)
        # skipping gen block
        for i in range(1, len(self.chain)):
            curr_block: Final[Block] = self.chain[i]
            prev_block: Final[Block] = self.chain[i-1]

            if curr_block.hash != curr_block.calc_hash():
                # hash is not valid
                return False
            
            if curr_block.prev_hash != prev_block.hash:
                return False
        
        # else things look good
        return True


# test run for curr blockchain code
chip_chain = Blockchain()


"""

Various tests for output while developing

"""

#print(f"Is chain valid? : {chip_chain.is_chain_valid()}")

# output test
#for block in chip_chain.chain:
#    print(f"Block {block.index} | Hash: {block.hash} \nPrev: {block.prev_hash}")

print("Mining block 1... \n")
block_1 = Block( 1, "05/12/2026", {"value": 4})
chip_chain.add_block(block_1)
print(f"Hash: {block_1.hash}\n")

print("Mining block 2... \n")
block_2 = Block( 2, "05/12/2026", {"value": 14})
chip_chain.add_block(block_2)
print(f"Hash: {block_2.hash}\n")