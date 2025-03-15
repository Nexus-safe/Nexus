from typing import List, Dict, Any
from web3 import Web3
from datetime import datetime
import json
import hashlib


class MedicalBlockchain:
    def __init__(self, provider_url: str):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.chain: List[Dict[str, Any]] = []
        self.pending_transactions = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = {
            "index": 0,
            "timestamp": str(datetime.now()),
            "transactions": [],
            "previous_hash": "0" * 64,
            "nonce": 0,
        }
        genesis_block["hash"] = self._calculate_hash(genesis_block)
        self.chain.append(genesis_block)

    def _calculate_hash(self, block: Dict[str, Any]) -> str:
        """Calculate hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_transaction(self, sender: str, recipient: str, data: Dict[str, Any]):
        """Add a new transaction to pending transactions"""
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "data": data,
            "timestamp": str(datetime.now()),
        }
        self.pending_transactions.append(transaction)
        return self.get_last_block()["index"] + 1

    def mine_block(self, miner_address: str) -> Dict[str, Any]:
        """Mine a new block with pending transactions"""
        previous_block = self.get_last_block()
        new_block = {
            "index": previous_block["index"] + 1,
            "timestamp": str(datetime.now()),
            "transactions": self.pending_transactions,
            "previous_hash": previous_block["hash"],
            "nonce": 0,
        }

        # Proof of Work
        while not self._is_hash_valid(self._calculate_hash(new_block)):
            new_block["nonce"] += 1

        new_block["hash"] = self._calculate_hash(new_block)
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def _is_hash_valid(self, hash_string: str) -> bool:
        """Check if hash meets difficulty requirements"""
        return hash_string.startswith("0000")

    def get_last_block(self) -> Dict[str, Any]:
        """Return the last block in the chain"""
        return self.chain[-1]

    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block["previous_hash"] != previous_block["hash"]:
                return False

            if not self._is_hash_valid(current_block["hash"]):
                return False

            if self._calculate_hash(current_block) != current_block["hash"]:
                return False

        return True

    def get_patient_data(self, patient_address: str) -> List[Dict[str, Any]]:
        """Retrieve all medical records for a specific patient"""
        patient_records = []
        for block in self.chain:
            for transaction in block["transactions"]:
                if transaction["recipient"] == patient_address:
                    patient_records.append(transaction)
        return patient_records
