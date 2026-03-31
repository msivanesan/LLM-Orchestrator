import requests, json, traceback

base = 'http://localhost:5004'

# 1. Health (no auth)
r = requests.get(f'{base}/api/chat/health', timeout=5)
print('Health:', r.status_code, r.text[:200])

# 2. Login via user service
r2 = requests.post('http://localhost/api/users/login',
    json={'username':'admin','password':'1234'}, timeout=10)
token = r2.json().get('access_token','')
print('Token:', bool(token), token[:30] if token else 'NONE')

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 3. List sessions (authenticated, non-streaming)
r3 = requests.get(f'{base}/api/chat/sessions', headers=headers, timeout=10)
print('Sessions:', r3.status_code, r3.text[:300])

# 4. Create session (authenticated, non-streaming)
r4 = requests.post(f'{base}/api/chat/sessions',
    headers=headers, json={'title':'test','model':'llama3-7b'}, timeout=10)
print('Create session:', r4.status_code, r4.text[:300])

# 5. Quick-stream
r5 = requests.post(f'{base}/api/chat/quick-stream',
    headers=headers, json={'content':'hello','model':'llama3-7b'},
    timeout=30, stream=True)
print('Quick-stream status:', r5.status_code)
if r5.status_code != 200:
    print('Body:', r5.text[:500])
else:
    for i, line in enumerate(r5.iter_lines()):
        if line:
            print('LINE:', line.decode()[:200])
        if i > 10: break
