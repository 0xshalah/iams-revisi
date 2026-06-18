#!/bin/sh
set -e

echo "Waiting for MariaDB/MySQL..."
while ! python -c "import socket; s=socket.socket(); s.connect(('mysql', 3306)); s.close()" 2>/dev/null; do
  sleep 1
done
echo "MariaDB/MySQL is ready."

# The baseline schema (docs/database.mysql.compat.sql) is mounted into
# /docker-entrypoint-initdb.d/ and executed automatically by the MariaDB
# container on first initialization. Wait until the core assets table exists
# before applying IAMS extension migrations.
echo "Waiting for baseline schema (assets table)..."
while ! python -c "
import sqlalchemy as sa
engine = sa.create_engine('${DATABASE_URL}')
with engine.connect() as conn:
    conn.execute(sa.text('SELECT 1 FROM assets'))
" 2>/dev/null; do
  sleep 1
done
echo "Baseline schema is ready."

echo "Running IAMS extension migrations..."
flask db upgrade

echo "Seeding default data..."
flask seed

echo "Starting Gunicorn..."
exec gunicorn -c /app/gunicorn.conf.py run:app
