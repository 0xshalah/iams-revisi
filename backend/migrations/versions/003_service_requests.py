"""add service_requests table for Request Management module

Revision ID: 003_service_requests
Revises: 002_strict_alignment
Create Date: 2026-06-18 04:30:00
"""
from alembic import op
import sqlalchemy as sa


revision = '003_service_requests'
down_revision = '002_strict_alignment'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'service_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('request_type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Open'),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('asset_id', sa.Integer(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id']),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id']),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_number')
    )


def downgrade():
    op.drop_table('service_requests')
