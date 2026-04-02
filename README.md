# 🌌 LLM-Orchestrator: Enterprise AI Microservice Ecosystem

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React: 18+](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![AI Gateway](https://img.shields.io/badge/AI%20Gateway-Hardened-6366f1.svg)](./ai/README.md)

A production-hardened, high-performance microservice architecture for secure AI model orchestration, centralized identity management, persistent LLM memory, and comprehensive APM observability. All traffic enters through a single **Nginx Gateway** — no backend service is exposed directly to the host.

---

## 🏗️ System Architecture

```
                         ┌──────────────────────────────────┐
           HTTP :80      │         Nginx Gateway            │
  Client ──────────────► │  Rate Limiting · CORS · Auth     │
                         └──────────────┬───────────────────┘
                                        │
              ┌─────────────────────────┼──────────────────────┐
              │                         │                      │
              ▼                         ▼                      ▼
    /api/users  /api/auth     /api/ai  /api/chat        /api/apikeys
         │                       │          │                  │
         ▼                       ▼          ▼                  │
    User Service           AI Gateway  Chat Service       ApiKey Service
     (port 5001)           (port 5003)  (port 5004)       (port 5002)
         │                       │          │            (auth sidecar)
         │              ┌────────┘          │
         │              ▼                   ▼
         │         Ollama Engine       ChromaDB (RAG)
         │         (port 11434)        (port 8000)
         │
         └──────────────────────► PostgreSQL · Redis
```

---

## 🌐 Port Exposure Policy

Only the absolute minimum number of ports are exposed to the host machine. All backend services communicate over the internal Docker network.

| Service | Internal Port | Host Exposed | Reason |
| :------ | :------------ | :----------- | :----- |
| **Nginx Gateway** | 80 | ✅ **:80** | Only public entry point |
| **Grafana** | 3000 | ✅ **:3000** | Admin dashboard |
| **Prometheus** | 9090 | ✅ **:9090** | Admin metrics UI |
| **Alertmanager** | 9093 | ✅ **:9093** | Admin alert management |
| **PostgreSQL** | 5432 | ✅ **:5432** | Direct DB access for dev/migrations |
| User Service | 5001 | ❌ Internal | Proxied via Nginx `/api/users` |
| ApiKey Service | 5002 | ❌ Internal | Nginx auth sidecar only |
| AI Gateway | 5003 | ❌ Internal | Proxied via Nginx `/api/ai` |
| Chat Service | 5004 | ❌ Internal | Proxied via Nginx `/api/chat` |
| Redis | 6379 | ❌ Internal | Docker network only |
| ChromaDB | 8000 | ❌ Internal | Docker network only |
| Ollama | 11434 | ❌ Internal | Docker network only |
| Redis Exporter | 9121 | ❌ Internal | Scraped by Prometheus internally |

> **Note:** PostgreSQL (:5432) remains exposed for developer convenience (migrations, DB clients). Remove this mapping in a locked-down production environment.

---

## 🌟 Key Features

### 🤖 Hardened AI Gateway (v1.0)
- **Strict Model-Role Enforcement**: Generative and embedding models are strictly separated. Using the wrong model type returns a `400 ModelRoleMismatch` error.
- **API Key Authentication**: All external agent requests require a valid `X-API-KEY` header. Authentication is delegated to the ApiKey service via Nginx `auth_request`.
- **RAG-Compatible Embeddings**: Dedicated `/embed` endpoint for vector embedding workloads, compatible with ChromaDB and any vector store.
- **12-Hour Model Cache**: Model lists are cached in memory for 12 hours, reducing redundant Ollama API calls.
- **Token Usage Tracking**: All responses include a `usage` field (prompt/completion/total tokens) for agent monitoring.
- **Frontend API Docs**: A public `/docs` page in the React UI provides interactive cURL examples for all Gateway endpoints — no login required.

### 🧠 Persistent LLM Memory & RAG
- **Background Extraction**: The Chat Service automatically parses conversations to extract user facts (name, preferences) and stores them in a memory key-value store.
- **Dynamic Context Injection**: Memories are injected into the LLM `system_prompt` so the AI remembers users across all sessions.
- **ChromaDB Vector Search**: Chat histories are embedded and stored in ChromaDB using Inner Product indexing for sub-second semantic retrieval.

### ⚡ Local Edge Inference
- **Ollama Integration**: Powered by local open-source models (`tinyllama`, `llama3`, `mistral`, etc.) running on-device.
- **vLLM Ready**: Exposes standard OpenAI `/v1/chat/completions` APIs. To scale to a cluster, change the `AI_ENGINE_URL` env var — no code changes needed.
- **Dynamic Model Discovery**: The Chat UI automatically discovers available models in real-time. Embedding-only models are filtered from the chat dropdown.

### 📊 Full-Stack APM & Observability
- **Prometheus**: Unified metrics across all services — `http_request_duration`, token counts, DB connection times, error rates.
- **Grafana**: Live cross-service dashboards.
- **AlertManager**: Error-rate and brute-force thresholds with email/Slack routing.

### 🛡️ Nginx API Gateway
- **Single Ingress**: All traffic enters on port 80. No backend ports are exposed.
- **Auth Sidecar**: Nginx `auth_request` delegates API key validation to the ApiKey service before forwarding to AI endpoints.
- **Rate Limiting**: Configured at the Nginx layer.
- **Streaming Ready**: Chunked transfer encoding and disabled buffering for LLM SSE streaming.

---

## 🛰️ Microservice Deep-Dive

| Service | Port | Technology | Responsibility |
| :------ | :--- | :--------- | :------------- |
| **User Service** | 5001 | Flask + PostgreSQL | Identity, JWT auth, password reset via OTP |
| **ApiKey Service** | 5002 | Flask + PostgreSQL + Redis | API key issuance, validation, rate limiting |
| **AI Gateway** | 5003 | Flask + Gunicorn | Model proxy, role enforcement, embeddings, token tracking |
| **Chat Service** | 5004 | Flask + Gunicorn | Streaming chat, persistent memory, RAG via ChromaDB |
| **Mailer** | — | Redis Worker | Background email delivery (OTP, alerts) |

### AI Gateway Endpoints
| Method | Path | Auth | Description |
| :----- | :--- | :--- | :---------- |
| `GET` | `/api/ai/models` | `X-API-KEY` | List all models with roles. Cached 12h. |
| `POST` | `/api/ai/models/{id}/generate` | `X-API-KEY` | Text generation. Generative models only. |
| `POST` | `/api/ai/models/{id}/embed` | `X-API-KEY` | Vector embeddings. Embedding models only. |

---

## 🚀 Installation & Deployment

### 1. Requirements
- Docker & Docker Compose
- (Optional) NVIDIA Container Toolkit for GPU acceleration

### 2. Environment Setup
```bash
git clone https://github.com/msivanesan/LLM-Orchestrator.git
cd LLM-Orchestrator
cp .env.example .env
```
Edit `.env` with your configuration:
```env
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=llm_orchestrator
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
CHROMA_AUTH_TOKEN=your_chroma_token
```

### 3. Start the Stack
```bash
docker compose up -d
```

### 4. Pull Models into Ollama
After the stack is running, pull models into the Ollama engine:
```bash
# Pull a generative model (for chat / text generation)
docker exec -it llm_ollama ollama pull tinyllama

# Pull an embedding model (for RAG / semantic search)
docker exec -it llm_ollama ollama pull nomic-embed-text

# Verify all pulled models
docker exec -it llm_ollama ollama list
```

> **Tip:** Substitute `tinyllama` with any model from [ollama.com/library](https://ollama.com/library) (e.g., `llama3`, `mistral`, `gemma2`).

### 5. Enable GPU (Optional)
Uncomment the `deploy` block in `docker-compose.yml` under the `ollama` service:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### 6. Access the Services

| Service | URL |
| :------ | :-- |
| **Frontend / Chat UI** | `http://localhost` |
| **API Docs** (public) | `http://localhost/docs` |
| **Grafana Dashboards** | `http://localhost:3000` |
| **Prometheus** | `http://localhost:9090` |
| **Alertmanager** | `http://localhost:9093` |

---

## 📂 Project Structure

```text
.
├── ai/                          # AI Gateway (Flask + Gunicorn)
│   ├── routes.py                # /models, /generate, /embed endpoints
│   ├── Dockerfile
│   └── README.md                # Internal developer reference
│
├── apikey/                      # ApiKey & Rate-Limit Service (Flask)
│   ├── routes.py                # Key issuance, validation, Nginx auth sidecar
│   └── Dockerfile
│
├── chat/                        # Chat & Memory Service (Flask + Gunicorn)
│   ├── routes.py                # SSE streaming, RAG, conversation history
│   ├── llm_client.py            # Ollama client with model caching & filtering
│   └── Dockerfile
│
├── user/                        # Identity & Profile Service (Flask)
│   ├── routes.py                # JWT auth, registration, OTP password reset
│   └── Dockerfile
│
├── mailer/                      # Background Email Worker (Redis Queue)
│   └── Dockerfile
│
├── frontend/                    # React (Vite) Dashboard & Chat UI
│   └── src/
│       ├── pages/
│       │   ├── Chat.jsx          # Streaming AI chat interface
│       │   ├── Docs.jsx          # Public API documentation page (/docs)
│       │   ├── KeyList.jsx       # Admin: manage API keys
│       │   ├── KeyCreate.jsx     # Admin: create API keys
│       │   ├── UserList.jsx      # Admin: manage users
│       │   └── Login.jsx         # Authentication page
│       └── components/
│           └── Layout.jsx        # App shell with sidebar navigation
│
├── docs/
│   └── api_guidance.md          # External API reference (Markdown)
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml        # Scrape targets for all services
│   │   └── alerts/              # Alerting rules (error rates, latency)
│   ├── grafana/
│   │   ├── provisioning/        # Auto-provisioned datasources
│   │   └── dashboards/          # Pre-built Grafana dashboards
│   └── alertmanager/
│       └── alertmanager.yml     # Alert routing (email/Slack)
│
├── nginx/
│   └── conf.d/
│       └── default.conf         # Routing, rate limiting, auth_request, SSE config
│
├── docker-compose.yml           # Full stack orchestration
├── .env.example                 # Configuration template
└── apm.py                       # Shared APM metrics wrapper
```

---

## 🔧 Common Maintenance Commands

```bash
# View logs for a specific service
docker compose logs -f ai
docker compose logs -f chat

# Restart a service to clear its cache
docker compose restart ai

# Rebuild and redeploy a service after code changes
docker compose up -d --build ai

# Run the AI Gateway test suite
python test_ai_gateway.py

# Check all running containers
docker compose ps

# Pull a new model into Ollama
docker exec -it llm_ollama ollama pull <model-name>

# List all models in Ollama
docker exec -it llm_ollama ollama list
```

---

© 2026 LLM Orchestration Infrastructure | Designed for Stability, Built for Scale.
