// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EvidenceVault {
    struct Evidence {
        string evidenceHash;
        uint256 caseId;
        address uploader;
        uint256 timestamp;
    }

    mapping(string => Evidence) public evidences;
    string[] public evidenceHashes;

    event EvidenceStored(string evidenceHash, uint256 caseId, address uploader, uint256 timestamp);

    function storeEvidence(string memory _evidenceHash, uint256 _caseId) public {
        require(bytes(evidences[_evidenceHash].evidenceHash).length == 0, "Evidence already exists");

        evidences[_evidenceHash] = Evidence({
            evidenceHash: _evidenceHash,
            caseId: _caseId,
            uploader: msg.sender,
            timestamp: block.timestamp
        });

        evidenceHashes.push(_evidenceHash);

        emit EvidenceStored(_evidenceHash, _caseId, msg.sender, block.timestamp);
    }

    function getEvidence(string memory _evidenceHash) public view returns (string memory, uint256, address, uint256) {
        Evidence memory e = evidences[_evidenceHash];
        return (e.evidenceHash, e.caseId, e.uploader, e.timestamp);
    }

    function getEvidenceCount() public view returns (uint256) {
        return evidenceHashes.length;
    }
}
