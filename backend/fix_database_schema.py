"""
fix_database_schema.py

One-time fix for: sqlite3.OperationalError: no such column: chat_messages.sources_json

Root cause: SQLAlchemy's Base.metadata.create_all() only creates NEW tables.
It never ALTERs existing tables to add columns that were added to a model
after the table was first created. So the .db file on disk drifts out of
sync with your models.py over time.

What this script does:
  1. Finds your SQLite .db file automatically (searches the backend folder).
  2. Imports your SQLAlchemy models + Base.
  3. Compares each model's expected columns against what's actually in the
     database.
  4. Runs ALTER TABLE ... ADD COLUMN for anything missing.

Run this ONCE from your backend folder (same folder as venv/, app/, etc.):

    cd C:\\policy_pilot\\PolicyPilot\\backend
    venv\\Scripts\\activate
    python fix_database_schema.py

Safe to re-run any time in the future after adding new columns to a model.
"""

import os
import sqlite3
import glob
import sys

# --- Step 1: locate the sqlite db file -------------------------------------

def find_db_file():
    # 1) Try to read it straight from your app's config/database module
    candidates = []
    for modname in ("app.database", "app.db", "app.core.database", "database"):
        try:
            mod = __import__(modname, fromlist=["*"])
            url = getattr(mod, "SQLALCHEMY_DATABASE_URL", None) or getattr(mod, "DATABASE_URL", None)
            if url and url.startswith("sqlite"):
                path = url.split("///")[-1]
                if os.path.exists(path):
                    return path
        except Exception:
            pass

    # 2) Fallback: scan for .db files in the current directory tree
    for path in glob.glob("**/*.db", recursive=True):
        if "venv" not in path:
            candidates.append(path)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    print("Multiple .db files found:")
    for i, c in enumerate(candidates):
        print(f"  [{i}] {c}")
    idx = int(input("Which one is your app database? Enter number: "))
    return candidates[idx]


db_path = find_db_file()
if not db_path:
    print("Could not auto-locate your SQLite .db file.")
    print("Open your database.py / config and find the DATABASE_URL, e.g.")
    print('  sqlite:///./policypilot.db')
    print("Then re-run this script from the same folder, or edit db_path below manually.")
    sys.exit(1)

print(f"Using database: {db_path}")

# --- Step 2: import your models so we know what columns SHOULD exist -------

sys.path.insert(0, os.getcwd())

try:
    from app.db.database import Base
    import app.db.models  # noqa: F401  (import so model classes register on Base.metadata)
except Exception as e:
    print("Could not import your SQLAlchemy models automatically.")
    print(f"Import error: {e}")
    print("Edit the import line near the top of this script to match your project,")
    print("e.g. 'from app.db.models import Base' or wherever your Base/models are defined.")
    sys.exit(1)

# --- Step 3: diff each model's columns against the live db -----------------

conn = sqlite3.connect(db_path)
cur = conn.cursor()

sqlalchemy_to_sqlite_type = {
    "INTEGER": "INTEGER",
    "VARCHAR": "TEXT",
    "TEXT": "TEXT",
    "BOOLEAN": "BOOLEAN",
    "DATETIME": "DATETIME",
    "FLOAT": "FLOAT",
    "JSON": "TEXT",
}

changes_made = False

for table in Base.metadata.sorted_tables:
    table_name = table.name

    cur.execute(f"PRAGMA table_info({table_name})")
    existing_cols = {row[1] for row in cur.fetchall()}

    if not existing_cols:
        # table doesn't exist at all yet — create_all() will handle that separately
        continue

    for col in table.columns:
        if col.name in existing_cols:
            continue

        sqlite_type = sqlalchemy_to_sqlite_type.get(
            str(col.type).split("(")[0].upper(), "TEXT"
        )
        nullable_sql = "" if col.nullable or col.default is not None else " DEFAULT NULL"

        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col.name} {sqlite_type}{nullable_sql}"
        print(f"Applying: {alter_sql}")
        cur.execute(alter_sql)
        changes_made = True

if changes_made:
    conn.commit()
    print("\nDone. Missing columns have been added.")
else:
    print("\nNo missing columns found — your database schema is already in sync.")

conn.close()