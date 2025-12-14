import sqlite3
from datetime import datetime
import bcrypt


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('checkin.db')
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def init_db():
    """Initialize database with tables and admin user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create checkin_tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Create checkin_records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES checkin_tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(task_id, user_id)
        )
    ''')
    
    # Check if admin user exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # Create default admin user
        admin_password = hash_password('admin')
        cursor.execute(
            'INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
            ('admin', admin_password, 'Administrator', 'admin')
        )
        import os
        if os.environ.get('FLASK_DEBUG', 'True') == 'True':
            print('Admin user created: username=admin, password=admin')
        else:
            print('Admin user created successfully')
    
    conn.commit()
    conn.close()
    print('Database initialized successfully')


def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user


def create_user(username, password, name, role='student'):
    """Create a new user"""
    conn = get_db_connection()
    try:
        hashed_pw = hash_password(password)
        conn.execute(
            'INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
            (username, hashed_pw, name, role)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def create_checkin_task(title, code, start_time, end_time, created_by):
    """Create a new checkin task"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'INSERT INTO checkin_tasks (title, code, start_time, end_time, created_by) VALUES (?, ?, ?, ?, ?)',
            (title, code, start_time, end_time, created_by)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_all_checkin_tasks():
    """Get all checkin tasks"""
    conn = get_db_connection()
    tasks = conn.execute(
        'SELECT * FROM checkin_tasks ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return tasks


def get_checkin_task_by_id(task_id):
    """Get checkin task by ID"""
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM checkin_tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    return task


def get_checkin_task_by_code(code):
    """Get checkin task by code"""
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM checkin_tasks WHERE code = ?', (code,)).fetchone()
    conn.close()
    return task


def create_checkin_record(task_id, user_id):
    """Create a checkin record"""
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO checkin_records (task_id, user_id) VALUES (?, ?)',
            (task_id, user_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def get_checkin_records_by_task(task_id):
    """Get all checkin records for a task"""
    conn = get_db_connection()
    records = conn.execute('''
        SELECT cr.*, u.username, u.name 
        FROM checkin_records cr
        JOIN users u ON cr.user_id = u.id
        WHERE cr.task_id = ?
        ORDER BY cr.checkin_time DESC
    ''', (task_id,)).fetchall()
    conn.close()
    return records


def has_checked_in(task_id, user_id):
    """Check if user has checked in for a task"""
    conn = get_db_connection()
    record = conn.execute(
        'SELECT id FROM checkin_records WHERE task_id = ? AND user_id = ?',
        (task_id, user_id)
    ).fetchone()
    conn.close()
    return record is not None


def get_all_students():
    """Get all students"""
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM users WHERE role = ? ORDER BY username',
        ('student',)
    ).fetchall()
    conn.close()
    return students
