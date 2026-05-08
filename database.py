import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_NAME = os.getenv("DATABASE_NAME", "laundry_aui_app")
DB_USER = os.getenv("DATABASE_USER", "llassri")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")

def get_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            port=DB_PORT,
            password=DB_PASSWORD if DB_PASSWORD else None
        )
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        raise

def fetch_all(query, params=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

def execute_update(query, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()

# ── STUDENT SIGNUP HELPERS ──────────────────────────────

def get_student_by_email(email):
    query = "SELECT * FROM Student WHERE email = %s"
    result = fetch_all(query, (email,))
    return result[0] if result else None

def create_student_with_id(student_id, first_name, last_name, email, phone_number, residence, room, password):
    query = """
        INSERT INTO Student (student_id, first_name, last_name, email, phone_number, residence, room, password, registered_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    """
    execute_update(query, (student_id, first_name, last_name, email, phone_number, residence, room, password))
    return student_id

def create_student_wallet_by_id(student_id):
    execute_update(
        "INSERT INTO Cash_Wallet (student_id, balance, last_updated) VALUES (%s, 0, CURRENT_TIMESTAMP)",
        (student_id,)
    )


# ── STAFF SIGNUP HELPERS ────────────────────────────────

def get_staff_by_email(email):
    query = "SELECT * FROM Laundry_Staff WHERE email = %s"
    result = fetch_all(query, (email,))
    return result[0] if result else None

def create_staff_with_id(staff_id, first_name, last_name, role, email, password):
    query = """
        INSERT INTO Laundry_Staff (staff_id, first_name, last_name, role, email, password)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    execute_update(query, (staff_id, first_name, last_name, role, email, password))
    return staff_id


# ── AUTHENTICATION ──────────────────────────────────────────────────────────

def get_student_by_id(student_id):
    query = "SELECT * FROM Student WHERE student_id = %s"
    result = fetch_all(query, (student_id,))
    return result[0] if result else None

def get_staff_by_id(staff_id):
    query = "SELECT * FROM Laundry_Staff WHERE staff_id = %s"
    result = fetch_all(query, (staff_id,))
    return result[0] if result else None

# ── STUDENT ──────────────────────────────────────────────────────────────────

def get_student_with_wallet(student_id):
    query = """
        SELECT s.*, COALESCE(cw.balance, 0) as account_balance
        FROM Student s
        LEFT JOIN Cash_Wallet cw ON s.student_id = cw.student_id
        WHERE s.student_id = %s
    """
    result = fetch_all(query, (student_id,))
    return result[0] if result else None

def get_student_order_history(student_id):
    query = """
        SELECT order_id, dropoff_date, expected_pickup, actual_pickup,
               order_status, total_price, payment_status,
               weight_kg as total_weight_kg, service_type, processed_by
        FROM Laundry_Order
        WHERE student_id = %s
        ORDER BY dropoff_date DESC
    """
    return fetch_all(query, (student_id,))

def get_all_students():
    query = """
        SELECT s.*, COALESCE(cw.balance, 0) as account_balance
        FROM Student s
        LEFT JOIN Cash_Wallet cw ON s.student_id = cw.student_id
        ORDER BY s.student_id
    """
    return fetch_all(query)

def get_student(student_id):
    return get_student_with_wallet(student_id)

# ── ORDERS ────────────────────────────────────────────────────────────────────

def get_next_order_id():
    query = "SELECT COALESCE(MAX(order_id), 0) + 1 as next_id FROM Laundry_Order"
    result = fetch_all(query)
    return result[0]['next_id'] if result else 1

def get_all_orders():
    query = """
        SELECT o.order_id, o.student_id, o.dropoff_date, o.expected_pickup,
               o.actual_pickup, o.order_status, o.total_price, o.payment_status,
               o.weight_kg as total_weight_kg, o.service_type, o.processed_by,
               s.first_name as student_first, s.last_name as student_last
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query)

def get_orders_by_status(status):
    query = """
        SELECT o.order_id, o.student_id, o.dropoff_date, o.expected_pickup,
               o.actual_pickup, o.order_status, o.total_price, o.payment_status,
               o.weight_kg as total_weight_kg, o.service_type, o.processed_by,
               s.first_name as student_first, s.last_name as student_last
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE o.order_status = %s
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query, (status,))

def get_pending_orders():
    return get_orders_by_status('Pending')

def update_order_status(order_id, status):
    query = "UPDATE Laundry_Order SET order_status = %s WHERE order_id = %s"
    execute_update(query, (status, order_id))

def complete_order(order_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT machine_id, order_status FROM Laundry_Order WHERE order_id = %s", (order_id,))
        row = cur.fetchone()
        if not row:
            raise Exception(f"Order #{order_id} not found")
        if row[1] != 'In Progress':
            raise Exception(f"Order #{order_id} is '{row[1]}' — only In Progress orders can be completed")
        machine_id = row[0]
        cur.execute(
            "UPDATE Laundry_Order SET order_status = 'Completed', actual_pickup = CURRENT_TIMESTAMP WHERE order_id = %s",
            (order_id,)
        )
        if machine_id:
            # Only free machine if it has no other active orders
            cur.execute(
                "SELECT COUNT(*) FROM Laundry_Order WHERE machine_id = %s AND order_status IN ('Pending', 'In Progress') AND order_id != %s",
                (machine_id, order_id)
            )
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "UPDATE Laundry_Machine SET current_status = 'Available' WHERE machine_id = %s AND current_status != 'Maintenance'",
                    (machine_id,)
                )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error completing order: {e}")
        raise

def assign_order_to_machine(order_id, machine_id, staff_id=None, staff_name=None):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        # Validate machine exists and is available
        cur.execute("SELECT machine_id, current_status FROM Laundry_Machine WHERE machine_id = %s", (machine_id,))
        machine = cur.fetchone()
        if not machine:
            raise Exception(f"Machine #{machine_id} not found")

        # Check for any active order already on this machine (authoritative check)
        cur.execute(
            "SELECT order_id FROM Laundry_Order WHERE machine_id = %s AND order_status IN ('Pending', 'In Progress') LIMIT 1",
            (machine_id,)
        )
        existing = cur.fetchone()
        if existing:
            raise Exception(f"Machine #{machine_id} already has active order #{existing['order_id']}")

        if machine['current_status'] == 'Maintenance':
            raise Exception(f"Machine #{machine_id} is under maintenance and cannot be assigned")

        # Validate order exists and is Pending
        cur.execute("SELECT order_id, order_status FROM Laundry_Order WHERE order_id = %s", (order_id,))
        order = cur.fetchone()
        if not order:
            raise Exception(f"Order #{order_id} not found")
        if order['order_status'] != 'Pending':
            raise Exception(f"Order #{order_id} is '{order['order_status']}' — only Pending orders can be assigned")

        cur.execute(
            """UPDATE Laundry_Order
               SET order_status = 'In Progress', machine_id = %s,
                   staff_id = %s, processed_by = COALESCE(%s, processed_by)
               WHERE order_id = %s""",
            (machine_id, staff_id, staff_name, order_id)
        )
        cur.execute(
            "UPDATE Laundry_Machine SET current_status = 'Busy' WHERE machine_id = %s",
            (machine_id,)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error assigning order: {e}")
        raise

def create_complete_order(student_id, machine_id, service_type, weight_kg, total_price, tokens):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO Laundry_Order
                    (student_id, machine_id, service_type, weight_kg, total_price,
                     order_status, payment_status, notes,
                     dropoff_date, expected_pickup)
                    VALUES (%s, %s, %s, %s, %s, 'Pending', 'Pending', %s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3 days')
                    RETURNING order_id
                """
                notes = f"Tokens: {tokens}"
                cur.execute(query, (student_id, machine_id, service_type, weight_kg, total_price, notes))
                order_id = cur.fetchone()[0]
                conn.commit()
                return order_id
    except Exception as e:
        print(f"Error creating order: {e}")
        raise

# ── MACHINES ──────────────────────────────────────────────────────────────────

def get_all_machines():
    query = """
        SELECT DISTINCT ON (m.machine_id)
            m.machine_id, m.machine_type, m.capacity_kg, m.location,
            CASE
                WHEN o.order_id IS NOT NULL THEN 'Busy'
                WHEN m.current_status = 'Maintenance' THEN 'Maintenance'
                ELSE 'Available'
            END AS current_status,
            o.order_id, s.first_name, o.weight_kg
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id
            AND o.order_status IN ('Pending', 'In Progress')
        LEFT JOIN Student s ON o.student_id = s.student_id
        ORDER BY m.machine_id, o.order_id DESC NULLS LAST
    """
    return fetch_all(query)

def get_machine_details(machine_id):
    query = """
        SELECT DISTINCT ON (m.machine_id)
            m.machine_id, m.machine_type, m.capacity_kg, m.location,
            CASE
                WHEN o.order_id IS NOT NULL THEN 'Busy'
                WHEN m.current_status = 'Maintenance' THEN 'Maintenance'
                ELSE 'Available'
            END AS current_status,
            o.order_id, o.student_id, s.first_name, o.order_status
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id
            AND o.order_status IN ('Pending', 'In Progress')
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE m.machine_id = %s
        ORDER BY m.machine_id, o.order_id DESC NULLS LAST
    """
    result = fetch_all(query, (machine_id,))
    return result[0] if result else None

def update_machine_status(machine_id, status):
    query = "UPDATE Laundry_Machine SET current_status = %s WHERE machine_id = %s"
    execute_update(query, (status, machine_id))

def get_machine_utilization():
    return get_all_machines()

# ── PRICING ───────────────────────────────────────────────────────────────────

def get_pricing():
    return fetch_all("SELECT * FROM Pricing ORDER BY service_type")

def get_pricing_for_service(service_type):
    result = fetch_all("SELECT price_per_kg FROM Pricing WHERE service_type = %s", (service_type,))
    return float(result[0]['price_per_kg']) if result else None

def get_all_service_types():
    query = "SELECT DISTINCT service_type FROM Pricing ORDER BY service_type"
    return fetch_all(query)

# ── STAFF / FINANCIAL ─────────────────────────────────────────────────────────

def get_performance_report():
    query = """
        SELECT s.staff_id, s.first_name, s.last_name, s.role,
               COUNT(o.order_id) as orders_handled,
               COALESCE(SUM(o.total_price), 0) as total_revenue
        FROM Laundry_Staff s
        LEFT JOIN Laundry_Order o ON s.staff_id = o.staff_id
        GROUP BY s.staff_id, s.first_name, s.last_name, s.role
        ORDER BY total_revenue DESC
    """
    return fetch_all(query)

def get_financial_tracking():
    query = """
        SELECT o.order_id, o.student_id, o.dropoff_date, o.order_status,
               o.total_price, o.payment_status,
               s.first_name as student_first, s.last_name as student_last
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE o.payment_status IN ('Pending', 'Unpaid')
        ORDER BY o.dropoff_date
    """
    return fetch_all(query)

def get_student_orders(student_id):
    return get_student_order_history(student_id)

def get_all_pending_orders_list():
    query = """
        SELECT o.order_id, o.student_id, s.first_name, s.last_name,
               o.dropoff_date, o.total_price, o.weight_kg as total_weight_kg,
               o.service_type
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE o.order_status = 'Pending'
        ORDER BY o.dropoff_date ASC
    """
    return fetch_all(query)

def mark_order_as_picked_up(order_id):
    query = "UPDATE Laundry_Order SET order_status = 'Picked Up', payment_status = 'Paid', actual_pickup = CURRENT_TIMESTAMP WHERE order_id = %s"
    execute_update(query, (order_id,))

# ── WALLET MANAGEMENT ────────────────────────────────────

def get_wallet_by_student_id(student_id):
    result = fetch_all("SELECT * FROM Cash_Wallet WHERE student_id = %s", (student_id,))
    return result[0] if result else None

def get_order_by_id(order_id):
    query = """
        SELECT o.*,
               o.weight_kg as total_weight_kg,
               s.first_name as student_first, s.last_name as student_last
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE o.order_id = %s
    """
    result = fetch_all(query, (order_id,))
    return result[0] if result else None

def mark_order_picked_up_and_deduct_wallet(order_id, amount, student_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Lock wallet row and double-check balance
        cur.execute(
            "SELECT balance FROM Cash_Wallet WHERE student_id = %s FOR UPDATE",
            (student_id,)
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            raise Exception("Wallet not found")
        if float(row[0]) < float(amount):
            cur.close()
            conn.close()
            raise Exception(f"Insufficient balance: {float(row[0]):.2f} < {float(amount):.2f}")

        cur.execute("SELECT machine_id FROM Laundry_Order WHERE order_id = %s", (order_id,))
        machine_row = cur.fetchone()
        machine_id = machine_row[0] if machine_row else None

        cur.execute(
            "UPDATE Laundry_Order SET order_status = 'Picked Up', payment_status = 'Paid', actual_pickup = CURRENT_TIMESTAMP WHERE order_id = %s",
            (order_id,)
        )
        if machine_id:
            cur.execute(
                "SELECT COUNT(*) FROM Laundry_Order WHERE machine_id = %s AND order_status IN ('Pending', 'In Progress') AND order_id != %s",
                (machine_id, order_id)
            )
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "UPDATE Laundry_Machine SET current_status = 'Available' WHERE machine_id = %s AND current_status != 'Maintenance'",
                    (machine_id,)
                )
        # Inserting a negative amount triggers update_wallet_on_transaction which does balance + NEW.amount
        cur.execute(
            "INSERT INTO Wallet_Transaction (student_id, order_id, transaction_type, amount) VALUES (%s, %s, 'Order Payment', %s)",
            (student_id, order_id, -amount)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in mark_order_picked_up_and_deduct_wallet: {e}")
        raise

def get_wallet_transactions(student_id):
    query = """
        SELECT wt.transaction_id, wt.order_id, wt.transaction_type, wt.amount, wt.created_at,
               lo.order_status
        FROM Wallet_Transaction wt
        LEFT JOIN Laundry_Order lo ON wt.order_id = lo.order_id
        WHERE wt.student_id = %s
        ORDER BY wt.created_at DESC
    """
    return fetch_all(query, (student_id,))

def add_wallet_balance(student_id, amount, reason='Admin addition'):
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Inserting a positive amount triggers update_wallet_on_transaction which does balance + NEW.amount
        cur.execute(
            "INSERT INTO Wallet_Transaction (student_id, transaction_type, amount) VALUES (%s, %s, %s)",
            (student_id, reason, amount)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding wallet balance: {e}")
        raise

def verify_student_password(student_id, password):
    query = "SELECT password FROM Student WHERE student_id = %s"
    result = fetch_all(query, (student_id,))
    if result and result[0].get('password') == password:
        return True
    return False

def verify_staff_password(staff_id, password):
    query = "SELECT password FROM Laundry_Staff WHERE staff_id = %s"
    result = fetch_all(query, (staff_id,))
    if result and result[0].get('password') == password:
        return True
    return False

def get_single_machine_status(machine_id):
    query = """
        SELECT DISTINCT ON (m.machine_id)
            m.machine_id, m.machine_type, m.capacity_kg, m.location,
            CASE
                WHEN o.order_id IS NOT NULL THEN 'Busy'
                WHEN m.current_status = 'Maintenance' THEN 'Maintenance'
                ELSE 'Available'
            END AS current_status,
            o.order_id, s.first_name, o.weight_kg
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id
            AND o.order_status IN ('Pending', 'In Progress')
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE m.machine_id = %s
        ORDER BY m.machine_id, o.order_id DESC NULLS LAST
    """
    result = fetch_all(query, (machine_id,))
    return result[0] if result else None

# ── ADMIN ─────────────────────────────────────────────────────────────────────

def get_admin_by_username(username):
    query = "SELECT * FROM Admin WHERE username = %s"
    result = fetch_all(query, (username,))
    return result[0] if result else None

def get_admin_by_id(admin_id):
    query = "SELECT * FROM Admin WHERE admin_id = %s"
    result = fetch_all(query, (admin_id,))
    return result[0] if result else None

def verify_admin_password(username, password):
    query = "SELECT password FROM Admin WHERE username = %s"
    result = fetch_all(query, (username,))
    return bool(result and result[0]['password'] == password)

def create_admin(admin_id, username, email, password):
    query = """
        INSERT INTO Admin (admin_id, username, email, password, created_at)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
    """
    execute_update(query, (admin_id, username, email, password))

def get_all_students_for_admin():
    query = """
        SELECT s.*, COALESCE(cw.balance, 0) as account_balance,
               COUNT(o.order_id) as total_orders,
               COALESCE(SUM(o.total_price), 0) as total_spent
        FROM Student s
        LEFT JOIN Cash_Wallet cw ON s.student_id = cw.student_id
        LEFT JOIN Laundry_Order o ON s.student_id = o.student_id
        GROUP BY s.student_id, cw.balance
        ORDER BY s.student_id
    """
    return fetch_all(query)

def get_student_detail_for_admin(student_id):
    query = """
        SELECT s.*, COALESCE(cw.balance, 0) as account_balance
        FROM Student s
        LEFT JOIN Cash_Wallet cw ON s.student_id = cw.student_id
        WHERE s.student_id = %s
    """
    result = fetch_all(query, (student_id,))
    return result[0] if result else None

def get_student_all_orders_for_admin(student_id):
    query = """
        SELECT order_id, dropoff_date, expected_pickup, actual_pickup,
               order_status, total_price, payment_status,
               weight_kg as total_weight_kg, service_type, processed_by
        FROM Laundry_Order
        WHERE student_id = %s
        ORDER BY dropoff_date DESC
    """
    return fetch_all(query, (student_id,))

def update_student_info(student_id, first_name, last_name, email, phone, residence):
    query = """
        UPDATE Student
        SET first_name = %s, last_name = %s, email = %s, phone_number = %s, residence = %s
        WHERE student_id = %s
    """
    execute_update(query, (first_name, last_name, email, phone, residence, student_id))

def get_all_staff_for_admin():
    query = """
        SELECT s.staff_id, s.first_name, s.last_name, s.role, s.email, s.password,
               COUNT(o.order_id) as orders_handled,
               COALESCE(SUM(o.total_price), 0) as total_revenue
        FROM Laundry_Staff s
        LEFT JOIN Laundry_Order o ON s.staff_id = o.staff_id
        GROUP BY s.staff_id, s.first_name, s.last_name, s.role, s.email, s.password
        ORDER BY s.staff_id
    """
    return fetch_all(query)

def get_staff_detail_for_admin(staff_id):
    query = """
        SELECT s.staff_id, s.first_name, s.last_name, s.role, s.email, s.password,
               COUNT(o.order_id) as orders_handled,
               COALESCE(SUM(o.total_price), 0) as total_revenue
        FROM Laundry_Staff s
        LEFT JOIN Laundry_Order o ON s.staff_id = o.staff_id
        WHERE s.staff_id = %s
        GROUP BY s.staff_id, s.first_name, s.last_name, s.role, s.email, s.password
    """
    result = fetch_all(query, (staff_id,))
    return result[0] if result else None

def get_staff_orders_for_admin(staff_id):
    query = """
        SELECT o.order_id, o.student_id,
               s.first_name as student_first, s.last_name as student_last,
               o.dropoff_date, o.order_status, o.total_price, o.payment_status,
               o.processed_by
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE o.staff_id = %s
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query, (staff_id,))

def delete_staff(staff_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                staff = get_staff_by_id(staff_id)
                if staff:
                    name = f"{staff['first_name']} {staff['last_name']}"
                    cur.execute(
                        "UPDATE Laundry_Order SET processed_by = %s WHERE staff_id = %s AND (processed_by IS NULL OR processed_by = 'Unassigned')",
                        (name, staff_id)
                    )
                cur.execute("DELETE FROM Laundry_Staff WHERE staff_id = %s", (staff_id,))
                conn.commit()
                return True
    except Exception as e:
        print(f"Error deleting staff: {e}")
        raise

def get_all_orders_for_admin():
    query = """
        SELECT o.order_id, o.student_id, o.staff_id,
               s.first_name as student_first, s.last_name as student_last,
               o.processed_by,
               o.dropoff_date, o.order_status, o.total_price, o.payment_status,
               o.weight_kg as total_weight_kg, o.service_type
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query)

# ── UTILS ─────────────────────────────────────────────────────────────────────

def test_connection():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM Student")
                count = cur.fetchone()[0]
                return True, f"[OK] Database connected! {count} students found."
    except Exception as e:
        return False, f"[ERROR] Database error: {e}"
