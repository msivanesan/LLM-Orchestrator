import requests
import json

# --- CONFIGURATION ---
API_KEY = "ak_9b8c02cc0e0add6ac78e26a789c74a189cb0a7b0179f795d"
GATEWAY_URL = "http://localhost" # The Unified Gateway Root

def test_api_orchestrator(key):
    headers = {"X-API-KEY": key, "Content-Type": "application/json"}
    
    print(f"🚀 LLM ORCHESTRATOR TEST SUITE")
    print(f"Using Key: {key[:10]}...")
    print("=" * 60)
    
    # 1. TEST IDENTITY (USER SERVICE)
    print("\n[TEST 1] Accessing Identity Layer (User Service)")
    print("-" * 40)
    try:
        # Note: Port 80 routes /api/users to microservice on 5001
        response = requests.get(f"{GATEWAY_URL}/api/users/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Payload: {response.text[:200]}")
    except Exception as e:
        print(f"Error connecting: {e}")

    # 2. TEST MODEL DISCOVERY
    print("\n[TEST 2] Fetching Available Models")
    print("-" * 40)
    try:
        response = requests.get(f"{GATEWAY_URL}/api/ai/models", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Models: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. TEST AI GENERATION (GEMINI STYLE)
    print("\n[TEST 3] Accessing Model-Specific Endpoint (Gemini Style)")
    print("-" * 40)
    # Using the new model-based route
    target_model = "llama3-7b"
    ai_payload = {
        "prompt": "What is the capital of France?"
    }
    try:
        print(f"Requesting generation from: {target_model}...")
        response = requests.post(
            f"{GATEWAY_URL}/api/ai/models/{target_model}/generate", 
            headers=headers, 
            json=ai_payload,
            timeout=45
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            answer = data['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ {target_model} Response: {answer}")
        else:
            print(f"❌ Rejection Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. TEST RATE LIMITING ON AI
    print("\n[TEST 3] Stress Testing AI Rate Limiter (RPM Enforcement)")
    print("-" * 40)
    for i in range(1, 11):
        try:
            response = requests.post(
                f"{GATEWAY_URL}/api/ai/completion", 
                headers=headers, 
                json=ai_payload
            )
            print(f"AI Request {i}: Status {response.status_code}")
            if response.status_code == 429:
                print("🚫 SUCCESS: Gateway enforced RPM Limit!")
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    print("\n" + "=" * 60)
    print("🏁 Orchestrator Test Suite Completed!")

if __name__ == "__main__":
    test_api_orchestrator(API_KEY)
