
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

# contract code to be imported
contract_code = {
    'log_impact': log_impact,
    'get_history': get_history,
    'get_value_add': get_value_add
}

