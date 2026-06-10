"""

This file will handle funcs related to voting power and proposals.
Voting power is derived from token balance. Proposals can be created by admins,
voted on by anyone with voting power, and resolve based on a quorum + majority.

"""

# constants for the chain rules
MIN_TOKENS_FOR_VOTING = 10
VOTING_PERIOD_BLOCKS = 5
QUORUM = 50

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

# create a new proposal, admin only
def create_proposal(state, args, caller, chain):
    # only admins can propose
    if caller not in chain.admins:
        raise Exception("Only admins can create proposals!...")
    
    # set up proposals dict if first time
    if 'proposals' not in state:
        state['proposals'] = {}
    
    # build a unique id from title + caller + count
    proposal_id = f"{caller[:8]}-{len(state['proposals'])}"

    # store the proposal
    state['proposals'][proposal_id] = {
        'id': proposal_id,
        'title': args['title'],
        'description': args.get('description', ''),
        'creator': caller,
        'created_at_block': len(chain.chain),  # current chain length when created
        'votes': {},  # wallet -> 'yes'/'no'/'abstain'
        'status': 'open'
    }
    return proposal_id

# cast a vote on a proposal
def cast_vote(state, args, caller, chain):
    proposal_id = args['proposal_id']
    choice = args['choice']  # 'yes', 'no', or 'abstain'

    # check that the proposal exists
    if 'proposals' not in state or proposal_id not in state['proposals']:
        raise Exception("Proposal does not exist!...")
    
    proposal = state['proposals'][proposal_id]

    # check voting choice is valid
    if choice not in ('yes', 'no', 'abstain'):
        raise Exception("Vote must be 'yes', 'no', or 'abstain'!...")

    # check voter has voting power
    voter_power = chain.get_balance(caller)
    if voter_power < MIN_TOKENS_FOR_VOTING:
        raise Exception("Voter does not have enough voting power!...")
    
    # check voting period is still open
    if len(chain.chain) > proposal['created_at_block'] + VOTING_PERIOD_BLOCKS:
        raise Exception("Voting period has ended!...")

    # check if already voted - reject re-votes for now
    if caller in proposal['votes']:
        raise Exception("Wallet has already voted on this proposal!...")
    
    # record the vote
    proposal['votes'][caller] = choice
    return choice

# tally and resolve a proposal after voting period ends
def resolve_proposal(state, args, caller, chain):
    proposal_id = args['proposal_id']

    if 'proposals' not in state or proposal_id not in state['proposals']:
        raise Exception("Proposal does not exist!...")
    
    proposal = state['proposals'][proposal_id]

    # cant resolve if voting period is still going
    if len(chain.chain) <= proposal['created_at_block'] + VOTING_PERIOD_BLOCKS:
        raise Exception("Voting period is still open!...")
    
    # already resolved
    if proposal['status'] != 'open':
        return proposal['status']

    # tally votes weighted by current voting power
    yes_power = 0
    no_power = 0
    abstain_power = 0

    for voter, choice in proposal['votes'].items():
        power = chain.get_balance(voter)
        # only count if they still have voting power
        if power < MIN_TOKENS_FOR_VOTING:
            continue
        if choice == 'yes':
            yes_power += power
        elif choice == 'no':
            no_power += power
        else:
            abstain_power += power

    # check quorum (total participating power)
    total_power = yes_power + no_power + abstain_power
    if total_power < QUORUM:
        proposal['status'] = 'failed_quorum'
    elif yes_power > no_power:
        proposal['status'] = 'passed'
    else:
        proposal['status'] = 'rejected'

    # store the tally for reference
    proposal['final_tally'] = {
        'yes': yes_power,
        'no': no_power,
        'abstain': abstain_power
    }
    return proposal['status']

# get a single proposal
def get_proposal(state, args, caller, chain):
    proposal_id = args['proposal_id']
    if 'proposals' not in state or proposal_id not in state['proposals']:
        raise Exception("Proposal does not exist!...")
    return dict(state['proposals'][proposal_id])

# list all proposals
def get_all_proposals(state, args, caller, chain):
    if 'proposals' not in state:
        return {}
    return dict(state['proposals'])

contract_code = {
    'is_admin': is_admin,
    'get_voting_power': get_voting_power,
    'get_admins': get_admins,
    'get_all_voters': get_all_voters,
    'create_proposal': create_proposal,
    'cast_vote': cast_vote,
    'resolve_proposal': resolve_proposal,
    'get_proposal': get_proposal,
    'get_all_proposals': get_all_proposals
}