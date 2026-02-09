"""Security utilities for encrypting sensitive data."""

import os
import base64
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_or_create_key() -> bytes:
    """Get or create encryption key based on machine ID."""
    key_file = Path.home() / ".llmlab" / ".key"
    key_file.parent.mkdir(parents=True, exist_ok=True)
    
    if key_file.exists():
        return key_file.read_bytes()
    
    # Generate a new key
    key = Fernet.generate_key()
    key_file.write_bytes(key)
    key_file.chmod(0o600)  # Only owner can read/write
    return key


def get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption."""
    key = get_or_create_key()
    return Fernet(key)


def encrypt_value(value: str) -> str:
    """Encrypt a string value and return base64 encoded result."""
    if not value:
        return ""
    f = get_fernet()
    encrypted = f.encrypt(value.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a base64 encoded encrypted value."""
    if not encrypted_value:
        return ""
    try:
        f = get_fernet()
        encrypted = base64.urlsafe_b64decode(encrypted_value.encode())
        return f.decrypt(encrypted).decode()
    except Exception:
        return ""


def mask_key(key: str, visible_chars: int = 4) -> str:
    """Mask an API key for display, showing only last N characters."""
    if not key or len(key) <= visible_chars * 2:
        return "****"
    return f"****{key[-visible_chars:]}"
