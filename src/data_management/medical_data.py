from typing import Dict, List, Optional, Any
from datetime import datetime
from cryptography.fernet import Fernet
import json
import base64


class MedicalRecord:
    def __init__(self, patient_id: str, data: Dict[str, Any], encryption_key: bytes):
        self.patient_id = patient_id
        self.timestamp = datetime.now()
        self.encryption_handler = Fernet(encryption_key)
        self.encrypted_data = self._encrypt_data(data)
        self.access_log = []

    def _encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt medical data"""
        json_data = json.dumps(data)
        return self.encryption_handler.encrypt(json_data.encode())

    def decrypt_data(self) -> Dict[str, Any]:
        """Decrypt medical data"""
        decrypted_data = self.encryption_handler.decrypt(self.encrypted_data)
        return json.loads(decrypted_data.decode())

    def log_access(self, accessor_id: str, purpose: str):
        """Log access to medical record"""
        access_entry = {
            "accessor_id": accessor_id,
            "timestamp": datetime.now(),
            "purpose": purpose,
        }
        self.access_log.append(access_entry)


class MedicalDataManager:
    def __init__(self):
        self.records: Dict[str, List[MedicalRecord]] = {}
        self.encryption_key = Fernet.generate_key()
        self.access_policies: Dict[str, List[str]] = {}

    def add_record(self, patient_id: str, data: Dict[str, Any]) -> str:
        """Add a new medical record"""
        if patient_id not in self.records:
            self.records[patient_id] = []

        record = MedicalRecord(patient_id, data, self.encryption_key)
        self.records[patient_id].append(record)
        return str(len(self.records[patient_id]) - 1)

    def get_record(
        self, patient_id: str, record_index: int, accessor_id: str, purpose: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a specific medical record"""
        if not self._check_access_permission(patient_id, accessor_id):
            raise PermissionError("Access denied")

        if patient_id in self.records and 0 <= record_index < len(
            self.records[patient_id]
        ):
            record = self.records[patient_id][record_index]
            record.log_access(accessor_id, purpose)
            return record.decrypt_data()
        return None

    def get_patient_history(
        self, patient_id: str, accessor_id: str
    ) -> List[Dict[str, Any]]:
        """Retrieve patient's complete medical history"""
        if not self._check_access_permission(patient_id, accessor_id):
            raise PermissionError("Access denied")

        if patient_id not in self.records:
            return []

        history = []
        for record in self.records[patient_id]:
            record.log_access(accessor_id, "History review")
            history.append(record.decrypt_data())
        return history

    def grant_access(self, patient_id: str, accessor_id: str):
        """Grant access to medical records"""
        if patient_id not in self.access_policies:
            self.access_policies[patient_id] = []
        if accessor_id not in self.access_policies[patient_id]:
            self.access_policies[patient_id].append(accessor_id)

    def revoke_access(self, patient_id: str, accessor_id: str):
        """Revoke access to medical records"""
        if (
            patient_id in self.access_policies
            and accessor_id in self.access_policies[patient_id]
        ):
            self.access_policies[patient_id].remove(accessor_id)

    def _check_access_permission(self, patient_id: str, accessor_id: str) -> bool:
        """Check if accessor has permission to access patient's records"""
        return patient_id == accessor_id or (
            patient_id in self.access_policies
            and accessor_id in self.access_policies[patient_id]
        )

    def get_access_log(self, patient_id: str, accessor_id: str) -> List[Dict[str, Any]]:
        """Get access log for patient's records"""
        if not self._check_access_permission(patient_id, accessor_id):
            raise PermissionError("Access denied")

        if patient_id not in self.records:
            return []

        all_logs = []
        for record in self.records[patient_id]:
            all_logs.extend(record.access_log)
        return all_logs

    def update_record(
        self,
        patient_id: str,
        record_index: int,
        accessor_id: str,
        updated_data: Dict[str, Any],
    ) -> bool:
        """Update an existing medical record"""
        if not self._check_access_permission(patient_id, accessor_id):
            raise PermissionError("Access denied")

        if patient_id in self.records and 0 <= record_index < len(
            self.records[patient_id]
        ):

            record = self.records[patient_id][record_index]
            new_record = MedicalRecord(patient_id, updated_data, self.encryption_key)
            new_record.access_log = record.access_log
            new_record.log_access(accessor_id, "Record update")
            self.records[patient_id][record_index] = new_record
            return True
        return False
