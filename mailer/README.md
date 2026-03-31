# 📬 Central Mailer Service (Worker)

The Mailer Service is a durable background worker that handles email delivery for all services in the ecosystem. It decouples the user-facing APIs from slow SMTP operations.

## 🚀 Key Features
-   **Durable Queueing**: Migrated from Pub/Sub to **Redis List (`email_queue`)**. This ensures no emails are lost if the worker is offline.
-   **Blocking Consumer**: Uses `BRPOP` for maximum efficiency and immediate processing of new tasks.
-   **High-Fidelity Templates**: Supports complex HTML templates with dynamic data hydration.
-   **Safe Management**: Includes a custom CLI for starting and stopping the background process with PID tracking.

## 🏃 Operation
### Start the Worker
```bash
python -m mailer.manage runserver
```

### Stop the Worker
```bash
python -m mailer.manage stop
```

## 🛠️ Configuration
Required in `.env`:
-   `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`: SMTP Credentials.
-   `MAIL_DEFAULT_SENDER`: The email address appearing in the "From" field.
-   `REDIS_URL`: Connection string for the shared Redis task queue.

## 📡 Message Format
Services trigger emails by pushing a JSON payload to the `email_queue`:
```json
{
  "to": "user@example.com",
  "subject": "Login OTP",
  "template": "otp_email",
  "data": { "otp": "123456" }
}
```
