import json
import time
from .main import create_app, mail, redis_client
from flask_mail import Message

def run_worker():
    app = create_app()
    with app.app_context():
        print("💡 Email Worker started. Listening on 'email_queue'...")
        
        # Subscribe to channel
        pubsub = redis_client.pubsub()
        pubsub.subscribe('email_queue')
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    email = data.get('email')
                    subject = data.get('subject')
                    body = data.get('body')
                    
                    if not email or not subject or not body:
                        continue
                        
                    msg = Message(
                        subject,
                        recipients=[email],
                        body=body
                    )
                    mail.send(msg)
                    print(f"✅ Email sent to {email}")
                except Exception as e:
                    print(f"❌ Worker Error: {str(e)}")

if __name__ == '__main__':
    run_worker()
