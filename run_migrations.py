"""
Run all SQL migrations in order.
Execute once after pulling new code that contains database changes.

Usage:
    python run_migrations.py
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_NAME = os.getenv("DATABASE_NAME", "laundry_aui_app")
DB_USER = os.getenv("DATABASE_USER", "llassri")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DB_PORT = os.getenv("DATABASE_PORT", "5432")


def run_migrations():
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")

    if not os.path.isdir(migrations_dir):
        print(f"[ERROR] migrations/ directory not found at {migrations_dir}")
        return False

    sql_files = sorted(f for f in os.listdir(migrations_dir) if f.endswith(".sql"))
    if not sql_files:
        print("[ERROR] No .sql files found in migrations/")
        return False

    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER,
            password=DB_PASSWORD, port=DB_PORT
        )
        conn.autocommit = False
        print(f"Connected to {DB_NAME}@{DB_HOST}")
    except Exception as e:
        print(f"[ERROR] Cannot connect to database: {e}")
        return False

    all_ok = True
    for filename in sql_files:
        path = os.path.join(migrations_dir, filename)
        print(f"\nRunning {filename} ...")
        try:
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            print(f"  OK: {filename}")
        except Exception as e:
            conn.rollback()
            print(f"  [ERROR] {filename} failed: {e}")
            all_ok = False
            break

    conn.close()

    if all_ok:
        print("\nAll migrations completed successfully.")
    else:
        print("\nMigration run stopped due to error.")
    return all_ok


if __name__ == "__main__":
    sys.exit(0 if run_migrations() else 1)
