import requests
import time

# --- CONFIGURATION ---
API_KEY = "ak_9b8c02cc0e0add6ac78e26a789c74a189cb0a7b0179f795d"
GATEWAY_URL = "http://localhost/external/"

def test_api_access(key):
    headers = {"X-API-KEY": key}
    
    print(f"🚀 Starting Test for Key: {key[:10]}...")
    print("-" * 50)
    
    # Test 1: Single Authorized Request
    print("Test 1: Normal Authorized Request")
    try:
        response = requests.get(GATEWAY_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)
    
    # Test 2: Unauthorized Request (Missing Header)
    print("Test 2: Unauthorized Request (No Header)")
    try:
        response = requests.get(GATEWAY_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")

    print("-" * 50)

    # Test 3: Rate Limiting Stress Test
    # (Sending 10 requests in a row to hit the RPM limit)
    print("Test 3: Rate Limiting Stress Test (10 requests)")
    for i in range(1, 11):
        try:
            response = requests.get(GATEWAY_URL, headers=headers)
            print(f"Request {i}: Status {response.status_code}")
            if response.status_code == 429:
                print("🚫 SUCCESS: Rate Limit Hit (429)!")
        except Exception as e:
            print(f"Error: {e}")
            break
            
    print("-" * 50)
    print("🏁 Tests Completed!")

if __name__ == "__main__":
    test_api_access(API_KEY)
