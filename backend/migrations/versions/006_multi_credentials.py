"""upgrade asset_credentials: 1:1 → 1:N, add credential_type/username/notes

Revision ID: 006_multi_credentials
Revises: 005_perf_indexes
Create Date: 2026-06-19 00:30:00
"""
from alembic import op
import sqlalchemy as sa


revision = '006_multi_credentials'
down_revision = '005_perf_indexes'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('asset_credentials', sa.Column('credential_type', sa.String(length=50), nullable=False, server_default='SSH'))
    op.add_column('asset_credentials', sa.Column('username', sa.String(length=255), nullable=True))
    op.add_column('asset_credentials', sa.Column('notes', sa.Text(), nullable=True))
    # Drop unique constraint on asset_id (auto-named by MariaDB)
    with op.batch_alter_table('asset_credentials') as batch_op:
        batch_op.drop_index('asset_id')
        batch_op.create_index('ix_asset_credentials_asset', ['asset_id'])


def downgrade():
    with op.batch_alter_table('asset_credentials') as batch_op:
        batch_op.drop_index('ix_asset_credentials_asset')
        batch_op.create_unique_constraint('uq_asset_credentials_asset', ['asset_id'])
    op.drop_column('asset_credentials', 'notes')
    op.drop_column('asset_credentials', 'username')
    op.drop_column('asset_credentials', 'credential_type')
