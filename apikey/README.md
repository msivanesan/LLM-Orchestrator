# 🔑 ApiKey & Rate Limiting Service

This service manages external API credentials and enforces usage policies across the ecosystem. It features a high-performance rate-limiting engine powered by Redis.

## 🚀 Key Features
-   **API Key Management**: Create, toggle, and delete keys with custom rate limits (RPM).
-   **Redis-based Rate Limiting**: Sub-millisecond latency for quota checks.
-   **Memory Efficiency**: Automatically expires rate-limit data using Redis TTL to prevent memory leaks.
-   **Auth Sidecar Support**: Provides the `/api/apikeys/validate_header` endpoint used by Nginx to authorize incoming requests.

## 🛠️ Configuration
Required in `.env`:
-   `REDIS_URL`: Link to your Redis instance.
-   `APIKEY_DATABASE_URL`: Path to the SQLite/PostgreSQL database.
-   `APIKEY_SERVICE_PORT`: Defaults to 5002.

## 🏃 Operation
### Start the Service
```bash
python -m apikey.manage runserver
```

## 📡 Notable Endpoints
-   `POST /api/apikeys/validate_header`: Fast-path validation for Nginx `auth_request`.
-   `GET /api/apikeys/me`: Get status of the provided key.
-   `POST /api/apikeys/create`: Register a new API key.
