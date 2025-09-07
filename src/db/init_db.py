# src/db/init_db.py
from pathlib import Path
import sys
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
# ensure .env is loaded
load_dotenv(ROOT / ".env")

# make src/ importable when running this file directly
sys.path.insert(0, str(ROOT / "src"))

from db.models import Base, get_engine

def main():
    engine = get_engine()
    engine_url = str(getattr(engine, "url", "unknown"))
    print(f"Creating tables (using DATABASE_URL={engine_url})...")
    Base.metadata.create_all(engine)
    print("Done — tables created (or already existed).")
    # print tables so user can confirm quickly
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables now:", tables)

if __name__ == "__main__":
    main()