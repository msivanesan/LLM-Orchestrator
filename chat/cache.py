"""
Redis cache helpers for the Chat service.

Key schema
----------
chat:session:{session_id}:messages   → JSON list of last N messages  (TTL 30 min)
chat:user:{user_id}:sessions         → JSON list of session summaries (TTL 10 min)
chat:lock:{session_id}               → Simple mutex while writing     (TTL 5 s)
chat:ctx:{session_id}                → Rolling context window list    (TTL 30 min)
"""
import json
import logging
from typing import List, Dict, Optional

from extensions import redis_client

logger = logging.getLogger(__name__)

# TTLs (seconds)
TTL_MESSAGES = 1800   # 30 min
TTL_SESSIONS = 600    # 10 min
TTL_LOCK     = 5

# Context window limits
MAX_CTX_MSGS        = 20    # max number of messages kept in the rolling window
MAX_CTX_TOKENS      = 3000  # soft token budget for the context sent to LLM
AVERAGE_TOKENS_PER_CHAR = 0.25  # ~4 chars per token


# ---------------------------------------------------------------------------
# Session list cache
# ---------------------------------------------------------------------------

def cache_user_sessions(user_id: int, sessions: List[Dict]) -> None:
    key = f"chat:user:{user_id}:sessions"
    try:
        redis_client.setex(key, TTL_SESSIONS, json.dumps(sessions))
    except Exception:
        logger.warning("Redis: failed to cache sessions for user %s", user_id)


def get_cached_user_sessions(user_id: int) -> Optional[List[Dict]]:
    key = f"chat:user:{user_id}:sessions"
    try:
        raw = redis_client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        logger.warning("Redis: failed to read sessions for user %s", user_id)
        return None


def invalidate_user_sessions(user_id: int) -> None:
    try:
        redis_client.delete(f"chat:user:{user_id}:sessions")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Message list cache (per session)
# ---------------------------------------------------------------------------

def cache_session_messages(session_id: int, messages: List[Dict]) -> None:
    key = f"chat:session:{session_id}:messages"
    try:
        redis_client.setex(key, TTL_MESSAGES, json.dumps(messages))
    except Exception:
        logger.warning("Redis: failed to cache messages for session %s", session_id)


def get_cached_session_messages(session_id: int) -> Optional[List[Dict]]:
    key = f"chat:session:{session_id}:messages"
    try:
        raw = redis_client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        logger.warning("Redis: failed to read messages for session %s", session_id)
        return None


def invalidate_session_messages(session_id: int) -> None:
    try:
        redis_client.delete(f"chat:session:{session_id}:messages")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Context window cache (last K messages for AI prompt building)
# ---------------------------------------------------------------------------

def push_message_to_context(session_id: int, role: str,
                            content: str, max_window: int = MAX_CTX_MSGS) -> None:
    """
    Maintain a rolling FIFO list of the last `max_window` messages
    in Redis for quick context assembly (no DB hit on every AI call).
    """
    key = f"chat:ctx:{session_id}"
    try:
        msg = json.dumps({"role": role, "content": content})
        redis_client.rpush(key, msg)
        redis_client.ltrim(key, -max_window, -1)
        redis_client.expire(key, TTL_MESSAGES)
    except Exception:
        logger.warning("Redis: failed to push context for session %s", session_id)


def get_context_window(session_id: int) -> List[Dict]:
    """Return the rolling context list for a session."""
    key = f"chat:ctx:{session_id}"
    try:
        items = redis_client.lrange(key, 0, -1)
        return [json.loads(i) for i in items]
    except Exception:
        logger.warning("Redis: failed to get context for session %s", session_id)
        return []


def is_context_warm(session_id: int) -> bool:
    """Return True if the Redis context window has been populated."""
    key = f"chat:ctx:{session_id}"
    try:
        return redis_client.llen(key) > 0
    except Exception:
        return False


def warm_context_from_db(session_id: int, db_messages: List[Dict]) -> None:
    """
    Seed the Redis context window from database messages.
    Called when the context window is cold (e.g. after server restart or TTL expiry).
    Only loads the last MAX_CTX_MSGS messages to keep the window bounded.
    """
    key = f"chat:ctx:{session_id}"
    try:
        # Take only the most recent messages up to the max window size
        recent = db_messages[-MAX_CTX_MSGS:] if len(db_messages) > MAX_CTX_MSGS else db_messages
        pipe = redis_client.pipeline()
        pipe.delete(key)
        for msg in recent:
            role    = msg.get('role', 'user')
            content = msg.get('content', '')
            pipe.rpush(key, json.dumps({"role": role, "content": content}))
        pipe.expire(key, TTL_MESSAGES)
        pipe.execute()
        logger.info("Context warmed from DB for session %s (%d messages)", session_id, len(recent))
    except Exception:
        logger.warning("Redis: failed to warm context for session %s", session_id)


def trim_messages_to_token_budget(messages: List[Dict],
                                   budget: int = MAX_CTX_TOKENS) -> List[Dict]:
    """
    Trim a message list from the FRONT (oldest) until it fits within
    the token budget. Always keeps at least the last message.
    """
    def estimate(msgs):
        return int(sum(len(m.get('content', '')) * AVERAGE_TOKENS_PER_CHAR for m in msgs))

    if estimate(messages) <= budget:
        return messages

    # Drop from front until we fit; always keep at least 1 message
    trimmed = list(messages)
    while len(trimmed) > 1 and estimate(trimmed) > budget:
        trimmed.pop(0)

    logger.debug("Context trimmed to %d messages to fit token budget %d", len(trimmed), budget)
    return trimmed


def invalidate_context(session_id: int) -> None:
    try:
        redis_client.delete(f"chat:ctx:{session_id}")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Redis health check
# ---------------------------------------------------------------------------

def redis_ping() -> bool:
    try:
        return redis_client.ping()
    except Exception:
        return False
