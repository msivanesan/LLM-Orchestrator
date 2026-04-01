import requests
import json
import time

# --- CONFIGURATION ---
GATEWAY_URL = "http://localhost"
# Use your active API Key (Ensure this exists in your apikey database!)
API_KEY = "ak_4acaa0bc566c5f15e089f09e1b9bc094197078412e780e63"

def run_test():
    print("🚀 AI Production Test Runner")
    print("=" * 60)
    
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    # 1. DISCOVER MODELS
    print("\n🔍 Step 1: Discovering downloaded models...")
    try:
        resp = requests.get(f"{GATEWAY_URL}/api/ai/models", headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"❌ Failed to list models. Status: {resp.status_code}\n{resp.text}")
            return

        models = resp.json().get('models', [])
        if not models:
            print("⚠️ Ollama is online but no models are downloaded yet.")
            return

        print(f"✅ Found {len(models)} model(s):")
        for m in models:
            print(f"   - {m['name']} (Display: {m['displayName']})")

        # Pick the first one for the test
        target_model = models[0]['name'].replace('models/', '')
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. TEST GENERATION
    print(f"\n🧠 Step 2: Testing generation with '{target_model}'...")
    payload = {
        "prompt": "Say 'System is online!' in a creative way in one sentence.",
        "temperature": 0.5,
        "max_tokens": 50
    }

    try:
        start = time.time()
        gen_url = f"{GATEWAY_URL}/api/ai/models/{target_model}/generate"
        res = requests.post(gen_url, headers=headers, json=payload, timeout=60)
        
        if res.status_code == 200:
            data = res.json()
            content = data['candidates'][0]['content']['parts'][0]['text']
            latency = data['metadata']['latency_ms']
            print(f"✅ AI Response ({latency}ms):")
            print(f"   \"{content.strip()}\"")
        else:
            print(f"❌ Generation failed! Error {res.status_code}: {res.text}")

    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "=" * 60)
    print("🏁 Test Suite Complete")

if __name__ == "__main__":
    run_test()
