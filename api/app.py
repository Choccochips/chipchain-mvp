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
    chain_data = [block]

@app.route('/balance/<address>')

@app.route('/mine', methods = ['POST'])

@app.route('/transaction', methods = ['POST'])

@app.route('/validate')

@app.route('/pending')

if __name__ == '__main__':
    app.run(debug = True)