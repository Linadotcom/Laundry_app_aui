import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_NAME = os.getenv("DATABASE_NAME", "laundry_db")
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

def get_pricing():
    return fetch_all("SELECT * FROM Pricing ORDER BY service_type")

def get_all_students():
    query = """
        SELECT s.*, COALESCE(cw.balance, 0) as account_balance
        FROM Student s
        LEFT JOIN Cash_Wallet cw ON s.student_id = cw.student_id
        ORDER BY s.student_id
    """
    return fetch_all(query)

def get_student(student_id):
    query = """
        SELECT s.*, COALESCE(cw.balance, 0) as account_balance
        FROM Student s
        LEFT JOIN Cash_Wallet cw ON s.student_id = cw.student_id
        WHERE s.student_id = %s
    """
    result = fetch_all(query, (student_id,))
    return result[0] if result else None

def get_student_orders(student_id):
    query = """
        SELECT o.order_id, o.student_id, o.dropoff_date, o.expected_pickup,
               o.actual_pickup, o.order_status, o.total_price, o.payment_status,
               o.notes
        FROM Laundry_Order o
        WHERE o.student_id = %s
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query, (student_id,))

def get_all_orders():
    query = """
        SELECT o.order_id, o.student_id, o.dropoff_date, o.expected_pickup,
               o.actual_pickup, o.order_status, o.total_price, o.payment_status,
               s.first_name as student_first, s.last_name as student_last
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query)

def update_order_status(order_id, status):
    query = "UPDATE Laundry_Order SET order_status = %s WHERE order_id = %s"
    execute_update(query, (status, order_id))

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

def get_machine_utilization():
    query = """
        SELECT m.machine_id, m.machine_type, m.capacity_kg, m.current_status, m.location,
               m.usage_count,
               COUNT(o.order_id) as times_used,
               COALESCE(SUM(o.weight_kg), 0) as total_weight_processed
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id
        GROUP BY m.machine_id, m.machine_type, m.capacity_kg, m.current_status, m.location, m.usage_count
        ORDER BY m.machine_id
    """
    return fetch_all(query)

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

def create_order(student_id, machine_id, service_type, weight_kg, total_price, notes=None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO Laundry_Order
                    (student_id, machine_id, service_type, weight_kg, total_price,
                     order_status, payment_status, notes,
                     dropoff_date, expected_pickup)
                    VALUES (%s, %s, %s, %s, %s, 'Pending', 'Unpaid', %s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3 days')
                    RETURNING order_id
                """
                cur.execute(query, (student_id, machine_id, service_type, weight_kg, total_price, notes))
                order_id = cur.fetchone()[0]
                conn.commit()
                return order_id
    except Exception as e:
        print(f"Error creating order: {e}")
        raise

def test_connection():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM Student")
                count = cur.fetchone()[0]
                return True, f"[OK] Database connected! {count} students found."
    except Exception as e:
        return False, f"[ERROR] Database error: {e}"
