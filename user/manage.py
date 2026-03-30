import argparse
import os
import sys
from .main import create_app
from .models import db, User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load .env from root folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

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
    print(f"🚀 Starting user microservice on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

def run_worker():
    from .email_worker import run_worker as start_worker
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

    # runworker command
    subparsers.add_parser('runworker', help='Run the background Email Worker')

    args = parser.parse_args()

    if args.command == 'init_db':
        init_db()
    elif args.command == 'createsuperuser':
        create_superuser(args)
    elif args.command == 'runserver':
        run_server()
    elif args.command == 'runworker':
        run_worker()
    else:
        parser.print_help()
