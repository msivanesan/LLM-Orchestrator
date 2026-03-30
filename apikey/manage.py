import argparse
import sys
import os
from .main import create_app
from .models import db

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ APIKey Database tables initialized successfully!")

def run_server():
    app = create_app()
    port = int(os.getenv('APIKEY_SERVICE_PORT', 5002))
    print(f"🚀 Starting APIKey microservice on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='APIKey Service Management Script')
    subparsers = parser.add_subparsers(dest='command')

    # init_db command
    subparsers.add_parser('init_db', help='Initialize the database tables')

    # runserver command
    subparsers.add_parser('runserver', help='Run the Flask development server')

    args = parser.parse_args()

    if args.command == 'init_db':
        init_db()
    elif args.command == 'runserver':
        run_server()
    else:
        parser.print_help()
