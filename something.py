from typing import List
import datetime
from flask_app.models.block import Block
from flask_app.config.mysqlconnection import MySQLConnection


class Blockchain:
    dB = "vault_data"
    genesis_hash = "0000000000000000000000000000000000000000000000000000000000000001"
    chain = []

    def __init__(self) -> None:
        self.id = None
        self.nodes = set()
        self.difficulty = 500

        if len(self.chain) == 0:
            # Create the genesis block
            genesis_block = Block(
                0,
                datetime.datetime.fromtimestamp(1231006505),
                "This is the first block in the blockchain",
                self.genesis_hash
            )
            self.chain.append(genesis_block)

            # Insert the genesis block into the database
            self.add_block(genesis_block, 0)

    @classmethod
    def add_block(cls, block: Block, blockchain_id: int) -> None:
        query = """
            INSERT INTO blocks (`index`, `timestamp`, `data`, `previous_hash`, `hash`, `blockchain_id`)
            VALUES (%(index)s, %(timestamp)s, %(data)s, %(previous_hash)s, %(hash)s, %(blockchain_id)s);
        """

        # Set previous hash to None for the genesis block
        if len(cls.chain) == 0:
            block.previous_hash = cls.genesis_hash

        last_block = cls.chain[-1]

        # Calculate hash for the new block based on the previous hash
        new_hash = Block.calculate_hash(
            last_block.index + 1,
            last_block.timestamp,
            block.data,
            last_block.hash
        )

        # Replace <BLOCKCHAIN_ID> with the appropriate value for your use case.
        blockchain_id = 1

        # Insert the new block into the database
        MySQLConnection(cls.dB).query_db(query, {
            **block.to_dict(),
            "previous_hash": last_block.hash,
            "hash": new_hash,
            "blockchain_id": blockchain_id
        })

        cls.chain.append(block)