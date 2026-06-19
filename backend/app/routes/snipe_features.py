"""Asset files, checkout, licenses, status labels routes."""
from datetime import date, datetime, timezone
import uuid

from flask import Blueprint, g, jsonify, request, send_file
import io

from app.extensions import db
from app.models import Asset, AssetFile, CheckoutHistory, SoftwareLicense, StatusLabel
from app.utils.audit import log_audit
from app.utils.decorators import admin_only, admin_or_operator, require_csrf
from app.utils.pagination import paginate

bp = Blueprint('snipe_features', __name__, url_prefix='/api')

# ── Asset Files ─────────────────────────────────────────────────────────────

@bp.route('/assets/<int:asset_id>/files', methods=['GET'])
@admin_or_operator
def list_files(asset_id):
    if not db.session.get(Asset, asset_id):
        return jsonify({'error': 'Asset not found'}), 404
    files = AssetFile.query.filter_by(asset_id=asset_id).order_by(AssetFile.created_at.desc()).all()
    return jsonify({'data': [f.to_dict() for f in files]})

@bp.route('/assets/<int:asset_id>/files', methods=['POST'])
@admin_or_operator
@require_csrf
def upload_file(asset_id):
    if not db.session.get(Asset, asset_id):
        return jsonify({'error': 'Asset not found'}), 404
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400
    af = AssetFile(
        asset_id=asset_id,
        filename=f'{uuid.uuid4().hex}_{file.filename}',
        original_name=file.filename,
        mime_type=file.mimetype,
        size=file.content_length or 0,
        data=file.read(),
    )
    db.session.add(af)
    db.session.commit()
    log_audit('UPLOAD', 'asset_file', resource_id=asset_id, status='success')
    return jsonify({'data': af.to_dict()}), 201

@bp.route('/assets/<int:asset_id>/files/<int:file_id>', methods=['GET'])
@admin_or_operator
def download_file(asset_id, file_id):
    af = AssetFile.query.filter_by(id=file_id, asset_id=asset_id).first()
    if not af:
        return jsonify({'error': 'File not found'}), 404
    return send_file(io.BytesIO(af.data), mimetype=af.mime_type,
                     download_name=af.original_name, as_attachment=True)

@bp.route('/assets/<int:asset_id>/files/<int:file_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_file(asset_id, file_id):
    af = AssetFile.query.filter_by(id=file_id, asset_id=asset_id).first()
    if not af:
        return jsonify({'error': 'File not found'}), 404
    db.session.delete(af)
    db.session.commit()
    return jsonify({'message': 'File deleted'})

# ── Status Labels ───────────────────────────────────────────────────────────

@bp.route('/status-labels', methods=['GET'])
@admin_or_operator
def list_status_labels():
    rows = StatusLabel.query.order_by(StatusLabel.name).all()
    return jsonify({'data': [r.to_dict() for r in rows]})

@bp.route('/status-labels', methods=['POST'])
@admin_only
@require_csrf
def create_status_label():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    if StatusLabel.query.filter_by(name=name).first():
        return jsonify({'error': 'Status label already exists'}), 409
    sl = StatusLabel(name=name, deployable=data.get('deployable', True))
    db.session.add(sl)
    db.session.commit()
    return jsonify({'data': sl.to_dict()}), 201

@bp.route('/status-labels/<int:sl_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_status_label(sl_id):
    sl = db.session.get(StatusLabel, sl_id)
    if not sl:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(sl)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# ── Software Licenses ───────────────────────────────────────────────────────

@bp.route('/licenses', methods=['GET'])
@admin_or_operator
def list_licenses():
    query = SoftwareLicense.query.order_by(SoftwareLicense.name)
    return jsonify(paginate(query))

@bp.route('/licenses', methods=['POST'])
@admin_or_operator
@require_csrf
def create_license():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    lic = SoftwareLicense(
        name=name,
        product_key=data.get('product_key'),
        seats=int(data.get('seats', 1)),
        licensed_to_email=data.get('licensed_to_email'),
        purchase_date=date.fromisoformat(data['purchase_date']) if data.get('purchase_date') else None,
        expiration_date=date.fromisoformat(data['expiration_date']) if data.get('expiration_date') else None,
        notes=(data.get('notes') or '').strip() or None,
    )
    db.session.add(lic)
    db.session.commit()
    log_audit('CREATE', 'software_license', resource_id=lic.id, status='success')
    return jsonify({'data': lic.to_dict()}), 201

@bp.route('/licenses/<int:lic_id>', methods=['PUT'])
@admin_or_operator
@require_csrf
def update_license(lic_id):
    lic = db.session.get(SoftwareLicense, lic_id)
    if not lic:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json(silent=True) or {}
    for f in ['name', 'product_key', 'licensed_to_email', 'notes']:
        if f in data:
            setattr(lic, f, data[f].strip() if isinstance(data[f], str) else data[f])
    for f in ['seats']:
        if f in data:
            setattr(lic, f, int(data[f]))
    for f in ['purchase_date', 'expiration_date']:
        if f in data:
            v = data[f]
            setattr(lic, f, date.fromisoformat(v) if v else None)
    db.session.commit()
    return jsonify({'data': lic.to_dict()})

@bp.route('/licenses/<int:lic_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_license(lic_id):
    lic = db.session.get(SoftwareLicense, lic_id)
    if not lic:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(lic)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# ── Checkout History ────────────────────────────────────────────────────────

@bp.route('/assets/<int:asset_id>/checkout', methods=['POST'])
@admin_or_operator
@require_csrf
def checkout_asset(asset_id):
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    ch = CheckoutHistory(
        asset_id=asset_id, user_id=int(user_id), action='checkout',
        expected_return_date=date.fromisoformat(data['expected_return_date']) if data.get('expected_return_date') else None,
        notes=(data.get('notes') or '').strip() or None,
        checked_out_by=g.current_user_id,
    )
    asset.user_id = int(user_id)
    db.session.add(ch)
    db.session.commit()
    log_audit('CHECKOUT', 'asset', resource_id=asset_id, status='success')
    return jsonify({'data': ch.to_dict()}), 201

@bp.route('/assets/<int:asset_id>/checkin', methods=['POST'])
@admin_or_operator
@require_csrf
def checkin_asset(asset_id):
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    data = request.get_json(silent=True) or {}
    ch = CheckoutHistory(
        asset_id=asset_id, user_id=asset.user_id, action='checkin',
        notes=(data.get('notes') or '').strip() or None,
        checked_out_by=g.current_user_id,
    )
    asset.user_id = None
    db.session.add(ch)
    db.session.commit()
    log_audit('CHECKIN', 'asset', resource_id=asset_id, status='success')
    return jsonify({'data': ch.to_dict()})

@bp.route('/assets/<int:asset_id>/history', methods=['GET'])
@admin_or_operator
def asset_history(asset_id):
    rows = CheckoutHistory.query.filter_by(asset_id=asset_id).order_by(CheckoutHistory.created_at.desc()).limit(50).all()
    return jsonify({'data': [r.to_dict() for r in rows]})
