from flask import Blueprint, request, jsonify
import requests
import os
import urllib3
import time

# Suppress insecure request warnings for internal/private IP targets
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ai_bp = Blueprint('ai_bp', __name__)

# --- CONFIGURATION ---
DEFAULT_ENGINE = 'https://192.168.5.23/ai/v1/chat/completions'
AI_ENGINE_URL = os.getenv('AI_ENGINE_URL', DEFAULT_ENGINE)

# Model Registry (Simulation of available models on this platform)
AVAILABLE_MODELS = {
    "llama3-7b": {"engine": AI_ENGINE_URL, "description": "Llama 3 7B - Fast & Capable"},
    "llama3-70b": {"engine": AI_ENGINE_URL, "description": "Llama 3 70B - High Reasoning (Experimental)"},
    "gemini-flash-proxy": {"engine": AI_ENGINE_URL, "description": "High-Efficiency Flash Proxy"},
}

@ai_bp.route('/models/<model_id>/generate', methods=['POST'])
@ai_bp.route('/models/<model_id>/completion', methods=['POST'])
def model_specific_completion(model_id):
    """
    Model-specific endpoint (Gemini Style)
    Usage: /api/ai/models/llama3-7b/generate
    """
    if model_id not in AVAILABLE_MODELS:
        return jsonify({"error": f"Model '{model_id}' not found on this platform."}), 404

    data = request.get_json() or {}
    user_prompt = data.get('prompt')
    user_messages = data.get('messages', [])
    
    # 1. Standardize Input
    if not user_messages:
        if not user_prompt:
            return jsonify({"error": "No 'prompt' or 'messages' provided"}), 400
        user_messages = [{"role": "user", "content": user_prompt}]

    target_engine = AVAILABLE_MODELS[model_id]['engine']
    
    # 2. Build Payload
    payload = {
        "model": model_id.split('-')[0], # Simplified model name for engine
        "messages": user_messages,
        "temperature": data.get('temperature', 0.7),
        "max_tokens": data.get('max_tokens', 1024)
    }

    try:
        start_time = time.time()
        response = requests.post(target_engine, json=payload, timeout=90, verify=False)
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
    return model_specific_completion("llama3-7b")

@ai_bp.route('/models', methods=['GET'])
def list_models():
    """List available model endpoints"""
    return jsonify({
        "models": [
            {
                "name": f"models/{mid}",
                "displayName": info['description'],
                "capabilities": ["generateContent"]
            } for mid, info in AVAILABLE_MODELS.items()
        ]
    }), 200

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    return jsonify({
        "status": "online",
        "platform": "ai-orchestrator-platform",
        "active_models": list(AVAILABLE_MODELS.keys())
    }), 200
