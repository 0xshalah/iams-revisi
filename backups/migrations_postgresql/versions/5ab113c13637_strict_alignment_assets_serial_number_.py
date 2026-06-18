"""strict alignment: assets serial_number not null unique, status default Available

Revision ID: 5ab113c13637
Revises: 8204aec45f61
Create Date: 2026-06-17 13:06:58.984671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ab113c13637'
down_revision = '8204aec45f61'
branch_labels = None
depends_on = None


def upgrade():
    # Backfill existing rows with placeholder serial numbers so the NOT NULL
    # and UNIQUE constraints can be applied safely. Placeholders use the
    # agreed format DEMO-SN-<asset_tag>.
    op.execute("""
        UPDATE assets
        SET serial_number = 'DEMO-SN-' || asset_tag
        WHERE serial_number IS NULL OR serial_number = ''
    """)

    # Apply schema strict alignment:
    # - serial_number becomes NOT NULL + UNIQUE (matches database.sql)
    # - status server default becomes 'Available' (matches database.sql)
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.alter_column('serial_number',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.create_unique_constraint('uq_assets_serial_number', ['serial_number'])
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=50),
               server_default=sa.text("'Available'"),
               existing_nullable=False)


def downgrade():
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=50),
               server_default=sa.text("'Active'"),
               existing_nullable=False)
        batch_op.drop_constraint('uq_assets_serial_number', type_='unique')
        batch_op.alter_column('serial_number',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
