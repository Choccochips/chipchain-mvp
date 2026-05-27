
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

contract_code = {
    'create_escrow': create_escrow,
    'release_escrow': release_escrow,
    'refund': refund
}