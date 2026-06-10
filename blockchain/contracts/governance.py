"""

This file will handle funcs related to voting power. There is no decision making component yet
Just need to be able to see if we can pick up on wallet power based on tokens

"""

# constants for the chain rule
MIN_TOKENS_FOR_VOTING = 10

# check if a wallet is an admin (set at genesis)
def is_admin(state, args, caller, chain):
    wallet = args['wallet']
    return wallet in chain.admins

# get a wallet's voting power based on token balance
def get_voting_power(state, args, caller, chain):
    wallet = args['wallet']
    balance = chain.get_balance(wallet)

    # no voting power if below threshold
    if balance < MIN_TOKENS_FOR_VOTING:
        return 0
    
    # voting power is just equal to balance (1:1)
    return balance

# return all admins from genesis
def get_admins(state, args, caller, chain):
    return list(chain.admins)

# return all wallets with voting power and their amount
def get_all_voters(state, args, caller, chain):
    voters = {}
    # walk through all known wallets on the chain
    for wallet in chain.get_all_wallets():
        power = chain.get_balance(wallet)
        if power >= MIN_TOKENS_FOR_VOTING:
            voters[wallet] = power
    return voters

contract_code = {
    'is_admin': is_admin,
    'get_voting_power': get_voting_power,
    'get_admins': get_admins,
    'get_all_voters': get_all_voters
}