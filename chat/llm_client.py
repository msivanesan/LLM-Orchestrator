import os
import time
import json
import logging
import urllib3
from typing import List, Dict, Optional, Generator

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Direct Ollama connection — no dependency on the AI orchestrator
OLLAMA_BASE = os.getenv('OLLAMA_BASE_URL', 'http://ollama:11434')
OLLAMA_URL  = f"{OLLAMA_BASE}/v1/chat/completions"
AI_TIMEOUT  = int(os.getenv('AI_SERVICE_TIMEOUT', '120'))

SYSTEM_PROMPT = os.getenv(
    'CHAT_SYSTEM_PROMPT',
    """You are an intelligent, helpful, and articulate AI assistant. \
Respond in the language the user writes in. Be conversational yet professional."""
)

def _build_messages(messages: List[Dict], system_prompt: Optional[str] = None) -> List[Dict]:
    prompt = system_prompt or SYSTEM_PROMPT
    if not messages or messages[0].get('role') != 'system':
        return [{'role': 'system', 'content': prompt}] + messages
    return messages


# ── Blocking completion ────────────────────────────────────────────────────────

def chat_completion(
    messages: List[Dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> Dict:
    full_messages = _build_messages(messages, system_prompt)
    payload = {
        'model':       model,
        'messages':    full_messages,
        'temperature': temperature,
        'max_tokens':  max_tokens,
        'stream':      False
    }

    start = time.time()
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=AI_TIMEOUT, verify=False)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Ollama Connection Error: {e}")
        raise RuntimeError(f'Cannot reach Ollama at {OLLAMA_URL}: {e}')

    latency_ms = int((time.time() - start) * 1000)
    data = resp.json()

    try:
        # Standard OpenAI/Ollama structure
        content = data['choices'][0]['message']['content']
        finish_reason = data['choices'][0].get('finish_reason', 'stop')
    except (KeyError, IndexError):
        raise RuntimeError(f'Unexpected Ollama response shape: {data}')

    return {'content': content, 'model': model, 'latency_ms': latency_ms,
            'finish_reason': finish_reason}


# ── Streaming completion ──────────────────────────────────────────────────────

def chat_completion_stream(
    messages: List[Dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Real-time native streaming from Ollama.
    """
    full_messages = _build_messages(messages, system_prompt)
    payload = {
        'model':       model,
        'messages':    full_messages,
        'temperature': temperature,
        'max_tokens':  max_tokens,
        'stream':      True
    }

    try:
        with requests.post(OLLAMA_URL, json=payload, timeout=AI_TIMEOUT, verify=False, stream=True) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    # Directly pass through Ollama's data chunks
                    yield f"{decoded}\n\n"

    except Exception as e:
        logger.error(f"Ollama Stream Error: {e}")
        yield f'data: {json.dumps({"error": str(e)})}\n\n'
    finally:
        yield 'data: [DONE]\n\n'


# ── Auto-title generation ─────────────────────────────────────────────────────

def generate_title(first_user_message: str, model: str) -> str:
    """Generate a short session title from the first user message."""
    try:
        result = chat_completion(
            messages=[{'role': 'user', 'content': first_user_message}],
            model=model,
            temperature=0.7,
            max_tokens=20,
            system_prompt='Generate a 3-6 word title for this chat. No quotes or intro. Just title.'
        )
        title = result['content'].strip().strip('"\'').strip()
        return title[:100] if title else 'New Chat'
    except Exception:
        return first_user_message[:60] or 'New Chat'


def ai_service_health() -> bool:
    """Check if Ollama is responsive."""
    try:
        resp = requests.get(f'{OLLAMA_BASE}/api/tags', timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def list_available_models() -> List[Dict]:
    """Dynamically list models pulled into the Ollama engine."""
    try:
        resp = requests.get(f'{OLLAMA_BASE}/api/tags', timeout=10)
        resp.raise_for_status()
        ollama_models = resp.json().get('models', [])
        
        models_list = []
        for m in ollama_models:
            mid = m['name']
            models_list.append({
                "name": f"models/{mid}",
                "displayName": f"Local: {mid}",
                "id": mid
            })
        return models_list
    except Exception as e:
        logger.warning('Could not fetch Ollama models: %s', e)
        return []
