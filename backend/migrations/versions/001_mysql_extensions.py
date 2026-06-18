"""MySQL/MariaDB extension schema for IAMS.

This migration assumes the supervisor's baseline schema
(docs/database.mysql.compat.sql) has already been executed.
It adds the IAMS-specific extension tables and columns required for
authentication, RBAC, credential encryption, incident/problem management,
and audit logging.

Revision ID: 001_mysql_extensions
Revises:
Create Date: 2026-06-17 21:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '001_mysql_extensions'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # -------------------------------------------------------------------------
    # 1. roles (extension)
    # -------------------------------------------------------------------------
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # -------------------------------------------------------------------------
    # 2. users extension columns
    # -------------------------------------------------------------------------
    op.add_column('users', sa.Column('password_hash', sa.Text(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

    # -------------------------------------------------------------------------
    # 3. master table extensions (description + timestamps)
    # -------------------------------------------------------------------------
    op.add_column('departments', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('departments', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('departments', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))
    op.create_unique_constraint('uq_departments_name', 'departments', ['name'])

    op.add_column('categories', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('categories', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('categories', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))
    op.create_unique_constraint('uq_categories_name', 'categories', ['name'])

    op.add_column('brands', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('brands', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('brands', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))
    op.create_unique_constraint('uq_brands_name', 'brands', ['name'])

    op.add_column('locations', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('locations', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))

    op.add_column('models', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('models', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))

    # -------------------------------------------------------------------------
    # 4. assets extension column
    # -------------------------------------------------------------------------
    op.add_column('assets', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))

    # -------------------------------------------------------------------------
    # 5. network_details extension columns
    # -------------------------------------------------------------------------
    op.add_column('network_details', sa.Column('hostname', sa.String(length=100), nullable=True))
    op.add_column('network_details', sa.Column('vlan', sa.String(length=50), nullable=True))
    op.add_column('network_details', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('network_details', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('network_details', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))

    # -------------------------------------------------------------------------
    # 6. asset_credentials (extension)
    # -------------------------------------------------------------------------
    op.create_table(
        'asset_credentials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('encrypted_secret', sa.Text(), nullable=False),
        sa.Column('nonce', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id')
    )

    # -------------------------------------------------------------------------
    # 7. incidents (extension)
    # -------------------------------------------------------------------------
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_id', sa.Integer(), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Open'),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # -------------------------------------------------------------------------
    # 8. problems (extension)
    # -------------------------------------------------------------------------
    op.create_table(
        'problems',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('root_cause_summary', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Open'),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # -------------------------------------------------------------------------
    # 9. audit_logs (extension)
    # -------------------------------------------------------------------------
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('metadata_redacted', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('problems')
    op.drop_table('incidents')
    op.drop_table('asset_credentials')

    op.drop_column('network_details', 'updated_at')
    op.drop_column('network_details', 'created_at')
    op.drop_column('network_details', 'notes')
    op.drop_column('network_details', 'vlan')
    op.drop_column('network_details', 'hostname')

    op.drop_column('assets', 'updated_at')

    op.drop_column('models', 'updated_at')
    op.drop_column('models', 'created_at')
    op.drop_column('locations', 'updated_at')
    op.drop_column('locations', 'created_at')

    op.drop_constraint('uq_brands_name', 'brands', type_='unique')
    op.drop_column('brands', 'updated_at')
    op.drop_column('brands', 'created_at')
    op.drop_column('brands', 'description')

    op.drop_constraint('uq_categories_name', 'categories', type_='unique')
    op.drop_column('categories', 'updated_at')
    op.drop_column('categories', 'created_at')
    op.drop_column('categories', 'description')

    op.drop_constraint('uq_departments_name', 'departments', type_='unique')
    op.drop_column('departments', 'updated_at')
    op.drop_column('departments', 'created_at')
    op.drop_column('departments', 'description')

    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role_id')
    op.drop_column('users', 'password_hash')

    op.drop_table('roles')
