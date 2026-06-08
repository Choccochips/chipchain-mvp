"""

This file is to be used for testing

"""


from blockchain.transaction import Transaction
from tests.utils import fresh_chain, log, header

NAME = "Basic transfers"

def run():
    header(NAME)

    # fresh chain + funded wallets
    chain, genesis, wallets = fresh_chain()

    # list of transfers to push through
    transfers = [
        ('manufacturer', 'certifier', 50),
        ('certifier', 'retailer', 30),
        ('retailer', 'consumer', 10),
        ('consumer', 'manufacturer', 5),
    ]

    all_good = True

    for sender_name, recip_name, amount in transfers:
        sender_wallet = wallets[sender_name]
        recip_wallet = wallets[recip_name]

        # build tx and sign w/ sender's private key
        tx = Transaction(sender_wallet['public'], recip_wallet['public'], amount)
        tx.sign_transaction(sender_wallet['private'])

        try:
            chain.add_transaction(tx)
            log(True, f"{sender_name} → {recip_name}: {amount} tokens")
        except Exception as e:
            all_good = False
            log(False, f"{sender_name} → {recip_name} failed: {e}")

    # mine everything pending into one block
    chain.mine_pending_transactions(genesis['public'])
    log(True, "Block mined")

    print()

    # see what shakes balance-wise
    for name, wallet in wallets.items():
        bal = chain.get_balance(wallet['public'])
        log(True, f"{name}: {bal} tokens")

    log(chain.is_chain_valid(), "Chain valid after transfers")
    print()
    log(all_good, "All transfers completed successfully")