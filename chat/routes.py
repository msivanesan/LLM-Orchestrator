"""
Production Chat Service routes — SQLAlchemy 2.0 compatible.

Auth: JWT Bearer (users only).
- Sessions created LAZILY on first message (POST /api/chat/quick-stream)
- HTTP Streaming via SSE (POST /api/chat/sessions/<id>/stream)
- Auto-title from LLM after first message
- NO ORM objects cross generator boundaries (avoids DetachedInstanceError)
"""
import json
import logging
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, abort, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import update as sa_update
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import ChatSession, ChatMessage
from memory_model import UserMemory
from memory import (
    get_memory_list, upsert_memory, delete_memory, clear_all_memory,
    extract_and_save, build_system_prompt_with_memory,
)
from cache import (
    cache_user_sessions, get_cached_user_sessions, invalidate_user_sessions,
    cache_session_messages, get_cached_session_messages, invalidate_session_messages,
    push_message_to_context, get_context_window, invalidate_context, redis_ping,
)
from vector_store import upsert_message, query_context, delete_session_vectors, chroma_health
from llm_client import (
    chat_completion, chat_completion_stream, generate_title,
    ai_service_health, list_available_models,
)

logger  = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__)

MAX_CTX_MSGS = 20


# ── Helpers ────────────────────────────────────────────────────────────────────

def _uid() -> int:
    return int(get_jwt_identity())


def _session_or_404(session_id: int, user_id: int) -> ChatSession:
    s = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not s:
        abort(404, description='Session not found')
    return s


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _ok(data, code=200):
    return jsonify({'status': 'success', 'data': data}), code


def _err(msg, code=400):
    return jsonify({'status': 'error', 'message': msg}), code


def _touch_session(session_id: int):
    """Update session.updated_at using SQLAlchemy 2.0 Core (safe inside generators)."""
    db.session.execute(
        sa_update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(updated_at=datetime.now(timezone.utc))
    )


def _save_message(session_id: int, role: str, content: str) -> dict:
    """
    Persist a ChatMessage. Returns a plain dict — no ORM object leaked out.
    Serializes to dict BEFORE commit to avoid DetachedInstanceError.
    """
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        tokens=_estimate_tokens(content),
    )
    db.session.add(msg)
    _touch_session(session_id)
    db.session.flush()          # assigns msg.id without detaching
    msg_dict = msg.to_dict()    # serialize while still attached
    db.session.commit()         # now commit (detaches object — but we don't use it after)
    return msg_dict


def _index_safe(user_id: int, msg_id: int, content: str, session_id: int, role: str):
    """Best-effort VectorDB indexing."""
    try:
        upsert_message(user_id, msg_id, content, session_id, role)
    except Exception:
        logger.exception('VectorDB index failed msg=%s', msg_id)


def _build_llm_messages(session_id: int, user_id: int, current_content: str,
                         use_context: bool = True) -> list:
    window = list(get_context_window(session_id))
    if use_context:
        relevant = query_context(user_id, current_content, n_results=5, session_id=session_id)
        existing = {m['content'] for m in window}
        extra    = [{'role': r['role'], 'content': r['content']}
                    for r in relevant if r['content'] not in existing]
        messages = extra + window
    else:
        messages = window
    if not messages or messages[-1].get('content') != current_content:
        messages.append({'role': 'user', 'content': current_content})
    return messages


def _post_send(session_id: int, user_id: int,
               user_msg_id: int, user_content: str,
               ai_msg_id: int, ai_content: str,
               is_first: bool, model: str) -> str:
    """
    Redis + VectorDB bookkeeping + optional auto-title.
    All arguments are primitives — safe to call inside a generator.
    Returns the (possibly updated) session title string.
    """
    push_message_to_context(session_id, 'user',      user_content, MAX_CTX_MSGS)
    push_message_to_context(session_id, 'assistant', ai_content,   MAX_CTX_MSGS)
    invalidate_session_messages(session_id)
    invalidate_user_sessions(user_id)
    _index_safe(user_id, user_msg_id, user_content, session_id, 'user')
    _index_safe(user_id, ai_msg_id,   ai_content,   session_id, 'assistant')

    # ── Memory extraction (best-effort, non-blocking background thread) ──
    try:
        from threading import Thread
        from flask import current_app
        app = current_app._get_current_object()
        
        def run_async_extraction():
            with app.app_context():
                try:
                    extract_and_save(user_id, session_id, user_content, ai_content, model)
                except Exception:
                    logger.debug('Async memory extraction failed')

        Thread(target=run_async_extraction).start()
    except Exception:
        logger.debug('Failed to start memory extraction thread')

    new_title = None
    if is_first:
        try:
            new_title = generate_title(user_content, model)
            db.session.execute(
                sa_update(ChatSession)
                .where(ChatSession.id == session_id)
                .values(title=new_title)
            )
            db.session.commit()
            invalidate_user_sessions(user_id)
        except Exception:
            logger.exception('Auto-title failed for session %s', session_id)
    return new_title


