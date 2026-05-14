from flask import Flask,jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy 

# get my classes from built modules
from blockchain.block import Block
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction

# keys
from ecdsa import SigningKey, SECP256k1

# chain instance to persist for curr testing
chip_chain = Blockchain()


app = Flask(__name__)

@app.route('/')
def index():
    # header to show
    return render_template('index.html')

@app.route ('/chain')
def get_chain():
    chain_data = [block.to_dict() for block in chip_chain.chain]
    return jsonify(chain_data)

@app.route('/balance/<address>')
def get_balance(address):
    balance = chip_chain.get_balance(address)
    # since we get values returned fxs, we can just plug them into json
    return jsonify({'address': address, 'balance': balance})

@app.route('/mine', methods = ['POST'])
def mine():
    data = request.get_json()
    reward_address = data['address']
    chip_chain.mine_pending_transactions(reward_address)
    return jsonify({'message': 'Block has been mined!...'})

@app.route('/transaction', methods = ['POST'])
# note difference here from 'add', we are creating and know the params we need vs just adding
# an exisitng transction (from here) to the pending list
def create_transaction():
    data = request.get_json()
    try:
        signing_key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve=SECP256k1)
        sender = signing_key.get_verifying_key().to_string().hex()

        tx = Transaction(sender, data['recipient'], data['amount'])
        tx.sign_transaction(signing_key)
        chip_chain.add_transaction(tx)
        return jsonify({'message': 'Transaction has been added!...'})
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/validate')
def validate():
    is_valid = chip_chain.is_chain_valid()
    return jsonify({'valid': is_valid})

@app.route('/pending')
def pending():
    pending = [tx.to_dict() for tx in chip_chain.pending_transactions]
    return jsonify(pending)

@app.route('/wallet', methods=['POST'])
def load_wallet():
    data = request.get_json()
    signing_key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve=SECP256k1)
    address = signing_key.get_verifying_key().to_string().hex()
    return jsonify({'address': address})

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)