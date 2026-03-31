import argparse
import os
import sys

# Add the parent directory to sys.path to allow imports of 'ai' as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.main import create_app
from dotenv import load_dotenv

# Load .env from root folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def run_server():
    app = create_app()
    port = int(os.getenv('AI_SERVICE_PORT', 5003))
    print(f"🚀 Starting AI Wrapper Microservice on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI Orchestration Service Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # runserver command to match the other services
    subparsers.add_parser('runserver', help='Run the Flask development server')

    args = parser.parse_args()

    if args.command == 'runserver':
        run_server()
    else:
        # Default behavior: if no command is given, show help
        parser.print_help()
