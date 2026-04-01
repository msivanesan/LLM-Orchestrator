# 🔑 ApiKey & Rate Limiting Service

This service manages external API credentials and enforces usage policies across the ecosystem. It features a high-performance rate-limiting engine powered by Redis.

## 🚀 Key Features
-   **API Key Management**: Create, toggle, and delete keys with custom rate limits (RPM).
-   **Redis-based Rate Limiting**: Sub-millisecond latency for quota checks.
-   **Memory Efficiency**: Automatically expires rate-limit data using Redis TTL to prevent memory leaks.
-   **Auth Sidecar Support**: Provides the `/api/apikeys/validate_header` endpoint used by Nginx to authorize incoming requests.

## 🛠️ Configuration
Required in `.env`:
-   `APIKEY_DATABASE_URL`: Connection string (PostgreSQL).
-   `REDIS_URL`: Shared caching and rate-limiting store.
-   `APIKEY_SERVICE_PORT`: Defaults to 5002.

## 🏃 Operation
### Start the Service (Standalone)
```powershell
cd apikey
python .\manage.py runserver
```

### Production Mode
```powershell
python .\manage.py runprod
```

## 📡 Notable Endpoints
-   `POST /api/apikeys/validate_header`: Fast-path validation for Nginx `auth_request`.
-   `GET /api/apikeys/me`: Get status of the provided key.
-   `POST /api/apikeys/create`: Register a new API key.
