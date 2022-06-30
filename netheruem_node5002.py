# Module 1
# (pt-1) Create a Blockchain
import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

# First step is to initialize the chain


class Blockchain:
    # The chain itself(to initiliaze the chain)
    def __init__(self):
     # (a list containing different block(an empty list))
        self.chain = []
    # a transaction list before they are added to a block
        self.transactions = []
    # To initialize the blockchain we have to create the first block(genesis_block)
        self.create_block(proof=1, previous_hash='0')
    # we are using a set and not a list because the nodes aren't placed in any particular order as they're distributed all around the world
        self.nodes = set()
    # A create block function that also adds newly mined blocks
    # The create block function is only executed after we have a mined block hence we pass the paramter proof & previous_hash which is gotten from the newly mined block

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    # To get the last block of the chain
    def get_lastblock(self):
        return self.chain[-1]

    # The proof of work function takes a parameter previous_proof as it must be put into consideration when finding the new proof
    def proof_of_work(self, previous_proof):
        # We increment the new_proof at each iteration of the while loop as the new proof = 1 isnt the right proof
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof ** 2 - previous_proof**2).encode()).hexdigest()
        # We take the first four indexes of the 64 strings generated
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    # This hash function takes a block(hash the block of our blockchain) has input and returns the sha256 cryptographic hash of the block.
    def hash(self, block):
        # The dumps function is used to convert data structures into strings
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # This takes the chain as a parameter because we're going to take the blocks of the chain and make our two checks for this blocks.
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof ** 2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            block_index += 1
            previous_block = block
        return True

    def add_transactions(self, sender, reciever, amount):
        self.transactions.append({'sender': sender,
                                  'reciever': reciever,
                                  'amount': amount})
        # what we re returning is the index of the block that would recieve this transaction
        last_block = self.get_lastblock()
        return last_block['index'] + 1

    def add_nodes(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://(node)/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        # This means- if longest chain was not none (meaning the chain was replaced)
        if longest_chain:
            # We then set the chain of our blockchain(self.chain) to the recently updated chain longest chain
            self.chain = longest_chain
            return True
        return False


        # (pt-2)
        # Mining our first blockchain
        # Creating a WebApp
app = Flask(__name__)
# Creating a Blockchain
blockchain = Blockchain()

# create a node adddress on port 5000
node_address = str(uuid4()).replace('-', '')

# Mining a new block
# The route decorator is used to specify the name of the request and most especially the request


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_lastblock()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(
        sender=node_address, reciever='Vicky', amount=1000)
    # The create block function appends and returns a block according to the create_block method in our blockchain class.
    block = blockchain.create_block(proof, previous_hash,)
    # The response variable don't just contain the information of the block, but also a nice message congratulating the miner for mining the block
    response = {'message': 'Congratulations! You just mined a block.',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200


# Getting the Full Blockchain (This function would allow us display the full chain in PostMan)
@app.route('/get_chain', methods=['GET'])
def get_chain():
    # This response contains what would be displayed when we send the get request
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Request to Know if Blockchain is Valid or Not
@app.route('/is_valid', methods=['GET'])
def is_valid():
    chain = blockchain.chain
    validity = blockchain.is_chain_valid(chain)
    return jsonify(validity), 200

# Adding a new transaction to the blockchain


@app.route('/add_transactions', methods=['POST'])
def add_transactions():
    json = request.get_json()
    transaction_keys = ['sender', 'reciever', 'amount']
    if not all(keys in json for keys in transaction_keys):
        return 'elements of the transaction is missing', 400
    index = blockchain.add_transactions(
        json['sender'], json['reciever'], json['amount'])
    response = {
        'message': f'this transaction would be added to the block{index}'}
    return jsonify(response), 201

# decentralizing the blockchain
# connecting new nodes


@app.route('/connect_nodes', methods=['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_nodes(node)
    response = {'message': 'All the nodes are now connected. The netheruem blockchain now contains the following amount of nodes:',
                'total_nodes': list[blockchain.nodes]}
    return jsonify(response), 201


# replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    # This returns a boolean (yes/no) and lets us know if our blockchain is replaced or not
    is_chain_replaced = blockchain.replace_chain
    if is_chain_replaced == True:
        response = {'message': 'nodes in the netheruem blockchain have differents chains, hence chain is replaced by the longest chain',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'this is the longest chain',
                    'actual_chain': blockchain.chain}
        return jsonify(response), 200


# Running the App
app.run(host='172.20.10.3', port=5002)
