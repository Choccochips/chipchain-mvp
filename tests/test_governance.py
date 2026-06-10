"""

This file is to be used for testing

"""
# imports
from blockchain.transaction import Transaction
from blockchain.contracts.governance import contract_code
from ecdsa import SigningKey, SECP256k1
from tests.utils import fresh_chain, log, header

NAME = "Governance voting power"

def run():
    header(NAME)

    # set up chain with genesis block and pre-funded wallets
    chain, genesis, wallets = fresh_chain()

    # deploy the governance contract from the genesis wallet (the admin)
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

    # check that the genesis wallet is an admin
    tx_check_admin = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='is_admin', function_args={'wallet': genesis['public']})
    tx_check_admin.sign_transaction(genesis['private'])
    try:
        is_admin = chain.add_transaction(tx_check_admin)
        chain.mine_pending_transactions(genesis['public'])
        log(is_admin == True, f"Genesis wallet is admin: {is_admin}")
    except Exception as e:
        log(False, f"Admin check failed: {e}")
        return

    # check that a non-genesis wallet is NOT an admin
    manufacturer = wallets['manufacturer']
    tx_check_nonadmin = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='is_admin', function_args={'wallet': manufacturer['public']})
    tx_check_nonadmin.sign_transaction(genesis['private'])
    try:
        is_not_admin = chain.add_transaction(tx_check_nonadmin)
        chain.mine_pending_transactions(genesis['public'])
        log(is_not_admin == False, f"Manufacturer is admin: {is_not_admin}")
    except Exception as e:
        log(False, f"Non-admin check failed: {e}")
        return

    # check voting power for the genesis wallet (should be high - starts with 1000 tokens)
    tx_genesis_power = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='get_voting_power', function_args={'wallet': genesis['public']})
    tx_genesis_power.sign_transaction(genesis['private'])
    try:
        genesis_power = chain.add_transaction(tx_genesis_power)
        chain.mine_pending_transactions(genesis['public'])
        log(genesis_power >= 10, f"Genesis voting power: {genesis_power}")
    except Exception as e:
        log(False, f"Genesis power check failed: {e}")
        return

    # check voting power for a pre-funded wallet (300 tokens from fresh_chain)
    tx_mfr_power = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='get_voting_power', function_args={'wallet': manufacturer['public']})
    tx_mfr_power.sign_transaction(genesis['private'])
    try:
        mfr_power = chain.add_transaction(tx_mfr_power)
        chain.mine_pending_transactions(genesis['public'])
        log(mfr_power == 300, f"Manufacturer voting power: {mfr_power} (expected 300)")
    except Exception as e:
        log(False, f"Manufacturer power check failed: {e}")
        return

    # check the bad_actor wallet (unfunded, should have 0 voting power)
    bad_actor = wallets['bad_actor']
    tx_bad_power = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='get_voting_power', function_args={'wallet': bad_actor['public']})
    tx_bad_power.sign_transaction(genesis['private'])
    try:
        bad_power = chain.add_transaction(tx_bad_power)
        chain.mine_pending_transactions(genesis['public'])
        log(bad_power == 0, f"Bad actor voting power: {bad_power} (expected 0)")
    except Exception as e:
        log(False, f"Bad actor power check failed: {e}")
        return

    # transfer just enough so a wallet sits below the 10-token threshold
    tx_drain = Transaction(manufacturer['public'], genesis['public'], 295)
    tx_drain.sign_transaction(manufacturer['private'])
    try:
        chain.add_transaction(tx_drain)
        chain.mine_pending_transactions(genesis['public'])
        log(True, "Manufacturer drained to 5 tokens (below threshold)")
    except Exception as e:
        log(False, f"Drain failed: {e}")
        return

    # voting power should now be 0 since under 10 tokens
    tx_below_threshold = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='get_voting_power', function_args={'wallet': manufacturer['public']})
    tx_below_threshold.sign_transaction(genesis['private'])
    try:
        below = chain.add_transaction(tx_below_threshold)
        chain.mine_pending_transactions(genesis['public'])
        log(below == 0, f"Below-threshold voting power: {below} (expected 0)")
    except Exception as e:
        log(False, f"Below-threshold check failed: {e}")
        return

    # get all voters - should include genesis and any wallets still above threshold
    tx_all_voters = Transaction(genesis['public'], None, 0, tx_type='call_contract', contract_address=contract_address, function_name='get_all_voters', function_args={})
    tx_all_voters.sign_transaction(genesis['private'])
    try:
        voters = chain.add_transaction(tx_all_voters)
        chain.mine_pending_transactions(genesis['public'])
        log(True, f"Active voters: {len(voters)} wallet(s)")
        for w, p in voters.items():
            log(True, f"  {w[:16]}...: {p} power")
    except Exception as e:
        log(False, f"Get all voters failed: {e}")
        return

    # verify the chain is still valid after everything
    print()
    log(chain.is_chain_valid(), "Chain valid after governance operations")