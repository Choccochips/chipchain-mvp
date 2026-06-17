from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 

# get my classes from built modules
from blockchain.block import Block
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction

# need to import 
from blockchain.contracts.escrow import contract_code as escrow_code
from blockchain.contracts.impact import contract_code as impact_code
from blockchain.contracts.governance import contract_code as governance_code

# keys
from ecdsa import SigningKey, SECP256k1

ALMIGHTY_WALLET = 'd9e56bb00aa6372b1dbafacc815c083ad50635ee477588a4135a9f22c484e271'



# chain instance to persist for curr testing
chip_chain = Blockchain()

# deploy governance on startup so all routes know the address
def deploy_governance():
    key = SigningKey.from_string(bytes.fromhex(ALMIGHTY_WALLET), curve=SECP256k1)
    sender = key.get_verifying_key().to_string().hex()
    tx = Transaction(sender, None, 0, tx_type='deploy_contract', contract_code=governance_code)
    tx.sign_transaction(key)
    chip_chain.add_transaction(tx)
    chip_chain.mine_pending_transactions(sender)
    return tx.calc_hash()

governance_address = deploy_governance()
print(f"Governance deployed at {governance_address[:16]}...")


app = Flask(__name__)
# allow React frontend on a different port to talk to this API
CORS(app)

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


@app.route('/transaction', methods=['POST'])
# note difference here from 'add', we are creating and know the params we need vs just adding
# an exisitng transction (from here) to the pending list
def create_transaction():
    data = request.get_json()
    try:
        signing_key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve=SECP256k1)
        sender = signing_key.get_verifying_key().to_string().hex()

        parent_hash = data.get('parent_tx_hash')
        tx = chip_chain.create_tracked_transaction(sender, data['recipient'], data['amount'], parent_hash)
        tx.sign_transaction(signing_key)
        chip_chain.add_transaction(tx)
        chip_chain.mine_pending_transactions(sender)
        return jsonify({'message': 'Transaction added!', 'tx_hash': tx.calc_hash()})
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

@app.route('/generate-wallet', methods=['POST'])
def generate_wallet():
    key = SigningKey.generate(curve=SECP256k1)
    private_key = key.to_string().hex()
    public_key = key.get_verifying_key().to_string().hex()
    return jsonify({'private_key': private_key, 'public_key': public_key})

@app.route('/trail/<tx_hash>')
def get_trail(tx_hash):
    tx = chip_chain.find_transaction(tx_hash)
    if tx:
        return jsonify({
            'hash': tx.calc_hash(),
            'trail': tx.trail,
            'sender': tx.sender_address,
            'recipient': tx.recip_address,
            'amount': tx.amount,
            'parent': tx.parent_tx_hash
        })
    return jsonify({'message': 'Transaction not found'}), 404

@app.route('/tx-hashes')
def get_tx_hashes():
    hashes = []
    for block in chip_chain.chain:
        for tx in block.transactions:
            hashes.append({
                'tx_hash': tx.calc_hash(),
                'sender': tx.sender_address,
                'recipient': tx.recip_address,
                'amount': tx.amount,
                'trail': tx.trail
            })
    return jsonify(hashes)

