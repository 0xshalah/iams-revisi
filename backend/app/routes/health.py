"""Health check endpoint — minimal, no internal details exposed."""
from flask import Blueprint, current_app, jsonify

from app.extensions import db

bp = Blueprint('health', __name__, url_prefix='/api')


@bp.route('/health', methods=['GET'])
def health():
    db_ok = False
    try:
        db.session.execute(db.text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False

    status = 'healthy' if db_ok else 'degraded'

    return jsonify({
        'status': status,
        'database': 'connected' if db_ok else 'unavailable',
    })
