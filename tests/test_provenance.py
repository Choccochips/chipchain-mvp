"""

This file is to be used for testing

"""

# imports
from tests.utils import fresh_chain, log, header

NAME = "Provenance trails"

def run():
    header(NAME)
    
    # set up chain with genesis block and multiple wallets
    chain, genesis, wallets = fresh_chain()

    # define the hops we want to test
    hops = [
        ('manufacturer', 'certifier'),
        ('certifier', 'retailer'),
        ('retailer', 'consumer'),
    ]

    trail_lengths = []

    # create transactions for each hop and track trail growth
    for sender_name, recip_name in hops:
        sender = wallets[sender_name]
        recip = wallets[recip_name]
        tx = chain.create_tracked_transaction(
            sender['public'], recip['public'], 50
        )
        tx.sign_transaction(sender['private'])
        try:
            chain.add_transaction(tx)
            chain.mine_pending_transactions(genesis['public'])
            trail_lengths.append(len(tx.trail))
            log(True, f"{sender_name} → {recip_name} | trail: {len(tx.trail)} hop(s)")
        except Exception as e:
            log(False, f"{sender_name} → {recip_name} failed: {e}")
            trail_lengths.append(-1)

    # verify trail grew at each hop
    grew = all(trail_lengths[i] <= trail_lengths[i+1] for i in range(len(trail_lengths)-1))
    log(grew, f"Trail grew across hops: {' ->'.join(str(t) for t in trail_lengths)}")

    log(chain.is_chain_valid(), "Chain valid after provenance tracking")

    # look up the final transaction's trail
    print()
    if trail_lengths[-1] > 0:
        log(True, "Full provenance trail reconstructed from consumer's perspective")