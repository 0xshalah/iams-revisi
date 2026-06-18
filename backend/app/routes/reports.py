"""Reports blueprint (Administrator only)."""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request

from app.models import Asset
from app.utils.decorators import admin_only

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/assets/full', methods=['GET'])
@admin_only
def full_asset_report():
    assets = Asset.query.order_by(Asset.asset_tag).all()
    return {'data': [a.to_dict() for a in assets]}


@bp.route('/assets/status-summary', methods=['GET'])
@admin_only
def status_summary():
    statuses = ['Active', 'Available', 'Repair', 'Disposed']
    summary = {s: Asset.query.filter_by(status=s).count() for s in statuses}
    summary['total'] = sum(summary.values())
    return {'data': summary}


@bp.route('/assets/by-po', methods=['GET'])
@admin_only
def by_po():
    po = (request.args.get('po_number') or '').strip()
    if not po:
        return {'error': 'po_number is required'}, 400
    assets = Asset.query.filter(Asset.po_number.like(f'%{po}%')).all()
    return {'data': [a.to_dict() for a in assets]}


@bp.route('/assets/warranty-expiring', methods=['GET'])
@admin_only
def warranty_expiring():
    try:
        months = int(request.args.get('months', 3))
    except ValueError:
        return {'error': 'months must be an integer'}, 400

    today = datetime.now(timezone.utc).date()
    threshold = today + timedelta(days=months * 30)
    assets = Asset.query.filter(
        Asset.purchase_date.isnot(None),
        Asset.warranty_months.isnot(None),
    ).all()
    result = []
    for a in assets:
        if not a.purchase_date or not a.warranty_months:
            continue
        expiry = a.purchase_date + timedelta(days=a.warranty_months * 30)
        remaining = (expiry - today).days
        if expiry <= threshold:
            data = a.to_dict()
            data['warranty_expiry'] = expiry.isoformat()
            data['warranty_remaining_days'] = max(0, remaining)
            data['warranty_status'] = 'expired' if remaining < 0 else 'expiring'
            result.append(data)
    return {'data': result}
