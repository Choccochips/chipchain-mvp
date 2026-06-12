"""

This file will handle funcs related to voting power and proposals.
Voting power is derived from token balance. Proposals can be created by admins,
voted on by anyone with voting power, and resolve based on a quorum + majority.

"""

# check if a wallet is an admin (set at genesis)
def is_admin(state, args, caller, chain):
    wallet = args['wallet']
    return wallet in chain.admins

# get a wallet's voting power based on token balance
def get_voting_power(state, args, caller, chain):
    wallet = args['wallet']
    balance = chain.get_balance(wallet)

    # no voting power if below threshold
    if balance < chain.config['voting']['min_tokens']:
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
        if power >= chain.config['voting']['min_tokens']:
            voters[wallet] = power
    return voters

# action handlers

# add a wallet to chain.admins
def action_add_admin(state, args, caller, chain):
    wallet = args['wallet']
    chain.admins.add(wallet)
    return f"Admin added: {wallet[:16]}..."

# remove a wallet from chain.admins, cant remove the last one
def action_remove_admin(state, args, caller, chain):
    wallet = args['wallet']
    if wallet not in chain.admins:
        raise Exception("Wallet is not an admin!...")
    if len(chain.admins) <= 1:
        raise Exception("Cannot remove the last admin!...")
    chain.admins.remove(wallet)
    return f"Admin removed: {wallet[:16]}..."

# modify a value inside chain.config, path uses dot notation
def action_change_parameter(state, args, caller, chain):
    # path like 'voting.quorum' tells us where to write
    path = args['path'].split('.')
    target = chain.config
    # walk down to the parent dict
    for key in path[:-1]:
        if key not in target:
            raise Exception(f"Config path does not exist: {args['path']}!...")
        target = target[key]
    # set the leaf value
    if path[-1] not in target:
        raise Exception(f"Config path does not exist: {args['path']}!...")
    target[path[-1]] = args['value']
    return f"Set {args['path']} = {args['value']}"

# pure signal, no state change
def action_signal(state, args, caller, chain):
    return "Signal recorded"

# registry - new action types are one function + one entry here
ACTION_HANDLERS = {
    'add_admin': action_add_admin,
    'remove_admin': action_remove_admin,
    'change_parameter': action_change_parameter,
    'signal': action_signal
}

# create a new proposal, admin only
def create_proposal(state, args, caller, chain):
    # only admins can propose
    if caller not in chain.admins:
        raise Exception("Only admins can create proposals!...")
    
    # validate the action payload, default to signal if none provided
    action = args.get('action', {'type': 'signal', 'args': {}})
    if action['type'] not in ACTION_HANDLERS:
        raise Exception(f"Unknown action type: {action['type']}!...")
    
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
        'status': 'open',
        'action': action # what will happen when the proposal passes
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
    if voter_power < chain.config['voting']['min_tokens']:
        raise Exception("Voter does not have enough voting power!...")
    
    # check voting period is still open
    if len(chain.chain) > proposal['created_at_block'] + chain.config['voting']['period_blocks']:
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
    if len(chain.chain) <= proposal['created_at_block'] + chain.config['voting']['period_blocks']:
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
        if power < chain.config['voting']['min_tokens']:
            continue
        if choice == 'yes':
            yes_power += power
        elif choice == 'no':
            no_power += power
        else:
            abstain_power += power

    # store the tally for reference (before any return)
    total_power = yes_power + no_power + abstain_power
    proposal['final_tally'] = {
        'yes': yes_power,
        'no': no_power,
        'abstain': abstain_power
    }

    # quorum check
    if total_power < chain.config['voting']['quorum']:
        proposal['status'] = 'failed_quorum'
        return proposal['status']
    
    # majority check, dispatch action if passed
    if yes_power > no_power:
        action = proposal['action']
        handler = ACTION_HANDLERS[action['type']]
        try:
            result = handler(state, action.get('args', {}), caller, chain)
            proposal['status'] = 'passed'
            proposal['action_result'] = result
        except Exception as e:
            # action execution failed but the vote passed, be honest about it
            proposal['status'] = 'passed_action_failed'
            proposal['action_error'] = str(e)
        return proposal['status']
    else:
        proposal['status'] = 'rejected'
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