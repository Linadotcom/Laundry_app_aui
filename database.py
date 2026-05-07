import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "ep-patient-sound-abb14rjt-pooler.eu-west-2.aws.neon.tech")
DB_NAME = os.getenv("DATABASE_NAME", "neondb")
DB_USER = os.getenv("DATABASE_USER", "neondb_owner")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "npg_b1G3HqTDPkER")

def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            port=DB_PORT,
            password=DB_PASSWORD,
            sslmode="require"
        )
        conn.cursor().execute("SET search_path TO public")
        return conn
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
               weight_kg as total_weight_kg, service_type
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
               o.weight_kg as total_weight_kg, o.service_type,
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
               o.weight_kg as total_weight_kg, o.service_type,
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
    query = "UPDATE Laundry_Order SET order_status = 'Completed', actual_pickup = CURRENT_TIMESTAMP WHERE order_id = %s"
    execute_update(query, (order_id,))

def assign_order_to_machine(order_id, machine_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE Laundry_Order SET order_status = 'In Progress', machine_id = %s WHERE order_id = %s",
                    (machine_id, order_id)
                )
                conn.commit()
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
        SELECT m.machine_id, m.machine_type, m.capacity_kg, m.location,
               CASE WHEN o.order_id IS NOT NULL THEN 'Busy' ELSE 'Available' END AS current_status,
               o.order_id, s.first_name, o.weight_kg
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id
            AND o.order_status = 'In Progress'
        LEFT JOIN Student s ON o.student_id = s.student_id
        ORDER BY m.machine_id
    """
    return fetch_all(query)

def get_machine_details(machine_id):
    query = """
        SELECT m.machine_id, m.machine_type, m.capacity_kg, m.current_status, m.location,
               o.order_id, o.student_id, s.first_name, o.order_status
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id
            AND o.order_status IN ('Pending', 'In Progress')
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE m.machine_id = %s
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
        SELECT m.machine_id, m.machine_type, m.capacity_kg, m.location,
               CASE WHEN o.order_id IS NOT NULL THEN 'Busy' ELSE 'Available' END AS current_status,
               o.order_id, s.first_name, o.weight_kg
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id
            AND o.order_status = 'In Progress'
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE m.machine_id = %s
        LIMIT 1
    """
    result = fetch_all(query, (machine_id,))
    return result[0] if result else None

# ── ADMIN ─────────────────────────────────────────────────────────────────────

def get_admin_by_username(username):
    query = "SELECT * FROM Admin WHERE username = %s"
    result = fetch_all(query, (username,))
    return result[0] if result else None

def verify_admin_password(username, password):
    query = "SELECT password FROM Admin WHERE username = %s"
    result = fetch_all(query, (username,))
    return bool(result and result[0]['password'] == password)

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
               weight_kg as total_weight_kg, service_type
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
        SELECT s.*, COUNT(o.order_id) as orders_handled,
               COALESCE(SUM(o.total_price), 0) as total_revenue
        FROM Laundry_Staff s
        LEFT JOIN Laundry_Order o ON s.staff_id = o.staff_id
        GROUP BY s.staff_id
        ORDER BY s.staff_id
    """
    return fetch_all(query)

def get_staff_detail_for_admin(staff_id):
    query = """
        SELECT s.*, COUNT(o.order_id) as orders_handled,
               COALESCE(SUM(o.total_price), 0) as total_revenue
        FROM Laundry_Staff s
        LEFT JOIN Laundry_Order o ON s.staff_id = o.staff_id
        WHERE s.staff_id = %s
        GROUP BY s.staff_id
    """
    result = fetch_all(query, (staff_id,))
    return result[0] if result else None

def get_staff_orders_for_admin(staff_id):
    query = """
        SELECT o.order_id, o.student_id, s.first_name, s.last_name,
               o.dropoff_date, o.order_status, o.total_price, o.payment_status
        FROM Laundry_Order o
        JOIN Student s ON o.student_id = s.student_id
        WHERE o.staff_id = %s
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query, (staff_id,))

def delete_staff(staff_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE Laundry_Order SET staff_id = NULL WHERE staff_id = %s", (staff_id,))
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
               st.first_name as staff_first, st.last_name as staff_last,
               o.dropoff_date, o.order_status, o.total_price, o.payment_status,
               o.weight_kg as total_weight_kg, o.service_type
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        LEFT JOIN Laundry_Staff st ON o.staff_id = st.staff_id
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query)

# ── UTILS ─────────────────────────────────────────────────────────────────────

def test_connection():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM student")
                count = cur.fetchone()[0]
                return True, f"[OK] Database connected! {count} students found."
    except Exception as e:
        return False, f"[ERROR] Database error: {e}"
