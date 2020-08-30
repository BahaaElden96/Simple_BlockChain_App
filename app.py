import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain=[]
        self.current_transactions=[]
        self.new_Block(previous_hash=1,proof=100)
    def new_Block(self,proof,previous_hash=None):
        # Create New Block
        #proof <int> the proof given by pwa
        #previous_hash :(optional) <str> Hash of Previous Block
        #return <dict< New Block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions=[]
        self.chain.append(block)
        return block

    def new_transction(self,sender,recipient,amount):
        # Add new Trans
        # "Creates new transaction\n"
        #    Sender : <str> addres of the sender\n"
        #    Recipient : <str> addres if reciver\n"
        #    amount : <int> Amount\n"
        #    return : <int> index of block of current transction submitted\n"
        self.current_transactions.append(
            {'sender': sender, 'recipient': recipient, 'amount':amount,})
        return self.last_block['index']+1


    @staticmethod
    def hash(block):
       # Create SHA 256 hash of block
        #:param block:<dict>Block
        #:return: <str>
        #we must make sure that dictionary is Ordered , or we'll have inconsisitent hashes
        block_string=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    @property
    def last_block(self):
        #return last block in chain
        return self.chain[-1]

    def proof_of_work(self,last_proof):
        #Simple Proof of Work Algorithm:
        #- Find a number p' such that hash(pp') contains leading 4 zeroes, wherep is the previous p'
        #- p is the
        #previous proof, and p ' is the new proof
        #: param
        #last_proof: < int >
        #:return: < int >
        proof=0
        while self.valid_proof(last_proof,proof) is False:
            proof+=1
        return proof
    @staticmethod
    def valid_proof(last_proof,proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = '{l_f}{p_f}'.format(l_f=last_proof,p_f=proof).encode()
        guess_hash=hashlib.sha256(guess).hexdigest()
        return guess_hash[:4]=="0000"

app = Flask(__name__)
node_identifier=str(uuid4()).replace('-','')
blockchain=Blockchain()
# generate global unique address for this node
node_identifier = str(uuid4()).replace('-', '')

@app.route('/')


@app.route('/mine',methods=['GET'])
def mine():
    last_block=blockchain.last_block
    last_proof=last_block['proof']
    proof=blockchain.proof_of_work(last_proof)
    #recive reward for finding proof
    #sender is 0 to signify that this node has mined a new coin
    blockchain.new_transction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    previous_hash=blockchain.hash(last_block)
    block=blockchain.new_Block(proof,previous_hash)
    response={
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response),200

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    values=request.get_json()
    required = ['sender','recipient','amount']
    if not all(k in values for k in required):
        return 'Missing Values Trans',400
    index=blockchain.new_transction(values['sender'],values['recipient'],values['amount'])
    response={'message':'Transaction will be added to Block {index}'.format(index=index)}
    return jsonify(response),201

@app.route('/chain',methods=['GET'])
def full_chain():
    response = {
        'chain':blockchain.chain,
        'length':len(blockchain.chain),
    }
    return jsonify(response),200
if __name__ == '__main__':
    app.run(host='localhost',port=5000)