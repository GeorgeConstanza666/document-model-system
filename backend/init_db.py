"""
Initialize the SQLite database and create all tables.

Run from the backend/ directory with the venv activated:
    python init_db.py
"""
import sys
from pathlib import Path

# Ensure the backend package root is on sys.path when run as a script.
sys.path.insert(0, str(Path(__file__).parent))

import app.models  # noqa: F401 — registers all models with Base.metadata
from app.core.database import engine
from app.models.base import Base


def init_db() -> None:
    """Drop nothing — only create missing tables."""
    Base.metadata.create_all(bind=engine)
    tables = sorted(Base.metadata.tables.keys())
    print(f"Database ready. {len(tables)} tables:")
    for name in tables:
        print(f"  + {name}")


if __name__ == "__main__":
    init_db()
