#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python << 'EOF'
import os
import time

from sqlalchemy import create_engine, text

database_url = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/directory_db",
)
engine = create_engine(database_url)

for i in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("PostgreSQL is ready!")
        break
    except Exception:
        print(f"Waiting... ({i + 1}/30)")
        time.sleep(2)
else:
    print("ERROR: Could not connect to PostgreSQL")
    exit(1)
EOF

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python seed.py

echo "Starting application..."
exec "$@"
