"""
Chat microservice application factory.
"""
import os
import sys
import logging
import logging.config
from flask import Flask, jsonify
from dotenv import load_dotenv

# Allow importing the shared apm module from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Configuration ────────────────────────────────────────────────────────
    app.config.update(
        # Database
        SQLALCHEMY_DATABASE_URI=os.getenv(
            'CHAT_DATABASE_URL', 'sqlite:///chat.db'
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_pre_ping": True,
            "connect_args": {"check_same_thread": False},  # SQLite
        },

        # JWT (shared secret with user service)
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'change-me-in-production'),
        JWT_TOKEN_LOCATION=['headers'],
        JWT_HEADER_NAME='Authorization',
        JWT_HEADER_TYPE='Bearer',

        # Flask-Caching → Redis
        CACHE_TYPE='RedisCache',
        CACHE_REDIS_URL=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        CACHE_DEFAULT_TIMEOUT=300,

        # General
        SECRET_KEY=os.getenv('SECRET_KEY', 'flask-secret'),
        JSON_SORT_KEYS=False,
    )

    # ── Extensions ───────────────────────────────────────────────────────────
    from extensions import db, jwt, cache
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)

    # ── Logging ──────────────────────────────────────────────────────────────
    _configure_logging(app)

    # ── Blueprints ───────────────────────────────────────────────────────────
    from routes import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    # ── Create DB tables ─────────────────────────────────────────────────────
    import models, memory_model   # ensure all models are registered
    with app.app_context():
        db.create_all()

    # ── APM ───────────────────────────────────────────────────────────────
    try:
        from apm import setup_metrics
        setup_metrics(app, service_name='chat')
    except Exception as e:
        logging.getLogger(__name__).warning('APM setup failed: %s', e)

    # ── JWT error handlers ───────────────────────────────────────────────────
    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"status": "error", "message": "Token missing"}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"status": "error", "message": "Invalid token"}), 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({"status": "error", "message": "Token expired"}), 401

    # ── Generic error handlers ───────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": str(e)}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app


def _configure_logging(app: Flask):
    log_dir  = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": os.path.join(log_dir, "chat_service.log"),
                "maxBytes": 5_000_000,
                "backupCount": 3,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
        },
    })
