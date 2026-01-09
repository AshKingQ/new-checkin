from datetime import datetime


class User:
    """User model"""
    def __init__(self, id, username, password, name, role, created_at):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def from_row(row):
        """Create User object from database row"""
        if row is None:
            return None
        return User(
            row['id'],
            row['username'],
            row['password'],
            row['name'],
            row['role'],
            row['created_at']
        )
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'


class CheckinTask:
    """Checkin task model"""
    def __init__(self, id, title, code, start_time, end_time, created_by, created_at):
        self.id = id
        self.title = title
        self.code = code
        self.start_time = start_time
        self.end_time = end_time
        self.created_by = created_by
        self.created_at = created_at
    
    @staticmethod
    def from_row(row):
        """Create CheckinTask object from database row"""
        if row is None:
            return None
        return CheckinTask(
            row['id'],
            row['title'],
            row['code'],
            row['start_time'],
            row['end_time'],
            row['created_by'],
            row['created_at']
        )
    
    def is_active(self):
        """Check if task is currently active"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.start_time <= now <= self.end_time


class CheckinRecord:
    """Checkin record model"""
    def __init__(self, id, task_id, user_id, checkin_time, 
                 latitude=None, longitude=None, location_accuracy=None, 
                 location_time=None, seat_row=None, seat_col=None):
        self.id = id
        self.task_id = task_id
        self.user_id = user_id
        self.checkin_time = checkin_time
        self.latitude = latitude
        self.longitude = longitude
        self.location_accuracy = location_accuracy
        self.location_time = location_time
        self.seat_row = seat_row
        self.seat_col = seat_col
    
    @staticmethod
    def from_row(row):
        """Create CheckinRecord object from database row"""
        if row is None:
            return None
        return CheckinRecord(
            row['id'],
            row['task_id'],
            row['user_id'],
            row['checkin_time'],
            row.get('latitude'),
            row.get('longitude'),
            row.get('location_accuracy'),
            row.get('location_time'),
            row.get('seat_row'),
            row.get('seat_col')
        )
    
    def get_seat_label(self):
        """Get formatted seat label (e.g., 'A1')"""
        if self.seat_row and self.seat_col:
            return f"{self.seat_row}{self.seat_col}"
        return None
    
    def has_location(self):
        """Check if record has location data"""
        return self.latitude is not None and self.longitude is not None
