def get_otp_template(username, otp):
    return f"""
    <div style="font-family: 'Inter', system-ui, sans-serif; background: #f8fafc; padding: 40px 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="background: #6366f1; padding: 24px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 600;">Security Code</h2>
            </div>
            <div style="padding: 32px; text-align: center;">
                <p style="color: #475569; font-size: 16px; line-height: 1.6; margin-bottom: 24px;">Hello <b>{username}</b>,</p>
                <p style="color: #475569; font-size: 16px; line-height: 1.6;">You requested a password reset. Please use the verification code below to proceed:</p>
                <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; margin: 32px 0; letter-spacing: 5px; font-size: 32px; font-weight: 700; color: #1e293b;">
                    {otp}
                </div>
                <p style="color: #94a3b8; font-size: 14px;">This code will expire in <b>10 minutes</b>. If you did not request this, you can safely ignore this email.</p>
            </div>
            <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px; text-align: center;">
               <p style="color: #94a3b8; font-size: 12px; margin: 0;">&copy; 2026 User Microservice • Secure Dashboard</p>
            </div>
        </div>
    </div>
    """

def get_apikey_template(key_user_name, key_name, key, rpm):
    return f"""
    <div style="font-family: 'Inter', system-ui, sans-serif; background: #f3f4f6; padding: 40px 10px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            <div style="background: #111827; padding: 24px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 600;">API Access Key</h2>
            </div>
            <div style="padding: 32px;">
                <p style="color: #4b5563; font-size: 16px; margin-bottom: 24px;">Hello <b>{key_user_name}</b>,</p>
                <p style="color: #4b5563; font-size: 16px;">An administrator has issued a new API access key for your project:</p>
                
                <div style="background: #f9fafb; border: 1px dashed #d1d5db; border-radius: 8px; padding: 20px; margin: 24px 0;">
                    <p style="margin: 0 0 8px 0; font-size: 13px; color: #6b7280; text-transform: uppercase;">Key Name</p>
                    <p style="margin: 0 0 20px 0; font-size: 18px; font-weight: 600; color: #111827;">{key_name}</p>
                    
                    <p style="margin: 0 0 8px 0; font-size: 13px; color: #6b7280; text-transform: uppercase;">Secret Key</p>
                    <p style="margin: 0 0 0 0; font-size: 20px; font-weight: 700; color: #6366f1; word-break: break-all;">{key}</p>
                </div>

                <p style="color: #4b5563; font-size: 15px;"><b>RPM Limit:</b> {rpm} requests per minute</p>
                <p style="color: #ef4444; font-size: 14px; margin-top: 32px;">Please store this key securely. Never share your secret key with unauthorized parties.</p>
            </div>
            <div style="background: #f9fafb; border-top: 1px solid #e5e7eb; padding: 20px; text-align: center;">
                <p style="color: #9ca3af; font-size: 13px; margin: 0;">&copy; 2026 Dashboard Microservice • API Infrastructure</p>
            </div>
        </div>
    </div>
    """

def get_welcome_template(username, email):
    return f"""
    <div style="font-family: 'Inter', sans-serif; background: #f4f7fa; padding: 40px 20px;">
        <div style="max-width: 550px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e1e8f0; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); padding: 32px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 700;">Welcome Aboard!</h2>
            </div>
            <div style="padding: 40px;">
                <p style="color: #1e293b; font-size: 18px; font-weight: 600; margin-bottom: 16px;">Hi {username},</p>
                <p style="color: #475569; font-size: 16px; line-height: 1.6;">Your administrative account has been successfully created. You can now access your secure dashboard using the credentials below:</p>
                
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin: 32px 0;">
                    <p style="margin: 0 0 8px 0; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Username</p>
                    <p style="margin: 0 0 16px 0; font-size: 16px; font-weight: 600; color: #1e293b;">{username}</p>
                    <p style="margin: 0 0 8px 0; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Registered Email</p>
                    <p style="margin: 0; font-size: 16px; font-weight: 600; color: #1e293b;">{email}</p>
                </div>

                <p style="color: #475569; font-size: 16px;">Please contact your administrator if you need to reset your initial password.</p>
            </div>
            <div style="background: #f8fafc; padding: 24px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 13px; margin: 0;">&copy; 2026 Admin Infrastructure • Enterprise Dashboard</p>
            </div>
        </div>
    </div>
    """

