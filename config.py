import os

import secrets as secrets_module

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets_module.token_hex(32)
    DATABASE = 'checkin.db'
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
