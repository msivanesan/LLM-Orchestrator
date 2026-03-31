# Application Architecture & Data Flow

This document outlines the complete end-to-end architecture, API lifecycle, and database flow of the LLM Orchestrator platform.

## 1. System Components
The application is built on a distributed microservices architecture, stitched together by an Nginx API Gateway.

### Core Services
1. **Frontend (React/Vite)**: Runs on localhost targeting the Gateway. Handles UI, streaming Server-Sent Events (SSE), and JWT storage.
2. **API Gateway (Nginx)**: Runs on port `80`. Routes `/api/users/*` to the User service, `/api/chat/*` to the Chat service, etc. Handles CORS and header forwarding.
3. **User Service (Flask - Port 5001)**: Manages authentication, JWT minting, and User Profiles.
4. **Chat Service (Flask - Port 5004)**: The core stateful service. Manages streaming, session persistence, vector retrieval, and long-term memory extraction.
5. **AI Proxy Service (Flask - Port 5003)**: Acts as an abstraction layer between the application and the local/remote LLM engines. 
6. **Local LLM Engine (Ollama - Port 11434)**: Runs the actual AI models natively. Fully OpenAI `/v1/chat/completions` API compatible (swappable with vLLM).

---

## 2. Typical API Request Flow (Sending a Chat Message)

When a user types a message and clicks "Send", the following sequence occurs:

1. **Frontend Request**: The React app sends a `POST /api/chat/quick-stream` (or `/sessions/{id}/stream`) HTTP request. This request includes the user's prompt and their `Bearer <JWT>` token.
2. **Gateway Routing**: Nginx intercepts the request on port `80`. It sees the `/api/chat` prefix and proxies the raw TCP stream to the Chat Service container (`localhost:5004`), keeping the connection open for chunked streaming.
3. **Authentication Boundary**: 
   - The Chat Service uses `@jwt_required()` to decode the Bearer token.
   - It identifies the user ID and ensures they own the chat session.
4. **Context Assembly**:
   - The Chat Service looks up the user's long-term persistent "Memory" (extracted facts about the user).
   - It retrieves the last `Max_CTX_Messages (e.g., 20)` from the PostgreSQL `chat_messages` table to build short-term chat history.
   - It builds a complex `system_prompt` containing formatting instructions and injected memory.
5. **LLM Execution**:
   - The Chat Service calls the AI Engine URL natively (`http://localhost:11434/v1/chat/completions`).
   - It passes exactly the model name requested (e.g., `llama3.2:1b`), the system prompt, and the messages with `stream=True`.
6. **Streaming Response**:
   - Ollama streams back tokens. 
   - The Chat Service captures these chunks, buffers them locally, and uses standard Server-Sent Events (`yield f"data: {{...}}\n\n"`) to stream them back to Nginx, passing instantly to the React frontend.
7. **Post-Completion Hook**:
   - Once Ollama outputs `[DONE]`, the stream generator drops to a post-processing block.
   - The newly generated full AI response is committed to the PostgreSQL `chat_messages` database.
   - The UI finishes the chunked layout.
   - **Background Memory Job**: The `_post_send` block seamlessly fires off a background sub-thread that recursively runs an LLM parser to extract new user preferences/facts to insert into the User Profile DB.

---

## 3. Database Architecture & Flow

The system employs a polyglot persistence strategy, using three different database engines for specific use-cases.

### PostgreSQL (Relational Master State)
- **Role**: Source of truth for users, chat histories, API keys, and extracted memories.
- **Workflow**: 
  - All Flask microservices connect to it via `SQLAlchemy`. 
  - Standard CRUD API patterns (Create Session -> Save Message -> Select Messages).
  - Designed for heavy read/writes on strictly schema'd data.

### Redis (High-Speed Cache & Ephemeral State)
- **Role**: Rate limiting, quick caching, and API Key verifications.
- **Workflow**: 
  - Nginx uses the `APIKey Service` (via internal `/auth` requests) to validate keys. To prevent DB spam, the service checks Redis first.
  - Used for storing high-frequency reads (e.g., cached user sessions lists) to speed up initial page loads.

### ChromaDB (Vector Database)
- **Role**: Semantic search and Retrieval-Augmented Generation (RAG).
- **Workflow**:
  - Unstructured files (like PDFs or codebase docs) are split, embedded as floating-point tensors, and shoved into Chroma.
  - When a user asks a factual question, the backend translates the question into a vector mapping, queries Chroma for mathematical nearness using **Inner Product (Dot Product)**, and injects those documents into the active context above.

---

## 4. APM & Observability Flow

All microservices are observable via standard APM stacks.

- **Metrics Ingestion**: Flask services use `prometheus-flask-exporter` to intercept HTTP start/end times.
- **Scraping**: The Prometheus container pings each service's `/metrics` endpoint every 15s.
- **Alerting**: If LLM Error rates spike, Prometheus ships an event to AlertManager, which emails the dev team or raises a PagerDuty incident.
- **Grafana Data**: Queries Prometheus TSDB directly to render live visual charts.