def _system_prompt_for(user_id: int) -> str:
    """Return the base system prompt enriched with the user's persistent memory."""
    from llm_client import SYSTEM_PROMPT
    return build_system_prompt_with_memory(SYSTEM_PROMPT, user_id)


@chat_bp.get('/memory')
@jwt_required()
def list_memory():
    return _ok(get_memory_list(_uid()))


@chat_bp.put('/memory/<string:key>')
@jwt_required()
def set_memory(key):
    user_id = _uid()
    body    = request.get_json(silent=True) or {}
    value   = (body.get('value') or '').strip()
    if not value:
        return _err("'value' is required")
    return _ok(upsert_memory(user_id, key, value))


@chat_bp.delete('/memory/<string:key>')
@jwt_required()
def remove_memory(key):
    if delete_memory(_uid(), key):
        return _ok({'deleted': True, 'key': key})
    return _err('Key not found', 404)


@chat_bp.delete('/memory')
@jwt_required()
def clear_memory():
    count = clear_all_memory(_uid())
    return _ok({'cleared': count})



# ── Health ─────────────────────────────────────────────────────────────────────

@chat_bp.get('/health')
def health():
    return _ok({
        'service':  'chat',
        'redis':    'connected' if redis_ping()         else 'unavailable',
        'chromadb': 'connected' if chroma_health()     else 'unavailable',
        'ai':       'connected' if ai_service_health() else 'unavailable',
    })


@chat_bp.get('/models')
@jwt_required()
def get_models():
    return _ok(list_available_models())


# ── Sessions CRUD ──────────────────────────────────────────────────────────────

@chat_bp.get('/sessions')
@jwt_required()
def list_sessions():
    user_id  = _uid()
    archived = request.args.get('archived', 'false').lower() == 'true'
    if not archived:
        cached = get_cached_user_sessions(user_id)
        if cached is not None:
            return _ok(cached)
    sessions = (ChatSession.query
                .filter_by(user_id=user_id, is_archived=archived)
                .order_by(ChatSession.updated_at.desc()).all())
    data = [s.to_dict() for s in sessions]
    if not archived:
        cache_user_sessions(user_id, data)
    return _ok(data)


@chat_bp.post('/sessions')
@jwt_required()
def create_session():
    user_id = _uid()
    body    = request.get_json(silent=True) or {}
    model   = (body.get('model') or '').strip()
    if not model:
        return _err("'model' is required")
    session = ChatSession(
        user_id=user_id,
        title=(body.get('title') or 'New Chat').strip()[:255],
        model=model,
    )
    try:
        db.session.add(session)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _err('Database error', 500)
    invalidate_user_sessions(user_id)
    return _ok(session.to_dict(), 201)


@chat_bp.get('/sessions/<int:session_id>')
@jwt_required()
def get_session(session_id):
    return _ok(_session_or_404(session_id, _uid()).to_dict(include_messages=True))


@chat_bp.patch('/sessions/<int:session_id>')
@jwt_required()
def update_session(session_id):
    user_id = _uid()
    session = _session_or_404(session_id, user_id)
    body    = request.get_json(silent=True) or {}
    if 'title'       in body: session.title       = (body['title'] or 'New Chat').strip()[:255]
    if 'model'       in body: session.model       = body['model'].strip()
    if 'is_archived' in body: session.is_archived = bool(body['is_archived'])
    session.updated_at = datetime.now(timezone.utc)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _err('Database error', 500)
    invalidate_user_sessions(user_id)
    invalidate_session_messages(session_id)
    return _ok(session.to_dict())


@chat_bp.delete('/sessions/<int:session_id>')
@jwt_required()
def delete_session(session_id):
    user_id = _uid()
    session = _session_or_404(session_id, user_id)
    try:
        db.session.delete(session)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _err('Database error', 500)
    invalidate_user_sessions(user_id)
    invalidate_session_messages(session_id)
    invalidate_context(session_id)
    delete_session_vectors(user_id, session_id)
    return _ok({'deleted': True, 'session_id': session_id})


# ── Messages ───────────────────────────────────────────────────────────────────

