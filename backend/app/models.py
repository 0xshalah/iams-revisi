"""SQLAlchemy models aligned with the supervisor SQL schema."""
import datetime as _dt

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def _utcnow():
    return _dt.datetime.now(_dt.timezone.utc)


class TimestampMixin:
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class Role(db.Model, TimestampMixin):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list['User']] = relationship('User', back_populates='role')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'is_active': self.is_active}


class Department(db.Model, TimestampMixin):
    __tablename__ = 'departments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    users: Mapped[list['User']] = relationship('User', back_populates='department')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


class Location(db.Model, TimestampMixin):
    __tablename__ = 'locations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    assets: Mapped[list['Asset']] = relationship('Asset', back_populates='location')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


class Category(db.Model, TimestampMixin):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    models: Mapped[list['DeviceModel']] = relationship('DeviceModel', back_populates='category')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


class Brand(db.Model, TimestampMixin):
    __tablename__ = 'brands'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    models: Mapped[list['DeviceModel']] = relationship('DeviceModel', back_populates='brand')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


class DeviceModel(db.Model, TimestampMixin):
    __tablename__ = 'models'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey('brands.id'), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    specifications: Mapped[str | None] = mapped_column(Text, nullable=True)

    brand: Mapped['Brand'] = relationship('Brand', back_populates='models')
    category: Mapped['Category'] = relationship('Category', back_populates='models')
    assets: Mapped[list['Asset']] = relationship('Asset', back_populates='model')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand_id': self.brand_id,
            'category_id': self.category_id,
            'brand_name': self.brand.name if self.brand else None,
            'category_name': self.category.name if self.category else None,
            'specifications': self.specifications,
        }


class User(db.Model, TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey('departments.id'), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped['Role'] = relationship('Role', back_populates='users')
    department: Mapped['Department | None'] = relationship('Department', back_populates='users')
    assets: Mapped[list['Asset']] = relationship('Asset', back_populates='user')

    def to_dict(self, include_sensitive: bool = False):
        avatar = ''.join(part[0].upper() for part in (self.name or '').split()[:2])
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role_id': self.role_id,
            'role': self.role.name if self.role else None,
            'role_name': self.role.name if self.role else None,
            'department_id': self.department_id,
            'department': self.department.name if self.department else None,
            'department_name': self.department.name if self.department else None,
            'is_active': self.is_active,
            'status': 'active' if self.is_active else 'inactive',
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'avatar': avatar,
        }
        if include_sensitive:
            data['password_hash'] = '<redacted>'
        return data


