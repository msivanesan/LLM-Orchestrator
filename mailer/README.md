# 🛰️ Centralized Mailer Service (Asynchronous Subscriber)

A high-fidelity HTML email delivery engine that scales independently of your API services.

## 🚀 Key Features
-   **Asynchronous Processing**: Reduces latency by processing emails from a Redis queue.
-   **Lightweight Context**: Receives only tiny "Template Context" instead of full HTML to minimize Redis memory usage.
-   **Dynamic Support**: Auto-hydrates various templates (Welcome, OTP, Security Alert, API Grant, etc.).
-   **Custom Templating**: Modern, branded design-system for all communications.

## 📡 Message Format (Redis Pub/Sub)
The Mailer subscribes to the `email_queue` channel.

```json
{
  "email": "user@example.com",
  "subject": "Security Alert",
  "template_id": "PASSWORD_CHANGED",
  "context": {
      "username": "DevUser"
  }
}
```

---

## 🛠️ Configuration
-   **Redis**: Requires `REDIS_URL` for subscription.
-   **SMTP**: Requires `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, and `MAIL_PASSWORD` in the root `.env`.

---

## 🏃 Running the Worker
```bash
python -m mailer.manage run
```

---

&copy; 2026 Admin Dashboard Infrastructure
