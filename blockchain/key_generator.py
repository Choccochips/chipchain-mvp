# for crypto stuff
from ecdsa import SigningKey, SECP256k1

# generate key pair
# used same curve btc uses
key = SigningKey.generate(curve = SECP256k1)
private_key = key.to_string().hex() # used to sign off (like authorization) on transcations
public_key = key.get_verifying_key().to_string().hex() # used by other nodes on network to verify that signature is valid w/o knowing secret key

print(f"Private key: {private_key}\nPublic key: {public_key}")

# test keys
# Private key: 327e1c6b4137a0b805f4dd0563483fb922612d96b1a92fd2ef7f5a2e58f06cc0
# Public key: 30a7526968de150602415cfbcfb23f7f83a0affe4d8e9d8965c9bf398ba52ead49d6c6a0b5ef9ca712cad8ed362b260b4e721480444a1d0299ce7b858c198b48