class ChangeRequest(db.Model, TimestampMixin):
    """IT change management (table: change_requests)."""
    __tablename__ = 'change_requests'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    change_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, default='Low')
    impact: Mapped[str] = mapped_column(String(50), nullable=False, default='Low')
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='Draft')
    requester_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    approver_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey('assets.id'), nullable=True)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey('incidents.id'), nullable=True)
    problem_id: Mapped[int | None] = mapped_column(ForeignKey('problems.id'), nullable=True)
    request_id: Mapped[int | None] = mapped_column(ForeignKey('service_requests.id'), nullable=True)
    planned_start: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)
    implementation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rollback_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)

    requester: Mapped['User'] = relationship('User', foreign_keys=[requester_id])
    assignee: Mapped['User | None'] = relationship('User', foreign_keys=[assignee_id])
    approver: Mapped['User | None'] = relationship('User', foreign_keys=[approver_id])
    asset: Mapped['Asset | None'] = relationship('Asset')
    incident: Mapped['Incident | None'] = relationship('Incident')
    problem: Mapped['Problem | None'] = relationship('Problem')
    related_request: Mapped['ServiceRequest | None'] = relationship('ServiceRequest')

    def to_dict(self):
        return {
            'id': self.id,
            'change_number': self.change_number,
            'title': self.title,
            'description': self.description,
            'change_type': self.change_type,
            'risk_level': self.risk_level,
            'impact': self.impact,
            'status': self.status,
            'requester_id': self.requester_id,
            'requester_name': self.requester.name if self.requester else None,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.name if self.assignee else None,
            'approver_id': self.approver_id,
            'approver_name': self.approver.name if self.approver else None,
            'asset_id': self.asset_id,
            'asset_tag': self.asset.asset_tag if self.asset else None,
            'incident_id': self.incident_id,
            'incident_code': self.incident.code if self.incident else None,
            'problem_id': self.problem_id,
            'problem_code': self.problem.code if self.problem else None,
            'request_id': self.request_id,
            'request_number': self.related_request.request_number if self.related_request else None,
            'planned_start': self.planned_start.isoformat() if self.planned_start else None,
            'planned_end': self.planned_end.isoformat() if self.planned_end else None,
            'implementation_notes': self.implementation_notes,
            'rollback_plan': self.rollback_plan,
            'approval_notes': self.approval_notes,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        if include_sensitive:
            data['password_hash'] = '<redacted>'
        return data


class Asset(db.Model, TimestampMixin):
    __tablename__ = 'assets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    po_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_id: Mapped[int] = mapped_column(ForeignKey('models.id'), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey('locations.id'), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    status: Mapped[str] = mapped_column(Enum('Active', 'Available', 'Repair', 'Disposed', name='asset_status'), default='Available', nullable=False)
    purchase_date: Mapped[_dt.date | None] = mapped_column(Date, nullable=True)
    warranty_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    os_license: Mapped[str | None] = mapped_column(String(100), nullable=True)

    model: Mapped['DeviceModel'] = relationship('DeviceModel', back_populates='assets')
    location: Mapped['Location'] = relationship('Location', back_populates='assets')
    user: Mapped['User | None'] = relationship('User', back_populates='assets')
    network_detail: Mapped['NetworkDetail | None'] = relationship(
        'NetworkDetail', back_populates='asset', uselist=False, cascade='all, delete-orphan'
    )
    credentials: Mapped[list['AssetCredential']] = relationship(
        'AssetCredential', back_populates='asset', cascade='all, delete-orphan'
    )

    def to_dict(self):
        m = self.model
        brand_name = m.brand.name if m and m.brand else None
        category_name = m.category.name if m and m.category else None
        return {
            'id': self.id,
            'asset_tag': self.asset_tag,
            'serial_number': self.serial_number,
            'po_number': self.po_number,
            'model_id': self.model_id,
            'model_name': m.name if m else None,
            'brand_name': brand_name,
            'category_name': category_name,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else None,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'IT Inventory / Server',
            'department_name': self.user.department.name if self.user and self.user.department else 'Infrastructure',
            'status': self.status,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'warranty_months': self.warranty_months,
            'os_license': self.os_license,
            'ip_address': self.network_detail.ip_address if self.network_detail else None,
            'mac_address': self.network_detail.mac_address if self.network_detail else None,
            'hostname': self.network_detail.hostname if self.network_detail else None,
            'vlan': self.network_detail.vlan if self.network_detail else None,
            'has_credential': len(self.credentials) > 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class NetworkDetail(db.Model):
    __tablename__ = 'network_details'

    asset_id: Mapped[int] = mapped_column(ForeignKey('assets.id', ondelete='CASCADE'), primary_key=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(17), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vlan: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    asset: Mapped['Asset'] = relationship('Asset', back_populates='network_detail')

    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'vlan': self.vlan,
            'notes': self.notes,
        }


class AssetCredential(db.Model, TimestampMixin):
    __tablename__ = 'asset_credentials'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey('assets.id'), nullable=False)
    credential_type: Mapped[str] = mapped_column(String(50), nullable=False, default='SSH')
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encrypted_secret: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    asset: Mapped['Asset'] = relationship('Asset', back_populates='credentials')


class Incident(db.Model, TimestampMixin):
    __tablename__ = 'incidents'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey('assets.id'), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='Open', nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)

    asset: Mapped['Asset | None'] = relationship('Asset')
    assignee: Mapped['User | None'] = relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'asset_id': self.asset_id,
            'related_asset_id': self.asset_id,
            'severity': self.severity,
            'status': self.status,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.name if self.assignee else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Problem(db.Model, TimestampMixin):
    __tablename__ = 'problems'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    root_cause_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='Open', nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)

    owner: Mapped['User | None'] = relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'root_cause': self.root_cause_summary,
            'root_cause_summary': self.root_cause_summary,
            'priority': self.priority,
            'status': self.status,
            'owner_id': self.owner_id,
            'owner_name': self.owner.name if self.owner else None,
            'related_incident_ids': [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class AuditLog(db.Model, TimestampMixin):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_redacted: Mapped[str | None] = mapped_column(Text, nullable=True)

    actor: Mapped['User | None'] = relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'actor': self.actor.email if self.actor else 'system',
            'actor_user_id': self.actor_user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'status': self.status,
            'timestamp': self.created_at.isoformat(),
            'detail': self.metadata_redacted,
            'ip_address': self.ip_address,
        }


class ServiceRequest(db.Model, TimestampMixin):
    """IT operational request (named service_requests table to avoid reserved word)."""
    __tablename__ = 'service_requests'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default='Medium')
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='Open')
    requester_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey('assets.id'), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey('departments.id'), nullable=True)
    due_date: Mapped[_dt.date | None] = mapped_column(Date, nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)

    requester: Mapped['User'] = relationship('User', foreign_keys=[requester_id])
    assigned_to: Mapped['User | None'] = relationship('User', foreign_keys=[assigned_to_id])
    asset: Mapped['Asset | None'] = relationship('Asset')
    department: Mapped['Department | None'] = relationship('Department')

    def to_dict(self):
        return {
            'id': self.id,
            'request_number': self.request_number,
            'title': self.title,
            'description': self.description,
            'request_type': self.request_type,
            'priority': self.priority,
            'status': self.status,
            'requester_id': self.requester_id,
            'requester_name': self.requester.name if self.requester else None,
            'assigned_to_id': self.assigned_to_id,
            'assigned_to_name': self.assigned_to.name if self.assigned_to else None,
            'asset_id': self.asset_id,
            'asset_tag': self.asset.asset_tag if self.asset else None,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'resolution_notes': self.resolution_notes,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
