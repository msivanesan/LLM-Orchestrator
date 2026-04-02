import requests
import json
import uuid

# --- CONFIGURATION ---
GATEWAY_URL = "http://localhost/api/ai"
API_KEY     = "ak_4acaa0bc566c5f15e089f09e1b9bc094197078412e780e63"

# Models to test
CHAT_MODEL  = "tinyllama"
EMBED_MODEL = "nomic-embed-text"

HEADERS = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def print_result(name, ok, data):
    status = "✅ PASS" if ok else "❌ FAIL"
    print(f"\n{'='*50}\n[{status}] {name}\n{'='*50}")
    print(json.dumps(data, indent=2))

def test_chat():
    print(f"Testing Chat Generation with '{CHAT_MODEL}'...")
    url = f"{GATEWAY_URL}/models/{CHAT_MODEL}/generate"
    payload = {
        "messages": [{"role": "user", "content": "Explain RAG in one sentence."}],
        "temperature": 0.7
    }
    try:
        r = requests.post(url, json=payload, headers=HEADERS)
        print_result("CHAT COMPLETION", r.status_code == 200, r.json())
    except Exception as e:
        print(f"Request failed: {e}")

def test_embed():
    print(f"Testing Embeddings with '{EMBED_MODEL}'...")
    url = f"{GATEWAY_URL}/models/{EMBED_MODEL}/embed"
    payload = {
        "content": "This is a document about Retrieval Augmented Generation."
    }
    try:
        r = requests.post(url, json=payload, headers=HEADERS)
        # Note: Success depends on whether you have pulled the model
        print_result("EMBEDDINGS", r.status_code == 200, r.json())
    except Exception as e:
        print(f"Request failed: {e}")

def test_rejection_chat():
    print(f"Testing REJECTION (Illegal Chat request to Embedding Model)...")
    url = f"{GATEWAY_URL}/models/{EMBED_MODEL}/generate"
    payload = {"prompt": "Hello"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS)
        # We expect a 400 rejection
        print_result("REJECT CHAT-BY-EMBED", r.status_code == 400, r.json())
    except Exception as e:
        print(f"Request failed: {e}")

def test_rejection_embed():
    print(f"Testing REJECTION (Illegal Embed request to Chat Model)...")
    url = f"{GATEWAY_URL}/models/{CHAT_MODEL}/embed"
    payload = {"content": "Hello"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS)
        # We expect a 400 rejection
        print_result("REJECT EMBED-BY-CHAT", r.status_code == 400, r.json())
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting AI Gateway Security & Role Validation Test...")
    
    test_chat()
    test_embed()
    test_rejection_chat()
    test_rejection_embed()
    
    print(f"\n{'-'*50}\nTests Complete.")
