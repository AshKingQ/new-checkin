# Student Check-in System

A complete web-based student attendance system built with Python 3.8, Flask, SQLite, and a modern web frontend.

## Features

### Administrator (Teacher)
- **Default Account:** Username: `admin`, Password: `admin`
- Login to the system
- Create check-in sessions with custom titles and duration
- Generate dynamic check-in codes automatically
- Set valid time ranges for check-in
- View check-in records (who checked in, who missed)
- Real-time session status monitoring

### Student
- Register with Name, Student ID, Username, and Password
- Login to student dashboard
- Check in using dynamic codes within the specified time window
- View personal check-in history
- Real-time feedback on check-in status

## Technical Stack

- **Backend:** Python 3.8+ with Flask framework
- **Database:** SQLite (auto-initialized)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Authentication:** Session-based with bcrypt password hashing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AshKingQ/new-checkin.git
cd new-checkin
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python database.py
```

4. Run the application:
```bash
# For development (debug mode enabled)
python app.py

# For production (disable debug mode)
export FLASK_DEBUG=False
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

**Note:** For production deployment, use a WSGI server like Gunicorn or uWSGI instead of the Flask development server, and ensure `FLASK_DEBUG=False` is set.

## Usage

### For Administrators

1. Navigate to the home page and click "Admin Login"
2. Login with:
   - Username: `admin`
   - Password: `admin`
3. Create a new check-in session:
   - Enter a session title (e.g., "Monday Morning Class")
   - Set the duration in minutes
   - Click "Create Session"
4. Share the generated check-in code with students
5. Click "View Records" on any session to see who checked in and who missed

### For Students

1. Navigate to the home page and click "Register" (first time only)
2. Fill in your details:
   - Full Name
   - Student ID
   - Username
   - Password
3. Login with your credentials
4. Enter the check-in code provided by your teacher
5. Click "Check In" to mark your attendance
6. View your check-in history on the dashboard

## Project Structure

```
new-checkin/
├── app.py                  # Main Flask application
├── database.py             # Database initialization and helpers
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── student_login.html
│   ├── student_register.html
│   └── student_dashboard.html
└── static/                 # Static assets
    └── css/
        └── style.css       # Stylesheet
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password (bcrypt)
- `role`: 'admin' or 'student'
- `name`: Full name
- `student_id`: Student ID (for students only)
- `created_at`: Registration timestamp

### Sessions Table
- `id`: Primary key
- `title`: Session title
- `checkin_code`: Unique dynamic code
- `start_time`: Session start time
- `end_time`: Session end time
- `created_by`: Admin user ID
- `created_at`: Creation timestamp

### Records Table
- `id`: Primary key
- `session_id`: Reference to session
- `user_id`: Reference to student
- `checkin_time`: Check-in timestamp
- Unique constraint on (session_id, user_id)

## Security Features

- Password hashing using bcrypt with automatic salting
- Session-based authentication
- Role-based access control
- Input validation on all forms
- SQL injection prevention using parameterized queries

## API Endpoints

### Authentication
- `POST /api/login` - Login (admin/student)
- `POST /api/register` - Student registration
- `POST /api/logout` - Logout

### Admin Endpoints
- `GET /api/admin/sessions` - Get all sessions
- `POST /api/admin/sessions` - Create new session
- `GET /api/admin/sessions/<id>/records` - Get session records

### Student Endpoints
- `POST /api/student/checkin` - Check in with code
- `GET /api/student/history` - Get check-in history

## License

MIT License