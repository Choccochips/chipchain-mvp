"""

This file will be used for testing

"""
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from blockchain.contracts.escrow import contract_code
from ecdsa import SigningKey, SECP256k1
from tests.utils import log, header

NAME = "Escrow smart contract"

def run():
    header(NAME)

    chain = Blockchain()

    # set up some wallet for the testing
    key1 = SigningKey.generate(curve=SECP256k1)
    wallet1 = key1.get_verifying_key().to_string().hex()

    key2 = SigningKey.generate(curve=SECP256k1)
    wallet2 = key2.get_verifying_key().to_string().hex()

    # deploy escrow contract
    tx_deploy = Transaction(wallet1, None, 0, tx_type='deploy_contract', contract_code=contract_code)
    tx_deploy.sign_transaction(key1)
    try:
        chain.add_transaction(tx_deploy)
        chain.mine_pending_transactions(wallet1)
        contract_address = tx_deploy.calc_hash()
        log(True, f"Escrow contract deployed at {contract_address[:16]}...")
    except Exception as e:
        log(False, f"Deploy failed: {e}")
        return

    # create escrow
    tx_create = Transaction(wallet1, None, 0, tx_type='call_contract', contract_address=contract_address, function_name='create_escrow', function_args={'recipient': wallet2, 'value': 500})
    tx_create.sign_transaction(key1)
    try:
        escrow_id = chain.add_transaction(tx_create)
        chain.mine_pending_transactions(wallet1)
        log(True, f"Escrow created: {escrow_id}")
    except Exception as e:
        log(False, f"Create escrow failed: {e}")
        return

    # release escrow
    tx_release = Transaction(wallet1, None, 0, tx_type='call_contract', contract_address=contract_address, function_name='release_escrow', function_args={'escrow_id': escrow_id})
    tx_release.sign_transaction(key1)
    try:
        chain.add_transaction(tx_release)
        chain.mine_pending_transactions(wallet1)
        log(True, "Escrow released")
    except Exception as e:
        log(False, f"Release escrow failed: {e}")
        return

    # verify escrow state to make sure things hit right
    contract = chain.smart_contracts[contract_address]
    escrow = contract.state[escrow_id]
    log(True, f"Escrow state: {escrow}")
    log(chain.is_chain_valid(), "Chain valid after escrow operations")