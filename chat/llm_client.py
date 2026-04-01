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

AI_ENGINE_URL   = os.getenv('AI_ENGINE_URL',       'http://localhost:11434/v1/chat/completions')
AI_SERVICE_URL  = os.getenv('AI_SERVICE_URL',      'http://localhost:5003')
AI_TIMEOUT      = int(os.getenv('AI_SERVICE_TIMEOUT', '90'))
DEFAULT_MODEL   = os.getenv('DEFAULT_CHAT_MODEL',  'llama3-7b')

# Model → engine URL mapping (mirrors ai/routes.py)
MODEL_ENGINE_MAP = {
    'llama3.2:1b':        AI_ENGINE_URL,
    'qwen2.5:0.5b':       AI_ENGINE_URL,
    'llama3-7b':          AI_ENGINE_URL,
    'llama3-70b':         AI_ENGINE_URL,
    'gemini-flash-proxy': AI_ENGINE_URL,
}

SYSTEM_PROMPT = os.getenv(
    'CHAT_SYSTEM_PROMPT',
    """You are an intelligent, helpful, and articulate AI assistant — similar to ChatGPT or Claude. \
You provide thorough, well-structured, and insightful responses.

## Core Behaviour
- Always respond in the same language the user writes in.
- Be conversational yet professional. Match the user's tone — formal when they're formal, relaxed when casual.
- Be direct and confident. Never hedge excessively or add unnecessary disclaimers.
- Proactively provide context, background, and related information the user might find useful — even if not explicitly asked.

## Response Quality
- **Be comprehensive**: Cover the topic in full. Do not give short, shallow answers unless the question is genuinely simple (e.g. "What is 2+2?").
- **Use structure**: For multi-part or complex answers, use headings (##), bullet points, numbered lists, and bold text to improve readability.
- **Give examples**: Concrete examples, analogies, and real-world scenarios make explanations clear and memorable.
- **Code formatting**: Always wrap code in markdown fenced blocks with the correct language tag (e.g. ```python). Explain what the code does.
- **Step-by-step reasoning**: For problems, tasks, or explanations, break things down into clear logical steps.

## Accuracy & Honesty
- If you are uncertain about something, say so clearly — but still try to provide the most helpful answer you can.
- Do not fabricate facts, statistics, URLs, or citations. If you don't know something, say so.
- For factual questions, give precise, accurate, and up-to-date information to the best of your knowledge.

## Conversation Awareness
- You have access to the conversation history. Reference prior messages where relevant.
- If a question is ambiguous, interpret it charitably in the most useful direction — or ask a clarifying question.

## Formatting Rules
- Use **bold** for key terms, important concepts, and action items.
- Use `code` for technical terms, variable names, commands, or file paths.
- Use numbered lists for sequential steps; bullet points for non-sequential items.
- Keep paragraphs concise (3–5 sentences max). Use whitespace to separate ideas.
- When comparing options, use a table.

Always aim to leave the user better informed, more capable, or with a concrete next step."""
)


def _build_messages(messages: List[Dict], system_prompt: Optional[str] = None) -> List[Dict]:
    prompt = system_prompt or SYSTEM_PROMPT
    if not messages or messages[0].get('role') != 'system':
        return [{'role': 'system', 'content': prompt}] + messages
    return messages


def _engine_url(model: str) -> str:
    return MODEL_ENGINE_MAP.get(model, AI_ENGINE_URL)


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
        'model':       model,
        'messages':    full_messages,
        'temperature': temperature,
        'max_tokens':  max_tokens,
        'stream':      False,
    }

    start = time.time()
    try:
        resp = requests.post(
            _engine_url(model), json=payload, timeout=AI_TIMEOUT, verify=False
        )
        resp.raise_for_status()
    except requests.Timeout:
        raise RuntimeError(f'AI engine timed out after {AI_TIMEOUT}s')
    except requests.ConnectionError:
        raise RuntimeError(f'Cannot connect to AI engine at {_engine_url(model)}')
    except requests.HTTPError as e:
        raise RuntimeError(f'AI engine error {resp.status_code}: {resp.text[:200]}')

    latency_ms = int((time.time() - start) * 1000)
    data = resp.json()

    try:
        content       = data['choices'][0]['message']['content']
        finish_reason = data['choices'][0].get('finish_reason', 'stop')
    except (KeyError, IndexError):
        raise RuntimeError(f'Unexpected AI response shape: {data}')

    return {'content': content, 'model': model, 'latency_ms': latency_ms,
            'finish_reason': finish_reason}


# ── Streaming completion (SSE generator) ──────────────────────────────────────

def chat_completion_stream(
    messages: List[Dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Yields raw SSE data lines from the AI engine.
    Each yielded string is already a complete SSE line: ``data: {...}\\n\\n``
    The final sentinel is ``data: [DONE]\\n\\n``.
    """
    full_messages = _build_messages(messages, system_prompt)
    payload = {
        'model':       model,
        'messages':    full_messages,
        'temperature': temperature,
        'max_tokens':  max_tokens,
        'stream':      True,
    }

    try:
        with requests.post(
            _engine_url(model), json=payload,
            stream=True, timeout=AI_TIMEOUT, verify=False
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if raw_line:
                    decoded = raw_line.decode('utf-8', errors='replace')
                    # Pass through exactly as-is (already "data: {...}" format)
                    yield f'{decoded}\n\n'
    except requests.Timeout:
        yield 'data: {"error":"AI engine timed out"}\n\n'
    except Exception as e:
        logger.exception('Streaming error')
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
