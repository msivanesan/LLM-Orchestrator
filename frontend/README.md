# 🖥️ Admin Dashboard (React/Vite)

A high-fidelity, microservice-aware administrative interface to manage your entire platform.

## 🚀 Key Features
-   **Service Aware**: Combines Port 5001 (User) and Port 5002 (ApiKey) into a unified UI.
-   **JWT Refresh**: Shared token rejuvenation across all microservices.
-   **Security recovery**: Branded multi-page OTP and password reset flow.
-   **Role-Based Access**: Specialized views for Administrators (API Management, User Creation).
-   **Modern Stack**: Vite, TailwindCSS (for custom styles), Lucide Icons.

## 📋 Available Pages

| Page | URL | Description |
|---|---|---|
| **Dashboard** | `/dashboard` | Ecosystem overview |
| **User List** | `/users` | Member management |
| **API Keys** | `/keys` | External integration control (Admin) |
| **Settings** | `/settings` | Password and profile updates |
| **Recovery** | `/forgot-password` | Security-first OTP recovery flow |

---

## 🛠️ Configuration
-   **API Base**: Controlled via `.env` (maps to User and ApiKey services).

---

## 🏃 Running the Development Server
```bash
npm install
npm run dev
```

---

&copy; 2026 Dashboard Microservice Ecosystem
