# src/utils/security.py

from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class Security:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        if not self.key:
            self.key = Fernet.generate_key()
            logger.info("Generated new encryption key.")
        self.cipher_suite = Fernet(self.key)
    
    def encrypt(self, plaintext: str) -> bytes:
        try:
            return self.cipher_suite.encrypt(plaintext.encode())
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return b""
    
    def decrypt(self, ciphertext: bytes) -> str:
        try:
            return self.cipher_suite.decrypt(ciphertext).decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return ""
