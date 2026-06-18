"""Assets blueprint."""
from datetime import date, datetime, timezone

from flask import Blueprint, current_app, g, jsonify, request

from app.extensions import db
from app.models import Asset, AssetCredential, NetworkDetail
from app.utils.audit import log_audit
from app.utils.decorators import admin_or_operator, audit_action, require_csrf, require_role
from app.utils.pagination import paginate
from app.utils.security import decrypt_secret, encrypt_secret

bp = Blueprint('assets', __name__, url_prefix='/api/assets')


ASSET_STATUSES = {'Active', 'Available', 'Repair', 'Disposed'}


def _validate_asset_payload(data: dict, updating: bool = False) -> tuple[dict | None, int | None]:
    required = {'asset_tag', 'serial_number', 'model_id', 'location_id'}
    if not updating:
        missing = required - set(data.keys())
        if missing:
            return {'error': f'Missing fields: {", ".join(missing)}'}, 400
    if not updating or 'serial_number' in data:
        serial = str(data.get('serial_number', '')).strip()
        if not serial:
            return {'error': 'serial_number is required'}, 400
    status = data.get('status', 'Available')
    if status not in ASSET_STATUSES:
        return {'error': f'Invalid status. Allowed: {", ".join(ASSET_STATUSES)}'}, 400
    return None, None


@bp.route('', methods=['GET'])
@admin_or_operator
def list_assets():
    query = Asset.query
    status = request.args.get('status')
    location_id = request.args.get('location_id')
    model_id = request.args.get('model_id')
    if status:
        query = query.filter_by(status=status)
    if location_id:
        query = query.filter_by(location_id=location_id)
    if model_id:
        query = query.filter_by(model_id=model_id)
    rows = query.order_by(Asset.asset_tag)
    return jsonify(paginate(rows))


@bp.route('', methods=['POST'])
@admin_or_operator
@require_csrf
@audit_action('CREATE', 'asset')
def create_asset():
    data = request.get_json(silent=True) or {}
    err, code = _validate_asset_payload(data)
    if err:
        return jsonify(err), code

    if Asset.query.filter_by(asset_tag=data['asset_tag'].strip()).first():
        return jsonify({'error': 'Asset tag already exists'}), 409
    if Asset.query.filter_by(serial_number=data['serial_number'].strip()).first():
        return jsonify({'error': 'Serial number already exists'}), 409

    asset = Asset(
        asset_tag=data['asset_tag'].strip(),
        serial_number=data['serial_number'].strip(),
        po_number=(data.get('po_number') or '').strip() or None,
        model_id=int(data['model_id']),
        location_id=int(data['location_id']),
        user_id=data.get('user_id'),
        status=data.get('status', 'Available'),
        purchase_date=date.fromisoformat(data['purchase_date']) if data.get('purchase_date') else None,
        warranty_months=data.get('warranty_months'),
        os_license=(data.get('os_license') or '').strip() or None,
    )
    db.session.add(asset)
    db.session.flush()

    net = data.get('network_detail') or {}
    if any(net.get(k) for k in ('ip_address', 'mac_address', 'hostname', 'vlan', 'notes')):
        nd = NetworkDetail(
            asset_id=asset.id,
            ip_address=(net.get('ip_address') or '').strip() or None,
            mac_address=(net.get('mac_address') or '').strip() or None,
            hostname=(net.get('hostname') or '').strip() or None,
            vlan=(net.get('vlan') or '').strip() or None,
            notes=(net.get('notes') or '').strip() or None,
        )
        db.session.add(nd)

    credential_plain = (data.get('credential') or '').strip()
    if credential_plain:
        enc, nonce = encrypt_secret(credential_plain, current_app.config['AES_KEY'])
        db.session.add(AssetCredential(asset_id=asset.id, encrypted_secret=enc, nonce=nonce))
        log_audit('CREATE', 'asset_credential', resource_id=asset.id, status='success',
                  metadata={'action': 'credential_created'})

    db.session.commit()
    return jsonify({'data': asset.to_dict()}), 201


@bp.route('/<int:asset_id>', methods=['GET'])
@admin_or_operator
def get_asset(asset_id):
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    return jsonify({'data': asset.to_dict()})


