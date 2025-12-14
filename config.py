import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE = 'checkin.db'
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
