# 💬 Chat & Persistence Service

The Chat Service is the stateful orchestration layer of the LLM ecosystem. It manages individual user sessions, real-time streaming, and the primary integration with the Vector Store (RAG).

## 🚀 Key Features
-   **SSE Streaming**: High-performance Server-Sent Events for real-time AI tokens.
-   **Durable Context**: Automatically manages Rolling Window Context and Semantic Context (ChromaDB retrieval).
-   **Automatic Title Generation**: Uses the LLM to summarize new chat sessions into human-readable titles.
-   **Memory Extraction**: Performs background extraction of user facts (e.g., name, skills) to provide infinite cross-session memory.

## 🛠️ Configuration
Required in `.env`:
-   `CHAT_DATABASE_URL`: Connection string (PostgreSQL).
-   `REDIS_URL`: Shared caching and context window layer.
-   `AI_ENGINE_URL`: Downstream inference engine (Ollama/vLLM).
-   `CHROMA_HOST`: Vector DB for semantic searching.

## 🏃 Operation
### Start the Service (Standalone)
```powershell
cd chat
python .\manage.py runserver
```

### Production Mode
```powershell
python .\manage.py runprod
```

## 📡 Notable Endpoints
-   `POST /api/chat/quick-stream`: Lazy-creation of a session and streaming of the first response.
-   `POST /api/chat/sessions/<id>/stream`: Token-by-token streaming for existing threads.
-   `GET /api/chat/sessions`: List active and archived user conversations.
-   `GET /api/chat/memory`: Retrieve extracted long-term user context.
