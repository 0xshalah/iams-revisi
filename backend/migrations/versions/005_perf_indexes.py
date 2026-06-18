"""add performance indexes for common queries

Revision ID: 005_perf_indexes
Revises: 004_change_requests
Create Date: 2026-06-18 09:30:00
"""
from alembic import op
import sqlalchemy as sa


revision = '005_perf_indexes'
down_revision = '004_change_requests'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_assets_status', 'assets', ['status'])
    op.create_index('ix_assets_location', 'assets', ['location_id'])
    op.create_index('ix_incidents_status', 'incidents', ['status'])
    op.create_index('ix_incidents_severity', 'incidents', ['severity'])
    op.create_index('ix_problems_status', 'problems', ['status'])
    op.create_index('ix_problems_priority', 'problems', ['priority'])
    op.create_index('ix_service_requests_status', 'service_requests', ['status'])
    op.create_index('ix_service_requests_priority', 'service_requests', ['priority'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_status', 'audit_logs', ['status'])
    op.create_index('ix_audit_logs_created', 'audit_logs', ['created_at'])


def downgrade():
    op.drop_index('ix_audit_logs_created', table_name='audit_logs')
    op.drop_index('ix_audit_logs_status', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_service_requests_priority', table_name='service_requests')
    op.drop_index('ix_service_requests_status', table_name='service_requests')
    op.drop_index('ix_problems_priority', table_name='problems')
    op.drop_index('ix_problems_status', table_name='problems')
    op.drop_index('ix_incidents_severity', table_name='incidents')
    op.drop_index('ix_incidents_status', table_name='incidents')
    op.drop_index('ix_assets_location', table_name='assets')
    op.drop_index('ix_assets_status', table_name='assets')
