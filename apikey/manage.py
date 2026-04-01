"""
APIKey Service management tool.

Usage
-----
python -m apikey.manage init_db      # create DB tables
python -m apikey.manage runserver    # start Flask dev server
python -m apikey.manage runprod      # start production server (Gunicorn)
python -m apikey.manage stop         # stop running server via PID file
"""
import argparse
import os
import sys
import signal
import subprocess
from dotenv import load_dotenv
from main import create_app
from models import db

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

PID_FILE = os.path.join(os.path.dirname(__file__), '..', 'apikey.pid')


def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ APIKey Service DB tables initialised.")


def run_server():
    app  = create_app()
    port = int(os.getenv('APIKEY_SERVICE_PORT', 5002))

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    print(f"🚀 Starting APIKey microservice on port {port}...")
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


def run_prod():
    """Start the service handles production traffic via Gunicorn."""
    port = os.getenv('APIKEY_SERVICE_PORT', '5002')
    # Try APIKEY-specific count, fall back to global, then default to 2
    workers = int(os.getenv('APIKEY_WORKERS', os.getenv('GUNICORN_WORKERS', '2')))
    
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
        print("❌ APIKey Service not running (no PID file).")
        return
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"✅ Stopped APIKey Service (PID {pid}).")
    except Exception as e:
        print(f"❌ {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='APIKey Service Manager')
    sub    = parser.add_subparsers(dest='cmd')

    sub.add_parser('init_db',   help='Create database tables')
    sub.add_parser('runserver', help='Start the dev service')
    sub.add_parser('runprod',   help='Start the production service (Gunicorn)')
    sub.add_parser('stop',      help='Stop the running service')

    args = parser.parse_args()

    if args.cmd == 'init_db':
        init_db()
    elif args.cmd == 'runserver':
        run_server()
    elif args.cmd == 'runprod':
        run_prod()
    elif args.cmd == 'stop':
        stop()
    else:
        parser.print_help()
