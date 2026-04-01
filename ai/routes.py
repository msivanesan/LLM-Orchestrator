from flask import Blueprint, request, jsonify
import requests
import os
import urllib3
import time

# Suppress insecure request warnings for internal/private IP targets
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ai_bp = Blueprint('ai_bp', __name__)

# --- CONFIGURATION ---
DEFAULT_ENGINE = os.getenv('AI_ENGINE_URL', 'http://ollama:11434/v1/chat/completions')
OLLAMA_BASE_URL = DEFAULT_ENGINE.replace('/v1/chat/completions', '')

@ai_bp.route('/models/<model_id>/generate', methods=['POST'])
@ai_bp.route('/models/<model_id>/completion', methods=['POST'])
def model_specific_completion(model_id):
    """
    Model-specific endpoint (Gemini Style)
    Usage: /api/ai/models/llama3-7b/generate
    """
    data = request.get_json() or {}
    user_prompt = data.get('prompt')
    user_messages = data.get('messages', [])
    
    # 1. Standardize Input
    if not user_messages:
        if not user_prompt:
            return jsonify({"error": "No 'prompt' or 'messages' provided"}), 400
        user_messages = [{"role": "user", "content": user_prompt}]

    # 2. Build Payload
    payload = {
        "model": model_id,
        "messages": user_messages,
        "temperature": data.get('temperature', 0.7),
        "max_tokens": data.get('max_tokens', 1024),
        "stream": False
    }

    try:
        start_time = time.time()
        response = requests.post(DEFAULT_ENGINE, json=payload, timeout=120, verify=False)
        response.raise_for_status()
        ai_data = response.json()
        
        # 3. Model-Centric Response Structure
        content = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '')

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
                "latency_ms": int((time.time() - start_time) * 1000)
            }
        }), 200

    except Exception as e:
        return jsonify({"error": f"Model '{model_id}' failed to respond: {str(e)}"}), 503

@ai_bp.route('/completion', methods=['POST'])
def legacy_completion():
    """Fallback / compatibility endpoint"""
    return model_specific_completion("tinyllama")

@ai_bp.route('/models', methods=['GET'])
def list_models():
    """List dynamically available models pulled into Ollama."""
    models_list = []
    
    try:
        # Use Ollama's native tag API to see what is actually downloaded
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
    except Exception as e:
        return jsonify({"error": f"Ollama connection failed: {str(e)}"}), 503

    return jsonify({ "models": models_list }), 200

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    return jsonify({
        "status": "online",
        "platform": "ai-orchestrator-platform",
    }), 200
