from flask import Flask
from routes import ai_bp
import os
import sys
from dotenv import load_dotenv
import logging

load_dotenv()

# Allow importing shared apm module from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def create_app():
    app = Flask(__name__)

    # Register AI Logic
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    # APM
    try:
        from apm import setup_metrics
        setup_metrics(app, service_name='ai')
    except Exception as e:
        logging.getLogger(__name__).warning('APM setup failed: %s', e)

    # Simple Health Check
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "AI Wrapper Healthy"}, 200

    return app
