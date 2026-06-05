import os
import json
import hashlib
from web3 import Web3
from solcx import compile_standard, install_solc

# Install Solidity compiler
install_solc("0.8.0")

class BlockchainHelper:
    def __init__(self, rpc_url="http://127.0.0.1:7545"):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = None
        self.contract = None
        self.contract_address_file = os.path.join(os.path.dirname(__file__), "contract_address.txt")

        if not self.w3.is_connected():
            print("Blockchain connection failed: Check if Ganache is running on http://127.0.0.1:7545")
            return

        try:
            self.account = self.w3.eth.accounts[0]
            self.load_or_deploy_contract()
        except Exception as e:
            print(f"Blockchain initialization error: {e}")

    def compile_contract(self):
        contract_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contracts", "EvidenceVault.sol")
        with open(contract_path, "r") as file:
            content = file.read()

        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {"EvidenceVault.sol": {"content": content}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                    }
                },
            },
            solc_version="0.8.0",
        )
        return compiled_sol

    def load_or_deploy_contract(self):
        compiled_sol = self.compile_contract()
        abi = compiled_sol["contracts"]["EvidenceVault.sol"]["EvidenceVault"]["abi"]
        bytecode = compiled_sol["contracts"]["EvidenceVault.sol"]["EvidenceVault"]["evm"]["bytecode"]["object"]

        if os.path.exists(self.contract_address_file):
            with open(self.contract_address_file, "r") as f:
                address = f.read().strip()
            self.contract = self.w3.eth.contract(address=address, abi=abi)
        else:
            # Deploy
            print("Deploying contract...")
            EvidenceVault = self.w3.eth.contract(abi=abi, bytecode=bytecode)
            tx_hash = EvidenceVault.constructor().transact({"from": self.account})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            address = tx_receipt.contractAddress
            
            with open(self.contract_address_file, "w") as f:
                f.write(address)
            
            self.contract = self.w3.eth.contract(address=address, abi=abi)
            print(f"Contract deployed at {address}")

    def get_current_block(self):
        if not self.w3.is_connected():
            return 0
        return self.w3.eth.block_number

    def store_evidence(self, file_content, case_id):
        evidence_hash = hashlib.sha256(file_content).hexdigest()
        
        tx_hash = self.contract.functions.storeEvidence(evidence_hash, int(case_id)).transact({"from": self.account})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return evidence_hash, tx_hash.hex()

def tx_receipt_hash_to_str(tx_hash):
    if isinstance(tx_hash, bytes):
        return tx_hash.hex()
    return str(tx_hash)

try:
    blockchain_helper = BlockchainHelper()
except Exception as e:
    print(f"Blockchain setup error: {e}")
