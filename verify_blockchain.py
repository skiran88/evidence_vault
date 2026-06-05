import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vault.blockchain_utils import blockchain_helper as bh
import hashlib

def test_blockchain_integration():
    print("Testing Blockchain Integration...")
    
    if not bh:
        print("Blockchain helper not initialized. Is Ganache running?")
        return

    print(f"Connected to Ganache: {bh.w3.is_connected()}")
    print(f"Using Account: {bh.account}")
    print(f"Contract Address: {bh.contract.address}")

    # Test storage
    test_content = b"Test Evidence Data 123"
    test_case_id = 42
    
    try:
        evidence_hash, tx_hash = bh.store_evidence(test_content, test_case_id)
        print(f"Evidence Hash: {evidence_hash}")
        print(f"Transaction Hash: {tx_hash}")
        
        # Verify on-chain
        on_chain_data = bh.contract.functions.getEvidence(evidence_hash).call()
        print(f"On-chain Verification: {on_chain_data}")
        
        if on_chain_data[0] == evidence_hash and on_chain_data[1] == test_case_id:
            print("BLOCKCHAIN INTEGRATION VERIFIED!")
        else:
            print("On-chain data mismatch!")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_blockchain_integration()
