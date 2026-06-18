"""add change_requests table for Change Management module

Revision ID: 004_change_requests
Revises: 003_service_requests
Create Date: 2026-06-18 04:30:00
"""
from alembic import op
import sqlalchemy as sa


revision = '004_change_requests'
down_revision = '003_service_requests'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'change_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('change_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='Low'),
        sa.Column('impact', sa.String(length=50), nullable=False, server_default='Low'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Draft'),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.Column('asset_id', sa.Integer(), nullable=True),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('problem_id', sa.Integer(), nullable=True),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('planned_start', sa.DateTime(), nullable=True),
        sa.Column('planned_end', sa.DateTime(), nullable=True),
        sa.Column('implementation_notes', sa.Text(), nullable=True),
        sa.Column('rollback_plan', sa.Text(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id']),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id']),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id']),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id']),
        sa.ForeignKeyConstraint(['request_id'], ['service_requests.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('change_number')
    )


def downgrade():
    op.drop_table('change_requests')
