"""Master data blueprint with full CRUD for Administrator."""
from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import Asset, Brand, Category, Department, DeviceModel, Location, User
from app.utils.audit import log_audit
from app.utils.decorators import admin_only, admin_or_operator, require_csrf
from app.utils.pagination import paginate

bp = Blueprint('master', __name__, url_prefix='/api')

# ── read-only (admin & operator) ────────────────────────────────────────────

@bp.route('/departments', methods=['GET'])
@admin_or_operator
def list_departments():
    rows = Department.query.order_by(Department.name)
    return jsonify(paginate(rows))

@bp.route('/departments/<int:dep_id>', methods=['GET'])
@admin_or_operator
def get_department(dep_id):
    d = db.session.get(Department, dep_id)
    if not d:
        return jsonify({'error': 'Department not found'}), 404
    return jsonify({'data': d.to_dict()})

@bp.route('/locations', methods=['GET'])
@admin_or_operator
def list_locations():
    rows = Location.query.order_by(Location.name)
    return jsonify(paginate(rows))

@bp.route('/locations/<int:loc_id>', methods=['GET'])
@admin_or_operator
def get_location(loc_id):
    l = db.session.get(Location, loc_id)
    if not l:
        return jsonify({'error': 'Location not found'}), 404
    return jsonify({'data': l.to_dict()})

@bp.route('/categories', methods=['GET'])
@admin_or_operator
def list_categories():
    rows = Category.query.order_by(Category.name)
    return jsonify(paginate(rows))

@bp.route('/categories/<int:cat_id>', methods=['GET'])
@admin_or_operator
def get_category(cat_id):
    c = db.session.get(Category, cat_id)
    if not c:
        return jsonify({'error': 'Category not found'}), 404
    return jsonify({'data': c.to_dict()})

@bp.route('/brands', methods=['GET'])
@admin_or_operator
def list_brands():
    rows = Brand.query.order_by(Brand.name)
    return jsonify(paginate(rows))

@bp.route('/brands/<int:br_id>', methods=['GET'])
@admin_or_operator
def get_brand(br_id):
    b = db.session.get(Brand, br_id)
    if not b:
        return jsonify({'error': 'Brand not found'}), 404
    return jsonify({'data': b.to_dict()})

@bp.route('/models', methods=['GET'])
@admin_or_operator
def list_models():
    rows = DeviceModel.query.order_by(DeviceModel.name)
    return jsonify(paginate(rows))

@bp.route('/models/<int:md_id>', methods=['GET'])
@admin_or_operator
def get_model(md_id):
    m = db.session.get(DeviceModel, md_id)
    if not m:
        return jsonify({'error': 'Model not found'}), 404
    return jsonify({'data': m.to_dict()})

# ── Departments CRUD (admin only) ───────────────────────────────────────────

@bp.route('/departments', methods=['POST'])
@admin_only
@require_csrf
def create_department():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    if Department.query.filter_by(name=name).first():
        return jsonify({'error': 'Department already exists'}), 409
    dep = Department(name=name, description=(data.get('description') or '').strip() or None)
    db.session.add(dep)
    db.session.commit()
    log_audit('CREATE_DEPARTMENT', 'department', resource_id=dep.id, status='success')
    return jsonify({'data': dep.to_dict()}), 201

