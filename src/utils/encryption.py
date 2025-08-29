"""
Encryption utilities for the Thai Traditional Medicine RAG Bot.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json
from typing import Dict, Any, Optional

class DataEncryption:
    """Utility class for encrypting and decrypting sensitive data."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize the DataEncryption utility.
        
        Args:
            encryption_key (Optional[str]): Base64 encoded encryption key. 
                                          If not provided, will be loaded from environment or generated.
        """
        if encryption_key:
            self.key = base64.urlsafe_b64decode(encryption_key)
        else:
            # Try to load from environment variable
            encryption_key_env = os.getenv("ENCRYPTION_KEY")
            if encryption_key_env:
                self.key = base64.urlsafe_b64decode(encryption_key_env)
            else:
                # Generate a new key
                self.key = Fernet.generate_key()
                # In production, you should store this key securely
                print("WARNING: Generated new encryption key. Store it securely!")
        
        self.cipher_suite = Fernet(self.key)
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string.
        
        Args:
            plaintext (str): The plaintext to encrypt
            
        Returns:
            str: Base64 encoded encrypted string
        """
        if not plaintext:
            return plaintext
            
        encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_bytes).decode()
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt a string.
        
        Args:
            encrypted_text (str): Base64 encoded encrypted string
            
        Returns:
            str: Decrypted plaintext
        """
        if not encrypted_text:
            return encrypted_text
            
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary by converting it to JSON and then encrypting.
        
        Args:
            data (Dict[str, Any]): The dictionary to encrypt
            
        Returns:
            str: Base64 encoded encrypted string
        """
        if not data:
            return ""
            
        json_string = json.dumps(data)
        return self.encrypt_string(json_string)
    
    def decrypt_dict(self, encrypted_text: str) -> Dict[str, Any]:
        """
        Decrypt a dictionary from an encrypted string.
        
        Args:
            encrypted_text (str): Base64 encoded encrypted string
            
        Returns:
            Dict[str, Any]: Decrypted dictionary
        """
        if not encrypted_text:
            return {}
            
        json_string = self.decrypt_string(encrypted_text)
        return json.loads(json_string)
    
    def get_key(self) -> str:
        """
        Get the base64 encoded encryption key.
        
        Returns:
            str: Base64 encoded encryption key
        """
        return base64.urlsafe_b64encode(self.key).decode()

# Global instance for the application
_encryption_util = None

def get_encryption_util() -> DataEncryption:
    """
    Get the global encryption utility instance.
    
    Returns:
        DataEncryption: The encryption utility instance
    """
    global _encryption_util
    if _encryption_util is None:
        _encryption_util = DataEncryption()
    return _encryption_util

def encrypt_sensitive_data(data: str) -> str:
    """
    Encrypt sensitive data using the global encryption utility.
    
    Args:
        data (str): The data to encrypt
        
    Returns:
        str: Encrypted data
    """
    util = get_encryption_util()
    return util.encrypt_string(data)

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data using the global encryption utility.
    
    Args:
        encrypted_data (str): The encrypted data
        
    Returns:
        str: Decrypted data
    """
    util = get_encryption_util()
    return util.decrypt_string(encrypted_data)