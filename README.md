# 🌌 LLM-Orchestrator: Enterprise AI Microservice Ecosystem

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React: 18+](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

A production-hardened, high-performance microservice architecture for secure AI model orchestration, centralized identity management, persistent LLM memory, and comprehensive APM observability. All traffic enters through a single **Nginx Gateway** — no backend service is exposed directly to the host.

---

## 🏗️ Project Analysis & Architecture

The LLM-Orchestrator is a modular ecosystem designed to handle complex AI workloads with a focus on security, scalability, and observability.

### System Components:
- **Nginx Gateway**: Acts as the single entry point, handling SSL termination (if configured), rate limiting, and request routing.
- **User Service**: Manages user identity, JWT-based authentication, and profile management.
- **ApiKey Service**: Issues and validates API keys for programmatic access to the AI models.
- **AI Gateway**: A smart proxy for LLM engines (Ollama/vLLM). It enforces model-role constraints (Generative vs. Embedding) and tracks token usage.
- **Chat Service**: Provides persistent chat history, long-term memory via key-value stores, and Retrieval-Augmented Generation (RAG) using ChromaDB.
- **Mailer**: Asynchronous background worker for email notifications (OTPs, system alerts).
- **Monitoring Stack**: Prometheus and Grafana for real-time metrics, coupled with Alertmanager for proactive system health monitoring.

---

## 🛠️ Performance Scaling (Ollama to vLLM)

For high-throughput production environments, you may want to migrate from **Ollama** to **vLLM**.

👉 **[View the Migration Guide (MIGRATION_VLLM.md)](./MIGRATION_VLLM.md)**

---

## 🚀 Getting Started

### 1. Requirements
- **Hardware**: 16GB+ RAM (32GB+ recommended for large models).
- **Software**: Docker & Docker Compose.
- **GPU (Optional but Recommended)**: NVIDIA Container Toolkit for accelerated inference.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/msivanesan/LLM-Orchestrator.git
cd LLM-Orchestrator

# Setup environment variables
cp .env.example .env
```

### 3. Start the Ecosystem
By default, the project uses **Ollama** as the inference engine.
```bash
docker compose up -d
```

---

## 🧠 LLM Runtimes: Ollama vs vLLM

This project supports two primary inference engines. Choose the one that fits your hardware and scaling needs.

### 🔹 Ollama (Default)
**Best for**: Local development, workstations without high-end GPUs.
- **Advantages**: 
  - Dynamic model swapping (loads/unloads automatically).
  - Supports CPU, Apple Silicon, and all standard GPUs.
  - Native support for embedding models (e.g., `nomic-embed-text`).
- **Requirements**: 8GB+ RAM. No strict GPU requirement.

### 🔹 vLLM (Production Ready)
**Best for**: High-throughput production environments and large-scale deployments.
- **Advantages**:
  - **PagedAttention**: Dramatically higher throughput.
  - **Continuous Batching**: Efficiently processes multiple users simultaneously.
  - Supports **Multi-LoRA** (multiple adapters on a single base model).
- **Requirements**: Dedicated NVIDIA GPU (CUDA), higher VRAM (12GB+). 
- **Constraint**: Serves only **one base model** per instance.

---

## 📥 Managing Models

### Pulling Models for Ollama
Once the stack is running, you must manually pull models into the Ollama container:
```bash
# Pull a generative/chat model
docker exec -it llm_ollama ollama pull llama3

# Pull an embedding model (Essential for RAG)
docker exec -it llm_ollama ollama pull nomic-embed-text

# List installed models
docker exec -it llm_ollama ollama list
```

### Pulling Models for vLLM
vLLM handles model downloads automatically when the container starts. You specify the model in the `command` section of `vllm.fragment.yml`.
- The model is downloaded from HuggingFace.
- Ensure you have enough disk space in the `vllm_cache` volume.

---

## ⚙️ Switching from Ollama to vLLM

To transition from the lightweight Ollama engine to the high-performance vLLM engine, follow these steps:

### 1. Update Docker Configuration
Modify the `include` section at the top of your `docker-compose.yml`:
```yaml
include:
  # - path: ollama.fragment.yml  <-- Comment this
  - path: vllm.fragment.yml     <-- Uncomment this
```

### 2. Update Environment Variables
Edit your `.env` file to point the services to the new vLLM endpoint (defaulting to port 8000):
```env
AI_ENGINE_URL=http://vllm:8000/v1/chat/completions
OLLAMA_BASE_URL=http://vllm:8000
```

### 3. Customize the Model
Open `vllm.fragment.yml` and modify the `--model` flag in the `command` section to your desired HuggingFace model (e.g., `mistralai/Mistral-7B-Instruct-v0.3`).

### 4. Code Adjustments (Discovery)
vLLM does not use the `/api/tags` endpoint found in Ollama. If you encounter issues with the UI model list:
- The **AI Gateway** fetches models from `OLLAMA_BASE_URL/api/tags`.
- For vLLM, you may need to manually update the `list_models` function in `ai/routes.py` to use `v1/models` or provide a static list.

### 5. Deployment
Restart the stack to apply changes:
```bash
docker compose down
docker compose up -d
```

---

## 📂 Project Structure Overview

| Directory | Responsibility |
| :--- | :--- |
| `ai/` | Smart AI Gateway with token tracking and role enforcement. |
| `user/` | User management and security. |
| `chat/` | Conversational logic, memory, and RAG integration. |
| `frontend/` | React-based interactive dashboard. |
| `monitoring/` | Prometheus, Grafana, and Alerting configurations. |
| `nginx/` | Unified entry point and security layer. |

---

© 2026 LLM Orchestration Infrastructure | Designed for Stability, Built for Scale.
