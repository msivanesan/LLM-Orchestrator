# 🔑 ApiKey Microservice (Integration Layer)

Manage external API credentials and high-performance rate limiting for third-party developers.

## 🚀 Key Features
-   **Key Generation**: Automatically generates secure, 24-character prefixed keys (`ak_...`).
-   **Granular Logic**: Rate limiting (RPM) can be adjusted per individual key.
-   **Security Controls**: Revoke/Enable access instantly from the dashboard.
-   **Scalability**: Indexed `key` column for O(1) database lookups.
-   **Communication**: Notifies developers of creation, status changes, and terminations.

## 📡 API Endpoints (Port 5002)

| Route | Method | Description |
|---|---|---|
| `/create` | POST | Generate a new integration key |
| `/` | GET | Paginated list of keys (Admin) |
| `/<id>` | PUT | Update RPM/Metadata |
| `/<id>/toggle` | PATCH | Revoke/Enable access |
| `/<id>` | DELETE | Terminate key permanently |

---

## 🛠️ Configuration
-   **Authorization**: Uses shared JWTs from the User service.
-   **Database**: Uses indexed SQLite (`apikey.db`).
-   **Shared Secrets**: Ensure `JWT_SECRET_KEY` matches the Identity Provider.

---

## 🏃 Running the Service
```bash
python -m apikey.manage runserver
```

---

&copy; 2026 Admin Portal Infrastructure