@chat_bp.get('/sessions/<int:session_id>/messages')
@jwt_required()
def list_messages(session_id):
    user_id = _uid()
    _session_or_404(session_id, user_id)
    cached = get_cached_session_messages(session_id)
    if cached is not None:
        return _ok(cached)
    msgs = (ChatMessage.query.filter_by(session_id=session_id)
            .order_by(ChatMessage.created_at.asc()).all())
    data = [m.to_dict() for m in msgs]
    cache_session_messages(session_id, data)
    return _ok(data)


@chat_bp.delete('/sessions/<int:session_id>/messages')
@jwt_required()
def clear_messages(session_id):
    user_id = _uid()
    _session_or_404(session_id, user_id)
    try:
        ChatMessage.query.filter_by(session_id=session_id).delete()
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _err('Database error', 500)
    invalidate_session_messages(session_id)
    invalidate_context(session_id)
    delete_session_vectors(user_id, session_id)
    return _ok({'cleared': True, 'session_id': session_id})


@chat_bp.patch('/sessions/<int:session_id>/messages/<int:message_id>/pin')
@jwt_required()
def toggle_pin(session_id, message_id):
    user_id = _uid()
    _session_or_404(session_id, user_id)
    msg = ChatMessage.query.filter_by(id=message_id, session_id=session_id).first()
    if not msg:
        return _err('Message not found', 404)
    msg.is_pinned = not msg.is_pinned
    db.session.commit()
    return _ok(msg.to_dict())


# ── QUICK STREAM — lazy session + streaming in one request ─────────────────────

@chat_bp.post('/quick-stream')
@jwt_required()
def quick_stream():
    """
    Create session + stream AI reply in one call.
    SSE: session → token* → done
    """
    user_id = _uid()
    body    = request.get_json(silent=True) or {}
    content = (body.get('content') or '').strip()
    model   = (body.get('model') or '').strip()

    if not content:
        return _err("'content' is required")
    if not model:
        return _err("'model' is required")

    try:
        # ── Create session ────────────────────────────────────────────────────
        new_session = ChatSession(user_id=user_id, title='New Chat', model=model)
        db.session.add(new_session)
        db.session.commit()
        session_id = new_session.id

        # ── Persist user message ──────────────────────────────────────────────
        user_msg_dict = _save_message(session_id, 'user', content)
        user_msg_id   = user_msg_dict['id']

    except Exception as e:
        db.session.rollback()
        logger.exception('quick-stream setup failed')
        return _err(f'Setup error: {str(e)}', 500)

    # Build memory-enriched system prompt BEFORE generator (safe — no ORM inside gen)
    sys_prompt = _system_prompt_for(user_id)

    # ── Stream generator (only primitives — no ORM objects) ──────────────────
    def generate():
        yield f'data: {json.dumps({"type":"session","session_id":session_id,"title":"New Chat","user_message":user_msg_dict})}\n\n'

        full_content = []
        client_disconnected = False

        try:
            for raw_line in chat_completion_stream(
                messages=[{'role': 'user', 'content': content}],
                model=model, temperature=0.7, max_tokens=1024,
                system_prompt=sys_prompt,
            ):
                stripped = raw_line.strip()
                if not stripped.startswith('data:'):
                    continue
                data_str = stripped[5:].strip()
                if data_str == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_str)
                    if 'error' in chunk:
                        if not client_disconnected:
                            yield f'data: {json.dumps({"type":"error","message":chunk["error"]})}\n\n'
                        break
                        
                    text  = chunk['choices'][0]['delta'].get('content', '')
                    if text:
                        full_content.append(text)
                        if not client_disconnected:
                            try:
                                yield f'data: {json.dumps({"type":"token","text":text})}\n\n'
                            except (GeneratorExit, ConnectionResetError):
                                client_disconnected = True
                                logger.info(f"Client disconnected during quick-stream session {session_id}")
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
        finally:
            ai_text = ''.join(full_content) or '(no response)'

            # Persist AI reply (even if client is gone)
            try:
                ai_msg_dict = _save_message(session_id, 'assistant', ai_text)
                ai_msg_id   = ai_msg_dict['id']
                
                # Bookkeeping + auto-title
                new_title = _post_send(
                    session_id, user_id,
                    user_msg_id, content,
                    ai_msg_id,   ai_text,
                    is_first=True, model=model,
                )

                if not client_disconnected:
                    final_title = new_title or 'New Chat'
                    done_payload = {
                        'type': 'done',
                        'session_id': session_id,
                        'title': final_title,
                        'assistant_message': dict(ai_msg_dict) if ai_msg_dict else {},
                    }
                    yield f'data: {json.dumps(done_payload)}\n\n'
            except Exception:
                logger.exception('Failed to finalize AI reply in background')
                if not client_disconnected:
                    yield f'data: {json.dumps({"type":"error","message":"Failed to save reply"})}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


