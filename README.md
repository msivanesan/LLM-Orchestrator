# 🌌 LLM-Orchestrator: Enterprise AI Microservice Ecosystem

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React: 18+](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

A production-hardened, high-performance microservice architecture designed for secure AI model orchestration, centralized identity management, persistent LLM memory, and comprehensive APM observability. Built to bridge the gap between volatile local prototypes and stable enterprise deployments.

---

## 🏗️ System Architecture

LLM-Orchestrator utilizes a **Gateway-First** design pattern with a suite of highly cohesive Python Flask microservices and a React (Vite) frontend.

```mermaid
graph TD
    %% Entry Points
    User((User/Client)) -->|HTTPS:80| GW[Nginx Gateway]
    
    subgraph "Core Microservices"
        US[User Service:5001]
        AS[ApiKey Service:5002]
        AI[AI Service:5003]
        CS[Chat Service:5004]
    end

    subgraph "Durable Infrastructure"
        R[(Redis Shared State)]
        DB[(PostgreSQL Primary Persistence)]
        VC[(ChromaDB Vector Store)]
    end

    subgraph "Observability (APM)"
        PR[Prometheus]
        GR[Grafana]
        AM[Alertmanager]
    end

    subgraph "External Inference"
        OL[Ollama Edge GPU Engine]
    end

    %% Flow logic
    GW -->|/api/users| US
    GW -->|/api/apikeys| AS
    GW -->|/api/chat| CS
    
    %% AI / Chat Logic
    CS <-->|Semantic Search| VC
    CS -->|Proxy Models| AI
    CS <-->|Direct Completion| OL
    AI <-->|Monitor Models| OL
    
    %% Auth Sidecar Logic
    AI -.->|Auth Request| AS
    
    %% Metrics
    PR -.->|Scrapes /metrics| US
    PR -.->|Scrapes /metrics| AS
    PR -.->|Scrapes /metrics| CS
    PR -.->|Scrapes /metrics| AI
```

---

## 🌟 Key Features

### 🧠 Persistent LLM Memory & RAG
- **Background Extraction**: The Chat Service automatically parses conversations in the background to extract user facts (name, preferences, habits) and stores them in a memory key-value DB.
- **Dynamic Context Injection**: Memories are automatically injected into the LLM `system_prompt` so the AI remembers the user infinitely across all future sessions.
- **ChromaDB Vector Search**: Chat histories are mathematically embedded (`all-MiniLM-L6-v2`) and stored in ChromaDB using fast dot-product (Inner Product) indexing for sub-second semantic retrieval.

### ⚡ Local Edge Inference
- **Ollama Integration**: Powered by local open-source models (like `llama3.2:1b` and `qwen2.5:0.5b`) running instantly on-device.
- **vLLM Ready**: Exposes standard OpenAI `/v1/chat/completions` APIs. To scale to a cluster, you simply point the URL to vLLM without changing a single line of backend code.
- **Dynamic Model Discovery**: The UI polls the proxy layer for actively downloaded models in real-time.

### 📊 Full-Stack APM & Observability
- **Prometheus Scrapers**: Unified metrics wrappers across all microservices. Tracks `http_request_duration`, token counts, DB connection times, and latency.
- **Grafana Live Dashboards**: Instant cross-service visualization.
- **AlertManager**: Tracks error-rate thresholds and security alerts (brute-force protection limits), configured to route to incident response channels.

### 🛡️ Nginx API Gateway
- **Centralized Security**: Manages CORS policy and Reverse Proxying across all services.
- **Streaming Ready**: Tuned with chunked transfer encoding and disabled buffering to support high-speed LLM Server-Sent Events (SSE).

---

## 🛰️ Microservice Deep-Dive

### 💬 Platform Services (Ports 5001-5004)
The ecosystem consists of five independent services, each with its own management layer:
1. **🆔 User Service (5001)**: Identity provider using PostgreSQL.
2. **🔑 ApiKey Service (5002)**: Integration & Rate-Limiting.
3. **🤖 AI Service (5003)**: Model Orchestration & Discovery.
4. **💬 Chat Service (5004)**: Persistent Memory & RAG.
5. **📬 Mailer Service**: Background Redis Worker for communications.

---

## 🚀 Installation & Deployment

### 1. Requirements
Ensure you have **Python 3.12+**, **PostgreSQL**, **Redis**, and **Ollama** (or vLLM) installed.

### 2. Environment Setup
```bash
git clone https://github.com/msivanesan/LLM-Orchestrator.git
cd LLM-Orchestrator
```
Populate `.env` with your PostgreSQL URIs:
```env
USER_DATABASE_URL=postgresql://user:pass@localhost:5432/llm_db
APIKEY_DATABASE_URL=postgresql://user:pass@localhost:5432/llm_db
REDIS_URL=redis://localhost:6379/0
AI_ENGINE_URL=http://localhost:11434/v1/chat/completions
```

### 3. Start Infrastructure
Boot the gateway and monitoring stack:
```bash
docker compose up -d
```

### 4. Run Microservices (Standalone Mode)
Each service can now be run independently from its own directory:
```bash
# Identity Service
cd user && python .\manage.py runserver

# Persistence Layer
cd chat && python .\manage.py runserver

# AI Proxy
cd ai && python .\manage.py runserver

# Integration Layer
cd apikey && python .\manage.py runserver
```

### 5. Start the React Frontend
```bash
# From root
cd frontend && npm install && npm run dev
```

---

## 📂 Project Structure
```text
.
├── ai/             # AI Proxy Service (Flask)
├── apikey/         # API Key & Rate Limit Service (Flask)
├── chat/           # Streaming / Memory / RAG Service (Flask)
├── user/           # Identity & Profile Service (Flask)
├── frontend/       # React (Vite) Chat Dashboard UI
├── monitoring/     # APM Rules (Prometheus/Grafana/Alertmanager)
├── nginx/          # API Gateway Configuration
├── command/        # Deep-dive architectural flowcharts
├── docker-compose.yml
└── .env            # Centralized Configuration
```

---

&copy; 2026 LLM Orchestration Infrastructure | Designed for Stability, Built for Scale.
