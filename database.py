import psycopg2
from psycopg2.extras import DictCursor

DB_NAME = "laundry_db"
DB_USER = "makabiri"

def get_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER)

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

def get_all_orders():
    # Fetch all orders along with student and staff basic info
    query = """
        SELECT o.*, s.first_name as student_first, s.last_name as student_last,
               st.first_name as staff_first, st.last_name as staff_last
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        LEFT JOIN Laundry_Staff st ON o.staff_id = st.staff_id
        ORDER BY o.dropoff_date DESC
    """
    return fetch_all(query)

def update_order_status(order_id, status):
    query = "UPDATE Laundry_Order SET order_status = %s WHERE order_id = %s"
    execute_update(query, (status, order_id))

def get_financial_tracking():
    # "Financial Tracking: SELECT * FROM Laundry_Order WHERE payment_status IN ('Pending', 'Unpaid')"
    query = """
        SELECT o.*, s.first_name as student_first, s.last_name as student_last 
        FROM Laundry_Order o
        LEFT JOIN Student s ON o.student_id = s.student_id
        WHERE payment_status IN ('Pending', 'Unpaid')
        ORDER BY o.dropoff_date
    """
    return fetch_all(query)

def get_machine_utilization():
    # Left join to view all machines, and their current order if any
    query = """
        SELECT m.machine_id, m.machine_type, m.capacity_kg, m.current_status, m.location,
               o.order_id, o.order_status
        FROM Laundry_Machine m
        LEFT JOIN Laundry_Order o ON m.machine_id = o.machine_id AND o.order_status IN ('In Progress', 'Received')
        ORDER BY m.machine_id;
    """
    return fetch_all(query)

def get_performance_report():
    # "A query using JOIN between Laundry_Staff and Laundry_Order to count orders handled."
    # "executes a SUM and GROUP BY query to show earnings per staff member."
    query = """
        SELECT s.staff_id, s.first_name, s.last_name, s.role,
               COUNT(o.order_id) as orders_handled,
               COALESCE(SUM(o.total_price), 0) as total_revenue
        FROM Laundry_Staff s
        LEFT JOIN Laundry_Order o ON s.staff_id = o.staff_id
        GROUP BY s.staff_id, s.first_name, s.last_name, s.role
        ORDER BY total_revenue DESC;
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

def get_all_students():
    query = """
        SELECT s.*, COALESCE(cw.balance, 0) as account_balance 
        FROM Student s 
        LEFT JOIN Cash_Wallet cw ON s.student_id = cw.student_id 
        ORDER BY s.student_id
    """
    return fetch_all(query)

def get_student_orders(student_id):
    query = "SELECT * FROM Laundry_Order WHERE student_id = %s ORDER BY dropoff_date DESC"
    return fetch_all(query, (student_id,))

def create_order(student_id, machine_id, service_type, weight_kg, total_price, notes=None):
    query = """
        INSERT INTO Laundry_Order (student_id, machine_id, service_type, weight_kg, total_price, order_status, notes)
        VALUES (%s, %s, %s, %s, %s, 'Pending', %s)
        RETURNING order_id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (student_id, machine_id, service_type, weight_kg, total_price, notes))
            order_id = cur.fetchone()[0]
            conn.commit()
            return order_id
