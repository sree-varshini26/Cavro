import hashlib
import json
import time
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Block:
    """Represents a block in the blockchain."""
    index: int
    timestamp: str
    data: Dict[str, Any]
    previous_hash: str
    nonce: int = 0
    hash: str = field(init=False)
    
    def __post_init__(self):
        """Calculate the block's hash after initialization."""
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the SHA-256 hash of the block."""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """Mine the block with the given difficulty."""
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    """A simple blockchain implementation for resume verification."""
    
    def __init__(self, difficulty: int = 4):
        """Initialize the blockchain with a genesis block."""
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = difficulty
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the genesis block (first block in the chain)."""
        genesis_block = Block(
            index=0,
            timestamp=str(datetime.utcnow()),
            data={
                'type': 'genesis',
                'message': 'Genesis block for Resume Verification Blockchain'
            },
            previous_hash='0' * 64  # Hash for the first block
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
    
    @property
    def last_block(self) -> Block:
        """Get the most recent block in the chain."""
        return self.chain[-1]
    
    def add_transaction(self, data: Dict[str, Any]) -> int:
        """Add a new transaction to the list of pending transactions."""
        self.pending_transactions.append({
            **data,
            'timestamp': str(datetime.utcnow())
        })
        return self.last_block.index + 1  # Index of the block that will contain this transaction
    
    def mine_pending_transactions(self, miner_address: str) -> Block:
        """Mine all pending transactions."""
        if not self.pending_transactions:
            raise ValueError("No transactions to mine")
        
        # Create a new block with all pending transactions
        new_block = Block(
            index=len(self.chain),
            timestamp=str(datetime.utcnow()),
            data={
                'transactions': self.pending_transactions.copy(),
                'miner': miner_address,
                'block_reward': 1.0  # Simulate block reward
            },
            previous_hash=self.last_block.hash
        )
        
        # Mine the block (proof of work)
        logger.info(f"Mining block {new_block.index}...")
        start_time = time.time()
        new_block.mine_block(self.difficulty)
        mining_time = time.time() - start_time
        
        logger.info(f"Block {new_block.index} mined in {mining_time:.2f} seconds. Hash: {new_block.hash}")
        
        # Add the block to the chain
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return new_block
    
    def is_chain_valid(self) -> bool:
        """Check if the blockchain is valid."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if the current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"Block {current_block.index} has an invalid hash")
                return False
            
            # Check if the previous hash matches
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Block {current_block.index} has an invalid previous hash")
                return False
            
            # Check if the proof of work is valid
            if current_block.hash[:self.difficulty] != '0' * self.difficulty:
                logger.error(f"Block {current_block.index} has an invalid proof of work")
                return False
        
        return True
    
    def verify_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Verify a resume by adding it to the blockchain and returning the verification details.
        
        Args:
            resume_text: The text content of the resume to verify
            
        Returns:
            A dictionary containing verification details
        """
        if not resume_text or not isinstance(resume_text, str):
            raise ValueError("Resume text must be a non-empty string")
        
        # Create a hash of the resume content
        resume_hash = hashlib.sha256(resume_text.encode()).hexdigest()
        
        # Create a verification record
        verification_id = f"VER-{int(time.time())}-{resume_hash[:8]}"
        
        # Add the verification as a transaction
        verification_data = {
            'type': 'resume_verification',
            'verification_id': verification_id,
            'resume_hash': resume_hash,
            'timestamp': str(datetime.utcnow()),
            'status': 'pending'
        }
        
        # Add to pending transactions
        block_index = self.add_transaction(verification_data)
        
        # Mine the block (in a real implementation, this would be done by miners)
        try:
            block = self.mine_pending_transactions("cavro_verification_node")
            verification_data['status'] = 'verified'
            verification_data['block_index'] = block.index
            verification_data['block_hash'] = block.hash
            verification_data['transaction_index'] = len(block.data['transactions']) - 1
        except Exception as e:
            logger.error(f"Failed to mine block: {e}")
            verification_data['status'] = 'failed'
            verification_data['error'] = str(e)
        
        return verification_data
    
    def get_verification_status(self, verification_id: str) -> Dict[str, Any]:
        """
        Get the status of a resume verification.
        
        Args:
            verification_id: The ID of the verification to check
            
        Returns:
            A dictionary containing the verification status and details
        """
        # Check pending transactions first
        for tx in self.pending_transactions:
            if tx.get('verification_id') == verification_id:
                return {
                    'verification_id': verification_id,
                    'status': 'pending',
                    'timestamp': tx.get('timestamp')
                }
        
        # Check the blockchain
        for block in self.chain[1:]:  # Skip genesis block
            if 'transactions' in block.data:
                for i, tx in enumerate(block.data['transactions']):
                    if tx.get('verification_id') == verification_id:
                        return {
                            'verification_id': verification_id,
                            'status': 'verified',
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'transaction_index': i,
                            'timestamp': tx.get('timestamp'),
                            'resume_hash': tx.get('resume_hash')
                        }
        
        return {
            'verification_id': verification_id,
            'status': 'not_found',
            'message': 'No verification found with the given ID'
        }

# Singleton instance of the blockchain
_blockchain_instance = None

def get_blockchain() -> Blockchain:
    """Get or create a singleton instance of the blockchain."""
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = Blockchain(difficulty=2)  # Lower difficulty for demo purposes
    return _blockchain_instance

def blockchain_verify(resume_text: str) -> Dict[str, Any]:
    """
    Verify a resume by adding it to the blockchain.
    
    Args:
        resume_text: The text content of the resume to verify
        
    Returns:
        A dictionary containing verification details
    """
    blockchain = get_blockchain()
    return blockchain.verify_resume(resume_text)

def get_verification_status(verification_id: str) -> Dict[str, Any]:
    """
    Get the status of a resume verification.
    
    Args:
        verification_id: The ID of the verification to check
        
    Returns:
        A dictionary containing the verification status and details
    """
    blockchain = get_blockchain()
    return blockchain.get_verification_status(verification_id)
