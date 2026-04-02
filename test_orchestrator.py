import requests
import json
import time
import sys
from datetime import datetime

# ── CONFIGURATION ───────────────────────────────────────────────────────────
GATEWAY_URL = "http://localhost"
TEST_USER = "admin"
TEST_PASS = "1234"
# This API Key should ideally be in your 'apikey' database for step 3 to pass
TEST_API_KEY = "ak_4acaa0bc566c5f15e089f09e1b9bc094197078412e780e63"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(msg, type="info"):
    icon = "ℹ️"
    color = ""
    if type == "success": icon, color = "✅", Colors.OKGREEN
    if type == "error": icon, color = "❌", Colors.FAIL
    if type == "warn": icon, color = "⚠️", Colors.WARNING
    if type == "header": icon, color = "🚀", Colors.HEADER + Colors.BOLD
    
    print(f"{color}{icon} {msg}{Colors.ENDC}")

def run_suite():
    print("\n" + "="*70)
    log("ULTIMATE LLM-ORCHESTRATOR TEST SUITE", "header")
    print("="*70 + "\n")

    ctx = {"token": None, "model": "llama3.2:1b"}

    # 1. USER AUTH (JWT)
    log("Step 1: Authenticating with User Service...", "info")
    try:
        r = requests.post(f"{GATEWAY_URL}/api/users/login", json={"username": TEST_USER, "password": TEST_PASS}, timeout=10)
        if r.status_code == 200:
            ctx["token"] = r.json().get('access_token')
            log(f"Authenticated successfully as '{TEST_USER}'", "success")
        else:
            log(f"Login failed: {r.status_code} - {r.text}", "error")
            return
    except Exception as e:
        log(f"Connection error to Gateway: {e}", "error")
        return

    headers = {"Authorization": f"Bearer {ctx['token']}", "Content-Type": "application/json"}

    # 2. CHAT MODEL DISCOVERY
    log("Step 2: Testing Model Discovery...", "info")
    try:
        r = requests.get(f"{GATEWAY_URL}/api/chat/models", headers=headers, timeout=10)
        if r.status_code == 200:
            models = r.json().get('data', [])
            if models:
                ctx["model"] = models[0].get('name', ctx["model"]).replace('models/', '')
                log(f"Found {len(models)} models. Using '{ctx['model']}' for tests.", "success")
            else:
                log("No models found in Ollama, using fallback.", "warn")
        else:
            log(f"Model discovery failed: {r.status_code}", "error")
    except Exception as e:
        log(f"Discovery error: {e}", "error")

    # 3. API KEY VALIDATION
    log("Step 3: External API Key Check...", "info")
    try:
        api_headers = {"X-API-KEY": TEST_API_KEY, "Content-Type": "application/json"}
        # Direct status check on AI service
        r = requests.get(f"{GATEWAY_URL}/api/ai/status", headers=api_headers, timeout=5)
        if r.status_code == 200:
            log("API Key authentication verified.", "success")
        else:
            log(f"API Key rejected ({r.status_code}). Ensure it exists in 'apikey' DB.", "warn")
    except Exception as e:
        log(f"API Key test error: {e}", "error")

    # 4. CHAT STREAMING (SSE)
    log(f"Step 4: Real-time SSE Streaming (Model: {ctx['model']})...", "info")
    payload = {"content": "Say 'Gateway OK' in exactly two words.", "model": ctx["model"]}
    try:
        with requests.post(f"{GATEWAY_URL}/api/chat/quick-stream", headers=headers, json=payload, stream=True, timeout=60) as r:
            if r.status_code == 200:
                print(f"      {Colors.OKCYAN}Streaming Output: {Colors.ENDC}", end="", flush=True)
                for line in r.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            chunk = line_str[6:]
                            if chunk == '[DONE]': break
                            try:
                                data = json.loads(chunk)
                                if data['type'] == 'token':
                                    print(data['text'], end="", flush=True)
                            except: pass
                print("\n")
                log("Streaming SSE verified.", "success")
            else:
                log(f"Streaming failed: {r.status_code}", "error")
    except Exception as e:
        log(f"Streaming connection error: {e}", "error")

    # 5. ASYNC MEMORY & FACTS
    log("Step 5: Testing Background Task Queue (Memory)...", "info")
    try:
        log("Waiting 3s for Huey to process facts...", "info")
        time.sleep(3) # Wait for Task Queue
        r = requests.get(f"{GATEWAY_URL}/api/chat/memory", headers=headers, timeout=10)
        facts = r.json().get('data', [])
        if facts:
            log(f"Task Queue OK. Facts extracted: {len(facts)}", "success")
            for f in facts[:2]: print(f"      📍 {f['key']}: {f['value']}")
        else:
            log("No facts found yet. Task queue might be slow or model didn't return facts.", "warn")
    except Exception as e:
        log(f"Memory check error: {e}", "error")

    # 6. SECURITY - GATEWAY SPOOF TEST
    log("Step 6: Security - Zero Trust Check...", "info")
    try:
        # Try to call Chat service directly on port 5004 (should fail if blocked by Docker network or Internal Secret)
        # We test if we can bypass Nginx using a fake key
        fake_headers = {"X-Internal-Service-Key": "fake-key-123", "Authorization": f"Bearer {ctx['token']}"}
        # Note: This is a best-effort check since we are running from Host, not inside Docker
        # A 403 response from Gateway for direct access attempt is what we're looking for
        log("Testing if random internal headers are rejected...", "info")
        r = requests.get(f"{GATEWAY_URL}/api/chat/sessions", headers=fake_headers, timeout=5)
        # Nginx forwards to backend which should reject 'fake-key-123' 
        # because it doesn't match INTERNAL_SERVICE_SECRET
        if r.status_code == 403:
            log("Spoofed Internal Header successfully rejected.", "success")
        else:
            log(f"Security Warning: System accepted request or returned {r.status_code}", "warn")
    except Exception as e:
        log(f"Security test error: {e}", "debug")

    # 7. INFRASTRUCTURE HEALTH
    log("Step 7: Probing Service Health Cluster...", "info")
    endpoints = [
        ("/api/chat/health", "Chat API"),
        ("/api/users/me", "User API"), # authenticated check
    ]
    for url, name in endpoints:
        try:
            r = requests.get(f"{GATEWAY_URL}{url}", headers=headers, timeout=5)
            status = "success" if r.status_code in [200, 401] else "error"
            log(f"{name}: HTTP {r.status_code}", status)
        except:
            log(f"{name}: UNREACHABLE", "error")

    print("\n" + "="*70)
    log("Full Cluster Pulse Completed!", "header")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_suite()
