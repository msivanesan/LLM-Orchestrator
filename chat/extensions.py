import redis
import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from dotenv import load_dotenv

load_dotenv()

# expire_on_commit=False prevents DetachedInstanceError in streaming generators:
# after commit(), ORM attributes remain accessible without a live session.
db = SQLAlchemy(session_options={"expire_on_commit": False})
jwt = JWTManager()
cache = Cache()

# Redis client (raw, for manual pub/sub, context management, etc.)
redis_client = redis.from_url(
    os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    decode_responses=True
)
