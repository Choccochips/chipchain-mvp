"""

This file will have test cases for the blockchain 

"""


# imports

from blockchain.block import Block
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from ecdsa import SigningKey, VerifyingKey, SECP256k1


# create a blockchain instance
chain1 = Blockchain()

key = SigningKey.generate(curve=SECP256k1) # rememeber this is private key, so we need to get the correspdnding wallet
wallet = key.get_verifying_key().to_string().hex()

# here is the simple smart contract we will be testing
def get_balance(state, args, caller):
    return state.get(caller, 0)

def mint(state, args, caller):
    state[caller] = state.get(caller, 0) + args['amount']

# stuff it into a dict for later use
contract_code = {
    'get_balance': get_balance,
    'mint': mint
}

