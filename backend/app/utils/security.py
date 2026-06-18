"""Security utilities: password hashing, AES-256-GCM, redaction."""
import base64
import os
import re

import bcrypt
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


SENSITIVE_KEYS = (
    'password', 'password_hash', 'secret', 'token', 'access_token', 'refresh_token',
    'aes_key', 'jwt_secret', 'encrypted_secret', 'nonce', 'authorization',
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def encrypt_secret(plaintext: str, key: bytes) -> tuple[str, str]:
    """Encrypt plaintext with AES-256-GCM; return (ciphertext_b64, nonce_b64)."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit IV/nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(ciphertext).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')


def decrypt_secret(ciphertext_b64: str, nonce_b64: str, key: bytes) -> str:
    """Decrypt AES-256-GCM ciphertext; raise ValueError on failure."""
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(
            base64.b64decode(nonce_b64),
            base64.b64decode(ciphertext_b64),
            None,
        )
    except InvalidTag as exc:
        raise ValueError('Credential decryption failed') from exc
    return plaintext.decode('utf-8')


def redact(value: dict | list | str | None) -> dict | list | str | None:
    """Recursively redact sensitive-looking keys from structures."""
    if isinstance(value, dict):
        return {
            k: '***REDACTED***' if any(s in str(k).lower() for s in SENSITIVE_KEYS) else redact(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def sanitize_error_message(message: str) -> str:
    """Remove paths, query hints, and stack traces from error messages."""
    if not isinstance(message, str):
        return 'An error occurred'
    # Remove filesystem paths
    message = re.sub(r'[A-Za-z]:\\[^\s]+|/[^\s]*', '[path]', message)
    # Remove SQLAlchemy internal markers
    message = re.sub(r'\(.*\)', '', message)
    return message.strip() or 'An error occurred'
