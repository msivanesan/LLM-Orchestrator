# 🛠️ Operational Command Guide

This guide contains the common terminal commands required to run, debug, and maintain the LLM Orchestrator ecosystem.

---

## 1. Starting the Microservices (Native Python)
Each service must be run from the root of the project with the virtual environment activated.

### 🆔 User Service
```bash
.\venv\Scripts\python -m user.manage runserver
```

### 🔑 ApiKey Service
```bash
.\venv\Scripts\python -m apikey.manage runserver
```

### 🤖 AI Proxy Service
```bash
.\venv\Scripts\python -m ai.manage runserver
```

### 💬 Chat Service
```bash
.\venv\Scripts\python -m chat.manage runserver
```

---

## 2. Infrastructure & Containers (Docker)
Ensure Docker Desktop is running before executing these.

### Start All Infrastructure (Redis, Postgres, ChromaDB, Nginx, APM)
```bash
docker compose up -d
```

### View Logs for Specific Service
```bash
docker logs <container_name> --tail 50 -f
# Examples: 
# docker logs llm_ollama
# docker logs llm_orchestrator_gateway
# docker logs llm_alertmanager
```

### Clean Up Resources
```bash
docker compose down -v  # Warning: -v deletes database volumes!
```

---

## 3. Local AI Management (Ollama)

### Check Downloaded Models
```bash
docker exec llm_ollama ollama list
```

### Pull a New Model
```bash
docker exec llm_ollama ollama pull llama3.2:1b
docker exec llm_ollama ollama pull qwen2.5:0.5b
```

### Monitor Resource Usage
```bash
docker stats llm_ollama
```

---

## 4. APM & Monitoring Endpoints

| Component | Local URL | Purpose |
|-----------|-----------|---------|
| **Nginx Gateway** | http://localhost:80 | Main API Entry Point |
| **Prometheus** | http://localhost:9090 | Metrics & Queries |
| **Grafana** | http://localhost:3000 | Dashboards (u: admin / p: password) |
| **Alertmanager** | http://localhost:9093 | Active Alerts |
| **Ollama API** | http://localhost:11434 | Direct LLM Access |

---

## 5. Troubleshooting Commands

### Reset/Update Database (via Flask Migrations)
```bash
.\venv\Scripts\python -m user.manage db upgrade
.\venv\Scripts\python -m chat.manage db upgrade
```

### Check Backend Health Check API
```bash
curl http://localhost:5004/api/chat/health
```

### Clear Redis Cache (Keys & RPM)
```bash
docker exec llm_redis redis-cli FLUSHALL
```
