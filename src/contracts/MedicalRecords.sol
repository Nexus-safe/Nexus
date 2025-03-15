// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalRecords {
    struct Record {
        string dataHash;
        address owner;
        uint256 timestamp;
        bool exists;
    }

    struct AccessControl {
        address patient;
        address accessor;
        bool hasAccess;
        uint256 expiryTime;
    }

    mapping(bytes32 => Record) private records;
    mapping(address => mapping(address => AccessControl)) private accessControls;
    mapping(address => bytes32[]) private patientRecords;

    event RecordAdded(bytes32 indexed recordId, address indexed owner, uint256 timestamp);
    event AccessGranted(address indexed patient, address indexed accessor, uint256 expiryTime);
    event AccessRevoked(address indexed patient, address indexed accessor);
    event RecordUpdated(bytes32 indexed recordId, address indexed owner, uint256 timestamp);

    modifier onlyOwner(bytes32 recordId) {
        require(records[recordId].owner == msg.sender, "Not the record owner");
        _;
    }

    modifier hasAccess(address patient) {
        require(
            msg.sender == patient ||
            (accessControls[patient][msg.sender].hasAccess &&
             accessControls[patient][msg.sender].expiryTime > block.timestamp),
            "No access rights"
        );
        _;
    }

    function addRecord(bytes32 recordId, string memory dataHash) public {
        require(!records[recordId].exists, "Record already exists");

        records[recordId] = Record({
            dataHash: dataHash,
            owner: msg.sender,
            timestamp: block.timestamp,
            exists: true
        });

        patientRecords[msg.sender].push(recordId);
        emit RecordAdded(recordId, msg.sender, block.timestamp);
    }

    function updateRecord(bytes32 recordId, string memory newDataHash)
        public
        onlyOwner(recordId)
    {
        require(records[recordId].exists, "Record does not exist");

        records[recordId].dataHash = newDataHash;
        records[recordId].timestamp = block.timestamp;

        emit RecordUpdated(recordId, msg.sender, block.timestamp);
    }

    function grantAccess(address accessor, uint256 durationInDays) public {
        require(accessor != address(0), "Invalid accessor address");
        require(accessor != msg.sender, "Cannot grant access to self");

        uint256 expiryTime = block.timestamp + (durationInDays * 1 days);

        accessControls[msg.sender][accessor] = AccessControl({
            patient: msg.sender,
            accessor: accessor,
            hasAccess: true,
            expiryTime: expiryTime
        });

        emit AccessGranted(msg.sender, accessor, expiryTime);
    }

    function revokeAccess(address accessor) public {
        require(accessor != address(0), "Invalid accessor address");
        require(accessControls[msg.sender][accessor].hasAccess, "No access to revoke");

        accessControls[msg.sender][accessor].hasAccess = false;
        accessControls[msg.sender][accessor].expiryTime = block.timestamp;

        emit AccessRevoked(msg.sender, accessor);
    }

    function getRecord(bytes32 recordId, address patient)
        public
        view
        hasAccess(patient)
        returns (string memory, uint256)
    {
        require(records[recordId].exists, "Record does not exist");
        Record memory record = records[recordId];
        return (record.dataHash, record.timestamp);
    }

    function getPatientRecords(address patient)
        public
        view
        hasAccess(patient)
        returns (bytes32[] memory)
    {
        return patientRecords[patient];
    }

    function checkAccess(address patient, address accessor)
        public
        view
        returns (bool, uint256)
    {
        AccessControl memory access = accessControls[patient][accessor];
        return (access.hasAccess, access.expiryTime);
    }
}