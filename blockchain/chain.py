"""
File is for the actual 'chain' portion of this blockchain 
"""

# import json for testing
import json

# import Block from block.py to create chain
from blockchain.block import Block
from blockchain.transaction import Transaction

# since we dont have CONST keyword in python, will be using Final to flag for changes in place of that
from typing import Final

# for timestamp on mining_reward part
import time

from ecdsa import SigningKey, SECP256k1

class Blockchain:
    def __init__(self):
        self.chain = []

        # start off chain w/ genesis block
        self.chain.append(self.create_genesis_block())

        # set difficulty of mining, which will affect speed at which blocks can be created (AKA proof of work)
        self.difficulty = 5

        # Transaction related portion of chain
        # need a bucket for pending transactions while blocks are mined
        self.pending_transactions = []

        # set up reward (coins later)
        self.mining_reward = 100

    # a gensis block is the first block of a blockchain and requires some special handling
    def create_genesis_block(self):
        return Block("05/12/2026", [], "0")
    
    def get_curr_block(self):
        return self.chain[len(self.chain) - 1]

    def mine_pending_transactions(self, reward_address):
        new_block = Block(time.time(), self.pending_transactions, self.get_curr_block().hash)
        new_block.mine_block(self.difficulty)
        print("Block has been mined!...")
        self.chain.append(new_block)

        # reset array since block was mined AND then pay the person who mined!
        reward_owed = Transaction(None, reward_address, self.mining_reward)
        self.pending_transactions = [reward_owed]

    def add_transaction(self, transaction):
        # perform checks
        if not transaction.sender_address or not transaction.recip_address:
            raise Exception("Both 'seneder' and 'recipient' address must be included for a transaction!...")
        
        if not transaction.is_valid():
            raise Exception("Cannot add invalid transaction to the chain!...")

        # if things looks solid then we can add this to the pending transactions list to be 'released' when respective block is mined
        self.pending_transactions.append(transaction)

    def get_balance(self,address):
        balance = 0

        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender_address == address:
                    balance -= transaction.amount
                
                if(transaction.recip_address == address):
                    balance += transaction.amount

        return balance


    def is_chain_valid(self):
        # loop through chain checking hash matches (curr into prev of next block)
        # skipping gen block
        for i in range(1, len(self.chain)):
            curr_block: Final[Block] = self.chain[i]
            prev_block: Final[Block] = self.chain[i-1]

            # added checks
            if not curr_block.has_valid_transactions():
                return False

            if curr_block.hash != curr_block.calc_hash():
                # hash is not valid
                return False
            
            if curr_block.prev_hash != prev_block.hash:
                return False
        
        # else things look good
        return True



"""

Various tests for output while developing

"""

#print(f"Is chain valid? : {chip_chain.is_chain_valid()}")

# output test
#for block in chip_chain.chain:
#    print(f"Block {block.index} | Hash: {block.hash} \nPrev: {block.prev_hash}")

#print("Mining block 1... \n")
#block_1 = Block( 1, "05/12/2026", {"value": 4})
#chip_chain.add_block(block_1)
#print(f"Hash: {block_1.hash}\n")

#print("Mining block 2... \n")
#block_2 = Block( 2, "05/12/2026", {"value": 14})
#chip_chain.add_block(block_2)
#print(f"Hash: {block_2.hash}\n")



# more testing
#my_key = SigningKey.from_string(bytes.fromhex("327e1c6b4137a0b805f4dd0563483fb922612d96b1a92fd2ef7f5a2e58f06cc0"), curve = SECP256k1)
#my_wallet = my_key.get_verifying_key().to_string().hex() 

# test run for curr blockchain code
#chip_chain = Blockchain()

# create new tx
#tx_1 = Transaction(my_wallet, 'public_key_goes_here', 100)
# sign tx
#tx_1.sign_transaction(my_key)
#chip_chain.add_transaction(tx_1)

#print("\nStarting miner...\n")
#chip_chain.mine_pending_transactions(my_wallet)

#print(f"\nBalance of wallet is {chip_chain.get_balance(my_wallet)}")

#print("\nStarting miner again...\n")
#chip_chain.mine_pending_transactions(my_wallet)

#print(f"\nBalance of wallet is {chip_chain.get_balance(my_wallet)}")


# chip_chain.create_transaction(Transaction("address_1","address_2", 100 ))
# chip_chain.create_transaction(Transaction("address_2", "address_1", 75))

# need ot create block to store transactions
# print("Starting to mine...")
# chip_chain.mine_pending_transactions("dummy_address_to_reward")

# print(f"Balance of miner 1 is {chip_chain.get_balance("dummy_address_to_reward")}")

# print("Starting to mine...")
# chip_chain.mine_pending_transactions("dummy_address_to_reward")
# print(f"Balance of miner 1 is {chip_chain.get_balance("dummy_address_to_reward")}")



