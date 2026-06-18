"""Application configuration with fail-fast secret validation."""
import base64
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


def _load_env(key: str, default=None, required: bool = True):
    value = os.environ.get(key, default)
    if required and not value:
        raise RuntimeError(f'Missing required environment variable: {key}')
    return value


def _validate_aes_key(key_b64: str) -> bytes:
    try:
        key = base64.b64decode(key_b64, validate=True)
    except Exception as exc:
        raise RuntimeError('AES_KEY_BASE64 is not valid base64') from exc
    if len(key) != 32:
        raise RuntimeError(f'AES key must be exactly 32 bytes, got {len(key)} bytes')
    return key


def _validate_jwt_secret(secret: str) -> str:
    if len(secret.encode()) < 32:
        raise RuntimeError('JWT_SECRET must be at least 32 bytes')
    return secret


class Config:
    """Base configuration."""

    # Database
    SQLALCHEMY_DATABASE_URI = _load_env('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secrets (validated at import time -> fail fast)
    JWT_SECRET = _validate_jwt_secret(_load_env('JWT_SECRET'))
    AES_KEY = _validate_aes_key(_load_env('AES_KEY_BASE64'))

    # CORS / Frontend
    FRONTEND_ORIGIN = _load_env('FRONTEND_ORIGIN')

    # Cookie settings
    COOKIE_SECURE = _load_env('COOKIE_SECURE', 'false').lower() in ('true', '1', 'yes')
    COOKIE_SAMESITE = _load_env('COOKIE_SAMESITE', 'Lax')

    # Flask
    FLASK_ENV = _load_env('FLASK_ENV', 'production')
    DEBUG = (FLASK_ENV == 'development')

    # Hard safety gate: never allow DEBUG in production
    if FLASK_ENV != 'development':
        DEBUG = False

    # Security headers
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 8 * 60 * 60  # 8 hours
    CSRF_COOKIE_NAME = 'csrf_token'
    JWT_COOKIE_NAME = 'access_token'

    # Rate limiting (can be disabled for integration tests)
    RATELIMIT_ENABLED = _load_env('RATELIMIT_ENABLED', 'true', required=False).lower() in ('true', '1', 'yes')
    RATELIMIT_STORAGE_URI = _load_env('RATELIMIT_STORAGE_URI', 'memory://', required=False)
