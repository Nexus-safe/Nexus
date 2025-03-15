from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64
import os


class EncryptionManager:
    def __init__(self):
        self.symmetric_key = None
        self.private_key = None
        self.public_key = None

    def generate_symmetric_key(self):
        """Generate a new symmetric encryption key"""
        self.symmetric_key = Fernet.generate_key()
        return self.symmetric_key

    def generate_asymmetric_keys(self):
        """Generate RSA key pair"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        self.public_key = self.private_key.public_key()
        return self.public_key

    def encrypt_symmetric(self, data: bytes) -> bytes:
        """Encrypt data using symmetric encryption"""
        if not self.symmetric_key:
            raise ValueError("Symmetric key not initialized")

        f = Fernet(self.symmetric_key)
        return f.encrypt(data)

    def decrypt_symmetric(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using symmetric encryption"""
        if not self.symmetric_key:
            raise ValueError("Symmetric key not initialized")

        f = Fernet(self.symmetric_key)
        return f.decrypt(encrypted_data)

    def encrypt_asymmetric(self, data: bytes) -> bytes:
        """Encrypt data using asymmetric encryption"""
        if not self.public_key:
            raise ValueError("Public key not initialized")

        return self.public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def decrypt_asymmetric(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using asymmetric encryption"""
        if not self.private_key:
            raise ValueError("Private key not initialized")

        return self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def export_public_key(self) -> bytes:
        """Export public key in PEM format"""
        if not self.public_key:
            raise ValueError("Public key not initialized")

        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def export_private_key(self, password: bytes) -> bytes:
        """Export encrypted private key in PEM format"""
        if not self.private_key:
            raise ValueError("Private key not initialized")

        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        )

    @staticmethod
    def generate_key_from_password(password: str, salt: bytes = None) -> bytes:
        """Generate encryption key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def hash_data(data: bytes) -> bytes:
        """Generate SHA-256 hash of data"""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        return digest.finalize()

    def secure_key_exchange(self, other_public_key_pem: bytes) -> bytes:
        """Perform secure key exchange"""
        other_public_key = serialization.load_pem_public_key(other_public_key_pem)

        # Generate a new symmetric key for the session
        session_key = Fernet.generate_key()

        # Encrypt the session key with the other party's public key
        encrypted_session_key = other_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return encrypted_session_key
