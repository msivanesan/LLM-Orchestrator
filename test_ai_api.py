import requests
import json
import time
import sys

# --- CONFIGURATION ---
GATEWAY_URL = "http://localhost"
# You MUST use a valid API Key from the ApiKey microservice
API_KEY = "ak_4acaa0bc566c5f15e089f09e1b9bc094197078412e780e63"

def print_header(title):
    print(f"\n🧠 {title}")
    print("-" * 60)

def test_ai_api():
    print(f"📡 AI ORCHESTRATION API TEST SUITE")
    print("=" * 60)
    
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    # 1. TEST AI SERVICE STATUS
    print_header("1. Checking AI Service Status")
    try:
        res = requests.get(f"{GATEWAY_URL}/api/ai/status", headers=headers, timeout=5)
        if res.status_code == 200:
            print(f"✅ AI Service Status: {res.json()}")
        elif res.status_code == 401:
            print("❌ Unauthorized! Please check if your API_KEY is valid.")
            return
        else:
            print(f"❌ Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

    # 2. GET AVAILABLE MODELS
    print_header("2. Fetching Available Models")
    target_model = "llama3.2:1b"
    try:
        res = requests.get(f"{GATEWAY_URL}/api/ai/models", headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json().get('models', [])
            print(f"✅ Found {len(data)} available models:")
            for m in data:
                print(f"   - {m.get('name')} ({m.get('displayName')})")
            
            # Select the first one for the generation test
            if len(data) > 0:
                target_model = data[0].get('name').replace('models/', '')
        else:
            print(f"❌ Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"❌ Error fetching models: {e}")

    # 3. TEST MODEL GENERATION (Prompt)
    print_header(f"3. Testing Generation (Model: {target_model})")
    payload = {
        "prompt": "Explain what an API Gateway is in one short sentence.",
        "temperature": 0.7,
        "max_tokens": 100
    }
    print(f"Sending prompt: '{payload['prompt']}'")
    
    try:
        start_time = time.time()
        res = requests.post(f"{GATEWAY_URL}/api/ai/models/{target_model}/generate", headers=headers, json=payload, timeout=60)
        
        if res.status_code == 200:
            response_data = res.json()
            # Extract content from Gemini-style response
            candidates = response_data.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                latency = response_data.get('metadata', {}).get('latency_ms', 'Unknown')
                print(f"✅ Response ({latency}ms): \n\n{content.strip()}\n")
            else:
                print(f"⚠️ Response received but no content generated: {response_data}")
        else:
            print(f"❌ Generation Error {res.status_code}: {res.text}")
    except requests.exceptions.Timeout:
        print(f"❌ Generation timed out. The local LLM might still be loading the model into memory.")
    except Exception as e:
        print(f"❌ Error during generation: {e}")

    print("\n" + "=" * 60)
    print("🏁 AI API Test Completed!")

if __name__ == "__main__":
    test_ai_api()
