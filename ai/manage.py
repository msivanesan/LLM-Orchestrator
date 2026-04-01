"""
AI Orchestration Service.

Usage
-----
python -m ai.manage runserver    # start Flask dev server
python -m ai.manage runprod      # start production server (Gunicorn)
python -m ai.manage stop         # stop running server via PID file
"""
import argparse
import os
import sys
import signal
import subprocess
from main import create_app
from dotenv import load_dotenv

# Load .env from root folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

PID_FILE = os.path.join(os.path.dirname(__file__), '..', 'ai.pid')


def run_server():
    app  = create_app()
    port = int(os.getenv('AI_SERVICE_PORT', 5003))

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    print(f"🚀 Starting AI Wrapper Microservice on port {port}...")
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


def run_prod():
    """Start the service handles production traffic via Gunicorn."""
    port = os.getenv('AI_SERVICE_PORT', '5003')
    workers = os.cpu_count() * 2 + 1
    
    cmd = [
        'gunicorn',
        '--workers', str(workers),
        '--bind', f'0.0.0.0:{port}',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--timeout', '300',
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
        print("❌ AI Service not running (no PID file).")
        return
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"✅ Stopped AI Service (PID {pid}).")
    except Exception as e:
        print(f"❌ {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI Orchestration Service Manager')
    sub    = parser.add_subparsers(dest='command')

    sub.add_parser('runserver', help='Start the dev service')
    sub.add_parser('runprod',   help='Start the production service (Gunicorn)')
    sub.add_parser('stop',      help='Stop the running service')

    args = parser.parse_args()

    if args.command == 'runserver':
        run_server()
    elif args.command == 'runprod':
        run_prod()
    elif args.command == 'stop':
        stop()
    else:
        parser.print_help()
