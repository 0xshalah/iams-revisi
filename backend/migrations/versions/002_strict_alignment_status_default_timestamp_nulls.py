"""strict alignment: status DEFAULT Available, created_at TIMESTAMP, models FKs nullable

Revision ID: 002_strict_alignment
Revises: 001_mysql_extensions
Create Date: 2026-06-18 03:34:00
"""
from alembic import op
import sqlalchemy as sa


revision = '002_strict_alignment'
down_revision = '001_mysql_extensions'
branch_labels = None
depends_on = None


def upgrade():
    # 1. assets.status: add server-side DEFAULT 'Available' (database.sql)
    # Must use raw SQL because Alembic alter_column does not reliably change
    # ENUM defaults in MySQL/MariaDB.
    op.execute("""
        ALTER TABLE assets
        MODIFY COLUMN status
        ENUM('Active','Available','Repair','Disposed')
        NOT NULL DEFAULT 'Available'
    """)

    # 2. assets.created_at: from datetime to TIMESTAMP (database.sql)
    # MariaDB session timezone is UTC; existing datetime values are UTC,
    # so no value shift occurs.
    op.execute("""
        ALTER TABLE assets
        MODIFY COLUMN created_at
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    """)

    # 3. models.brand_id: NOT NULL -> nullable (database.sql has INT nullable)
    op.alter_column('models', 'brand_id',
                    existing_type=sa.Integer(),
                    nullable=True)

    # 4. models.category_id: NOT NULL -> nullable (database.sql has INT nullable)
    op.alter_column('models', 'category_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade():
    op.alter_column('models', 'category_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('models', 'brand_id',
                    existing_type=sa.Integer(),
                    nullable=False)

    op.execute("""
        ALTER TABLE assets
        MODIFY COLUMN created_at
        DATETIME NOT NULL
    """)

    op.execute("""
        ALTER TABLE assets
        MODIFY COLUMN status
        ENUM('Active','Available','Repair','Disposed')
        NOT NULL
    """)
