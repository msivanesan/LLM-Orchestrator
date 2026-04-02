from flask import Blueprint, request, jsonify
import requests
import os
import urllib3
import time
import logging

# Suppress insecure request warnings for internal/private IP targets
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai_bp', __name__)

# --- CONFIGURATION ---
DEFAULT_ENGINE = os.getenv('AI_ENGINE_URL', 'http://ollama:11434/v1/chat/completions')
OLLAMA_BASE_URL = DEFAULT_ENGINE.replace('/v1/chat/completions', '')
AI_TIMEOUT = int(os.getenv('AI_SERVICE_TIMEOUT', '120'))

# --- HELPERS ---
def is_embedding_model(model_name: str) -> bool:
    """Helper to detect if a model is intended for embeddings only."""
    keywords = ['embed', 'minilm', 'arctic', 'sentence', 'bert', 'nomic']
    return any(k in model_name.lower() for k in keywords)


@ai_bp.route('/models/<model_id>/generate', methods=['POST'])
@ai_bp.route('/models/<model_id>/completion', methods=['POST'])
def model_specific_completion(model_id):
    """
    Model-specific completion endpoint (Generative task).
    REJECTS embedding models to prevent improper usage.
    """
    # ── Strict Role Enforcement Check ──
    if is_embedding_model(model_id):
        return jsonify({
            "error": f"Model '{model_id}' is a dedicated embedding model and cannot be used for text generation.",
            "type": "ModelRoleMismatch"
        }), 400

    data = request.get_json() or {}
    user_prompt = data.get('prompt')
    user_messages = data.get('messages', [])
    
    # 1. Standardize Input
    if not user_messages:
        if not user_prompt:
            return jsonify({"error": "No 'prompt' or 'messages' provided"}), 400
        user_messages = [{"role": "user", "content": user_prompt}]

    # 2. Advanced Parameters for Agents
    payload = {
        "model": model_id,
        "messages": user_messages,
        "temperature": data.get('temperature', 0.7),
        "max_tokens": data.get('max_tokens', 1024),
        "top_p": data.get('top_p', 1.0),
        "presence_penalty": data.get('presence_penalty', 0.0),
        "frequency_penalty": data.get('frequency_penalty', 0.0),
        "stream": False
    }

    # Handle Blocking Path
    try:
        start_time = time.time()
        response = requests.post(DEFAULT_ENGINE, json=payload, timeout=AI_TIMEOUT, verify=False)
        response.raise_for_status()
        ai_data = response.json()
        
        # 3. Extract Content and Usage Metadata
        content = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        usage = ai_data.get('usage', {}) # Standard OpenAI/Ollama usage object

        return jsonify({
            "model": model_id,
            "candidates": [
                {
                    "content": {"parts": [{"text": content}]},
                    "finish_reason": "STOP"
                }
            ],
            "metadata": {
                "engine": "distributed-gpu",
                "latency_ms": int((time.time() - start_time) * 1000),
                "usage": usage
            }
        }), 200

    except requests.exceptions.HTTPError as he:
        status = he.response.status_code if he.response else 502
        try:
            err_body = he.response.json()
            msg = err_body.get('error', str(he))
        except:
            msg = str(he)
        return jsonify({"error": f"AI Engine error ({status}): {msg}", "type": "EngineError"}), status

    except Exception as e:
        logger.exception("AI Service critical failure")
        return jsonify({"error": f"Internal AI Service Error: {str(e)}", "type": "InternalError"}), 500


@ai_bp.route('/models/<model_id>/embed', methods=['POST'])
def embed_content(model_id):
    """
    Model-specific embedding endpoint (Semantic Search task).
    REJECTS chat/generative models to prevent improper usage.
    """
    # ── Strict Role Enforcement Check ──
    if not is_embedding_model(model_id):
        return jsonify({
            "error": f"Model '{model_id}' is a generative model. Please use a dedicated embedding model (like 'nomic-embed-text') for search and RAG tasks.",
            "type": "ModelRoleMismatch"
        }), 400

    data = request.get_json() or {}
    text_content = data.get('content') or data.get('input')
    
    if not text_content:
        return jsonify({"error": "No 'content' or 'input' provided for embedding"}), 400

    embed_payload = {
        "model": model_id,
        "input": text_content
    }

    try:
        # Route to Ollama's embeddings endpoint
        embed_url = DEFAULT_ENGINE.replace('/chat/completions', '/embeddings')
        resp = requests.post(embed_url, json=embed_payload, timeout=AI_TIMEOUT, verify=False)
        resp.raise_for_status()
        embed_data = resp.json()

        return jsonify({
            "model": model_id,
            "embedding": embed_data.get('data', [{}])[0].get('embedding', []),
            "metadata": {
                "engine": "distributed-gpu-embed",
                "usage": embed_data.get('usage', {})
            }
        }), 200

    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return jsonify({"error": f"Embedding engine failure: {str(e)}"}), 502

@ai_bp.route('/completion', methods=['POST'])
def legacy_completion():
    """Fallback / compatibility endpoint"""
    return model_specific_completion("tinyllama")

# Global in-memory cache (12 hours = 43200 seconds)
_MODEL_CACHE = {"data": None, "updated_at": 0}
CACHE_TTL = 43200

@ai_bp.route('/models', methods=['GET'])
def list_models():
    """List dynamically available models pulled into Ollama (cached for 12 hours)."""
    global _MODEL_CACHE
    now = time.time()

    # 1. Check if cache is still valid
    if _MODEL_CACHE["data"] and (now - _MODEL_CACHE["updated_at"]) < CACHE_TTL:
        return jsonify(_MODEL_CACHE["data"]), 200

    # 2. Fetch fresh list from Ollama
    models_list = []
    try:
        # Use Ollama's native tag API directly for discovery
        tags_url = OLLAMA_BASE_URL.replace('/v1', '') + '/api/tags'
        resp = requests.get(tags_url, timeout=5)
        if resp.status_code == 200:
            ollama_models = resp.json().get('models', [])
            for m in ollama_models:
                mid = m['name']
                models_list.append({
                    "name": f"models/{mid}",
                    "displayName": f"Local: {mid}",
                    "capabilities": ["generateContent"]
                })
        else:
             # Fallback if Ollama returns error (still serve cache if we have it)
             if _MODEL_CACHE["data"]: return jsonify(_MODEL_CACHE["data"]), 200
             return jsonify({"error": "Ollama service unavailable"}), 503

        # 3. Update Cache
        final_resp = { "models": models_list }
        _MODEL_CACHE = {"data": final_resp, "updated_at": now}
        return jsonify(final_resp), 200

    except Exception as e:
        # On error, serve from stale cache if available
        if _MODEL_CACHE["data"]:
            logger.warning("Serving stale model list due to Ollama error: %s", e)
            return jsonify(_MODEL_CACHE["data"]), 200
        return jsonify({"error": f"Discovery failed: {str(e)}"}), 503

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    return jsonify({
        "status": "online",
        "platform": "ai-orchestrator-platform",
    }), 200
