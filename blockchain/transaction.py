# needed for sha256 implementation
import hashlib

# since we dont have CONST keyword in python, will be using Final to flag for changes in place of that
from typing import Final

# for keys
from ecdsa import SigningKey, VerifyingKey, SECP256k1

# replacing 'data' filler with 'transactions'
class Transaction():
    # basic stuff for now
    def __init__(self, sender_address, recip_address, amount):
        self.sender_address = sender_address
        self.recip_address = recip_address
        self.amount = amount
        self.signature = None # needed to initialize this 
    
    # need for serialization, will return dict
    def to_dict(self):
        return{
            'sender': self.sender_address,
            'recipient': self.recip_address,
            'amount': self.amount
        }
    
    def calc_hash(self)-> str: # type hint to stop pylance complaining in sign transaction
        # set up string so we can hash it
        return_string = str(self.sender_address) + str(self.recip_address) + str(self.amount)
        return hashlib.sha256(return_string.encode()).hexdigest()

    def sign_transaction(self, signing_key): # remember signing key = private key and we can get public key from it
        # from address check 
        if signing_key.get_verifying_key().to_string().hex() != self.sender_address:
            raise Exception("Can't sign transactions for other wallets!! -_-")
            
        hashtx: Final[str] = self.calc_hash()
        self.signature  = signing_key.sign(hashtx.encode()).hex()

    def is_valid(self):
        # need to remember mining reward edge case on key check w/ address
        if self.sender_address is None:
            return True
        
        if not self.signature or len(self.signature) == 0:
            raise Exception("There are no signatures in this transaction")
        
        try:
            # have to use this function since we dont have private key to verify public. this is from other nodes POV
            public_key = VerifyingKey.from_string(bytes.fromhex(self.sender_address), curve = SECP256k1)
            # converting back into bytes to be encoded and then examined for verification
            public_key.verify(bytes.fromhex(self.signature), self.calc_hash().encode())
            return True
        except:
            return False
