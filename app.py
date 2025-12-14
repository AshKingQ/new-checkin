"""
Main Flask application for the Student Check-in System.
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import secrets
import string
import functools
import os
import sqlite3
from database import get_db_connection, hash_password, verify_password, init_database

app = Flask(__name__)
# Use persistent secret key from environment or generate one (sessions will be lost on restart if generated)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Initialize database on first run
init_database()

def generate_checkin_code(length=6):
    """Generate a random check-in code."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def parse_datetime(datetime_str):
    """Parse datetime from database (handles both ISO format and SQLite format)."""
    try:
        return datetime.fromisoformat(datetime_str)
    except ValueError:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')

def login_required(role=None):
    """Decorator to check if user is logged in."""
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            if role and session.get('role') != role:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Routes for pages
@app.route('/')
def index():
    """Home page - redirect based on login status."""
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/admin/login')
def admin_login():
    """Admin login page."""
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard page."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/student/register')
def student_register():
    """Student registration page."""
    return render_template('student_register.html')

@app.route('/student/login')
def student_login():
    """Student login page."""
    return render_template('student_login.html')

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard page."""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    return render_template('student_dashboard.html')

# API Routes
@app.route('/api/login', methods=['POST'])
def api_login():
    """Login endpoint for both admin and students."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND role = ?',
        (username, role)
    ).fetchone()
    conn.close()
    
    if user and verify_password(password, user['password']):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['name'] = user['name']
        return jsonify({
            'success': True,
            'role': user['role'],
            'name': user['name']
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    """Student registration endpoint."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    student_id = data.get('student_id')
    
    if not all([username, password, name, student_id]):
        return jsonify({'error': 'All fields are required'}), 400
    
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password, role, name, student_id) VALUES (?, ?, ?, ?, ?)',
            (username, hash_password(password), 'student', name, student_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username or Student ID already exists'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout endpoint."""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/admin/sessions', methods=['GET'])
@login_required(role='admin')
def api_get_sessions():
    """Get all check-in sessions."""
    conn = get_db_connection()
    sessions = conn.execute(
        'SELECT * FROM sessions ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    return jsonify([dict(s) for s in sessions])

@app.route('/api/admin/sessions', methods=['POST'])
@login_required(role='admin')
def api_create_session():
    """Create a new check-in session."""
    data = request.json
    title = data.get('title')
    duration_minutes = data.get('duration_minutes', 60)
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    checkin_code = generate_checkin_code()
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=int(duration_minutes))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO sessions (title, checkin_code, start_time, end_time, created_by) VALUES (?, ?, ?, ?, ?)',
        (title, checkin_code, start_time, end_time, session['user_id'])
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'checkin_code': checkin_code,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat()
    })

@app.route('/api/admin/sessions/<int:session_id>/records', methods=['GET'])
@login_required(role='admin')
def api_get_session_records(session_id):
    """Get check-in records for a specific session."""
    conn = get_db_connection()
    
    # Get session details
    session_data = conn.execute(
        'SELECT * FROM sessions WHERE id = ?',
        (session_id,)
    ).fetchone()
    
    if not session_data:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    # Get all students
    all_students = conn.execute(
        'SELECT id, name, student_id FROM users WHERE role = "student"'
    ).fetchall()
    
    # Get check-in records
    records = conn.execute(
        '''SELECT r.*, u.name, u.student_id 
           FROM records r 
           JOIN users u ON r.user_id = u.id 
           WHERE r.session_id = ?
           ORDER BY r.checkin_time''',
        (session_id,)
    ).fetchall()
    conn.close()
    
    checked_in = [dict(r) for r in records]
    checked_in_ids = {r['user_id'] for r in records}
    
    missed = [
        {'id': s['id'], 'name': s['name'], 'student_id': s['student_id']}
        for s in all_students if s['id'] not in checked_in_ids
    ]
    
    return jsonify({
        'session': dict(session_data),
        'checked_in': checked_in,
        'missed': missed
    })

@app.route('/api/student/checkin', methods=['POST'])
@login_required(role='student')
def api_student_checkin():
    """Student check-in endpoint."""
    data = request.json
    checkin_code = data.get('checkin_code')
    
    if not checkin_code:
        return jsonify({'error': 'Check-in code is required'}), 400
    
    conn = get_db_connection()
    
    # Find the session with this code
    session_data = conn.execute(
        'SELECT * FROM sessions WHERE checkin_code = ?',
        (checkin_code,)
    ).fetchone()
    
    if not session_data:
        conn.close()
        return jsonify({'error': 'Invalid check-in code'}), 400
    
    # Check if within time window
    current_time = datetime.now()
    start_time = parse_datetime(session_data['start_time'])
    end_time = parse_datetime(session_data['end_time'])
    
    if current_time < start_time:
        conn.close()
        return jsonify({'error': 'Check-in has not started yet'}), 400
    
    if current_time > end_time:
        conn.close()
        return jsonify({'error': 'Check-in time has expired'}), 400
    
    # Check if already checked in
    existing_record = conn.execute(
        'SELECT * FROM records WHERE session_id = ? AND user_id = ?',
        (session_data['id'], session['user_id'])
    ).fetchone()
    
    if existing_record:
        conn.close()
        return jsonify({'error': 'You have already checked in for this session'}), 400
    
    # Record the check-in
    conn.execute(
        'INSERT INTO records (session_id, user_id) VALUES (?, ?)',
        (session_data['id'], session['user_id'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Check-in successful',
        'session_title': session_data['title']
    })

@app.route('/api/student/history', methods=['GET'])
@login_required(role='student')
def api_student_history():
    """Get student's check-in history."""
    conn = get_db_connection()
    history = conn.execute(
        '''SELECT s.title, s.start_time, s.end_time, r.checkin_time
           FROM records r
           JOIN sessions s ON r.session_id = s.id
           WHERE r.user_id = ?
           ORDER BY r.checkin_time DESC''',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(h) for h in history])

if __name__ == '__main__':
    # WARNING: Debug mode is enabled for development purposes only.
    # Set debug=False in production to prevent security vulnerabilities.
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
