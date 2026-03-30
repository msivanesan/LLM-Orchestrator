from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_user_name = db.Column(db.String(80), nullable=False)
    key_name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(64), unique=True, index=True, nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=True)
    rpm = db.Column(db.Integer, default=60, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "key_name": self.key_name,
            "key_user_name": self.key_user_name,
            "key": self.key,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "rpm": self.rpm,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
