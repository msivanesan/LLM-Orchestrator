r"""
Mailer Service Manager.

Usage
-----
python .\manage.py runworker    # Run the worker process
python .\manage.py stop         # Stop the worker process
"""
import argparse
import os
import sys
import signal
import subprocess
from dotenv import load_dotenv

# Load .env from root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# PID file for process management
PID_FILE = os.path.join(os.path.dirname(__file__), '..', 'mailer.pid')

def run_worker():
    """Start the background Redis worker process."""
    from main import run_worker as start_worker
    
    # Save current PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
        
    print("🚀 Starting Central Mailer background worker...")
    try:
        start_worker()
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def stop():
    """Stop the running worker using the PID file."""
    if not os.path.exists(PID_FILE):
        print("❌ Mailer Service not running (no PID file).")
        return
        
    with open(PID_FILE) as f:
        try:
            pid = int(f.read().strip())
        except ValueError:
            print("❌ Invalid PID format in file.")
            return

    print(f"🛑 Stopping Mailer Service (PID {pid})...")
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"✅ Successfully stopped Mailer Service.")
    except Exception as e:
        print(f"❌ Failed to stop process: {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mailer Service Management Tool')
    sub = parser.add_subparsers(dest='command', help='Commands')

    sub.add_parser('runworker', help='Start the background Redis worker')
    sub.add_parser('stop', help='Stop the running worker process')

    args = parser.parse_args()

    if args.command == 'runworker':
        run_worker()
    elif args.command == 'stop':
        stop()
    else:
        parser.print_help()
