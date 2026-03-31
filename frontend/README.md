# 🖥️ Admin Dashboard (React/Vite)

A high-fidelity, microservice-aware administrative interface to manage your entire platform, including AI Orchestration and API Gateway monitoring.

## 🚀 Key Features
-   **Service Aware**: Unified UI for Port 5001 (User), Port 5002 (ApiKey), and Port 5003 (AI).
-   **AI Management**: Interactive model discovery and AI generation testing interface.
-   **Gateway Integration**: All requests are routed through the Nginx gateway for consistent CORS and Auth Sidecar handling.
-   **JWT Lifecycle**: Shared token rejuvenation and cross-service session management.
-   **Modern Stack**: Powered by Vite, TailwindCSS, and Lucide Icons for a premium developer experience.

## 📋 Available Pages

| Page | URL | Description |
|---|---|---|
| **Dashboard** | `/dashboard` | Ecosystem overview & service status |
| **User List** | `/users` | Member management & activation control |
| **API Keys** | `/keys` | Key generation, RPM limits, and usage logs |
| **AI Hub** | `/ai` | Model discovery and prompt testing playground |
| **Settings** | `/settings` | Password, Profile, and OTP security updates |

---

## 🏃 Operation
### Start the Application
```bash
npm install
npm run dev
```

## 🛠️ Configuration
The frontend communicates with the **Nginx Gateway** (typically on port 80). Ensure your `.env` points to the gateway URL.

---

&copy; 2026 Admin Dashboard Infrastructure
