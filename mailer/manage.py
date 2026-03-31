import argparse
import os
import signal
import sys
from .main import run_worker

PID_FILE = "mailer.pid"

def start():
    # Save PID
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    try:
        run_worker()
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def stop():
    if not os.path.exists(PID_FILE):
        print("❌ Mailer is not running (no PID file found).")
        return

    with open(PID_FILE, "r") as f:
        try:
            pid = int(f.read().strip())
        except ValueError:
            print("❌ Invalid PID in file.")
            return

    try:
        if os.name == 'nt':
            # Windows
            import ctypes
            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
        else:
            # POSIX
            os.kill(pid, signal.SIGTERM)
        
        print(f"🛑 Mailer service (PID {pid}) stopped.")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except ProcessLookupError:
        print("❌ Process already dead.")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception as e:
        print(f"❌ Failed to stop: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Central Mailer Service Management')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('runserver', help='Start the background mail processor')
    subparsers.add_parser('stop', help='Stop the background mail processor')

    args = parser.parse_args()

    if args.command == 'runserver':
        start()
    elif args.command == 'stop':
        stop()
    else:
        parser.print_help()
