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

# another key to test 
key2 = SigningKey.generate(curve=SECP256k1)
wallet2 = key2.get_verifying_key().to_string().hex()

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

# Escrow contract, will have something to do with reputation later
def create_escrow(state, args, caller):
    # create a unique ID
    escrow_id = caller + '-' + args['recipient'] + '-' + str(len(state)) # added counter to have a unique addition to the id
    entry = {
        'creator': caller,
        'recipient': args['recipient'],
        'value': args['value'],
        'status': 'pending'
    }

    # store in state
    state[escrow_id] = entry

    # return escrow ID so caller has it
    return escrow_id

def release_escrow(state, args, caller):
    id = args['escrow_id'] # we look up the id but still need to use it to find escrow entry
    # some checks
    if id not in state:
        raise Exception("This escrow ID does not exist!...")
    escrow_entry = state[id]
    if caller != escrow_entry['creator']:
        raise Exception("Only creator can call this function!...")
    # change the status if it is still locked
    if escrow_entry['status'] == 'pending':
        escrow_entry['status'] = 'released'
    return escrow_entry['status']

def refund(state, args, caller):
    # need to get ID
    id = args['escrow_id']
    # check that the id is in the list of escrow entries
    if id not in state:
        raise Exception("This escrow ID does not exist!...")
    escrow_entry = state[id]

    # check that the caller is the creator in state
    if caller != escrow_entry['creator']:
        raise Exception("Only creator can call this function!...")
    # update status
    if escrow_entry['status'] == 'pending':
        escrow_entry['status'] = 'refunded'


"""

Packaging up functions into 'contract_code' for testing

"""

contract_code = {
    # add functions we just defined
    'create_escrow': create_escrow,
    'release_escrow': release_escrow,
    'refund': refund
}


# This can stay throughout changes as we are jusy deploying the contract 
tx_1 = Transaction(wallet,None, 0, tx_type = 'deploy_contract', contract_code=contract_code)
tx_1.sign_transaction(key)
chain1.add_transaction(tx_1)
chain1.mine_pending_transactions(wallet) # now that smart contract should be deployed

contract_address = tx_1.calc_hash() # to know which contract to call w/ address
tx_2 = Transaction(wallet, None, 0, contract_address=contract_address, tx_type= 'call_contract', function_name='create_escrow', function_args={'recipient': wallet2, 'value': 500})
tx_2.sign_transaction(key)
chain1.add_transaction(tx_2)
chain1.mine_pending_transactions(wallet)

# we will need to get the escrow_id to then release the funds, we know it gets returned from executing the function. store address
contract = chain1.smart_contracts[contract_address]

# one more impact
tx_3 = Transaction(wallet, None, 0, contract_address=contract_address, tx_type= 'call_contract', function_name='release_escrow', function_args={'escrow_id': escrow_id})
tx_3.sign_transaction(key)
chain1.add_transaction(tx_3)
chain1.mine_pending_transactions(wallet)

# output 
contract = chain1.smart_contracts[contract_address]
print(f"History: ", contract.execute('get_history', {}, wallet))
print(f"Total impact: ", contract.execute('get_value_add', {}, wallet))

