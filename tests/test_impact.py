"""

This file will be used for testing

"""
# imports
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from ecdsa import SigningKey, SECP256k1
from blockchain.contracts.impact import contract_code
from tests.utils import log, header

NAME = "Impact tracker smart contract"

def run():
    header(NAME)

    # create a blockchain and wallet
    chain = Blockchain()
    key = SigningKey.generate(curve=SECP256k1)
    wallet = key.get_verifying_key().to_string().hex()

    # This can stay throughout changes as we are just deploying the contract
    tx_deploy = Transaction(wallet, None, 0, tx_type='deploy_contract', contract_code=contract_code)
    tx_deploy.sign_transaction(key)
    try:
        chain.add_transaction(tx_deploy)
        chain.mine_pending_transactions(wallet)  # now that smart contract should be deployed
        contract_address = tx_deploy.calc_hash()  # to know which contract to call w/ address
        log(True, f"Impact contract deployed at {contract_address[:16]}...")
    except Exception as e:
        log(False, f"Deploy failed: {e}")
        return

    # log first impact
    tx_log1 = Transaction(wallet, None, 0, contract_address=contract_address, tx_type='call_contract', function_name='log_impact', function_args={'description': 'Test_log_1', 'value': 1})
    tx_log1.sign_transaction(key)
    try:
        chain.add_transaction(tx_log1)  # will need this ID later
        chain.mine_pending_transactions(wallet)
        log(True, "Impact logged: Test_log_1 (value: 1)")
    except Exception as e:
        log(False, f"First impact log failed: {e}")
        return

    # one more impact
    tx_log2 = Transaction(wallet, None, 0, contract_address=contract_address, tx_type='call_contract', function_name='log_impact', function_args={'description': 'Testing_log_2', 'value': 2})
    tx_log2.sign_transaction(key)
    try:
        chain.add_transaction(tx_log2)
        chain.mine_pending_transactions(wallet)
        log(True, "Impact logged: Testing_log_2 (value: 2)")
    except Exception as e:
        log(False, f"Second impact log failed: {e}")
        return

    # output
    contract = chain.smart_contracts[contract_address]
    history = contract.execute('get_history', {}, wallet)
    total = contract.execute('get_value_add', {}, wallet)

    log(len(history) == 2, f"History has {len(history)} entries")
    log(total == 3, f"Total impact: {total}")
    log(chain.is_chain_valid(), "Chain valid after impact tracking")