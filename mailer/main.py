from flask import Flask
from flask_mail import Mail, Message
import redis
import json
import os
from .templates import (
    get_otp_template, 
    get_apikey_template, 
    get_welcome_template, 
    get_password_changed_template, 
    get_status_changed_template,
    get_apikey_status_changed_template,
    get_apikey_deleted_template
)
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    return app

def run_worker():
    app = create_app()
    mail = Mail(app)
    
    redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    
    with app.app_context():
        print("📮 Central Mailer Service started. Listening on 'email_queue'...")
        pubsub = redis_client.pubsub()
        pubsub.subscribe('email_queue')
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    email = data.get('email')
                    subject = data.get('subject', 'Notification')
                    template_id = data.get('template_id')
                    context = data.get('context', {})
                    
                    html = None
                    if template_id == 'OTP_VERIFICATION':
                        html = get_otp_template(context.get('username'), context.get('otp'))
                    elif template_id == 'API_KEY_CREATED':
                        html = get_apikey_template(
                            context.get('username'), 
                            context.get('key_name'), 
                            context.get('key'),
                            context.get('rpm')
                        )
                    elif template_id == 'WELCOME_EMAIL':
                        html = get_welcome_template(context.get('username'), context.get('email'))
                    elif template_id == 'PASSWORD_CHANGED':
                        html = get_password_changed_template(context.get('username'))
                    elif template_id == 'STATUS_UPDATE':
                        html = get_status_changed_template(context.get('username'), context.get('status'))
                    elif template_id == 'APIKEY_STATUS_UPDATE':
                        html = get_apikey_status_changed_template(
                            context.get('username'), 
                            context.get('key_name'), 
                            context.get('status')
                        )
                    elif template_id == 'APIKEY_DELETED':
                        html = get_apikey_deleted_template(context.get('username'), context.get('key_name'))
                    
                    # Fallback to direct html if provided
                    if not html:
                        html = data.get('html')
                        
                    body = data.get('body', 'Please view this email in an HTML-compatible client.')
                    
                    if not email:
                        continue
                        
                    msg = Message(
                        subject,
                        recipients=[email],
                        body=body,
                        html=html
                    )
                    mail.send(msg)
                    print(f"📧 [Mailer] Successfully sent {template_id or 'direct'} email to: {email}")
                except Exception as e:
                    print(f"❌ [Mailer] Error: {str(e)}")

if __name__ == '__main__':
    run_worker()
