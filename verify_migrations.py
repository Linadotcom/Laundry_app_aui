"""
Verify that migrations have been applied to the database.

Usage:
    python verify_migrations.py
"""

import os
import sys
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_NAME = os.getenv("DATABASE_NAME", "laundry_aui_app")
DB_USER = os.getenv("DATABASE_USER", "llassri")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DB_PORT = os.getenv("DATABASE_PORT", "5432")

REQUIRED_TRIGGERS = {"trg_sync_machine_busy", "trg_sync_machine_available"}
REQUIRED_FUNCTIONS = {"sync_machine_busy", "sync_machine_available"}


def verify():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER,
            password=DB_PASSWORD, port=DB_PORT
        )
    except Exception as e:
        print(f"[ERROR] Cannot connect: {e}")
        return False

    ok = True
    with conn.cursor(cursor_factory=DictCursor) as cur:

        # ── Triggers ─────────────────────────────────────────
        cur.execute("""
            SELECT trigger_name, event_manipulation
            FROM information_schema.triggers
            WHERE event_object_table = 'laundry_order'
            ORDER BY trigger_name
        """)
        found_triggers = {row["trigger_name"] for row in cur.fetchall()}

        print("Triggers on Laundry_Order:")
        for name in sorted(found_triggers):
            print(f"  [OK] {name}")
        for name in sorted(REQUIRED_TRIGGERS - found_triggers):
            print(f"  [MISSING] {name}")
            ok = False

        # ── Functions ─────────────────────────────────────────
        cur.execute("""
            SELECT proname FROM pg_proc
            WHERE proname = ANY(%s)
            ORDER BY proname
        """, (list(REQUIRED_FUNCTIONS),))
        found_functions = {row["proname"] for row in cur.fetchall()}

        print("\nFunctions:")
        for name in sorted(found_functions):
            print(f"  [OK] {name}()")
        for name in sorted(REQUIRED_FUNCTIONS - found_functions):
            print(f"  [MISSING] {name}()")
            ok = False

        # ── Partial unique index ──────────────────────────────
        cur.execute("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'laundry_order'
              AND indexname = 'one_active_order_per_machine'
        """)
        if cur.fetchone():
            print("\nUnique index:")
            print("  [OK] one_active_order_per_machine")
        else:
            print("\nUnique index:")
            print("  [MISSING] one_active_order_per_machine")
            ok = False

        # ── Integrity check: stored status vs actual orders ───
        cur.execute("""
            SELECT m.machine_id, m.current_status,
                   COUNT(o.order_id) AS active_orders
            FROM Laundry_Machine m
            LEFT JOIN Laundry_Order o
                   ON o.machine_id = m.machine_id
                  AND o.order_status IN ('Pending', 'In Progress')
            GROUP BY m.machine_id, m.current_status
            HAVING (m.current_status = 'Busy'  AND COUNT(o.order_id) = 0)
                OR (m.current_status = 'Available' AND COUNT(o.order_id) > 0)
        """)
        mismatches = cur.fetchall()
        print("\nStatus integrity:")
        if mismatches:
            for row in mismatches:
                print(f"  [MISMATCH] Machine #{row['machine_id']}: "
                      f"stored={row['current_status']}, "
                      f"active_orders={row['active_orders']}")
            ok = False
        else:
            print("  [OK] All machine statuses match their active orders")

    conn.close()
    print()
    if ok:
        print("All checks passed.")
    else:
        print("Some checks failed — run: python run_migrations.py")
    return ok


if __name__ == "__main__":
    sys.exit(0 if verify() else 1)
