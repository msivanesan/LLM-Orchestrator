"""
Memory extractor — automatically pulls facts from conversations and stores them.
Also provides helpers to load memory and inject it into the system prompt.
"""
import os
import json
import logging
from typing import Dict, List, Optional

from extensions import db
from memory_model import UserMemory

logger = logging.getLogger(__name__)

# Keys the extractor looks for — add more as needed
MEMORY_SCHEMA = {
    "name":         "The user's name or nickname",
    "profession":   "The user's job, role, or field of work",
    "skills":       "Programming languages, tools, or technologies the user knows or uses",
    "location":     "City, country, or timezone the user is in",
    "project":      "Current project or product the user is working on",
    "preferences":  "Stated preferences about communication style, verbosity, format, etc.",
    "goals":        "What the user is trying to achieve or learn",
    "language":     "Preferred spoken language (if not English)",
    "company":      "Company or organisation the user works at",
    "os":           "Operating system or development environment the user uses",
}

EXTRACTION_PROMPT = """You are a memory extractor. Your job is to analyse a conversation and extract \
factual information about the USER (not the assistant).

Extract ONLY facts that are explicitly stated or strongly implied by the user. \
Do NOT infer or guess. Only extract HIGH-CONFIDENCE facts.

Return a JSON object with keys from this schema (omit keys where no fact was found):
{schema}

Rules:
- Values must be short strings (under 100 chars).
- If the user said "I am a developer", set "profession" = "Developer".
- If no new facts are found, return an empty JSON object: {{}}
- Return ONLY valid JSON. No explanation, no markdown, no extra text.

Conversation to analyse:
{conversation}
""".strip()


# ── Load memory for a user ─────────────────────────────────────────────────────

def get_user_memory(user_id: int) -> Dict[str, str]:
    """Return all memory facts for a user as a plain dict."""
    rows = UserMemory.query.filter_by(user_id=user_id).all()
    return {row.key: row.value for row in rows}


def get_memory_list(user_id: int) -> List[dict]:
    """Return all memory facts as a list of dicts (for API responses)."""
    rows = UserMemory.query.filter_by(user_id=user_id).order_by(UserMemory.key).all()
    return [row.to_dict() for row in rows]


# ── Inject memory into system prompt ──────────────────────────────────────────

def build_memory_block(user_id: int) -> Optional[str]:
    """
    Build a "What I know about you" block to prepend to every system prompt.
    Returns None if no memory exists yet.
    """
    memory = get_user_memory(user_id)
    if not memory:
        return None

    lines = ["## What I Know About You"]
    for key, value in memory.items():
        label = MEMORY_SCHEMA.get(key, key).split(" — ")[0]
        lines.append(f"- **{key.title()}**: {value}")

    lines.append("")  # blank line after block
    return "\n".join(lines)


def build_system_prompt_with_memory(base_prompt: str, user_id: int) -> str:
    """Prepend the user memory block to the base system prompt."""
    block = build_memory_block(user_id)
    if block:
        return block + "\n---\n\n" + base_prompt
    return base_prompt


# ── Extract and save new facts ─────────────────────────────────────────────────

def extract_and_save(user_id: int, session_id: int,
                     user_message: str, assistant_reply: str) -> Dict[str, str]:
    """
    Call the LLM to extract facts from a message exchange and upsert them.
    Returns the dict of newly extracted facts (may be empty).
    Best-effort — never raises.
    """
    from llm_client import chat_completion  # local import to avoid circular

    schema_lines = "\n".join(f"  {k}: {v}" for k, v in MEMORY_SCHEMA.items())
    conversation = f"User: {user_message}\nAssistant: {assistant_reply}"

    prompt = EXTRACTION_PROMPT.format(schema=schema_lines, conversation=conversation)

    try:
        result = chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=os.getenv('DEFAULT_CHAT_MODEL', 'llama3-7b'),
            temperature=0.1,      # very low — we want deterministic factual output
            max_tokens=256,
            system_prompt="You are a precise JSON extractor. Output only valid JSON.",
        )
        raw = result["content"].strip()

        # Strip markdown fences if model wrapped in ```json
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        facts = json.loads(raw)
        if not isinstance(facts, dict):
            return {}

        saved = {}
        for key, value in facts.items():
            key   = key.strip().lower()
            value = str(value).strip()
            if key not in MEMORY_SCHEMA or not value or value.lower() == "null":
                continue

            # Upsert: update if key exists, insert if new
            existing = UserMemory.query.filter_by(user_id=user_id, key=key).first()
            if existing:
                if existing.value != value:
                    existing.value          = value
                    existing.source_session = session_id
                    existing.updated_at     = __import__('datetime').datetime.utcnow()
                    saved[key] = value
            else:
                db.session.add(UserMemory(
                    user_id=user_id, key=key, value=value,
                    source_session=session_id, confidence='high',
                ))
                saved[key] = value

        if saved:
            db.session.commit()
            logger.info("Memory updated for user %s: %s", user_id, list(saved.keys()))

        return saved

    except (json.JSONDecodeError, Exception):
        logger.debug("Memory extraction produced no facts for user %s", user_id)
        return {}


# ── CRUD helpers ───────────────────────────────────────────────────────────────

def upsert_memory(user_id: int, key: str, value: str) -> dict:
    """Manually set a memory fact (called from API)."""
    key   = key.strip().lower()[:100]
    value = str(value).strip()[:500]
    existing = UserMemory.query.filter_by(user_id=user_id, key=key).first()
    if existing:
        existing.value = value
        existing.updated_at = __import__('datetime').datetime.utcnow()
    else:
        existing = UserMemory(user_id=user_id, key=key, value=value, confidence='high')
        db.session.add(existing)
    db.session.commit()
    return existing.to_dict()


def delete_memory(user_id: int, key: str) -> bool:
    row = UserMemory.query.filter_by(user_id=user_id, key=key).first()
    if not row:
        return False
    db.session.delete(row)
    db.session.commit()
    return True


def clear_all_memory(user_id: int) -> int:
    count = UserMemory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return count
