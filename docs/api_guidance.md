# AI Gateway: API Guidance for Agents

This document provides technical guidance for external agents and developers connecting to the AI Gateway.

## 1. Authentication
All requests must include your designated API key in the `X-API-KEY` header.
> [!IMPORTANT]
> Do not use `Bearer` tokens. The gateway specifically expects the `X-API-KEY` header.

**Header Example:**
```http
X-API-KEY: ak_your_key_here
Content-Type: application/json
```

---

## 2. Model Discovery
Retrieve a list of available models and their capabilities.
- **Endpoint**: `GET /api/ai/models`

**Example Request:**
```bash
curl -X GET http://<gateway-ip>/api/ai/models \
     -H "X-API-KEY: ak_..."
```

---

## 3. Generative AI (Text Generation)
Use this endpoint for chat, reasoning, or content creation.
- **Endpoint**: `POST /api/ai/models/<model_id>/generate`
- **Enforcement**: Only generative models (e.g., `tinyllama`, `llama3`) are allowed.

**Request Body:**
| Field | Type | Description |
| :--- | :--- | :--- |
| `messages` | array | **Required**. List of message objects `{"role": "user", "content": "..."}`. |
| `temperature` | float | **Optional**. Control randomness (default: 0.7). |
| `max_tokens` | int | **Optional**. Maximum tokens to generate (default: 1024). |

**cURL Example:**
```bash
curl -X POST http://<gateway-ip>/api/ai/models/tinyllama/generate \
     -H "X-API-KEY: ak_..." \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [{"role": "user", "content": "Explain RAG in one sentence."}],
       "temperature": 0.5
     }'
```

---

## 4. Semantic Search (Embeddings)
Use this endpoint to generate vector embeddings for RAG (Retrieval-Augmented Generation).
- **Endpoint**: `POST /api/ai/models/<model_id>/embed`
- **Enforcement**: Only embedding models (e.g., `nomic-embed-text`) are allowed.

**Request Body:**
| Field | Type | Description |
| :--- | :--- | :--- |
| `input` | string/array | The text to turn into a vector. |

**cURL Example:**
```bash
curl -X POST http://<gateway-ip>/api/ai/models/nomic-embed-text/embed \
     -H "X-API-KEY: ak_..." \
     -H "Content-Type: application/json" \
     -d '{
       "input": "This is a document about machine learning."
     }'
```

---

## 5. Security Rejections
The gateway enforces strict model roles. If you attempt to use the wrong model for a task, you will receive a `400 Bad Request` with a `ModelRoleMismatch` error.

**Error Response Example:**
```json
{
  "error": "Model 'nomic-embed-text' is a dedicated embedding model and cannot be used for text generation.",
  "type": "ModelRoleMismatch"
}
```
