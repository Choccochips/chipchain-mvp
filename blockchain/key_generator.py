# for crypto stuff
from ecdsa import SigningKey, SECP256k1

# generate key pair
# used same curve btc uses
key = SigningKey.generate(curve = SECP256k1)
private_key = key.to_string().hex() # used to sign off (like authorization) on transcations
public_key = key.get_verifying_key().to_string().hex() # used by other nodes on network to verify that signature is valid w/o knowing secret key

print(f"Private key: {private_key}\nPublic key: {public_key}")