@bp.route('/<int:asset_id>', methods=['PUT'])
@admin_or_operator
@require_csrf
@audit_action('UPDATE', 'asset', resource_id_key='asset_id')
def update_asset(asset_id):
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    data = request.get_json(silent=True) or {}
    err, code = _validate_asset_payload(data, updating=True)
    if err:
        return jsonify(err), code

    if 'asset_tag' in data:
        new_tag = data['asset_tag'].strip()
        if new_tag != asset.asset_tag and Asset.query.filter_by(asset_tag=new_tag).first():
            return jsonify({'error': 'Asset tag already exists'}), 409
        asset.asset_tag = new_tag
    if 'serial_number' in data:
        new_serial = data['serial_number'].strip()
        if not new_serial:
            return jsonify({'error': 'serial_number cannot be empty'}), 400
        if new_serial != asset.serial_number and Asset.query.filter_by(serial_number=new_serial).first():
            return jsonify({'error': 'Serial number already exists'}), 409
        asset.serial_number = new_serial
    if 'po_number' in data:
        asset.po_number = (data['po_number'] or '').strip() or None
    if 'model_id' in data:
        asset.model_id = int(data['model_id'])
    if 'location_id' in data:
        asset.location_id = int(data['location_id'])
    if 'user_id' in data:
        asset.user_id = data['user_id']
    if 'status' in data:
        asset.status = data['status']
    if 'purchase_date' in data:
        asset.purchase_date = date.fromisoformat(data['purchase_date']) if data['purchase_date'] else None
    if 'warranty_months' in data:
        asset.warranty_months = data['warranty_months']
    if 'os_license' in data:
        asset.os_license = (data['os_license'] or '').strip() or None

    asset.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'data': asset.to_dict()})


@bp.route('/<int:asset_id>', methods=['DELETE'])
@require_role('Administrator')
@require_csrf
@audit_action('DELETE', 'asset', resource_id_key='asset_id')
def delete_asset(asset_id):
    """Only administrators may delete assets."""
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Asset deleted'})


@bp.route('/<int:asset_id>/network-details', methods=['GET'])
@admin_or_operator
def get_network_details(asset_id):
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    nd = asset.network_detail
    return jsonify({'data': nd.to_dict() if nd else None})


@bp.route('/<int:asset_id>/network-details', methods=['PUT'])
@admin_or_operator
@require_csrf
@audit_action('UPDATE', 'network_details', resource_id_key='asset_id')
def update_network_details(asset_id):
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    data = request.get_json(silent=True) or {}
    nd = asset.network_detail
    if not nd:
        nd = NetworkDetail(asset_id=asset.id)
        db.session.add(nd)

    nd.ip_address = (data.get('ip_address') or '').strip() or None
    nd.mac_address = (data.get('mac_address') or '').strip() or None
    nd.hostname = (data.get('hostname') or '').strip() or None
    nd.vlan = (data.get('vlan') or '').strip() or None
    nd.notes = (data.get('notes') or '').strip() or None
    db.session.commit()
    return jsonify({'data': nd.to_dict()})


@bp.route('/<int:asset_id>/credential-status', methods=['GET'])
@admin_or_operator
def credential_status(asset_id):
    """Return only whether a credential exists; never plaintext."""
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    has_credential = asset.credential is not None
    if has_credential:
        log_audit('ACCESS', 'asset_credential', resource_id=asset.id, status='success',
                  metadata={'action': 'credential_status_check', 'by_user': g.current_user_id})
    return jsonify({'data': {'has_credential': has_credential}})


@bp.route('/<int:asset_id>/credential', methods=['PUT'])
@admin_or_operator
@require_csrf
@audit_action('UPDATE', 'asset_credential', resource_id_key='asset_id')
def update_credential(asset_id):
    """Store or rotate encrypted credential. Plaintext is never persisted."""
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404
    data = request.get_json(silent=True) or {}
    plaintext = data.get('credential')
    cred = asset.credential
    if plaintext is not None and plaintext.strip():
        enc, nonce = encrypt_secret(plaintext.strip(), current_app.config['AES_KEY'])
        if not cred:
            cred = AssetCredential(asset_id=asset.id)
            db.session.add(cred)
        cred.encrypted_secret = enc
        cred.nonce = nonce
    elif cred and data.get('remove'):
        db.session.delete(cred)
    db.session.commit()
    return jsonify({'data': {'has_credential': asset.credential is not None}})
