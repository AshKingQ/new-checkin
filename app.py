from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
from datetime import datetime
import secrets
import os
import csv
import io

from config import Config
from database import (
    init_db, get_user_by_username, create_user, verify_password,
    create_checkin_task, get_all_checkin_tasks, get_checkin_task_by_id,
    get_checkin_task_by_code, create_checkin_record, get_checkin_records_by_task,
    has_checked_in, get_all_students, get_student_attendance_stats,
    get_task_attendance_stats, get_overall_stats, bulk_create_users, get_occupied_seats
)
from models import User, CheckinTask

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on first run
if not os.path.exists(app.config['DATABASE']):
    init_db()


def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('需要管理员权限', 'danger')
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('请填写完整信息', 'danger')
            return render_template('login.html')
        
        user = get_user_by_username(username)
        if user and verify_password(password, user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            session['role'] = user['role']
            flash(f'欢迎回来，{user["name"]}！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not name or not password:
            flash('请填写完整信息', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('密码长度至少6位', 'danger')
            return render_template('register.html')
        
        if create_user(username, password, name):
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        else:
            flash('学号已被注册', 'danger')
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    tasks = get_all_checkin_tasks()
    task_list = []
    for task in tasks:
        task_dict = dict(task)
        task_dict['has_checked_in'] = has_checked_in(task['id'], session['user_id'])
        task_dict['is_active'] = CheckinTask.from_row(task).is_active()
        task_list.append(task_dict)
    
    return render_template('student/dashboard.html', tasks=task_list)


@app.route('/student/checkin', methods=['GET', 'POST'])
@login_required
def student_checkin():
    """Student checkin page"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location_accuracy = request.form.get('location_accuracy')
        location_time = request.form.get('location_time')
        seat_row = request.form.get('seat_row', '').strip()
        seat_col = request.form.get('seat_col', '').strip()
        
        if not code:
            flash('请输入签到码', 'danger')
            return render_template('student/checkin.html')
        
        task = get_checkin_task_by_code(code)
        if not task:
            flash('签到码不存在', 'danger')
            return render_template('student/checkin.html')
        
        task_obj = CheckinTask.from_row(task)
        if not task_obj.is_active():
            flash('签到码已过期或尚未开始', 'danger')
            return render_template('student/checkin.html')
        
        if has_checked_in(task['id'], session['user_id']):
            flash('您已经签到过了', 'warning')
            return redirect(url_for('student_dashboard'))
        
        # If no seat selected yet, show step 2 (seat selection and location)
        if not seat_row or not seat_col:
            return render_template('student/checkin.html', task=task)
        
        # Convert location data to proper types with error handling
        try:
            lat = float(latitude) if latitude else None
            lng = float(longitude) if longitude else None
            acc = float(location_accuracy) if location_accuracy else None
            seat_col_int = int(seat_col) if seat_col else None
        except (ValueError, TypeError):
            flash('位置或座位数据格式错误', 'danger')
            return render_template('student/checkin.html', task=task)
        
        if create_checkin_record(task['id'], session['user_id'], 
                                lat, lng, acc, location_time, 
                                seat_row, seat_col_int):
            location_msg = f"（位置：{lat:.6f}, {lng:.6f}）" if lat and lng else ""
            seat_msg = f"（座位：{seat_row}{seat_col}）" if seat_row and seat_col else ""
            flash(f'签到成功：{task["title"]} {location_msg} {seat_msg}', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('签到失败，请重试', 'danger')
    
    return render_template('student/checkin.html')


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    tasks = get_all_checkin_tasks()
    task_list = []
    for task in tasks:
        task_dict = dict(task)
        records = get_checkin_records_by_task(task['id'])
        task_dict['checkin_count'] = len(records)
        task_dict['is_active'] = CheckinTask.from_row(task).is_active()
        task_list.append(task_dict)
    
    return render_template('admin/dashboard.html', tasks=task_list)


@app.route('/admin/create_task', methods=['GET', 'POST'])
@admin_required
def create_task():
    """Create checkin task"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        
        if not title or not start_time or not end_time:
            flash('请填写完整信息', 'danger')
            return render_template('admin/create_task.html')
        
        try:
            # Validate datetime format
            datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('时间格式不正确', 'danger')
            return render_template('admin/create_task.html')
        
        # Convert to SQLite datetime format
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        
        if start_time >= end_time:
            flash('结束时间必须晚于开始时间', 'danger')
            return render_template('admin/create_task.html')
        
        # Generate unique code (8 bytes = 16 hex characters for better security)
        code = secrets.token_hex(8).upper()
        
        task_id = create_checkin_task(title, code, start_time, end_time, session['user_id'])
        if task_id:
            flash(f'签到任务创建成功！签到码：{code}', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('创建失败，请重试', 'danger')
    
    return render_template('admin/create_task.html')


@app.route('/admin/view_records/<int:task_id>')
@admin_required
def view_records(task_id):
    """View checkin records for a task"""
    task = get_checkin_task_by_id(task_id)
    if not task:
        flash('签到任务不存在', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    records = get_checkin_records_by_task(task_id)
    students = get_all_students()
    
    # Create a set of checked-in user IDs
    checked_in_ids = {record['user_id'] for record in records}
    
    # Prepare student status list
    student_status = []
    for student in students:
        status = {
            'id': student['id'],
            'username': student['username'],
            'name': student['name'],
            'checked_in': student['id'] in checked_in_ids,
            'checkin_time': None
        }
        
        # Find checkin time if checked in
        for record in records:
            if record['user_id'] == student['id']:
                status['checkin_time'] = record['checkin_time']
                break
        
        student_status.append(status)
    
    return render_template('admin/view_records.html', task=task, records=records, student_status=student_status)


@app.route('/admin/export_records/<int:task_id>')
@admin_required
def export_records(task_id):
    """Export checkin records as CSV"""
    task = get_checkin_task_by_id(task_id)
    if not task:
        return '任务不存在', 404
    
    records = get_checkin_records_by_task(task_id)
    students = get_all_students()
    
    # Create a set of checked-in user IDs
    checked_in_ids = {record['user_id'] for record in records}
    
    # Create a map of user_id to record data
    record_map = {record['user_id']: record for record in records}
    
    # Generate CSV content using csv module for proper escaping
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['学号', '姓名', '签到状态', '签到时间', '座位', '纬度', '经度', '定位精度(米)'])
    
    for student in students:
        status = '已签到' if student['id'] in checked_in_ids else '未签到'
        record = record_map.get(student['id'])
        
        checkin_time = record['checkin_time'] if record else ''
        seat = f"{record['seat_row']}{record['seat_col']}" if record and record['seat_row'] and record['seat_col'] else ''
        latitude = f"{record['latitude']:.6f}" if record and record['latitude'] else ''
        longitude = f"{record['longitude']:.6f}" if record and record['longitude'] else ''
        accuracy = f"{record['location_accuracy']:.0f}" if record and record['location_accuracy'] else ''
        
        writer.writerow([student['username'], student['name'], status, checkin_time, 
                        seat, latitude, longitude, accuracy])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=checkin_{task_id}.csv'}
    )


@app.route('/admin/statistics')
@admin_required
def statistics():
    """Statistics page"""
    student_stats = get_student_attendance_stats()
    task_stats = get_task_attendance_stats()
    overall_stats = get_overall_stats()
    
    return render_template('admin/statistics.html', 
                         student_stats=student_stats,
                         task_stats=task_stats,
                         overall_stats=overall_stats)


@app.route('/admin/import_students', methods=['GET', 'POST'])
@admin_required
def import_students():
    """Import students from CSV file"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('请选择文件', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            flash('请选择文件', 'danger')
            return redirect(request.url)
        
        # Check file extension
        if not file.filename.endswith('.csv'):
            flash('只支持 CSV 格式文件', 'danger')
            return redirect(request.url)
        
        try:
            # Check file size (5MB limit) - read in chunks to avoid memory issues
            max_size = 5 * 1024 * 1024
            file_size = 0
            chunk_size = 4096
            file_content = b''
            
            while True:
                chunk = file.stream.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > max_size:
                    flash('文件大小不能超过 5MB', 'danger')
                    return redirect(request.url)
                file_content += chunk
            
            # Decode CSV file
            stream = io.StringIO(file_content.decode('utf-8-sig'), newline=None)
            csv_reader = csv.reader(stream)
            
            # Skip header row
            header = next(csv_reader, None)
            if not header:
                flash('CSV 文件为空', 'danger')
                return redirect(request.url)
            
            # Parse student data
            users_data = []
            for row in csv_reader:
                if len(row) >= 3:
                    username = row[0].strip()
                    name = row[1].strip()
                    password = row[2].strip()
                    
                    if username and name and password:
                        users_data.append((username, password, name))
            
            if not users_data:
                flash('没有有效的学生数据', 'danger')
                return redirect(request.url)
            
            # Bulk create users
            result = bulk_create_users(users_data)
            
            # Show results
            if result['success_count'] > 0:
                flash(f'成功导入 {result["success_count"]} 个学生', 'success')
            
            if result['skip_count'] > 0:
                flash(f'跳过 {result["skip_count"]} 个已存在的学号', 'warning')
            
            if result['errors']:
                for error in result['errors']:
                    flash(error, 'danger')
            
            return redirect(url_for('import_students'))
            
        except Exception as e:
            flash(f'导入失败：{str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('admin/import_students.html')


@app.route('/admin/download_template')
@admin_required
def download_template():
    """Download CSV template for student import"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['学号', '姓名', '初始密码'])
    writer.writerow(['20210001', '张三', '123456'])
    writer.writerow(['20210002', '李四', '123456'])
    writer.writerow(['20210003', '王五', '123456'])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=student_import_template.csv'}
    )


@app.route('/api/occupied_seats/<int:task_id>')
@login_required
def api_occupied_seats(task_id):
    """API endpoint to get occupied seats for a task"""
    if session.get('role') == 'admin':
        # Admin can see all occupied seats
        occupied = get_occupied_seats(task_id)
    else:
        # Students can only see occupied seats (without names)
        task = get_checkin_task_by_code(request.args.get('code', ''))
        if not task or task['id'] != task_id:
            return jsonify({'error': 'Invalid task'}), 403
        occupied = get_occupied_seats(task_id)
        # Remove names for students (privacy)
        occupied = [{'seat_row': s['seat_row'], 'seat_col': s['seat_col']} for s in occupied]
    
    return jsonify(occupied)


@app.route('/admin/view_seats/<int:task_id>')
@admin_required
def view_seats(task_id):
    """View classroom seat layout for a task"""
    task = get_checkin_task_by_id(task_id)
    if not task:
        flash('签到任务不存在', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    occupied_seats = get_occupied_seats(task_id)
    
    # Create seat grid (6 rows x 8 columns)
    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    cols = list(range(1, 9))
    
    # Create a map of seat position to student info
    seat_map = {}
    for seat in occupied_seats:
        key = f"{seat['seat_row']}{seat['seat_col']}"
        seat_map[key] = {
            'name': seat['name'],
            'username': seat['username']
        }
    
    return render_template('admin/view_seats.html', 
                         task=task, 
                         rows=rows, 
                         cols=cols, 
                         seat_map=seat_map)


if __name__ == '__main__':
    app.run(debug=app.config['FLASK_DEBUG'])
