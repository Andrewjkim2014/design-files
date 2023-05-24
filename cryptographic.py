from pyblockchain import Block, Blockchain
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import json
from flask import Flask, request

app = Flask(__name__)
blockchain = Blockchain()

# Generate public and private key pairs for each node
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block.data['proof_of_work']
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(sender='0', recipient=node_identifier, amount=1)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    # Sign the block with the node's private key
    signature = private_key.sign(json.dumps(block.data).encode('utf-8'), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    response = {
        'message': "New Block forged",
        'index': block.index,
        'transactions': block.data['transactions'],
        'proof': block.data['proof_of_work'],
        'previous_hash': block.data['previous_hash'],
        'signature': signature
    }
    return json.dumps(response)

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Encrypt the transaction data with the recipient's public key
    ciphertext = public_key.encrypt(json.dumps(values).encode('utf-8'), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    index = blockchain.new_transaction(sender='anonymous', recipient=ciphertext, amount=0)
    response = {'message': f'Transaction will be added to Block {index}'}
    return json.dumps(response)

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return json.dumps(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
