# 🤖 AI Orchestration Service

The AI Orchestration Service is a Gemini-compatible middleware that manages interactions with external inference engines (like Ollama or vLLM). It provides a unified API for model discovery and generation while integrating with the ecosystem's security and rate-limiting layers.

## 🚀 Key Features
-   **Model-Specific Endpoints**: Support for `/api/ai/models/<id>/generate` and generic `/api/ai/v1/chat/completions`.
-   **Ollama Integration**: Configured to proxy requests to an external GPU-powered Ollama instance.
-   **Auth Request Compatibility**: Designed to work with Nginx `auth_request` for API key validation.

## 🛠️ Configuration
The service uses the following environment variables:
-   `AI_ENGINE_URL`: The URL of the external inference engine (e.g., `https://192.168.5.23/ai/v1/chat/completions`).
-   `AI_SERVICE_PORT`: Port to run the Flask app (Default: 5003).

## 🏃 Operation
### Start the Service
```bash
python -m ai.manage runserver
```

## 📡 API Endpoints
-   `GET /api/ai/models`: List available models.
-   `POST /api/ai/models/<model_id>/generate`: Generate a completion using a specific model.
-   `POST /api/ai/v1/chat/completions`: OpenAI-compatible chat completion endpoint.
