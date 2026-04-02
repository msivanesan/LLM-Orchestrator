# AI Gateway Service — Internal README

The AI Service acts as a production-hardened, strictly enforcing proxy between external agents and the private LLM engine (Ollama). It provides standardized endpoints for generative AI and semantic embeddings while preventing model-task mixing through strict role-based validation.

---

## Architecture

```
External Agent
      │  X-API-KEY header
      ▼
 Nginx Gateway  ──── auth_request ──► ApiKey Service (5002)
      │
      ▼
 AI Gateway (5003)
      │  Role validation
      │  Model cache (12h TTL)
      ▼
 Ollama Engine (11434)
```

- **Tech Stack**: Flask, Requests, Gunicorn.
- **Upstream**: Connects to `llm_ollama:11434` (Internal OpenAI-compatible API).
- **Ingress**: Exposed via the Nginx Gateway for authentication and rate limiting.

---

## Endpoints

| Method | Path | Description |
| :----- | :--- | :---------- |
| `GET` | `/models` | List all available models with their roles. Cached for 12 hours. |
| `POST` | `/models/<model_id>/generate` | Text generation. Rejects embedding-only models. |
| `POST` | `/models/<model_id>/embed` | Vector embeddings. Rejects chat/generative models. |

All endpoints require a valid `X-API-KEY` header (enforced at the Nginx layer).

---

## Key Features

1. **Model-Role Enforcement**:
    - **Generate endpoint**: Rejects embedding-only models (e.g., `nomic-embed-text`) with a `400 ModelRoleMismatch` error.
    - **Embed endpoint**: Rejects chat/generative models (e.g., `tinyllama`) with a `400 ModelRoleMismatch` error.

2. **12-Hour Model Cache**: The model list is fetched from Ollama once and cached in memory for 12 hours. Reduces overhead on the Ollama API.

3. **Token Usage Tracking**: All responses include a `usage` field with `prompt_tokens`, `completion_tokens`, and `total_tokens` for downstream agent monitoring.

4. **Chat UI Filtering**: Embedding-only models are automatically excluded from the Chat Service's model dropdown so they never appear in the UI.

---

## Environment Variables

| Variable | Default | Purpose |
| :------- | :------ | :------ |
| `AI_ENGINE_URL` | `http://ollama:11434/v1/chat/completions` | Ollama completions endpoint. |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama base URL for model listing. |
| `AI_SERVICE_TIMEOUT` | `120` | Request timeout in seconds. |

---

## Pulling Models into Ollama

After spinning up the stack, pull models into the Ollama engine before making any requests.

### Pull a generative model (for `/generate`)
```bash
docker exec -it llm_ollama ollama pull tinyllama
```

### Pull an embedding model (for `/embed`)
```bash
docker exec -it llm_ollama ollama pull nomic-embed-text
```

### List all pulled models
```bash
docker exec -it llm_ollama ollama list
```

> **Tip**: You can use any model from [ollama.com/library](https://ollama.com/library). Generative models include `llama3`, `mistral`, `gemma2`, `tinyllama`. Embedding models include `nomic-embed-text`, `mxbai-embed-large`.

---

## Maintenance Tasks

### Clearing the Model Cache
The model list is cached in-process for 12 hours. To force a refresh before TTL expires, restart the service:
```bash
docker compose restart ai
```

### Viewing Logs
```bash
docker compose logs -f ai
```

### Running the Test Suite
From the project root:
```bash
python test_ai_gateway.py
```
The test suite validates:
- Chat generation with a generative model ✅
- Embedding with an embedding model ✅
- Rejection of embedding model used for generation ✅
- Rejection of generative model used for embedding ✅

---

## Error Reference

| HTTP Status | Error Type | Cause |
| :---------- | :--------- | :---- |
| `401` | `Unauthorized` | Missing or invalid `X-API-KEY` header. |
| `400` | `ModelRoleMismatch` | Wrong model type for the requested task. |
| `404` | `ModelNotFound` | Requested model is not present in Ollama. |
| `500` | `InternalError` | Upstream Ollama failure or network error. |
