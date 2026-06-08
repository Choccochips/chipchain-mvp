"""

This file is used for support to testing files

"""

from ecdsa import SigningKey, SECP256k1
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction

# wallets we will be needing for testing
def make_wallet():
    sk = SigningKey.generate(curve=SECP256k1)
    return {
        'private': sk,
        'public': sk.get_verifying_key().to_string().hex()
    }

def load_genesis_wallet():
    sk = SigningKey.from_string(bytes.fromhex("d9e56bb00aa6372b1dbafacc815c083ad50635ee477588a4135a9f22c484e271"), curve=SECP256k1)
    return {
        'private': sk,
        'public': "7d077faca9b85e2feb19331266baa0ca59751ad6521e8958e85165510c4ad5ed9dc2c35d8975b049faf54c2ecf12ac3c667a2908674ade1297de471236f754a2"
    }


# dummy values for now, may change later as we get more into what Wish wants the simulation tests to look like
# maybe we can incorporate his world simulation idea into this kind of?
def fresh_chain():
    chain = Blockchain()
    genesis = load_genesis_wallet()
    wallets = {
        'manufacturer': make_wallet(),
        'certifier': make_wallet(),
        'retailer': make_wallet(),
        'consumer': make_wallet(),
        'bad_actor': make_wallet(),
    }
    for name, wallet in wallets.items():
        if name == 'bad_actor':
            continue
        tx = Transaction(genesis['public'], wallet['public'], 300)
        tx.sign_transaction(genesis['private'])
        chain.add_transaction(tx)
    chain.mine_pending_transactions(genesis['public'])
    return chain, genesis, wallets

# output checks 
def log(status, msg):
    icon = "^__^" if status else "X"
    print(f"    [{icon}] {msg}")

# formatting output stuff
def header(title):
    print(f"\n  {'*' * 46}")
    print(f"    {title}")
    print(f"  {'*' * 46}")