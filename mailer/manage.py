import argparse
from .main import run_worker

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Central Mailer Service Management')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('run', help='Start the background mail processor')

    args = parser.parse_args()

    if args.command == 'run':
        run_worker()
    else:
        parser.print_help()
