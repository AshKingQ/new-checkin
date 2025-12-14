#!/usr/bin/env python3
"""
Simple script to initialize and run the Student Check-in System.
"""
import os
import sys

def main():
    """Initialize database and run the Flask application."""
    # Check if database exists, if not initialize it
    if not os.path.exists('checkin_system.db'):
        print("Database not found. Initializing...")
        from database import init_database
        init_database()
        print("Database initialized successfully!\n")
    
    print("Starting Student Check-in System...")
    print("=" * 60)
    print("Default Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin")
    print("=" * 60)
    print("\nAccess the system at: http://localhost:5000")
    print("Press Ctrl+C to stop the server.\n")
    
    # Import and run the app
    from app import app
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    if debug_mode:
        print("⚠️  Running in DEBUG mode (for development only)")
        print("   Set FLASK_DEBUG=False for production\n")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit(0)
