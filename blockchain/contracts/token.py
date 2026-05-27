
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