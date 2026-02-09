"""
Security utilities for encryption and API key management.

Uses Fernet symmetric encryption for API keys.
"""

from cryptography.fernet import Fernet, InvalidToken

from config import get_settings


def get_fernet() -> Fernet:
    """
    Get Fernet instance for encryption/decryption.

    Returns:
        Fernet: Configured Fernet instance.

    Raises:
        ValueError: If encryption key is invalid.
    """
    settings = get_settings()
    try:
        return Fernet(settings.encryption_key.encode())
    except Exception as e:
        raise ValueError(f"Invalid encryption key: {e}")


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for secure storage.

    Args:
        api_key: Plain text API key to encrypt.

    Returns:
        str: Base64-encoded encrypted key.

    Example:
        >>> encrypted = encrypt_api_key("sk-abc123...")
        >>> # encrypted is safe to store in database
    """
    fernet = get_fernet()
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_key: Base64-encoded encrypted key.

    Returns:
        str: Original plain text API key.

    Raises:
        InvalidToken: If decryption fails (wrong key or corrupted data).

    Example:
        >>> decrypted = decrypt_api_key(encrypted)
        >>> # decrypted contains original "sk-abc123..."
    """
    fernet = get_fernet()
    try:
        decrypted = fernet.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except InvalidToken:
        raise ValueError("Failed to decrypt API key - invalid or corrupted data")


def mask_api_key(api_key: str, show_chars: int = 4) -> str:
    """
    Mask an API key for safe display.

    Shows only the first few characters.

    Args:
        api_key: Full API key to mask.
        show_chars: Number of characters to show at start.

    Returns:
        str: Masked key like "sk-a...****"

    Example:
        >>> mask_api_key("sk-abc123xyz")
        'sk-a...****'
    """
    if len(api_key) <= show_chars:
        return "*" * len(api_key)
    return f"{api_key[:show_chars]}...****"
