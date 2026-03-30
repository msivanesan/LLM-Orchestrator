from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import redis
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
mail = Mail()
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
