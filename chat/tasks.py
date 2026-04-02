import logging
from extensions import huey, db
from flask import Flask
import os

logger = logging.getLogger(__name__)

def create_worker_app():
    """Lightweight app initialization for the worker process."""
    app = Flask(__name__)
    # Support both naming conventions for safety
    db_url = os.getenv('DATABASE_URL') or os.getenv('CHAT_DATABASE_URL')
    if not db_url:
        # Fallback for local development if not in Docker
        db_url = "postgresql://postgres:postgres123@localhost:5432/llm_orchestrator"
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

worker_app = create_worker_app()

@huey.task()
def bg_process_chat_message(user_id, session_id, user_msg_id, user_content, 
                           ai_msg_id, ai_content, model_id):
    """
    Persistent background worker for:
    1. Fact extraction (Memory Layer 4)
    2. Vector Indexing (Layer 3)
    3. Session Summarization (Layer 3.5)
    """
    with worker_app.app_context():
        try:
            from memory import extract_and_save, summarize_session
            from vector_store import upsert_message
            from models import ChatMessage

            # ── 1. Vector Indexing (ChromaDB) ──
            upsert_message(user_id, user_msg_id, user_content, session_id, 'user')
            upsert_message(user_id, ai_msg_id,   ai_content,   session_id, 'assistant')

            # ── 2. Fact Extraction ──
            extract_and_save(user_id, session_id, user_content, ai_content, model_id)

            # ── 3. Periodic Summarization (every 10 msgs) ──
            msg_count = ChatMessage.query.filter_by(session_id=session_id).count()
            if msg_count > 0 and msg_count % 10 == 0:
                summarize_session(session_id, model_id)

            logger.info("BG task finished for user %s session %s", user_id, session_id)
        except Exception:
            logger.exception("Persistent BG task failed")
