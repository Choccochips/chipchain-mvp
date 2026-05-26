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

# creating a transaction
tx_1 = Transaction(wallet, None, 0, tx_type='deploy_contract', contract_code=contract_code)
tx_1.sign_transaction(key)

# now that this is all squared away, we can add it to the chain
chain1.add_transaction(tx_1)
# mine the block the tx currently is in (only block we have rn)
chain1.mine_pending_transactions(wallet)
contract_address = tx_1.calc_hash()

# since we are calling an exisitng contract, the arguments passed will be a little different
tx_2 = Transaction(wallet, None, 0, tx_type='call_contract',contract_address=contract_address, function_name='mint', function_args={'amount': 100})
tx_2.sign_transaction(key)
chain1.add_transaction(tx_2)
chain1.mine_pending_transactions(wallet)

# call get balance to see state
tx_3 = Transaction(wallet, None, 0, tx_type='call_contract', contract_address=contract_address, function_name = 'get_balance', function_args={})
tx_3.sign_transaction(key)
chain1.add_transaction(tx_3)
chain1.mine_pending_transactions(wallet)

contract = chain1.smart_contracts[contract_address]
result = contract.execute('get_balance', {}, wallet)

# see what shakes
print(f"Balance: {result}")