def get_password_changed_template(username):
    return f"""
    <div style="font-family: 'Inter', sans-serif; background: #fff5f5; padding: 40px 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #fed7d7; overflow: hidden; box-shadow: 0 10px 15px rgba(0,0,0,0.05);">
            <div style="background: #ef4444; padding: 24px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 600;">Security Notification</h2>
            </div>
            <div style="padding: 32px; text-align: center;">
                <p style="color: #1e293b; font-size: 16px; font-weight: 600; margin-bottom: 16px;">Hello {username},</p>
                <p style="color: #475569; font-size: 16px; line-height: 1.6;">The password for your account was recently changed. If you performed this action, you can safely ignore this email.</p>
                
                <div style="margin: 32px 0; padding: 20px; background: #fffcf0; border: 1px solid #fef3c7; border-radius: 12px; text-align: left;">
                    <p style="margin: 0; color: #92400e; font-size: 14px;"><b>⚠️ Not you?</b> If you did not change your password, please contact our security team immediately to lock your account.</p>
                </div>
            </div>
            <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0;">&copy; 2026 Secure Auth Systems</p>
            </div>
        </div>
    </div>
    """

def get_status_changed_template(username, status_text):
    color = "#10b981" if "enabled" in status_text.lower() else "#f59e0b"
    return f"""
    <div style="font-family: 'Inter', sans-serif; padding: 40px 20px; background: #f8fafc;">
        <div style="max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 15px rgba(0,0,0,0.05);">
            <div style="background: {color}; padding: 24px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 600;">Account Status Update</h2>
            </div>
            <div style="padding: 32px; text-align: center;">
                <p style="color: #1e293b; font-size: 16px; font-weight: 600; margin-bottom: 16px;">Account Update for {username}</p>
                <p style="color: #475569; font-size: 16px; line-height: 1.6;">An administrator has updated your account status to: <b>{status_text}</b>.</p>
            </div>
            <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0;">&copy; 2026 Dashboard Systems</p>
            </div>
        </div>
    </div>
    """

def get_apikey_status_changed_template(username, key_name, status):
    color = "#10b981" if "active" in status.lower() else "#f59e0b"
    return f"""
    <div style="font-family: 'Inter', sans-serif; background: #f8fafc; padding: 40px 20px;">
        <div style="max-width: 550px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 15px rgba(0,0,0,0.05);">
            <div style="background: {color}; padding: 24px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 600;">API Key Policy Update</h2>
            </div>
            <div style="padding: 32px;">
                <p style="color: #1e293b; font-size: 16px; font-weight: 600; margin-bottom: 16px;">Hello {username},</p>
                <p style="color: #475569; font-size: 15px; line-height: 1.6;">Your API Key <b>"{key_name}"</b> has been updated by an administrator.</p>
                
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin: 24px 0; text-align: center;">
                    <p style="margin: 0; color: #1e293b; font-size: 14px;">The current status of this key is now:</p>
                    <p style="margin: 8px 0 0 0; font-size: 18px; font-weight: 700; color: {color}; text-transform: uppercase;">{status}</p>
                </div>

                <p style="color: #64748b; font-size: 14px;">If this key is revoked, all incoming requests using this credential will be blocked immediately.</p>
            </div>
            <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0;">&copy; 2026 API Infrastructure Services</p>
            </div>
        </div>
    </div>
    """

def get_apikey_deleted_template(username, key_name):
    return f"""
    <div style="font-family: 'Inter', sans-serif; background: #fff5f5; padding: 40px 20px;">
        <div style="max-width: 550px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #fed7d7; overflow: hidden; box-shadow: 0 10px 15px rgba(0,0,0,0.05);">
            <div style="background: #ef4444; padding: 24px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 600;">API Key Terminated</h2>
            </div>
            <div style="padding: 32px;">
                <p style="color: #1e293b; font-size: 16px; font-weight: 600; margin-bottom: 16px;">Hello {username},</p>
                <p style="color: #475569; font-size: 15px; line-height: 1.6;">The API Key <b>"{key_name}"</b> has been permanently deleted from our system.</p>
                
                <div style="margin: 32px 0; padding: 20px; background: #fff5f5; border: 1px solid #feb2b2; border-radius: 12px;">
                    <p style="margin: 0; color: #c53030; font-size: 14px;"><b>⚠️ Key Recalled:</b> All existing integrations using this key will stop working immediately. This action cannot be undone.</p>
                </div>
            </div>
            <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0;">&copy; 2026 Admin Management Portal</p>
            </div>
        </div>
    </div>
    """
