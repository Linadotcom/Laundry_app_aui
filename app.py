from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from functools import wraps
import database
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_laundry_key'

# ── DECORATORS ────────────────────────────────────────────────────────────────

def student_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_type') != 'student':
            flash('Please log in as a student.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def staff_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_type') != 'staff':
            flash('Please log in as staff.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Please log in as admin.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── HOME ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('layout.html', active_page='home')

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')

        if not user_type or not user_id or not password:
            flash('Please fill in all fields.', 'error')
            role = request.form.get('user_type', '')
            return render_template('login.html', role=role)

        try:
            if user_type == 'student':
                student = database.get_student_by_id(int(user_id))
                if student and database.verify_student_password(int(user_id), password):
                    session['user_type'] = 'student'
                    session['user_id'] = int(user_id)
                    session['first_name'] = student['first_name']
                    flash(f'Welcome {student["first_name"]}!', 'success')
                    return redirect(url_for('student_dashboard'))
                else:
                    flash('Invalid Student ID or password.', 'error')
            elif user_type == 'staff':
                staff = database.get_staff_by_id(int(user_id))
                if staff and database.verify_staff_password(int(user_id), password):
                    session['user_type'] = 'staff'
                    session['user_id'] = int(user_id)
                    session['first_name'] = staff['first_name']
                    flash(f'Welcome {staff["first_name"]}!', 'success')
                    return redirect(url_for('staff_dashboard'))
                else:
                    flash('Invalid Staff ID or password.', 'error')
            elif user_type == 'admin':
                if database.verify_admin_password(user_id, password):
                    session['user_type'] = 'admin'
                    session['username'] = user_id
                    flash('Welcome Admin!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid admin credentials.', 'error')
            else:
                flash('Invalid user type.', 'error')
        except ValueError:
            flash('ID must be a number.', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    role = request.args.get('role', '')
    return render_template('login.html', role=role)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# ── STUDENT ROUTES ────────────────────────────────────────────────────────────

@app.route('/student-dashboard')
@student_login_required
def student_dashboard():
    student_id = session.get('user_id')
    student = database.get_student_with_wallet(student_id)
    order_history = database.get_student_order_history(student_id)
    if 'order_flash' in session:
        flash(session.pop('order_flash'), 'success')
    return render_template('student_dashboard.html',
                           student=student,
                           order_history=order_history,
                           active_page='student')

@app.route('/student-new-order')
@student_login_required
def student_new_order():
    student_id = session.get('user_id')
    student = database.get_student_with_wallet(student_id)
    next_order_id = database.get_next_order_id()
    service_types = database.get_all_service_types()
    return render_template('student_new_order.html',
                           student=student,
                           next_order_id=next_order_id,
                           service_types=service_types,
                           active_page='student')

@app.route('/api/student/create-order', methods=['POST'])
@student_login_required
def api_create_student_order():
    try:
        student_id = session.get('user_id')
        data = request.json

        service_type = data.get('service_type')
        weight_kg = float(data.get('weight_kg', 0))
        tokens = int(data.get('tokens', 0))

        if not service_type or weight_kg <= 0 or tokens <= 0:
            return jsonify({'success': False, 'error': 'Please fill in all fields correctly.'}), 400

        total_price = weight_kg * 1.50 * tokens

        order_id = database.create_complete_order(
            student_id, None, service_type, weight_kg, total_price, tokens
        )
        session['order_flash'] = f'Order #{order_id} placed successfully — {total_price:.2f} Dhs ({tokens} token{"s" if tokens != 1 else ""}). Staff will assign a machine shortly.'
        return jsonify({'success': True, 'order_id': order_id, 'total_price': total_price})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── STAFF ROUTES ──────────────────────────────────────────────────────────────

@app.route('/staff-dashboard')
@staff_login_required
def staff_dashboard():
    status = request.args.get('status', 'All')
    all_orders = database.get_all_orders()
    orders = all_orders if status == 'All' else database.get_orders_by_status(status)
    machines = database.get_all_machines()
    pending_orders = database.get_all_pending_orders_list()
    financials = database.get_financial_tracking()
    pending_count = sum(1 for o in all_orders if o['order_status'] == 'Pending')
    in_progress_count = sum(1 for o in all_orders if o['order_status'] == 'In Progress')
    completed_count = sum(1 for o in all_orders if o['order_status'] == 'Completed')
    available_machines = sum(1 for m in machines if m['current_status'] == 'Available')
    return render_template('staff_dashboard.html',
                           orders=orders,
                           machines=machines,
                           pending_orders=pending_orders,
                           financials=financials,
                           current_status=status,
                           pending_count=pending_count,
                           in_progress_count=in_progress_count,
                           completed_count=completed_count,
                           available_machines=available_machines,
                           active_page='staff')

@app.route('/api/machine/<int:machine_id>/assign-order', methods=['POST'])
@staff_login_required
def api_assign_order_to_machine(machine_id):
    try:
        data = request.json
        order_id = int(data.get('order_id'))
        database.assign_order_to_machine(order_id, machine_id)
        machine = database.get_single_machine_status(machine_id)
        return jsonify({
            'success': True,
            'machine': {
                'machine_id': machine['machine_id'],
                'current_status': machine['current_status'],
                'order_id': machine['order_id'],
                'student_name': machine['first_name'],
                'weight_kg': str(machine['weight_kg']) if machine['weight_kg'] else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/order/<int:order_id>/complete', methods=['POST'])
@staff_login_required
def api_complete_order(order_id):
    try:
        # Find which machine this order was on before completing
        order_machine = database.fetch_all(
            "SELECT machine_id FROM Laundry_Order WHERE order_id = %s", (order_id,)
        )
        machine_id = order_machine[0]['machine_id'] if order_machine else None
        database.complete_order(order_id)
        return jsonify({'success': True, 'new_status': 'Completed', 'machine_id': machine_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/order/<int:order_id>/picked-up', methods=['POST'])
@staff_login_required
def api_picked_up_order(order_id):
    try:
        database.mark_order_as_picked_up(order_id)
        return jsonify({'success': True, 'new_status': 'Picked Up'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/order/<int:order_id>/status', methods=['POST'])
@staff_login_required
def api_update_order_status(order_id):
    try:
        data = request.json
        new_status = data.get('status')
        if new_status not in ['Pending', 'In Progress', 'Completed', 'Picked Up']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        database.update_order_status(order_id, new_status)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── PRICING (public) ──────────────────────────────────────────────────────────

@app.route('/pricing')
def pricing():
    pricing_data = database.get_pricing()
    return render_template('pricing.html', pricing=pricing_data, active_page='pricing')

# ── TEST ──────────────────────────────────────────────────────────────────────

@app.route('/test-db')
def test_db():
    success, message = database.test_connection()
    return jsonify({'success': success, 'message': message})

# ── ADMIN ROUTES ──────────────────────────────────────────────────────────────

@app.route('/admin-dashboard')
@admin_login_required
def admin_dashboard():
    students = database.get_all_students_for_admin()
    orders = database.get_all_orders_for_admin()
    staff = database.get_all_staff_for_admin()
    student_count = len(students)
    order_count = len(orders)
    staff_count = len(staff)
    pending_orders = sum(1 for o in orders if o['order_status'] == 'Pending')
    return render_template('admin_dashboard.html',
                           students=students, orders=orders, staff=staff,
                           student_count=student_count, order_count=order_count,
                           staff_count=staff_count, pending_orders=pending_orders,
                           active_page='admin')

@app.route('/admin/student/<int:student_id>')
@admin_login_required
def admin_student_detail(student_id):
    student = database.get_student_detail_for_admin(student_id)
    orders = database.get_student_all_orders_for_admin(student_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_student_detail.html',
                           student=student, orders=orders, active_page='admin')

@app.route('/admin/staff/<int:staff_id>')
@admin_login_required
def admin_staff_detail(staff_id):
    staff = database.get_staff_detail_for_admin(staff_id)
    orders = database.get_staff_orders_for_admin(staff_id)
    if not staff:
        flash('Staff not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_staff_detail.html',
                           staff=staff, orders=orders, active_page='admin')

@app.route('/api/admin/student/<int:student_id>/update', methods=['POST'])
@admin_login_required
def api_update_student(student_id):
    try:
        data = request.json
        database.update_student_info(
            student_id,
            data.get('first_name'), data.get('last_name'),
            data.get('email'), data.get('phone'), data.get('residence')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/staff/<int:staff_id>/delete', methods=['POST'])
@admin_login_required
def api_delete_staff(staff_id):
    try:
        database.delete_staff(staff_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
