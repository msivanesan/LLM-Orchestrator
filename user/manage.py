"""
User Identity Manager Service.

Usage
-----
python -m user.manage init_db      # create DB tables
python -m user.manage runserver    # start Flask dev server
python -m user.manage runprod      # start production server (Gunicorn)
python -m user.manage stop         # stop running server via PID file
"""
import argparse
import os
import sys
import signal
import subprocess
from main import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load .env from root folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

PID_FILE = os.path.join(os.path.dirname(__file__), '..', 'user.pid')

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables initialized successfully!")

def create_superuser(args):
    app = create_app()
    with app.app_context():
        print("\n--- Create Superuser ---")
        username = args.username or input("Username: ")
        email = args.email or input("Email: ")
        password = args.password or input("Password: ")
        
        if not all([username, email, password]):
            print("❌ All fields are required.")
            return

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists.")
            return

        hashed_pw = generate_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Admin user '{username}' created successfully!")

def run_server():
    app = create_app()
    port = int(os.getenv('USER_SERVICE_PORT', 5001))

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    print(f"🚀 Starting user microservice on port {port}...")
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def run_prod():
    """Start the service handles production traffic via Gunicorn."""
    port = os.getenv('USER_SERVICE_PORT', '5001')
    workers = os.cpu_count() * 2 + 1
    
    cmd = [
        'gunicorn',
        '--workers', str(workers),
        '--bind', f'0.0.0.0:{port}',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--timeout', '60',
        'main:create_app()'
    ]
    
    print(f"🔥 Starting PRODUCTION server (Gunicorn) on port {port} with {workers} workers...")
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("❌ Error: 'gunicorn' not found. Install it with: pip install gunicorn")
    except KeyboardInterrupt:
        print("\n👋 Production server stopped.")

def stop():
    if not os.path.exists(PID_FILE):
        print("❌ User Service not running (no PID file).")
        return
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"✅ Stopped User Service (PID {pid}).")
    except Exception as e:
        print(f"❌ {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def run_worker():
    from email_worker import run_worker as start_worker
    start_worker()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='User Microservice Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # init_db command
    subparsers.add_parser('init_db', help='Initialize the database tables')

    # createsuperuser command
    csp = subparsers.add_parser('createsuperuser', help='Create an admin user interactively')
    csp.add_argument('--username', type=str, help='Admin username')
    csp.add_argument('--email', type=str, help='Admin email')
    csp.add_argument('--password', type=str, help='Admin password')

    # runserver command
    subparsers.add_parser('runserver', help='Run the Flask development server')

    # runprod command
    subparsers.add_parser('runprod', help='Start the production service (Gunicorn)')

    # stop command
    subparsers.add_parser('stop', help='Stop the running service')

    # runworker command
    subparsers.add_parser('runworker', help='Run the background Email Worker')

    args = parser.parse_args()

    if args.command == 'init_db':
        init_db()
    elif args.command == 'createsuperuser':
        create_superuser(args)
    elif args.command == 'runserver':
        run_server()
    elif args.command == 'runprod':
        run_prod()
    elif args.command == 'stop':
        stop()
    elif args.command == 'runworker':
        run_worker()
    else:
        parser.print_help()
