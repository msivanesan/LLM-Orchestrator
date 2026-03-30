# 🏰 User Microservice (Identity Provider)

This service manages all aspects of user authentication, security, and profile management. It acts as the "Identity Provider" for the entire microservice ecosystem.

## 🚀 Key Features
-   **JWT Management**: Issues access (7 minutes) and refresh (30 days) tokens.
-   **Security Controls**: Brute-force protection for OTP verification.
-   **Identity Retrieval**: Provides the `/me` endpoint for cross-service authorization.
-   **Communication**: Enqueues welcome and security emails via the central Redis channel.

## 📡 API Endpoints (Port 5001)

| Route | Method | Description |
|---|---|---|
| `/register` | POST | Register a new user (Admin) |
| `/login` | POST | Authenticate and get JWTs |
| `/refresh` | POST | Renew access tokens |
| `/me` | GET | Current user context |
| `/forgot-password` | POST | Trigger OTP recovery (Resend logic enabled) |
| `/verify-otp` | POST | Reset password via numeric code |
| `/change-password` | POST | Manual security update |

---

## 🛠️ Configuration
-   **Redis**: Requires a running Redis instance for OTP storage and attempt tracking.
-   **Database**: Uses SQLite (`user.db`).
-   **JWT Shared Secret**: Must match other services to allow cross-service validation.

---

## 🏃 Running the Service
```bash
python -m user.manage runserver
```

---

&copy; 2026 Identity Infrastructure Service
