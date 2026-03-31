from flask import Blueprint, request, jsonify, current_app
import secrets
import json
import redis
import os
from .models import db, ApiKey
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

apikey_bp = Blueprint('apikeys', __name__)
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Admin required middleware (checks shared JWT)
def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        # Since this service doesn't have a 'User' model, 
        # we'll use custom claims or just check the role if stored in the JWT.
        # However, our current user service DOES NOT put the role in the JWT by default.
        # So I'll need to update the User service to include the 'role' in the JWT claims!
        if claims.get("role") == "admin":
            return fn(*args, **kwargs)
        return jsonify({"message": "Admin access required"}), 403
    wrapper.__name__ = fn.__name__
    return wrapper

@apikey_bp.route('/', methods=['GET'])
@admin_required
def list_keys():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = ApiKey.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "items": [k.to_dict() for k in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    })

@apikey_bp.route('/create', methods=['POST'])
@admin_required
def create_key():
    data = request.get_json()
    if not data or not data.get('key_name') or not data.get('key_user_name') or not data.get('contact_email'):
        return jsonify({"message": "Key Name, Key User Name, and Contact Email are required"}), 400

    new_secret = f"ak_{secrets.token_hex(24)}"
    
    new_key = ApiKey(
        key_user_name=data['key_user_name'],
        key_name=data['key_name'],
        key=new_secret,
        contact_email=data['contact_email'],
        contact_phone=data.get('contact_phone'),
        rpm=data.get('rpm', 60)
    )
    
    db.session.add(new_key)
    db.session.commit()
    
    # Notify via Central Mailer
    email_data = {
        "email": new_key.contact_email,
        "subject": f"API Access Granted: {new_key.key_name}",
        "template_id": "API_KEY_CREATED",
        "context": {
            "username": new_key.key_user_name,
            "key_name": new_key.key_name,
            "key": new_key.key,
            "rpm": new_key.rpm
        }
    }
    try:
        redis_client.publish('email_queue', json.dumps(email_data))
        current_app.logger.info(f"API Key notification queued for {new_key.contact_email}")
    except Exception as e:
        current_app.logger.error(f"Failed to queue API key notification: {str(e)}")

    return jsonify(new_key.to_dict()), 201

@apikey_bp.route('/<int:key_id>', methods=['PUT'])
@admin_required
def update_key(key_id):
    data = request.get_json()
    key = ApiKey.query.get_or_404(key_id)
    
    if 'rpm' in data:
        key.rpm = int(data['rpm'])
    if 'key_name' in data:
        key.key_name = data['key_name']
        
    db.session.commit()
    return jsonify(key.to_dict())

@apikey_bp.route('/<int:key_id>/toggle', methods=['PATCH'])
@admin_required
def toggle_key(key_id):
    key = ApiKey.query.get_or_404(key_id)
    key.is_active = not key.is_active
    db.session.commit()
    
    # Notify Owner of Status Change
    status_text = "Active" if key.is_active else "Revoked"
    email_data = {
        "email": key.contact_email,
        "subject": f"Security Alert: API Key {key.key_name} is now {status_text}",
        "template_id": "APIKEY_STATUS_UPDATE",
        "context": {
            "username": key.key_user_name,
            "key_name": key.key_name,
            "status": status_text
        }
    }
    try:
        redis_client.publish('email_queue', json.dumps(email_data))
    except:
        pass

    return jsonify(key.to_dict())

@apikey_bp.route('/<int:key_id>', methods=['DELETE'])
@admin_required
def delete_key(key_id):
    key = ApiKey.query.get_or_404(key_id)
    
    # Notify before deletion
    email_data = {
        "email": key.contact_email,
        "subject": f"API Access Terminated: {key.key_name}",
        "template_id": "APIKEY_DELETED",
        "context": {
            "username": key.key_user_name,
            "key_name": key.key_name
        }
    }
    try:
        redis_client.publish('email_queue', json.dumps(email_data))
    except:
        pass

    db.session.delete(key)
    db.session.commit()
    return jsonify({"message": "Key deleted successfully"}), 200

@apikey_bp.route('/validate', methods=['POST'])
def validate_key():
    """
    Public validation endpoint for external services to check key validity and rate limits.
    Expects JSON: {"key": "ak_..."}
    """
    data = request.get_json()
    key_str = data.get('key')
    
    if not key_str:
        return jsonify({"valid": False, "message": "Key is required"}), 400
        
    # 1. Check DB (or Redis cache for better performance)
    key_record = ApiKey.query.filter_by(key=key_str).first()
    
    if not key_record:
        return jsonify({"valid": False, "message": "Invalid API Key"}), 401
        
    if not key_record.is_active:
        return jsonify({"valid": False, "message": "API Key is revoked"}), 403
        
    # 2. Rate Limiting Logic (Redis Sliding Window/Fixed Window)
    # Current minute timestamp
    from datetime import datetime
    now = datetime.utcnow()
    minute_timestamp = now.strftime('%Y%m%d%H%M')
    redis_limit_key = f"rate_limit:{key_str}:{minute_timestamp}"
    
    try:
        # Atomic Increment
        current_requests = redis_client.incr(redis_limit_key)
        
        # Set expiry for the key if it's the first request of the minute
        if current_requests == 1:
            redis_client.expire(redis_limit_key, 60)
            
        if current_requests > key_record.rpm:
            return jsonify({
                "valid": True,
                "allowed": False,
                "message": "Rate limit exceeded (RPM limit reached)",
                "limit": key_record.rpm,
                "current": current_requests
            }), 429
            
        return jsonify({
            "valid": True,
            "allowed": True,
            "key_name": key_record.key_name,
            "rpm_limit": key_record.rpm,
            "remaining": max(0, key_record.rpm - current_requests)
        }), 200
        
    except Exception as e:
        # Fallback if Redis is down (fail open or fail closed depends on policy)
        current_app.logger.error(f"Rate limiting error: {str(e)}")
        return jsonify({"valid": True, "allowed": True, "message": "Validation warning: Rate checking unavailable"}), 200

@apikey_bp.route('/validate_header', methods=['GET', 'POST'])
def validate_header():
    """Reads key from X-API-KEY header for Nginx auth_request."""
    key_str = request.headers.get('X-API-KEY')
    if not key_str or not ApiKey.query.filter_by(key=key_str, is_active=True).first():
        return jsonify({"message": "Invalid or missing key"}), 401
    
    # Rate limit check
    from datetime import datetime
    now = datetime.utcnow()
    redis_limit_key = f"rate_limit:{key_str}:{now.strftime('%Y%m%d%H%M')}"
    key_record = ApiKey.query.filter_by(key=key_str).first()
    
    try:
        if redis_client.incr(redis_limit_key) > key_record.rpm:
            # We return 403 here because Nginx auth_request 
            # only understands 401/403 as "denied".
            return jsonify({"message": "Rate limit exceeded"}), 403
        return "", 200
    except:
        return "", 200