@bp.route('/departments/<int:dep_id>', methods=['PUT'])
@admin_only
@require_csrf
def update_department(dep_id):
    dep = db.session.get(Department, dep_id)
    if not dep:
        return jsonify({'error': 'Department not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        existing = Department.query.filter_by(name=name).first()
        if existing and existing.id != dep_id:
            return jsonify({'error': 'Department already exists'}), 409
        dep.name = name
    if 'description' in data:
        dep.description = (data['description'] or '').strip() or None
    db.session.commit()
    log_audit('UPDATE_DEPARTMENT', 'department', resource_id=dep.id, status='success')
    return jsonify({'data': dep.to_dict()})

@bp.route('/departments/<int:dep_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_department(dep_id):
    dep = db.session.get(Department, dep_id)
    if not dep:
        return jsonify({'error': 'Department not found'}), 404
    if User.query.filter_by(department_id=dep_id).first():
        return jsonify({'error': 'Cannot delete resource because it is still in use.'}), 409
    db.session.delete(dep)
    db.session.commit()
    log_audit('DELETE_DEPARTMENT', 'department', resource_id=dep_id, status='success')
    return jsonify({'message': 'Department deleted'})

# ── Locations CRUD (admin only) ─────────────────────────────────────────────

@bp.route('/locations', methods=['POST'])
@admin_only
@require_csrf
def create_location():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    loc = Location(name=name, description=(data.get('description') or '').strip() or None)
    db.session.add(loc)
    db.session.commit()
    log_audit('CREATE_LOCATION', 'location', resource_id=loc.id, status='success')
    return jsonify({'data': loc.to_dict()}), 201

@bp.route('/locations/<int:loc_id>', methods=['PUT'])
@admin_only
@require_csrf
def update_location(loc_id):
    loc = db.session.get(Location, loc_id)
    if not loc:
        return jsonify({'error': 'Location not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        loc.name = name
    if 'description' in data:
        loc.description = (data['description'] or '').strip() or None
    db.session.commit()
    log_audit('UPDATE_LOCATION', 'location', resource_id=loc.id, status='success')
    return jsonify({'data': loc.to_dict()})

@bp.route('/locations/<int:loc_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_location(loc_id):
    loc = db.session.get(Location, loc_id)
    if not loc:
        return jsonify({'error': 'Location not found'}), 404
    if Asset.query.filter_by(location_id=loc_id).first():
        return jsonify({'error': 'Cannot delete resource because it is still in use.'}), 409
    db.session.delete(loc)
    db.session.commit()
    log_audit('DELETE_LOCATION', 'location', resource_id=loc_id, status='success')
    return jsonify({'message': 'Location deleted'})

# ── Categories CRUD (admin only) ────────────────────────────────────────────

@bp.route('/categories', methods=['POST'])
@admin_only
@require_csrf
def create_category():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    if Category.query.filter_by(name=name).first():
        return jsonify({'error': 'Category already exists'}), 409
    cat = Category(name=name, description=(data.get('description') or '').strip() or None)
    db.session.add(cat)
    db.session.commit()
    log_audit('CREATE_CATEGORY', 'category', resource_id=cat.id, status='success')
    return jsonify({'data': cat.to_dict()}), 201

@bp.route('/categories/<int:cat_id>', methods=['PUT'])
@admin_only
@require_csrf
def update_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({'error': 'Category not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != cat_id:
            return jsonify({'error': 'Category already exists'}), 409
        cat.name = name
    if 'description' in data:
        cat.description = (data['description'] or '').strip() or None
    db.session.commit()
    log_audit('UPDATE_CATEGORY', 'category', resource_id=cat.id, status='success')
    return jsonify({'data': cat.to_dict()})

@bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({'error': 'Category not found'}), 404
    if DeviceModel.query.filter_by(category_id=cat_id).first():
        return jsonify({'error': 'Cannot delete resource because it is still in use.'}), 409
    db.session.delete(cat)
    db.session.commit()
    log_audit('DELETE_CATEGORY', 'category', resource_id=cat_id, status='success')
    return jsonify({'message': 'Category deleted'})

# ── Brands CRUD (admin only) ────────────────────────────────────────────────

@bp.route('/brands', methods=['POST'])
@admin_only
@require_csrf
def create_brand():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    if Brand.query.filter_by(name=name).first():
        return jsonify({'error': 'Brand already exists'}), 409
    brand = Brand(name=name, description=(data.get('description') or '').strip() or None)
    db.session.add(brand)
    db.session.commit()
    log_audit('CREATE_BRAND', 'brand', resource_id=brand.id, status='success')
    return jsonify({'data': brand.to_dict()}), 201

@bp.route('/brands/<int:br_id>', methods=['PUT'])
@admin_only
@require_csrf
def update_brand(br_id):
    brand = db.session.get(Brand, br_id)
    if not brand:
        return jsonify({'error': 'Brand not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        existing = Brand.query.filter_by(name=name).first()
        if existing and existing.id != br_id:
            return jsonify({'error': 'Brand already exists'}), 409
        brand.name = name
    if 'description' in data:
        brand.description = (data['description'] or '').strip() or None
    db.session.commit()
    log_audit('UPDATE_BRAND', 'brand', resource_id=brand.id, status='success')
    return jsonify({'data': brand.to_dict()})

@bp.route('/brands/<int:br_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_brand(br_id):
    brand = db.session.get(Brand, br_id)
    if not brand:
        return jsonify({'error': 'Brand not found'}), 404
    if DeviceModel.query.filter_by(brand_id=br_id).first():
        return jsonify({'error': 'Cannot delete resource because it is still in use.'}), 409
    db.session.delete(brand)
    db.session.commit()
    log_audit('DELETE_BRAND', 'brand', resource_id=br_id, status='success')
    return jsonify({'message': 'Brand deleted'})

# ── Models CRUD (admin only) ────────────────────────────────────────────────

@bp.route('/models', methods=['POST'])
@admin_only
@require_csrf
def create_model():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    brand_id = data.get('brand_id')
    category_id = data.get('category_id')
    if brand_id and not Brand.query.get(int(brand_id)):
        return jsonify({'error': 'Invalid brand_id'}), 400
    if category_id and not Category.query.get(int(category_id)):
        return jsonify({'error': 'Invalid category_id'}), 400
    mdl = DeviceModel(
        name=name,
        brand_id=int(brand_id) if brand_id else None,
        category_id=int(category_id) if category_id else None,
        specifications=(data.get('specifications') or '').strip() or None,
    )
    db.session.add(mdl)
    db.session.commit()
    log_audit('CREATE_MODEL', 'model', resource_id=mdl.id, status='success')
    return jsonify({'data': mdl.to_dict()}), 201

@bp.route('/models/<int:md_id>', methods=['PUT'])
@admin_only
@require_csrf
def update_model(md_id):
    mdl = db.session.get(DeviceModel, md_id)
    if not mdl:
        return jsonify({'error': 'Model not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        mdl.name = name
    if 'brand_id' in data:
        bid = data['brand_id']
        if bid and not Brand.query.get(int(bid)):
            return jsonify({'error': 'Invalid brand_id'}), 400
        mdl.brand_id = int(bid) if bid else None
    if 'category_id' in data:
        cid = data['category_id']
        if cid and not Category.query.get(int(cid)):
            return jsonify({'error': 'Invalid category_id'}), 400
        mdl.category_id = int(cid) if cid else None
    if 'specifications' in data:
        mdl.specifications = (data['specifications'] or '').strip() or None
    db.session.commit()
    log_audit('UPDATE_MODEL', 'model', resource_id=mdl.id, status='success')
    return jsonify({'data': mdl.to_dict()})

@bp.route('/models/<int:md_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_model(md_id):
    mdl = db.session.get(DeviceModel, md_id)
    if not mdl:
        return jsonify({'error': 'Model not found'}), 404
    if Asset.query.filter_by(model_id=md_id).first():
        return jsonify({'error': 'Cannot delete resource because it is still in use.'}), 409
    db.session.delete(mdl)
    db.session.commit()
    log_audit('DELETE_MODEL', 'model', resource_id=md_id, status='success')
    return jsonify({'message': 'Model deleted'})
