# 👤 Identity & User Service

The User Service is the central identity provider for the ecosystem. It handles user registration, authentication, and personalized profile management.

## 🚀 Key Features
-   **JWT-based Authentication**: Secure, stateless authentication with shared secret key rotation support.
-   **OTP Lifecycle**: Includes email-based OTP verification for secure signups and password resets.
-   **Self-Healing Notifications**: Uses the durable Redis queue (`LPUSH`) to ensure critical account updates are always delivered.
-   **Account Security**: Automated protection against brute-force attacks via account locking after 5 failed attempts.

## 🛠️ Configuration
Required in `.env`:
-   `DATABASE_URL`: Path to your database (supports SQLite/PostgreSQL).
-   `JWT_SECRET_KEY`: Secret string for token signing.
-   `USER_SERVICE_PORT`: Defaults to 5001.

## 🏃 Operation
### Start the Service
```bash
python -m user.manage runserver
```

## 📡 Notable Endpoints
-   `POST /api/users/login`: Login and receive access/refresh tokens.
-   `POST /api/users/register`: Register and trigger OTP email.
-   `GET /api/users/profile`: Private route to manage user settings.
