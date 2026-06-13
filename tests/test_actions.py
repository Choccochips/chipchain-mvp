"""

This file is to be used for testing proposal action handlers

"""
# imports
from blockchain.transaction import Transaction
from blockchain.contracts.governance import contract_code
from tests.utils import fresh_chain, log, header

NAME = "Governance action handlers"

# helper to advance past the voting period by mining empty blocks
def advance_past_voting_period(chain, miner):
    for _ in range(chain.config['voting']['period_blocks'] + 1):
        chain.mine_pending_transactions(miner)

# helper to create + vote yes + resolve a proposal in one shot
def run_passing_proposal(chain, genesis, voters, contract_address, title, action):
    # admin creates proposal
    tx_propose = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='create_proposal', function_args={'title': title, 'action': action})
    tx_propose.sign_transaction(genesis['private'])
    proposal_id = chain.add_transaction(tx_propose)
    chain.mine_pending_transactions(genesis['public'])

    # every voter votes yes to make sure we hit quorum and majority
    for voter in voters:
        tx_vote = Transaction(voter['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='cast_vote', function_args={'proposal_id': proposal_id, 'choice': 'yes'})
        tx_vote.sign_transaction(voter['private'])
        chain.add_transaction(tx_vote)
        chain.mine_pending_transactions(genesis['public'])

    # mine past voting period
    advance_past_voting_period(chain, genesis['public'])

    # resolve
    tx_resolve = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='resolve_proposal', function_args={'proposal_id': proposal_id})
    tx_resolve.sign_transaction(genesis['private'])
    status = chain.add_transaction(tx_resolve)
    chain.mine_pending_transactions(genesis['public'])
    return proposal_id, status


def run():
    header(NAME)

    # set up chain with genesis and pre-funded wallets
    chain, genesis, wallets = fresh_chain()
    manufacturer = wallets['manufacturer']
    certifier = wallets['certifier']
    retailer = wallets['retailer']

    # deploy governance contract once, reuse for the whole test
    tx_deploy = Transaction(genesis['public'], None, 0, tx_type='deploy_contract', contract_code=contract_code)
    tx_deploy.sign_transaction(genesis['private'])
    try:
        chain.add_transaction(tx_deploy)
        chain.mine_pending_transactions(genesis['public'])
        contract_address = tx_deploy.calc_hash()
        log(True, f"Governance contract deployed at {contract_address[:16]}...")
    except Exception as e:
        log(False, f"Deploy failed: {e}")
        return

    # voters that have voting power
    voters = [manufacturer, certifier, retailer]

    # signal action - passes with no state change
    print()
    _, status = run_passing_proposal(chain, genesis, voters, contract_address, "Test signal", {'type': 'signal', 'args': {}})
    log(status == 'passed', f"Signal proposal status: {status}")

    # add_admin action - manufacturer becomes admin
    print()
    _, status = run_passing_proposal(chain, genesis, voters, contract_address, "Promote manufacturer", {'type': 'add_admin', 'args': {'wallet': manufacturer['public']}})
    log(status == 'passed', f"Add admin proposal status: {status}")

    # verify manufacturer is now admin via is_admin call
    tx_check = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='is_admin', function_args={'wallet': manufacturer['public']})
    tx_check.sign_transaction(genesis['private'])
    is_admin_now = chain.add_transaction(tx_check)
    chain.mine_pending_transactions(genesis['public'])
    log(is_admin_now == True, f"Manufacturer is now admin: {is_admin_now}")

    # remove_admin action - remove the manufacturer we just added
    print()
    _, status = run_passing_proposal(chain, genesis, voters, contract_address, "Demote manufacturer", {'type': 'remove_admin', 'args': {'wallet': manufacturer['public']}})
    log(status == 'passed', f"Remove admin proposal status: {status}")

    # verify manufacturer is no longer admin
    tx_check = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='is_admin', function_args={'wallet': manufacturer['public']})
    tx_check.sign_transaction(genesis['private'])
    is_admin_after = chain.add_transaction(tx_check)
    chain.mine_pending_transactions(genesis['public'])
    log(is_admin_after == False, f"Manufacturer no longer admin: {not is_admin_after}")

    # cant remove the last admin (genesis)
    print()
    _, status = run_passing_proposal(chain, genesis, voters, contract_address, "Remove genesis", {'type': 'remove_admin', 'args': {'wallet': genesis['public']}})
    log(status == 'passed_action_failed', f"Last-admin removal blocked: {status}")

    # change_parameter action - lower quorum from 50 to 30
    print()
    original_quorum = chain.config['voting']['quorum']
    _, status = run_passing_proposal(chain, genesis, voters, contract_address, "Lower quorum to 30", {'type': 'change_parameter', 'args': {'path': 'voting.quorum', 'value': 30}})
    log(status == 'passed', f"Change parameter proposal status: {status}")
    log(chain.config['voting']['quorum'] == 30, f"Quorum changed from {original_quorum} to {chain.config['voting']['quorum']}")

    # unknown action type - should fail at creation, not resolution
    print()
    tx_bad = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='create_proposal', function_args={'title': 'Bad action', 'action': {'type': 'nonexistent', 'args': {}}})
    tx_bad.sign_transaction(genesis['private'])
    try:
        chain.add_transaction(tx_bad)
        chain.mine_pending_transactions(genesis['public'])
        log(False, "Unknown action type should have failed but didn't")
    except Exception as e:
        log(True, f"Unknown action correctly rejected: {e}")

    # final chain integrity check
    print()
    log(chain.is_chain_valid(), "Chain valid after all action handler tests")