import requests
import json
import time
import sys

# --- CONFIGURATION ---
GATEWAY_URL = "http://localhost"
LOGIN_USER = "admin"  # Changed from email to username
LOGIN_PASS = "1234"
# External API Key (Create one in the dashboard and paste here if testing API directly)
TEST_API_KEY = "ak_4acaa0bc566c5f15e089f09e1b9bc094197078412e780e63"

def print_header(title):
    print(f"\n🚀 {title}")
    print("-" * 60)

def test_full_chain():
    print(f"📡 LLM-ORCHESTRATOR END-TO-END TEST SUITE")
    print("=" * 60)

    # 1. USER LOGIN (JWT AUTH)
    print_header("1. Authenticating with User Service")
    login_url = f"{GATEWAY_URL}/api/users/login"
    try:
        res = requests.post(login_url, json={"username": LOGIN_USER, "password": LOGIN_PASS})
        if res.status_code != 200:
            print(f"❌ Login failed: {res.text}")
            return
        
        token = res.json().get('access_token')
        auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print(f"✅ Authenticated as {LOGIN_USER}")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return

    # 2. MODEL DISCOVERY
    print_header("2. Model Discovery (Ollama via AI Proxy)")
    try:
        # Chat API wraps in a .data object
        res = requests.get(f"{GATEWAY_URL}/api/chat/models", headers=auth_headers)
        res_json = res.json()
        
        # The API returns {'status': 'success', 'data': [...]}
        data_field = res_json.get('data')
        
        if isinstance(data_field, list):
            models = data_field
        elif isinstance(data_field, dict):
            models = data_field.get('models') or []
        else:
            models = []
        
        if models:
            print(f"✅ Found {len(models)} models:")
            for m in models:
                name = m.get('name') or m.get('id', 'unknown')
                display = m.get('displayName') or name
                print(f"   - {name} ({display})")
            target_model = models[0].get('name', 'llama3.2:1b').replace('models/', '')
        else:
            print("⚠️ No models returned from API logic, using fallback.")
            target_model = "llama3.2:1b"
    except Exception as e:
        print(f"❌ Discovery error: {e}")
        target_model = "llama3.2:1b"

    # 3. CHAT STREAMING (SSE)
    print_header(f"3. Chat Streaming (Model: {target_model})")
    stream_url = f"{GATEWAY_URL}/api/chat/quick-stream"
    payload = {
        "content": "Tell me a very short 1-sentence fact about space.",
        "model": target_model
    }
    
    try:
        print(f"Sending prompt: {payload['content']}")
        # Use stream=True to handle SSE
        with requests.post(stream_url, headers=auth_headers, json=payload, stream=True) as r:
            if r.status_code != 200:
                print(f"❌ Stream failed: {r.text}")
            else:
                print("📡 Receiving stream: ", end="", flush=True)
                full_text = ""
                for line in r.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            chunk = line_str[6:].strip()
                            if chunk == '[DONE]':
                                break
                            try:
                                data = json.loads(chunk)
                                if data['type'] == 'token':
                                    txt = data['text']
                                    full_text += txt
                                    print(txt, end="", flush=True)
                            except:
                                pass
                print(f"\n✅ Stream complete.")
    except Exception as e:
        print(f"\n❌ Stream connection error: {e}")

    # 4. USER MEMORY
    print_header("4. Context & Memory Layer")
    try:
        # Wait a second for the background memory extraction thread to finish
        print("Waiting for async memory extraction...")
        time.sleep(2) 
        res = requests.get(f"{GATEWAY_URL}/api/chat/memory", headers=auth_headers)
        memories = res.json().get('data', [])
        print(f"✅ Current Memory Facts: {len(memories)}")
        for m in memories:
            print(f"   - {m['key']}: {m['value']}")
    except Exception as e:
        print(f"❌ Memory error: {e}")

    # 5. EXTERNAL API KEY ACCESS
    print_header("5. External API Key Validation")
    api_headers = {"X-API-KEY": TEST_API_KEY, "Content-Type": "application/json"}
    try:
        # Direct generation via the AI Proxy layer (bypasses chat state)
        res = requests.post(
            f"{GATEWAY_URL}/api/ai/models/{target_model}/generate",
            headers=api_headers,
            json={"prompt": "Say 'Gateway OK'"},
            timeout=10
        )
        if res.status_code == 200:
            print("✅ API Key Authentication: SUCCESS")
        elif res.status_code == 401:
            print("⚠️ API Key: UNAUTHORIZED (Update TEST_API_KEY in script to test this)")
        else:
            print(f"❌ API Key Rejection: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ API Key test error: {e}")

    print("\n" + "=" * 60)
    print("🏁 Full Chain Test Completed!")

if __name__ == "__main__":
    test_full_chain()
