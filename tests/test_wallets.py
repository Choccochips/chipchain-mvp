"""

This file is to be used for testing

"""

from tests.utils import fresh_chain, log, header

NAME = "Wallet creation & funding"

def run():
    header(NAME)
    
    # set up chain with genesis block and pre-funded wallets
    chain, genesis, wallets = fresh_chain()

    log(True, f"Created {len(wallets)} wallets")
    log(True, f"Genesis balance: {chain.get_balance(genesis['public'])}")

    # verify each wallet has the correct balance
    all_good = True
    for name, wallet in wallets.items():
        bal = chain.get_balance(wallet['public'])
        if name == 'bad_actor':
            # bad_actor should not be funded
            passed = bal == 0
            log(passed, f"{name} (unfunded): {bal} tokens")
        else:
            # all other wallets should have 300 tokens
            passed = bal == 300
            log(passed, f"{name}: {bal} tokens")
        if not passed:
            all_good = False

    log(chain.is_chain_valid(), "Chain valid after funding")
    print()
    log(all_good, "All wallet balances are correct!...")