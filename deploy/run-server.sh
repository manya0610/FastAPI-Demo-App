#!/bin/bash
set -e
# python3 create_db.py
# alembic upgrade head
# python3 seed_db.py
uvicorn src.app:app --host 0.0.0.0 --port 8000