# smart contract logic
@app.route('/contract/deploy', methods = ['POST'])
def deploy_contract():
    data = request.get_json()
    try:
        key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve = SECP256k1)
        sender = key.get_verifying_key().to_string().hex()

        # make sure you got the right contract code
        if data['contract_type'] == 'impact':
            code = impact_code
        elif data['contract_type'] ==  'escrow':
            code = escrow_code
        
        # if neither of the options just return error
        else:
            return jsonify({'message': 'Unknown Contract'}), 400

        # set up tx for deployment
        tx = Transaction(sender, None, 0, tx_type='deploy_contract', contract_code = code)
        # sign off on tx
        tx.sign_transaction(key)
        chip_chain.add_transaction(tx)
        chip_chain.mine_pending_transactions(sender)
        # get address
        contract_address = tx.calc_hash()

        # get the right contract code

        return jsonify({'message': 'Contract has been deployed!...', 'Contract Address: ': contract_address})
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/contract/call', methods = ['POST'])
def call_contract():
    data = request.get_json()

    try:

        key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve = SECP256k1)
        wallet = key.get_verifying_key().to_string().hex()

        # create a call tx 
        tx = Transaction(wallet, None, 0, tx_type = 'call_contract', contract_address=data['contract_address'],function_name= data['function_name'], function_args=data.get('function_args', {}))
        tx.sign_transaction(key)
        result = chip_chain.add_transaction(tx)
        chip_chain.mine_pending_transactions(wallet)

        return jsonify({'message': 'Contract has been called!...', 'Result: ': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@app.route('/contract/<address>/state')
def get_contract_state(address):
    # check if contract exists in smart contracts
    if address in chip_chain.smart_contracts:
        return jsonify(chip_chain.smart_contracts[address].state)
    return jsonify({'message': 'Smart contract not found!...'}), 400
        
# governance routes

@app.route('/governance/proposals')
def get_proposals():
    # read straight from contract state, no signing needed for queries
    contract = chip_chain.smart_contracts.get(governance_address)
    proposals = contract.state.get('proposals', {})

    # weight each vote by the voter's current voting power so the ui can show real numbers
    min_tokens = chip_chain.config['voting']['min_tokens']
    enriched = {}
    for pid, p in proposals.items():
        tally = {'yes': 0, 'no': 0, 'abstain': 0}
        for voter, choice in (p.get('votes') or {}).items():
            if choice not in tally:
                continue
            balance = chip_chain.get_balance(voter)
            power = balance if balance >= min_tokens else 0
            tally[choice] += power
        enriched[pid] = {**p, 'tally': tally}
    return jsonify(enriched)

@app.route('/governance/proposal/<proposal_id>')
def get_proposal(proposal_id):
    contract = chip_chain.smart_contracts.get(governance_address)
    proposal = contract.state.get('proposals', {}).get(proposal_id)
    if not proposal:
        return jsonify({'message': 'Proposal not found!...'}), 404
    return jsonify(proposal)

@app.route('/governance/proposal', methods=['POST'])
def create_proposal():
    data = request.get_json()
    try:
        key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve=SECP256k1)
        sender = key.get_verifying_key().to_string().hex()

        # build args from request, default to signal if no action passed
        function_args = {
            'title': data['title'],
            'description': data.get('description', ''),
            'action': data.get('action', {'type': 'signal', 'args': {}})
        }

        tx = Transaction(sender, None, 0, tx_type='call_contract', contract_address=governance_address, function_name='create_proposal', function_args=function_args)
        tx.sign_transaction(key)
        proposal_id = chip_chain.add_transaction(tx)
        chip_chain.mine_pending_transactions(sender)
        return jsonify({'message': 'Proposal created!...', 'proposal_id': proposal_id})
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/governance/vote', methods=['POST'])
def cast_vote():
    data = request.get_json()
    try:
        key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve=SECP256k1)
        sender = key.get_verifying_key().to_string().hex()

        function_args = {
            'proposal_id': data['proposal_id'],
            'choice': data['choice']
        }

        tx = Transaction(sender, None, 0, tx_type='call_contract', contract_address=governance_address, function_name='cast_vote', function_args=function_args)
        tx.sign_transaction(key)
        choice = chip_chain.add_transaction(tx)
        chip_chain.mine_pending_transactions(sender)
        return jsonify({'message': 'Vote cast!...', 'choice': choice})
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/governance/resolve', methods=['POST'])
def resolve_proposal():
    data = request.get_json()
    try:
        key = SigningKey.from_string(bytes.fromhex(data['private_key']), curve=SECP256k1)
        sender = key.get_verifying_key().to_string().hex()

        function_args = {'proposal_id': data['proposal_id']}

        tx = Transaction(sender, None, 0, tx_type='call_contract', contract_address=governance_address, function_name='resolve_proposal', function_args=function_args)
        tx.sign_transaction(key)
        status = chip_chain.add_transaction(tx)
        chip_chain.mine_pending_transactions(sender)
        return jsonify({'message': 'Proposal resolved!...', 'status': status})
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/governance/voting_power/<address>')
def get_voting_power(address):
    # apply the threshold rule directly, same logic as the contract
    balance = chip_chain.get_balance(address)
    min_tokens = chip_chain.config['voting']['min_tokens']
    power = balance if balance >= min_tokens else 0
    return jsonify({'address': address, 'voting_power': power})

@app.route('/governance/admins')
def get_admins():
    return jsonify({'admins': list(chip_chain.admins)})

@app.route('/governance/voters')
def get_voters():
    # walk every wallet on the chain and return the ones with enough tokens
    min_tokens = chip_chain.config['voting']['min_tokens']
    voters = {}
    for wallet in chip_chain.get_all_wallets():
        balance = chip_chain.get_balance(wallet)
        if balance >= min_tokens:
            voters[wallet] = balance
    return jsonify(voters)

@app.route('/governance/config', methods=['GET'])
def get_governance_config():
    return jsonify(chip_chain.config)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)