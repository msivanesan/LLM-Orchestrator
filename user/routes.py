from flask import Blueprint, request, jsonify
from models import db, User, TokenBlocklist
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from flask_mail import Message
from extensions import db, mail, redis_client
from flask import current_app
import random
import json

user_bp = Blueprint('users', __name__)

# Middleware to check if user is admin
def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user and user.role == 'admin':
            return fn(*args, **kwargs)
        return jsonify({"message": "Admin access required"}), 403
    wrapper.__name__ = fn.__name__
    return wrapper

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = User.query.order_by(User.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "items": [u.to_dict() for u in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    })

@user_bp.route('/register', methods=['POST'])
@admin_required # Only admin can register new users now as per previous request
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 409

    hashed_pw = generate_password_hash(data['password'])
    role = data.get('role', 'user')
    is_active = data.get('is_active', True)
    
    if role not in ['admin', 'user']:
        return jsonify({"message": "Invalid role specified"}), 400

    new_user = User(
        username=data['username'], 
        email=data['email'], 
        password_hash=hashed_pw, 
        role=role,
        is_active=is_active
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Notify New User
    email_data = {
        "email": new_user.email,
        "subject": "Your New Account Credentials",
        "template_id": "WELCOME_EMAIL",
        "context": {
            "username": new_user.username,
            "email": new_user.email
        }
    }
    try:
        redis_client.rpush('email_queue', json.dumps(email_data))
    except:
        pass

    current_app.logger.info(f"User created: {new_user.username} by admin {get_jwt_identity()}")
    return jsonify(new_user.to_dict()), 201

@user_bp.route('/<int:user_id>/toggle', methods=['PATCH'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    # Notify User of Status Change
    status_text = "Enabled" if user.is_active else "Disabled"
    email_data = {
        "email": user.email,
        "subject": f"Security Alert: Your account is now {status_text}",
        "template_id": "STATUS_UPDATE",
        "context": {
            "username": user.username,
            "status": status_text
        }
    }
    try:
        redis_client.rpush('email_queue', json.dumps(email_data))
    except:
        pass

    current_app.logger.info(f"User status toggled: {user.username} to {user.is_active} by {get_jwt_identity()}")
    return jsonify(user.to_dict())

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/<int:user_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data: user.username = data['username']
    if 'email' in data: user.email = data['email']
    if 'role' in data and data['role'] in ['admin', 'user']: user.role = data['role']
    if 'is_active' in data: user.is_active = data['is_active']
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    
    db.session.commit()
    current_app.logger.info(f"User updated: {user.username} by admin {get_jwt_identity()}")
    return jsonify(user.to_dict())

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Prevent self-deletion if needed, but for now allow direct admin delete
    identity = str(get_jwt_identity())
    if str(user.id) == identity:
        return jsonify({"message": "You cannot delete your own admin account"}), 403
        
    db.session.delete(user)
    db.session.commit()
    current_app.logger.info(f"User deleted: {user.username} by admin {identity}")
    return jsonify({"message": "User deleted successfully"}), 200

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400

    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        if not user.is_active:
            return jsonify({"message": "Account is disabled. Please contact administrator."}), 403
            
        access_token = create_access_token(
            identity=str(user.id), 
            additional_claims={"role": user.role}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200
    
    current_app.logger.warning(f"Failed login attempt for username: {data['username']}")
    return jsonify({"message": "Invalid username or password"}), 401

@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    
    new_access_token = create_access_token(
        identity=identity, 
        additional_claims={"role": user.role if user else "user"}
    )
    new_refresh_token = create_refresh_token(identity=identity)
    
    return jsonify({
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }), 200

@user_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify({"message": "Access token revoked"}), 200

@user_bp.route('/logout-refresh', methods=['DELETE'])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify({"message": "Refresh token revoked"}), 200

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"message": "Old and New passwords are required"}), 400
        
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if not check_password_hash(user.password_hash, old_password):
        return jsonify({"message": "Incorrect old password"}), 400
        
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    current_app.logger.info(f"Password changed by user: {user.username}")
    # Security Notification
    email_data = {
        "email": user.email,
        "subject": "Security Alert: Password Changed",
        "template_id": "PASSWORD_CHANGED",
        "context": {
            "username": user.username
        }
    }
    try:
        redis_client.rpush('email_queue', json.dumps(email_data))
    except:
        pass

    return jsonify({"message": "Password updated successfully"}), 200

# PASSWORD RESET Logic
@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"message": "Email is required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User does not exist. Please contact admin."}), 404
        
    if not user.is_active:
        return jsonify({"message": "User is not active. Please contact admin."}), 403
    
    # Generate or Reuse 6-digit OTP
    redis_key = f"otp:{email}"
    existing_otp = redis_client.get(redis_key)
    
    if existing_otp:
        otp = existing_otp.decode('utf-8')
    else:
        import random
    # Push to Redis List (Durable Queue Model)
    email_data = {
        "email": email,
        "subject": "Your Security Code",
        "template_id": "OTP_VERIFICATION",
        "context": {
            "username": user.username,
            "otp": otp
        }
    }
    
    try:
        redis_client.rpush('email_queue', json.dumps(email_data))
        current_app.logger.info(f"Email task pushed to Redis for {email}")
    except Exception as e:
        current_app.logger.error(f"Failed to push email task: {str(e)}")
        # In development, you can return the OTP for testing
        if current_app.debug:
            return jsonify({"message": "OTP task created (Debug Mode)", "otp": otp}), 200
        return jsonify({"message": "Service busy. Please try again later."}), 500

    return jsonify({"message": "If this email is registered, you will receive an OTP shortly."}), 200

@user_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    
    if not all([email, otp, new_password]):
        return jsonify({"message": "Email, OTP and New Password are required"}), 400
        
    # Check Login attempts in Redis
    attempts_key = f"otp_attempts:{email}"
    attempts = redis_client.get(attempts_key)
    attempts_count = int(attempts) if attempts else 0
    
    if attempts_count >= 5:
        # Disable User account
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_active = False
            db.session.commit()
            current_app.logger.warning(f"Account disabled due to brute-force OTP attempts: {email}")
        return jsonify({"message": "Too many failed attempts. Your account has been disabled. Please contact admin."}), 403

    # Check OTP in Redis
    stored_otp = redis_client.get(f"otp:{email}")
    if not stored_otp or stored_otp.decode('utf-8') != otp:
        # Increment attempts
        redis_client.setex(attempts_key, 600, attempts_count + 1)
        return jsonify({"message": f"Invalid or expired OTP. Attempt {attempts_count + 1}/5"}), 400
        
    # Update Password if correct
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    # Clear OTP and attempts from Redis
    redis_client.delete(f"otp:{email}")
    redis_client.delete(attempts_key)
    
    current_app.logger.info(f"Password reset success for {email}")
    
    # Security Notification
    email_data = {
        "email": email,
        "subject": "Security Alert: Password Changed",
        "template_id": "PASSWORD_CHANGED",
        "context": {
            "username": user.username
        }
    }
    try:
        redis_client.rpush('email_queue', json.dumps(email_data))
    except:
        pass

    return jsonify({"message": "Password reset successfully"}), 200
