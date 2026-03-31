from flask import Flask
from .routes import ai_bp
import os
from dotenv import load_dotenv
import logging

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Initialize Core Security
    # (Note: CORS is handled by Nginx Gateway)
    
    # Register AI Logic
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # Simple Health Check
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "AI Wrapper Healthy"}, 200

    return app
