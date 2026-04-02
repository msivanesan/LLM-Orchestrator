# AI Gateway Service (Internal README)

The AI Service acts as a high-performance, strictly blocking proxy between external agents and the private LLM engine (Ollama). It provides standardized endpoints for generative AI and semantic embeddings while enforcing strict task-to-model role separation.

## Architecture
- **Tech Stack**: Flask, Requests, Gunicorn.
- **Upstream**: Connects to `llm_ollama:11434` (Internal OpenAI-compatible API).
- **Ingress**: Exposed via the Nginx Gateway (`llm_orchestrator_gateway`) for authentication and rate limiting.

## Key Features
1. **Model Discovery & Caching**: Models are discovered dynamically from Ollama. The list is cached for **12 hours** to reduce overhead.
2. **Role Enforcement**:
    - **Generative Task**: Rejects embedding-only models (e.g., `nomic-embed-text`).
    - **Embedding Task**: Rejects chat/generative-only models (e.g., `llama3`).
3. **Metadata Enrichment**: Automatically extracts token usage (`usage`) and latency stats for agent tracking.

## Environment Variables
| Variable | Default | Purpose |
| :------- | :------ | :------ |
| `AI_ENGINE_URL` | `http://ollama:11434/v1/chat/completions` | Address of the LLM engine. |
| `AI_SERVICE_TIMEOUT` | `120` | Request timeout in seconds. |

---

## Maintenance Tasks
### Clearing Cache
To force-refresh the model list before the 12-hour TTL expires, restart the `ai` service:
```bash
docker compose restart ai
```

### Pulling a new Embedding model
For RAG workloads, pull a dedicated embedding model into the engine:
```bash
docker exec -it llm_ollama ollama pull nomic-embed-text
```
