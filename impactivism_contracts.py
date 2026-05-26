"""

Smart Contracts to be used on the platform

"""


# imports

from blockchain.block import Block
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from ecdsa import SigningKey, VerifyingKey, SECP256k1

# create a blockchain and wallet
chain1 = Blockchain()
key = SigningKey.generate(curve=SECP256k1)
wallet = key.get_verifying_key().to_string().hex()

# --- define functions to be used --- 

# this will add an entry to a caller's list 
def log_impact(state, args, caller):
    caller_list = state.get(caller, [])
    entry = {'description': args['description'], 'value': args['value']}
    caller_list.append(entry)
    
    # save back to state
    state[caller] = caller_list

# this fx is just going to return all entries that have been logged for a wallet
def get_history(state, args, caller):
    caller_list = state.get(caller, [])
    return caller_list

# just cycle through the list to add up the total value add
def get_value_add(state, args, caller):
    caller_list = state.get(caller, [])

    # start off value add at zero and add as we work through each entry
    value_added = 0

    for values in caller_list:
        value_added +=  values['value']
     
    return value_added

contract_code = {
    # add functions we just defined
    'log_impact': log_impact,
    'get_history': get_history,
    'get_value_add': get_value_add
}

# full test cycle
tx_1 = Transaction(wallet,None, 0, tx_type = 'deploy_contract', contract_code=contract_code)
tx_1.sign_transaction(key)
chain1.add_transaction(tx_1)
chain1.mine_pending_transactions(wallet) # now that smart contract should be deployed

contract_address = tx_1.calc_hash() # to know which contract to call w/ address
tx_2 = Transaction(wallet, None, amount = 0, contract_address=contract_address, tx_type= 'call_contract', function_name='log_impact', function_args={'description':'Packaged water bottle', 'value': 50})
tx_2.sign_transaction(key)
chain1.add_transaction(tx_2)
chain1.mine_pending_transactions(wallet)

# one more impact
tx_3 = Transaction(wallet, None, amount = 0, tx_type= 'call_contract', contract_address=contract_address, contract_code=contract_code, function_name='log_impact', function_args={'description': 'sold water', 'value': 25})
tx_3.sign_transaction(key)
chain1.add_transaction(tx_3)
chain1.mine_pending_transactions(wallet)

# output
contract = chain1.smart_contracts[contract_address]
print(f"History: ", contract.execute('get_history', {}, wallet))
print(f"Total impact: ", contract.execute('get_value_add', {}, wallet))

