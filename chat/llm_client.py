"""
LLM Client — communicates with the internal AI Orchestration Service.
Supports both regular and streaming (SSE) responses.
"""
import os
import time
import logging
import urllib3
from typing import List, Dict, Optional, Generator

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

AI_SERVICE_URL  = os.getenv('AI_SERVICE_URL',      'http://ai:5003')
AI_TIMEOUT      = int(os.getenv('AI_SERVICE_TIMEOUT', '120'))
DEFAULT_MODEL   = os.getenv('DEFAULT_CHAT_MODEL',  'tinyllama')

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


# ── Internal Bridge ────────────────────────────────────────────────────────────

def _get_ai_service_model_url(model: str) -> str:
    """Routes requests to the central AI Orchestration Service."""
    # Maps internal chat shorthand to AI service proxy routes
    return f"{AI_SERVICE_URL}/api/ai/models/{model}/generate"


# ── Blocking completion ────────────────────────────────────────────────────────

def chat_completion(
    messages: List[Dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> Dict:
    full_messages = _build_messages(messages, system_prompt)
    payload = {
        'messages':    full_messages,
        'temperature': temperature,
        'max_tokens':  max_tokens,
    }

    start = time.time()
    try:
        url = _get_ai_service_model_url(model)
        resp = requests.post(url, json=payload, timeout=AI_TIMEOUT, verify=False)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"AI Service Error: {e}")
        raise RuntimeError(f'Cannot reach AI Service at {url}: {e}')

    latency_ms = int((time.time() - start) * 1000)
    data = resp.json()

    try:
        # Note: AI Service returns Gemini-style candidate structure
        content = data['candidates'][0]['content']['parts'][0]['text']
        finish_reason = data['candidates'][0].get('finish_reason', 'STOP')
    except (KeyError, IndexError):
        raise RuntimeError(f'Unexpected AI Service response shape: {data}')

    return {'content': content, 'model': model, 'latency_ms': latency_ms,
            'finish_reason': finish_reason}


# ── Streaming completion (Legacy Bridge) ──────────────────────────────────────

def chat_completion_stream(
    messages: List[Dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    NOTE: Currently proxying streaming via the standard blocking call 
    because the AI Service generates full candidates. 
    Streaming is simulated for UI stability.
    """
    try:
        result = chat_completion(messages, model, temperature, max_tokens, system_prompt)
        text = result['content']
        # Yield as one big chunk for now (simulated stream)
        yield f'data: {{"choices":[{{"delta":{{"content":"{text}"}}}}]}}\n\n'
    except Exception as e:
        yield f'data: {{"error":"{str(e)}"}}\n\n'
    finally:
        yield 'data: [DONE]\n\n'


# ── Auto-title generation ─────────────────────────────────────────────────────

def generate_title(first_user_message: str, model: str = DEFAULT_MODEL) -> str:
    """Generate a short session title from the first user message."""
    try:
        result = chat_completion(
            messages=[{'role': 'user', 'content': first_user_message}],
            model=model,
            temperature=0.5,
            max_tokens=20,
            system_prompt=(
                'Generate a short, descriptive 3-6 word title for this conversation. '
                'Output ONLY the title, no punctuation, no quotes.'
            ),
        )
        title = result['content'].strip().strip('"\'').strip()
        return title[:100] if title else 'New Chat'
    except Exception:
        logger.warning('Title generation failed, using default')
        return first_user_message[:60] or 'New Chat'


def ai_service_health() -> bool:
    try:
        resp = requests.get(
            f'{AI_SERVICE_URL}/api/ai/status', timeout=5, verify=False
        )
        return resp.status_code == 200
    except Exception:
        return False


def list_available_models() -> List[Dict]:
    try:
        resp = requests.get(f'{AI_SERVICE_URL}/api/ai/models', timeout=10, verify=False)
        resp.raise_for_status()
        return resp.json().get('models', [])
    except Exception as e:
        logger.warning('Could not fetch models: %s', e)
        return []
