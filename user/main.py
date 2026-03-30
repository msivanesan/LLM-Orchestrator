from flask import Flask, request
from flask_cors import CORS
from .extensions import db, mail, redis_client
from .models import TokenBlocklist
from .routes import user_bp
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
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # Expiry settings from .env
    access_minutes = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 7))
    refresh_days = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30))
    
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=access_minutes)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=refresh_days)
    
    # Mail Config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    db.init_app(app)
    jwt = JWTManager(app)
    mail.init_app(app)
    CORS(app)

    # Token Blocklist Loader
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    # Logging Configuration
    log_file = os.getenv('USER_SERVICE_LOG_FILE', 'logs/user_service.log')
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
    
    # Conditional Formatter for APM (JSON)
    if os.getenv('APM_LOGGING_ENABLED', 'False').lower() == 'true':
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('User Service Startup')
    
    app.register_blueprint(user_bp, url_prefix='/api/users')

    # Global Response Logging (for APM)
    @app.after_request
    def log_response(response):
        log_options = os.getenv('LOG_OPTIONS_REQUESTS', 'False').lower() == 'true'
        if not log_options and request.method == 'OPTIONS':
            return response
            
        app.logger.info(
            f"{request.method} {request.path} - Status: {response.status_code}"
        )
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=os.getenv('USER_SERVICE_PORT', 5001), debug=True)