# ── STREAM — existing session ──────────────────────────────────────────────────

@chat_bp.post('/sessions/<int:session_id>/stream')
@jwt_required()
def stream_message(session_id):
    """
    Stream AI response for an existing session.
    SSE: session → token* → done
    """
    user_id = _uid()
    session = _session_or_404(session_id, user_id)

    body        = request.get_json(silent=True) or {}
    content     = (body.get('content') or '').strip()
    # Use explicit model, then session-stored model, then fail
    model       = (body.get('model') or session.model or '').strip()
    
    if not content:
        return _err("'content' is required")
    if not model:
        return _err("'model' is required")

    temperature = float(body.get('temperature', 0.7))
    max_tokens  = int(body.get('max_tokens', 1024))
    use_context = bool(body.get('use_context', True))
    session_title = session.title   # snapshot — don't touch ORM later

    is_first = ChatMessage.query.filter_by(session_id=session_id).count() == 0

    # Persist user message synchronously
    try:
        user_msg_dict = _save_message(session_id, 'user', content)
        user_msg_id   = user_msg_dict['id']
    except SQLAlchemyError:
        db.session.rollback()
        return _err('Database error', 500)

    # Build LLM context and memory-enriched system prompt before generator
    llm_messages = _build_llm_messages(session_id, user_id, content, use_context)
    sys_prompt   = _system_prompt_for(user_id)

    def generate():
        yield f'data: {json.dumps({"type":"session","session_id":session_id,"title":session_title,"user_message":user_msg_dict})}\n\n'

        full_content = []
        client_disconnected = False

        try:
            for raw_line in chat_completion_stream(
                messages=llm_messages, model=model,
                temperature=temperature, max_tokens=max_tokens,
                system_prompt=sys_prompt,
            ):
                stripped = raw_line.strip()
                if not stripped.startswith('data:'):
                    continue
                data_str = stripped[5:].strip()
                if data_str == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_str)
                    if 'error' in chunk:
                        if not client_disconnected:
                            yield f'data: {json.dumps({"type":"error","message":chunk["error"]})}\n\n'
                        break

                    text  = chunk['choices'][0]['delta'].get('content', '')
                    if text:
                        full_content.append(text)
                        if not client_disconnected:
                            try:
                                yield f'data: {json.dumps({"type":"token","text":text})}\n\n'
                            except (GeneratorExit, ConnectionResetError):
                                client_disconnected = True
                                logger.info(f"Client disconnected during stream session {session_id}")
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
        finally:
            ai_text = ''.join(full_content) or '(no response)'

            # Persist AI reply (even if client is gone)
            try:
                ai_msg_dict = _save_message(session_id, 'assistant', ai_text)
                ai_msg_id   = ai_msg_dict['id']

                # Bookkeeping + auto-title
                new_title = _post_send(
                    session_id, user_id,
                    user_msg_id, content,
                    ai_msg_id,   ai_text,
                    is_first=is_first, model=model,
                )

                if not client_disconnected:
                    final_title = new_title or session_title
                    done_payload = {
                        'type': 'done',
                        'session_id': session_id,
                        'title': final_title,
                        'user_message': dict(user_msg_dict) if user_msg_dict else {},
                        'assistant_message': dict(ai_msg_dict) if ai_msg_dict else {},
                    }
                    yield f'data: {json.dumps(done_payload)}\n\n'
            except Exception:
                logger.exception('Failed to finalize AI reply in background')
                if not client_disconnected:
                    yield f'data: {json.dumps({"type":"error","message":"Failed to save reply"})}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


# ── Context ────────────────────────────────────────────────────────────────────

@chat_bp.get('/sessions/<int:session_id>/context')
@jwt_required()
def get_semantic_context(session_id):
    user_id = _uid()
    _session_or_404(session_id, user_id)
    q = request.args.get('q', '').strip()
    n = min(int(request.args.get('n', 8)), 20)
    if not q:
        return _err("Query param 'q' is required")
    return _ok({'query': q,
                'results': query_context(user_id, q, n_results=n, session_id=session_id)})


@chat_bp.get('/sessions/<int:session_id>/context/window')
@jwt_required()
def get_rolling_window(session_id):
    user_id = _uid()
    _session_or_404(session_id, user_id)
    return _ok({'session_id': session_id, 'window': get_context_window(session_id)})
