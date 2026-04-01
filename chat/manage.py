"""
Chat Service management tool.

Usage
-----
python -m chat.manage init_db      # create DB tables
python -m chat.manage runserver    # start Flask dev server (NOT for prod)
python -m chat.manage runprod      # start production server (Gunicorn)
python -m chat.manage stop         # stop running server via PID file
"""
import argparse
import os
import sys
import signal
import subprocess
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

PID_FILE = os.path.join(os.path.dirname(__file__), '..', 'chat.pid')


def init_db():
    from main import create_app
    from extensions import db
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Chat Service DB tables initialised.")


def run_server():
    from main import create_app
    app  = create_app()
    port = int(os.getenv('CHAT_SERVICE_PORT', 5004))

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    print(f"🚀 Chat Service running on http://0.0.0.0:{port}")
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


def run_prod():
    """Start the service handles production traffic via Gunicorn."""
    port = os.getenv('CHAT_SERVICE_PORT', '5004')
    # Try CHAT-specific count, fall back to global, then default to 2
    workers = int(os.getenv('CHAT_WORKERS', os.getenv('GUNICORN_WORKERS', '2')))
    
    cmd = [
        'gunicorn',
        '--workers', str(workers),
        '--bind', f'0.0.0.0:{port}',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--timeout', '120',
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
        print("❌ Chat Service not running (no PID file).")
        return
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"✅ Stopped Chat Service (PID {pid}).")
    except Exception as e:
        print(f"❌ {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat Service Manager')
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
