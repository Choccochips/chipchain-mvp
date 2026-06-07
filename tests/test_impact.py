"""

This file will be used for testing

"""
# imports
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from ecdsa import SigningKey, SECP256k1

from blockchain.contracts.impact import contract_code

# create a blockchain and wallet
chain1 = Blockchain()
key = SigningKey.generate(curve=SECP256k1)
wallet = key.get_verifying_key().to_string().hex()

# This can stay throughout changes as we are jusy deploying the contract 
tx_1 = Transaction(wallet,None, 0, tx_type = 'deploy_contract', contract_code=contract_code)
tx_1.sign_transaction(key)
chain1.add_transaction(tx_1)
chain1.mine_pending_transactions(wallet) # now that smart contract should be deployed

contract_address = tx_1.calc_hash() # to know which contract to call w/ address
tx_2 = Transaction(wallet, None, 0, contract_address=contract_address, tx_type= 'call_contract', function_name='log_impact', function_args={'description': 'Test_log_1', 'value': 1})
tx_2.sign_transaction(key)
escrow_id = chain1.add_transaction(tx_2) # will need this ID later
chain1.mine_pending_transactions(wallet)

# one more impact
tx_3 = Transaction(wallet, None, 0, contract_address=contract_address, tx_type= 'call_contract', function_name='log_impact', function_args={'description': 'Testing_log_2', 'value': 2})
tx_3.sign_transaction(key)
chain1.add_transaction(tx_3)
chain1.mine_pending_transactions(wallet)

# output 
contract = chain1.smart_contracts[contract_address]
print(f"History: ", contract.execute('get_history', {}, wallet))
print(f"Total impact: ", contract.execute('get_value_add', {}, wallet))
