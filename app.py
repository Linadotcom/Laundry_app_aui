from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from functools import wraps
import database

app = Flask(__name__)
app.secret_key = 'super_secret_laundry_key'

STAFF_CREDENTIALS = {
    'admin': 'laundry2024',
    'staff': 'aui2024',
}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access the Staff Dashboard.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('layout.html', active_page='home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('staff'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if STAFF_CREDENTIALS.get(username) == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('staff'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', active_page='login')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/staff')
@login_required
def staff():
    orders = database.get_all_orders()
    machines = database.get_machine_utilization()
    performance = database.get_performance_report()
    financials = database.get_financial_tracking()

    return render_template('staff.html',
                           orders=orders,
                           machines=machines,
                           performance=performance,
                           financials=financials,
                           active_page='staff')

@app.route('/student', methods=['GET', 'POST'])
def student():
    student_info = None
    orders = []
    error = None
    all_students = database.get_all_students()

    if request.method == 'POST':
        student_id_str = request.form.get('student_id')
        if student_id_str and student_id_str.isdigit():
            student_id = int(student_id_str)
            student_info = database.get_student(student_id)
            if student_info:
                orders = database.get_student_orders(student_id)
            else:
                error = "Student ID not found."
        else:
            error = "Please enter a valid numeric Student ID."

    return render_template('student.html',
                           student=student_info,
                           orders=orders,
                           error=error,
                           all_students=all_students,
                           active_page='student')

@app.route('/pricing')
def pricing():
    pricing_data = database.get_pricing()
    return render_template('pricing.html',
                           pricing=pricing_data,
                           active_page='pricing')

@app.route('/api/update_status', methods=['POST'])
def update_status():
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')

    if not order_id or not new_status:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400

    try:
        database.update_order_status(int(order_id), new_status)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create_order', methods=['POST'])
def create_order_api():
    try:
        data = request.json
        student_id = data.get('student_id')
        machine_id = data.get('machine_id')
        service_type = data.get('service_type')
        weight_kg = float(data.get('weight_kg', 0))

        if not all([student_id, machine_id, service_type, weight_kg]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        if weight_kg <= 0:
            return jsonify({'success': False, 'error': 'Weight must be greater than 0'}), 400

        total_price = weight_kg * 1.50

        order_id = database.create_order(student_id, machine_id, service_type, weight_kg, total_price)

        return jsonify({'success': True, 'order_id': order_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test-db')
def test_db():
    success, message = database.test_connection()
    return jsonify({'success': success, 'message': message})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
