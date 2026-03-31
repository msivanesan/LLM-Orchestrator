# 🕸️ Nginx API Gateway

The Nginx Gateway is the high-performance entry point for the entire microservice ecosystem. It handles reverse proxying, CORS enforcement, and integrates with the **Auth Sidecar** to secure sensitive routes.

## 🚀 Key Features
-   **Centralized Routing**: Proxies `/api/users`, `/api/apikeys`, and `/api/ai` to their respective services.
-   **Auth Sidecar**: Uses `auth_request` on AI routes to ensure every LLM request has a valid, rate-limited API key.
-   **Performance Tuning**: Increased `proxy_read_timeout` (300s) to handle long-running generative AI responses.
-   **Security Headers**: Enforces CORS and provides consistent error handling for downstream service failures.

## 🛠️ Configuration
-   `conf.d/default.conf`: The main configuration file defining service upstreams and location blocks.

## 🏃 Operation
Ensure Nginx is running and pointing to this configuration directory. Any changes to the configuration require a reload:
```bash
nginx -s reload
```

## 🏗️ Internal Routing Logic
-   `80/` -> Gateway Entry
-   `80/api/users` -> `user-service:5001`
-   `80/api/apikeys` -> `apikey-service:5002`
-   `80/api/ai` -> `ai-service:5003` (Secured via `auth_request`)
