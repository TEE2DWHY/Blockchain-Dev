# Module 1
# (pt-1) Create a Blockchain
import datetime
import hashlib
from itertools import chain
import json
from flask import Flask, jsonify

# First step is to initialize the chain


class Blockchain:
    # The chain itself(to initiliaze the chain)
    def __init__(self):
     # (a list containing different block(an empty list))
        self.chain = []
    # To initialize the blockchain we have to create the first block(genesis_block)
        self.create_block(proof=1, previous_hash='0')

    # A create block function that also adds newly mined blocks
    # The create block function is only executed after we have a mined block hence we pass the paramter proof & previous_hash which is gotten from the newly mined block
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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


# (pt-2)
# Mining our first blockchain
# Creating a WebApp
app = Flask(__name__)
# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
# The route decorator is used to specify the name of the request and most especially the request


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_lastblock()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    # The create block function appends and returns a block according to the create_block method in our blockchain class.
    block = blockchain.create_block(proof, previous_hash,)
    # The response variable don't just contain the information of the block, but also a nice message congratulating the miner for mining the block
    response = {'message': 'Congratulations! You just mined a block.',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
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


# Running the App
app.run(host='172.20.10.3', port=5000)
