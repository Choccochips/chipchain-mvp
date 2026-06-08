"""

This file is to be used for testing

"""

from blockchain.transaction import Transaction
from tests.utils import fresh_chain, log, header

NAME = "Chain integrity & tamper detection"


# will be deliberately tampering wtih different components of the blockchain and seeing if the network is able to 
# rebound and find homeostasis after
def run():
    header(NAME)
    chain, genesis, wallets = fresh_chain()

    # build up a few blocks
    for i in range(3):
        tx = Transaction(
            wallets['manufacturer']['public'],
            wallets['certifier']['public'],
            10
        )
        tx.sign_transaction(wallets['manufacturer']['private'])
        chain.add_transaction(tx)
        chain.mine_pending_transactions(genesis['public'])

    log(True, f"Built chain with {len(chain.chain)} blocks")
    log(chain.is_chain_valid(), "Clean chain validates")

    #  tamper with transaction amount
    original_amount = chain.chain[1].transactions[0].amount
    chain.chain[1].transactions[0].amount = 99999
    tampered = not chain.is_chain_valid()
    log(tampered, "Tampered transaction amount detected")
    chain.chain[1].transactions[0].amount = original_amount

    # tamper with block hash
    original_hash = chain.chain[2].hash
    chain.chain[2].hash = "0" * 64
    tampered2 = not chain.is_chain_valid()
    log(tampered2, "Tampered block hash detected")
    chain.chain[2].hash = original_hash

    # tamper with prev_hash link
    original_prev = chain.chain[2].prev_hash
    chain.chain[2].prev_hash = "0" * 64
    tampered3 = not chain.is_chain_valid()
    log(tampered3, "Broken hash link detected")
    chain.chain[2].prev_hash = original_prev

    # verify restoration
    log(chain.is_chain_valid(), "Chain valid after restoring tampered values")