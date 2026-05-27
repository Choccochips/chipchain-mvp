"""

This file will be used for testing

"""
# imports
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from ecdsa import SigningKey, VerifyingKey, SECP256k1

from blockchain.contracts.escrow import contract_code

# create a blockchain instance
chain1 = Blockchain()

# set up some wallet for the testing
key = SigningKey.generate(curve=SECP256k1) # rememeber this is private key, so we need to get the correspdnding wallet
wallet = key.get_verifying_key().to_string().hex()

key2 = SigningKey.generate(curve = SECP256k1)
wallet2 = key2.get_verifying_key().to_string().hex()

# creating a transaction
tx_1 = Transaction(wallet, None, 0, tx_type='deploy_contract', contract_code=contract_code)
tx_1.sign_transaction(key)

# now that this is all squared away, we can add it to the chain
chain1.add_transaction(tx_1)
# mine the block the tx currently is in (only block we have rn)
chain1.mine_pending_transactions(wallet)
contract_address = tx_1.calc_hash()

# since we are calling an exisitng contract, the arguments passed will be a little different
tx_2 = Transaction(wallet, None, 0, tx_type='call_contract',contract_address=contract_address, function_name='create_escrow', function_args={'recipient': wallet2, 'value': 500 })
tx_2.sign_transaction(key)
escrow_id = chain1.add_transaction(tx_2) # remember we changed this to return the escrow_id
chain1.mine_pending_transactions(wallet)

# releasing escrow
tx_3 = Transaction(wallet, None, 0, tx_type='call_contract', contract_address=contract_address, function_name = 'release_escrow', function_args={'escrow_id': escrow_id})
tx_3.sign_transaction(key)
chain1.add_transaction(tx_3)
chain1.mine_pending_transactions(wallet)

contract = chain1.smart_contracts[contract_address]
escrow = contract.state[escrow_id]

# see what shakes
print(f"Escrow: {escrow}")

