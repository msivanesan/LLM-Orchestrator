from flask import Flask, request
from flask_cors import CORS
from .models import db, ApiKey
from .routes import apikey_bp
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    # Each service can have its own database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('APIKEY_DATABASE_URL', 'sqlite:///d:/llm_project/apikey.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # Expiry settings from .env (shared keys)
    access_minutes = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 7))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=access_minutes)
    
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)

    # Logging Configuration
    log_file = os.getenv('APIKEY_SERVICE_LOG_FILE', 'logs/apikey_service.log')
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
    if os.getenv('APM_LOGGING_ENABLED', 'False').lower() == 'true':
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('APIKey Service Startup')

    app.register_blueprint(apikey_bp, url_prefix='/api/apikeys')

    @app.after_request
    def log_response(response):
        log_options = os.getenv('LOG_OPTIONS_REQUESTS', 'False').lower() == 'true'
        if not log_options and request.method == 'OPTIONS':
            return response
        app.logger.info(f"{request.method} {request.path} - Status: {response.status_code}")
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=os.getenv('APIKEY_SERVICE_PORT', 5002), debug=True)
