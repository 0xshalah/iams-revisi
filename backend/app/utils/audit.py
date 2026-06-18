"""Audit log helpers."""
from flask import current_app, g, request

from app.extensions import db
from app.models import AuditLog
from app.utils.security import redact


def get_client_ip() -> str:
    """Best-effort client IP extraction."""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def log_audit(action: str, resource_type: str, resource_id: str | None = None,
              status: str = 'success', metadata: dict | None = None):
    """Append-only audit log creation. Never stores plaintext secrets."""
    try:
        actor_id = getattr(g, 'current_user_id', None)
        redacted_metadata = None
        if metadata is not None:
            redacted_metadata = str(redact(metadata))[:2000]
        entry = AuditLog(
            actor_user_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id)[:255] if resource_id else None,
            status=status,
            ip_address=get_client_ip(),
            user_agent=(request.headers.get('User-Agent') or '')[:500],
            metadata_redacted=redacted_metadata,
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('Failed to write audit log')
