"""

This file is to be used for testing proposals and voting

"""

# imports
from blockchain.transaction import Transaction
from blockchain.contracts.governance import contract_code
from tests.utils import fresh_chain, log, header

NAME = "Governance proposals & voting"

def run():
    header(NAME)

    # set up chain with genesis block and pre-funded wallets
    chain, genesis, wallets = fresh_chain()
    manufacturer = wallets['manufacturer']
    certifier = wallets['certifier']
    retailer = wallets['retailer']

    #  deploy governance contract
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

    # admin creates a proposal
    tx_propose = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='create_proposal', function_args={'title': 'Test proposal', 'description': 'A signaling proposal for testing'})
    tx_propose.sign_transaction(genesis['private'])
    try:
        proposal_id = chain.add_transaction(tx_propose)
        chain.mine_pending_transactions(genesis['public'])
        log(True, f"Proposal created with id: {proposal_id}")
    except Exception as e:
        log(False, f"Proposal creation failed: {e}")
        return

    # non-admin tries to propose, should fail
    tx_bad_propose = Transaction(manufacturer['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='create_proposal', function_args={'title': 'Bad proposal'})
    tx_bad_propose.sign_transaction(manufacturer['private'])
    try:
        chain.add_transaction(tx_bad_propose)
        chain.mine_pending_transactions(genesis['public'])
        log(False, "Non-admin proposal should have failed but didn't")
    except Exception as e:
        log(True, f"Non-admin proposal correctly rejected: {e}")

    # cast some votes
    # manufacturer votes yes
    tx_vote_yes = Transaction(manufacturer['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='cast_vote', function_args={'proposal_id': proposal_id, 'choice': 'yes'})
    tx_vote_yes.sign_transaction(manufacturer['private'])
    try:
        chain.add_transaction(tx_vote_yes)
        chain.mine_pending_transactions(genesis['public'])
        log(True, "Manufacturer voted yes")
    except Exception as e:
        log(False, f"Manufacturer vote failed: {e}")

    # certifier votes no
    tx_vote_no = Transaction(certifier['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='cast_vote', function_args={'proposal_id': proposal_id, 'choice': 'no'})
    tx_vote_no.sign_transaction(certifier['private'])
    try:
        chain.add_transaction(tx_vote_no)
        chain.mine_pending_transactions(genesis['public'])
        log(True, "Certifier voted no")
    except Exception as e:
        log(False, f"Certifier vote failed: {e}")

    # retailer votes abstain
    tx_vote_abstain = Transaction(retailer['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='cast_vote', function_args={'proposal_id': proposal_id, 'choice': 'abstain'})
    tx_vote_abstain.sign_transaction(retailer['private'])
    try:
        chain.add_transaction(tx_vote_abstain)
        chain.mine_pending_transactions(genesis['public'])
        log(True, "Retailer abstained")
    except Exception as e:
        log(False, f"Retailer vote failed: {e}")

    # double voting should fail
    tx_double = Transaction(manufacturer['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='cast_vote', function_args={'proposal_id': proposal_id, 'choice': 'no'})
    tx_double.sign_transaction(manufacturer['private'])
    try:
        chain.add_transaction(tx_double)
        chain.mine_pending_transactions(genesis['public'])
        log(False, "Double vote should have failed but didn't")
    except Exception as e:
        log(True, f"Double vote correctly rejected: {e}")

    # try to resolve too early, should fail
    tx_early_resolve = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='resolve_proposal', function_args={'proposal_id': proposal_id})
    tx_early_resolve.sign_transaction(genesis['private'])
    try:
        chain.add_transaction(tx_early_resolve)
        chain.mine_pending_transactions(genesis['public'])
        log(False, "Early resolve should have failed but didn't")
    except Exception as e:
        log(True, f"Early resolve correctly rejected: {e}")

    for _ in range(5):
        chain.mine_pending_transactions(genesis['public'])
    log(True, "Mined empty blocks to advance past voting period")

    # now resolve
    tx_resolve = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='resolve_proposal', function_args={'proposal_id': proposal_id})
    tx_resolve.sign_transaction(genesis['private'])
    try:
        status = chain.add_transaction(tx_resolve)
        chain.mine_pending_transactions(genesis['public'])
        # manufacturer voted yes (300), certifier voted no (300), retailer abstained (300)
        # yes_power = 300, no_power = 300, abstain_power = 300, total = 900
        # quorum met (>=50), but yes is not > no, so rejected
        # all of this is subject to change down the road 
        log(status == 'rejected', f"Proposal status: {status} (expected rejected - tie vote)")
    except Exception as e:
        log(False, f"Resolve failed: {e}")

    # final chain validity
    print()
    log(chain.is_chain_valid(), "Chain valid after proposals & voting")