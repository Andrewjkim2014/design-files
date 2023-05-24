from typing import List
from flask_app.config.mysqlconnection import MySQLConnection
from flask_app.models.blockchain import Blockchain
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
import json

class Transaction:
    dB = "vault_data"

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(sender=data["sender"], receiver=data["receiver"], amount=data["amount"])

    @classmethod
    def get_transactions(cls, sender):
        query = """
            SELECT * FROM transactions WHERE sender = %(sender)s;
        """
        results = MySQLConnection(cls.dB).query_db(query, {"sender": sender})
        return results

    @classmethod
    def get_recent_transactions(cls, account_id: int) -> List['Transaction']:
        query = """
            SELECT * FROM transactions WHERE sender = %(account_id)s OR receiver = %(account_id)s ORDER BY timestamp DESC LIMIT 10;
        """
        results = MySQLConnection(cls.dB).query_db(query, {"account_id": account_id})

        if isinstance(results, bool):
            # Handle case where results is a boolean value
            return []

        return [cls(result["id"], result["sender"], result["receiver"], result["amount"], result["timestamp"]) for result in results]

    def add_transaction(self, transaction):
        # Check if the transaction is valid.
        if not transaction.is_valid():
            raise ValueError("Invalid transaction")

        # Add the transaction to the blockchain.
        blockchain = Blockchain()
        blockchain.add_transaction(transaction)

    def is_valid(self):
        # Instantiate a new blockchain.
        blockchain = Blockchain()

        # Check if the sender has enough balance.
        if self.sender_balance < self.amount:
             return False

        # Check if the receiver is valid.
        if not self.receiver in blockchain.nodes:
            return False

        return True

    def is_valid_transaction(self, transaction):
        """
        Checks if a transaction is valid.

        Args:
            transaction: The transaction to be checked.

        Returns:
            True if the transaction is valid, False otherwise.
        """

        # Check if the sender has enough funds.
        if transaction.sender_balance < transaction.amount:
            return False

        # Check if the recipient exists.
        account_query = """
            SELECT * FROM accounts WHERE name=%(name)s;
        """

        account_result = MySQLConnection(Transaction.dB).query_db(account_query, {"name":transaction.recipient})

        if len(account_result) == 0:
            return False

        # Check if the transaction's signature is valid.
        signature_validity = transaction.verify_signature(transaction.sender)

        return signature_validity

    def sign_transaction(self, transaction_data: dict):
        """
        Signs a transaction using the private key.

        Args:
            transaction_data: The transaction data to be signed.

        Returns:
            The signature of the transaction.
        """
        private_key = ec.generate_private_key(ec.SECP256R1())
        transaction_json = json.dumps(transaction_data).encode('utf-8')
        signature = private_key.sign(
            transaction_json,
            ec.ECDSA(hashes.SHA256())
        )
        return signature

    def verify_signature(self, transaction_data: dict):
        """
        Verifies the signature of a transaction using the sender's public key.

        Args:
            transaction_data: The transaction data to be verified.

        Returns:
            True if the signature is valid, False otherwise.
        """
        public_key = self.get_public_key()
        try:
            public_key.verify(
                transaction_data["signature"],
                json.dumps(transaction_data).encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

    def get_public_key(self):
        """
        Retrieves the public key associated with the sender.

        Returns:
            The public key of the sender.
        """
        # Retrieve the public key from the database or key store based on sender's identifier.
        # Example:
        # public_key = key_store.get_public_key(self.sender)
        public_key = ec.generate_private_key(ec.SECP256R1()).public_key()
        return public_key

    @staticmethod
    def get_all() -> List['Transaction']:
        query = """
            SELECT * FROM transactions;
        """
        results = MySQLConnection(Transaction.dB).query_db(query)
        return [Transaction.from_dict(result) for result in results]

    @staticmethod
    def get_by_sender(sender: str) -> List['Transaction']:
        query = """
            SELECT * FROM transactions WHERE sender=%(sender)s;
        """

        results = MySQLConnection(Transaction.dB).query_db(query, {"sender": sender})

        return [Transaction.from_dict(result) for result in results]

    @staticmethod
    def get_by_receiver(receiver: str) -> List['Transaction']:
        query="""
            SELECT * FROM transactions WHERE receiver=%(receiver)s;
        """

        results = MySQLConnection(Transaction.dB).query_db(query, {"receiver": receiver})

        return [Transaction.from_dict(result) for result in results]