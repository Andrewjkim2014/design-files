import secrets
import hashlib
from datetime import datetime
from flask_app.config.mysqlconnection import MySQLConnection
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from typing import Dict, Any

class Block:
    dB = "vault_data"

    # Key management parameters
    SECRET_KEY_SALT = secrets.token_urlsafe(16)
    KEY_DERIVATION_ROUNDS = 100000
    SECRET_KEY_LENGTH = 32

    def __init__(self, index: int, timestamp: datetime, data: str, previous_hash: str) -> None:
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash(self.index, self.timestamp, self.data, self.previous_hash)

    def __repr__(self) -> str:
        return f"Block(index={self.index}, timestamp={self.timestamp}, data={self.data}, previous_hash={self.previous_hash})"

    def to_dict(self) -> Dict[str, Any]:
        # Return a dictionary representation of the block.
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    @staticmethod
    def derive_key(password: str, salt: str) -> bytes:
        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=Block.SECRET_KEY_LENGTH,
            salt=salt.encode(),
            iterations=Block.KEY_DERIVATION_ROUNDS,
            backend=backend
        )
        return kdf.derive(password.encode())

    def encrypt_data(self, data: dict) -> dict:
        encrypted_data = {}
        for key, value in data.items():
            if key != 'hash':
                encrypted_value = self.encrypt(value)
                encrypted_data[key] = encrypted_value
        return encrypted_data

    def encrypt(self, data: str) -> str:
        password = self.derive_key(self.secret_key, self.SECRET_KEY_SALT)
        fernet = Fernet(base64.urlsafe_b64encode(password))
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data.decode()

    def decrypt(self, data: str) -> str:
        password = self.derive_key(self.secret_key, self.SECRET_KEY_SALT)
        fernet = Fernet(base64.urlsafe_b64encode(password))
        decrypted_data = fernet.decrypt(data.encode())
        return decrypted_data.decode()

    @classmethod
    def mint_block(cls, data: dict) -> 'Block':
        """
        Create and store a new block with the given data.

        The `data` parameter should be a dictionary containing at least the following keys:
        - index (int)
        - timestamp (datetime)
        - data (str)
        - previous_hash (str)
        - hash (str)
        - blockchains_id (int)

        Returns:
            A new Block instance.
        """
        query = """
            INSERT INTO blocks (index, timestamp, data, previous_hash, hash, blockchains_id)
            VALUES (%(index)s, %(timestamp)s, %(data)s, %(previous_hash)s, %(hash)s, %(blockchains_id)s);
        """
        results = MySQLConnection(cls.dB).query_db(query, data)
        return cls.from_dict(data)

    @classmethod
    def create_block(cls, data: dict) -> 'Block':
        """
        Create and store a new block with the given data.

        The `data` parameter should be a dictionary containing at least the following keys:
        - id (int): ID of transaction associated with this block.
        - other keys as required

        Returns:
            A new Block instance.
        """

        # Get the current length of the blockchain to determine the index of the new block
        chain_length = len(cls.get_all())

        # Create a new block with appropriate data and previous hash
        timestamp = datetime.now()
        previous_hash = cls.get_by_index(chain_length - 1).hash if chain_length > 0 else None
        blockchains_id = 1

        new_block_data = {
            "index": chain_length,
            "timestamp": timestamp,
            "data": cls.encrypt_data(data),
            "previous_hash": previous_hash,
            "hash": None,
            "blockchains_id": blockchains_id
        }

        # Mint and return the new block
        return cls.mint_block(new_block_data)

    @classmethod
    def from_dict(cls, data):
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            data=data["data"],
            previous_hash=data["previous_hash"]
        )

    @classmethod
    def get_all(cls) -> list['Block']:
        query = """
            SELECT * FROM blocks;
        """
        results = MySQLConnection(cls.dB).query_db(query)
        return [cls.from_dict(result) for result in results]

    @classmethod
    def get_by_index(cls, index: int) -> 'Block':
        query = """
            SELECT * FROM blocks WHERE index=%(index)s;
        """
        result = MySQLConnection(cls.dB).query_db(query, {"index": index})

        if len(result) > 0:
            return cls.from_dict(result[0])

        else:
            raise ValueError(f"No block with index {index} found")

    @classmethod
    def get_by_timestamp(cls, timestamp: datetime) -> 'Block':
        query = """
            SELECT * FROM blocks WHERE timestamp=%(timestamp)s;
        """
        result = MySQLConnection(cls.dB).query_db(query, {"timestamp": timestamp})

        if len(result) > 0:
            return cls.from_dict(result[0])

        else:
            raise ValueError(f"No block with timestamp {timestamp} found")

    @classmethod
    def get_by_previous_hash(cls, previous_hash: str) -> 'Block':
        query = """
            SELECT * FROM blocks WHERE previous_hash=%(previous_hash)s;
        """
        result = MySQLConnection(cls.dB).query_db(query, {"previous_hash": previous_hash})

        if len(result) > 0:
            return cls.from_dict(result[0])

        else:
            raise ValueError(f"No block with previous hash {previous_hash} found")